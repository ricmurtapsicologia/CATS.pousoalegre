from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "index.html"
page = path.read_text(encoding="utf-8")

replacements = {
    "Doze unidades formativas:": "Oito aulas teóricas:",
    "12 unidades formativas": "8 aulas teóricas",
    "com 12 unidades formativas": "com 8 aulas teóricas",
    "12 unidades": "8 aulas",
    "Doze unidades": "Oito aulas",
    "Recohecimento do timing, contenção física humanizada,técnicas de salvamento com segurança.":
        "Reconhecimento do timing, contenção física humanizada e técnicas de salvamento com segurança.",
    "estratégias de autoregulação e suporte.": "estratégias de autorregulação e suporte.",
}
for old, new in replacements.items():
    page = page.replace(old, new)

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

card_pattern = re.compile(
    r'<article class="card" data-module="([1-8])".*?</article>', re.S
)


def normalize_lesson_card(match: re.Match[str]) -> str:
    module = int(match.group(1))
    block = match.group(0)
    pdf = f"assets/lessons/aula-0{module}.pdf"
    anchor = (
        f'<a class="btn small open-slide" data-slide-id="{LESSONS[module]}" '
        f'data-slide-url="{pdf}" href="{pdf}">Acessar aula</a>'
    )

    # Remove dois caminhos legados concorrentes: link direto ao Google Slides e
    # aviso de “material não publicado”. Todas as oito aulas possuem PDF local.
    block, changed = re.subn(
        r'<a class="btn small open-slide"[^>]*>Acessar aula</a>|'
        r'<span class="practice-note">.*?</span>',
        anchor,
        block,
        count=1,
        flags=re.S,
    )
    if changed != 1:
        raise SystemExit(f"Falha: não foi possível normalizar o acesso da Aula {module}")

    if module in CARD_IMAGES:
        block, image_changed = re.subn(
            r'(<img\b[^>]*\bsrc=")[^"]+("[^>]*>)',
            rf'\g<1>{CARD_IMAGES[module]}\g<2>',
            block,
            count=1,
            flags=re.S,
        )
        if image_changed != 1:
            raise SystemExit(f"Falha: imagem da Aula {module} não localizada")

    return block


page, card_count = card_pattern.subn(normalize_lesson_card, page)
if card_count != 8:
    raise SystemExit(f"Falha: esperados 8 cards teóricos, encontrados {card_count}")

# O viewer antigo construía embeds do Google Slides e competia com o viewer
# canônico de PDFs locais. Mantemos apenas o controle de fechamento; a abertura
# e a origem do conteúdo pertencem a presentation-originals.js.
controls = '''<div class="controls">
        <button id="slidesClose" class="btn ghost" aria-label="Encerrar"><i class="ri-close-circle-line"></i> Encerrar</button>
        <span class="tip">Use o visualizador para navegar pela aula. O conteúdo permanece dentro do portal.</span>
      </div>'''
page, controls_count = re.subn(
    r'<div class="controls">.*?</div>\s*<div class="frame-wrap">',
    controls + '\n      <div class="frame-wrap">',
    page,
    count=1,
    flags=re.S,
)
if controls_count != 1:
    raise SystemExit("Falha: controles do viewer não foram normalizados")

viewer_runtime = '''/* ===== Viewer local — somente fechamento ===== */
    const slidesViewer = document.getElementById('slidesViewer');
    const slidesFrame  = document.getElementById('slidesFrame');
    const slidesClose  = document.getElementById('slidesClose');
    const closeX       = document.getElementById('closeX');

    function closeViewer(){
      slidesFrame.src='about:blank';
      if(slidesViewer.open){ slidesViewer.close(); }
      slidesViewer.removeAttribute('open');
      document.documentElement.style.overflow='';
    }

    [slidesClose, closeX].forEach(b=> b?.addEventListener('click', closeViewer));
    slidesViewer.addEventListener('click', e=>{ if(e.target===slidesViewer) closeViewer(); });

    '''
page, viewer_count = re.subn(
    r'/\* ===== Viewer \(Prev/Next funcionais\) ===== \*/.*?(?=/\* ===== CVV ===== \*/)',
    viewer_runtime,
    page,
    count=1,
    flags=re.S,
)
if viewer_count != 1:
    raise SystemExit("Falha: runtime legado do Google Slides não foi removido")

# A superfície curricular não pode sugerir presença de práticas como disciplinas.
for forbidden in (
    'data-title="Prática de conversação em ATS"',
    'data-title="Prática em ATS: risco de incêndio/explosão"',
    'data-title="Prática em ATS: risco de precipitação"',
    'data-title="Prática em ATS: risco de afogamento"',
    'class="card practice-card"',
):
    if forbidden in page:
        raise SystemExit(f"Falha: disciplina prática permaneceu na superfície final: {forbidden}")

if "12 unidades formativas" in page or "Doze unidades formativas" in page:
    raise SystemExit("Falha: terminologia de 12 unidades permaneceu na página final")

# Contrato final: aula não depende de permissão do Drive/Slides.
if "docs.google.com/presentation/d/" in page:
    raise SystemExit("Falha: link legado do Google Slides permaneceu na superfície curricular")
if "baseEmbed =" in page or "viewUrl   =" in page or "openExternal" in page:
    raise SystemExit("Falha: runtime legado do Google Slides permaneceu no viewer")
if "practice-note" in page:
    raise SystemExit("Falha: aviso legado de material indisponível permaneceu nos cards")

for module, source_id in LESSONS.items():
    pdf = ROOT / f"assets/lessons/aula-0{module}.pdf"
    if not pdf.is_file() or pdf.stat().st_size < 10_000:
        raise SystemExit(f"Falha: PDF local da Aula {module} ausente ou inválido")
    if pdf.read_bytes()[:5] != b"%PDF-":
        raise SystemExit(f"Falha: ativo da Aula {module} não é PDF")
    href = f'href="assets/lessons/aula-0{module}.pdf"'
    if page.count(href) != 1 or source_id not in page:
        raise SystemExit(f"Falha: rastreabilidade/acesso local da Aula {module} inconsistente")

for module, image in CARD_IMAGES.items():
    card = re.search(
        rf'<article class="card" data-module="{module}".*?</article>', page, re.S
    )
    if not card or image not in card.group(0):
        raise SystemExit(f"Falha: imagem canônica da Aula {module} não aplicada")

path.write_text(page, encoding="utf-8")
print("PASS: superfície consolidada — 8 aulas locais, sem runtime concorrente do Google Slides.")
