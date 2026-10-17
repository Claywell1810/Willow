#!/usr/bin/env python3
"""action_convert.py — Standardaktionen für den Actions-Tab (Paket Z2, 17.10.2026)

Aufruf (aus dem Ordner über dem Klon; braucht src/actions.json und src/variantrules.json, setup.sh effekte lädt beide):
    python3 willow/tools/action_convert.py DnD_Character_App.html src [--write]

Erzeugt den Block `const STD_ACTIONS=[…]` zwischen `// STD_ACTIONS-START` und `// STD_ACTIONS-END`:
  [{n, t, x, u?}] für alle XPHB-Einträge aus actions.json (18: Attack … Utilize) plus Unarmed Strike (XPHB-Glossar,
  variantrules.json; steht nicht in actions.json).
  n = Name (heilig, Zustand der Karte hängt an der Karten-id), t = Zeit: 'aktion' | 'bonus' | 'reaktion' | 'frei' (Free)
  | 'varies' (Improvising an Action), x = Text über class_extract.render (Zwischenüberschriften als „Name. Text“),
  u = 1 nur bei Unarmed Strike (Würfel-Knöpfe in der App, Werte aus STR/PB bzw. Monk Martial Arts/Tavern Brawler).
Ohne --write nur Bericht. Erstes Einfügen: Block direkt vor `// COND_DATA-START`.
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from class_extract import render, Ctx  # noqa: E402

SRC = 'XPHB'
UNIT = {'action': 'aktion', 'bonus': 'bonus', 'reaction': 'reaktion'}
ORD = ['aktion', 'bonus', 'reaktion', 'frei', 'varies']
PFLICHT = ('Attack', 'Dash', 'Disengage', 'Dodge', 'Help', 'Hide', 'Influence', 'Magic', 'Ready', 'Search', 'Study',
           'Utilize', 'Opportunity Attack', 'Two-Weapon Fighting', 'Unarmed Strike')


def zeit(e):
    t = (e.get('time') or [None])[0]
    if isinstance(t, dict):
        if t.get('number') != 1 or t.get('unit') not in UNIT:
            sys.exit(f'Zeit nicht unterstützt: {e["name"]} {t}')
        return UNIT[t['unit']]
    if t == 'Free':
        return 'frei'
    if t == 'Varies':
        return 'varies'
    sys.exit(f'Zeit nicht unterstützt: {e["name"]} {t!r}')


def build(src_dir):
    ctx = Ctx({'classFeature': [], 'subclassFeature': []})
    txt = lambda e: '\n'.join(x for x in render(e['entries'], ctx, []) if x.strip())
    acts = json.load(open(os.path.join(src_dir, 'actions.json'), encoding='utf-8'))['action']
    out = [{'n': e['name'], 't': zeit(e), 'x': txt(e)} for e in acts if e['source'] == SRC]
    vr = [e for e in json.load(open(os.path.join(src_dir, 'variantrules.json'), encoding='utf-8'))['variantrule']
          if e['name'] == 'Unarmed Strike' and e['source'] == SRC]
    if len(vr) != 1:
        sys.exit(f'Unarmed Strike (XPHB) {len(vr)}x in variantrules.json')
    out.append({'n': 'Unarmed Strike', 't': 'aktion', 'x': txt(vr[0]), 'u': 1})
    # Reihenfolge: Zeit, dann Unarmed Strike direkt nach Attack, sonst alphabetisch
    key = lambda a: (ORD.index(a['t']), 'Attack ~' if a['n'] == 'Unarmed Strike' else a['n'])
    return sorted(out, key=key)


def main():
    html, src = sys.argv[1], sys.argv[2]
    write = '--write' in sys.argv
    data = build(src)
    fehler = [f'fehlt: {n}' for n in PFLICHT if not any(a['n'] == n for a in data)]
    for a in data:
        if '{@' in a['x'] or not a['x']:
            fehler.append(f'Text leer/Tag nicht aufgelöst: {a["n"]}')
        print(f'  {a["t"]:8} {a["n"]}: {len(a["x"])} Zeichen · {a["x"][:60]!r}')
    if fehler:
        print('FEHLER:', *fehler, sep='\n  ')
        sys.exit(1)
    block = '// STD_ACTIONS-START (tools/action_convert.py, 5e.tools actions.json + variantrules.json XPHB)\nconst STD_ACTIONS=' + \
        json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n// STD_ACTIONS-END\n'
    s = open(html, encoding='utf-8').read()
    m = re.search(r'// STD_ACTIONS-START.*?// STD_ACTIONS-END\n', s, re.S)
    if m:
        neu = s[:m.start()] + block + s[m.end():]
    else:
        k = s.count('// COND_DATA-START')
        if k != 1:
            sys.exit(f'Anker // COND_DATA-START {k}x gefunden')
        i = s.index('// COND_DATA-START')
        neu = s[:i] + block + s[i:]
    print(f'{len(data)} Standardaktionen, Block {len(block)} Bytes' + ('' if write else ' (Bericht, ohne --write)'))
    if write and neu != s:
        open(html, 'w', encoding='utf-8').write(neu)
        print('geschrieben:', html)


if __name__ == '__main__':
    main()
