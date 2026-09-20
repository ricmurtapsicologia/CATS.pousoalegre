(()=>{
  "use strict";

  const PODCAST_BASE = "https://ricmurtapsicologia.github.io/Podcast-ATS-CBMMG/";
  const MANIFEST_URL = `${PODCAST_BASE}content-manifest.js?v=gav-learning-v4-20260902`;

  function installStyles(){
    if(document.getElementById('cats-audio-inline-style')) return;
    const style = document.createElement('style');
    style.id = 'cats-audio-inline-style';
    style.textContent = `
      #catsAudioLibrary{max-width:1200px;margin:0 auto;padding:32px 16px}
      #catsAudioLibrary .audio-head{margin-bottom:16px}
      #catsAudioLibrary .audio-kicker{display:block;color:#ffd166;font-size:12px;font-weight:850;letter-spacing:.12em;text-transform:uppercase;margin-bottom:7px}
      #catsAudioLibrary .audio-title{margin:0;color:var(--text-1);font-size:clamp(1.45rem,2.7vw,2rem);line-height:1.12}
      #catsAudioLibrary .audio-intro{max-width:760px;margin:8px 0 0;color:var(--text-3);line-height:1.55}
      #catsAudioLibrary .audio-series{margin-top:14px;border:1px solid var(--stroke);border-radius:var(--radius);background:var(--glass);overflow:hidden}
      #catsAudioLibrary .audio-series summary{cursor:pointer;list-style:none;padding:16px 18px;color:var(--text-1);font-weight:850;display:flex;justify-content:space-between;gap:12px;align-items:center}
      #catsAudioLibrary .audio-series summary::-webkit-details-marker{display:none}
      #catsAudioLibrary .audio-series summary::after{content:'+';font-size:1.3rem;color:var(--brand)}
      #catsAudioLibrary .audio-series[open] summary::after{content:'−'}
      #catsAudioLibrary .audio-series-desc{margin:-4px 18px 14px;color:var(--text-3);line-height:1.5}
      #catsAudioLibrary .audio-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;padding:0 14px 16px}
      #catsAudioLibrary .audio-card{min-width:0;border:1px solid var(--stroke);border-radius:14px;background:rgba(255,255,255,.04);padding:13px}
      #catsAudioLibrary .audio-code{display:block;color:var(--brand);font-size:.75rem;font-weight:850;letter-spacing:.06em;margin-bottom:5px}
      #catsAudioLibrary .audio-card h3{margin:0 0 10px;color:var(--text-1);font-size:.95rem;line-height:1.35}
      #catsAudioLibrary audio{width:100%;height:42px;display:block}
      #catsAudioLibrary .audio-note{margin-top:10px;color:var(--text-3);font-size:.82rem;line-height:1.4}
      @media(max-width:700px){#catsAudioLibrary{padding-top:22px}#catsAudioLibrary .audio-grid{grid-template-columns:1fr;padding:0 10px 12px}#catsAudioLibrary .audio-series summary{padding:14px}}
    `;
    document.head.appendChild(style);
  }

  function protectAudio(audio){
    audio.preload = 'metadata';
    audio.setAttribute('controls','');
    audio.setAttribute('controlsList','nodownload noremoteplayback');
    audio.setAttribute('disableRemotePlayback','');
    audio.setAttribute('draggable','false');
    try{ audio.disableRemotePlayback = true; }catch{}
    const block = event=>{ event.preventDefault(); event.stopPropagation(); };
    audio.addEventListener('contextmenu', block, true);
    audio.addEventListener('dragstart', block, true);
    audio.addEventListener('play', ()=>{
      document.querySelectorAll('#catsAudioLibrary audio').forEach(other=>{
        if(other !== audio && !other.paused) other.pause();
      });
    });
  }

  function absoluteAudioUrl(relative){
    return new URL(relative, PODCAST_BASE).href;
  }

  function buildSeries(series, index){
    const details = document.createElement('details');
    details.className = 'audio-series';
    details.open = index === 0;

    const summary = document.createElement('summary');
    const count = Array.isArray(series.items) ? series.items.length : 0;
    summary.textContent = `${series.title} · ${count} episódios`;
    details.appendChild(summary);

    const desc = document.createElement('p');
    desc.className = 'audio-series-desc';
    desc.textContent = series.description || '';
    details.appendChild(desc);

    const grid = document.createElement('div');
    grid.className = 'audio-grid';

    (series.items || []).forEach(item=>{
      if(item.type !== 'audio') return;
      const card = document.createElement('article');
      card.className = 'audio-card';
      card.dataset.audioId = item.id;

      const code = document.createElement('span');
      code.className = 'audio-code';
      code.textContent = item.code;

      const title = document.createElement('h3');
      title.textContent = item.title;

      const audio = document.createElement('audio');
      audio.src = absoluteAudioUrl(item.url);
      audio.setAttribute('aria-label', `${item.code} — ${item.title}`);
      protectAudio(audio);

      card.append(code, title, audio);
      grid.appendChild(card);
    });

    details.appendChild(grid);
    return details;
  }

  function retargetProjectCard(){
    const card = document.querySelector('article[data-module="proj"]');
    const link = card?.querySelector('.actions a');
    if(!link) return;
    link.href = '#catsAudioLibrary';
    link.removeAttribute('target');
    link.removeAttribute('rel');
    link.removeAttribute('download');
    link.innerHTML = '<i class="ri-headphone-line" aria-hidden="true"></i> Ouvir áudios';
    link.setAttribute('aria-label','Ouvir biblioteca de áudios nesta página');
  }

  function buildAudioLibrary(){
    const manifest = window.GAV_MANIFEST;
    if(!manifest?.series) return false;
    if(document.getElementById('catsAudioLibrary')) return true;

    const audioSeries = manifest.series.filter(series=>series.kind === 'audio' && Array.isArray(series.items));
    if(!audioSeries.length) return false;

    installStyles();
    const section = document.createElement('section');
    section.id = 'catsAudioLibrary';
    section.dataset.ready = 'true';
    section.setAttribute('aria-labelledby','cats-audio-title');

    const head = document.createElement('div');
    head.className = 'audio-head';
    head.innerHTML = '<span class="audio-kicker">Áudios</span><h2 class="audio-title" id="cats-audio-title">Girando a Ampulheta da Vida</h2><p class="audio-intro">Biblioteca sonora complementar às aulas de ATS. Os episódios são reproduzidos diretamente nesta página, sem redirecionamento e sem opção visível de download.</p>';
    section.appendChild(head);

    audioSeries.forEach((series,index)=>section.appendChild(buildSeries(series,index)));

    const note = document.createElement('p');
    note.className = 'audio-note';
    note.textContent = 'A reprodução ocorre no navegador. O portal não oferece link ou botão de download dos arquivos de áudio.';
    section.appendChild(note);

    const videos = document.getElementById('videos');
    if(videos) videos.insertAdjacentElement('afterend', section);
    else document.querySelector('main')?.appendChild(section);

    retargetProjectCard();
    window.CATSPousoAlegreAudioMode = Object.freeze({
      inline: true,
      externalNavigation: false,
      downloadOffered: false,
      series: audioSeries.length,
      episodes: section.querySelectorAll('audio').length
    });
    return true;
  }

  function loadManifest(){
    if(buildAudioLibrary()) return;
    let script = document.getElementById('cats-gav-manifest');
    if(script) return;
    script = document.createElement('script');
    script.id = 'cats-gav-manifest';
    script.src = MANIFEST_URL;
    script.defer = true;
    script.addEventListener('load', ()=>buildAudioLibrary(), {once:true});
    document.head.appendChild(script);
  }

  loadManifest();
})();
