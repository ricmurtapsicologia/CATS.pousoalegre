from __future__ import annotations

import json
import sys
import time

from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765/"
PODCAST_URL = "https://ricmurtapsicologia.github.io/Podcast-ATS-CBMMG/"
EXPECTED_IMAGES = {
    "5": "https://i.pinimg.com/736x/aa/88/6a/aa886a6b4cf5d8b3d7148fe09c999113.jpg",
    "6": "https://i.pinimg.com/736x/54/70/f1/5470f1732df396897fe4d27575180b50.jpg",
}


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
        f"sessionStorage.setItem('cats_pa_auth_v1', {json.dumps(payload)});"
        "localStorage.setItem('cats_pa_onboarded_v2','1');"
    )


def neutralize_nonessential_network(page) -> None:
    page.route("**/Curso-ATS/access-2026.js*", lambda route: route.fulfill(
        status=200, content_type="application/javascript", body="/* E2E stub */"
    ))
    page.route("**/youtube.com/embed/**", lambda route: route.fulfill(
        status=200, content_type="text/html", body="<!doctype html><title>YouTube E2E</title>"
    ))
    page.route("**/fonts.googleapis.com/**", lambda route: route.abort())
    page.route("**/fonts.gstatic.com/**", lambda route: route.abort())
    page.route("**/i.pinimg.com/**", lambda route: route.fulfill(
        status=200,
        content_type="image/svg+xml",
        body='<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900"><rect width="100%" height="100%" fill="#222"/></svg>',
    ))
    # A visualização das aulas não pode depender do Drive/Google Slides.
    page.route("**/docs.google.com/presentation/**", lambda route: route.abort())
    page.route("**/drive.google.com/**", lambda route: route.abort())


def assert_gate(browser) -> None:
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    page = context.new_page()
    page.goto(BASE, wait_until="domcontentloaded")
    page.wait_for_selector('#catsAuthGate[data-cats-pa-branded="true"]', timeout=15000)
    gate = page.locator("#catsAuthGate")
    assert gate.is_visible(), "Gate de acesso não está visível sem sessão"
    text = gate.inner_text()
    assert "VIII CATS" in text and "Pouso Alegre" in text
    assert "Acesso do aluno" in text
    context.close()


def assert_authenticated_portal(browser, viewport: dict[str, int]) -> None:
    context = browser.new_context(viewport=viewport)
    install_session(context)
    page = context.new_page()
    neutralize_nonessential_network(page)
    page.goto(BASE, wait_until="domcontentloaded")
    page.wait_for_selector("#aulas", timeout=15000)
    page.wait_for_function(
        "() => window.CATSPousoAlegreInlineDeckMode?.viewer === 'local-pdf'",
        timeout=15000,
    )
    assert page.locator("#catsAuthGate").is_hidden()

    # 8/8 aulas: botão visível após expansão, viewer local, sem download/Drive.
    for module in range(1, 9):
        card = page.locator(f'#cards article[data-module="{module}"]')
        assert card.count() == 1, f"Aula {module} ausente"
        link = card.locator("a.open-slide[data-internal-lesson='true']")
        assert link.count() == 1, f"Aula {module} sem acesso canônico"
        assert link.get_attribute("href") == "#"
        assert link.get_attribute("target") is None
        assert link.get_attribute("download") is None
        assert link.get_attribute("data-slide-url") == f"assets/lessons/aula-0{module}.pdf"

        if not link.is_visible():
            card.locator(".lesson-toggle").click()
            link.wait_for(state="visible", timeout=3000)

        link.click()
        viewer = page.locator("#slidesViewer")
        assert viewer.get_attribute("open") is not None, f"Aula {module}: viewer não abriu"
        src = page.locator("#slidesFrame").get_attribute("src") or ""
        assert f"/assets/lessons/aula-0{module}.pdf" in src, (module, src)
        assert "drive.google.com" not in src and "docs.google.com" not in src
        assert page.locator("#openExternal").count() == 0
        assert page.locator("#downloadOriginalPptx").count() == 0
        page.locator("#closeX").click()
        assert viewer.get_attribute("open") is None

    assert page.locator('#cards article[data-module="9"]').count() == 0

    for module, expected in EXPECTED_IMAGES.items():
        src = page.locator(f'#cards article[data-module="{module}"] .media img').get_attribute("src")
        assert src == expected, (module, src)

    # Vídeos: reprodução inline; nenhum link ou atributo de download oferecido.
    page.wait_for_selector('#videos[data-ats-video-parity="true"]', timeout=10000)
    assert page.locator("#videos iframe").count() == 6
    assert page.locator("#videos a[download]").count() == 0
    assert page.locator("#videos audio, #videos video").count() == 0
    assert page.locator("#videosToggle").count() == 0

    # Áudio é servido pela biblioteca sonora protegida; o portal não expõe arquivo direto.
    podcast = page.locator('article[data-module="proj"] .actions a').first
    assert podcast.get_attribute("href") == PODCAST_URL
    assert podcast.get_attribute("target") == "_blank"
    assert "noopener" in (podcast.get_attribute("rel") or "")
    assert page.locator('a[download][href*=".mp3"],a[download][href*=".m4a"]').count() == 0

    # Resíduos conhecidos não podem reaparecer na DOM publicada.
    html = page.content()
    assert "material não publicado neste portal" not in html
    assert "Abrir no Google Slides" not in html
    assert "Recohecimento" not in html

    assert page.evaluate(
        "document.documentElement.scrollWidth <= document.documentElement.clientWidth + 2"
    )
    context.close()


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    assert_gate(browser)
    assert_authenticated_portal(browser, {"width": 1280, "height": 900})
    assert_authenticated_portal(browser, {"width": 390, "height": 844})
    browser.close()

print("PASS: E2E release — gate, 8/8 aulas locais, vídeos inline, áudio protegido por biblioteca e mobile sem regressão.")
