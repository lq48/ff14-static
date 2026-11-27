from lib import *
# 揪團：職能統計依志願排位、「最多人」標籤不被拆字；近期安排的請假改成附註
async def m():
  async with async_playwright() as pw:
    b=await browser(pw)
    for w in (1280,768,390,360):
      ctx,p,errs,calls=await open_page(b,"events.html?mock=member&e=e3",w,900);await p.wait_for_timeout(600)
      res=await p.query_selector(".res.best")
      ok(res is not None,f"[{w}] 有標示最多人的時間")
      t=await res.inner_text()
      if w==1280:
        print("  ---\n"+t+"\n  ---")
        ok("坦 1/2" in t and "補 2/2" in t and "輸出 2/4" in t,"職能統計依第一志願（坦 1/2、補 2/2、輸出 2/4）")
        ok("山壯 也能坦" in t,"缺的職能列出可以轉的人")
        lu=" ".join((await p.inner_text(".res.best .lineup")).split());ok("山壯 武僧" in lu and "諾爾 暗騎" in lu and "楓之旋律 占星" in lu,"排位明細顯示每個人排到的職業")
        ok("志願" not in lu,"大家都排到第一志願時，不顯示志願標記")
      # 「最多人」：::after 是 inline-block + nowrap，量它的高度 = 一行
      h=await p.evaluate("(()=>{const el=document.querySelector('.res.best .when');const cs=getComputedStyle(el,'::after');return [cs.display,cs.whiteSpace]})()")
      ok(h==["inline-block","nowrap"],f"[{w}] 「最多人」整個標籤一起換行，不會拆字 {h}")
      ok(await p.evaluate("document.documentElement.scrollWidth-innerWidth")<=0,f"[{w}] 無水平溢位")
      ok(errs==[],f"[{w}] 沒有 JS 錯誤 "+str(errs[:1]))
      el=await p.query_selector(".res.best");await el.scroll_into_view_if_needed();await el.screenshot(path=OUT+f"/L-res-{w}.png")
      await ctx.close()
    # 需要有人轉職才湊得滿：自動排到第二志願並標示
    ctx,p,errs,calls=await open_page(b,"events.html?mock=member&e=e3",1280,900);await p.wait_for_timeout(500)
    await ctx.close()
    # 近期安排
    for w in (1280,390):
      ctx,p,errs,calls=await open_page(b,"index.html?mock=member",w,900);await p.wait_for_timeout(600)
      n_ag=await p.evaluate("document.querySelectorAll('#agendaBody .ag-away').length");ok(n_ag==0,f"[{w}] 請假不再用活動卡片")
      st=await p.evaluate("""(()=>{const a=document.querySelector('#agendaBody .ag-awayl a'),e=document.querySelector('#agendaBody a.ag');if(!a||!e)return null;const A=getComputedStyle(a),E=getComputedStyle(e);return {af:parseFloat(A.fontSize),ef:parseFloat(E.fontSize),ah:a.getBoundingClientRect().height,eh:e.getBoundingClientRect().height,bg:A.backgroundColor}})()""")
      ok(st and st["af"]<st["ef"] and st["ah"]<st["eh"] and st["bg"] in ("rgba(0, 0, 0, 0)","transparent"),f"[{w}] 請假是較小、無底色的一行 {st}")
      q=await p.evaluate("[...document.querySelectorAll('#agendaBody .ag-day.quiet')].map(d=>d.getBoundingClientRect().height)")
      nq=await p.evaluate("[...document.querySelectorAll('#agendaBody .ag-day:not(.quiet)')].map(d=>d.getBoundingClientRect().height)")
      ok(q and max(q)<min(nq),f"[{w}] 只有請假的日子縮成矮的一行 {q[:3]} vs {nq[:3]}")
      ok(await p.evaluate("document.documentElement.scrollWidth-innerWidth")<=0,f"[{w}] 無水平溢位")
      ok(errs==[],f"[{w}] 沒有 JS 錯誤 "+str(errs[:1]))
      el=await p.query_selector("#agenda");await el.scroll_into_view_if_needed();await el.screenshot(path=OUT+f"/AG-{w}.png")
      await ctx.close()
    await b.close();print(RES)
asyncio.run(m())
