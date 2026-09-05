from __future__ import annotations

import json
import sys
import time
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765/"


def auth_payload() -> str:
    now = int(time.time() * 1000)
    return json.dumps({
        "authenticated": True,
        "createdAt": now,
        "expiresAt": now + 8 * 60 * 60 * 1000,
        "version": 3,
    })


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    # Gate: identidade CATS, mesma base de credenciais e fluxo automático.
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    page = context.new_page()
    page.goto(BASE, wait_until="networkidle")
    page.wait_for_selector('#catsAuthGate[data-cats-pa-branded="true"]', timeout=15000)
    gate = page.locator("#catsAuthGate")
    assert gate.is_visible()
    assert "VIII CATS" in (gate.text_content() or "")
    assert "Pouso Alegre" in (gate.text_content() or "")
    assert gate.locator("#catsAuthSubmit").count() == 0

    # Sessão própria libera o portal sem expor credencial real no teste.
    page.evaluate("payload => sessionStorage.setItem('cats_pa_auth_v1', payload)", auth_payload())
    page.evaluate("localStorage.setItem('cats_pa_onboarded_v2','1')")
    page.reload(wait_until="networkidle")
    page.wait_for_selector("#catsAuthGate", state="attached")
    assert page.locator("#catsAuthGate").is_hidden()
    page.wait_for_selector("#aulas")
    page.wait_for_timeout(700)

    # Malha oficial: 12 unidades, oito teóricas e quatro práticas.
    for n in range(1, 13):
        assert page.locator(f'#cards article[data-module="{n}"]').count() == 1, n
    assert page.locator('#cards article[data-module="8"]', has_text="Prática de conversação").count() == 1
    assert page.locator('#cards article[data-module="9"]', has_text="incêndio/explosão").count() == 1
    assert page.locator('#cards article[data-module="10"]', has_text="precipitação").count() == 1
    assert page.locator('#cards article[data-module="11"]', has_text="afogamento").count() == 1
    assert page.locator('#cards article[data-module="12"]', has_text="Prevenção").count() == 1
    assert page.locator('article[data-module="proj"] a[href*="Podcast-ATS-CBMMG"]').count() == 1
    assert page.locator('article[data-module="biblioteca"] a[href*="Curso-ATS"]').count() == 1
    assert "Lucas Antônio de Oliveira" in page.locator(".coordination-card").inner_text()
    assert "21–25/09/2026" in page.locator(".hero-card").inner_text()
    assert "46 h/a" in page.locator(".hero-card").inner_text()
    assert "12 unidades" in page.locator(".hero-card").inner_text()

    # Desktop mantém conteúdo de aula visível e toggles mobile ocultos.
    assert page.locator('#cards article[data-module="1"] .content').is_visible()
    assert page.locator('#cards article[data-module="1"] .lesson-toggle').is_hidden()

    # Avaliação existe, fica fechada e sem link oficial inventado.
    assert page.locator("#assessmentPanel").is_hidden()
    assert page.locator("#avaliacao a").count() == 0
    page.locator('#avaliacao .folder-toggle').click()
    assert page.locator("#assessmentPanel").is_visible()

    # Onboarding: boas-vindas do coordenador e texto justificado.
    welcome = browser.new_context(viewport={"width": 390, "height": 844})
    payload = auth_payload().replace("\\", "\\\\").replace("'", "\\'")
    welcome.add_init_script(f"sessionStorage.setItem('cats_pa_auth_v1','{payload}');")
    w = welcome.new_page()
    w.goto(BASE, wait_until="networkidle")
    w.wait_for_selector("#onboard", state="visible", timeout=7000)
    assert "Lucas Antônio de Oliveira" in w.locator("#onboard").inner_text()
    assert "Boas-vindas" in w.locator("#onboard").inner_text()
    text_align = w.locator(".onboard-welcome p").first.evaluate("el => getComputedStyle(el).textAlign")
    assert text_align == "justify", text_align
    w.locator("#ob-next").click()
    assert w.locator("#onboard").is_hidden()
    welcome.close()

    # Pré-curso preservado e protegido pela mesma sessão CATS.
    page.goto(BASE + "precurso.html", wait_until="networkidle")
    page.wait_for_selector("#catsAuthGate", state="attached", timeout=15000)
    assert page.locator("#catsAuthGate").is_hidden()
    assert page.locator("#app").count() == 1

    # Acesso direto ao legado sem sessão retorna ao fluxo protegido.
    fresh = browser.new_context(viewport={"width": 900, "height": 800})
    fresh_page = fresh.new_page()
    fresh_page.goto(BASE + "legacy.html", wait_until="domcontentloaded")
    fresh_page.wait_for_url("**/precurso.html", timeout=10000)
    fresh_page.wait_for_selector('#catsAuthGate[data-cats-pa-branded="true"]', timeout=15000)
    assert fresh_page.locator("#catsAuthGate").is_visible()
    fresh.close()

    # Mobile-first: menor densidade visual, menu e cascatas apenas por clique.
    mobile = browser.new_context(viewport={"width": 390, "height": 844})
    mobile.add_init_script(f"sessionStorage.setItem('cats_pa_auth_v1','{payload}'); localStorage.setItem('cats_pa_onboarded_v2','1');")
    m = mobile.new_page()
    m.goto(BASE, wait_until="networkidle")
    m.wait_for_selector("#aulas")
    m.wait_for_timeout(700)
    assert m.locator("#catsAuthGate").is_hidden()

    width_ok = m.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 2")
    assert width_ok, (m.evaluate("document.documentElement.scrollWidth"), m.evaluate("document.documentElement.clientWidth"))
    assert m.locator(".hero-card").is_hidden()
    assert m.locator("#courseInfoToggle").is_visible()
    assert m.locator("#mobileCoursePanel").is_hidden()
    m.locator("#courseInfoToggle").click()
    assert m.locator("#mobileCoursePanel").is_visible()

    # Menu principal inicia fechado e abre somente por botão.
    assert m.locator("#mainNavLinks").is_hidden()
    m.locator("#mobileMenuBtn").click()
    assert m.locator("#mainNavLinks").is_visible()
    m.locator("#mobileMenuBtn").click()
    assert m.locator("#mainNavLinks").is_hidden()

    # Logout é integrado à barra, sem sobrepor o CTA/hero.
    assert m.locator(".nav-cta #catsAuthLogout").count() == 1

    # Unidades começam fechadas; somente uma fica aberta por vez.
    first = m.locator('#cards article[data-module="1"]')
    second = m.locator('#cards article[data-module="2"]')
    assert first.locator(".content").is_hidden()
    assert second.locator(".content").is_hidden()
    first.locator(".lesson-toggle").click()
    assert first.locator(".content").is_visible()
    second.locator(".lesson-toggle").click()
    assert second.locator(".content").is_visible()
    assert first.locator(".content").is_hidden()

    # Pastas permanecem fechadas até o clique explícito.
    assert m.locator("#materialsPanel").is_hidden()
    m.locator('[aria-controls="materialsPanel"]').click()
    assert m.locator("#materialsPanel").is_visible()
    assert m.locator("#videosGrid").is_hidden()
    m.locator("#videosToggle").click()
    assert m.locator("#videosGrid").is_visible()
    assert m.locator("#assessmentPanel").is_hidden()

    # Elementos flutuantes de alta saliência não competem no mobile.
    assert m.locator(".fab").first.is_hidden()
    assert m.locator("#toTop").is_hidden()

    mobile.close()
    context.close()
    browser.close()

print("PASS: E2E VIII CATS — auth, onboarding, 12 unidades, práticas, progressive disclosure, cascatas por clique, recursos, avaliação, pré-curso e mobile-first.")
