from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / "index.html").read_text(encoding="utf-8")

LESSONS = {
    1: "1ZYiAFZwrDE2i2zRpMg714cBqC4R-2OeH",
    2: "19n4VMAyYdaCjbYYIH8eZB3duNC1FkSF7",
    3: "1GuEU435vhorxZt42dAEurX2mVopFpFEz",
    4: "1kiKcOToIu1tKJRzWFVmARJYPP3N4J0S_",
    5: "1AasaqZYAqBZJtoNCOh8e6TyBeb_11Fm-",
    6: "1SNvZyrliydPk6iTkwAKhZ66FZ9AO7ac9",
    7: "1hx-CVfbGbCzen1Ygc0-9lTHm81xVcaxw",
    8: "1lVMb2TMiex4Z48_y1S2GA_mnTTgogS6u",
}
CARD_IMAGES = {
    5: "https://i.pinimg.com/736x/aa/88/6a/aa886a6b4cf5d8b3d7148fe09c999113.jpg",
    6: "https://i.pinimg.com/736x/54/70/f1/5470f1732df396897fe4d27575180b50.jpg",
}

errors: list[str] = []

def require(ok: bool, message: str) -> None:
    if not ok:
        errors.append(message)

# O arquivo versionado já deve estar no estado final; este script não o modifica.
for forbidden in (
    "Doze unidades formativas",
    "12 unidades formativas",
    "Recohecimento",
    "humanizada,técnicas",
    "estratégias de autoregulação",
    "docs.google.com/presentation/d/",
    "baseEmbed =",
    "viewUrl   =",
    "openExternal",
    "practice-note",
    'class="card practice-card"',
):
    require(forbidden not in PAGE, f"resíduo legado presente: {forbidden}")

require(PAGE.count('data-module="') >= 8, "cards curriculares ausentes")
require("Reconhecimento do timing, contenção física humanizada e técnicas de salvamento com segurança." in PAGE,
        "copy canônica da Aula 6 ausente")
require("estratégias de autorregulação e suporte." in PAGE,
        "copy canônica de autorregulação ausente")

for module, source_id in LESSONS.items():
    pdf_rel = f"assets/lessons/aula-0{module}.pdf"
    pdf = ROOT / pdf_rel
    require(pdf.is_file(), f"PDF da Aula {module} ausente")
    if pdf.is_file():
        require(pdf.stat().st_size > 10_000, f"PDF da Aula {module} pequeno/inválido")
        require(pdf.read_bytes()[:5] == b"%PDF-", f"Aula {module} não é PDF")
    require(PAGE.count(f'data-module="{module}"') == 1, f"Aula {module} duplicada/ausente")
    require(PAGE.count(f'href="{pdf_rel}"') == 1, f"Aula {module} não aponta unicamente para PDF local")
    require(PAGE.count(f'data-slide-url="{pdf_rel}"') == 1, f"data-slide-url da Aula {module} inconsistente")
    require(source_id in PAGE, f"rastreabilidade da fonte da Aula {module} ausente")

for module, image in CARD_IMAGES.items():
    card = re.search(rf'<article class="card" data-module="{module}".*?</article>', PAGE, re.S)
    require(bool(card and image in card.group(0)), f"imagem canônica da Aula {module} ausente")

require("/* ===== Viewer local — somente fechamento ===== */" in PAGE,
        "viewer local canônico não materializado")
require("O conteúdo permanece dentro do portal." in PAGE,
        "copy canônica do viewer ausente")

if errors:
    raise SystemExit("SOURCE_CANONICAL_DRIFT_FAIL:\n- " + "\n- ".join(errors))

print("SOURCE_CANONICAL_DRIFT_PASS: index.html já está materializado; nenhuma mutação executada.")
