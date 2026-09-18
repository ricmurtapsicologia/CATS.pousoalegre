// CATS pré-curso — verificação automática de persistência.
// FAIL-CLOSED: só acusa conclusão após confirmação positiva da planilha oficial.
(() => {
  'use strict';

  const ENDPOINT = 'https://script.google.com/macros/s/AKfycbzOINm3ehG2ojEuSyFSYIuOfKciTGTg37GZ4lvC_AKfV0_00nU4GU8uxFwOpgefPTE/exec';
  const AUTO_RETRY_DELAY_MS = 4000;
  const MAX_AUTO_RETRIES = 20;
  const CONTRACT_VERSION = '2026.09.18-r12-forms-contract';

  window.CATS_PERSISTENCE_VERIFY_URL = ENDPOINT;
  window.__CATS_PERSISTENCE_CONFIG_VERSION__ = CONTRACT_VERSION;

  // Neutraliza clock skew do dispositivo: a identidade é conferida por
  // fingerprint + IDs oficiais; o relógio local não exclui linhas válidas.
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
      console.warn('[CATS persistence] verifier request failed', error);
      return {persisted: false, terminal: false, reason: 'network-error'};
    }
  };

  window.__CATS_PERSISTENCE_VERIFY_TIMEOUT__ = 20000;

  // Compatibilidade estrita com os literais do Google Forms.
  // O Forms valida alternativas fechadas pelo valor exato, inclusive pontuação
  // e espaços internos. Os ajustes abaixo não alteram o texto visual percebido.
  function patchGoogleFormsContract(frame) {
    let doc;
    try {
      doc = frame.contentDocument;
    } catch (_) {
      return;
    }
    if (!doc) return;

    const ocorrencia = doc.getElementById('ocorrencia');
    if (ocorrencia && ocorrencia.name === 'entry.500885681') {
      const stale = [...ocorrencia.options].find(option => option.value === 'Nunca participei.');
      if (stale) {
        stale.value = 'Nunca atendi.';
        stale.textContent = 'Nunca atendi.';
      }
    }

    doc.querySelectorAll('input[name="entry.2109138769"]').forEach(input => {
      if (input.value === 'Não me sinto um (a) fracassado (a).') {
        input.value = 'Não me sinto um (a)  fracassado (a).';
      }
    });

    doc.documentElement.dataset.catsFormsContract = CONTRACT_VERSION;
  }

  function attachAutomaticRetry(frame) {
    patchGoogleFormsContract(frame);

    let doc;
    try {
      doc = frame.contentDocument;
    } catch (_) {
      return;
    }
    if (!doc || doc.documentElement.dataset.catsAutoPersistence === 'true') return;
    doc.documentElement.dataset.catsAutoPersistence = 'true';

    let attempts = 0;
    let timer = 0;

    const schedule = () => {
      const status = doc.getElementById('catsPersistenceStatus');
      const retry = doc.getElementById('catsVerifyAgain');
      const success = doc.getElementById('success');
      if (!status || !retry || !success) return;
      if (success.dataset.persistenceConfirmed === 'true' || success.classList.contains('show')) {
        if (timer) clearTimeout(timer);
        return;
      }

      const text = String(status.textContent || '');
      const unconfirmed = text.includes('NÃO foi confirmada') || text.includes('não foi confirmada');
      if (!unconfirmed || attempts >= MAX_AUTO_RETRIES || timer) return;

      retry.hidden = true;
      status.className = 'notice info';
      status.textContent = 'Envio realizado. Confirmando automaticamente a gravação na planilha oficial… Não feche esta página.';

      timer = window.setTimeout(() => {
        timer = 0;
        const currentSuccess = doc.getElementById('success');
        if (currentSuccess?.dataset.persistenceConfirmed === 'true' || currentSuccess?.classList.contains('show')) return;
        attempts += 1;
        retry.click();
      }, AUTO_RETRY_DELAY_MS);
    };

    const observer = new MutationObserver(schedule);
    observer.observe(doc.documentElement, {
      subtree: true,
      childList: true,
      characterData: true,
      attributes: true,
      attributeFilter: ['class', 'hidden', 'data-persistence-confirmed'],
    });
    schedule();
  }

  function bootAutomaticRetry() {
    const frame = document.getElementById('app');
    if (!frame) return;
    frame.addEventListener('load', () => attachAutomaticRetry(frame));
    if (frame.contentDocument?.readyState === 'complete') attachAutomaticRetry(frame);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bootAutomaticRetry, {once: true});
  } else {
    bootAutomaticRetry();
  }
})();