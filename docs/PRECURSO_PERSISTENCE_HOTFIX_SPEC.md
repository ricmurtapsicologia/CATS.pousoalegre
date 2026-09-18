# SPEC — CATS Pré-curso: confirmação de persistência

Data: 2026-09-18
Status: hotfix r8

## Problema pinpointado

A resposta era efetivamente gravada na planilha oficial, mas a página permanecia em "Envio sem confirmação". O verificador usava `submittedAtEpochMs = Date.now()` do navegador e o backend aplicava um corte temporal de 2 minutos antes de comparar o fingerprint. Se o relógio do notebook estivesse adiantado, ou houvesse qualquer divergência relevante entre relógio local e timestamp da planilha, a varredura podia executar `break` antes de alcançar/comparar a linha já persistida.

Além disso, a configuração havia ampliado o timeout visual para 120 segundos. Isso não corrigia a causa raiz e piorava a UX: o aluno podia ficar até 2 minutos esperando uma confirmação que nunca viria.

## Evidência observada

- A interface exibiu "gravação ... NÃO foi confirmada".
- A mesma submissão já estava materializada na planilha oficial.
- Form e Sheet IDs estavam corretos.
- O fingerprint usa nome, e-mail, CPF e data de preenchimento; a falha estava no filtro temporal anterior à comparação, não na existência da linha.

## Requisitos do hotfix

1. O cliente não pode usar o relógio local como critério de exclusão de uma resposta persistida.
2. O sistema permanece fail-closed: HTTP 200 do Google Forms, load do iframe ou resposta do endpoint sem `persisted=true` não concluem o preenchimento.
3. O sucesso só é mostrado quando o verificador devolve simultaneamente:
   - protocolo esperado;
   - Form ID oficial;
   - Sheet ID oficial;
   - fingerprint idêntico;
   - `persisted=true`.
4. O cliente deve neutralizar `submittedAtEpochMs` para compatibilidade imediata com o verificador v1.x já implantado.
5. O timeout de UX deve ser de 20 s, não 120 s.
6. Após timeout, o formulário continua não concluído e oferece nova verificação sem reenviar os dados.
7. Nenhum dado clínico ou PII adicional deve ser exposto pelo endpoint de confirmação.

## Hotfix aplicado

`persistence-config.js` agora intercepta a chamada do verificador e envia `submittedAtEpochMs: 0`. Isso força o backend v1.x implantado a varrer as linhas recentes sem usar o relógio do notebook como barreira. A confirmação continua vinculada ao fingerprint e aos IDs oficiais.

Timeout máximo da tentativa automática: 20 s.

## Backend hardening recomendado

Na próxima implantação do Apps Script, remover definitivamente o `break` baseado em `lowerBound` antes do cálculo do fingerprint. O timestamp pode ser usado para telemetria/diagnóstico, mas não como condição que impeça a comparação de uma linha candidata.

## Critérios de aceite

- Uma linha já presente entre as últimas respostas é confirmada mesmo que o relógio do navegador esteja artificialmente +10 minutos.
- Uma resposta inexistente nunca mostra sucesso.
- Form ID incorreto, Sheet ID incorreto ou fingerprint incorreto nunca mostram sucesso.
- O POST ao `formResponse` isoladamente nunca mostra sucesso.
- O usuário não precisa reenviar a resposta para tentar nova confirmação.
- Smoke e E2E existentes permanecem verdes após o hotfix.
