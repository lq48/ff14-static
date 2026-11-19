/* 外觀設定（放在 <head> 最前面，畫面出現前就套用，避免閃爍）
   - 預設使用溫馨風格（cozy）
   - 網址加 ?skin=classic 可換回舊版外觀，?skin=cozy 換回溫馨；也可以在右上角的使用者選單切換
   - 深淺色：跟隨系統，或在使用者選單指定（存在這台裝置）
   註：舊的試用期設定（localStorage "skin"）不再沿用，所以每個人都會先看到新外觀 */
(function(){
  var d=document.documentElement,skin="",theme="";
  try{
    var q=new URLSearchParams(location.search).get("skin");
    if(q==="cozy"||q==="classic")localStorage.setItem("skinPref",q);
    skin=localStorage.getItem("skinPref")||"";
    theme=localStorage.getItem("themePref")||"";
  }catch(e){}
  if(skin!=="classic")d.setAttribute("data-skin","cozy");
  if(theme==="light"||theme==="dark")d.setAttribute("data-theme",theme);
})();
