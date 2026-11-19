import asyncio,json,sys,os
from playwright.async_api import async_playwright
H=os.path.dirname(os.path.abspath(__file__));REPO=os.path.dirname(H);OUT=os.path.join(H,"out");os.makedirs(OUT,exist_ok=True)
MOCK={"firebase-app.js":open(H+"/mock/fb-app.js",encoding="utf-8").read(),"firebase-auth.js":open(H+"/mock/fb-auth.js",encoding="utf-8").read(),"firebase-firestore.js":open(H+"/mock/fb-store.js",encoding="utf-8").read()}
FIX=open(H+"/mock/fixture.js",encoding="utf-8").read()
def _png(w=64,h=64,c=(150,170,210)):
    import zlib,struct
    raw=b"".join(b"\x00"+bytes(c)*w for _ in range(h))
    ch=lambda t,d:struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
    return b"\x89PNG\r\n\x1a\n"+ch(b"IHDR",struct.pack(">IIBBBBB",w,h,8,2,0,0,0))+ch(b"IDAT",zlib.compress(raw))+ch(b"IEND",b"")
PNG=_png()  # Discord 頭像用的假圖片
LAUNCH=dict(args=["--no-sandbox"],**({"executable_path":os.environ["CHROME"]} if os.environ.get("CHROME") else {}))
async def route(r):
    u=r.request.url
    if "gstatic.com/firebasejs" in u:
        name=u.split("/")[-1].split("?")[0];return await r.fulfill(status=200,content_type="text/javascript",body=MOCK[name])
    if "cdn.discordapp.com" in u:return await r.fulfill(status=200,content_type="image/png",body=PNG)
    if "fonts.googleapis.com" in u or "fonts.gstatic.com" in u:return await r.fulfill(status=200,content_type="text/css",body="")
    if u.startswith("http://localhost:876"):return await r.continue_()
    return await r.abort()
async def shot(b,url,name,w=1280,h=900,dark=False,full=True,actions=None):
    ctx=await b.new_context(viewport={"width":w,"height":h},color_scheme="dark" if dark else "light",device_scale_factor=1,has_touch=w<500,is_mobile=w<500)
    await ctx.add_init_script(FIX);await ctx.route("**/*",route)
    p=await ctx.new_page();errs=[]
    p.on("console",lambda m:errs.append(m.text) if m.type=="error" else None);p.on("pageerror",lambda e:errs.append("PAGEERR "+str(e)))
    await p.goto("http://localhost:8765/"+url);await p.wait_for_timeout(900)
    if actions:await actions(p)
    info=await p.evaluate("""()=>({ov:document.documentElement.scrollWidth-innerWidth,writes:window.__writes||[],log:window.__log||[],
      wide:[...document.querySelectorAll('body *')].filter(e=>{const r=e.getBoundingClientRect();return r.right>innerWidth+1&&r.width>0&&getComputedStyle(e).position!=='fixed'&&!e.closest('.am-gw,.gw,.mtable,.bisgridw,.tw,[style*=overflow]')}).slice(0,4).map(e=>e.tagName+'.'+e.className+' '+Math.round(e.getBoundingClientRect().right))})""")
    await p.screenshot(path=f"{OUT}/{name}.png",full_page=full)
    await ctx.close()
    bad=[e for e in errs if "favicon" not in e]
    print(f"{name:34s} overflow={info['ov']:3d} writes={len(info['writes'])} errs={len(bad)} {info['wide'] if info['ov']>0 else ''} {bad[:3]}")
    return info
async def main(which):
    async with async_playwright() as pw:
        b=await pw.chromium.launch(**LAUNCH)
        for name,url,w,h,dark in which:
            await shot(b,url,name,w,h,dark)
        await b.close()
if __name__=="__main__":
    spec=json.loads(sys.argv[1]);asyncio.run(main(spec))
