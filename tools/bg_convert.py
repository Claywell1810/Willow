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
    for e in b.get('entries', []):
        if isinstance(e, dict) and e.get('type') == 'list' and not L:
            for it in e.get('items', []):
                nm = clean(it.get('name', '')).rstrip(':').strip()
                if nm.lower() in HEAD_SKIP: continue
                body = render(tables_to_text(it.get('entry') or it.get('entries', [])), None, [])
                if body: L.append(f'{nm}: {body[0]}'); L.extend(body[1:])
            continue
        emit([e], L)
    return '\n'.join(x for x in L if x.strip())


def main():
    html, src = sys.argv[1], sys.argv[2]
    write = '--write' in sys.argv
    s = open(html, encoding='utf-8').read()
    bgs = json.load(open(os.path.join(src, 'backgrounds.json'), encoding='utf-8'))['background']
    by = {(b['name'], b['source']): b for b in bgs}

    a, z = grab(s, 'BG_EXTRA'); ex = json.loads(s[a:z])
    a2, z2 = grab(s, 'BG_DATA'); bgd = json.loads(s[a2:z2])
    a3, z3 = grab(s, 'ZB_SPELLS'); zb = {x['name'].lower(): x['name'] for x in json.loads(s[a3:z3])}

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
