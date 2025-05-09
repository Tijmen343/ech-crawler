#!/usr/bin/env python3
"""
crawl_ech.py  –  MVP-crawler voor https://www.ech.nl
- probeert eerst de sitemap
- valt terug op breadth-first crawl
- respecteert robots.txt
- schrijft 1 JSON-bestand per pagina in ./data/
"""

import hashlib, json, os, re, sys, time, datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from usp.tree import sitemap_tree_for_homepage         # uit het 'usp'-pakket
from urllib.robotparser import RobotFileParser

ROOT = "https://www.ech.nl"
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# 👉  KIES HIER je eigen contact-mail (liefst zakelijk) -----------------
USER_AGENT = "ECH-MVP-bot tlogge@ech.nl"
# ----------------------------------------------------------------------

RATE_LIMIT = 0.3          # seconden tussen requests (vriendelijk crawlen)
TIMEOUT = 10              # request-timeout in sec
HEADERS = {"User-Agent": USER_AGENT}

# ---------- Helpers ----------------------------------------------------


def sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()


def allowed_by_robots(url: str, rp: RobotFileParser) -> bool:
    # robots-parser gebruikt volledige url
    return rp.can_fetch(USER_AGENT, url)


def save_json(meta: dict):
    """Schrijf één pagina naar data/<sha1>.json (pretty-printed)."""
    out_path = DATA_DIR / f"{meta['id']}.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


# ---------- URL-discovering -------------------------------------------


def discover_with_sitemap() -> set[str]:
    urls = set()
    try:
        print(">> Probeer sitemap…")
        tree = sitemap_tree_for_homepage(ROOT)
        for page in tree.all_pages():
            urls.add(page.url)
    except Exception as e:
        print("!! Geen sitemap of parse-fout:", e)
    return urls


def discover_with_bfs(rp: RobotFileParser) -> set[str]:
    """Breadth-first crawl vanaf ROOT, binnen hetzelfde domein."""
    print(">> Fallback: breadth-first crawl")
    queue = [ROOT]
    seen = set(queue)
    urls = set()

    while queue:
        current = queue.pop(0)
        if not allowed_by_robots(current, rp):
            continue
        try:
            r = requests.get(current, timeout=TIMEOUT, headers=HEADERS)
            if "text/html" not in r.headers.get("Content-Type", ""):
                continue
            soup = BeautifulSoup(r.text, "html.parser")

            # voeg toe
            urls.add(current)

            # ontdek links
            for a in soup.find_all("a", href=True):
                href = a["href"].split("#")[0]          # verwijder anchors
                if href.startswith("mailto:") or href.startswith("tel:"):
                    continue
                href = urljoin(current, href)
                if href.startswith(ROOT) and href not in seen:
                    seen.add(href)
                    queue.append(href)
        except requests.RequestException:
            pass
        time.sleep(RATE_LIMIT)
    return urls


# ---------- Main crawl -------------------------------------------------


def fetch_and_extract(url: str) -> dict | None:
    if not allowed_by_robots(url, RP):
        return None
    try:
        r = requests.get(url, timeout=TIMEOUT, headers=HEADERS)
    except requests.RequestException:
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = " ".join(soup.stripped_strings)
    if not text:
        return None

    return {
        "id": sha1(url),
        "url": url,
        "title": soup.title.string.strip() if soup.title else "",
        "text": text,
        "retrieved_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "source": "ech.nl",
    }


def main():
    print("== ECH crawler start ==")
    urls = discover_with_sitemap()

    # vul aan met fallback BFS als sitemap leeg is
    if not urls:
        urls = discover_with_bfs(RP)

    print(f"☑️  {len(urls)} URLs verzameld – starten met ophalen…")

    for i, url in enumerate(sorted(urls), 1):
        meta = fetch_and_extract(url)
        if meta:
            save_json(meta)
            print(f"{i:>3}/{len(urls)}  ✅ {url}")
        else:
            print(f"{i:>3}/{len(urls)}  ⚠️  {url} (overgeslagen)")
        time.sleep(RATE_LIMIT)

    print("== Klaar ==")


# ---------- Entry-point -----------------------------------------------

if __name__ == "__main__":
    # robots.txt inlezen
    RP = RobotFileParser()
    RP.set_url(urljoin(ROOT, "/robots.txt"))
    try:
        RP.read()
    except Exception:
        print("!! robots.txt niet bereikbaar – ga door met voorzichtigheid.")
    main()#!/usr/bin/env python3
"""
crawl_ech.py  –  MVP-crawler voor https://www.ech.nl
- probeert eerst de sitemap
- valt terug op breadth-first crawl
- respecteert robots.txt
- schrijft 1 JSON-bestand per pagina in ./data/
"""

import hashlib, json, os, re, sys, time, datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from usp.tree import sitemap_tree_for_homepage         # uit het 'usp'-pakket
from urllib.robotparser import RobotFileParser

ROOT = "https://www.ech.nl"
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# 👉  KIES HIER je eigen contact-mail (liefst zakelijk) -----------------
USER_AGENT = "ECH-MVP-bot (+voornaam.achternaam@example.com)"
# ----------------------------------------------------------------------

RATE_LIMIT = 0.3          # seconden tussen requests (vriendelijk crawlen)
TIMEOUT = 10              # request-timeout in sec
HEADERS = {"User-Agent": USER_AGENT}

# ---------- Helpers ----------------------------------------------------


def sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()


def allowed_by_robots(url: str, rp: RobotFileParser) -> bool:
    # robots-parser gebruikt volledige url
    return rp.can_fetch(USER_AGENT, url)


def save_json(meta: dict):
    """Schrijf één pagina naar data/<sha1>.json (pretty-printed)."""
    out_path = DATA_DIR / f"{meta['id']}.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


# ---------- URL-discovering -------------------------------------------


def discover_with_sitemap() -> set[str]:
    urls = set()
    try:
        print(">> Probeer sitemap…")
        tree = sitemap_tree_for_homepage(ROOT)
        for page in tree.all_pages():
            urls.add(page.url)
    except Exception as e:
        print("!! Geen sitemap of parse-fout:", e)
    return urls


def discover_with_bfs(rp: RobotFileParser) -> set[str]:
    """Breadth-first crawl vanaf ROOT, binnen hetzelfde domein."""
    print(">> Fallback: breadth-first crawl")
    queue = [ROOT]
    seen = set(queue)
    urls = set()

    while queue:
        current = queue.pop(0)
        if not allowed_by_robots(current, rp):
            continue
        try:
            r = requests.get(current, timeout=TIMEOUT, headers=HEADERS)
            if "text/html" not in r.headers.get("Content-Type", ""):
                continue
            soup = BeautifulSoup(r.text, "html.parser")

            # voeg toe
            urls.add(current)

            # ontdek links
            for a in soup.find_all("a", href=True):
                href = a["href"].split("#")[0]          # verwijder anchors
                if href.startswith("mailto:") or href.startswith("tel:"):
                    continue
                href = urljoin(current, href)
                if href.startswith(ROOT) and href not in seen:
                    seen.add(href)
                    queue.append(href)
        except requests.RequestException:
            pass
        time.sleep(RATE_LIMIT)
    return urls


# ---------- Main crawl -------------------------------------------------


def fetch_and_extract(url: str) -> dict | None:
    if not allowed_by_robots(url, RP):
        return None
    try:
        r = requests.get(url, timeout=TIMEOUT, headers=HEADERS)
    except requests.RequestException:
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = " ".join(soup.stripped_strings)
    if not text:
        return None

    return {
        "id": sha1(url),
        "url": url,
        "title": soup.title.string.strip() if soup.title else "",
        "text": text,
        "retrieved_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "source": "ech.nl",
    }


def main():
    print("== ECH crawler start ==")
    urls = discover_with_sitemap()

    # vul aan met fallback BFS als sitemap leeg is
    if not urls:
        urls = discover_with_bfs(RP)

    print(f"☑️  {len(urls)} URLs verzameld – starten met ophalen…")

    for i, url in enumerate(sorted(urls), 1):
        meta = fetch_and_extract(url)
        if meta:
            save_json(meta)
            print(f"{i:>3}/{len(urls)}  ✅ {url}")
        else:
            print(f"{i:>3}/{len(urls)}  ⚠️  {url} (overgeslagen)")
        time.sleep(RATE_LIMIT)

    print("== Klaar ==")


# ---------- Entry-point -----------------------------------------------

if __name__ == "__main__":
    # robots.txt inlezen
    RP = RobotFileParser()
    RP.set_url(urljoin(ROOT, "/robots.txt"))
    try:
        RP.read()
    except Exception:
        print("!! robots.txt niet bereikbaar – ga door met voorzichtigheid.")
    main()
cd ~/ech-crawler           # project­map
nano crawl_ech.py          # of gebruik VS Code / andere editor
#!/usr/bin/env python3
"""
crawl_ech.py  –  MVP-crawler voor https://www.ech.nl
- probeert eerst de sitemap
- valt terug op breadth-first crawl
- respecteert robots.txt
- schrijft 1 JSON-bestand per pagina in ./data/
"""

import hashlib, json, os, re, sys, time, datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from usp.tree import sitemap_tree_for_homepage         # uit het 'usp'-pakket
from urllib.robotparser import RobotFileParser

ROOT = "https://www.ech.nl"
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# 👉  KIES HIER je eigen contact-mail (liefst zakelijk) -----------------
USER_AGENT = "ECH-MVP-bot tlogge@ech.nl)"
# ----------------------------------------------------------------------

RATE_LIMIT = 0.3          # seconden tussen requests (vriendelijk crawlen)
TIMEOUT = 10              # request-timeout in sec
HEADERS = {"User-Agent": USER_AGENT}

# ---------- Helpers ----------------------------------------------------


def sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()


def allowed_by_robots(url: str, rp: RobotFileParser) -> bool:
    # robots-parser gebruikt volledige url
    return rp.can_fetch(USER_AGENT, url)


def save_json(meta: dict):
    """Schrijf één pagina naar data/<sha1>.json (pretty-printed)."""
    out_path = DATA_DIR / f"{meta['id']}.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


# ---------- URL-discovering -------------------------------------------


            continue
        try:
            r = requests.get(current, timeout=TIMEOUT, headers=HEADERS)
            if "text/html" not in r.headers.get("Content-Type", ""):
                continue
            soup = BeautifulSoup(r.text, "html.parser")

            # voeg toe
            urls.add(current)

            # ontdek links
            for a in soup.find_all("a", href=True):
                href = a["href"].split("#")[0]          # verwijder anchors
                if href.startswith("mailto:") or href.startswith("tel:"):
                    continue
                href = urljoin(current, href)
                if href.startswith(ROOT) and href not in seen:
                    seen.add(href)
                    queue.append(href)
        except requests.RequestException:
            pass
        time.sleep(RATE_LIMIT)
    return urls


# ---------- Main crawl -------------------------------------------------


def fetch_and_extract(url: str) -> dict | None:
    if not allowed_by_robots(url, RP):
        return None
    try:
        r = requests.get(url, timeout=TIMEOUT, headers=HEADERS)
    except requests.RequestException:
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = " ".join(soup.stripped_strings)
    if not text:
        return None

    return {
        "id": sha1(url),
        "url": url,
        "title": soup.title.string.strip() if soup.title else "",
        "text": text,
        "retrieved_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "source": "ech.nl",
    }


def main():
    print("== ECH crawler start ==")
    urls = discover_with_sitemap()

    # vul aan met fallback BFS als sitemap leeg is
    if not urls:
        urls = discover_with_bfs(RP)

    print(f"☑️  {len(urls)} URLs verzameld – starten met ophalen…")

    for i, url in enumerate(sorted(urls), 1):
        meta = fetch_and_extract(url)
        if meta:
            save_json(meta)
            print(f"{i:>3}/{len(urls)}  ✅ {url}")
        else:
            print(f"{i:>3}/{len(urls)}  ⚠️  {url} (overgeslagen)")
        time.sleep(RATE_LIMIT)

    print("== Klaar ==")


# ---------- Entry-point -----------------------------------------------

if __name__ == "__main__":
    # robots.txt inlezen
    RP = RobotFileParser()
    RP.set_url(urljoin(ROOT, "/robots.txt"))
    try:
        RP.read()
    except Exception:
        print("!! robots.txt niet bereikbaar – ga door met voorzichtigheid.")
    main()
python crawl_ech.py
source /Users/tijmen/PycharmProjects/ECH-LLM/.venv/bin/activate
# prompt zou nu beginnen met (.venv)
#!/usr/bin/env python3
"""
crawl_ech.py  –  MVP-crawler voor https://www.ech.nl
- probeert eerst de sitemap
- valt terug op breadth-first crawl
- respecteert robots.txt
- schrijft 1 JSON-bestand per pagina in ./data/
"""

import hashlib, json, os, re, sys, time, datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from usp.tree import sitemap_tree_for_homepage         # uit het 'usp'-pakket
from urllib.robotparser import RobotFileParser

ROOT = "https://www.ech.nl"
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# 👉  KIES HIER je eigen contact-mail (liefst zakelijk) -----------------
USER_AGENT = "ECH-MVP-bot tlogge@ech.nl"
# ----------------------------------------------------------------------

RATE_LIMIT = 0.3          # seconden tussen requests (vriendelijk crawlen)
TIMEOUT = 10              # request-timeout in sec
HEADERS = {"User-Agent": USER_AGENT}

# ---------- Helpers ----------------------------------------------------


def sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()


def allowed_by_robots(url: str, rp: RobotFileParser) -> bool:
    # robots-parser gebruikt volledige url
    return rp.can_fetch(USER_AGENT, url)


def save_json(meta: dict):
    """Schrijf één pagina naar data/<sha1>.json (pretty-printed)."""
    out_path = DATA_DIR / f"{meta['id']}.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


# ---------- URL-discovering -------------------------------------------


def discover_with_sitemap() -> set[str]:
    urls = set()
    try:
        print(">> Probeer sitemap…")
        tree = sitemap_tree_for_homepage(ROOT)
        for page in tree.all_pages():
            urls.add(page.url)
    except Exception as e:
        print("!! Geen sitemap of parse-fout:", e)
    return urls


def discover_with_bfs(rp: RobotFileParser) -> set[str]:
    """Breadth-first crawl vanaf ROOT, binnen hetzelfde domein."""
    print(">> Fallback: breadth-first crawl")
    queue = [ROOT]
    seen = set(queue)
    urls = set()

    while queue:
        current = queue.pop(0)
        if not allowed_by_robots(current, rp):
            continue
        try:
            r = requests.get(current, timeout=TIMEOUT, headers=HEADERS)
            if "text/html" not in r.headers.get("Content-Type", ""):
                continue
            soup = BeautifulSoup(r.text, "html.parser")

            # voeg toe
            urls.add(current)

            # ontdek links
            for a in soup.find_all("a", href=True):
                href = a["href"].split("#")[0]          # verwijder anchors
                if href.startswith("mailto:") or href.startswith("tel:"):
                    continue
                href = urljoin(current, href)
                if href.startswith(ROOT) and href not in seen:
                    seen.add(href)
                    queue.append(href)
        except requests.RequestException:
            pass
        time.sleep(RATE_LIMIT)
    return urls


# ---------- Main crawl -------------------------------------------------


def fetch_and_extract(url: str) -> dict | None:
    if not allowed_by_robots(url, RP):
        return None
    try:
        r = requests.get(url, timeout=TIMEOUT, headers=HEADERS)
    except requests.RequestException:
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = " ".join(soup.stripped_strings)
    if not text:
        return None

    return {
        "id": sha1(url),
        "url": url,
        "title": soup.title.string.strip() if soup.title else "",
        "text": text,
        "retrieved_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "source": "ech.nl",
    }


def main():
    print("== ECH crawler start ==")
    urls = discover_with_sitemap()

    # vul aan met fallback BFS als sitemap leeg is
    if not urls:
        urls = discover_with_bfs(RP)

    print(f"☑️  {len(urls)} URLs verzameld – starten met ophalen…")

    for i, url in enumerate(sorted(urls), 1):
        meta = fetch_and_extract(url)
        if meta:
            save_json(meta)
            print(f"{i:>3}/{len(urls)}  ✅ {url}")
        else:
            print(f"{i:>3}/{len(urls)}  ⚠️  {url} (overgeslagen)")
        time.sleep(RATE_LIMIT)

    print("== Klaar ==")


# ---------- Entry-point -----------------------------------------------

if __name__ == "__main__":
    # robots.txt inlezen
    RP = RobotFileParser()
    RP.set_url(urljoin(ROOT, "/robots.txt"))
    try:
        RP.read()
    except Exception:
        print("!! robots.txt niet bereikbaar – ga door met voorzichtigheid.")
    main()

#!/usr/bin/env python3 """ crawl_ech.py – MVP-crawler voor https://www.ech.nl - probeert eerst de sitemap - valt terug op breadth-first crawl - respecteert robots.txt - schrijft 1 JSON-bestand per pagina in ./data/ "

import hashlib, json, os, re, sys, time, datetime
            print(f"{i:>3}/{len(urls)}  ✅ {url}")
        else:
            print(f"{i:>3}/{len(urls)}  ⚠️  {url} (overgeslagen)")
        time.sleep(RATE_LIMIT)

    print("== Klaar ==")


# ---------- Entry-point -----------------------------------------------

if __name__ == "__main__":
    # robots.txt inlezen
    RP = RobotFileParser()
    RP.set_url(urljoin(ROOT, "/robots.txt"))
    try:
        RP.read()
    except Exception:
        print("!! robots.txt niet bereikbaar – ga door met voorzichtigheid.")
    main()
cd ~/ech-crawler           # project­map
nano crawl_ech.py          # of gebruik VS Code / andere editor
#!/usr/bin/env python3
"""
crawl_ech.py  –  MVP-crawler voor https://www.ech.nl
- probeert eerst de sitemap
- valt terug op breadth-first crawl
- respecteert robots.txt
- schrijft 1 JSON-bestand per pagina in ./data/
"""

import hashlib, json, os, re, sys, time, datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from usp.tree import sitemap_tree_for_homepage         # uit het 'usp'-pakket
from urllib.robotparser import RobotFileParser

ROOT = "https://www.ech.nl"
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# 👉  KIES HIER je eigen contact-mail (liefst zakelijk) -----------------
USER_AGENT = "ECH-MVP-bot tlogge@ech.nl)"
# ----------------------------------------------------------------------

RATE_LIMIT = 0.3          # seconden tussen requests (vriendelijk crawlen)
TIMEOUT = 10              # request-timeout in sec
HEADERS = {"User-Agent": USER_AGENT}

# ---------- Helpers ----------------------------------------------------


def sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()


def allowed_by_robots(url: str, rp: RobotFileParser) -> bool:
    # robots-parser gebruikt volledige url
    return rp.can_fetch(USER_AGENT, url)


def save_json(meta: dict):
    """Schrijf één pagina naar data/<sha1>.json (pretty-printed)."""
    out_path = DATA_DIR / f"{meta['id']}.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


# ---------- URL-discovering -------------------------------------------


def discover_with_sitemap() -> set[str]:
    urls = set()
    try:
        print(">> Probeer sitemap…")
        tree = sitemap_tree_for_homepage(ROOT)
        for page in tree.all_pages():
            urls.add(page.url)
    except Exception as e:
        print("!! Geen sitemap of parse-fout:", e)
    return urls


def discover_with_bfs(rp: RobotFileParser) -> set[str]:
    """Breadth-first crawl vanaf ROOT, binnen hetzelfde domein."""
    print(">> Fallback: breadth-first crawl")
    queue = [ROOT]
    seen = set(queue)
    urls = set()

    while queue:
        current = queue.pop(0)
        if not allowed_by_robots(current, rp):
            continue
        try:
            r = requests.get(current, timeout=TIMEOUT, headers=HEADERS)
            if "text/html" not in r.headers.get("Content-Type", ""):
                continue
            soup = BeautifulSoup(r.text, "html.parser")

            # voeg toe
            urls.add(current)

            # ontdek links
            for a in soup.find_all("a", href=True):
                href = a["href"].split("#")[0]          # verwijder anchors
                if href.startswith("mailto:") or href.startswith("tel:"):
                    continue
                href = urljoin(current, href)
                if href.startswith(ROOT) and href not in seen:
                    seen.add(href)
                    queue.append(href)
        except requests.RequestException:
            pass
        time.sleep(RATE_LIMIT)
    return urls


# ---------- Main crawl -------------------------------------------------


def fetch_and_extract(url: str) -> dict | None:
    if not allowed_by_robots(url, RP):
        return None
    try:
        r = requests.get(url, timeout=TIMEOUT, headers=HEADERS)
    except requests.RequestException:
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = " ".join(soup.stripped_strings)
    if not text:
        return None

    return {
        "id": sha1(url),
        "url": url,
        "title": soup.title.string.strip() if soup.title else "",
        "text": text,
        "retrieved_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "source": "ech.nl",
    }


def main():
    print("== ECH crawler start ==")
    urls = discover_with_sitemap()

    # vul aan met fallback BFS als sitemap leeg is
    if not urls:
        urls = discover_with_bfs(RP)

    print(f"☑️  {len(urls)} URLs verzameld – starten met ophalen…")

    for i, url in enumerate(sorted(urls), 1):
        meta = fetch_and_extract(url)
        if meta:
            save_json(meta)
            print(f"{i:>3}/{len(urls)}  ✅ {url}")
        else:
            print(f"{i:>3}/{len(urls)}  ⚠️  {url} (overgeslagen)")
        time.sleep(RATE_LIMIT)

    print("== Klaar ==")


# ---------- Entry-point -----------------------------------------------

if __name__ == "__main__":
    # robots.txt inlezen
    RP = RobotFileParser()
    RP.set_url(urljoin(ROOT, "/robots.txt"))
    try:
        RP.read()
    except Exception:
        print("!! robots.txt niet bereikbaar – ga door met voorzichtigheid.")
    main()
python crawl_ech.py
source /Users/tijmen/PycharmProjects/ECH-LLM/.venv/bin/activate
# prompt zou nu beginnen met (.venv)
#!/usr/bin/env python3
"""
crawl_ech.py  –  MVP-crawler voor https://www.ech.nl
- probeert eerst de sitemap
- valt terug op breadth-first crawl
- respecteert robots.txt
- schrijft 1 JSON-bestand per pagina in ./data/
"""

import hashlib, json, os, re, sys, time, datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from usp.tree import sitemap_tree_for_homepage         # uit het 'usp'-pakket
from urllib.robotparser import RobotFileParser

ROOT = "https://www.ech.nl"
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# 👉  KIES HIER je eigen contact-mail (liefst zakelijk) -----------------
USER_AGENT = "ECH-MVP-bot tlogge@ech.nl"
# ----------------------------------------------------------------------

RATE_LIMIT = 0.3          # seconden tussen requests (vriendelijk crawlen)
TIMEOUT = 10              # request-timeout in sec
HEADERS = {"User-Agent": USER_AGENT}

# ---------- Helpers ----------------------------------------------------


def sha1(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()


def allowed_by_robots(url: str, rp: RobotFileParser) -> bool:
    # robots-parser gebruikt volledige url
    return rp.can_fetch(USER_AGENT, url)


def save_json(meta: dict):
    """Schrijf één pagina naar data/<sha1>.json (pretty-printed)."""
    out_path = DATA_DIR / f"{meta['id']}.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


# ---------- URL-discovering -------------------------------------------


def discover_with_sitemap() -> set[str]:
    urls = set()
    try:
        print(">> Probeer sitemap…")
        tree = sitemap_tree_for_homepage(ROOT)
        for page in tree.all_pages():
            urls.add(page.url)
    except Exception as e:
        print("!! Geen sitemap of parse-fout:", e)
    return urls


def discover_with_bfs(rp: RobotFileParser) -> set[str]:
    """Breadth-first crawl vanaf ROOT, binnen hetzelfde domein."""
    print(">> Fallback: breadth-first crawl")
    queue = [ROOT]
    seen = set(queue)
    urls = set()

    while queue:
        current = queue.pop(0)
        if not allowed_by_robots(current, rp):
            continue
        try:
            r = requests.get(current, timeout=TIMEOUT, headers=HEADERS)
            if "text/html" not in r.headers.get("Content-Type", ""):
                continue
            soup = BeautifulSoup(r.text, "html.parser")

            # voeg toe
            urls.add(current)

            # ontdek links
            for a in soup.find_all("a", href=True):
                href = a["href"].split("#")[0]          # verwijder anchors
                if href.startswith("mailto:") or href.startswith("tel:"):
                    continue
                href = urljoin(current, href)
                if href.startswith(ROOT) and href not in seen:
                    seen.add(href)
                    queue.append(href)
        except requests.RequestException:
            pass
        time.sleep(RATE_LIMIT)
    return urls


# ---------- Main crawl -------------------------------------------------


def fetch_and_extract(url: str) -> dict | None:
    if not allowed_by_robots(url, RP):
        return None
    try:
        r = requests.get(url, timeout=TIMEOUT, headers=HEADERS)
    except requests.RequestException:
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = " ".join(soup.stripped_strings)
    if not text:
        return None

    return {
        "id": sha1(url),
        "url": url,
        "title": soup.title.string.strip() if soup.title else "",
        "text": text,
        "retrieved_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "source": "ech.nl",
    }


def main():
    print("== ECH crawler start ==")
    urls = discover_with_sitemap()

    # vul aan met fallback BFS als sitemap leeg is
    if not urls:
        urls = discover_with_bfs(RP)

    print(f"☑️  {len(urls)} URLs verzameld – starten met ophalen…")

    for i, url in enumerate(sorted(urls), 1):
        meta = fetch_and_extract(url)
        if meta:
            save_json(meta)
            print(f"{i:>3}/{len(urls)}  ✅ {url}")
        else:
            print(f"{i:>3}/{len(urls)}  ⚠️  {url} (overgeslagen)")
        time.sleep(RATE_LIMIT)

    print("== Klaar ==")


# ---------- Entry-point -----------------------------------------------

if __name__ == "__main__":
    # robots.txt inlezen
    RP = RobotFileParser()
    RP.set_url(urljoin(ROOT, "/robots.txt"))
    try:
        RP.read()
    except Exception:
        print("!! robots.txt niet bereikbaar – ga door met voorzichtigheid.")
    main()

