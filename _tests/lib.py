import asyncio,json
from run import *
import socket,subprocess,time
def ensure_server(root=REPO,port=8765):
    s=socket.socket()
    try:s.connect(("127.0.0.1",port));s.close();return
    except OSError:pass
    subprocess.Popen(["python3","-m","http.server",str(port)],cwd=root,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True);time.sleep(1)
ensure_server()
RES={"pass":0,"fail":0}
def ok(c,m):
    RES["pass" if c else "fail"]+=1;print(("PASS " if c else "FAIL ")+m)
async def open_page(b,url,w=1280,h=900,dark=False,init="",worker=None):
    ctx=await b.new_context(viewport={"width":w,"height":h},color_scheme="dark" if dark else "light",is_mobile=w<500,has_touch=w<500)
    await ctx.add_init_script(init+FIX);await ctx.route("**/*",route)
    calls=[]
    async def wk(r):
        calls.append({"url":r.request.url,"body":r.request.post_data})
        await r.fulfill(status=200,content_type="application/json",body=json.dumps(worker or {"ok":True,"tagged":2}))
    await ctx.route("https://ff14-notify.lq0408.workers.dev/**",wk)
    p=await ctx.new_page();errs=[];p.on("pageerror",lambda e:errs.append(str(e)))
    await p.goto("http://localhost:8765/"+url);await p.wait_for_timeout(1000)
    return ctx,p,errs,calls
async def browser(pw):return await pw.chromium.launch(**LAUNCH)
