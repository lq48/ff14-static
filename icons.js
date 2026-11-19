/* 溫馨風格的小圖示（線條風格，跟著文字顏色）：依標題文字自動加在大廳各區塊與功能卡前面 */
const P={
  team:'<circle cx="9" cy="7" r="4"/><path d="M3 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/><path d="M21 21v-2a4 4 0 0 0-3-3.85"/>',
  event:'<path d="M4 10a2 2 0 0 0-2 2v2a2 2 0 0 0 2 2h3l3 4a1.5 1.5 0 0 0 2.5-1.5L10.5 16"/> <path d="M4 10h5l8-5v14l-8-5H4"/> <path d="M20 9a5 5 0 0 1 0 8"/> <path d="M21 5a9 9 0 0 1 0 2"/>',
  cal:'<rect x="3" y="5" width="18" height="16" rx="3"/> <path d="M7.5 3v4"/> <path d="M16.5 3v4"/> <path d="M3 10h18"/> <path d="M12 18.5s-4-2.4-4-4.7a2 2 0 0 1 4-0.3 2 2 0 0 1 4 0.3c0 2.3-4 4.7-4 4.7Z"/>',
  home:'<path d="M3 11 10 4.5a3 3 0 0 1 4 0L21 11"/> <path d="M5 10v9a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-9"/> <path d="M12 17.5s-3.5-2-3.5-4a1.8 1.8 0 0 1 3.5-.5 1.8 1.8 0 0 1 3.5.5c0 2-3.5 4-3.5 4Z"/>',
  link:'<path d="m10 13.5 4-4"/> <path d="m8.5 16-1.7 1.7a3.5 3.5 0 0 1-5-5l4.5-4.5a3.5 3.5 0 0 1 5 0"/> <path d="m15.5 8 1.7-1.7a3.5 3.5 0 0 1 5 5l-4.5 4.5a3.5 3.5 0 0 1-5 0"/>',
  shield:'<path d="M12 2.5c2.8 2.2 5.5 2.8 8 3.2v6c0 5-3.2 8-8 10.3-4.8-2.3-8-5.3-8-10.3v-6c2.5-.4 5.2-1 8-3.2Z"/> <path d="M12 16.5s-4-2.5-4-5a2 2 0 0 1 4-0.5 2 2 0 0 1 4 0.5c0 2.5-4 5-4 5Z"/>',
  check:'<rect x="4" y="4.5" width="16" height="17" rx="2.5"/> <path d="M9 4.5V3.8A1.8 1.8 0 0 1 10.8 2h2.4A1.8 1.8 0 0 1 15 3.8v0.7"/> <rect x="8" y="3.5" width="8" height="3" rx="1.5"/> <path d="m8 13 3 3 5-5"/>',
  book:'<path d="M12 6c-2.5-1.8-5.6-2-9-1.5v14c3.4-.5 6.5-.3 9 1.5"/> <path d="M12 6c2.5-1.8 5.6-2 9-1.5v14c-3.4-.5-6.5-.3-9 1.5"/> <path d="M12 6v14"/> <path d="M5.5 9c1.5-.1 3 .2 4 0.8"/> <path d="M14.5 9.8c1-.6 2.5-.9 4-.8"/>',
  sword:'<path d="M20 4v5l-9 7-4 4-3-3 4-4 7-9z"/><path d="M6.5 11.5l6 6"/>',
  note:'<path d="M19 9v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h8Z"/> <path d="M13 3v4a2 2 0 0 0 2 2h4"/> <path d="M7 12h8"/> <path d="M7 16h8"/> <path d="M7 8h2"/>',
  gift:'<rect x="3" y="10" width="18" height="11" rx="2"/> <rect x="2" y="7" width="20" height="4" rx="1.5"/> <path d="M12 7v14"/> <path d="M12 7C8 7 5 6 5 3.8A2 2 0 0 1 7 2c2.2 0 4 2.5 5 5Z"/> <path d="M12 7c4 0 7-1 7-3.2A2 2 0 0 0 17 2c-2.2 0-4 2.5-5 5Z"/>',
  target:'<circle cx="12" cy="12" r="9"/> <circle cx="12" cy="12" r="5.5"/> <circle cx="12" cy="12" r="1.5"/> <path d="M16 8 21 3"/> <path d="M18.5 3H21v2.5"/>',
  users:'<circle cx="12" cy="7" r="4"/><path d="M6 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/>',
  key:'<circle cx="8" cy="9" r="5.5"/> <circle cx="8" cy="9" r="1.5"/> <path d="m12 13 8.5 8.5"/> <path d="M17 18.5 19.5 16"/> <path d="m14.5 16 2.5-2.5"/>',
};
/* 標題關鍵字 → 圖示、底色 */
const RULES=[
  [/固定團/,"team","peach"],[/揪團/,"event","butter"],[/請假|行事曆/,"cal","sage"],[/飛地成員|成員/,"home","sky"],
  [/工具|網站|連結/,"link","sage"],[/減傷/,"shield","sky"],[/出席|調查/,"check","sage"],[/攻略/,"book","butter"],
  [/BiS|配裝/,"sword","peach"],[/復盤|紀錄/,"note","sky"],[/莫古|收集|道具/,"gift","butter"],[/目標|進度/,"target","peach"],
  [/權限/,"key","butter"],
];
const svg=k=>'<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+P[k]+'</svg>';
function deco(root){
  root.querySelectorAll(".panel>h2,.panel>.phead>h2,.mod>.t").forEach(h=>{
    if(h.dataset.ico)return;const t=h.textContent||"";const r=RULES.find(([re])=>re.test(t));h.dataset.ico="1";if(!r)return;
    const s=document.createElement("span");s.className="ico ico-"+r[2];s.innerHTML=svg(r[1]);h.prepend(s);
  });
}
export function startIcons(){
  const run=()=>deco(document);run();
  new MutationObserver(run).observe(document.body,{childList:true,subtree:true});
}
