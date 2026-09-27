from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / "index.html").read_text(encoding="utf-8")

errors: list[str] = []

def require(ok: bool, message: str) -> None:
    if not ok:
        errors.append(message)

# Este arquivo passou a ser somente um gate de drift. Nenhuma alteração é feita.
require("G-38D052F915" not in PAGE, "tag GA4 legada ainda presente")
require('meta name="ric-analytics-ga" content="G-N1GEBDNZ8B"' in PAGE,
        "propriedade GA4 canônica ausente")
require("ric-analytics.js?v=1.1.3" in PAGE,
        "loader canônico de analytics não está pinado em 1.1.3")
require("portal-ui.js?v=20260918-r18" in PAGE,
        "portal-ui não está no release r18 materializado")

require('fonts.googleapis.com/css2?family=Inter' in PAGE, "fonte Inter ausente")
require('media="print" onload="this.media=\'all\'"' in PAGE,
        "fontes/ícones externos voltaram a bloquear a primeira pintura")
require('rel="preconnect" href="https://cdn.jsdelivr.net"' in PAGE,
        "preconnect do CDN de ícones ausente")

# Os seis vídeos devem ficar deferred: nenhum YouTube oculto pode iniciar download
# antes de o usuário abrir a respectiva pasta.
youtube_src = re.findall(r'<iframe\s+class="video-embed"[^>]*\bsrc="https://www\.youtube\.com/embed/', PAGE, re.I)
youtube_deferred = re.findall(r'<iframe\s+class="video-embed"[^>]*\bdata-src="https://www\.youtube\.com/embed/', PAGE, re.I)
require(not youtube_src, "iframe de YouTube voltou a carregar eager/lazy via src")
require(len(youtube_deferred) == 6, f"esperados 6 vídeos deferred; encontrados {len(youtube_deferred)}")

if errors:
    raise SystemExit("PERFORMANCE_DRIFT_FAIL:\n- " + "\n- ".join(errors))

print("PERFORMANCE_DRIFT_PASS: otimizações já materializadas; nenhuma mutação executada.")
