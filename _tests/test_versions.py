# 快取版本號檢查：改了 JS 模組卻沒把 ?v= 加一，使用者的瀏覽器會一直用舊檔（例：「調整站位」按鈕看不到）
# 改了某個檔案後：把所有引用它的 ?v= 加一，再執行 python _tests/test_versions.py --update
import re,glob,hashlib,json,os,sys
H=os.path.dirname(os.path.abspath(__file__));R=os.path.dirname(H);V=os.path.join(H,"data","versions.json")
os.chdir(R)
refs={}
for f in glob.glob("*.html")+glob.glob("*.js"):
    for m in re.finditer(r'\./([a-z0-9_-]+\.(?:js|css))\?v=(\d+)',open(f,encoding="utf-8").read()):
        refs.setdefault(m.group(1),{}).setdefault(int(m.group(2)),[]).append(f)
sha=lambda k:hashlib.sha256(open(k,"rb").read()).hexdigest()[:16]
rec=json.load(open(V))
if "--update" in sys.argv:
    for k,vs in refs.items():
        v=max(vs);old=rec.get(k)
        if old and old["sha"]!=sha(k) and v<=old["v"]:print(f"！ {k} 內容改了，請先把 ?v= 加到 {old['v']+1} 以上");sys.exit(1)
        rec[k]={"v":v,"sha":sha(k)}
    json.dump(rec,open(V,"w"),indent=1);print("已更新 versions.json");sys.exit(0)
P=F=0
def ok(c,m):
    global P,F
    if c:P+=1;print("PASS",m)
    else:F+=1;print("FAIL",m)
for k,vs in sorted(refs.items()):
    ok(len(vs)==1,f"{k}：所有頁面用同一個版本號 {sorted(vs)}"+("" if len(vs)==1 else "（"+"、".join(f"v{v}: {','.join(fs)}" for v,fs in vs.items())+"）"))
    r=rec.get(k);v=max(vs)
    ok(r is not None and r["sha"]==sha(k) and r["v"]==v,f"{k}：內容有改就要加版本號（目前 v{v}）"+("" if r and r["sha"]==sha(k) else "→ 檔案改過了：?v= 加一後執行 python _tests/test_versions.py --update"))
print({"pass":P,"fail":F})
