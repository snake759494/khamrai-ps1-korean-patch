import struct
from PIL import Image
def parse(d,o):
    if d[o:o+4]!=b'\x10\0\0\0': return None
    fl=struct.unpack_from('<I',d,o+4)[0]
    if fl not in (8,9,2,3,0,1): return None
    bpp=fl&3; p=o+8; clut=None
    if fl&8:
        L,cx,cy,cw,ch=struct.unpack_from('<IHHHH',d,p)
        if L!=12+cw*ch*2 or cw==0 or ch==0 or cw>256 or ch>256: return None
        clut=(cx,cy,cw,ch,p+12); p+=L
    L,x,y,w,h=struct.unpack_from('<IHHHH',d,p)
    if L!=12+w*h*2 or w==0 or h==0 or w>1024 or h>512 or x>=1024 or y>=512: return None
    return dict(o=o,bpp=bpp,clut=clut,x=x,y=y,w=w,h=h,pix=p+12,end=p+L)
def col(v,t=True):
    r=(v&31)<<3; g=((v>>5)&31)<<3; b=((v>>10)&31)<<3
    return (r,g,b,0 if (v==0 and t) else 255)
def render(d,t,pal=0):
    bpp=t['bpp']; w=t['w']*(4 if bpp==0 else 2 if bpp==1 else 1); h=t['h']
    im=Image.new('RGBA',(w,h)); px=im.load()
    if t['clut']:
        cx,cy,cw,ch,cp=t['clut']; n=16 if bpp==0 else 256
        base=cp+pal*cw*2
        P=[col(struct.unpack_from('<H',d,base+i*2)[0]) for i in range(min(n,cw*ch-pal*cw))]
        P+= [(0,0,0,0)]*(n-len(P))
    for yy in range(h):
        row=t['pix']+yy*t['w']*2
        for xx in range(w):
            if bpp==0: v=(d[row+xx//2]>>((xx&1)*4))&15; px[xx,yy]=P[v]
            elif bpp==1: px[xx,yy]=P[d[row+xx]]
            else: px[xx,yy]=col(struct.unpack_from('<H',d,row+xx*2)[0])
    return im
