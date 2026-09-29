#!/usr/bin/env python3
"""race_convert.py – 5e.tools races.json → Block RACE_PICKS in der App (Paket C3, 29.09.2026, Anleitung REFERENZ B13)

Aufruf (aus dem Arbeitsordner, braucht src/races.json und src/spells-xphb.json, src/spells-phb.json):
    python3 willow/tools/race_convert.py DnD_Character_App.html src           # nur prüfen und anzeigen
    python3 willow/tools/race_convert.py DnD_Character_App.html src --write   # Block einsetzen/ersetzen (nur bei 0 Fehlern)

Quelle je Rasse wie in RACE_DATA (10× XPHB, Half-Elf/Half-Orc PHB). Alles strukturiert aus races.json:
- size (Liste; mehr als ein Eintrag = Wahl, Schlüssel race:size), speed, darkvision (dv), resist (res, feste Arten)
- Wahl-Traits (ch) aus _versions (Elf, Gnome, Tiefling, Goliath) bzw. _implementations (Dragonborn):
  Option {n, txt (Text der Version), dv/speed/res (nur wenn der Text sie nennt), sp {Stufe: [Zauber]}, dmg}
  ab = Zauberattribut-Wahl (additionalSpells.ability.choose), tbl = Tabelle aus dem Grund-Trait (Elven Lineages …)
- Skills (sk): skillProficiencies (fest / choose / any) mit dem Trait-Namen, der sie gibt (SKILL_TRAIT)
- Attributsboni (asi, nur PHB-2014-Rassen): ability
- Kuratiert und gegen den 5e.tools-Text geprüft: Vorteile auf Saves (ADV), Dwarven Toughness (HP)
- Paket C4 (Actions-Tab): tr = Tracker (TRACK: id rc_…, tag, uses, restore, minLvl, Icon; check_track prüft Aktionsart,
  PB/1×, Rast und Stufe am Text), Option-Feld inn = [{s, l, u}] (Zauber ohne Platz: u 1 = 1×/Long Rest, 'pb'),
  Option-Feld tag (Goliath-Boon: GIANT_TAG), spk = feste Zauber aus Traits ohne Wahl (Light Bearer, Otherworldly Presence)
Das Skript prüft, dass jeder Trait-Name auch im App-Text (RACE_DATA.traits) als Karte „• Name: …“ steht.
"""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from class_extract import clean, render  # {@…}-Tags und entries → Textzeilen (wie bei den Klassen)

RACES = {'Aasimar': 'XPHB', 'Dragonborn': 'XPHB', 'Dwarf': 'XPHB', 'Elf': 'XPHB', 'Gnome': 'XPHB', 'Goliath': 'XPHB',
         'Half-Elf': 'PHB', 'Half-Orc': 'PHB', 'Halfling': 'XPHB', 'Human': 'XPHB', 'Orc': 'XPHB', 'Tiefling': 'XPHB'}
SKILL_TRAIT = {'Elf': 'Keen Senses', 'Human': 'Skillful', 'Half-Elf': 'Skill Versatility', 'Half-Orc': 'Menacing'}
# Vorteile als Hinweis an den Saves: s = Save-Attribute, c = Zustand (Text muss „Advantage“ und den Zustand enthalten)
ADV = {'Dwarf': [{'t': 'Dwarven Resilience', 'c': 'Poisoned'}],
       'Elf': [{'t': 'Fey Ancestry', 'c': 'Charmed'}],
       'Half-Elf': [{'t': 'Fey Ancestry', 'c': 'Charmed'}],
       'Gnome': [{'t': 'Gnomish Cunning', 's': ['INT', 'WIS', 'CHA']}],
       'Halfling': [{'t': 'Brave', 'c': 'Frightened'}]}
HP = {'Dwarf': {'t': 'Dwarven Toughness', 'per': 1}}
# Tracker im Actions-Tab (Paket C4, 29.09.2026): (id, Trait, tag, uses, restore, minLvl, Icon) – Schema wie CLASS_DATA-Tracker (B2).
# ids mit Präfix rc_ sind heilig (Verbrauch in st.abUses). Jede Angabe wird gegen den 5e.tools-Text geprüft (check_track).
TRACK = {'Aasimar': [('rc_healinghands', 'Healing Hands', 'aktion', 1, 'long', None, '✋'),
                     ('rc_celestialrevelation', 'Celestial Revelation', 'bonus', 1, 'long', 3, '🌟')],
         'Dragonborn': [('rc_breathweapon', 'Breath Weapon', 'aktion', 'pb', 'long', None, '🐉'),
                        ('rc_draconicflight', 'Draconic Flight', 'bonus', 1, 'long', 5, '🕊️')],
         'Dwarf': [('rc_stonecunning', 'Stonecunning', 'bonus', 'pb', 'long', None, '⛰️')],
         'Goliath': [('rc_giantancestry', 'Giant Ancestry', 'passiv', 'pb', 'long', None, '🗿'),
                     ('rc_largeform', 'Large Form', 'bonus', 1, 'long', 5, '🏔️')],
         'Half-Orc': [('rc_relentlessendurance', 'Relentless Endurance', 'passiv', 1, 'long', None, '🩸')],
         'Orc': [('rc_adrenalinerush', 'Adrenaline Rush', 'bonus', 'pb', 'short', None, '💨'),
                 ('rc_relentlessendurance', 'Relentless Endurance', 'passiv', 1, 'long', None, '🩸')]}
# Giant Ancestry: Aktionsart je Boon (Option-Feld tag); übrige Boons wirken beim Treffer ohne eigene Aktion → Tracker-tag passiv
GIANT_TAG = {"Cloud's Jaunt": 'bonus', "Stone's Endurance": 'reaktion', "Storm's Thunder": 'reaktion'}
TAG_TXT = {'bonus': 'bonus action', 'reaktion': 'reaction', 'aktion': ('magic action', 'attack action')}


def check_track(race, t, tag, uses, restore, minlvl, tx):
    """tx = 5e.tools-Text des Traits (klein). Meldet Abweichungen als Fehler."""
    need = TAG_TXT.get(tag)
    if need and not any(x in tx for x in (need if isinstance(need, tuple) else (need,))): err(f'{race}: {t} – tag {tag} nicht im Text')
    if tag == 'passiv' and ('bonus action' in tx.split('•')[0] or 'as a reaction' in tx): err(f'{race}: {t} – passiv, Text nennt Aktion')
    if uses == 'pb' and 'number of times equal to your proficiency' not in tx: err(f'{race}: {t} – uses pb nicht im Text')
    if uses == 1 and not re.search(r"can't (?:use it|do so|use this feature) again until you finish a long rest", tx): err(f'{race}: {t} – 1×/Long Rest nicht im Text')
    if restore == 'short' and not re.search(r'finish a short (?:rest )?or long rest', tx): err(f'{race}: {t} – Short Rest nicht im Text')
    if restore == 'long' and uses == 'pb' and 'regain all expended uses when you finish a long rest' not in tx: err(f'{race}: {t} – Long Rest nicht im Text')
    if minlvl and not re.search(r'character level %d\b' % minlvl, tx): err(f'{race}: {t} – Stufe {minlvl} nicht im Text')
ABBR = {'str': 'STR', 'dex': 'DEX', 'con': 'CON', 'int': 'INT', 'wis': 'WIS', 'cha': 'CHA'}
SKILLS = ['Acrobatics', 'Animal Handling', 'Arcana', 'Athletics', 'Deception', 'History', 'Insight', 'Intimidation',
          'Investigation', 'Medicine', 'Nature', 'Perception', 'Performance', 'Persuasion', 'Religion', 'Sleight of Hand',
          'Stealth', 'Survival']
SKL = {s.lower(): s for s in SKILLS}
ERR = []


def err(m): ERR.append(m); print('  ✘', m)


def cap(s): return s[:1].upper() + s[1:]


def lines(entries): return render(entries, None, [])


def find_trait(r, name):
    for e in r['entries']:
        if isinstance(e, dict) and e.get('name') == name: return e
    return None


def app_race_data(html):
    js = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dump.js')
    out = '/tmp/_rd_race_convert.json' if not os.environ.get('RC_TMP') else os.environ['RC_TMP']
    subprocess.run(['node', js, html, 'RACE_DATA', out], check=True, capture_output=True)
    return json.load(open(out))


def spell_tags(txt):
    r = []
    for x in re.findall(r'\{@spell ([^}]*)\}', txt):
        n = clean('{@spell ' + x + '}')
        if n not in r: r.append(n)
    return r


def main():
    if len(sys.argv) < 3: print(__doc__); sys.exit(2)
    html, srcdir, write = sys.argv[1], sys.argv[2], '--write' in sys.argv
    data = json.load(open(os.path.join(srcdir, 'races.json')))['race']
    names = {}
    for f in ('spells-xphb.json', 'spells-phb.json'):
        for s in json.load(open(os.path.join(srcdir, f)))['spell']: names.setdefault(s['name'].lower(), s['name'])
    app = app_race_data(html)
    out = {}
    for race, src in RACES.items():
        r = next((x for x in data if x['name'] == race and x['source'] == src), None)
        if not r: err(f'{race} ({src}) fehlt in races.json'); continue
        at = app.get(race)
        if not at: err(f'{race} fehlt in RACE_DATA'); continue
        cards = set(re.findall(r'^• ([^:\n]{1,48}): ', at['traits'], re.M))
        def need(t):
            if t not in cards: err(f'{race}: Trait „{t}“ nicht als Karte im App-Text')
        e = {'src': src, 'size': r['size'], 'speed': r['speed'] if isinstance(r['speed'], int) else r['speed'].get('walk')}
        if r.get('darkvision'): e['dv'] = r['darkvision']
        fixres = [cap(x) for x in r.get('resist', []) if isinstance(x, str)]
        if fixres: e['res'] = fixres
        # Skills
        for sp in r.get('skillProficiencies', []):
            t = SKILL_TRAIT.get(race)
            if not t: err(f'{race}: skillProficiencies ohne Trait-Zuordnung'); continue
            need(t)
            if 'choose' in sp: e['sk'] = {'t': t, 'f': [SKL[x] for x in sp['choose']['from']], 'n': sp['choose'].get('count', 1)}
            elif 'any' in sp: e['sk'] = {'t': t, 'any': sp['any']}
            else: e['sk'] = {'t': t, 'fix': [SKL[x] for x in sp if sp[x] is True]}
        # Attributsboni (PHB 2014)
        for ab in r.get('ability', []):
            a = {'fix': {ABBR[k]: v for k, v in ab.items() if k in ABBR}}
            if 'choose' in ab:
                c = ab['choose']; a['ch'] = {'f': [ABBR[x] for x in c['from']], 'n': c.get('count', 1), 'v': c.get('amount', 1)}
            e['asi'] = a
        # Wahl-Traits
        ch = []
        vers = r.get('_versions', [])
        if vers and '_abstract' in vers[0]:  # Dragonborn
            ab = vers[0]['_abstract']; mods = ab['_mod']['entries']
            base = find_trait(r, 'Draconic Ancestry')
            tbl = [x for x in lines(base['entries']) if x]
            opts = []
            for im in vers[0]['_implementations']:
                v = im['_variables']
                opts.append({'n': v['color'], 'dmg': v['damageType'], 'res': [cap(x) for x in im.get('resist', [])]})
            lk = [m['replace'] for m in mods if m.get('mode') == 'replaceArr']
            for t in ['Draconic Ancestry'] + lk: need(t)
            # Tabelle nur mit Kopf „Draconic Ancestors:“ und Zeilen „• Farbe: Art“ (Grundtext steht schon in der App)
            tb = [x for x in tbl if x.endswith(':') or x.startswith('• ')]
            ch.append({'t': 'Draconic Ancestry', 'o': opts, 'lk': lk, 'tbl': '\n'.join(tb)})
            rows = {x['n']: x['dmg'] for x in opts}
            for x in tb:
                m = re.match(r'• (\w+): (\w+)$', x)
                if m and rows.get(m.group(1)) != m.group(2): err(f'Dragonborn: Tabelle {x} ≠ Implementierung')
        elif vers:
            groups = {}
            for v in vers:
                mod = v['_mod']['entries']; mod = mod if isinstance(mod, list) else [mod]
                rep = next(m for m in mod if m['replace'] not in ('Darkvision',))
                t = rep['replace']; it = rep['items']
                m = re.match(r'.+\((.+)\)$', it['name']); n = m.group(1) if m else it['name']
                txt = lines(it['entries'])
                o = {'n': n}
                if race == 'Goliath':  # Boon-Name aus der Liste (Cloud's Jaunt …)
                    lst = next(x for x in it['entries'] if isinstance(x, dict) and x.get('type') == 'list')
                    o['n'] = lst['items'][0]['name']; o['anc'] = n
                    o['txt'] = '\n'.join(lines(lst['items'][0]['entries']))
                else:
                    o['txt'] = '\n'.join(txt)
                full = ' '.join(txt)
                if v.get('darkvision'):
                    if re.search(r'Darkvision[^.]*%d feet' % v['darkvision'], full): o['dv'] = v['darkvision']
                    else: print(f'  ⚠ {race}/{n}: darkvision {v["darkvision"]} in 5e.tools, aber nicht im Text → nicht übernommen')
                if v.get('speed'):
                    if re.search(r'Speed[^.]*%d feet' % v['speed'], full): o['speed'] = v['speed']
                    else: print(f'  ⚠ {race}/{n}: speed {v["speed"]} nicht im Text → nicht übernommen')
                if v.get('resist'): o['res'] = [cap(x) for x in v['resist']]
                # Zauber: Stufe 1 = {@spell}-Tags im ersten Absatz; höhere Stufen aus additionalSpells.innate,
                # Stufe nur übernehmen, wenn der Text „character level N“ nennt (sonst ab Stufe 1)
                sp = {}
                first = next((x for x in it['entries'] if isinstance(x, str)), '')
                if race == 'Goliath': first = ''
                if spell_tags(first): sp['1'] = spell_tags(first)
                ab = None
                for a in v.get('additionalSpells', []):
                    if isinstance(a.get('ability'), dict) and 'choose' in a['ability']: ab = [ABBR[x] for x in a['ability']['choose']]
                    for lv, d in (a.get('innate') or {}).items():
                        for per, lst in d.get('daily', {}).items():
                            for s in lst:
                                nm = names.get(s.split('|')[0].lower())
                                if not nm: err(f'{race}/{n}: Zauber {s} nicht in spells-xphb/phb'); continue
                                L = lv if re.search(r'character level %s\b' % lv, full) else '1'
                                if L != lv: print(f'  ⚠ {race}/{n}: {nm} in 5e.tools ab Stufe {lv}, Text nennt keine Stufe → ab 1')
                                if nm not in sp.get(L, []): sp.setdefault(L, []).append(nm)
                                # Paket C4: Tracker je Zauber (1×/Long Rest laut Grund-Trait bzw. PB laut Versionstext)
                                if per == '1':
                                    bt = ' '.join(lines(find_trait(r, t)['entries'])).lower()
                                    if 'cast it once without a spell slot' not in bt or 'finish a long rest' not in bt: err(f'{race}/{n}: {nm} 1×/Long Rest nicht im Text')
                                    u = 1
                                elif per == 'pb':
                                    if 'number of times equal to your proficiency' not in full.lower(): err(f'{race}/{n}: {nm} PB-Nutzungen nicht im Text')
                                    u = 'pb'
                                else: err(f'{race}/{n}: daily {per} nicht unterstützt'); continue
                                o.setdefault('inn', []).append({'s': nm, 'l': int(L), 'u': u})
                if sp: o['sp'] = sp
                if race == 'Goliath':
                    tg = GIANT_TAG.get(o['n'], 'passiv'); o['tag'] = tg
                    check_track(race, o['n'], tg, None, None, None, o['txt'].lower())
                g = groups.setdefault(t, {'t': t, 'o': []})
                if ab: g['ab'] = ab
                g['o'].append(o)
            for t, g in groups.items():
                need(t)
                base = find_trait(r, t)
                tb = [x for x in lines(base['entries'])]
                i = next((k for k, x in enumerate(tb) if x.endswith(':') and ' | ' in (tb[k + 1] if k + 1 < len(tb) else '')), None)
                if i is not None: g['tbl'] = '\n'.join(tb[i:i + 2 + len(g['o'])])
                ch.append(g)
        if ch: e['ch'] = ch
        if len(r['size']) > 1: e['size'] = r['size']
        # Vorteile, HP
        for a in ADV.get(race, []):
            need(a['t'])
            tr = find_trait(r, a['t']); tx = ' '.join(lines(tr['entries'])).lower() if tr else ''
            if 'advantage' not in tx or (a.get('c') and a['c'].lower() not in tx): err(f'{race}: {a["t"]} – Vorteil nicht im 5e.tools-Text')
            for s in a.get('s', []):
                if {'INT': 'intelligence', 'WIS': 'wisdom', 'CHA': 'charisma'}[s] not in tx: err(f'{race}: {a["t"]} – {s} nicht im Text')
        if race in ADV: e['adv'] = ADV[race]
        if race in HP:
            h = HP[race]; need(h['t']); tr = find_trait(r, h['t'])
            if 'increases by 1' not in ' '.join(lines(tr['entries'])): err(f'{race}: {h["t"]} – Text geändert')
            e['hp'] = h
        # Paket C4: Tracker (Actions-Tab) und feste Zauber außerhalb der Wahl-Traits (Light Bearer, Otherworldly Presence)
        tr = []
        for (i, t, tag, uses, restore, ml, ic) in TRACK.get(race, []):
            need(t); ft = find_trait(r, t)
            if not ft: err(f'{race}: Trait {t} fehlt in races.json'); continue
            check_track(race, t, tag, uses, restore, ml, ' '.join(lines(ft['entries'])).lower())
            x = {'id': i, 't': t, 'tag': tag, 'uses': uses, 'restore': restore, 'ic': ic}
            if ml: x['minLvl'] = ml
            tr.append(x)
        if tr: e['tr'] = tr
        chn = {c['t'] for c in ch} | {x for c in ch for x in c.get('lk', [])}
        spk = []
        for tr_ in r['entries']:
            if not isinstance(tr_, dict) or not tr_.get('name') or tr_['name'] in chn: continue
            s_ = [names.get(x.lower(), x) for x in spell_tags(json.dumps(tr_['entries']))]
            if s_: need(tr_['name']); spk.append({'t': tr_['name'], 's': s_})
        if spk: e['spk'] = spk
        out[race] = e
        print(f'  {race:<11} size {"/".join(e["size"])}, speed {e["speed"]}, dv {e.get("dv", "–")}, res {e.get("res", "–")}'
              f'{", sk " + e["sk"]["t"] if "sk" in e else ""}{", asi" if "asi" in e else ""}'
              + ''.join(f', {c["t"]}: {"/".join(o["n"] for o in c["o"])}{" ab " + "/".join(c["ab"]) if c.get("ab") else ""}' for c in ch)
              + (', tr ' + '/'.join(x['id'] for x in e.get('tr', [])) if e.get('tr') else '')
              + ''.join(f', {x["t"]}: {"/".join(x["s"])}' for x in e.get('spk', []))
              + ''.join(f', inn {o["n"]}: ' + '/'.join(f'{z["s"]}@{z["l"]}×{z["u"]}' for z in o['inn']) for c in ch for o in c['o'] if o.get('inn')))
    print(f'Fehler: {len(ERR)}')
    if ERR or not write: sys.exit(1 if ERR else 0)
    s = open(html, encoding='utf-8').read()
    block = '// RACE_PICKS-START\nconst RACE_PICKS=' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n// RACE_PICKS-END'
    if '// RACE_PICKS-START' in s:
        a, b = s.index('// RACE_PICKS-START'), s.index('// RACE_PICKS-END') + len('// RACE_PICKS-END')
        s = s[:a] + block + s[b:]
    else:
        anchor = '\nconst CLASS_CORE_TRAITS = {'
        assert s.count(anchor) == 1
        s = s.replace(anchor, '\n' + block + '\n' + anchor, 1)
    open(html, 'w', encoding='utf-8').write(s)
    print('RACE_PICKS geschrieben:', len(block), 'Zeichen')


if __name__ == '__main__':
    main()
