"""tc_lib.py（繁中技能表 136 個）→ 網站技能庫匯入檔 mit-lib-tc.json
圖示：依名稱對到日文 7.11 減傷表的官方圖示網址（xivapi v2 高解析版），對不到的手動指定；仍沒有的留空（網站顯示文字方塊）"""
import csv,io,re,json,sys
import opencc
from tc_lib import R,INVULN
s2twp=opencc.OpenCC('s2twp');s2t=opencc.OpenCC('s2t')
t=open(sys.argv[1],encoding='utf-8').read()
parts=re.split(r'^## Sheet name: (.+)$',t,flags=re.M);sh={parts[i].strip():parts[i+1] for i in range(1,len(parts),2)}
rows=list(csv.reader(io.StringIO(sh['Skill'].strip())))[1:]
norm=lambda x:re.sub(r"[\s・·\-]","",x)
byname={};byen={}
for r in rows:
    if len(r)<51 or not r[45]:continue
    for n in (s2twp.convert(r[50]),s2t.convert(r[50]),r[50]):byname.setdefault(norm(n),r[45])
    byen.setdefault(r[46].strip(),r[45])
MANUAL={"禮儀之鈴":"Liturgy of the Bell(damage trigger)","地星":"Earthly Star(Giant Dominance)","大宇宙":"Macrocosmos(minimum)",
 "先天稟賦":"Essential Dignity(minimum)","天星交錯":"Celestial Intersection","乙太超流":"Aetherflow","消化":"Pepsis(Eukrasian Prognosis)",
 "療傷":"Cure","中療傷":"Cure II","大療傷":"Cure III","乙太契約":"Fey Union"}
def icon(name):
    u=byname.get(norm(name)) or byen.get(MANUAL.get(name,""))
    if not u:return ""
    m=re.search(r'/i/(\d{6})/(\d{6})\.png',u)
    return f"https://v2.xivapi.com/api/asset?path=ui/icon/{m.group(1)}/{m.group(2)}_hr1.tex&format=png" if m else ""
out={};noicon=[]
for x in R:
    if x["cat"]=="lb":continue
    fx=[]
    if x["ph"] or x["mg"]:
        if x["ph"]==x["mg"]:fx.append({"k":"mit","v":str(x["ph"]),"w":x["w"],"t":"all"})
        else:
            if x["ph"]:fx.append({"k":"mit","v":str(x["ph"]),"w":x["w"],"t":"phys"})
            if x["mg"]:fx.append({"k":"mit","v":str(x["mg"]),"w":x["w"],"t":"magic"})
    if x["sh"]!="":fx.append({"k":"shield","v":str(x["sh"]),"w":x["w"]})
    if (x["job"],x["name"]) in INVULN:fx.append({"k":"other","v":"無敵","w":"self"})
    # 表上的等級是「這個數值從幾級開始生效」（例：雪仇 Lv98 起持續 15 秒），不是學會技能的等級
    # 新技能一律從 1 級開始（Lv100 副本用的就是這組數值）；合併到既有技能時，才用 from 當成新的等級分頁
    tier={"lv":1,"from":x["lv"],"cd":x["cd"],"dur":x["dur"],"fx":fx}
    if x["ch"]>1:tier["ch"]=x["ch"]
    sk={"name":x["name"],"cat":x["cat"],"grp":x["grp"],"tiers":[tier]}
    if x["w"]=="target":sk["tgt"]="ally"
    ic=icon(x["name"])
    if ic:sk["img"]=ic
    else:noicon.append(x["name"])
    out.setdefault(x["job"],[]).append(sk)
json.dump({"type":"mit-lib","v":1,"src":"繁中工具箱「基礎計算資料」（絕 光暗未來殲滅戰、Lv100）；圖示：日文 7.11 減傷表","jobs":out},
          open(sys.argv[2],"w",encoding="utf-8"),ensure_ascii=False,separators=(",",":"))
print(sum(len(v) for v in out.values()),"skills, no icon:",noicon)
