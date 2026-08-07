# VIII CATS 2026 — Boas-vindas | Pouso Alegre

Página responsiva de boas-vindas e levantamento prévio do CATS 2026 em Pouso Alegre, com interface própria e envio direto ao Google Forms.

## Estado atual

Build atual: `2026.08.07-r4`.

A página pública mantém o preenchimento integral dentro da própria interface do CATS. O respondente não precisa abrir o Google Forms.

Ao acionar `Enviar formulário`, os dados são enviados por `POST` diretamente ao endpoint oficial `formResponse` do Google Forms, como uma única resposta.

## Arquitetura

Arquivos necessários:

- `index.html`: camada pública, identidade visual, adaptação mobile first, verificação de mapeamento e integração com o formulário;
- `legacy.html`: formulário-base e lógica funcional de preenchimento/envio;
- `.nojekyll`: publicação estática direta no GitHub Pages;
- `README.md`: documentação técnica.

O `legacy.html` é carregado em contexto próprio e de mesma origem. O `index.html` ajusta automaticamente a altura desse conteúdo para evitar barra de rolagem interna e preservar a aparência de página única.

Essa arquitetura preserva a lógica nativa de envio do formulário que já havia sido utilizada no projeto, sem redirecionar o respondente para a interface do Google Forms.

## Integração com Google Forms

O formulário é enviado para:

`https://docs.google.com/forms/d/e/1FAIpQLScVj6HESm2cWDN3sNQCaoNOtWSKini7NbSHgiTXemwlyvqAXg/formResponse`

Configuração aplicada no carregamento:

- método `POST`;
- destino oculto `google-response`;
- codificação `application/x-www-form-urlencoded`;
- preservação dos identificadores `entry.*` do Google Forms;
- parâmetros auxiliares `fvv`, `pageHistory` e `submit`;
- correção dos campos de seleção específicos;
- verificação automática para impedir envio caso exista campo obrigatório sem mapeamento ou identificador temporário.

O botão final permanece `Enviar formulário`. Após o envio, a interface exibe `Envio concluído` sem abrir o Google Forms para o respondente.

## Banner oficial

A versão atual mantém:

- `CBMMG • 7ª Cia Ind - Pouso Alegre`;
- `Boas-vindas • VIII Edição`;
- `Curso de Atendimento a Tentativas de Suicídio`;
- `Caros abordadores e abordadoras, sejam bem-vindos.`;
- `Lucas Antônio de Oliveira, Capitão BM — Coordenador do CATS`.

## Mobile first

A página mantém tipografia responsiva, campos com fonte mínima de 16 px, áreas de toque ampliadas e altura automática do conteúdo. A mudança de etapa reposiciona a página na área de progresso para evitar perda de contexto no celular.

## Publicação

Fonte do GitHub Pages:

- branch: `main`;
- diretório: `/ (root)`.

URL pública:

`https://ricmurtapsicologia.github.io/CATS.pousoalegre/`

## Privacidade

- respostas não são armazenadas no GitHub;
- não há uso de `localStorage` ou `sessionStorage` para guardar respostas;
- o envio ocorre diretamente para o Google Forms;
- `noindex` permanece habilitado para evitar indexação da página.
