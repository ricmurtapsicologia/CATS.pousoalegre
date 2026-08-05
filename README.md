# CATS — Inscrição personalizada

Página customizada para inscrição no Curso de Atendimento a Tentativas de Suicídio (CATS), com interface própria e integração preparada para envio ao Google Forms.

## Estrutura

- `index.html`: aplicação web responsiva, em etapas.
- Integração: Google Forms via `formResponse` em iframe oculto.
- Sem elementos visuais do Google Forms para o participante.

## Situação da integração

Os campos administrativos já estão mapeados para os `entry.xxxxx` fornecidos pelo formulário. Dois identificadores não vieram no link pré-preenchido recebido: o campo sobre experiência prévia em ocorrência e o item clínico de irritabilidade. O bloco clínico está estruturado, mas o conteúdo literal do instrumento padronizado não é redistribuído neste repositório.

A interface impede envio enquanto a configuração obrigatória estiver incompleta, evitando respostas parciais ou corrompidas.

## GitHub Pages

Após os arquivos estarem no branch `main`, em **Settings → Pages**, selecione **Deploy from a branch**, branch `main`, pasta `/ (root)`.
