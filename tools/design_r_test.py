# Paket R – Design-Test (03.10.2026), Vorlage für den Umbau, verändert die App NICHT:
# Aufruf aus dem Ordner über dem Klon: python3 willow/tools/design_r_test.py → TEST2.html (Kopie von DnD_Character_App.html),
# Fotos: python3 willow/tools/design_r_shots.py [breite] → design2_dark.png / design2_light.png (Druid, Wizard, Rogue).
# Modus im Test über localStorage 'willow_mode' = dark|light. app_check meldet 2 erwartete ✘ (Farb-Tests, Klassen-Themes übergangen).
# neutrales Grunddesign Leder (dunkel) / Pergament (hell) mit Textur, Klassen-Vignette im Kopf, Klassen-Emblem im HP-Block.
import sys, math, random, urllib.parse, shutil
sys.path.insert(0, 'willow/tools'); from rep import Datei
shutil.copy('DnD_Character_App.html', 'TEST2.html')
d = Datei('TEST2.html')

def uri(svg): return 'url("data:image/svg+xml,' + urllib.parse.quote(svg) + '")'

# ---------- Texturen (SVG-Rauschen, keine Bilder) ----------
LEATHER = uri("<svg xmlns='http://www.w3.org/2000/svg' width='220' height='220'>"
    "<filter id='a'><feTurbulence type='fractalNoise' baseFrequency='.62' numOctaves='3' stitchTiles='stitch'/>"
    "<feColorMatrix values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1.6 0 0 0 -.62'/></filter>"
    "<filter id='b'><feTurbulence type='fractalNoise' baseFrequency='.012' numOctaves='3' seed='4' stitchTiles='stitch'/>"
    "<feColorMatrix values='0 0 0 0 1 0 0 0 0 .85 0 0 0 0 .6 1 0 0 0 -.38'/></filter>"
    "<rect width='100%' height='100%' filter='url(#a)' opacity='.55'/><rect width='100%' height='100%' filter='url(#b)' opacity='.10'/></svg>")
PARCH = uri("<svg xmlns='http://www.w3.org/2000/svg' width='260' height='260'>"
    "<filter id='a'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/>"
    "<feColorMatrix values='0 0 0 0 .35 0 0 0 0 .22 0 0 0 0 .08 1.4 0 0 0 -.62'/></filter>"
    "<filter id='b'><feTurbulence type='fractalNoise' baseFrequency='.008' numOctaves='4' seed='9' stitchTiles='stitch'/>"
    "<feColorMatrix values='0 0 0 0 .45 0 0 0 0 .28 0 0 0 0 .1 1.3 0 0 0 -.5'/></filter>"
    "<rect width='100%' height='100%' filter='url(#a)' opacity='.35'/><rect width='100%' height='100%' filter='url(#b)' opacity='.35'/></svg>")

def corner(rot):
    p = ('<path d="M2 30 V8 Q2 2 8 2 H30" fill="none" stroke="#000" stroke-width="1.6"/>'
         '<path d="M7 26 V12 Q7 7 12 7 H26" fill="none" stroke="#000" stroke-width=".9"/>'
         '<path d="M12 12 q6 -1 7 4 q1 4 -3 4 q-3 0 -2 -3" fill="none" stroke="#000" stroke-width="1.1"/>'
         '<circle cx="34" cy="2" r="1.6"/><circle cx="2" cy="34" r="1.6"/>')
    return uri(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40"><g transform="rotate({rot} 20 20)">{p}</g></svg>')
C = [corner(r) for r in (0, 90, 180, 270)]

# ---------- Vignetten (Silhouetten, viewBox 400x130, rechts unten verankert) ----------
def V(body): return f'<svg class="hx-vig" viewBox="0 0 400 130" preserveAspectRatio="xMaxYMax slice" aria-hidden="true">{body}</svg>'
def dots(pts, cls='st'): return ''.join(f'<circle class="{cls}" cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in pts)

def vig_druid():
    random.seed(3)
    def layer(base, hmin, hmax, step, cls):
        pts = [f'M0 {base}']; x = 0
        while x < 410:
            h = random.uniform(hmin, hmax); w = random.uniform(step * .7, step * 1.3)
            pts.append(f'L{x + w/2:.0f} {base - h:.0f} L{x + w:.0f} {base - h*0.35:.0f}'); x += w
        pts.append(f'L410 {base} L410 131 L0 131 Z'); return f'<path class="{cls}" d="{" ".join(pts)}"/>'
    glow = [(262, 52, 2.2), (318, 30, 1.6), (352, 64, 2), (230, 78, 1.4), (385, 44, 1.5)]
    return V(layer(128, 45, 95, 26, 's1') + layer(131, 20, 52, 18, 's2') +
             ''.join(f'<circle class="halo" cx="{x}" cy="{y}" r="{r*7}"/>' for x, y, r in glow) + dots(glow, 'lit'))

def vig_wizard():
    stars = [(150, 20, 1.2), (190, 44, .9), (228, 14, 1.4), (262, 36, 1), (300, 10, 1.1), (392, 30, 1.2), (170, 70, .8), (382, 70, .9)]
    tower = ('M318 131 V58 L314 58 L338 4 L362 58 L358 58 V131 Z'          # Turm mit Spitzdach
             'M300 131 V92 L296 92 L310 66 L324 92 L320 92 V131 Z')         # Nebenturm
    hills = 'M0 131 L0 118 Q60 104 120 114 T240 108 T400 112 L400 131 Z'
    moon = '<path class="moon" d="M248 40 a16 16 0 1 0 14 -24 a12 12 0 1 1 -14 24 Z"/>'
    win = ('<rect class="lit" x="334" y="66" width="7" height="11" rx="3.5"/><rect class="lit" x="334" y="90" width="7" height="11" rx="3.5"/>'
           '<rect class="lit" x="307" y="100" width="5" height="8" rx="2.5"/>')
    motes = [(286, 58, 1.1), (372, 84, 1), (296, 30, .8)]
    return V(dots(stars) + moon + f'<path class="s2" d="{hills}"/><path class="s1" d="{tower}"/>' + win + dots(motes, 'lit'))

def vig_rogue():
    random.seed(11); x = 120; p = ['M120 131']; wins = []
    while x < 405:
        w = random.uniform(28, 46); h = random.uniform(40, 82); roof = random.choice(['gable', 'flat', 'gable'])
        p.append(f'L{x:.0f} {131-h:.0f}')
        if roof == 'gable': p.append(f'L{x+w/2:.0f} {131-h-16:.0f} L{x+w:.0f} {131-h:.0f}')
        else:
            p.append(f'L{x+w*.7:.0f} {131-h:.0f} L{x+w*.7:.0f} {131-h-10:.0f} L{x+w*.7+6:.0f} {131-h-10:.0f} L{x+w*.7+6:.0f} {131-h:.0f} L{x+w:.0f} {131-h:.0f}')
        if random.random() < .7: wins.append((x + w * .3, 131 - h + 14))
        x += w
    p.append('L405 131 Z')
    moon = '<circle class="moon" cx="230" cy="34" r="15"/>'
    stars = [(160, 18, 1), (290, 14, 1.2), (330, 40, .9), (380, 22, 1.1), (200, 60, .8)]
    back = 'M0 131 L0 104 L30 104 L30 92 L60 92 L60 100 L95 100 L95 86 L120 86 L120 131 Z'
    return V(dots(stars) + moon + f'<path class="s2" d="{back}"/><path class="s1" d="{" ".join(p)}"/>' +
             ''.join(f'<rect class="lit" x="{wx:.0f}" y="{wy:.0f}" width="6" height="8"/>' for wx, wy in wins))

# ---------- Embleme im HP-Block (Strichzeichnung) ----------
def E(body, vb='0 0 120 130'): return f'<svg class="hpx-emb" viewBox="{vb}" aria-hidden="true" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">{body}</svg>'
def emb_druid():
    random.seed(7); segs = []
    def br(x, y, a, l, w, n):
        if n == 0: return
        x2, y2 = x + l * math.cos(a), y - l * math.sin(a)
        segs.append(f'M{x:.0f} {y:.0f}L{x2:.0f} {y2:.0f}'); br(x2, y2, a + .42, l * .74, w, n - 1); br(x2, y2, a - .42, l * .74, w, n - 1)
    br(60, 118, math.pi / 2, 30, 3, 6)
    return E(f'<path d="{"".join(segs)}" stroke-width="2"/><path d="M60 118 Q48 121 38 126 M60 118 Q72 121 82 126" stroke-width="2"/>')
def emb_wizard():
    return E('<path d="M60 112 C44 102 24 102 10 108 V50 C24 44 44 44 60 54 C76 44 96 44 110 50 V108 C96 102 76 102 60 112 Z M60 54 V112" stroke-width="2.4"/>'
             '<path d="M18 62 C30 58 42 58 52 64 M18 76 C30 72 42 72 52 78 M68 64 C78 58 90 58 102 62 M68 78 C78 72 90 72 102 76" stroke-width="1.4"/>'
             '<path d="M60 8 L64 24 L80 28 L64 32 L60 48 L56 32 L40 28 L56 24 Z" stroke-width="2"/>')
def emb_rogue():
    dag = ('<path d="M0 -56 L7 -14 L0 -8 L-7 -14 Z M-16 -8 H16 M0 -8 V18 M0 18 m-5 0 a5 5 0 1 0 10 0 a5 5 0 1 0 -10 0" stroke-width="2.4"/>'
           '<path d="M0 -50 V-16" stroke-width="1"/>')
    return E(f'<g transform="translate(60 66) rotate(35)">{dag}</g><g transform="translate(60 66) rotate(-35)">{dag}</g>')

VIG = {'Druid': vig_druid(), 'Wizard': vig_wizard(), 'Rogue': vig_rogue()}
EMB = {'Druid': emb_druid(), 'Wizard': emb_wizard(), 'Rogue': emb_rogue()}

CSS = """
/* ===== DESIGN-TEST 2 (lokal) ===== */
:root{--tex:LEATHER;--tex-size:220px}
html[data-mode="light"]{--tex:PARCH;--tex-size:260px}
body{background:var(--tex) 0 0/var(--tex-size),radial-gradient(140% 90% at 50% 0%,var(--bg1),var(--bg0)) fixed}
.act-panel,.char-bar,.hdr{background-image:var(--tex)!important;background-size:var(--tex-size)!important}
.hdr.hx-bar{background-color:color-mix(in srgb,var(--bg1) 85%,#000);border-bottom:1px solid color-mix(in srgb,var(--gold) 35%,transparent);padding:8px 10px;gap:4px}
.hx-title{flex:1;text-align:center;margin:0;font-size:var(--fs-sm);letter-spacing:5px;color:var(--gold);text-transform:uppercase;text-shadow:0 1px 0 rgba(0,0,0,.6),0 -1px 0 rgba(255,225,160,.12)}
.hx-hero{position:relative;overflow:hidden;display:flex;align-items:center;gap:16px;padding:20px 16px 24px 20px;min-height:132px;
  background:var(--tex) 0 0/var(--tex-size),radial-gradient(120% 120% at 85% 10%,color-mix(in srgb,var(--gold) 14%,transparent),transparent 60%),
    radial-gradient(160% 140% at 50% 50%,transparent 45%,rgba(0,0,0,.55)),var(--bg1);
  border-bottom:1px solid color-mix(in srgb,var(--gold) 45%,transparent);box-shadow:inset 0 -1px 0 rgba(0,0,0,.6)}
.hx-vig{position:absolute;right:0;bottom:0;height:100%;width:72%;pointer-events:none;-webkit-mask:linear-gradient(90deg,transparent 0,rgba(0,0,0,.35) 30%,#000 62%);mask:linear-gradient(90deg,transparent 0,rgba(0,0,0,.35) 30%,#000 62%)}
.hx-vig .s1{fill:#060403;opacity:.82}.hx-vig .s2{fill:#060403;opacity:.5}
.hx-vig .st{fill:color-mix(in srgb,var(--gold) 60%,#fff);opacity:.75}
.hx-vig .moon{fill:color-mix(in srgb,var(--gold) 45%,#fff);opacity:.55}
.hx-vig .lit{fill:color-mix(in srgb,var(--gold) 80%,#fff);filter:drop-shadow(0 0 3px var(--gold))}
.hx-vig .halo{fill:var(--gold);opacity:.07}
.hx-portrait{position:relative;flex:0 0 auto;width:92px;height:92px}
.hx-portrait .rune{position:absolute;inset:0;width:auto;height:auto;font-size:44px;border-radius:50%;
  background:radial-gradient(circle at 50% 35%,var(--bg2),var(--bg0) 78%);border:3px solid var(--gold);
  box-shadow:0 0 0 1px rgba(0,0,0,.6),0 0 0 5px var(--bg1),0 0 0 6px color-mix(in srgb,var(--gold) 55%,transparent),0 6px 16px rgba(0,0,0,.6)}
.hx-portrait::before,.hx-portrait::after{content:'';position:absolute;left:50%;width:9px;height:9px;margin-left:-5px;background:var(--bg1);border:1px solid var(--gold);transform:rotate(45deg);z-index:1}
.hx-portrait::before{top:-9px}.hx-portrait::after{bottom:-9px}
.hx-id{position:relative;min-width:0;flex:1}
.hx-name.name-in{border:none;padding:0;font-size:32px;font-weight:700;line-height:1.05;letter-spacing:.5px;
  background:linear-gradient(180deg,#fff7e0 5%,#f1dc9a 50%,var(--gold) 100%);-webkit-background-clip:text;background-clip:text;color:transparent;-webkit-text-fill-color:transparent;
  filter:drop-shadow(0 2px 2px rgba(0,0,0,.85));overflow-wrap:anywhere}
.hx-cls{margin-top:6px;font-size:18px;color:var(--text);text-shadow:0 1px 3px #000}
.hx-sub{margin-top:2px;font-size:15px;color:var(--text2);text-shadow:0 1px 3px #000}
.hx-cls:empty,.hx-sub:empty{display:none}

#hpPanel{position:relative;background-color:var(--bg1);
  border:1px solid color-mix(in srgb,var(--gold) 45%,transparent);box-shadow:inset 0 0 30px rgba(0,0,0,.45),0 4px 14px rgba(0,0,0,.45)}
#hpPanel::before{content:'';position:absolute;inset:4px;pointer-events:none;background:color-mix(in srgb,var(--gold) 80%,transparent);
  -webkit-mask:C0 top left/30px 30px no-repeat,C1 top right/30px 30px no-repeat,C2 bottom right/30px 30px no-repeat,C3 bottom left/30px 30px no-repeat;
          mask:C0 top left/30px 30px no-repeat,C1 top right/30px 30px no-repeat,C2 bottom right/30px 30px no-repeat,C3 bottom left/30px 30px no-repeat}
#hpPanel::after{content:'';position:absolute;inset:8px;border:1px dashed color-mix(in srgb,var(--gold) 28%,transparent);border-radius:8px;pointer-events:none}
#hpPanel > .sec:first-child{border-bottom:none;flex-wrap:nowrap;padding-left:14px;padding-right:10px;text-shadow:0 1px 0 rgba(0,0,0,.6),0 -1px 0 rgba(255,225,160,.12)}
#hpPanel > .sec:first-child > span:first-child{display:flex;align-items:center;gap:10px;flex:1;min-width:0;letter-spacing:4px}
#hpPanel > .sec:first-child > span:first-child::before{content:'';width:7px;height:7px;flex:0 0 auto;border:1px solid var(--gold);transform:rotate(45deg)}
#hpPanel > .sec:first-child > span:first-child::after{content:'';flex:1;height:1px;min-width:10px;background:linear-gradient(90deg,var(--gold),transparent)}
.hp-row.hpx .hpx-main{grid-column:span 2;position:relative;overflow:hidden;min-width:0;padding:6px 10px 12px;text-align:center}
.hpx-emb{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);height:118%;width:auto;color:var(--gold);opacity:.13;pointer-events:none}
.hpx-nums{position:relative;display:flex;align-items:baseline;justify-content:center;gap:4px}
.hpx-main #hpC{font-size:52px;font-weight:700;line-height:1;color:var(--text);text-shadow:0 2px 5px rgba(0,0,0,.7);min-width:0}
.hpx-sl{font-family:'Cinzel',serif;font-size:36px;color:color-mix(in srgb,var(--text) 45%,transparent)}
.hpx-main .hpx-max{font-size:38px;font-weight:600;width:2.3ch;color:color-mix(in srgb,var(--text) 55%,transparent);text-align:left}
.hpx-barwrap{position:relative;margin:12px 0 0;padding:0 9px}
.hpx-bar.hpbar-w{position:relative;height:16px;margin:0;padding:2px;border-radius:9px;overflow:hidden;background:linear-gradient(180deg,#050302,#17110c);border:1px solid color-mix(in srgb,var(--gold) 60%,transparent);box-shadow:inset 0 2px 4px #000}
.hpx-barwrap::before,.hpx-barwrap::after{z-index:1;content:'';position:absolute;top:50%;width:9px;height:9px;background:var(--bg1);border:1px solid var(--gold);transform:translateY(-50%) rotate(45deg)}
.hpx-barwrap::before{left:3px}.hpx-barwrap::after{right:3px}
.hpx-bar .hpbar{position:relative;border-radius:7px}
.hpx-bar .hpbar::after{content:'';position:absolute;inset:1px 4px 50%;border-radius:6px;background:linear-gradient(180deg,rgba(255,255,255,.45),rgba(255,255,255,0))}
.hpx-temp.hpbox{align-self:center;background:color-mix(in srgb,var(--bg0) 70%,#000);border:1px solid color-mix(in srgb,var(--gold) 32%,transparent)!important;border-radius:10px;padding:10px 4px;box-shadow:inset 0 2px 6px rgba(0,0,0,.5)}
.hpx-temp .hpin{font-size:30px;color:var(--text)!important;width:2.4ch}
.dmg-box{background:transparent;border:none;padding:4px 2px 2px}
.dmg-btn{border:1px solid color-mix(in srgb,var(--gold) 38%,transparent);border-radius:7px;color:var(--text);font-size:var(--fs-sm);
  background:linear-gradient(180deg,color-mix(in srgb,var(--bg2) 85%,#fff),color-mix(in srgb,var(--bg0) 85%,#000));box-shadow:inset 0 1px 0 rgba(255,255,255,.06),0 2px 4px rgba(0,0,0,.45)}
.dmg-btn.d{background:linear-gradient(180deg,color-mix(in srgb,var(--red) 24%,var(--bg2)),color-mix(in srgb,var(--red) 8%,var(--bg0)))}
.dmg-btn.h{background:linear-gradient(180deg,color-mix(in srgb,var(--green) 30%,var(--bg2)),color-mix(in srgb,var(--green) 10%,var(--bg0)))}
.dmg-btn.t{background:linear-gradient(180deg,color-mix(in srgb,var(--gold) 24%,var(--bg2)),color-mix(in srgb,var(--gold) 6%,var(--bg0)))}
.dmg-amt{border-color:color-mix(in srgb,var(--gold) 32%,transparent);background:color-mix(in srgb,var(--bg0) 60%,#000);box-shadow:inset 0 2px 4px rgba(0,0,0,.6)}
@container (max-width:362px){.hp-row.hpx .hpx-main{grid-column:1/-1}}
@media (max-width:408px){.hp-row.hpx .hpx-main{grid-column:1/-1}}
@media (max-width:469px){html[data-ts="gross"] .hp-row.hpx .hpx-main{grid-column:1/-1}}
@media (max-width:530px){html[data-ts="sehrgross"] .hp-row.hpx .hpx-main{grid-column:1/-1}}

/* --- Pergament (hell): Tusche statt Leuchten --- */
html[data-mode="light"] .hx-hero{background:var(--tex) 0 0/var(--tex-size),radial-gradient(160% 140% at 50% 50%,transparent 40%,rgba(90,55,15,.35)),var(--bg1)}
html[data-mode="light"] .hx-vig .s1{fill:#3a2412;opacity:.32}html[data-mode="light"] .hx-vig .s2{fill:#3a2412;opacity:.2}
html[data-mode="light"] .hx-vig .st,html[data-mode="light"] .hx-vig .moon{fill:#3a2412;opacity:.35}
html[data-mode="light"] .hx-vig .lit{fill:#b07a22;filter:none;opacity:.9}
html[data-mode="light"] .hx-vig .halo{fill:#b07a22;opacity:.08}
html[data-mode="light"] .hx-name.name-in{background:linear-gradient(180deg,#8a5a1c,#4a2c0c);-webkit-background-clip:text;background-clip:text;filter:drop-shadow(0 1px 0 rgba(255,250,235,.7))}
html[data-mode="light"] .hx-cls,html[data-mode="light"] .hx-sub,html[data-mode="light"] .hx-title,html[data-mode="light"] #hpPanel > .sec:first-child{text-shadow:0 1px 0 rgba(255,250,235,.6)}
html[data-mode="light"] .hx-portrait .rune{background:radial-gradient(circle at 50% 35%,#fbf3df,var(--bg3) 80%);box-shadow:0 0 0 1px rgba(80,50,15,.5),0 0 0 5px var(--bg1),0 0 0 6px color-mix(in srgb,var(--gold) 55%,transparent),0 4px 10px rgba(80,50,15,.35)}
html[data-mode="light"] .hdr.hx-bar{background-color:var(--bg2)}
html[data-mode="light"] #hpPanel{box-shadow:inset 0 0 30px rgba(110,70,20,.18),0 3px 10px rgba(80,50,15,.25)}
html[data-mode="light"] .hpx-main #hpC{text-shadow:0 1px 0 rgba(255,250,235,.7)}
html[data-mode="light"] .hpx-emb{opacity:.14}
html[data-mode="light"] .hpx-bar.hpbar-w{background:linear-gradient(180deg,#d9c7a2,#efe2c6);box-shadow:inset 0 2px 3px rgba(80,50,15,.35)}
html[data-mode="light"] .hpx-temp.hpbox,html[data-mode="light"] .dmg-amt{background:color-mix(in srgb,var(--bg3) 80%,#fff);box-shadow:inset 0 2px 4px rgba(80,50,15,.25)}
html[data-mode="light"] .dmg-btn{background:linear-gradient(180deg,#f8efdb,#e6d5b2);box-shadow:0 1px 2px rgba(80,50,15,.3)}
html[data-mode="light"] .dmg-btn.d{background:linear-gradient(180deg,#f2d9cc,#e2bfae)}
html[data-mode="light"] .dmg-btn.h{background:linear-gradient(180deg,#d9e8d2,#bcd5b2)}
html[data-mode="light"] .dmg-btn.t{background:linear-gradient(180deg,#f3e3bb,#e2cc95)}
"""
CSS = CSS.replace('LEATHER', LEATHER).replace('PARCH', PARCH)
for i, c in enumerate(C): CSS = CSS.replace(f'C{i}', c)
d.rep('<script>try{var _ts', '<style>' + CSS + '</style>\n<script>try{var _ts')

# ---------- Kopf ----------
HDR_ALT = d.s[d.s.index('  <div class="hdr">'):d.s.index('  <div class="char-bar">')]
btns = HDR_ALT[HDR_ALT.index('    <button class="undo-btn" id="undoBtn"'):]
b_undo = btns[:btns.index('    <button onclick="openWebSearch()"')]
b_right = btns[btns.index('    <button onclick="openWebSearch()"'):btns.rindex('  </div>')]
d.rep(HDR_ALT, '  <div class="hdr hx-bar">\n' + b_undo + '    <div class="hdr-title hx-title">Character Sheet</div>\n' + b_right + '  </div>\n'
      '  <div class="hx-hero"><div id="hxVig"></div><div class="hx-portrait"><div class="rune">⚔</div></div>'
      '<div class="hx-id"><div class="name-in hx-name" id="charName" style="cursor:default"></div>'
      '<div class="hx-cls" id="hxCls"></div><div class="hx-sub" id="hxSub"></div></div></div>\n\n')

# ---------- HP-Zeile ----------
a = d.s.index('      <div class="hp-row">'); e = d.s.index('      <!-- SCHADEN / HEILUNG')
d.rep(d.s[a:e], '      <div class="hp-row hpx">\n'
      '        <div class="hpx-main"><div id="hxEmb"></div>'
      '<div class="hpx-nums"><div class="hpval hp-tap" id="hpC" onclick="hpCEdit()" title="Tap to correct">10</div>'
      '<span class="hpx-sl">/</span>'
      '<input class="hpin hpx-max" type="number" id="hpM" value="10" min="1" inputmode="numeric" oninput="autoSave()" onchange="onHpMChange()" aria-label="Maximum HP"></div>'
      '<div class="hpx-barwrap"><div class="hpbar-w hpx-bar"><div class="hpbar" id="hpBar" style="width:100%"></div></div></div>'
      '<div class="rc-hint" id="hpMHint"></div></div>\n'
      '        <div class="hpbox hpx-temp"><div class="hp-lbl">Temp</div><div class="hp-ctrl">'
      '<input class="hpin" type="number" id="hpT" value="0" min="0" inputmode="numeric" oninput="autoSave()"></div></div>\n'
      '      </div>\n')

# ---------- Grundfarben (statt Klassen-Theme), Vignette/Emblem je Klasse ----------
import json
PAL = {
 'dark': {'bg0':'#120d09','bg1':'#1e1610','bg2':'#2a1f16','bg3':'#160f0a','gold':'#d6b05c','gold2':'#b08c46','purple':'#e8cf8a','purple2':'#9a7438','purple3':'#3a2a18',
          'text':'#f3e8d2','text2':'#c2ad8e','text3':'#cfae6e','desc':'#e8dcc6','muted':'#9a846c','border':'rgba(214,176,92,.30)','border2':'rgba(214,176,92,.15)',
          'green':'#62b07c','red':'#e26d5e','blue':'#6a9fd0'},
 'light':{'bg0':'#e6d6b6','bg1':'#f1e5ca','bg2':'#ecdcbc','bg3':'#e2cfaa','gold':'#6a4310','gold2':'#5a3a10','purple':'#5e3c0e','purple2':'#a0773a','purple3':'#d8c39a',
          'text':'#2a1c0f','text2':'#46331d','text3':'#5a3e12','desc':'#33241a','muted':'#6a563c','border':'rgba(110,72,28,.38)','border2':'rgba(110,72,28,.2)',
          'green':'#1f6034','red':'#922a20','blue':'#2e5f93'}}
JS = """
<script>/* DESIGN-TEST 2 */
const HX_PAL=%s, HX_VIG=%s, HX_EMB=%s;
function hxMode(){try{return localStorage.getItem('willow_mode')||'dark'}catch(e){return 'dark'}}
function hxBase(){const m=hxMode();document.documentElement.dataset.mode=m;const t=HX_PAL[m],r=document.documentElement.style;
  for(const k in t)r.setProperty('--'+k,t[k]);
  try{const ic=themeIco(t);r.setProperty('--ico-act',ic.icoAct);r.setProperty('--ico-bonus',ic.icoBonus);r.setProperty('--ico-react',ic.icoReact);r.setProperty('--ico-pass',ic.icoPass);r.setProperty('--ico-other',ic.icoOther)}catch(e){}}
function hxUpd(){const v=id=>{const e=document.getElementById(id);return e?(e.value||'').trim():''};const nm=s=>s.replace(/\\s*\\([^)]*\\)\\s*$/,'');
  const cls=v('cls'),sub=v('subcls'),lvl=v('lvl');
  document.getElementById('hxCls').textContent=cls?(cls+(lvl?' '+lvl:'')+(sub?' · '+nm(sub):'')):'';
  document.getElementById('hxSub').textContent=[nm(v('race')),v('bg')].filter(Boolean).join(' · ');
  document.getElementById('hxVig').innerHTML=HX_VIG[cls]||HX_VIG.Druid;document.getElementById('hxEmb').innerHTML=HX_EMB[cls]||'';}
const _hxAT=applyTheme;applyTheme=function(c){_hxAT(c);hxBase()};
['applyState','onClsChange','onSubclsChange','onRaceChange'].forEach(f=>{const o=window[f];if(typeof o==='function')window[f]=function(){const r=o.apply(this,arguments);try{hxUpd()}catch(e){}return r}});
document.addEventListener('change',()=>{try{hxUpd()}catch(e){}});
hxBase();window.addEventListener('load',()=>setTimeout(()=>{try{hxBase();hxUpd()}catch(e){}},300));
</script>
</body>""" % (json.dumps(PAL), json.dumps(VIG), json.dumps(EMB))
d.rep('</body>', JS)
d.save()
print('TEST2.html geschrieben')
