import asyncio
from lib import *
async def ctxp(b,url,w=1280,h=900,dark=False):
    ctx=await b.new_context(viewport={"width":w,"height":h},color_scheme="dark" if dark else "light",is_mobile=w<500,has_touch=w<500)
    await ctx.add_init_script(FIX);await ctx.route("**/*",route);p=await ctx.new_page();errs=[];p.on("pageerror",lambda e:errs.append(str(e)))
    await p.goto("http://localhost:8765/"+url);await p.wait_for_timeout(900);return ctx,p,errs
def ok(c,msg):print(("PASS " if c else "FAIL ")+msg)
async def m():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(**LAUNCH)
        ctx,p,errs=await ctxp(b,"index.html?mock=member")
        # nav menu
        await p.click("#sbUbtn");await p.wait_for_timeout(100)
        ok(await p.is_visible("#sbMenu"),"使用者選單可以打開")
        ok(await p.evaluate("document.activeElement&&document.activeElement.closest('#sbMenu')!==null"),"打開選單後焦點移到第一個項目")
        await p.keyboard.press("Escape");await p.wait_for_timeout(100)
        ok(not await p.is_visible("#sbMenu") and await p.evaluate("document.activeElement.id")=="sbUbtn","Esc 關閉選單並回到按鈕")
        await p.click("#sbUbtn");await p.click('[data-theme-set="dark"]');await p.wait_for_timeout(100)
        ok(await p.evaluate("document.documentElement.dataset.theme")=="dark" and await p.evaluate("localStorage.themePref")=="dark","切換深色並記住")
        await p.click('[data-theme-set=""]');ok(await p.evaluate("!document.documentElement.dataset.theme"),"切回跟隨系統")
        await p.click('[data-nav="skin"]');ok(await p.evaluate("!document.documentElement.dataset.skin && localStorage.skinPref==='classic'"),"可換回舊版外觀")
        await p.click("#sbUbtn");await p.click('[data-nav="skin"]');ok(await p.evaluate("document.documentElement.dataset.skin==='cozy'"),"可換回溫馨外觀")
        # profile via menu
        await p.click("#sbUbtn");await p.click('[data-nav="profile"]');await p.wait_for_timeout(150)
        ok(await p.is_visible("#pNick"),"選單「我的靈魂水晶」打開編輯表單")
        await p.click('[data-navk="lobby"] >> nth=0');await p.wait_for_timeout(200)
        ok(await p.is_visible("#nextH"),"點品牌回到大廳")
        # jump
        await p.click('.sb-nav [data-navk="tools"]');await p.wait_for_timeout(1600)
        y=await p.evaluate("[document.getElementById('tools').getBoundingClientRect().top, innerHeight+scrollY>=document.documentElement.scrollHeight-2]");ok(abs(y[0])<80 or y[1],f"導覽「工具」捲到工具區（top={y[0]:.0f}，到底={y[1]}）")
        ok(await p.evaluate("performance.getEntriesByType('navigation').length===1 && !!document.getElementById('nextH')"),"跳區塊不會重新載入頁面")
        # quick tiles
        await p.evaluate("window.scrollTo(0,0)");await p.click('.qt[data-act="openBis"]');await p.wait_for_timeout(300)
        ok("mod=bis" in p.url and await p.is_visible("text=BiS 裝備獲取表"),"「裝備進度」直接開啟該團 BiS")
        ok(await p.evaluate("document.querySelector('.sb-nav [aria-current=page]').dataset.navk")=="team","在固定團頁時導覽標示「固定團」")
        await p.go_back();await p.wait_for_timeout(300);ok(await p.is_visible("#nextH"),"瀏覽器上一頁回到大廳")
        await p.click('.qt[data-act="openTeam"]');await p.wait_for_timeout(300);ok("team=s1" in p.url and await p.is_visible("text=陣容"),"「我的固定團」開啟固定團")
        await p.click('.sb-nav [data-navk="team"]');await p.wait_for_timeout(800);ok(await p.is_visible("#teams") and "team=" not in p.url,"在固定團頁點導覽「固定團」回大廳固定團區")
        # todo manage
        await p.click('.todo-list [data-act="openManage"]');await p.wait_for_timeout(300);ok(await p.is_visible("text=管理") and await p.evaluate("location.search.includes('team=s1')"),"待辦「申請加入」打開管理頁")
        await p.goto("http://localhost:8765/index.html?mock=member");await p.wait_for_timeout(900)
        await p.click('[data-act="membersToggle"]');await p.wait_for_timeout(100);ok(await p.is_visible(".crystals"),"展開完整靈魂水晶")
        hrefs=await p.evaluate("[...document.querySelectorAll('.quick a,.todo-list a,#nextBody a')].map(a=>a.getAttribute('href'))");print("  連結：",hrefs)
        ok(await p.evaluate("(window.__writes||[]).filter(w=>w.path!=='users/u1').length")==0,"大廳操作沒有額外寫入（只有原本的 Discord 名稱同步）")
        # logout
        await p.click("#sbUbtn");await p.click('[data-nav="logout"]');await p.wait_for_timeout(300)
        ok(await p.is_visible("text=用 Discord 登入") and "signOut" in await p.evaluate("__log.join()"),"登出後回到未登入首頁")
        ok(errs==[],"大廳沒有 JS 錯誤 "+str(errs[:2]))
        await ctx.close()
        # discord login redirect target
        ctx,p,errs=await ctxp(b,"index.html?mock=signedout")
        req=[]
        p.on("request",lambda r:req.append(r.url) if "workers.dev" in r.url else None)
        await p.click('[data-act="dclogin"]',no_wait_after=True);await p.wait_for_timeout(800)
        ok(req and "/auth/discord/login?return=http%3A%2F%2Flocalhost%3A8765%2Findex.html" in req[0],"Discord 登入仍導向 Worker（"+(req[0][:80] if req else "無")+"）")
        await ctx.close()
        # dctoken handling preserved
        ctx,p,errs=await ctxp(b,"index.html?mock=signedout#dctoken=abc")
        ok("signInWithCustomToken:abc" in await p.evaluate("__log.join()") and "dctoken" not in p.url,"從 Discord 回來的 token 仍會登入並清掉網址")
        await ctx.close()
        # #profile from other page
        ctx,p,errs=await ctxp(b,"index.html?mock=member#profile")
        ok(await p.is_visible("#pNick") and "#profile" not in p.url,"從其他頁點「我的靈魂水晶」會打開編輯")
        await ctx.close()
        ctx,p,errs=await ctxp(b,"index.html?mock=member#tools");await p.wait_for_timeout(300)
        y=await p.evaluate("[document.getElementById('tools').getBoundingClientRect().top, innerHeight+scrollY>=document.documentElement.scrollHeight-2]");ok(abs(y[0])<80 or y[1],"從其他頁點「工具」直接到工具區")
        await ctx.close()
        # other pages menu/logout & aria-current
        for url,k in [("events.html?mock=member","events"),("away.html?mock=member","away"),("schedule.html?mock=member","team"),("mit.html?mock=member&team=s1","team"),("moogle.html","tools")]:
            ctx,p,errs=await ctxp(b,url,375,812)
            cur=await p.evaluate("(document.querySelector('[aria-current=page]')||{}).dataset?.navk")
            bn=await p.evaluate("getComputedStyle(document.getElementById('bnav')).display")
            ok(cur==k and errs==[],f"{url.split('?')[0]}：目前位置={cur} 底部導覽={bn}")
            await ctx.close()
        ctx,p,errs=await ctxp(b,"events.html?mock=member");await p.click("#sbUbtn");await p.click('[data-nav="logout"]');await p.wait_for_timeout(300)
        ok("signOut" in await p.evaluate("__log.join()"),"揪團頁選單可以登出");await ctx.close()
        # old skin pref ignored
        ctx=await b.new_context();await ctx.add_init_script("localStorage.setItem('skin','classic');"+FIX);await ctx.route("**/*",route);p=await ctx.new_page()
        await p.goto("http://localhost:8765/index.html?mock=signedout");ok(await p.evaluate("document.documentElement.dataset.skin")=="cozy","舊試用設定 skin=classic 不會擋住新外觀");await ctx.close()
        await b.close()
asyncio.run(m())
