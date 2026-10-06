# Paket W (06.10.2026) – Klassen-Themes im Leder: erzeugt WILLOW_METAL (Metall-Vorgaben Dark/Light) und WILLOW_CLS (je Klasse
# lederHue/lederSat/metal/inlay; Einlage = D&D-Beyond-Klassenfarbe) als JSON. Aufruf: python3 willow/tools/design_w_pal.py const.json
# Danach die beiden Konstanten in der HTML per rep() ersetzen (Zeilen "const WILLOW_METAL=" / "const WILLOW_CLS="). OKLCH-Hilfen wie in der App.
# Neue Klasse: Eintrag in DDB (Einlage) + MET (Metall) ergänzen. Fotos: design_w_shots.py (REAL=1 = Themes der App, MODE=light).
# Entwurf Klassen-Themes im Leder: Leder (Färbung) + Prägung (Metall) + Einlage (frame)
import math, json, sys
def h2r(h): h=h.lstrip('#'); return [int(h[i:i+2],16)/255 for i in (0,2,4)]
def r2h(c): return '#'+''.join('%02x'%max(0,min(255,round(x*255))) for x in c)
def lin(x): return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4
def gam(x): x=max(0,min(1,x)); return 12.92*x if x<=.0031308 else 1.055*x**(1/2.4)-.055
def to_lch(h):
    r,g,b=[lin(x) for x in h2r(h)]
    l=.4122214708*r+.5363325363*g+.0514459929*b; m=.2119034982*r+.6806995451*g+.1073969566*b; s=.0883024619*r+.2817188376*g+.6299787005*b
    l,m,s=[math.copysign(abs(v)**(1/3),v) for v in (l,m,s)]
    L=.2104542553*l+.7936177850*m-.0040720468*s; a=1.9779984951*l-2.4285922050*m+.4505937099*s; bb=.0259040371*l+.7827717662*m-.8086757660*s
    return L, math.hypot(a,bb), math.degrees(math.atan2(bb,a))%360
def from_lch(L,C,H):
    a=C*math.cos(math.radians(H)); b=C*math.sin(math.radians(H))
    l=(L+.3963377774*a+.2158037573*b)**3; m=(L-.1055613458*a-.0638541728*b)**3; s=(L-.0894841775*a-1.2914855480*b)**3
    r=4.0767416621*l-3.3077115913*m+.2309699292*s; g=-1.2684380046*l+2.6097574011*m-.3413193965*s; bl=-.0041960863*l-.7034186147*m+1.7076147010*s
    return r2h([gam(x) for x in (r,g,bl)])
def lum(h): c=[lin(x) for x in h2r(h)]; return .2126*c[0]+.7152*c[1]+.0722*c[2]
def cr(a,b): x,y=sorted([lum(a),lum(b)]); return (y+.05)/(x+.05)

BASE={"bg0":"#120d09","bg1":"#1e1610","bg2":"#2a1f16","bg3":"#160f0a","gold":"#d6b05c","gold2":"#b08c46","purple":"#e8cf8a","purple2":"#9a7438","purple3":"#3a2a18","text":"#f3e8d2","text2":"#c2ad8e","text3":"#cfae6e","desc":"#e8dcc6","muted":"#a48e74"}
# Metalle: gold, gold2, purple (Highlight), purple2, text3 (kleine Labels)
METAL={
 'gold':   dict(gold='#d6b05c',gold2='#b08c46',purple='#e8cf8a',purple2='#9a7438',text3='#cfae6e'),
 'sonne':  dict(gold='#e8c35a',gold2='#bf9a3c',purple='#f4dc8e',purple2='#a07e30',text3='#dcbc6a'),
 'weissgold':dict(gold='#e0cd98',gold2='#b9a572',purple='#f2e6c4',purple2='#8f7d52',text3='#d4c194'),
 'bronze': dict(gold='#c99a5e',gold2='#b2864e',purple='#e6c898',purple2='#8c6438',text3='#c6a070'),
 'kupfer': dict(gold='#d98e5e',gold2='#bf7c50',purple='#f0c29c',purple2='#8c5434',text3='#d39c74'),
 'silber': dict(gold='#c9ced6',gold2='#9ea6b0',purple='#e6eaf0',purple2='#6e7682',text3='#b9c0ca'),
 'stahl':  dict(gold='#b4bac2',gold2='#8e959e',purple='#dde1e7',purple2='#646b75',text3='#aab1ba'),
 'mondsilber':dict(gold='#c4bfd6',gold2='#9a94b0',purple='#e6e2f2',purple2='#6c6684',text3='#b8b2cc'),
}
# Klasse: (Leder-Farbton, Leder-Sättigung, Metall, Einlage frame, Beschreibung)
CLS={
 '':          (60, 0.000,'gold',     None,     'Standard: Umbra-Leder, Gold'),
 'Artificer': (55, 0.010,'kupfer',   '#5cc3c9','Umbra-Leder, Kupfer, Türkis'),
 'Barbarian': (22, 0.034,'bronze',   '#e4583c','Ochsenblut-Leder, Bronze, Glut'),
 'Bard':      (355,0.032,'gold',     '#e07a9c','Burgunder-Leder, Gold, Rosé'),
 'Cleric':    (95, 0.010,'sonne',    '#f6dc78','Steingraues Leder, Sonnengold, Sonnenlicht'),
 'Druid':     (125,0.026,'bronze',   '#93c46f','Waldgrünes Leder, Bronze, Blattgrün'),
 'Fighter':   (250,0.010,'silber',   '#9db4cf','Stahlgraues Leder, Silber, Stahlblau'),
 'Monk':      (50, 0.030,'gold',     '#ef8d3a','Teak-Leder, Gold, Safran'),
 'Paladin':   (262,0.030,'weissgold','#efe2bd','Königsblaues Leder, Weißgold, Elfenbein'),
 'Ranger':    (160,0.020,'bronze',   '#68b293','Tannengrünes Leder, Bronze, Tanne'),
 'Rogue':     (285,0.006,'stahl',    '#d4505e','Kohle-Leder, Stahl, Blutrot'),
 'Sorcerer':  (330,0.034,'gold',     '#cd77e0','Weinrotes Leder, Gold, Magenta'),
 'Warlock':   (295,0.030,'mondsilber','#9b86ec','Auberginen-Leder, Mondsilber, Violett'),
 'Wizard':    (270,0.030,'silber',   '#6ea9ec','Mitternachts-Leder, Silber, Arkanblau'),
}
def make(cls):
    H,C,metal,frame,_=CLS[cls]; t={}
    M=METAL[metal]; mh=to_lch(M['gold'])[2]; mc=to_lch(M['gold'])[1]
    for k in ('bg0','bg1','bg2','bg3'):
        L,c0,h0=to_lch(BASE[k]); t[k]=BASE[k] if C==0 else from_lch(L,C,H)
    t.update(M)
    L,c0,_=to_lch(BASE['purple3']); t['purple3']=from_lch(L,min(.05,mc*.45),mh) if metal!='gold' else (BASE['purple3'] if C==0 else from_lch(L,.045,(mh*0.7+H*0.3) if abs(mh-H)<90 else mh))
    for k,mixc in (('text',.025),('desc',.02)):
        L,c0,_=to_lch(BASE[k]); t[k]=from_lch(L,min(c0,mixc+mc*.08,0.012 if mc<.03 else 1),mh)
    for k in ('text2','muted'):
        L,c0,_=to_lch(BASE[k]); hh=mh if C<.015 else (H if abs((H-mh+180)%360-180)<120 else mh)
        t[k]=from_lch(L+(0.02 if k=='muted' else 0),min(c0,0.03+C*0.6),hh)
    g=h2r(t['gold']); rgb=','.join(str(round(x*255)) for x in g)
    t['border']=f'rgba({rgb},.30)'; t['border2']=f'rgba({rgb},.15)'
    if frame: t['frame']=frame
    return t
def check(t):
    P=[]
    for f in ['text','text2','text3','desc','muted','gold','gold2','purple']:
        for s in ['bg0','bg1','bg2','bg3']:
            r=cr(t[f],t[s]); 
            if r<4.5: P.append(f'{f}/{s} {r:.2f}')
    for f in ['text','gold','purple']:
        r=cr(t[f],t['purple3'])
        if r<4.5: P.append(f'{f}/purple3 {r:.2f}')
    if cr(t['bg0'],t['gold'])<4.5: P.append('bg0/gold')
    if 'frame' in t:
        r=min(cr(t['frame'],t[s]) for s in ('bg1','bg2'))
        if r<3: P.append(f'frame {r:.2f}')
    return P

import sys; P=sys.modules[__name__]
LIGHT={"bg0":"#efe5ce","bg1":"#f6efdf","bg2":"#fcf9f0","bg3":"#f0e7d3","gold":"#74490f","gold2":"#6a4310","purple":"#7a2e1c","purple2":"#9c7436","purple3":"#ecdcb8","text":"#2a1c0f","text2":"#4e3a22","text3":"#6a4614","desc":"#33241a","muted":"#665236"}
B=P.BASE; gL,gC,gH=P.to_lch(B['gold'])
dark={}; light={}
for m,M in P.METAL.items():
    mL,mc,mh=P.to_lch(M['gold']); d=dict(M)
    L,_,_=P.to_lch(B['purple3']); d['purple3']=B['purple3'] if m=='gold' else P.from_lch(L,min(.05,mc*.45),mh)
    for k,mix in (('text',.025),('desc',.02)):
        L,c0,_=P.to_lch(B[k]); d[k]=B[k] if m=='gold' else P.from_lch(L,min(c0,mix+mc*.08,.012 if mc<.03 else 1),mh)
    dark[m]=d
    r=mc/gC; l={}
    for k in ('gold','gold2','purple2','text3','purple3','text','desc'):
        L,c0,h0=P.to_lch(LIGHT[k])
        l[k]=LIGHT[k] if m=='gold' else P.from_lch(L,c0*min(r,1.15),mh)
    light[m]=l
CLS={}
DDB={'Artificer':'#d59139','Barbarian':'#e7623e','Bard':'#ab6dac','Cleric':'#91a1b2','Druid':'#7a853b','Fighter':'#7f513e','Monk':'#51a5c5','Paladin':'#b59e54','Ranger':'#507f62','Rogue':'#555752','Sorcerer':'#992e2e','Warlock':'#7b469b','Wizard':'#2a50a1'}
MET={'Artificer':'kupfer','Barbarian':'bronze','Bard':'gold','Cleric':'silber','Druid':'bronze','Fighter':'bronze','Monk':'gold','Paladin':'weissgold','Ranger':'bronze','Rogue':'stahl','Sorcerer':'gold','Warlock':'mondsilber','Wizard':'silber'}
for c,h in DDB.items():
    L,C,H=P.to_lch(h); dye=min(.034,max(.008,C*.22))
    CLS[c]={'lederHue':round(H),'lederSat':round(dye/.04*100),'metal':MET[c],'inlay':h}
json.dump({'metal':{'dark':dark,'light':light},'cls':CLS},open(sys.argv[1] if len(sys.argv)>1 else 'const.json','w'),separators=(',',':'))
for m in light: print(m, light[m]['gold'], light[m]['text'], light[m]['purple3'])
print(CLS)
