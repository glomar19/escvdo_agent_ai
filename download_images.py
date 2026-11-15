import time, pathlib, requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (personal research project)"}
EXTS = (".jpg", ".jpeg", ".png", ".webp")

def download_images(page_url, out_dir, limit=60, keyword=None):
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    html = requests.get(page_url, headers=HEADERS, timeout=20).text
    soup = BeautifulSoup(html, "html.parser")

    urls = []
    for img in soup.find_all("img"):
        src = img.get("data-src") or img.get("src")
        if not src:
            continue
        full = urljoin(page_url, src.split(" ")[0])
        if full in urls or not urlparse(full).path.lower().endswith(EXTS):
            continue
        if keyword and keyword.lower() not in full.lower():
            continue
        urls.append(full)

    print(f"{len(urls)} imágenes encontradas")
    for i, url in enumerate(urls[:limit], 1):
        ext = pathlib.Path(urlparse(url).path).suffix
        (out / f"{i:03d}{ext}").write_bytes(
            requests.get(url, headers=HEADERS, timeout=20).content)
        time.sleep(1)  # pausa para no cargar el servidor
    return len(urls[:limit])