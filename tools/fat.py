import struct
def load(p='orig/ASDATA.FAT'):
    d=open(p,'rb').read();L=[];s=0
    for i in range(0,len(d)-9,10):
        n=d[i:i+8].rstrip(b'\0').decode('latin1');c=struct.unpack_from('<H',d,i+8)[0]
        if not n: break
        L.append((n,s,c));s+=c
    return L
