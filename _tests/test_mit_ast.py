from lib import *
# 占星抽卡：星極／靈極共用 CD；卡要先抽到才能放、每次抽卡每張一次；P1 開場有星極的卡；之後階段延續手上的卡（CD 當作好了）。只提醒、不擋
URL="mit.html?mock=owner&team=s1&duty=d1"
W="""async(a)=>{const fs=await import('https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js');const db=fs.getFirestore();await fs.setDoc(fs.doc(db,...a.path),a.data,a.merge?{merge:true}:{});}"""
SK=[("a1","星極抽卡",55,0),("a2","靈極抽卡",55,0),("a3","放浪神之箭",1,15),("a4","建築神之塔",1,30),("a5","世界樹之幹",1,15),("a6","河流神之瓶",1,15)]
ST1=[{"id":"r0","kind":"head","mech":"開場"},{"id":"r1","t":"0:12","mech":"全體 AOE A","hits":[]},{"id":"r2","t":"0:30","mech":"死刑 B","hits":[]},{"id":"r3","t":"0:50","mech":"分攤 C","hits":[]},{"id":"r4","t":"1:10","mech":"全體 AOE D","hits":[]},{"id":"r5","t":"1:40","mech":"全體 AOE E","hits":[]}]
ST2=[{"id":"q1","t":"0:10","mech":"二王 A","hits":[]},{"id":"q2","t":"0:20","mech":"二王 B","hits":[]}]
A={"r1":["a3"],"r2":["a2","a5"],"r3":["a1"],"r4":["a6"],"r5":["a5"],"q1":["a6"],"q2":["a1","a4"]}
async def m():
  async with async_playwright() as pw:
    b=await browser(pw)
    ctx,p,errs,calls=await open_page(b,URL,1440,900,init="localStorage.setItem('mitView','grid');");await p.wait_for_timeout(900)
    await p.evaluate(W,{"path":["mitSkills","lib"],"data":{"jobs":{"AST":{"skills":[{"id":i,"name":n,"cd":c,"dur":d,"minLv":1} for i,n,c,d in SK]}}},"merge":True})
    await p.evaluate(W,{"path":["mitDuties","d1"],"data":{"stages":[{"id":"st1","name":"一王","rows":ST1},{"id":"st2","name":"二王","rows":ST2}]},"merge":True})
    await p.evaluate(W,{"path":["statics","s1","mit","d1"],"data":{"comp":{"H2":"AST"}},"merge":True})
    await p.evaluate(W,{"path":["statics","s1","mit","d1","slots","H2"],"data":{"a":A,"o":{},"tg":{}}})
    await p.wait_for_timeout(900)
    T=lambda r,k:p.locator(f'#gw td.cell[data-r="{r}"][data-s="H2"][data-k="{k}"]').get_attribute("title")
    C=lambda r,k:p.locator(f'#gw td.cell[data-r="{r}"][data-s="H2"][data-k="{k}"]').get_attribute("class")
    t=await T("r1","a3");ok("沒有" not in t and "使用" in t,"P1 開場：放浪神之箭可以直接用（已經有星極抽卡的卡）")
    t=await T("r2","a2");ok("CD" not in t and "使用" in t,"P1 開場：靈極抽卡可以直接用")
    t=await T("r2","a5");ok("沒有" not in t,"靈極抽卡後同一列放世界樹之幹：可以")
    t=await T("r3","a1");ok("和靈極抽卡共用 CD" in t and "bad" in await C("r3","a1"),"0:50 星極抽卡：和 0:30 的靈極抽卡共用 CD，提醒 "+t)
    t=await T("r4","a6");ok("沒有" not in t,"河流神之瓶：還在手上")
    t=await T("r5","a5");ok("沒有靈極抽卡的卡可用" in t and "short" in await C("r5","a5"),"世界樹之幹第二次：這次抽卡已經用過了，提醒")
    ok(await p.locator('#gw td.cell[data-r="r5"][data-s="H2"][data-k="a5"] .ico,#gw td.cell[data-r="r5"][data-s="H2"][data-k="a5"] .tx').count()==1,"只提醒、不擋：格子還是排上去")
    await p.screenshot(path=OUT+"/AST-p1-1440.png")
    await p.click('[data-a="stage"][data-i="1"]');await p.wait_for_timeout(700)
    t=await T("q1","a6");ok("沒有靈極抽卡的卡可用" in t,"P2：延續 P1 手上的卡（河流神已用掉）")
    t=await T("q2","a1");ok("CD" not in t,"P2：抽卡 CD 當作已經好了")
    t=await T("q2","a4");ok("沒有" not in t,"P2：星極抽卡後放建築神之塔：可以")
    # 我的減傷清單也看得到提醒
    await p.click('[data-a="vmode"][data-v="list"]');await p.click('[data-a="filt"][data-s="H2"]');await p.wait_for_timeout(500)
    ok("沒有靈極抽卡的卡可用" in await p.inner_text("#gw"),"我的減傷清單也有提醒")
    ok(errs==[],"沒有 JS 錯誤 "+str(errs[:1]));await ctx.close();await b.close();print(RES)
asyncio.run(m())
