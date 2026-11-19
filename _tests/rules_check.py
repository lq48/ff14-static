"""照 firestore.rules.phase3-draft 的 memories / memoryImgs 規則，逐筆檢查頁面送出的寫入"""
import re
OWNER_UIDS={"u2"}  # 測試資料裡的總團長
KINDS={'first','prog','gather','festival','daily','other'}
MKEYS={'title','date','kind','desc','tid','eid','duty','members','note','thumb','imgs','by','createdAt','updatedAt'}
def is_img(s):return isinstance(s,str) and s.split(',')[0] in ('data:image/webp;base64','data:image/jpeg;base64')
def valid_memory(d):
    errs=[]
    if not set(d)<=MKEYS:errs.append("多出欄位 %s"%(set(d)-MKEYS))
    if not(isinstance(d.get('title'),str) and 0<len(d['title'])<=40):errs.append("title")
    if not(isinstance(d.get('date'),str) and re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}',d['date'])):errs.append("date")
    if d.get('kind') not in KINDS:errs.append("kind")
    for k,n in (('desc',300),('tid',40),('eid',40),('duty',40),('note',200)):
        v=d.get(k,'');
        if not(isinstance(v,str) and len(v)<=n):errs.append(k)
    if not(isinstance(d.get('members',[]),list) and len(d.get('members',[]))<=24):errs.append("members")
    if not(isinstance(d.get('imgs',[]),list) and len(d.get('imgs',[]))<=4):errs.append("imgs")
    th=d.get('thumb','')
    if not(th=='' or (is_img(th) and len(th)<=60000)):errs.append("thumb(%d)"%len(th or ''))
    if not isinstance(d.get('by'),str):errs.append("by")
    for k in('createdAt','updatedAt'):
        if not isinstance(d.get(k),(int,float)) or isinstance(d.get(k),bool):errs.append(k)
    return errs
def check(w):
    """回傳 (允許?, 原因)"""
    op,path,data,prev,uid=w['op'],w['path'],w.get('data'),w.get('prev'),w.get('uid')
    owner=uid in OWNER_UIDS
    if path.startswith('memories/'):
        if op=='setDoc':
            e=valid_memory(data)
            if prev is None:
                if data.get('by')!=uid:e.append("建立者不是自己")
            else:
                if not(owner or prev.get('by')==uid):e.append("不是作者也不是總團長")
                if data.get('by')!=prev.get('by'):e.append("改了作者")
            return (not e,"、".join(e) or "ok")
        if op=='updateDoc':
            # 被標記的人移除自己
            new={**prev,**data};changed={k for k in set(prev)|set(new) if prev.get(k)!=new.get(k)}
            ok_=uid in prev.get('members',[]) and changed<={'members','updatedAt'} and uid not in new['members'] and len(new['members'])==len(prev['members'])-1
            if ok_:return(True,"移除自己")
            if (owner or prev.get('by')==uid) and not valid_memory(new) and new.get('by')==prev.get('by'):return(True,"作者修改")
            return(False,"更新不符合規則")
        if op=='deleteDoc':
            return(owner or (prev or {}).get('by')==uid,"刪除")
    if path.startswith('memoryImgs/'):
        if op=='setDoc':
            e=[]
            if prev is not None:e.append("不允許修改照片")
            if not set(data)<={'mid','data','w','h','by','createdAt'}:e.append("多出欄位")
            if data.get('by')!=uid:e.append("by 不是自己")
            if not isinstance(data.get('mid'),str):e.append("mid")
            if not is_img(data.get('data')):e.append("不是 webp/jpeg")
            if len(data.get('data',''))>950000:e.append("太大 %d"%len(data['data']))
            return(not e,"、".join(e) or "ok")
        if op=='deleteDoc':
            return(owner or (prev or {}).get('by')==uid,"刪除照片")
        return(False,"不允許的操作 "+op)
    return(True,"其他 collection（不在這次檢查範圍）")
