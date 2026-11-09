import struct,re
def find(d):
    for m in re.finditer(rb'\$ASS',d):
        o=m.start();t=o+struct.unpack_from('<I',d,o+16)[0]
        first=o+struct.unpack_from('<I',d,t)[0];n=(first-t)//4
        offs=[o+struct.unpack_from('<I',d,t+4*i)[0] for i in range(n)]
        strs=[]
        for a in offs:
            b=d.index(b'\0',a);strs.append(d[a:b])
        yield o,t,n,offs,strs
