#!/usr/bin/env python3
"""cond_convert.py — Zustände (Conditions) aus 5e.tools für „Effects & Conditions“ (Paket E, 02.10.2026)

Aufruf (aus dem Ordner über dem Klon, braucht src/conditionsdiseases.json; setup.sh effekte lädt sie):
    python3 willow/tools/cond_convert.py DnD_Character_App.html src [--write]

Erzeugt den Block `const COND_DATA={…}` zwischen `// COND_DATA-START` und `// COND_DATA-END`:
  {Name: Text} für alle XPHB-Conditions (Blinded … Unconscious, Exhaustion) und die XPHB-Status
  Bloodied und Concentration. Text über class_extract.render (Zwischenüberschriften als „Name. Text“).
Ohne --write nur Bericht. Erstes Einfügen: Block direkt vor `// RACE_PICKS-START`.

Willow 2014 (Paket T5, 19.10.2026):  python3 willow/tools/cond_convert.py DnD_Character_App.html src14 --t14 [--write]
  Quelle src14/ (5etools-2014-src), nur PHB mit `srd`: 15 Zustände (Exhaustion mit der 2014-Tabelle „• 1: …“) und der
  Status Concentration; kein Bloodied (kein 2014-Begriff, Weiche h). Schreibt tools/t14/COND_DATA.js (build_2014.py).
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from class_extract import render, Ctx  # noqa: E402

T14 = '--t14' in sys.argv
SRC = 'PHB' if T14 else 'XPHB'
STATUS = ('Concentration',) if T14 else ('Bloodied', 'Concentration')


def build(src_dir):
    d = json.load(open(os.path.join(src_dir, 'conditionsdiseases.json'), encoding='utf-8'))
    ctx = Ctx({'classFeature': [], 'subclassFeature': []})
    out = {}
    for c in d['condition'] + [s for s in d.get('status', []) if s['name'] in STATUS]:
        if c['source'] != SRC or (T14 and not c.get('srd')):
            continue
        lines = [x for x in render(c['entries'], ctx, []) if x.strip()]
        out[c['name']] = '\n'.join(lines)
    return out


def main():
    html, src = sys.argv[1], sys.argv[2]
    write = '--write' in sys.argv
    data = build(src)
    fehler = []
    for n in ('Blinded', 'Charmed', 'Deafened', 'Exhaustion', 'Frightened', 'Grappled', 'Incapacitated', 'Invisible',
              'Paralyzed', 'Petrified', 'Poisoned', 'Prone', 'Restrained', 'Stunned', 'Unconscious', 'Bloodied', 'Concentration'):
        if T14 and n == 'Bloodied':
            continue
        if not data.get(n):
            fehler.append(f'fehlt: {n}')
    for n, t in data.items():
        if '{@' in t:
            fehler.append(f'Tag nicht aufgelöst: {n}')
        print(f'  {n}: {len(t)} Zeichen · {t[:70]!r}')
    if fehler:
        print('FEHLER:', *fehler, sep='\n  ')
        sys.exit(1)
    if T14:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 't14', 'COND_DATA.js')
        line = 'const COND_DATA=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n'
        alt = open(p, encoding='utf-8').read() if os.path.exists(p) else ''
        print(f'{len(data)} Einträge, tools/t14/COND_DATA.js {len(line)} Bytes', '– unverändert' if alt == line else '')
        if write and alt != line:
            open(p, 'w', encoding='utf-8').write(line)
            print('geschrieben')
        return
    block = '// COND_DATA-START (tools/cond_convert.py, 5e.tools conditionsdiseases.json XPHB)\nconst COND_DATA=' + \
        json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n// COND_DATA-END\n'
    s = open(html, encoding='utf-8').read()
    m = re.search(r'// COND_DATA-START.*?// COND_DATA-END\n', s, re.S)
    if m:
        neu = s[:m.start()] + block + s[m.end():]
    else:
        k = s.count('// RACE_PICKS-START')
        if k != 1:
            sys.exit(f'Anker // RACE_PICKS-START {k}x gefunden')
        i = s.index('// RACE_PICKS-START')
        neu = s[:i] + block + s[i:]
    print(f'{len(data)} Einträge, Block {len(block)} Bytes', '– unverändert' if neu == s else '')
    if write and neu != s:
        open(html, 'w', encoding='utf-8').write(neu)
        print('geschrieben')


if __name__ == '__main__':
    main()
