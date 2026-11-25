#!/usr/bin/env python3
"""New thumbs for 2026 videos + extra photos (NVIDIA GPU detail, risks, EU)."""
import json, os, time, urllib.request, urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(BASE, "assets", "img")
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

thumbs = {
    "astra": "C1zYX5jwqq4", "fable": "6a1QSJlsYpU", "veo31": "B78BJuPxmBU",
    "gen45": "ei2PsDpPbB4", "kling4": "nlM7kL3kv_Y", "elevenv4": "th_tXR2QQ6U",
    "sunov6": "_lHvWn2SNC4",
}
for key, vid in thumbs.items():
    try:
        save(os.path.join(IMG, "thumbs", key + ".jpg"), get(f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg", timeout=20))
    except Exception as e:
        print("ERR thumb", key, e)
    time.sleep(0.5)

def commons_photo(queries, out, minw=900):
    for query in queries:
        try:
            q = urllib.parse.urlencode({
                "action": "query", "format": "json", "generator": "search",
                "gsrsearch": query, "gsrnamespace": 6, "gsrlimit": "12",
                "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": "1400",
            })
            d = json.loads(get("https://commons.wikimedia.org/w/api.php?" + q, timeout=30).decode())
            cands = []
            for p in (d.get("query", {}).get("pages", {}) or {}).values():
                ii = (p.get("imageinfo") or [{}])[0]
                if ii.get("mime") in ("image/jpeg", "image/png") and ii.get("width", 0) >= minw:
                    cands.append((ii.get("width", 0), ii.get("thumburl"), p.get("title", "")))
            cands.sort(reverse=True)
            for w, url, title in cands[:3]:
                try:
                    data = get(url, timeout=60)
                    if len(data) > 25000:
                        save(out, data)
                        print("     q:", query, "| from:", title[:75])
                        return True
                except Exception:
                    continue
            print("none for:", query)
        except Exception as e:
            print("ERR", query, str(e)[:70])
        time.sleep(3)
    return False

targets = [
    (["NVIDIA H100 GPU", "NVIDIA GH100 die", "NVIDIA DGX H100", "NVIDIA Blackwell B200 chip", "GB200 superchip"],
     "assets/img/photos/nvidia_gpu.jpg"),
    (["NVIDIA GeForce RTX 4090 graphics card", "NVIDIA RTX 5090"],
     "assets/img/photos/nvidia_card.jpg"),
    (["flooded street city flood water", "flooding urban street"],
     "assets/img/photos/flood.jpg"),
    (["hacker hoodie computer code dark", "cyber attack code screen"],
     "assets/img/photos/hacker.jpg"),
    (["video call laptop screen", "video conference laptop"],
     "assets/img/photos/videocall.jpg"),
    (["European Parliament Strasbourg hemicycle", "European Union flag Brussels Berlaymont"],
     "assets/img/photos/eu.jpg"),
    (["server fire smoke datacenter", "wildfire burning forest"],
     "assets/img/photos/fire.jpg"),
    (["balance scale justice", "gavel court"],
     "assets/img/photos/bias.jpg"),
]
for queries, out in targets:
    if os.path.exists(os.path.join(BASE, out)):
        print("exists, skip:", out); continue
    commons_photo(queries, os.path.join(BASE, out))
    time.sleep(2)

print("DONE")
