from lib import *
import re,os
# 坦克 LB3：全員減傷 80%、8 秒，算進血量檢查；補師、輸出的 LB 不算
SEED=open(os.path.join(os.path.dirname(__file__),"data","fru-mit-seed.json"),encoding="utf-8").read()
row=lambda p,mech,n=0:p.locator("#gw tbody tr",has=p.locator(".cm .n",has_text=re.compile("^"+re.escape(mech)+"$"))).nth(n)
num=lambda s:int(re.sub(r"[^\d]","",s.strip().split("\n")[0]) or 0)
async def m():
  async with async_playwright() as pw:
    b=await browser(pw)
    ctx,p,errs,calls=await open_page(b,"mit.html?mock=owner&team=s1",1440,900);await p.wait_for_timeout(700)
    await p.click('[data-a="io"]');await p.fill("#ta",SEED)
    imp=p.locator('[data-a="import"]');await imp.click();await imp.click();await p.wait_for_timeout(900)
    if await p.locator('[data-a="vmode"][data-v="grid"][aria-pressed="false"]').count():await p.click('[data-a="vmode"][data-v="grid"]');await p.wait_for_timeout(300)
    if not await p.locator("#gw td.h5").count():
      await p.click('[data-a="tools"]');await p.click('.tmenu [data-a="hpchk"]');await p.wait_for_timeout(400)
    R=lambda:row(p,"暴風破")
    a0=num(await R().locator("td.h5").inner_text())
    lc=R().locator('[data-a="lcell"]')
    await lc.click();await p.wait_for_timeout(500)
    lbw=await R().locator('[data-a="lcell"]').get_attribute("title")
    a1=num(await R().locator("td.h5").inner_text())
    ok("MT" in lbw and a0==92000 and a1==18400,f"MT 放 LB：這一下再減 80%（{a0} → {a1}）")
    t=await row(p,"罪炎 或 罪雷").locator("td.h5").inner_text()
    ok(num(t)==23000,"8 秒內的下一個傷害（0:17 罪炎）也有吃到 "+t.split(chr(10))[0])
    for _ in range(2):await R().locator('[data-a="lcell"]').click();await p.wait_for_timeout(400)
    a2=num(await R().locator("td.h5").inner_text())
    ok("H1" in (await R().locator('[data-a="lcell"]').get_attribute("title")) and a2==a0,f"補師放 LB 不算減傷（{a2}）")
    await R().locator(".cm .n").click();await p.wait_for_timeout(500)
    await p.locator("#dr .drtabs button",has_text="分工").click();await p.wait_for_timeout(300)
    ok("80%" in await p.inner_text("#dr"),"抽屜的 LB 欄位有寫坦克 LB3 的效果")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close();await b.close();print(RES)
asyncio.run(m())
