# CATS 2026 — Inscrição | Pouso Alegre

Página responsiva para inscrição e levantamento prévio do CATS 2026, com interface própria e envio ao Google Forms sem exibir a interface do Google ao participante.

## Identidade e apresentação

- Título público: `CATS 2026 | Inscrição — Pouso Alegre`.
- Identidade visual alinhada ao ambiente do Curso ATS/CBMMG: azul institucional, fundo escuro no hero e amarelo de destaque.
- Hero responsivo com imagem em `background-size: cover`, evitando deformação da fotografia em celular ou desktop.
- Informações técnicas de implementação foram retiradas da comunicação principal e substituídas por identificação institucional e contexto do formulário.
- Rodapé institucional: `© 2026 CBMMG — Equipe de Coordenação do CATS. Todos os direitos reservados.`

O símbolo `©` foi utilizado por ser o sinal adequado para indicação de direitos autorais. O símbolo `®` é reservado à indicação de marca registrada.

## Compartilhamento em WhatsApp e redes sociais

O `index.html` possui metadados Open Graph e Twitter Card próprios para compartilhamento do link.

A imagem social utilizada é a mesma fotografia operacional selecionada na página do Curso ATS:

`https://i.pinimg.com/736x/56/4d/63/564d63712210ee0e48975b8c57392db7.jpg`

Foram definidos `og:title`, `og:description`, `og:url`, `og:image`, `og:image:alt`, `twitter:card`, `twitter:title`, `twitter:description` e `twitter:image`.

Observação: WhatsApp, Facebook e outros serviços podem manter cache do preview de links já compartilhados. Uma alteração no Open Graph pode demorar a aparecer em mensagens que reutilizam a mesma URL.

## Arquitetura

- `index.html`: camada principal, responsável pela identidade visual, metadados sociais, configuração da integração, validações de mapeamento e adaptação da interface.
- `legacy.html`: preserva a implementação funcional e o conteúdo original do formulário multipasso.
- Google Forms: recebe os dados por `POST` no endpoint `formResponse`, através de iframe de resposta oculto.

A separação entre a camada adaptadora e o formulário funcional reduz o risco de regressão na integração enquanto permite evoluir design e identidade visual sem reescrever toda a lógica do formulário.

Não foram adicionados frameworks de interface ou bibliotecas JavaScript externas. Para uma página estática hospedada no GitHub Pages, HTML, CSS e JavaScript nativos reduzem dependências, peso, superfície de falha e custo de manutenção.

Não há arquitetura de prompt ou modelo generativo em execução nesta página; portanto, adicionar bibliotecas de engenharia de prompt não traria benefício técnico ao projeto.

## Integração com Google Forms

O formulário envia diretamente para:

`https://docs.google.com/forms/d/e/1FAIpQLScVj6HESm2cWDN3sNQCaoNOtWSKini7NbSHgiTXemwlyvqAXg/formResponse`

A camada principal mantém o mapeamento explícito dos campos para os respectivos identificadores `entry.*`, incluindo os campos que necessitam de correção dinâmica. Também acrescenta os parâmetros de navegação usados pelo Forms (`fvv`, `pageHistory` e `submit`).

Antes de liberar o envio, a página verifica se existem campos obrigatórios sem `name`, campos temporários ainda não mapeados ou divergências nos identificadores principais. Isso evita falhas silenciosas de integração.

## Privacidade e armazenamento

- O envio é feito por `POST`, evitando colocar as respostas na URL.
- A página não grava respostas no GitHub.
- A página não utiliza `localStorage` ou `sessionStorage` para armazenar as respostas do participante.
- O Google Forms continua sendo o destino dos dados preenchidos.

## Responsividade e acessibilidade

A interface segue abordagem mobile-first:

- campos e botões com área de toque mínima adequada;
- fonte de 16 px nos controles para evitar zoom automático em navegadores móveis;
- layout adaptável para telas estreitas;
- foco visível para navegação por teclado;
- suporte a `prefers-reduced-motion`;
- `viewport-fit=cover` e respeito à safe area no rodapé;
- contraste reforçado nos elementos principais.

## Publicação

O GitHub Pages deve permanecer configurado para o branch `main` e a pasta `/ (root)`.

URL pública:

`https://ricmurtapsicologia.github.io/CATS.pousoalegre/`

O nome do repositório não foi alterado para preservar a URL pública já distribuída. A identidade exibida ao usuário, no navegador e no compartilhamento social foi aprimorada sem quebrar links existentes.

## Validação operacional

Como o envio ocorre entre origens diferentes, o navegador não permite que a página leia o conteúdo da resposta retornada pelo Google. Antes da divulgação definitiva, deve ser feita uma submissão controlada e confirmada diretamente na aba **Respostas** do Google Forms ou na planilha vinculada.
