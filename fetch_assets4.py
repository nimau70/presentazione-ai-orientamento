#!/usr/bin/env python3
"""Missing logos (simpleicons, single attempt) + photos via Openverse API."""
import json, os, time, urllib.request, urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(BASE, "assets", "img")
UA = {"User-Agent": "VibeDeckBuilder/1.0 (educational non-commercial) Mozilla/5.0"}

def get(url, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    print("OK  ", os.path.relpath(path, BASE), len(data))

# 1) missing logos from simpleicons (slug may not exist -> skip fast)
slugs = {"anthropic": "D97757", "midjourney": "FFFFFF", "pytorch": "EE4C2C",
         "huggingface": "FFD21E", "suno": "FFFFFF", "runway": "FFFFFF",
         "kling": "FFFFFF", "higgsfield": "FFFFFF"}
for slug, color in slugs.items():
    try:
        d = get(f"https://cdn.simpleicons.org/{slug}/{color}", timeout=20)
        if b"<svg" in d[:500]:
            save(os.path.join(IMG, "logos", slug + ".svg"), d)
        else:
            print("NO SVG", slug)
    except Exception as e:
        print("NO LOGO", slug, str(e)[:60])
    time.sleep(0.3)

# 2) photos via Openverse (no key needed, anonymous)
def openverse(query, out, tries=2):
    for t in range(tries):
        try:
            q = urllib.parse.urlencode({"q": query, "page_size": 12, "license_type": "all", "size": "large"})
            d = json.loads(get("https://api.openverse.org/v1/images/?" + q, timeout=30).decode())
            for r in d.get("results", []):
                url = r.get("url") or ""
                w = r.get("width") or 0
                if url and w >= 1200 and any(url.lower().endswith(e) for e in (".jpg", ".jpeg", ".png")):
                    try:
                        data = get(url, timeout=45)
                        if len(data) > 40000:
                            save(out, data)
                            print("     from:", r.get("title", "")[:70], "|", r.get("creator", ""))
                            return True
                    except Exception:
                        continue
            print("no result:", query)
            return False
        except Exception as e:
            print("ERR", query, str(e)[:80])
            time.sleep(4)
    return False

photos = [
    ("data center server racks corridor", "assets/img/photos/datacenter.jpg"),
    ("server room blue lights", "assets/img/photos/datacenter2.jpg"),
    ("silicon wafer", "assets/img/photos/wafer.jpg"),
    ("CPU processor macro", "assets/img/photos/chip.jpg"),
    ("graphics card GPU", "assets/img/photos/gpu.jpg"),
    ("submarine cable ship undersea", "assets/img/photos/cable.jpg"),
]
for q, out in photos:
    openverse(q, os.path.join(BASE, out))
    time.sleep(1.5)

print("DONE")
