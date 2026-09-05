(() => {
  "use strict";

  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

  function moveLogoutIntoNav() {
    const logout = document.getElementById("catsAuthLogout");
    const nav = $(".nav-cta");
    if (!logout || !nav || logout.parentElement === nav) return false;
    logout.setAttribute("aria-label", "Encerrar sessão");
    nav.appendChild(logout);
    return true;
  }

  function installLogoutObserver() {
    if (moveLogoutIntoNav()) return;
    const observer = new MutationObserver(() => {
      if (moveLogoutIntoNav()) observer.disconnect();
    });
    observer.observe(document.body, { childList: true, subtree: true });
    setTimeout(() => observer.disconnect(), 10000);
  }

  function setupMobileNav() {
    const button = $("#mobileMenuBtn");
    const links = $(".nav-links");
    if (!button || !links) return;
    const close = () => {
      links.classList.remove("is-open");
      button.setAttribute("aria-expanded", "false");
    };
    button.addEventListener("click", () => {
      const open = links.classList.toggle("is-open");
      button.setAttribute("aria-expanded", String(open));
    });
    links.addEventListener("click", event => {
      if (event.target.closest("a")) close();
    });
    window.addEventListener("resize", () => {
      if (window.innerWidth >= 761) close();
    }, { passive: true });
  }

  function setupCourseInfo() {
    const button = $("#courseInfoToggle");
    const panel = $("#mobileCoursePanel");
    if (!button || !panel) return;
    button.addEventListener("click", () => {
      const opening = panel.hidden;
      panel.hidden = !opening;
      button.setAttribute("aria-expanded", String(opening));
      button.querySelector("span").textContent = opening ? "Ocultar informações do curso" : "Ver informações do curso";
    });
  }

  function closeOtherCourseCards(active) {
    $$(".course-card.is-open").forEach(card => {
      if (card === active) return;
      card.classList.remove("is-open");
      card.querySelector(".lesson-toggle")?.setAttribute("aria-expanded", "false");
    });
  }

  function setupCourseCards() {
    $$("#cards article[data-module]").forEach(card => {
      const module = card.dataset.module || "";
      if (!/^\d+$/.test(module)) return;
      card.classList.add("course-card");
      const content = $(".content", card);
      const heading = $("h3", content);
      if (!content || !heading) return;
      const panelId = `course-panel-${module}`;
      content.id = panelId;

      const toggle = document.createElement("button");
      toggle.type = "button";
      toggle.className = "lesson-toggle";
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-controls", panelId);
      const hours = card.dataset.hours ? ` • ${card.dataset.hours}` : "";
      toggle.innerHTML = `<span><span class="lesson-meta">Unidade ${module}${hours}</span><span class="lesson-name"></span></span><i class="ri-arrow-down-s-line lesson-chevron" aria-hidden="true"></i>`;
      $(".lesson-name", toggle).textContent = heading.textContent.replace(/^Módulo\s+\d+:\s*/i, "").replace(/^Unidade\s+\d+:\s*/i, "");
      card.insertBefore(toggle, content);

      toggle.addEventListener("click", () => {
        const opening = !card.classList.contains("is-open");
        if (opening && window.innerWidth < 761) closeOtherCourseCards(card);
        card.classList.toggle("is-open", opening);
        toggle.setAttribute("aria-expanded", String(opening));
        if (opening && window.innerWidth < 761) {
          setTimeout(() => card.scrollIntoView({ block: "nearest", behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" }), 30);
        }
      });
    });
  }

  function setupFolders() {
    $$(".folder-toggle").forEach(button => {
      const id = button.getAttribute("aria-controls");
      const panel = id ? document.getElementById(id) : null;
      if (!panel) return;
      panel.hidden = true;
      button.setAttribute("aria-expanded", "false");
      button.addEventListener("click", () => {
        const opening = panel.hidden;
        panel.hidden = !opening;
        button.setAttribute("aria-expanded", String(opening));
      });
    });
  }

  function setupTopButton() {
    const button = $("#toTop");
    if (!button) return;
    const sync = () => button.classList.toggle("is-visible", window.scrollY > 700);
    window.addEventListener("scroll", sync, { passive: true });
    sync();
  }

  function init() {
    setupMobileNav();
    setupCourseInfo();
    setupCourseCards();
    setupFolders();
    setupTopButton();
    installLogoutObserver();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
})();
