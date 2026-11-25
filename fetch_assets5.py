#!/usr/bin/env python3
"""Remaining photos via Commons search, looser filters, multiple query variants."""
import json, os, time, urllib.request, urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "VibeDeckBuilder/1.0 (educational non-commercial) Mozilla/5.0"}

def get(url, timeout=45):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    print("OK  ", os.path.relpath(path, BASE), len(data))

def commons_photo(queries, out):
    for query in queries:
        try:
            q = urllib.parse.urlencode({
                "action": "query", "format": "json", "generator": "search",
                "gsrsearch": query, "gsrnamespace": 6, "gsrlimit": "12",
                "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "1600",
            })
            d = json.loads(get("https://commons.wikimedia.org/w/api.php?" + q, timeout=30).decode())
            cands = []
            for p in (d.get("query", {}).get("pages", {}) or {}).values():
                ii = (p.get("imageinfo") or [{}])[0]
                if ii.get("mime") in ("image/jpeg", "image/png") and ii.get("width", 0) >= 900:
                    cands.append((ii.get("width", 0), ii.get("thumburl"), p.get("title", "")))
            cands.sort(reverse=True)
            for w, url, title in cands[:3]:
                try:
                    data = get(url, timeout=60)
                    if len(data) > 30000:
                        save(out, data)
                        print("     q:", query, "| from:", title[:80])
                        return True
                except Exception:
                    continue
            print("none for:", query)
        except Exception as e:
            print("ERR", query, str(e)[:70])
        time.sleep(3)
    return False

targets = [
    (["data centre server racks", "server room datacenter", "Google data center servers", "rack mount servers"],
     "assets/img/photos/datacenter.jpg"),
    (["server room blue", "network server room", "server racks lights"],
     "assets/img/photos/datacenter2.jpg"),
    (["microprocessor CPU macro", "central processing unit chip", "CPU delidded"],
     "assets/img/photos/chip.jpg"),
    (["graphics card", "video card PCB", "GPU graphics card"],
     "assets/img/photos/gpu.jpg"),
    (["submarine communications cable", "cable ship undersea cable", "undersea fibre optic cable"],
     "assets/img/photos/cable.jpg"),
]
for queries, out in targets:
    if os.path.exists(os.path.join(BASE, out)):
        print("exists, skip:", out)
        continue
    commons_photo(queries, os.path.join(BASE, out))
    time.sleep(2)

print("DONE")
