# 그래픽 라벨 한글화: ext/<파일>의 TIM을 한글로 다시 그려 gfx/<파일>로 저장
import sys,os,struct
sys.path.insert(0,os.path.dirname(__file__))
from tim import parse
from PIL import Image,ImageDraw,ImageFont
_R=os.path.join(os.path.dirname(__file__),'..');SERIF=os.path.join(_R,'..','SeoulHangangB.ttf'); SMALL=os.path.join(_R,'fonts','Galmuri11.ttf')
def tims(d):
    r=[];o=0
    while o<len(d)-8:
        t=parse(d,o)
        if t: r.append(t); o=t['end']; o=(o+3)&~3
        else: o+=4
    return r
def pal(d,t):
    cx,cy,cw,ch,cp=t['clut']
    return [struct.unpack_from('<H',d,cp+i*2)[0] for i in range(16)]
def rgb(v): return ((v&31)<<3,((v>>5)&31)<<3,((v>>10)&31)<<3)
def getpix(d,t):
    W=t['w']*4;return W,[[(d[t['pix']+y*t['w']*2+x//2]>>((x&1)*4))&15 for x in range(W)] for y in range(t['h'])]
def setpix(d,t,P):
    for y,row in enumerate(P):
        for x in range(0,len(row),2):
            d[t['pix']+y*t['w']*2+x//2]=row[x]|(row[x+1]<<4)
def _r(fp,size,s):
    f=ImageFont.truetype(fp,size);bb=f.getbbox(s)
    im=Image.new('L',(bb[2]-bb[0]+1,bb[3]-bb[1]+1));ImageDraw.Draw(im).text((-bb[0],-bb[1]),s,font=f,fill=255)
    return im
def text_mask(s,W,H,size):
    for fp,sz in ((SERIF,size),(SMALL,12),(os.path.join(_R,'fonts','Galmuri9.ttf'),10)):
        im=_r(fp,sz,s)
        if im.width<=W-1 and im.height<=H-1: return im
    return im.resize((W-1,im.height),Image.LANCZOS)
def relabel(d,t,labels,rowh,size,align='left'):
    P16=[rgb(v) for v in pal(d,t)]
    W,px=getpix(d,t)
    from collections import Counter
    used=Counter(v for r in px for v in r)
    bg=used.most_common(1)[0][0]
    cand=[i for i in used if used[i]>0]
    fg=max(cand,key=lambda i:sum(P16[i]))
    sh=min((i for i in cand if i!=bg),key=lambda i:sum(P16[i]))
    for k,s in enumerate(labels):
        if s is None: continue
        y0=k*rowh
        m=text_mask(s,W,rowh,size)
        ox=1 if align=='left' else (W-m.width)//2
        oy=y0+(rowh-m.height)//2
        for y in range(y0,y0+rowh):
            for x in range(W): px[y][x]=bg
        for y in range(m.height):
            for x in range(m.width):
                if m.getpixel((x,y))<110: continue
                for dx,dy,v in ((1,1,sh),(0,0,fg)):
                    yy,xx=oy+y+dy,ox+x+dx
                    if y0<=yy<y0+rowh and 0<=xx<W and (v==fg or px[yy][xx]==bg): px[yy][xx]=v
    setpix(d,t,px)
WMAP={9:'아지트',10:'아마르하라 고원',11:'수도 엔가',12:'카루 호수',13:'가르바렌',14:'쿠아라',15:'타스타리',
16:'하라스',17:'북쪽 동굴',18:'탄식의 계곡',19:'빛의 나라',20:'대지의 나라',21:'천공의 나라',22:'불의 나라',
23:'생명의 나라',24:'어둠의 나라',25:'어둠의 숲',26:'짐승의 계곡',27:'신전',28:'성산 볼자르',29:'유적',
30:'구름다리',31:'영수의 숲',32:'코란'}
def main():
    d=bytearray(open('ext/WMAP_T','rb').read()); T=tims(d)
    for i,s in WMAP.items(): relabel(d,T[i],[s],16,14)
    open('gfx/WMAP_T','wb').write(d)
    d=bytearray(open('ext/MIND_T','rb').read()); T=tims(d)
    relabel(d,T[7],['동료','개인','질서','혼돈'],16,15,'center')
    relabel(d,T[8],['카가토','후시','슈온','유','키리하','츠키카게','츠루노히메','사요히메'],24,20,'center')
    open('gfx/MIND_T','wb').write(d)
if __name__=='__main__': main()
