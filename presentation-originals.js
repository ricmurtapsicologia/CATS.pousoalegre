(()=>{
  "use strict";

  /*
   * VIII CATS Pouso Alegre 2026 — apresentações canônicas vigentes.
   * Aulas 3–7 apontam para a pasta oficial compartilhada do CATS 2026.
   * Todas as apresentações são abertas dentro do próprio portal por preview
   * do Google Drive, sem redirecionamento para nova aba.
   */
  const DECKS = Object.freeze({
    "1": {
      title: "Aspectos Gerais do Comportamento Suicida",
      id: "1ZYiAFZwrDE2i2zRpMg714cBqC4R-2OeH"
    },
    "2": {
      title: "Psicopatologia do Comportamento Suicida",
      id: "19n4VMAyYdaCjbYYIH8eZB3duNC1FkSF7"
    },
    "3": {
      title: "Abordagem Técnica: Aspectos Gerais",
      id: "1GuEU435vhorxZt42dAEurX2mVopFpFEz"
    },
    "4": {
      title: "Abordagem Técnica: Aspectos Específicos",
      id: "1kiKcOToIu1tKJRzWFVmARJYPP3N4J0S_"
    },
    "5": {
      title: "Abordagem Técnica: Comunicação Dissuasiva",
      id: "1AasaqZYAqBZJtoNCOh8e6TyBeb_11Fm-"
    },
    "6": {
      title: "Abordagem Tática",
      id: "1SNvZyrliydPk6iTkwAKhZ66FZ9AO7ac9"
    },
    "7": {
      title: "Gestão em ATS",
      id: "1hx-CVfbGbCzen1Ygc0-9lTHm81xVcaxw"
    },
    "8": {
      title: "Prevenção ao Comportamento Suicida",
      id: "1lVMb2TMiex4Z48_y1S2GA_mnTTgogS6u"
    }
  });

  const CARD_IMAGES = Object.freeze({
    "5": {
      original: "https://i.pinimg.com/originals/44/c7/d2/44c7d24202a6aa571b7c548ac02fa467.jpg",
      fallback: "https://i.pinimg.com/736x/44/c7/d2/44c7d24202a6aa571b7c548ac02fa467.jpg",
      alt: "Bombeiros em atuação de apoio e comunicação durante atendimento de emergência"
    },
    "6": {
      original: "https://i.pinimg.com/originals/3d/d7/44/3dd744f00802e7b721f8ae69199652fd.jpg",
      fallback: "https://i.pinimg.com/736x/3d/d7/44/3dd744f00802e7b721f8ae69199652fd.jpg",
      alt: "Bombeiro em cenário de resgate técnico em altura"
    }
  });

  const drivePreview = id => `https://drive.google.com/file/d/${id}/preview`;

  function ensureAccessLink(card, module, deck){
    const actions = card.querySelector('.actions');
    if(!actions) return null;

    let link = actions.querySelector('a.open-slide, .open-slide');
    if(link && link.tagName !== 'A'){
      const replacement = document.createElement('a');
      replacement.className = link.className;
      [...link.attributes].forEach(attr=>replacement.setAttribute(attr.name, attr.value));
      replacement.innerHTML = link.innerHTML;
      link.replaceWith(replacement);
      link = replacement;
    }

    if(!link){
      const note = actions.querySelector('.practice-note');
      link = document.createElement('a');
      link.className = 'btn small open-slide';
      link.href = '#';
      link.innerHTML = '<i class="ri-presentation-line" aria-hidden="true"></i> Acessar aula';
      if(note) note.replaceWith(link);
      else actions.prepend(link);
    }

    link.dataset.slideId = deck.id;
    link.dataset.originalPptx = 'true';
    link.dataset.module = module;
    link.href = '#';
    link.removeAttribute('target');
    link.removeAttribute('download');
    link.setAttribute('role','button');
    link.setAttribute('aria-label', `Assistir aula na página: ${deck.title}`);
    return link;
  }

  function applyCanonicalDecks(){
    Object.entries(DECKS).forEach(([module, deck])=>{
      const card = document.querySelector(`#cards article[data-module="${module}"]`);
      if(!card) return;
      ensureAccessLink(card, module, deck);
    });
  }

  function applyCardImages(){
    Object.entries(CARD_IMAGES).forEach(([module, cfg])=>{
      const img = document.querySelector(`#cards article[data-module="${module}"] .media img`);
      if(!img) return;
      img.removeAttribute('srcset');
      img.removeAttribute('sizes');
      img.alt = cfg.alt;
      img.decoding = 'async';
      img.loading = 'lazy';
      img.dataset.catsImageSource = 'Pinterest';
      img.onerror = ()=>{
        if(img.src !== cfg.fallback){
          img.onerror = null;
          img.src = cfg.fallback;
        }
      };
      img.src = cfg.original;
    });
  }

  function hardenViewer(viewer, frame){
    const external = document.getElementById('openExternal');
    const download = document.getElementById('downloadOriginalPptx');
    if(external) external.remove();
    if(download) download.remove();

    const controls = viewer?.querySelector('.controls');
    if(controls){
      controls.querySelectorAll('a[target="_blank"], a[download]').forEach(el=>el.remove());
    }

    frame.setAttribute('allow', 'autoplay; fullscreen; encrypted-media; picture-in-picture');
    frame.setAttribute('allowfullscreen', '');
    frame.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin');
  }

  function openOriginalDeck(link){
    const id = link.dataset.slideId;
    if(!id) return;

    const card = link.closest('.card');
    const title = card?.querySelector('h3')?.textContent?.trim() || 'CATS 2026';
    const viewer = document.getElementById('slidesViewer');
    const frame = document.getElementById('slidesFrame');
    const heading = document.getElementById('slidesTitle');
    const prev = document.getElementById('prevSlide');
    const next = document.getElementById('nextSlide');
    const tip = viewer?.querySelector('.tip');

    /* Fail-closed: nunca redireciona o aluno para outra aba. */
    if(!viewer || !frame || !heading) return;

    heading.textContent = title;
    frame.src = drivePreview(id);
    frame.title = `Apresentação do VIII CATS — ${title}`;
    hardenViewer(viewer, frame);

    if(prev) prev.hidden = true;
    if(next) next.hidden = true;
    if(tip) tip.textContent = 'Navegue pelos slides usando os controles do visualizador. Vídeos e áudios compatíveis são reproduzidos no próprio quadro.';

    if(!viewer.open) viewer.showModal();
    document.documentElement.style.overflow = 'hidden';
    setTimeout(()=>frame.focus(), 120);
  }

  /* Vídeos de apoio inline, sem pasta intermediária e sem download oferecido. */
  const VIDEO_ALLOW = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';

  function installATSVideoStyles(){
    if(document.getElementById('ats-video-parity-style')) return;
    const style = document.createElement('style');
    style.id = 'ats-video-parity-style';
    style.textContent = `
      #videos[data-ats-video-parity="true"]{padding-top:24px}
      #videos[data-ats-video-parity="true"] .ats-video-head{margin:0 0 14px}
      #videos[data-ats-video-parity="true"] .ats-video-kicker{display:block;color:#ffd166;font-size:12px;font-weight:850;letter-spacing:.12em;text-transform:uppercase;margin-bottom:7px}
      #videos[data-ats-video-parity="true"] .ats-video-title{margin:0;color:var(--text-1);font-size:clamp(1.45rem,2.7vw,2rem);line-height:1.12}
      #videos[data-ats-video-parity="true"] .ats-video-text{max-width:650px;margin:8px 0 0;color:var(--text-3);line-height:1.55}
      #videos[data-ats-video-parity="true"] .videos-box{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;margin-top:18px}
      #videos[data-ats-video-parity="true"] .video-card{min-width:0;overflow:hidden;border:1px solid var(--stroke);border-radius:var(--radius);background:var(--glass);box-shadow:var(--shadow);transition:transform .2s,border-color .2s}
      #videos[data-ats-video-parity="true"] .video-card:hover{transform:translateY(-2px);border-color:rgba(255,255,255,.22)}
      #videos[data-ats-video-parity="true"] .video-frame{width:100%;aspect-ratio:16/9;overflow:hidden;background:#000;border-bottom:1px solid var(--stroke)}
      #videos[data-ats-video-parity="true"] .video-frame iframe{width:100%;height:100%;display:block;border:0}
      #videos[data-ats-video-parity="true"] .video-body{display:flex;flex-direction:column;gap:8px;padding:14px}
      #videos[data-ats-video-parity="true"] .video-body h3{margin:0;color:var(--text-1);font-size:1rem;line-height:1.3}
      #videos[data-ats-video-parity="true"] .video-body p{margin:0;color:var(--text-2);font-size:.9rem;line-height:1.45}
      @media(max-width:900px){#videos[data-ats-video-parity="true"] .videos-box{grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}}
      @media(max-width:640px){
        #videos[data-ats-video-parity="true"]{padding-top:12px}
        #videos[data-ats-video-parity="true"] .videos-box{grid-template-columns:1fr;gap:12px;margin-top:14px}
        #videos[data-ats-video-parity="true"] .video-card{border-width:1px;box-shadow:none}
        #videos[data-ats-video-parity="true"] .video-body{padding:12px 13px}
      }
      @media(prefers-reduced-motion:reduce){#videos[data-ats-video-parity="true"] .video-card{transition:none}}
    `;
    document.head.appendChild(style);
  }

  function normalizeVideoCard(sourceCard){
    const iframe = sourceCard.querySelector('iframe');
    if(!iframe) return null;

    const title = sourceCard.querySelector('.video-title, .video-body h3')?.textContent?.trim() || iframe.title || 'Vídeo de apoio';
    const description = sourceCard.querySelector('.video-desc, .video-body p')?.textContent?.trim() || 'Conteúdo selecionado para revisão e aprofundamento.';

    iframe.classList.remove('video-embed');
    iframe.loading = 'lazy';
    iframe.title = title;
    iframe.setAttribute('allow', VIDEO_ALLOW);
    iframe.setAttribute('allowfullscreen', '');
    iframe.setAttribute('referrerpolicy','strict-origin-when-cross-origin');
    iframe.removeAttribute('width');
    iframe.removeAttribute('height');

    const article = document.createElement('article');
    article.className = 'video-card';

    const frame = document.createElement('div');
    frame.className = 'video-frame';
    frame.appendChild(iframe);

    const body = document.createElement('div');
    body.className = 'video-body';
    const heading = document.createElement('h3');
    heading.textContent = title;
    const paragraph = document.createElement('p');
    paragraph.textContent = description;
    body.append(heading, paragraph);

    article.append(frame, body);
    return article;
  }

  function applyATSVideoExperience(){
    const section = document.getElementById('videos');
    if(!section || section.dataset.atsVideoParity === 'true') return;

    const sourceCards = [...section.querySelectorAll('#videosGrid .card, .video-grid .card, .video-card')];
    const normalized = sourceCards.map(normalizeVideoCard).filter(Boolean);
    if(!normalized.length) return;

    section.dataset.atsVideoParity = 'true';
    section.setAttribute('aria-labelledby', 'videos-title');

    const head = document.createElement('div');
    head.className = 'ats-video-head';
    head.innerHTML = '<span class="ats-video-kicker">Vídeos</span><h2 class="ats-video-title" id="videos-title">Vídeos de apoio</h2><p class="ats-video-text">Conteúdos selecionados para revisão e aprofundamento, reproduzidos diretamente nesta página.</p>';

    const box = document.createElement('div');
    box.className = 'videos-box';
    box.setAttribute('aria-label', 'Vídeos selecionados');
    normalized.forEach(card=>box.appendChild(card));

    section.replaceChildren(head, box);
    installATSVideoStyles();
  }

  /* Remove oferta de download para mídia HTML5 existente no portal. */
  function hardenInlineMedia(){
    document.querySelectorAll('audio, video').forEach(media=>{
      media.setAttribute('controlsList','nodownload noremoteplayback');
      media.setAttribute('disableRemotePlayback','');
      media.addEventListener('contextmenu', event=>event.preventDefault());
    });
  }

  applyCanonicalDecks();
  applyCardImages();
  applyATSVideoExperience();
  hardenInlineMedia();

  /* Captura antes dos listeners legados: a aula sempre permanece no portal. */
  document.addEventListener('click', event=>{
    const link = event.target.closest?.('a.open-slide[data-original-pptx="true"]');
    if(!link) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    openOriginalDeck(link);
  }, true);

  window.CATSPousoAlegreOriginalDecks = DECKS;
  window.CATSPousoAlegreInlineDeckMode = Object.freeze({
    inline: true,
    externalNavigation: false,
    downloadButton: false,
    viewer: 'google-drive-preview',
    mediaAllow: 'autoplay; fullscreen; encrypted-media; picture-in-picture'
  });
  window.CATSPousoAlegreVideoMode = Object.freeze({
    pattern: 'ATS-inline-youtube',
    directPlay: true,
    folderGate: false,
    aspectRatio: '16/9',
    desktopColumns: 3,
    mobileColumns: 1,
    downloadOffered: false
  });
})();
