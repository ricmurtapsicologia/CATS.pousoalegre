# CATS 2026 — Inscrição personalizada

Página responsiva para inscrição e levantamento prévio do CATS 2026, com interface própria e envio ao Google Forms sem exibir a interface do Google ao participante.

## Arquitetura

- `index.html`: camada principal mobile-first e adaptadora da interface.
- `legacy.html`: preserva a implementação funcional e o conteúdo já existente do formulário.
- `assets/cats2026-banner.webp`: banner oficial exibido no cabeçalho.
- Google Forms: envio por `POST` ao endpoint `formResponse`, usando iframe oculto.

A camada principal converte os campos de Posto/Graduação e Tempo de Serviço em listas suspensas, configura as listas de experiência prévia e exposição a ocorrências, e aplica os identificadores Google Forms que faltavam (`entry.500885681` e `entry.327261555`). Também acrescenta os metadados de navegação do Forms necessários ao envio das seções.

## Responsividade

A interface foi ajustada em abordagem mobile-first, com controles de no mínimo 48 px, tipografia adequada a telas pequenas e expansão progressiva para tablets e desktops.

## Publicação

O GitHub Pages deve usar o branch `main` e a pasta `/ (root)`.

## Validação operacional

Como o envio ocorre entre origens diferentes, o navegador não permite que a página leia o conteúdo da resposta retornada pelo Google. Antes da divulgação definitiva, deve ser realizada uma submissão controlada e confirmada diretamente na aba **Respostas** do Google Forms ou na planilha vinculada.
