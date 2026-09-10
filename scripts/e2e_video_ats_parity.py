from __future__ import annotations

import json
import sys
import time
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765/"
EXPECTED_IDS = [
    "gJBlY3opAVU",
    "N88STTQVaE8",
    "VW3mvMz5AXs",
    "YmIIiuaJgkk",
    "BbJi72PmDXI",
    "w6qQW5neQek",
]
REQUIRED_ALLOW = [
    "accelerometer",
    "autoplay",
    "clipboard-write",
    "encrypted-media",
    "gyroscope",
    "picture-in-picture",
    "web-share",
]


def session_script() -> str:
    now = int(time.time() * 1000)
    payload = json.dumps({
        "authenticated": True,
        "createdAt": now,
        "expiresAt": now + 8 * 60 * 60 * 1000,
        "version": 3,
    })
    return (
        f"sessionStorage.setItem('cats_pa_auth_v1', {json.dumps(payload)});"
        "localStorage.setItem('cats_pa_onboarded_v2','1');"
    )


def neutralize_external_noise(page) -> None:
    page.route("**/Curso-ATS/access-2026.js*", lambda route: route.fulfill(
        status=200, content_type="application/javascript", body="/* E2E stub */"
    ))
    page.route("**/youtube.com/embed/**", lambda route: route.fulfill(
        status=200, content_type="text/html", body="<!doctype html><title>YouTube E2E stub</title>"
    ))
    page.route("**/fonts.googleapis.com/**", lambda route: route.abort())
    page.route("**/fonts.gstatic.com/**", lambda route: route.abort())
    page.route("**/i.pinimg.com/**", lambda route: route.abort())


def assert_common(page) -> None:
    page.wait_for_selector('#videos[data-ats-video-parity="true"]', timeout=15000)
    section = page.locator('#videos[data-ats-video-parity="true"]')
    assert section.count() == 1
    assert page.locator('#videosToggle').count() == 0, "Gate/pasta de vídeos permaneceu"
    assert page.locator('#videos .folder').count() == 0, "Wrapper de pasta permaneceu"
    assert page.locator('#videos .videos-box').count() == 1
    assert page.locator('#videos .video-card').count() == 6
    assert page.locator('#videos .video-frame').count() == 6
    assert page.locator('#videos iframe').count() == 6
    assert page.locator('#videos [hidden]').count() == 0, "Há conteúdo de vídeo oculto"

    ids = page.locator('#videos iframe').evaluate_all(
        "els => els.map(e => (e.getAttribute('src') || '').split('/embed/')[1]?.split(/[?#]/)[0] || '')"
    )
    assert ids == EXPECTED_IDS, ids

    attrs = page.locator('#videos iframe').evaluate_all(
        "els => els.map(e => ({allow:e.getAttribute('allow')||'', fullscreen:e.hasAttribute('allowfullscreen'), loading:e.getAttribute('loading')}))"
    )
    for attrs_one in attrs:
        assert attrs_one["fullscreen"] is True
        assert attrs_one["loading"] == "lazy"
        for token in REQUIRED_ALLOW:
            assert token in attrs_one["allow"], (token, attrs_one["allow"])

    ratios = page.locator('#videos .video-frame').evaluate_all(
        "els => els.map(e => {const r=e.getBoundingClientRect(); return r.width/r.height;})"
    )
    assert all(1.72 <= ratio <= 1.84 for ratio in ratios), ratios

    mode = page.evaluate("window.CATSPousoAlegreVideoMode")
    assert mode["pattern"] == "ATS-inline-youtube"
    assert mode["directPlay"] is True
    assert mode["folderGate"] is False
    assert mode["aspectRatio"] == "16/9"


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    desktop = browser.new_context(viewport={"width": 1280, "height": 900})
    desktop.add_init_script(session_script())
    d = desktop.new_page()
    neutralize_external_noise(d)
    d.goto(BASE, wait_until="domcontentloaded")
    assert_common(d)
    columns = d.locator('#videos .videos-box').evaluate(
        "el => getComputedStyle(el).gridTemplateColumns.split(' ').filter(Boolean).length"
    )
    assert columns == 3, columns
    assert d.locator('#videos .video-card').first.is_visible()
    desktop.close()

    mobile = browser.new_context(viewport={"width": 390, "height": 844})
    mobile.add_init_script(session_script())
    m = mobile.new_page()
    neutralize_external_noise(m)
    m.goto(BASE, wait_until="domcontentloaded")
    assert_common(m)
    columns = m.locator('#videos .videos-box').evaluate(
        "el => getComputedStyle(el).gridTemplateColumns.split(' ').filter(Boolean).length"
    )
    assert columns == 1, columns
    assert m.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 2")
    assert m.locator('#videos .video-card').first.is_visible()
    mobile.close()

    browser.close()

print("PASS: vídeos de Pouso Alegre em paridade funcional com ATS — 6 players inline, 16:9, sem pasta, 3 colunas desktop, 1 coluna mobile e permissões completas do YouTube.")
