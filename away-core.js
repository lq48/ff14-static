/* 請假行事曆共用資料：away.html 和大廳預覽都用這份 */

/* 國定假日（行政院人事行政總處 115、116 年政府行政機關辦公日曆表；含補假） */
export const HOLI={"2026-12-25":"行憲紀念日",
"2027-01-01":"元旦","2027-02-04":"小年夜","2027-02-05":"除夕","2027-02-06":"春節","2027-02-07":"春節","2027-02-08":"春節","2027-02-09":"春節補假","2027-02-10":"春節補假",
"2027-02-28":"和平紀念日","2027-03-01":"和平紀念日補假","2027-04-04":"兒童節","2027-04-05":"清明節","2027-04-06":"兒童節補假","2027-04-30":"勞動節補假","2027-05-01":"勞動節",
"2027-06-09":"端午節","2027-09-15":"中秋節","2027-09-28":"教師節","2027-10-10":"國慶日","2027-10-11":"國慶日補假","2027-10-25":"臺灣光復暨金門古寧頭大捷紀念日",
"2027-12-24":"行憲紀念日補假","2027-12-25":"行憲紀念日","2027-12-31":"元旦補假（2028 年）"};

/* 設定裡還沒存過順序時，用名字對照的預設順序 */
export const DEFAULT_ORDER=["Satoru","Paku","Jman","草八刀","山壯","Cirtus","33","來來","楓之旋律","飛雷虛","Sealcy"];

const nm=u=>u?(u.nick||u.dcName||"未命名"):"未知成員";
export function orderList(users,cfg){
  if(cfg&&Array.isArray(cfg.order)&&cfg.order.length)return cfg.order;
  const out=[];
  DEFAULT_ORDER.forEach(n=>{const k=n.toLowerCase();
    const id=Object.keys(users).find(i=>!out.includes(i)&&[users[i].nick,users[i].dcName].some(v=>v&&String(v).trim().toLowerCase()===k));
    if(id)out.push(id);});
  return out;
}
export function sortIdsBy(users,cfg,ids){
  const o=orderList(users,cfg),ix=id=>{const i=o.indexOf(id);return i<0?1e9:i;};
  return ids.slice().sort((x,y)=>ix(x)-ix(y)||nm(users[x]).localeCompare(nm(users[y]),"zh-Hant"));
}

/* 揪團活動同步到行事曆：已定案的放確定日期，調查中的放候選日期 */
export function eventMarks(events){
  const m={};
  Object.entries(events||{}).forEach(([id,e])=>{
    if(!e||e.status==="closed")return;
    const slots=e.slots||[];
    const list=e.status==="fixed"?slots.filter(s=>s.id===e.fixed):slots;
    list.forEach(s=>{if(!s.d)return;(m[s.d]=m[s.d]||[]).push({id,title:e.title||"",t:s.t||"",fixed:e.status==="fixed"});});
  });
  Object.values(m).forEach(a=>a.sort((x,y)=>(y.fixed-x.fixed)||x.t.localeCompare(y.t)));
  return m;
}
export const markTip=a=>a.map(x=>(x.fixed?"【已定案】":"【調查中】")+(x.t?x.t+" ":"")+x.title).join("\n");
