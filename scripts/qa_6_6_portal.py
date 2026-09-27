from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
page = (ROOT / "index.html").read_text(encoding="utf-8")
auth = (ROOT / "cats-auth.js").read_text(encoding="utf-8")
presentation = (ROOT / "presentation-originals.js").read_text(encoding="utf-8")
portal = (ROOT / "portal-ui.js").read_text(encoding="utf-8")
portal_core = (ROOT / "portal-ui-core.js").read_text(encoding="utf-8")
workflow = (ROOT / ".github/workflows/cats-pa-gate.yml").read_text(encoding="utf-8")
lighthouse = (ROOT / ".github/workflows/lighthouse-production.yml").read_text(encoding="utf-8")

LESSON_IDS = {
    1: "1ZYiAFZwrDE2i2zRpMg714cBqC4R-2OeH",
    2: "19n4VMAyYdaCjbYYIH8eZB3duNC1FkSF7",
    3: "1GuEU435vhorxZt42dAEurX2mVopFpFEz",
    4: "1kiKcOToIu1tKJRzWFVmARJYPP3N4J0S_",
    5: "1AasaqZYAqBZJtoNCOh8e6TyBeb_11Fm-",
    6: "1SNvZyrliydPk6iTkwAKhZ66FZ9AO7ac9",
    7: "1hx-CVfbGbCzen1Ygc0-9lTHm81xVcaxw",
    8: "1lVMb2TMiex4Z48_y1S2GA_mnTTgogS6u",
}

checks: list[tuple[str, bool, str]] = []

def gate(name: str, ok: bool, evidence: str) -> None:
    checks.append((name, bool(ok), evidence))

# 1 — Acesso autenticado e fail-closed na interface.
gate(
    "Acesso autenticado",
    "cats_pa_auth_v1" in auth
    and "cats-auth-failed" in auth
    and "Acesso do aluno" in auth
    and "Curso-ATS/auth.js" in page
    and "noindex,nofollow,noarchive" in page,
    "Sessão isolada, gate institucional e falha fechada da interface.",
)

# 2 — Oito aulas integralmente locais e rastreáveis.
lesson_ok = True
for module, source_id in LESSON_IDS.items():
    pdf = ROOT / f"assets/lessons/aula-0{module}.pdf"
    lesson_ok &= pdf.is_file() and pdf.stat().st_size > 10_000 and pdf.read_bytes()[:5] == b"%PDF-"
    lesson_ok &= page.count(f'data-module="{module}"') == 1
    lesson_ok &= page.count(f'href="assets/lessons/aula-0{module}.pdf"') == 1
    lesson_ok &= source_id in presentation and source_id in page

gate(
    "Aulas locais e rastreáveis",
    lesson_ok
    and "docs.google.com/presentation/d/" not in page
    and "local-pdf" in presentation
    and "externalNavigation:false" in presentation,
    "8/8 PDFs locais válidos; Drive preservado apenas como rastreabilidade da fonte.",
)

# 3 — Política de mídia: assistir/ouvir, sem oferta explícita de download.
video_sources = re.findall(r'https://www\.youtube\.com/embed/[A-Za-z0-9_-]+', page)
media_ok = (
    len(video_sources) == 6
    and "controlsList','nodownload noremoteplayback" in presentation
    and "disableRemotePlayback" in presentation
    and "Podcast-ATS-CBMMG" in page
    and not re.search(r'<(?:audio|video)\b[^>]*\bdownload\b', page, re.I)
    and not re.search(r'<a\b[^>]*\bdownload\b[^>]*(?:mp3|m4a|aac|wav|ogg|mp4|webm)', page, re.I)
)
gate(
    "Mídia sem download exposto",
    media_ok,
    "6 vídeos deferred, podcast acessível e política nodownload/noremoteplayback para mídia nativa.",
)

# 4 — Resíduos, duplicidades e incongruências removidos do arquivo versionado.
gate(
    "Fonte materializada sem legado concorrente",
    "baseEmbed =" not in page
    and "viewUrl   =" not in page
    and "openExternal" not in page
    and "practice-note" not in page
    and "material não publicado neste portal" not in page
    and "Recohecimento" not in page
    and "humanizada,técnicas" not in page
    and page.count("Podcast-ATS-CBMMG") == 1,
    "O próprio index versionado já está no estado canônico; o CI não precisa reescrevê-lo.",
)

# 5 — UX responsiva e acesso real ao conteúdo.
gate(
    "UX e acessibilidade operacional",
    'class="skip-link"' in page
    and 'aria-labelledby="slidesTitle"' in page
    and "lesson-toggle" in portal_core
    and "closeOtherCourseCards" in portal_core
    and "presentation-originals.js" in portal
    and "prefers-reduced-motion:reduce" in (ROOT / "portal-ui.css").read_text(encoding="utf-8"),
    "Skip link, modal rotulado, acordeão mobile, reduced motion e viewer canônico.",
)

# 6 — O pipeline deve testar sem mutar/pushar a fonte e o Lighthouse deve rodar
# sobre o checkout exato do candidato, com artefato obrigatório.
pipeline_ok = (
    "pull_request:" in workflow
    and "branches: [main]" in workflow
    and "contents: read" in workflow
    and "persist-credentials: false" in workflow
    and "git push" not in workflow
    and "git commit" not in workflow
    and "git diff --exit-code" in workflow
    and "qa_30_30.py" in workflow
    and "qa_90_90.py" in workflow
    and "qa_6_6_portal.py" in workflow
    and "smoke_portal.py" in workflow
    and "e2e_precurso.py" in workflow
    and "e2e_release.py" in workflow
    and "pull_request:" in lighthouse
    and "lighthouse-candidate" in lighthouse
    and "http://127.0.0.1:8765" in lighthouse
    and "LIGHTHOUSE_GATE_PASS" in lighthouse
    and "if-no-files-found: error" in lighthouse
    and "curl -fsSL --max-time 20 \"$BASE/\" -o /tmp/cats-home.html" in lighthouse
)
gate(
    "Pipeline de entrega verificável",
    pipeline_ok,
    "PR testa fonte imutável; release gate não escreve; Lighthouse audita o checkout exato e exige artefato.",
)

print("GATES_PORTAL_6_6")
for index, (name, ok, evidence) in enumerate(checks, 1):
    print(f'{index}/6 {"PASS" if ok else "FAIL"} | {name} | {evidence}')

failed = [name for name, ok, _ in checks if not ok]
if failed:
    raise SystemExit("GATES_PORTAL_6_6_FAIL: " + ", ".join(failed))
print("GATES_PORTAL_6_6_PASS")
