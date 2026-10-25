#!/usr/bin/env python3
"""친정엄마 살림노트 이미지 생성기.
사용법: python3 tools/make_images.py specs/<파일>.json
spec 형식:
{"posts":[{"slug":"gaseupgi",
  "thumb":{"tag":"가습기 청소","lines":["가습기 청소","물만 갈아도 절반"],"hl":"절반","sub":"매일 물 갈기부터","emoji":"💧","tape":"MINT","note":"YEL"},
  "cards":[{"title":["물은 매일","새로 갈아요"],"bullets":["...","..."],"emoji":"🚰","v":"dot|num|warn","note":"PINK"}]}],
 "threads":[{"slug":"t1026-boiler","tag":"보일러","lines":["보일러","미리 켜 봐"],"hl":"미리","sub":"추워지기 전에 점검","emoji":"🔥","tape":"YEL","note":"PINK"}]}
출력: thumbs/<slug>.jpg, cards_v2/<slug><번호>.jpg, threads/<slug>.jpg
주의: 가운뎃점(·) 등 일부 기호는 폰트에 없어 네모로 나옴. '과/와'나 쉼표를 쓸 것.
"""
import os, sys, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FD=os.path.join(ROOT,'tools','fonts')
OUT=None
W=H=1080
def BH(s): return ImageFont.truetype(f'{FD}/BlackHanSans-Regular.ttf', s)
def JU(s): return ImageFont.truetype(f'{FD}/Jua-Regular.ttf', s)
EMO=ImageFont.truetype(os.path.join(FD,'NotoColorEmoji.ttf'),109)
INK=(40,34,30); SUB=(112,100,90); ACC=(238,96,112)
PINK=(255,214,222); YEL=(255,238,160); BLUE=(210,232,255); MINT=(210,242,226)
def emoji(ch,size,outline=10,rot=0):
    im=Image.new('RGBA',(160,160),(0,0,0,0)); ImageDraw.Draw(im).text((80,80),ch,font=EMO,embedded_color=True,anchor='mm')
    im=im.crop(im.getbbox()).resize((size,size),Image.LANCZOS)
    pad=outline+4; big=Image.new('RGBA',(size+pad*2,size+pad*2),(0,0,0,0)); big.paste(im,(pad,pad),im)
    a=big.split()[3].filter(ImageFilter.MaxFilter(outline*2+1))
    white=Image.new('RGBA',big.size,(255,255,255,255)); white.putalpha(a)
    sh=Image.new('RGBA',big.size,(0,0,0,0)); sh.putalpha(a.point(lambda v:v*0.18).filter(ImageFilter.GaussianBlur(6)))
    out=Image.new('RGBA',(big.width+12,big.height+12),(0,0,0,0)); out.alpha_composite(sh,(8,10)); out.alpha_composite(white,(0,0)); out.alpha_composite(big,(0,0))
    return out.rotate(rot,expand=True,resample=Image.BICUBIC) if rot else out
def P(c,im,xy): c.alpha_composite(im,(int(xy[0]),int(xy[1])))
def bg():
    c=Image.new('RGBA',(W,H),(252,249,243,255)); d=ImageDraw.Draw(c)
    for x in range(0,W,42): d.line([(x,0),(x,H)],fill=(238,231,218),width=2)
    for y in range(0,H,42): d.line([(0,y),(W,y)],fill=(238,231,218),width=2)
    return c
def tape(c,x,y,w,h,col,rot):
    t=Image.new('RGBA',(w,h),col+(185,)); dt=ImageDraw.Draw(t)
    for i in range(0,w,18): dt.line([(i,0),(i,h)],fill=(255,255,255,45),width=6)
    P(c,t.rotate(rot,expand=True,resample=Image.BICUBIC),(x,y))
def hl(c,box,col=(255,222,89),rot=-1.2):
    x0,y0,x1,y1=[int(v) for v in box]
    m=Image.new('RGBA',(x1-x0+40,y1-y0+40),(0,0,0,0)); ImageDraw.Draw(m).rounded_rectangle([20,20,20+x1-x0,20+y1-y0],12,fill=col+(235,))
    P(c,m.rotate(rot,resample=Image.BICUBIC),(x0-20,y0-20))
def note(c,box,col,rot=0,r=20):
    x0,y0,x1,y1=box; w,h=x1-x0,y1-y0
    n=Image.new('RGBA',(w+60,h+60),(0,0,0,0)); dn=ImageDraw.Draw(n)
    dn.rounded_rectangle([34,40,34+w,40+h],r,fill=(0,0,0,34)); n=n.filter(ImageFilter.GaussianBlur(8))
    ImageDraw.Draw(n).rounded_rectangle([30,30,30+w,30+h],r,fill=col+(255,))
    P(c,n.rotate(rot,resample=Image.BICUBIC),(x0-30,y0-30))
def thumb(name,tag,lines,hlword,sub,emo,tapecol,notecol):
    c=bg(); d=ImageDraw.Draw(c)
    tape(c,30,26,260,60,tapecol,-7); tape(c,60,960,240,56,BLUE,-4)
    tw=d.textlength(tag,font=JU(40)); d.rounded_rectangle([64,120,64+tw+56,188],34,fill=ACC); d.text((92,128),tag,font=JU(40),fill='white')
    size=124
    while max(d.textlength(l,font=BH(size)) for l in lines)>900: size-=4
    y=300
    for l in lines:
        if hlword and hlword in l:
            pre=l.split(hlword)[0]; x0=56+d.textlength(pre,font=BH(size)); x1=x0+d.textlength(hlword,font=BH(size))
            hl(c,(x0-6,y+size*0.42,x1+10,y+size*1.12)); d=ImageDraw.Draw(c)
        d.text((56,y),l,font=BH(size),fill=INK); y+=int(size*1.28)
    note(c,(64,y+40,W-64,y+40+150),notecol,-1); d=ImageDraw.Draw(c)
    s2=44
    while d.textlength(sub,font=JU(s2))>860: s2-=2
    d.text((110,y+40+48),sub,font=JU(s2),fill=INK)
    P(c,emoji(emo,300,14,8),(690,690))
    d=ImageDraw.Draw(c); d.text((64,H-96),'친정엄마 살림노트',font=JU(36),fill=SUB)
    c.convert('RGB').save(f'{OUT}/{name}.jpg',quality=92)
    return c.convert('RGB')
RED=(226,68,68); REDBG=(255,225,222)
def card(name,tag,num,title_lines,bullets,emo,tapecol,notecol,v='dot'):
    c=bg(); d=ImageDraw.Draw(c)
    tape(c,30,26,260,60,tapecol,-7)
    acc=RED if v=='warn' else ACC
    if v=='warn': notecol=REDBG
    tw=d.textlength(tag,font=JU(40)); d.rounded_rectangle([64,120,64+tw+56,188],34,fill=acc); d.text((92,128),tag,font=JU(40),fill='white')
    P(c,emoji(emo,210,12,8),(790,40)); d=ImageDraw.Draw(c)
    d.text((64,236),f'POINT {num}',font=BH(48),fill=acc)
    size=112 if len(bullets)<4 else 92
    while max(d.textlength(l,font=BH(size)) for l in title_lines)>930: size-=4
    y=310
    for l in title_lines:
        d.text((56,y),l,font=BH(size),fill=RED if v=='warn' else INK); y+=int(size*1.24)
    y+=26
    n=len(bullets); RH=min(118,int((945-y-40)/n)); h=40+n*RH
    note(c,(64,y,W-64,y+h),notecol,-0.6); d=ImageDraw.Draw(c)
    by=y+30
    for i,b in enumerate(bullets):
        fs=min(56,RH-30)
        while d.textlength(b,font=JU(fs))>770: fs-=2
        if v=='num':
            d.ellipse([96,by+4,96+54,by+4+54],fill=INK); d.text((123,by+31),str(i+1),font=BH(38),fill='white',anchor='mm')
        else:
            d.ellipse([100,by+22,100+26,by+22+26],fill=acc)
        d.text((178,by),b,font=JU(fs),fill=INK); by+=RH
    d.text((64,H-84),'친정엄마 살림노트',font=JU(34),fill=SUB)
    c.convert('RGB').save(f'{OUT}/{name}.jpg',quality=92)
    return c.convert('RGB')

COL={'PINK':PINK,'YEL':YEL,'BLUE':BLUE,'MINT':MINT}
def main(path):
    global OUT
    spec=json.load(open(path,encoding='utf-8')); made=[]
    for p in spec.get('posts',[]):
        th=p['thumb']; OUT=os.path.join(ROOT,'thumbs'); os.makedirs(OUT,exist_ok=True)
        thumb(p['slug'],th['tag'],th['lines'],th.get('hl'),th['sub'],th['emoji'],COL[th.get('tape','PINK')],COL[th.get('note','YEL')])
        made.append(f"thumbs/{p['slug']}.jpg")
        OUT=os.path.join(ROOT,'cards_v2'); os.makedirs(OUT,exist_ok=True)
        for i,cd in enumerate(p.get('cards',[]),1):
            card(f"{p['slug']}{i}",th['tag'],i,cd['title'],cd['bullets'],cd['emoji'],COL[th.get('tape','PINK')],COL[cd.get('note','YEL')],cd.get('v','dot'))
            made.append(f"cards_v2/{p['slug']}{i}.jpg")
    for th in spec.get('threads',[]):
        OUT=os.path.join(ROOT,'threads'); os.makedirs(OUT,exist_ok=True)
        thumb(th['slug'],th['tag'],th['lines'],th.get('hl'),th['sub'],th['emoji'],COL[th.get('tape','PINK')],COL[th.get('note','YEL')])
        made.append(f"threads/{th['slug']}.jpg")
    print('\n'.join(made))
if __name__=='__main__': main(sys.argv[1])
