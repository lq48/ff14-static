from lib import *
import re
# 攻略 ↔ 減傷軸 互相連結：減傷軸那一列連到攻略的某一段；攻略自動列出「減傷軸連到這裡」；網址 &row= 直接打開那一列
W="""async(a)=>{const fs=await import('https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js');const db=fs.getFirestore();await fs.setDoc(fs.doc(db,...a.path),a.data,a.merge?{merge:true}:{});}"""
GA={"did":"d1","stage":"st1","title":"P1 全攻略","order":1,"blocks":[{"id":"hb","t":"h","text":"暴風破"},{"id":"p1","t":"p","text":"說明"},{"id":"hc","t":"h","text":"罪炎"}],"by":"u2","createdAt":1,"updatedAt":1}
row=lambda p,mech:p.locator("#gw tbody tr",has=p.locator(".cm .n",has_text=re.compile("^"+re.escape(mech)+"$"))).first
async def m():
  async with async_playwright() as pw:
    b=await browser(pw)
    ctx,p,errs,calls=await open_page(b,"mit.html?mock=owner&team=s1&duty=d1",1440,900,init="localStorage.setItem('mitView','grid');");await p.wait_for_timeout(900)
    await p.evaluate(W,{"path":["statics","s1","guides","gA"],"data":GA});await p.wait_for_timeout(700)
    await row(p,"全體 AOE D").locator(".cm .n").click();await p.wait_for_timeout(500)
    await p.locator("#dr .drtabs button",has_text="攻略").click();await p.wait_for_timeout(300)
    opts=await p.locator("#glSel option").all_inner_texts()
    ok("P1 全攻略" in opts and any("暴風破" in o for o in opts),"相關攻略：列出這個副本的文章和段落 "+str(opts))
    await p.select_option("#glSel","gA#hb");await p.click('#dr [data-a="gladd"]');await p.wait_for_timeout(1500)
    ws=[w for w in await p.evaluate("window.__writes") if w["path"]=="statics/s1/mit/d1"]
    ok(ws and ws[-1]["data"]["rows"]["r4"].get("gl")==[{"g":"gA","b":"hb"}],"存在減傷軸那一列（gl）")
    await p.click('#dr [data-a="sdone"]');await p.wait_for_timeout(300)
    lk=p.locator("#dr .glk")
    ok(await lk.count()==1 and "攻略：P1 全攻略 › 暴風破" in await lk.inner_text() and (await lk.get_attribute("href")).endswith("guide.html?team=s1&duty=d1&g=gA#b-hb"),"抽屜最上面：攻略連結，點了跳到那一段")
    ok("攻略" in await row(p,"全體 AOE D").locator("[data-pv]").inner_text(),"表格標籤多「攻略」")
    await p.screenshot(path=OUT+"/GL-mit-drawer.png")
    # 文章被刪掉
    await p.evaluate(W,{"path":["statics","s1","mit","d1"],"data":{"rows":{"r1":{"gl":[{"g":"nope"}],"note":"x"}}},"merge":True});await p.wait_for_timeout(600)
    await row(p,"全體 AOE A").locator(".cm .n").click();await p.wait_for_timeout(500)
    ok(await p.locator("#dr .glk").count()==0,"連到已刪除的文章：不顯示")
    await p.click('#dr [data-a="sedit"]');await p.wait_for_timeout(300)
    ok("（文章已刪除）" in await p.inner_text("#dr"),"編輯時看得到「文章已刪除」可以移除")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # 攻略：反向連結
    ctx,p,errs,calls=await open_page(b,"guide.html?mock=owner&team=s1&duty=d1&g=gA",1440,900);await p.wait_for_timeout(700)
    await p.evaluate(W,{"path":["statics","s1","guides","gA"],"data":GA})
    await p.evaluate(W,{"path":["statics","s1","mit","d1"],"data":{"rows":{"r4":{"gl":[{"g":"gA","b":"hb"}]},"r2":{"gl":[{"g":"gA","b":"hb"}]},"r5":{"gl":[{"g":"gA"}]}}},"merge":True});await p.wait_for_timeout(900)
    bl=p.locator("#b-hb + .bl a")
    ok(await bl.all_inner_texts()==["0:30 死刑 B","1:10 全體 AOE D"],"段落下面：減傷軸連到這裡（依時間排） "+str(await bl.all_inner_texts()))
    ok("row=r4" in await bl.nth(1).get_attribute("href"),"點了跳到減傷軸那一列")
    ok(await p.locator(".meta + .bl a",has_text="1:40 全體 AOE E").count()==1,"連到整篇的列在標題下面")
    ok(await p.locator("#b-hc + .bl").count()==0,"沒人連的段落不顯示")
    await p.screenshot(path=OUT+"/GL-guide.png")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # 網址 &row= 直接打開
    ctx,p,errs,calls=await open_page(b,"mit.html?mock=owner&team=s1&duty=d1&row=r4",1440,900,init="localStorage.setItem('mitView','grid');");await p.wait_for_timeout(2000)
    ok(await p.locator("#dr").is_visible() and "全體 AOE D" in await p.locator("#gw tr.on").inner_text() and await p.locator('#dr .drtabs button[aria-pressed="true"],#dr .drtabs button[aria-selected="true"]').inner_text()=="攻略","減傷軸 &row=r4：直接打開那一列的攻略分頁")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # 沒有攻略法權限：不顯示、不出錯
    ctx,p,errs,calls=await open_page(b,"mit.html?mock=plain&team=s1&duty=d1",1440,900,init="localStorage.setItem('mitView','grid');");await p.wait_for_timeout(900)
    await p.evaluate(W,{"path":["statics","s1","mit","d1"],"data":{"rows":{"r4":{"gl":[{"g":"gA","b":"hb"}]}}},"merge":True});await p.wait_for_timeout(700)
    ok(await p.locator("#gw .glk").count()==0 and "攻略" not in (await row(p,"全體 AOE D").inner_text()),"沒有攻略法權限：不顯示攻略連結")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # 手機清單
    ctx,p,errs,calls=await open_page(b,"mit.html?mock=owner&team=s1&duty=d1",390,800,init="localStorage.setItem('mitView','list');");await p.wait_for_timeout(900)
    await p.evaluate(W,{"path":["statics","s1","guides","gA"],"data":GA})
    await p.evaluate(W,{"path":["statics","s1","mit","d1"],"data":{"rows":{"r4":{"gl":[{"g":"gA","b":"hb"}]}}},"merge":True});await p.wait_for_timeout(900)
    it=p.locator(".litem",has_text="全體 AOE D")
    ok(await it.locator(".glk").count()==1,"我的減傷清單也有攻略連結")
    ok(await p.evaluate("document.documentElement.scrollWidth-innerWidth")<=0,"無水平溢位")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    await b.close();print(RES)
asyncio.run(m())
