#!/usr/bin/env python3
"""bg_convert.py — 5e.tools backgrounds.json → Background-Texte der App (BG_EXTRA[].f) und BG_SPELLS.

Aufruf (aus dem Ordner über dem Klon, braucht src/backgrounds.json):
    python3 willow/tools/bg_convert.py DnD_Character_App.html src [--write]

- BG_EXTRA[].f = voller Text aus 5e.tools `entries`: aus der Kopfliste nur die Punkte, die das Raster
  (Skills/Tools/Origin Feat/Attribute) nicht zeigt (Languages, Equipment …), danach alle Abschnitte
  („Feature: …“, „Specialty“, „Suggested Characteristics“, „Building a … Character“ …) mit Tabellen.
  Abschnittsnamen als Zeile „**Name**“ (renderBgText → .bg-cap), Tabellen im fmtDesc-Format:
  „Caption:“, Kopfzeile „A | B“ ohne Punkt, Zeilen „• a | b“.
- BG_EXTRA[].n/.s/.l bleiben unverändert (Namen sind heilig, B7). Einträge ohne 5e.tools-Fundstelle bleiben wie sie sind.
- BG_SPELLS = {"<Background>": [Zaubernamen]} aus `additionalSpells[].expanded` (Strixhaven, Ravnica):
  diese Zauber kommen auf die Liste der Zauberklasse (Spell List „★ My Class“, slMySpellCtx).
  Namen werden gegen ZB_SPELLS aufgelöst; fehlende werden gemeldet, nicht erfunden.
- `--add AU,RHW,EFA`: Backgrounds dieser Quellen (ohne `reprintedAs`/`_copy`) in BG_DATA ergänzen
  (Felder s/t/f/a aus skillProficiencies/toolProficiencies/feats/ability, sortiert eingefügt) und in BG_EXTRA
  (`l` aus fluff-backgrounds.json). Gleicher Name schon da: nur ersetzen, wenn der alte Eintrag laut
  5e.tools `reprintedAs` auf den neuen zeigt (Name bleibt, nur Quelle/Felder neu, z. B. Haunted One VRGR → RHW),
  sonst melden. Origin Feat nur „Dark Gift nach Wahl“ (RHW) → f leer, Zeile „Feat:“ bleibt im Text.
Ohne --write nur Bericht.
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from class_extract import render, cell, clean  # noqa: E402

HEAD_SKIP = {'skill proficiencies', 'skill proficiency', 'tool proficiencies', 'tool proficiency',
             'ability scores', 'feat'}


def grab(s, name):
    m = re.search(r'const ' + name + r'\s*=\s*', s)
    i = m.end(); d = 0; j = i; q = False; esc = False
    while True:
        c = s[j]
        if q:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == '"': q = False
        elif c == '"': q = True
        elif c in '[{': d += 1
        elif c in ']}':
            d -= 1
            if d == 0: break
        j += 1
    return i, j + 1


def tables_to_text(e):
    """Tabellen im Baum durch fertige Textzeilen ersetzen (fmtDesc-Format)."""
    if isinstance(e, list): return [tables_to_text(x) for x in e]
    if not isinstance(e, dict): return e
    if e.get('type') == 'table':
        L = []
        if e.get('caption'): L.append(clean(e['caption']) + ':')
        if e.get('colLabels'): L.append(' | '.join(clean(x) for x in e['colLabels']))
        for r in e.get('rows', []):
            if isinstance(r, dict): r = r.get('row', [])
            L.append('• ' + ' | '.join(cell(c).replace(' | ', ' / ') for c in r))
        for fn in e.get('footnotes', []): L.extend(render(fn, None, []))
        return {'type': 'entries', 'entries': L}
    out = dict(e)
    for k in ('entries', 'items'):
        if k in out: out[k] = tables_to_text(out[k])
    if 'entry' in out: out['entry'] = tables_to_text(out['entry'])
    return out


SECT = ('entries', 'section', 'inset', 'variant', 'variantSub')


def emit(entries, L):
    # benannte Blöcke (auch verschachtelte, z. B. „Suggested Characteristics“ in „Building a … Character“) → Überschrift
    for x in entries:
        if isinstance(x, dict) and x.get('name') and x.get('type', 'entries') in SECT:
            L.append('**' + clean(x['name']) + '**')
            emit(x.get('entries', []), L)
        else:
            L.extend(render(tables_to_text(x), None, []))


def bg_text(b):
    L = []
    skip = HEAD_SKIP - ({'feat'} if any('anyFromCategory' in x for x in b.get('feats', [])) else set())
    for e in b.get('entries', []):
        if isinstance(e, dict) and e.get('type') == 'list' and not L:
            for it in e.get('items', []):
                nm = clean(it.get('name', '')).rstrip(':').strip()
                if nm.lower() in skip: continue
                body = render(tables_to_text(it.get('entry') or it.get('entries', [])), None, [])
                if body: L.append(f'{nm}: {body[0]}'); L.extend(body[1:])
            continue
        emit([e], L)
    return '\n'.join(x for x in L if x.strip())


def ttl(k):
    return ' '.join(w if w in ('of', 'and', 'the') and i else w[:1].upper() + w[1:] for i, w in enumerate(k.split(' ')))


TOOL_ANY = {'anyArtisansTool': "Any Artisan's Tool", 'anyGamingSet': 'Any Gaming Set', 'anyMusicalInstrument': 'Any Musical Instrument'}


def bg_data(b, featnames):
    sk = []
    for k, v in (b.get('skillProficiencies') or [{}])[0].items():
        if v is True: sk.append(ttl(k))
        elif k == 'choose': sk.append(f"Wähle {v.get('count', 1)}: " + ', '.join(ttl(x) for x in v['from']))
        else: raise ValueError(f"Skill-Form nicht unterstützt: {b['name']}: {k}")
    tl = []
    for k, v in (b.get('toolProficiencies') or [{}])[0].items():
        if v is True: tl.append(ttl(k))
        elif k in TOOL_ANY: tl.append(TOOL_ANY[k])
        else: raise ValueError(f"Tool-Form nicht unterstützt: {b['name']}: {k}")
    ft = ''
    for x in b.get('feats', []):
        k = next(iter(x))
        if k != 'anyFromCategory': ft = featnames.get(k.split('|')[0].split(';')[0].strip(), ttl(k.split('|')[0])); break
    ab = ''
    for x in b.get('ability', []):
        w = (x.get('choose') or {}).get('weighted')
        if w: ab = ', '.join(a.upper() for a in w['from']); break
    return {'n': b['name'], 's': sk, 't': tl, 'f': ft, 'a': ab, 'src': b['source']}


def add_bgs(bgd, ex, bgs, srcs, src):
    featnames = {f['name'].lower(): f['name'] for f in json.load(open(os.path.join(src, 'feats.json'), encoding='utf-8'))['feat']}
    fl = {(f['name'], f['source']): f for f in json.load(open(os.path.join(src, 'fluff-backgrounds.json'), encoding='utf-8'))['backgroundFluff']}
    by = {(b['name'], b['source']): b for b in bgs}
    added, repl, skip = [], [], []
    for b in bgs:
        if b['source'] not in srcs or b.get('reprintedAs') or '_copy' in b: continue
        if any(d['n'] == b['name'] and d['src'] == b['source'] for d in bgd): continue
        new = bg_data(b, featnames)
        old = next((i for i, d in enumerate(bgd) if d['n'] == b['name']), None)
        if old is not None:
            ob = by.get((b['name'], bgd[old]['src'])) or {}
            if f"{b['name']}|{b['source']}" in (ob.get('reprintedAs') or []):
                repl.append(f"{b['name']} {bgd[old]['src']}→{b['source']}"); bgd[old] = new
            else:
                skip.append(f"{b['name']}|{b['source']}"); continue
        else:
            k = next((i for i, d in enumerate(bgd) if d['n'].lower() > b['name'].lower()), len(bgd))
            bgd.insert(k, new); added.append(f"{b['name']}|{b['source']}")
        if not any(e['n'] == b['name'] and e['s'] == b['source'] for e in ex):
            f = fl.get((b['name'], b['source']))
            ex.append({'n': b['name'], 's': b['source'], 'f': '', 'l': '\n'.join(render(f.get('entries', []), None, [])) if f else ''})
    print(f'BG_DATA neu: {len(added)} {added}\n   ersetzt (reprintedAs): {repl or "keine"}\n   Name belegt, übersprungen: {skip or "keine"}')


def main():
    html, src = sys.argv[1], sys.argv[2]
    write = '--write' in sys.argv
    s = open(html, encoding='utf-8').read()
    bgs = json.load(open(os.path.join(src, 'backgrounds.json'), encoding='utf-8'))['background']
    by = {(b['name'], b['source']): b for b in bgs}

    a, z = grab(s, 'BG_EXTRA'); ex = json.loads(s[a:z])
    a2, z2 = grab(s, 'BG_DATA'); bgd = json.loads(s[a2:z2])
    a3, z3 = grab(s, 'ZB_SPELLS'); zb = {x['name'].lower(): x['name'] for x in json.loads(s[a3:z3])}
    assert json.dumps(bgd, ensure_ascii=False) == s[a2:z2], 'BG_DATA-Format weicht ab'
    if '--add' in sys.argv:
        add_bgs(bgd, ex, bgs, sys.argv[sys.argv.index('--add') + 1].split(','), src)

    neu, miss, chg = [], [], 0
    for e in ex:
        b = by.get((e['n'], e['s']))
        if not b or '_copy' in b:
            miss.append(f"{e['n']}|{e['s']}"); neu.append(e); continue
        f = bg_text(b)
        if f != e.get('f', ''): chg += 1
        neu.append(dict(e, f=f))
    print(f'BG_EXTRA: {len(ex)} Einträge, {chg} Texte geändert, ohne Fundstelle: {miss or "keine"}')

    sp, fehlt = {}, []
    for d in bgd:
        b = by.get((d['n'], d['src']))
        if not b: continue
        names = []
        for blk in b.get('additionalSpells', []):
            for lst in (blk.get('expanded') or {}).values():
                for x in (lst if isinstance(lst, list) else []):
                    if not isinstance(x, str): continue
                    k = x.split('#')[0].split('|')[0].strip().lower()
                    if k in zb: names.append(zb[k])
                    else: fehlt.append(f"{d['n']}: {x}")
        if names: sp[d['n']] = names
    print(f'BG_SPELLS: {len(sp)} Backgrounds, {sum(map(len, sp.values()))} Zauber; nicht in ZB_SPELLS: {fehlt or "keine"}')

    if not write: return
    s = s[:a2] + json.dumps(bgd, ensure_ascii=False) + s[z2:]  # BG_DATA steht vor BG_EXTRA
    a, z = grab(s, 'BG_EXTRA')
    s = s[:a] + json.dumps(neu, ensure_ascii=False, separators=(',', ':')) + s[z:]
    line = '// BG_SPELLS (bg_convert.py, 5e.tools additionalSpells.expanded): Zauber, die der Background der Zauberliste hinzufügt\nconst BG_SPELLS=' + json.dumps(sp, ensure_ascii=False, separators=(',', ':')) + ';\n'
    m = re.search(r'// BG_SPELLS \(bg_convert\.py.*\nconst BG_SPELLS=.*;\n', s)
    if m: s = s[:m.start()] + line + s[m.end():]
    else:
        anc = 'const BG_EXTRA_MAP='
        assert s.count(anc) == 1, anc
        s = s.replace(anc, line + anc)
    open(html, 'w', encoding='utf-8').write(s)
    print('geschrieben:', html)


if __name__ == '__main__':
    main()
