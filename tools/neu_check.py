#!/usr/bin/env python3
"""neu_check.py – „Was ist neu in 5e.tools?“ (Paket N, 03.10.2026, Anleitung A12)

Vergleicht 5e.tools (src/, `bash willow/tools/setup.sh neu`) je Inhaltsart mit der App und listet, was fehlt oder
einen Nachdruck (`reprintedAs`) / eine neuere Fassung hat – mit Quellen-Kürzel und dem Ablauf, der es einpflegt.

Aufruf (aus dem Ordner über dem Klon):
  python3 willow/tools/neu_check.py DnD_Character_App.html src            # nur Neues seit dem letzten Stand
  python3 willow/tools/neu_check.py DnD_Character_App.html src --alle     # auch bekannte (schon entschiedene) Lücken
  python3 willow/tools/neu_check.py DnD_Character_App.html src --bekannt  # heutigen Stand als „bekannt“ merken

Bekannt-Liste `tools/neu_bekannt.json` = Funde, über die Simon schon entschieden hat („nur auf Wunsch“, absichtlich
nicht). Sie wird nur mit `--bekannt` geschrieben – erst nachdem Simon die neuen Funde gesehen hat. Was eingepflegt
wird, verschwindet beim nächsten Lauf von selbst aus den Funden.

Inhaltsarten: Klassen (class/index.json), Subklassen (je App-Klasse, maßgebliche Fassung), Zauber (alle spells-*.json;
Quellen außerhalb DEFAULT_SOURCES zählen als „andere Quelle“), Feats, Backgrounds (ohne `_copy`), Rassen (ohne `_copy`),
Bestien (Typ beast aus den geladenen Bestiarien bis zum höchsten CR der App). Nur Bericht, ändert nichts.
"""
import json, os, re, subprocess, sys, glob
from collections import defaultdict

T = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, T)
from class_extract import main_class, extract          # noqa: E402
from klassen import app_classes, sub_proposal          # noqa: E402
from spell_convert import DEFAULT_SOURCES, spell_classes   # noqa: E402

args = [a for a in sys.argv[1:] if not a.startswith('--')]
HTML = args[0] if args else 'DnD_Character_App.html'
SRC = args[1] if len(args) > 1 else 'src'
ALLE, BEKANNT = '--alle' in sys.argv, '--bekannt' in sys.argv
KF = os.path.join(T, 'neu_bekannt.json')
html = open(HTML, encoding='utf-8').read()

# ── App-Daten (jsdom, wie dump.js)
EXPR = ("{CD:Object.fromEntries(Object.entries(CLASS_DATA).map(([k,v])=>[k,{list:v.subclassList,keys:Object.keys(v.subclass||{})}])),"
        "SL:SUBCLASS_LABELS,ZB:ZB_SPELLS.map(s=>[s.name,s.src,s.classes]),FT:FT_FEATS.map(f=>[f.n,f.src]),BG:BG_DATA.map(b=>[b.n,b.src]),"
        "RC:Object.entries(RACE_DATA).map(([k,r])=>[k,r.src]),BST:BST_DATA.map(b=>[b.n,b.cr])}")
tmp = os.path.join(os.path.dirname(os.path.abspath(HTML)) or '.', '.neu_app.json')
subprocess.run(['node', os.path.join(T, 'dump.js'), HTML, EXPR, tmp], check=True, stdout=subprocess.DEVNULL)
APP = json.load(open(tmp)); os.remove(tmp)
strip = lambda x: re.sub(r'\s*\([^)]+\)\s*$', '', x).strip()
low = lambda x: x.lower()
J = lambda f: json.load(open(os.path.join(SRC, f), encoding='utf-8')) if os.path.exists(os.path.join(SRC, f)) else None
ref_name = lambda r: (r['uid'] if isinstance(r, dict) else r).split('|')[0]
ref_src = lambda r: ((r['uid'] if isinstance(r, dict) else r).split('|') + ['', ''])[1]
asrc = lambda s: 'XPHB' if s == "PHB'24" else s          # Quellen-Kürzel der App → 5e.tools

F = defaultdict(list)    # Kategorie → [(id, Text)]
fehlt_quelle = []        # fehlende Quelldateien


def add(kat, ident, txt): F[kat].append((ident, txt))


# ── 1) Klassen
idx = J('neu/index.json')
have_cls = {low(c) for c in APP['CD']}
if idx is None:
    fehlt_quelle.append('src/neu/index.json (setup.sh neu)')
else:
    for key, fn in idx.items():
        d = J('neu/' + fn) or J(fn)
        if not d: fehlt_quelle.append('src/neu/' + fn); continue
        try: mc = main_class(d)
        except AssertionError: mc = d['class'][0]
        if low(mc['name']) not in have_cls:
            add('Klassen', mc['name'], f"{mc['name']} ({mc['source']}), {len(sub_proposal(d, mc))} Subklassen → Ablauf Klasse (A4)")

# ── 2) Subklassen + Fassungen (je App-Klasse)
for C in app_classes(html):
    d = J(f'neu/class-{C.lower()}.json') or J(f'class-{C.lower()}.json')
    if not d: fehlt_quelle.append(f'class-{C.lower()}.json'); continue
    mc = main_class(d)
    cm = re.search(r'// Quelle: 5e\.tools class-%s\.json \((\w+)\)([^\n]*)' % C.lower(), html)
    if cm and cm.group(1) != mc['source']:
        add('Fassungen', f'{C}|Klasse', f"{C}: App {cm.group(1)} → 5e.tools {mc['source']} → Klasse neu bauen (build_class.py --rebuild, rebuild_diff.py)")
    old = dict((strip(k), v) for k, v in re.findall(r'([^,:;]+?)=(\w+)', cm.group(2).split('Fassung:', 1)[1])) if cm and 'Fassung:' in cm.group(2) else {}
    try:
        _, _, _, srcs = extract(d, APP['CD'][C]['list'])
        for k, v in srcs.items():
            if k in old and old[k] != v:
                add('Fassungen', f'{C}|{k}|{v}', f"{C} – {k}: App {old[k]} → 5e.tools {v} → build_class.py --rebuild (+ Folgeskripte)")
    except AssertionError as e:
        add('Fassungen', f'{C}|Konverter', f'{C}: Subklassen-Zuordnung nicht eindeutig ({e}) → class_extract.py prüfen')
    keys = {strip(k) for k in APP['CD'][C]['keys']} | {strip(v) for v in (APP['SL'].get(C) or {}).values()}
    allsubs = [s for s in d.get('subclass', []) if s.get('className') == mc['name']]
    by_ss = {(s.get('shortName'), s['source']): s['name'] for s in allsubs}
    def targets(name):   # Nachdruck-Ziele (uid „Kurzname|Klasse|KlassenQ|Quelle“) aller Fassungen dieses Namens
        out = set()
        for s in allsubs:
            if s['name'] == name:
                for r in s.get('reprintedAs') or []:
                    p = (r['uid'] if isinstance(r, dict) else r).split('|')
                    if len(p) > 3 and (p[0], p[3]) in by_ss: out.add(by_ss[(p[0], p[3])])
        return out
    for _ in range(3):   # Nachdruck-Ziele vorhandener Subklassen zählen als vorhanden (Shadow Magic → Shadow Sorcery)
        keys |= {t for k in list(keys) for t in targets(k)}
    subs = [s for s in allsubs if s.get('classSource') == mc['source']]
    for s in subs:
        if s.get('reprintedAs') or s['name'] in keys or targets(s['name']) & keys: continue
        add('Subklassen', f"{C}|{s['name']}|{s['source']}", f"{C}: {s['name']} ({s['source']}) → build_class.py … --rebuild --add-sub \"{s['name']} ({s['source']})\"")

# ── 3) Zauber
zb = {low(n): asrc(s) for n, s, _ in APP['ZB']}
zbc = {(low(n), asrc(s)): set(c) for n, s, c in APP['ZB']}
look = J('gendata-spell-source-lookup.json') or {}
CLS = set(app_classes(html))
sp_all = []
for f in sorted(glob.glob(os.path.join(SRC, 'spells-*.json'))):
    sp_all += json.load(open(f, encoding='utf-8')).get('spell', [])
if not sp_all: fehlt_quelle.append('spells-*.json (setup.sh zauber)')
by_key = {(low(s['name']), s['source']): s for s in sp_all}
for s in sp_all:
    n, q = low(s['name']), s['source']
    cs = spell_classes(look, s) & CLS                       # Klassen der App laut 5e.tools (wie spell_merge.py)
    if (n, q) in zbc and cs - zbc[(n, q)] and not s.get('reprintedAs'):   # Nachdrucke → „Zauber-Nachdrucke“ (spell_merge.py überspringt sie)
        add('Zauber-Klassen', f"{s['name']}|{q}|{','.join(sorted(cs - zbc[(n, q)]))}", f"{s['name']} ({q}): Klasse fehlt {', '.join(sorted(cs - zbc[(n, q)]))} → spell_merge.py <Klasse>")
    if n in zb:
        if zb[n] == q and s.get('reprintedAs'):
            tgt = [r for r in s['reprintedAs'] if (low(ref_name(r)), ref_src(r)) in by_key]
            if tgt: add('Zauber-Nachdrucke', f"{s['name']}|{q}", f"{s['name']}: App {q} → Nachdruck {ref_name(tgt[0])} ({ref_src(tgt[0])}) → spell_merge.py")
        continue
    if s.get('reprintedAs') and any(low(ref_name(r)) in zb for r in s['reprintedAs']): continue
    kat = 'Zauber (andere Quelle)' if q not in DEFAULT_SOURCES or s.get('reprintedAs') else 'Zauber' if cs else 'Zauber (ohne Klassenliste)'
    add(kat, f"{s['name']}|{q}", f"{s['name']} ({q}, Grad {s.get('level')})" + (' → spell_merge.py + Folgeskripte (A12)' if kat == 'Zauber' else ''))


# ── 4) Feats / Backgrounds / Rassen (gleiches Muster: Name fehlt → neu; App-Fassung hat reprintedAs → Nachdruck)
def name_src(kat, items, app_pairs, ablauf, skip_copy=False):
    have = {low(n): s for n, s in app_pairs}
    pairs = {(low(n), s) for n, s in app_pairs}
    for x in items:
        if skip_copy and '_copy' in x: continue
        n, q = low(x['name']), x['source']
        if (n, q) in pairs and x.get('reprintedAs'):
            r = x['reprintedAs'][0]
            if (low(ref_name(r)), ref_src(r)) not in pairs:
                add(kat + '-Nachdrucke', f"{x['name']}|{q}", f"{x['name']}: App {q} → Nachdruck {ref_name(r)} ({ref_src(r)}) → {ablauf}")
            continue
        if n in have or x.get('reprintedAs'): continue
        add(kat, f"{x['name']}|{q}", f"{x['name']} ({q}) → {ablauf}")


ft = J('feats.json'); bg = J('backgrounds.json'); rc = J('races.json')
if ft: name_src('Feats', ft['feat'], APP['FT'], f'feat_add.py … <QUELLE> --write')
else: fehlt_quelle.append('feats.json')
if bg: name_src('Backgrounds', bg['background'], APP['BG'], 'bg_convert.py --add <QUELLE>', skip_copy=True)
else: fehlt_quelle.append('backgrounds.json (setup.sh neu)')
if rc: name_src('Rassen', rc['race'], [(n, asrc(s)) for n, s in APP['RC']], 'nur auf Wunsch (race_convert.py, B13)', skip_copy=True)
else: fehlt_quelle.append('races.json')

# ── 5) Bestien (Typ beast bis zum höchsten CR der App)
def crv(c):
    c = c.get('cr') if isinstance(c, dict) else c
    try: return eval(str(c)) if c not in (None, '', '—') else None
    except Exception: return None


bn = {low(n) for n, _ in APP['BST']}
maxcr = max([crv(c) for _, c in APP['BST'] if crv(c) is not None] or [0])
mons = []
for f in sorted(glob.glob(os.path.join(SRC, 'bestiary-*.json'))):
    mons += json.load(open(f, encoding='utf-8')).get('monster', [])
if not mons: fehlt_quelle.append('bestiary-*.json (setup.sh bestien)')
for m in mons:
    t = m.get('type'); t = t.get('type') if isinstance(t, dict) else t
    if t != 'beast' or m.get('reprintedAs') or '_copy' in m or low(m['name']) in bn: continue
    if any(low(ref_name(r)) in bn for r in m.get('reprintedAs') or []): continue
    c = crv(m.get('cr'))
    if c is None or c > maxcr: continue
    add('Bestien', f"{m['name']}|{m['source']}", f"{m['name']} ({m['source']}, CR {m.get('cr') if not isinstance(m.get('cr'), dict) else m['cr'].get('cr')}) → BST_DATA nur auf Wunsch (bst_convert.py, B11)")

# ── Ausgabe
bek = json.load(open(KF, encoding='utf-8')) if os.path.exists(KF) else {}
KAT = ['Klassen', 'Fassungen', 'Subklassen', 'Zauber', 'Zauber-Klassen', 'Zauber-Nachdrucke', 'Feats', 'Feats-Nachdrucke', 'Backgrounds',
       'Backgrounds-Nachdrucke', 'Rassen', 'Rassen-Nachdrucke', 'Bestien', 'Zauber (ohne Klassenliste)', 'Zauber (andere Quelle)']
commit = ''
try: commit = subprocess.run(['git', 'ls-remote', 'https://github.com/5etools-mirror-3/5etools-src', 'refs/heads/main'], capture_output=True, text=True, timeout=30).stdout[:8]
except Exception: pass
print(f'== Neu-Prüfung 5e.tools{(" main " + commit) if commit else ""} gegen {HTML}' + ('' if bek else '  (noch keine Bekannt-Liste)'))
if fehlt_quelle: print('   Quellen fehlen:', ', '.join(sorted(set(fehlt_quelle))), '→ bash willow/tools/setup.sh neu')
gesamt_neu = 0
for k in KAT:
    L = sorted(set(F.get(k, [])))
    known = set(bek.get(k, []))
    neu = [x for x in L if x[0] not in known]
    alt = [x for x in L if x[0] in known]
    gesamt_neu += len(neu)
    if not L: print(f'-- {k}: nichts'); continue
    print(f'-- {k}: {len(neu)} neu' + (f', {len(alt)} bekannt' if alt else '') + (' (--alle zeigt sie)' if alt and not ALLE else ''))
    for ident, txt in neu + (alt if ALLE else []):
        print(('   ' if ident in known else ' + ') + txt)
if BEKANNT:
    json.dump({k: sorted({x[0] for x in F.get(k, [])}) for k in KAT}, open(KF, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(f'== Bekannt-Liste geschrieben: {KF}')
print(f'== ERGEBNIS: {gesamt_neu} neue Funde' + (' (+ = neu seit der Bekannt-Liste)' if gesamt_neu else ''))
