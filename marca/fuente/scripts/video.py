"""Genera video.html: animación determinista controlada por render(t)."""
import os
from logo import rhex, monogram, wordmark, vertical, R, K, W

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.abspath(os.path.join(HERE, '..', 'fuentes'))
MOCK = '/home/user/Bronstor/marca/mockups'

# --- logo del intro, por piezas (vertical, centrado) ---
wm, ww, wh = wordmark(96, W, W)
intro = f'''
<svg id="intro" width="1920" height="1080" viewBox="0 0 1920 1080">
  <defs><clipPath id="wipe"><rect id="wiperect" x="0" y="-40" width="0" height="400"/></clipPath></defs>
  <g transform="translate(960,380)">
    <g id="ring"><path d="{rhex(0, 0, 124 * 1.35, 14 * 1.35)}" fill="{R}"/></g>
    <g id="core"><path d="{rhex(0, 0, 100 * 1.35, 8 * 1.35)}" fill="{K}"/></g>
    <g id="mono"><g transform="scale(1.35)">{monogram(64, W, R)}</g></g>
  </g>
  <g id="wm" transform="translate({960 - ww / 2:.1f},620)"><g clip-path="url(#wipe)">{wm}</g></g>
</svg>'''

ew, eh, ebody = vertical(True)
endcard = f'<svg id="endlogo" width="{ew:.0f}" height="{eh:.0f}" viewBox="0 0 {ew:.1f} {eh:.1f}">{ebody}</svg>'

SLIDES = [('07-logo', 'Sistema de logo'), ('08-colores', 'Colores y tipografía'), ('01-polo', 'Polo oficial'),
          ('02-camisa', 'Camisa de trabajo'), ('03-casaca-gorra', 'Casaca y gorra'), ('04-letrero', 'Letrero de fachada'),
          ('05-tarjetas', 'Tarjetas de presentación'), ('06-redes', 'Redes sociales')]
slides_html = ''.join(
    f'<div class="slide" id="s{i}"><img src="file://{MOCK}/{f}.png"></div>' for i, (f, _) in enumerate(SLIDES))
titles_js = repr([t.upper() for _, t in SLIDES])

html = f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:AExp;src:url(file://{FONTS}/ArchivoExpBlack.ttf)}}
@font-face{{font-family:ABold;src:url(file://{FONTS}/ArchivoBold.ttf)}}
@font-face{{font-family:Mono;src:url(file://{FONTS}/PlexMono.ttf)}}
html,body{{margin:0;width:1920px;height:1080px;overflow:hidden;background:#0A0A0B}}
#stage{{position:absolute;inset:0;overflow:hidden}}
.bg{{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 40%,#2A2B2E 0%,#16171A 60%,#0A0A0B 100%)}}
#intro{{position:absolute;left:0;top:0}}
.tag{{position:absolute;left:0;right:0;text-align:center;font-family:Mono;color:#9A9DA3;letter-spacing:.3em;font-size:22px}}
.slide{{position:absolute;inset:0;opacity:0}}
.slide img{{position:absolute;left:0;top:0;width:1920px;height:1200px;transform-origin:50% 35%}}
#lt{{position:absolute;left:80px;bottom:80px;display:flex;align-items:stretch;opacity:0}}
#lt .bar{{width:12px;background:{R}}}
#lt .box{{background:#111;padding:22px 34px 20px 28px;display:flex;flex-direction:column;gap:8px}}
#lt .n{{font-family:Mono;font-size:18px;color:#9A9DA3;letter-spacing:.2em}}
#lt .t{{font-family:AExp;font-size:38px;color:#fff;transform:skewX(-12deg);transform-origin:0 100%;white-space:nowrap}}
#sweep1{{position:absolute;top:-100px;height:1280px;width:2600px;background:{R};transform:skewX(-14deg);left:-3000px}}
#sweep2{{position:absolute;top:-100px;height:1280px;width:2600px;background:#111;transform:skewX(-14deg);left:-3000px}}
#end{{position:absolute;inset:0;opacity:0}}
#endlogo{{position:absolute;left:50%;top:44%;width:820px;height:auto;transform:translate(-50%,-50%)}}
#fade{{position:absolute;inset:0;background:#000;opacity:0}}
</style></head><body><div id="stage">
<div class="bg"></div>
<div id="introwrap">{intro}<div class="tag" id="tag" style="top:900px">MANUAL DE IDENTIDAD VISUAL</div></div>
{slides_html}
<div id="lt"><div class="bar"></div><div class="box"><div class="n" id="ltn">01 / 08</div><div class="t" id="ltt">TITULO</div></div></div>
<div id="end"><div class="bg"></div>{endcard}<div class="tag" style="top:880px;color:#fff;font-size:30px;letter-spacing:.12em">[TELÉFONO] · [DIRECCIÓN]</div></div>
<div id="sweep1"></div><div id="sweep2"></div><div id="fade"></div>
</div>
<script>
const TITLES={titles_js};
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const prog=(t,a,b)=>clamp((t-a)/(b-a));
const eo=x=>1-Math.pow(1-x,3);
const eio=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;
const back=x=>{{const c1=1.70158,c3=c1+1;return 1+c3*Math.pow(x-1,3)+c1*Math.pow(x-1,2);}};
const $=id=>document.getElementById(id);
const S0=6.0, SD=3.0, N=TITLES.length, SEND=S0+SD*N, TOTAL=SEND+4.5;
window.TOTAL=TOTAL;
function render(t){{
  // intro
  const ring=back(prog(t,.4,1.3)), core=eo(prog(t,.9,1.5)), mono=eo(prog(t,1.4,2.0));
  $('ring').setAttribute('transform',`rotate(${{(1-ring)*-120}}) scale(${{Math.max(ring,0.0001)}})`);
  $('ring').style.opacity=prog(t,.4,.7);
  $('core').setAttribute('transform',`scale(${{Math.max(core,0.0001)}})`);
  $('mono').setAttribute('transform',`translate(${{(1-mono)*-60}},0)`);
  $('mono').style.opacity=mono;
  const wp=eio(prog(t,2.0,3.0));
  $('wiperect').setAttribute('width',{ww + 40:.1f}*wp);
  const hold=prog(t,3.0,6.0);
  $('intro').style.transform=`scale(${{1+hold*0.04}})`;
  $('tag').style.opacity=prog(t,3.0,3.6);
  $('introwrap').style.opacity=t<S0?1:0;
  // barridos
  const w1=prog(t,S0-0.5,S0+0.5); $('sweep1').style.left=(-2900+w1*5200)+'px';
  const w2=prog(t,SEND-0.5,SEND+0.5); $('sweep2').style.left=(-2900+w2*5200)+'px';
  // láminas
  let cur=-1;
  for(let i=0;i<N;i++){{
    const a=S0+i*SD, b=a+SD;
    let o=0;
    o = i===0 ? (t>=a?1:0) : eio(prog(t,a-.35,a+.35));
    if(i<N-1 && t>=b+.35) o=0;
    if(t>=SEND) o=0;
    const el=$('s'+i); el.style.opacity=o;
    el.firstChild.style.transform=`scale(${{1+0.07*prog(t,a-.3,b+.3)}})`;
    if(t>=a&&t<b) cur=i;
  }}
  if(cur>=0){{
    const a=S0+cur*SD, b=a+SD;
    const inn=eo(prog(t,a+.25,a+.75)), out=prog(t,b-.35,b-.05);
    $('lt').style.opacity=inn*(1-out);
    $('lt').style.transform=`translateX(${{(1-inn)*-40}}px)`;
    $('ltn').textContent=String(cur+1).padStart(2,'0')+' / '+String(N).padStart(2,'0');
    $('ltt').textContent=TITLES[cur];
  }} else $('lt').style.opacity=0;
  // cierre
  $('end').style.opacity=t>=SEND?1:0;
  const e=eo(prog(t,SEND+.3,SEND+1.3));
  $('endlogo').style.opacity=e;
  $('endlogo').style.transform=`translate(-50%,-50%) scale(${{0.92+0.08*e}})`;
  $('fade').style.opacity=prog(t,TOTAL-.6,TOTAL);
}}
render(0);
</script></body></html>'''

with open(os.path.join(HERE, 'video.html'), 'w') as f:
    f.write(html)
print('ok')
