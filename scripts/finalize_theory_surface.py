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
}
for old, new in replacements.items():
    page = page.replace(old, new)

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

path.write_text(page, encoding="utf-8")
