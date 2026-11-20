(function(){
const sc=(new URLSearchParams(location.search).get("mock"))||localStorage.getItem("mockScenario")||"member";
localStorage.setItem("mockScenario",sc);
const pd=n=>String(n).padStart(2,"0"),day=k=>{const d=new Date();d.setDate(d.getDate()+k);return d.getFullYear()+"-"+pd(d.getMonth()+1)+"-"+pd(d.getDate());};
const now=Date.now();
const U={u1:{nick:"飛雷虛",dc:"390511952625008640",job:"SCH",charName:"Hikari Lei",server:"伊弗利特",bio:"這次一定要過 P5！"},
 u2:{nick:"Satoru",dc:"886243755051601921",job:"PLD",charName:"Satoru Gojo",server:"伊弗利特"},
 u3:{nick:"諾爾",dc:"867669258992222208",job:"WAR",server:"伊弗利特"},u4:{nick:"楓之旋律",dc:"488186522663649280",job:"WHM",server:"伊弗利特"},
 u5:{nick:"Jman",dc:"517588902006095883",job:"SAM",server:"迦樓羅"},u6:{nick:"草八刀",dc:"693797650532663326",job:"DNC",server:"伊弗利特"},
 u7:{nick:"來來",dc:"687696892372844623",job:"PCT",server:"伊弗利特"},u8:{nick:"Paku",dc:"1243145228962103317",job:"VPR",server:"伊弗利特"},
 u9:{nick:"山壯",dc:"513206089303719936",job:"GNB",server:"伊弗利特"}};
const db={};
const full=sc==="member"||sc==="owner"||sc==="nosurvey"||sc==="plain";
Object.entries(U).forEach(([k,v])=>db["users/"+k]={...v,createdAt:1});
if(sc==="empty"){["u2","u3"].forEach(k=>{});}
if(full||sc==="empty"){
 db["statics/s1"]={name:"週三零式團",slogan:"穩穩打，一起畢業",createdAt:1,leaders:sc==="member"?{u1:{members:true,info:false,modules:false,survey:true}}:{},
   modules:{bis:"all",mit:"all",guide:"owner",review:"owner"},targets:[{n:"M5S",t:"savage",main:true,done:true},{n:"M6S",t:"savage"},{n:"M7S",t:"savage"},{n:"M8S",t:"savage"}],
   roles:{MT:"u2",ST:"u3",H1:"u1",H2:"u4",D1:"u5",D2:"u8",D3:"u6",D4:"u7"}};
 db["statics/s2"]={name:"絕伊甸挑戰團",createdAt:2,leaders:{},modules:{},targets:[{n:"絕伊甸",t:"ultimate",main:true}]};
 const act=sc==="empty"?["u2","u3","u4"]:["u1","u2","u3","u4","u5","u6","u7","u8"];
 act.forEach(k=>db["statics/s1/members/"+k]={status:"active",perms:{bis:"own",mit:"view"}});
 db["statics/s1/members/u9"]={status:"pending",note:"我是坦"};
 ["u2","u9"].forEach(k=>db["statics/s2/members/"+k]={status:"active"});
}
if(full){
 db["events/e1"]={title:"絕伊甸 練習",kind:"高難本",status:"fixed",fixed:"x1",slots:[{id:"x1",d:day(1),t:"21:00"},{id:"x2",d:day(2),t:"21:00"}],size:8,minSize:8,by:"u2",createdAt:now};
 db["events/e1/rsvp/u2"]={by:"u2",go:"y",slots:{x1:"y"}};db["events/e1/rsvp/u3"]={by:"u3",go:"y",slots:{x1:"y"}};db["events/e1/rsvp/u1"]={by:"u1",go:"y",slots:{x1:"m"}};
 db["events/e1/rsvp/u5"]={by:"u5",go:"m",slots:{x1:"m"}};
 db["events/e2"]={title:"週末挖寶團（一起開藏寶圖、順便聊天）",kind:"藏寶圖",status:"open",fixed:"",slots:[{id:"y1",d:day(3),t:"22:00"},{id:"y2",d:day(4),t:"22:00"}],size:8,minSize:4,by:"u3",createdAt:now};
 db["events/e2/rsvp/u3"]={by:"u3",go:"y",slots:{y1:"y"}};
 /* 有職能需求的揪團：多數人填了好幾個職業，用來檢查「依志願排位」 */
 db["events/e3"]={title:"幻 青龍初見團",kind:"高難度",status:"open",fixed:"",slots:[{id:"z1",d:day(2),t:"14:00",te:"17:00"},{id:"z2",d:day(2),t:"20:00"}],size:8,minSize:8,roles:true,t:2,h:2,d:4,due:now+5*3600e3,by:"u2",createdAt:now-1000};
 /* 回覆已經截止的揪團（發起人 Satoru） */
 db["events/e4"]={title:"週末夜跑團",kind:"一般副本",status:"open",fixed:"",slots:[{id:"w1",d:day(3),t:"22:00",te:"01:00"}],size:4,minSize:4,due:now-3600e3,by:"u2",createdAt:now-2000};
 db["events/e4/rsvp/u2"]={by:"u2",go:"y",slots:{w1:"y"}};
 [["u2",["SCH"]],["u9",["MNK","DRK","AST"]],["u3",["DRK","PLD","AST"]],["u8",["RDM","BLM"]],["u4",["AST","VPR"]]].forEach(([u,j])=>db["events/e3/rsvp/"+u]={by:u,go:"y",jobs:j,slots:{z1:"y"}});
 const ds=[0,1,2,3,4,5,6].map(day);
 db["surveys/sv1"]={team:"週三零式團",tid:"s1",title:"12 月第一週",dates:ds,holidays:[],note:"",closed:false,createdAt:now,
   members:[{k:"a",n:"飛雷虛",did:"390511952625008640"},{k:"b",n:"Satoru",did:"886243755051601921"},{k:"c",n:"諾爾",did:"867669258992222208"},{k:"d",n:"Jman",did:"517588902006095883"},{k:"e",n:"小明"}],memberKeys:["a","b","c","d","e"],
   events:[{d:day(2),a:40,b:46,label:"M6S 開荒"},{d:day(5),a:41,b:46,label:"M6S 複習＋M7S 看機制"}]};
 db["surveys/sv1/responses/b"]={slots:{[day(1)]:[40,41,42]}};
 db["away/u3"]={entries:[{from:day(2),to:day(2),kind:"off"}]};db["away/u4"]={entries:[{from:day(5),to:day(6),kind:"maybe"}]};
 db["away/u1"]={entries:[{from:day(0),to:day(0),kind:"off"}]};
 /* Satoru 請假當天卻勾了時間：出席調查的「和請假衝突？」 */
 db["away/u2"]={entries:[{from:day(1),to:day(1),kind:"off"}]};
 db["awayCfg/main"]={access:{u1:"view"},proxies:{}};
 db["links/l1"]={title:"FFLogs",url:"https://www.fflogs.com/",cat:"戰鬥與排行",desc:"上傳戰鬥紀錄，看傷害、死因和排名",lang:"英文",status:"approved",pinned:true,by:"u2",byName:"Satoru",createdAt:1};
 db["links/l2"]={title:"繁中工具箱",url:"https://xivtc.com/",cat:"資料查詢",desc:"繁中服玩家的綜合工具網站",lang:"繁中",status:"approved",by:"u2",byName:"Satoru",createdAt:2};
 db["links/l3"]={title:"魚糕",url:"https://fish.ffmomola.com/",cat:"生活職業",desc:"釣魚好幫手",lang:"簡中",status:"pending",by:"u5",byName:"Jman",createdAt:3};
 db["mitDuties/d1"]={name:"M6S",level:100,slots:["MT","ST","H1","H2","D1","D2","D3","D4"],createdAt:1,stages:[{id:"st1",name:"一王",rows:[
   {id:"r0",kind:"head",mech:"開場"},
   {id:"r1",t:"0:12",mech:"全體 AOE A",tag:"全體AOE",hits:[{dtype:"magic",dmg:"8萬"}]},
   {id:"r2",t:"0:30",mech:"死刑 B",tag:"死刑",hits:[{dtype:"phys",dmg:"20萬"}]},
   {id:"r3",mech:"分攤 C",tag:"分攤",hits:[]},
   {id:"r4",t:"1:10",mech:"全體 AOE D",tag:"全體AOE",hits:[]},
   {id:"r5",t:"1:40",mech:"全體 AOE E",hits:[]}]},{id:"st2",name:"二王",rows:[]}]};
 const T1="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAoHBwgHBgoICAgLCgoLDhgQDg0NDh0VFhEYIx8lJCIfIiEmKzcvJik0KSEiMEExNDk7Pj4+JS5ESUM8SDc9Pjv/2wBDAQoLCw4NDhwQEBw7KCIoOzs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozv/wAARCAAwAEADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwC9RRRXin1QUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAH/2Q==",T2="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAoHBwgHBgoICAgLCgoLDhgQDg0NDh0VFhEYIx8lJCIfIiEmKzcvJik0KSEiMEExNDk7Pj4+JS5ESUM8SDc9Pjv/2wBDAQoLCw4NDhwQEBw7KCIoOzs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozv/wAARCAAwAEADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwB9FFFe8eOFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQB//2Q==",BIG="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAoHBwgHBgoICAgLCgoLDhgQDg0NDh0VFhEYIx8lJCIfIiEmKzcvJik0KSEiMEExNDk7Pj4+JS5ESUM8SDc9Pjv/2wBDAQoLCw4NDhwQEBw7KCIoOzs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozs7Ozv/wAARCAEsAZADASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwDWooorzzywooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigD/9k=";
 db["memories/m1"]={title:"M5S 首通！",date:"2026-10-30",kind:"first",desc:"打了三週終於過了，最後一下大家都在叫。",tid:"s1",eid:"",duty:"零式 M5S",members:["u1","u2","u3","u4"],note:"謝謝大家一直沒放棄！",thumb:T1,imgs:["i1","i2"],by:"u1",createdAt:1,updatedAt:1};
 db["memoryImgs/i1"]={mid:"m1",data:BIG,w:400,h:300,by:"u1",createdAt:1};db["memoryImgs/i2"]={mid:"m1",data:T2,w:64,h:48,by:"u1",createdAt:1};
 db["memories/m2"]={title:"萬聖節大合照",date:"2026-10-31",kind:"festival",desc:"大家都換上了奇怪的衣服。",tid:"",eid:"",duty:"",members:["u1","u5","u6"],note:"",thumb:T2,imgs:[],by:"u2",createdAt:2,updatedAt:2};
 db["memories/m3"]={title:"週末挖寶團",date:"2026-11-15",kind:"gather",desc:"",tid:"",eid:"e2",duty:"",members:["u3"],note:"",thumb:"",imgs:[],by:"u3",createdAt:3,updatedAt:3};
 db["memories/m4"]={title:"M6S 開荒第一晚",date:"2026-11-12",kind:"prog",desc:"一王之後的機制太多了",tid:"s1",eid:"",duty:"",members:["u1","u2"],note:"",thumb:"",imgs:[],by:"u2",createdAt:4,updatedAt:4};
 db["mitSkills/lib"]={jobs:{SCH:{skills:[{id:"k1",name:"野戰治療陣",cd:120,dur:20,minLv:1},{id:"k2",name:"展開戰術",cd:90,dur:15,minLv:1}]},
   PLD:{skills:[{id:"p1",name:"聖盾陣",cd:5,dur:8,minLv:1},{id:"p2",name:"神聖領域",cd:420,dur:10,minLv:1}]},WAR:{skills:[{id:"w1",name:"戰慄",cd:60,dur:10,minLv:1}]},WHM:{skills:[{id:"h1",name:"節制",cd:120,dur:20,minLv:1}]}}};
 db["statics/s1/mit/d1"]={comp:{},rows:{r1:{note:"大家集合在中間",burst:"120",pot:true},r5:{lb:"H1"}}};
 db["statics/s1/mit/d1/slots/H1"]={a:{r1:["k1"],r4:["k1"],r3:["k2"]},o:{r3:{k2:3}},tg:{}};
 db["statics/s1/mit/d1/slots/MT"]={a:{r2:["p1","p2"]},o:{},tg:{}};
 db["statics/s1/mit/d1/slots/H2"]={a:{r1:["h1"]},o:{},tg:{}};
 db["statics/s1/bisTiers/t1"]={name:"次重量級",floors:["M5S","M6S","M7S","M8S"],drops:{f0:["ears","neck","wrists","ring"],f1:["head","hands","feet","matAcc"],f2:["head","hands","feet","legs","matArmor","matWeapon"],f3:["body","weapon","c:mount1"]},
   mats:{matWeapon:"武器強化素材",matArmor:"防具強化素材",matAcc:"飾品強化素材"},colls:[{id:"mount1",n:"飛梭C9"}],kw:{raid:"天選冠軍",aug:"改良型",tome:"王國傳奇"},confirmed:true,createdAt:1};
 const R=(src,st,aug)=>({src,st,aug:!!aug,name:""});
 db["statics/s1/bis/t1__u1"]={tier:"t1",uid:"u1",coll:{},links:{},
   final:{weapon:R("raid","got"),head:R("raid","none"),body:R("raid","got"),hands:R("tome","got",1),legs:R("tome","aug",1),feet:R("raid","none"),ears:R("tome","none",1),neck:R("raid","got"),wrists:R("raid","got"),ring1:R("raid","none"),ring2:R("tome","aug",1)},
   prog:{weapon:R("tome","got"),head:R("tome","got"),body:R("tome","got"),hands:R("tome","got"),legs:R("tome","got"),feet:R("tome","got"),ears:R("tome","got"),neck:R("tome","got"),wrists:R("tome","got"),ring1:R("tome","got"),ring2:R("tome","got")}};
 db["statics/s1/bis/t1__u3"]={tier:"t1",uid:"u3",coll:{},links:{},final:{weapon:R("raid","got"),head:R("raid","none")},prog:{}};
}
const users={member:{uid:"u1",claims:{dc:"390511952625008640",dcn:"飛雷虛",dca:""}},owner:{uid:"u2",claims:{dc:"886243755051601921",dcn:"Satoru",dca:""}},
  empty:{uid:"u9",claims:{dc:"513206089303719936",dcn:"山壯",dca:""}},google:{uid:"g1",email:"someone@gmail.com",claims:{}},plain:{uid:"u5",claims:{dc:"517588902006095883",dcn:"Jman",dca:""}},nosurvey:{uid:"u1",claims:{dc:"390511952625008640",dcn:"飛雷虛",dca:""}},denied:{uid:"u1",claims:{dc:"390511952625008640",dcn:"飛雷虛",dca:""}},signedout:null};
window.__log=[];
window.__MOCK={user:users[sc]||null,db,failWrites:localStorage.getItem("mockFail")||"",deny:sc==="denied"?["users"]:sc==="nosurvey"?["surveys"]:localStorage.getItem("mockDenyMem")?["memories","memoryImgs"]:[]};
})();
