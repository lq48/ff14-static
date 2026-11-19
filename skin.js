/* 風格切換：網址加 ?skin=cozy 試用溫馨風格，?skin=classic 換回原本；選過之後會記住，並在右下角顯示切換按鈕 */
(function(){
  var K="skin",v="";
  try{var q=new URLSearchParams(location.search).get("skin");if(q==="cozy"||q==="classic")localStorage.setItem(K,q);v=localStorage.getItem(K)||"";}catch(e){}
  if(v==="cozy")document.documentElement.setAttribute("data-skin","cozy");
  if(!v)return;
  document.addEventListener("DOMContentLoaded",function(){
    var b=document.createElement("button");b.type="button";b.className="skin-toggle";
    var set=function(){var on=document.documentElement.getAttribute("data-skin")==="cozy";b.textContent=on?"換回原本風格":"試試溫馨風格";};
    set();
    b.addEventListener("click",function(){var on=document.documentElement.getAttribute("data-skin")==="cozy";
      if(on)document.documentElement.removeAttribute("data-skin");else document.documentElement.setAttribute("data-skin","cozy");
      try{localStorage.setItem(K,on?"classic":"cozy");}catch(e){}set();});
    document.body.appendChild(b);
  });
})();
