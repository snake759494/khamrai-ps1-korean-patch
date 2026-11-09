import sys,subprocess,os
from PIL import Image
S=sys.argv[1];n=int(sys.argv[2]);cmd=sys.argv[3] if len(sys.argv)>3 else 'k o 0.2;w 2'
fs=[]
for i in range(n):
    p=f'{S}/q{i}.png'
    if os.path.exists(p): os.remove(p)
    subprocess.run(['python',os.path.join(os.path.dirname(__file__),'c.py'),f'{cmd};shot {p}'],capture_output=True)
    if os.path.exists(p): fs.append(p)
W=640;H=511;cols=2;rows=(len(fs)+1)//2
c=Image.new('RGB',(W*cols,H*rows))
for i,f in enumerate(fs): c.paste(Image.open(f).resize((W,H)),((i%cols)*W,(i//cols)*H))
c.save(f'{S}/sheet.png');print(len(fs))
