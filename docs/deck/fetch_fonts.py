"""Fetch Google Fonts CSS + woff2 files locally so the deck renders offline and deterministically."""

import pathlib
import re
import urllib.request

FAMILIES = {
    "fraunces": "https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300..800&display=swap",
    "manrope": "https://fonts.googleapis.com/css2?family=Manrope:wght@300..800&display=swap",
    "notoserifdev": "https://fonts.googleapis.com/css2?family=Noto+Serif+Devanagari:wght@600&display=swap",
}

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36"
    )
}

HERE = pathlib.Path(__file__).parent
FONTS = HERE / "fonts"
FONTS.mkdir(exist_ok=True)

chunks = []
for name, url in FAMILIES.items():
    req = urllib.request.Request(url, headers=UA)
    css = urllib.request.urlopen(req).read().decode()

    def grab(match: re.Match) -> str:
        remote = match.group(1)
        filename = f"{name}-{remote.rsplit('/', 1)[1]}"
        dest = FONTS / filename
        if not dest.exists():
            with urllib.request.urlopen(urllib.request.Request(remote, headers=UA)) as resp:
                dest.write_bytes(resp.read())
        return f"url(fonts/{filename})"

    css = re.sub(r"url\((https://fonts\.gstatic\.com/[^)]+)\)", grab, css)
    chunks.append(f"/* {name} */\n{css}")

(HERE / "fonts.css").write_text("\n".join(chunks))
print("fonts.css written;", len(list(FONTS.glob('*.woff2'))), "font files")
