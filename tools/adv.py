# 대사 넘기기 n회, 매 k회마다 스크린샷 → 시트. python adv.py 출력폴더 n k
import sys,subprocess,os
from PIL import Image
S,n,k=sys.argv[1],int(sys.argv[2]),int(sys.argv[3])
C=os.path.join(os.path.dirname(__file__),'c.py');fs=[]
for i in range(n):
    cmd='k sq 0.12;w 0.35;k o 0.12;w 1.2'
    if (i+1)%k==0:
        p=f'{S}/adv{i}.png'
        if os.path.exists(p): os.remove(p)
        cmd+=f';shot {p}'
        subprocess.run(['python',C,cmd],capture_output=True)
        if os.path.exists(p): fs.append(p)
    else: subprocess.run(['python',C,cmd],capture_output=True)
W,H=480,383;cols=2;rows=(len(fs)+1)//2
c=Image.new('RGB',(W*cols,H*max(rows,1)))
for i,f in enumerate(fs): c.paste(Image.open(f).resize((W,H)),((i%cols)*W,(i//cols)*H));os.remove(f)
c.save(f'{S}/sheet.png');print(len(fs))
