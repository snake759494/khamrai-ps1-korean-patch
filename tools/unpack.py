# 원본 디스크에서 orig/(루트 파일)와 ext/(ASDATA.BIN 내부 파일)를 추출: python tools/unpack.py [원본.bin]
import sys,os
sys.path.insert(0,os.path.dirname(__file__))
from iso import Disc
from fat import load
src=sys.argv[1] if len(sys.argv)>1 else os.path.join('..','Khamrai (Japan).bin')
d=Disc(src);os.makedirs('orig',exist_ok=True);os.makedirs('ext',exist_ok=True)
for p,lba,size,*_ in d.walk():
    n=p.strip('/').split(';')[0]
    if '/' in n or n.endswith(('.STR','.XAP','.NOP')): continue
    open('orig/'+n,'wb').write(d.read(lba,size))
A=open('orig/ASDATA.BIN','rb').read()
L=load()
for n,s,c in L: open('ext/'+n,'wb').write(A[s*2048:(s+c)*2048])
print('orig',len(os.listdir('orig')),'ext',len(L))
