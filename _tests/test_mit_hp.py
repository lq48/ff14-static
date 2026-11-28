from lib import *
import json,os
# 減傷軸：血量檢查（類型、對象、原始傷害、血條；連段、持續傷害、各職能血量）
SEED=open(os.path.join(os.path.dirname(__file__),"data","fru-mit-seed.json"),encoding="utf-8").read()
async def load(b,w,h=900,scen="owner"):
    ctx,p,errs,calls=await open_page(b,f"mit.html?mock={scen}",w,h);await p.wait_for_timeout(700)
    await p.click('[data-a="io"]');await p.fill("#ta",SEED)
    imp=p.locator('[data-a="import"]');await imp.click();await imp.click();await p.wait_for_timeout(900)
    if await p.locator('[data-a="vmode"][data-v="grid"][aria-pressed="false"]').count():await p.click('[data-a="vmode"][data-v="grid"]');await p.wait_for_timeout(300)
    return ctx,p,errs
import re
row=lambda p,mech,n=0:p.locator("#gw tbody tr",has=p.locator(".cm .n",has_text=re.compile("^"+re.escape(mech)+"$"))).nth(n)
async def m():
  async with async_playwright() as pw:
    b=await browser(pw)
    # ---- 純計算（在瀏覽器裡載入 mit-hp.js）
    ctx,p,errs,calls=await open_page(b,"mit.html?mock=owner",1280,900);await p.wait_for_timeout(400)
    r=await p.evaluate("""async()=>{const m=await import('./mit-hp.js?v=3');const c=m.hpCfg({});
      const R=[{id:"a",hits:[{dtype:"phys",dmg:"92,000"}]},{id:"b",hits:[{dtype:"magic",dmg:"115,000"}]},{id:"c",tag:"死刑",hits:[{dtype:"magic",dmg:"800,000"}]},
        {id:"d",hits:[{dtype:"magic",dmg:"132,000",dot:"92,000",tk:5}]},{id:"x",aoe:"<img src=x>",hits:[{dmg:"<b>1</b>"}]}];
      const o=m.hpCheck(R,[15,17,24,86,200],c);
      return {p:[m.parseDmg("9.2萬"),m.parseDmg("80k"),m.parseDmg("1,200,000"),m.parseDmg("abc")],a:[o.a.role,o.a.left],b:[o.b.role,o.b.left,o.b.chain],c:[o.c.role,o.c.left],d:[o.d.left,o.d.dotLeft],x:o.x===undefined,aoe:m.aoeOf({aoe:"<img>"})}}""")
    ok(r["p"]==[92000,80000,1200000,0],"傷害文字解析（9.2萬、80k、1,200,000）")
    ok(r["a"]==["caster",50000],"物理看法系")
    ok(r["b"]==["ranged",-65000,True],"魔法看遠敏，2 秒內接連的傷害疊加")
    ok(r["c"]==["tank",225800-640000],"死刑看坦克（含坦克自帶 20%），不疊全體傷害以外的連段")
    ok(r["d"]==[10000,10000-460000],"持續傷害：每 3 秒一跳，跳完的剩餘血量")
    ok(r["x"] and r["aoe"]=="","看不懂的數值和對象會被忽略")
    await ctx.close()
    # ---- 畫面
    ctx,p,errs=await load(b,1440)
    t=await row(p,"暴風破").inner_text();ok("法系 142,000" in t and "剩 50,000" in t and "92,000" in t,"0:15 暴風破：原始 92,000、法系剩 50,000")
    t=await row(p,"罪炎 或 罪雷").inner_text();ok("遠敏" in t and "連段" in t and "會死・差 65,000" in t,"0:17 罪炎：遠敏、連段、會死差 65,000")
    ok(await row(p,"罪炎 或 罪雷").locator(".hpb.dead").count()==1,"會死的血條是紅字")
    t=await row(p,"連鎖爆印銘刻").inner_text();ok("坦克 225,800" in t and "死刑" in t,"死刑看坦克")
    t=await row(p,"爆印").inner_text();ok("雙坦分攤" in t and "剩 -" not in t,"雙坦分攤看坦克")
    ok(await p.locator("#gw thead .hc").count()==5,"表頭多五欄（含減傷後）")
    ok(await p.locator("#gw .cm .dm").count()==0,"開血量檢查時，機制欄不重複顯示傷害")
    # 持續傷害（光焰圓光 132,000＋92,000×5）
    t=await row(p,"光焰圓光").inner_text();ok("持續 92,000×5" in t and "持續傷害跳完" in t,"持續傷害顯示每跳與跳完的血量")
    # 速度：每個階段重畫
    ms=await p.evaluate("""()=>{const bs=[...document.querySelectorAll('[data-a="stage"]')],out=[];bs.forEach((b,i)=>{const q=document.querySelectorAll('[data-a="stage"]')[i];const t0=performance.now();q.click();document.body.offsetHeight;out.push(performance.now()-t0);});return Math.max(...out)}""")
    ok(ms<150,f"切換階段（含血量計算）最慢 {ms:.0f} 毫秒")
    print(f"  切換階段最慢 {ms:.0f} ms")
    await p.click('[data-a="stage"][data-i="0"]');await p.wait_for_timeout(200)
    # 寬螢幕：血量欄固定在左邊
    pos=await p.evaluate("getComputedStyle(document.querySelector('#gw tbody .h4')).position");ok(pos=="sticky","寬螢幕血量欄固定在左邊")
    # 編輯：把暴風破改成死刑對象 → 看坦克
    await row(p,"暴風破").locator(".mb").click();await p.wait_for_timeout(300)
    await p.select_option('#dr [data-f="aoe"]',"tank");await p.wait_for_timeout(500)
    t=await row(p,"暴風破").inner_text();ok("坦克" in t and "死刑" in t,"抽屜改對象，血條改看坦克")
    await p.select_option('#dr [data-f="aoe"]',"");await p.wait_for_timeout(1200)  # 存檔有 0.7 秒延遲
    d=await p.evaluate("window.__MOCK.db['mitDuties/fru'].stages[0].rows.find(r=>r.mech==='暴風破')")
    ok("aoe" not in d,"改回「依類型標籤」時不留空欄位")
    await p.fill('#dr [data-h="dot"][data-i="0"]',"10,000");await p.fill('#dr [data-h="tk"][data-i="0"]',"3");await p.wait_for_timeout(1200)
    d=await p.evaluate("window.__MOCK.db['mitDuties/fru'].stages[0].rows.find(r=>r.mech==='暴風破')")
    ok(d["hits"][0].get("dot")=="10,000" and d["hits"][0].get("tk")==3,"抽屜可以填持續傷害（存成每跳文字、跳數數字）")
    t=await row(p,"暴風破").inner_text();ok("持續 10,000×3" in t,"表格顯示新填的持續傷害")
    await p.click('#dr [data-a="dclose"]')
    # 副本設定：法系血量改 160,000
    await p.click('[data-a="tools"]');await p.click('[data-a="dutyset"]');await p.wait_for_timeout(300)
    await p.fill('[data-hp="caster"]',"160000");await p.fill('[data-hp="chain"]',"3");await p.click('[data-a="dutysave"]');await p.wait_for_timeout(700)
    d=await p.evaluate("window.__MOCK.db['mitDuties/fru']")
    ok(d["hp"]["caster"]==160000 and d["chain"]==3 and d["hp"]["tank"]==225800,"副本設定存各職能血量和連段秒數")
    t=await row(p,"暴風破").inner_text();ok("法系 160,000" in t and "剩 68,000" in t and "持續傷害跳完會死" in t,"改血量後血條跟著變；主要數字是這一下打完，小字是持續傷害跳完")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]))
    await p.screenshot(path=OUT+"/H-grid-1440.png")
    # 關掉
    await p.click('[data-a="tools"]');await p.click('[data-a="hpchk"]');await p.wait_for_timeout(300)
    ok(await p.locator("#gw .hc").count()==0 and await p.locator("#gw .cm .dm").count()>0,"關掉血量檢查：回到原本的表格")
    ok(await p.evaluate("localStorage.getItem('mitHp')")=="0","開關記在這台裝置")
    await ctx.close()
    # ---- 舊資料（M6S：「8萬」、類型標籤）也能畫
    ctx,p,errs,calls=await open_page(b,"mit.html?mock=owner",1280,900);await p.wait_for_timeout(700)
    if await p.locator('[data-a="vmode"][data-v="grid"][aria-pressed="false"]').count():await p.click('[data-a="vmode"][data-v="grid"]');await p.wait_for_timeout(300)
    t=await row(p,"全體 AOE A").inner_text();ok("全體" in t and "80,000" in t and "剩 62,000" in t,"舊資料「8萬」＋全體AOE 標籤直接有血條")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    # ---- 手機
    for w in (360,390):
      ctx,p,errs=await load(b,w,850)
      if await p.locator('[data-a="vmode"][data-v="list"][aria-pressed="false"]').count():await p.click('[data-a="vmode"][data-v="list"]');await p.wait_for_timeout(300)
      ok(await p.locator(".litem .hpb.cp").count()>=5,f"[{w}] 我的減傷（全部）列出有傷害的機制和血條")
      ok(await p.evaluate("document.documentElement.scrollWidth-innerWidth")<=0,f"[{w}] 無水平溢位")
      if w==390:await p.screenshot(path=OUT+"/H-list-390.png")
      await p.click('[data-a="vmode"][data-v="grid"]');await p.wait_for_timeout(300)
      pos=await p.evaluate("getComputedStyle(document.querySelector('#gw tbody .h4')).position");ok(pos!="sticky",f"[{w}] 窄螢幕血量欄跟著捲動，不佔住畫面")
      ok(errs==[],f"[{w}] 沒有 JS 錯誤 "+str(errs[:1]));await ctx.close()
    await b.close();print(RES)
asyncio.run(m())
