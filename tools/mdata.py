# 데이터 파일 문자열 읽기/쓰기 정의
import struct
def tbl(d,cnt,ptab,base):
    out=[]
    for i in range(cnt):
        o=base+struct.unpack_from('<I',d,ptab+4*i)[0]
        out.append(d[o:d.index(b'\0',o)])
    return out
def item(d):
    h=struct.unpack_from('<7I',d,0);n=h[0]
    return n,(h[3],h[5]),(h[4],h[6])   # (ptab,base) name, desc
def magic(d):
    h=struct.unpack_from('<7I',d,0);n=h[0]
    return n,(h[2],h[4]),(h[3],h[5])
ENEMY0,ENEMYSTRIDE,ENEMYN=0x3862,0x5a,182
def enemy_names(d):
    return [d[ENEMY0+k*ENEMYSTRIDE+2:ENEMY0+k*ENEMYSTRIDE+0x12].split(b'\0')[0] for k in range(ENEMYN)]
WILL_BASE,WILL_TAB,WILL_END=0x9b8,0x4a5c,0x4ff4
def will(d):
    vals=[struct.unpack_from('<I',d,i)[0] for i in range(WILL_TAB,WILL_END,4)]
    uniq=sorted(set(vals))
    strs={v:d[WILL_BASE+v:d.index(b'\0',WILL_BASE+v)] for v in uniq}
    return vals,uniq,strs
