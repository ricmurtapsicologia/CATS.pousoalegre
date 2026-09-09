from __future__ import annotations

import json
import re
import sys
import time
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765/"
PRE = BASE.rstrip("/") + "/precurso.html"
LEGACY = BASE.rstrip("/") + "/legacy.html"


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

    # 1) Smoke sem sessão: deve exibir o gate e não liberar o formulário.
    c0 = browser.new_context(viewport={"width": 390, "height": 844})
    p0 = c0.new_page()
    p0.goto(PRE, wait_until="networkidle")
    p0.wait_for_selector('#catsAuthGate[data-cats-pa-branded="true"]', timeout=15000)
    assert p0.locator("#catsAuthGate").is_visible()
    assert "VIII CATS" in p0.locator("#catsAuthGate").inner_text()
    assert "Pouso Alegre" in p0.locator("#catsAuthGate").inner_text()
    c0.close()

    # 2) Sessão válida: renderiza o formulário e testa o fluxo completo.
    c1 = browser.new_context(viewport={"width": 390, "height": 844})
    payload = auth_payload()
    c1.add_init_script(f"sessionStorage.setItem('cats_pa_auth_v1', {json.dumps(payload)});")

    submitted = {"seen": False}

    def intercept_form(route):
        submitted["seen"] = True
        assert route.request.method == "POST"
        assert route.request.url.endswith("/formResponse")
        route.fulfill(status=200, content_type="text/html", body="<html><body>ok</body></html>")

    c1.route("**/formResponse", intercept_form)
    page = c1.new_page()
    page.goto(PRE, wait_until="networkidle")
    page.wait_for_selector("#app.ready", timeout=15000)
    assert page.locator("#catsAuthGate").is_hidden()
    assert page.locator("#boot").is_hidden()

    # Smoke de metadados e prévia social.
    assert page.locator('link[rel="canonical"]').get_attribute("href").endswith("/precurso.html")
    assert page.locator('meta[property="og:url"]').get_attribute("content").endswith("/precurso.html")
    assert page.locator('meta[property="og:title"]').count() == 1
    assert page.locator('meta[property="og:description"]').count() == 1
    assert page.locator('meta[property="og:image"]').count() == 1
    assert page.locator('meta[property="og:image:secure_url"]').count() == 1
    assert page.locator('meta[name="twitter:card"][content="summary_large_image"]').count() == 1
    assert page.locator('link[rel="icon"]').count() == 1

    frame = page.frame(url=re.compile(r"legacy\.html"))
    assert frame is not None

    # Branding e resíduos.
    hero = frame.locator("header.hero").inner_text()
    assert "Pouso Alegre" in hero
    assert "7ª Cia Ind" in hero
    assert "Lucas Antônio de Oliveira" in hero
    body_text = frame.locator("body").inner_text()
    for forbidden in ("4º BBM", "4° BBM", "CATS 2025"):
        assert forbidden not in body_text, forbidden

    form = frame.locator("#catsForm")
    assert form.count() == 1
    assert form.get_attribute("method").lower() == "post"
    assert form.get_attribute("target") == "google-response"
    assert form.get_attribute("data-forms-linked") == "true"
    assert form.get_attribute("action").endswith("/formResponse")
    assert frame.locator(".step").count() == 3
    assert frame.locator("[required]:not([name])").count() == 0
    assert frame.locator('[name^="temp_"]').count() == 0

    # Selects canônicos.
    assert frame.locator("#posto option").count() == 15
    assert frame.locator("#tempo option").count() == 7
    assert frame.locator("#ocorrencia option").count() == 5
    assert frame.locator("#presenciou option").count() == 5

    # Validação negativa.
    frame.locator('[data-step="1"] [data-next]').click()
    assert "active" in (frame.locator('[data-step="1"]').get_attribute("class") or "")
    assert frame.locator(".error").evaluate_all("els => els.some(e => e.textContent.trim().length > 0)")

    # Etapa 1: dados sintéticos.
    frame.locator("#nome").fill("TESTE AUTOMATIZADO CATS")
    frame.locator("#posto").select_option(label="Cap")
    frame.locator("#tempo").select_option(index=1)
    frame.locator("#email").fill("teste.e2e@example.invalid")
    frame.locator("#instituicao").fill("CBMMG TESTE")
    frame.locator("#unidade").fill("UNIDADE TESTE")
    frame.locator("#registro").fill("0000000")
    frame.locator("#cpf").fill("00000000000")
    frame.locator("#sangue").fill("O+")
    frame.locator('input[name="entry.192985690"][value="Não."]').check()
    if not frame.locator("#data").input_value():
        frame.locator("#data").fill("2026-09-09")
    frame.locator('[data-step="1"] [data-next]').click()
    assert "active" in (frame.locator('[data-step="2"]').get_attribute("class") or "")
    assert frame.locator("#progressLabel").inner_text() == "Etapa 2 de 3"

    # Etapa 2.
    frame.locator("#motivo").fill("Teste automatizado de fluxo ponta a ponta.")
    frame.locator("#ocorrencia").select_option(index=1)
    frame.locator("#presenciou").select_option(index=1)
    frame.locator('[data-step="2"] [data-next]').click()
    assert "active" in (frame.locator('[data-step="3"]').get_attribute("class") or "")
    assert frame.locator("#progressLabel").inner_text() == "Etapa 3 de 3"

    # Etapa 3: 21 grupos com nomes únicos e mapeados.
    assert frame.locator(".clinical-item").count() == 21
    names = frame.locator('.clinical-item input[type="radio"]').evaluate_all(
        "els => [...new Set(els.map(e => e.name))]"
    )
    assert len(names) == 21, names
    assert all(name.startswith("entry.") for name in names), names
    for name in names:
        frame.locator(f'input[name="{name}"]').first.check()
    assert frame.locator("[required]:invalid").count() == 0

    # Envio E2E sem gravar dados reais: POST é interceptado.
    frame.locator("#submitBtn").click()
    frame.locator("#success").wait_for(state="visible", timeout=10000)
    assert submitted["seen"]
    assert "Envio concluído" in frame.locator("#success").inner_text()
    assert "formulário oficial" in frame.locator("#success").inner_text()
    assert form.is_hidden()

    # Mobile: sem overflow horizontal e controles com tamanho adequado.
    assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 2")
    assert frame.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 2")
    assert frame.locator("#posto").evaluate("el => getComputedStyle(el).fontSize") == "16px"
    assert frame.locator("#submitBtn").evaluate("el => el.getBoundingClientRect().height >= 44")
    c1.close()

    # 3) Legado direto sem sessão deve voltar ao gate protegido.
    c2 = browser.new_context(viewport={"width": 900, "height": 800})
    p2 = c2.new_page()
    p2.goto(LEGACY, wait_until="domcontentloaded")
    p2.wait_for_url("**/precurso.html", timeout=10000)
    p2.wait_for_selector('#catsAuthGate[data-cats-pa-branded="true"]', timeout=15000)
    assert p2.locator("#catsAuthGate").is_visible()
    c2.close()

    browser.close()

print("PASS: Smoke + E2E pré-curso CATS — gate, metadados, 3 etapas, 21 grupos, POST interceptado e mobile.")
