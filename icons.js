/* 溫馨風格的小圖示（線條風格，跟著文字顏色）：依標題文字自動加在大廳各區塊與功能卡前面 */
const P={
  team:'<circle cx="9" cy="7" r="4"/><path d="M3 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/><path d="M21 21v-2a4 4 0 0 0-3-3.85"/>',
  event:'<path d="M18 8a3 3 0 0 1 0 6"/><path d="M10 8v11a1 1 0 0 1-1 1h-1a1 1 0 0 1-1-1v-5"/><path d="M12 8l4.524-3.77a.9.9 0 0 1 1.476.692v12.156a.9.9 0 0 1-1.476.692L12 14H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1h8"/>',
  cal:'<rect x="4" y="5" width="16" height="16" rx="2"/><path d="M16 3v4M8 3v4M4 11h16"/><path d="M11 15h1v3"/>',
  home:'<path d="M21 12l-9-9-9 9h2v7a2 2 0 0 0 2 2h6"/><path d="M9 21v-6a2 2 0 0 1 2-2h2"/><path d="M18 22l3.35-3.284a2.143 2.143 0 0 0 .005-3.071 2.242 2.242 0 0 0-3.129-.006l-.224.22-.223-.22a2.242 2.242 0 0 0-3.128-.006 2.143 2.143 0 0 0-.006 3.071L18 22z"/>',
  link:'<path d="M9 15l6-6"/><path d="M11 6l.463-.536a5 5 0 0 1 7.071 7.072L18 13"/><path d="M13 18l-.397.534a5.068 5.068 0 0 1-7.127 0 4.972 4.972 0 0 1 0-7.071L6 11"/>',
  shield:'<path d="M12 3a12 12 0 0 0 8.5 3A12 12 0 0 1 12 21 12 12 0 0 1 3.5 6 12 12 0 0 0 12 3"/>',
  check:'<path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="2"/><path d="M9 14l2 2 4-4"/>',
  book:'<path d="M3 19a9 9 0 0 1 9 0a9 9 0 0 1 9 0"/><path d="M3 6a9 9 0 0 1 9 0a9 9 0 0 1 9 0"/><path d="M3 6v13M12 6v13M21 6v13"/>',
  sword:'<path d="M20 4v5l-9 7-4 4-3-3 4-4 7-9z"/><path d="M6.5 11.5l6 6"/>',
  note:'<path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M9 13h6M9 17h4"/>',
  gift:'<rect x="3" y="8" width="18" height="4" rx="1"/><path d="M12 8v13"/><path d="M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7"/><path d="M7.5 8a2.5 2.5 0 0 1 0-5A4.8 8 0 0 1 12 8a4.8 8 0 0 1 4.5-5 2.5 2.5 0 0 1 0 5"/>',
  target:'<circle cx="12" cy="12" r="1"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="9"/>',
  users:'<circle cx="12" cy="7" r="4"/><path d="M6 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/>',
  key:'<circle cx="8" cy="15" r="4"/><path d="M10.85 12.15L19 4M18 5l2 2M15 8l2 2"/>',
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
