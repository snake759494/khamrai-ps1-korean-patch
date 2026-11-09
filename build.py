# 카무라이 한글패치 빌드: python build.py [출력.bin]
import sys,os,re,json,struct,shutil,time
ROOT=os.path.dirname(os.path.abspath(__file__));os.chdir(ROOT)
sys.path.insert(0,'tools')
import gfxall
from fat import load as fat_load
import ass,mdata,kfont,tim
from charset import sets as font_sets
from cdsec import form1
from iso import Disc,SEC
from PIL import Image,ImageFont,ImageDraw

SRC_BIN=os.path.join('..','Khamrai (Japan).bin')
OUT_BIN=sys.argv[1] if len(sys.argv)>1 else os.path.join('..','Khamrai (Japan) [KR].bin')
LOG=open('build.log','w',encoding='utf-8')
def log(*a):
    print(*a,file=LOG)
CODE=re.compile(r'%[A-Za-z][0-9]|%-?[0-9]*[sdI]|%[0-9]+d')

# ---------------- 번역 읽기 ----------------
ja=json.load(open('text/ja.json',encoding='utf-8'))
ko={}
for fn in sorted(os.listdir('text/ko')):
    if not fn.endswith('.tsv'): continue
    for l in open('text/ko/'+fn,encoding='utf-8'):
        l=l.rstrip('\n')
        if not l or l.startswith('#') or '\t' not in l: continue
        i,t=l.split('\t',1);ko[int(i)]=t
fix={}
if os.path.exists('text/fix.tsv'):
    for l in open('text/fix.tsv',encoding='utf-8'):
        l=l.rstrip('\n')
        if l and not l.startswith('#') and '\t' in l:
            i,t=l.split('\t',1);fix[int(i)]=t
ko.update(fix)
def mload(name):
    p=f'text/mko/{name}.tsv';r={}
    if os.path.exists(p):
        for l in open(p,encoding='utf-8'):
            l=l.rstrip('\n')
            if l and '\t' in l and not l.startswith('#'):
                k,t=l.split('\t',1);r[k]=t.replace('<n>','\n')
    return r
M={n:mload(n) for n in ['exe','P_LOD','P_WLD','ITEM','MAGIC','ENEMY','WILL_D']}

# ---------------- 문자 정규화 ----------------
def norm_dialog(s):
    s=s.replace('...','・・・').replace('…','・・・')
    s=s.replace('!','☆').replace('！','☆').replace('?','★').replace('？','★')
    s=s.replace(',','，').replace('、','，').replace(' ','\x01').replace('　','\x01')
    s=s.replace('~','～').replace(':','：').replace('(','（').replace(')','）').replace('-','－')
    s=re.sub(r'(?<=[가-힣」』☆★）])\.(?!\.)','',s).replace('.','')
    return s
def norm_data(s):
    # '!x' 반각 코드와 printf 코드는 유지
    out='';i=0
    while i<len(s):
        c=s[i]
        if c=='!' and i+1<len(s): out+=s[i:i+2];i+=2;continue
        if c=='%':
            m=CODE.match(s,i)
            if m: out+=m.group();i=m.end();continue
        if c==' ' or c=='　': out+='\x01'
        elif c=='.': pass
        elif c==':': out+='：'
        elif c==',': out+='，'
        elif c=='?': out+='★'
        elif c=='~': out+='～'
        else: out+=c
        i+=1
    return out

# 대사 문자열 → 정규화 (제어코드 보존)
def norm_keep_codes(s,f):
    parts=re.split(r'(%[A-Za-z][0-9])',s)
    return ''.join(p if re.fullmatch(r'%[A-Za-z][0-9]',p) else f(p) for p in parts)

KO={}   # ja index -> normalized korean
WRAP=17
def wrap(s):
    # 보이는 글자 17자 초과 시 그 이전 마지막 공백에서 줄바꿈
    toks=re.findall(r'%M\d.*?%M\d|%[A-Za-z]\d|%|.',s)
    out=[];n=0;last=None
    for t in toks:
        if len(t)==1 and t!='%':
            if n>=WRAP and last is not None:
                out[last]='\n';n=sum(1 for x in out[last+1:] if len(x)==1 and x!='%');last=None
            if t=='\x01': last=len(out)
            n+=1
        out.append(t)
    return ''.join(out)
for i,t in ko.items(): KO[i]=norm_keep_codes(t,norm_dialog)
import reflow
# 실제 스크립트 안에서의 앞뒤 관계: 공유 문자열(예: 빈 줄 '＿%')이 엉뚱한 대사와 묶이지 않도록
import ass as _ass
_ji={s.encode('cp932'):i for i,s in reversed(list(enumerate(ja)))}
NXT={};PRV={}
for _nm in os.listdir('ext'):
    _d=open('ext/'+_nm,'rb').read()
    if _d[:4]!=b'$ASS': continue
    for _o,_t,_n,_offs,_strs in _ass.find(_d):
        _q=[_ji.get(x) for x in _strs]
        for _a,_b in zip(_q,_q[1:]+[None]):
            if _a is not None: NXT.setdefault(_a,set()).add(_b)
            if _b is not None: PRV.setdefault(_b,set()).add(_a)
def LINK(a,b): return NXT.get(a)=={b} and PRV.get(b)=={a}
log('대사 재배치',reflow.reflow(KO,sorted(KO),LINK),'단독줄 줄바꿈',reflow.split_single(KO,sorted(KO),LINK),'남은 17자 초과',sum(1 for v in KO.values() if max(reflow.vis(p) for p in v.split(chr(10)))>17))
MN={}
for n,dct in M.items():
    MN[n]={k:norm_data(v) for k,v in dct.items()}

# ---------------- 글꼴 ----------------
hangul=set()
for t in list(KO.values())+[v for d in MN.values() for v in d.values()]:
    hangul|=set(ch for ch in t if '가'<=ch<='힣')
GREEK_KO={'α':'력','β':'기','γ':'격','δ':'공','ε':'방','ζ':'신','η':'순','θ':'발','ι':'체','κ':'어','λ':'력','μ':'경','ν':'험','ξ':'치'}
hangul=sorted(hangul)
def sjis_seq():
    for lead in list(range(0x88,0xa0))+list(range(0xe0,0xeb)):
        for tr in list(range(0x40,0x7f))+list(range(0x80,0xfd)):
            c=lead<<8|tr
            if c>=0x889f: yield c
g=sjis_seq();KMAP={h:next(g) for h in hangul}
log('한글 음절 수',len(hangul))
def enc(s):
    out=bytearray()
    for ch in s:
        if ch in KMAP: out+=KMAP[ch].to_bytes(2,'big')
        elif ch=='\x01': out+=b'! '
        elif ch=='\n': out+=b'\n'
        else: out+=ch.encode('cp932')
    return bytes(out)

FONT=ImageFont.truetype('fonts/Galmuri11.ttf',12)
def kglyph(ch):
    im=Image.new('L',(16,16),0);ImageDraw.Draw(im).text((0,-1),ch,font=FONT,fill=255)
    a=im.load();body=[[1 if a[x,y]>127 else 0 for x in range(12)] for y in range(12)]
    g=[[0]*12 for _ in range(12)]
    for y in range(12):
        for x in range(12):
            if body[y][x]: g[y][x]=1
            elif y>0 and x>0 and body[y-1][x-1]: g[y][x]=3
            elif (x>0 and body[y][x-1]) or (y>0 and body[y-1][x]): g[y][x]=3
    return g

def build_font(kanji):
    d=bytearray(kanji);S=font_sets(bytes(kanji))
    used_nonk=set()
    for t in [*KO.values(),*[v for dd in MN.values() for v in dd.values()]]:
        for ch in t:
            if ch in KMAP: continue
            try: b=ch.encode('cp932')
            except UnicodeEncodeError: continue
            if len(b)==2: used_nonk.add(int.from_bytes(b,'big'))
    old={}
    for k in range(9):
        for i,c in enumerate(S[k]):
            if c<0x889f and c not in old: old[c]=kfont.glyph(bytes(kanji),k,i)
    kana=lambda c:0x829f<=c<=0x82f1 or 0x8340<=c<=0x8396
    keep=sorted(c for c in old if not kana(c) or c in used_nonk)
    missing=[c for c in used_nonk if c not in old and c<0x889f]
    if missing: log('글꼴에 없는 기호',[bytes([c>>8,c&255]).decode('cp932') for c in missing])
    for k in range(9):
        base=k*kfont.BLK
        codes=keep+[KMAP[h] for h in hangul]
        if len(codes)>1512: raise SystemExit(f'글꼴 세트 {k}: {len(codes)}자 > 1512')
        codes.sort()
        tab=b''.join(struct.pack('<H',c) for c in codes)
        d[base:base+0x1000]=tab.ljust(0x1000,b'\xff')
        for tx in range(2):
            t=tim.parse(bytes(d),base+0x1000+tx*0x7000)
            d[t['pix']:t['pix']+256*108]=bytes(256*108)
        inv={v:h for h,v in KMAP.items()}
        for i,c in enumerate(codes):
            if c in inv: g=kglyph(inv[c])
            elif c in old:
                g=old[c]
                ch=bytes([c>>8,c&255]).decode('cp932')
                if ch in GREEK_KO: g=kglyph(GREEK_KO[ch])
            kfont.put(d,k,i,g)
        log('글꼴 세트',k,'유지',len(keep),'합계',len(codes))
    return bytes(d)

# ---------------- 스크립트 ----------------
JAIDX={}
for i,s in enumerate(ja): JAIDX.setdefault(s.encode('cp932'),i)
miss=set()
def patch_ass(d):
    d=bytearray(d)
    o=0;t=struct.unpack_from('<I',d,16)[0]
    first=struct.unpack_from('<I',d,t)[0];n=(first-t)//4
    offs=[struct.unpack_from('<I',d,t+4*i)[0] for i in range(n)]
    region=bytearray();pos={};newoffs=[]
    for a in offs:
        raw=bytes(d[a:d.index(b'\0',a)])
        idx=JAIDX.get(raw)
        if idx is not None and idx in KO: new=enc(KO[idx])
        else:
            new=raw
            if idx is not None: miss.add(idx)
        if new not in pos: pos[new]=first+len(region);region+=new+b'\0'
        newoffs.append(pos[new])
    for i,v in enumerate(newoffs): struct.pack_into('<I',d,t+4*i,v)
    out=bytes(d[:first])+bytes(region)
    return out

# ---------------- 데이터 파일 ----------------
def rebuild_tables(d,n,N,D,keyN,keyD,name):
    d=bytearray(d);tr=MN[name]
    names=mdata.tbl(bytes(d),n,*N);descs=mdata.tbl(bytes(d),n,*D)
    nb=N[1];region=bytearray()
    def add(lst,key,ptab,base):
        nonlocal region
        cache={}
        for i,x in enumerate(lst):
            k=f'{key}{i}';v=enc(tr[k]) if k in tr else x
            if k not in tr: log('번역 없음',name,k)
            if v not in cache: cache[v]=len(region)-(base-nb);region+=v+b'\0'
            struct.pack_into('<I',d,ptab+4*i,cache[v])
    add(names,keyN,N[0],nb)
    while len(region)%4: region+=b'\0'
    dbase=nb+len(region)
    add(descs,keyD,D[0],dbase)
    end=nb+len(region)
    return d,dbase,end
def patch_item(d):
    n,N,D=mdata.item(d)
    d,dbase,end=rebuild_tables(d,n,N,D,'N','D','ITEM')
    struct.pack_into('<I',d,24,dbase)
    return bytes(d[:nb_end(d,end)])
def nb_end(d,end):
    return end
def patch_item2(d):
    n,N,D=mdata.item(d);size=len(d)
    nd,dbase,end=rebuild_tables(d,n,N,D,'N','D','ITEM')
    struct.pack_into('<I',nd,24,dbase)
    out=bytes(nd[:end]);return out.ljust(max(size,len(out)),b'\0') if len(out)<=size else out
def patch_magic(d):
    n,N,D=mdata.magic(d);size=len(d)
    nd,dbase,end=rebuild_tables(d,n,N,D,'N','D','MAGIC')
    struct.pack_into('<I',nd,20,dbase)
    rest=bytes(d[0x2000:]) if len(d)>0x2000 else b''
    body=bytes(nd[:end])
    if len(body)>0x2000: raise SystemExit('MAGIC 넘침')
    return body.ljust(0x2000,b'\0')+rest
def patch_enemy(d):
    d=bytearray(d);tr=MN['ENEMY']
    for k in range(mdata.ENEMYN):
        key=f'E{k}'
        if key not in tr: continue
        v=enc(tr[key])
        if len(v)>16: log('적 이름 넘침',key,tr[key]);v=v[:16]
        o=mdata.ENEMY0+k*mdata.ENEMYSTRIDE+2
        d[o:o+16]=v.ljust(16,b'\0')
    return bytes(d)
def patch_will(d):
    d=bytearray(d);tr=MN['WILL_D']
    vals,uniq,strs=mdata.will(bytes(d))
    region=bytearray();newv={}
    for i,v in enumerate(uniq):
        k=f'W{i}';s=enc(tr[k]) if k in tr else strs[v]
        newv[v]=len(region);region+=s+b'\0'
    cap=mdata.WILL_TAB-mdata.WILL_BASE
    if len(region)>cap: raise SystemExit(f'WILL_D 넘침 {len(region)}>{cap}')
    d[mdata.WILL_BASE:mdata.WILL_TAB]=bytes(region).ljust(cap,b'\0')
    for j,v in enumerate(vals): struct.pack_into('<I',d,mdata.WILL_TAB+4*j,newv[v])
    return bytes(d)
def patch_inplace(d,name):
    d=bytearray(d);src={}
    for l in open(f'text/msrc/{name if name!="exe" else "exe_all"}.tsv',encoding='utf-8'):
        o,n,s=l.rstrip('\n').split('\t',2);src[o]=(int(o,16),int(n))
    for k,v in MN[name].items():
        if k not in src: log('위치 없음',name,k);continue
        o,slot=src[k];b=enc(v)
        if len(b)+1>slot: log('넘침',name,k,len(b)+1,'>',slot,v);b=b[:slot-1]
        d[o:o+slot]=b.ljust(slot,b'\0')
    return bytes(d)

# ---------------- 메인 ----------------
def main():
    t0=time.time()
    L=fat_load()
    disc=Disc(SRC_BIN)
    files={p:(l,s) for p,l,s,_,_ in disc.walk()}
    alba,asz=files['/ASDATA.BIN']
    newfiles=[]
    for nm,s,c in L:
        d=open('ext/'+nm,'rb').read()
        nd=None
        if d[:4]==b'$ASS': nd=patch_ass(d)
        elif nm=='KANJI': nd=build_font(d)
        elif nm=='ITEM': nd=patch_item2(d)
        elif nm=='MAGIC': nd=patch_magic(d)
        elif nm=='ENEMY': nd=patch_enemy(d)
        elif nm=='WILL_D': nd=patch_will(d)
        elif nm in ('P_LOD','P_WLD'): nd=patch_inplace(d,nm)
        if nm in gfxall.JOBS: nd=gfxall.apply(nm,nd if nd is not None else d)
        if nd is not None and nd!=d:
            nc=(len(nd)+2047)//2048
            if nc>c: log('크기 증가',nm,c,'->',nc)
            if d[:4]==b'$ASS' and nc>10: raise SystemExit(f'{nm} 10섹터 초과')
            newfiles.append((nm,s,c,nd.ljust(max(nc,1)*2048,b'\0'),max(nc,1)))
        else: newfiles.append((nm,s,c,None,c))
    total=sum(x[4] for x in newfiles)
    log('ASDATA 섹터',asz//2048,'->',total)
    # 출력 디스크 준비
    shutil.copyfile(SRC_BIN,OUT_BIN)
    src=open(SRC_BIN,'rb');out=open(OUT_BIN,'r+b')
    end=os.path.getsize(SRC_BIN)//SEC
    newlba=alba if total<=asz//2048 else end
    bcd=lambda x:((x//10)<<4)|(x%10)
    def msf(lba):
        l=lba+150;return bytes([bcd(l//4500),bcd((l//75)%60),bcd(l%75),2])
    lba=newlba;cnt=0
    for nm,s,c,nd,nc in newfiles:
        for i in range(nc):
            last=(cnt==total-1)
            if nd is None:
                src.seek((alba+s+i)*SEC);sec=bytearray(src.read(SEC))
                sm=sec[18]
                if last!=(sm==0x89) :
                    sec[16:24]=bytes([0,0,0x89 if last else 8,0]*2);sec[24:2072]=sec[24:2072];form1(sec)
                sec[12:16]=msf(lba)
            else:
                sec=bytearray(SEC);sec[0:12]=b'\x00'+b'\xff'*10+b'\x00';sec[12:16]=msf(lba)
                sm=0x89 if last else 0x08
                sec[16:24]=bytes([0,0,sm,0,0,0,sm,0]);sec[24:2072]=nd[i*2048:(i+1)*2048];form1(sec)
            out.seek(lba*SEC);out.write(sec);lba+=1;cnt+=1
    out.close()
    # FAT, 실행파일, 디렉터리
    from disc import Writer
    w=Writer(OUT_BIN)
    if newlba!=alba: w.end=lba
    w._update_dir('/ASDATA.BIN',newlba,total*2048)
    fat=bytearray(open('orig/ASDATA.FAT','rb').read())
    for k,(nm,s,c,nd,nc) in enumerate(newfiles): struct.pack_into('<H',fat,k*10+8,nc)
    w.replace('/ASDATA.FAT',bytes(fat),allow_move=False)
    exe=bytearray(patch_inplace(open('orig/SLPS_026.40','rb').read(),'exe'))
    # 글자 출력 루틴: 표에 없는 코드('! ' 반각 공백)는 6px 공백으로 (메뉴의 '!'+' '는 원래 8px 공백)
    import spacepatch; spacepatch.apply(exe)
    exe=bytes(exe)
    w.replace('/SLPS_026.40',exe,allow_move=False)
    w.f.close()
    log('번역 없는 대사',len(miss))
    LOG.close()
    print('완료',OUT_BIN,f'{time.time()-t0:.0f}초')
if __name__=='__main__': main()
