import sys,os,json;sys.path.insert(0,os.path.dirname(__file__))
from exestr import scan
def esc(s): return s.replace(chr(10),'<n>')
def dump(name,d,ranges,minjp=1):
    with open(f'text/msrc/{name}.tsv','w',encoding='utf-8',newline='\n') as f:
        for lo,hi in ranges:
            for o,n,s in scan(d,lo,hi,minjp): f.write(f'{o:x}\t{n}\t{esc(s)}\n')
d=open('orig/SLPS_026.40','rb').read()
dump('exe_all',d,[(0x800,0x2e00),(0xaf000,0xd1200)])
for nm in ['P_LOD','P_WLD']:
    d=open('ext/'+nm,'rb').read();dump(nm,d,[(0,len(d))],2)
