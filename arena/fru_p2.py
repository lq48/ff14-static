"""絕伊甸 P2（希瓦·米特隆）地板：照遊戲截圖量的比例描成線條圖，風格比照 xivplan 的 e11.svg
600×600，圓心 (300,300)，可站區域半徑 300；顏色用 xivplan 的主題變數，深淺主題都會換色
量測（截圖可站半徑 635px）：內圈黑環 253px→0.40、外圈黑環 479px→0.755"""
import math
C=300
def pt(r,deg):  # deg：0＝北，順時針
    a=math.radians(deg);return C+r*math.sin(a),C-r*math.cos(a)
def line(r1,r2,deg,cls,w):x1,y1=pt(r1,deg);x2,y2=pt(r2,deg);return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" class="{cls}" stroke-width="{w}" stroke-linecap="round"/>'
def branch(r,deg,ang,L,cls,w):  # 從軸上 r 處往外斜出去的枝
    x,y=pt(r,deg);out=[]
    for s in (-1,1):
        a=math.radians(deg+s*ang);out.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x+L*math.sin(a):.1f}" y2="{y-L*math.cos(a):.1f}" class="{cls}" stroke-width="{w}" stroke-linecap="round"/>')
    return "".join(out)
def star(cx,cy,r,cls,w):  # 小六芒雪花
    return "".join(f'<line x1="{cx-r*math.sin(math.radians(a)):.1f}" y1="{cy-r*math.cos(math.radians(a)):.1f}" x2="{cx+r*math.sin(math.radians(a)):.1f}" y2="{cy+r*math.cos(math.radians(a)):.1f}" class="{cls}" stroke-width="{w}"/>' for a in (0,60,120))
def poly(pts,cls):return '<polygon points="'+" ".join(f"{x:.1f},{y:.1f}" for x,y in pts)+f'" class="{cls}"/>'
g=[]
# 兩圈黑環（大家用來對位置的那兩圈）
g.append(f'<circle cx="{C}" cy="{C}" r="120" class="darkStroke" fill="none" stroke-width="4"/>')
g.append(f'<circle cx="{C}" cy="{C}" r="226" class="darkStroke" fill="none" stroke-width="4"/>')
# 正方位四條主軸＋枝
for d in (0,90,180,270):
    g.append(line(58,292,d,"lineStroke",5))
    for r,L in ((262,30),(238,44),(212,58)):g.append(branch(r,d,38,L,"lineStroke",4))
    for r,L in ((112,22),(100,16)):g.append(branch(r,d,40,L,"lineStroke",3))
    x,y=pt(155,d);g.append(star(x,y,14,"lineStroke",2))
    x,y=pt(90,d);g.append(poly([(x+6*math.sin(math.radians(d+a)),y-6*math.cos(math.radians(d+a))) for a in (0,90,180,270)],"dark"))
# 斜角四條：中間一段粗、往外細線，外面有方塊花紋
for d in (45,135,225,315):
    g.append(line(45,165,d,"lineStroke",6));g.append(line(165,292,d,"lineStroke",2))
    for r in (135,):g.append(branch(r,d,50,32,"lineStroke",4))
    for r in (205,250):
        x,y=pt(r,d);s=13 if r==205 else 10
        g.append(poly([(x+s*math.sin(math.radians(d+a)),y-s*math.cos(math.radians(d+a))) for a in (0,90,180,270)],"lineFill"))
        g.append(star(x,y,s+9,"lineStroke",1.5))
# 中心的星形
pts=[]
for i in range(16):
    r=(52 if i%4==0 else 36 if i%4==2 else 16);a=i*22.5+45
    pts.append(pt(r,a))
g.append(poly(pts,"dark"))
g.append(f'<circle cx="{C}" cy="{C}" r="6" class="lineFill"/>')
# 邊緣八個冰晶標記（正方位＋斜角）
for d in range(0,360,45):
    x,y=pt(296,d);g.append(poly([pt(296-14,d),pt(296+2,d-3),pt(296+2,d+3)],"lineFill"))
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">
<!-- 絕伊甸（Futures Rewritten Ultimate）P2 地板，依遊戲截圖描繪的示意線條圖。光之戰士飛地，MIT。 -->
<style>.darkStroke{{stroke:var(--xiv-colorArenaDark,#352b21)}}.dark{{fill:var(--xiv-colorArenaDark,#352b21)}}
.lineStroke{{stroke:var(--xiv-colorArenaLight,#4c4034)}}.lineFill{{fill:var(--xiv-colorArenaLight,#4c4034)}}</style>
<g>{"".join(g)}</g></svg>'''
open("/home/claude/ff14-static/arena/fru-p2.svg","w").write(svg);print(len(svg),"bytes")
