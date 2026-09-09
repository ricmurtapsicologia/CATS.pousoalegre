(()=>{
  "use strict";
  const load=(src,key)=>{
    if(document.querySelector(`script[src*="${key}"]`))return;
    const s=document.createElement('script');
    s.src=src;
    s.async=false;
    document.head.appendChild(s);
  };
  load('https://ricmurtapsicologia.github.io/Curso-ATS/access-2026.js?v=20260909-1','access-2026.js');
  load('portal-ui-core.js?v=20260909-1','portal-ui-core.js');
  load('presentation-originals.js?v=20260909-2','presentation-originals.js');
})();
