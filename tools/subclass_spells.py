#!/usr/bin/env python3
"""subclass_spells.py – erzeugt SUBCLASS_SPELLS und CLASS_SPELL_EXTRA aus 5e.tools (additionalSpells).

Aufruf:  python3 subclass_spells.py DnD_Character_App.html src [--write]
  src/ enthält class-<k>.json aller Klassen der App (setup.sh klassen) und feats.json (5e.tools).
  Ohne --write: nur Bericht. Mit --write: Block zwischen den Ankern
  '// SUBCLASS_SPELLS-START' und '// SUBCLASS_SPELLS-END' in der HTML ersetzen
  (vorher `cd.json` mit dump.js erzeugen: ZB_SPELLS-Namen und Subklassen-Keys).

Welche Subklassen-Fassung gilt, steht in der Kommentarzeile '// Quelle: … neueste Fassung: Key=SRC, …'
von build_class.py in der HTML (gleiche Fassung wie die Features).
additionalSpells: prepared / known / expanded / innate → feste Zauber (Name) und Filter
('choose'/'all': level=…|class=…|school=…) → zur Laufzeit gegen ZB_SPELLS ausgewertet.
Zauber, die nicht in ZB_SPELLS stehen (andere Quellen, B5), werden gemeldet, nicht erfunden.
"""
import json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from class_extract import main_class   # XPHB-Klasse bzw. Artificer EFA (Paket M)
from klassen import app_classes        # Paket N: Klassen aus der App

HTML, SRC = sys.argv[1], sys.argv[2]
WRITE = '--write' in sys.argv
CLASSES = app_classes(HTML)   # Paket N (03.10.2026): alle CLASS_DATA-Klassen der HTML statt fester Liste
SCHOOL = {'A': 'Abjuration', 'C': 'Conjuration', 'D': 'Divination', 'E': 'Enchantment', 'V': 'Evocation', 'I': 'Illusion', 'N': 'Necromancy', 'T': 'Transmutation'}
# Fighting-Style-Feats, die Cantrips einer anderen Klasse geben (zählen als Klassenzauber)
FEAT_EXTRA = {'Paladin': 'Blessed Warrior', 'Ranger': 'Druidic Warrior'}

html = open(HTML, encoding='utf-8').read()
cd = json.load(open('cd.json'))
zb_names = {s['name'].lower(): s['name'] for s in cd['ZB']}


def canon(ref):
    """'fire shield|xphb#c' → Name, wie er in ZB_SPELLS steht (oder None)."""
    n = ref.split('#')[0].split('|')[0].strip().lower()
    return zb_names.get(n), n


def parse_filter(f):
    out = {}
    for part in f.split('|'):
        if '=' not in part: continue
        k, v = part.split('=', 1)
        k = k.strip().lower(); vals = [x.strip() for x in v.split(';')]
        if k == 'level': out['grad'] = [int(x) for x in vals]
        elif k == 'class': out['cls'] = [x[:1].upper() + x[1:].lower() for x in vals]
        elif k == 'school': out['school'] = [SCHOOL.get(x.upper(), x) for x in vals]
        elif k == 'source': out['src'] = vals
        else: out.setdefault('unbekannt', []).append(part)
    return out


def collect(node, names, filters, missing):
    """Rekursiv alle Zauber-Refs (Strings) und Filter (choose/all) einsammeln."""
    if isinstance(node, str):
        n, raw = canon(node)
        if n: names.add(n)
        else: missing.add(raw)
    elif isinstance(node, list):
        for x in node: collect(x, names, filters, missing)
    elif isinstance(node, dict):
        for k in ('choose', 'all'):
            if k in node and isinstance(node[k], str):
                filters.append(parse_filter(node[k]))
        for k, v in node.items():
            if k in ('choose', 'all', 'count', 'name', 'ability', 'resourceName'): continue
            collect(v, names, filters, missing)


def add_spells(a_list):
    names, filters, missing = set(), [], set()
    for a in a_list or []:
        for cat in ('prepared', 'known', 'expanded', 'innate'):
            if cat in a: collect(a[cat], names, filters, missing)
    uniq = []
    for f in filters:   # gleiche Liste/Schule/Quelle mit mehreren Graden zusammenführen
        same = next((u for u in uniq if {k: v for k, v in u.items() if k != 'grad'} == {k: v for k, v in f.items() if k != 'grad'}), None)
        if same and 'grad' in same and 'grad' in f: same['grad'] = sorted(set(same['grad']) | set(f['grad']))
        elif f not in uniq: uniq.append(dict(f))
    return names, uniq, missing


def resolve_additional(sc, subs):
    if sc.get('additionalSpells') is not None: return sc['additionalSpells']
    cp = sc.get('_copy')
    if cp:
        for o in subs:
            if o['name'] == cp['name'] and o['source'] == cp['source'] and o.get('classSource', 'PHB') == cp.get('classSource', 'PHB') and '_copy' not in o:
                mod = cp.get('_mod', {})
                if 'additionalSpells' in mod: print('   !! _mod additionalSpells bei', sc['name'])
                return o.get('additionalSpells')
    return None


def find_sub(subs, key, src):
    name = re.sub(r'\s*\([A-Za-z]+\)\s*$', '', key)
    def pick(n, s):
        c = [x for x in subs if x['name'] == n and x['source'] == s]
        c.sort(key=lambda x: x.get('classSource') not in ('XPHB', 'EFA'))   # 2024-Anpassung zuerst (Artificer: EFA)
        return c[0] if c else None
    sc = pick(name, src)
    if sc: return sc
    # Nachdruck unter neuem Namen: reprintedAs-Kette ab dem alten Namen
    seen, todo = set(), [x for x in subs if x['name'] == name]
    while todo:
        x = todo.pop(0)
        for r in x.get('reprintedAs', []) or []:
            r = r if isinstance(r, str) else r.get('uid', '')
            p = r.split('|')
            if len(p) < 4 or (p[0], p[-1]) in seen: continue
            seen.add((p[0], p[-1]))
            nxt = [y for y in subs if y.get('shortName') == p[0] and y['source'] == p[-1]]
            if p[-1] == src and nxt: return nxt[0]
            todo += nxt
    return None


result, report_missing, total = {}, {}, 0
for cls in CLASSES:
    m = re.search(r'// Quelle: 5e\.tools class-' + cls.lower() + r'\.json[^\n]*?neueste Fassung: ([^\n]*)', html)
    if not m: print('!! keine Quellzeile für', cls); continue
    pairs = [p.rsplit('=', 1) for p in m.group(1).split(', ')]
    subs = json.load(open(os.path.join(SRC, f'class-{cls.lower()}.json')))['subclass']
    keys = cd['SUBS'][cls]['keys']
    for key, src in pairs:
        key = key.strip(); src = src.strip()
        if key not in keys: print(f'!! {cls}: Key {key!r} nicht in CLASS_DATA'); continue
        sc = find_sub(subs, key, src)
        if not sc: print(f'!! {cls}/{key} ({src}): Subklasse nicht gefunden'); continue
        names, filters, missing = add_spells(resolve_additional(sc, subs))
        for f in filters:
            if 'unbekannt' in f: print(f'!! {cls}/{key}: Filter unbekannt {f}')
        if not names and not filters: continue
        e = {'src': src}
        if names: e['spells'] = sorted(names)
        if filters: e['filters'] = filters
        result.setdefault(cls, {})[key] = e
        total += len(names)
        if missing: report_missing[f'{cls}/{key} ({src})'] = sorted(missing)
        print(f'   {cls:9} {key:34} {src:6} {len(names):2} Zauber, {len(filters)} Filter' + (f', fehlen in ZB_SPELLS: {len(missing)}' if missing else ''))

own = lambda cls: set(cd['MAP'].get(cls, []))
zb_cls = {s['name']: set(s.get('classes') or []) for s in cd['ZB']}
def own_filter(cls, f):   # Filter nur über die eigene Klassenliste → nichts Neues
    return f.get('cls') and set(f['cls']) <= own(cls) and not f.get('src')

# Subklassen: Filter über die eigene Liste weglassen (z. B. Wizard-Schulen, Eldritch Knight → Wizard)
for cls, d in result.items():
    for key in list(d):
        e = d[key]
        if 'filters' in e:
            e['filters'] = [f for f in e['filters'] if not own_filter(cls, f)]
            if not e['filters']: del e['filters']
        if 'spells' not in e and 'filters' not in e: del d[key]

# Klassen-Ebene: Fighting-Style-Feats (Blessed/Druidic Warrior) und additionalSpells der XPHB-Klasse
feats = {f['name']: f for f in json.load(open(os.path.join(SRC, 'feats.json')))['feat'] if f['source'] == 'XPHB'}
extra = {}
def feat_level(cls, feat_name):
    c = [x for x in json.load(open(os.path.join(SRC, f'class-{cls.lower()}.json')))['class'] if x['source'] == 'XPHB'][0]
    for r in c['classFeatures']:
        r = r if isinstance(r, str) else r['classFeature']
        if r.startswith('Fighting Style|'): return int(r.split('|')[3])
for cls, feat in FEAT_EXTRA.items():
    names, filters, missing = add_spells(feats[feat].get('additionalSpells'))
    assert filters and not names, feat
    extra.setdefault(cls, []).extend({'via': feat, 'lvl': feat_level(cls, feat), **f} for f in filters)
for cls in CLASSES:
    data = json.load(open(os.path.join(SRC, f'class-{cls.lower()}.json')))
    c = main_class(data)
    feats_x = [f for f in data.get('classFeature', []) if f.get('source') == c['source'] and f.get('className') == cls]
    for a in c.get('additionalSpells') or []:
        for cat in ('prepared', 'known', 'expanded', 'innate'):
            blk = a.get(cat) or {}
            nums = [int(k) for k in blk if k.isdigit()]
            for k, v in blk.items():
                lvl = int(k) if k.isdigit() else min(nums)
                names, filters, missing = set(), [], set()
                collect(v, names, filters, missing)
                names = {n for n in names if not (zb_cls.get(n, set()) & own(cls))}
                filters = [f for f in filters if not own_filter(cls, f)]
                if not names and not filters: continue
                # Feature-Name der Stufe, dessen Text den Zauber bzw. die fremde Klasse nennt
                probe = [n.lower() for n in names] + [x.lower() for f in filters for x in f.get('cls', [])]
                via = next((f['name'] for f in feats_x if f['level'] == lvl and any(p in json.dumps(f['entries']).lower() for p in probe)), f'{cls} {lvl}')
                old = next((e for e in extra.get(cls, []) if e['via'] == via and e['lvl'] == lvl and 'spells' in e), None)
                if names:
                    if old: old['spells'] = sorted(set(old['spells']) | names)
                    else: extra.setdefault(cls, []).append({'via': via, 'lvl': lvl, 'spells': sorted(names)})
                for f in filters:
                    if not any(e.get('via') == via and e.get('cls') == f.get('cls') for e in extra.get(cls, [])):
                        extra.setdefault(cls, []).append({'via': via, 'lvl': lvl, **f})
                    else:   # gleiche Liste, weitere Grade (Magical Secrets s6–s9) zusammenführen
                        e = next(e for e in extra[cls] if e.get('via') == via and e.get('cls') == f.get('cls'))
                        e['grad'] = sorted(set(e.get('grad', [])) | set(f.get('grad', [])))
for cls, l in extra.items():
    for e in l: print(f'   Klasse {cls}: {e}')

print(f'\nSubklassen mit Zusatzzaubern: {sum(len(v) for v in result.values())}, feste Zauber: {total}')
print('Nicht in ZB_SPELLS (Quellenregel B5, nicht eingefügt):')
for k, v in report_missing.items(): print('  ', k, ':', ', '.join(v))

# ── ALWAYS_PREP (Paket H, 01.10.2026): automatisch eingetragene Always-Prepared-Zauber nach Stufe ──
# Regel: alle festen Zauber aus `prepared`; aus `known` feste Cantrips immer, feste Zauber ab Grad 1 außer beim Wizard
# (dort heißt „known“ = im Zauberbuch, z. B. Necromancy AU Find Familiar). Seit Paket U (05.10.2026) auch alle festen
# Zauber aus `innate` (ohne Platz/als Ritual/über Ressource wirkbar: Artificer Tinker's Magic Mending, Glamour Command,
# Wild Heart Rituale, Psi Warrior Telekinesis …; die freien Würfe zählen die Tracker der Features). Nicht: `expanded`,
# choose/all-Filter. Alternativen ohne Namen mit je genau einem Zauber (Path of the Giant: Druidcraft oder Thaumaturgy)
# heißen wie dieser Zauber und koppeln an die FEATURE_PICKS-Wahl gleichen Namens.
# Mehrere additionalSpells-Einträge = Alternativen: mit Namen und passender FEATURE_PICKS-Wahl gekoppelt (Landtyp,
# Divine-Soul-Affinität), sonst übersprungen und gemeldet. Format: {Klasse:{Gruppe:{v:Abzeichen,pick?:FEATURE_PICKS-Key,
# s:[[Stufe,Zauber,Option?],…]}}}, Gruppe = 'base' oder CLASS_DATA-Subklassen-Key.
fp_m = re.search(r'const FEATURE_PICKS=(\{.*?\});\n', html)
FPICKS = json.loads(fp_m.group(1)) if fp_m else {}
grad = {s['name']: s['grad'] for s in cd['ZB']}
ap, ap_skip, ap_choose = {}, [], []

def ap_levels(cls, cat, blk, lst, opt):
    for k, v in (blk or {}).items():
        lvl = int(k) if k.isdigit() else (None if cat == 'innate' else 1)   # innate '_' (Archfey Misty Step) = erste Stufe der Gruppe
        names, filters, missing = set(), [], set()
        collect(v, names, filters, missing)
        if filters: ap_choose.append(f'{cls} {cat} L{lvl}')
        for n in sorted(names):
            if cat == 'known' and grad.get(n, 0) > 0 and cls == 'Wizard': continue
            lst.append([lvl, n] + ([opt] if opt else []))

AP_CATS = ('prepared', 'known', 'innate')
def ap_alt_name(x):   # Paket U: unbenannte Alternative mit genau einem festen Zauber → Zaubername
    if x.get('name'): return x['name']
    names, filters, missing = set(), [], set()
    for cat in AP_CATS: collect(x.get(cat) or {}, names, filters, missing)
    return next(iter(names)) if len(names) == 1 and not filters else None

def ap_group(cls, a_list, lst, label, pick_prefix):
    a_list = a_list or []
    named = [ap_alt_name(x) for x in a_list]
    if len(a_list) > 1:
        pk = next((k for k, v in FPICKS.items() if k.startswith(pick_prefix) and all(n in v.get('o', []) for n in named)), None) if all(named) else None
        if not pk:
            if any(c in x for x in a_list for c in AP_CATS): ap_skip.append(f'{label} ({len(a_list)} Alternativen ohne Wahl)')
            return None
    else: pk = None
    for x in a_list:
        for cat in AP_CATS:
            if cat in x: ap_levels(cls, cat, x[cat], lst, ap_alt_name(x) if pk else None)
    m = min([e[0] for e in lst if e[0] is not None], default=1)
    for e in lst:
        if e[0] is None: e[0] = m
    return pk

for cls in CLASSES:
    data = json.load(open(os.path.join(SRC, f'class-{cls.lower()}.json')))
    c = main_class(data)
    lst = []
    ap_group(cls, c.get('additionalSpells'), lst, cls, None)
    if lst: ap.setdefault(cls, {})['base'] = {'v': cls, 's': lst}
    m = re.search(r'// Quelle: 5e\.tools class-' + cls.lower() + r'\.json[^\n]*?neueste Fassung: ([^\n]*)', html)
    for key, src in [p.rsplit('=', 1) for p in m.group(1).split(', ')]:
        key = key.strip(); src = src.strip()
        sc = find_sub(data['subclass'], key, src) if key in cd['SUBS'][cls]['keys'] else None
        if not sc: continue
        lst = []
        pk = ap_group(cls, resolve_additional(sc, data['subclass']), lst, f'{cls}/{key}', f'{cls}|{key}|')
        if not lst: continue
        best = {}
        for e in lst:   # gleicher Zauber (und Option) mehrfach → niedrigste Stufe
            k = (e[1], e[2] if len(e) > 2 else None)
            if k not in best or e[0] < best[k][0]: best[k] = e
        g = {'v': re.sub(r'\s*\([A-Za-z]+\)\s*$', '', key), 's': sorted(best.values(), key=lambda e: (e[0], e[1]))}
        if pk: g['pick'] = pk
        ap.setdefault(cls, {})[key] = g
n_ap = sum(len(g['s']) for d in ap.values() for g in d.values())
print(f'\nALWAYS_PREP: {sum(len(d) for d in ap.values())} Gruppen, {n_ap} Einträge;'
      f' gekoppelt an Wahl: {[f"{c}/{k}" for c, d in ap.items() for k, g in d.items() if "pick" in g]}')
if ap_skip: print('   übersprungen:', '; '.join(ap_skip))
if ap_choose: print('   Auswahl (nicht automatisch):', ', '.join(sorted(set(ap_choose))))

# ── FEAT_SPELLS (Paket H2, 01.10.2026): Zauber aus Feats (alle FT_FEATS-Feats mit additionalSpells, Name+Quelle) ──
# Feats geben ihre Zauber dauerhaft (XPHB: „You always have … prepared“), daher prepared/known/innate gleich behandelt.
# Format: {Feat:[{o:Variante|null, s:[[Stufe,Zauber],…], c:[{k,l,n,f:{grad,cls,school,ritual,from}},…]},…]}
# Stufe = Charakterstufe ('_' = 1); c = Wahl-Plätze (n Zauber aus Filter f, zur Laufzeit gegen ZB_SPELLS).
ft_pairs = re.findall(r'\{"n": "((?:[^"\\]|\\.)*)", "src": "([^"]*)"', html[html.index('const FT_FEATS='):html.index('\n', html.index('const FT_FEATS='))])
feats_all = json.load(open(os.path.join(SRC, 'feats.json')))['feat']
fs, fs_miss = {}, {}
# Rune Shaper (BGG): 5e.tools führt alle 14 Runen-Zauber als fest; laut Text fest nur Comprehend Languages,
# die übrigen nur für die gewählten Runen → nur Comprehend Languages automatisch.
FS_ONLY = {'Rune Shaper': ['Comprehend Languages']}

def fs_filter(x):
    if isinstance(x, dict):   # {"from":[…],"count":n}
        fr = []
        for r in x.get('from', []):
            n, raw = canon(r)
            if n: fr.append(n)
            else: fs_miss.setdefault('from', set()).add(raw)
        return {'from': fr}, x.get('count', 1)
    out, rit = {}, False
    parts = []
    for part in x.split('|'):
        if part.strip().lower().startswith('components & miscellaneous='):
            rit = 'ritual' in part.lower()
        else: parts.append(part)
    out = parse_filter('|'.join(parts))
    if rit: out['ritual'] = True
    return out, None

def fs_walk(node, lvl, fixed, slots, feat):
    if isinstance(node, str):
        n, raw = canon(node)
        if n: fixed.append([lvl, n])
        else: fs_miss.setdefault(feat, set()).add(raw)
    elif isinstance(node, list):
        for x in node: fs_walk(x, lvl, fixed, slots, feat)
    elif isinstance(node, dict):
        if 'choose' in node:
            f, cnt = fs_filter(node['choose'])
            slots.append({'k': 'c%d' % len(slots), 'l': lvl, 'n': node.get('count', cnt or 1), 'f': f})
            return
        for k, v in node.items():
            if k in ('count', 'name', 'ability', 'resourceName'): continue
            fs_walk(v, lvl, fixed, slots, feat)

for name, src in ft_pairs:
    f = next((x for x in feats_all if x['name'] == name and x['source'] == src), None)
    if not f or not f.get('additionalSpells'): continue
    var = []
    for a in f['additionalSpells']:
        fixed, slots = [], []
        for cat in ('prepared', 'known', 'innate'):
            for k, v in (a.get(cat) or {}).items():
                fs_walk(v, int(k) if k.isdigit() else 1, fixed, slots, name)
        if fixed or slots:
            e = {'o': a.get('name') if len(f['additionalSpells']) > 1 else None, 's': sorted({(l, n) for l, n in fixed})}
            e['s'] = [list(x) for x in e['s']]
            if slots: e['c'] = slots
            var.append(e)
    if len(var) > 1 and not all(v['o'] for v in var):
        for i, v in enumerate(var): v['o'] = v['o'] or f'Option {i + 1}'
    if name in FS_ONLY:   # 5e.tools-Daten weiter als der Text (s. FS_ONLY)
        for v in var: v['s'] = [x for x in v['s'] if x[1] in FS_ONLY[name]]
    if var: fs[name] = var
print(f'\nFEAT_SPELLS: {len(fs)} Feats ({", ".join(fs)})')
if fs_miss: print('   nicht in ZB_SPELLS:', {k: sorted(v) for k, v in fs_miss.items()})

if '--show' in sys.argv:
    for k, v in fs.items(): print('   FS', k, json.dumps(v)[:300])
    for cls, d in ap.items():
        for k, g in d.items(): print('   AP', cls, k, g)
    for cls, d in result.items():
        for k, e in d.items():
            if 'filters' in e: print('   Filter', cls, k, e['filters'])

if WRITE:
    js = ('// SUBCLASS_SPELLS-START (erzeugt von subclass_spells.py aus 5e.tools additionalSpells; nicht von Hand ändern)\n'
          'const SUBCLASS_SPELLS=' + json.dumps(result, ensure_ascii=False, separators=(',', ':')) + ';\n'
          'const CLASS_SPELL_EXTRA=' + json.dumps(extra, ensure_ascii=False, separators=(',', ':')) + ';\n'
          'const ALWAYS_PREP=' + json.dumps(ap, ensure_ascii=False, separators=(',', ':')) + ';\n'
          'const FEAT_SPELLS=' + json.dumps(fs, ensure_ascii=False, separators=(',', ':')) + ';\n'
          '// SUBCLASS_SPELLS-END')
    a, b = html.find('// SUBCLASS_SPELLS-START'), html.find('// SUBCLASS_SPELLS-END')
    assert a > 0 and b > a and html.count('// SUBCLASS_SPELLS-START') == 1, 'Anker fehlt'
    html = html[:a] + js + html[b + len('// SUBCLASS_SPELLS-END'):]
    open(HTML, 'w', encoding='utf-8').write(html)
    print('geschrieben:', HTML)
