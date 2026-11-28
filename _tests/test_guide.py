from lib import *
import json,os,re
# 攻略法：圖文攻略（新增、編輯區塊、連結、影片、站位圖、權限、XSS、手機）
URL="guide.html?mock={}&team=s1&duty=d1"
L=json.load(open(os.path.join(os.path.dirname(__file__),"data","fru-p1-cyclonic-strat.json")))["rows"][0]
FIRE=L["xp"][0]["url"]
W="""async(a)=>{const fs=await import('https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js');const db=fs.getFirestore();await fs.setDoc(fs.doc(db,...a.path),a.data,a.merge?{merge:true}:{});}"""
G=lambda p:p.evaluate("Object.entries(window.__mockdb||{}).length")
async def writes(p,pre):return [w for w in await p.evaluate("window.__writes") if w["path"].startswith(pre)]
async def m():
  async with async_playwright() as pw:
    b=await browser(pw)
    # ---- 團主：新增、寫、存
    ctx,p,errs,calls=await open_page(b,URL.format("owner"),1440,900);await p.wait_for_timeout(900)
    await p.evaluate(W,{"path":["statics","s1","mit","d1"],"data":{"rows":{"r4":{"xp":[{"label":"火","url":FIRE}]}}},"merge":True})
    ok("還沒有攻略" in await p.inner_text("main") and await p.locator('[data-a="newg"]').count()>=1,"還沒有文章：提示＋新增文章")
    await p.locator('.bar [data-a="newg"]').click();await p.wait_for_timeout(700)
    ok(await p.locator('[data-f="title"]').count()==1 and await p.evaluate("document.activeElement.dataset.f")=="title","新增後直接進編輯、游標在標題")
    await p.fill('[data-f="title"]',"P1 全攻略")
    await p.click('[data-a="add"][data-t="h"]');await p.keyboard.type("暴風破")
    await p.click('[data-a="add"][data-t="p"]');await p.keyboard.type("八方扇形連續 4 下，看")
    pid=await p.evaluate("document.activeElement.dataset.b")
    await p.click(f'[data-a="fbold"][data-b="{pid}"]');await p.keyboard.type("火雷");await p.keyboard.press("End");await p.keyboard.type("。詳見 ")
    await p.click(f'[data-a="flink"][data-b="{pid}"]');await p.wait_for_timeout(300)
    ok(await p.locator("#modal .pick button").count()>=4,"插入連結：列出減傷軸的機制")
    await p.locator("#modal .pick button",has_text="全體 AOE D").click();await p.wait_for_timeout(200)
    v=await p.input_value(f'textarea[data-b="{pid}"]')
    ok("**火雷**" in v and "[1:10 全體 AOE D](mit:r4)" in v,"粗體、減傷軸連結插進文字 "+v)
    await p.click('[data-a="add"][data-t="ul"]');await p.keyboard.type("第 1 下站正位\n火：分攤")
    await p.click('[data-a="add"][data-t="video"]');await p.wait_for_timeout(200)
    await p.fill("#vu","https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=205");await p.fill("#vc","日本攻略");await p.click('[data-a="vadd"]');await p.wait_for_timeout(200)
    await p.click('[data-a="add"][data-t="video"]');await p.fill("#vu","https://www.bilibili.com/video/BV1xx411c7mD?p=2");await p.fill("#vt","1:05");await p.click('[data-a="vadd"]');await p.wait_for_timeout(200)
    await p.click('[data-a="add"][data-t="video"]');await p.fill("#vu","https://evil.example/watch?v=dQw4w9WgXcQ");await p.click('[data-a="vadd"]');await p.wait_for_timeout(200)
    ok(await p.locator("#modal").count()==1 and await p.locator(".eb",has_text="影片").count()==2,"不是 YouTube／Bilibili 的網址不收");await p.click('#modal [data-a="mclose"]')
    await p.click('[data-a="add"][data-t="xpnew"]');await p.wait_for_timeout(300)
    ok(await p.locator('#modal [data-a="xpref"]').count()==1,"站位圖：從減傷軸挑（列出有站位圖的機制）")
    await p.click('#modal [data-a="xpref"]');await p.wait_for_timeout(300)
    await p.click('[data-a="add"][data-t="xpnew"]');await p.wait_for_timeout(200);await p.click('#modal [data-a="xptab"][data-t="new"]');await p.wait_for_timeout(200)
    await p.click('#modal [data-a="xpblank"]');await p.wait_for_timeout(900)
    ok(await p.locator("#modal .xpv-edit").count()==1,"新增空白站位圖：直接打開調整站位")
    await p.locator('#modal .tok[data-k="MT"]').focus();await p.keyboard.press("ArrowUp");await p.wait_for_timeout(200)
    await p.click('#modal [data-xe="save"]');await p.wait_for_timeout(800)
    ok(await p.locator("#modal").count()==0 and await p.locator(".eb .xpm .xpv-stage svg").count()==1,"調整完回到文章編輯")
    await p.screenshot(path=OUT+"/GD-edit-1440.png",full_page=True)
    n0=len(await writes(p,"statics/s1/guides/"))
    await p.click('[data-a="save"]');await p.wait_for_timeout(900)
    ws=await writes(p,"statics/s1/guides/");d=ws[-1]["data"] if ws else {}
    ok(len(ws)>n0 and d.get("title")=="P1 全攻略" and d.get("did")=="d1" and d.get("by")=="u2","存到 statics/s1/guides，作者是自己")
    ok([x["t"] for x in d.get("blocks",[])]==["h","p","ul","video","video","xpref","xp"],"區塊順序 "+str([x["t"] for x in d.get("blocks",[])]))
    vb=[x for x in d["blocks"] if x["t"]=="video"]
    ok(vb[0]["src"]=="yt" and vb[0]["s"]==205 and vb[1]["src"]=="bili" and vb[1]["s"]==65 and vb[1]["p"]==2,"影片：YouTube 從 3:25、Bilibili 第 2P 從 1:05")
    ok(set(d.keys())<={"did","stage","title","order","blocks","by","createdAt","updatedAt","updatedBy"},"只寫規則允許的欄位")
    # 閱讀
    ok(await p.locator("article h2").inner_text()=="P1 全攻略" and await p.locator("h3.bh").count()==1,"閱讀：標題、小標題")
    ok(await p.locator(".toc a.sub",has_text="暴風破").count()==1,"目錄列出小標題")
    ok(await p.locator(".bp b",has_text="火雷").count()==1,"粗體")
    lk=p.locator(".bp a.gl");ok(await lk.count()==1 and "mit.html?team=s1&duty=d1&row=r4" in await lk.get_attribute("href"),"減傷軸連結")
    fr=p.locator(".vid [data-src]");srcs=[await fr.nth(i).get_attribute("data-src") for i in range(await fr.count())]
    ok(await p.locator(".vid iframe").count()==0,"影片先放封面，不會一次載入所有播放器")
    ok(len(srcs)==2 and srcs[0].startswith("https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ") and "start=205" in srcs[0] and srcs[1].startswith("https://player.bilibili.com/player.html?bvid=BV1xx411c7mD&page=2&t=65"),"影片直接嵌入、從指定秒數 "+str(srcs))
    ok(await p.locator("figcaption",has_text="從 3:25 開始").count()==1,"影片說明寫從幾分幾秒")
    ok(await p.locator(".bxp .xpv-stage svg").count()==2,"兩張站位圖（減傷軸的、文章自己的）都能播放")
    ok(await p.locator(".bxp .ref a",has_text="減傷軸 1:10 全體 AOE D").count()==1,"從減傷軸挑的站位圖標明出處")
    await p.screenshot(path=OUT+"/GD-view-1440.png",full_page=True)
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]))
    await p.locator(".vplay").first.click();await p.wait_for_timeout(300)
    s=await p.locator(".vid iframe").first.get_attribute("src")
    ok(s.startswith("https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ") and "start=205" in s and "autoplay=1" in s,"按播放：在文章裡直接播，從 3:25 開始")
    await ctx.close()
    # ---- XSS：有人繞過網站直接寫奇怪的資料
    ctx,p,errs,calls=await open_page(b,URL.format("owner"),1440,900);await p.wait_for_timeout(700)
    bad=[{"id":"h1","t":"h","text":"<img src=x onerror=window.__x=1>"},{"id":"p1","t":"p","text":"<script>window.__x=1</script>[點我](javascript:window.__x=1) [x](data:text/html,hi) **<b onclick=1>粗</b>**"},
         {"id":"v1","t":"video","src":"yt","vid":"abc\"onload=\"x"},{"id":"v2","t":"video","src":"evil","vid":"dQw4w9WgXcQ"},{"id":"i1","t":"img","img":"../../x"},{"id":"x1","t":"xp","url":"javascript:alert(1)"},
         {"id":"u1","t":"ul","items":["<svg onload=window.__x=1>"]},{"id":"z","t":"html","html":"<img src=x onerror=window.__x=1>"}]
    await p.evaluate(W,{"path":["statics","s1","guides","gx"],"data":{"did":"d1","stage":"","title":"<img src=x onerror=window.__x=1>","order":1,"blocks":bad,"by":"u3","createdAt":1,"updatedAt":1}})
    await p.wait_for_timeout(900)
    ok(await p.evaluate("window.__x")is None and await p.locator("main img[src=x],main script,main svg[onload]").count()==0,"文字一律當純文字，不會執行")
    ok(await p.locator('main a[href^="javascript"],main a[href^="data:"]').count()==0,"不接受 javascript:／data: 連結")
    ok(await p.locator(".vid").count()==0 and await p.locator("[data-gimg]").count()==0 and await p.locator(".bxp").count()==0,"假的影片、圖片、站位圖都不顯示")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # ---- 權限
    ctx,p,errs,calls=await open_page(b,URL.format("plain"),1440,900);await p.wait_for_timeout(800)
    ok("沒有這個固團「攻略法整理」的檢視權限" in await p.inner_text("#app"),"功能還沒開放：一般成員看不到")
    await p.evaluate(W,{"path":["statics","s1"],"data":{"modules":{"guide":"all"}},"merge":True})
    await p.evaluate(W,{"path":["statics","s1","guides","gy"],"data":{"did":"d1","stage":"","title":"團主的文章","order":2,"blocks":[{"id":"a","t":"p","text":"hi"}],"by":"u2","createdAt":1,"updatedAt":1}})
    await p.wait_for_timeout(900)
    ok(await p.locator(".toc a",has_text="團主的文章").count()==1,"全團開放後看得到文章")
    ok(await p.locator('[data-a="newg"]').count()==0 and await p.locator('[data-a="edit"]').count()==0,"可檢視：沒有新增、編輯")
    await p.evaluate(W,{"path":["statics","s1","members","u5"],"data":{"perms":{"guide":"own"}},"merge":True});await p.wait_for_timeout(700)
    ok(await p.locator('.bar [data-a="newg"]').count()==1 and await p.locator('[data-a="edit"]').count()==0,"編輯自己的：可以新增，但不能改別人的文章")
    await p.locator('.bar [data-a="newg"]').click();await p.wait_for_timeout(700)
    ok(await p.locator('[data-a="delg"]').count()==0,"編輯自己的：沒有刪除")
    await p.click('[data-a="save"]');await p.wait_for_timeout(700)
    ws=await writes(p,"statics/s1/guides/");ok(ws and ws[-1]["data"]["by"]=="u5","自己寫的文章作者是自己")
    ok(await p.locator('[data-a="edit"]').count()==1,"自己寫的可以編輯")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # ---- 手機
    for w in (360,390):
      ctx,p,errs,calls=await open_page(b,URL.format("owner"),w,800);await p.wait_for_timeout(700)
      await p.evaluate(W,{"path":["statics","s1","guides","gz"],"data":{"did":"d1","stage":"","title":"手機測試","order":1,"blocks":[{"id":"h","t":"h","text":"暴風破"},{"id":"p","t":"p","text":"很長很長的一段文字"*10},{"id":"v","t":"video","src":"yt","vid":"dQw4w9WgXcQ","s":30},{"id":"x","t":"xp","url":FIRE}],"by":"u2","createdAt":1,"updatedAt":1}})
      await p.wait_for_timeout(1200)
      ok(await p.locator(".tocm").is_visible() and not await p.locator("nav.toc").is_visible(),f"[{w}] 手機：目錄收成一顆按鈕")
      ok(await p.evaluate("document.documentElement.scrollWidth-innerWidth")<=0,f"[{w}] 無水平溢位")
      await p.screenshot(path=OUT+f"/GD-view-{w}.png",full_page=True)
      ok(errs==[],f"[{w}] 沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # ---- 規則檔
    R=open(os.path.join(os.path.dirname(__file__),"..","firestore.rules"),encoding="utf-8").read()
    ok("match /guides/{gid}" in R and "guideCanEditOwn(tid) && resource.data.by == request.auth.uid" in R and "request.resource.data.by == resource.data.by" in R,"規則：編輯自己的只能改自己寫的、作者不能改")
    ok("match /guideImgs/{id}" in R and "allow delete: if guideCanEditAll(tid);" in R,"規則：圖片、刪除文章只給編輯全部")
    await b.close();print(RES)
asyncio.run(m())
