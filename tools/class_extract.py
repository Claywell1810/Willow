#!/usr/bin/env python3
"""class_extract.py — 5e.tools class-<k>.json → Willow-Datenblöcke (Anleitung B6)

Aufruf:  python3 class_extract.py class-cleric.json "Knowledge Domain (PHB)|Life Domain (PHB)|…" > cleric.json
         (zweites Argument = subclassList aus der App, mit | getrennt)

Ausgabe (JSON): base, subclass, table, traits, subclassSources
- Klasse: XPHB-Fassung; gibt es keine (Artificer, seit 03.10.2026), die Fassung ohne `reprintedAs` (EFA) – `main_class()`.
- Subklassen: jeweils die NEUESTE Fassung für die 2024-Klasse (classSource XPHB):
  Subklasse ohne reprintedAs; Alt-Subklassen in der 5e.tools-Anpassung an die 2024-Klasse
  (_copy mit angepassten Stufen). Key = Dropdown-Name ohne Quellen-Kürzel (B3).
- Texte: entries rekursiv, {@…}-Tags aufgelöst, Flavor-Einleitung der Subklasse weggelassen.
"""
import json, re, sys

ATK = {'mw': 'Melee Weapon Attack:', 'rw': 'Ranged Weapon Attack:', 'ms': 'Melee Spell Attack:',
       'rs': 'Ranged Spell Attack:', 'mw,rw': 'Melee or Ranged Weapon Attack:', 'm': 'Melee Attack Roll:',
       'r': 'Ranged Attack Roll:', 'm,r': 'Melee or Ranged Attack Roll:'}
ABIL = {'str': 'Strength', 'dex': 'Dexterity', 'con': 'Constitution', 'int': 'Intelligence', 'wis': 'Wisdom', 'cha': 'Charisma'}
TAG_RE = re.compile(r'\{@(\w+)(?: ([^{}]*))?\}')


def tag_repl(m):
    tag, body = m.group(1), (m.group(2) or '')
    p = body.split('|')
    if tag == 'dc': return 'DC ' + p[0]
    if tag == 'hit': return p[0] if p[0][:1] in '+-' else '+' + p[0]
    if tag == 'chance': return (p[2] if len(p) > 2 and p[2] else p[0] + ' percent')
    if tag in ('atk', 'atkr'): return ATK.get(p[0], p[0])
    if tag == 'h': return 'Hit: '
    if tag == 'recharge': return f'(Recharge {p[0]}–6)' if p[0] else '(Recharge 6)'
    if tag == 'classFeature': return p[5] if len(p) > 5 and p[5] else p[0]
    if tag == 'subclassFeature': return p[7] if len(p) > 7 and p[7] else p[0]
    if tag == 'subclass': return p[4] if len(p) > 4 and p[4] else p[0]  # {@subclass Kurz|Klasse|KQ|SQ|Anzeige} (Artificer EFA)
    if tag == 'quickref': return p[4] if len(p) > 4 and p[4] else p[0]
    if tag == 'deity': return p[3] if len(p) > 3 and p[3] else p[0]
    if tag in ('b', 'i', 'u', 's', 'note', 'bold', 'italic', 'b', 'strike', 'book', 'adventure', '5etools', 'filter', 'link', 'footnote', 'help'):
        return p[0]
    return p[2] if len(p) > 2 and p[2] else p[0]


def clean(s):
    prev = None
    while prev != s:
        prev, s = s, TAG_RE.sub(tag_repl, s)
    assert '{@' not in s, s
    return s


class Ctx:
    def __init__(self, data, optf=None, feats=None, items=None):
        # optf: Liste aus optionalfeatures.json (Manöver, Runen, Arcane Shots …) → refOptionalfeature mit Text
        self.of = {(o['name'].lower(), o['source']): o for o in (optf or [])}
        self.ft = {(o['name'].lower(), o['source']): o for o in (feats or [])}  # feats.json → refFeat
        self.it = {(o['name'].lower(), o['source']): o for o in (items or [])}  # items.json → statblock (Rogue: Psychic Blade)
        self.cf = {}  # (name, classSource, level, source) -> feature
        self.sf = {}  # (name, classSource, short, subSource, level, source) -> feature
        for f in data['classFeature']:
            self.cf[(f['name'], f['classSource'], f['level'], f['source'])] = f
        for f in data['subclassFeature']:
            self.sf[(f['name'], f['classSource'], f['subclassShortName'], f['subclassSource'], f['level'], f['source'])] = f

    def resolve_sf(self, f):
        if '_copy' in f:
            c = f['_copy']
            base = self.sf[(c['name'], c['classSource'], c['subclassShortName'], c['subclassSource'], c['level'], c['source'])]
            base = self.resolve_sf(base)
            out = dict(base); out.update({k: v for k, v in f.items() if k != '_copy'})
            assert '_mod' not in c, 'TODO _mod: ' + f['name']
            return out
        return f

    def cf_ref(self, ref):
        p = ref.split('|')
        name, cls, csrc, lvl = p[0], p[1], p[2] or 'PHB', int(p[3])
        src = p[4] if len(p) > 4 and p[4] else csrc
        return self.cf[(name, csrc, lvl, src)]

    def sf_ref(self, ref):
        p = ref.split('|')
        name, csrc, short, ssrc, lvl = p[0], p[2] or 'PHB', p[3], p[4] or 'PHB', int(p[5])
        src = p[6] if len(p) > 6 and p[6] else ssrc
        return self.resolve_sf(self.sf[(name, csrc, short, ssrc, lvl, src)])


def cell(c):
    if isinstance(c, str): return clean(c)
    if isinstance(c, (int, float)): return str(c)
    if isinstance(c, dict) and c.get('type') == 'cell':
        r = c.get('roll', {})
        if 'exact' in r: return str(r['exact'])
        return f"{r.get('min')}–{r.get('max')}"
    return render(c, None)


def render(e, ctx, lines=None):
    """Gibt Liste von Textzeilen zurück."""
    out = [] if lines is None else lines
    if isinstance(e, str):
        out.append(clean(e)); return out
    if isinstance(e, list):
        bullet = False  # lose `item`s nach „…features:“ = Liste ohne list-Hülle (5e.tools Artificer Guardian, Paket M)
        for x in e:
            if isinstance(x, dict) and x.get('type') == 'item' and x.get('name') and bullet:
                sub = render(x, ctx, [])
                if sub: out.append('• ' + sub[0]); out.extend(sub[1:])
                continue
            bullet = isinstance(x, str) and x.rstrip().endswith(':')
            render(x, ctx, out)
        return out
    t = e.get('type', 'entries')
    if t in ('entries', 'inset', 'section', 'variant', 'variantSub', 'item', 'optfeature'):
        sub = []
        for x in e.get('entries', []) + ([e['entry']] if 'entry' in e else []): render(x, ctx, sub)
        if e.get('name'):
            if sub: sub[0] = clean(e['name']) + '. ' + sub[0]
            else: sub = [clean(e['name']) + '.']
        out.extend(sub)
    elif t == 'list':
        for it in e.get('items', []):
            sub = render(it, ctx, [])
            if sub: out.append('• ' + sub[0]); out.extend(sub[1:])
    elif t == 'table':
        if e.get('caption'): out.append(clean(e['caption']) + ':')
        rows = e.get('rows', [])
        ncol = len(e.get('colLabels', rows[0] if rows else []))
        if ncol > 2 and e.get('colLabels'): out.append(' | '.join(clean(x) for x in e['colLabels']))
        for r in rows:
            if isinstance(r, dict): r = r.get('row', [])
            cs = [cell(c) for c in r]
            out.append('• ' + (cs[0] + ': ' + ', '.join(cs[1:]) if ncol == 2 else ' | '.join(cs)))
        for fn in e.get('footnotes', []): out.append(clean(fn) if isinstance(fn, str) else text(fn, ctx))
    elif t == 'options':
        for x in e.get('entries', []):
            sub = render(x, ctx, [])
            if sub: out.append(sub[0] if sub[0].startswith('• ') else '• ' + sub[0]); out.extend(sub[1:])
    elif t == 'refClassFeature':
        f = ctx.cf_ref(e['classFeature'])
        sub = render(f['entries'], ctx, [])
        out.append(f['name'] + ': ' + (sub[0] if sub else '')); out.extend(sub[1:])
    elif t == 'refSubclassFeature':
        f = ctx.sf_ref(e['subclassFeature'])
        sub = render(f['entries'], ctx, [])
        out.append(f['name'] + ': ' + (sub[0] if sub else '')); out.extend(sub[1:])
    elif t == 'refOptionalfeature':
        p = e['optionalfeature'].split('|')
        o = ctx.of.get((p[0].lower(), (p[1] if len(p) > 1 and p[1] else 'PHB'))) if ctx else None
        if not o:
            out.append('• ' + clean(p[0]))
        else:
            lv = [x['level']['level'] for x in o.get('prerequisite', []) if isinstance(x.get('level'), dict)]
            sub = render(o['entries'], ctx, [])
            out.append('• ' + clean(o['name']) + (f' (Level {lv[0]}+)' if lv else '') + '. ' + (sub[0] if sub else ''))
            out.extend(sub[1:])
    elif t == 'refFeat':
        p = e['feat'].split('|')
        o = ctx.ft.get((p[0].lower(), (p[1] if len(p) > 1 and p[1] else 'PHB'))) if ctx else None
        if not o:
            out.append('• ' + clean(p[0]))
        else:
            sub = render(o['entries'], ctx, [])
            out.append('• ' + clean(o['name']) + '. ' + (sub[0] if sub else ''))
            out.extend(sub[1:])
    elif t == 'abilityDc':
        out.append(f"{clean(e['name'])} save DC = 8 + {' or '.join(ABIL[a] for a in e['attributes'])} modifier + Proficiency Bonus")
    elif t == 'abilityAttackMod':
        out.append(f"{clean(e['name'])} attack modifier = {' or '.join(ABIL[a] for a in e['attributes'])} modifier + Proficiency Bonus")
    elif t in ('inline', 'inlineBlock'):
        out.append(''.join(render(x, ctx, [])[0] if not isinstance(x, str) else clean(x) for x in e.get('entries', [])))
    elif t == 'statblock' and e.get('tag') == 'item':
        # Verweis auf einen Gegenstand (Rogue Soulknife: Psychic Blade) → Eigenschaften aus items.json als eine Zeile
        o = ctx.it.get((e['name'].lower(), e.get('source', 'PHB'))) if ctx else None
        if not o:
            out.append('• ' + clean(e['name']))
        else:
            PROP = {'F': 'Finesse', 'T': 'Thrown', 'L': 'Light', 'H': 'Heavy', 'R': 'Reach', '2H': 'Two-Handed', 'A': 'Ammunition', 'LD': 'Loading', 'V': 'Versatile', 'S': 'Special'}
            DMG = {'B': 'Bludgeoning', 'P': 'Piercing', 'S': 'Slashing', 'Y': 'Psychic'}
            props = [PROP[x.split('|')[0]] for x in o.get('property', [])]
            if 'Thrown' in props and o.get('range'): props[props.index('Thrown')] = f"Thrown (range {o['range']})"
            mast = [m if isinstance(m, str) else m['uid'] for m in o.get('mastery', [])]
            notes = [m['note'] for m in o.get('mastery', []) if isinstance(m, dict) and m.get('note')]
            parts = [f"{o['weaponCategory'].capitalize()} {'Melee' if o['type'] == 'M' else 'Ranged'} weapon", f"{o['dmg1']} {DMG[o['dmgType']]} damage"]
            if props: parts.append(', '.join(props))
            for mu in mast: parts.append(mu.split('|')[0] + ' mastery' + (f" ({notes[0]})" if notes else ''))
            out.append('• ' + clean(o['name']) + ': ' + '; '.join(parts) + '.')
    elif t in ('quote', 'insetReadaloud', 'image', 'gallery', 'hr'):
        pass
    else:
        raise ValueError('Unbekannter entry-Typ: ' + t)
    return out


LVL_HDR = re.compile(r'^\d+(?:st|nd|rd|th)-level .+ feature$', re.I)


def text(entries, ctx):
    # Zeilen wie "1st-level Peace Domain feature" (TCE-Überschriften) entfallen – Stufe steht im Feld lvl
    return '\n'.join(x for x in render(entries, ctx, []) if x.strip() and not LVL_HDR.match(x.strip()))


ACTION_PATS = [('Bonusaktion', r'\bBonus Action\b'), ('Reaktion', r'\bReaction\b'),
               ('Aktion', r'\b(?:Magic action|Utilize action|an action|your action|as an action|use an action|Action to)\b')]


def feat_tag(desc):
    best = None
    for tag, pat in ACTION_PATS:
        m = re.search(pat, desc, re.I)
        if m and (best is None or m.start() < best[0]): best = (m.start(), tag)
    return best[1] if best else 'Passiv'


def feature(name, lvl, desc):
    return {'lvl': lvl, 'name': clean(name), 'desc': desc, 'tag': feat_tag(desc)}


def main_class(data):
    """Maßgebliche Klassen-Fassung: XPHB, sonst die einzige ohne `reprintedAs` (Artificer: EFA ersetzt TCE)."""
    x = [c for c in data['class'] if c['source'] == 'XPHB']
    if x: return x[0]
    x = [c for c in data['class'] if not c.get('reprintedAs')]
    assert len(x) == 1, [(c['name'], c['source']) for c in data['class']]
    return x[0]


def extract(data, dropdown, optf=None, feats=None, items=None):
    ctx = Ctx(data, optf, feats, items)
    cls = main_class(data)
    # --- base
    base = []
    for ref in cls['classFeatures']:
        r = ref['classFeature'] if isinstance(ref, dict) else ref
        if r.split('|')[0].lower() == 'subclass feature': continue  # Artificer (EFA): Verweis „Subclass Feature“, Eintrag „Subclass feature“
        f = ctx.cf_ref(r)
        base.append(feature(f['name'], f['level'], text(f['entries'], ctx)))
    # --- subclasses
    subs = [s for s in data['subclass'] if s['className'] == cls['name'] and s.get('classSource') == cls['source']]
    def resolved(s):
        if '_copy' in s:
            c = s['_copy']
            o = next(x for x in data['subclass'] if x['name'] == c['name'] and x['source'] == c['source'] and x.get('classSource', 'PHB') == c['classSource'] and '_copy' not in x)
            r = dict(o); r.update({k: v for k, v in s.items() if k != '_copy'})
            return r
        return s
    subs = [resolved(s) for s in subs]
    out, srcs = {}, {}
    keys = {re.sub(r'\s*\([^)]+\)\s*$', '', x).strip() for x in dropdown}
    for dd in dropdown:
        key = re.sub(r'\s*\([^)]+\)\s*$', '', dd).strip()
        cands = [s for s in subs if s['name'] == key and not s.get('reprintedAs')]
        if not cands:  # Nachdruck unter NEUEM Namen (nur Sorcerer bisher), Key bleibt Dropdown-Name
            old = [s for s in subs if s['name'] == key and s.get('reprintedAs')]
            if len(old) == 1:
                rp = old[0]['reprintedAs'][0]; rp = rp['uid'] if isinstance(rp, dict) else rp
                short, ssrc = rp.split('|')[0], rp.split('|')[3]
                tgt = [s for s in subs if s.get('shortName') == short and s['source'] == ssrc and not s.get('reprintedAs')]
                if tgt and tgt[0]['name'] in keys:
                    cands = old  # Nachdruck steht selbst im Dropdown (Draconic Bloodline → Draconic Sorcery): alte Fassung (5e.tools-Anpassung) behalten
                else:
                    cands = tgt  # sonst Nachdruck-Kette folgen (Shadow Magic XGE → Shadow Sorcery RHW) → SUBCLASS_LABELS
        assert len(cands) == 1, (dd, [(s['name'], s['source']) for s in cands])
        s = cands[0]; srcs[key] = s['source']
        feats = []
        for ref in s['subclassFeatures']:
            f = ctx.sf_ref(ref if isinstance(ref, str) else ref['subclassFeature'])
            lvl = int((ref if isinstance(ref, str) else ref['subclassFeature']).split('|')[5])
            if f['name'] == s['name']:
                # Einleitung: Flavor weglassen; Tabellen/benannte Blöcke/Refs übernehmen
                pending_str = None
                for e in f['entries']:
                    if isinstance(e, str):
                        pending_str = e; continue
                    t = e.get('type')
                    if t == 'refSubclassFeature':
                        sf = ctx.sf_ref(e['subclassFeature'])
                        feats.append(feature(sf['name'], lvl, text(sf['entries'], ctx)))
                    elif t == 'table':
                        if not ((pending_str and re.search(r'spell', pending_str, re.I)) or 'Spells' in (e.get('caption') or '')):
                            pending_str = None; continue  # z. B. Götter-Tabelle = Flavor
                        pre = [pending_str] if pending_str and re.search(r'spell', pending_str, re.I) else []
                        feats.append(feature('Domain Spells' if 'Domain' in s['name'] else (e.get('caption') or 'Subclass Spells'), lvl, text(pre + [dict(e, caption=None)], ctx)))
                    elif t == 'entries' and e.get('name'):
                        if feats and feats[-1]['name'] == e['name'] and e['name'] == 'Domain Spells':
                            feats[-1]['desc'] = text(e['entries'], ctx) + '\n' + feats[-1]['desc']
                        else:
                            feats.append(feature(e['name'], lvl, text(e['entries'], ctx)))
                    pending_str = None
            else:
                feats.append(feature(f['name'], lvl, text(f['entries'], ctx)))
        out[key] = feats
    return cls, base, out, srcs


if __name__ == '__main__':
    data = json.load(open(sys.argv[1]))
    dropdown = sys.argv[2].split('|')
    cls, base, subs, srcs = extract(data, dropdown)
    json.dump({'base': base, 'subclass': subs, 'subclassSources': srcs}, sys.stdout, ensure_ascii=False, indent=1)
