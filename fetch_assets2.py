#!/usr/bin/env python3
import json, os, time, urllib.request, urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(BASE, "assets", "img")
UA = {"User-Agent": "VibeDeckBuilder/1.0 (educational, non-commercial; contact: local use) Mozilla/5.0"}

def get(url, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    print("OK  ", os.path.relpath(path, BASE), len(data))

def get_retry(url, tries=4, sleep=4):
    for i in range(tries):
        try:
            return get(url)
        except Exception as e:
            print("retry", i, url[:90], e)
            time.sleep(sleep * (i + 1))
    return None

# ---------- logos via simpleicons CDN ----------
logos = {
    "nvidia": ("nvidia", "76B900"), "amd": ("amd", "ED1C24"), "intel": ("intel", "0068B5"),
    "asml": ("asml", "0A4C95"), "tsmc": ("tsmc", "C9002B"), "samsung": ("samsung", "1428A0"),
    "openai": ("openai", "FFFFFF"), "anthropic": ("anthropic", "D97757"), "google": ("google", "4285F4"),
    "gemini": ("googlegemini", "4E8CF5"), "meta": ("meta", "0081FB"), "amazon": ("amazon", "FF9900"),
    "aws": ("amazonwebservices", "FF9900"), "x": ("x", "FFFFFF"), "mistral": ("mistralai", "FF7000"),
    "elevenlabs": ("elevenlabs", "FFFFFF"), "perplexity": ("perplexity", "20B8CD"), "midjourney": ("midjourney", "FFFFFF"),
    "suno": ("suno", "FFFFFF"), "huggingface": ("huggingface", "FFD21E"), "github": ("github", "FFFFFF"),
    "colab": ("googlecolab", "F9AB00"), "pytorch": ("pytorch", "EE4C2C"), "jupyter": ("jupyter", "F37726"),
    "vscode": ("visualstudiocode", "22A6F2"), "docker": ("docker", "2496ED"), "kubernetes": ("kubernetes", "326CE5"),
    "python": ("python", "3776AB"), "linux": ("linux", "FCC624"),
}
for key, (slug, color) in logos.items():
    d = get_retry(f"https://cdn.simpleicons.org/{slug}/{color}")
    if d and b"<svg" in d[:400]:
        save(os.path.join(IMG, "logos", key + ".svg"), d)
    else:
        print("NO LOGO", key)
    time.sleep(0.4)

# ---------- photos via commons (paced) ----------
def commons_photo(query, out, width=1600, tries=3):
    for t in range(tries):
        try:
            q = urllib.parse.urlencode({
                "action": "query", "format": "json", "generator": "search",
                "gsrsearch": query + " filetype:bitmap", "gsrnamespace": 6, "gsrlimit": "10",
                "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": str(width),
            })
            d = json.loads(get("https://commons.wikimedia.org/w/api.php?" + q, timeout=30).decode())
            cands = []
            for p in (d.get("query", {}).get("pages", {}) or {}).values():
                ii = (p.get("imageinfo") or [{}])[0]
                if ii.get("mime") == "image/jpeg" and ii.get("width", 0) >= 1400:
                    cands.append((ii.get("width", 0), ii.get("thumburl"), p.get("title", "")))
            cands.sort(reverse=True)
            if cands:
                d2 = get_retry(cands[0][1])
                if d2:
                    save(out, d2)
                    print("     from:", cands[0][2])
                    return True
            print("no candidate for", query)
            return False
        except Exception as e:
            print("ERR", query, e)
            time.sleep(6)
    return False

photos = [
    ("datacenter", "data center server room corridor racks", "assets/img/photos/datacenter.jpg"),
    ("datacenter2", "server racks blue lights data centre", "assets/img/photos/datacenter2.jpg"),
    ("wafer", "silicon wafer macro processor", "assets/img/photos/wafer.jpg"),
    ("chip", "integrated circuit chip macro black", "assets/img/photos/chip.jpg"),
    ("gpu", "graphics card PCB close up", "assets/img/photos/gpu.jpg"),
    ("cable", "submarine communications cable", "assets/img/photos/cable.jpg"),
    ("power", "high voltage power lines pylon sunset", "assets/img/photos/power.jpg"),
    ("satellite", "satellite space earth orbit", "assets/img/photos/satellite.jpg"),
    ("robot", "industrial robot arm factory", "assets/img/photos/robot.jpg"),
    ("city", "city skyline night lights aerial", "assets/img/photos/city.jpg"),
]
for key, q, out in photos:
    commons_photo(q, os.path.join(BASE, out))
    time.sleep(3)

print("DONE")
