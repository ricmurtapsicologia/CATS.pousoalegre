from __future__ import annotations

import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD_URL = "https://raw.githubusercontent.com/ricmurtapsicologia/cats-2025-4bbm-jf/main/index.html"


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "CATS-Portal-Builder/1.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8")


def inject_before(text: str, needle: str, fragment: str) -> str:
    if fragment.strip() in text:
        return text
    if needle not in text:
        raise RuntimeError(f"Ponto de inserção ausente: {needle!r}")
    return text.replace(needle, fragment + needle, 1)


def protect_precurso(text: str) -> str:
    if 'cats-auth.js?v=20260905-1' in text:
        return text
    text = text.replace('<html lang="pt-BR"', '<html lang="pt-BR" class="cats-auth-pending"', 1)
    auth = '''\n  <link data-cats-auth rel="stylesheet" href="https://ricmurtapsicologia.github.io/Curso-ATS/auth.css?v=20260905-2">\n  <link rel="stylesheet" href="cats-auth.css?v=20260905-1">\n  <script defer src="cats-auth.js?v=20260905-1"></script>\n  <script defer src="https://ricmurtapsicologia.github.io/Curso-ATS/auth.js?v=20260905-2"></script>\n'''
    return text.replace('</head>', auth + '</head>', 1)


def guard_legacy(text: str) -> str:
    marker = 'data-cats-legacy-guard="1"'
    if marker in text:
        return text
    guard = '''\n<script data-cats-legacy-guard="1">\n(()=>{\n  try{\n    const s=JSON.parse(sessionStorage.getItem('cats_pa_auth_v1')||'null');\n    if(!s||s.authenticated!==true||Date.now()>=Number(s.expiresAt||0)){location.replace('precurso.html');}\n  }catch{location.replace('precurso.html');}\n})();\n</script>\n'''
    return text.replace('<body', guard + '<body', 1)


def main() -> None:
    current_index = ROOT / "index.html"
    precurso = ROOT / "precurso.html"
    legacy = ROOT / "legacy.html"

    if not precurso.exists():
        original = current_index.read_text(encoding="utf-8")
        if "FORM_ACTION" not in original and "levantamento prévio" not in original.lower():
            raise RuntimeError("O index atual não parece ser a página canônica de pré-curso; preservação abortada.")
        precurso.write_text(protect_precurso(original), encoding="utf-8")
    else:
        precurso.write_text(protect_precurso(precurso.read_text(encoding="utf-8")), encoding="utf-8")

    if legacy.exists():
        legacy.write_text(guard_legacy(legacy.read_text(encoding="utf-8")), encoding="utf-8")

    source = fetch_text(OLD_URL)
    page = source

    replacements = [
        ("CATS 2025 – CBMMG | Aulas e Materiais (CATS VII 4º BBM/JF • Presencial)", "VIII CATS 2026 – CBMMG | Aulas e Materiais • Pouso Alegre"),
        ("CATS 2025 – CBMMG | CATS VII 4º BBM/JF (Presencial)", "VIII CATS 2026 – CBMMG | Pouso Alegre (Presencial)"),
        ("CATS VII • 4º BBM/JF", "VIII CATS • Pouso Alegre"),
        ("CATS VII 4º BBM/JF", "VIII CATS • Pouso Alegre"),
        ("CATS VII 4º BBM (Juiz de Fora) • Presencial", "VIII CATS • Pouso Alegre • Presencial"),
        ("CATS VII • 4º BBM - Juiz de Fora", "VIII CATS • Pouso Alegre"),
        ("CATS VII no 4º BBM Juiz de Fora", "VIII CATS em Pouso Alegre"),
        ("CATS VII", "VIII CATS"),
        ("CATS) VII", "CATS) VIII"),
        ("CATS 2025", "CATS 2026"),
        ("4º BBM/JF", "7ª Cia Ind • Pouso Alegre"),
        ("4º BBM (Juiz de Fora)", "7ª Cia Ind • Pouso Alegre"),
        ("4º BBM Juiz de Fora", "7ª Cia Ind - Pouso Alegre"),
        ("4º BBM - Juiz de Fora", "7ª Cia Ind - Pouso Alegre"),
        ("4º BBM", "7ª Cia Ind"),
        ("Juiz de Fora", "Pouso Alegre"),
        ("no 7ª Cia Ind - Pouso Alegre", "na 7ª Cia Ind, em Pouso Alegre"),
        ("https://ricmurtapsicologia.github.io/cats-2025-4bbm-jf/", "https://ricmurtapsicologia.github.io/CATS.pousoalegre/"),
        ("© 2025 Corpo de Bombeiros Militar de Minas Gerais", "© 2026 Corpo de Bombeiros Militar de Minas Gerais"),
        ("ats_progress_v6", "cats_pa_progress_v1"),
        ("ats_onboarded", "cats_pa_onboarded"),
        ("color:#text-3", "color:var(--text-3)"),
    ]
    for old, new in replacements:
        page = page.replace(old, new)

    page = page.replace('<html lang="pt-BR">', '<html lang="pt-BR" class="cats-auth-pending">', 1)
    page = page.replace('<meta charset="UTF-8" />', '<meta charset="UTF-8" />\n  <meta name="robots" content="noindex,nofollow,noarchive" />\n  <meta name="theme-color" content="#07101f" />\n  <meta name="cats-release" content="viii-cats-pa-2026-r2" />', 1)

    auth_head = '''\n  <link data-cats-auth rel="stylesheet" href="https://ricmurtapsicologia.github.io/Curso-ATS/auth.css?v=20260905-2" />\n  <link rel="stylesheet" href="cats-auth.css?v=20260905-1" />\n  <script defer src="cats-auth.js?v=20260905-1"></script>\n  <script defer src="https://ricmurtapsicologia.github.io/Curso-ATS/auth.js?v=20260905-2"></script>\n'''
    page = page.replace('</head>', auth_head + '</head>', 1)

    page = re.sub(r'\n\s*<!-- Tawk\.to -->\s*<script[^>]*>.*?</script>\s*', '\n', page, flags=re.S)

    page = page.replace(
        '<div class="hero-kpi"><small>Extras</small><strong>Prevenção + Projeto</strong></div>',
        '<div class="hero-kpi"><small>Período</small><strong>21–25/09/2026</strong></div>'
    )
    page = page.replace(
        '<div class="hero-kpi"><small>Formato</small><strong>Presencial</strong></div>',
        '<div class="hero-kpi"><small>Formato</small><strong>Presencial • 46 h/a</strong></div>'
    )

    coordinator_css = '''\n    .coordination-band{padding-top:18px;padding-bottom:0}\n    .coordination-card{display:flex;align-items:center;justify-content:space-between;gap:18px;padding:16px 18px;border:1px solid var(--stroke);border-left:4px solid #ffd166;border-radius:14px;background:var(--glass);box-shadow:var(--shadow)}\n    .coordination-card small{display:block;color:var(--text-3);font-weight:700;margin-bottom:4px}\n    .coordination-card strong{color:var(--text-1);font-size:1rem}\n    .coordination-card .coord-badge{display:inline-flex;align-items:center;gap:7px;padding:8px 11px;border-radius:999px;background:rgba(255,209,102,.14);color:#ffe08a;font-size:.85rem;font-weight:800;white-space:nowrap}\n    .resource-note{color:var(--text-3);font-size:.9rem}\n    .skip-link{position:fixed;left:12px;top:8px;z-index:10001;transform:translateY(-160%);padding:9px 12px;border-radius:10px;background:#fff;color:#07101f;font-weight:800}\n    .skip-link:focus{transform:translateY(0)}\n    @media(max-width:680px){.coordination-card{align-items:flex-start;flex-direction:column}.coordination-card .coord-badge{white-space:normal}}\n'''
    page = page.replace('</style>', coordinator_css + '\n  </style>', 1)

    page = page.replace('<body>', '<body>\n  <a class="skip-link" href="#conteudo">Pular para o conteúdo</a>', 1)
    page = page.replace('role="menubar"', '', 1).replace('role="menuitem"', '').replace('role="menuitem"', '')

    page = page.replace(
        '<a  href="#materiais">Materiais</a>' if '<a  href="#materiais">Materiais</a>' in page else '<a href="#materiais">Materiais</a>',
        '<a href="#materiais">Materiais</a>\n        <a href="precurso.html">Pré-curso</a>\n        <a href="#recursos">Biblioteca</a>',
        1,
    )

    coordinator = '''\n  <section class="container coordination-band" aria-label="Coordenação do curso">\n    <div class="coordination-card">\n      <div><small>Coordenação do VIII CATS 2026</small><strong>Capitão BM Lucas Antônio de Oliveira</strong></div>\n      <span class="coord-badge"><i class="ri-map-pin-2-line" aria-hidden="true"></i> Pouso Alegre • 7ª Cia Ind</span>\n    </div>\n  </section>\n'''
    page = page.replace('</header>', '</header>' + coordinator, 1)

    library_card = '''\n        <!-- RECURSO: Biblioteca ATS -->\n        <article class="card" id="recursos" data-module="biblioteca" data-title="Biblioteca ATS CBMMG">\n          <div class="media">\n            <span class="badge">Biblioteca</span>\n            <img loading="lazy" decoding="async" src="https://i.pinimg.com/736x/35/c5/64/35c5641e66c602835ca66dbcde48b5ff.jpg" alt="Biblioteca ATS CBMMG" />\n          </div>\n          <div class="content">\n            <h3>Biblioteca ATS CBMMG</h3>\n            <p>Ambiente complementar com materiais de apoio às aulas e à formação em Atendimento a Tentativas de Suicídio.</p>\n            <div class="actions">\n              <a class="btn small" target="_blank" rel="noopener" href="https://ricmurtapsicologia.github.io/Curso-ATS/"><i class="ri-book-open-line"></i> Acessar biblioteca</a>\n            </div>\n          </div>\n        </article>\n'''
    if 'Biblioteca ATS CBMMG' not in page:
        marker = '      </div>\n\n      <!-- Materiais -->'
        if marker not in page:
            raise RuntimeError('Fechamento da grade de aulas não localizado')
        page = page.replace(marker, library_card + '      </div>\n\n      <!-- Materiais -->', 1)

    if 'https://ricmurtapsicologia.github.io/Podcast-ATS-CBMMG/' not in page:
        raise RuntimeError('Podcast canônico ausente após migração')

    page = page.replace(
        '<div class="mat-links">',
        '<div class="mat-links">\n            <a href="precurso.html">Levantamento pré-curso e dados da turma</a>',
        1,
    )

    audit_gate = '''\n      <section class="container" id="avaliacao" aria-labelledby="avaliacaoTitle">\n        <details class="materials">\n          <summary id="avaliacaoTitle"><i class="ri-shield-check-line"></i> Avaliação do curso</summary>\n          <p class="resource-note" style="margin-top:12px">A avaliação será disponibilizada neste ambiente após vinculação da URL oficial.</p>\n        </details>\n      </section>\n'''
    page = page.replace('</main>', audit_gate + '\n  </main>', 1)

    remnants: list[str] = []
    if re.search(r'CATS\)? VII(?!I)', page):
        remnants.append('CATS VII')
    for term in ("Juiz de Fora", "4º BBM"):
        if term in page:
            remnants.append(term)
    if remnants:
        raise RuntimeError("Resquícios da edição anterior: " + ", ".join(remnants))

    current_index.write_text(page, encoding="utf-8")

    readme = '''# VIII CATS 2026 — Pouso Alegre

Portal de apoio às aulas presenciais do VIII Curso de Atendimento a Tentativas de Suicídio do CBMMG, em Pouso Alegre.

- Edição: VIII CATS 2026
- Período: 21–25/09/2026
- Carga horária: 46 h/a
- Coordenação: Capitão BM Lucas Antônio de Oliveira
- Unidade: 7ª Cia Ind — Pouso Alegre
- Aulas: preservadas da plataforma CATS anterior, sem alteração dos oito módulos
- Recursos: Biblioteca ATS CBMMG + podcast Girando a Ampulheta da Vida
- Pré-curso: `precurso.html`, com o formulário histórico/BDI-II preservado
- Autenticação: mesma base canônica de credenciais do Curso ATS e do podcast; sessão CATS isolada
- Auditorias: 30/30 e 90/90 obrigatórias antes da publicação
- Avaliação final: campo preparado; URL oficial ainda não localizada nas fontes conectadas

URL pública: https://ricmurtapsicologia.github.io/CATS.pousoalegre/
'''
    (ROOT / 'README.md').write_text(readme, encoding='utf-8')


if __name__ == "__main__":
    main()
