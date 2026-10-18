#!/usr/bin/env python3
"""spell_merge.py — Zauber einer Klasse in ZB_SPELLS der HTML einpflegen (Anleitung B5)
Aufruf: python3 spell_merge.py DnD_Character_App.html <data-dir> Cleric [--dry]
Regeln: Schlüssel name+src; vorhanden → nur Klasse in classes ergänzen; neu → anhängen;
nie löschen/umbenennen; Quellen = DEFAULT_SOURCES (kein PHB'14); Reprints (reprintedAs) übersprungen.

Willow 2014 (Paket T3, 18.10.2026):  python3 spell_merge.py 2014/index.html src14 --t14 [--dry]
  erzeugt ZB_SPELLS komplett neu aus src14/spells-phb.json: nur `srd`, SRD-Namen (T-E1, auch {@spell}-Verweise im Text),
  src "PHB", Klassen = gendata-spell-source-lookup class.PHB ∩ Klassen der 2014-App mit Spellcasting (Monk/Astral
  Projection entfällt), Reihenfolge Grad → Name; schreibt tools/t14/ZB_SPELLS.js (build_2014.py ersetzt damit ZB_SPELLS)
  und tools/t14/CLASS_SPELL_MAP.js (leer: keine SRD-Subklasse zaubert über eine fremde Liste, Eldritch Knight/Arcane
  Trickster sind nicht SRD). Folgeschritte: spell_cats.py/spell_rolls.py --t14, bst_convert.py spells --t14.
"""
import json, re, sys, os, collections, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spell_convert import load_all, convert, spell_classes, DEFAULT_SOURCES, zsrc


def main_t14(ddir, dry):
    import class_extract
    class_extract.t14_setup(ddir)
    here = os.path.dirname(os.path.abspath(__file__))
    cd = open(os.path.join(here, 't14', 'CLASS_DATA.js'), encoding='utf-8').read()
    app = set(json.loads(cd[cd.index('=') + 1:cd.rstrip().rindex(';')]))
    caster = set()
    for f in glob.glob(os.path.join(ddir, 'class-*.json')):
        for c in json.load(open(f, encoding='utf-8'))['class']:
            if c['source'] == 'PHB' and c.get('spellcastingAbility') and c['name'] in app: caster.add(c['name'])
    look = json.load(open(os.path.join(ddir, 'gendata-spell-source-lookup.json'), encoding='utf-8'))['phb']
    zb, ohne, weg = [], [], collections.Counter()
    for sp in sorted(json.load(open(os.path.join(ddir, 'spells-phb.json'), encoding='utf-8'))['spell'], key=lambda x: (x['level'], x.get('srd') if isinstance(x.get('srd'), str) else x['name'])):
        if not sp.get('srd'): continue
        cl = set(look.get(sp['name'].lower(), {}).get('class', {}).get('PHB', {}))
        for c in cl - caster: weg[c] += 1
        cl = sorted(cl & caster)
        if not cl: ohne.append(sp['name']); continue
        e = convert(sp, cl)
        e['name'] = class_extract.srd_name(sp['name']); e['src'] = 'PHB'
        zb.append(e)
    assert len({x['name'] for x in zb}) == len(zb), 'doppelte Namen'
    rest = [x['name'] for x in zb if '{@' in json.dumps(x)]
    assert not rest, f'Tag-Rest: {rest[:5]}'
    print(f'ZB_SPELLS 2014: {len(zb)} SRD-Zauber, Klassen mit Liste: {sorted(caster)}')
    print('  je Klasse:', dict(sorted(collections.Counter(c for x in zb for c in x['classes']).items())))
    print('  je Grad:', dict(sorted(collections.Counter(x['grad'] for x in zb).items())))
    print('  SRD-Namen:', ', '.join(x['name'] for x in zb if x['name'] in class_extract.T14['rename'].values()))
    if weg: print('  Klassen ohne eigene Zauberliste übergangen:', dict(weg))
    if ohne: print('  ohne Klasse (nicht übernommen):', ohne)
    if dry: print('(Trockenlauf)'); return
    for name, data in (('ZB_SPELLS', zb), ('CLASS_SPELL_MAP', {})):
        p = os.path.join(here, 't14', name + '.js')
        open(p, 'w', encoding='utf-8').write(f'const {name}=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')
        print('geschrieben', p, os.path.getsize(p), 'Bytes')


if '--t14' in sys.argv:
    main_t14(sys.argv[2], '--dry' in sys.argv); sys.exit(0)

html, ddir, cls = sys.argv[1:4]; dry = '--dry' in sys.argv
s = open(html, encoding='utf-8').read()
m = re.search(r'const ZB_SPELLS=(\[.*?\]);\n', s)
assert m and s.count('const ZB_SPELLS=') == 1
zb = json.loads(m.group(1))
spells, look = load_all(ddir)
idx = {(x['name'], x['src']): x for x in zb}
added, extended, skipped = [], [], collections.Counter()
for sp in sorted(spells, key=lambda x: (x['level'], x['name'])):
    if cls not in spell_classes(look, sp): continue
    if sp['source'] not in DEFAULT_SOURCES: skipped[sp['source']] += 1; continue
    if sp.get('reprintedAs'): skipped['reprint'] += 1; continue
    key = (sp['name'], zsrc(sp['source']))
    if key in idx:
        if cls not in idx[key]['classes']: idx[key]['classes'].append(cls); extended.append(key[0])
    else:
        e = convert(sp, [cls]); zb.append(e); idx[key] = e; added.append(key[0])
print(f'{cls}: neu {len(added)}, Klasse ergänzt {len(extended)}, übersprungen {dict(skipped)}')
print('  neu:', ', '.join(added))
print('  ergänzt:', ', '.join(extended))
print(f'  {cls} gesamt in ZB_SPELLS:', sum(cls in x['classes'] for x in zb), '/ Einträge:', len(zb))
if not dry:
    new = 'const ZB_SPELLS=' + json.dumps(zb, ensure_ascii=False, separators=(',', ':')) + ';\n'
    s = s[:m.start()] + new + s[m.end():]
    open(html, 'w', encoding='utf-8').write(s)
