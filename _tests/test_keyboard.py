from lib import *
async def m():
  async with async_playwright() as pw:
    b=await browser(pw)
    for url in ["index.html?mock=member","schedule.html?mock=member&s=sv1","memories.html?mock=member","mit.html?mock=member&team=s1&duty=d1"]:
        ctx=await b.new_context(viewport={"width":1280,"height":900});await ctx.add_init_script(FIX);await ctx.route("**/*",route)
        p=await ctx.new_page();await p.goto("http://localhost:8765/"+url);await p.wait_for_timeout(1100)
        seen=[];invis=[]
        for i in range(30):
            await p.keyboard.press("Tab")
            r=await p.evaluate("""(()=>{const e=document.activeElement;if(!e||e===document.body)return null;const s=getComputedStyle(e);
              const vis=(s.outlineStyle!=='none'&&parseFloat(s.outlineWidth)>0)||(s.boxShadow&&s.boxShadow!=='none');
              return {t:(e.tagName+'.'+(e.className||'')).slice(0,30),txt:(e.textContent||e.value||'').trim().slice(0,10),vis}})()""")
            if not r:continue
            seen.append(r)
            if not r['vis']:invis.append(r['t']+' '+r['txt'])
        ok(len(seen)>=15 and not invis,f"{url.split('?')[0]}：Tab 走過 {len(seen)} 個元素，焦點都看得見"+("" if not invis else " ← 看不見："+str(invis[:5])))
        await ctx.close()
    await b.close();print(RES)
asyncio.run(m())
