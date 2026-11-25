#!/usr/bin/env python3
"""Logos via Wikipedia pageimages (batched) + photos via Commons search (paced)."""
import json, os, time, urllib.request, urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(BASE, "assets", "img")
UA = {"User-Agent": "VibeDeckBuilder/1.0 (educational non-commercial use) Mozilla/5.0"}

def get(url, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    print("OK  ", os.path.relpath(path, BASE), len(data))

# key -> wikipedia title (pageimages = infobox logo)
brands = {
    "nvidia": "NVIDIA", "tsmc": "TSMC", "asml": "ASML", "samsung": "Samsung",
    "skhynix": "SK hynix", "amd": "Advanced Micro Devices", "intel": "Intel",
    "openai": "OpenAI", "anthropic": "Anthropic (company)", "google": "Google",
    "gemini": "Google Gemini", "meta": "Meta Platforms", "amazon": "Amazon (company)",
    "aws": "Amazon Web Services", "x": "X Corp.", "mistral": "Mistral AI",
    "elevenlabs": "ElevenLabs", "perplexity": "Perplexity AI", "midjourney": "Midjourney",
    "github": "GitHub", "colab": "Google Colab", "pytorch": "PyTorch",
    "huggingface": "Hugging Face", "python": "Python (programming language)",
}
titles = "|".join(brands.values())
q = urllib.parse.urlencode({
    "action": "query", "format": "json", "redirects": "1",
    "titles": titles, "prop": "pageimages", "piprop": "thumbnail", "pithumbsize": 320,
})
d = json.loads(get("https://en.wikipedia.org/w/api.php?" + q, timeout=60).decode())
title2key = {}
for k, t in brands.items():
    title2key[t] = k
# normalized lookup
norm = {}
for p in d.get("query", {}).get("pages", {}).values():
    th = p.get("thumbnail", {}).get("source")
    if not th:
        continue
    t = p.get("title", "")
    norm[t] = th
    if "normalized" in d.get("query", {}):
        for nn in d["query"]["normalized"]:
            if nn.get("to") == t:
                norm[nn.get("from", "")] = th
    if "redirects" in d.get("query", {}):
        for rr in d["query"]["redirects"]:
            if rr.get("to") == t:
                norm[rr.get("from", "")] = th
for k, t in brands.items():
    th = norm.get(t)
    if th:
        try:
            data = get(th, timeout=30)
            ext = ".png" if th.lower().split("?")[0].endswith((".svg", ".svg.png")) or "thumb" in th else ".png"
            save(os.path.join(IMG, "logos", k + ext), data)
        except Exception as e:
            print("ERR dl", k, e)
    else:
        print("NO LOGO", k, "(", t, ")")
    time.sleep(0.8)

# photos
def commons_photo(query, out, tries=2):
    for t in range(tries):
        try:
            q = urllib.parse.urlencode({
                "action": "query", "format": "json", "generator": "search",
                "gsrsearch": query + " filetype:bitmap", "gsrnamespace": 6, "gsrlimit": "10",
                "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "1600",
            })
            d = json.loads(get("https://commons.wikimedia.org/w/api.php?" + q, timeout=30).decode())
            cands = []
            for p in (d.get("query", {}).get("pages", {}) or {}).values():
                ii = (p.get("imageinfo") or [{}])[0]
                if ii.get("mime") == "image/jpeg" and ii.get("width", 0) >= 1400:
                    cands.append((ii.get("width", 0), ii.get("thumburl"), p.get("title", "")))
            cands.sort(reverse=True)
            if cands:
                data = get(cands[0][1], timeout=60)
                save(out, data)
                print("     from:", cands[0][2])
                return True
            print("no candidate:", query)
            return False
        except Exception as e:
            print("ERR", query, e)
            time.sleep(5)
    return False

photos = [
    ("data center server room corridor racks", "assets/img/photos/datacenter.jpg"),
    ("server racks blue lights data centre", "assets/img/photos/datacenter2.jpg"),
    ("silicon wafer macro", "assets/img/photos/wafer.jpg"),
    ("integrated circuit macro black background", "assets/img/photos/chip.jpg"),
    ("graphics card PCB close-up", "assets/img/photos/gpu.jpg"),
    ("submarine communications cable", "assets/img/photos/cable.jpg"),
    ("high voltage power lines pylon sunset", "assets/img/photos/power.jpg"),
    ("satellite orbit earth space", "assets/img/photos/satellite.jpg"),
]
for q, out in photos:
    commons_photo(q, os.path.join(BASE, out))
    time.sleep(2.5)

print("DONE")
