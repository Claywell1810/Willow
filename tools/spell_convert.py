#!/usr/bin/env python3
"""spell_convert.py — 5e.tools spells-*.json → ZB_SPELLS-Einträge (Anleitung B5)

Als Modul:  from spell_convert import load_all, convert
Als Skript: python3 spell_convert.py <data-dir> zb_old.json   → Abnahmetest gegen den Bestand
  <data-dir> enthält index.json, spells-*.json, gendata-spell-source-lookup.json
"""
import json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from class_extract import clean

SCHOOL = {'A': 'Abjuration', 'C': 'Conjuration', 'D': 'Divination', 'E': 'Enchantment', 'V': 'Evocation',
          'I': 'Illusion', 'N': 'Necromancy', 'T': 'Transmutation'}
# Quellen wie im Bestand (CSV-Export der 5e.tools-Website): kein PHB'14, keine AU/LLK/AitFR-AVT
DEFAULT_SOURCES = {'XPHB', 'XGE', 'TCE', 'FTD', 'FRHoF', 'AI', 'SCC', 'BMT', 'IDRotF', 'AAG', 'SatO', 'EGW', 'GGR', 'EFA'}


def zsrc(s): return "PHB'24" if s == 'XPHB' else s


def plural(n, unit):
    return f'{n} {unit}' + ('' if n == 1 else 's')


def f_time(t):
    t = t[0]; n, u = t['number'], t['unit']
    if u == 'action': return 'Action'
    if u == 'bonus': return 'Bonus'
    if u == 'reaction': return 'Reaction'
    if u == 'minute': return f'{n} Min.'
    if u == 'hour': return f'{n} Hr.'
    return f'{n} {u}'


def f_range(r):
    t = r['type']
    if t in ('sphere', 'cone', 'line', 'radius', 'hemisphere', 'cube', 'emanation', 'cylinder'): return 'Self'
    if t == 'special': return 'Special'
    d = r['distance']; dt = d['type']
    if dt == 'self': return 'Self'
    if dt == 'touch': return 'Touch'
    if dt == 'sight': return 'Sight'
    if dt == 'unlimited': return 'Unlimited'
    if dt == 'feet': return f"{d['amount']} feet" if d['amount'] != 1 else '1 foot'
    if dt == 'miles': return f"{d['amount']} mile" + ('' if d['amount'] == 1 else 's')
    return f"{d.get('amount', '')} {dt}".strip()


def f_duration(ds):
    out = []
    for d in ds:
        t = d['type']
        if t == 'instant': out.append('Instantaneous')
        elif t == 'timed':
            x = plural(d['duration']['amount'], d['duration']['type'])
            out.append(('Concentration, up to ' + x) if d.get('concentration') else x)
        elif t == 'permanent':
            ends = d.get('ends', [])
            out.append('Until dispelled' + (' or triggered' if 'trigger' in ends else ''))
        elif t == 'special': out.append('Special')
        else: out.append(t)
    return ' or '.join(out) + (' (see below)' if len(out) > 1 else '')


def f_comp(c, lvl=0):
    p = []
    if c.get('v'): p.append('V')
    if c.get('s'): p.append('S')
    if 'm' in c:
        m = c['m']; m = m['text'] if isinstance(m, dict) else m
        p.append('M' if m is True else f'M ({clean(m)})')
    if c.get('r'): p.append(f'R ({lvl} gp)')  # Royalty (AI) = Zaubergrad in GP, wie 5e.tools
    return ', '.join(p)


def render(e, out):
    """Absatzliste (CSV-Stil: Absätze mit Leerzeile getrennt)."""
    if isinstance(e, str): out.append(clean(e)); return out
    if isinstance(e, list):
        for x in e: render(x, out)
        return out
    t = e.get('type', 'entries')
    if t in ('entries', 'inset', 'section', 'item'):
        sub = []
        for x in e.get('entries', []) + ([e['entry']] if 'entry' in e else []): render(x, sub)
        if e.get('name'):
            sub = [clean(e['name']) + '. ' + (sub[0] if sub else '')] + sub[1:]
        out.extend(sub)
    elif t == 'list':
        for it in e.get('items', []):
            sub = render(it, [])
            if sub: out.append('• ' + sub[0]); out.extend(sub[1:])
    elif t == 'table':
        lines = []
        if e.get('caption'): lines.append(clean(e['caption']) + ':')
        if e.get('colLabels'): lines.append(' | '.join(clean(x) for x in e['colLabels']))
        for r in e.get('rows', []):
            if isinstance(r, dict): r = r.get('row', [])
            lines.append(' | '.join(cellstr(c) for c in r))
        out.append('\n'.join(lines))
    elif t in ('inline', 'inlineBlock'):
        out.append(''.join(render(x, [])[0] if render(x, []) else '' for x in e.get('entries', [])))
    elif t == 'quote':
        out.append('“' + ' '.join(render(e.get('entries', []), [])) + '”')
        if e.get('by'): out.append('— ' + clean(e['by']))
    elif t in ('insetReadaloud', 'image', 'gallery', 'hr'):
        pass
    else:
        raise ValueError('entry-Typ ' + t)
    return out


def cellstr(c):
    if isinstance(c, (int, float)): return str(c)
    if isinstance(c, str): return clean(c)
    if c.get('type') == 'cell':
        r = c.get('roll', {})
        return str(r['exact']) if 'exact' in r else f"{r.get('min')}–{r.get('max')}"
    return ' '.join(render(c, []))


def higher(sp):
    h = sp.get('entriesHigherLevel')
    if not h: return ''
    return re.sub(r'^At Higher Levels\. ', '', '\n\n'.join(render(h, [])))


def convert(sp, classes):
    school = SCHOOL[sp['school']] + (' (ritual)' if sp.get('meta', {}).get('ritual') else '')
    return {'name': sp['name'], 'src': zsrc(sp['source']), 'grad': sp['level'], 'school': school,
            'zeit': f_time(sp['time']), 'reichweite': f_range(sp['range']), 'dauer': f_duration(sp['duration']),
            'komp': f_comp(sp['components'], sp['level']), 'classes': classes,
            'desc': '\n\n'.join(render(sp['entries'], [])), 'higher': higher(sp)}


def load_all(ddir):
    idx = json.load(open(os.path.join(ddir, 'index.json')))
    spells = []
    for src, fn in idx.items():
        spells += json.load(open(os.path.join(ddir, fn)))['spell']
    look = json.load(open(os.path.join(ddir, 'gendata-spell-source-lookup.json')))
    return spells, look


def spell_classes(look, sp):
    """Alle Klassen laut gendata (class + classVariant), unabhängig von der Klassen-Quelle."""
    e = look.get(sp['source'].lower(), {}).get(sp['name'].lower(), {})
    cs = set()
    for part in ('class', 'classVariant'):
        for _, d in e.get(part, {}).items(): cs |= set(d)
    return cs


if __name__ == '__main__':
    ddir, old = sys.argv[1], sys.argv[2]
    spells, look = load_all(ddir)
    by = {(s['name'], zsrc(s['source'])): s for s in spells}
    z = json.load(open(old))
    FIELDS = ['grad', 'school', 'zeit', 'reichweite', 'dauer', 'komp', 'desc', 'higher']
    diff = {f: [] for f in FIELDS}; miss = []; ok = 0
    for x in z:
        sp = by.get((x['name'], x['src']))
        if not sp: miss.append(x['name']); continue
        c = convert(sp, x['classes'])
        bad = [f for f in FIELDS if c[f] != x[f]]
        for f in bad: diff[f].append((x['name'], x[f], c[f]))
        ok += not bad
    print(f'Bestand {len(z)}, feldgenau identisch {ok}, nicht gefunden {len(miss)} {miss[:5]}')
    for f, l in diff.items():
        print(f'  {f}: {len(l)} Abweichungen')
    json.dump(diff, open('spell_diff.json', 'w'), ensure_ascii=False, indent=1)
    # Einstufung: nur Formatierung (Absatz-/Listen-/Tabellen-Trenner) oder inhaltlich (Errata/Tippfehler)
    norm = lambda t: re.sub(r'[\s•|:–-]+', '', t)
    for f in ('desc', 'higher', 'dauer'):
        form = [n for n, a, b in diff[f] if norm(a) == norm(b)]
        inh = [n for n, a, b in diff[f] if norm(a) != norm(b)]
        print(f'  {f}: nur Formatierung {len(form)}, inhaltlich {len(inh)}: {inh}')
