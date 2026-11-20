/* =====================================================================
   全站共用：資料表與「同一個數字只算一次」的業務邏輯
   - 這裡只放「純函式」與常數，不讀寫 Firestore，方便測試，也不會影響各頁的資料流程
   - 新增職業、調整成團判斷，都只改這一個檔案
   ===================================================================== */

/* ---------- 職業 ----------
   n：全名（大廳、BiS、減傷軸）　s：簡稱（揪團）
   c：細分類（tank／heal／melee／phys／magic）　r：職能（tank／heal／dps） */
export const JOBS=[
  ["PLD","騎士","騎士","tank"],["WAR","戰士","戰士","tank"],["DRK","暗黑騎士","暗騎","tank"],["GNB","絕槍戰士","絕槍","tank"],
  ["WHM","白魔道士","白魔","heal"],["SCH","學者","學者","heal"],["AST","占星術師","占星","heal"],["SGE","賢者","賢者","heal"],
  ["MNK","武僧","武僧","melee"],["DRG","龍騎士","龍騎","melee"],["NIN","忍者","忍者","melee"],["SAM","武士","武士","melee"],["RPR","奪魂者","鐮刀","melee"],["VPR","毒蛇劍士","蛇","melee"],
  ["BRD","吟遊詩人","詩人","phys"],["MCH","機工士","機工","phys"],["DNC","舞者","舞者","phys"],
  ["BLM","黑魔道士","黑魔","magic"],["SMN","召喚士","召喚","magic"],["RDM","赤魔道士","赤魔","magic"],["PCT","繪靈法師","繪靈","magic"]
].map(([k,n,s,c])=>({k,n,s,c,r:c==="tank"||c==="heal"?c:"dps"}));
export const JOB=Object.fromEntries(JOBS.map(j=>[j.k,j]));

/* ---------- 輸出到畫面 ---------- */
export const esc=s=>String(s==null?"":s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
/* 連結只接受 http(s)，其他（例如 javascript:）一律不給連 */
export const safeUrl=u=>/^https?:\/\//i.test(String(u||""))?String(u):"#";

/* ---------- 揪團 ---------- */
const YMN=new Set(["y","m","n"]);
/* 回覆內容會被拿來組 HTML（例如 class 名稱），讀進來時先限定成已知的值 */
export function cleanRsvp(r){
  r=r&&typeof r==="object"?{...r}:{};
  r.go=YMN.has(r.go)?r.go:"n";
  const sl={};Object.entries(r.slots&&typeof r.slots==="object"?r.slots:{}).forEach(([k,v])=>{if(YMN.has(v))sl[k]=v;});r.slots=sl;
  r.jobs=Array.isArray(r.jobs)?r.jobs.filter(j=>JOB[j]):[];
  if(r.note!=null)r.note=String(r.note);
  return r;
}
/* 某個時間誰能來：沒有說「不行」，而且這個時間勾「可以」（ok）或「勉強」（mb）
   R：{uid: 回覆}；回傳的每一筆都帶 u（uid） */
export function slotTally(R,slotId){
  const list=Object.entries(R||{}).map(([u,r])=>({u,...r}));
  const ok=list.filter(r=>r.go!=="n"&&(r.slots||{})[slotId]==="y"),mb=list.filter(r=>r.go!=="n"&&(r.slots||{})[slotId]==="m");
  return{ok,mb,score:ok.length*2+mb.length};
}
/* 排位：有空的人能不能湊滿 坦/補/輸出
   每個人只能占一個位置，用二分圖匹配算最多能填滿幾格 */
export function fillComp(e,people){
  const seats=[];[["tank",e.t||0],["heal",e.h||0],["dps",e.d||0]].forEach(([r,n])=>{for(let i=0;i<n;i++)seats.push(r);});
  const roles=people.map(p=>new Set((p.jobs||[]).map(k=>(JOB[k]||{}).r).filter(Boolean)));
  const owner=new Array(seats.length).fill(-1);
  function aug(pi,seen){for(let s=0;s<seats.length;s++){if(seen[s]||!roles[pi].has(seats[s]))continue;seen[s]=true;if(owner[s]<0||aug(owner[s],seen)){owner[s]=pi;return true;}}return false;}
  people.forEach((_,pi)=>aug(pi,[]));
  const got={tank:0,heal:0,dps:0};owner.forEach((o,s)=>{if(o>=0)got[seats[s]]++;});
  return got;
}
/* 這個時間能不能成團：人數到最少門檻、職能也湊得齊
   回傳 state：""（沒有設門檻）、ok（可以成團）、maybe（算上勉強的可以）、roles（人夠但職能不齊）、short（還差 lack 人）
   over：超過人數上限 */
export function readyState(e,x){
  const mn=e.minSize||e.size||0;if(!mn&&!e.roles)return{state:"",need:0,lack:0,over:false};
  const okRoles=g=>!e.roles||(g.tank>=(e.t||0)&&g.heal>=(e.h||0)&&g.dps>=(e.d||0));
  const need=e.roles?Math.max(mn,(e.t||0)+(e.h||0)+(e.d||0)):mn;
  const A=x.ok,B=x.ok.concat(x.mb);
  const state=A.length>=need&&okRoles(fillComp(e,A))?"ok":B.length>=need&&okRoles(fillComp(e,B))?"maybe":A.length>=need?"roles":"short";
  return{state,need,lack:Math.max(0,need-A.length),over:!!(e.size&&A.length>e.size)};
}
/* 整個活動要看哪個時間：定案了就看定案的時間，否則看分數最高（最多人能來）的時間 */
export function bestSlot(e,R){
  const slots=e.slots||[];if(!slots.length)return null;
  if(e.status==="fixed"){const f=slots.find(s=>s.id===e.fixed);if(f)return{s:f,...slotTally(R,f.id),fixed:true};}
  let best=null;slots.forEach(s=>{const t={s,...slotTally(R,s.id)};if(!best||t.score>best.score)best=t;});
  return best;
}
