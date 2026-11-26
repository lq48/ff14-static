"""日文 7.11 減傷表的 Skill 分頁 → 網站技能庫的效果參考資料 mit-ref.json
每個技能取等級最高的那筆（Lv100 適用）；只轉減傷與護盾（回復不列入血量計算）
護盾數值：Barrier 是威力，依 Option 分頁的標準屬性換算成 HP（Heal100／Barrier100），屬約略值"""
import sys,csv,io,re,json
import opencc
s2twp=opencc.OpenCC('s2twp');s2t=opencc.OpenCC('s2t')
t=open(sys.argv[1],encoding='utf-8').read()
parts=re.split(r'^## Sheet name: (.+)$',t,flags=re.M);sh={parts[i].strip():parts[i+1] for i in range(1,len(parts),2)}
rows=list(csv.reader(io.StringIO(sh['Skill'].strip())))[1:]
JOBJP={"ナイト":"PLD","戦士":"WAR","暗黒騎士":"DRK","ガンブレイカー":"GNB","白魔道士":"WHM","学者":"SCH","占星術師":"AST","賢者":"SGE",
 "モンク":"MNK","竜騎士":"DRG","忍者":"NIN","侍":"SAM","リーパー":"RPR","ヴァイパー":"VPR","吟遊詩人":"BRD","機工士":"MCH","踊り子":"DNC",
 "黒魔道士":"BLM","召喚士":"SMN","赤魔道士":"RDM","ピクトマンサー":"PCT"}
ROLEJP={"タンク":["PLD","WAR","DRK","GNB"],"近接":["MNK","DRG","NIN","SAM","RPR","VPR"],"キャスター":["BLM","SMN","RDM","PCT"]}
W={"SELF":"self","SINGLE_PARTY":"target","RANGE_PARTY":"party","RANGE_ENEMY":"enemy","SINGLE_ENEMY":"enemy"}
# 標準屬性（Option 分頁）：治療 100 威力＝多少 HP；坦克 Barrier100；坦克最大 HP
opt=sh['Option']
def optv(job,key):
    m=re.search(r'^,'+re.escape(job)+r',.*?'+key+r',,(\d+)',opt,flags=re.M);return int(m.group(1)) if m else 0
HEAL100={"WHM":optv("白魔道士","Heal100") or 3823,"AST":optv("占星術師","Heal100") or 3898,"SCH":optv("学者","Heal100") or 3806,"SGE":optv("賢者","Heal100") or 3823}
BAR100=optv("ナイト","Barrier100") or 6524;TANK_HP=225800
num=lambda s:float(s.replace(",","")) if s and re.match(r'^[\d.,]+$',s) else None
best={}
for r in rows:
    if len(r)<51 or not r[1]:continue
    lv=int(r[3] or 0);key=(r[0],r[1])
    if lv>100:continue
    if key not in best or lv>best[key][0]:best[key]=(lv,r)
out={}
for (role,jp),(lv,r) in best.items():
    jobs=[JOBJP[role]] if role in JOBJP else ROLEJP.get(role,[])
    if not jobs:continue
    fx=[];w=W.get(r[7],"self")
    eff=num(r[4]) or 0;mt=num(r[9])
    mg,ph=num(r[10]),num(r[11])
    def addmit(t,mul):
        if mul is None or mul>=1:return
        f={"k":"mit","v":str(round((1-mul)*100,1)).rstrip("0").rstrip("."),"w":w,"t":t}
        if mt and mt!=eff:f["d"]=int(mt)
        fx.append(f)
    if mg is not None and ph is not None and mg==ph:addmit("all",mg)
    else:addmit("magic",mg);addmit("phys",ph)
    for job in jobs:
        jf=[dict(f) for f in fx]
        # 護盾：Barrier（威力）或 Barrier Buffed（施放者最大 HP 的比例）
        bt,bv=num(r[39]),num(r[40]);bbt,bbv=num(r[33]),num(r[34])
        if bv and bt:
            per=HEAL100.get(job,0) or BAR100
            f={"k":"shield","v":str(int(round(bv*per/100,-2))),"w":w,"c2":"約，依標準屬性換算"};
            if bt!=eff:f["d"]=int(bt)
            jf.append(f)
        if bbv and bbt and bbv<1:
            f={"k":"shield","v":str(int(round(bbv*TANK_HP,-2))),"w":w,"c2":"約，施放者最大 HP 的 "+str(round(bbv*100))+"%"}
            if bbt!=eff:f["d"]=int(bbt)
            jf.append(f)
        if not jf:continue
        cn=r[50]
        out.setdefault(job,[]).append({"jp":jp,"en":r[46],"cn":cn,"names":list(dict.fromkeys(filter(None,[s2twp.convert(cn),s2t.convert(cn),cn]))),
            "lv":lv,"cd":num(r[5]),"dur":eff,"fx":jf})
for j in out:out[j].sort(key=lambda x:-x["lv"])
json.dump({"src":"@lastagous FFXIV 7.11 減傷表（Skill 分頁）","v":1,"jobs":out},open(sys.argv[2],"w",encoding="utf-8"),ensure_ascii=False,separators=(",",":"))
print({j:len(v) for j,v in out.items()})
for j in ["PLD","SCH","WHM","MNK"]:
    for s in out.get(j,[])[:8]:print(j,s["names"],s["dur"],s["fx"])
