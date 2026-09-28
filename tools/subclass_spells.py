#!/usr/bin/env python3
"""subclass_spells.py – erzeugt SUBCLASS_SPELLS und CLASS_SPELL_EXTRA aus 5e.tools (additionalSpells).

Aufruf:  python3 subclass_spells.py DnD_Character_App.html src [--write]
  src/ enthält class-<k>.json aller 12 Klassen und feats.json (5e.tools).
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

HTML, SRC = sys.argv[1], sys.argv[2]
WRITE = '--write' in sys.argv
CLASSES = ['Barbarian', 'Bard', 'Cleric', 'Druid', 'Fighter', 'Monk', 'Paladin', 'Ranger', 'Rogue', 'Sorcerer', 'Warlock', 'Wizard']
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
        c.sort(key=lambda x: x.get('classSource') != 'XPHB')   # 2024-Anpassung zuerst
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
    c = [x for x in data['class'] if x['source'] == 'XPHB'][0]
    feats_x = [f for f in data.get('classFeature', []) if f.get('source') == 'XPHB' and f.get('className') == cls]
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

if '--show' in sys.argv:
    for cls, d in result.items():
        for k, e in d.items():
            if 'filters' in e: print('   Filter', cls, k, e['filters'])

if WRITE:
    js = ('// SUBCLASS_SPELLS-START (erzeugt von subclass_spells.py aus 5e.tools additionalSpells; nicht von Hand ändern)\n'
          'const SUBCLASS_SPELLS=' + json.dumps(result, ensure_ascii=False, separators=(',', ':')) + ';\n'
          'const CLASS_SPELL_EXTRA=' + json.dumps(extra, ensure_ascii=False, separators=(',', ':')) + ';\n'
          '// SUBCLASS_SPELLS-END')
    a, b = html.find('// SUBCLASS_SPELLS-START'), html.find('// SUBCLASS_SPELLS-END')
    assert a > 0 and b > a and html.count('// SUBCLASS_SPELLS-START') == 1, 'Anker fehlt'
    html = html[:a] + js + html[b + len('// SUBCLASS_SPELLS-END'):]
    open(HTML, 'w', encoding='utf-8').write(html)
    print('geschrieben:', HTML)
