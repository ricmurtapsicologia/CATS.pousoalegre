from __future__ import annotations

import hashlib
import json
import sys
import time
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765/"
PRE = BASE.rstrip("/") + "/precurso.html"
LEGACY = BASE.rstrip("/") + "/legacy.html"
CONFIG_VERSION = "2026.09.18-r16-iso-pure"
FIXTURE_DATE = "2026-09-18"


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

    # 1) Gate real + formulário já preparado atrás da autenticação.
    context = browser.new_context(viewport={"width": 390, "height": 844})
    submitted = {"seen": False}

    def intercept_form(route):
        submitted["seen"] = True
        assert route.request.method == "POST"
        assert route.request.url.endswith("/formResponse")
        route.fulfill(status=200, content_type="text/html", body="<html><body>ok</body></html>")

    context.route("**/formResponse", intercept_form)
    page = context.new_page()
    page.goto(PRE, wait_until="networkidle")
    page.wait_for_selector('#catsAuthGate[data-cats-pa-branded="true"]', timeout=15000)
    gate = page.locator("#catsAuthGate")
    assert gate.is_visible()
    assert "VIII CATS" in gate.inner_text()
    assert "Pouso Alegre" in gate.inner_text()

    page.wait_for_selector("#app.ready", timeout=15000)
    iframe_handle = page.locator("#app").element_handle()
    assert iframe_handle is not None
    frame = iframe_handle.content_frame()
    assert frame is not None
    assert frame.locator("#catsForm").count() == 1
    assert page.locator("#boot").is_hidden()

    page.evaluate("window.__catsE2EFirstLoad = 'preservado'")
    start = time.perf_counter()
    payload = auth_payload()
    page.evaluate(
        """payload => {
          sessionStorage.setItem('cats_pa_auth_v1', payload);
          const gate = document.getElementById('catsAuthGate');
          if (gate) gate.hidden = true;
          document.documentElement.classList.remove('cats-auth-locked');
          window.dispatchEvent(new CustomEvent('cats:authenticated', {detail:{source:'e2e'}}));
        }""",
        payload,
    )
    page.wait_for_function("document.getElementById('catsAuthGate')?.hidden === true", timeout=1500)
    elapsed = time.perf_counter() - start
    assert elapsed < 1.0, f"Transição pós-login lenta: {elapsed:.3f}s"
    assert page.evaluate("window.__catsE2EFirstLoad") == "preservado"
    assert page.locator("#boot").is_hidden()
    assert frame.locator("#catsForm").count() == 1
    frame.wait_for_function(
        "document.documentElement.dataset.catsSubmitFeedback === '1'",
        timeout=5000,
    )

    # 2) Metadados, prévia social e contrato de persistência.
    assert page.locator('link[rel="canonical"]').get_attribute("href").endswith("/precurso.html")
    assert page.locator('meta[property="og:url"]').get_attribute("content").endswith("/precurso.html")
    assert page.locator('meta[property="og:title"]').count() == 1
    assert page.locator('meta[property="og:description"]').count() == 1
    assert page.locator('meta[property="og:image"]').count() == 1
    assert page.locator('meta[property="og:image:secure_url"]').count() == 1
    assert page.locator('meta[name="twitter:card"][content="summary_large_image"]').count() == 1
    assert page.locator('link[rel="icon"]').count() == 1
    assert frame.evaluate("sessionStorage.getItem('cats_pa_auth_v1')") is not None
    assert page.evaluate("window.__CATS_PERSISTENCE_CONFIG_VERSION__") == CONFIG_VERSION
    assert page.evaluate("window.__CATS_PERSISTENCE_VERIFY_MODE__") == "pure-payload"

    # 3) Identidade: a rota é Pouso Alegre; o hero pode permanecer institucional.
    title = page.title().lower()
    description = page.locator('meta[name="description"]').get_attribute("content").lower()
    hero = frame.locator("header.hero").inner_text().lower()
    assert "pouso alegre" in title
    assert "pouso alegre" in description
    assert "viii cats" in hero
    assert "curso de atendimento a tentativas de suicídio" in hero
    body_text = frame.locator("body").inner_text().lower()
    for forbidden in ("4º bbm", "4° bbm", "cats 2025"):
        assert forbidden not in body_text, forbidden

    # 4) Estrutura e integração com Google Forms.
    form = frame.locator("#catsForm")
    assert form.count() == 1
    assert form.get_attribute("method").lower() == "post"
    assert form.get_attribute("target") == "google-response"
    assert form.get_attribute("data-forms-linked") == "true"
    assert form.get_attribute("action").endswith("/formResponse")
    assert frame.locator(".step").count() == 3
    assert frame.locator("[required]:not([name])").count() == 0
    assert frame.locator('[name^="temp_"]').count() == 0

    assert frame.locator("#posto option").count() == 15
    assert frame.locator("#tempo option").count() == 7
    assert frame.locator("#ocorrencia option").count() == 5
    assert frame.locator("#presenciou option").count() == 5

    assert frame.locator('#ocorrencia').get_attribute('name') == 'entry.500885681'
    first_occurrence = frame.locator('#ocorrencia option').nth(1)
    assert first_occurrence.get_attribute('value') == 'Nunca atendi.'
    assert first_occurrence.inner_text() == 'Nunca atendi.'
    assert frame.evaluate("document.documentElement.dataset.catsFormsContract") == CONFIG_VERSION

    # 5) Validação negativa: vazio não pode avançar.
    frame.locator('[data-step="1"] [data-next]').click()
    assert "active" in (frame.locator('[data-step="1"]').get_attribute("class") or "")
    assert frame.locator(".error").evaluate_all("els => els.some(e => e.textContent.trim().length > 0)")

    # 6) Etapa 1 com dados sintéticos e data fixa.
    frame.locator("#nome").fill("TESTE AUTOMATIZADO CATS")
    frame.locator("#posto").select_option(label="Cap")
    frame.locator("#tempo").select_option(index=1)
    frame.locator("#email").fill("teste.e2e@example.invalid")
    frame.locator("#instituicao").fill("CBMMG TESTE")
    frame.locator("#unidade").fill("UNIDADE TESTE")
    frame.locator("#registro").fill("0000000")
    frame.locator("#cpf").fill("11144477735")
    frame.locator("#sangue").fill("O+")
    frame.locator('input[name="entry.192985690"][value="Não."]').check(force=True)
    frame.locator("#data").fill(FIXTURE_DATE)
    frame.locator('[data-step="1"] [data-next]').click()
    assert "active" in (frame.locator('[data-step="2"]').get_attribute("class") or "")
    assert frame.locator("#progressLabel").inner_text() == "Etapa 2 de 3"

    # 7) Etapa 2 exercitando a opção corrigida no contrato Forms.
    frame.locator("#motivo").fill("Teste automatizado de fluxo ponta a ponta.")
    frame.locator("#ocorrencia").select_option(label="Nunca atendi.")
    frame.locator("#presenciou").select_option(index=1)
    frame.locator('[data-step="2"] [data-next]').click()
    assert "active" in (frame.locator('[data-step="3"]').get_attribute("class") or "")
    assert frame.locator("#progressLabel").inner_text() == "Etapa 3 de 3"

    # 8) 21 grupos clínicos mapeados de forma única.
    assert frame.locator(".clinical-item").count() == 21
    names = frame.locator('.clinical-item input[type="radio"]').evaluate_all(
        "els => [...new Set(els.map(e => e.name))]"
    )
    assert len(names) == 21, names
    assert all(name.startswith("entry.") for name in names), names
    for name in names:
        frame.locator(f'input[name="{name}"]').first.check(force=True)
    assert frame.locator("[required]:invalid").count() == 0

    # 9) Mobile-first / alvo de toque.
    assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 2")
    assert frame.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 2")
    assert frame.locator("#posto").evaluate("el => getComputedStyle(el).fontSize") == "16px"
    assert frame.locator("#submitBtn").evaluate("el => el.getBoundingClientRect().height >= 44")

    # 10) Gate de persistência e feedback imediato.
    # O mock substitui somente o backend de verificação. O POST do formulário continua
    # real dentro do browser de teste e HTTP 200, sozinho, jamais marca persistência.
    page.evaluate(
        """() => {
          window.__catsVerifierMode = 'wrong-sheet';
          window.__catsLastPayload = null;
          window.__CATS_PERSISTENCE_VERIFY_TIMEOUT__ = 5000;
          window.__CATS_PERSISTENCE_VERIFY__ = async payload => {
            window.__catsLastPayload = {...payload};
            const positive = window.__catsVerifierMode === 'positive';
            return {
              protocol: 'cats-persistence-v1',
              persisted: true,
              terminal: positive,
              sheetId: positive
                ? '1wQ0nc6TmCqqbu-ZqloIRLptO6iHqDhD00qrFLxP-fUk'
                : 'SHEET-ERRADA',
              formEditId: '1107fjdaiL42Zb0n2jNjKr0aiNNysyEADQCesdBTbD_E',
              fingerprint: payload.fingerprint
            };
          };
        }"""
    )

    frame.locator("#submitBtn").click()
    pending = frame.locator("#catsSubmitPending")
    pending.wait_for(state="visible", timeout=3000)
    pending_text = pending.inner_text()
    assert "Envio realizado" in pending_text
    assert "confirmando o registro" in pending_text
    assert form.is_hidden()
    assert frame.locator("#success").get_attribute("data-persistence-confirmed") != "true"

    # Privacidade: nenhum resultado BDI-II, escore ou classificação pode chegar ao respondente.
    participant_text = frame.locator("body").inner_text().lower()
    assert "bdi-ii" not in participant_text
    assert "intensidade mínima" not in participant_text
    assert "intensidade leve" not in participant_text
    assert "intensidade moderada" not in participant_text
    assert "intensidade grave" not in participant_text

    frame.locator("#catsPersistenceStatus").wait_for(state="visible", timeout=10000)
    frame.wait_for_function(
        "document.getElementById('catsPersistenceStatus').textContent.includes('Confirmando automaticamente')",
        timeout=10000,
    )
    assert submitted["seen"]

    expected_canonical = f"TESTE AUTOMATIZADO CATS|teste.e2e@example.invalid|11144477735|{FIXTURE_DATE}"
    expected_fingerprint = hashlib.sha256(expected_canonical.encode("utf-8")).hexdigest()
    assert page.evaluate("window.__catsLastPayload?.fingerprint") == expected_fingerprint

    # Resposta positiva apontando para planilha errada não pode promover o estado final.
    assert frame.locator("#success").get_attribute("data-persistence-confirmed") != "true"
    assert "registrada com sucesso" not in frame.locator("body").inner_text().lower()
    assert frame.locator("#submitBtn").is_disabled()
    assert frame.locator("#catsVerifyAgain").is_hidden()

    # Apenas a confirmação independente da planilha oficial libera a mensagem final.
    page.evaluate("window.__catsVerifierMode = 'positive'")
    success = frame.locator("#success")
    success.wait_for(state="visible", timeout=15000)
    frame.wait_for_function(
        "document.getElementById('success')?.textContent.includes('Parabéns! Sua participação foi registrada com sucesso.')",
        timeout=3000,
    )
    final_text = success.inner_text()
    assert "Parabéns! Sua participação foi registrada com sucesso." in final_text
    assert "Seja bem-vindo(a) ao VIII Curso de Atendimento a Tentativas de Suicídio" in final_text
    assert "CATS 2026" in final_text
    assert "Pouso Alegre" in final_text
    assert form.is_hidden()
    assert success.get_attribute("data-persistence-confirmed") == "true"
    assert frame.locator("#catsSubmitPending").is_hidden()

    final_participant_text = frame.locator("body").inner_text().lower()
    assert "bdi-ii" not in final_participant_text
    context.close()

    # 11) Acesso direto ao legado sem sessão continua protegido.
    fresh = browser.new_context(viewport={"width": 900, "height": 800})
    fresh_page = fresh.new_page()
    fresh_page.goto(LEGACY, wait_until="domcontentloaded")
    fresh_page.wait_for_url("**/precurso.html", timeout=10000)
    fresh_page.wait_for_selector('#catsAuthGate[data-cats-pa-branded="true"]', timeout=15000)
    assert fresh_page.locator("#catsAuthGate").is_visible()
    fresh.close()

    browser.close()

print("PASS: Smoke + E2E CATS — envio imediato sem falso positivo, confirmação independente, boas-vindas finais e BDI-II ausente do navegador.")
