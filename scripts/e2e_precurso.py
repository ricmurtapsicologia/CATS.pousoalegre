from __future__ import annotations

import json
import sys
import time
from datetime import date
from urllib.parse import parse_qsl

from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765/"
BUILD_VERSION = "2026.09.19-r17-coord-oliveira"
FIXTURE_DATE = date.today().isoformat()
SESSION_KEY = "cats_pa_auth_v1"


def auth_payload() -> str:
    now = int(time.time() * 1000)
    return json.dumps({
        "authenticated": True,
        "createdAt": now,
        "expiresAt": now + 8 * 60 * 60 * 1000,
        "version": 3,
    })


def install_session(context) -> None:
    payload = auth_payload()
    context.add_init_script(
        f"sessionStorage.setItem({json.dumps(SESSION_KEY)}, {json.dumps(payload)});"
        "localStorage.setItem('cats_pa_onboarded_v2','1');"
    )


def configure_verifier(page) -> None:
    page.add_init_script(
        """() => {
          window.__CATS_PERSISTENCE_VERIFY_TIMEOUT__ = 5000;
          window.__CATS_PERSISTENCE_VERIFY__ = async payload => ({
            protocol: 'cats-persistence-v1',
            persisted: true,
            terminal: true,
            sheetId: '1wQ0nc6TmCqqbu-ZqloIRLptO6iHqDhD00qrFLxP-fUk',
            formEditId: '1107fjdaiL42Zb0n2jNjKr0aiNNysyEADQCesdBTbD_E',
            fingerprint: payload.fingerprint
          });
        }"""
    )


def extract_form_payload(request) -> dict[str, str]:
    body = request.post_data or ""
    pairs = parse_qsl(body, keep_blank_values=True)
    return {k: v for k, v in pairs}


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    context = browser.new_context(viewport={"width": 390, "height": 844})
    install_session(context)
    page = context.new_page()
    configure_verifier(page)

    captured: list[dict[str, str]] = []
    def capture_form_response(route, request):
        captured.append(extract_form_payload(request))
        route.fulfill(status=200, content_type="text/html", body="<!doctype html><title>ok</title>")

    page.route("**/formResponse", capture_form_response)
    page.goto(BASE + "precurso.html", wait_until="domcontentloaded")
    page.wait_for_selector("#app.ready", state="attached", timeout=15000)
    page.wait_for_function("() => !document.documentElement.classList.contains('cats-auth-pending')", timeout=15000)
    frame = page.frame_locator("#app")
    form = frame.locator("#catsForm")
    form.wait_for(state="visible", timeout=15000)
    assert page.locator("#catsAuthGate").is_hidden()
    assert (form.get_attribute("action") or "").endswith("/formResponse")
    assert frame.locator("[required]:not([name])").count() == 0

    date_field = frame.locator("#data")
    assert date_field.get_attribute("type") == "date"
    assert date_field.get_attribute("name") == "entry.2092238618"
    assert date_field.get_attribute("required") is not None
    assert frame.locator("#ocorrencia option").count() == 5
    assert frame.locator("#presenciou option").count() == 5
    assert frame.locator('#ocorrencia').get_attribute('name') == 'entry.500885681'
    first_occurrence = frame.locator('#ocorrencia option').nth(1)
    assert first_occurrence.get_attribute('value') == 'Nunca atendi.'
    assert first_occurrence.inner_text() == 'Nunca atendi.'
    assert frame.locator("html").evaluate("el => el.dataset.catsBuild") == BUILD_VERSION
    assert form.get_attribute("data-forms-linked") == "true"
    assert form.get_attribute("data-persistence-guard") == "strict"

    participant_text = frame.locator("body").inner_text().lower()
    assert "bdi-ii" not in participant_text

    frame.locator('[data-step="1"] [data-next]').click()
    assert "active" in (frame.locator('[data-step="1"]').get_attribute("class") or "")
    assert frame.locator(".error").evaluate_all("els => els.some(e => e.textContent.trim().length > 0)")

    frame.locator("#nome").fill("TESTE AUTOMATIZADO CATS")
    frame.locator("#posto").select_option(label="Cap")
    frame.locator("#tempo").select_option(index=1)
    frame.locator("#email").fill("teste.e2e@example.invalid")
    frame.locator("#instituicao").fill("CBMMG TESTE")
    frame.locator("#unidade").fill("UNIDADE TESTE")
    frame.locator("#registro").fill("0000000")
    frame.locator("#cpf").fill("11144477735")
    frame.locator("#sangue").fill("O+")
    frame.locator('input[name="entry.192985690"][value="Não."]').locator("xpath=..").click()
    assert frame.locator('input[name="entry.192985690"][value="Não."]').is_checked()
    date_field.fill(FIXTURE_DATE)
    assert date_field.input_value() == FIXTURE_DATE
    frame.locator('[data-step="1"] [data-next]').click()
    assert "active" in (frame.locator('[data-step="2"]').get_attribute("class") or "")
    assert frame.locator("#progressLabel").inner_text() == "Etapa 2 de 3"

    frame.locator("#motivo").fill("Teste automatizado de fluxo ponta a ponta.")
    frame.locator("#ocorrencia").select_option(label="Nunca atendi.")
    frame.locator("#presenciou").select_option(index=1)
    frame.locator('[data-step="2"] [data-next]').click()
    assert "active" in (frame.locator('[data-step="3"]').get_attribute("class") or "")
    assert frame.locator("#progressLabel").inner_text() == "Etapa 3 de 3"

    assert frame.locator(".clinical-item").count() == 21
    names = frame.locator('.clinical-item input[type="radio"]').evaluate_all("els => [...new Set(els.map(e => e.name))]")
    assert len(names) == 21, names
    assert all(name.startswith("entry.") for name in names), names
    for name in names:
        radio = frame.locator(f'input[name="{name}"]').first
        radio.locator("xpath=..").click()
        assert radio.is_checked(), f"Escolha clínica não permaneceu marcada: {name}"
    assert frame.locator("[required]:invalid").count() == 0

    assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 2")
    assert frame.locator("html").evaluate("el => el.scrollWidth <= el.clientWidth + 2")
    assert frame.locator("#posto").evaluate("el => getComputedStyle(el).fontSize") == "16px"
    assert frame.locator("#submitBtn").evaluate("el => el.getBoundingClientRect().height >= 44")

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
              sheetId: positive ? '1wQ0nc6TmCqqbu-ZqloIRLptO6iHqDhD00qrFLxP-fUk' : 'SHEET-ERRADA',
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
    assert "confirmando o registro" in pending_text.lower()

    # O verificador apontando para Sheet errada não pode produzir falso positivo.
    page.wait_for_timeout(800)
    success = frame.locator("#success")
    assert success.get_attribute("data-persistence-confirmed") != "true"
    assert not success.is_visible()

    # O retry só é habilitado quando a primeira janela de verificação termina.
    verify_again = frame.locator("#catsVerifyAgain")
    verify_again.wait_for(state="visible", timeout=7000)
    assert not verify_again.is_disabled()

    page.evaluate("window.__catsVerifierMode='positive'")
    verify_again.click()
    success.wait_for(state="visible", timeout=7000)
    assert success.get_attribute("data-persistence-confirmed") == "true"
    success_text = success.inner_text()
    assert "participação foi registrada com sucesso" in success_text
    assert "VIII Curso de Atendimento a Tentativas de Suicídio" in success_text
    final_participant_text = frame.locator("body").inner_text().lower()
    assert "bdi-ii" not in final_participant_text

    assert captured, "POST ao Google Forms não foi observado"
    payload = captured[-1]
    assert payload.get("entry.500885681") == "Nunca atendi."
    assert payload.get("entry.1067284683") == "TESTE AUTOMATIZADO CATS"
    assert payload.get("entry.426148251") == "11144477735"
    assert payload.get("entry.192985690") == "Não."
    assert all(name in payload for name in names), "Campos clínicos ausentes no POST"

    # Nenhuma resposta clínica/BDI-II deve ser persistida em storages do navegador.
    storage_dump = page.evaluate("JSON.stringify({local:{...localStorage},session:{...sessionStorage}})")
    assert "entry.626004811" not in storage_dump
    assert "bdi" not in storage_dump.lower()

    context.close()
    browser.close()

print("PASS: E2E pré-curso — fluxo real de escolha, POST, persistência confirmada e privacidade validados.")
