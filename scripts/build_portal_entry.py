from __future__ import annotations

import re
from pathlib import Path

import build_portal as portal


ROOT = Path(__file__).resolve().parents[1]


def transform_videos(page: str) -> str:
    """Converte a seção legada de vídeos em pasta fechada por botão."""
    section_start = page.find('<section id="videos" class="container">')
    if section_start < 0:
        raise RuntimeError("Seção de vídeos não localizada")
    section_end = page.find('</section>', section_start)
    if section_end < 0:
        raise RuntimeError("Fechamento da seção de vídeos não localizado")
    section_end += len('</section>')

    section = page[section_start:section_end]
    grid_marker = '<div class="grid video-grid">'
    grid_pos = section.find(grid_marker)
    if grid_pos < 0:
        raise RuntimeError("Grade de vídeos não localizada")

    section_head = section[:grid_pos]
    head_start = section_head.find('<div class="section-head">')
    if head_start < 0:
        raise RuntimeError("Cabeçalho da seção de vídeos não localizado")

    folder_open = '''<div class="folder">
        <button class="folder-toggle" id="videosToggle" type="button" aria-expanded="false" aria-controls="videosGrid">
          <span><i class="ri-movie-line"></i> Vídeos de apoio</span><i class="ri-arrow-down-s-line" aria-hidden="true"></i>
        </button>
        <div class="grid video-grid" id="videosGrid" hidden>'''

    section_prefix = section[:head_start]
    section = section_prefix + folder_open + section[grid_pos + len(grid_marker):]
    section_close = section.rfind('</section>')
    last_div = section.rfind('</div>', 0, section_close)
    if last_div < 0:
        raise RuntimeError("Fechamento da grade de vídeos não localizado")
    insert_at = last_div + len('</div>')
    section = section[:insert_at] + '\n      </div>' + section[insert_at:]
    return page[:section_start] + section + page[section_end:]


def keep_theory_only() -> None:
    """Corrige a superfície curricular: oito aulas teóricas, todas com card ilustrado.

    As práticas continuam pertencendo ao curso presencial, porém não aparecem como
    disciplinas/cards nesta página, conforme a regra editorial do portal.
    """
    path = ROOT / "index.html"
    page = path.read_text(encoding="utf-8")

    # Remove a faixa e os quatro cards de práticas criados pelo construtor-base.
    pattern = (
        r'\s*<div class="course-break"><span>Treino supervisionado</span>'
        r'.*?<div class="course-break"><span>Fechamento preventivo</span>'
        r'.*?</div>\s*<!-- 12 -->'
    )
    page, removed = re.subn(pattern, '\n        <!-- 8 -->', page, count=1, flags=re.S)
    if removed != 1:
        raise RuntimeError("Bloco de práticas não localizado para remoção")

    # Prevenção volta a ser a oitava aula teórica da página.
    page = page.replace('data-module="12" data-hours="2 h/a"', 'data-module="8" data-hours="2 h/a"', 1)
    page = page.replace('<span class="badge">Unidade 12</span>', '<span class="badge">Aula 8</span>', 1)
    page = page.replace('<h3>Unidade 12: Prevenção ao comportamento suicida</h3>', '<h3>Aula 8: Prevenção ao comportamento suicida</h3>', 1)

    # Os sete primeiros cards também passam a ser denominados aulas, sem alterar links/imagens.
    for n in range(1, 8):
        page = page.replace(f'<span class="badge">Unidade {n}</span>', f'<span class="badge">Aula {n}</span>', 1)
        page = page.replace(f'<h3>Unidade {n}:', f'<h3>Aula {n}:', 1)

    # Retira a faixa redundante "Aulas teóricas" interna; o próprio título da seção já cumpre esse papel.
    page = re.sub(
        r'\s*<div class="course-break"><span>Fundamentos e aplicação</span><h3>Aulas teóricas</h3><p>.*?</p></div>',
        '',
        page,
        count=1,
        flags=re.S,
    )

    # Mensagens e indicadores: a página mostra 8 aulas teóricas, embora o curso completo tenha 46 h/a.
    page = page.replace(
        'Seu ambiente de apoio ao VIII CATS: aulas, práticas presenciais e recursos essenciais, organizados para consulta simples ao longo da semana.',
        'Seu ambiente de apoio ao VIII CATS: aulas teóricas e recursos essenciais, organizados para consulta simples ao longo da semana.',
        1,
    )
    page = page.replace(
        'A trilha abaixo reproduz as 12 unidades formativas previstas no Plano de Ensino CATS 2026: oito unidades teóricas e quatro práticas presenciais. Avaliações permanecem em seção própria.',
        'Esta página reúne exclusivamente as oito aulas teóricas atuais do CATS 2026, organizadas para consulta e acompanhamento da aprendizagem.',
        1,
    )
    page = page.replace('<h2><i class="ri-route-line"></i> Trilha do curso</h2>', '<h2><i class="ri-book-2-line"></i> Aulas teóricas</h2>', 1)
    page = page.replace('<div><small>Trilha</small><strong>12 unidades</strong></div>', '<div><small>Aulas</small><strong>8 teóricas</strong></div>', 1)
    page = page.replace('<div class="mobile-progress"><i class="ri-bar-chart-box-line"></i> Progresso: <b id="mobileProgressLabel">0</b>/12</div>', '<div class="mobile-progress"><i class="ri-bar-chart-box-line"></i> Progresso: <b id="mobileProgressLabel">0</b>/8</div>', 1)
    page = page.replace('<div class="hero-kpi"><small>Trilha</small><strong id="kpi-modulos">12 unidades</strong></div>', '<div class="hero-kpi"><small>Aulas teóricas</small><strong id="kpi-modulos">8 aulas</strong></div>', 1)
    page = page.replace('<span><b id="progressLabel">0</b>/12</span>', '<span><b id="progressLabel">0</b>/8</span>', 1)
    page = page.replace('Progresso dos módulos', 'Progresso das aulas', 1)

    # Onboarding coerente com a superfície teórica.
    page = page.replace(
        'Este ambiente foi organizado para apoiar sua aprendizagem sem substituir a experiência presencial, a supervisão dos instrutores e a segurança das práticas.',
        'Este ambiente foi organizado para apoiar sua aprendizagem sem substituir a experiência presencial e a orientação dos instrutores.',
        1,
    )
    page = page.replace(
        'As unidades ficam compactas no celular; toque em <b>Ver conteúdo</b> para abrir uma de cada vez.',
        'As aulas ficam compactas no celular; toque no card para abrir uma de cada vez.',
        1,
    )
    page = page.replace(
        'Seu progresso fica salvo neste navegador e pode ser atualizado ao concluir cada unidade.',
        'Seu progresso fica salvo neste navegador e pode ser atualizado ao concluir cada aula.',
        1,
    )

    # Objetivos e progresso restritos às oito aulas teóricas.
    objectives = '''const objectivesMap = {
      "1":['Compreender conceitos, continuum e multicausalidade do comportamento suicida.','Reconhecer fatores de risco e de proteção em perspectiva operacional.'],
      "2":['Reconhecer sinais psicopatológicos relevantes ao atendimento sem assumir diagnóstico clínico formal.','Relacionar alterações de julgamento e risco à segurança da cena.'],
      "3":['Organizar a cena e estabelecer condições iniciais de segurança.','Aplicar fundamentos gerais da Abordagem Técnica em ATS.'],
      "4":['Aplicar aproximação, silêncio inicial, apresentação pessoal e manejo do diálogo.','Adequar condutas aos aspectos específicos do cenário.'],
      "5":['Aplicar escuta, vínculo, perguntas, validação e comunicação dissuasiva.','Reconhecer condutas comunicacionais a evitar.'],
      "6":['Diferenciar Abordagem Técnica e noções de Abordagem Tática.','Reconhecer critérios gerais de transição conforme risco e segurança.'],
      "7":['Organizar comando, funções e integração de recursos.','Conduzir documentação, encerramento e encaminhamento de forma segura.'],
      "8":['Adotar prevenção e comunicação responsável.','Realizar encaminhamento e cuidado com a equipe após a ocorrência.'],
      "proj":['Ampliar aprendizagem com podcasts temáticos.','Conectar teoria e prática por conteúdos complementares.']
    };'''
    page, count = re.subn(r'const objectivesMap = \{.*?\n    \};', objectives, page, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError("Mapa de objetivos não localizado na superfície final")

    page = page.replace('/* ===== Progresso das 12 unidades formativas ===== */', '/* ===== Progresso das 8 aulas teóricas ===== */', 1)
    page = page.replace('const TOTAL = 12;', 'const TOTAL = 8;', 1)
    page = page.replace("['1','2','3','4','5','6','7','8','9','10','11','12'].includes(String(n))", "['1','2','3','4','5','6','7','8'].includes(String(n))", 1)

    # Release específica para invalidar cache e registrar a correção editorial.
    page = page.replace('content="viii-cats-pa-2026-r3"', 'content="viii-cats-pa-2026-r4"', 1)

    # Garantias: exatamente 8 cards curriculares e nenhuma disciplina prática.
    for forbidden in (
        'Prática de conversação em ATS',
        'data-title="Prática em ATS: risco de incêndio/explosão"',
        'data-title="Prática em ATS: risco de precipitação"',
        'data-title="Prática em ATS: risco de afogamento"',
        'class="card practice-card"',
    ):
        if forbidden in page:
            raise RuntimeError(f"Disciplina prática permaneceu na página: {forbidden}")
    if sum(page.count(f'data-module="{n}"') for n in range(1, 9)) != 8:
        raise RuntimeError("A página final não contém exatamente oito aulas teóricas")

    path.write_text(page, encoding="utf-8")

    readme = '''# VIII CATS 2026 — Pouso Alegre

Portal de apoio ao VIII Curso de Atendimento a Tentativas de Suicídio do CBMMG, em Pouso Alegre.

- Edição: VIII CATS 2026
- Período: 21–25/09/2026
- Carga horária total do curso: 46 h/a
- Coordenação: Capitão BM Lucas Antônio de Oliveira
- Unidade executora: 7ª Cia Ind / 6º COB
- Superfície curricular da página: somente 8 aulas teóricas atuais
- Aulas exibidas: Aspectos Gerais do Comportamento Suicida; Psicopatologia do Comportamento Suicida; Abordagem Técnica — Aspectos Gerais; Abordagem Técnica — Aspectos Específicos; Comunicação Dissuasiva; Abordagem Tática; Gestão em ATS; Prevenção ao Comportamento Suicida
- Cards das aulas: identidade visual com imagem preservada também no mobile
- Práticas presenciais: pertencem à programação do curso, mas não são exibidas como disciplinas/cards neste portal
- Recursos extras: Biblioteca ATS CBMMG + podcast Girando a Ampulheta da Vida
- UX: mobile-first, progressive disclosure, cascatas por clique e uma aula aberta por vez no celular
- Autenticação: mesma base canônica de credenciais do Curso ATS e do podcast; sessão CATS isolada
- Auditorias: 30/30 e 90/90 obrigatórias antes da publicação

Fontes curriculares canônicas usadas na reconciliação: Plano de Ensino CATS 2026 e QTS CATS 2026.
URL pública: https://ricmurtapsicologia.github.io/CATS.pousoalegre/
'''
    (ROOT / "README.md").write_text(readme, encoding="utf-8")


portal.transform_videos = transform_videos
portal.main()
keep_theory_only()
