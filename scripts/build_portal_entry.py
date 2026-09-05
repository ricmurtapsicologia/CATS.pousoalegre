from __future__ import annotations

import build_portal as portal


def transform_videos(page: str) -> str:
    """Converte a seção legada de vídeos em pasta fechada por botão.

    A transformação trabalha no limite semântico da própria <section>, evitando
    depender de espaços ou quebras de linha do HTML legado.
    """
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

    # Mantém apenas a abertura da seção e substitui cabeçalho + abertura da grade.
    section_prefix = section[:head_start]
    section = section_prefix + folder_open + section[grid_pos + len(grid_marker):]

    # O último </div> antes de </section> fecha a grade original. Acrescenta o
    # fechamento da pasta imediatamente depois dele.
    section_close = section.rfind('</section>')
    last_div = section.rfind('</div>', 0, section_close)
    if last_div < 0:
        raise RuntimeError("Fechamento da grade de vídeos não localizado")
    insert_at = last_div + len('</div>')
    section = section[:insert_at] + '\n      </div>' + section[insert_at:]

    return page[:section_start] + section + page[section_end:]


portal.transform_videos = transform_videos
portal.main()
