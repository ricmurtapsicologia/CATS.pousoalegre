# VIII CATS 2026 — Boas-vindas | Pouso Alegre

Página responsiva de boas-vindas e levantamento prévio do VIII CATS 2026, com interface própria e envio ao Google Forms sem exibir a interface do Google ao participante.

## Identidade e apresentação

- Título público: `VIII CATS 2026 | Boas-vindas — Pouso Alegre`.
- Abertura destinada aos alunos já vinculados à VIII Edição, sem linguagem de inscrição.
- Mensagem inicial receptiva e objetiva, solicitando o preenchimento obrigatório do formulário de levantamento prévio.
- Assinatura institucional da abertura: `Lucas Oliveira, Capitão BM — Coordenador do VIII CATS`.
- Identidade visual alinhada ao ambiente do Curso ATS/CBMMG: azul institucional, fundo escuro no hero e amarelo de destaque.
- Hero responsivo com imagem em `background-size: cover`, evitando deformação da fotografia em celular ou desktop.
- Identificação visual da edição por `VIII Edição`, `Pouso Alegre` e `CBMMG`.
- Informações técnicas de implementação permanecem fora da comunicação principal.
- Rodapé institucional: `© 2026 CBMMG — Equipe de Coordenação do CATS. Todos os direitos reservados.`

O símbolo `©` foi utilizado por ser o sinal adequado para indicação de direitos autorais. O símbolo `®` é reservado à indicação de marca registrada.

## Compartilhamento em WhatsApp e redes sociais

O `index.html` possui metadados Open Graph e Twitter Card próprios para compartilhamento do link, atualizados para caracterizar a página como boas-vindas e levantamento prévio do VIII CATS, e não como página de inscrição.

A imagem social utilizada é a mesma fotografia operacional selecionada na página do Curso ATS:

`https://i.pinimg.com/736x/56/4d/63/564d63712210ee0e48975b8c57392db7.jpg`

Foram definidos `og:title`, `og:description`, `og:url`, `og:image`, `og:image:alt`, `twitter:card`, `twitter:title`, `twitter:description` e `twitter:image`.

Observação: WhatsApp, Facebook e outros serviços podem manter cache do preview de links já compartilhados. Uma alteração no Open Graph pode demorar a aparecer em mensagens que reutilizam a mesma URL.

## Arquitetura

- `index.html`: camada de apresentação e adaptação visual da interface.
- `legacy.html`: preserva a implementação funcional do formulário multipasso e sua configuração de envio.
- Google Forms: recebe os dados por `POST` no endpoint `formResponse`, através de iframe de resposta oculto.

A separação entre a camada visual e o formulário funcional permite evoluir identidade, responsividade e metadados sociais sem reescrever a lógica principal do formulário.

Não foram adicionados frameworks de interface ou bibliotecas JavaScript externas. Para uma página estática hospedada no GitHub Pages, HTML, CSS e JavaScript nativos reduzem dependências, peso, superfície de falha e custo de manutenção.

## Integração com Google Forms

A configuração de integração foi restaurada ao comportamento anterior que já existia no projeto, preservando o formulário funcional original em `legacy.html`.

O `index.html` não reescreve globalmente os identificadores dos campos nem força uma nova configuração do `action`, `method`, `target` e `enctype`. Ele realiza apenas as adaptações específicas já utilizadas no projeto:

- conversão de Posto/Graduação e Tempo de Serviço para listas, preservando os `name` originais;
- mapeamento de experiência prévia para `entry.500885681`;
- mapeamento de exposição a suicídio consumado para `entry.212330805`;
- mapeamento do campo temporário de irritabilidade para `entry.327261555`;
- inclusão de `fvv=1`, `pageHistory=0,1,2,3` e `submit=Submit`.

O formulário funcional continua enviando para:

`https://docs.google.com/forms/d/e/1FAIpQLScVj6HESm2cWDN3sNQCaoNOtWSKini7NbSHgiTXemwlyvqAXg/formResponse`

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
- contraste reforçado nos elementos principais;
- hero ampliado de forma responsiva para acomodar a mensagem de boas-vindas e a assinatura sem sobreposição.

## Publicação

O GitHub Pages deve permanecer configurado para o branch `main` e a pasta `/ (root)`.

URL pública:

`https://ricmurtapsicologia.github.io/CATS.pousoalegre/`

O nome do repositório não foi alterado para preservar a URL pública já distribuída.

## Validação operacional

O arquivo `legacy.html` permanece responsável pela integração funcional com o Google Forms. A alteração da abertura foi feita no `index.html`, preservando os mapeamentos e o envio já existentes.

Como o envio ocorre entre origens diferentes, o navegador não consegue confirmar pelo conteúdo da resposta se o Google Forms registrou efetivamente os dados. A homologação final deve ser feita com uma submissão controlada e conferência direta na aba **Respostas** do Google Forms ou na planilha vinculada.
