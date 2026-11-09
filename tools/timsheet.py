# 파일 그룹의 모든 TIM을 접촉 시트로 렌더: python timsheet.py 출력.png 최대폭 파일...
import sys,os
sys.path.insert(0,os.path.dirname(__file__))
from gfx import tims
from tim import render
from PIL import Image,ImageDraw
out=sys.argv[1];W=int(sys.argv[2]);files=sys.argv[3:]
items=[]
for nm in files:
    d=open('ext/'+nm,'rb').read()
    for i,t in enumerate(tims(d)):
        try:
            im=render(d,t)
        except Exception: continue
        if im.width*im.height<64: continue
        items.append((f'{nm}:{i}',im))
x=y=rowh=0;pos=[]
for lab,im in items:
    w,h=im.size;w=min(w,W)
    if x+w>W: x=0;y+=rowh+10;rowh=0
    pos.append((x,y));x+=w+4;rowh=max(rowh,h)
H=y+rowh+10
S=Image.new('RGB',(W,max(H,1)),(255,0,255));dr=ImageDraw.Draw(S)
for (lab,im),(x,y) in zip(items,pos):
    S.paste(im,(x,y+10),im);dr.text((x,y),lab,fill=(0,0,0))
S.save(out);print(len(items),S.size)
