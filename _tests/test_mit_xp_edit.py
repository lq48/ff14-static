from lib import *
import json,os
# 減傷軸：電腦版「調整站位」——拖人、點名圈跟著、標記全步驟一起移、標題、增刪步驟、存回同一個站位圖
URL="mit.html?mock={}&team=s1&duty=d1"
L=json.load(open(os.path.join(os.path.dirname(__file__),"data","fru-p1-cyclonic-strat.json")))["rows"][0]
FIRE,THUN=L["xp"][0]["url"],L["xp"][1]["url"]
W="""async(a)=>{const fs=await import('https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js');const db=fs.getFirestore();await fs.setDoc(fs.doc(db,...a.path),a.data,{merge:true});}"""
DEC="""async(u)=>{const m=await import('./xivplan.js?v=2');return await m.xpDecode(u);}"""
row=lambda p,mech:p.locator("#gw tbody tr",has=p.locator(".cm .n",has_text=mech)).first
async def center(loc):
    b=await loc.bounding_box();return b["x"]+b["width"]/2,b["y"]+b["height"]/2
async def drag(p,loc,dx,dy,shift=False):
    x,y=await center(loc);await p.mouse.move(x,y);await p.mouse.down()
    if shift:await p.keyboard.down("Shift")
    for k in range(1,9):await p.mouse.move(x+dx*k/8,y+dy*k/8);await p.wait_for_timeout(15)
    await p.mouse.up()
    if shift:await p.keyboard.up("Shift")
    await p.wait_for_timeout(250)
def party(sc,i,k):
    for o in sc["steps"][i]["objects"]:
        if o.get("type")=="party" and o.get("name")==k:return o
async def m():
  async with async_playwright() as pw:
    b=await browser(pw)
    ctx,p,errs,calls=await open_page(b,URL.format("owner"),1440,900,init="localStorage.setItem('mitView','grid');");await p.wait_for_timeout(900)
    await p.evaluate(W,{"path":["statics","s1","mit","d1"],"data":{"rows":{"r4":{"xp":[{"label":"火","url":FIRE},{"label":"雷","url":THUN}],"rn":L["rn"]}}}});await p.wait_for_timeout(800)
    await row(p,"全體 AOE D").locator("[data-pv]").click();await p.wait_for_timeout(1000)
    ok(await p.locator("#dr [data-xedit]").count()==1,"電腦版能編輯的人看得到「調整站位」")
    await p.click('#dr [data-xi="1"]');await p.wait_for_timeout(300)
    await p.click("#dr [data-xedit]");await p.wait_for_timeout(800)
    ed=p.locator("#modal .xpedsheet")
    ok(await ed.count()==1 and await ed.locator(".xpv-stage svg").count()==1,"打開大視窗編輯")
    ok(await ed.locator('[data-xi="1"][aria-current="step"]').count()==1,"從原本看的那一步開始（0:17）")
    att=await ed.locator(".att text").evaluate_all("e=>e.map(x=>x.textContent)")
    ok(len(att)==4 and all("＋" in t for t in att),"火分攤圈：標示跟著兩個人 "+str(att))
    ok(await ed.locator(".trl").count()>0 and await ed.locator(".tok").count()==8,"編輯時看得到全員和軌跡")
    sc0=await p.evaluate(DEC,FIRE);mt0=party(sc0,1,"MT");d30=party(sc0,1,"D3")
    # 只拖 MT：分攤圈不跟（D3 還在）
    await drag(p,ed.locator('.tok[data-k="MT"]'),0,-60,shift=True)
    att2=await ed.locator(".att").count()
    ok(await p.locator("#modal .xpedsheet").count()==1,"拖曳後還在編輯")
    # Esc 不會丟掉
    await p.keyboard.press("Escape");await p.wait_for_timeout(200)
    ok(await p.locator("#modal .xpedsheet").count()==1,"有沒存的調整時按 Esc 不會關掉")
    # 拖 D3 到 MT 旁邊 → 自動對齊到同一點、分攤圈跟過去
    mx,my=await center(ed.locator('.tok[data-k="MT"]'));dx,dy=await center(ed.locator('.tok[data-k="D3"]'))
    await drag(p,ed.locator('.tok[data-k="D3"]'),mx-dx+4,my-dy+3)
    ok(await ed.locator('.tok[data-k="MT"]').get_attribute("data-pos")!=await ed.locator('.tok[data-k="D3"]').get_attribute("data-pos") and len(await ed.locator(".att").all())==4,"拖到別人旁邊：對齊成分攤（兩人並排顯示）")
    await p.screenshot(path=OUT+"/XPE-edit-1440.png")
    # 標記 A：所有步驟一起移
    await drag(p,ed.locator('.xm').first,30,0,shift=True)
    # 標題
    await ed.locator('[data-xcap="0"]').fill("0:18 第 2 下改")
    ok("0:18" in await ed.locator('[data-xi="1"]').inner_text(),"改標題：步驟按鈕跟著換時間")
    # 增刪步驟
    await ed.locator('[data-xe="add"]').click();await p.wait_for_timeout(200)
    ok(await ed.locator("[data-xi]").count()==5 and await ed.locator('[data-xi="2"][aria-current="step"]').count()==1,"複製成新的一步")
    await ed.locator('[data-xe="del"]').click();await p.wait_for_timeout(100)
    ok("再按一次" in await ed.locator('[data-xe="del"]').inner_text(),"刪除要按兩次")
    await ed.locator('[data-xe="del"]').click();await p.wait_for_timeout(200)
    ok(await ed.locator("[data-xi]").count()==4,"刪掉剛剛複製的那一步")
    # 復原：先做一個多餘的移動再復原
    await drag(p,ed.locator('.tok[data-k="H1"]'),-80,0,shift=True)
    h1a=await ed.locator('.tok[data-k="H1"]').get_attribute("data-pos")
    await ed.locator('[data-xe="undo"]').click();await p.wait_for_timeout(200)
    ok(await ed.locator('.tok[data-k="H1"]').get_attribute("data-pos")!=h1a,"復原上一個動作")
    n0=len(await p.evaluate("window.__writes"))
    await ed.locator('[data-xe="save"]').click();await p.wait_for_timeout(1800)
    ok(await p.locator("#modal").count()==0,"儲存後關閉")
    ws=[w for w in (await p.evaluate("window.__writes"))[n0:] if w["path"]=="statics/s1/mit/d1"]
    xp=ws[-1]["data"]["rows"]["r4"]["xp"] if ws else []
    ok(len(xp)==2 and xp[0]["label"]=="火" and xp[0]["url"]!=FIRE and xp[1]["url"]==THUN,"存回同一個站位圖（火），雷不動")
    sc=await p.evaluate(DEC,xp[0]["url"])
    mt=party(sc,1,"MT");d3=party(sc,1,"D3")
    ok(abs(mt["y"]-mt0["y"])>20 and abs(mt["x"]-d3["x"])<0.5 and abs(mt["y"]-d3["y"])<0.5,"MT 移動、D3 自動對齊到 MT 的位置 "+str((mt0["x"],mt0["y"],mt["x"],mt["y"],d3["x"],d3["y"])))
    circ=[o for o in sc["steps"][1]["objects"] if o["type"]=="circle" and abs(o["x"]-mt["x"])<1 and abs(o["y"]-mt["y"])<1]
    old=[o for o in sc["steps"][1]["objects"] if o["type"]=="circle" and abs(o["x"]-mt0["x"])<1 and abs(o["y"]-mt0["y"])<1]
    ok(len(circ)==1 and len(old)==0,"兩個人都移開後，分攤圈跟著走")
    ok(party(sc,0,"MT")["x"]==party(sc0,0,"MT")["x"],"其他步驟的位置不動")
    A=[[o["x"],o["y"]] for st in sc["steps"] for o in st["objects"] if o["type"]=="marker" and o["name"]=="A"]
    A0=[o for o in sc0["steps"][0]["objects"] if o["type"]=="marker" and o["name"]=="A"][0]
    ok(len(set(map(tuple,A)))==1 and A[0][0]!=A0["x"],"場地標記 A：所有步驟一起移 "+str(A[:2]))
    caps=[o["text"] for o in sc["steps"][1]["objects"] if o["type"]=="text"]
    ok("0:18 第 2 下改" in caps,"標題存進去")
    arr=[o for o in sc["steps"][1]["objects"] if o["type"]=="arrow"]
    ok(len(arr)==8 and all(o["color"]=="#ffffff" for o in arr),"依新位置重新產生移動箭頭（給 xivplan 看） "+str(len(arr)))
    await p.wait_for_timeout(600)
    ok(await p.locator("#dr .xpmount .xpv-stage svg").count()==1,"抽屜的站位圖換成新的")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # 一般成員、手機：沒有調整站位
    ctx,p,errs,calls=await open_page(b,URL.format("plain"),1440,900,init="localStorage.setItem('mitView','grid');");await p.wait_for_timeout(900)
    await p.evaluate(W,{"path":["statics","s1","mit","d1"],"data":{"rows":{"r4":{"xp":[{"label":"火","url":FIRE}]}}}});await p.wait_for_timeout(800)
    await row(p,"全體 AOE D").locator("[data-pv]").click();await p.wait_for_timeout(900)
    ok(await p.locator("#dr .xpv-stage svg").count()==1 and await p.locator("#dr [data-xedit]").count()==0,"一般成員沒有「調整站位」")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    ctx,p,errs,calls=await open_page(b,URL.format("owner"),390,800,init="localStorage.setItem('mitView','list');");await p.wait_for_timeout(900)
    await p.evaluate(W,{"path":["statics","s1","mit","d1"],"data":{"rows":{"r4":{"xp":[{"label":"火","url":FIRE}]}}}});await p.wait_for_timeout(900)
    await p.locator(".litem",has_text="全體 AOE D").locator(".xpthb").click();await p.wait_for_timeout(900)
    ok(await p.locator("#modal .xpv-stage svg").count()==1 and await p.locator("#modal [data-xedit]").count()==0,"手機不提供調整站位")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    await b.close();print(RES)
asyncio.run(m())
