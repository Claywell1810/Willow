#!/usr/bin/env python3
"""feat_add.py — fehlende Feats aus 5e.tools feats.json in FT_FEATS ergänzen (nur hinzufügen, nichts ändern).

Aufruf (aus dem Ordner über dem Klon, braucht src/feats.json):
    python3 willow/tools/feat_add.py DnD_Character_App.html src AU,RHW [--write]

- Nimmt alle Feats der genannten Quellen ohne `reprintedAs`, die als Name|Quelle noch nicht in FT_FEATS stehen.
  Name schon vorhanden (andere Quelle) → nur melden, nicht einfügen (Namen sind eindeutig, B7).
- Eintrag {n, src, cat, pre, d}: cat = 5e.tools-Kategorie (O, G, FS, EB, DG …), pre aus `prerequisite`
  (Alternativen mit „ or “), d = Text über class_extract.render, Tabellen wie bg_convert.tables_to_text
  („Caption:“, Kopfzeile „A | B“, Zeilen „• a | b“).
- Einfügeposition: vor dem ersten bestehenden Feat mit größerem Namen (bestehende Reihenfolge bleibt).
Ohne --write nur Bericht.
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from class_extract import render, clean, Ctx  # noqa: E402
from bg_convert import tables_to_text  # noqa: E402

ABIL = {'str': 'STR', 'dex': 'DEX', 'con': 'CON', 'int': 'INT', 'wis': 'WIS', 'cha': 'CHA'}


def title(ref):
    n = ref.split('|')[0]
    return ' '.join(w if w in ('of', 'the', 'and') and i else w[:1].upper() + w[1:] for i, w in enumerate(n.split(' ')))


def pre_text(pr):
    alts = []
    for p in pr or []:
        parts = []
        if 'level' in p:
            lv = p['level']; parts.append(f"Level {lv if isinstance(lv, int) else lv.get('level')}")
        for a in p.get('ability', []):
            parts.extend(f'{ABIL[k]} {v}+' for k, v in a.items())
        if p.get('spellcasting2020') or p.get('spellcasting'): parts.append('Spellcasting or Pact Magic Feature')
        for f in p.get('feature', []): parts.append(f'{f} Feature')
        for f in p.get('feat', []): parts.append(title(f))
        for c in p.get('campaign', []): parts.append(f'{c} Campaign')
        if p.get('other'): parts.append(clean(p['other']))
        rest = set(p) - {'level', 'ability', 'spellcasting2020', 'spellcasting', 'feature', 'feat', 'campaign', 'other'}
        assert not rest, f'Voraussetzung nicht unterstützt: {rest}'
        alts.append(', '.join(parts))
    return ' or '.join(alts)


def grab_ft(s):
    i = s.index('const FT_FEATS=') + len('const FT_FEATS=')
    ft, j = json.JSONDecoder().raw_decode(s, i)
    return i, j, ft


def main():
    html, src, srcs = sys.argv[1], sys.argv[2], sys.argv[3].split(',')
    write = '--write' in sys.argv
    s = open(html, encoding='utf-8').read()
    i, j, ft = grab_ft(s)
    feats = json.load(open(os.path.join(src, 'feats.json'), encoding='utf-8'))['feat']
    ctx = Ctx({'classFeature': [], 'subclassFeature': []}, feats=feats)
    have = {(f['n'], f['src']) for f in ft}; names = {f['n'] for f in ft}
    neu, skip = [], []
    for f in feats:
        if f['source'] not in srcs or f.get('reprintedAs') or (f['name'], f['source']) in have: continue
        if f['name'] in names: skip.append(f"{f['name']}|{f['source']}"); continue
        d = '\n'.join(x for x in render(tables_to_text(f['entries']), ctx, []) if x.strip())
        neu.append({'n': f['name'], 'src': f['source'], 'cat': f.get('category', ''), 'pre': pre_text(f.get('prerequisite')), 'd': d})
    print(f'neu: {len(neu)} ({", ".join(x["n"] + "|" + x["src"] for x in neu)}); Name schon vorhanden: {skip or "keine"}')
    if not write: return
    for e in sorted(neu, key=lambda x: x['n'].lower()):
        k = next((x for x, f in enumerate(ft) if f['n'].lower() > e['n'].lower()), len(ft))
        ft.insert(k, e)
    s = s[:i] + json.dumps(ft, ensure_ascii=False) + s[j:]
    open(html, 'w', encoding='utf-8').write(s)
    print('geschrieben:', html)


if __name__ == '__main__':
    main()
