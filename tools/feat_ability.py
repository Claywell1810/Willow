"""feat_ability.py — Attributs-Bonus und Mehrfach-Wahl der Feats aus 5e.tools feats.json in FT_FEATS eintragen.

Aufruf (aus dem Ordner über dem Klon):
    python3 willow/tools/feat_ability.py DnD_Character_App.html src [--write]

- Je FT_FEATS-Eintrag (Name + Quelle) aus feats.json:
  `ab`  = Feld `ability` unverändert (Liste; fest `{"con":1}` oder `{"choose":{"from":[…],"amount":n,"count":n,"entry":…}}`,
          optional `max` (Boons 30) und `hidden` (Text steht schon im Feat, z. B. Ability Score Improvement)).
  `rep` = 1, wenn `repeatable` gesetzt ist und das Feat keine Feat-Zauber (`FEAT_SPELLS`) hat
          (deren Wahl hängt am Feat-Namen, Mehrfach-Wahl dort nicht unterstützt, z. B. Magic Initiate).
- Vorhandene `ab`/`rep` werden neu gesetzt (wiederholbar, z. B. nach 5e.tools-Update). Sonst ändert sich nichts.
- Ohne --write nur Bericht.
"""
import json, sys, re

def grab(s, name):
    i = s.index('const ' + name + '=') + len('const ' + name + '=')
    j = s.index('\n', i)
    raw = s[i:j].rstrip()
    end = len(raw) - (1 if raw.endswith(';') else 0)
    return i, i + end, json.loads(raw[:end])

def main():
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    html, src = a[0], a[1]
    write = '--write' in sys.argv
    s = open(html, encoding='utf-8').read()
    i, j, ft = grab(s, 'FT_FEATS')
    m = re.search(r'const FEAT_SPELLS=(\{.*?\});?\n', s)
    fsp = set(json.loads(m.group(1)).keys()) if m else set()
    feats = {(f['name'], f['source']): f for f in json.load(open(src + '/feats.json', encoding='utf-8'))['feat']}
    n_ab = n_rep = 0; fehlt = []; ohne = []
    for e in ft:
        e.pop('ab', None); e.pop('rep', None)
        f = feats.get((e['n'], e['src']))
        if not f:
            fehlt.append(e['n'] + '|' + e['src']); continue
        if f.get('ability'):
            e['ab'] = f['ability']; n_ab += 1
        if f.get('repeatable'):
            if e['n'] in fsp: ohne.append(e['n'])
            else: e['rep'] = 1; n_rep += 1
    print(f'FT_FEATS: {len(ft)} Feats, mit Attributs-Bonus {n_ab}, mehrfach wählbar {n_rep}')
    if ohne: print('  repeatable, aber Feat-Zauber (nicht mehrfach):', ', '.join(ohne))
    if fehlt: print('  nicht in feats.json gefunden:', ', '.join(fehlt))
    if write:
        s = s[:i] + json.dumps(ft, ensure_ascii=False) + s[j:]
        open(html, 'w', encoding='utf-8').write(s)
        print('geschrieben:', html)

if __name__ == '__main__':
    main()
