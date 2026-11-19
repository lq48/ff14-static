(function(){
  const P='"\'><img src=x onerror="window.__xss=(window.__xss||[]).concat(1)"><svg onload="window.__xss=(window.__xss||[]).concat(2)">';
  const KEYS=new Set(["nick","dcName","charName","server","bio","name","slogan","intro","n","note","title","desc","kind","t","label","mech","ctag","dmg","burst","duty","byName","team","dtype"]);
  const SKIP_PATH=/^memories\//; // 回憶錄的 kind 是規則限定的選項，另外處理
  function walk(o,path){
    if(Array.isArray(o)){o.forEach((v,i)=>{if(typeof v==="object"&&v)walk(v,path);});return;}
    Object.keys(o).forEach(k=>{const v=o[k];
      if(typeof v==="string"&&KEYS.has(k)&&!(SKIP_PATH.test(path)&&k==="kind"))o[k]=v+P;
      else if(v&&typeof v==="object")walk(v,path);});
  }
  const db=window.__MOCK.db;
  Object.keys(db).forEach(p=>walk(db[p],p));
  // 請假：私人理由與公開理由
  (db["away/u3"]||{}).entries&&db["away/u3"].entries.forEach((e,i)=>{e.id="ea"+i;e.label="出差"+P;e.pub=true;});
  db["awayPriv/u3"]={labels:{ea0:"私事"+P}};
  // 推薦網站：網址也試試
  db["links/l9"]={title:"壞連結"+P,url:"javascript:window.__xss=[9]",cat:"其他",desc:P,lang:"其他",status:"approved",by:"u5",byName:"x"+P,createdAt:9};
  // 減傷軸技能名稱
  const L=db["mitSkills/lib"];if(L)Object.values(L.jobs).forEach(j=>j.skills.forEach(s=>{s.name+=P;}));
  window.__XSS_PAYLOAD=P;
})();
