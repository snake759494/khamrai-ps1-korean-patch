import struct,sys,os
sys.path.insert(0,os.path.dirname(__file__))
import tim
BLK=0xf000
def loc(i):
    p,r=divmod(i,189); tex=p&1; layer=(p>>1)&1; half=p>>2
    row,col=divmod(r,21)
    return tex,layer,half*256+col*12,row*12
def texoff(d,blk,tex):
    t=tim.parse(d,blk*BLK+0x1000+tex*0x7000); return t['pix']
def glyph(d,blk,i):
    tex,layer,x0,y0=loc(i);o=texoff(d,blk,tex);g=[]
    for y in range(12):
        row=[]
        for x in range(12):
            X=x0+x;v=(d[o+(y0+y)*256+X//2]>>((X&1)*4))&15
            row.append((v>>(2*layer))&3)
        g.append(row)
    return g
def put(d,blk,i,g):
    tex,layer,x0,y0=loc(i);o=texoff(d,blk,tex)
    for y in range(12):
        for x in range(12):
            X=x0+x;a=o+(y0+y)*256+X//2;sh=(X&1)*4+2*layer
            d[a]=(d[a]&~(3<<sh)&0xff)|(g[y][x]<<sh)
