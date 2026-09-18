# SPEC — CATS Pré-curso · confirmação de persistência

## Pinpoint

- Página pública: `precurso.html` (carrega `legacy.html` em iframe same-origin).
- Google Form oficial informado pelo coordenador, ID de edição: `1107fjdaiL42Zb0n2jNjKr0aiNNysyEADQCesdBTbD_E`.
- Endpoint publicado atualmente usado pela página: `https://docs.google.com/forms/d/e/1FAIpQLScVj6HESm2cWDN3sNQCaoNOtWSKini7NbSHgiTXemwlyvqAXg/formResponse`.
- Planilha oficial de respostas: `1wQ0nc6TmCqqbu-ZqloIRLptO6iHqDhD00qrFLxP-fUk` · aba `Respostas ao formulário 1`.

## Defeito raiz

`legacy.html` tratava qualquer evento `load` do iframe `google-response` como sucesso. Um HTTP 200 sintético, uma página de erro ou qualquer resposta carregada no iframe era suficiente para esconder o formulário e mostrar “Envio concluído”. O E2E anterior repetia exatamente esse falso positivo: interceptava `/formResponse`, devolvia HTML 200 e considerava o fluxo aprovado, sem conferir Google Forms nem Google Sheets.

## Invariantes do hotfix

1. `load` de `formResponse` sozinho nunca libera sucesso.
2. `#success` fica bloqueado por CSS enquanto não existir `data-persistence-confirmed="true"`.
3. A confirmação positiva exige simultaneamente:
   - `persisted === true`;
   - protocolo `cats-persistence-v1`;
   - `formEditId === 1107fjdaiL42Zb0n2jNjKr0aiNNysyEADQCesdBTbD_E`;
   - `sheetId === 1wQ0nc6TmCqqbu-ZqloIRLptO6iHqDhD00qrFLxP-fUk`;
   - `fingerprint` igual ao calculado no navegador para NOME + melhor e-mail + CPF + data de preenchimento.
4. Ausência do verificador, erro de rede, timeout, ID divergente ou fingerprint divergente = **fail closed**: o formulário continua visível e a página declara explicitamente que o preenchimento NÃO está confirmado.
5. O botão “Verificar gravação” repete apenas a conferência; não faz novo POST e não cria duplicidade.
6. A mensagem “Preenchimento confirmado” só aparece depois de a planilha oficial conter a linha correspondente.

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
  "formEditId": "1107fjdaiL42Zb0n2jNjKr0aiNNysyEADQCesdBTbD_E",
  "sheetId": "1wQ0nc6TmCqqbu-ZqloIRLptO6iHqDhD00qrFLxP-fUk",
  "fingerprint": "mesmo fingerprint"
}
```

O código de referência está em `apps-script/CATS_PersistenceVerifier.gs`. Ele também confere, via `FormApp.openById()`, se o Form oficial está efetivamente vinculado à planilha oficial antes de liberar qualquer resposta positiva.

## Ativação positiva em produção

1. Criar/deployar o Apps Script como Web App, executando como o proprietário e com acesso restrito ao necessário.
2. Copiar a URL `/exec` do deployment.
3. Preencher essa URL em `persistence-config.js`.
4. Rodar `scripts/e2e_precurso.py` e o workflow `CATS Pré-curso — Smoke e E2E`.

Enquanto `persistence-config.js` estiver vazio, o comportamento é deliberadamente fail-closed: o POST pode acontecer, mas a página não declara conclusão.

## Gates

- Smoke: IDs oficiais fixos, guard instalado, nenhum campo obrigatório sem `name`, nenhum `temp_`.
- E2E negativo: `/formResponse` retorna HTTP 200, mas verificador aponta planilha errada → sucesso deve permanecer invisível.
- E2E positivo: mesmo POST + confirmação com planilha/form/fingerprint corretos → sucesso visível e formulário oculto.
