import re,sys,os
sys.path.insert(0,os.path.dirname(__file__))
from charset import ALL
def tokens_ok_suffix(raw):
    # 뒤에서부터 유효 토큰만으로 된 가장 긴 접미부 시작 위치
    # 앞에서부터 파싱해 유효 구간 시작점 후보를 갱신
    i=0;start=0;n=len(raw)
    while i<n:
        b=raw[i]
        if i+1<n and (raw[i]<<8|raw[i+1]) in ALL: i+=2;continue
        if 0x20<=b<0x7f or b==10: i+=1;continue
        i+=1;start=i
    return start
def scan(d,lo,hi,minjp=1):
    out=[];i=lo
    while i<hi:
        if d[i]==0: i+=1;continue
        j=d.index(b'\0',i);raw=d[i:j];s0=tokens_ok_suffix(raw);a=i+s0
        try: s=d[a:j].decode('cp932')
        except: i=j+1;continue
        jp=len(re.findall('[\u3000-\u9fff\uff01-\uff60]',s))
        if jp>=minjp and (jp>=2 or len(s)<=3):
            k=j+1
            while k<len(d) and d[k]==0: k+=1
            out.append((a,k-a,s))
        i=j+1
    return out
