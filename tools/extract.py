# 스크립트 대사 추출: text/ja.json (고유 줄 목록), text/src/sNN.tsv
import sys,os,re,json;sys.path.insert(0,os.path.dirname(__file__))
from fat import load;import ass
JP=re.compile(rb'[\x81-\x9f\xe0-\xef]')
L=load();U={};order=[];where={}
for nm,s,c in L:
    d=open('ext/'+nm,'rb').read()
    for o,t,n,offs,strs in ass.find(d):
        for x in strs:
            if not JP.search(x): continue
            if x not in U: U[x]=len(order);order.append(x);where[x]=nm
ja=[x.decode('cp932') for x in order]
json.dump(ja,open('text/ja.json','w',encoding='utf-8'),ensure_ascii=False,indent=0)
# 청크: 파일 경계 유지, ~1000줄
chunks=[];cur=[];last=None
for i,x in enumerate(order):
    if len(cur)>=1000 and where[x]!=last: chunks.append(cur);cur=[]
    cur.append(i);last=where[x]
chunks.append(cur)
for k,ch in enumerate(chunks):
    with open(f'text/src/s{k:02d}.tsv','w',encoding='utf-8') as f:
        lastf=None
        for i in ch:
            if where[order[i]]!=lastf: f.write(f'#FILE {where[order[i]]}\n');lastf=where[order[i]]
            f.write(f'{i}\t{ja[i]}\n')
print(len(order),len(chunks))
