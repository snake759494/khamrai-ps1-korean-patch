import re,struct,sys,os
sys.path.insert(0,os.path.dirname(__file__))
from charset import ALL
def good(d,minc=2):
    i=0;n=len(d);out=[]
    while i<n-3:
        j=i;cnt=0;ok=True
        while j<n-1:
            c=d[j]<<8|d[j+1]
            if c in ALL: j+=2;cnt+=1
            elif d[j]==0x25 and j+1<n and d[j+1] in b'MCNWPKSIBTE0123456789': j+=2
            elif 0x20<=d[j]<0x7f and d[j]!=0x25: j+=1
            else: break
        if cnt>=minc and j<n and d[j] in (0,0x25):
            out.append((i,d[i:j]));i=j+1
        else: i+=1
    return out
