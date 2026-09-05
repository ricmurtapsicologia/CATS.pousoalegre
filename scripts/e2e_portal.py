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

    # Gate: identidade CATS, mesma base de credenciais, sem botão manual.
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    page = context.new_page()
    page.goto(BASE, wait_until="networkidle")
    page.wait_for_selector('#catsAuthGate[data-cats-pa-branded="true"]', timeout=15000)
    gate = page.locator("#catsAuthGate")
    assert gate.is_visible()
    assert "VIII CATS" in (gate.text_content() or "")
    assert "Pouso Alegre" in (gate.text_content() or "")
    assert gate.locator("#catsAuthSubmit").count() == 0

    # Sessão própria libera o portal sem usar credencial real em teste.
    page.evaluate("payload => sessionStorage.setItem('cats_pa_auth_v1', payload)", auth_payload())
    page.evaluate("localStorage.setItem('cats_pa_onboarded','1')")
    page.reload(wait_until="networkidle")
    page.wait_for_selector("#catsAuthGate", state="attached")
    assert page.locator("#catsAuthGate").is_hidden()
    page.wait_for_selector("#aulas")
    page.wait_for_timeout(1000)

    assert page.locator('#cards article[data-module="1"]').count() == 1
    assert page.locator('#cards article[data-module="2"]').count() == 1
    assert page.locator('#cards article[data-module="3"]').count() == 1
    assert page.locator('#cards article[data-module="4"]').count() == 1
    assert page.locator('#cards article[data-module="5"]').count() == 1
    assert page.locator('#cards article[data-module="6"]').count() == 1
    assert page.locator('#cards article[data-module="7"]').count() == 1
    assert page.locator('#cards article[data-module="8"]').count() == 1
    assert page.locator('article[data-module="proj"] a[href*="Podcast-ATS-CBMMG"]').count() == 1
    assert page.locator('article[data-module="biblioteca"] a[href*="Curso-ATS"]').count() == 1
    assert "Lucas Antônio de Oliveira" in page.locator(".coordination-card").inner_text()
    assert "21–25/09/2026" in page.locator(".hero-card").inner_text()
    assert "46 h/a" in page.locator(".hero-card").inner_text()

    # A avaliação não pode ter link enquanto não houver URL oficial.
    assert page.locator("#avaliacao a").count() == 0

    # Pré-curso preservado e protegido pela mesma sessão CATS.
    page.goto(BASE + "precurso.html", wait_until="networkidle")
    page.wait_for_selector("#catsAuthGate", state="attached", timeout=15000)
    assert page.locator("#catsAuthGate").is_hidden()
    assert page.locator("#app").count() == 1

    # Acesso direto ao legado sem sessão deve retornar ao fluxo protegido.
    fresh = browser.new_context(viewport={"width": 900, "height": 800})
    fresh_page = fresh.new_page()
    fresh_page.goto(BASE + "legacy.html", wait_until="domcontentloaded")
    fresh_page.wait_for_url("**/precurso.html", timeout=10000)
    fresh_page.wait_for_selector('#catsAuthGate[data-cats-pa-branded="true"]', timeout=15000)
    assert fresh_page.locator("#catsAuthGate").is_visible()
    fresh.close()

    # Mobile: gate e portal sem overflow horizontal estrutural.
    mobile = browser.new_context(viewport={"width": 390, "height": 844})
    payload = auth_payload().replace("\\", "\\\\").replace("'", "\\'")
    mobile.add_init_script(f"sessionStorage.setItem('cats_pa_auth_v1','{payload}'); localStorage.setItem('cats_pa_onboarded','1');")
    m = mobile.new_page()
    m.goto(BASE, wait_until="networkidle")
    m.wait_for_selector("#aulas")
    m.wait_for_timeout(900)
    assert m.locator("#catsAuthGate").is_hidden()
    width_ok = m.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 2")
    assert width_ok, (m.evaluate("document.documentElement.scrollWidth"), m.evaluate("document.documentElement.clientWidth"))
    assert m.locator('#cards article[data-module="8"]').count() == 1
    mobile.close()

    context.close()
    browser.close()

print("PASS: E2E VIII CATS — autenticação, portal, 8 módulos, recursos, coordenação, pré-curso, gate da avaliação e mobile.")
