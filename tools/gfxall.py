# 모든 그래픽 한글화 작업 목록. build.py가 apply(파일명, 데이터)를 호출
import sys,os
sys.path.insert(0,os.path.dirname(__file__))
import gfx
from gfx import tims
from gfx2 import draw_aa,draw_style,draw_replace
S,G7,G9='serif','g7','g9'
FN=['어둠의 숲','도적의 아지트','타스타리 마을','북쪽 동굴']+\
   [('어둠의 유적','－1층－')]+[('어둠의 유적',f'－지하 {i}층－') for i in range(1,7)]+\
   ['구름다리','생명의 신전','사요히메의 방','츠루노히메의 방','츠키카게의 방','코란 마을']+\
   [('빛의 신전',f'－{i}층－') for i in (1,2,3)]+[('빛의 신전','－지하 1층－')]+\
   ['영수의 숲','아마르하라 고원']+[('천공의 신전',f'－{i}층－') for i in range(1,10)]+\
   ['6층 · 상계기 발착장','7층 · 분수의 방','8층 · 분수의 방','수도 엔가','성채도시 가르바렌']+\
   [('불의 신전',f'－{i}층－') for i in (1,2,3)]+[('불의 신전','－지하 1층－'),'불의 신전 · 대광간']+\
   [('불의 신전 · 지하 회랑',x) for x in ('－1층－','－2층－','－지하 1층－','－지하 2층－')]+\
   ['성산 볼자르','탄식의 계곡','쿠아라 마을','대지의 신전','하라스 마을','카루 호숫가 동굴','짐승의 계곡','투기장','프롤로그',
    '제1장　각자의 여행길','제2장　두 개의 만남','제3장　저항하는 의지','제4장　시련과 숙명','제5장　사투의 끝에',
    '제6장　암전, 그리고…','제7장　신인의 유전','신왕의 방','천상문의 방','무기점','대장간','도구점','잡화점','여관','지식고']
assert len(FN)==70,len(FN)
def fname(d):
    T=tims(d)
    for i,s in enumerate(FN):
        L=[(s,'serifm',21)] if isinstance(s,str) else [(s[0],'serifm',19),(s[1],'serifm',11)]
        for half in (0,32): draw_aa(d,T[i],(0,half,256,32),L,italic=0.3)
POP={17:'순발력↗',18:'순발력↘',19:'방어력↗',20:'공격력↗',21:'경직',22:'독',23:'혼란',24:'신위봉인',25:'도구봉인',26:'투명',27:'신위방어'}
def init(d):
    T=tims(d)
    for i,s in POP.items(): draw_style(d,T[i],(0,0,64,8),[(s,G7,8)],outline=0,pad=0,thr=128)
    draw_style(d,T[54],(0,0,24,8),[('도움말',G7,8)],outline=0,pad=0,thr=128)
    for i,s in {57:'남',58:'북',59:'서',60:'동'}.items(): draw_aa(d,T[i],(0,0,8,12),[(s,G7,8)],pad=0,thr=128)
    for i,s in {70:'공',71:'방',72:'신',73:'순',74:'체'}.items(): draw_replace(d,T[i],(1,1,10,10),[(s,G9,10)])
    draw_replace(d,T[75],(2,2,12,12),[('장',G9,10)])
    for i,s in {45:'획득 경험치',46:'전리품',47:'레벨 업',48:'전투 승리'}.items():
        t=T[i];draw_style(d,t,(0,0,t['w']*4,24),[(s,'serifeb',22)],italic=0.3,outline=1)
    for i,s in {76:'공',172:'수',175:'집',176:'산'}.items(): draw_replace(d,T[i],(3,3,26,26),[(s,'serifeb',24)],outline=1,thr=110,lumthr='mid')
def will(d):
    T=tims(d)
    draw_style(d,T[0],(0,0,128,24),[('전투 결과','serifeb',20)],outline=1)
    for k,s in enumerate(['호감','혐오','신뢰','불신']): draw_aa(d,T[11],(0,k*16,32,16),[(s,S,14)],italic=0.2)
def wmap(d):
    T=tims(d)
    for i,s in gfx.WMAP.items(): gfx.relabel(d,T[i],[s],16,14)
def mind(d):
    T=tims(d)
    gfx.relabel(d,T[7],['동료','개인','질서','혼돈'],16,15,'center')
    gfx.relabel(d,T[8],['카가토','후시','슈온','유','키리하','츠키카게','츠루노히메','사요히메'],24,20,'center')
def kham(d):
    # 화면에서 가로로 약 1/3.5 압축되어 표시되므로 가로로 늘려 그림
    from gfx2 import line_img,lum
    from gfx import pal,rgb
    from PIL import Image
    T=tims(d);t=T[3];W,px=gfx.getpix(d,t);px=[[0]*len(r) for r in px]
    P=[rgb(v) for v in pal(d,t)]
    for cx,ch in zip((100,170,250,325),'카무라이'):
        im=line_img(ch,'serifeb',40).resize((22,8),Image.LANCZOS)
        for y in range(8):
            for x in range(22):
                a=im.getpixel((x,y))/255
                if a<0.25: continue
                L=60+180*a
                px[y][cx-11+x]=min(range(1,16),key=lambda k:abs(lum(P[k])-L))
    gfx.setpix(d,t,px)
JOBS={'KHAM_T':kham,'FNAME':fname,'INIT':init,'WILL_D':will,'WMAP_T':wmap,'MIND_T':mind}
def apply(nm,data):
    if nm not in JOBS: return data
    d=bytearray(data);JOBS[nm](d);return bytes(d)
