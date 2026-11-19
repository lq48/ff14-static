/* =====================================================================
   照片處理：在瀏覽器裡壓縮成 WebP（不支援時用 JPEG），再存進 Firestore
   做法與減傷軸站位圖相同；上限要和 firestore.rules 的 memoryImgs 一致（≤ 950000 字元）
   ===================================================================== */
export const PHOTO_MAX_CHARS=700000;   // 大圖：約 500KB
export const THUMB_MAX_CHARS=58000;    // 縮圖：規則上限 60000
const load=src=>new Promise((res,rej)=>{const i=new Image();i.onload=()=>res(i);i.onerror=()=>rej(new Error("圖片讀取失敗"));i.src=src;});
function encode(img,maxSide,limit,q0){
  let scale=Math.min(1,maxSide/Math.max(img.width,img.height)),q=q0,out="",w=0,h=0;
  for(let i=0;i<10;i++){
    w=Math.max(1,Math.round(img.width*scale));h=Math.max(1,Math.round(img.height*scale));
    const c=document.createElement("canvas");c.width=w;c.height=h;const x=c.getContext("2d");
    x.fillStyle="#FFFFFF";x.fillRect(0,0,w,h);x.drawImage(img,0,0,w,h);
    out=c.toDataURL("image/webp",q);if(!out.startsWith("data:image/webp"))out=c.toDataURL("image/jpeg",q);
    if(out.length<=limit)break;
    if(q>.56)q-=.1;else scale*=.82;
  }
  if(out.length>limit)throw new Error("照片太大，壓縮後仍超過上限");
  return{data:out,w,h};
}
/* 使用者選的檔案 → {data,w,h}（長邊 1600px） */
export async function compressFile(file){
  if(!file||!/^image\//.test(file.type))throw new Error("請選擇圖片檔");
  const url=URL.createObjectURL(file);
  try{return encode(await load(url),1600,PHOTO_MAX_CHARS,.82);}finally{URL.revokeObjectURL(url);}
}
/* 已經壓好的照片 → 列表用的小縮圖（長邊 480px） */
export async function makeThumb(dataUrl){return encode(await load(dataUrl),480,THUMB_MAX_CHARS,.72).data;}
