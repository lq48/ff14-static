"""把 lastagous 的 7.11 減傷表（各階段時間軸）轉成網站減傷軸的匯入檔（type: mit-seed）
用法：python build.py 試算表匯出.txt [譯名對照.csv]
- 譯名對照.csv 的「繁中服正式名」欄有填的，優先使用；沒填的用簡中轉繁體暫代
- 輸出：fru-mit-seed.json（匯入用）、譯名對照.csv（給人補正式譯名）"""
import sys,csv,io,re,json,os
import opencc
cc=opencc.OpenCC('s2twp')
src=sys.argv[1];ov_path=sys.argv[2] if len(sys.argv)>2 else None
t=open(src,encoding='utf-8').read()
parts=re.split(r'^## Sheet name: (.+)$',t,flags=re.M)
sh={parts[i].strip():parts[i+1] for i in range(1,len(parts),2)}
TR={}
for r in list(csv.reader(io.StringIO(sh['Translate'].strip())))[1:]:
    if r and r[0]:TR[r[0]]={"en":r[1],"cn":r[5] if len(r)>5 else ""}
OV={}
if ov_path and os.path.exists(ov_path):
    for r in csv.DictReader(open(ov_path,encoding='utf-8-sig')):
        if (r.get("繁中服正式名") or "").strip():OV[r["日文"]]=r["繁中服正式名"].strip()
used={}  # 日文 -> 實際用到的
HEAD_EXTRA={"戦闘前":"開打前","開幕":"開場","塔":"踩塔"}
def tc(jp):
    jp=jp.replace("\n"," ").strip()
    if jp in OV:v=OV[jp]
    elif jp in HEAD_EXTRA:v=HEAD_EXTRA[jp]
    elif jp in TR and TR[jp]["cn"]:v=cc.convert(TR[jp]["cn"])
    else:
        m=re.match(r'^(.*?)\s*(\d+)\s*回目$',jp)
        if m:return tc(m.group(1))+f"（第 {m.group(2)} 次）"
        v=jp
    used.setdefault(jp,{"en":TR.get(jp,{}).get("en",""),"cn":TR.get(jp,{}).get("cn",""),"tc":v,"official":jp in OV})
    return v
def num(s):
    s=(s or "").replace(",","").strip()
    return int(s) if s.isdigit() else 0
def wan(n):
    if n>=9_000_000:return "即死"
    v=n/10000;return (f"{v:.1f}".rstrip("0").rstrip("."))+"萬"
DT={"Magic":"magic","Physical":"phys","Unique":"true","Darkness":"true"}
# 階段名（王的名字）翻譯表裡沒有，先放簡中譯名轉繁體，一樣列進譯名對照讓人改
BOSS_CN={"フェイトブレイカー":"绝命战士","シヴァ・ミトロン":"希瓦·米特隆","闇の巫女":"暗之巫女","2体":"双王","パンドラ・ミトロン":"潘多拉·米特隆"}
for k,v in BOSS_CN.items():TR.setdefault(k,{"en":"","cn":v})
stages=[];n_id=0;skipped={"AA":0,"倒數":0}
def rid():
    global n_id;n_id+=1;return f"f{n_id:03d}"
for name in [k for k in sh if re.match(r'P\d_',k)]:
    key=name[:2];rows=[]
    for r in csv.reader(io.StringIO(sh[name].strip())):
        if len(r)<15 or not re.match(r'^-?\d\d:\d\d$',r[3] or ''):continue
        tm=r[3]
        if tm.startswith("-"):skipped["倒數"]+=1;continue
        if r[1]:rows.append({"id":rid(),"kind":"head","mech":tc(r[1])})
        jp=r[5].strip()
        if jp in ("戦闘開始！",):continue
        if jp=="AA" or jp.endswith(" AA"):skipped["AA"]+=1;continue
        mm,ss=tm.split(":");row={"id":rid(),"t":f"{int(mm)}:{ss}","mech":tc(jp),"tag":"","ctag":"","hits":[]}
        atk=r[8].strip();tot,split,hit,dot,tick=num(r[10]),num(r[11]),num(r[12]),num(r[13]),num(r[14])
        dt=DT.get(r[6].strip(),"")
        if atk=="T Buster":row["tag"]="死刑";row["aoe"]="tank"
        elif atk=="T Share":row["tag"]="死刑";row["ctag"]="坦克分攤";row["aoe"]="tanks"
        elif atk=="Share":row["tag"]="分攤";row["aoe"]="share"
        elif hit and hit<9_000_000:row["aoe"]="all"   # 試算表沒標對象的有傷害招式：先當全體，團長再改
        elif hit>=9_000_000:row["tag"]="狂暴"   # 試算表用 9,999,999 表示時間到（轉場前沒打完）
        if hit:
            h={"dtype":dt,"dmg":f"{hit:,}" if hit<9_000_000 else "即死"}
            if dot and tick:h.update({"dot":f"{dot:,}","tk":tick,"iv":3})
            row["hits"].append(h)
        elif dot and tick:row["hits"].append({"dtype":dt,"dot":f"{dot:,}","tk":tick,"iv":3})
        desc=["日文："+jp]
        if split>1 and tot:desc.append(f"總傷害 {wan(tot)}，{split} 人分攤")
        row["desc"]="\n".join(desc)
        rows.append(row)
    # 把只有標題、後面沒有東西的標題去掉
    stages.append({"id":key.lower(),"name":key+" "+tc(name[3:]),"rows":rows})
# 血量：日文表 Option 分頁（坦克 225,800；「全て（一番低い人基準）」142,000）
def opt_hp(label):
    m=re.search(r'^,'+re.escape(label)+r',.*?,HP,,(\d+)',sh['Option'],flags=re.M);return int(m.group(1)) if m else 0
tank_hp=opt_hp("ナイト") or 225800;low_hp=opt_hp("全て(一番低い人基準)") or 142000
duty={"id":"fru","name":"絕光暗未來殲滅戰","level":100,"slots":["MT","ST","H1","H2","D1","D2","D3","D4"],"hp":{"tank":tank_hp,"ranged":low_hp,"caster":low_hp},"chain":5,"stages":stages}
out={"type":"mit-seed","v":1,"duty":duty}
json.dump(out,open("fru-mit-seed.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
with open("譯名對照.csv","w",encoding="utf-8-sig",newline="") as f:
    w=csv.writer(f);w.writerow(["日文","英文","簡中","目前使用（暫代）","繁中服正式名"])
    for jp,v in used.items():w.writerow([jp,v["en"],v["cn"],v["tc"],OV.get(jp,"")])
print({s["name"]:len(s["rows"]) for s in stages},"略過",skipped,"譯名",len(used),"已有正式名",len(OV))
