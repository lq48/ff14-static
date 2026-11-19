/* =====================================================================
   共用互動元件：可以「復原」的提示
   用法：
     import { undoToast } from "./ui.js?v=1";
     undoToast("已刪除 11/20 的請假", async()=>{ ...把資料寫回去... });
   - 提示停留 8 秒（滑鼠移上去或鍵盤聚焦時暫停），按「復原」會執行一次 onUndo
   - 同時只會有一個；出現新的提示時，舊的就不能再復原
   ===================================================================== */
let cur=null;
function el(){
  let e=document.getElementById("utoast");
  if(!e){e=document.createElement("div");e.id="utoast";e.className="utoast";e.setAttribute("role","status");e.setAttribute("aria-live","polite");e.hidden=true;document.body.appendChild(e);}
  return e;
}
function hide(){const e=el();e.hidden=true;e.innerHTML="";if(cur){clearTimeout(cur.t);cur=null;}}
export function undoToast(msg,onUndo,ms=8000){
  hide();
  const e=el(),c={done:false,t:null,left:ms,start:Date.now()};cur=c;
  e.innerHTML='<span class="ut-msg"></span>'+(onUndo?'<button type="button" class="ut-undo">復原</button>':'')+'<button type="button" class="ut-x" aria-label="關閉提示">×</button>';
  e.querySelector(".ut-msg").textContent=msg;e.hidden=false;
  const arm=()=>{c.start=Date.now();c.t=setTimeout(()=>{if(cur===c)hide();},c.left);};
  const pause=()=>{clearTimeout(c.t);c.left=Math.max(1500,c.left-(Date.now()-c.start));};
  e.onmouseenter=pause;e.onmouseleave=arm;e.onfocusin=pause;e.onfocusout=arm;
  e.querySelector(".ut-x").onclick=hide;
  const b=e.querySelector(".ut-undo");
  if(b)b.onclick=async()=>{if(c.done)return;c.done=true;b.disabled=true;b.textContent="復原中…";
    try{await onUndo();e.querySelector(".ut-msg").textContent="已復原";b.remove();clearTimeout(c.t);c.left=2500;arm();}
    catch(err){console.error(err);e.querySelector(".ut-msg").textContent=err&&err.code==="permission-denied"?"復原失敗：沒有權限":"復原失敗，請再試一次";b.remove();c.left=4000;arm();}};
  arm();
}
