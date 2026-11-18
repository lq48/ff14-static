/* 飛地大廳：請假行事曆近 30 天預覽（可展開／收起） */
import { collection, doc, onSnapshot } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";
import { HOLI, sortIdsBy } from "./away-core.js?v=1";

const DAYS=30,WK="日一二三四五六";
const pad=n=>String(n).padStart(2,"0");
const ymd=d=>d.getFullYear()+"-"+pad(d.getMonth()+1)+"-"+pad(d.getDate());
const parse=s=>{const[a,b,c]=s.split("-").map(Number);return new Date(a,b-1,c);};
const md=s=>{const d=parse(s);return (d.getMonth()+1)+"/"+d.getDate()+"（"+WK[d.getDay()]+"）";};
const esc=s=>String(s==null?"":s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

const CSS=`
.am{--am-off:#5F6B7D;--am-maybe:#E19A2B;--am-we:color-mix(in srgb,var(--line) 40%,transparent);--am-hol:color-mix(in srgb,#E0566C 16%,transparent);--am-holink:#D9485F;--am-good:#2E8B57}
.am-strip{display:grid;grid-template-columns:repeat(${DAYS},minmax(0,1fr));gap:2px;margin:2px 0 4px}
.am-strip .c{border-radius:4px;text-align:center;font-size:11px;line-height:1.15;padding:3px 0;font-variant-numeric:tabular-nums;color:var(--muted);background:var(--am-we);min-width:0}
.am-strip .c.wd{background:transparent;border:1px solid color-mix(in srgb,var(--line) 70%,transparent)}
.am-strip .c.hol{background:var(--am-hol)}
.am-strip .c .dn{display:block;font-size:10px}
.am-strip .c.hol .dn{color:var(--am-holink);font-weight:800}
.am-strip .c b{display:block;font-size:12px;color:var(--am-good)}
.am-strip .c.low b{color:var(--am-off)}
.am-strip .c.mb b{color:var(--am-maybe)}
.am-ml{display:flex;justify-content:space-between;font-size:11.5px;color:var(--muted);margin-bottom:8px}
.am-list{list-style:none;margin:6px 0 0;padding:0;display:flex;flex-direction:column;gap:4px;font-size:14px}
.am-list li{display:flex;flex-wrap:wrap;gap:4px 10px;align-items:baseline}
.am-list .w{font-weight:700}
.am-list .d{font-variant-numeric:tabular-nums;color:var(--muted);font-size:13px}
.am-pill{font-size:11.5px;border-radius:999px;padding:0 7px;font-weight:700}
.am-pill.off{background:var(--am-off);color:#fff}
.am-pill.maybe{border:1px dashed var(--am-maybe);color:var(--am-maybe)}
.am-bar{display:flex;justify-content:space-between;align-items:center;gap:8px;margin-top:10px;flex-wrap:wrap}
.am-gw{overflow-x:auto;border:1px solid var(--line);border-radius:8px;margin-top:4px}
.am-g{border-collapse:separate;border-spacing:0;font-size:12px}
.am-g th,.am-g td{border-bottom:1px solid color-mix(in srgb,var(--line) 60%,transparent);padding:0}
.am-g .nm{position:sticky;left:0;z-index:1;background:var(--surface);text-align:left;font-weight:700;padding:3px 8px;white-space:nowrap;max-width:110px;overflow:hidden;text-overflow:ellipsis;border-right:1px solid var(--line)}
.am-g .nm img{width:18px;height:18px;border-radius:50%;vertical-align:-4px;margin-right:5px}
.am-g .dy{width:22px;min-width:22px;text-align:center;font-weight:500;color:var(--muted);font-size:10.5px;line-height:1.15;padding:2px 0}
.am-g .we{background:var(--am-we)}
.am-g .hol{background:var(--am-hol)}
.am-g thead tr:first-child .hol{color:var(--am-holink);font-weight:800}
.am-g td{height:26px}
.am-g td.off{background:var(--am-off)}
.am-g td.maybe{background:color-mix(in srgb,var(--am-maybe) 16%,transparent) repeating-linear-gradient(135deg,color-mix(in srgb,var(--am-maybe) 45%,transparent) 0 1.5px,transparent 1.5px 6px)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .am{--am-off:#8A96AB}}
:root[data-theme="dark"] .am{--am-off:#8A96AB}
.am-g .ms{border-left:1px solid var(--line)}
.am-g .cn{font-weight:800;color:var(--am-good);font-size:11.5px}
.am-g .cn.low{color:var(--am-off)}
.am-g .cn.mbx{color:var(--am-maybe)}
.am-g tr.st .nm{font-weight:500;font-size:11.5px;color:var(--muted)}
.am-g tr.st:last-child th{border-bottom:1px solid var(--line)}
.am-legend{display:flex;flex-wrap:wrap;gap:12px;font-size:12px;color:var(--muted);margin-top:6px}
.am-sw{display:inline-block;width:12px;height:12px;border-radius:3px;vertical-align:-2px;margin-right:4px}
.am-g .cn small{display:block;font-size:9px;color:var(--am-maybe);font-weight:500}
@media (max-width:640px){.am-strip .c .dn{font-size:9px}.am-strip .c b{font-size:11px}}
`;

export function initAwayMini({db,getCtx}){
  if(!document.getElementById("amCss")){const st=document.createElement("style");st.id="amCss";st.textContent=CSS;document.head.appendChild(st);}
  let cfg={access:{},proxies:{}},away={},subs={},canList=false,nDays=30;
  const sub=(k,ref,fn,err)=>{if(subs[k])return;subs[k]=onSnapshot(ref,fn,err||(e=>console.warn("awayMini",k,e&&e.code)));};
  const unsub=k=>{if(subs[k]){subs[k]();delete subs[k];}};

  function access(){
    const {me,isOwner}=getCtx();if(!me)return;
    const a=(cfg.access||{})[me.uid]||"";canList=isOwner||a==="view"||a==="lead";
    if(canList)sub("all",collection(db,"away"),s=>{away={};s.forEach(d=>{away[d.id]=d.data();});paint();},()=>{canList=false;unsub("all");access();paint();});
    else{unsub("all");mine().forEach(id=>sub("u/"+id,doc(db,"away",id),s=>{if(s.exists())away[id]=s.data();else delete away[id];paint();},()=>{}));}
  }
  function mine(){const {me,isOwner,users}=getCtx();if(!me)return[];
    const P=cfg.proxies||{};return Object.keys(users).filter(t=>t===me.uid||isOwner||(P[t]||{})[me.uid]).concat(me.uid);}
  sub("cfg",doc(db,"awayCfg","main"),s=>{cfg=s.exists()?s.data():{};cfg.access=cfg.access||{};cfg.proxies=cfg.proxies||{};access();paint();},()=>{access();paint();});

  const entriesOf=u=>((away[u]||{}).entries)||[];
  function dayState(u,d){let st="";entriesOf(u).forEach(e=>{if(e.from<=d&&d<=e.to){if(e.kind==="off")st="off";else if(!st)st="maybe";}});return st;}
  function rowIds(){
    const {me,users,mem}=getCtx();let ids=Object.keys(users);
    let sel=[];try{const f=JSON.parse(localStorage.getItem("awayFilter")||"null");sel=(f&&f.sel)||[];}catch(e){}
    sel=sel.filter(t=>mem[t]);
    if(canList&&sel.length)ids=ids.filter(id=>sel.some(t=>mem[t][id]&&mem[t][id].status==="active"));
    if(!canList){const m=new Set(mine());ids=ids.filter(id=>m.has(id));}
    return {ids:sortIdsBy(users,cfg,ids),sel};
  }

  function paint(){draw();
    // 依畫面寬度調整天數，讓表格剛好填滿不留白
    for(let k=0;k<3;k++){const gw=document.querySelector("#awayMini .am-gw"),tb=gw&&gw.querySelector("table"),c=tb&&tb.querySelector("thead th.dy");if(!c)return;
      const cw=c.getBoundingClientRect().width||22,diff=gw.clientWidth-tb.getBoundingClientRect().width,add=Math.floor(diff/cw);
      const n=Math.max(14,Math.min(184,nDays+add));if(n===nDays)break;nDays=n;draw();}}
  function draw(){
    const el=document.getElementById("awayMini");if(!el)return;
    const {me,users,statics,mem,avatarUrl,nameOf}=getCtx();if(!me)return;
    const t=new Date();t.setHours(0,0,0,0);const D=[];for(let i=0;i<nDays;i++){const x=new Date(t);x.setDate(t.getDate()+i);D.push(ymd(x));}
    const {ids,sel}=rowIds(),N=ids.length,first=D[0],last=D[D.length-1];
        const cls=d=>{const x=parse(d);return HOLI[d]?" hol":(x.getDay()===0||x.getDay()===6)?" we":"";};
    let h='';
    if(!canList)h+='<p class="muted" style="margin:0 0 8px;font-size:13px">你目前只看得到自己'+(mine().length>2?'和你負責代填的人':'')+'的請假。</p>';
    else if(sel.length)h+='<p class="muted" style="margin:0 0 8px;font-size:13px">只看：'+esc(sel.map(t=>(statics.find(s=>s.id===t)||{}).name||"").filter(Boolean).join("、"))+'（在行事曆頁面可以改）</p>';
      let tb='<div class="am-gw"><table class="am-g"><thead><tr><th class="nm" style="font-weight:500;color:var(--muted)">成員（'+N+'）</th>'+
        D.map((d,i)=>{const x=parse(d);return '<th class="dy'+cls(d)+(x.getDate()===1&&i?" ms":"")+'" title="'+esc(md(d)+(HOLI[d]?" "+HOLI[d]:""))+'">'+(x.getDate()===1||i===0?(x.getMonth()+1)+'/':'')+x.getDate()+'<br>'+WK[x.getDay()]+'</th>';}).join("")+'</tr>';
      // 每個固定團一列：全員到齊打勾，有人不在就顯示缺幾人
      const shown=new Set(ids);
      statics.forEach(st=>{const ms=Object.keys(mem[st.id]||{}).filter(id=>mem[st.id][id].status==="active"&&shown.has(id));if(!ms.length)return;
        tb+='<tr class="st"><th class="nm" title="'+esc(st.name)+'">'+esc(st.name)+'</th>'+D.map((d,i)=>{const x=parse(d);let off=[],mb=[];ms.forEach(id=>{const s=dayState(id,d);if(s==="off")off.push(id);else if(s==="maybe")mb.push(id);});
          const tip=md(d)+(HOLI[d]?" "+HOLI[d]:"")+"："+(off.length||mb.length?(off.length?"請假 "+off.map(id=>nameOf(users[id])).join("、"):"")+(mb.length?(off.length?"；":"")+"可能不在 "+mb.map(id=>nameOf(users[id])).join("、"):""):"全員到齊（"+ms.length+" 人）");
          return '<th class="dy cn'+(off.length?" low":mb.length?" mbx":"")+cls(d)+(x.getDate()===1&&i?" ms":"")+'" title="'+esc(tip)+'">'+(off.length?'−'+off.length:mb.length?'?':'✓')+'</th>';}).join("")+'</tr>';});
      tb+='</thead><tbody>';
      ids.forEach(id=>{const u=users[id];tb+='<tr><th class="nm" scope="row"><img src="'+esc(avatarUrl(u))+'" alt="" loading="lazy">'+esc(nameOf(u))+'</th>'+
        D.map((d,i)=>{const s=dayState(id,d),x=parse(d);return '<td class="'+(s||cls(d).trim())+(x.getDate()===1&&i?" ms":"")+'" title="'+esc(nameOf(u)+" "+md(d)+(s?"："+(s==="off"?"請假":"可能不在"):""))+'"></td>';}).join("")+'</tr>';});
      h+=tb+'</tbody></table></div>';
    h+='<div class="am-legend"><span><span class="am-sw" style="background:var(--am-off)"></span>請假</span><span><span class="am-sw" style="background:color-mix(in srgb,var(--am-maybe) 16%,transparent) repeating-linear-gradient(135deg,color-mix(in srgb,var(--am-maybe) 45%,transparent) 0 1.5px,transparent 1.5px 6px);border:1px solid var(--am-maybe)"></span>可能不在</span><span><span class="am-sw" style="background:var(--am-hol)"></span>國定假日</span><span>固定團那列：✓ 全員到齊、−2 是有 2 人請假、? 是有人可能不在（滑鼠移上去看是誰）</span></div>';
    h+='<p class="muted" style="margin:6px 0 0;font-size:12.5px;text-align:right">顯示到 '+md(last)+'，要請假或看更久，請按右上「打開行事曆」</p>';
    const gw=el.querySelector(".am-gw"),sx=gw?gw.scrollLeft:0;
    el.innerHTML=h;const ng=el.querySelector(".am-gw");if(ng)ng.scrollLeft=sx;
  }
  let rt=null;const onR=()=>{clearTimeout(rt);rt=setTimeout(()=>{nDays=30;paint();},150);};window.addEventListener("resize",onR);
  return {paint,stop(){Object.keys(subs).forEach(unsub);window.removeEventListener("resize",onR);}};
}
