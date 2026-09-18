from __future__ import annotations

import json
import sys
import time
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765/"
PRE = BASE.rstrip("/") + "/precurso.html"
LEGACY = BASE.rstrip("/") + "/legacy.html"
PRECURSO_CONFIG_VERSION = "2026.09.18-r16-iso-pure"


def auth_payload() -> str:
    now = int(time.time() * 1000)
    return json.dumps({
        "authenticated": True,
        "createdAt": now,
        "expiresAt": now + 8 * 60 * 60 * 1000,
        "version": 3,
    })


def install_session(context, onboarded: bool = True) -> None:
    payload = auth_payload()
    script = f"sessionStorage.setItem('cats_pa_auth_v1', {json.dumps(payload)});"
    if onboarded:
        script += "localStorage.setItem('cats_pa_onboarded_v2','1');"
    context.add_init_script(script)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    # ------------------------------------------------------------------
    # Portal principal: gate, autenticação e superfície curricular.
    # ------------------------------------------------------------------
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    page = context.new_page()
    page.goto(BASE, wait_until="networkidle")
    page.wait_for_selector('#catsAuthGate[data-cats-pa-branded="true"]', timeout=15000)
    gate = page.locator("#catsAuthGate")
    assert gate.is_visible()
    assert "VIII CATS" in (gate.text_content() or "")
    assert "Pouso Alegre" in (gate.text_content() or "")
    assert gate.locator("#catsAuthSubmit").count() == 0

    page.evaluate("payload => sessionStorage.setItem('cats_pa_auth_v1', payload)", auth_payload())
    page.evaluate("localStorage.setItem('cats_pa_onboarded_v2','1')")
    page.reload(wait_until="networkidle")
    page.wait_for_selector("#catsAuthGate", state="attached")
    assert page.locator("#catsAuthGate").is_hidden()
    page.wait_for_selector("#aulas")
    page.wait_for_timeout(500)

    for n in range(1, 9):
        lesson = page.locator(f'#cards article[data-module="{n}"]')
        assert lesson.count() == 1, n
        assert lesson.locator("img").count() == 1, f"Aula {n} sem imagem"
    for n in range(9, 13):
        assert page.locator(f'#cards article[data-module="{n}"]').count() == 0, n

    body_text = page.locator("body").inner_text()
    for forbidden in (
        "Prática de conversação em ATS",
        "Risco de incêndio/explosão",
        "Risco de precipitação",
        "Risco de afogamento",
        "Avaliação do curso",
        "prova teórica",
        "prova prática",
        "4º BBM",
        "4° BBM",
    ):
        assert forbidden not in body_text, forbidden

    assert page.locator('#cards article[data-module="8"]', has_text="Prevenção").count() == 1
    assert page.locator('article[data-module="proj"] a[href*="Podcast-ATS-CBMMG"]').count() == 1
    assert page.locator('article[data-module="biblioteca"] a[href*="Curso-ATS"]').count() == 1
    assert "Lucas Antônio de Oliveira" in page.locator(".coordination-card").inner_text()
    assert "8 aulas" in page.locator(".hero-card").inner_text()
    assert "46 h/a" in page.locator(".hero-card").inner_text()
    assert page.locator("#avaliacao").count() == 0
    assert page.locator("#assessmentPanel").count() == 0

    first_desktop = page.locator('#cards article[data-module="1"]')
    assert first_desktop.locator(".media").is_visible()
    assert first_desktop.locator("img").is_visible()
    assert first_desktop.locator(".content").is_visible()
    assert first_desktop.locator(".lesson-toggle").is_hidden()

    # Onboarding: valida conteúdo e fechamento real pelo CTA.
    welcome = browser.new_context(viewport={"width": 390, "height": 844})
    install_session(welcome, onboarded=False)
    w = welcome.new_page()
    w.goto(BASE, wait_until="networkidle")
    w.wait_for_selector("#onboard", state="visible", timeout=7000)
    assert "Lucas Antônio de Oliveira" in w.locator("#onboard").inner_text()
    assert "Caros(as) abordadores(as)," in w.locator("#onboard").inner_text()
    assert "avaliação" not in w.locator("#onboard").inner_text().lower()
    text_align = w.locator(".onboard-welcome p").first.evaluate("el => getComputedStyle(el).textAlign")
    assert text_align == "justify", text_align
    w.locator("#ob-next").click(force=True)
    w.locator("#onboard").wait_for(state="hidden", timeout=3000)
    welcome.close()

    # ------------------------------------------------------------------
    # Integração do portal com a página de pré-curso.
    # O contrato profundo de envio/persistência pertence a e2e_precurso.py.
    # ------------------------------------------------------------------
    page.goto(PRE, wait_until="networkidle")
    page.wait_for_selector("#catsAuthGate", state="attached", timeout=15000)
    assert page.locator("#catsAuthGate").is_hidden()
    page.wait_for_selector("#app.ready", timeout=15000)
    assert page.locator("#boot").is_hidden()

    assert "Pouso Alegre" in page.title()
    assert "Pouso Alegre" in page.locator('meta[name="description"]').get_attribute("content")
    assert page.locator('meta[property="og:title"]').count() == 1
    assert page.locator('meta[property="og:description"]').count() == 1
    assert page.locator('meta[property="og:image"]').count() == 1
    assert page.locator('meta[name="twitter:card"][content="summary_large_image"]').count() == 1
    assert page.evaluate("window.__CATS_PERSISTENCE_CONFIG_VERSION__") == PRECURSO_CONFIG_VERSION
    assert page.evaluate("window.__CATS_PERSISTENCE_VERIFY_MODE__") == "pure-payload"

    iframe_handle = page.locator("#app").element_handle()
    assert iframe_handle is not None
    form_frame = iframe_handle.content_frame()
    assert form_frame is not None

    hero_text = form_frame.locator("header.hero").inner_text().lower()
    assert "viii cats" in hero_text
    assert "curso de atendimento a tentativas de suicídio" in hero_text
    for forbidden in ("4º BBM", "4° BBM", "CATS 2025"):
        assert forbidden.lower() not in form_frame.locator("body").inner_text().lower(), forbidden

    form = form_frame.locator("#catsForm")
    assert form.count() == 1
    assert form.get_attribute("method").lower() == "post"
    assert form.get_attribute("target") == "google-response"
    assert form.get_attribute("data-forms-linked") == "true"
    assert form.get_attribute("data-persistence-guard") == "strict"
    assert form.get_attribute("action").endswith("/formResponse")
    assert form_frame.locator(".step").count() == 3
    assert form_frame.locator("[required]:not([name])").count() == 0
    assert form_frame.locator('[name^="temp_"]').count() == 0
    assert form_frame.locator(".clinical-item").count() == 21
    assert form_frame.locator("#posto option").count() == 15
    assert form_frame.locator("#tempo option").count() == 7
    assert form_frame.locator("#ocorrencia option").count() == 5
    assert form_frame.locator("#presenciou option").count() == 5
    assert form_frame.locator("#ocorrencia option").nth(1).get_attribute("value") == "Nunca atendi."

    # Acesso direto ao legado sem sessão continua protegido.
    fresh = browser.new_context(viewport={"width": 900, "height": 800})
    fresh_page = fresh.new_page()
    fresh_page.goto(LEGACY, wait_until="domcontentloaded")
    fresh_page.wait_for_url("**/precurso.html", timeout=10000)
    fresh_page.wait_for_selector('#catsAuthGate[data-cats-pa-branded="true"]', timeout=15000)
    assert fresh_page.locator("#catsAuthGate").is_visible()
    fresh.close()

    # ------------------------------------------------------------------
    # Mobile-first: portal e pré-curso sem overflow horizontal.
    # ------------------------------------------------------------------
    mobile = browser.new_context(viewport={"width": 390, "height": 844})
    install_session(mobile, onboarded=True)
    m = mobile.new_page()
    m.goto(BASE, wait_until="networkidle")
    m.wait_for_selector("#aulas")
    m.wait_for_timeout(500)
    assert m.locator("#catsAuthGate").is_hidden()

    # O portal atual pode exibir onboarding; feche-o quando presente para testar a UI subjacente.
    if m.locator("#onboard").is_visible():
        m.locator("#ob-next").click(force=True)
        m.locator("#onboard").wait_for(state="hidden", timeout=3000)

    width_ok = m.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 2")
    assert width_ok, (m.evaluate("document.documentElement.scrollWidth"), m.evaluate("document.documentElement.clientWidth"))
    assert m.locator(".hero-card").is_hidden()
    assert m.locator("#courseInfoToggle").is_visible()
    assert m.locator("#mobileCoursePanel").is_hidden()
    m.locator("#courseInfoToggle").click()
    assert m.locator("#mobileCoursePanel").is_visible()
    assert "8 teóricas" in m.locator("#mobileCoursePanel").inner_text()

    assert m.locator("#mainNavLinks").is_hidden()
    m.locator("#mobileMenuBtn").click()
    assert m.locator("#mainNavLinks").is_visible()
    m.locator("#mobileMenuBtn").click()
    assert m.locator("#mainNavLinks").is_hidden()
    assert m.locator(".nav-cta #catsAuthLogout").count() == 1

    first = m.locator('#cards article[data-module="1"]')
    second = m.locator('#cards article[data-module="2"]')
    assert first.locator(".media").is_visible()
    assert first.locator("img").is_visible()
    assert second.locator("img").is_visible()
    media_height = first.locator(".media").evaluate("el => Math.round(el.getBoundingClientRect().height)")
    assert 100 <= media_height <= 140, media_height
    assert first.locator(".content").is_hidden()
    assert second.locator(".content").is_hidden()
    first.locator(".lesson-toggle").click()
    assert first.locator(".content").is_visible()
    second.locator(".lesson-toggle").click()
    assert second.locator(".content").is_visible()
    assert first.locator(".content").is_hidden()

    assert m.locator("#materialsPanel").is_hidden()
    m.locator('[aria-controls="materialsPanel"]').click()
    assert m.locator("#materialsPanel").is_visible()
    assert m.locator("#videosGrid").is_hidden()
    m.locator("#videosToggle").click()
    assert m.locator("#videosGrid").is_visible()
    assert m.locator("#assessmentPanel").count() == 0

    m.goto(PRE, wait_until="networkidle")
    m.wait_for_selector("#app.ready", timeout=15000)
    assert m.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 2")
    iframe_handle_mobile = m.locator("#app").element_handle()
    assert iframe_handle_mobile is not None
    mf = iframe_handle_mobile.content_frame()
    assert mf is not None
    assert mf.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 2")
    assert mf.locator("#posto").evaluate("el => getComputedStyle(el).fontSize") == "16px"
    assert mf.locator("#submitBtn").evaluate("el => el.getBoundingClientRect().height >= 44")

    mobile.close()
    context.close()
    browser.close()

print("PASS: Smoke + E2E VIII CATS — portal, autenticação, onboarding, integração do pré-curso e mobile-first; persistência profunda delegada ao E2E dedicado.")