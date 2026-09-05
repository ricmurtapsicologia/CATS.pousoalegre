from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
page = (ROOT / "index.html").read_text(encoding="utf-8")
auth = (ROOT / "cats-auth.js").read_text(encoding="utf-8")
auth_css = (ROOT / "cats-auth.css").read_text(encoding="utf-8")
portal_css = (ROOT / "portal-ui.css").read_text(encoding="utf-8")
portal_js = (ROOT / "portal-ui.js").read_text(encoding="utf-8")
pre = (ROOT / "precurso.html").read_text(encoding="utf-8")
legacy = (ROOT / "legacy.html").read_text(encoding="utf-8")
readme = (ROOT / "README.md").read_text(encoding="utf-8")

THEORY = [
    "Aspectos Gerais do Comportamento Suicida",
    "Psicopatologia do Comportamento Suicida",
    "Abordagem Técnica: Aspectos Gerais",
    "Abordagem Técnica: Aspectos Específicos",
    "Abordagem Técnica: Comunicação Dissuasiva",
    "Abordagem Tática",
    "Gestão em ATS",
    "Prevenção ao comportamento suicida",
]
PRACTICE_MARKERS = [
    'data-title="Prática de conversação em ATS"',
    'data-title="Prática em ATS: risco de incêndio/explosão"',
    'data-title="Prática em ATS: risco de precipitação"',
    'data-title="Prática em ATS: risco de afogamento"',
    'class="card practice-card"',
]


def card(n: int) -> str:
    m = re.search(rf'<article class="card[^\"]*" data-module="{n}".*?</article>', page, re.S)
    return m.group(0) if m else ""


checks: list[tuple[str, bool]] = []
def add(name: str, condition: bool): checks.append((name, bool(condition)))

# 01–10 — identidade e fonte curricular
add("01 edição", "VIII CATS 2026" in page)
add("02 cidade", "Pouso Alegre" in page)
add("03 unidade", "7ª Cia Ind" in page)
add("04 período", "21–25/09/2026" in page)
add("05 carga total", "46 h/a" in page)
add("06 coordenador", "Capitão BM Lucas Antônio de Oliveira" in page)
add("07 curso", "Curso de Atendimento a Tentativas de Suicídio" in page)
add("08 sem edição VII", not re.search(r'CATS\)? VII(?!I)', page))
add("09 sem local legado", "Juiz de Fora" not in page and "4º BBM" not in page)
add("10 fontes declaradas", "Plano de Ensino CATS 2026" in readme and "QTS CATS 2026" in readme)

# 11–18 — exatamente oito cards curriculares
for n in range(1, 9):
    add(f"{10+n:02d} aula {n} única", page.count(f'data-module="{n}"') == 1)

# 19–26 — todos os cards teóricos mantêm imagem
for n in range(1, 9):
    add(f"{18+n:02d} aula {n} com imagem", '<img ' in card(n) and 'alt=' in card(n))

# 27–34 — oito disciplinas teóricas atuais
for idx, name in enumerate(THEORY, start=27):
    add(f"{idx:02d} conteúdo {name[:24]}", name in page)

# 35–44 — exclusão de práticas, progresso e recursos
add("35 sem módulos 9–12", not any(f'data-module="{n}"' in page for n in range(9, 13)))
add("36 sem cards de prática", not any(marker in page for marker in PRACTICE_MARKERS))
add("37 progresso oito", "const TOTAL = 8" in page and "/8</span>" in page)
add("38 oito conclusões", page.count('class="btn small complete"') == 8)
add("39 título aulas teóricas", "Aulas teóricas" in page)
add("40 intro teoria-only", "exclusivamente as oito aulas teóricas atuais" in page)
add("41 podcast preservado", "https://ricmurtapsicologia.github.io/Podcast-ATS-CBMMG/" in page)
add("42 biblioteca preservada", "https://ricmurtapsicologia.github.io/Curso-ATS/" in page)
add("43 recursos fora da contagem", 'data-module="proj"' in page and 'data-module="biblioteca"' in page)
avaliacao = re.search(r'<section class="container" id="avaliacao".*?</section>', page, re.S)
add("44 avaliação sem link inventado", bool(avaliacao) and '<a ' not in avaliacao.group(0))

# 45–54 — autenticação, privacidade e superfície de risco
add("45 sessão isolada", 'curso_ats_auth_v3: "cats_pa_auth_v1"' in auth)
add("46 tentativas isoladas", 'ats_login_attempts_v3: "cats_pa_login_attempts_v1"' in auth)
add("47 auth css canônico", "Curso-ATS/auth.css?v=20260905-2" in page)
add("48 auth js canônico", "Curso-ATS/auth.js?v=20260905-2" in page)
add("49 wrapper antes base", page.find("cats-auth.js?v=20260905-1") < page.find("Curso-ATS/auth.js?v=20260905-2"))
add("50 fail closed", "cats-auth-failed" in auth and "cats-auth-failed" in auth_css)
add("51 noindex", "noindex,nofollow,noarchive" in page)
add("52 sem credencial crua", all(x not in page for x in ("baseValidas", "novasMatriculas", "terapiadoesquema")))
add("53 sem Tawk", "embed.tawk.to" not in page and "Tawk.to" not in page)
add("54 precurso e legado protegidos", "cats-auth.js?v=20260905-1" in pre and "data-cats-legacy-guard" in legacy)

# 55–64 — onboarding e ergonomia afetiva
add("55 boas-vindas", "Boas-vindas ao VIII CATS 2026" in page)
add("56 fala coordenador", "Seja bem-vindo(a) ao VIII Curso" in page)
add("57 assinatura coordenador", "Coordenador do VIII CATS 2026" in page)
add("58 texto justificado", "text-align:justify" in portal_css)
add("59 hifenização", "hyphens:auto" in portal_css)
add("60 onboarding rolável", "max-height:90dvh" in portal_css and "overflow:auto" in portal_css)
add("61 CTA entrada", "Entrar na trilha" in page)
add("62 orientação compacta", page.count('class="onboard-list"') == 1)
add("63 mensagem de autonomia", "avance no seu ritmo" in page)
add("64 linguagem coerente", "toque no card para abrir uma de cada vez" in page)

# 65–74 — mobile-first e ergonomia cognitiva
add("65 css mobile-first", "@media(min-width:761px)" in portal_css)
add("66 hero reduzido mobile", ".hero-card{display:none}" in portal_css)
add("67 info sob demanda", "courseInfoToggle" in page and 'id="mobileCoursePanel" hidden' in page)
add("68 conteúdo recolhido", ".course-card .content{display:none" in portal_css)
add("69 abertura por botão", "lesson-toggle" in portal_js)
add("70 uma aula por vez", "closeOtherCourseCards" in portal_js)
add("71 imagens visíveis mobile", ".course-card .media{display:block" in portal_css)
add("72 imagem compacta mobile", "height:118px" in portal_css and "object-fit:cover" in portal_css)
add("73 ações empilhadas", ".course-card .actions{display:grid" in portal_css)
add("74 sem FABs no mobile", ".fab,.to-top{display:none}" in portal_css)

# 75–84 — navegabilidade, cascatas e acessibilidade
add("75 logout integrado", "moveLogoutIntoNav" in portal_js and "position:static!important" in portal_css)
add("76 menu mobile", 'id="mobileMenuBtn"' in page and 'aria-controls="mainNavLinks"' in page)
add("77 menu fechado inicial", ".nav-links{display:none" in portal_css)
add("78 materiais por botão", 'aria-controls="materialsPanel"' in page and 'id="materialsPanel" hidden' in page)
add("79 vídeos por botão", 'id="videosToggle"' in page and 'id="videosGrid" hidden' in page)
add("80 avaliação por botão", 'aria-controls="assessmentPanel"' in page and 'id="assessmentPanel" hidden' in page)
add("81 sem details legado", '<details class="materials">' not in page)
add("82 skip link", 'class="skip-link"' in page and 'id="conteudo"' in page)
add("83 diálogos rotulados", 'aria-labelledby="modalTitle"' in page and 'aria-labelledby="slidesTitle"' in page)
add("84 reduced motion", "prefers-reduced-motion:reduce" in portal_css and "prefers-reduced-motion:reduce" in auth_css)

# 85–90 — manutenção, coerência e publicação
add("85 release r4", 'content="viii-cats-pa-2026-r4"' in page)
add("86 progresso persistente", "cats_pa_progress_v2" in page)
add("87 onboarding persistente", "cats_pa_onboarded_v2" in page)
add("88 README teoria-only", "somente 8 aulas teóricas atuais" in readme and "Cards das aulas" in readme)
add("89 sem linguagem manutenção", "Em manutenção" not in page)
add("90 fechamento HTML", page.rstrip().endswith("</html>"))

assert len(checks) == 90, len(checks)
failed = [name for name, ok in checks if not ok]
for name, ok in checks:
    print(f"{'PASS' if ok else 'FAIL'} — {name}")
if failed:
    raise SystemExit("Auditoria 90/90 falhou: " + ", ".join(failed))
print("PASS: Auditoria 90/90 — 90 de 90 critérios aprovados.")
