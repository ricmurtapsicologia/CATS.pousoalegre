from __future__ import annotations

import sys
import time
from urllib.parse import urljoin

import requests

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765/"
TIMEOUT = 20


def get(url: str, attempts: int = 3) -> requests.Response:
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            response = requests.get(url, timeout=TIMEOUT, allow_redirects=True)
            if response.status_code < 500:
                return response
        except requests.RequestException as exc:
            last = exc
        time.sleep(1 + attempt)
    if last:
        raise last
    raise AssertionError(f"Sem resposta: {url}")


required_text = [
    "",
    "cats-auth.js",
    "cats-auth.css",
    "portal-ui.js",
    "portal-ui-core.js",
    "portal-ui.css",
    "presentation-originals.js",
    "precurso.html",
]
for relative in required_text:
    url = urljoin(BASE, relative)
    response = get(url)
    assert response.status_code == 200, (url, response.status_code)
    assert len(response.content) > 100, f"Ativo vazio: {url}"

for module in range(1, 9):
    relative = f"assets/lessons/aula-0{module}.pdf"
    response = get(urljoin(BASE, relative))
    assert response.status_code == 200, (relative, response.status_code)
    assert response.content[:5] == b"%PDF-", f"Aula {module}: assinatura PDF inválida"
    assert len(response.content) > 10_000, f"Aula {module}: PDF anormalmente pequeno"

# Dependências externas essenciais: autenticação e biblioteca sonora.
auth = get("https://ricmurtapsicologia.github.io/Curso-ATS/auth.js?v=20260905-2")
assert auth.status_code == 200 and len(auth.text) > 500, "Auth canônico indisponível"

podcast = get("https://ricmurtapsicologia.github.io/Podcast-ATS-CBMMG/")
assert podcast.status_code == 200, podcast.status_code
assert "audio-protection.js" in podcast.text, "Podcast sem proteção de áudio publicada"
assert "podcast-auth.js" in podcast.text, "Podcast sem gate de acesso publicado"

print("PASS: smoke — portal, 8 PDFs locais, autenticação canônica e biblioteca sonora disponíveis.")
