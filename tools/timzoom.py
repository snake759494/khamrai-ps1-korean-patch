# python timzoom.py out.png 파일 배율 idx...  (배경 회색, 인덱스·크기·bpp 라벨)
import sys,os
sys.path.insert(0,os.path.dirname(__file__))
from gfx import tims
from tim import render
from PIL import Image,ImageDraw
out,nm,z=sys.argv[1],sys.argv[2],int(sys.argv[3]);idx=[int(a) for a in sys.argv[4:]]
d=open('ext/'+nm,'rb').read();T=tims(d)
ims=[(i,render(d,T[i])) for i in idx]
W=max(im.width*z for _,im in ims)+10;H=sum(im.height*z+14 for _,im in ims)
S=Image.new('RGB',(max(W,300),H),(90,90,90));dr=ImageDraw.Draw(S);y=0
for i,im in ims:
    t=T[i];dr.text((0,y),f'{i} {im.size} bpp{t["bpp"]} clut{t["clut"][:4] if t["clut"] else ""}',fill=(255,255,0));y+=12
    im2=im.resize((im.width*z,im.height*z),0);S.paste(im2,(0,y),im2);y+=im2.height+2
S.save(out)
