from __future__ import annotations

import json
import sys
import time

import requests
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765/"
PODCAST_URL = "https://ricmurtapsicologia.github.io/Podcast-ATS-CBMMG/"

SOURCE_IDS = {
    "1": "1ZYiAFZwrDE2i2zRpMg714cBqC4R-2OeH",
    "2": "19n4VMAyYdaCjbYYIH8eZB3duNC1FkSF7",
    "3": "1GuEU435vhorxZt42dAEurX2mVopFpFEz",
    "4": "1kiKcOToIu1tKJRzWFVmARJYPP3N4J0S_",
    "5": "1AasaqZYAqBZJtoNCOh8e6TyBeb_11Fm-",
    "6": "1SNvZyrliydPk6iTkwAKhZ66FZ9AO7ac9",
    "7": "1hx-CVfbGbCzen1Ygc0-9lTHm81xVcaxw",
    "8": "1lVMb2TMiex4Z48_y1S2GA_mnTTgogS6u",
}


def auth_payload() -> str:
    now = int(time.time() * 1000)
    return json.dumps({
        "authenticated": True,
        "createdAt": now,
        "expiresAt": now + 8 * 60 * 60 * 1000,
        "version": 3,
    })


def assert_local_lesson_assets() -> None:
    for module in range(1, 9):
        url = f"{BASE.rstrip('/')}/assets/lessons/aula-0{module}.pdf"
        response = requests.get(url, timeout=15)
        assert response.status_code == 200, (module, response.status_code)
        assert response.content[:5] == b"%PDF-", f"Aula {module}: visualização não é PDF válido"
        assert len(response.content) > 10000, f"Aula {module}: PDF inesperadamente pequeno"


def install_session(context) -> None:
    payload = auth_payload()
    context.add_init_script(
        f"sessionStorage.setItem('cats_pa_auth_v1', {json.dumps(payload)});"
        "localStorage.setItem('cats_pa_onboarded_v2','1');"
    )


def neutralize_external_noise(page) -> None:
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


def assert_portal(viewport: dict[str, int]) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport=viewport)
        install_session(context)
        page = context.new_page()
        neutralize_external_noise(page)
        page.goto(BASE, wait_until="domcontentloaded")
        page.wait_for_selector("#aulas", timeout=15000)
        page.wait_for_function("() => window.CATSPousoAlegreInlineDeckMode?.viewer === 'local-pdf'", timeout=15000)

        assert page.locator("#catsAuthGate").is_hidden()
        deck_map = page.evaluate("window.CATSPousoAlegreOriginalDecks")
        assert set(deck_map.keys()) == set(SOURCE_IDS.keys()), deck_map

        for module, source_id in SOURCE_IDS.items():
            card = page.locator(f'#cards article[data-module="{module}"]')
            assert card.count() == 1, f"Aula {module} ausente"
            link = card.locator("a.open-slide[data-internal-lesson='true']")
            assert link.count() == 1, f"Aula {module} sem Acessar aula interno"
            assert link.get_attribute("target") is None, f"Aula {module} abre nova aba"
            assert link.get_attribute("download") is None, f"Aula {module} oferece download"
            assert link.get_attribute("data-slide-id") == source_id
            assert link.get_attribute("data-slide-url") == f"assets/lessons/aula-0{module}.pdf"

            if not link.is_visible():
                toggle = card.locator(".lesson-toggle")
                assert toggle.count() == 1, f"Aula {module}: conteúdo oculto sem controle de expansão"
                toggle.click()
                link.wait_for(state="visible", timeout=3000)

            link.click()
            viewer = page.locator("#slidesViewer")
            assert viewer.get_attribute("open") is not None, f"Aula {module}: modal não abriu"
            frame = page.locator("#slidesFrame")
            src = frame.get_attribute("src") or ""
            assert f"/assets/lessons/aula-0{module}.pdf" in src, (module, src)
            assert "drive.google.com" not in src
            assert page.locator("#openExternal").count() == 0
            assert page.locator("#downloadOriginalPptx").count() == 0
            page.locator("#closeX").click()
            assert viewer.get_attribute("open") is None

        # Sanidade visual básica dos cards 5 e 6, sem acoplar o gate do podcast
        # a uma imagem editorial específica.
        for module in ("5", "6"):
            img = page.locator(f'#cards article[data-module="{module}"] .media img')
            assert img.count() == 1
            assert (img.get_attribute("src") or "").strip()
            assert (img.get_attribute("alt") or "").strip()

        page.wait_for_selector('#videos[data-ats-video-parity="true"]', timeout=10000)
        assert page.locator('#videos iframe').count() == 6
        assert page.locator('#videosToggle').count() == 0
        assert page.locator('#videos [hidden]').count() == 0

        # O podcast permanece como recurso externo protegido na própria página do projeto.
        assert page.locator('#catsAudioLibrary').count() == 0
        assert page.locator('script[src*="audio-inline.js"]').count() == 0
        assert page.locator('audio').count() == 0
        project_link = page.locator('article[data-module="proj"] .actions a').first
        assert project_link.get_attribute("href") == PODCAST_URL
        assert project_link.get_attribute("target") == "_blank"
        assert "noopener" in (project_link.get_attribute("rel") or "")
        assert "Acessar projeto" in project_link.inner_text()

        deck_mode = page.evaluate("window.CATSPousoAlegreInlineDeckMode")
        assert deck_mode["inline"] is True
        assert deck_mode["externalNavigation"] is False
        assert deck_mode["viewer"] == "local-pdf"

        assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 2")
        context.close()
        browser.close()


if __name__ == "__main__":
    assert_local_lesson_assets()
    assert_portal({"width": 1280, "height": 900})
    assert_portal({"width": 390, "height": 844})
    print("PASS: 8 aulas locais inline, 6 vídeos e card externo do podcast; nenhum áudio do podcast incorporado à página CATS.")
