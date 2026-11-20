(function(){
  const P='x"\'><img src=x onerror="window.__xss=(window.__xss||[]).concat(3)">';
  const db=window.__MOCK.db,clone=o=>JSON.parse(JSON.stringify(o));
  const add=(from,to)=>{if(db[from])db[to]=clone(db[from]);};
  add("events/e1","events/"+P);add("events/e1/rsvp/u2","events/"+P+"/rsvp/u2");
  add("links/l1","links/"+P);
  add("memories/m1","memories/"+P);
  if(db["memories/"+P])db["memories/"+P].imgs=[P];db["memoryImgs/"+P]=clone(db["memoryImgs/i1"]||{});
  add("statics/s1/bisTiers/t1","statics/s1/bisTiers/"+P);
  if(db["statics/s1/bisTiers/"+P])db["statics/s1/bisTiers/"+P].createdAt=99;
  add("statics/s1/bis/t1__u1","statics/s1/bis/"+P+"__u1");
  add("statics/s1/bis/t1__u1","statics/s1/bis/t1__"+P);
  add("surveys/sv1","surveys/"+P);
})();
