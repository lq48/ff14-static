from lib import *
import re,json
# 技能庫：匯入完整技能庫（合併）、可存次數、無敵、坦克自帶減傷、圖示載入失敗退回文字
URL="mit.html?mock=owner&team=s1&duty=d1"
row=lambda p,mech:p.locator("#gw tbody tr",has=p.locator(".cm .n",has_text=re.compile("^"+re.escape(mech)+"$"))).first
W="""async(a)=>{const fs=await import('https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js');const db=fs.getFirestore();await fs.setDoc(fs.doc(db,...a.path),a.data);}"""
async def merge(p,cats=None):
    await p.click('[data-a="skills"]');await p.wait_for_timeout(300)
    await p.click('[data-a="libmerge"]');await p.wait_for_selector(".lmsum")
    for k in (cats or []):await p.click(f'[data-a="lmcat"][data-k="{k}"]');await p.wait_for_timeout(100)
async def m():
  async with async_playwright() as pw:
    b=await browser(pw)
    ctx,p,errs,calls=await open_page(b,URL,1440,900,init="localStorage.setItem('mitView','grid');");await p.wait_for_timeout(900)
    before=await p.evaluate("JSON.parse(JSON.stringify(window.__MOCK.db['mitSkills/lib']))")
    await merge(p)
    t=await p.inner_text(".lmsum");print("  ",t)
    ok("新增" in t and "更新" in t,"預覽新增／更新數量")
    upd=await p.evaluate("[...document.querySelectorAll('.lm.upd')].map(x=>x.textContent)")
    ok(set(upd)>={"聖盾陣","神聖領域","野戰治療陣","節制"},"同名技能標成「更新」："+",".join(upd))
    ok(await p.locator('.lm.add',has_text="禮儀之鈴").count()==0,"預設不含治療技能")
    await p.click('[data-a="lmcat"][data-k="h"]');await p.wait_for_timeout(150)
    ok(await p.locator('.lm',has_text="禮儀之鈴").count()==1,"勾「能力技治療」就會列出")
    await p.click('[data-a="lmcat"][data-k="h"]');await p.wait_for_timeout(150)
    await p.screenshot(path=OUT+"/L-merge-1440.png")
    btn=p.locator('[data-a="lmapply"]');await btn.click();await btn.click();await p.wait_for_timeout(1300)
    lib=await p.evaluate("window.__MOCK.db['mitSkills/lib']")
    pld=lib["jobs"]["PLD"]["skills"];names=[s["name"] for s in pld]
    ok("雪仇" in names and "極致防禦" in names,"騎士加上雪仇、極致防禦等技能")
    rep=[s for s in pld if s["name"]=="雪仇"][0]
    ok([t["lv"] for t in rep["tiers"]]==[1] and "from" not in rep["tiers"][0],"新技能從 1 級開始（表上的 Lv98 是效果生效等級，不是學會等級）")
    sh=[s for s in pld if s["name"]=="聖盾陣"][0]
    ok(sh["id"]=="p1" and any(t["lv"]==82 and t["cd"]==5 and t["dur"]==8 for t in sh["tiers"]),"同名的聖盾陣保留原本的代碼 p1，新數值放在生效等級 82（原本 1 級的數值保留給低等級副本）")
    ok(len([s for s in pld if s["name"]=="聖盾陣"])==1,"不會重複出現同名技能")
    whm=lib["jobs"]["WHM"]["skills"];ben=[s for s in whm if s["name"]=="神祝禱"][0]
    ok(ben["tiers"][-1].get("ch")==2 and ben.get("tgt")=="ally","神祝禱：可存 2 次、對隊友")
    ok(ben.get("img","").startswith("https://v2.xivapi.com/"),"附官方圖示網址")
    ok("SAM" in lib["jobs"] and lib["jobs"]["SAM"]["skills"][0]["name"]=="牽制","武士原本沒技能，加上牽制")
    # 原本排好的分工還在（MT 在死刑 B 用聖盾陣、神聖領域）
    t=await row(p,"死刑 B").inner_text();ok("-100%" in t,"已排的分工不受影響（神聖領域仍算進去）")
    # 圖示載入失敗（測試環境連不到外部）→ 文字方塊，不留破圖
    await p.wait_for_timeout(800)
    broken=await p.evaluate("[...document.querySelectorAll('#gw img.ico')].filter(i=>i.complete&&i.naturalWidth===0).length")
    ok(broken==0 and await p.locator('#gw .sh .tx',has_text="牽制").count()>=1,"官方圖示載不到時換成文字方塊")
    # 復原
    await p.click("#utoast .ut-undo");await p.wait_for_timeout(1300)
    lib2=await p.evaluate("window.__MOCK.db['mitSkills/lib']")
    ok(json.dumps(lib2["jobs"],sort_keys=True)==json.dumps(before["jobs"],sort_keys=True),"按復原：技能庫回到原本")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # 可存次數：神祝禱 ×2（CD 30）在 0:12、0:30 連用不算衝突；只能存 1 次時會標衝突
    ctx,p,errs,calls=await open_page(b,URL,1440,900,init="localStorage.setItem('mitView','grid');");await p.wait_for_timeout(900)
    base=await p.locator("#gw .cell.bad").count()  # 假資料本來就有一個衝突（野戰 0:12、1:10，CD 120）
    for ch in (2,1):
      L=json.loads(json.dumps(before));L["jobs"]["WHM"]["skills"].append({"id":"hb","name":"神祝禱","tgt":"ally","tiers":[dict(lv=1,cd=30,dur=15,fx=[dict(k="shield",v="13162",w="target")],**({"ch":ch} if ch>1 else {}))]})
      await p.evaluate(W,{"path":["mitSkills","lib"],"data":L})
      await p.evaluate(W,{"path":["statics","s1","mit","d1","slots","H2"],"data":{"a":{"r1":["h1","hb"],"r2":["hb"]},"o":{},"tg":{"r1":{"hb":"MT"},"r2":{"hb":"MT"}}}})
      await p.wait_for_timeout(600)
      bad=await p.locator("#gw .cell.bad").count()-base
      ok((bad==0) if ch==2 else (bad==1),f"可存 {ch} 次：{'不算' if ch==2 else '要標'} CD 衝突（bad={bad}）")
      if ch==2:
        t=await row(p,"死刑 B").inner_text();ok("盾 13,162" in t,"神祝禱的盾算進坦克")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # 無敵＋坦克自帶減傷設定
    ctx,p,errs,calls=await open_page(b,URL,1440,900,init="localStorage.setItem('mitView','grid');");await p.wait_for_timeout(900)
    L=json.loads(json.dumps(before));L["jobs"]["WAR"]["skills"].append({"id":"wh","name":"死鬥","tiers":[{"lv":1,"cd":240,"dur":10,"fx":[{"k":"other","v":"無敵","w":"self"}]}]})
    await p.evaluate(W,{"path":["mitSkills","lib"],"data":L})
    await p.evaluate(W,{"path":["statics","s1","mit","d1","slots","MT"],"data":{"a":{},"o":{}}})
    await p.wait_for_timeout(500)
    t=await row(p,"死刑 B").inner_text();ok("160,000" in t and "-20%" in t,"坦克自帶 20%：200,000→160,000")
    await p.evaluate(W,{"path":["statics","s1","mit","d1","slots","ST"],"data":{"a":{"r2":["wh"]},"o":{}}})
    await p.wait_for_timeout(500)
    t=await row(p,"死刑 B").inner_text();ok("無敵" in t,"排了死鬥：減傷後欄標示無敵")
    await p.click('[data-a="dutyset"]');await p.wait_for_timeout(300)
    await p.fill('[data-hp="tankMit"]',"0");await p.click('[data-a="dutysave"]');await p.wait_for_timeout(700)
    d=await p.evaluate("window.__MOCK.db['mitDuties/d1']");ok(d.get("tankMit")==0,"副本設定可以把坦克自帶減傷設成 0")
    t=await p.inner_text("#gw .foot");ok("坦克自帶減傷 0%" in t,"下方說明顯示坦克自帶減傷")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # 手機預覽
    ctx,p,errs,calls=await open_page(b,URL,390,850);await p.wait_for_timeout(900)
    await merge(p);ok(await p.evaluate("document.documentElement.scrollWidth-innerWidth")<=0,"[390] 預覽無水平溢位")
    await p.screenshot(path=OUT+"/L-merge-390.png");ok(errs==[],"[390] 沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    await b.close();print(RES)
asyncio.run(m())
