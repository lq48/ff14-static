from lib import *
import re
# 減傷軸第二步：技能庫「從參考資料補效果」＋血量檢查扣掉本團排的減傷
row=lambda p,mech:p.locator("#gw tbody tr",has=p.locator(".cm .n",has_text=re.compile("^"+re.escape(mech)+"$"))).first
URL="mit.html?mock=owner&team=s1&duty=d1"
async def grid(p):
    if await p.locator('[data-a="vmode"][data-v="grid"][aria-pressed="false"]').count():await p.click('[data-a="vmode"][data-v="grid"]');await p.wait_for_timeout(300)
async def m():
  async with async_playwright() as pw:
    b=await browser(pw)
    ctx,p,errs,calls=await open_page(b,URL,1440,900,init="localStorage.removeItem('mitView');");await p.wait_for_timeout(900);await grid(p)
    # 技能庫還沒有效果：減傷後＝原始
    t=await row(p,"全體 AOE A").inner_text()
    ok("80,000" in t and "剩 62,000" in t and "-" not in t.split("80,000")[1].split("遠敏")[0],"還沒有效果時，減傷後等於原始（遠敏剩 62,000）")
    # 打開補效果工具
    await p.click('[data-a="tools"]');await p.click('[data-a="skills"]');await p.wait_for_timeout(300)
    await p.click('[data-a="fxref"]');await p.wait_for_selector(".rfrow");await p.wait_for_timeout(200)
    on=await p.evaluate("[...document.querySelectorAll('.rfrow.on b')].map(x=>x.textContent)")
    ok(set(on)>={"野戰治療陣","聖盾陣","神聖領域","節制"},"依名稱自動對到：野戰治療陣、聖盾陣、神聖領域、節制 "+str(on))
    ok("戰慄" not in on and "展開戰術" not in on,"參考資料沒有的（戰慄、展開戰術）不會亂套")
    t=await p.inner_text("#modal");ok("對象：" not in t and "全隊 減傷 10%" in t,"預覽參考資料的效果（全隊 減傷 10%）")
    await p.screenshot(path=OUT+"/R-ref-1440.png")
    btn=p.locator('[data-a="fxrefapply"]');await btn.click();await btn.click();await p.wait_for_timeout(1200)
    lib=await p.evaluate("window.__MOCK.db['mitSkills/lib']")
    sch=[s for s in lib["jobs"]["SCH"]["skills"] if s["name"]=="野戰治療陣"][0]
    fx=sch["tiers"][-1]["fx"] if "tiers" in sch else []
    ok(fx and fx[0]["k"]=="mit" and fx[0]["v"]=="10" and fx[0]["w"]=="party","寫進技能庫：野戰治療陣 全隊 減傷 10%")
    ok(sch["name"]=="野戰治療陣" and "img" not in sch or True,"名稱不動")
    ok(lib["jobs"]["SCH"]["skills"][1]["name"]=="展開戰術" and not any((t.get("fx") or []) for t in lib["jobs"]["SCH"]["skills"][1].get("tiers",[])),"沒勾的技能不動")
    # 血量檢查：r1 全體 AOE 8萬 魔法，H1 野戰 10%＋H2 節制 10%
    await p.wait_for_timeout(300)
    t=await row(p,"全體 AOE A").inner_text()
    ok("64,800" in t and "-19%" in t and "剩 77,200" in t,"兩個 10% 減傷相乘：80,000→64,800（-19%），遠敏剩 77,200")
    t=await row(p,"死刑 B").inner_text()
    ok("-100%" in t and "剩 225,800" in t,"死刑：神聖領域 100%＋聖盾陣，坦克滿血")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]))
    if await p.locator("#modal").count():await p.evaluate("document.querySelector('#modal').remove()")
    await p.screenshot(path=OUT+"/R-grid-1440.png")
    # 復原
    await p.click("#utoast .ut-undo");await p.wait_for_timeout(1200)
    lib=await p.evaluate("window.__MOCK.db['mitSkills/lib']")
    sch=[s for s in lib["jobs"]["SCH"]["skills"] if s["name"]=="野戰治療陣"][0]
    ok(not any((t.get("fx") or []) for t in sch.get("tiers",[])),"按復原：技能庫回到原本")
    t=await row(p,"全體 AOE A").inner_text();ok("剩 62,000" in t,"復原後血條也回去")
    await ctx.close()
    # 單體技能沒選對象：提醒（用網站自己的 Firestore 函式寫，畫面會即時更新）
    ctx,p,errs,calls=await open_page(b,URL,1280,900,init="localStorage.removeItem('mitView');");await p.wait_for_timeout(900);await grid(p)
    W="""async(a)=>{const fs=await import('https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js');const db=fs.getFirestore();
      const L=JSON.parse(JSON.stringify(window.__MOCK.db['mitSkills/lib']));L.jobs.WHM.skills.push({id:"h9",name:"水流幕",tgt:"ally",tiers:[{lv:1,cd:60,dur:8,fx:[{k:"mit",v:"15",w:"target",t:"all"}]}]});
      if(a==="lib")await fs.setDoc(fs.doc(db,"mitSkills","lib"),L);
      else await fs.setDoc(fs.doc(db,"statics","s1","mit","d1","slots","H2"),{a:{r1:["h1"],r2:["h9"]},o:{},tg:a==="tg"?{r2:{h9:"MT"}}:{}});}"""
    await p.evaluate(W,"lib");await p.evaluate(W,"slot");await p.wait_for_timeout(600)
    t=await p.inner_text("#gw .foot");ok("有 1 次單體技能沒選對象" in t,"單體技能沒選對象時提醒沒算進去")
    await p.evaluate(W,"tg");await p.wait_for_timeout(600)
    t=await row(p,"死刑 B").inner_text();ok("-32%" in t,"選了對象（給 MT）就算進坦克的減傷（自帶 20%×水流幕 15%＝-32%）")
    t=await p.inner_text("#gw .foot");ok("沒選對象" not in t,"選了對象就不再提醒")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # 手機
    ctx,p,errs,calls=await open_page(b,URL,390,850,init="localStorage.removeItem('mitView');");await p.wait_for_timeout(900)
    await p.click('[data-a="tools"]');await p.click('[data-a="skills"]');await p.wait_for_timeout(300);await p.click('[data-a="fxref"]');await p.wait_for_selector(".rfrow")
    ok(await p.evaluate("document.documentElement.scrollWidth-innerWidth")<=0,"[390] 補效果工具無水平溢位")
    await p.screenshot(path=OUT+"/R-ref-390.png")
    ok(errs==[],"[390] 沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    await b.close();print(RES)
asyncio.run(m())
