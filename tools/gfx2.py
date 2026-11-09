# 범용 그래픽 한글 재작화 (4bpp TIM)
#  - aa   : 원본 배경/가장 밝은 색 사이를 알파로 보간해 원본 팔레트에서 가장 가까운 색 선택(명조 지역명 등)
#  - style: 원본 글자 몸통의 행별 색(그라데이션) + 외곽선(가장 어두운 색) + 글로우(중간색) 재현
import sys,os,struct
sys.path.insert(0,os.path.dirname(__file__))
from gfx import tims,pal,rgb,getpix,setpix
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from collections import Counter
ROOT=os.path.join(os.path.dirname(__file__),'..')
F={'serif':os.path.join(ROOT,'..','SeoulHangangB.ttf'),'serifm':os.path.join(ROOT,'..','SeoulHangangM.ttf'),'serifeb':os.path.join(ROOT,'..','SeoulHangangEB.ttf'),
   'g7':os.path.join(ROOT,'fonts','Galmuri7.ttf'),'g9':os.path.join(ROOT,'fonts','Galmuri9.ttf'),'g11':os.path.join(ROOT,'fonts','Galmuri11.ttf')}
def lum(c): return c[0]*0.3+c[1]*0.59+c[2]*0.11
def line_img(s,font,size,thr=None):
    f=ImageFont.truetype(F[font],size);bb=f.getbbox(s)
    im=Image.new('L',(max(1,bb[2]-bb[0]),max(1,bb[3]-bb[1])));ImageDraw.Draw(im).text((-bb[0],-bb[1]),s,font=f,fill=255)
    if thr: im=im.point(lambda v:255 if v>=thr else 0)
    return im
def text_mask(lines,W,H,italic=0.0,pad=1,thr=None,gap=1,center=True):
    """lines: [(문자열,폰트,크기)] → W×H 알파 마스크 (넘치면 축소)"""
    ims=[line_img(s,f,z,thr) for s,f,z in lines]
    tw=max(i.width for i in ims)+int(italic*max(i.height for i in ims))+1;th=sum(i.height for i in ims)+gap*(len(ims)-1)
    M=Image.new('L',(tw,th));y=0
    for im in ims:
        x=(tw-im.width)//2 if center else 0
        M.paste(im,(x,y));y+=im.height+gap
    if italic:
        M=M.transform((tw,th),Image.AFFINE,(1,italic,-italic*th,0,1,0),Image.BICUBIC)
    sx=min(1,(W-2*pad)/M.width);sy=min(1,(H-2*pad)/M.height)
    if sx<1 or sy<1:
        M=M.resize((max(1,int(M.width*sx)),max(1,int(M.height*sy))),Image.LANCZOS)
        if thr: M=M.point(lambda v:255 if v>=thr else 0)
    out=Image.new('L',(W,H));out.paste(M,((W-M.width)//2,(H-M.height)//2));return out
def region_info(px,P,x0,y0,w,h):
    used=Counter(px[y][x] for y in range(y0,y0+h) for x in range(x0,x0+w))
    bg=0 if 0 in used and P[0]==(0,0,0) else used.most_common(1)[0][0]
    return used,bg
def nearest(cands,P,c): return min(cands,key=lambda i:sum((P[i][k]-c[k])**2 for k in range(3)))
def draw_aa(d,t,box,lines,italic=0.0,fg=None,thr=None,pad=1):
    P=[rgb(v) for v in pal(d,t)];W,px=getpix(d,t);x0,y0,w,h=box
    used,bg=region_info(px,P,x0,y0,w,h)
    cands=[i for i in used if i!=bg] or list(range(1,16))
    if fg is None: fg=max(cands,key=lambda i:lum(P[i]))
    M=text_mask(lines,w,h,italic,thr=thr,pad=pad)
    for y in range(h):
        for x in range(w):
            a=M.getpixel((x,y))/255
            if a<0.2: px[y0+y][x0+x]=bg;continue
            c=tuple(P[fg][k]*a+(P[bg][k] if bg else P[fg][k]*0.25)*(1-a) for k in range(3))
            px[y0+y][x0+x]=nearest(cands,P,c)
    setpix(d,t,px)
def draw_style(d,t,box,lines,italic=0.0,outline=1,glow=0,thr=None,shadow=False,pad=1):
    P=[rgb(v) for v in pal(d,t)];W,px=getpix(d,t);x0,y0,w,h=box
    used,bg=region_info(px,P,x0,y0,w,h)
    cands=[i for i in used if i!=bg]
    cands.sort(key=lambda i:lum(P[i]))
    dark=cands[0]
    # 행별 몸통 색: 그 행의 상위 밝기 색
    rows=[]
    for y in range(h):
        r=[px[y0+y][x0+x] for x in range(w) if px[y0+y][x0+x]!=bg]
        r=[i for i in r if lum(P[i])>=lum(P[cands[len(cands)*2//3]])] or None
        rows.append(Counter(r).most_common(1)[0][0] if r else None)
    # 비어 있는 행은 가까운 행 값으로
    for y in range(h):
        if rows[y] is None:
            near=[rows[j] for j in sorted(range(h),key=lambda j:abs(j-y)) if rows[j] is not None]
            rows[y]=near[0] if near else cands[-1]
    mid=cands[len(cands)//2]
    M=text_mask(lines,w-2*(outline+glow),h-2*(outline+glow),italic,thr=thr or 110,pad=pad)
    Mf=Image.new('L',(w,h));Mf.paste(M,(outline+glow,outline+glow))
    body=Mf.point(lambda v:255 if v>=110 else 0)
    ol=body.filter(ImageFilter.MaxFilter(2*outline+1)) if outline else body
    gl=ol.filter(ImageFilter.MaxFilter(2*glow+1)) if glow else ol
    for y in range(h):
        for x in range(w):
            if body.getpixel((x,y)): v=rows[y]
            elif ol.getpixel((x,y)): v=dark
            elif gl.getpixel((x,y)): v=mid
            elif shadow and x>0 and y>0 and body.getpixel((x-1,y-1)): v=dark
            else: v=bg
            px[y0+y][x0+x]=v
    setpix(d,t,px)
def draw_replace(d,t,box,lines,lumthr=None,outline=0,pad=0,thr=128,italic=0.0):
    """원본 테두리·글로우 유지: 밝은 글자 픽셀을 주변 색으로 지운 뒤 한글을 원래 글자 색으로 그림"""
    P=[rgb(v) for v in pal(d,t)];W,px=getpix(d,t);x0,y0,w,h=box
    reg=[(x,y) for y in range(y0,y0+h) for x in range(x0,x0+w)]
    used=Counter(px[y][x] for x,y in reg)
    nz=[i for i in used if not(i==0 and P[0]==(0,0,0))]
    nz.sort(key=lambda i:lum(P[i]))
    fill=used.most_common(1)[0][0]
    if lumthr=='mid': lumthr=(lum(P[nz[0]])+lum(P[nz[-1]]))/2
    if lumthr is None: lumthr=lum(P[fill])+(lum(P[nz[-1]])-lum(P[fill]))*0.3
    glyph=set((x,y) for x,y in reg if px[y][x] in nz and lum(P[px[y][x]])>=lumthr)
    gcol=Counter(px[y][x] for x,y in glyph)
    body=max(gcol,key=lambda i:lum(P[i]))
    edge=min(gcol,key=lambda i:lum(P[i]))
    # 지우기: 반복적으로 이웃의 비글자 색으로 채움
    rem=set(glyph)
    while rem:
        nxt=set()
        for x,y in rem:
            nb=[px[y+dy][x+dx] for dx,dy in((1,0),(-1,0),(0,1),(0,-1)) if (x+dx,y+dy) not in rem and x0<=x+dx<x0+w and y0<=y+dy<y0+h]
            if nb: px[y][x]=Counter(nb).most_common(1)[0][0]
            else: nxt.add((x,y))
        if nxt==rem: break
        rem=nxt
    M=text_mask(lines,w-2*outline,h-2*outline,italic,thr=thr,pad=pad)
    Mf=Image.new('L',(w,h));Mf.paste(M,(outline,outline))
    B=Mf.point(lambda v:255 if v>=thr else 0)
    O=B.filter(ImageFilter.MaxFilter(2*outline+1)) if outline else B
    for y in range(h):
        for x in range(w):
            if B.getpixel((x,y)): px[y0+y][x0+x]=body
            elif O.getpixel((x,y)): px[y0+y][x0+x]=edge
    setpix(d,t,px)
