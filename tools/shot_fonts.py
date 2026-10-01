# shot_fonts.py – echte App-Schriften für Bildschirmfotos (seit 02.10.2026, Anleitung B8)
# Die App lädt Cinzel und Crimson Pro von Google Fonts; die Testumgebung erreicht das nicht und zeichnet
# sonst mit einer schmaleren Ersatzschrift → Überstände (Knöpfe, Titel) fallen im Test nicht auf.
# setup.sh fotos installiert @fontsource/cinzel und @fontsource/crimson-pro nach node_modules (Arbeitsordner).
import os

def _base():
    for d in (os.getcwd(), os.path.dirname(os.path.dirname(os.path.abspath(__file__)))):
        for c in (d, os.path.dirname(d)):
            p = os.path.join(c, 'node_modules', '@fontsource')
            if os.path.isdir(os.path.join(p, 'cinzel')): return p
    return None

def faces():
    F = _base()
    if not F: return None
    return ''.join(f"@font-face{{font-family:'{n}';font-weight:{w};src:url('file://{F}/{d}/files/{d}-latin-{w}-normal.woff2') format('woff2')}}"
                   for n, d in [('Cinzel', 'cinzel'), ('Crimson Pro', 'crimson-pro')] for w in (400, 600))

def apply(pg):
    """Nach pg.goto() aufrufen. Gibt True zurück, wenn die echten Schriften aktiv sind."""
    css = faces()
    if not css:
        print('WARNUNG: echte Schriften fehlen (bash willow/tools/setup.sh fotos) – Fotos mit Ersatzschrift, Überstände evtl. unsichtbar')
        return False
    pg.add_style_tag(content=css)
    pg.evaluate("Promise.all([document.fonts.load('16px Cinzel'),document.fonts.load('600 16px Cinzel'),document.fonts.load('16px \"Crimson Pro\"')])")
    pg.wait_for_timeout(300)
    ok = pg.evaluate("document.fonts.check('16px Cinzel')")
    if not ok: print('WARNUNG: Cinzel nicht geladen')
    return ok

# Überstand in Karten: Kind ragt über eine gerahmte Karte (Rahmen + Rundung) hinaus oder Text läuft in sich über.
# Aufruf: pg.evaluate(CARD_CHECK, 'tab-info') → {"Karte > Element": Pixel}; 1–2 px (Knopf-Sperrung) werden ignoriert.
CARD_CHECK = """(tab) => { const out={}; const root=document.getElementById(tab); if(!root) return out;
 for (const c of root.querySelectorAll('*')) { const cs=getComputedStyle(c);
   if(!(parseFloat(cs.borderRightWidth)>0 && parseFloat(cs.borderTopRightRadius)>0) || cs.display==='none') continue;
   const r=c.getBoundingClientRect(); if(!r.width||!r.height) continue;
   for (const e of c.querySelectorAll('*')) { const q=e.getBoundingClientRect(); if(!q.width||!q.height) continue;
     if (/pip|sw-|dot/.test(e.className)) continue;
     const own=(getComputedStyle(e).overflow==='visible'&&!/^(INPUT|SELECT|TEXTAREA)$/.test(e.tagName))?e.scrollWidth-e.clientWidth:0;
     const o=Math.max(q.right-r.right, r.left-q.left, own);
     if (o>2.5) { const k=(c.id?'#'+c.id:'.'+String(c.className).split(' ')[0])+' > '+(e.id?'#'+e.id:'.'+String(e.className||e.tagName).split(' ')[0]); out[k]=Math.max(out[k]||0,Math.round(o)); } } }
 return out; }"""
