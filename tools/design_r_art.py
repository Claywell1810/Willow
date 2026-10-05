# Paket R (Design) – Bildbausteine als SVG-Text, ohne Bilddateien (seit R2, 05.10.2026):
#   ICO  = einfarbige Symbole 24×24 (Kopfleiste, untere Leiste, More-Fenster, Charakterliste; Farbe = currentColor)
#   VIG  = Vignette je Klasse im Kopf (Silhouette, viewBox 400×130, rechts unten verankert; '' = ohne Klasse)
#   EMB  = Emblem je Klasse (Strichzeichnung 120×120): Rune im Porträt-Ring (R2), Wasserzeichen hinter den HP (R3)
# Wird von den Patch-Skripten importiert (sys.path.insert(0,'willow/tools'); import design_r_art as A) und als JS-Konstanten
# WILLOW_ICO / WILLOW_VIG / WILLOW_EMB in die HTML geschrieben. Zufall nur mit festem seed → gleiche Ausgabe bei jedem Lauf.
# Vorschau: python3 willow/tools/design_r_art.py OUT.html  (alle Vignetten + Embleme + Symbole auf einer Seite)
import math, random

# ───────────────────────── Symbole (24×24, Strich) ─────────────────────────
def _gear(cx, cy, n, ro, ri, tw=.42):
    p = []
    for i in range(n):
        a = 2 * math.pi * i / n
        for da, r in ((-tw, ri), (-tw * .6, ro), (tw * .6, ro), (tw, ri)):
            b = a + da * 2 * math.pi / n
            p.append(f'{cx + r * math.cos(b):.2f} {cy + r * math.sin(b):.2f}')
    return 'M' + ' L'.join(p) + ' Z'

def _i(body, fill=False):
    return ('<svg class="ico" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" '
            'stroke-linecap="round" stroke-linejoin="round">' + body + '</svg>')

ICO = {
 'undo':   _i('<path d="M9 14 4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 0 11H11"/>'),
 'redo':   _i('<path d="m15 14 5-5-5-5"/><path d="M20 9H9.5a5.5 5.5 0 0 0 0 11H13"/>'),
 'search': _i('<circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.5 15.5 5 5"/>'),
 'gear':   _i(f'<path d="{_gear(12, 12, 8, 9.6, 7.4)}"/><circle cx="12" cy="12" r="3"/>'),
 # untere Leiste
 'info':   _i('<path d="M7 4h11a2 2 0 0 1 2 2v12"/><path d="M7 4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2v-1H9v1a2 2 0 0 1-2 2"/>'
              '<path d="M9 8h7M9 11.5h7M9 15h4"/>'),
 'skills': _i('<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.8"/><circle cx="12" cy="12" r="1.2" fill="currentColor"/>'),
 'dice':   _i('<path d="M12 2.5 20.5 7.3v9.4L12 21.5 3.5 16.7V7.3z"/><path d="M12 7.6 16.6 15.6H7.4z"/>'
              '<path d="M12 2.5v5.1M20.5 7.3l-3.9 8.3M3.5 7.3l3.9 8.3M7.4 15.6 3.5 16.7M16.6 15.6l3.9 1.1M7.4 15.6 12 21.5l4.6-5.9"/>'),
 'items':  _i('<path d="M6 9a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v10a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2z"/><path d="M9.5 5V4a2.5 2.5 0 0 1 5 0v1"/>'
              '<path d="M6 12h12M9 16h6v5H9z"/>'),
 'actions':_i('<path d="M3.5 3.5h3l9.5 9.5M13 17l4-4M15.5 15.5l4 4M18.5 20.5l2-2"/>'
              '<path d="M20.5 3.5h-3L12.8 8.2M11 17l-4-4M8.5 15.5l-4 4M5.5 20.5l-2-2M7.5 11.5 3.5 7.5v-4"/>'),
 'more':   _i('<circle cx="5" cy="12" r="1.7" fill="currentColor" stroke="none"/><circle cx="12" cy="12" r="1.7" fill="currentColor" stroke="none"/>'
              '<circle cx="19" cy="12" r="1.7" fill="currentColor" stroke="none"/>'),
 # More-Fenster
 'beasts': _i('<ellipse cx="12" cy="16.2" rx="4.6" ry="3.8"/><ellipse cx="5.2" cy="11" rx="1.9" ry="2.4"/><ellipse cx="9.2" cy="6.6" rx="1.9" ry="2.5"/>'
              '<ellipse cx="14.8" cy="6.6" rx="1.9" ry="2.5"/><ellipse cx="18.8" cy="11" rx="1.9" ry="2.4"/>'),
 'background': _i('<path d="M12 6.5C10 4.8 6.8 4.3 3 5v13.5c3.8-.7 7-.2 9 1.5 2-1.7 5.2-2.2 9-1.5V5c-3.8-.7-7-.2-9 1.5z"/><path d="M12 6.5V20"/>'),
 'feats':  _i('<circle cx="12" cy="9" r="6"/><path d="m12 6 1 2 2.2.3-1.6 1.5.4 2.2-2-1-2 1 .4-2.2-1.6-1.5L11 8z"/><path d="m8.5 14 -1.5 7 5-2.5 5 2.5-1.5-7"/>'),
 'spells': _i('<path d="M5 4.5A1.5 1.5 0 0 1 6.5 3H19v15H6.5A1.5 1.5 0 0 0 5 19.5z"/><path d="M5 19.5A1.5 1.5 0 0 0 6.5 21H19v-3"/>'
              '<path d="m12 6.5.9 2.6 2.6.9-2.6.9-.9 2.6-.9-2.6-2.6-.9 2.6-.9z"/>'),
 'notes':  _i('<path d="M20 3c-6 1-10.5 5.5-12 12l-2 6"/><path d="M20 3c.5 5-2 9.5-7 12H8"/><path d="M11 9h5M9.5 12h4.5"/>'),
 'log':    _i('<path d="M3.5 12a8.5 8.5 0 1 0 2.5-6"/><path d="M3 3v4h4"/><path d="M12 7.5V12l3 2"/>'),
 # Charakterliste
 'plus':   _i('<path d="M12 5v14M5 12h14"/>'),
 'trash':  _i('<path d="M4 7h16M9 7V4.5h6V7M6 7l1 13h10l1-13M10 11v6M14 11v6"/>'),
 'chev':   _i('<path d="m7 10 5 5 5-5"/>'),
 'save':   _i('<path d="M5 3h11l3 3v13a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2z"/><path d="M8 3v5h7V3M8 21v-7h8v7"/>'),
}

# ───────────────────────── Vignetten (Silhouetten) ─────────────────────────
def V(body): return f'<svg class="hx-vig" viewBox="0 0 400 130" preserveAspectRatio="xMaxYMax slice" aria-hidden="true">{body}</svg>'
def dots(pts, cls='st'): return ''.join(f'<circle class="{cls}" cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in pts)
def halos(pts, k=7): return ''.join(f'<circle class="halo" cx="{x}" cy="{y}" r="{r*k}"/>' for x, y, r in pts)
def ridge(seed, base, hmin, hmax, step, cls, x0=0, jag=.35):
    random.seed(seed); pts = [f'M{x0} {base}']; x = x0
    while x < 410:
        h = random.uniform(hmin, hmax); w = random.uniform(step * .7, step * 1.3)
        pts.append(f'L{x + w/2:.0f} {base - h:.0f} L{x + w:.0f} {base - h*jag:.0f}'); x += w
    pts.append(f'L410 {base} L410 131 L{x0} 131 Z'); return f'<path class="{cls}" d="{" ".join(pts)}"/>'
def hills(d, cls='s2'): return f'<path class="{cls}" d="{d}"/>'
def note(x, y, s=1):
    return (f'<g class="st" transform="translate({x} {y}) scale({s}) rotate(-12)"><ellipse cx="0" cy="0" rx="3.4" ry="2.4"/>'
            f'<rect x="2.4" y="-13" width="1.2" height="13"/><path d="M3.6 -13 q5 3 4 8 q-1-4-4-5z"/></g>')

def vig_none():
    stars = [(170, 22, 1), (210, 50, .8), (250, 14, 1.2), (300, 34, 1), (350, 18, 1.3), (385, 52, .9), (280, 66, .7)]
    return V(dots(stars) + '<circle class="moon" cx="374" cy="30" r="11"/>' +
             hills('M0 131 L0 112 Q80 92 160 106 T300 98 T400 104 L400 131 Z') +
             hills('M120 131 Q200 112 270 120 T400 114 L400 131 Z', 's1'))

def vig_artificer():
    g = _gear(238, 92, 12, 34, 27, .36)
    hole = ' M238 81 a11 11 0 1 0 .01 0 Z'
    shop = ('M262 131 V84 L300 60 L338 84 V131 Z M338 131 V96 H400 V131 Z'
            'M282 74 V40 H292 V68 Z M352 96 V52 H362 V96 Z')
    saw = 'M120 131 V100 L150 86 V100 L180 86 V100 L210 86 V100 L240 86 V131 Z'
    smoke = ''.join(f'<circle class="moon" cx="{x}" cy="{y}" r="{r}" opacity=".25"/>' for x, y, r in
                    [(288, 32, 5), (294, 22, 7), (302, 10, 8), (357, 44, 5), (362, 33, 6)])
    wins = ''.join(f'<rect class="lit" x="{x}" y="{y}" width="8" height="10" rx="1"/>' for x, y in [(284, 98), (308, 98), (352, 106), (374, 106)])
    sparks = [(318, 120, 1.1), (326, 112, .9), (312, 114, .8), (330, 122, .7)]
    return V(hills(saw) + f'<path class="s2" fill-rule="evenodd" d="{g}{hole}"/>' + smoke +
             f'<path class="s1" d="{shop}"/>' + wins + halos(sparks, 5) + dots(sparks, 'lit'))

def vig_barbarian():
    fire = [(312, 120, 2.6)]
    flame = '<path class="lit" d="M306 127 Q304 116 311 108 Q311 116 316 112 Q320 120 317 127 Z"/>'
    embers = [(318, 96, .9), (306, 86, .8), (324, 74, .7), (312, 64, .6)]
    stars = [(180, 20, 1), (240, 12, 1.2), (390, 16, 1), (360, 40, .8)]
    return V(dots(stars) + ridge(5, 124, 60, 108, 46, 's2', 100, .2) + ridge(8, 131, 26, 54, 30, 's1', 140, .4) +
             halos(fire, 9) + flame + dots(embers, 'lit'))

def vig_bard():
    inn = ('M250 131 V82 L290 52 L330 82 V131 Z M330 131 V96 H384 V131 Z'
           'M306 66 V44 H316 V74 Z M330 96 L357 76 L384 96 Z')
    sign = '<path class="s1" d="M246 86 H226 V88 H246 Z M230 88 V92 M242 88 V92"/><rect class="s1" x="227" y="92" width="18" height="13" rx="2"/>'
    wins = ''.join(f'<rect class="lit" x="{x}" y="{y}" width="9" height="11" rx="4.5"/>' for x, y in [(262, 94), (306, 94), (342, 106), (364, 106)])
    door = '<rect class="lit" x="283" y="110" width="12" height="21" rx="6"/>'
    notes = note(318, 34, .9) + note(334, 18, .75) + note(352, 30, .65)
    return V(hills('M0 131 L0 116 Q90 100 170 112 T400 108 L400 131 Z') + notes + f'<path class="s1" d="{inn}"/>' + sign + wins + door +
             halos([(289, 120, 2)], 6))

def vig_cleric():
    rays = ''.join(f'<path class="halo" d="M{300+dx} -10 L{300+dx*3-14} 131 L{300+dx*3+14} 131 Z"/>' for dx in (-24, 0, 24))
    church = ('M232 131 V90 L262 70 L292 90 V131 Z'          # Schiff
              'M292 131 V58 L291 58 L306 18 L321 58 L320 58 V131 Z'   # Turm mit Spitze
              'M320 131 V96 L346 80 L372 96 V131 Z')
    sym = '<circle class="lit" cx="306" cy="12" r="3.4"/>'
    rose = '<circle class="lit" cx="262" cy="96" r="7"/><rect class="lit" x="301" y="72" width="10" height="16" rx="5"/>'
    wins = ''.join(f'<rect class="lit" x="{x}" y="108" width="7" height="13" rx="3.5"/>' for x in (240, 276, 334, 352))
    return V(rays + hills('M0 131 L0 120 Q100 104 200 116 T400 112 L400 131 Z') + f'<path class="s1" d="{church}"/>' + sym + rose + wins +
             halos([(306, 12, 3.4)], 6))

def vig_druid():
    random.seed(3)
    def layer(base, hmin, hmax, step, cls):
        pts = [f'M0 {base}']; x = 0
        while x < 410:
            h = random.uniform(hmin, hmax); w = random.uniform(step * .7, step * 1.3)
            pts.append(f'L{x + w/2:.0f} {base - h:.0f} L{x + w:.0f} {base - h*0.35:.0f}'); x += w
        pts.append(f'L410 {base} L410 131 L0 131 Z'); return f'<path class="{cls}" d="{" ".join(pts)}"/>'
    glow = [(262, 52, 2.2), (318, 30, 1.6), (352, 64, 2), (230, 78, 1.4), (385, 44, 1.5)]
    return V(layer(128, 45, 95, 26, 's1') + layer(131, 20, 52, 18, 's2') + halos(glow) + dots(glow, 'lit'))

def vig_fighter():
    def crenel(x0, x1, top, w=10):
        p = [f'M{x0} 131 V{top}']; x = x0
        while x + w <= x1:
            p.append(f'H{x + w/2:.0f} V{top - 7} H{x + w:.0f} V{top}' if (x - x0) // w % 2 == 0 else f'H{x + w:.0f}'); x += w
        p.append(f'H{x1} V131 Z'); return ' '.join(p)
    wall = crenel(150, 400, 100) + ' ' + crenel(290, 346, 52, 8)
    pole = '<rect class="s1" x="317" y="14" width="2.4" height="32"/><path class="s1" d="M319.4 16 H344 L337 23 L344 30 H319.4 Z"/>'
    gate = '<path class="lit" d="M306 131 V116 a12 12 0 0 1 24 0 V131 Z" opacity=".55"/>'
    torches = [(298, 112, 1.6), (338, 112, 1.6)]
    stars = [(170, 30, 1), (220, 16, 1.2), (270, 40, .8), (380, 26, 1.1)]
    slits = ''.join(f'<rect class="lit" x="{x}" y="{y}" width="3" height="9" rx="1.5"/>' for x, y in [(304, 68), (330, 68), (200, 110), (370, 110)])
    return V(dots(stars) + '<circle class="moon" cx="230" cy="40" r="12"/>' + hills('M0 131 L0 114 Q90 100 170 110 L170 131 Z') +
             f'<path class="s1" d="{wall}"/>' + pole + gate + slits + halos(torches, 5) + dots(torches, 'lit'))

def vig_monk():
    cliff = 'M200 131 Q230 120 250 104 L268 96 Q300 92 330 98 L360 104 Q390 112 405 110 V131 Z'
    roofs = ''.join(f'<path class="s1" d="M{300-w} {y} Q{300-w*.4} {y-3} 300 {y-11} Q{300+w*.4} {y-3} {300+w} {y} Z"/>' +
                    f'<rect class="s1" x="{300-w*.62:.0f}" y="{y}" width="{w*1.24:.0f}" height="{gap}"/>'
                    for w, y, gap in [(34, 86, 10), (27, 66, 9), (20, 47, 8)])
    spire = '<rect class="s1" x="299" y="18" width="2" height="20"/>'
    lant = [(276, 92, 1.5), (324, 92, 1.5), (300, 72, 1.2)]
    mist = ''.join(f'<ellipse class="mist" cx="{x}" cy="{y}" rx="{rx}" ry="4"/>' for x, y, rx in [(250, 110, 70), (350, 118, 60), (200, 100, 40)])
    return V('<circle class="moon" cx="350" cy="34" r="20"/>' + hills('M0 131 L0 108 Q60 92 120 104 T230 96 L230 131 Z') +
             f'<path class="s1" d="{cliff}"/>' + roofs + spire + halos(lant, 4) + dots(lant, 'lit') + mist)

def vig_paladin():
    sun = '<circle class="halo" cx="318" cy="112" r="56"/><circle class="halo" cx="318" cy="112" r="36"/><circle class="moon" cx="318" cy="112" r="20"/>'
    rays = ''.join(f'<path class="halo" d="M318 112 L{318+80*math.cos(a-.05):.0f} {112-80*math.sin(a-.05):.0f} L{318+80*math.cos(a+.05):.0f} {112-80*math.sin(a+.05):.0f} Z"/>'
                   for a in [math.pi * k / 9 for k in range(1, 9)])
    sword = 'M314 104 V42 L318 30 L322 42 V104 Z M302 42 H334 V47 H302 Z M315.5 30 V16 H320.5 V30 Z M318 7 a5 5 0 1 0 .01 0 Z'
    hill = 'M150 131 Q230 102 318 100 T410 112 V131 Z'
    return V(rays + sun + f'<path class="s2" d="M0 131 L0 118 Q90 106 180 116 L180 131 Z"/>' + f'<path class="s1" d="{sword}"/>' +
             f'<path class="s1" d="{hill}"/>')

def vig_ranger():
    def pine(x, h, w):
        t = []; n = 4
        for i in range(n):
            y0 = 131 - h * i / n * .9 - 6; y1 = y0 - h * .38; ww = w * (1 - i / (n + 1.2))
            t.append(f'M{x - ww:.0f} {y0:.0f} L{x} {y1:.0f} L{x + ww:.0f} {y0:.0f} Z')
        t.append(f'M{x-2} 131 V{131-8} H{x+2} V131 Z'); return ' '.join(t)
    random.seed(21); trees = []; x = 150
    while x < 410:
        h = random.uniform(48, 96); trees.append(pine(x, h, h * .26)); x += random.uniform(16, 26)
    bird = '<path class="st" d="M246 34 q8 -6 14 0 q6 -6 14 0 q-7 -2 -14 3 q-7 -5 -14 -3z"/>'
    stars = [(190, 20, 1), (300, 14, 1.1), (360, 26, .9), (220, 50, .8)]
    return V(dots(stars) + '<circle class="moon" cx="330" cy="40" r="11"/>' + bird + ridge(13, 118, 30, 70, 50, 's2', 60, .3) +
             f'<path class="s1" d="{" ".join(trees)}"/>')

def vig_rogue():
    random.seed(11); x = 150; p = ['M150 131']; wins = []
    while x < 405:
        w = random.uniform(28, 46); h = random.uniform(40, 82); roof = random.choice(['gable', 'flat', 'gable'])
        p.append(f'L{x:.0f} {131-h:.0f}')
        if roof == 'gable': p.append(f'L{x+w/2:.0f} {131-h-16:.0f} L{x+w:.0f} {131-h:.0f}')
        else:
            p.append(f'L{x+w*.7:.0f} {131-h:.0f} L{x+w*.7:.0f} {131-h-10:.0f} L{x+w*.7+6:.0f} {131-h-10:.0f} L{x+w*.7+6:.0f} {131-h:.0f} L{x+w:.0f} {131-h:.0f}')
        if random.random() < .7 and x > 190: wins.append((x + w * .3, 131 - h + 14))
        x += w
    p.append('L405 131 Z')
    moon = '<circle class="moon" cx="230" cy="34" r="15"/>'
    stars = [(160, 18, 1), (290, 14, 1.2), (330, 40, .9), (380, 22, 1.1), (200, 60, .8)]
    back = 'M0 131 L0 104 L30 104 L30 92 L60 92 L60 100 L95 100 L95 86 L150 86 L150 131 Z'
    return V(dots(stars) + moon + f'<path class="s2" d="{back}"/><path class="s1" d="{" ".join(p)}"/>' +
             ''.join(f'<rect class="lit" x="{wx:.0f}" y="{wy:.0f}" width="6" height="8"/>' for wx, wy in wins))

def vig_sorcerer():
    shards = [(232, 30, 9, -8), (252, 58, 12, 6), (276, 88, 15, -4), (300, 66, 11, 9), (322, 104, 16, -6), (348, 72, 12, 5), (372, 52, 10, -7), (394, 84, 13, 3)]
    p = ' '.join(f'M{x-w} 131 L{x-w*.7:.0f} {131-h*.55:.0f} L{x+lean} {131-h} L{x+w*.7:.0f} {131-h*.6:.0f} L{x+w} 131 Z' for x, h, w, lean in shards)
    random.seed(17); spiral = []
    for i in range(14):
        a = i * .62; r = 8 + i * 3.2; spiral.append((round(300 + r * math.cos(a)), round(42 + r * .55 * math.sin(a)), round(1.5 - i * .06, 2)))
    comet = '<path class="moon" d="M196 22 L250 34 L196 26 Z" opacity=".45"/><circle class="lit" cx="250" cy="34" r="2.2"/>'
    return V(comet + hills('M0 131 L0 118 Q80 104 170 116 L170 131 Z') + f'<path class="s1" d="{p}"/>' + halos(spiral[:5], 4) + dots(spiral, 'lit'))

def vig_warlock():
    moon = '<circle class="halo" cx="300" cy="44" r="40"/><circle class="moon" cx="300" cy="44" r="28"/>'
    eye = '<path class="s1" d="M280 44 Q300 30 320 44 Q300 58 280 44 Z"/><ellipse class="lit" cx="300" cy="44" rx="2.6" ry="7"/>'
    random.seed(5); segs = []
    def br(x, y, a, l, n):
        if n == 0: return
        x2, y2 = x + l * math.cos(a), y - l * math.sin(a)
        segs.append(f'M{x:.0f} {y:.0f} Q{(x+x2)/2 + random.uniform(-5, 5):.0f} {(y+y2)/2 + random.uniform(-5, 5):.0f} {x2:.0f} {y2:.0f}')
        br(x2, y2, a + random.uniform(.3, .7), l * .7, n - 1); br(x2, y2, a - random.uniform(.3, .7), l * .66, n - 1)
    br(352, 116, math.pi / 2 + .12, 34, 5)
    tree = f'<path class="s1 br" d="{" ".join(segs)}"/>'
    hill = 'M210 131 Q290 108 352 112 T410 118 V131 Z'
    motes = [(262, 92, 1.2), (236, 70, .9), (330, 86, 1), (382, 60, .8), (250, 40, .8)]
    return V(moon + eye + hills('M0 131 L0 120 Q90 108 200 118 L200 131 Z') + tree + f'<path class="s1" d="{hill}"/>' + halos(motes, 4) + dots(motes, 'lit'))

def vig_wizard():
    stars = [(150, 20, 1.2), (190, 44, .9), (228, 14, 1.4), (262, 36, 1), (300, 10, 1.1), (392, 30, 1.2), (170, 70, .8), (382, 70, .9)]
    tower = ('M318 131 V58 L314 58 L338 4 L362 58 L358 58 V131 Z'
             'M300 131 V92 L296 92 L310 66 L324 92 L320 92 V131 Z')
    hl = 'M0 131 L0 118 Q60 104 120 114 T240 108 T400 112 L400 131 Z'
    moon = '<path class="moon" d="M248 40 a16 16 0 1 0 14 -24 a12 12 0 1 1 -14 24 Z"/>'
    win = ('<rect class="lit" x="334" y="66" width="7" height="11" rx="3.5"/><rect class="lit" x="334" y="90" width="7" height="11" rx="3.5"/>'
           '<rect class="lit" x="307" y="100" width="5" height="8" rx="2.5"/>')
    motes = [(286, 58, 1.1), (372, 84, 1), (296, 30, .8)]
    return V(dots(stars) + moon + f'<path class="s2" d="{hl}"/><path class="s1" d="{tower}"/>' + win + dots(motes, 'lit'))

VIG = {'': vig_none(), 'Artificer': vig_artificer(), 'Barbarian': vig_barbarian(), 'Bard': vig_bard(), 'Cleric': vig_cleric(),
       'Druid': vig_druid(), 'Fighter': vig_fighter(), 'Monk': vig_monk(), 'Paladin': vig_paladin(), 'Ranger': vig_ranger(),
       'Rogue': vig_rogue(), 'Sorcerer': vig_sorcerer(), 'Warlock': vig_warlock(), 'Wizard': vig_wizard()}

# ───────────────────────── Embleme (Strichzeichnung 120×120) ─────────────────────────
def E(body): return ('<svg class="emb" viewBox="0 0 120 120" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="3" '
                     f'stroke-linecap="round" stroke-linejoin="round">{body}</svg>')

def emb_none(): return E('<path d="M60 14 L68 52 L106 60 L68 68 L60 106 L52 68 L14 60 L52 52 Z"/><circle cx="60" cy="60" r="7"/>')
def emb_artificer():
    return E(f'<path d="{_gear(60, 60, 10, 44, 35, .38)}"/><circle cx="60" cy="60" r="15"/>'
             '<path d="M60 45 V75 M45 60 H75" class="th"/>')
def emb_barbarian():
    return E('<path d="M60 10 V112"/><path d="M63 20 Q98 6 108 40 Q98 74 63 60 Z M57 20 Q22 6 12 40 Q22 74 57 60 Z"/>'
             '<path d="M55 78 H65 M55 88 H65 M55 98 H65" class="th"/>')
def emb_bard():
    return E('<path d="M60 52 C84 52 92 76 86 94 C80 112 40 112 34 94 C28 76 36 52 60 52 Z"/><circle cx="60" cy="80" r="7"/>'
             '<path d="M54 53 L56 18 H64 L66 53"/><path d="M56 18 L52 8 H68 L64 18"/><path d="M57 30 V100 M60 30 V100 M63 30 V100" class="th"/>'
             '<path d="M50 100 H70"/>')
def emb_cleric():
    r = ''.join(f'<path d="M{60+24*math.cos(a):.1f} {60+24*math.sin(a):.1f} L{60+(46 if k%2==0 else 36)*math.cos(a):.1f} {60+(46 if k%2==0 else 36)*math.sin(a):.1f}"/>'
                for k, a in enumerate([2 * math.pi * i / 12 for i in range(12)]))
    return E('<circle cx="60" cy="60" r="17"/><circle cx="60" cy="60" r="7" class="th"/>' + r)
def emb_druid():
    random.seed(7); segs = []
    def br(x, y, a, l, n):
        if n == 0: return
        x2, y2 = x + l * math.cos(a), y - l * math.sin(a)
        segs.append(f'M{x:.0f} {y:.0f}L{x2:.0f} {y2:.0f}'); br(x2, y2, a + .5, l * .7, n - 1); br(x2, y2, a - .5, l * .7, n - 1)
    br(60, 104, math.pi / 2, 30, 4)
    return E(f'<path d="{"".join(segs)}"/><path d="M60 104 Q48 108 36 112 M60 104 Q72 108 84 112 M60 104 V112"/>'
             '<path d="M22 64 C20 34 40 14 60 14 C80 14 100 34 98 64" class="th"/>')
def emb_fighter():
    return E('<path d="M60 6 L66 18 V96 H54 V18 Z"/><path d="M40 96 H80"/><path d="M60 96 V108"/><circle cx="60" cy="112" r="4"/>'
             '<path d="M60 30 C78 30 92 42 92 60 C92 78 78 90 60 90 C42 90 28 78 28 60 C28 42 42 30 60 30 Z" class="th"/>'
             '<path d="M60 18 V92" class="th"/>')
def emb_monk():
    return E('<path d="M60 26 C72 42 72 66 60 82 C48 66 48 42 60 26 Z"/>'
             '<path d="M58 82 C46 76 36 62 36 46 C48 50 56 60 58 70"/><path d="M62 82 C74 76 84 62 84 46 C72 50 64 60 62 70"/>'
             '<path d="M56 84 C40 86 26 78 18 66 C32 64 44 68 52 76"/><path d="M64 84 C80 86 94 78 102 66 C88 64 76 68 68 76"/>'
             '<path d="M24 96 H96 M36 104 H84" class="th"/>')
def emb_paladin():
    return E('<path d="M60 12 L98 24 V58 C98 84 80 100 60 110 C40 100 22 84 22 58 V24 Z"/>'
             '<path d="M60 22 L88 31 V58 C88 78 75 91 60 99 C45 91 32 78 32 58 V31 Z" class="th"/>'
             '<path d="M60 36 V86 M44 52 H76"/>')
def emb_ranger():
    return E('<path d="M42 14 C78 34 78 86 42 106"/><path d="M42 14 V106" class="th"/>'
             '<path d="M20 60 H104"/><path d="M104 60 L94 54 M104 60 L94 66"/><path d="M20 60 L12 52 M20 60 L12 68 M28 60 L20 52 M28 60 L20 68" class="th"/>')
def emb_rogue():
    dag = ('<path d="M0 -50 L7 -14 L0 -8 L-7 -14 Z M-16 -8 H16 M0 -8 V18"/><circle cx="0" cy="23" r="5"/><path d="M0 -44 V-16" class="th"/>')
    return E(f'<g transform="translate(60 60) rotate(38) scale(1.18)">{dag}</g><g transform="translate(60 60) rotate(-38) scale(1.18)">{dag}</g>')
def emb_sorcerer():
    return E('<path d="M60 108 C36 108 24 90 28 70 C31 56 42 48 44 32 C52 40 54 48 54 56 C58 42 66 26 62 10 C80 22 94 44 94 70 C94 92 82 108 60 108 Z"/>'
             '<path d="M60 62 L64 76 L78 80 L64 84 L60 98 L56 84 L42 80 L56 76 Z"/>')
def emb_warlock():
    return E('<path d="M14 60 Q60 18 106 60 Q60 102 14 60 Z"/><circle cx="60" cy="60" r="16"/><path d="M60 46 Q66 60 60 74 Q54 60 60 46 Z"/>'
             '<path d="M60 14 V24 M34 22 L39 31 M86 22 L81 31 M18 36 L25 42 M102 36 L95 42" class="th"/>')
def emb_wizard():
    return E('<path d="M60 108 C44 98 24 98 10 104 V46 C24 40 44 40 60 50 C76 40 96 40 110 46 V104 C96 98 76 98 60 108 Z M60 50 V108"/>'
             '<path d="M18 58 C30 54 42 54 52 60 M18 72 C30 68 42 68 52 74 M68 60 C78 54 90 54 102 58 M68 74 C78 68 90 68 102 72" class="th"/>'
             '<path d="M60 6 L64 22 L80 26 L64 30 L60 44 L56 30 L40 26 L56 22 Z"/>')

EMB = {'': emb_none(), 'Artificer': emb_artificer(), 'Barbarian': emb_barbarian(), 'Bard': emb_bard(), 'Cleric': emb_cleric(),
       'Druid': emb_druid(), 'Fighter': emb_fighter(), 'Monk': emb_monk(), 'Paladin': emb_paladin(), 'Ranger': emb_ranger(),
       'Rogue': emb_rogue(), 'Sorcerer': emb_sorcerer(), 'Warlock': emb_warlock(), 'Wizard': emb_wizard()}

# ─────────── Masken-Symbole (Paket R4, 05.10.2026): <i class="mi mi-<name>"></i> in Knöpfen/Feldern ───────────
# Farbe = currentColor (CSS-Maske), Größe 1.1em → passen sich Schrift und Design (Leather/Classic) an. mi_css() erzeugt
# die CSS-Zeilen für <style id="willowTabs"> (Klasse .mi + je Symbol --mi). Ersetzen bunte Emojis in Knöpfen (R-E3).
MI = {
 'dz':    '<path d="M12 2.5 20.5 7.3v9.4L12 21.5l-8.5-4.8V7.3z"/><path d="M12 7.6l4.4 7.6H7.6z"/><path d="M12 2.5v5.1M20.5 7.3l-4.1 7.9M3.5 7.3l4.1 7.9M7.6 15.2l-4.1 1.5M16.4 15.2l4.1 1.5M7.6 15.2 12 21.5l4.4-6.3"/>',
 'srch':  '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.5 15.5 5 5"/>',
 'filt':  '<path d="M4 5h16l-6.2 7.4V19l-3.6-1.8v-4.8z"/>',
 'exp':   '<path d="M4 9V4h5M15 4h5v5M20 15v5h-5M9 20H4v-5"/>',
 'ext':   '<path d="M14 4h6v6M20 4l-8.5 8.5"/><path d="M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>',
 'shield':'<path d="M12 3 5 6v5.5c0 4.3 3 7.8 7 9.5 4-1.7 7-5.2 7-9.5V6z"/>',
 'swords':'<path d="M4 4l10 10M12 16l4-4M14 14l4.5 4.5"/><path d="M20 4 10 14M8 12l4 4M10 14l-4.5 4.5"/><circle cx="19.3" cy="19.3" r="1"/><circle cx="4.7" cy="19.3" r="1"/>',
 'box':   '<path d="M3.5 7.5 12 3l8.5 4.5v9L12 21l-8.5-4.5z"/><path d="M3.5 7.5 12 12l8.5-4.5M12 12v9"/>',
 'link':  '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
 'trash': '<path d="M4 7h16M9 7V4.5h6V7M6 7l1 13h10l1-13M10 11v6M14 11v6"/>',
 'share': '<path d="M12 3v12M7.5 7.5 12 3l4.5 4.5"/><path d="M8.5 10H6a1 1 0 0 0-1 1v9a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-9a1 1 0 0 0-1-1h-2.5"/>',
 'down':  '<path d="M12 4v11M7.5 10.5 12 15l4.5-4.5"/><path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"/>',
 'up':    '<path d="M12 15V4M7.5 8.5 12 4l4.5 4.5"/><path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"/>',
 'gear':  f'<path d="{_gear(12, 12, 8, 9.6, 7.4)}"/><circle cx="12" cy="12" r="3"/>',
 'hist':  '<path d="M3.5 12a8.5 8.5 0 1 0 2.5-6"/><path d="M3 3v4h4"/><path d="M12 7.5V12l3 2"/>',
 'plus':  '<path d="M12 5v14M5 12h14"/>',
 'check': '<path d="m5 12.5 4.5 4.5L19 7"/>',
 'reset': '<path d="M4.5 12a7.5 7.5 0 1 0 2.2-5.3"/><path d="M4 4v4.5h4.5"/>',
 'pen':   '<path d="M15.5 4.5l4 4L8 20H4v-4z"/><path d="M13.5 6.5l4 4"/>',
}
def mi_css():
    from urllib.parse import quote
    rows = ['.mi{display:inline-block;width:1.1em;height:1.1em;vertical-align:-.2em;flex:0 0 auto;background-color:currentColor;'
            '-webkit-mask:var(--mi) center/contain no-repeat;mask:var(--mi) center/contain no-repeat}']
    for k, body in MI.items():
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="1.8" '
               'stroke-linecap="round" stroke-linejoin="round">' + body + '</svg>')
        rows.append(f'.mi-{k}{{--mi:url("data:image/svg+xml,{quote(svg, safe="")}")}}')
    return '\n'.join(rows)

if __name__ == '__main__':
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else 'design_r_art.html'
    css = ('body{background:#120d09;color:#d6b05c;font-family:serif;margin:10px}.c{display:inline-block;margin:6px;vertical-align:top;text-align:center}'
           '.v{width:390px;height:140px;position:relative;background:#1e1610;overflow:hidden}.hx-vig{position:absolute;right:0;bottom:0;height:100%;width:72%}'
           '.hx-vig .s1{fill:#060403;opacity:.82}.hx-vig .s2{fill:#060403;opacity:.5}.hx-vig .st{fill:#efdcae;opacity:.75}.hx-vig .moon{fill:#eadbb8;opacity:.55}'
           '.hx-vig .lit{fill:#f1dc9a}.hx-vig .halo{fill:#d6b05c;opacity:.07}.hx-vig .mist{fill:#eadbb8;opacity:.06}.hx-vig .br{fill:none;stroke:#060403;stroke-width:3;opacity:.85}'
           '.emb{width:90px;height:90px}.emb .th{stroke-width:1.6}.ico{width:32px;height:32px}')
    h = [f'<style>{css}</style>']
    h += [f'<div class="c"><div class="v">{v}</div>{k or "—"}</div>' for k, v in VIG.items()]
    h += ['<br>'] + [f'<div class="c">{v}<br>{k or "—"}</div>' for k, v in EMB.items()]
    h += ['<br>'] + [f'<div class="c">{v}<br>{k}</div>' for k, v in ICO.items()]
    h += ['<br>'] + [f'<div class="c">{_i(v)}<br>mi-{k}</div>' for k, v in MI.items()]
    open(out, 'w').write('<!doctype html><meta charset="utf-8">' + ''.join(h))
    print(out, 'geschrieben', sum(map(len, VIG.values())), 'Bytes Vignetten,', sum(map(len, EMB.values())), 'Embleme,', sum(map(len, ICO.values())), 'Symbole')
