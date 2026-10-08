import os
from lockup import tp, horiz, vert
from em3 import mark, E_path, P, R, K, W
UB='Unbounded-ExtraBold.ttf'; UBR='Unbounded-Regular.ttf'; AR='ArchivoRegular.ttf'; MONO='PlexMono.ttf'
G='#8A8E95'

def fit(body, b, x, y, w, h, fill=0.8):
    bw=b[2]-b[0]; bh=b[3]-b[1]; sc=min(w*fill/bw, h*fill/bh)
    return f'<g transform="translate({x+(w-bw*sc)/2-b[0]*sc:.1f},{y+(h-bh*sc)/2-b[1]*sc:.1f}) scale({sc:.4f})">{body}</g>'

def concepto():
    Wd,Hd=1600,1000
    o=[f'<rect width="{Wd}" height="{Hd}" fill="#0E0E0F"/>']
    o.append(tp(MONO,'MULTIREPUESTO E&M · CONCEPTO DE MARCA',15,80,90,tracking=0.2,fill=G)[0])
    o.append(tp(UB,'LA E GIRADA',62,80,190,fill=W)[0])
    o.append(tp(UB,'ES LA M.',62,80,272,fill=R)[0])
    lines=['Dos dueños, una sola pieza. Las iniciales E y M son',
           'exactamente la misma forma: solo cambia su posición.',
           'Como un buen repuesto: la pieza exacta, en el lugar exacto.']
    for i,l in enumerate(lines):
        o.append(tp(AR,l,24,80,350+i*36,fill='#C9CCD1')[0])
    # secuencia E -> giro -> M = símbolo
    s=150; y0=560; d=E_path(s)
    o.append(f'<g transform="translate(80,{y0})"><path d="{d}" fill="{W}"/></g>')
    # flecha de giro
    cx,cy=330,y0+s/2
    o.append(f'<path d="M {cx-40} {cy-20} A 50 50 0 1 1 {cx+20} {cy+42}" fill="none" stroke="{R}" stroke-width="6"/>')
    o.append(f'<polygon points="{cx+4},{cy+52} {cx+34},{cy+30} {cx+30},{cy+58}" fill="{R}"/>')
    o.append(tp(MONO,'90°',20,cx,cy+8,anchor='middle',fill=R)[0])
    o.append(f'<g transform="translate({430+s},{y0}) rotate(90)"><path d="{d}" fill="{R}"/></g>')
    o.append(tp(UBR,'=',70,660,y0+s/2+26,anchor='middle',fill=G)[0])
    body,b=mark(s=s,cE=W)
    o.append(f'<g transform="translate(720,{y0})">{body}</g>')
    o.append(tp(MONO,'E',16,80+s/2,y0+s+40,anchor='middle',fill=G)[0])
    o.append(tp(MONO,'M',16,430+s/2,y0+s+40,anchor='middle',fill=G)[0])
    o.append(tp(MONO,'SÍMBOLO',16,720+b[2]/2,y0+s+40,anchor='middle',fill=G)[0])
    # construcción a la derecha
    s2=360; x2=1110; y2=330; T=P['t']*s2; g=(s2-3*T)/2
    o.append(tp(MONO,'CONSTRUCCIÓN',15,x2,y2-60,tracking=0.2,fill=G)[0])
    for v in [0,T,T+g,2*T+g,2*T+2*g,s2]:
        o.append(f'<line x1="{x2-40}" y1="{y2+v:.1f}" x2="{x2+s2+40}" y2="{y2+v:.1f}" stroke="#2C2D31" stroke-width="1.5"/>')
    for v in [0,T,s2]:
        o.append(f'<line x1="{x2+v:.1f}" y1="{y2-40}" x2="{x2+v:.1f}" y2="{y2+s2+40}" stroke="#2C2D31" stroke-width="1.5"/>')
    o.append(f'<g transform="translate({x2},{y2})"><path d="{E_path(s2)}" fill="{W}" fill-opacity="0.92"/></g>')
    # cotas
    def cota(xa,xb,y,lab,vert=False):
        a=f'<line x1="{xa:.1f}" y1="{y:.1f}" x2="{xb:.1f}" y2="{y:.1f}" stroke="{R}" stroke-width="2"/>'
        if not vert:
            a+=f'<line x1="{xa:.1f}" y1="{y-9}" x2="{xa:.1f}" y2="{y+9}" stroke="{R}" stroke-width="2"/><line x1="{xb:.1f}" y1="{y-9}" x2="{xb:.1f}" y2="{y+9}" stroke="{R}" stroke-width="2"/>'
        return a
    o.append(cota(x2,x2+s2,y2-22,''))
    o.append(tp(MONO,'1 MÓDULO',14,x2+s2/2,y2-32,anchor='middle',fill=R)[0])
    o.append(f'<line x1="{x2+s2+22}" y1="{y2}" x2="{x2+s2+22}" y2="{y2+T:.1f}" stroke="{R}" stroke-width="2"/>'
             f'<line x1="{x2+s2+13}" y1="{y2}" x2="{x2+s2+31}" y2="{y2}" stroke="{R}" stroke-width="2"/>'
             f'<line x1="{x2+s2+13}" y1="{y2+T:.1f}" x2="{x2+s2+31}" y2="{y2+T:.1f}" stroke="{R}" stroke-width="2"/>')
    o.append(tp(MONO,'0,29',14,x2+s2+40,y2+T/2+5,fill=R)[0])
    RO=P['ro']*T
    o.append(f'<circle cx="{x2+RO:.1f}" cy="{y2+s2-RO:.1f}" r="4" fill="{R}"/>'
             f'<line x1="{x2+RO:.1f}" y1="{y2+s2-RO:.1f}" x2="{x2+RO-RO*0.707:.1f}" y2="{y2+s2-RO+RO*0.707:.1f}" stroke="{R}" stroke-width="2"/>')
    o.append(tp(MONO,'R ESQUINA',14,x2-10,y2+s2+70,fill=R)[0])
    o.append(tp(MONO,'RANURAS CON EXTREMO SEMICIRCULAR, COMO UNA PIEZA FRESADA',13,x2-40,y2+s2+110,tracking=0.06,fill=G)[0])
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wd}" height="{Hd}" viewBox="0 0 {Wd} {Hd}">'+''.join(o)+'</svg>'

def sistema():
    Wd,Hd=1600,1000
    o=[f'<rect width="{Wd}" height="{Hd}" fill="#D9DADD"/>']
    body,b=horiz(UB,False); o.append(f'<rect x="40" y="40" width="1000" height="440" fill="{W}"/>'+fit(body,b,40,40,1000,440,0.78))
    o.append(tp(MONO,'LOGO PRINCIPAL',14,70,78,tracking=0.2,fill=G)[0])
    body,b=vert(UB,True); o.append(f'<rect x="1060" y="40" width="500" height="440" fill="{K}"/>'+fit(body,b,1060,60,500,420,0.7))
    o.append(tp(MONO,'VERTICAL',14,1090,78,tracking=0.2,fill=G)[0])
    tiles=[(R,W,K,'SOBRE ROJO'),(K,W,R,'SOBRE NEGRO'),(W,K,R,'SOBRE BLANCO')]
    for i,(bg,cE,cM,lab) in enumerate(tiles):
        x=40+i*340
        body,b=mark(s=100,cE=cE,cM=cM)
        o.append(f'<rect x="{x}" y="500" width="320" height="250" fill="{bg}"/>'+fit(body,b,x,515,320,235,0.62))
        o.append(tp(MONO,lab,13,x+20,530,tracking=0.2,fill=(W if bg!=W else G))[0])
    # ícono app
    x=1060
    o.append(f'<rect x="{x}" y="500" width="500" height="250" fill="#EDEDEE"/>')
    for j,(sz,bg) in enumerate([(150,K),(96,R),(64,K)]):
        xx=x+40+[0,190,320][j]; yy=520+(210-sz)/2
        body,b=mark(s=100,cE=W,cM=(R if bg==K else K))
        o.append(f'<rect x="{xx}" y="{yy:.0f}" width="{sz}" height="{sz}" rx="{sz*0.22:.0f}" fill="{bg}"/>'+fit(body,b,xx,yy,sz,sz,0.66))
    o.append(tp(MONO,'ÍCONO · PERFIL · APP',13,x+20,530,tracking=0.2,fill=G)[0])
    # fila inferior: una tinta + tamaños mínimos
    body,b=horiz(UB,False,cE=K); body=body.replace(R,K)
    o.append(f'<rect x="40" y="770" width="660" height="190" fill="{W}"/>'+fit(body,b,40,780,660,180,0.8))
    o.append(tp(MONO,'UNA TINTA',13,60,798,tracking=0.2,fill=G)[0])
    o.append(f'<rect x="720" y="770" width="840" height="190" fill="{W}"/>')
    o.append(tp(MONO,'TAMAÑO MÍNIMO',13,740,798,tracking=0.2,fill=G)[0])
    xx=760
    for h in [70,44,28,18]:
        body,b=mark(s=100,cE=K,cM=R); sc=h/100
        o.append(f'<g transform="translate({xx},{880-h/2:.0f}) scale({sc})">{body}</g>')
        o.append(tp(MONO,f'{h}px',12,xx,935,fill=G)[0])
        xx+=b[2]*sc+60
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wd}" height="{Hd}" viewBox="0 0 {Wd} {Hd}">'+''.join(o)+'</svg>'

if __name__=='__main__':
    open('b1.svg','w').write(concepto()); open('b2.svg','w').write(sistema()); print('ok')
