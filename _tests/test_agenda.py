from lib import *
async def m():
  async with async_playwright() as pw:
    b=await browser(pw)
    ctx,p,errs,calls=await open_page(b,"index.html?mock=member");await p.wait_for_timeout(500)
    t=await p.inner_text("#agendaBody");print("  ---\n"+t[:900]+"\n  ---")
    ok("固定團" in t and "M6S 開荒" in t and "20:00–23:00" in t,"顯示固定團既定活動與時間")
    ok("揪團" in t and "絕伊甸 練習" in t and "已定案" in t,"顯示已定案揪團")
    ok("揪團候選" in t and "候選時間，還在調查" in t,"候選時間另外標示為還在調查")
    ok("諾爾" in t and "可能不在 楓之旋律" in t,"有檢視權限時顯示團員請假")
    kinds=await p.evaluate("[...document.querySelectorAll('#agendaBody .ag')].map(a=>a.className)")
    bgs=await p.evaluate("[...new Set([...document.querySelectorAll('#agendaBody .ag-k')].map(k=>k.parentElement.className.split(' ')[1]+':'+getComputedStyle(k).backgroundColor))]");print("  標示顏色：",bgs)
    ok(len(set(x.split(':')[1] for x in bgs))>=2,"固定團與揪團使用不同底色（請假改成附註小字）")
    hrefs=await p.evaluate("[...document.querySelectorAll('#agendaBody .ag, #agendaBody .ag-awayl a')].map(a=>a.getAttribute('href'))");ok(all(h.startswith(("schedule.html?s=","events.html?e=","away.html")) for h in hrefs),"每一項都連到原本的完整頁面")
    ok(not any("12:00" in x for x in [t]) and "最多人有空" not in t,"不把調查空檔當成開團時間")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await p.screenshot(path=OUT+"/B-1280.png",full_page=True);await ctx.close()
    # 一般團員：只看得到自己的請假
    ctx,p,errs,calls=await open_page(b,"index.html?mock=plain");await p.wait_for_timeout(500)
    t=await p.inner_text("#agendaBody");ok("諾爾" not in t and "楓之旋律" not in t and "飛雷虛" not in t,"沒有檢視權限的人看不到別人的請假")
    ok("M6S 開荒" in t,"一般團員也看得到所屬固定團的活動")
    await ctx.close()
    # 沒資料
    ctx,p,errs,calls=await open_page(b,"index.html?mock=empty",375,812);await p.wait_for_timeout(400)
    t=await p.inner_text("#agendaBody");ok("接下來兩週沒有排定的活動或請假" in t,"沒有資料時顯示空狀態")
    ok(await p.evaluate("document.documentElement.scrollWidth-innerWidth")<=0,"手機無溢位");await ctx.close()
    ctx,p,errs,calls=await open_page(b,"index.html?mock=member",375,812);await p.wait_for_timeout(400)
    el=await p.query_selector("#agenda");await el.scroll_into_view_if_needed();await p.screenshot(path=OUT+"/B-375.png");
    ok(await p.evaluate("document.documentElement.scrollWidth-innerWidth")<=0,"手機（有資料）無溢位");await ctx.close()
    await b.close();print(RES)
asyncio.run(m())
