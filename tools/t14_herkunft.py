#!/usr/bin/env python3
"""t14_herkunft.py – Willow 2014 (Paket T4, 19.10.2026): Rassen, Backgrounds und Feats aus 5etools-2014-src → tools/t14/

Aufruf (aus dem Ordner über dem Klon; braucht src14/ = `bash willow/tools/setup.sh t14` und tools/t14/ZB_SPELLS.js aus T3):
    python3 willow/tools/t14_herkunft.py DnD_Character_App.html src14            # nur Bericht
    python3 willow/tools/t14_herkunft.py DnD_Character_App.html src14 --write    # tools/t14/<BLOCK>.js schreiben

Nur Einträge mit `srd` (SRD 5.1). Erzeugt je eine Zeile `const <BLOCK>=…;`:
- RACE_DATA  {Name: {src, speed, size, ability, traits}} – 9 Rassen, Grundrasse + SRD-Unterrasse zusammengeführt (T-E2:
             „Hill Dwarf“, „High Elf“, „Rock Gnome“, „Lightfoot Halfling“; Dragonborn, Half-Elf, Half-Orc, Human, Tiefling).
             traits = „• Name: Text“ je Trait (Grundrasse, dann Unterrasse; verschachtelte Abschnitte bleiben in der Karte).
- RACE_PICKS Schema wie race_convert.py (REFERENZ B13): size, speed, dv, res, sk, asi (Attributsboni 2014 = Weiche a),
             adv, hp, tr (Tracker, 2014-Text geprüft), ch (Dragonborn-Ahnen aus subrace._versions; Zauber-Traits aus
             additionalSpells: Tiefling „Infernal Legacy“ = eine Option ohne Wahl, High Elf „Cantrip“ = Wahl aus den
             Wizard-Cantrips von ZB_SPELLS 2014; `fab` = festes Zauberattribut), more (Nicht-Kampf-Traits → „Weitere“),
             pf (Paket AA3: Waffen-/Werkzeug-/Sprach-Proficiencies aus Grundrasse + Unterrasse, race_profs aus race_convert.py;
             Sprachwahl aus den PHB-Standardsprachen in src14/languages.json).
- BG_DATA / BG_EXTRA / BG_SPELLS  Acolyte (SRD; Text aus backgrounds.json, Beschreibung aus fluff-backgrounds.json) und
             „Custom Background“ unverändert aus der 2024-App (eigener Background, Plan T: „Acolyte + Custom“); keine
             Attributswahl, kein Origin Feat (Weiche b), BG_SPELLS {}.
- FT_FEATS / FEAT_SPELLS  Grappler (SRD, PHB-Text, `cat` leer = keine 2024-Kategorie, Weiche k), FEAT_SPELLS {}.
Die Prüfungen (Tracker-Text, Vorteile, Attributsboni, Trait-Karten) brechen bei Abweichung ab – nichts wird erfunden.
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from class_extract import render, clean, t14_setup, Ctx  # noqa: E402
from bg_convert import grab, bg_text, bg_data, tables_to_text  # noqa: E402
from feat_add import pre_text  # noqa: E402
from race_convert import race_profs, std_langs  # noqa: E402  (Paket AA3)

T14 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 't14')
ABBR = {'str': 'STR', 'dex': 'DEX', 'con': 'CON', 'int': 'INT', 'wis': 'WIS', 'cha': 'CHA'}
SKILLS = ['Acrobatics', 'Animal Handling', 'Arcana', 'Athletics', 'Deception', 'History', 'Insight', 'Intimidation',
          'Investigation', 'Medicine', 'Nature', 'Perception', 'Performance', 'Persuasion', 'Religion', 'Sleight of Hand',
          'Stealth', 'Survival']
SKL = {s.lower(): s for s in SKILLS}
SKILL_TRAIT = {'Elf': 'Keen Senses', 'Half-Elf': 'Skill Versatility', 'Half-Orc': 'Menacing'}
# Vorteile als Hinweis an den Saves (Schema B13); 2014-Text muss „advantage“ und w enthalten
ADV = {'Dwarf': [({'t': 'Dwarven Resilience', 'c': 'Poisoned'}, 'poison')],
       'Elf': [({'t': 'Fey Ancestry', 'c': 'Charmed'}, 'charmed')],
       'Half-Elf': [({'t': 'Fey Ancestry', 'c': 'Charmed'}, 'charmed')],
       'Gnome': [({'t': 'Gnome Cunning', 's': ['INT', 'WIS', 'CHA']}, 'intelligence, wisdom, and charisma saving throws')],
       'Halfling': [({'t': 'Brave', 'c': 'Frightened'}, 'frightened')]}
HP = {'Hill Dwarf': {'t': 'Dwarven Toughness', 'per': 1}}
# Tracker (ids wie 2024, heilig): (id, Trait, tag, uses, restore, Icon) – Prüfung am PHB-Text (check_track14)
TRACK = {'Dragonborn': [('rc_breathweapon', 'Breath Weapon', 'aktion', 1, 'short', '🐉')],
         'Half-Orc': [('rc_relentlessendurance', 'Relentless Endurance', 'passiv', 1, 'long', '🩸')]}
# Nicht-Kampf-Traits → Gruppe „Weitere“ im Actions-Tab (zusätzlich zu RC_MORE der App: Age, Size, Languages …)
MORE = {'Speed', 'Trance', 'Dwarven Combat Training', 'Tool Proficiency', 'Stonecunning', 'Elf Weapon Training',
        'Extra Language', "Artificer's Lore", 'Tinker'}
ERR = []


def err(m): ERR.append(m); print('  ✘', m)


def cap(s): return s[:1].upper() + s[1:]


def lines(entries): return render(entries, None, [])


def trait_text(entries):
    """„• Name: Text“ je benanntem Trait; Folgezeilen (Absätze, Tabellen, verschachtelte Abschnitte) gehören zur Karte."""
    out = []
    for e in entries:
        if not isinstance(e, dict) or not e.get('name'): err(f'Trait ohne Namen: {str(e)[:60]}'); continue
        L = [x for x in lines(tables_to_text(e['entries'])) if x.strip()]
        out.append(f'• {clean(e["name"])}: {L[0]}')
        out.extend(L[1:])
    return '\n'.join(out)


def check_track14(race, t, tag, uses, restore, tx):
    if tag == 'aktion' and 'use your action' not in tx: err(f'{race}: {t} – Aktion nicht im Text')
    if uses == 1 and restore == 'short' and "can't use it again until you complete a short or long rest" not in tx:
        err(f'{race}: {t} – 1×/Short Rest nicht im Text')
    if uses == 1 and restore == 'long' and not re.search(r"can't use (?:it|this feature) again until you finish a long rest", tx):
        err(f'{race}: {t} – 1×/Long Rest nicht im Text')


def find(entries, name):
    return next((e for e in entries if isinstance(e, dict) and e.get('name') == name), None)


def ordinal_lvl(tx, lv):
    return bool(re.search(r'\b%s(?:st|nd|rd|th) level' % lv, tx))


def races(src14, zb):
    d = json.load(open(os.path.join(src14, 'races.json'), encoding='utf-8'))
    wiz0 = sorted(z['name'] for z in zb if z['grad'] == 0 and 'Wizard' in z['classes'])
    names = {z['name'].lower(): z['name'] for z in zb}
    RD, RP = {}, {}
    for r in sorted((x for x in d['race'] if x.get('srd') and x['source'] == 'PHB'), key=lambda x: x['name']):
        subs = [s for s in d['subrace'] if s.get('srd') and s.get('raceName') == r['name'] and s.get('raceSource') == 'PHB']
        if len(subs) != 1: err(f'{r["name"]}: {len(subs)} SRD-Unterrassen'); continue
        sb = subs[0]
        name = f'{sb["name"]} {r["name"]}' if sb.get('name') else r['name']
        ents = list(r['entries']) + [e for e in sb.get('entries', []) if isinstance(e, dict)]
        traits = trait_text(ents)
        cards = set(re.findall(r'^• ([^:\n]{1,48}): ', traits, re.M))
        def need(t):
            if t not in cards: err(f'{name}: Trait „{t}“ nicht als Karte im Text')
        txt = lambda t: ' '.join(lines(find(ents, t)['entries'])).lower() if find(ents, t) else ''
        speed = sb.get('speed', r['speed']); speed = speed if isinstance(speed, int) else speed.get('walk')
        e = {'src': 'PHB', 'size': r['size'], 'speed': speed}
        if r.get('darkvision') or sb.get('darkvision'): e['dv'] = sb.get('darkvision') or r['darkvision']
        res = [cap(x) for x in r.get('resist', []) + sb.get('resist', []) if isinstance(x, str)]
        if res: e['res'] = res
        # Skills
        for sp in r.get('skillProficiencies', []) + sb.get('skillProficiencies', []):
            t = SKILL_TRAIT.get(r['name'])
            if not t: err(f'{name}: skillProficiencies ohne Trait'); continue
            need(t)
            if 'choose' in sp: e['sk'] = {'t': t, 'f': [SKL[x] for x in sp['choose']['from']], 'n': sp['choose'].get('count', 1)}
            elif 'any' in sp: e['sk'] = {'t': t, 'any': sp['any']}
            else: e['sk'] = {'t': t, 'fix': [SKL[x] for x in sp if sp[x] is True]}
        # Attributsboni (Weiche a): Grundrasse + Unterrasse
        fix, ch_ = {}, None
        for ab in r.get('ability', []) + sb.get('ability', []):
            for k, v in ab.items():
                if k in ABBR: fix[ABBR[k]] = fix.get(ABBR[k], 0) + v
            if 'choose' in ab:
                c = ab['choose']; ch_ = {'f': [ABBR[x] for x in c['from']], 'n': c.get('count', 1), 'v': c.get('amount', 1)}
        if not fix and not ch_: err(f'{name}: keine Attributsboni')
        fix = dict(sorted(fix.items(), key=lambda x: (-x[1], list(ABBR.values()).index(x[0]))))   # +2 vor +1
        asi = {'fix': fix}
        if ch_: asi['ch'] = ch_
        e['asi'] = asi
        ability = ', '.join(f'+{v} {k}' for k, v in sorted(fix.items(), key=lambda x: (-x[1], list(ABBR.values()).index(x[0]))))
        if len(fix) == 6 and set(fix.values()) == {1}: ability = '+1 to all'
        if ch_: ability += f', +{ch_["v"]} to {ch_["n"]} others'
        # Wahl-Traits
        ch = []
        for v in sb.get('_versions', []):   # Dragonborn: Ahnen aus der (namenlosen) SRD-Unterrasse
            mods = v['_abstract']['_mod']['entries']
            lk = [m['replace'] for m in mods if m.get('mode') == 'replaceArr']
            opts = [{'n': im['_variables']['color'], 'dmg': cap(im['_variables']['damageType']),
                     'res': [cap(x) for x in im.get('resist', [])]} for im in v['_implementations']]
            for t in ['Draconic Ancestry'] + lk: need(t)
            rows = {m.group(1): m.group(2) for m in re.finditer(r'^• (\w+) \| (\w+) \|', traits, re.M)}
            for o in opts:
                if rows.get(o['n']) != o['dmg']: err(f'{name}: Tabelle {o["n"]} {rows.get(o["n"])} ≠ {o["dmg"]}')
            ch.append({'t': 'Draconic Ancestry', 'o': opts, 'lk': lk})
        for a in r.get('additionalSpells', []) + sb.get('additionalSpells', []):
            fab = ABBR[a['ability']] if isinstance(a.get('ability'), str) else None
            if not fab: err(f'{name}: additionalSpells ohne festes Attribut'); continue
            known = a.get('known', {})
            if '1' in known and isinstance(known['1'], dict):   # High Elf: Cantrip nach Wahl
                ch_x = known['1']['_'][0]['choose']
                if ch_x != 'level=0|class=Wizard': err(f'{name}: Wahl {ch_x} nicht unterstützt'); continue
                t = next(x['name'] for x in ents if isinstance(x, dict) and 'cantrip of your choice from the wizard' in ' '.join(lines(x['entries'])).lower())
                need(t)
                ch.append({'t': t, 'o': [{'n': s, 'sp': {'1': [s]}} for s in wiz0], 'fab': fab})
                continue
            sp, inn = {}, []
            for lv, L in known.items():
                for s in L: sp.setdefault(lv, []).append(names[s.split('#')[0].lower()])
            for lv, dd in (a.get('innate') or {}).items():
                for per, L in dd.get('daily', {}).items():
                    if per != '1': err(f'{name}: daily {per} nicht unterstützt'); continue
                    for s in L:
                        nm = names.get(s.split('#')[0].lower())
                        if not nm: err(f'{name}: Zauber {s} nicht in ZB_SPELLS 2014'); continue
                        sp.setdefault(lv, []).append(nm); inn.append({'s': nm, 'l': int(lv), 'u': 1})
            allsp = [x for v in sp.values() for x in v]
            t = next((x['name'] for x in ents if isinstance(x, dict) and all(s.lower() in ' '.join(lines(x['entries'])).lower() for s in allsp)), None)
            if not t: err(f'{name}: Trait zu {allsp} nicht gefunden'); continue
            need(t); tx = txt(t)
            for z in inn:
                if not ordinal_lvl(tx, z['l']): err(f'{name}: {z["s"]} ab Stufe {z["l"]} nicht im Text')
            if inn and 'finish a long rest' not in tx: err(f'{name}: Long Rest nicht im Text')
            if {'cha': 'charisma', 'int': 'intelligence', 'wis': 'wisdom'}[a['ability']] not in tx: err(f'{name}: Attribut nicht im Text')
            o = {'n': t, 'sp': dict(sorted(sp.items(), key=lambda x: int(x[0])))}
            if inn: o['inn'] = inn
            ch.append({'t': t, 'o': [o], 'fab': fab})
        if ch: e['ch'] = ch
        # Vorteile, HP
        adv = []
        for a, w in ADV.get(r['name'], []):
            need(a['t']); tx = txt(a['t'])
            if 'advantage' not in tx or w not in tx: err(f'{name}: {a["t"]} – Vorteil nicht im Text')
            adv.append(a)
        if adv: e['adv'] = adv
        if name in HP:
            h = HP[name]; need(h['t'])
            if 'increases by 1' not in txt(h['t']): err(f'{name}: {h["t"]} – Text geändert')
            e['hp'] = h
        tr = []
        for (i, t, tag, uses, restore, ic) in TRACK.get(r['name'], []):
            need(t); check_track14(name, t, tag, uses, restore, txt(t))
            tr.append({'id': i, 't': t, 'tag': tag, 'uses': uses, 'restore': restore, 'ic': ic})
        if tr: e['tr'] = tr
        # Paket AA3: Waffen-/Werkzeug-/Sprach-Proficiencies (Grundrasse + Unterrasse)
        tt = {x['name']: ' '.join(lines(x['entries'])).lower() for x in ents if isinstance(x, dict) and x.get('name')}
        pf = race_profs(name, [r, sb], tt, std_langs(src14, 'PHB'), err)
        for x in pf: need(x['t'])
        if pf: e['pf'] = pf
        more = sorted(cards & MORE)
        if more: e['more'] = more
        RP[name] = e
        RD[name] = {'src': 'PHB', 'speed': speed, 'size': '/'.join(r['size']), 'ability': ability, 'traits': traits}
        print(f'  {name:<18} {ability:<26} speed {speed}, dv {e.get("dv", "–")}, res {e.get("res", "–")}'
              f'{", sk " + e["sk"]["t"] if "sk" in e else ""}'
              + ''.join(f', {c["t"]}: {len(c["o"])} Opt.' + (f' ({c["fab"]})' if c.get('fab') else '') for c in ch)
              + (', tr ' + '/'.join(x['id'] for x in tr) if tr else '') + (', more ' + '/'.join(more) if more else '')
              + ''.join(f', pf {x["k"]} {x["t"]}: ' + ('/'.join(x['fix']) if 'fix' in x else f'{x["n"]} aus {"/".join(x["f"])}') for x in pf))
    return dict(sorted(RD.items())), dict(sorted(RP.items()))


def backgrounds(html, src14):
    s = open(html, encoding='utf-8').read()
    a, z = grab(s, 'BG_DATA'); bgd = json.loads(s[a:z])
    a, z = grab(s, 'BG_EXTRA'); ex = json.loads(s[a:z])
    bgs = json.load(open(os.path.join(src14, 'backgrounds.json'), encoding='utf-8'))['background']
    fl = {(f['name'], f['source']): f for f in json.load(open(os.path.join(src14, 'fluff-backgrounds.json'), encoding='utf-8'))['backgroundFluff']}
    D, X = [], []
    for b in sorted((x for x in bgs if x.get('srd')), key=lambda x: x['name']):
        d = bg_data(b, {})
        if d['f'] or d['a']: err(f'{b["name"]}: Origin Feat/Attributswahl in 2014?')
        D.append(d)
        f = fl.get((b['name'], b['source']))
        X.append({'n': b['name'], 's': b['source'], 'f': bg_text(b), 'l': '\n'.join(render(f.get('entries', []), None, [])) if f else ''})
    cd = [x for x in bgd if x['n'] == 'Custom Background']
    ce = [x for x in ex if x['n'] == 'Custom Background']
    if len(cd) != 1 or len(ce) != 1: err('Custom Background fehlt in der 2024-App')
    D += cd; X += ce
    for d in D: print(f'  BG {d["n"]} ({d["src"]}): Skills {d["s"]}, Tools {d["t"] or "–"}')
    return D, X


def feats(src14):
    fs = json.load(open(os.path.join(src14, 'feats.json'), encoding='utf-8'))['feat']
    ctx = Ctx({'classFeature': [], 'subclassFeature': []}, feats=fs)
    out = []
    for f in sorted((x for x in fs if x.get('srd')), key=lambda x: x['name']):
        d = '\n'.join(x for x in render(tables_to_text(f['entries']), ctx, []) if x.strip())
        e = {'n': f['name'], 'src': f['source'], 'cat': '', 'pre': pre_text(f.get('prerequisite')), 'd': d}
        if f.get('ability'): e['ab'] = f['ability']
        if f.get('repeatable'): e['rep'] = 1
        if f.get('additionalSpells'): err(f'{f["name"]}: Feat-Zauber – FEAT_SPELLS 2014 erweitern')
        out.append(e)
        print(f'  Feat {e["n"]} ({e["src"]}), Voraussetzung {e["pre"] or "–"}')
    return out


def main():
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    if len(a) < 2: print(__doc__); sys.exit(2)
    html, src14 = a
    t14_setup(src14)
    zbl = open(os.path.join(T14, 'ZB_SPELLS.js'), encoding='utf-8').read().strip()
    zb = json.loads(zbl[len('const ZB_SPELLS='):-1])
    print('Rassen (SRD):')
    RD, RP = races(src14, zb)
    print('Backgrounds:')
    BD, BX = backgrounds(html, src14)
    print('Feats:')
    FT = feats(src14)
    print(f'Fehler: {len(ERR)}')
    if ERR: sys.exit(1)
    blocks = {'RACE_DATA': RD, 'RACE_PICKS': RP, 'BG_DATA': BD, 'BG_EXTRA': BX, 'BG_SPELLS': {}, 'FT_FEATS': FT, 'FEAT_SPELLS': {}}
    for k, v in blocks.items():
        line = f'const {k}=' + json.dumps(v, ensure_ascii=False, separators=(',', ':')) + ';\n'
        p = os.path.join(T14, k + '.js')
        alt = open(p, encoding='utf-8').read() if os.path.exists(p) else None
        print(f'  {k}: {len(line) // 1024} KB', '(unverändert)' if alt == line else '')
        if '--write' in sys.argv and alt != line: open(p, 'w', encoding='utf-8').write(line)
    if '--write' not in sys.argv: print('(nur Bericht, --write schreibt tools/t14/)')


if __name__ == '__main__':
    main()
