# 사용: python tools/rfcheck.py text/rf/outN.tsv  → 17자 초과 줄과 형식 오류 출력
import sys,re,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
TOK=re.compile(r'%M\d.*?%M\d|%[A-Za-z]\d|%|.')
def vis(s): return sum(1 for t in TOK.findall(s) if len(t)==1 and t!='%')
src={}
for k in range(6):
    try:
        for l in open(f'text/rf/in{k}.txt',encoding='utf-8'):
            if '\t' in l: a,b,_=l.split('\t',2); src[a]=b
    except FileNotFoundError: pass
bad=0;n=0
for l in open(sys.argv[1],encoding='utf-8'):
    l=l.rstrip('\n')
    if not l: continue
    n+=1
    try: k,v=l.split('\t',1)
    except ValueError: print('형식 오류:',l);bad+=1;continue
    if k not in src: print('없는 번호',k);bad+=1;continue
    o=src[k]
    if vis(v)>17: print(f'{k} {vis(v)}자 초과: {v}');bad+=1
    if o.endswith('%')!=v.endswith('%'): print(k,'끝 % 불일치');bad+=1
    if re.findall(r'%[A-Za-z]\d',o)!=re.findall(r'%[A-Za-z]\d',v): print(k,'제어코드 불일치',v);bad+=1
print('줄',n,'문제',bad)
