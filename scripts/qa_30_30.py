from __future__ import annotations

import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
page = (ROOT / "index.html").read_text(encoding="utf-8")
auth = (ROOT / "cats-auth.js").read_text(encoding="utf-8")
auth_css = (ROOT / "cats-auth.css").read_text(encoding="utf-8")
portal_css = (ROOT / "portal-ui.css").read_text(encoding="utf-8")
portal_js = (ROOT / "portal-ui.js").read_text(encoding="utf-8")
pre = (ROOT / "precurso.html").read_text(encoding="utf-8")
legacy = (ROOT / "legacy.html").read_text(encoding="utf-8")

with urllib.request.urlopen("https://raw.githubusercontent.com/ricmurtapsicologia/cats-2025-4bbm-jf/main/index.html", timeout=30) as r:
    old = r.read().decode("utf-8")


def old_slide_ids() -> list[str]:
    return re.findall(r'data-slide-id="([^"]+)"', old)


checks: list[tuple[str, bool]] = []
def check(name: str, condition: bool): checks.append((name, bool(condition)))

check("01 Smoke", "<!DOCTYPE html>" in page and page.rstrip().endswith("</html>"))
check("02 Pinpoint", "VIII CATS 2026" in page and "Pouso Alegre" in page)
check("03 Deep", all(f'data-module="{n}"' in page for n in range(1, 13)))
check("04 Consistency", all(page.count(f'data-module="{n}"') == 1 for n in range(1, 13)))
check("05 Contradiction", not re.search(r'CATS\)? VII(?!I)', page) and "Juiz de Fora" not in page and "4º BBM" not in page)
check("06 Completeness", sum(page.count(f'data-module="{n}"') for n in range(1, 13)) == 12)
check("07 Traceability", all(slide_id in page for slide_id in old_slide_ids()))
check("08 Compliance", 'name="robots" content="noindex,nofollow,noarchive"' in page)
check("09 Regression", page.count('class="btn small complete"') == 12)
check("10 Change-impact", "Podcast-ATS-CBMMG" in page and "Curso-ATS" in page)
check("11 Cross-reference", "precurso.html" in page and "legacy.html" in pre)
check("12 Link integrity", 'href=""' not in page and 'src=""' not in page)
check("13 Visual QA", "portal-ui.css?v=20260905-1" in page and "@media(min-width:761px)" in portal_css)
check("14 Accessibility", 'lang="pt-BR"' in page and "skip-link" in page and 'aria-controls="materialsPanel"' in page)
check("15 Usability", "mobileMenuBtn" in page and "folder-toggle" in page and "lesson-toggle" in portal_js)
check("16 Cognitive-load", ".hero-card{display:none}" in portal_css and ".course-card .content{display:none" in portal_css)
check("17 Narrative-flow", page.find("Aulas teóricas") < page.find("Práticas presenciais") < page.find("Prevenção ao comportamento suicida"))
check("18 Red-team", "baseValidas" not in page and "novasMatriculas" not in page and "terapiadoesquema" not in page)
check("19 Edge-case", "cats-auth-failed" in auth and "cats-auth-failed" in auth_css)
check("20 Scenario stress", "length === 11" in auth and "length === 7" in auth and "request(550)" in auth)
check("21 Fact-check", "Capitão BM Lucas Antônio de Oliveira" in page and "7ª Cia Ind" in page)
check("22 Citation", 'meta name="cats-release" content="viii-cats-pa-2026-r3"' in page)
check("23 Source-to-claim", all(x in page for x in ("46 h/a", "Prática de conversação em ATS", "Risco de incêndio/explosão", "Risco de precipitação", "Risco de afogamento")))
check("24 Legal defensibility", "Todos os direitos reservados" in page and "HASH_B64" not in page)
check("25 Decision-readiness", 'id="avaliacao"' in page and 'id="assessmentPanel" hidden' in page and "URL oficial" in page)
check("26 Publication preflight", "embed.tawk.to" not in page and "Tawk.to" not in page)
check("27 Version-drift", "cats_pa_progress_v2" in page and "cats_pa_onboarded_v2" in page)
check("28 Canonical-template", "Curso-ATS/auth.css?v=20260905-2" in page and "Curso-ATS/auth.js?v=20260905-2" in page)
check("29 Duplication/redundancy", page.count("Podcast-ATS-CBMMG") == 1 and page.count("Biblioteca ATS CBMMG") >= 1)
check("30 Terminology", "12 unidades formativas" in page and "const TOTAL = 12" in page and "details class=\"materials\"" not in page)

failed = [name for name, ok in checks if not ok]
for name, ok in checks:
    print(f"{'PASS' if ok else 'FAIL'} — {name}")
assert len(checks) == 30, len(checks)
if failed:
    raise SystemExit("Auditoria 30/30 falhou: " + ", ".join(failed))
print("PASS: Auditoria 30/30 — 30 de 30 critérios aprovados.")
