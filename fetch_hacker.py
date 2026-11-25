#!/usr/bin/env python3
import json, os, time, urllib.request, urllib.parse
BASE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "VibeDeckBuilder/1.0 (educational non-commercial) Mozilla/5.0"}
def get(url, timeout=45):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r: return r.read()

def commons(queries, out):
    for query in queries:
        try:
            q = urllib.parse.urlencode({"action":"query","format":"json","generator":"search",
                "gsrsearch":query,"gsrnamespace":6,"gsrlimit":"12","prop":"imageinfo",
                "iiprop":"url|size|mime","iiurlwidth":"1400"})
            d = json.loads(get("https://commons.wikimedia.org/w/api.php?"+q, timeout=30).decode())
            cands=[]
            for p in (d.get("query",{}).get("pages",{}) or {}).values():
                ii=(p.get("imageinfo") or [{}])[0]
                if ii.get("mime") in ("image/jpeg","image/png") and ii.get("width",0)>=900:
                    cands.append((ii.get("width",0), ii.get("thumburl"), p.get("title","")))
            cands.sort(reverse=True)
            for w,url,title in cands[:3]:
                try:
                    data=get(url, timeout=60)
                    if len(data)>25000:
                        open(out,"wb").write(data); print("OK", out, len(data), "| from:", title[:70]); return True
                except Exception: continue
            print("none:", query)
        except Exception as e: print("ERR", query, str(e)[:60])
        time.sleep(3)
    return False

out = os.path.join(BASE, "assets/img/photos/hacker.jpg")
if not os.path.exists(out):
    commons(["Matrix digital rain code green", "hacker silhouette hoodie", "cybersecurity padlock digital",
             "computer virus code screen dark", "Anonymous mask hacker", "malware code screen"], out)
if not os.path.exists(out):
    for qy in ["hacker code screen dark", "cyber attack computer"]:
        try:
            q = urllib.parse.urlencode({"q": qy, "page_size": 10, "size": "large"})
            d = json.loads(get("https://api.openverse.org/v1/images/?"+q, timeout=30).decode())
            done = False
            for r in d.get("results", []):
                url = r.get("url") or ""
                if url.lower().endswith((".jpg",".jpeg",".png")) and (r.get("width") or 0) >= 1200:
                    try:
                        data = get(url, timeout=45)
                        if len(data) > 40000:
                            open(out,"wb").write(data)
                            print("OK openverse", len(data), r.get("title","")[:60]); done = True; break
                    except Exception: continue
            if done: break
        except Exception as e: print("ERR ov", qy, str(e)[:60])
        time.sleep(2)
print("DONE", os.path.exists(out))
