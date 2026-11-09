# 대사창 줄 재배치: 같은 대사(연속 줄)의 단어를 옮겨 각 줄을 LIM자 이내로
import re
LIM=17
TOK=re.compile(r'%M\d.*?%M\d|%[A-Za-z]\d|%|.',re.S)
def vis(s): return sum(1 for t in TOK.findall(s) if len(t)==1 and t!='%')
def body(s):
    """(머리코드, 본문, 꼬리%) 분리"""
    m=re.match(r'((?:%M\d.*?%M\d|%[A-Za-z]\d)*)(.*?)(%?)$',s,re.S)
    return m.group(1),m.group(2),m.group(3)
def cont(a,b):
    if not a.endswith('%') or a.endswith('」%') or a.endswith('』%'): return False
    h,bd,_=body(b)
    if '%M' in h: return False
    return not bd.startswith(('「','『'))
def words(bd): return bd.split('\x01')
def fill(ws,n):
    """단어열을 n줄에 탐욕 배치, 실패 시 None"""
    lines=[[] for _ in range(n)];k=0
    for w in ws:
        while k<n:
            cur='\x01'.join(lines[k]+[w])
            if vis(cur)<=LIM or not lines[k]:
                if vis(cur)>LIM: return None
                lines[k].append(w);break
            k+=1
        if k>=n: return None
    return ['\x01'.join(l) for l in lines]
def reflow(KO,order,link=lambda a,b:b==a+1):
    """KO: idx->정규화 문자열. order: 원래 순서의 idx 목록. 변경 수 반환"""
    ch=0;i=0;order=list(order)
    while i<len(order):
        j=i
        while j+1<len(order) and link(order[j],order[j+1]) and order[j] in KO and order[j+1] in KO and cont(KO[order[j]],KO[order[j+1]]): j+=1
        grp=order[i:j+1]
        if any(vis(KO[x])>LIM for x in grp if x in KO) and len(grp)>1:
            parts=[body(KO[x]) for x in grp]
            ws=[]
            for h,bd,t in parts: ws+=words(bd)
            res=fill(ws,len(grp))
            if res and all(r for r in res):
                for x,(h,bd,t),r in zip(grp,parts,res): KO[x]=h+r+t
                ch+=1
        i=j+1
    return ch
def split_single(KO,order,link=lambda a,b:b==a+1):
    """다른 줄과 이어지지 않는 단독 줄이 17자를 넘으면 균형 잡힌 공백 위치에 줄바꿈 삽입"""
    order=list(order);s=set(order);n=0
    for x in order:
        v=KO[x]
        if vis(v)<=LIM or '\n' in v: continue
        if (x-1 in s and link(x-1,x) and cont(KO[x-1],v)) or (x+1 in s and link(x,x+1) and cont(v,KO[x+1])): continue
        h,bd,t=body(v)
        ws=bd.split('\x01')
        best=None
        for k in range(1,len(ws)):
            a='\x01'.join(ws[:k]);b='\x01'.join(ws[k:])
            if vis(a)<=LIM and vis(b)<=LIM-1:
                sc=abs(vis(a)-vis(b)-1)
                if best is None or sc<best[0]: best=(sc,a,b)
        if best: KO[x]=h+best[1]+'\n'+best[2]+t;n+=1
    return n
