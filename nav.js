/* =====================================================================
   全站共用導覽：桌面版頂部列＋手機版底部導覽＋使用者選單
   用法（每頁一行）：
     import { mountNav } from "./nav.js?v=1";
     mountNav({ page:"events", auth });          // auth 可省略（例如莫古試算）
   大廳另外用 setNavUser() 帶入暱稱，用 setNavActive() 切換目前所在位置。
   這個模組只負責顯示與登出，不會讀寫 Firestore。
   ===================================================================== */
import { icon } from "./icons.js?v=4";
import { OWNER_EMAIL, OWNER_DISCORD_ID } from "./config.js";
const FB_AUTH="https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js"; // 只有傳入 auth 的頁面才會載入

const ITEMS=[
  {k:"lobby", href:"index.html",       ico:"home",  n:"大廳",   full:"大廳"},
  {k:"team",  href:"index.html#teams", ico:"team",  n:"固定團", full:"固定團"},
  {k:"events",href:"events.html",      ico:"event", n:"揪團",   full:"揪團活動"},
  {k:"away",  href:"away.html",        ico:"cal",   n:"請假",   full:"請假日曆"},
  {k:"tools", href:"index.html#tools", ico:"link",  n:"工具",   full:"工具"},
];
const S={page:"",active:"",auth:null,user:null,over:null,open:false,opts:{},bottom:true};
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const store={get(k){try{return localStorage.getItem(k)||"";}catch(e){return"";}},set(k,v){try{v?localStorage.setItem(k,v):localStorage.removeItem(k);}catch(e){}}};
function dcAvatar(dc,av){
  if(!dc)return"https://cdn.discordapp.com/embed/avatars/0.png";
  if(av)return"https://cdn.discordapp.com/avatars/"+dc+"/"+av+".png?size=64";
  let i=0;try{i=Number((BigInt(dc)>>22n)%6n);}catch(_){}return"https://cdn.discordapp.com/embed/avatars/"+i+".png";
}

export function mountNav(opts={}){
  S.opts=opts;S.page=opts.page||"";S.active=opts.active||S.page;S.auth=opts.auth||null;S.bottom=opts.bottom!==false;
  let bar=document.getElementById("sitebar");
  if(!bar){bar=document.createElement("header");bar.id="sitebar";document.body.prepend(bar);}
  bar.className="sitebar";
  if(!document.getElementById("bnav")){const b=document.createElement("nav");b.id="bnav";b.className="bnav";b.setAttribute("aria-label","主要導覽");document.body.appendChild(b);}
  document.body.classList.toggle("has-bnav",S.bottom);
  paint();
  if(S.auth)import(FB_AUTH).then(({onAuthStateChanged})=>{
    onAuthStateChanged(S.auth,async u=>{
      if(!u){S.user=null;paint();return;}
      let c={};try{c=(await u.getIdTokenResult()).claims||{};}catch(_){}
      const owner=!!((u.email&&u.email.toLowerCase()===OWNER_EMAIL.toLowerCase())||c.dc===OWNER_DISCORD_ID);
      S.user={name:c.dcn||u.email||"已登入",avatar:c.dc?dcAvatar(c.dc,c.dca):"",owner};paint();
    });
  }).catch(e=>console.warn("nav auth",e));
  document.addEventListener("click",onDocClick);
  document.addEventListener("keydown",e=>{if(e.key==="Escape"&&S.open){S.open=false;paint();const b=document.getElementById("sbUbtn");if(b)b.focus();}});
}
/* 大廳登入後帶入暱稱與頭像（比 Discord 名稱更像自己） */
export function setNavUser(over){const k=JSON.stringify(over||null);if(k===S.overKey)return;S.overKey=k;S.over=over||null;paint();}
export function setNavActive(k){if(S.active===k)return;S.active=k;paint();}

function navLinks(cls){
  return ITEMS.map(it=>{const cur=it.k===S.active;
    return '<a href="'+it.href+'"'+(cur?' aria-current="page"':'')+' data-navk="'+it.k+'">'+
      (cls==="b"?'<span class="bi">'+icon(it.ico,22)+'</span><span>'+it.n+'</span>':icon(it.ico,18)+'<span>'+it.full+'</span>')+'</a>';}).join("");
}
function userHTML(){
  const u=S.user?{...S.user,...(S.over||{})}:null;
  if(!u)return (!S.auth||S.page==="lobby")?"":'<a class="sb-login" href="index.html">登入</a>';
  const theme=store.get("themePref"),classic=store.get("skinPref")==="classic";
  let h='<button type="button" class="sb-ubtn" id="sbUbtn" aria-expanded="'+S.open+'" aria-controls="sbMenu">'+
    (u.avatar?'<img src="'+esc(u.avatar)+'" alt="">':icon("users",20))+'<span class="nm">'+esc(u.name)+'</span>'+icon("down",16)+'</button>';
  if(S.open){
    h+='<div class="sb-menu" id="sbMenu">'+
      '<div class="mh">'+esc(u.name)+(u.owner?'・總團長':'')+'</div>'+
      '<a href="index.html#profile" data-nav="profile">'+icon("users")+'我的靈魂水晶</a>'+
      '<hr><div class="mh">深淺色</div><div class="sb-seg" role="group" aria-label="深淺色">'+
        [["","跟隨系統"],["light","淺色"],["dark","深色"]].map(([v,n])=>'<button type="button" data-theme-set="'+v+'" aria-pressed="'+(theme===v)+'">'+n+'</button>').join("")+'</div>'+
      '<button type="button" class="mi" data-nav="skin">'+icon("refresh")+(classic?'換成溫馨外觀':'暫時換回舊版外觀')+'</button>'+
      '<hr><button type="button" class="mi" data-nav="logout">'+icon("logout")+'登出</button></div>';
  }
  return h;
}
function paint(){
  const bar=document.getElementById("sitebar");if(!bar)return;
  bar.innerHTML='<div class="sb-in"><a class="sb-brand" href="index.html" data-navk="lobby"><span class="sb-logo">'+icon("home",20)+'</span><span>光之戰士飛地</span></a>'+
    '<nav class="sb-nav" aria-label="主要導覽">'+navLinks("t")+'</nav><div class="sb-user">'+userHTML()+'</div></div>';
  const b=document.getElementById("bnav");if(b)b.innerHTML=S.bottom?navLinks("b"):"";
}
async function onDocClick(e){
  const t=e.target;
  if(t.closest("#sbUbtn")){S.open=!S.open;paint();if(S.open){const f=document.querySelector("#sbMenu a,#sbMenu button");if(f)f.focus();}return;}
  if(S.open&&!t.closest("#sbMenu")){S.open=false;paint();}
  const th=t.closest("[data-theme-set]");
  if(th){const v=th.dataset.themeSet;store.set("themePref",v);
    if(v)document.documentElement.setAttribute("data-theme",v);else document.documentElement.removeAttribute("data-theme");
    paint();const nb=document.querySelector('[data-theme-set="'+v+'"]');if(nb)nb.focus();return;}
  const a=t.closest("[data-nav]");if(!a)return;
  const k=a.dataset.nav;
  if(k==="profile"&&S.opts.onProfile){e.preventDefault();S.open=false;paint();S.opts.onProfile();return;}
  if(k==="skin"){const classic=store.get("skinPref")==="classic";store.set("skinPref",classic?"cozy":"classic");
    if(classic)document.documentElement.setAttribute("data-skin","cozy");else document.documentElement.removeAttribute("data-skin");S.open=false;paint();return;}
  if(k==="logout"&&S.auth){S.open=false;paint();try{const {signOut}=await import(FB_AUTH);await signOut(S.auth);}catch(err){console.error(err);}if(S.opts.onLogout)S.opts.onLogout();}
  /* 大廳內部跳到區塊：同一頁時交給大廳處理，不重新載入 */
}
document.addEventListener("click",e=>{
  const a=e.target.closest("[data-navk]");if(!a||!S.opts.onNavigate)return;
  if(S.opts.onNavigate(a.dataset.navk,a.getAttribute("href"))===true)e.preventDefault();
});
