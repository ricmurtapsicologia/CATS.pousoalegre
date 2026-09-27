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


def install_session(context) -> None:
    now = int(time.time() * 1000)
    payload = json.dumps({
        "authenticated": True,
        "createdAt": now,
        "expiresAt": now + 8 * 60 * 60 * 1000,
        "version": 3,
    })
    context.add_init_script(
        f"sessionStorage.setItem('cats_pa_auth_v1', {json.dumps(payload)});"
        "localStorage.setItem('cats_pa_onboarded_v2','1');"
    )


def neutralize_nonessential(page) -> None:
    page.route("**/youtube.com/embed/**", lambda route: route.fulfill(
        status=200,
        content_type="text/html",
        body="<!doctype html><title>YouTube functional stub</title>",
    ))
    page.route("**/i.pinimg.com/**", lambda route: route.abort())
    page.route("**/fonts.googleapis.com/**", lambda route: route.abort())
    page.route("**/fonts.gstatic.com/**", lambda route: route.abort())


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    # Matrícula: 7 dígitos devem disparar submit automaticamente em ~550 ms,
    # sem depender de clique no botão nem Enter.
    gate_context = browser.new_context(viewport={"width": 1280, "height": 900})
    gate_page = gate_context.new_page()
    gate_page.goto(BASE, wait_until="domcontentloaded")
    gate_page.wait_for_selector('#catsAuthGate[data-cats-pa-branded="true"]', timeout=15000)
    gate_page.wait_for_function(
        "() => document.querySelector('#catsAuthInput')?.dataset.catsFastMatricula === '1'",
        timeout=10000,
    )
    gate_page.evaluate(
        """() => {
          window.__catsAutoSubmitAt = 0;
          const form = document.querySelector('#catsAuthForm');
          form.addEventListener('submit', event => {
            window.__catsAutoSubmitAt = performance.now();
            event.preventDefault();
            event.stopImmediatePropagation();
          }, true);
        }"""
    )
    started = gate_page.evaluate("performance.now()")
    gate_page.locator('#catsAuthInput').fill('1234567')
    gate_page.wait_for_function("() => window.__catsAutoSubmitAt > 0", timeout=1500)
    elapsed = gate_page.evaluate("start => window.__catsAutoSubmitAt - start", started)
    assert 350 <= elapsed <= 1200, elapsed
    gate_context.close()

    # Vídeos: os 6 players devem chegar ao frontend já com src real e sem
    # data-src residual; assim aparecem naturalmente e respondem ao play.
    video_context = browser.new_context(viewport={"width": 1280, "height": 900})
    install_session(video_context)
    video_page = video_context.new_page()
    neutralize_nonessential(video_page)
    video_page.goto(BASE, wait_until="domcontentloaded")
    video_page.wait_for_selector('#videos[data-ats-video-parity="true"] iframe', timeout=15000)
    video_page.wait_for_function(
        "() => document.querySelectorAll('#videos iframe[src*=\"youtube.com/embed/\"]').length === 6",
        timeout=10000,
    )
    assert video_page.locator('#videos iframe').count() == 6
    assert video_page.locator('#videos iframe[data-src]').count() == 0
    ids = video_page.locator('#videos iframe').evaluate_all(
        "els => els.map(e => ((e.getAttribute('src') || '').split('/embed/')[1]?.split(/[?#]/)[0] || ''))"
    )
    assert ids == EXPECTED_IDS, ids
    assert all(video_page.locator('#videos iframe').nth(i).is_visible() for i in range(6))
    video_context.close()

    browser.close()

print("PASS: frontend restaurado — matrícula 7 dígitos com autoacesso rápido e 6 vídeos visíveis/playable sem data-src residual.")
