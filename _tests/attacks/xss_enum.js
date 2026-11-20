(function(){
  const P='"\'><img src=x onerror="window.__xss=(window.__xss||[]).concat(1)">';
  // 只保留串接資料用的 ID 欄位，其他所有字串（包含看起來像選項的 src、st、kind、tag、job、日期）全部汙染
  const KEEP=new Set(["id","uid","by","tier","tid","eid","mid","fixed","dc","did","status","k","to_","access"]);
  function walk(o){
    if(Array.isArray(o)){for(let i=0;i<o.length;i++){if(typeof o[i]==="string"){}else if(o[i]&&typeof o[i]==="object")walk(o[i]);}return;}
    Object.keys(o).forEach(k=>{const v=o[k];
      if(typeof v==="string"&&!KEEP.has(k)&&!/^data:image/.test(v))o[k]=v+P;
      else if(v&&typeof v==="object")walk(v);});
  }
  const db=window.__MOCK.db;Object.keys(db).forEach(p=>walk(db[p]));
  // 物件的 key 也可能被拿來組 HTML（例如 bis 的部位、減傷軸的列 ID）：另外加一筆奇怪 key 的資料
  // 數字欄位也可能被改成字串：揪團的回覆截止
  if(db["events/e3"])db["events/e3"].due=P;
  if(db["statics/s1/bis/t1__u1"])db["statics/s1/bis/t1__u1"].final[P]={src:"raid"+P,st:"got"+P};
})();
