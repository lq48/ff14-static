from lib import *
PAGES=[("index.html?mock=member","大廳"),("index.html?mock=signedout","未登入"),("events.html?mock=member","揪團"),("events.html?mock=member&e=e1","揪團詳情"),
 ("away.html?mock=member","請假"),("schedule.html?mock=member&s=sv1","出席調查"),("mit.html?mock=member&team=s1&duty=d1","減傷軸"),
 ("index.html?mock=member&team=s1&mod=bis","BiS"),("memories.html?mock=member","回憶錄"),("moogle.html","莫古")]
MEASURE="""(async()=>{
  const cls=await new Promise(res=>{let v=0;try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)v+=e.value;}).observe({type:'layout-shift',buffered:true});}catch(e){}setTimeout(()=>res(v),400);});
  const vis=e=>{const r=e.getBoundingClientRect();const s=getComputedStyle(e);return r.width>0&&r.height>0&&s.visibility!=='hidden'&&s.display!=='none';};
  const small=[...document.querySelectorAll('button,a.btn,select,input:not([type=hidden]),.chip,.tab,[role=button]')].filter(vis).filter(e=>{const r=e.getBoundingClientRect();return (r.height<32||r.width<32)&&!e.closest('#fillGrid,table.g,.gw table,.am-g,.cal,.bisgrid');});
  const imgs=[...document.images].filter(i=>i.getBoundingClientRect().top>innerHeight*1.2&&i.loading!=='lazy'&&!i.src.startsWith('data:'));
  return {ov:document.documentElement.scrollWidth-innerWidth,cls:+cls.toFixed(3),small:small.length,smallEx:[...new Set(small.slice(0,6).map(e=>(e.className||e.tagName).toString().slice(0,24)+':'+Math.round(e.getBoundingClientRect().height)))],eager:imgs.length,
    anim:document.getAnimations().filter(a=>a.playState==='running').length};
})()"""
async def m():
  async with async_playwright() as pw:
    b=await browser(pw)
    rows=[]
    for url,name in PAGES:
      for w in (360,390,768,1280):
        ctx=await b.new_context(viewport={"width":w,"height":800},is_mobile=w<500,has_touch=w<800,reduced_motion="reduce");await ctx.add_init_script(FIX);await ctx.route("**/*",route)
        p=await ctx.new_page();errs=[];p.on("pageerror",lambda e:errs.append(str(e)))
        await p.goto("http://localhost:8765/"+url);await p.wait_for_timeout(1300)
        r=await p.evaluate(MEASURE);r["errs"]=len(errs);rows.append((name,w,r));await ctx.close()
    print(f"{'頁面':8s}{'寬':>5s} 溢位  CLS   小按鈕 未延遲圖 動畫 錯誤")
    for name,w,r in rows:
        flag="" if (r['ov']<=0 and r['cls']<0.1 and r['errs']==0) else "  ←"
        print(f"{name:8s}{w:5d} {r['ov']:4d} {r['cls']:5.3f} {r['small']:5d} {r['eager']:6d} {r['anim']:4d} {r['errs']:3d} {r['smallEx'] if r['small'] else ''}{flag}")
    await b.close()
asyncio.run(m())
