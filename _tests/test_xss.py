"""XSS 攻擊測試：把會執行程式的字串塞進資料庫（三種方式），再打開每一頁，確認沒有任何一段被執行"""
from lib import *
import sys
ATTACKS=[("自由文字欄位","xss_text.js"),("選項型欄位","xss_enum.js"),("文件 ID","xss_ids.js")]
MUT=""
CHECK="""(()=>({x:window.__xss||null,bad:[...document.querySelectorAll('[onerror],[onload]')].length,js:[...document.querySelectorAll('a[href^="javascript:" i]')].length}))()"""
async def visit(b,url,name,actions=None,w=1280):
    name=CUR+"｜"+name
    ctx=await b.new_context(viewport={"width":w,"height":900});await ctx.add_init_script(FIX);await ctx.add_init_script(MUT);await ctx.route("**/*",route)
    p=await ctx.new_page();errs=[];p.on("pageerror",lambda e:errs.append(str(e)))
    await p.goto("http://localhost:8765/"+url);await p.wait_for_timeout(1100)
    res=[]
    async def snap(lbl):
        r=await p.evaluate(CHECK);res.append((lbl,r))
    await snap("載入")
    if actions:
        for lbl,js in actions:
            try:
                await p.evaluate(js);await p.wait_for_timeout(500);await snap(lbl)
            except Exception as e:res.append((lbl,{"err":str(e)[:80]}))
    await ctx.close()
    bad=[(l,r) for l,r in res if r.get("x") or r.get("bad") or r.get("js")]
    ok(not bad,f"{name}：{len(res)} 個畫面都沒有執行注入的程式"+("" if not bad else " ← "+str(bad)))
    return res
C=lambda sel:f"(document.querySelector({json.dumps(sel)})||{{click(){{}}}}).click()"
CUR=""
async def m():
  global MUT,CUR
  async with async_playwright() as pw:
    b=await browser(pw)
    for label,fn in ATTACKS:
      MUT=open(os.path.join(H,"attacks",fn),encoding="utf-8").read();CUR=label
      await visit(b,"index.html?mock=owner","大廳（總團長）",[("展開成員",C('[data-act="membersToggle"]')),("近期安排更多",C('[data-act="agendaMore"]')),("選固定團",C('[data-pick="team"]'))])
      await visit(b,"index.html?mock=member","大廳（團員）",[("靈魂水晶",C('[data-nav="profile"]'))])
      await visit(b,"index.html?mock=owner&team=s1","固定團頁",[("管理",C('[data-act="manage"]')),("管理-團隊資料",C('[data-mg="team"]')),("管理-權限",C('[data-mg="leaders"]'))])
      await visit(b,"index.html?mock=owner&team=s1&mod=bis","BiS",[("全團",C('[data-bistab="all"]')),("分裝",C('[data-bistab="loot"]')),("設定",C('[data-bistab="settings"]'))])
      await visit(b,"events.html?mock=member","揪團列表",[("打開活動",C('.card a, .card, [data-e]'))])
      await visit(b,"events.html?mock=member&e=e1","揪團詳情")
      await visit(b,"events.html?mock=member&e=e2","揪團詳情（調查中）")
      await visit(b,"events.html?mock=member&e=e3","揪團詳情（有截止、結束時間、職能）")
      await visit(b,"events.html?mock=member&e=e4","揪團詳情（已截止）")
      await visit(b,"away.html?mock=member","請假行事曆",[("打開請假",C('[data-a="edit"]'))])
      await visit(b,"schedule.html?mock=member&s=sv1","出席調查",[("結果",C('.tab[data-tab="results"]')),("管理",C('.tab[data-tab="manage"]'))])
      await visit(b,"schedule.html","出席調查（未登入）")
      await visit(b,"mit.html?mock=member&team=s1&duty=d1","減傷軸",[("我的減傷",C('[data-a="vmode"][data-v="list"]')),("完整",C('[data-a="vmode"][data-v="grid"]')),("文字小抄",C('[data-a="text"]')),("機制詳情",C('[data-a="open"]'))])
      await visit(b,"memories.html?mock=member","回憶錄",[("首通",C('[data-kind="first"]'))])
      await visit(b,"memories.html?mock=member&m=m1","回憶詳情")
      await visit(b,"memories.html?mock=member&edit=m1","回憶編輯")
      await visit(b,"index.html?mock=signedout","未登入首頁")
    await b.close();print(RES)
asyncio.run(m())
