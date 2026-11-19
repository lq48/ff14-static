const M=window.__MOCK||{};const DB=M.db||{};
window.__writes=[];
const segs=p=>p.split("/");
function mkRef(path){const s=segs(path);return {path,id:s[s.length-1],get parent(){return s.length>1?mkColRef(s.slice(0,-1).join("/")):null;},type:"doc"};}
function mkColRef(path){const s=segs(path);return {path,id:s[s.length-1],get parent(){return s.length>1?mkRef(s.slice(0,-1).join("/")):null;},type:"col"};}
export function getFirestore(){return {};}
export function collection(db,...p){return mkColRef(p.join("/"));}
export function collectionGroup(db,id){return {type:"group",id};}
export function doc(a,...p){if(a&&a.type==="col"){return mkRef(a.path+"/"+(p[0]||("auto"+Math.random().toString(36).slice(2,8))));}return mkRef(p.join("/"));}
export function where(f,op,v){return {f,op,v};}
export function query(ref,...w){return {...ref,where:w.filter(x=>x&&x.op),ob:w.filter(x=>x&&x.ob).map(x=>x.ob),lim:(w.find(x=>x&&x.lim)||{}).lim};}
export function orderBy(f,dir){return {ob:[f,dir||"asc"]};} export function limit(n){return {lim:n};}
function snapDoc(path){const d=DB[path];return {id:segs(path).pop(),ref:mkRef(path),metadata:{hasPendingWrites:false},exists:()=>d!==undefined,data:()=>d===undefined?undefined:JSON.parse(JSON.stringify(d))};}
function listFor(ref){
  let paths=Object.keys(DB);
  if(ref.type==="group")paths=paths.filter(p=>{const s=segs(p);return s.length>=2&&s[s.length-2]===ref.id;});
  else paths=paths.filter(p=>{const s=segs(p);return s.slice(0,-1).join("/")===ref.path;});
  let docs=paths.map(snapDoc);
  (ref.where||[]).forEach(w=>{docs=docs.filter(d=>{const v=d.data()[w.f];return w.op==="=="?v===w.v:true;});});
  (ref.ob||[]).forEach(([f,dir])=>{docs=docs.filter(d=>d.data()[f]!==undefined);docs.sort((a,b)=>{const x=a.data()[f],y=b.data()[f];const c=x<y?-1:x>y?1:0;return dir==="desc"?-c:c;});});
  if(ref.lim)docs=docs.slice(0,ref.lim);
  return {docs,size:docs.length,empty:!docs.length,forEach:f=>docs.forEach(f),docChanges:()=>docs.map(d=>({type:"added",doc:d}))};
}
const LIS=[];
function fire(ref,next){if((M.deny||[]).some(x=>(ref.path||ref.id||"").startsWith(x)))return;try{next(ref.type==="doc"?snapDoc(ref.path):listFor(ref));}catch(e){console.error("mock",e);}}
export function onSnapshot(ref,next,err){
  const L={ref,next};LIS.push(L);
  setTimeout(()=>{try{
    if((M.deny||[]).some(x=>(ref.path||ref.id||"").startsWith(x))){err&&err({code:"permission-denied"});return;}
    next(ref.type==="doc"?snapDoc(ref.path):listFor(ref));}catch(e){console.error("mock",e);}},20+Math.random()*40);
  return()=>{const i=LIS.indexOf(L);if(i>=0)LIS.splice(i,1);};
}
function setPath(o,k,v){const ks=k.split(".");let c=o;for(let i=0;i<ks.length-1;i++)c=c[ks[i]]=c[ks[i]]||{};c[ks[ks.length-1]]=v;}
function apply(op,path,data){
  if(M.failWrites){const e=new Error("mock fail");e.code=M.failWrites;throw e;}
  if(op==="setMerge"){DB[path]=deepMerge(DB[path]?JSON.parse(JSON.stringify(DB[path])):{},data);}
  else if(op==="setDoc"||op==="batch.set")DB[path]=JSON.parse(JSON.stringify(data));
  else if(op==="updateDoc"||op==="batch.update"){const d=DB[path]?JSON.parse(JSON.stringify(DB[path])):{};Object.entries(data).forEach(([k,v])=>setPath(d,k,v));DB[path]=d;}
  else if(op==="deleteDoc"||op==="batch.delete")delete DB[path];
  else if(op==="addDoc")DB[path]=JSON.parse(JSON.stringify(data));
  setTimeout(()=>LIS.slice().forEach(L=>fire(L.ref,L.next)),15);
}
export async function getDocs(ref){return listFor(ref);}
export async function getDoc(ref){return snapDoc(ref.path);}
const DEL={__del:1};export function deleteFieldX(){return DEL;}
function deepMerge(a,b){Object.entries(b).forEach(([k,v])=>{if(v&&v.__del){delete a[k];return;}if(v&&typeof v==="object"&&!Array.isArray(v)&&a[k]&&typeof a[k]==="object"&&!Array.isArray(a[k]))deepMerge(a[k],v);else a[k]=JSON.parse(JSON.stringify(v));});return a;}
const W=(op)=>async(ref,data,opt)=>{if(op==="setDoc"&&opt&&opt.merge)op="setMerge";await new Promise(r=>setTimeout(r,M.writeDelay||30));let path=ref.path;if(op==="addDoc")path=ref.path+"/new"+Math.random().toString(36).slice(2,6);
  window.__writes.push({op,path,data,prev:DB[path]?JSON.parse(JSON.stringify(DB[path])):null,uid:(M.user||{}).uid||null});apply(op,path,data);return op==="addDoc"?mkRef(path):undefined;};
export const setDoc=W("setDoc"),updateDoc=W("updateDoc"),deleteDoc=W("deleteDoc"),addDoc=W("addDoc");
export function writeBatch(){const ops=[];return {set:(r,d)=>ops.push({op:"batch.set",path:r.path,data:d}),update:(r,d)=>ops.push({op:"batch.update",path:r.path,data:d}),delete:r=>ops.push({op:"batch.delete",path:r.path}),commit:async()=>{window.__writes.push(...ops);ops.forEach(o=>apply(o.op,o.path,o.data));}};}
export function serverTimestamp(){return Date.now();}
export function arrayUnion(...a){return a;} export function arrayRemove(...a){return a;} export function deleteField(){return {__del:1};}
