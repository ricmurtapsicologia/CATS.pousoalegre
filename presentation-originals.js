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

  applyCanonicalDecks();

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
})();
