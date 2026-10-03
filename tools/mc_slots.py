#!/usr/bin/env python3
"""Paket F4 (03.10.2026): Multiclass-Zauberplätze aus 5e.tools.

Erzeugt den Block
  const MC_SLOTS={rows:[[9 Zahlen] × 20], prog:{Klasse:'full'|'artificer'|'1/2'|'1/3'|'pact'},
                  sub:{Klasse:{Subklasse:{p:'1/3', ab:'INT'}}}, src}
zwischen `// MC_SLOTS-START` und `// MC_SLOTS-END` (direkt nach `// CLASS_MC_GAINS-END`).

Quellen (`setup.sh klassen`):
- `src/book-xphb.json`, Kapitel „Multiclassing“ → Abschnitt „Spellcasting“: Tabelle „Multiclass Spellcaster:
  Spell Slots per Spell Level“ (rows) und die Liste unter „Spell Slots“ (Rundungsregeln, nur zur Prüfung).
- `src/class-<k>.json`: `casterProgression` der XPHB-Klasse (prog) bzw. der neuesten Fassung je Subklasse mit
  eigener Zauberei (sub, z. B. Eldritch Knight/Arcane Trickster, mit `spellcastingAbility`).
Bedeutung in der App (`mcSlotLvl`): full = Klassenstufe, artificer = halbe Stufe aufgerundet (XPHB Paladin/Ranger,
„Half your levels (round up)“), 1/2 = halbe Stufe abgerundet (PHB 2014), 1/3 = ein Drittel abgerundet, pact = Pact Magic
(eigene Plätze, zählt nicht). Das Skript prüft die Rundungsregeln gegen den Buchtext und meldet Abweichungen.

Aufruf: python3 willow/tools/mc_slots.py DnD_Character_App.html src [--write]   (--write nur bei 0 Fehlern)
"""
import json, re, sys, os

AB = {'str': 'STR', 'dex': 'DEX', 'con': 'CON', 'int': 'INT', 'wis': 'WIS', 'cha': 'CHA'}
PROGS = {'full', 'artificer', '1/2', '1/3', 'pact'}


def find(o, pred):
    if isinstance(o, dict):
        if pred(o):
            return o
        for v in o.values():
            r = find(v, pred)
            if r is not None:
                return r
    elif isinstance(o, list):
        for v in o:
            r = find(v, pred)
            if r is not None:
                return r
    return None


def num(x):
    x = str(x).strip()
    return 0 if x in ('—', '-', '') else int(x)


def main():
    html, src = sys.argv[1], sys.argv[2]
    write = '--write' in sys.argv
    errors = []
    book = json.load(open(os.path.join(src, 'book-xphb.json'), encoding='utf-8'))
    mc = find(book, lambda o: o.get('type') == 'section' and o.get('name') == 'Multiclassing')
    sc = mc and find(mc, lambda o: o.get('name') == 'Spellcasting' and o.get('type') == 'entries')
    tab = sc and find(sc, lambda o: o.get('type') == 'table' and 'Multiclass Spellcaster' in str(o.get('caption')))
    if not tab:
        print('FEHLER Tabelle „Multiclass Spellcaster“ nicht gefunden'); sys.exit(1)
    rows = []
    for i, r in enumerate(tab['rows']):
        if num(r[0]) != i + 1 or len(r) != 10:
            errors.append(f'Tabellenzeile {i + 1}: {r}')
        rows.append([num(x) for x in r[1:10]])
    if len(rows) != 20:
        errors.append(f'{len(rows)} Zeilen statt 20')
    items = (find(sc, lambda o: o.get('name') == 'Spell Slots') or {}).get('entries', [])
    lst = next((e for e in items if isinstance(e, dict) and e.get('type') == 'list'), {}).get('items', [])
    txt = ' | '.join(lst)
    print('Buch, Spell Slots:', txt)

    prog, sub = {}, {}
    for f in sorted(os.listdir(src)):
        if not re.match(r'class-\w+\.json$', f):
            continue
        d = json.load(open(os.path.join(src, f), encoding='utf-8'))
        for c in d.get('class', []):
            if c.get('source') != 'XPHB':
                continue
            p = c.get('casterProgression')
            if p:
                if p not in PROGS:
                    errors.append(f"{c['name']}: unbekannte casterProgression {p}")
                prog[c['name']] = p
        newest = {}
        for s in d.get('subclass', []):
            if not s.get('casterProgression') or s.get('className') is None:
                continue
            k = s['name']
            if k not in newest or s.get('source') == 'XPHB' or s.get('classSource') == 'XPHB':
                newest[k] = s
        for k, s in newest.items():
            p, a = s['casterProgression'], AB.get(s.get('spellcastingAbility', ''))
            if p not in PROGS or not a:
                errors.append(f"{s['className']} {k}: {p} / {s.get('spellcastingAbility')}"); continue
            sub.setdefault(s['className'], {})[k] = {'p': p, 'ab': a, 'src': s['source']}

    # Prüfung gegen den Buchtext: volle Zauberer, Paladin/Ranger aufgerundet, EK/AT ein Drittel abgerundet
    m = re.search(r'All your levels in the ([^|]+?) classes', txt)
    full = re.findall(r'[A-Z]\w+', m.group(1)) if m else []
    for k in full:
        if prog.get(k) != 'full':
            errors.append(f'{k}: Buch „all your levels“, Daten {prog.get(k)}')
    m = re.search(r'Half your levels \(round up\) in the ([^|]+?) classes', txt)
    for k in (re.findall(r'[A-Z]\w+', m.group(1)) if m else []):
        if prog.get(k) != 'artificer':
            errors.append(f'{k}: Buch „half, round up“, Daten {prog.get(k)}')
    m = re.search(r'One third of your ([^|]+?) levels \(round down\) if you have the ([^|]+?) subclass', txt)
    if m:
        for k in re.findall(r'[A-Z][\w ]+?(?= or |$)', m.group(2)):
            if not any(k in v and v[k]['p'] == '1/3' for v in sub.values()):
                errors.append(f'{k}: Buch „one third“, nicht in den Subklassen-Daten')
    else:
        errors.append('Regel „One third …“ nicht im Buchtext')
    for k, p in sorted(prog.items()):
        print(f'{k}: {p}')
    for c, v in sorted(sub.items()):
        for k, e in v.items():
            print(f"{c} / {k}: {e['p']} · {e['ab']} · {e['src']}")
    for e in errors:
        print('FEHLER', e)
    out = {'rows': rows, 'prog': prog, 'sub': {c: {k: {'p': e['p'], 'ab': e['ab']} for k, e in v.items()} for c, v in sub.items()},
           'src': 'XPHB'}
    block = ('// MC_SLOTS-START (tools/mc_slots.py, 5e.tools book-xphb „Multiclass Spellcaster“ + casterProgression; Paket F4 03.10.2026)\n'
             'const MC_SLOTS=' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n// MC_SLOTS-END')
    if not write or errors:
        print('(Trockenlauf)' if not errors else 'nicht geschrieben'); return
    s = open(html, encoding='utf-8').read()
    if '// MC_SLOTS-START' in s:
        s = re.sub(r'// MC_SLOTS-START[\s\S]*?// MC_SLOTS-END', lambda _: block, s)
    else:
        assert s.count('// CLASS_MC_GAINS-END') == 1
        s = s.replace('// CLASS_MC_GAINS-END', '// CLASS_MC_GAINS-END\n' + block, 1)
    open(html, 'w', encoding='utf-8').write(s)
    print('geschrieben')


if __name__ == '__main__':
    main()
