from lib import *
EXTRA="""(function(){const db=window.__MOCK.db,pd=n=>String(n).padStart(2,"0"),day=k=>{const d=new Date();d.setDate(d.getDate()+k);return d.getFullYear()+"-"+pd(d.getMonth()+1)+"-"+pd(d.getDate());};
 // 人數夠（4 人都勾可以）但都是輸出 → 職能不齊
 db["events/e3"]={title:"職能測試團",kind:"高難度",status:"open",fixed:"",roles:true,t:1,h:1,d:2,minSize:4,size:8,slots:[{id:"z1",d:day(2),t:"21:00"},{id:"z2",d:day(3),t:"21:00"}],by:"u2",createdAt:5};
 ["u5","u6","u7","u8"].forEach(u=>db["events/e3/rsvp/"+u]={by:u,go:"y",slots:{z1:"y"},jobs:["SAM"]});
 // 勉強才湊得齊
 db["events/e4"]={title:"勉強成團",kind:"其他",status:"open",fixed:"",minSize:3,size:8,slots:[{id:"w1",d:day(4),t:"20:00"}],by:"u2",createdAt:6};
 db["events/e4/rsvp/u2"]={by:"u2",go:"y",slots:{w1:"y"}};db["events/e4/rsvp/u3"]={by:"u3",go:"y",slots:{w1:"m"}};db["events/e4/rsvp/u4"]={by:"u4",go:"m",slots:{w1:"m"}};
 // 有回「想參加」但沒勾任何時間的人，不算確定
 db["events/e1/rsvp/u6"]={by:"u6",go:"y",slots:{}};
})();"""
async def m():
  async with async_playwright() as pw:
    b=await browser(pw)
    ctx,p,errs,calls=await open_page(b,"index.html?mock=member",init="");
    await ctx.close()
    ctx=await b.new_context(viewport={"width":1280,"height":900});await ctx.add_init_script(FIX);await ctx.add_init_script(EXTRA);await ctx.route("**/*",route)
    p=await ctx.new_page();errs=[];p.on("pageerror",lambda e:errs.append(str(e)))
    await p.goto("http://localhost:8765/index.html?mock=member");await p.wait_for_timeout(1200)
    lobby=await p.evaluate("""Object.fromEntries([...document.querySelectorAll('#events .evi')].map(a=>[a.querySelector('.evt, b, strong')?a.querySelector('.evt, b, strong').textContent:a.textContent.slice(0,12), [...a.querySelectorAll('.evs')].map(x=>x.textContent).filter(t=>/成團|還差|職能/.test(t)).join('|')]))""")
    print("  大廳：",lobby)
    next_=" ".join((await p.inner_text("#nextBody")).split())
    for eid,title in [("e1","絕伊甸 練習"),("e2","週末挖寶團"),("e3","職能測試團"),("e4","勉強成團")]:
        await p.goto(f"http://localhost:8765/events.html?mock=member&e={eid}");await p.wait_for_timeout(900)
        pills=await p.evaluate("""[...document.querySelectorAll('.res')].map(r=>({best:r.classList.contains('best'),t:[...r.querySelectorAll('.pill')].map(x=>x.textContent).join('|')}))""")
        fixed=await p.evaluate("!!document.querySelector('.res.fixed, .res .fx')")
        page=[x['t'] for x in pills if x['best']] or [pills[0]['t'] if pills else '']
        lob=next((v for k,v in lobby.items() if title[:4] in k),None)
        norm=lambda t:(t or "").split("|")[0].replace("算上勉強的可以成團","勉強").replace("可以成團","可以")
        print(f"  {title}: 揪團頁={page} 大廳={lob}")
        ok(lob is not None and norm(lob)==norm(page[0]),f"「{title}」大廳與揪團頁的成團狀態一致")
    await p.goto("http://localhost:8765/index.html?mock=nosurvey");await p.wait_for_timeout(1200)
    next_=" ".join((await p.inner_text("#nextBody")).split())
    ok("2 人確定參加" in next_,"下一場冒險：只勾「想參加」沒勾時間的人不算確定（2 人）："+next_[:60])
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]))
    await b.close();print(RES)
asyncio.run(m())
