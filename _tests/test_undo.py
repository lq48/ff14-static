from lib import *
async def m():
  async with async_playwright() as pw:
    b=await browser(pw)
    # BiS 一鍵套用 → 復原
    ctx,p,errs,calls=await open_page(b,"index.html?mock=member&team=s1&mod=bis");await p.wait_for_timeout(600)
    before=await p.evaluate("JSON.stringify(window.__MOCK.db['statics/s1/bis/t1__u1'].final)")
    await p.click('[data-act="bisTemplate"]');await p.click('[data-act="bisTemplate"]');await p.wait_for_timeout(500)
    ok(await p.is_visible("#utoast") and "已套用常見配置" in await p.inner_text("#utoast"),"一鍵套用後出現可復原提示")
    changed=await p.evaluate("JSON.stringify(window.__MOCK.db['statics/s1/bis/t1__u1'].final)");ok(changed!=before,"套用確實改了資料")
    await p.click("#utoast .ut-undo");await p.wait_for_timeout(500)
    after=await p.evaluate("JSON.stringify(window.__MOCK.db['statics/s1/bis/t1__u1'].final)")
    ok(json.loads(after)==json.loads(before),"按「復原」後畢業設定完全回到原本")
    ok("已復原" in await p.inner_text("#utoast"),"顯示「已復原」")
    # 分裝紀錄 → 復原
    await p.click('[data-bistab="loot"]');await p.wait_for_timeout(300)
    sels=await p.evaluate("[...document.querySelectorAll('#view select')].map(s=>[s.getAttribute('data-loot')||s.id||s.className,[...s.options].map(o=>o.value).slice(0,8)])");print("  分裝表單：",sels)
    await ctx.close()
    # 大廳表單未儲存
    ctx,p,errs,calls=await open_page(b,"index.html?mock=member");await p.wait_for_timeout(500)
    await p.click("#sbUbtn");await p.click('[data-nav="profile"]');await p.wait_for_timeout(200)
    await p.fill("#pBio","還沒存的宣言");await p.wait_for_timeout(100)
    await p.click('.sb-nav [data-navk="team"]');await p.wait_for_timeout(300)
    ok(await p.is_visible("#pNick") and "再按一次" in await p.inner_text("#toast"),"表單沒存就切走：先提醒，不會直接離開")
    await p.click('.sb-nav [data-navk="team"]');await p.wait_for_timeout(500)
    ok(not await p.is_visible("#pNick"),"再按一次才離開")
    await p.click("#sbUbtn");await p.click('[data-nav="profile"]');await p.wait_for_timeout(200);await p.fill("#pBio","要存的");
    await p.click('[data-act="saveProfile"]');await p.wait_for_timeout(500)
    await p.click('.sb-nav [data-navk="tools"]');await p.wait_for_timeout(300)
    ok("再按一次" not in await p.inner_text("#toast") or not await p.is_visible("#pNick"),"儲存後就不會再提醒")
    p.on("dialog",lambda d:asyncio.ensure_future(d.dismiss()))
    await p.click("#sbUbtn");await p.click('[data-nav="profile"]');await p.wait_for_timeout(200);await p.fill("#pBio","又改了")
    bu=await p.evaluate("(()=>{const e=new Event('beforeunload',{cancelable:true});window.dispatchEvent(e);return e.defaultPrevented;})()")
    ok(bu,"關閉分頁時會跳出瀏覽器的離開確認")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # 請假：刪除 → 復原；表單未儲存
    ctx,p,errs,calls=await open_page(b,"away.html?mock=member");await p.wait_for_timeout(800)
    await p.evaluate("document.querySelector('[data-a=\"edit\"]')?document.querySelector('[data-a=\"edit\"]').click():null");await p.wait_for_timeout(300)
    if not await p.is_visible("#modal"):
        await p.click('[data-a="new"]');await p.wait_for_timeout(300)
    await p.click('[data-a="fcancel"]') if await p.is_visible('[data-a="fcancel"]') else None
    await p.wait_for_timeout(200)
    before=await p.evaluate("JSON.stringify(window.__MOCK.db['away/u1'])")
    dels=p.locator('[data-a="fdel"]');n=await dels.count();print("  刪除按鈕：",n)
    if n:
        await dels.first.click();await dels.first.click();await p.wait_for_timeout(500)
        mid=await p.evaluate("JSON.stringify(window.__MOCK.db['away/u1'])");ok(mid!=before and "已刪除" in await p.inner_text("#utoast"),"刪除請假後出現可復原提示")
        await p.click("#utoast .ut-undo");await p.wait_for_timeout(500)
        ok(json.loads(await p.evaluate("JSON.stringify(window.__MOCK.db['away/u1'])"))["entries"]==json.loads(before)["entries"],"復原後請假紀錄回來了")
    await p.click('[data-a="fnew"]');await p.wait_for_timeout(200)
    await p.fill('[data-ff="label"]',"出差") if await p.is_visible('[data-ff="label"]') else None
    await p.mouse.click(5,5);await p.wait_for_timeout(200)
    ok(await p.is_visible("#modal") and "還沒儲存" in await p.inner_text("#toast"),"請假表單有改動時，點背景不會直接關掉")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # 出席調查：清除勾選 → 復原；團長清除回覆 → 復原
    ctx,p,errs,calls=await open_page(b,"schedule.html?mock=member&s=sv1");await p.wait_for_timeout(500)
    await p.wait_for_selector("#fillGrid td.cell:not(.ev)")
    try:await p.wait_for_selector(".lvnote",timeout=8000)   # 請假提醒到了會重畫一次表格，先等它（不是這裡要測的，等不到就繼續）
    except Exception:pass
    await p.wait_for_timeout(300)  # 等請假提醒到齊再開始點（CI 機器較慢）
    c=p.locator("#fillGrid td.cell:not(.ev)");await c.nth(10).click();await c.nth(11).click()
    await p.click('[data-act="clear"]');await p.wait_for_timeout(200)
    ok(await p.locator("#fillGrid td.cell.on").count()==0,"全部清除")
    await p.click("#utoast .ut-undo");await p.wait_for_timeout(300)
    ok(await p.locator("#fillGrid td.cell.on").count()==2,"復原後勾選回來（2 格）")
    await p.click('.tab[data-tab="results"]');await p.wait_for_timeout(300)
    rb=p.locator('[data-remove="b"]');await rb.click();await rb.click();await p.wait_for_timeout(500)
    ok("surveys/sv1/responses/b" not in await p.evaluate("Object.keys(window.__MOCK.db).join()"),"團長清除 Satoru 的回覆")
    await p.click("#utoast .ut-undo");await p.wait_for_timeout(500)
    r=await p.evaluate("window.__MOCK.db['surveys/sv1/responses/b']");ok(r is not None and set(r.keys())<={"slots","updatedAt","note"},"復原後回覆回來，欄位符合規則（slots／updatedAt）")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # 復原失敗的提示
    ctx,p,errs,calls=await open_page(b,"index.html?mock=member&team=s1&mod=bis");await p.wait_for_timeout(600)
    await p.click('[data-act="bisTemplate"]');await p.click('[data-act="bisTemplate"]');await p.wait_for_timeout(400)
    await p.evaluate("window.__MOCK.failWrites='permission-denied'");await p.click("#utoast .ut-undo");await p.wait_for_timeout(400)
    ok("復原失敗：沒有權限" in await p.inner_text("#utoast"),"復原失敗時說明原因");await ctx.close()
    await b.close();print(RES)
asyncio.run(m())
