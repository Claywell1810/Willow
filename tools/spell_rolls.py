#!/usr/bin/env python3
"""SPELL_ROLLS (Paket Q, 03.10.2026): Würfel-Angaben je Zauber aus den 5e.tools-Zauberdaten.

Aufruf (aus dem Ordner über dem Klon, nach `setup.sh zauber`):
    python3 willow/tools/spell_rolls.py DnD_Character_App.html src [--write]

Quelle je Zauber: die Fassung, die `ZB_SPELLS[].src` nennt (PHB'24 = XPHB, sonst gleiche Abkürzung).
Nichts wird erfunden: Werte nur aus 5e.tools-Feldern bzw. -Tags:
  a   spellAttack           'M' | 'R'   (Zauber-Angriffswurf)
  s   savingThrow           ['DEX', …]  (Rettungswurf des Ziels)
  h   1, wenn der Text „half as much damage“ / „half the damage“ enthält (½ bei erfolgreichem Save)
  o   Würfel-Optionen aus {@damage X} (Schaden) bzw. {@dice X} bei Heilung (miscTags HL) / Temp HP (THP)
      {k:'dmg'|'heal'|'temp', d:'2d10+4d6', t:'Bludgeoning + Cold', m:1 (+ Zaubermodifikator), l (Label),
       up:{g, d}  aus {@scaledamage|@scaledice BASE|g-9|INC} (je Platz über g: + INC),
       upk:{g, k} aus „N additional … for each spell slot level above g“ (fester Zuschlag),
       cs:{'1':'1d10','5':'2d10',…} aus scalingLevelDice (Cantrips, Charakterstufe)}
Zwei Würfel in einem Satz („{@damage 2d10} Bludgeoning damage and {@damage 4d6} Cold damage“) = eine Option.
"""
import glob, json, re, sys

ABBR = {'strength': 'STR', 'dexterity': 'DEX', 'constitution': 'CON', 'intelligence': 'INT', 'wisdom': 'WIS', 'charisma': 'CHA'}
TYPES = 'acid|bludgeoning|cold|fire|force|lightning|necrotic|piercing|poison|psychic|radiant|slashing|thunder'
TAG = re.compile(r'\{@(damage|dice) ([^}|]+)(?:\|[^}]*)?\}')
SCALE = re.compile(r'\{@(scaledamage|scaledice) ([^}|]+)\|(\d)-9\|([^}|]+)(?:\|[^}]*)?\}')


def strings(e, out):
    """Alle Textstücke der Einträge (ohne Tabellen: dort stehen Zufallstabellen, keine festen Würfe)."""
    if isinstance(e, str): out.append(e)
    elif isinstance(e, list):
        for x in e: strings(x, out)
    elif isinstance(e, dict) and e.get('type') != 'table':
        for k in ('entries', 'items', 'entry'):
            if k in e: strings(e[k], out)
    return out


def norm(d): return re.sub(r'\s+', '', d)


def plain(t): return re.sub(r'\{@\w+ ([^|}]*)[^}]*\}', r'\1', t)


def typ_after(rest):
    m = re.match(rf'\s*((?:{TYPES})(?:(?:,\s*|,?\s*or\s+)(?:{TYPES}))*)\s+damage', rest, re.I)
    return ' or '.join(x.capitalize() for x in re.split(r',\s*or\s+|,\s*|\s+or\s+', m.group(1))) if m else ''


def typ_before(pre):
    m = re.search(rf'\b({TYPES}) damage equal to\s*$', pre, re.I)
    return m.group(1).capitalize() if m else ''


def options(sp):
    """Würfel-Optionen aus dem Haupttext."""
    tags = set(sp.get('miscTags') or [])
    out = []
    for t in strings(sp.get('entries', []), []):
        ms = list(TAG.finditer(t)); i = 0
        while i < len(ms):
            m = ms[i]; kind, d = m.group(1), norm(m.group(2))
            rest, pre = t[m.end():m.end() + 160], t[max(0, m.start() - 120):m.start()]
            if kind == 'damage':
                o = {'k': 'dmg', 'd': d, 't': typ_after(rest) or typ_before(pre)}
                # „{@damage A} X damage and {@damage B} Y damage“ → eine Option
                while i + 1 < len(ms) and ms[i + 1].group(1) == 'damage':
                    gap = t[m.end():ms[i + 1].start()]
                    if not re.fullmatch(rf'\s*(?:{TYPES})\s+damage\s+(?:and|plus)\s+', gap, re.I): break
                    if re.match(r'\s*(?:' + TYPES + r')\s+damage\s+at the (?:start|end)', t[ms[i + 1].end():], re.I): break  # später (Melf's Acid Arrow)
                    i += 1; m = ms[i]
                    o['d'] += '+' + norm(m.group(2)); o['t'] += ' + ' + typ_after(t[m.end():m.end() + 160])
                    rest = t[m.end():m.end() + 160]
            else:
                win = plain(pre[-80:] + ' ' + rest[:80])
                if 'THP' in tags and (re.search(r'temporary hit points', plain(rest[:60]), re.I) or re.search(r'temporary hit points equal to\s*$', plain(pre), re.I)): o = {'k': 'temp', 'd': d, 't': ''}
                elif 'HL' in tags and re.search(r'hit points', win, re.I) and not re.search(r'temporary hit points', win, re.I): o = {'k': 'heal', 'd': d, 't': ''}
                else: i += 1; continue
            if re.match(r'\s*(?:(?:' + TYPES + r')\s+damage\s+)?plus your spellcasting ability modifier', rest, re.I): o['m'] = 1
            if not any(x['k'] == o['k'] and x['d'] == o['d'] and x['t'] == o['t'] for x in out): out.append(o)
            i += 1
    return out


def scaling(sp, opts, warn):
    hl = ' '.join(strings(sp.get('entriesHigherLevel') or [], []))
    for m in SCALE.finditer(hl):
        bases, g, inc = norm(m.group(2)).split(';'), int(m.group(3)), norm(m.group(4))
        if not re.fullmatch(r'\d+d\d+', inc): warn.append(f"{sp['name']}: Skalierung {m.group(0)} ohne Würfel, übergangen"); continue
        k = 'dmg' if m.group(1) == 'scaledamage' else None
        cand = [o for o in opts if (k is None or o['k'] == k) and (k is not None or o['k'] != 'dmg')]
        # gleiche Basis bei mehreren Optionen (Spirit Guardians Radiant/Necrotic, „4d8;2d8“) → alle
        hit = [o for o in cand if o['d'] in bases or o['d'].split('+')[0] in bases]
        base = '/'.join(bases)
        if not hit:  # Basis im Tag weicht ab (z. B. Ice Storm 2d8 statt 2d10): Typ im Satz davor
            sent = plain(hl[:m.start()]).split('.')[-1].lower()
            hit = [o for o in cand if o['t'] and any(x.strip().lower() in sent for x in o['t'].split('+'))]
            if len(hit) != 1 and len(cand) == 1: hit = cand
            if len(hit) == 1: warn.append(f"{sp['name']}: Skalierungs-Basis {base} ≠ {hit[0]['d']}, per Typ/Einzeloption zugeordnet")
        if not hit:
            warn.append(f"{sp['name']}: Skalierung {m.group(0)} keiner Option zuzuordnen"); continue
        for o in hit: o['up'] = {'g': g, 'd': inc}
    # fester Zuschlag ohne Tag: „You gain 5 additional Temporary Hit Points for each spell slot level above 1.“
    for m in re.finditer(r'(\d+) additional ([^.]*?) for each (?:spell )?slot level above (\d)', plain(hl)):
        what = m.group(2).lower()
        kind = 'temp' if 'temporary hit points' in what else 'heal' if 'hit points' in what else 'dmg' if 'damage' in what else None
        hit = [o for o in opts if o['k'] == kind and 'up' not in o]
        if len(hit) == 1: hit[0]['upk'] = {'g': int(m.group(3)), 'k': int(m.group(1))}
        else: warn.append(f"{sp['name']}: Zuschlag „{m.group(0)}“ keiner Option zuzuordnen")


def cantrip(sp, opts):
    sld = sp.get('scalingLevelDice')
    if not sld: return opts
    sld = sld if isinstance(sld, list) else [sld]
    vals = {norm(v) for x in sld for v in x['scaling'].values()}
    out = []
    for x in sld:
        # Green-Flame Blade: „{{spellcasting_mod}}“ = Zaubermodifikator → Platzhalter MOD (App setzt die Zahl ein)
        sc = {k: norm(v).replace('{{spellcasting_mod}}', 'MOD') for k, v in x['scaling'].items()}
        first = sc[min(sc, key=int)]
        src = next((o for o in opts if o['d'] == first), None) or {'k': 'heal' if 'heal' in x['label'].lower() else 'dmg', 'd': first, 't': ''}
        o = dict(src); o['cs'] = sc
        if not o['t']:
            m = re.search(TYPES, x['label'], re.I)
            if m: o['t'] = m.group(0).capitalize()
        o['l'] = x['label'][0].upper() + x['label'][1:]
        out.append(o)
    return out + [o for o in opts if o['d'] not in vals]


def main():
    html, srcdir = sys.argv[1], sys.argv[2]; write = '--write' in sys.argv
    S = {}
    for f in sorted(glob.glob(srcdir + '/spells-*.json')):
        for s in json.load(open(f, encoding='utf-8')).get('spell', []): S.setdefault(s['name'], []).append(s)
    h = open(html, encoding='utf-8').read()
    a = h.index('const ZB_SPELLS='); line = h[a + 16:h.index('\n', a)].rstrip().rstrip(';')
    Z = json.loads(line)
    res, warn, ohne = {}, [], []
    for z in Z:
        L = S.get(z['name']) or []
        want = 'XPHB' if z['src'] == "PHB'24" else z['src'].lower()
        sp = next((x for x in L if x['source'].lower() == want.lower()), None)
        if not sp: ohne.append(f"{z['name']} ({z['src']})"); continue
        opts = options(sp)
        if sp['level'] == 0: opts = cantrip(sp, opts)
        else: scaling(sp, opts, warn)
        for o in opts:
            if o['k'] == 'dmg' and not o['t']:
                di = sp.get('damageInflict') or []
                o['t'] = di[0].capitalize() if len(di) == 1 else ''
            if 'l' not in o:
                o['l'] = {'heal': 'Healing', 'temp': 'Temporary HP'}.get(o['k']) or (o['t'] + ' damage' if o['t'] else 'Damage')
        r = {}
        if sp.get('spellAttack'): r['a'] = sp['spellAttack'][0]
        if sp.get('savingThrow'): r['s'] = [ABBR[x] for x in sp['savingThrow'] if x in ABBR]
        if re.search(r'half as much damage|half the damage|half as much\b', plain(' '.join(strings(sp.get('entries', []), []))), re.I) and any(o['k'] == 'dmg' for o in opts): r['h'] = 1
        if opts: r['o'] = opts
        if r: res[z['name']] = r
    from collections import Counter
    c = Counter()
    for r in res.values():
        c['Angriff'] += 'a' in r; c['Save'] += 's' in r; c['Save ohne Würfel'] += 's' in r and 'o' not in r; c['½'] += 'h' in r
        for o in r.get('o', []):
            c['Opt ' + o['k']] += 1; c['Hochstufen'] += 'up' in o or 'upk' in o; c['Cantrip-Stufen'] += 'cs' in o
        c['mehrere Optionen'] += len(r.get('o', [])) > 1
    print(f'{len(Z)} Zauber, {len(res)} mit Wurf-Angaben, ohne 5e.tools-Fassung: {ohne}')
    print(dict(c))
    for w in warn: print('  !', w)
    if '--list' in sys.argv:
        for n, r in res.items():
            if len(r.get('o', [])) > 1: print(' ', n, '→', ' | '.join(f"{o['l']}: {o['d']}" for o in r['o']))
    if not write: print('(Trockenlauf, --write schreibt)'); return
    row = 'const SPELL_ROLLS=' + json.dumps(res, ensure_ascii=False, separators=(',', ':')) + ';'
    if 'const SPELL_ROLLS=' in h:
        b = h.index('const SPELL_ROLLS='); h = h[:b] + row + h[h.index('\n', b):]
    else:
        b = h.index('const SPELL_CATS='); e = h.index('\n', b)
        assert h.count('const SPELL_CATS=') == 1
        h = h[:e + 1] + '// SPELL_ROLLS (tools/spell_rolls.py, Paket Q, REFERENZ B21): Angriff/Save/Würfel je Zauber aus 5e.tools\n' + row + '\n' + h[e + 1:]
    open(html, 'w', encoding='utf-8').write(h); print('geschrieben')


if __name__ == '__main__':
    main()
