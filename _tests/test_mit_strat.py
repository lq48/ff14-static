from lib import *
import re
# 減傷軸第三步：攻略（解法、站位圖、連結）直接在時間軸上看
URL="mit.html?mock=member&team=s1&duty=d1"
row=lambda p,mech:p.locator("#gw tbody tr",has=p.locator(".cm .n",has_text=re.compile("^"+re.escape(mech)+"$"))).first
async def view(p,v):
    if await p.locator(f'[data-a="vmode"][data-v="{v}"][aria-pressed="false"]').count():await p.click(f'[data-a="vmode"][data-v="{v}"]');await p.wait_for_timeout(300)
async def m():
  async with async_playwright() as pw:
    b=await browser(pw)
    ctx,p,errs,calls=await open_page(b,URL,1440,900,init="localStorage.removeItem('mitView');");await p.wait_for_timeout(900);await view(p,"grid")
    chip=row(p,"死刑 B").locator("[data-pv]")
    ok(await chip.count()==1 and "圖 2" in await chip.inner_text() and "連結 1" in await chip.inner_text(),"表格上一個「攻略」標籤：圖 2・連結 1")
    # 桌面：停在標籤上浮出預覽
    reads0=len([x for x in await p.evaluate("window.__reads") if "mitImgs" in x])
    ok(reads0==0,"還沒看攻略前不會下載站位圖")
    await chip.hover();await p.wait_for_timeout(700)
    box=p.locator("#pvbox");ok(await box.is_visible() and "還有 1 張" in await box.inner_text(),"滑鼠停在標籤上浮出站位圖預覽")
    ok(await p.evaluate("!!document.querySelector('#pvbox img[src^=\"data:image\"]')"),"預覽圖片載入")
    await p.screenshot(path=OUT+"/S-hover-1440.png")
    await p.mouse.move(5,890);await p.wait_for_timeout(300);ok(not await box.is_visible(),"滑鼠離開就收起來")
    # 點標籤 → 抽屜直接開「攻略」
    await chip.click();await p.wait_for_timeout(500)
    ok(await p.locator('#dr [data-a="drtab"][data-k="s"][aria-selected="true"]').count()==1,"點攻略標籤：抽屜直接開「攻略」分頁")
    ok(await p.locator("#dr .drp-s .imgs img").count()==2 and "攻略影片" in await p.inner_text("#dr"),"攻略分頁：兩張站位圖（整張寬度）和連結")
    ok(await p.locator('#dr [data-p="burst"]').count()==0 and await p.locator('#dr [data-f="mech"]').count()==0,"其他分頁的欄位不在畫面上")
    await p.screenshot(path=OUT+"/S-drawer-1440.png")
    # 切分頁並記住
    await p.click('#dr [data-a="drtab"][data-k="t"]');await p.wait_for_timeout(200)
    ok(await p.locator('#dr .uses').count()==1,"「分工」分頁：減傷分工")
    await row(p,"全體 AOE A").locator(".mb .n").click();await p.wait_for_timeout(300)
    ok(await p.locator('#dr [data-a="drtab"][data-k="t"][aria-selected="true"]').count()==1,"自己選過分頁，換別的機制仍停在同一個分頁")
    await p.click('#dr [data-a="drtab"][data-k="m"]');await p.wait_for_timeout(200)
    ok(await p.locator('#dr [data-f="mech"]').count()==1,"「機制」分頁：名稱、時間、傷害")
    # 鍵盤
    await p.focus('#dr [data-a="drtab"][data-k="s"]');await p.keyboard.press("Enter");await p.wait_for_timeout(200)
    ok(await p.evaluate("document.activeElement.dataset.k")=="s","用鍵盤切分頁，焦點留在分頁按鈕上")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # 第一次打開、沒攻略內容的機制：一般成員預設「分工」
    ctx,p,errs,calls=await open_page(b,URL,1440,900,init="localStorage.removeItem('mitView');");await p.wait_for_timeout(900);await view(p,"grid")
    await row(p,"全體 AOE D").locator(".mb .n").click();await p.wait_for_timeout(300)
    ok(await p.locator('#dr [data-a="drtab"][data-k="t"][aria-selected="true"]').count()==1,"沒有攻略內容的機制，成員預設打開「分工」")
    await p.click('#dr [data-a="dclose"]')
    await row(p,"全體 AOE A").locator(".mb .n").click();await p.wait_for_timeout(300)
    note=await p.evaluate("(()=>{const t=document.querySelector('#dr .drp-s [data-p=note]');return t?t.value:document.querySelector('#dr .drp-s').textContent})()")
    ok(await p.locator('#dr [data-a="drtab"][data-k="s"][aria-selected="true"]').count()==1 and "大家集合在中間" in note,"有解法的機制預設打開「攻略」")
    await ctx.close()
    # 手機清單：直接看到站位圖和連結；捲到才下載
    for w in (360,390):
      ctx,p,errs,calls=await open_page(b,URL,w,800,init="localStorage.removeItem('mitView');");await p.wait_for_timeout(900);await view(p,"list")
      if await p.locator('[data-a="filt"][data-s="all"]').count():await p.click('[data-a="filt"][data-s="all"]');await p.wait_for_timeout(300)
      it=p.locator(".litem",has_text="死刑 B")
      ok(await it.locator(".limgs img").count()==2 and await it.locator(".llinks a").count()==1,f"[{w}] 清單直接顯示站位圖和連結")
      ok(await it.locator(".llinks a").get_attribute("href")=="https://example.com/m6s" and await it.locator(".llinks a").get_attribute("rel")=="noopener noreferrer","連結安全屬性")
      await it.scroll_into_view_if_needed();await p.wait_for_timeout(700)
      ok(await it.locator('.limgs img[src^="data:image"]').count()==2,f"[{w}] 捲到時才載入圖片")
      await it.locator(".limgs img").first.click();await p.wait_for_timeout(300)
      ok(await p.locator("#modal img").count()==1,f"[{w}] 點圖放大")
      await p.click('#modal [data-a="mclose"]')
      ok(await p.evaluate("document.documentElement.scrollWidth-innerWidth")<=0,f"[{w}] 無水平溢位")
      if w==390:await it.screenshot(path=OUT+"/S-list-390.png")
      ok(errs==[],f"[{w}] 沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # 只能檢視的成員：看得到攻略，但不能改
    ctx,p,errs,calls=await open_page(b,"mit.html?mock=plain&team=s1&duty=d1",1280,800,init="localStorage.setItem('mitView','grid');");await p.wait_for_timeout(900)
    await row(p,"死刑 B").locator("[data-pv]").click();await p.wait_for_timeout(500)
    ok(await p.locator("#dr .drp-s .imgs img").count()==2,"僅檢視的成員也看得到站位圖")
    ok(await p.locator("#dr #up").count()==0 and await p.locator('#dr [data-p="note"]').count()==0 and await p.locator('#dr [data-a="idel"]').count()==0,"僅檢視：沒有上傳、刪圖、編輯解法")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    await b.close();print(RES)
asyncio.run(m())
