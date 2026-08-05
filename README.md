# CATS 2026 — Inscrição personalizada

Página responsiva de inscrição e levantamento prévio do CATS 2026, com interface própria e envio direto ao Google Forms sem incorporar a interface visual do Google.

## Arquitetura

- `index.html`: camada adaptadora, validação de integração, identidade visual e ajustes mobile-first.
- `legacy.html`: preserva o conteúdo e a lógica funcional do formulário.
- Google Forms: recebe os dados por `POST` no endpoint oficial `formResponse`, por meio de iframe de resposta oculto.
- O navegador não grava respostas em `localStorage`, `sessionStorage` nem no repositório.

A solução permanece deliberadamente sem framework JavaScript. Para uma página estática hospedada no GitHub Pages, JavaScript nativo reduz dependências, superfície de falha, peso de carregamento e manutenção sem perder funcionalidade.

## Identidade visual

O cabeçalho utiliza o mesmo conceito visual da página `Curso-ATS`: fundo escuro institucional, amarelo de destaque e a mesma imagem de hero. A imagem é aplicada como `background-size: cover`, com posicionamento responsivo, evitando deformação ou esticamento em celular e notebook.

## Integração com Google Forms

A camada adaptadora:

1. fixa o endpoint oficial do Google Forms;
2. aplica os identificadores `entry.*` aos campos da interface;
3. corrige os campos que não possuíam mapeamento direto;
4. inclui os campos técnicos `fvv`, `pageHistory` e `submit` necessários ao fluxo atual;
5. impede a inicialização do formulário se houver campo obrigatório sem identificação ou campo temporário sem mapeamento;
6. mantém o envio por `POST`, evitando que dados pessoais sejam colocados na URL.

O participante preenche somente a página personalizada. No envio, os valores são encaminhados ao Google Forms correspondente.

## Responsividade e acessibilidade

A página foi ajustada com abordagem mobile-first, controles com altura mínima de 48 px, tipografia de 16 px nos campos, foco visível, `viewport-fit=cover`, suporte a `prefers-reduced-motion` e adaptação específica para telas estreitas.

## Publicação

O GitHub Pages deve utilizar o branch `main` e a pasta `/ (root)`.

## Validação operacional

Por segurança, não foi criada resposta fictícia no formulário. Como a resposta do Google ocorre em outra origem, a página não consegue confirmar o conteúdo retornado pelo Google Forms. Antes da divulgação definitiva, faça uma submissão controlada com dados de teste autorizados e confirme o registro na aba **Respostas** do formulário ou na planilha vinculada.
