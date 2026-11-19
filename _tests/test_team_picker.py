import asyncio
from lib import *
# 三個固定團：s1（BiS＋減傷都開放）、s2（只開減傷）、s3（都沒開，但是成員）
FIX3=FIX.replace('["u2","u9"].forEach(k=>db["statics/s2/members/"+k]={status:"active"});','''["u2","u9","u1"].forEach(k=>db["statics/s2/members/"+k]={status:"active",perms:{bis:"own",mit:"view"}});
 db["statics/s2"].modules={mit:"all"};db["statics/s2"].roles={H1:"u1"};
 db["statics/s3"]={name:"休閒挖寶團",createdAt:3,leaders:{},modules:{},targets:[]};db["statics/s3/members/u1"]={status:"active"};''')
assert FIX3!=FIX
def ok(c,m):print(("PASS " if c else "FAIL ")+m)
async def m():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(**LAUNCH)
        for w,h in [(1280,900),(375,812)]:
            ctx=await b.new_context(viewport={"width":w,"height":h},is_mobile=w<500,has_touch=w<500);await ctx.add_init_script(FIX3);await ctx.route("**/*",route)
            p=await ctx.new_page();errs=[];p.on("pageerror",lambda e:errs.append(str(e)))
            await p.goto("http://localhost:8765/index.html?mock=member");await p.wait_for_timeout(1000)
            d=await p.evaluate("Object.fromEntries([...document.querySelectorAll('.qt')].slice(3).map(a=>[a.querySelector('.qn').textContent,a.querySelector('.qd').textContent]))");print(" ",d)
            if w==1280:
                ok(d["我的固定團"].startswith("3 個") and d["裝備進度"]=="週三零式團" and d["攻略與減傷"].startswith("2 個"),"依權限計算：固定團 3、BiS 1（直接開）、減傷 2（要選）")
                await p.click('[data-pick="mit"]');await p.wait_for_timeout(150)
                names=await p.evaluate("[...document.querySelectorAll('#qpick .qp-n')].map(x=>x.textContent)");print("  選單：",names)
                ok(len(names)==2 and await p.evaluate("document.activeElement.classList.contains('qp')"),"出現 2 團可選，焦點移到第一項")
                ok(await p.evaluate("document.querySelector('[data-pick=mit]').getAttribute('aria-expanded')")=="true","按鈕標示已展開")
                await p.keyboard.press("Escape");await p.wait_for_timeout(100)
                ok(not await p.is_visible("#qpick") and await p.evaluate("document.activeElement.dataset.pick")=="mit","Esc 關閉並回到按鈕")
                await p.click('[data-pick="team"]');await p.wait_for_timeout(150)
                await p.click('#qpick .qp:has-text("休閒挖寶團")');await p.wait_for_timeout(300)
                ok("team=s3" in p.url and await p.evaluate("localStorage.lastTeam")=="s3","選了「休閒挖寶團」就打開那一團並記住")
                await p.click('.sb-nav [data-navk="lobby"]');await p.wait_for_timeout(300)
                await p.click('[data-pick="team"]');await p.wait_for_timeout(150)
                first=await p.evaluate("document.querySelector('#qpick .qp-n').textContent");ok(first.startswith("休閒挖寶團") and "上次" in first,"再打開時上次用的排第一並標示「上次」："+first)
                await p.click('[data-pick="mit"]');await p.wait_for_timeout(150)
                await p.click('#qpick .qp:has-text("絕伊甸挑戰團")');await p.wait_for_timeout(500)
                ok("mit.html?team=s2" in p.url,"減傷軸選「絕伊甸挑戰團」開對的團："+p.url.split("/")[-1])
                await p.go_back();await p.wait_for_timeout(1000)
                ok(await p.evaluate("localStorage.lastTeam")=="s2","從大廳選減傷軸也會記住")
            else:
                await p.click('[data-pick="team"]');await p.wait_for_timeout(200)
                await p.screenshot(path=OUT+"/picker-375.png")
                ov=await p.evaluate("document.documentElement.scrollWidth-innerWidth");ok(ov<=0,"手機版沒有水平溢位")
            ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]))
            await ctx.close()
        await b.close()
asyncio.run(m())
