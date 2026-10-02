#!/usr/bin/env python3
"""armor_convert.py — Rüstungen für die AC-Berechnung (Paket E, 02.10.2026)

Aufruf (aus dem Ordner über dem Klon, braucht src/items-base.json; setup.sh effekte lädt sie):
    python3 willow/tools/armor_convert.py DnD_Character_App.html src [--write]

Erzeugt `const ARMOR_DATA=[…]` zwischen `// ARMOR_DATA-START` und `// ARMOR_DATA-END`:
  [{n, c, ac, str, st}] aus 5e.tools items-base.json, Quelle XPHB, Typen LA/MA/HA/S
  (c = 'L' Light: AC + DEX, 'M' Medium: AC + DEX max 2, 'H' Heavy: AC, 'S' Shield: +AC; Regeln XPHB-Tabelle „Armor“),
  str = Mindest-Stärke (Heavy), st = Nachteil auf Stealth. Sortiert nach Kategorie und AC.
Ohne --write nur Bericht. Erstes Einfügen: direkt vor `// COND_DATA-START`.
"""
import json, os, re, sys

CAT = {'LA': 'L', 'MA': 'M', 'HA': 'H', 'S': 'S'}
ORD = 'LMHS'


def build(src_dir):
    d = json.load(open(os.path.join(src_dir, 'items-base.json'), encoding='utf-8'))
    out = []
    for i in d['baseitem']:
        t = str(i.get('type', '')).split('|')[0]
        if i.get('source') != 'XPHB' or t not in CAT:
            continue
        e = {'n': i['name'], 'c': CAT[t], 'ac': i['ac']}
        if i.get('strength'):
            e['str'] = int(i['strength'])
        if i.get('stealth'):
            e['st'] = 1
        out.append(e)
    out.sort(key=lambda e: (ORD.index(e['c']), e['ac'], e['n']))
    return out


def main():
    html, src = sys.argv[1], sys.argv[2]
    data = build(src)
    for e in data:
        print(' ', e)
    if len([e for e in data if e['c'] != 'S']) < 12 or not any(e['c'] == 'S' for e in data):
        sys.exit('FEHLER: erwartet 12 Rüstungen + Shield')
    block = '// ARMOR_DATA-START (tools/armor_convert.py, 5e.tools items-base.json XPHB)\nconst ARMOR_DATA=' + \
        json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n// ARMOR_DATA-END\n'
    s = open(html, encoding='utf-8').read()
    m = re.search(r'// ARMOR_DATA-START.*?// ARMOR_DATA-END\n', s, re.S)
    if m:
        neu = s[:m.start()] + block + s[m.end():]
    else:
        if s.count('// COND_DATA-START') != 1:
            sys.exit('Anker // COND_DATA-START fehlt')
        i = s.index('// COND_DATA-START')
        neu = s[:i] + block + s[i:]
    print(f'{len(data)} Einträge', '– unverändert' if neu == s else '')
    if '--write' in sys.argv and neu != s:
        open(html, 'w', encoding='utf-8').write(neu)
        print('geschrieben')


if __name__ == '__main__':
    main()
