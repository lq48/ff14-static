const M=window.__MOCK||{};
let cur=null;const subs=[];
function mkUser(u){return u&&{uid:u.uid,email:u.email||"",getIdTokenResult:async()=>({claims:u.claims||{}}),getIdToken:async()=>"tok"};}
const A={get currentUser(){return cur;}};
export function getAuth(){return A;}
export function onAuthStateChanged(a,fn){subs.push(fn);setTimeout(()=>fn(cur),30);return()=>{};}
export class GoogleAuthProvider{}
export async function signInWithPopup(){window.__log.push("signInWithPopup");}
export async function signInWithCustomToken(a,t){window.__log.push("signInWithCustomToken:"+t);}
export async function signOut(){window.__log.push("signOut");cur=null;subs.forEach(f=>f(null));}
cur=mkUser(M.user);
