#!/usr/bin/env python3
"""Paket D (29.09.2026): Zauber-Tabellen von Subklassen (Eldritch Knight, Arcane Trickster …) aus 5e.tools.

Erzeugt den Block `const SUBCLASS_TABLES={Klasse:{Subklassen-Key:{src, extra:[{k,l}], rows:[{lvl, <k>, slots:[9]}]}}}`
zwischen `// SUBCLASS_TABLES-START` und `// SUBCLASS_TABLES-END` (direkt nach `// RACE_PICKS-END`).

Quelle: `subclassTableGroups` der Subklasse in `src/class-<k>.json` (`setup.sh klassen`), und zwar in der Fassung,
die laut Kommentarzeile `// Quelle: 5e.tools class-<k>.json …` in der App steckt (z. B. „Eldritch Knight=XPHB“).
Nur Subklassen, die in `CLASS_DATA[k].subclass` stehen und eine Zauberplatz-Tabelle (`rowsSpellProgression`) haben.

Aufruf: python3 willow/tools/subclass_tables.py DnD_Character_App.html src [--write]
"""
import json, re, sys, os

def clean(label):
    m = re.match(r'\{@\w+ ([^|}]+)', label)
    return (m.group(1) if m else label).strip()

def cell(v):
    if isinstance(v, dict):  # z. B. {"type":"bonus","value":2}
        if 'value' in v: return v['value']
        return json.dumps(v)
    return '—' if v in (0, None, '') else v

def main():
    html, src = sys.argv[1], sys.argv[2]
    write = '--write' in sys.argv
    s = open(html, encoding='utf-8').read()
    out, errors = {}, []
    for f in sorted(os.listdir(src)):
        m = re.match(r'class-(\w+)\.json$', f)
        if not m: continue
        d = json.load(open(os.path.join(src, f), encoding='utf-8'))
        cls = d['class'][0]['name'] if d.get('class') else m.group(1).title()
        cm = re.search(r'// Quelle: 5e\.tools class-%s\.json[^\n]*' % m.group(1), s)
        vers = dict(re.findall(r'([^,:;]+?)=(\w+)', cm.group(0).split('Fassung:', 1)[1])) if cm and 'Fassung:' in cm.group(0) else {}
        vers = {k.strip(): v for k, v in vers.items()}
        for sc in d.get('subclass', []):
            groups = sc.get('subclassTableGroups') or []
            if not any('rowsSpellProgression' in g for g in groups): continue
            name = sc['name']
            if vers.get(name) != sc['source']: continue
            # Key in CLASS_DATA[cls].subclass (B3: ohne Kürzel, sonst mit)
            key = None
            for k in (name, f'{name} ({sc["source"]})'):
                if re.search(r'CLASS_DATA\["%s"\][\s\S]{0,400000}?\n  "%s":\[' % (re.escape(cls), re.escape(k)), s):
                    key = k; break
            if not key:
                errors.append(f'{cls}/{name}: Key in CLASS_DATA.subclass nicht gefunden'); continue
            extra, rows = [], [{'lvl': i + 1, 'slots': [0] * 9} for i in range(20)]
            for g in groups:
                labels = [clean(x) for x in g.get('colLabels', [])]
                if 'rowsSpellProgression' in g:
                    rs = g['rowsSpellProgression']
                    if len(rs) != 20: errors.append(f'{cls}/{name}: {len(rs)} Zeilen'); continue
                    for i, r in enumerate(rs):
                        rows[i]['slots'] = (list(r) + [0] * 9)[:9]
                else:
                    rs = g.get('rows') or []
                    if len(rs) != 20: errors.append(f'{cls}/{name}: {len(rs)} Zeilen'); continue
                    for j, l in enumerate(labels):
                        k = l.split()[0].lower()
                        extra.append({'k': k, 'l': l})
                        for i, r in enumerate(rs): rows[i][k] = cell(r[j])
            out.setdefault(cls, {})[key] = {'src': sc['source'], 'extra': extra, 'rows': rows}
            first = next((r['lvl'] for r in rows if any(r['slots'])), None)
            print(f'{cls} / {key} ({sc["source"]}): Spalten {[e["l"] for e in extra]}, Plätze ab Stufe {first}, Stufe 20 {rows[19]["slots"][:4]}')
    for e in errors: print('FEHLER', e)
    block = '// SUBCLASS_TABLES-START (tools/subclass_tables.py, 5e.tools subclassTableGroups; Paket D 29.09.2026)\nconst SUBCLASS_TABLES=' + \
            json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n// SUBCLASS_TABLES-END'
    if not write or errors:
        print('(Trockenlauf)' if not errors else 'nicht geschrieben'); return
    if '// SUBCLASS_TABLES-START' in s:
        s = re.sub(r'// SUBCLASS_TABLES-START[\s\S]*?// SUBCLASS_TABLES-END', lambda _: block, s)
    else:
        assert s.count('// RACE_PICKS-END') == 1
        s = s.replace('// RACE_PICKS-END', '// RACE_PICKS-END\n' + block, 1)
    open(html, 'w', encoding='utf-8').write(s)
    print('geschrieben')

if __name__ == '__main__':
    main()
