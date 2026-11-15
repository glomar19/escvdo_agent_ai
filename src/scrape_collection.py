import csv, time, pathlib, requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (personal research project)"}

def download_escvdo(page_url, out_dir="images/escvdo", pages=3):
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows, seen = [], set()

    for p in range(1, pages + 1):
        r = requests.get(page_url, params={"page": p}, headers=HEADERS, timeout=20)
        if r.status_code != 200:
            print(f"página {p}: código {r.status_code}, paro")
            break
        soup = BeautifulSoup(r.text, "html.parser")
        new = 0
        for img in soup.find_all("img"):
            alt, src = img.get("alt", ""), img.get("src")
            if "|" not in alt or not src or alt in seen:
                continue
            seen.add(alt)
            new += 1
            name, color = [x.strip() for x in alt.split("|", 1)]
            file = f"{len(rows) + 1:03d}.jpg"
            (out / file).write_bytes(
                requests.get(urljoin(page_url, src), headers=HEADERS, timeout=20).content)
            rows.append({"file": file, "name": name,
                         "category": name.split()[-1].lower(), "color": color})
            time.sleep(1)
        if new == 0:
            break
        time.sleep(2)

    if not rows:
        print("0 productos encontrados")
        return []
    with open(out / "products.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} productos guardados")
    return rows