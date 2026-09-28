#!/usr/bin/env python3
"""spell_merge.py — Zauber einer Klasse in ZB_SPELLS der HTML einpflegen (Anleitung B5)
Aufruf: python3 spell_merge.py DnD_Character_App.html <data-dir> Cleric [--dry]
Regeln: Schlüssel name+src; vorhanden → nur Klasse in classes ergänzen; neu → anhängen;
nie löschen/umbenennen; Quellen = DEFAULT_SOURCES (kein PHB'14); Reprints (reprintedAs) übersprungen.
"""
import json, re, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spell_convert import load_all, convert, spell_classes, DEFAULT_SOURCES, zsrc

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
