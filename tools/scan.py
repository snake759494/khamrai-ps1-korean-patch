import sys,re
pat=re.compile(rb'(?:[\x82\x83][\x40-\xfc]|[\x88-\x9f\xe0-\xea][\x40-\xfc]|\x81[\x40-\xac]|[\x20-\x7e]){3,}')
def strs(d):
    for m in pat.finditer(d):
        t=m.group().decode('cp932','replace')
        if re.search('[ぁ-んァ-ン一-龥]',t): yield m.start(),t
if __name__=='__main__':
    for nm in sys.argv[1:]:
        d=open('ext/'+nm,'rb').read()
        for o,t in list(strs(d))[:int(sys.argv[0:1] and 25)]: print(nm,hex(o),t[:60])
