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
   每個人只能占一個位置。先求「最多能填滿幾格」，填法一樣多時，選最符合每個人志願順序的那一種
   （jobs 陣列的順序就是志願順序，第一個是主職）。用最小成本最大流計算，人數再多也很快。
   回傳 got：各職能填了幾格；pick：每個人被排到的職業（沒排到是 null）；rank：那是他的第幾志願（0 起算） */
export function assignComp(e,people){
  const R=["tank","heal","dps"],cap={tank:e.t||0,heal:e.h||0,dps:e.d||0},P=people.length;
  const S=0,T=P+4,N=P+5,G=[...Array(N)].map(()=>[]);
  const edge=(a,b,c,w)=>{G[a].push({to:b,c,w,r:G[b].length});G[b].push({to:a,c:0,w:-w,r:G[a].length-1});};
  const best=people.map(p=>{const m={};(p.jobs||[]).forEach((k,i)=>{const r=(JOB[k]||{}).r;if(r&&!(r in m))m[r]={k,i};});return m;});
  people.forEach((_,i)=>{edge(S,1+i,1,0);R.forEach((r,ri)=>{const b=best[i][r];if(b&&cap[r])edge(1+i,P+1+ri,1,b.i);});});
  R.forEach((r,ri)=>{if(cap[r])edge(P+1+ri,T,cap[r],0);});
  for(;;){ /* 每次沿著成本最低的路多排一個人（Bellman-Ford，可處理反向的負成本） */
    const d=Array(N).fill(Infinity),pv=Array(N).fill(null);d[S]=0;
    for(let it=0,ch=true;it<N&&ch;it++){ch=false;for(let a=0;a<N;a++)if(d[a]<Infinity)G[a].forEach((x,xi)=>{if(x.c>0&&d[a]+x.w<d[x.to]){d[x.to]=d[a]+x.w;pv[x.to]=[a,xi];ch=true;}});}
    if(d[T]===Infinity)break;
    for(let v=T;v!==S;){const[a,xi]=pv[v],x=G[a][xi];x.c--;G[v][x.r].c++;v=a;}
  }
  const got={tank:0,heal:0,dps:0},pick=Array(P).fill(null),rank=Array(P).fill(null);
  people.forEach((_,i)=>G[1+i].forEach(x=>{if(x.to>P&&x.to<=P+3&&x.c===0){const r=R[x.to-P-1];got[r]++;pick[i]=best[i][r].k;rank[i]=best[i][r].i;}}));
  return{got,pick,rank};
}
export function fillComp(e,people){return assignComp(e,people).got;}
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
/* ---------- 揪團時間 ----------
   候選時間 slot：{id, d:"YYYY-MM-DD", t:"HH:MM"（開始，可空）, te:"HH:MM"（結束，選填）, note}
   結束比開始早＝打到隔天（例如 22:00–01:00）
   回覆截止 e.due：毫秒時間戳，0 或沒有＝不設定 */
const HM=/^([01]\d|2[0-3]):([0-5]\d)$/;
export const cleanHM=v=>HM.test(String(v||""))?String(v):"";
export const slotTimeTxt=s=>{const t=cleanHM(s&&s.t),te=cleanHM(s&&s.te);return t?(te&&te!==t?t+"–"+te:t):"";};
export function slotStart(s){if(!s||!/^\d{4}-\d{2}-\d{2}$/.test(s.d||""))return null;const[y,m,d]=s.d.split("-").map(Number),t=cleanHM(s.t);return new Date(y,m-1,d,t?+t.slice(0,2):0,t?+t.slice(3):0);}
export const evDue=e=>{const v=Number(e&&e.due);return Number.isFinite(v)&&v>0?v:0;};
export const dueOver=(e,now=Date.now())=>{const v=evDue(e);return !!v&&now>=v;};
const WK1="日一二三四五六",p2=n=>String(n).padStart(2,"0");
export function dueTxt(ms){const d=new Date(ms);return (d.getMonth()+1)+"/"+d.getDate()+"（"+WK1[d.getDay()]+"）"+p2(d.getHours())+":"+p2(d.getMinutes());}
export function dueLeft(ms,now=Date.now()){const m=Math.floor((ms-now)/60000);if(m<0)return"";if(m<60)return"還有 "+Math.max(1,m)+" 分鐘";const h=Math.floor(m/60);if(h<48)return"還有 "+h+" 小時";return"還有 "+Math.round(h/24)+" 天";}

/* 整個活動要看哪個時間：定案了就看定案的時間，否則看分數最高（最多人能來）的時間 */
export function bestSlot(e,R){
  const slots=e.slots||[];if(!slots.length)return null;
  if(e.status==="fixed"){const f=slots.find(s=>s.id===e.fixed);if(f)return{s:f,...slotTally(R,f.id),fixed:true};}
  let best=null;slots.forEach(s=>{const t={s,...slotTally(R,s.id)};if(!best||t.score>best.score)best=t;});
  return best;
}

/* ---------- 請假 ----------
   away/{uid}.entries：[{from:"YYYY-MM-DD", to:"YYYY-MM-DD", kind:"off"|"maybe"}]，只記到「哪幾天」，沒有幾點
   讀進來時只留日期格式正確的，kind 不認得就當成「可能不在」 */
const AWD=/^\d{4}-\d{2}-\d{2}$/;
export function awayEntries(data){return(Array.isArray(data&&data.entries)?data.entries:[]).filter(e=>e&&typeof e==="object"&&AWD.test(e.from)&&AWD.test(e.to)).map(e=>({from:e.from,to:e.to,kind:e.kind==="off"?"off":"maybe"}));}
/* 某一天的狀態：off（請假）優先於 maybe（可能不在）；沒有就是 "" */
export function awayDay(entries,d){let st="";for(const e of entries||[])if(e.from<=d&&d<=e.to){if(e.kind==="off")return"off";st="maybe";}return st;}
