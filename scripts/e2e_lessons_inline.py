from __future__ import annotations

import json
import sys
import time
from urllib.parse import urlparse

import requests
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765/"

DECKS = {
    "1": "1ZYiAFZwrDE2i2zRpMg714cBqC4R-2OeH",
    "2": "19n4VMAyYdaCjbYYIH8eZB3duNC1FkSF7",
    "3": "1GuEU435vhorxZt42dAEurX2mVopFpFEz",
    "4": "1kiKcOToIu1tKJRzWFVmARJYPP3N4J0S_",
    "5": "1AasaqZYAqBZJtoNCOh8e6TyBeb_11Fm-",
    "6": "1SNvZyrliydPk6iTkwAKhZ66FZ9AO7ac9",
    "7": "1hx-CVfbGbCzen1Ygc0-9lTHm81xVcaxw",
    "8": "1lVMb2TMiex4Z48_y1S2GA_mnTTgogS6u",
}

DENIAL_MARKERS = (
    "you need access",
    "request access",
    "access denied",
    "você precisa de acesso",
    "solicitar acesso",
    "acesso negado",
)


def auth_payload() -> str:
    now = int(time.time() * 1000)
    return json.dumps({
        "authenticated": True,
        "createdAt": now,
        "expiresAt": now + 8 * 60 * 60 * 1000,
        "version": 3,
    })


def assert_anonymous_drive_access() -> None:
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 CATS-E2E/2026",
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.7",
    })
    failures = []
    for module, file_id in DECKS.items():
        url = f"https://drive.google.com/file/d/{file_id}/preview"
        try:
            response = session.get(url, timeout=25, allow_redirects=True)
        except Exception as exc:
            failures.append(f"Aula {module}: erro de rede {exc!r}")
            continue
        final_host = urlparse(response.url).netloc.lower()
        text = response.text[:300000].lower()
        if response.status_code >= 400:
            failures.append(f"Aula {module}: HTTP {response.status_code}")
        if "accounts.google.com" in final_host:
            failures.append(f"Aula {module}: redirecionou para login ({response.url})")
        marker = next((m for m in DENIAL_MARKERS if m in text), None)
        if marker:
            failures.append(f"Aula {module}: bloqueio detectado ({marker})")
    if failures:
        raise AssertionError("\n".join(failures))


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
    page.route("https://drive.google.com/file/d/**/preview*", lambda route: route.fulfill(
        status=200, content_type="text/html", body="<!doctype html><title>Drive preview E2E</title><p>preview</p>"
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
        page.wait_for_timeout(800)

        assert page.locator("#catsAuthGate").is_hidden()
        deck_map = page.evaluate("window.CATSPousoAlegreOriginalDecks")
        assert set(deck_map.keys()) == set(DECKS.keys()), deck_map

        for module, file_id in DECKS.items():
            card = page.locator(f'#cards article[data-module="{module}"]')
            assert card.count() == 1, f"Aula {module} ausente"
            link = card.locator("a.open-slide")
            assert link.count() == 1, f"Aula {module} sem Acessar aula"
            assert link.get_attribute("target") is None, f"Aula {module} abre nova aba"
            assert link.get_attribute("download") is None, f"Aula {module} oferece download"
            assert link.get_attribute("data-slide-id") == file_id

            link.click()
            viewer = page.locator("#slidesViewer")
            assert viewer.get_attribute("open") is not None, f"Aula {module}: modal não abriu"
            frame = page.locator("#slidesFrame")
            src = frame.get_attribute("src") or ""
            expected = f"https://drive.google.com/file/d/{file_id}/preview"
            assert src == expected, (module, src, expected)
            allow = frame.get_attribute("allow") or ""
            assert "autoplay" in allow
            assert "fullscreen" in allow
            assert "encrypted-media" in allow
            assert page.locator("#openExternal").count() == 0
            assert page.locator("#downloadOriginalPptx").count() == 0
            page.locator("#closeX").click()
            assert viewer.get_attribute("open") is None

        img5 = page.locator('#cards article[data-module="5"] .media img')
        img6 = page.locator('#cards article[data-module="6"] .media img')
        assert "44c7d24202a6aa571b7c548ac02fa467" in (img5.get_attribute("src") or "")
        assert "3dd744f00802e7b721f8ae69199652fd" in (img6.get_attribute("src") or "")
        assert img5.get_attribute("data-cats-image-source") == "Pinterest"
        assert img6.get_attribute("data-cats-image-source") == "Pinterest"

        page.wait_for_selector('#videos[data-ats-video-parity="true"]', timeout=10000)
        assert page.locator('#videos iframe').count() == 6
        assert page.locator('#videosToggle').count() == 0
        assert page.locator('#videos [hidden]').count() == 0

        media_mode = page.evaluate("window.CATSPousoAlegreInlineDeckMode")
        assert media_mode["inline"] is True
        assert media_mode["externalNavigation"] is False
        assert media_mode["downloadButton"] is False

        assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 2")
        context.close()
        browser.close()


if __name__ == "__main__":
    assert_anonymous_drive_access()
    assert_portal({"width": 1280, "height": 900})
    assert_portal({"width": 390, "height": 844})
    print("PASS: 8 aulas inline, links canônicos, imagens 5/6 atualizadas, vídeos inline e Drive acessível anonimamente.")
