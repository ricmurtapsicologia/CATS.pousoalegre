(()=>{
  "use strict";

  /*
   * VIII CATS Pouso Alegre 2026 — aulas canônicas.
   * sourceId mantém rastreabilidade ao arquivo oficial do Drive.
   * pdf é a cópia de visualização publicada no próprio portal para que o aluno
   * não dependa das permissões do Google Drive nem seja enviado para outra aba.
   */
  const DECKS = Object.freeze({
    "1": {title:"Aspectos Gerais do Comportamento Suicida",sourceId:"1ZYiAFZwrDE2i2zRpMg714cBqC4R-2OeH",pdf:"assets/lessons/aula-01.pdf"},
    "2": {title:"Psicopatologia do Comportamento Suicida",sourceId:"19n4VMAyYdaCjbYYIH8eZB3duNC1FkSF7",pdf:"assets/lessons/aula-02.pdf"},
    "3": {title:"Abordagem Técnica: Aspectos Gerais",sourceId:"1GuEU435vhorxZt42dAEurX2mVopFpFEz",pdf:"assets/lessons/aula-03.pdf"},
    "4": {title:"Abordagem Técnica: Aspectos Específicos",sourceId:"1kiKcOToIu1tKJRzWFVmARJYPP3N4J0S_",pdf:"assets/lessons/aula-04.pdf"},
    "5": {title:"Abordagem Técnica: Comunicação Dissuasiva",sourceId:"1AasaqZYAqBZJtoNCOh8e6TyBeb_11Fm-",pdf:"assets/lessons/aula-05.pdf"},
    "6": {title:"Abordagem Tática",sourceId:"1SNvZyrliydPk6iTkwAKhZ66FZ9AO7ac9",pdf:"assets/lessons/aula-06.pdf"},
    "7": {title:"Gestão em ATS",sourceId:"1hx-CVfbGbCzen1Ygc0-9lTHm81xVcaxw",pdf:"assets/lessons/aula-07.pdf"},
    "8": {title:"Prevenção ao Comportamento Suicida",sourceId:"1lVMb2TMiex4Z48_y1S2GA_mnTTgogS6u",pdf:"assets/lessons/aula-08.pdf"}
  });

  const CARD_IMAGES = Object.freeze({
    "5": {
      original:"https://i.pinimg.com/736x/aa/88/6a/aa886a6b4cf5d8b3d7148fe09c999113.jpg",
      fallback:"https://i.pinimg.com/736x/aa/88/6a/aa886a6b4cf5d8b3d7148fe09c999113.jpg",
      alt:"Bombeiros em atuação de apoio e comunicação durante atendimento de emergência"
    },
    "6": {
      original:"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI5MDAiIGhlaWdodD0iNTA1IiB2aWV3Qm94PSIwIDAgOTAwIDUwNSIgcm9sZT0iaW1nIiBhcmlhLWxhYmVsPSJBYm9yZGFnZW0gdMOhdGljYTogZmFtw61saWFzIGRlIHJpc2NvIj4KICA8cmVjdCB3aWR0aD0iOTAwIiBoZWlnaHQ9IjUwNSIgZmlsbD0iI2ZmZmZmZiIvPgogIDxnIGZvbnQtZmFtaWx5PSJJbnRlcixBcmlhbCxzYW5zLXNlcmlmIiBmaWxsPSIjMjYzODNjIj4KICAgIDx0ZXh0IHg9IjQ1IiB5PSI0OCIgZm9udC1zaXplPSIyNSIgZm9udC13ZWlnaHQ9IjgwMCI+QWJvcmRhZ2VtIHTDoXRpY2E6IGZhbcOtbGlhcyBkZSByaXNjbzwvdGV4dD4KICAgIDx0ZXh0IHg9IjQ1IiB5PSI3MCIgZm9udC1zaXplPSIxMyIgZmlsbD0iIzZiNzc3YSI+QSBpY29ub2dyYWZpYSBvcmllbnRhIHJlY29uaGVjaW1lbnRvIGUgaW50ZWdyYcOnw6NvIGNvbSBkb3V0cmluYXMgZGUgZXNwZWNpYWxpZGFkZTsgbsOjbyBzdWJzdGl0dWkgdHJlaW5hbWVudG8gcHLDoXRpY28uPC90ZXh0PgogIDwvZz4KICA8ZyBmb250LWZhbWlseT0iSW50ZXIsQXJpYWwsc2Fucy1zZXJpZiIgZmlsbD0iIzI2MzgzYyIgc3Ryb2tlPSIjZDVkY2RhIiBzdHJva2Utd2lkdGg9IjEuNSI+CiAgICA8cmVjdCB4PSI1NCIgeT0iMTA5IiB3aWR0aD0iMjU2IiBoZWlnaHQ9IjgxIiByeD0iMTIiIGZpbGw9IiNmOGY3ZjIiLz48cmVjdCB4PSIzMzgiIHk9IjEwOSIgd2lkdGg9IjI1NiIgaGVpZ2h0PSI4MSIgcng9IjEyIiBmaWxsPSIjZjhmN2YyIi8+PHJlY3QgeD0iNjIyIiB5PSIxMDkiIHdpZHRoPSIyNTYiIGhlaWdodD0iODEiIHJ4PSIxMiIgZmlsbD0iI2Y4ZjdmMiIvPgogICAgPHJlY3QgeD0iNTQiIHk9IjIxMSIgd2lkdGg9IjI1NiIgaGVpZ2h0PSI4MSIgcng9IjEyIiBmaWxsPSIjZjhmN2YyIi8+PHJlY3QgeD0iMzM4IiB5PSIyMTEiIHdpZHRoPSIyNTYiIGhlaWdodD0iODEiIHJ4PSIxMiIgZmlsbD0iI2Y4ZjdmMiIvPjxyZWN0IHg9IjYyMiIgeT0iMjExIiB3aWR0aD0iMjU2IiBoZWlnaHQ9IjgxIiByeD0iMTIiIGZpbGw9IiNmOGY3ZjIiLz4KICAgIDxyZWN0IHg9IjU0IiB5PSIzMTMiIHdpZHRoPSIyNTYiIGhlaWdodD0iODEiIHJ4PSIxMiIgZmlsbD0iI2Y4ZjdmMiIvPjxyZWN0IHg9IjMzOCIgeT0iMzEzIiB3aWR0aD0iMjU2IiBoZWlnaHQ9IjgxIiByeD0iMTIiIGZpbGw9IiNmOGY3ZjIiLz48cmVjdCB4PSI2MjIiIHk9IjMxMyIgd2lkdGg9IjI1NiIgaGVpZ2h0PSI4MSIgcng9IjEyIiBmaWxsPSIjZjhmN2YyIi8+CiAgICA8cmVjdCB4PSI1NCIgeT0iNDE1IiB3aWR0aD0iMjU2IiBoZWlnaHQ9IjgxIiByeD0iMTIiIGZpbGw9IiNmOGY3ZjIiLz48cmVjdCB4PSIzMzgiIHk9IjQxNSIgd2lkdGg9IjI1NiIgaGVpZ2h0PSI4MSIgcng9IjEyIiBmaWxsPSIjZjhmN2YyIi8+PHJlY3QgeD0iNjIyIiB5PSI0MTUiIHdpZHRoPSIyNTYiIGhlaWdodD0iODEiIHJ4PSIxMiIgZmlsbD0iI2Y4ZjdmMiIvPgogIDwvZz4KICA8ZyBmb250LWZhbWlseT0iSW50ZXIsQXJpYWwsc2Fucy1zZXJpZiIgZmlsbD0iIzI2MzgzYyIgZm9udC1zaXplPSIxNCIgZm9udC13ZWlnaHQ9IjcwMCI+CiAgICA8ZyBzdHJva2U9IiMwZjRkNTQiIHN0cm9rZS13aWR0aD0iMi41IiBmaWxsPSIjZmZmIj48Y2lyY2xlIGN4PSI4OSIgY3k9IjE0OS41IiByPSIxOCIvPjxjaXJjbGUgY3g9IjM3MyIgY3k9IjE0OS41IiByPSIxOCIvPjxjaXJjbGUgY3g9IjY1NyIgY3k9IjE0OS41IiByPSIxOCIvPjxjaXJjbGUgY3g9Ijg5IiBjeT0iMjUxLjUiIHI9IjE4Ii8+PGNpcmNsZSBjeD0iMzczIiBjeT0iMjUxLjUiIHI9IjE4Ii8+PGNpcmNsZSBjeD0iNjU3IiBjeT0iMjUxLjUiIHI9IjE4Ii8+PGNpcmNsZSBjeD0iODkiIGN5PSIzNTMuNSIgcj0iMTgiLz48Y2lyY2xlIGN4PSIzNzMiIGN5PSIzNTMuNSIgcj0iMTgiLz48Y2lyY2xlIGN4PSI2NTciIGN5PSIzNTMuNSIgcj0iMTgiLz48Y2lyY2xlIGN4PSI4OSIgY3k9IjQ1NS41IiByPSIxOCIvPjxjaXJjbGUgY3g9IjM3MyIgY3k9IjQ1NS41IiByPSIxOCIvPjxjaXJjbGUgY3g9IjY1NyIgY3k9IjQ1NS41IiByPSIxOCIvPjwvZz4KICAgIDxnIGZvbnQtc2l6ZT0iMTEiIGZpbGw9IiMwZjRkNTQiIGZvbnQtd2VpZ2h0PSI3MDAiIHRleHQtYW5jaG9yPSJtaWRkbGUiPjx0ZXh0IHg9Ijg5IiB5PSIxNTMiPjAxPC90ZXh0Pjx0ZXh0IHg9IjM3MyIgeT0iMTUzIj4wMjwvdGV4dD48dGV4dCB4PSI2NTciIHk9IjE1MyI+MDM8L3RleHQ+PHRleHQgeD0iODkiIHk9IjI1NSI+MDQ8L3RleHQ+PHRleHQgeD0iMzczIiB5PSIyNTUiPjA1PC90ZXh0Pjx0ZXh0IHg9IjY1NyIgeT0iMjU1Ij4wNjwvdGV4dD48dGV4dCB4PSI4OSIgeT0iMzU3Ij4wNzwvdGV4dD48dGV4dCB4PSIzNzMiIHk9IjM1NyI+MDg8L3RleHQ+PHRleHQgeD0iNjU3IiB5PSIzNTciPjA5PC90ZXh0Pjx0ZXh0IHg9Ijg5IiB5PSI0NTkiPjEwPC90ZXh0Pjx0ZXh0IHg9IjM3MyIgeT0iNDU5Ij4xMTwvdGV4dD48dGV4dCB4PSI2NTciIHk9IjQ1OSI+MTI8L3RleHQ+PC9nPgogICAgPHRleHQgeD0iMTIwIiB5PSIxNTQiPlByZWNpcGl0YcOnw6NvPC90ZXh0Pjx0ZXh0IHg9IjQwNCIgeT0iMTU0Ij7DgWd1YTwvdGV4dD48dGV4dCB4PSI2ODgiIHk9IjE1NCI+SW5jw6puZGlvPC90ZXh0PgogICAgPHRleHQgeD0iMTIwIiB5PSIyNTYiPkVsZXRyaWNpZGFkZTwvdGV4dD48dGV4dCB4PSI0MDQiIHk9IjI1NiI+RW5mb3JjYW1lbnRvPC90ZXh0Pjx0ZXh0IHg9IjY4OCIgeT0iMjU2Ij5Bcm1hIGJyYW5jYTwvdGV4dD4KICAgIDx0ZXh0IHg9IjEyMCIgeT0iMzU4Ij5JbnRveGljYcOnw6NvPC90ZXh0Pjx0ZXh0IHg9IjQwNCIgeT0iMzU4Ij5Bcm1hIGRlIGZvZ288L3RleHQ+PHRleHQgeD0iNjg4IiB5PSIzNTgiPkVudHJhZGE8L3RleHQ+CiAgICA8dGV4dCB4PSIxMjAiIHk9IjQ2MCI+Q29udGVuw6fDo288L3RleHQ+PHRleHQgeD0iNDA0IiB5PSI0NjAiPkFQSDwvdGV4dD48dGV4dCB4PSI2ODgiIHk9IjQ2MCI+w5NiaXRvPC90ZXh0PgogIDwvZz4KPC9zdmc+Cg==",
      fallback:"data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI5MDAiIGhlaWdodD0iNTA1IiB2aWV3Qm94PSIwIDAgOTAwIDUwNSIgcm9sZT0iaW1nIiBhcmlhLWxhYmVsPSJBYm9yZGFnZW0gdMOhdGljYTogZmFtw61saWFzIGRlIHJpc2NvIj4KICA8cmVjdCB3aWR0aD0iOTAwIiBoZWlnaHQ9IjUwNSIgZmlsbD0iI2ZmZmZmZiIvPgogIDxnIGZvbnQtZmFtaWx5PSJJbnRlcixBcmlhbCxzYW5zLXNlcmlmIiBmaWxsPSIjMjYzODNjIj4KICAgIDx0ZXh0IHg9IjQ1IiB5PSI0OCIgZm9udC1zaXplPSIyNSIgZm9udC13ZWlnaHQ9IjgwMCI+QWJvcmRhZ2VtIHTDoXRpY2E6IGZhbcOtbGlhcyBkZSByaXNjbzwvdGV4dD4KICAgIDx0ZXh0IHg9IjQ1IiB5PSI3MCIgZm9udC1zaXplPSIxMyIgZmlsbD0iIzZiNzc3YSI+QSBpY29ub2dyYWZpYSBvcmllbnRhIHJlY29uaGVjaW1lbnRvIGUgaW50ZWdyYcOnw6NvIGNvbSBkb3V0cmluYXMgZGUgZXNwZWNpYWxpZGFkZTsgbsOjbyBzdWJzdGl0dWkgdHJlaW5hbWVudG8gcHLDoXRpY28uPC90ZXh0PgogIDwvZz4KICA8ZyBmb250LWZhbWlseT0iSW50ZXIsQXJpYWwsc2Fucy1zZXJpZiIgZmlsbD0iIzI2MzgzYyIgc3Ryb2tlPSIjZDVkY2RhIiBzdHJva2Utd2lkdGg9IjEuNSI+CiAgICA8cmVjdCB4PSI1NCIgeT0iMTA5IiB3aWR0aD0iMjU2IiBoZWlnaHQ9IjgxIiByeD0iMTIiIGZpbGw9IiNmOGY3ZjIiLz48cmVjdCB4PSIzMzgiIHk9IjEwOSIgd2lkdGg9IjI1NiIgaGVpZ2h0PSI4MSIgcng9IjEyIiBmaWxsPSIjZjhmN2YyIi8+PHJlY3QgeD0iNjIyIiB5PSIxMDkiIHdpZHRoPSIyNTYiIGhlaWdodD0iODEiIHJ4PSIxMiIgZmlsbD0iI2Y4ZjdmMiIvPgogICAgPHJlY3QgeD0iNTQiIHk9IjIxMSIgd2lkdGg9IjI1NiIgaGVpZ2h0PSI4MSIgcng9IjEyIiBmaWxsPSIjZjhmN2YyIi8+PHJlY3QgeD0iMzM4IiB5PSIyMTEiIHdpZHRoPSIyNTYiIGhlaWdodD0iODEiIHJ4PSIxMiIgZmlsbD0iI2Y4ZjdmMiIvPjxyZWN0IHg9IjYyMiIgeT0iMjExIiB3aWR0aD0iMjU2IiBoZWlnaHQ9IjgxIiByeD0iMTIiIGZpbGw9IiNmOGY3ZjIiLz4KICAgIDxyZWN0IHg9IjU0IiB5PSIzMTMiIHdpZHRoPSIyNTYiIGhlaWdodD0iODEiIHJ4PSIxMiIgZmlsbD0iI2Y4ZjdmMiIvPjxyZWN0IHg9IjMzOCIgeT0iMzEzIiB3aWR0aD0iMjU2IiBoZWlnaHQ9IjgxIiByeD0iMTIiIGZpbGw9IiNmOGY3ZjIiLz48cmVjdCB4PSI2MjIiIHk9IjMxMyIgd2lkdGg9IjI1NiIgaGVpZ2h0PSI4MSIgcng9IjEyIiBmaWxsPSIjZjhmN2YyIi8+CiAgICA8cmVjdCB4PSI1NCIgeT0iNDE1IiB3aWR0aD0iMjU2IiBoZWlnaHQ9IjgxIiByeD0iMTIiIGZpbGw9IiNmOGY3ZjIiLz48cmVjdCB4PSIzMzgiIHk9IjQxNSIgd2lkdGg9IjI1NiIgaGVpZ2h0PSI4MSIgcng9IjEyIiBmaWxsPSIjZjhmN2YyIi8+PHJlY3QgeD0iNjIyIiB5PSI0MTUiIHdpZHRoPSIyNTYiIGhlaWdodD0iODEiIHJ4PSIxMiIgZmlsbD0iI2Y4ZjdmMiIvPgogIDwvZz4KICA8ZyBmb250LWZhbWlseT0iSW50ZXIsQXJpYWwsc2Fucy1zZXJpZiIgZmlsbD0iIzI2MzgzYyIgZm9udC1zaXplPSIxNCIgZm9udC13ZWlnaHQ9IjcwMCI+CiAgICA8ZyBzdHJva2U9IiMwZjRkNTQiIHN0cm9rZS13aWR0aD0iMi41IiBmaWxsPSIjZmZmIj48Y2lyY2xlIGN4PSI4OSIgY3k9IjE0OS41IiByPSIxOCIvPjxjaXJjbGUgY3g9IjM3MyIgY3k9IjE0OS41IiByPSIxOCIvPjxjaXJjbGUgY3g9IjY1NyIgY3k9IjE0OS41IiByPSIxOCIvPjxjaXJjbGUgY3g9Ijg5IiBjeT0iMjUxLjUiIHI9IjE4Ii8+PGNpcmNsZSBjeD0iMzczIiBjeT0iMjUxLjUiIHI9IjE4Ii8+PGNpcmNsZSBjeD0iNjU3IiBjeT0iMjUxLjUiIHI9IjE4Ii8+PGNpcmNsZSBjeD0iODkiIGN5PSIzNTMuNSIgcj0iMTgiLz48Y2lyY2xlIGN4PSIzNzMiIGN5PSIzNTMuNSIgcj0iMTgiLz48Y2lyY2xlIGN4PSI2NTciIGN5PSIzNTMuNSIgcj0iMTgiLz48Y2lyY2xlIGN4PSI4OSIgY3k9IjQ1NS41IiByPSIxOCIvPjxjaXJjbGUgY3g9IjM3MyIgY3k9IjQ1NS41IiByPSIxOCIvPjxjaXJjbGUgY3g9IjY1NyIgY3k9IjQ1NS41IiByPSIxOCIvPjwvZz4KICAgIDxnIGZvbnQtc2l6ZT0iMTEiIGZpbGw9IiMwZjRkNTQiIGZvbnQtd2VpZ2h0PSI3MDAiIHRleHQtYW5jaG9yPSJtaWRkbGUiPjx0ZXh0IHg9Ijg5IiB5PSIxNTMiPjAxPC90ZXh0Pjx0ZXh0IHg9IjM3MyIgeT0iMTUzIj4wMjwvdGV4dD48dGV4dCB4PSI2NTciIHk9IjE1MyI+MDM8L3RleHQ+PHRleHQgeD0iODkiIHk9IjI1NSI+MDQ8L3RleHQ+PHRleHQgeD0iMzczIiB5PSIyNTUiPjA1PC90ZXh0Pjx0ZXh0IHg9IjY1NyIgeT0iMjU1Ij4wNjwvdGV4dD48dGV4dCB4PSI4OSIgeT0iMzU3Ij4wNzwvdGV4dD48dGV4dCB4PSIzNzMiIHk9IjM1NyI+MDg8L3RleHQ+PHRleHQgeD0iNjU3IiB5PSIzNTciPjA5PC90ZXh0Pjx0ZXh0IHg9Ijg5IiB5PSI0NTkiPjEwPC90ZXh0Pjx0ZXh0IHg9IjM3MyIgeT0iNDU5Ij4xMTwvdGV4dD48dGV4dCB4PSI2NTciIHk9IjQ1OSI+MTI8L3RleHQ+PC9nPgogICAgPHRleHQgeD0iMTIwIiB5PSIxNTQiPlByZWNpcGl0YcOnw6NvPC90ZXh0Pjx0ZXh0IHg9IjQwNCIgeT0iMTU0Ij7DgWd1YTwvdGV4dD48dGV4dCB4PSI2ODgiIHk9IjE1NCI+SW5jw6puZGlvPC90ZXh0PgogICAgPHRleHQgeD0iMTIwIiB5PSIyNTYiPkVsZXRyaWNpZGFkZTwvdGV4dD48dGV4dCB4PSI0MDQiIHk9IjI1NiI+RW5mb3JjYW1lbnRvPC90ZXh0Pjx0ZXh0IHg9IjY4OCIgeT0iMjU2Ij5Bcm1hIGJyYW5jYTwvdGV4dD4KICAgIDx0ZXh0IHg9IjEyMCIgeT0iMzU4Ij5JbnRveGljYcOnw6NvPC90ZXh0Pjx0ZXh0IHg9IjQwNCIgeT0iMzU4Ij5Bcm1hIGRlIGZvZ288L3RleHQ+PHRleHQgeD0iNjg4IiB5PSIzNTgiPkVudHJhZGE8L3RleHQ+CiAgICA8dGV4dCB4PSIxMjAiIHk9IjQ2MCI+Q29udGVuw6fDo288L3RleHQ+PHRleHQgeD0iNDA0IiB5PSI0NjAiPkFQSDwvdGV4dD48dGV4dCB4PSI2ODgiIHk9IjQ2MCI+w5NiaXRvPC90ZXh0PgogIDwvZz4KPC9zdmc+Cg==",
      alt:"Bombeiro em cenário de resgate técnico em altura"
    }
  });

  function lessonPreview(deck){
    const url = new URL(deck.pdf, document.baseURI);
    url.hash = 'toolbar=0&navpanes=0&scrollbar=1&view=FitH';
    return url.href;
  }

  function ensureAccessLink(card,module,deck){
    const actions=card.querySelector('.actions');
    if(!actions) return null;

    let link=actions.querySelector('a.open-slide, .open-slide');
    if(link && link.tagName!=='A'){
      const replacement=document.createElement('a');
      replacement.className=link.className;
      [...link.attributes].forEach(attr=>replacement.setAttribute(attr.name,attr.value));
      replacement.innerHTML=link.innerHTML;
      link.replaceWith(replacement);
      link=replacement;
    }

    if(!link){
      const note=actions.querySelector('.practice-note');
      link=document.createElement('a');
      link.className='btn small open-slide';
      link.innerHTML='<i class="ri-presentation-line" aria-hidden="true"></i> Acessar aula';
      if(note) note.replaceWith(link); else actions.prepend(link);
    }

    link.href='#';
    link.dataset.lessonModule=module;
    link.dataset.slideId=deck.sourceId;
    link.dataset.slideUrl=deck.pdf;
    link.dataset.internalLesson='true';
    link.removeAttribute('target');
    link.removeAttribute('download');
    link.setAttribute('role','button');
    link.setAttribute('aria-label',`Assistir aula nesta página: ${deck.title}`);
    return link;
  }

  function applyCanonicalDecks(){
    Object.entries(DECKS).forEach(([module,deck])=>{
      const card=document.querySelector(`#cards article[data-module="${module}"]`);
      if(card) ensureAccessLink(card,module,deck);
    });
  }

  function applyCardImages(){
    Object.entries(CARD_IMAGES).forEach(([module,cfg])=>{
      const img=document.querySelector(`#cards article[data-module="${module}"] .media img`);
      if(!img) return;
      img.removeAttribute('srcset');
      img.removeAttribute('sizes');
      img.alt=cfg.alt;
      img.decoding='async';
      img.loading='lazy';
      img.dataset.catsImageSource='Pinterest';
      img.onerror=()=>{
        if(img.src!==cfg.fallback){img.onerror=null;img.src=cfg.fallback;}
      };
      img.src=cfg.original;
    });
  }

  function hardenViewer(viewer,frame){
    document.getElementById('openExternal')?.remove();
    document.getElementById('downloadOriginalPptx')?.remove();
    viewer?.querySelectorAll('.controls a[target="_blank"], .controls a[download]').forEach(el=>el.remove());
    frame.setAttribute('allowfullscreen','');
    frame.setAttribute('referrerpolicy','strict-origin-when-cross-origin');
  }

  function openLesson(link){
    const module=link.dataset.lessonModule;
    const deck=DECKS[module];
    if(!deck) return;

    const viewer=document.getElementById('slidesViewer');
    const frame=document.getElementById('slidesFrame');
    const heading=document.getElementById('slidesTitle');
    const prev=document.getElementById('prevSlide');
    const next=document.getElementById('nextSlide');
    const tip=viewer?.querySelector('.tip');
    if(!viewer || !frame || !heading) return;

    heading.textContent=deck.title;
    frame.src=lessonPreview(deck);
    frame.title=`Aula ${module} do VIII CATS — ${deck.title}`;
    hardenViewer(viewer,frame);
    if(prev) prev.hidden=true;
    if(next) next.hidden=true;
    if(tip) tip.textContent='Use o visualizador para avançar e retornar entre os slides. A aula permanece dentro do portal.';
    if(!viewer.open) viewer.showModal();
    document.documentElement.style.overflow='hidden';
    setTimeout(()=>frame.focus(),120);
  }

  /* Vídeos de apoio: players YouTube inline, sem pasta intermediária. */
  const VIDEO_ALLOW='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';

  function installATSVideoStyles(){
    if(document.getElementById('ats-video-parity-style')) return;
    const style=document.createElement('style');
    style.id='ats-video-parity-style';
    style.textContent=`
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
      @media(max-width:640px){#videos[data-ats-video-parity="true"]{padding-top:12px}#videos[data-ats-video-parity="true"] .videos-box{grid-template-columns:1fr;gap:12px;margin-top:14px}#videos[data-ats-video-parity="true"] .video-card{border-width:1px;box-shadow:none}#videos[data-ats-video-parity="true"] .video-body{padding:12px 13px}}
      @media(prefers-reduced-motion:reduce){#videos[data-ats-video-parity="true"] .video-card{transition:none}}
    `;
    document.head.appendChild(style);
  }

  function normalizeVideoCard(sourceCard){
    const iframe=sourceCard.querySelector('iframe');
    if(!iframe) return null;
    const title=sourceCard.querySelector('.video-title, .video-body h3')?.textContent?.trim()||iframe.title||'Vídeo de apoio';
    const description=sourceCard.querySelector('.video-desc, .video-body p')?.textContent?.trim()||'Conteúdo selecionado para revisão e aprofundamento.';
    iframe.classList.remove('video-embed');
    iframe.loading='lazy';
    iframe.title=title;
    iframe.setAttribute('allow',VIDEO_ALLOW);
    iframe.setAttribute('allowfullscreen','');
    iframe.setAttribute('referrerpolicy','strict-origin-when-cross-origin');
    iframe.removeAttribute('width');
    iframe.removeAttribute('height');
    const article=document.createElement('article'); article.className='video-card';
    const frame=document.createElement('div'); frame.className='video-frame'; frame.appendChild(iframe);
    const body=document.createElement('div'); body.className='video-body';
    const heading=document.createElement('h3'); heading.textContent=title;
    const paragraph=document.createElement('p'); paragraph.textContent=description;
    body.append(heading,paragraph); article.append(frame,body); return article;
  }

  function applyATSVideoExperience(){
    const section=document.getElementById('videos');
    if(!section || section.dataset.atsVideoParity==='true') return;
    const sourceCards=[...section.querySelectorAll('#videosGrid .card, .video-grid .card, .video-card')];
    const normalized=sourceCards.map(normalizeVideoCard).filter(Boolean);
    if(!normalized.length) return;
    section.dataset.atsVideoParity='true';
    section.setAttribute('aria-labelledby','videos-title');
    const head=document.createElement('div'); head.className='ats-video-head';
    head.innerHTML='<span class="ats-video-kicker">Vídeos</span><h2 class="ats-video-title" id="videos-title">Vídeos de apoio</h2><p class="ats-video-text">Conteúdos selecionados para revisão e aprofundamento, reproduzidos diretamente nesta página.</p>';
    const box=document.createElement('div'); box.className='videos-box'; box.setAttribute('aria-label','Vídeos selecionados');
    normalized.forEach(card=>box.appendChild(card));
    section.replaceChildren(head,box); installATSVideoStyles();
  }

  function hardenInlineMedia(){
    document.querySelectorAll('audio, video').forEach(media=>{
      media.setAttribute('controlsList','nodownload noremoteplayback');
      media.setAttribute('disableRemotePlayback','');
      media.setAttribute('draggable','false');
      const block=event=>{event.preventDefault();event.stopPropagation();};
      media.addEventListener('contextmenu',block,true);
      media.addEventListener('dragstart',block,true);
    });
  }

  applyCanonicalDecks();
  applyCardImages();
  applyATSVideoExperience();
  hardenInlineMedia();

  document.addEventListener('click',event=>{
    const link=event.target.closest?.('a.open-slide[data-internal-lesson="true"]');
    if(!link) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    openLesson(link);
  },true);

  window.CATSPousoAlegreOriginalDecks=DECKS;
  window.CATSPousoAlegreInlineDeckMode=Object.freeze({inline:true,externalNavigation:false,downloadButton:false,viewer:'local-pdf',lessons:8});
  window.CATSPousoAlegreVideoMode=Object.freeze({pattern:'ATS-inline-youtube',directPlay:true,folderGate:false,aspectRatio:'16/9',desktopColumns:3,mobileColumns:1,downloadOffered:false});
})();