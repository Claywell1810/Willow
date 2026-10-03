#!/usr/bin/env python3
"""Paket F3 (03.10.2026): Multiclass-Proficiencies aus 5e.tools.

Erzeugt den Block `const CLASS_MC_GAINS={Klasse:{w:[…], a:[…], t:[…], sk:{n, f:[Skills]}|null, src}}`
zwischen `// CLASS_MC_GAINS-START` und `// CLASS_MC_GAINS-END` (direkt nach `// SUBCLASS_TABLES-END`).

Quelle: `multiclassing.proficienciesGained` der Klasse in `src/class-<k>.json` (`setup.sh klassen`), Fassung XPHB
(wie `CLASS_CORE_TRAITS`). w = Waffen, a = Rüstung, t = Werkzeuge (Anzeige-Text, {@item …}-Tags aufgelöst),
sk = Skill-Wahl (n aus f; Namen wie `SKILLS` in der App). Klassen ohne Gewinn (Monk, Sorcerer, Wizard) stehen mit
leeren Listen drin. Das Skript prüft: jede App-Klasse (`CLASS_CORE_TRAITS`) hat eine XPHB-Quelle, jeder Skill-Name
steht in `SKILLS`, keine unbekannten Felder/Werte.

Aufruf: python3 willow/tools/mc_convert.py DnD_Character_App.html src [--write]
"""
import json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from class_extract import main_class   # XPHB-Klasse bzw. Artificer EFA (Paket M)

WEAPON = {'martial': 'Martial weapons', 'simple': 'Simple weapons'}
ARMOR = {'light': 'Light armor', 'medium': 'Medium armor', 'heavy': 'Heavy armor', 'shield': 'Shields'}
KNOWN = {'weapons', 'armor', 'tools', 'skills', 'armorProficiencies', 'weaponProficiencies', 'toolProficiencies', 'skillProficiencies'}


def untag(t):
    t = re.sub(r'\{@\w+ ([^|}]+)(?:\|[^}]*)?\}', r'\1', t)
    if re.search(r'[{}]', t):
        raise ValueError('Tag nicht aufgelöst: ' + t)
    return t


def main():
    html, src = sys.argv[1], sys.argv[2]
    write = '--write' in sys.argv
    s = open(html, encoding='utf-8').read()
    skills = re.search(r'const SKILLS\s*=\s*\[([\s\S]*?)\];', s)
    app_sk = re.findall(r"n:\s*['\"]([^'\"]+)['\"]", skills.group(1)) if skills else []
    if len(app_sk) != 18:
        print('FEHLER SKILLS in der App nicht gelesen:', app_sk); sys.exit(1)
    by_low = {x.lower(): x for x in app_sk}
    m = re.search(r'const CLASS_CORE_TRAITS = \{', s)
    app_cls = re.findall(r'\n  "?(\w+)"?\s*:\s*\{', s[m.end() - 1:s.index('\n};', m.end())]) if m else []
    out, errors = {}, []
    for f in sorted(os.listdir(src)):
        if not re.match(r'class-\w+\.json$', f):
            continue
        d = json.load(open(os.path.join(src, f), encoding='utf-8'))
        for c in d.get('class', []):
            if c is not main_class(d):
                continue
            name = c['name']
            pg = (c.get('multiclassing') or {}).get('proficienciesGained') or {}
            for k in pg:
                if k not in KNOWN:
                    errors.append(f'{name}: unbekanntes Feld {k}')
            e = {'w': [], 'a': [], 't': [], 'sk': None, 'src': c['source']}
            for w in pg.get('weapons', []):
                if w not in WEAPON: errors.append(f'{name}: Waffe {w}'); continue
                e['w'].append(WEAPON[w])
            for a in pg.get('armor', []):
                if a not in ARMOR: errors.append(f'{name}: Rüstung {a}'); continue
                e['a'].append(ARMOR[a])
            for t in pg.get('tools', []):
                try: e['t'].append(untag(t))
                except ValueError as x: errors.append(f'{name}: {x}')
            for sk in pg.get('skills', []):
                ch = sk.get('choose') if isinstance(sk, dict) else None
                if not ch or set(sk) != {'choose'}:
                    errors.append(f'{name}: Skill-Form {sk}'); continue
                fl = []
                for x in ch['from']:
                    if x not in by_low: errors.append(f'{name}: Skill {x} nicht in SKILLS'); continue
                    fl.append(by_low[x])
                if e['sk']: errors.append(f'{name}: mehrere Skill-Wahlen')
                e['sk'] = {'n': ch.get('count', 1), 'f': fl}
            out[name] = e
            print(f"{name}: W {e['w']} · A {e['a']} · T {e['t']} · Skill {e['sk']['n'] if e['sk'] else 0} aus {len(e['sk']['f']) if e['sk'] else 0}")
    for k in app_cls:
        if k not in out:
            errors.append(f'{k}: keine XPHB-Quelle in {src}')
    for e in errors:
        print('FEHLER', e)
    block = ('// CLASS_MC_GAINS-START (tools/mc_convert.py, 5e.tools multiclassing.proficienciesGained XPHB; Paket F3 03.10.2026)\n'
             'const CLASS_MC_GAINS=' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n// CLASS_MC_GAINS-END')
    if not write or errors:
        print('(Trockenlauf)' if not errors else 'nicht geschrieben'); return
    if '// CLASS_MC_GAINS-START' in s:
        s = re.sub(r'// CLASS_MC_GAINS-START[\s\S]*?// CLASS_MC_GAINS-END', lambda _: block, s)
    else:
        assert s.count('// SUBCLASS_TABLES-END') == 1
        s = s.replace('// SUBCLASS_TABLES-END', '// SUBCLASS_TABLES-END\n' + block, 1)
    open(html, 'w', encoding='utf-8').write(s)
    print('geschrieben')


if __name__ == '__main__':
    main()
