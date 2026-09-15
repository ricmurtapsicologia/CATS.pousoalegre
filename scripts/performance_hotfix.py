from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


def main() -> None:
    s = INDEX.read_text(encoding="utf-8")

    # Analytics: manter somente a camada canônica, com consentimento.
    s = re.sub(
        r'\n\s*<!-- Google Analytics \(defer\) -->\s*\n\s*<script defer src="https://www\.googletagmanager\.com/gtag/js\?id=G-38D052F915"></script>\s*\n\s*<script>.*?gtag\(\'config\', \'G-38D052F915\'\);\s*</script>',
        '', s, count=1, flags=re.S,
    )
    s = s.replace('ric-analytics.js?v=1.0.0', 'ric-analytics.js?v=1.1.2')

    # Fontes/ícones externos não devem bloquear a primeira pintura.
    google = '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet" />'
    google_async = '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet" media="print" onload="this.media=\'all\'" />\n  <noscript>' + google + '</noscript>'
    if google in s and 'fonts.googleapis.com/css2?family=Inter' in s and 'media="print" onload="this.media=' not in s:
        s = s.replace(google, google_async, 1)

    icons = '<link href="https://cdn.jsdelivr.net/npm/remixicon@4.3.0/fonts/remixicon.css" rel="stylesheet" />'
    icons_async = '<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin />\n  <link href="https://cdn.jsdelivr.net/npm/remixicon@4.3.0/fonts/remixicon.css" rel="stylesheet" media="print" onload="this.media=\'all\'" />\n  <noscript>' + icons + '</noscript>'
    if icons in s and 'rel="preconnect" href="https://cdn.jsdelivr.net"' not in s:
        s = s.replace(icons, icons_async, 1)

    # Iframes ocultos do YouTube só são requisitados quando a pasta é aberta.
    s = re.sub(
        r'(<iframe\s+class="video-embed"\s+loading="lazy"\s+)src=("https://www\.youtube\.com/embed/[^"]+")',
        r'\1data-src=\2', s,
    )

    INDEX.write_text(s, encoding="utf-8")


if __name__ == "__main__":
    main()
