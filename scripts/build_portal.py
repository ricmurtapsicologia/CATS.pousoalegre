from __future__ import annotations

import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD_URL = "https://raw.githubusercontent.com/ricmurtapsicologia/cats-2025-4bbm-jf/main/index.html"

HOURS = {1: "4 h/a", 2: "2 h/a", 3: "2 h/a", 4: "2 h/a", 5: "2 h/a", 6: "2 h/a", 7: "4 h/a", 8: "2 h/a", 9: "6 h/a", 10: "8 h/a", 11: "2 h/a", 12: "2 h/a"}


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "CATS-Portal-Builder/1.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8")


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


def replace_onboarding(page: str) -> str:
    onboarding = '''  <!-- Onboarding -->
  <div id="onboard" role="dialog" aria-modal="true" aria-labelledby="ob-title">
    <div class="onboard-card" role="document">
      <h3 id="ob-title">Boas-vindas ao VIII CATS 2026</h3>
      <div class="onboard-welcome">
        <p>Seja bem-vindo(a) ao VIII Curso de Atendimento a Tentativas de Suicídio. Este ambiente foi organizado para apoiar sua aprendizagem sem substituir a experiência presencial, a supervisão dos instrutores e a segurança das práticas.</p>
        <p>Ao longo da semana, avance no seu ritmo pela trilha, consulte somente o que precisar e use os materiais como apoio para transformar conhecimento em atuação técnica, segura e humanizada.</p>
        <span class="onboard-signature">Capitão BM Lucas Antônio de Oliveira<br>Coordenador do VIII CATS 2026</span>
      </div>
      <ul class="onboard-list">
        <li>As unidades ficam compactas no celular; toque em <b>Ver conteúdo</b> para abrir uma de cada vez.</li>
        <li>Materiais, vídeos e avaliação permanecem fechados até você acionar o respectivo botão.</li>
        <li>Seu progresso fica salvo neste navegador e pode ser atualizado ao concluir cada unidade.</li>
      </ul>
      <div class="o-actions">
        <button class="btn ghost" id="ob-skip"><i class="ri-skip-forward-mini-fill"></i> Agora não</button>
        <button class="btn" id="ob-next">Entrar na trilha</button>
      </div>
    </div>
  </div>'''
    pattern = r'  <!-- Onboarding -->\s*<div id="onboard".*?</div>\s*</div>\s*\n\s*<!-- Navbar -->'
    updated, count = re.subn(pattern, onboarding + '\n\n  <!-- Navbar -->', page, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError("Onboarding canônico não localizado")
    return updated


def transform_materials(page: str) -> str:
    pattern = r'<div id="materiais" style="margin-top:18px">\s*<details class="materials">\s*<summary>.*?</summary>\s*(<div class="mat-links">.*?</div>)\s*</details>\s*</div>'
    match = re.search(pattern, page, flags=re.S)
    if not match:
        raise RuntimeError("Pasta de materiais não localizada")
    links = match.group(1)
    replacement = f'''<div id="materiais" style="margin-top:18px">
        <div class="folder">
          <button class="folder-toggle" type="button" aria-expanded="false" aria-controls="materialsPanel">
            <span><i class="ri-archive-2-line"></i> Materiais complementares</span><i class="ri-arrow-down-s-line" aria-hidden="true"></i>
          </button>
          <div class="folder-panel" id="materialsPanel" hidden>
            {links}
          </div>
        </div>
      </div>'''
    return page[:match.start()] + replacement + page[match.end():]


def transform_videos(page: str) -> str:
    old = '''      <div class="section-head">
        <div>
          <h2><i class="ri-movie-line"></i> Vídeos Selecionados</h2>
          <p>Repertório de apoio para aprofundar conceitos e práticas.</p>
        </div>
      </div>
      <div class="grid video-grid">'''
    new = '''      <div class="folder">
        <button class="folder-toggle" id="videosToggle" type="button" aria-expanded="false" aria-controls="videosGrid">
          <span><i class="ri-movie-line"></i> Vídeos de apoio</span><i class="ri-arrow-down-s-line" aria-hidden="true"></i>
        </button>
        <div class="grid video-grid" id="videosGrid" hidden>'''
    if old not in page:
        raise RuntimeError("Seção de vídeos não localizada")
    page = page.replace(old, new, 1)
    marker = '''      </div>
    </section>
  
'''
    pos = page.find(marker, page.find('id="videosGrid"'))
    if pos == -1:
        raise RuntimeError("Fechamento da pasta de vídeos não localizado")
    page = page[:pos] + '''        </div>
      </div>
    </section>
  
''' + page[pos + len(marker):]
    return page


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

    page = fetch_text(OLD_URL)

    replacements = [
        ("CATS 2025 – CBMMG | Aulas e Materiais (CATS VII 4º BBM/JF • Presencial)", "VIII CATS 2026 – CBMMG | Aulas e práticas • Pouso Alegre"),
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
        ("ats_progress_v6", "cats_pa_progress_v2"),
        ("ats_onboarded", "cats_pa_onboarded_v2"),
        ("color:#text-3", "color:var(--text-3)"),
        ("Oito módulos:", "Doze unidades formativas:"),
        ("com oito módulos:", "com 12 unidades formativas:"),
    ]
    for old, new in replacements:
        page = page.replace(old, new)

    page = page.replace('<html lang="pt-BR">', '<html lang="pt-BR" class="cats-auth-pending">', 1)
    page = page.replace('<meta charset="UTF-8" />', '<meta charset="UTF-8" />\n  <meta name="robots" content="noindex,nofollow,noarchive" />\n  <meta name="theme-color" content="#07101f" />\n  <meta name="cats-release" content="viii-cats-pa-2026-r3" />', 1)

    auth_head = '''\n  <link data-cats-auth rel="stylesheet" href="https://ricmurtapsicologia.github.io/Curso-ATS/auth.css?v=20260905-2" />\n  <link rel="stylesheet" href="cats-auth.css?v=20260905-1" />\n  <link rel="stylesheet" href="portal-ui.css?v=20260905-1" />\n  <script defer src="cats-auth.js?v=20260905-1"></script>\n  <script defer src="https://ricmurtapsicologia.github.io/Curso-ATS/auth.js?v=20260905-2"></script>\n  <script defer src="portal-ui.js?v=20260905-1"></script>\n'''
    page = page.replace('</head>', auth_head + '</head>', 1)
    page = re.sub(r'\n\s*<!-- Tawk\.to -->\s*<script[^>]*>.*?</script>\s*', '\n', page, flags=re.S)

    coordinator_css = '''\n    .coordination-band{padding-top:18px;padding-bottom:0}\n    .coordination-card{display:flex;align-items:center;justify-content:space-between;gap:18px;padding:16px 18px;border:1px solid var(--stroke);border-left:4px solid #ffd166;border-radius:14px;background:var(--glass);box-shadow:var(--shadow)}\n    .coordination-card small{display:block;color:var(--text-3);font-weight:700;margin-bottom:4px}\n    .coordination-card strong{color:var(--text-1);font-size:1rem}\n    .coordination-card .coord-badge{display:inline-flex;align-items:center;gap:7px;padding:8px 11px;border-radius:999px;background:rgba(255,209,102,.14);color:#ffe08a;font-size:.85rem;font-weight:800;white-space:nowrap}\n    .resource-note{color:var(--text-3);font-size:.9rem}\n    .skip-link{position:fixed;left:12px;top:8px;z-index:10001;transform:translateY(-160%);padding:9px 12px;border-radius:10px;background:#fff;color:#07101f;font-weight:800}\n    .skip-link:focus{transform:translateY(0)}\n'''
    page = page.replace('</style>', coordinator_css + '\n  </style>', 1)

    page = replace_onboarding(page)
    page = page.replace('<body>', '<body>\n  <a class="skip-link" href="#conteudo">Pular para o conteúdo</a>', 1)
    page = page.replace('role="menubar"', '').replace('role="menuitem"', '')

    page = page.replace(
        '<a  href="#materiais">Materiais</a>' if '<a  href="#materiais">Materiais</a>' in page else '<a href="#materiais">Materiais</a>',
        '<a href="#materiais">Materiais</a>\n        <a href="precurso.html">Pré-curso</a>\n        <a href="#recursos">Recursos</a>',
        1,
    )
    page = page.replace(
        '<button class="theme-toggle" id="themeBtn" aria-pressed="false" title="Alternar tema">',
        '<button id="mobileMenuBtn" type="button" aria-expanded="false" aria-controls="mainNavLinks" title="Abrir menu"><i class="ri-menu-line" aria-hidden="true"></i><span class="sr-only">Menu</span></button>\n        <button class="theme-toggle" id="themeBtn" aria-pressed="false" title="Alternar tema">',
        1,
    )
    page = page.replace('<div class="nav-links" >', '<div class="nav-links" id="mainNavLinks">', 1)

    hero_old = '<p>Conteúdo de apoio complementar ao curso presencial do VIII CATS, com foco em <b>comunicação dissuasiva técnico-humanizada</b>, <b>abordagem tática especializada</b>, <b>gestão do atendimento a tentativas de suicídio</b> e <b>prevenção em saúde mental na caserna</b>.</p>'
    hero_new = '''<p>Seu ambiente de apoio ao VIII CATS: aulas, práticas presenciais e recursos essenciais, organizados para consulta simples ao longo da semana.</p>
        <div class="mobile-course-info">
          <button class="btn ghost" id="courseInfoToggle" type="button" aria-expanded="false" aria-controls="mobileCoursePanel"><i class="ri-information-line"></i> <span>Ver informações do curso</span></button>
          <div class="mobile-course-panel" id="mobileCoursePanel" hidden>
            <div class="mobile-course-meta">
              <div><small>Carga horária</small><strong>46 h/a</strong></div>
              <div><small>Período</small><strong>21–25/09/2026</strong></div>
              <div><small>Trilha</small><strong>12 unidades</strong></div>
              <div><small>Local</small><strong>Pouso Alegre</strong></div>
            </div>
            <div class="mobile-progress"><i class="ri-bar-chart-box-line"></i> Progresso: <b id="mobileProgressLabel">0</b>/12</div>
          </div>
        </div>'''
    if hero_old not in page:
        raise RuntimeError("Texto principal do hero não localizado")
    page = page.replace(hero_old, hero_new, 1)

    page = page.replace('<div class="hero-kpi"><small>Módulos</small><strong id="kpi-modulos">8 módulos</strong></div>', '<div class="hero-kpi"><small>Trilha</small><strong id="kpi-modulos">12 unidades</strong></div>', 1)
    page = page.replace('<span><b id="progressLabel">0</b>/8</span>', '<span><b id="progressLabel">0</b>/12</span>', 1)
    page = page.replace(
        '<div class="hero-kpi"><small>Extras</small><strong>Prevenção + Projeto</strong></div>',
        '<div class="hero-kpi"><small>Período</small><strong>21–25/09/2026</strong></div>', 1,
    )
    page = page.replace(
        '<div class="hero-kpi"><small>Formato</small><strong>Presencial</strong></div>',
        '<div class="hero-kpi"><small>Formato</small><strong>Presencial • 46 h/a</strong></div>', 1,
    )

    coordinator = '''\n  <section class="container coordination-band" aria-label="Coordenação do curso">\n    <div class="coordination-card">\n      <div><small>Coordenação do VIII CATS 2026</small><strong>Capitão BM Lucas Antônio de Oliveira</strong></div>\n      <span class="coord-badge"><i class="ri-map-pin-2-line" aria-hidden="true"></i> Pouso Alegre • 7ª Cia Ind</span>\n    </div>\n  </section>\n'''
    page = page.replace('</header>', '</header>' + coordinator, 1)

    page = page.replace('<h2><i class="ri-book-2-line"></i> Aulas</h2>', '<h2><i class="ri-route-line"></i> Trilha do curso</h2>', 1)
    old_intro = '<p>O <b>VIII CATS</b> aborda <b>comunicação dissuasiva</b>, <b>abordagem técnica</b> e <b>gestão de ATS</b>, com base em <i>“Girando a Ampulheta da Vida”</i>. O curso integra <b>psicopatologia aplicada</b> e <b>prevenção em saúde mental na caserna</b>, com foco na atuação segura e humanizada.</p>'
    new_intro = '<p>A trilha abaixo reproduz as 12 unidades formativas previstas no Plano de Ensino CATS 2026: oito unidades teóricas e quatro práticas presenciais. Avaliações permanecem em seção própria.</p>'
    page = page.replace(old_intro, new_intro, 1)

    theory_break = '''        <div class="course-break"><span>Fundamentos e aplicação</span><h3>Aulas teóricas</h3><p>Conteúdo doutrinário e decisório que sustenta a atuação nas práticas.</p></div>\n'''
    page = page.replace('        <!-- 1 -->', theory_break + '        <!-- 1 -->', 1)

    for n in range(1, 8):
        page = page.replace(f'data-module="{n}" data-title=', f'data-module="{n}" data-hours="{HOURS[n]}" data-title=', 1)
        page = page.replace(f'<span class="badge">Módulo {n}</span>', f'<span class="badge">Unidade {n}</span>', 1)
        page = page.replace(f'<h3>Módulo {n}:', f'<h3>Unidade {n}:', 1)

    prevention_match = re.search(r'<article class="card" data-module="8".*?</article>', page, flags=re.S)
    if not prevention_match:
        raise RuntimeError("Unidade de prevenção legada não localizada")
    prevention = prevention_match.group(0)
    prevention = prevention.replace('data-module="8"', 'data-module="12" data-hours="2 h/a"', 1)
    prevention = prevention.replace('data-title="Prevenção"', 'data-title="Prevenção ao comportamento suicida"', 1)
    prevention = prevention.replace('<span class="badge">Módulo 8</span>', '<span class="badge">Unidade 12</span>', 1)
    prevention = prevention.replace('<h3>Módulo 8: Prevenção</h3>', '<h3>Unidade 12: Prevenção ao comportamento suicida</h3>', 1)
    page = page[:prevention_match.start()] + prevention + page[prevention_match.end():]

    practice_cards = '''        <div class="course-break"><span>Treino supervisionado</span><h3>Práticas presenciais</h3><p>As quatro práticas previstas na malha oficial aparecem na sequência e são realizadas com briefing, supervisão e debriefing.</p></div>

        <article class="card practice-card" data-module="8" data-hours="2 h/a" data-title="Prática de conversação em ATS">
          <div class="content"><h3>Unidade 8: Prática de conversação em ATS</h3><p>Role-play, simulação controlada, escuta, validação, manejo do silêncio e feedback formativo.</p><div class="actions"><span class="practice-note"><i class="ri-team-line"></i> Atividade presencial supervisionada.</span><button class="btn small ghost objectives">Ver objetivos</button><button class="btn small complete">Concluir unidade</button></div></div>
        </article>
        <article class="card practice-card" data-module="9" data-hours="6 h/a" data-title="Prática em ATS: risco de incêndio/explosão">
          <div class="content"><h3>Unidade 9: Risco de incêndio/explosão</h3><p>Estação prática controlada com foco em segurança da cena, integração de recursos e condutas proporcionais ao risco.</p><div class="actions"><span class="practice-note"><i class="ri-fire-line"></i> Atividade presencial supervisionada.</span><button class="btn small ghost objectives">Ver objetivos</button><button class="btn small complete">Concluir unidade</button></div></div>
        </article>
        <article class="card practice-card" data-module="10" data-hours="8 h/a" data-title="Prática em ATS: risco de precipitação">
          <div class="content"><h3>Unidade 10: Risco de precipitação</h3><p>Estação prática controlada para decisão, segurança, comunicação e integração com técnicas de salvamento em altura.</p><div class="actions"><span class="practice-note"><i class="ri-building-line"></i> Atividade presencial supervisionada.</span><button class="btn small ghost objectives">Ver objetivos</button><button class="btn small complete">Concluir unidade</button></div></div>
        </article>
        <article class="card practice-card" data-module="11" data-hours="2 h/a" data-title="Prática em ATS: risco de afogamento">
          <div class="content"><h3>Unidade 11: Risco de afogamento</h3><p>Estação prática controlada com integração entre ATS, salvamento aquático, segurança e comunicação.</p><div class="actions"><span class="practice-note"><i class="ri-water-flash-line"></i> Atividade presencial supervisionada.</span><button class="btn small ghost objectives">Ver objetivos</button><button class="btn small complete">Concluir unidade</button></div></div>
        </article>

        <div class="course-break"><span>Fechamento preventivo</span><h3>Prevenção</h3><p>Última unidade formativa antes das avaliações previstas na malha.</p></div>
'''
    if '        <!-- 8 -->' not in page:
        raise RuntimeError("Marcador da antiga unidade 8 não localizado")
    page = page.replace('        <!-- 8 -->', practice_cards + '        <!-- 12 -->', 1)

    # Unidades teóricas sem material público: não rotular como manutenção.
    page = page.replace('<button class="btn small" disabled title="Em manutenção"><i class="ri-tools-line"></i> Em manutenção</button>', '<span class="practice-note"><i class="ri-presentation-line"></i> Conteúdo ministrado presencialmente; material não publicado neste portal.</span>', 3)

    resource_break = '''        <div class="course-break" id="recursos"><span>Consulta opcional</span><h3>Recursos complementares</h3><p>Biblioteca e podcast ficam fora da contagem curricular e podem ser acessados quando úteis.</p></div>\n'''
    page = page.replace('        <!-- PROJETO: Girando a Ampulheta da Vida -->', resource_break + '        <!-- PROJETO: Girando a Ampulheta da Vida -->', 1)
    page = page.replace('<article class="card" data-module="proj"', '<article class="card resource-card" data-module="proj"', 1)

    library_card = '''\n        <!-- RECURSO: Biblioteca ATS -->\n        <article class="card resource-card" data-module="biblioteca" data-title="Biblioteca ATS CBMMG">\n          <div class="media">\n            <span class="badge">Biblioteca</span>\n            <img loading="lazy" decoding="async" src="https://i.pinimg.com/736x/35/c5/64/35c5641e66c602835ca66dbcde48b5ff.jpg" alt="Biblioteca ATS CBMMG" />\n          </div>\n          <div class="content">\n            <h3>Biblioteca ATS CBMMG</h3>\n            <p>Materiais de apoio às aulas e à formação em Atendimento a Tentativas de Suicídio.</p>\n            <div class="actions"><a class="btn small" target="_blank" rel="noopener" href="https://ricmurtapsicologia.github.io/Curso-ATS/"><i class="ri-book-open-line"></i> Acessar biblioteca</a></div>\n          </div>\n        </article>\n'''
    marker = '      </div>\n\n      <!-- Materiais -->'
    if marker not in page:
        raise RuntimeError('Fechamento da grade de aulas não localizado')
    page = page.replace(marker, library_card + '      </div>\n\n      <!-- Materiais -->', 1)

    if 'https://ricmurtapsicologia.github.io/Podcast-ATS-CBMMG/' not in page:
        raise RuntimeError('Podcast canônico ausente após migração')

    page = page.replace('<div class="mat-links">', '<div class="mat-links">\n            <a href="precurso.html">Levantamento pré-curso e dados da turma</a>', 1)
    page = transform_materials(page)
    page = transform_videos(page)

    audit_gate = '''\n      <section class="container" id="avaliacao" aria-label="Avaliação do curso">\n        <div class="folder">\n          <button class="folder-toggle" type="button" aria-expanded="false" aria-controls="assessmentPanel"><span><i class="ri-shield-check-line"></i> Avaliação do curso</span><i class="ri-arrow-down-s-line" aria-hidden="true"></i></button>\n          <div class="folder-panel" id="assessmentPanel" hidden><p class="resource-note" style="margin-top:12px">A malha prevê prova teórica (2 h/a) e prova prática (6 h/a). O acesso à prova on-line será inserido aqui somente quando a URL oficial estiver vinculada.</p></div>\n        </div>\n      </section>\n'''
    page = page.replace('</main>', audit_gate + '\n  </main>', 1)

    objectives = '''const objectivesMap = {
      "1":['Compreender conceitos, continuum e multicausalidade do comportamento suicida.','Reconhecer fatores de risco e de proteção em perspectiva operacional.'],
      "2":['Reconhecer sinais psicopatológicos relevantes ao atendimento sem assumir diagnóstico clínico formal.','Relacionar alterações de julgamento e risco à segurança da cena.'],
      "3":['Organizar a cena e estabelecer condições iniciais de segurança.','Aplicar fundamentos gerais da Abordagem Técnica em ATS.'],
      "4":['Aplicar aproximação, silêncio inicial, apresentação pessoal e manejo do diálogo.','Adequar condutas aos aspectos específicos do cenário.'],
      "5":['Aplicar escuta, vínculo, perguntas, validação e comunicação dissuasiva.','Reconhecer condutas comunicacionais a evitar.'],
      "6":['Diferenciar Abordagem Técnica e noções de Abordagem Tática.','Reconhecer critérios gerais de transição conforme risco e segurança.'],
      "7":['Organizar comando, funções e integração de recursos.','Conduzir documentação, encerramento e encaminhamento de forma segura.'],
      "8":['Executar conversação supervisionada em role-play.','Receber e aplicar feedback formativo sobre comunicação e postura.'],
      "9":['Atuar em cenário controlado de incêndio/explosão.','Integrar segurança, comunicação e recursos especializados.'],
      "10":['Atuar em cenário controlado de precipitação.','Integrar ATS e segurança em ambiente de altura.'],
      "11":['Atuar em cenário controlado de afogamento.','Integrar ATS e salvamento aquático com segurança.'],
      "12":['Adotar prevenção e comunicação responsável.','Realizar encaminhamento e cuidado com a equipe após a ocorrência.'],
      "proj":['Ampliar aprendizagem com podcasts temáticos.','Conectar teoria e prática por conteúdos complementares.']
    };'''
    page, count = re.subn(r'const objectivesMap = \{.*?\n    \};', objectives, page, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError("Mapa de objetivos não localizado")

    page = page.replace('/* ===== Termômetro (8 módulos) ===== */', '/* ===== Progresso das 12 unidades formativas ===== */', 1)
    page = page.replace('const TOTAL = 8;', 'const TOTAL = 12;', 1)
    page = page.replace("['1','2','3','4','5','6','7','8'].includes(String(n))", "['1','2','3','4','5','6','7','8','9','10','11','12'].includes(String(n))", 1)
    page = page.replace("label.textContent = done;", "label.textContent = done; const mobileLabel=document.getElementById('mobileProgressLabel'); if(mobileLabel) mobileLabel.textContent=done;", 1)

    remnants: list[str] = []
    if re.search(r'CATS\)? VII(?!I)', page):
        remnants.append('CATS VII')
    for term in ("Juiz de Fora", "4º BBM"):
        if term in page:
            remnants.append(term)
    if remnants:
        raise RuntimeError("Resquícios da edição anterior: " + ", ".join(remnants))
    if page.count('data-module="') < 14:
        raise RuntimeError("Trilha curricular incompleta após construção")
    if 'details class="materials"' in page:
        raise RuntimeError("Cascata nativa antiga permaneceu na página")

    current_index.write_text(page, encoding="utf-8")

    readme = '''# VIII CATS 2026 — Pouso Alegre

Portal de apoio às aulas presenciais do VIII Curso de Atendimento a Tentativas de Suicídio do CBMMG, em Pouso Alegre.

- Edição: VIII CATS 2026
- Período: 21–25/09/2026
- Carga horária: 46 h/a
- Coordenação: Capitão BM Lucas Antônio de Oliveira
- Unidade executora: 7ª Cia Ind / 6º COB
- Malha exibida: 12 unidades formativas do Plano de Ensino CATS 2026
- Teóricas: unidades 1–7 e 12
- Práticas: conversação, incêndio/explosão, precipitação e afogamento (unidades 8–11)
- Avaliações: prova teórica (2 h/a) e prova prática (6 h/a), em seção própria
- Recursos extras: Biblioteca ATS CBMMG + podcast Girando a Ampulheta da Vida
- UX: mobile-first, progressive disclosure, cascatas por clique e uma unidade aberta por vez no celular
- Autenticação: mesma base canônica de credenciais do Curso ATS e do podcast; sessão CATS isolada
- Auditorias: 30/30 e 90/90 obrigatórias antes da publicação

Fontes curriculares canônicas usadas na reconciliação: Plano de Ensino CATS 2026 e QTS CATS 2026.
URL pública: https://ricmurtapsicologia.github.io/CATS.pousoalegre/
'''
    (ROOT / 'README.md').write_text(readme, encoding='utf-8')


if __name__ == "__main__":
    main()
