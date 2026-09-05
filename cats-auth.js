(() => {
  "use strict";

  const KEY_MAP = Object.freeze({
    curso_ats_auth_v3: "cats_pa_auth_v1",
    ats_login_attempts_v3: "cats_pa_login_attempts_v1"
  });

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
    if (msg?.textContent?.includes("Abrindo o ambiente")) return;
  }

  function observeGate() {
    if (brandGate()) {
      const gate = document.getElementById("catsAuthGate");
      if (gate && !gate.__catsPaObserver) {
        const observer = new MutationObserver(() => maintain(gate));
        observer.observe(gate, { childList: true, subtree: true, characterData: true });
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
        brandingObserver.observe(gate, { childList: true, subtree: true, characterData: true });
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

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", observeGate, { once: true });
  else observeGate();
})();
