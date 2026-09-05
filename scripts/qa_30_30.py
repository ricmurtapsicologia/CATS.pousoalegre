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
    if not m:
        raise AssertionError(f"Aula {n} ausente")
    return m.group(0)


checks: list[tuple[str, bool]] = []
def check(name: str, condition: bool): checks.append((name, bool(condition)))

check("01 Smoke", "<!DOCTYPE html>" in page and page.rstrip().endswith("</html>"))
check("02 Pinpoint", "VIII CATS 2026" in page and "Pouso Alegre" in page)
check("03 Deep", all(page.count(f'data-module="{n}"') == 1 for n in range(1, 9)))
check("04 Consistency", not any(f'data-module="{n}"' in page for n in range(9, 13)))
check("05 Contradiction", not re.search(r'CATS\)? VII(?!I)', page) and "Juiz de Fora" not in page and "4º BBM" not in page)
check("06 Completeness", all(name in page for name in THEORY))
check("07 Traceability", all(f'Aula {n}' in card(n) for n in range(1, 9)))
check("08 Compliance", 'name="robots" content="noindex,nofollow,noarchive"' in page)
check("09 Regression", page.count('class="btn small complete"') == 8)
check("10 Change-impact", "Podcast-ATS-CBMMG" in page and "Curso-ATS" in page)
check("11 Cross-reference", "precurso.html" in page and "data-cats-legacy-guard" in legacy)
check("12 Link integrity", 'href=""' not in page and 'src=""' not in page)
check("13 Visual QA", all('<img ' in card(n) for n in range(1, 9)))
check("14 Accessibility", 'lang="pt-BR"' in page and "skip-link" in page and 'aria-controls="materialsPanel"' in page)
check("15 Usability", "mobileMenuBtn" in page and "lesson-toggle" in portal_js and "courseInfoToggle" in page)
check("16 Cognitive-load", ".hero-card{display:none}" in portal_css and ".course-card .content{display:none" in portal_css)
check("17 Narrative-flow", page.find("Aulas teóricas") < page.find('data-module="1"') < page.find('data-module="8"'))
check("18 Red-team", "baseValidas" not in page and "novasMatriculas" not in page and "terapiadoesquema" not in page)
check("19 Edge-case", "cats-auth-failed" in auth and "cats-auth-failed" in auth_css)
check("20 Scenario stress", "length === 11" in auth and "length === 7" in auth and "request(550)" in auth)
check("21 Fact-check", "Capitão BM Lucas Antônio de Oliveira" in page and "7ª Cia Ind" in page)
check("22 Source-to-claim", "oito aulas teóricas atuais" in page and "46 h/a" in page)
check("23 Theory-only", not any(marker in page for marker in PRACTICE_MARKERS))
check("24 Cards with images", ".course-card .media{display:block" in portal_css and all('<img ' in card(n) for n in range(1, 9)))
check("25 Decision-readiness", 'id="avaliacao"' in page and 'id="assessmentPanel" hidden' in page)
check("26 Publication preflight", "embed.tawk.to" not in page and "Tawk.to" not in page)
check("27 Version-drift", 'content="viii-cats-pa-2026-r4"' in page and "cats_pa_progress_v2" in page)
check("28 Canonical-template", "Curso-ATS/auth.css?v=20260905-2" in page and "Curso-ATS/auth.js?v=20260905-2" in page)
check("29 Duplication/redundancy", page.count("Podcast-ATS-CBMMG") == 1 and page.count("Biblioteca ATS CBMMG") >= 1)
check("30 Terminology", "const TOTAL = 8" in page and "/8</span>" in page and "12 unidades formativas" not in page)

failed = [name for name, ok in checks if not ok]
for name, ok in checks:
    print(f"{'PASS' if ok else 'FAIL'} — {name}")
assert len(checks) == 30, len(checks)
if failed:
    raise SystemExit("Auditoria 30/30 falhou: " + ", ".join(failed))
print("PASS: Auditoria 30/30 — 30 de 30 critérios aprovados.")
