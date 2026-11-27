from lib import *
import json,re,os
# 減傷軸：xivplan 站位圖＋各位置走法（每個人看到「只看自己」的版本）
URL="mit.html?mock={}&team=s1&duty=d1"
L=json.load(open(os.path.join(os.path.dirname(__file__),"data","fru-p1-cyclonic-strat.json")))["rows"][0]
FIRE,THUN=L["xp"][0]["url"],L["xp"][1]["url"]
PRE="https://xivplan.netlify.app/#/plan/"
# 用 M6S 測試副本的「全體 AOE D」（1:10）當目標
STRAT=json.dumps({"type":"mit-strat","rows":[{"t":"1:10","mech":"全體 AOE D","xp":[{"label":"火","url":FIRE},{"label":"雷","url":THUN},{"label":"壞","url":"javascript:alert(1)"}],"rn":{**L["rn"],"XX":"不存在的位置"}},{"t":"9:99","mech":"不存在"}]},ensure_ascii=False)
W="""async(a)=>{const fs=await import('https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js');const db=fs.getFirestore();await fs.setDoc(fs.doc(db,...a.path),a.data,{merge:true});}"""
row=lambda p,mech:p.locator("#gw tbody tr",has=p.locator(".cm .n",has_text=re.compile("^"+re.escape(mech)+"$"))).first
DEC="""async(u)=>{const m=await import('./xivplan.js?v=1');const s=await m.xpDecode(u);return s.steps.map(st=>st.objects.filter(o=>o.type==='circle'&&o.hollow).length);}"""
async def view(p,v):
    if await p.locator(f'[data-a="vmode"][data-v="{v}"][aria-pressed="false"]').count():await p.click(f'[data-a="vmode"][data-v="{v}"]');await p.wait_for_timeout(300)
async def m():
  async with async_playwright() as pw:
    b=await browser(pw)
    # ---- 匯入（團主）----
    ctx,p,errs,calls=await open_page(b,URL.format("owner"),1440,900,init="localStorage.removeItem('mitView');");await p.wait_for_timeout(900);await view(p,"grid")
    await p.click('[data-a="io"]');await p.fill("#ta",STRAT)
    btn=p.locator('[data-a="import"]')
    await btn.click();await p.wait_for_timeout(150);await btn.click();await p.wait_for_timeout(1200)
    plan=[w for w in await p.evaluate("window.__writes") if w["path"]=="statics/s1/mit/d1"]
    d=plan[-1]["data"] if plan else {}
    r4=(d.get("rows") or {}).get("r4",{})
    ok([x["label"] for x in r4.get("xp",[])]==["火","雷"],"匯入：寫進火、雷兩張站位圖，非 xivplan 連結被丟掉")
    ok(sorted(r4.get("rn",{}))==sorted(["MT","ST","H1","H2","D1","D2","D3","D4"]),"匯入：八個位置的走法，不存在的位置被忽略")
    ok(r4.get("note") is None and (d.get("rows") or {}).get("r1",{}).get("note")=="大家集合在中間","匯入不動其他攻略欄位")
    chip=row(p,"全體 AOE D").locator("[data-pv]")
    ok(await chip.count()==1 and "站位圖 2" in await chip.inner_text() and "走法" in await chip.inner_text(),"表格上的攻略標籤：站位圖 2・走法")
    # 團主是 MT
    await chip.click();await p.wait_for_timeout(800)
    me=p.locator("#dr .rnme")
    ok(await me.count()==1 and "你（MT）" in await me.inner_text() and "和 D3 分攤" in await me.inner_text(),"抽屜攻略分頁：最上面是自己那句（MT）")
    a=p.locator("#dr a.xpbtn").first
    ok("看 MT 的站位" in await a.inner_text(),"按鈕寫「火・看 MT 的站位」")
    href=await a.get_attribute("href")
    ok(href.startswith(PRE) and href!=FIRE,"按鈕連結換成只看自己的版本")
    ok(await a.get_attribute("target")=="_blank" and await a.get_attribute("rel")=="noopener noreferrer","站位圖連結安全屬性")
    ok(await p.locator("#dr a.xpall").first.get_attribute("href")==FIRE,"旁邊有「全員」原版連結")
    hc=await p.evaluate(DEC,href);ok(hc and all(n==1 for n in hc),"只看自己的版本每一步都有一個黃圈 "+str(hc))
    ok(await p.locator('#dr [data-rn]').count()==8 and await p.locator('#dr #xpU').count()==1,"編輯者看得到 8 格走法和新增站位圖")
    await p.screenshot(path=OUT+"/XP-drawer-owner-1440.png")
    # 新增：非 xivplan 連結被拒
    n0=len(await p.evaluate("window.__writes"))
    await p.fill("#xpL","測");await p.fill("#xpU","https://evil.example/#/plan/abc");await p.click('#dr [data-a="xpadd"]');await p.wait_for_timeout(1500)
    ok(len([w for w in (await p.evaluate("window.__writes"))[n0:] if w["path"]=="statics/s1/mit/d1"])==0 and await p.locator("#dr a.xpbtn").count()==2,"非 xivplan 連結不會存")
    # 改一句走法
    await p.fill('#dr [data-rn="D4"]',"");await p.wait_for_timeout(1500)
    d=[w for w in await p.evaluate("window.__writes") if w["path"]=="statics/s1/mit/d1"][-1]["data"]
    ok("D4" not in d["rows"]["r4"]["rn"] and "MT" in d["rows"]["r4"]["rn"],"清空某位置的走法：那一格被移除，其他保留")
    # 只看 D3
    await p.click('[data-a="filt"][data-s="D3"]');await p.wait_for_timeout(600)
    if not await p.locator("#dr").is_visible():await chip.click();await p.wait_for_timeout(600)
    ok("你（D3）" in await p.inner_text("#dr .rnme") and "看 D3 的站位" in await p.locator("#dr a.xpbtn").first.inner_text(),"上方只看 D3：抽屜改顯示 D3 的走法和站位圖")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # ---- 一般成員（不能編輯）、XSS ----
    ctx,p,errs,calls=await open_page(b,URL.format("plain"),1440,900,init="localStorage.removeItem('mitView');");await p.wait_for_timeout(900);await view(p,"grid")
    await p.evaluate(W,{"path":["statics","s1","mit","d1"],"data":{"rows":{"r4":{"xp":[{"label":"火","url":FIRE},{"label":"<img src=x onerror=window.__x=1>","url":"javascript:window.__x=1"},{"label":"<b>x</b>","url":PRE+"abc\"onmouseover=\"window.__x=1"}],"rn":{"D1":"<img src=x onerror=window.__x=1>站 3","MT":"MT 的走法"}}}}})
    await p.wait_for_timeout(800)
    await row(p,"全體 AOE D").locator("[data-pv]").click();await p.wait_for_timeout(800)
    ok(await p.locator("#dr a.xpbtn").count()==1,"假的或壞掉的站位圖連結不會顯示")
    ok(await p.evaluate("window.__x")is None and await p.locator("#dr img[src=x]").count()==0,"走法內容不會執行 HTML")
    ok("你（D1）" in await p.inner_text("#dr .rnme"),"一般成員（D1）看到自己那句")
    ok(await p.locator('#dr [data-rn]').count()==0 and await p.locator('#dr #xpU').count()==0,"一般成員沒有編輯欄位")
    ok(await p.locator("#dr details.rnall").count()==1,"一般成員可以展開看其他位置的走法")
    await p.screenshot(path=OUT+"/XP-drawer-member-1440.png")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # ---- 手機清單 ----
    for w in (360,390):
      ctx,p,errs,calls=await open_page(b,URL.format("plain"),w,800,init="localStorage.removeItem('mitView');");await p.wait_for_timeout(900);await view(p,"list")
      await p.evaluate(W,{"path":["statics","s1","mit","d1"],"data":{"rows":{"r4":{"xp":[{"label":"火","url":FIRE},{"label":"雷","url":THUN}],"rn":L["rn"]}}}});await p.wait_for_timeout(900)
      it=p.locator(".litem",has_text="全體 AOE D")
      ok(await it.count()==1 and "你（D1）" in await it.inner_text() and await it.locator("a.xpbtn").count()==2,f"[{w}] 我的減傷清單：自己那句＋兩個站位圖按鈕")
      h=await it.locator("a.xpbtn").first.get_attribute("href");ok(h!=FIRE and h.startswith(PRE),f"[{w}] 清單按鈕是只看自己的版本")
      bx=await it.locator("a.xpbtn").first.bounding_box();ok(bx["height"]>=44,f"[{w}] 按鈕夠大好按")
      ok(await p.evaluate("document.documentElement.scrollWidth-innerWidth")<=0,f"[{w}] 無水平溢位")
      await it.scroll_into_view_if_needed();await p.screenshot(path=OUT+f"/XP-list-{w}.png")
      ok(errs==[],f"[{w}] 沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    await b.close();print(RES)
asyncio.run(m())
