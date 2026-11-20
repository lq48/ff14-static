"""一次跑完全部回歸測試：python3 _tests/run_all.py
   每個測試檔各自開瀏覽器，只要有任何 FAIL 或程式錯誤，結束代碼就不是 0（CI 會顯示失敗）"""
import subprocess,sys,os,glob,re,time
H=os.path.dirname(os.path.abspath(__file__))
files=sorted(glob.glob(os.path.join(H,"test_*.py")))
if len(sys.argv)>1:files=[f for f in files if any(a in os.path.basename(f) for a in sys.argv[1:])]
tot_p=tot_f=0;bad=[]
for f in files:
    t=time.time();r=subprocess.run([sys.executable,f],cwd=H,capture_output=True,text=True,timeout=900)
    out=r.stdout+r.stderr;p=len(re.findall(r"^PASS ",out,re.M));fl=len(re.findall(r"^FAIL ",out,re.M))
    crashed=r.returncode!=0 or "Traceback" in out
    tot_p+=p;tot_f+=fl
    status="✅" if not fl and not crashed else "❌"
    print(f"{status} {os.path.basename(f):24s} 通過 {p:3d}　失敗 {fl:2d}　{time.time()-t:5.1f} 秒"+("　（程式錯誤）" if crashed else ""))
    if fl or crashed:
        bad.append(f);print("\n".join(["     "+l for l in out.splitlines() if l.startswith("FAIL ") or "Error" in l or "Traceback" in l][:12]))
print(f"\n合計：通過 {tot_p} 項，失敗 {tot_f} 項" + ("" if not bad else f"，有問題的檔案 {len(bad)} 個"))
sys.exit(1 if bad else 0)
