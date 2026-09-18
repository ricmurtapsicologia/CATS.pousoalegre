# SPEC — CATS Pré-curso · confirmação de persistência

## Pinpoint

- Página pública: `precurso.html`, carregando `legacy.html` em iframe same-origin.
- Google Form oficial, ID de edição: `1107fjdaiL42Zb0n2jNjKr0aiNNysyEADQCesdBTbD_E`.
- Endpoint de submissão: `https://docs.google.com/forms/d/e/1FAIpQLScVj6HESm2cWDN3sNQCaoNOtWSKini7NbSHgiTXemwlyvqAXg/formResponse`.
- Planilha oficial: `1wQ0nc6TmCqqbu-ZqloIRLptO6iHqDhD00qrFLxP-fUk`, aba `Respostas ao formulário 1`.
- Verificador: Web App configurado em `persistence-config.js`.

## Defeito raiz original — falso positivo

`legacy.html` tratava qualquer `load` do iframe `google-response` como sucesso. Um HTTP 200 ou qualquer documento carregado no iframe podia mostrar “Envio concluído” sem comprovar persistência. O hotfix r7 mudou o fluxo para fail-closed: somente a existência da linha na planilha oficial libera sucesso.

## Defeito de produção identificado em 18/09/2026 — falso negativo por timeout

O primeiro gate usava uma janela fixa de apenas 18 segundos (`VERIFY_TIMEOUT_MS=18000`). Em produção, a resposta de teste foi materializada na planilha oficial, mas a interface já havia expirado a janela de verificação e exibido “gravação NÃO foi confirmada”. Portanto:

- o POST ao Google Forms funcionou;
- a linha foi efetivamente persistida na Sheet;
- a falha ocorreu apenas na camada de confirmação/UX;
- o estado exibido ao usuário era um falso negativo, não perda de dados.

A janela máxima agora é sobrescrita em `persistence-config.js` para 120 segundos. Isso não atrasa um sucesso: a confirmação continua ocorrendo no primeiro polling positivo; apenas evita encerrar prematuramente enquanto Google Forms/Sheets ainda convergem.

## Invariantes

1. `load` de `formResponse` sozinho nunca libera sucesso.
2. `#success` permanece bloqueado até `data-persistence-confirmed="true"`.
3. A confirmação positiva exige simultaneamente `persisted === true`, protocolo correto, Form ID correto, Sheet ID correto e fingerprint correspondente.
4. Ausência do verificador, erro de rede, ID divergente ou fingerprint divergente continuam fail-closed.
5. `row-not-yet-visible` é transitório durante a janela de consistência e deve ser reconsultado automaticamente.
6. O botão “Verificar gravação” apenas repete a conferência e nunca reenvia o formulário.
7. Timeout nunca deve gerar novo POST automaticamente.
8. A mensagem “Preenchimento confirmado” só aparece depois de a planilha conter a linha correspondente.

## Janela de consistência

- polling-base: 1,2 s;
- janela máxima de produção: 120 s;
- sucesso: encerra imediatamente no primeiro retorno positivo;
- timeout: mantém fail-closed e permite verificação manual, sem duplicar submissão.

## Contrato do verificador

Requisição `POST text/plain`:

```json
{
  "protocol": "cats-persistence-v1",
  "formEditId": "1107fjdaiL42Zb0n2jNjKr0aiNNysyEADQCesdBTbD_E",
  "sheetId": "1wQ0nc6TmCqqbu-ZqloIRLptO6iHqDhD00qrFLxP-fUk",
  "submittedAtEpochMs": 0,
  "fingerprint": "sha256(...)"
}
```

Resposta positiva:

```json
{
  "protocol": "cats-persistence-v1",
  "persisted": true,
  "terminal": true,
  "formEditId": "1107fjdaiL42Zb0n2jNjKr0aiNNysyEADQCesdBTbD_E",
  "sheetId": "1wQ0nc6TmCqqbu-ZqloIRLptO6iHqDhD00qrFLxP-fUk",
  "fingerprint": "mesmo fingerprint"
}
```

## Gates obrigatórios

- Smoke estrutural: IDs oficiais, campos obrigatórios mapeados e guard instalado.
- Smoke live negativo: fingerprint inexistente deve retornar `persisted=false` e `row-not-yet-visible`.
- Smoke live positivo: uma fixture sintética já existente na planilha deve retornar `persisted=true` sem escrever nova linha.
- E2E negativo: HTTP 200 do `formResponse` sem confirmação não pode mostrar sucesso.
- E2E positivo: confirmação correta deve mostrar “Preenchimento confirmado”.
- Regressão de duplicidade: verificação/retry nunca pode disparar um segundo POST.
- Gate de consistência: configuração de produção deve manter janela >= 60 s; valor atual = 120 s.

## Critério de fechamento

A missão só fecha quando smoke live negativo, smoke live positivo e E2E estiverem verdes. O E2E positivo mockado, sozinho, não é evidência suficiente de reconhecimento real da Sheet.
