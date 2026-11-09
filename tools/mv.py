# python mv.py 출력폴더 "명령1|명령2|..." → 각 명령 후 스크린샷, 시트
import sys,subprocess,os
from PIL import Image
S=sys.argv[1];cmds=sys.argv[2].split('|');C=os.path.join(os.path.dirname(__file__),'c.py');fs=[]
for i,c in enumerate(cmds):
    p=f'{S}/mv{i}.png'
    if os.path.exists(p): os.remove(p)
    subprocess.run(['python',C,f'{c};w 0.4;shot {p}'],capture_output=True)
    fs.append(p if os.path.exists(p) else None)
W,H=480,383;cols=2 if len(cmds)<=4 else 3;rows=(len(cmds)+cols-1)//cols
o=Image.new('RGB',(W*cols,H*rows))
for i,f in enumerate(fs):
    if f: o.paste(Image.open(f).resize((W,H)),((i%cols)*W,(i//cols)*H));os.remove(f)
o.save(f'{S}/sheet.png')
