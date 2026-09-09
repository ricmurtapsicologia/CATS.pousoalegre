from __future__ import annotations
import json, re, sys, time
from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8765/'
PRE = BASE.rstrip('/') + '/precurso.html'
now = int(time.time()*1000)
payload = json.dumps({'authenticated':True,'createdAt':now,'expiresAt':now+8*60*60*1000,'version':3})

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    ctx=browser.new_context(viewport={'width':390,'height':844})
    page=ctx.new_page()
    page.goto(PRE, wait_until='networkidle')
    page.wait_for_selector('#catsAuthGate[data-cats-pa-branded="true"]', timeout=15000)
    page.evaluate("payload => sessionStorage.setItem('cats_pa_auth_v1', payload)", payload)
    page.reload(wait_until='networkidle')
    page.wait_for_selector('#app.ready', timeout=15000)
    frame=page.frame(url=re.compile(r'legacy\.html'))
    print('FRAMES=', [f.url for f in page.frames])
    print('APP_CLASS=', page.locator('#app').get_attribute('class'))
    print('BOOT=', page.locator('#boot').inner_text())
    print('FRAME_SESSION=', frame.evaluate("sessionStorage.getItem('cats_pa_auth_v1')"))
    print('HEADER_HTML=', frame.locator('header.hero').inner_html())
    print('HEADER_TEXT=', repr(frame.locator('header.hero').inner_text()))
    print('COURSE_BRAND_COUNT=', frame.locator('.course-brand').count())
    if frame.locator('.course-brand').count():
        print('COURSE_BRAND_TEXT=', repr(frame.locator('.course-brand').inner_text()))
        print('COURSE_BRAND_VISIBLE=', frame.locator('.course-brand').is_visible())
    browser.close()
