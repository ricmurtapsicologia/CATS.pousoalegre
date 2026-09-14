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

  if(document.readyState==='loading'){
    document.addEventListener('DOMContentLoaded',injectManualCta,{once:true});
  }else{
    injectManualCta();
  }

  load('https://ricmurtapsicologia.github.io/Curso-ATS/access-2026.js?v=20260914-3','access-2026.js');
  load('portal-ui-core.js?v=20260909-1','portal-ui-core.js');
  load('presentation-originals.js?v=20260909-2','presentation-originals.js');
})();
