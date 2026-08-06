# VIII CATS 2026 — Boas-vindas | Pouso Alegre

Página responsiva de boas-vindas e levantamento prévio do CATS 2026 em Pouso Alegre, com interface própria e envio ao Google Forms.

## Estado atual

A renderização foi refatorada para eliminar o iframe visual que causava divergência entre a página publicada e o conteúdo atualizado. O `index.html` agora carrega o formulário-base de `legacy.html` com `fetch`, aplica as adaptações antes da renderização e escreve o resultado no DOM principal da página. Dessa forma, o banner, o formulário e os estilos passam a existir no mesmo documento visual, evitando sobreposição de CSS entre dois contextos de página.

Build atual: `2026.08.06-r2`.

O build também é registrado em `<meta name="cats-build">` e em `data-cats-build` no elemento `<html>`, permitindo identificar objetivamente qual versão foi publicada pelo GitHub Pages.

## Banner oficial

A versão atual do hero utiliza uma única ocorrência de `VIII`:

- identificação institucional: `CBMMG • 7ª Cia Ind - Pouso Alegre`;
- edição: `Boas-vindas • VIII Edição`;
- título: `Curso de Atendimento a Tentativas de Suicídio`;
- abertura: `Seja bem-vindo(a).`;
- assinatura: `Lucas Antônio de Oliveira, Capitão BM — Coordenador do CATS`.

A duplicação de `VIII` foi removida do texto de boas-vindas e da assinatura.

## Correção tipográfica

O hero não usa mais altura mínima fixa para tentar acomodar o conteúdo. A composição utiliza altura automática, espaçamento vertical entre blocos, `line-height` ampliado, `letter-spacing` menos agressivo e tamanho tipográfico responsivo.

No mobile:

- o título usa `line-height` de aproximadamente `1.13`;
- o texto utiliza `line-height` de aproximadamente `1.62`;
- a altura do card é definida pelo conteúdo;
- identificação, edição, título, mensagem, obrigatoriedade e assinatura possuem espaços próprios;
- os controles mantêm área de toque adequada e fonte mínima de 16 px.

Isso elimina o efeito de tipografia encavalada em telas estreitas.

## Arquitetura

Arquivos necessários:

- `index.html`: camada pública, metadados, carregamento, normalização visual e integração do formulário no DOM principal;
- `legacy.html`: formulário-base e lógica funcional já homologada com o Google Forms;
- `.nojekyll`: publicação estática direta no GitHub Pages;
- `README.md`: documentação técnica.

O `legacy.html` permanece temporariamente como motor funcional para preservar os campos e a lógica de envio já existentes. Ele não é mais exibido dentro de um iframe visual.

## Integração com Google Forms

O envio permanece direcionado ao endpoint `formResponse` já utilizado pelo projeto. A refatoração preserva os identificadores dos campos e aplica os mapeamentos específicos necessários antes da renderização.

Também permanecem os parâmetros auxiliares `fvv`, `pageHistory` e `submit`.

O botão final foi padronizado para `Enviar formulário`, e a confirmação visual utiliza `Envio concluído`.

## Cache e publicação

O carregamento do formulário-base utiliza `cache: no-store` e inclui a versão do build na URL interna de `legacy.html`, reduzindo o risco de reutilização de uma cópia antiga pelo navegador.

A única fonte prevista para GitHub Pages é:

- branch: `main`;
- diretório: `/ (root)`.

URL pública:

`https://ricmurtapsicologia.github.io/CATS.pousoalegre/`

Se a página pública não apresentar `7ª Cia Ind - Pouso Alegre` e o build `2026.08.06-r2`, a causa deve ser investigada no processo de publicação do GitHub Pages, e não no HTML atual do branch `main`.

## Privacidade

- respostas não são armazenadas no GitHub;
- o formulário não utiliza `localStorage` ou `sessionStorage` para guardar respostas;
- o envio ocorre por `POST` para o Google Forms;
- `noindex` permanece habilitado para evitar indexação da página.
