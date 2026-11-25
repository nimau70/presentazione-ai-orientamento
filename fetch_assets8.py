#!/usr/bin/env python3
"""Proper datacenter photos via Commons categories + Openverse, saved as candidates for visual check."""
import json, os, time, urllib.request, urllib.parse
BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "assets", "img", "cand")
os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "VibeDeckBuilder/1.0 (educational non-commercial) Mozilla/5.0"}
def get(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r: return r.read()

def cat_members(cat, limit=60):
    q = urllib.parse.urlencode({"action":"query","format":"json","list":"categorymembers",
        "cmtitle":"Category:"+cat,"cmtype":"file","cmlimit":str(limit)})
    d = json.loads(get("https://commons.wikimedia.org/w/api.php?"+q, timeout=30).decode())
    return [m["title"] for m in d.get("query",{}).get("categorymembers",[])]

def thumbs(titles, width=1600):
    if not titles: return {}
    q = urllib.parse.urlencode({"action":"query","format":"json","titles":"|".join(titles[:40]),
        "prop":"imageinfo","iiprop":"url|size|mime","iiurlwidth":str(width)})
    d = json.loads(get("https://commons.wikimedia.org/w/api.php?"+q, timeout=30).decode())
    out = {}
    for p in d.get("query",{}).get("pages",{}).values():
        ii = (p.get("imageinfo") or [{}])[0]
        if ii.get("mime") in ("image/jpeg","image/png") and ii.get("width",0) >= 1200:
            out[p["title"]] = (ii.get("thumburl"), ii.get("width",0))
    return out

def openverse(query, limit=10):
    q = urllib.parse.urlencode({"q": query, "page_size": limit, "size": "large"})
    try:
        d = json.loads(get("https://api.openverse.org/v1/images/?"+q, timeout=30).decode())
        res = []
        for r in d.get("results", []):
            url = r.get("url") or ""
            if url.lower().endswith((".jpg",".jpeg",".png")) and (r.get("width") or 0) >= 1400:
                res.append((url, r.get("title") or "", r.get("creator") or ""))
        return res
    except Exception as e:
        print("ERR ov", query, str(e)[:60]); return []

interior_cats = ["Server rooms", "Server room", "Data centers", "Interiors of data centers", "Computer rooms", "Data centre interiors"]
exterior_cats = ["Data centers", "Buildings of data centers", "Exteriors of data centers", "Industrial buildings", "Warehouses"]

print("== INTERIOR candidates ==")
n = 0
for cat in interior_cats:
    try:
        titles = cat_members(cat)
        th = thumbs(titles)
        for t,(u,w) in list(th.items()):
            if any(k in t.lower() for k in ["server","data cent","datacenter","rack","room","corridor","aisle"]):
                n += 1
                try:
                    data = get(u, timeout=90)
                    if len(data) > 50000:
                        open(os.path.join(OUT, f"int_{n:02d}.jpg"), "wb").write(data)
                        print(f"int_{n:02d}.jpg  {w}px  {t[:90]}")
                except Exception: pass
    except Exception as e:
        print("ERR cat", cat, str(e)[:60])
    time.sleep(2)
    if n >= 10: break

for qy in ["data center server aisle corridor", "colocation server room racks", "hyperscale datacenter interior hall"]:
    for i,(u,t,c) in enumerate(openverse(qy)[:4]):
        n += 1
        try:
            data = get(u, timeout=60)
            if len(data) > 60000:
                open(os.path.join(OUT, f"int_{n:02d}.jpg"), "wb").write(data)
                print(f"int_{n:02d}.jpg  OV  {t[:60]} | {c[:30]}")
        except Exception: pass
    time.sleep(2)
    if n >= 16: break

print("== EXTERIOR candidates ==")
m = 0
for cat in exterior_cats:
    try:
        titles = cat_members(cat)
        th = thumbs(titles)
        for t,(u,w) in list(th.items()):
            if any(k in t.lower() for k in ["data cent","datacenter","server","warehouse","industrial","cooling","facebook","google","amazon","microsoft","apple","equinix","digital realty","qts","switch"]):
                m += 1
                try:
                    data = get(u, timeout=90)
                    if len(data) > 50000:
                        open(os.path.join(OUT, f"ext_{m:02d}.jpg"), "wb").write(data)
                        print(f"ext_{m:02d}.jpg  {w}px  {t[:90]}")
                except Exception: pass
    except Exception as e:
        print("ERR cat", cat, str(e)[:60])
    time.sleep(2)
    if m >= 10: break

for qy in ["data center building exterior", "server farm building outside", "data center rooftop chillers cooling", "hyperscale data center campus"]:
    for i,(u,t,c) in enumerate(openverse(qy)[:4]):
        m += 1
        try:
            data = get(u, timeout=60)
            if len(data) > 60000:
                open(os.path.join(OUT, f"ext_{m:02d}.jpg"), "wb").write(data)
                print(f"ext_{m:02d}.jpg  OV  {t[:60]} | {c[:30]}")
        except Exception: pass
    time.sleep(2)
    if m >= 16: break

print("DONE int:", n, "ext:", m)
