#!/usr/bin/env python3
import json, os, time, urllib.request, urllib.parse
BASE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "VibeDeckBuilder/1.0 (educational non-commercial) Mozilla/5.0"}
def get(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r: return r.read()
def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "wb").write(data)
    print("OK  ", os.path.relpath(path, BASE), len(data))

# ITS logo (2026 negative/white version, square)
save(os.path.join(BASE, "assets/img/logo-its.png"),
     get("https://www.its-ictacademy.com/wp-content/uploads/2025/03/ITS_Academy_Logo_2026_NEG-768x768.png"))

def commons(queries, out, minw=1200):
    for query in queries:
        try:
            q = urllib.parse.urlencode({"action":"query","format":"json","generator":"search",
                "gsrsearch":query,"gsrnamespace":6,"gsrlimit":"12","prop":"imageinfo",
                "iiprop":"url|size|mime","iiurlwidth":"1800"})
            d = json.loads(get("https://commons.wikimedia.org/w/api.php?"+q, timeout=30).decode())
            cands=[]
            for p in (d.get("query",{}).get("pages",{}) or {}).values():
                ii=(p.get("imageinfo") or [{}])[0]
                if ii.get("mime") in ("image/jpeg","image/png") and ii.get("width",0)>=minw:
                    cands.append((ii.get("width",0), ii.get("thumburl"), p.get("title","")))
            cands.sort(reverse=True)
            for w,url,title in cands[:3]:
                try:
                    data=get(url, timeout=90)
                    if len(data)>40000:
                        save(out, data); print("     q:", query, "| from:", title[:80]); return True
                except Exception: continue
            print("none:", query)
        except Exception as e: print("ERR", query, str(e)[:60])
        time.sleep(3)
    return False

def openverse(queries, out, minw=1400):
    for query in queries:
        try:
            q = urllib.parse.urlencode({"q": query, "page_size": 12, "size": "large"})
            d = json.loads(get("https://api.openverse.org/v1/images/?"+q, timeout=30).decode())
            for r in d.get("results", []):
                url = r.get("url") or ""
                if url.lower().endswith((".jpg",".jpeg",".png")) and (r.get("width") or 0) >= minw:
                    try:
                        data = get(url, timeout=60)
                        if len(data) > 60000:
                            save(out, data); print("     ov:", query, "|", (r.get("title") or "")[:70]); return True
                    except Exception: continue
            print("ov none:", query)
        except Exception as e: print("ERR ov", query, str(e)[:60])
        time.sleep(2)
    return False

# modern datacenter INTERIOR
out_i = os.path.join(BASE, "assets/img/photos/dc_interior.jpg")
if not os.path.exists(out_i):
    commons(["modern data center interior corridor", "hyperscale data center hall servers white",
             "Google data center interior servers", "server room modern LED racks",
             "data centre aisle containment modern"], out_i)
if not os.path.exists(out_i):
    openverse(["modern data center interior", "server room corridor modern"], out_i)

# datacenter EXTERIOR aerial / campus
out_e = os.path.join(BASE, "assets/img/photos/dc_exterior.jpg")
if not os.path.exists(out_e):
    commons(["data center building exterior", "hyperscale data center campus aerial",
             "Facebook data center Luleå exterior", "Microsoft data center exterior",
             "Amazon data center building", "cloud data center facility outside"], out_e)
if not os.path.exists(out_e):
    openverse(["data center building exterior aerial", "hyperscale data center campus"], out_e)

print("DONE")
