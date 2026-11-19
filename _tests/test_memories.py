from lib import *
from rules_check import check
def _photos():
    from PIL import Image
    out=[]
    for i,c in enumerate([(200,120,80),(80,130,200)]):
        f=os.path.join(OUT,f"photo{i+1}.jpg")
        if not os.path.exists(f):
            im=Image.effect_noise((2400,1600),60).convert("RGB");Image.blend(Image.new("RGB",(2400,1600),c),im,0.35).save(f,quality=92)
        out.append(f)
    return out
PH=_photos()
def audit(ws,label):
    bad=[(w['op'],w['path'],r) for w in ws for a,r in [check(w)] if not a and (w['path'].startswith('memor'))]
    ok(not bad,label+("：全部符合規則" if not bad else "：違反 "+str(bad)))
async def m():
  async with async_playwright() as pw:
    b=await browser(pw)
    # ---- 列表 ----
    ctx,p,errs,calls=await open_page(b,"memories.html?mock=member");await p.wait_for_timeout(700)
    t=" ".join((await p.inner_text("#app")).split());print("  列表：",t[:260])
    order=await p.evaluate("[...document.querySelectorAll('.mcard .mtitle')].map(x=>x.textContent)")
    ok(order==["週末挖寶團","M6S 開荒第一晚","萬聖節大合照","M5S 首通！"],"依日期新到舊排列："+str(order))
    ok("2026" in t and "11 月" in t and "10 月" in t,"依年份、月份分組")
    await p.click('[data-kind="first"]');await p.wait_for_timeout(200)
    t=" ".join((await p.inner_text("#app")).split());ok("首通里程碑" in t and "零式 M5S" in t and "週末挖寶團" not in t,"首通篩選＋里程碑")
    ok(await p.is_visible('.sb-nav [data-navk="memories"][aria-current="page"]'),"桌面導覽「回憶」標示目前位置")
    # ---- 詳情（自己記錄的） ----
    await p.click('.miles a');await p.wait_for_timeout(700)
    t=" ".join((await p.inner_text("#app")).split())
    ok("紀念留言" in t and "謝謝大家一直沒放棄" in t and "一起的人（4）" in t and "週三零式團" in t,"詳情：紀念留言、成員、相關固定團")
    ok(await p.evaluate("!!document.querySelector('#gal .main img')") and await p.evaluate("document.querySelectorAll('#gal .rest button').length")==2,"照片載入：主圖＋2 張縮圖")
    ok(await p.is_visible('[data-a="del"]') and not await p.is_visible('[data-a="untag"]'),"作者看得到編輯、刪除")
    # ---- 別人記錄、有標記到我 ----
    await p.goto("http://localhost:8765/memories.html?mock=member&m=m2");await p.wait_for_timeout(700)
    ok(not await p.is_visible('[data-a="del"]') and await p.is_visible('[data-a="untag"]'),"別人的回憶：沒有編輯刪除，只有「把我從名單移除」")
    await p.click('[data-a="untag"]');await p.wait_for_timeout(400)
    ws=await p.evaluate("__writes");audit(ws,"移除自己")
    ok(await p.evaluate("window.__MOCK.db['memories/m2'].members.join()")=="u5,u6","名單已移除自己")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # ---- 新增（含真實照片壓縮） ----
    ctx,p,errs,calls=await open_page(b,"memories.html?mock=member&new=1");await p.wait_for_timeout(700)
    await p.click('[data-fk="first"]');await p.fill('[data-ff="title"]',"M6S 首通紀念");await p.fill('[data-ff="duty"]',"零式 M6S");await p.fill('[data-ff="note"]',"終於！")
    await p.fill('[data-ff="desc"]',"大家辛苦了")
    await p.set_input_files("#pfile",PH);await p.wait_for_timeout(2500)
    ok(await p.evaluate("document.querySelectorAll('#phs .pitem').length")==2,"兩張照片已壓縮並預覽")
    await p.click('[data-mu="u3"]');await p.select_option('[data-ff="tid"]',"s1");await p.wait_for_timeout(200)
    await p.click('[data-a="teamMembers"]');await p.wait_for_timeout(400)
    n=await p.evaluate("document.querySelectorAll('[data-mu][aria-pressed=true]').length");ok(n==8,"帶入固定團成員（8 人）")
    await p.click('[data-a="save"]');await p.wait_for_timeout(2500)
    ws=await p.evaluate("__writes");audit(ws,"新增回憶")
    imgs=[w for w in ws if w['path'].startswith('memoryImgs/') and w['op']=='setDoc'];mem=[w for w in ws if w['path'].startswith('memories/') and w['op']=='setDoc']
    print("  照片大小：",[len(w['data']['data']) for w in imgs],"縮圖：",len(mem[0]['data']['thumb']) if mem else None, "格式：",imgs[0]['data']['data'][:22] if imgs else None)
    ok(len(imgs)==2 and all(len(w['data']['data'])<=700000 for w in imgs),"2400px 照片壓縮後都在 70 萬字元以內")
    ok(len(mem)==1 and mem[0]['data']['imgs']==[w['path'].split('/')[1] for w in imgs] and mem[0]['data']['kind']=="first" and mem[0]['data']['duty']=="零式 M6S","回憶文件記錄照片順序、類型、副本")
    ok("m=" in p.url and "M6S 首通紀念" in await p.inner_text("#app"),"儲存後打開新回憶")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # ---- 編輯：移除第二張、換標題 ----
    ctx,p,errs,calls=await open_page(b,"memories.html?mock=member&edit=m1");await p.wait_for_timeout(1000)
    ok(await p.evaluate("document.querySelectorAll('#phs .pitem img').length")==2,"編輯時載入原本的 2 張照片")
    await p.fill('[data-ff="title"]',"M5S 首通！（補記）");await p.click('[data-pr="1"]');await p.click('[data-a="save"]');await p.wait_for_timeout(1200)
    ws=await p.evaluate("__writes");audit(ws,"編輯回憶")
    ok(any(w['op']=='deleteDoc' and w['path']=='memoryImgs/i2' for w in ws) and await p.evaluate("window.__MOCK.db['memories/m1'].imgs.join()")=="i1","移除的照片一併刪除")
    # ---- 刪除自己的回憶 → 復原 ----
    await p.click('[data-a="del"]');await p.click('[data-a="del"]');await p.wait_for_timeout(800)
    ok(await p.evaluate("!window.__MOCK.db['memories/m1'] && !window.__MOCK.db['memoryImgs/i1']"),"刪除回憶與照片")
    await p.click("#utoast .ut-undo");await p.wait_for_timeout(800)
    ok(await p.evaluate("!!window.__MOCK.db['memories/m1'] && !!window.__MOCK.db['memoryImgs/i1']"),"按「復原」後回憶和照片都回來")
    ws=await p.evaluate("__writes");audit(ws,"刪除與復原")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # ---- 總團長刪別人的：可以刪，但不提供復原 ----
    ctx,p,errs,calls=await open_page(b,"memories.html?mock=owner&m=m3");await p.wait_for_timeout(700)
    await p.click('[data-a="del"]');ok("無法復原" in await p.inner_text('[data-a="del"]'),"總團長刪別人的回憶會特別提醒");await p.click('[data-a="del"]');await p.wait_for_timeout(600)
    ok(not await p.is_visible("#utoast .ut-undo"),"刪別人的回憶不提供復原（規則不允許代建）")
    ws=await p.evaluate("__writes");audit(ws,"總團長刪除");await ctx.close()
    # ---- 未儲存保護、儲存失敗 ----
    ctx,p,errs,calls=await open_page(b,"memories.html?mock=member&new=1");await p.wait_for_timeout(600)
    await p.fill('[data-ff="title"]',"打到一半");await p.click('.foot a.btn');await p.wait_for_timeout(200)
    ok("form" and await p.is_visible('[data-ff="title"]') and "再按一次" in await p.inner_text("#toast"),"表單沒存就取消：先提醒")
    await p.evaluate("window.__MOCK.failWrites='permission-denied'")
    await p.set_input_files("#pfile",PH[:1]);await p.wait_for_timeout(1500);await p.click('[data-a="save"]');await p.wait_for_timeout(800)
    st=await p.inner_text("#fstat");ok("儲存失敗" in st and "填好的內容都還在" in st and await p.input_value('[data-ff="title"]')=="打到一半","儲存失敗：說明原因、保留內容："+st)
    await ctx.close()
    # ---- 權限情境 ----
    ctx,p,errs,calls=await open_page(b,"memories.html?mock=signedout");ok("請先登入" in await p.inner_text("#app"),"未登入：看不到回憶錄");await ctx.close()
    ctx,p,errs,calls=await open_page(b,"memories.html?mock=google");ok("Discord 登入的飛地成員" in await p.inner_text("#app"),"非 Discord 帳號：看不到");await ctx.close()
    ctx,p,errs,calls=await open_page(b,"memories.html?mock=owner",init="localStorage.setItem('mockDenyMem','1');");await p.wait_for_timeout(600)
    ok("回憶錄還在準備中" in await p.inner_text("#app") and "發布新版 firestore.rules" in await p.inner_text("#app"),"規則還沒發布：總團長看到發布說明");await ctx.close()
    ctx,p,errs,calls=await open_page(b,"index.html?mock=member",init="localStorage.setItem('mockDenyMem','1');");await p.wait_for_timeout(700)
    ok("回憶錄還在準備中" in await p.inner_text("#memories") and errs==[],"規則還沒發布：大廳安靜顯示準備中，其他功能正常");await ctx.close()
    # ---- 大廳 ----
    ctx,p,errs,calls=await open_page(b,"index.html?mock=member");await p.wait_for_timeout(700)
    t=await p.evaluate("[...document.querySelectorAll('#memories .mm-t')].map(x=>x.textContent)");ok(t==["週末挖寶團","M6S 開荒第一晚","萬聖節大合照"],"大廳只顯示最新 3 筆："+str(t))
    await ctx.close()
    ctx,p,errs,calls=await open_page(b,"index.html?mock=member",375,812);await p.wait_for_timeout(600)
    bn=await p.evaluate("[...document.querySelectorAll('#bnav a')].map(a=>a.dataset.navk)");ok(len(bn)==5 and "memories" not in bn,"手機底部導覽維持 5 格")
    await ctx.close()
    # ---- 手機、深色 ----
    for url,name in [("memories.html?mock=member","p3-list"),("memories.html?mock=member&m=m1","p3-detail"),("memories.html?mock=member&new=1","p3-form")]:
      for dark in (False,True):
        ctx,p,errs,calls=await open_page(b,url,375,812,dark);await p.wait_for_timeout(900)
        ov=await p.evaluate("document.documentElement.scrollWidth-innerWidth");ok(ov<=0 and errs==[],f"{name} {'深色' if dark else '淺色'} 手機無溢位、無錯誤")
        await p.screenshot(path=OUT+f"/{name}-{'d' if dark else 'l'}.png",full_page=True);await ctx.close()
    ctx,p,errs,calls=await open_page(b,"memories.html?mock=member",1280,900);await p.wait_for_timeout(800);await p.screenshot(path=OUT+"/p3-list-1280.png",full_page=True);await ctx.close()
    await b.close();print(RES)
asyncio.run(m())
