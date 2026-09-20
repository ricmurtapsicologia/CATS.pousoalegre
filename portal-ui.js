(()=>{
  "use strict";
  const load=(src,key)=>{
    if(document.querySelector(`script[src*="${key}"]`))return;
    const s=document.createElement('script');
    s.src=src;
    s.async=false;
    document.head.appendChild(s);
  };

  const MANUAL_URL='https://manual-participante-cats-digital.vercel.app';
  const injectManualCta=()=>{
    if(document.getElementById('manual-participante-cta'))return;
    const heroText=document.querySelector('.hero .hero-inner > div > p');
    if(!heroText)return;

    const wrap=document.createElement('div');
    wrap.className='manual-cta-wrap';
    wrap.style.cssText='margin-top:16px;display:flex;gap:10px;flex-wrap:wrap';

    const link=document.createElement('a');
    link.id='manual-participante-cta';
    link.className='btn';
    link.href=MANUAL_URL;
    link.target='_blank';
    link.rel='noopener noreferrer';
    link.setAttribute('aria-label','Acessar Manual do Participante CATS');
    link.innerHTML='<i class="ri-book-open-line" aria-hidden="true"></i> Manual do Participante';

    wrap.appendChild(link);
    heroText.insertAdjacentElement('afterend',wrap);
  };

  const applyCourseCardImages=()=>{
    const images={
      '5':{
        src:'https://i.pinimg.com/736x/aa/88/6a/aa886a6b4cf5d8b3d7148fe09c999113.jpg',
        alt:'Abordagem Técnica: Comunicação Dissuasiva',
        fit:'cover'
      },
      '6':{
        src:'assets/abordagem-tatica-panorama.svg?v=20260920-1',
        alt:'Abordagem Tática — fluxo panorâmico do Sistema ATS',
        fit:'contain',
        background:'#ffffff'
      }
    };

    Object.entries(images).forEach(([module,config])=>{
      const card=document.querySelector(`.card[data-module="${module}"]`);
      const img=card?.querySelector('.media img');
      if(!img)return;
      img.src=config.src;
      img.alt=config.alt;
      img.style.objectFit=config.fit;
      if(config.background)img.style.background=config.background;
    });
  };

  const enhancePage=()=>{
    injectManualCta();
    applyCourseCardImages();
  };

  if(document.readyState==='loading'){
    document.addEventListener('DOMContentLoaded',enhancePage,{once:true});
  }else{
    enhancePage();
  }

  load('https://ricmurtapsicologia.github.io/Curso-ATS/access-2026.js?v=20260914-4','access-2026.js');
  load('portal-ui-core.js?v=20260918-r18','portal-ui-core.js');
  load('presentation-originals.js?v=20260920-local-pdf-2','presentation-originals.js');
})();