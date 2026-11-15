import pathlib, shutil, time, requests
from urllib.parse import urljoin, unquote, urlparse
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (personal research project)"}

def parse_saved_page(html_file, out_dir, site_url="", sep="|"):
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    base = pathlib.Path(html_file).parent
    soup = BeautifulSoup(open(html_file, encoding="utf-8").read(), "html.parser")
    rows, seen = [], set()

    for img in soup.find_all("img"):
        alt, src = img.get("alt", ""), img.get("src", "")
        if sep not in alt or not src or alt in seen or src.startswith("data:"):
            continue
        
        seen.add(alt)
        name, color = [x.strip() for x in alt.split(sep, 1)]
        ext = pathlib.Path(urlparse(src).path).suffix or ".jpg"
        file = f"{len(rows) + 1:03d}{ext}"

        if src.startswith(("http", "//")):
            data = requests.get(urljoin(site_url, src), headers=HEADERS, timeout=20).content
            (out / file).write_bytes(data)
            time.sleep(1)
        else:
            local = base / unquote(src.split("?")[0])
            if not local.exists():
                print("no encontrada:", local)
                continue
            shutil.copy(local, out / file)

        rows.append({"file": file, "name": name,
                     "category": name.split()[-1].lower(), "color": color})
    print(f"{len(rows)} productos guardados en {out}")
    return rows