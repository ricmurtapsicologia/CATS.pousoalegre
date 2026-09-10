(()=>{
  "use strict";

  /*
   * CATS Pouso Alegre 2026 — restauração das apresentações originais.
   * Fonte canônica dos decks: conjunto efetivamente utilizado pelo Maj BM Richelmy
   * no CATS 2025 / 3º COB — Juiz de Fora (08–10/09/2025).
   * Mantém os arquivos PPTX originais no Drive e evita o /presentation/embed,
   * que pode alterar a renderização de arquivos do PowerPoint.
   */
  const DECKS = Object.freeze({
    "1": {
      title: "Aspectos Gerais do Comportamento Suicida",
      id: "1XbZNfO9M-yUR-Nvow2-u46TvCC15sR6T"
    },
    "2": {
      title: "Psicopatologia do Comportamento Suicida",
      id: "1eZhr-fsON3t8NDkG8Fji3_mXIzKnhiZj"
    },
    "3": {
      title: "Abordagem Técnica: Aspectos Gerais",
      id: "1N_KATaJiVIMsFyXBHMJ44nkwhkfdQvJU"
    },
    "4": {
      title: "Abordagem Técnica: Aspectos Específicos",
      id: "1wE_p3OJjCrRV6S1JN3G6z27L93mDlwUd"
    },
    "8": {
      title: "Prevenção ao Comportamento Suicida",
      id: "12PpmEAJo3aw_3sGfZRHHQKHKg57wAZvv"
    }
  });

  const driveView = id => `https://drive.google.com/file/d/${id}/view`;
  const drivePreview = id => `https://drive.google.com/file/d/${id}/preview`;
  const driveDownload = id => `https://drive.google.com/uc?export=download&id=${id}`;

  function applyCanonicalDecks(){
    Object.entries(DECKS).forEach(([module, deck])=>{
      const card = document.querySelector(`#cards article[data-module="${module}"]`);
      if(!card) return;
      const link = card.querySelector('a.open-slide');
      if(!link) return;
      link.dataset.slideId = deck.id;
      link.dataset.originalPptx = "true";
      link.href = driveView(deck.id);
      link.setAttribute('aria-label', `Abrir apresentação original: ${deck.title}`);
    });
  }

  function ensureDownloadButton(id){
    const controls = document.querySelector('#slidesViewer .controls');
    const external = document.getElementById('openExternal');
    if(!controls || !external) return;

    external.href = driveView(id);
    external.innerHTML = '<i class="ri-external-link-line"></i> Abrir original';

    let download = document.getElementById('downloadOriginalPptx');
    if(!download){
      download = document.createElement('a');
      download.id = 'downloadOriginalPptx';
      download.className = 'btn ghost';
      download.target = '_blank';
      download.rel = 'noopener';
      download.innerHTML = '<i class="ri-download-2-line"></i> PPTX original';
      external.insertAdjacentElement('afterend', download);
    }
    download.href = driveDownload(id);
  }

  function openOriginalDeck(link){
    const id = link.dataset.slideId;
    if(!id) return;

    const card = link.closest('.card');
    const title = card?.querySelector('h3')?.textContent || 'CATS 2026';
    const viewer = document.getElementById('slidesViewer');
    const frame = document.getElementById('slidesFrame');
    const heading = document.getElementById('slidesTitle');
    const prev = document.getElementById('prevSlide');
    const next = document.getElementById('nextSlide');
    const tip = viewer?.querySelector('.tip');

    if(!viewer || !frame || !heading) {
      window.open(driveView(id), '_blank', 'noopener');
      return;
    }

    heading.textContent = `Apresentação original – ${title}`;
    frame.src = drivePreview(id);
    frame.title = `Apresentação original em PowerPoint — ${title}`;
    if(prev) prev.hidden = true;
    if(next) next.hidden = true;
    if(tip) tip.textContent = 'Use os controles do visualizador para navegar pelos slides.';
    ensureDownloadButton(id);

    if(!viewer.open) viewer.showModal();
    document.documentElement.style.overflow = 'hidden';
    setTimeout(()=>frame.focus(), 120);
  }

  /*
   * Paridade de vídeos com a página ATS.
   * AS IS: pasta expansível -> grade oculta -> player.
   * TO BE: seção visível -> card 16:9 -> play direto no iframe do YouTube.
   */
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
    head.innerHTML = '<span class="ats-video-kicker">Vídeos</span><h2 class="ats-video-title" id="videos-title">Vídeos de apoio</h2><p class="ats-video-text">Conteúdos selecionados para revisão e aprofundamento.</p>';

    const box = document.createElement('div');
    box.className = 'videos-box';
    box.setAttribute('aria-label', 'Vídeos selecionados');
    normalized.forEach(card=>box.appendChild(card));

    section.replaceChildren(head, box);
    installATSVideoStyles();
  }

  applyCanonicalDecks();
  applyATSVideoExperience();

  /*
   * Captura antes do listener legado do index.html. Assim o arquivo PPTX é exibido
   * pelo visualizador de arquivo do Drive, e não pelo Google Slides /embed.
   */
  document.addEventListener('click', event=>{
    const link = event.target.closest?.('a.open-slide[data-original-pptx="true"]');
    if(!link) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    openOriginalDeck(link);
  }, true);

  window.CATSPousoAlegreOriginalDecks = DECKS;
  window.CATSPousoAlegreVideoMode = Object.freeze({
    pattern: 'ATS-inline-youtube',
    directPlay: true,
    folderGate: false,
    aspectRatio: '16/9',
    desktopColumns: 3,
    mobileColumns: 1
  });
})();
