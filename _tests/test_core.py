"""核心流程回歸：請假建立、揪團發起與回覆、分享到 Discord、登出（寫入內容照 firestore.rules 檢查）"""
from lib import *
def away_ok(w):  # match /away/{uid}
    d=w["data"];return set(d)<={"entries","updatedAt","by"} and isinstance(d.get("entries"),list) and len(d["entries"])<=100
def event_ok(w,uid):  # match /events/{eid} create
    d=w["data"];return d.get("by")==uid and isinstance(d.get("title"),str) and len(d["title"])<=40 and len(d.get("desc",""))<=1500
def rsvp_ok(w):  # match /events/{eid}/rsvp/{uid}
    d=w["data"];return set(d)<={"go","slots","jobs","note","at","updatedAt","by"} and d.get("go") in ("y","m","n")
async def m():
  async with async_playwright() as pw:
    b=await browser(pw)
    # ---- 請假：建立 ----
    ctx,p,errs,calls=await open_page(b,"away.html?mock=member",390,800)
    await p.click('[data-a="new"]');await p.wait_for_timeout(300)
    if await p.is_visible('[data-a="fnew"]'):await p.click('[data-a="fnew"]');await p.wait_for_timeout(200)
    from datetime import date,timedelta
    d1=(date.today()+timedelta(days=9)).isoformat();d2=(date.today()+timedelta(days=10)).isoformat()
    await p.fill('[data-ff="from"]',d1);await p.fill('[data-ff="to"]',d2)
    if await p.is_visible('[data-ff="label"]'):await p.fill('[data-ff="label"]',"回老家")
    await p.click('[data-a="fsave"]');await p.wait_for_timeout(600)
    ws=[w for w in await p.evaluate("__writes") if w["path"].startswith("away")]
    main=[w for w in ws if w["path"]=="away/u1"]
    ok(main and away_ok(main[-1]) and any(e.get("from")==d1 and e.get("to")==d2 for e in main[-1]["data"]["entries"]),"建立請假：寫入 away/u1，格式符合規則")
    ok(errs==[],"請假頁沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # ---- 揪團：發起 ----
    ctx,p,errs,calls=await open_page(b,"events.html?mock=member&new=1",390,800)
    await p.fill('[data-ff="title"]',"回歸測試團");await p.fill('[data-ff="desc"]',"說明 https://example.com")
    if not await p.query_selector('[data-sd="0"]'):await p.click('[data-a="sadd"]');await p.wait_for_timeout(200)
    await p.fill('[data-sd="0"]',d1);await p.fill('[data-st="0"]',"21:00")
    await p.click('[data-a="fsave"]');await p.wait_for_timeout(700)
    ws=[w for w in await p.evaluate("__writes") if w["path"].startswith("events/")]
    ev=[w for w in ws if w["path"].count("/")==1 and w["op"] in("setDoc","addDoc")]
    ok(ev and event_ok(ev[-1],"u1"),"發起揪團：作者是自己、標題與說明長度符合規則")
    eid=ev[-1]["path"].split("/")[1] if ev else ""
    ok("e="+eid in p.url or await p.is_visible('[data-a="go"]'),"發起後打開活動頁")
    # ---- 揪團：回覆 ----
    if not await p.is_visible('[data-a="go"]'):await p.goto(f"http://localhost:8765/events.html?mock=member&e={eid}");await p.wait_for_timeout(800)
    await p.click('[data-a="go"][data-v="y"]');await p.wait_for_timeout(150)
    sl=p.locator('[data-a="sl"][data-v="y"]')
    if await sl.count():await sl.first.click()
    jb=p.locator('[data-a="job"]')
    if await jb.count():await jb.first.click()   # 高難本範本要求選職業
    await p.click('[data-a="save"]');await p.wait_for_timeout(600)
    rs=[w for w in await p.evaluate("__writes") if "/rsvp/" in w["path"]]
    if not rs:print("   (debug) writes:",[(w["op"],w["path"]) for w in await p.evaluate("__writes")],"go:",await p.locator('[data-a="go"]').count())
    ok(rs and rsvp_ok(rs[-1]) and rs[-1]["path"].endswith("/rsvp/u1") and rs[-1]["data"]["go"]=="y","回覆揪團：寫入自己的 rsvp，go＝y，格式符合規則")
    # ---- 分享到 Discord（Worker /event，需帶 idToken） ----
    await p.click('[data-a="share"]');await p.wait_for_timeout(300);await p.click('#shareM [data-x="post"]');await p.wait_for_timeout(600)
    post=[c for c in calls if c["url"].endswith("/event")]
    ok(post and json.loads(post[0]["body"]).get("idToken") and json.loads(post[0]["body"]).get("eid")==eid,"分享到 Discord：呼叫 Worker /event，帶 idToken 與活動 ID")
    ok(errs==[],"揪團頁沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # ---- 一般團員看不到管理功能，總團長看得到 ----
    ctx,p,errs,calls=await open_page(b,"index.html?mock=plain&team=s1")
    ok(not await p.is_visible('[data-act="manage"]'),"一般團員：固定團頁沒有「管理」");await ctx.close()
    ctx,p,errs,calls=await open_page(b,"index.html?mock=owner&team=s1")
    ok(await p.is_visible('[data-act="manage"]'),"總團長：固定團頁有「管理」");await ctx.close()
    # ---- 登出：每一頁的選單都能登出 ----
    for url in ["events.html?mock=member","away.html?mock=member","memories.html?mock=member","mit.html?mock=member&team=s1"]:
        ctx,p,errs,calls=await open_page(b,url)
        await p.click("#sbUbtn");await p.click('[data-nav="logout"]');await p.wait_for_timeout(400)
        ok("signOut" in await p.evaluate("__log.join()") and await p.is_visible(".sb-login"),url.split("?")[0]+"：選單登出後顯示「登入」")
        await ctx.close()
    await b.close();print(RES)
asyncio.run(m())
