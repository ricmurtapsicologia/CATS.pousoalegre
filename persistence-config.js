// CATS pré-curso — endpoint de verificação de persistência.
// FAIL-CLOSED: a interface só acusa preenchimento concluído após confirmação positiva deste verificador.
(() => {
  'use strict';

  const ENDPOINT = 'https://script.google.com/macros/s/AKfycbzOINm3ehG2ojEuSyFSYIuOfKciTGTg37GZ4lvC_AKfV0_00nU4GU8uxFwOpgefPTE/exec';

  window.CATS_PERSISTENCE_VERIFY_URL = ENDPOINT;

  // Hotfix 2026-09-18 r8:
  // O verificador v1.x aplicava um corte temporal baseado em Date.now() do notebook.
  // Qualquer relógio local adiantado podia fazer o backend interromper a varredura
  // antes de comparar a linha que já estava gravada na planilha. A identidade da
  // resposta já é protegida pelo fingerprint + IDs oficiais; portanto o cliente
  // deixa de enviar seu relógio como critério de exclusão.
  window.__CATS_PERSISTENCE_VERIFY__ = async payload => {
    const requestPayload = {
      ...payload,
      submittedAtEpochMs: 0,
    };

    try {
      const response = await fetch(ENDPOINT, {
        method: 'POST',
        headers: {'Content-Type': 'text/plain;charset=UTF-8'},
        body: JSON.stringify(requestPayload),
        cache: 'no-store',
        credentials: 'omit',
        redirect: 'follow',
      });

      if (!response.ok) {
        return {persisted: false, terminal: false, reason: `http-${response.status}`};
      }
      return await response.json();
    } catch (error) {
      console.warn('[CATS persistence hotfix] verifier request failed', error);
      return {persisted: false, terminal: false, reason: 'network-error'};
    }
  };

  // Janela curta o suficiente para não deixar o aluno preso, mas suficiente para
  // cold start do Apps Script e consistência eventual Forms -> Sheets.
  window.__CATS_PERSISTENCE_VERIFY_TIMEOUT__ = 20000;
})();
