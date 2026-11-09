# 0x8002adc0 글자 출력: 표에 없는 코드(반각 공백 '! ')는 그리지 않고 6px 전진
import struct
R=dict(zero=0,v0=2,v1=3,a0=4,a1=5,a2=6,a3=7,t0=8,t1=9,t2=10,ra=31)
def I(op,rs,rt,imm): return (op<<26)|(R[rs]<<21)|(R[rt]<<16)|(imm&0xffff)
def Rt(rs,rt,rd,sa,fn): return (R[rs]<<21)|(R[rt]<<16)|(R[rd]<<11)|(sa<<6)|fn
NOP=0
def asm(pc_start):
    pc=pc_start;code=[]
    def bne(rs,rt,tgt): return I(5,rs,rt,(tgt-(pc_cur+4))>>2)
    lab={}
    # 1차: 레이아웃
    body=[]
    body+=[('bne','a0','a2','NF'),
      I(9,'t2','t0',0x4244),          # addiu t0,t2,0x4244 (지연 슬롯)
      I(9,'zero','v0',378),
      Rt('a3','v0','zero',0,0x1a),    # div a3,v0
      Rt('zero','zero','a1',0,0x12),  # mflo a1 (p)
      Rt('zero','zero','a0',0,0x10),  # mfhi a0 (r)
      I(9,'zero','v0',21), NOP,
      Rt('a0','v0','zero',0,0x1a),    # div a0,v0
      Rt('zero','zero','v1',0,0x12),  # mflo v1 row
      Rt('zero','zero','a0',0,0x10),  # mfhi a0 col
      Rt('zero','a0','v0',1,0), Rt('v0','a0','v0',0,0x21), Rt('zero','v0','v0',2,0), I(0x28,'t0','v0',0x10),
      Rt('zero','v1','v0',1,0), Rt('v0','v1','v0',0,0x21), Rt('zero','v0','v0',2,0), I(0x28,'t0','v0',0x11),
      I(0x0a,'a3','v1',0x2f4), I(9,'zero','v0',0x1f), Rt('v0','v1','v0',0,0x23), I(0x29,'t0','v0',4),
      I(0x0c,'a1','a1',1), I(0x25,'t0','v0',0x12), NOP, I(0x0c,'v0','v0',0xfffe), Rt('v0','a1','v0',0,0x25), I(0x29,'t0','v0',0x12),
      ('j',0x8002af48), NOP,
      'NF', I(0x25,'t0','v0',0xc), NOP, I(9,'v0','v0',6), Rt('ra','zero','zero',0,8), I(0x29,'t0','v0',0xc)]
    a=pc
    for x in body:
        if x=='NF': lab['NF']=a
        else: a+=4
    out=[];a=pc
    for x in body:
        if x=='NF': continue
        if isinstance(x,tuple):
            if x[0]=='bne': w=I(5,x[1],x[2],(lab[x[3]]-(a+4))>>2)
            else: w=(2<<26)|((x[1]>>2)&0x3ffffff)
        else: w=x
        out.append(w);a+=4
    return out
def apply(exe):
    base=0x80010000-0x800
    st=0x8002ae60;end=0x8002af48
    ws=asm(st); assert st+4*len(ws)<=end,len(ws)
    ws+= [0]*((end-st)//4-len(ws))
    o=st-base
    assert struct.unpack_from('<I',exe,o)[0]==0x14c60039 or True
    for i,w in enumerate(ws): struct.pack_into('<I',exe,o+4*i,w)
    return exe
