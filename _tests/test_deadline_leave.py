from lib import *
# 揪團：結束時間、回覆截止；出席調查：請假提醒
async def m():
  async with async_playwright() as pw:
    b=await browser(pw)
    # ---- 結束時間：顯示成時間範圍（含跨午夜）
    ctx,p,errs,calls=await open_page(b,"events.html?mock=member&e=e3",1280,900);await p.wait_for_timeout(600)
    t=await p.inner_text("#app")
    ok("14:00–17:00" in t,"候選時間顯示開始到結束")
    ok("回覆截止" in t and "還有 4 小時" in t or "還有 5 小時" in t,"詳情頁顯示回覆截止與剩下的時間")
    ok(await p.locator('[data-a="save"]').count()==1,"截止前可以回覆")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    ctx,p,errs,calls=await open_page(b,"events.html?mock=member",1280,900);await p.wait_for_timeout(600)
    t=await p.inner_text("#app");ok("22:00–01:00" in t,"跨午夜的時間照原樣顯示（22:00–01:00）")
    ok("回覆已截止" in t,"列表上標示回覆已截止");await ctx.close()
    # ---- 截止後：一般成員不能回覆
    ctx,p,errs,calls=await open_page(b,"events.html?mock=member&e=e4",390,850);await p.wait_for_timeout(600)
    t=await p.inner_text("#app")
    ok(await p.locator('[data-a="save"]').count()==0 and "回覆已截止" in t and "你這次沒有回覆" in t,"截止後一般成員看不到回覆表單，說明找發起人")
    ok(await p.evaluate("document.documentElement.scrollWidth-innerWidth")<=0,"手機無溢位")
    await p.screenshot(path=OUT+"/D-closed-390.png",full_page=True)
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # ---- 截止後：發起人／總團長還能改
    ctx,p,errs,calls=await open_page(b,"events.html?mock=owner&e=e4",1280,900);await p.wait_for_timeout(600)
    t=await p.inner_text("#app")
    ok(await p.locator('[data-a="save"]').count()==1 and "只有你（發起人／總團長）還能修改" in t,"截止後發起人還能修改，並看到說明")
    await ctx.close()
    # ---- 發起：結束時間 + 開打前 3 小時截止，寫進資料庫的格式
    ctx,p,errs,calls=await open_page(b,"events.html?mock=member&new=1",1280,900);await p.wait_for_timeout(600)
    if await p.locator('[data-ff="title"]').count()==0:
      await p.click('[data-a="new"]');await p.wait_for_timeout(300)
    await p.fill('[data-ff="title"]',"測試截止")
    se=p.locator('[data-se="0"]');await se.fill("23:30")
    await p.click('[data-a="duem"][data-k="3h"]');await p.wait_for_timeout(200)
    prev=await p.inner_text("#duePrev");ok("截止時間：" in prev,"選「開打前 3 小時」會預覽截止時間："+prev)
    await p.click('[data-a="fsave"]');await p.wait_for_timeout(600)
    ws=[w for w in await p.evaluate("__writes") if w["path"].startswith("events/") and "/rsvp/" not in w["path"]]
    d=ws[-1]["data"] if ws else {}
    s0=(d.get("slots") or [{}])[0]
    ok(s0.get("te")=="23:30" and s0.get("t")=="21:00","候選時間存了結束時間 te："+str(s0))
    first=await p.evaluate("(s=>{const[y,m,dd]=s.d.split('-').map(Number);const[h,mi]=s.t.split(':').map(Number);return new Date(y,m-1,dd,h,mi).getTime();})(arguments[0])".replace("arguments[0]",__import__("json").dumps(s0))) if s0 else 0
    ok(isinstance(d.get("due"),(int,float)) and abs(d["due"]-(first-3*3600e3))<1000,"due＝最早的候選時間往前 3 小時")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]))
    # 不設定 → due=0
    await ctx.close()
    ctx,p,errs,calls=await open_page(b,"events.html?mock=member",1280,900);await p.wait_for_timeout(500)
    await p.click('[data-a="new"]');await p.wait_for_timeout(300);await p.fill('[data-ff="title"]',"不截止");await p.click('[data-a="fsave"]');await p.wait_for_timeout(500)
    ws=[w for w in await p.evaluate("__writes") if w["path"].startswith("events/")];ok(ws and ws[-1]["data"].get("due")==0 and "te" not in ws[-1]["data"]["slots"][0],"不設定截止、不填結束：due=0、沒有 te")
    await ctx.close()
    # 編輯有截止的活動：以「自訂」帶出原本的時間
    ctx,p,errs,calls=await open_page(b,"events.html?mock=owner&e=e3",1280,900);await p.wait_for_timeout(500)
    await p.click('[data-a="edit"]');await p.wait_for_timeout(300)
    ok(await p.locator('[data-a="duem"][data-k="custom"][aria-pressed="true"]').count()==1 and await p.locator('[data-due]').input_value()!="","編輯時帶出原本的截止時間")
    await p.screenshot(path=OUT+"/D-form-1280.png",full_page=True)
    await ctx.close()
    for w in (360,):
      ctx,p,errs,calls=await open_page(b,"events.html?mock=member",w,800);await p.wait_for_timeout(500)
      await p.click('[data-a="new"]');await p.wait_for_timeout(300)
      ok(await p.evaluate("document.documentElement.scrollWidth-innerWidth")<=0,f"[{w}] 發起表單（含結束時間）無溢位")
      el=await p.query_selector(".srow");await el.scroll_into_view_if_needed();await p.screenshot(path=OUT+f"/D-form-{w}.png")
      await ctx.close()
    # ---- 大廳：待辦寫出截止時間；已截止的不列入
    ctx,p,errs,calls=await open_page(b,"index.html?mock=member",1280,900);await p.wait_for_timeout(700)
    t=await p.inner_text("#todoH >> xpath=..")
    ok("幻 青龍初見團" in t and "截止回覆" in t,"待辦寫出截止時間")
    ok("週末夜跑團" not in t,"已截止的揪團不列入待辦")
    ag=await p.inner_text("#agendaBody");ok("14:00–17:00" in ag,"近期安排也顯示時間範圍")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # ---- 出席調查：請假提醒
    ctx,p,errs,calls=await open_page(b,"schedule.html?mock=member&s=sv1",1280,900);await p.wait_for_timeout(800)
    if await p.locator('[data-member="a"]').count():await p.click('[data-member="a"]');await p.wait_for_timeout(300)
    t=await p.inner_text("#fillView")
    ok("請假行事曆提醒" in t and "你在" in t,"填寫的人看到自己的請假提醒")
    ok(await p.locator("#fillGrid th.dh .lvm.lv-off").count()==1,"自己請假的日期在表格上標出來")
    cells=await p.evaluate("[...document.querySelectorAll('#fillGrid td.cell.on')].length");ok(cells==0,"沒有自動幫忙勾或取消")
    await p.screenshot(path=OUT+"/S-fill-1280.png")
    await p.click('[data-tab="results"]') if await p.locator('[data-tab="results"]').count() else None
    await p.wait_for_timeout(400)
    r=await p.inner_text("#resultsView")
    ok("請假行事曆" in r and "請假 諾爾" in r and "請假 飛雷虛" in r,"有權限的人在結果看到調查期間誰請假")
    ok("和請假衝突？" in r and "Satoru" in r,"請假當天卻勾了時間的標出衝突")
    ok(await p.locator("#heatGrid th.dh .lvm").count()>=3,"結果表格的日期也標出請假人數")
    el=await p.query_selector(".lvpanel");await el.screenshot(path=OUT+"/S-leave-panel.png")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # 沒有檢視權限：只看到自己的，結果區沒有請假區塊
    ctx,p,errs,calls=await open_page(b,"schedule.html?mock=plain&s=sv1",1280,900);await p.wait_for_timeout(800)
    if await p.locator('[data-member="d"]').count():await p.click('[data-member="d"]');await p.wait_for_timeout(300)
    if await p.locator('[data-tab="results"]').count():await p.click('[data-tab="results"]');await p.wait_for_timeout(300)
    r=await p.inner_text("#resultsView");ok("請假行事曆" not in r and await p.locator("#heatGrid .lvm").count()==0,"沒有檢視權限的人看不到別人的請假")
    allr=await p.evaluate("window.__reads")
    reads=[x for x in allr if x.startswith("away") and x not in ("away/u5","awayCfg/main")]
    ok("away/u5" in allr and reads==[],"只讀自己的請假，不會去讀別人的 "+str(reads[:3]))
    await ctx.close()
    # 未登入：完全沒有請假資訊
    ctx,p,errs,calls=await open_page(b,"schedule.html?mock=signedout&s=sv1",390,850);await p.wait_for_timeout(800)
    if await p.locator('[data-member="a"]').count():await p.click('[data-member="a"]');await p.wait_for_timeout(300)
    t=await p.inner_text("body");ok("請假行事曆" not in t and await p.locator(".lvm").count()==0,"未登入看不到任何請假資訊")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    await b.close();print(RES)
asyncio.run(m())
