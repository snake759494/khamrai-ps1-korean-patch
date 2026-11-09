# 사용: python tools/check.py s00 [s01 ...]  -> 번역 파일 검사
import sys,re,os
os.chdir(os.path.join(os.path.dirname(__file__),'..'))
CODE=re.compile(r'%[A-Z][0-9]')
OKCH=set('「」『』、。・…～ー☆★（）＋－×％＿，,.!?：:　 ０１２３４５６７８９0123456789▲■△▼▽○□♪≫→←↑↓ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｇｈｉｍｎｏｒｗ―／~')
def vis(s): return CODE.sub('',s).rstrip('%')
bad=0
for k in sys.argv[1:]:
    src={};
    for l in open(f'text/src/{k}.tsv',encoding='utf-8'):
        if l.startswith('#'): continue
        i,t=l.rstrip('\n').split('\t',1);src[i]=t
    ko={}
    p=f'text/ko/{k}.tsv'
    if not os.path.exists(p): print(k,'번역 파일 없음');bad+=1;continue
    for n,l in enumerate(open(p,encoding='utf-8'),1):
        l=l.rstrip('\n')
        if not l or l.startswith('#'): continue
        if '\t' not in l: print(k,n,'탭 없음',l);bad+=1;continue
        i,t=l.split('\t',1)
        if i not in src: print(k,n,'없는 번호',i);bad+=1;continue
        ko[i]=t;j=src[i]
        if CODE.findall(j)!=CODE.findall(t): print(k,i,'제어코드 불일치',j,'|',t);bad+=1
        if j.endswith('%')!=t.endswith('%'): print(k,i,'끝 % 불일치',j,'|',t);bad+=1
        v=vis(t)
        if len(v)>22: print(k,i,'22자 초과',len(v),t);bad+=1
        for ch in v:
            if not('\uac00'<=ch<='\ud7a3' or ch in OKCH): print(k,i,'허용 안 되는 문자',repr(ch),t);bad+=1;break
    miss=[i for i in src if i not in ko]
    if miss: print(k,'누락',len(miss),miss[:20]);bad+=len(miss)
print('문제',bad)
