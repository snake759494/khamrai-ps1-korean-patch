import struct
def sets(p='ext/KANJI'):
    d=p if isinstance(p,bytes) else open(p,'rb').read();R=[]
    for blk in range(9):
        i=blk*0xf000;codes=[]
        while True:
            c=struct.unpack_from('<H',d,i)[0]
            if not(0x8140<=c<=0xeafc): break
            codes.append(c);i+=2
        R.append(codes)
    return R
ALL=set(c for s in sets() for c in s)
