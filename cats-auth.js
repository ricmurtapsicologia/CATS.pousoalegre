(() => {
  "use strict";

  const KEY_MAP = Object.freeze({
    curso_ats_auth_v3: "cats_pa_auth_v1",
    ats_login_attempts_v3: "cats_pa_login_attempts_v1"
  });
  const PRELOAD_URL = "legacy.html?v=2026.09.09-r7";
  const LEGACY_GUARD = /<script\s+data-cats-legacy-guard=["']1["'][^>]*>[\s\S]*?<\/script>/i;
  let preloadPromise = null;
  let preloadedHtml = "";

  const storageProto = Storage.prototype;
  if (!window.__catsPaStorageMapped) {
    const original = Object.freeze({
      getItem: storageProto.getItem,
      setItem: storageProto.setItem,
      removeItem: storageProto.removeItem
    });
    const mapKey = key => KEY_MAP[String(key)] || String(key);
    storageProto.getItem = function (key) { return original.getItem.call(this, mapKey(key)); };
    storageProto.setItem = function (key, value) { return original.setItem.call(this, mapKey(key), value); };
    storageProto.removeItem = function (key) { return original.removeItem.call(this, mapKey(key)); };
    Object.defineProperty(window, "__catsPaStorageMapped", { value: true });
  }

  function loadSupplementalAuth() {
    if (document.querySelector("script[data-cats-extra-auth]")) return;
    const script = document.createElement("script");
    script.src = "https://ricmurtapsicologia.github.io/Curso-ATS/auth-extra.js?v=20260917-1";
    script.dataset.catsExtraAuth = "true";
    document.head.appendChild(script);
  }

  function hasValidSession() {
    try {
      const data = JSON.parse(sessionStorage.getItem("cats_pa_auth_v1") || "null");
      return Boolean(data && data.authenticated === true && Date.now() < Number(data.expiresAt || 0));
    } catch {
      return false;
    }
  }

  function frameHasForm(frame) {
    try {
      return Boolean(frame?.contentDocument?.getElementById("catsForm"));
    } catch {
      return false;
    }
  }

  function primeFormFrame() {
    const frame = document.getElementById("app");
    if (!frame) return Promise.resolve(false);
    if (frameHasForm(frame)) return Promise.resolve(true);

    if (!preloadPromise) {
      preloadPromise = fetch(PRELOAD_URL, { cache: "force-cache", credentials: "same-origin" })
        .then(response => {
          if (!response.ok) throw new Error(`HTTP ${response.status}`);
          return response.text();
        })
        .then(html => {
          preloadedHtml = html.replace(LEGACY_GUARD, "");
          return preloadedHtml;
        })
        .catch(error => {
          console.warn("[CATS] Pré-carregamento do formulário indisponível; usando fallback.", error);
          preloadedHtml = "";
          return "";
        });
    }

    return preloadPromise.then(html => {
      if (!html || frameHasForm(frame)) return frameHasForm(frame);
      if (frame.dataset.catsPreloadInjected === "1") return true;
      frame.dataset.catsPreloadInjected = "1";
      frame.srcdoc = html;
      return true;
    });
  }

  function navigateFallback(frame) {
    if (!frame || frame.dataset.catsRecovery === "loading") return;
    frame.dataset.catsRecovery = "loading";

    const boot = document.getElementById("boot");
    if (boot) {
      boot.hidden = false;
      boot.textContent = "Carregando formulário…";
    }
    frame.classList.remove("ready");

    const url = new URL("legacy.html", window.location.href);
    url.searchParams.set("v", "2026.09.09-r7");
    url.searchParams.set("auth", Date.now().toString(36));
    frame.src = url.href;
  }

  function recoverFormAfterAuth() {
    if (!hasValidSession()) return false;

    const frame = document.getElementById("app");
    if (!frame) return false;
    if (frameHasForm(frame)) return true;

    if (preloadedHtml) {
      frame.dataset.catsPreloadInjected = "1";
      frame.srcdoc = preloadedHtml;
      return true;
    }

    primeFormFrame().then(ok => {
      if (!ok && !frameHasForm(frame)) navigateFallback(frame);
    });
    return true;
  }

  function watchAuthenticatedForm() {
    window.addEventListener("cats:authenticated", recoverFormAfterAuth);
    if (recoverFormAfterAuth()) return;

    const timer = window.setInterval(() => {
      if (!recoverFormAfterAuth()) return;
      window.clearInterval(timer);
    }, 250);
  }

  let autoTimer = 0;
  const digits = value => String(value || "").replace(/\D/g, "");
  const setText = (root, selector, value) => {
    const node = root?.querySelector(selector);
    if (node && node.textContent !== value) node.textContent = value;
  };

  function bindAutoAccess(gate) {
    const form = gate.querySelector("#catsAuthForm");
    const input = gate.querySelector("#catsAuthInput");
    if (!form || !input) return;

    gate.querySelector("#catsAuthSubmit")?.remove();
    setText(gate, "#catsAuthHelp", "Matrícula BM/PM: 7 números. CPF cadastrado: 11 números.");

    if (input.dataset.autoAccessBound === "1") return;
    input.dataset.autoAccessBound = "1";

    const request = delay => {
      window.clearTimeout(autoTimer);
      const current = digits(input.value);
      if (current.length !== 7 && current.length !== 11) return;
      autoTimer = window.setTimeout(() => {
        if (input.disabled) return;
        const latest = digits(input.value);
        if (latest !== current) return;
        if (latest.length !== 7 && latest.length !== 11) return;
        form.requestSubmit();
      }, delay);
    };

    input.addEventListener("input", () => {
      const length = digits(input.value).length;
      window.clearTimeout(autoTimer);
      if (length === 11) request(0);
      else if (length === 7) request(550);
    });
  }

  function brandGate() {
    const gate = document.getElementById("catsAuthGate");
    if (!gate) return false;

    gate.setAttribute("aria-label", "Acesso ao VIII CATS 2026");
    setText(gate, ".cats-auth-brand span", "CBMMG • VIII CATS 2026");
    setText(gate, ".cats-auth-kicker", "Curso de Atendimento a Tentativas de Suicídio");

    const heroTitle = gate.querySelector("#catsAuthTitle");
    if (heroTitle && heroTitle.dataset.catsPa !== "1") {
      heroTitle.innerHTML = `VIII CATS <span class="cats-auth-accent">2026</span>`;
      heroTitle.dataset.catsPa = "1";
    }

    setText(gate, ".cats-auth-hero-text", "Ambiente de apoio às aulas presenciais do VIII CATS em Pouso Alegre.");
    setText(gate, ".cats-auth-hero-foot span", "Identifique-se para acessar o ambiente do curso.");
    setText(gate, ".cats-auth-eyebrow", "Acesso do aluno");

    const loginTitle = gate.querySelector("#catsAuthLoginTitle");
    if (loginTitle && loginTitle.dataset.catsPa !== "1") {
      loginTitle.innerHTML = `Entre no <span class="cats-auth-accent">VIII CATS</span>`;
      loginTitle.dataset.catsPa = "1";
    }

    setText(gate, ".cats-auth-subtitle", "Informe sua credencial de acesso.");
    setText(gate, ".cats-auth-course-title", "VIII Curso de Atendimento a Tentativas de Suicídio");
    setText(gate, ".cats-auth-course-note", "Pouso Alegre • CBMMG • 2026");
    setText(gate, ".cats-auth-note", "Acesso individual para pessoas cadastradas.");

    const footerSpans = gate.querySelectorAll(".cats-auth-footer span");
    if (footerSpans[0]) footerSpans[0].textContent = "© 2026 Corpo de Bombeiros Militar de Minas Gerais. Todos os direitos reservados.";
    if (footerSpans[1]) footerSpans[1].textContent = "VIII CATS • Pouso Alegre";

    bindAutoAccess(gate);
    gate.dataset.catsPaBranded = "true";
    document.documentElement.classList.remove("cats-auth-pending");
    return true;
  }

  function maintain(gate) {
    bindAutoAccess(gate);
    const msg = gate.querySelector("#catsAuthMessageText");
    if (msg?.textContent?.includes("Abrindo o ambiente")) recoverFormAfterAuth();
  }

  function observeGate() {
    if (brandGate()) {
      const gate = document.getElementById("catsAuthGate");
      if (gate && !gate.__catsPaObserver) {
        const observer = new MutationObserver(() => maintain(gate));
        observer.observe(gate, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ["hidden"] });
        Object.defineProperty(gate, "__catsPaObserver", { value: observer });
      }
      return;
    }

    const observer = new MutationObserver(() => {
      if (!brandGate()) return;
      observer.disconnect();
      const gate = document.getElementById("catsAuthGate");
      if (gate && !gate.__catsPaObserver) {
        const brandingObserver = new MutationObserver(() => maintain(gate));
        brandingObserver.observe(gate, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ["hidden"] });
        Object.defineProperty(gate, "__catsPaObserver", { value: brandingObserver });
      }
    });
    observer.observe(document.documentElement, { childList: true, subtree: true });

    window.setTimeout(() => {
      if (document.getElementById("catsAuthGate")) return;
      observer.disconnect();
      document.documentElement.classList.remove("cats-auth-pending");
      document.documentElement.classList.add("cats-auth-failed");
    }, 5000);
  }

  function init() {
    primeFormFrame();
    loadSupplementalAuth();
    observeGate();
    watchAuthenticatedForm();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
})();

/*
 * UX de submissão do pré-curso.
 * Importante: "Envio realizado" significa apenas que o POST foi disparado.
 * A mensagem de participação registrada só aparece após o verificador independente
 * marcar #success[data-persistence-confirmed="true"]. Nenhum resultado BDI-II é
 * calculado ou exibido no navegador.
 */
(() => {
  "use strict";

  const PENDING_ID = "catsSubmitPending";
  const FINAL_TITLE = "Parabéns! Sua participação foi registrada com sucesso.";
  const FINAL_TEXT = "Seja bem-vindo(a) ao VIII Curso de Atendimento a Tentativas de Suicídio — CATS 2026. Nos vemos em Pouso Alegre.";

  function bindFeedback() {
    const frame = document.getElementById("app");
    let doc;
    try { doc = frame?.contentDocument; } catch { return false; }
    if (!doc) return false;

    const form = doc.getElementById("catsForm");
    const success = doc.getElementById("success");
    const submit = doc.getElementById("submitBtn");
    if (!form || !success || !submit) return false;
    if (doc.documentElement.dataset.catsSubmitFeedback === "1") return true;
    doc.documentElement.dataset.catsSubmitFeedback = "1";

    const style = doc.createElement("style");
    style.id = "catsSubmitFeedbackStyle";
    style.textContent = `
      #${PENDING_ID}{display:none;text-align:center;padding:30px 16px}
      #${PENDING_ID}.show{display:block}
      #${PENDING_ID} .cats-submit-icon{width:58px;height:58px;margin:0 auto 12px;border-radius:50%;display:grid;place-items:center;background:#e8f5ee;color:#1f7a55;font-weight:900;font-size:1.4rem}
      #${PENDING_ID} h2{margin:0 0 8px;color:#17212b}
      #${PENDING_ID} p{max-width:610px;margin:0 auto;color:#66717c}
      body.cats-submit-pending #catsForm{display:none!important}
      #success[data-persistence-confirmed="true"] ~ #${PENDING_ID}{display:none!important}
    `;
    doc.head.appendChild(style);

    const pending = doc.createElement("section");
    pending.id = PENDING_ID;
    pending.className = "card";
    pending.setAttribute("role", "status");
    pending.setAttribute("aria-live", "polite");
    pending.innerHTML = '<div class="cats-submit-icon" aria-hidden="true">✓</div><h2>Envio realizado</h2><p>Obrigado por concluir o levantamento pré-curso. Estamos confirmando o registro dos seus dados.</p>';
    success.insertAdjacentElement("afterend", pending);

    const showPending = () => {
      success.removeAttribute("data-persistence-confirmed");
      doc.body.classList.add("cats-submit-pending");
      pending.classList.add("show");
      pending.scrollIntoView({ block: "start", behavior: "smooth" });
    };

    const restoreOnFailure = () => {
      const verifyAgain = doc.getElementById("catsVerifyAgain");
      const failed = submit.textContent.includes("Envio sem confirmação") || Boolean(verifyAgain && !verifyAgain.hidden);
      if (!failed) return;
      doc.body.classList.remove("cats-submit-pending");
      pending.classList.remove("show");
    };

    const applyConfirmedWelcome = () => {
      if (success.getAttribute("data-persistence-confirmed") !== "true") return;
      const h = success.querySelector("h2");
      const p = success.querySelector("p");
      if (h) h.textContent = FINAL_TITLE;
      if (p) p.textContent = FINAL_TEXT;
      doc.body.classList.remove("cats-submit-pending");
      pending.classList.remove("show");
      success.setAttribute("aria-live", "polite");
      success.scrollIntoView({ block: "start", behavior: "smooth" });
    };

    form.addEventListener("submit", event => {
      queueMicrotask(() => {
        if (event.defaultPrevented) return;
        showPending();
      });
    });

    const observer = new MutationObserver(() => {
      applyConfirmedWelcome();
      restoreOnFailure();
    });
    observer.observe(success, { attributes: true, childList: true, subtree: true, characterData: true });
    observer.observe(submit, { childList: true, subtree: true, characterData: true, attributes: true });
    const verifyAgain = doc.getElementById("catsVerifyAgain");
    if (verifyAgain) observer.observe(verifyAgain, { attributes: true });

    applyConfirmedWelcome();
    return true;
  }

  function start() {
    const frame = document.getElementById("app");
    if (frame) frame.addEventListener("load", () => window.setTimeout(bindFeedback, 0));
    const timer = window.setInterval(() => {
      if (bindFeedback()) window.clearInterval(timer);
    }, 120);
    window.setTimeout(() => window.clearInterval(timer), 15000);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, { once: true });
  else start();
})();
