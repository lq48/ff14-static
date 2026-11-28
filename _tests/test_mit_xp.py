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
#DEC="""async(u)=>{const m=await import('./xivplan.js?v=2');const s=await m.xpDecode(u);return s.steps.map(st=>st.objects.filter(o=>o.type==='circle'&&o.hollow).length);}"""
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
    ok(await chip.count()==1 and "站位圖 火・雷" in await chip.inner_text() and "走法" in await chip.inner_text(),"表格上的攻略標籤：站位圖 火・雷・走法")
    # 團主是 MT：先看到「看」的畫面
    await chip.click();await p.wait_for_timeout(1000)
    ok(await p.locator('#dr [data-a="sedit"]').count()==1 and await p.locator('#dr [data-rn]').count()==0,"有內容時先顯示閱讀畫面，編輯欄位收起來")
    me=p.locator("#dr .rnme")
    ok(await me.count()==1 and "你（MT）" in await me.inner_text() and "和 D3 分攤" in await me.inner_text(),"最上面是自己那句（MT）")
    ok(await p.locator("#dr .xpmount .xpv-stage svg").count()==1,"站位圖直接畫在抽屜裡")
    ok(await p.locator("#dr .xpv-seg button").all_inner_texts()==["火","雷"],"火／雷切換")
    ok(await p.locator("#dr .xpv-steps button").all_inner_texts()==["0:15","0:17","0:19","0:21"],"步驟按鈕用時間標示")
    ok("0:15" in await p.inner_text("#dr .xpv-cap"),"說明文字顯示第一步")
    ok("只看我（MT）" in await p.inner_text("#dr .xpv-me") and await p.is_checked("#dr [data-xme]"),"預設只看我")
    tok=lambda k:p.locator(f'#dr .tok[aria-label="{k}"]')
    ok(await tok("MT").locator(".ring").evaluate("e=>getComputedStyle(e).display")!="none" and float(await tok("ST").evaluate("e=>e.style.opacity"))<.5,"自己有黃圈、其他人變淡")
    ok("icons/jobs/PLD.webp" in (await tok("MT").locator("image").get_attribute("href") or ""),"有職業的位置用職業圖示")
    t0=await tok("MT").get_attribute("data-pos");a0=await tok("MT").get_attribute("transform")
    await p.click('#dr [data-xi="1"]');await p.wait_for_timeout(350);am=await tok("MT").get_attribute("transform")
    await p.wait_for_timeout(900);a1=await tok("MT").get_attribute("transform")
    ok(am not in (a0,a1) and a0!=a1,"換步驟時隊員是平移過去的（中途有在半路） "+str((a0,am,a1)))
    xy=lambda a:[float(v) for v in a[a.index("(")+1:-1].split()]
    ok(abs(sum(v*v for v in xy(am))**.5-sum(v*v for v in xy(a0))**.5)<12,"繞著王走弧線，不是直線切過去")
    ok("0:17" in await p.inner_text("#dr .xpv-cap") and await tok("MT").get_attribute("data-pos")!=t0,"切到 0:17：說明換了、自己移動了")
    ok(await p.locator("#dr .trl.me").count()==1 and await p.locator("#dr .trl:not(.me)").count()==0 and await p.locator("#dr .xa").count()==0,"只看我：只剩自己的細虛線軌跡，不畫箭頭")
    await p.screenshot(path=OUT+"/XP-drawer-owner-1440.png")
    # 自動播放
    await p.click('#dr [data-xp]');await p.wait_for_timeout(1600)
    ok("0:19" in await p.inner_text("#dr .xpv-cap") and await p.get_attribute('#dr [data-xp]',"aria-pressed")=="true","按播放：自動跑到下一步")
    await p.click('#dr [data-xp]');await p.wait_for_timeout(2200)
    ok("0:19" in await p.inner_text("#dr .xpv-cap") and await p.get_attribute('#dr [data-xp]',"aria-label")=="自動播放","再按一次暫停")
    await p.click('#dr [data-xi="1"]');await p.wait_for_timeout(400)
    ok(await p.evaluate("(()=>{const v=document.querySelector('#dr .xpv-stage svg').viewBox.baseVal;return v.width>=600})()"),"顯示完整場地（不自動放大）")
    ok(await p.locator("#dr .xpv-floor circle[r='150']").count()>=1,"P1 場地底圖（e11）用向量畫出來")
    await p.click('#dr .xpv-arr[data-xs="1"]');await p.wait_for_timeout(500)
    ok("0:19" in await p.inner_text("#dr .xpv-cap"),"下一步按鈕")
    await p.click('#dr [data-xv="1"]');await p.wait_for_timeout(700)
    ok("0:19" in await p.inner_text("#dr .xpv-cap") and await p.locator('#dr [data-xv="1"][aria-pressed="true"]').count()==1,"換成雷，停在同一步")
    xl=p.locator("#dr .xpv-foot a");ok(await xl.get_attribute("href")==THUN and await xl.get_attribute("rel")=="noopener noreferrer","「在 xivplan 開啟」連到目前的版本")
    await p.click("#dr [data-xme]");await p.wait_for_timeout(400)
    ok(float(await tok("ST").evaluate("e=>e.style.opacity"))>.9 and await tok("MT").locator(".ring").evaluate("e=>getComputedStyle(e).display")=="none","取消只看我：全員一樣清楚")
    await p.click("#dr [data-xme]");await p.wait_for_timeout(300)
    # 編輯
    await p.click('#dr [data-a="sedit"]');await p.wait_for_timeout(400)
    ok(await p.locator('#dr [data-rn]').count()==8 and await p.locator('#dr #xpU').count()==1 and await p.locator('#dr .xpmount').count()==0,"按「編輯攻略」：出現欄位，閱讀畫面收起來（不重複）")
    n0=len(await p.evaluate("window.__writes"))
    await p.fill("#xpL","測");await p.fill("#xpU","https://evil.example/#/plan/abc");await p.click('#dr [data-a="xpadd"]');await p.wait_for_timeout(1500)
    ok(len([w for w in (await p.evaluate("window.__writes"))[n0:] if w["path"]=="statics/s1/mit/d1"])==0 and await p.locator("#dr .xpl").count()==2,"非 xivplan 連結不會存")
    await p.fill('#dr [data-rn="D4"]',"");await p.wait_for_timeout(1500)
    d=[w for w in await p.evaluate("window.__writes") if w["path"]=="statics/s1/mit/d1"][-1]["data"]
    ok("D4" not in d["rows"]["r4"]["rn"] and "MT" in d["rows"]["r4"]["rn"],"清空某位置的走法：那一格被移除，其他保留")
    await p.screenshot(path=OUT+"/XP-drawer-edit-1440.png")
    await p.click('#dr [data-a="sdone"]');await p.wait_for_timeout(600)
    ok(await p.locator('#dr [data-rn]').count()==0 and await p.locator("#dr .xpmount .xpv-stage svg").count()==1,"按「完成」回到閱讀畫面")
    # 只看 D3
    await p.click('[data-a="filt"][data-s="D3"]');await p.wait_for_timeout(800)
    ok("你（D3）" in await p.inner_text("#dr .rnme") and "只看我（D3）" in await p.inner_text("#dr .xpv-me"),"上方只看 D3：抽屜改成 D3 的走法和站位圖")
    # 分攤錯開：D4 從 1 走過來、H2 從 B 走過來 → D4 在北（y 比較小）
    await p.click('#dr [data-xv="0"]');await p.wait_for_timeout(500);await p.click('#dr [data-xi="1"]');await p.wait_for_timeout(1200)
    d4=[float(v) for v in (await tok("D4").get_attribute("data-pos")).split(",")];h2=[float(v) for v in (await tok("H2").get_attribute("data-pos")).split(",")]
    ok(d4[1]<h2[1] and abs(d4[0]-h2[0])<40,"火分攤：D4 在上、H2 略下，兩個人並排 "+str((d4,h2)))
    mt=[float(v) for v in (await tok("MT").get_attribute("data-pos")).split(",")];d3=[float(v) for v in (await tok("D3").get_attribute("data-pos")).split(",")]
    ok(mt[0]>d3[0],"MT 從 A 往逆時針、D3 從 4 往順時針：MT 在東側、D3 在西側")
    await p.click('#dr [data-xv="1"]');await p.wait_for_timeout(600);await p.click('#dr [data-xi="3"]');await p.wait_for_timeout(1200)
    rs=[]
    for k in ["MT","ST","H1","H2","D1","D2","D3","D4"]:
      x,y=[float(v) for v in (await tok(k).get_attribute("data-pos")).split(",")];rs.append(round((x*x+y*y)**.5))
    ok(all(95<=r<=115 for r in rs),"雷 0:21：所有人回到內圈（不用再散開） "+str(rs))
    ok(await p.locator("#dr .xm [stroke-dasharray]").count()==8,"場地標記是虛線框")
    ok(await p.locator("#dr .xe path").count()>=6,"王有身位圈（正面三角、兩側箭頭）")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # ---- 一般成員（不能編輯）、XSS、壞掉的資料 ----
    ctx,p,errs,calls=await open_page(b,URL.format("plain"),1440,900,init="localStorage.removeItem('mitView');");await p.wait_for_timeout(900);await view(p,"grid")
    await p.evaluate(W,{"path":["statics","s1","mit","d1"],"data":{"rows":{"r4":{"xp":[{"label":"<img src=x onerror=window.__x=1>","url":FIRE},{"label":"js","url":"javascript:window.__x=1"},{"label":"<b>x</b>","url":PRE+"abc\"onmouseover=\"window.__x=1"}],"rn":{"D1":"<img src=x onerror=window.__x=1>站 3","MT":"MT 的走法"}},"r1":{"xp":[{"label":"壞","url":PRE+"AAAA"}]}}}})
    await p.wait_for_timeout(800)
    await row(p,"全體 AOE D").locator("[data-pv]").click();await p.wait_for_timeout(1000)
    ok(await p.locator("#dr .xpmount .xpv-stage svg").count()==1 and await p.locator("#dr .xpv-seg").count()==0,"假的或壞掉的站位圖連結被濾掉，只剩一張就不顯示切換")
    ok(await p.evaluate("window.__x")is None and await p.locator("#dr img[src=x]").count()==0,"名稱、走法不會執行 HTML")
    ok("你（D1）" in await p.inner_text("#dr .rnme") and "只看我（D1）" in await p.inner_text("#dr .xpv-me"),"一般成員（D1）看到自己那句和自己的站位")
    ok(await p.locator('#dr [data-a="sedit"]').count()==0 and await p.locator('#dr [data-rn]').count()==0,"一般成員沒有編輯按鈕")
    ok(await p.locator("#dr details.rnall").count()==1,"可以展開看其他位置的走法")
    await p.screenshot(path=OUT+"/XP-drawer-member-1440.png")
    await row(p,"全體 AOE A").locator(".mb .n").click();await p.wait_for_timeout(800)
    await p.click('#dr [data-a="drtab"][data-k="s"]');await p.wait_for_timeout(800)
    ok(await p.locator("#dr .xpv-err").count()==1 and await p.locator("#dr .xpv-err a").get_attribute("rel")=="noopener noreferrer","讀不出來的站位圖：顯示提示和原始連結")
    th=await p.evaluate("""async(u)=>{const m=await import('./xp-render.js?v=7');return await m.xpThumb(u,{me:'',job:()=>''});}""",FIRE)
    ok(">MT<" in th and "<image" not in th,"沒設定職業時用位置文字")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # ---- 手機清單 ----
    for w in (360,390):
      ctx,p,errs,calls=await open_page(b,URL.format("plain"),w,800,init="localStorage.removeItem('mitView');");await p.wait_for_timeout(900);await view(p,"list")
      await p.evaluate(W,{"path":["statics","s1","mit","d1"],"data":{"rows":{"r4":{"xp":[{"label":"火","url":FIRE},{"label":"雷","url":THUN}],"rn":L["rn"]}}}});await p.wait_for_timeout(1200)
      it=p.locator(".litem",has_text="全體 AOE D")
      ok(await it.count()==1 and "你（D1）" in await it.inner_text() and await it.locator(".xpthb .xpthi svg").count()==1,f"[{w}] 我的減傷清單：自己那句＋站位圖縮圖")
      bx=await it.locator(".xpthb").bounding_box();ok(bx["height"]>=44,f"[{w}] 縮圖按鈕夠大好按")
      ok(await p.evaluate("document.documentElement.scrollWidth-innerWidth")<=0,f"[{w}] 無水平溢位")
      await it.scroll_into_view_if_needed();await p.screenshot(path=OUT+f"/XP-list-{w}.png")
      await it.locator(".xpthb").click();await p.wait_for_timeout(1000)
      ok(await p.locator("#modal .xpmount .xpv-stage svg").count()==1 and "你（D1）" in await p.inner_text("#modal"),f"[{w}] 點縮圖：彈出完整站位圖")
      await p.click('#modal [data-xi="1"]');await p.wait_for_timeout(600)
      ok(await p.evaluate("(()=>{const m=document.querySelector('#modal .sheet');return m.scrollWidth<=m.clientWidth+1})()"),f"[{w}] 彈出視窗沒有水平溢位")
      await p.screenshot(path=OUT+f"/XP-modal-{w}.png")
      await p.click('#modal [data-a="mclose"]');await p.wait_for_timeout(300)
      ok(await p.locator("#modal").count()==0,f"[{w}] 可以關閉")
      ok(errs==[],f"[{w}] 沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    await b.close();print(RES)
asyncio.run(m())
