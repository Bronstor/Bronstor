import os, subprocess
from lockup import horiz, vert
from em3 import mark, R, K, W
UB='Unbounded-ExtraBold.ttf'
OUT='/home/user/Bronstor/marca/rediseno-v2/logo'
for sub in ['svg','png','para-gemini']: os.makedirs(f'{OUT}/{sub}', exist_ok=True)
RENDER=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','build','render.js')
def svg(body,b,pad,bg=None):
    x0,y0,x1,y1=b; w=x1-x0+2*pad; h=y1-y0+2*pad
    r=f'<rect x="{x0-pad:.1f}" y="{y0-pad:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{bg}"/>' if bg else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0-pad:.1f} {y0-pad:.1f} {w:.1f} {h:.1f}" width="{w:.0f}" height="{h:.0f}">{r}{body}</svg>',w,h
def png(svgtext,path,w,h,px,transp):
    tmp=path+'.tmp.svg'; open(tmp,'w').write(svgtext)
    subprocess.run(['node',RENDER,tmp,path,str(round(w)),str(round(h)),f'{px/w:.4f}','1' if transp else '0'],check=True); os.remove(tmp)
items={
 'logo-horizontal':horiz(UB,False),
 'logo-horizontal-negativo':horiz(UB,True),
 'logo-vertical':vert(UB,False),
 'logo-vertical-negativo':vert(UB,True),
 'simbolo':mark(s=200,cE=K,cM=R),
 'simbolo-negativo':mark(s=200,cE=W,cM=R),
 'simbolo-sobre-rojo':mark(s=200,cE=W,cM=K),
}
for name,(body,b) in items.items():
    pad=(b[3]-b[1])*0.15
    s,w,h=svg(body,b,pad); open(f'{OUT}/svg/{name}.svg','w').write(s)
    png(s,f'{OUT}/png/{name}.png',w,h,2400,True)
G=f'{OUT}/para-gemini'
for fname,key,bg in [('1-simbolo-sobre-negro','simbolo-negativo',K),('2-simbolo-sobre-blanco','simbolo',W),
                     ('3-logo-horizontal-sobre-blanco','logo-horizontal',W),('4-logo-horizontal-sobre-negro','logo-horizontal-negativo',K)]:
    body,b=items[key]; pad=(b[3]-b[1])*0.35
    s,w,h=svg(body,b,pad,bg); png(s,f'{G}/{fname}.png',w,h,2000,False)
print('ok')
