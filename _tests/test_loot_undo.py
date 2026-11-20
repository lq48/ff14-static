from lib import *
async def m():
  async with async_playwright() as pw:
    b=await browser(pw)
    ctx,p,errs,calls=await open_page(b,"index.html?mock=owner&team=s1&mod=bis");await p.wait_for_timeout(700)
    await p.click('[data-bistab="loot"]');await p.wait_for_timeout(300)
    await p.select_option('[data-loot="floor"]',"1");await p.wait_for_timeout(200)
    await p.select_option('[data-loot="item"]',"head");await p.wait_for_timeout(200)
    await p.select_option('[data-loot="to"]',"u1");await p.wait_for_timeout(200)
    await p.click('[data-act="lootAdd"]');await p.wait_for_timeout(600)
    db=await p.evaluate("window.__MOCK.db")
    loot=[k for k in db if k.startswith("statics/s1/loot/")]
    ok(len(loot)==1 and db["statics/s1/bis/t1__u1"]["final"]["head"]["st"]=="got","記錄分裝：新增紀錄並自動勾選飛雷虛的頭")
    ok("已勾選畢業的頭" in await p.inner_text("#utoast"),"出現可復原提示")
    await p.click("#utoast .ut-undo");await p.wait_for_timeout(600)
    db=await p.evaluate("window.__MOCK.db")
    ok(not [k for k in db if k.startswith("statics/s1/loot/")] and db["statics/s1/bis/t1__u1"]["final"]["head"]["st"]=="none","復原：刪掉這筆紀錄，頭改回未取得")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close();await b.close();print(RES)
asyncio.run(m())
