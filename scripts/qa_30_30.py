from __future__ import annotations

import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
page = (ROOT / "index.html").read_text(encoding="utf-8")
auth = (ROOT / "cats-auth.js").read_text(encoding="utf-8")
auth_css = (ROOT / "cats-auth.css").read_text(encoding="utf-8")
pre = (ROOT / "precurso.html").read_text(encoding="utf-8")
legacy = (ROOT / "legacy.html").read_text(encoding="utf-8")

with urllib.request.urlopen("https://raw.githubusercontent.com/ricmurtapsicologia/cats-2025-4bbm-jf/main/index.html", timeout=30) as r:
    old = r.read().decode("utf-8")


def module_block(text: str, n: int) -> str:
    m = re.search(rf'<article class="card" data-module="{n}".*?</article>', text, re.S)
    if not m:
        raise AssertionError(f"módulo {n} ausente")
    return m.group(0)

checks: list[tuple[str, bool]] = []
def check(name: str, condition: bool):
    checks.append((name, bool(condition)))

check("01 Smoke", "<!DOCTYPE html>" in page and "</html>" in page)
check("02 Pinpoint", "VIII CATS 2026" in page and "Pouso Alegre" in page)
check("03 Deep", all(f'data-module="{n}"' in page for n in range(1, 9)))
check("04 Consistency", page.count("VIII CATS") >= 4)
check("05 Contradiction", all(term not in page for term in ("Juiz de Fora", "CATS VII", "CATS) VII", "4º BBM")))
check("06 Completeness", sum(page.count(f'data-module="{n}"') for n in range(1, 9)) == 8)
check("07 Traceability", all(module_block(page, n) == module_block(old, n) for n in range(1, 9)))
check("08 Compliance", 'name="robots" content="noindex,nofollow,noarchive"' in page)
check("09 Regression", all("Concluir módulo" in module_block(page, n) for n in range(1, 9)))
check("10 Change-impact", "Podcast-ATS-CBMMG" in page and "Curso-ATS" in page)
check("11 Cross-reference", "precurso.html" in page and "legacy.html" in pre)
check("12 Link integrity", 'href=""' not in page and 'src=""' not in page)
check("13 Visual QA", "@media" in page and "--brand" in page)
check("14 Accessibility", 'lang="pt-BR"' in page and "skip-link" in page and 'id="conteudo"' in page)
check("15 Usability", all(x in page for x in (">Aulas<", ">Materiais<", ">Pré-curso<", ">Biblioteca<")))
check("16 Cognitive-load", page.count('class="hero-kpi"') >= 4)
check("17 Narrative-flow", page.find('id="aulas"') < page.find('id="materiais"') < page.find('id="videos"'))
check("18 Red-team", "baseValidas" not in page and "novasMatriculas" not in page and "terapiadoesquema" not in page)
check("19 Edge-case", "cats-auth-failed" in auth and "cats-auth-failed" in auth_css)
check("20 Scenario stress", "length === 11" in auth and "length === 7" in auth and "request(550)" in auth)
check("21 Fact-check", "Capitão BM Lucas Antônio de Oliveira" in page and "7ª Cia Ind" in page)
check("22 Citation", 'meta name="cats-release"' in page)
check("23 Source-to-claim", "21–25/09/2026" in page and "46 h/a" in page)
check("24 Legal defensibility", "Todos os direitos reservados" in page and "HASH_B64" not in page)
check("25 Decision-readiness", 'id="avaliacao"' in page and "URL oficial" in page)
check("26 Publication preflight", "embed.tawk.to" not in page and "Tawk.to" not in page)
check("27 Version-drift", 'content="viii-cats-pa-2026-r2"' in page)
check("28 Canonical-template", "Curso-ATS/auth.css?v=20260905-2" in page and "Curso-ATS/auth.js?v=20260905-2" in page)
check("29 Duplication/redundancy", page.count("Podcast-ATS-CBMMG") == 1 and page.count("Biblioteca ATS CBMMG") >= 1)
check("30 Terminology", "VIII Curso de Atendimento a Tentativas de Suicídio" in auth and "VIII CATS" in page)

failed = [name for name, ok in checks if not ok]
for name, ok in checks:
    print(f"{'PASS' if ok else 'FAIL'} — {name}")
assert len(checks) == 30, len(checks)
if failed:
    raise SystemExit("Auditoria 30/30 falhou: " + ", ".join(failed))
print("PASS: Auditoria 30/30 — 30 de 30 critérios aprovados.")
