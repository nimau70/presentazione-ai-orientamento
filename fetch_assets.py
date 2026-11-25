#!/usr/bin/env python3
"""Fetch assets for the AI orientation deck: world geojson, portraits, logos, photos, thumbs, QR."""
import json, math, os, re, sys, urllib.request, urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(BASE, "assets", "img")
DATA = os.path.join(BASE, "assets", "data")

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36 VibeDeckBuilder/1.0 (contact: local educational use)"}

def get(url, binary=True, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read() if binary else r.read().decode("utf-8", "replace")

def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if isinstance(data, str):
        data = data.encode("utf-8")
    with open(path, "wb") as f:
        f.write(data)
    print("OK  ", os.path.relpath(path, BASE), len(data), "bytes")

def jget(url):
    return json.loads(get(url, binary=False))

# ---------- 1. TopoJSON -> GeoJSON ----------
def topo_to_geojson(topo_path, out_path):
    with open(topo_path, "r", encoding="utf-8") as f:
        topo = json.load(f)
    transform = topo.get("transform")
    scale = transform["scale"] if transform else [1, 1]
    translate = transform["translate"] if transform else [0, 0]
    arcs = topo["arcs"]
    # decode arcs to absolute coords
    decoded = []
    for arc in arcs:
        pts = []
        x = y = 0
        for dx, dy in arc:
            x += dx; y += dy
            pts.append([x * scale[0] + translate[0], y * scale[1] + translate[1]])
        decoded.append(pts)
    def arc_coords(idx):
        if idx >= 0:
            return decoded[idx]
        return list(reversed(decoded[~idx]))
    def ring(arcs_idx):
        pts = []
        for i in arcs_idx:
            seg = arc_coords(i)
            pts.extend(seg if not pts else seg[1:])
        return pts
    def geom(g):
        t = g["type"]
        if t == "Polygon":
            return {"type": "Polygon", "coordinates": [ring(r) for r in g["arcs"]]}
        if t == "MultiPolygon":
            return {"type": "MultiPolygon", "coordinates": [[ring(r) for r in poly] for poly in g["arcs"]]}
        if t == "LineString":
            return {"type": "LineString", "coordinates": ring(g["arcs"])}
        if t == "MultiLineString":
            return {"type": "MultiLineString", "coordinates": [ring(l) for l in g["arcs"]]}
        return None
    feats = []
    for g in topo["objects"]["countries"]["geometries"]:
        gg = geom(g)
        if gg:
            feats.append({"type": "Feature", "properties": {"name": g.get("properties", {}).get("name", "")}, "geometry": gg})
    fc = {"type": "FeatureCollection", "features": feats}
    save(out_path, json.dumps(fc))
    return len(feats)

n = topo_to_geojson(os.path.join(DATA, "countries-110m.json"), os.path.join(DATA, "world.geojson"))
print("geojson features:", n)

# ---------- 2. Wikipedia portraits ----------
people = {
    "musk": "Elon Musk",
    "huang": "Jensen Huang",
    "altman": "Sam Altman",
    "amodei": "Dario Amodei",
    "hassabis": "Demis Hassabis",
    "pichai": "Sundar Pichai",
    "bezos": "Jeff Bezos",
    "zuckerberg": "Mark Zuckerberg",
    "mensch": "Arthur Mensch",
    "su": "Lisa Su",
}
for key, title in people.items():
    try:
        q = urllib.parse.urlencode({"action": "query", "titles": title, "prop": "pageimages", "format": "json", "pithumbsize": 480})
        d = jget("https://en.wikipedia.org/w/api.php?" + q)
        pages = d["query"]["pages"]
        thumb = None
        for p in pages.values():
            thumb = p.get("thumbnail", {}).get("source")
        if thumb:
            save(os.path.join(IMG, "people", key + ".jpg"), get(thumb))
        else:
            print("NO THUMB", title)
    except Exception as e:
        print("ERR", title, e)

# ---------- 3. Commons logos & photos ----------
def commons_search(query, limit=6):
    q = urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": query + " filetype:svg OR filetype:bitmap", "gsrnamespace": 6, "gsrlimit": str(limit),
        "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": 400,
    })
    d = jget("https://commons.wikimedia.org/w/api.php?" + q)
    out = []
    for p in (d.get("query", {}).get("pages", {}) or {}).values():
        ii = (p.get("imageinfo") or [{}])[0]
        if ii.get("mime") in ("image/svg+xml", "image/png", "image/jpeg") and ii.get("width", 0) >= 100:
            out.append((p.get("title", ""), ii.get("thumburl") or ii.get("url"), ii.get("mime")))
    return out

logos = {
    "nvidia": "NVIDIA logo svg",
    "tsmc": "TSMC logo svg",
    "asml": "ASML logo svg",
    "samsung": "Samsung logo svg",
    "skhynix": "SK hynix logo svg",
    "amd": "AMD logo svg",
    "intel": "Intel logo svg",
    "openai": "OpenAI logo svg",
    "anthropic": "Anthropic logo svg",
    "google": "Google logo 2015 svg",
    "meta": "Meta Platforms logo svg",
    "amazon": "Amazon logo svg",
    "x": "X logo 2023 svg",
    "mistral": "Mistral AI logo svg",
    "apple": "Apple logo svg",
}
for key, q in logos.items():
    try:
        res = commons_search(q)
        if res:
            title, url, mime = res[0]
            ext = ".png" if "svg" in mime or mime == "image/svg+xml" else ".jpg"
            save(os.path.join(IMG, "logos", key + ext), get(url))
        else:
            print("NO LOGO", key)
    except Exception as e:
        print("ERR logo", key, e)

photos = {
    "datacenter": "data center server racks corridor",
    "datacenter2": "Google data center Council Bluffs servers",
    "wafer": "silicon wafer integrated circuits macro",
    "chip": "computer processor CPU macro photo",
    "gpu": "graphics card GPU PCB photo",
    "cable": "submarine communications cable shore landing",
    "power": "high voltage electricity pylons sunset",
    "grid": "electrical substation transformers",
    "satellite": "satellite in orbit earth",
}
for key, q in photos.items():
    try:
        q2 = urllib.parse.urlencode({
            "action": "query", "format": "json", "generator": "search",
            "gsrsearch": q + " filetype:bitmap", "gsrnamespace": 6, "gsrlimit": "8",
            "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": 1600,
        })
        d = jget("https://commons.wikimedia.org/w/api.php?" + q2)
        cands = []
        for p in (d.get("query", {}).get("pages", {}) or {}).values():
            ii = (p.get("imageinfo") or [{}])[0]
            if ii.get("mime") == "image/jpeg" and ii.get("width", 0) >= 1200:
                cands.append((p.get("title", ""), ii.get("thumburl"), ii.get("width", 0)))
        cands.sort(key=lambda c: -c[2])
        if cands:
            save(os.path.join(IMG, "photos", key + ".jpg"), get(cands[0][1]))
        else:
            print("NO PHOTO", key)
    except Exception as e:
        print("ERR photo", key, e)

# ---------- 4. YouTube thumbnails ----------
thumbs = {
    "sora": "gzneGhpXwjU",
    "veo": "ODyROOW1dCo",
    "veo2": "QYnJ3qJ5qJQ",
    "oasis": "jPP3fx64gPg",
    "astra": "hIIlJt8JERI",
    "runway": "br9b3-cxTPQ",
    "higgsfield": "qsgDMygRTto",
    "eleven": "zv_IoWIO5Ek",
    "suno": "lYaRuzzVRMc",
    "kling": "o9AfzyyUWX4",
}
for key, vid in thumbs.items():
    try:
        save(os.path.join(IMG, "thumbs", key + ".jpg"), get(f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"))
    except Exception as e:
        print("ERR thumb", key, e)

# ---------- 5. QR code ----------
try:
    qr = "https://api.qrserver.com/v1/create-qr-code/?size=500x500&margin=8&color=0b1220&bgcolor=ffffff&data=" + urllib.parse.quote("https://www.its-ictacademy.com/ai-digital-innovation-specialist/", safe="")
    save(os.path.join(IMG, "qr-its.png"), get(qr))
except Exception as e:
    print("ERR qr", e)

print("DONE")
