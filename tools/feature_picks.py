#!/usr/bin/env python3
"""feature_picks.py – erzeugt FEATURE_PICKS (Paket C2, 29.09.2026): Feature-Auswahl, Bonus-Skills, Expertise, Saves.

Aufruf:  python3 feature_picks.py DnD_Character_App.html src [--write]
  src/ enthält class-<k>.json aller 13 Klassen (5e.tools, setup.sh klassen).
  Ohne --write: nur Bericht. Mit --write: Zeile zwischen '// FEATURE_PICKS-START' und
  '// FEATURE_PICKS-END' in der HTML ersetzen.

Die Liste SPEC unten ist kuratiert (Anleitung REFERENZ B7/B12): nur einmalige oder wechselbare Wahl,
nichts, was pro Einsatz gewählt wird (Rage of the Wilds, Third Eye, Blade Flourish …).
Schlüssel 'Klasse|Gruppe|Feature' (Gruppe = 'base' oder Subklassen-Key wie in CLASS_DATA),
bei gleichnamigen Features derselben Gruppe mit '@Stufe' (Rogue Expertise@1/@6).
Optionsnamen werden aus dem desc der App gelesen ('• Name: …', 'Name. …', 'Name:'-Überschrift), außer 'o' ist
angegeben. Geprüft wird: Feature vorhanden, jede Option im App-Text und im 5e.tools-Text des Features.

Typen (Feld t):
  opt   Wahl zwischen Optionen: n (Anzahl, Standard 1), sw (wechselbar, Anzeige-Text), lk (verknüpfte Features
        derselben Gruppe, zeigen die Wahl mit), fx {Option: {b:[Skills], a:'WIS', m:1}} = Bonus Attributsmod. (min m)
        auf Skills bzw. {p:{n:2, f:[Skills]}} = zusätzliche Skill-Wahl bei dieser Option, nt = Optionen ohne eigenen Text
  skill Bonus-Skills: fix (fest), n + f (Wahl; 'cls' = Klassen-Skill-Liste L1, 'any' = alle 18), e = zusätzlich Expertise
  exp   Expertise: n aus geübten Skills (f schränkt ein)
  save  Saving-Throw-Übung: fix (Attribut-Kürzel)
  half  Jack of All Trades: halber Übungsbonus (abgerundet) auf nicht geübte Skills
Erzeugt je Eintrag zusätzlich l (Stufe des Features).
"""
import json, re, sys, os, subprocess, tempfile

HTML, SRC = sys.argv[1], sys.argv[2]
WRITE = '--write' in sys.argv
HERE = os.path.dirname(os.path.abspath(__file__))

SPEC = {
    # ── Wahl zwischen Optionen ──
    'Druid|base|Primal Order': {'t': 'opt', 'fx': {'Magician': {'b': ['Arcana', 'Nature'], 'a': 'WIS', 'm': 1}}},
    'Druid|base|Elemental Fury': {'t': 'opt'},
    'Cleric|base|Divine Order': {'t': 'opt', 'fx': {'Thaumaturge': {'b': ['Arcana', 'Religion'], 'a': 'WIS', 'm': 1}}},
    'Cleric|base|Blessed Strikes': {'t': 'opt'},
    'Druid|Circle of the Land|Circle of the Land Spells': {'t': 'opt', 'o': ['Arid Land', 'Polar Land', 'Temperate Land', 'Tropical Land'],
                                                           'sw': 'Long Rest', 'lk': ["Nature's Ward"]},
    'Barbarian|Path of the Totem Warrior|Totem Spirit': {'t': 'opt'},
    'Barbarian|Path of the Totem Warrior|Aspect of the Beast': {'t': 'opt',
        'fx': {'Tiger': {'p': {'n': 2, 'f': ['Athletics', 'Acrobatics', 'Stealth', 'Survival']}}}},
    'Barbarian|Path of the Totem Warrior|Totemic Attunement': {'t': 'opt'},
    'Barbarian|Path of the Wild Heart|Aspect of the Wilds': {'t': 'opt', 'sw': 'Long Rest'},
    'Barbarian|Path of the Storm Herald|Storm Aura': {'t': 'opt', 'sw': 'Level up', 'lk': ['Storm Soul', 'Raging Storm']},
    "Ranger|Hunter|Hunter's Prey": {'t': 'opt', 'sw': 'Short or Long Rest'},
    'Ranger|Hunter|Defensive Tactics': {'t': 'opt', 'sw': 'Short or Long Rest'},
    'Sorcerer|Draconic Bloodline|Dragon Ancestor': {'t': 'opt', 'lk': ['Elemental Affinity']},
    'Sorcerer|Draconic Sorcery|Elemental Affinity': {'t': 'opt', 'o': ['Acid', 'Cold', 'Fire', 'Lightning', 'Poison'], 'nt': 1},
    'Sorcerer|Divine Soul|Divine Magic': {'t': 'opt'},
    # Paket U (05.10.2026): Cantrip-Wahl (5e.tools additionalSpells innate, zwei Alternativen) → ALWAYS_PREP koppelt daran
    'Barbarian|Path of the Giant|Giant Power': {'t': 'opt', 'o': ['Druidcraft', 'Thaumaturgy'], 'nt': 1},
    'Bard|College of Swords|Fighting Style': {'t': 'opt'},
    # Artificer (Paket M): „You can change the armor's model whenever you finish a Short or Long Rest"
    'Artificer|Armorer|Armor Model': {'t': 'opt', 'o': ['Dreadnaught', 'Guardian', 'Infiltrator'], 'sw': 'Short or Long Rest', 'lk': ['Perfected Armor']},
    # Genie-Art: Tabelle „Genie Kind“ (5e.tools, Einleitung der Subklasse) steht nicht im App-Text → nt
    'Warlock|The Genie|Expanded Spell List': {'t': 'opt', 'o': ['Dao', 'Djinni', 'Efreeti', 'Marid'], 'nt': 1,
                                              'lk': ["Genie's Vessel", 'Elemental Gift']},
    # ── Bonus-Skills ──
    'Barbarian|base|Primal Knowledge': {'t': 'skill', 'n': 1, 'f': 'cls'},
    'Bard|College of Lore|Bonus Proficiencies': {'t': 'skill', 'n': 3, 'f': 'any'},
    'Cleric|Knowledge Domain|Blessings of Knowledge': {'t': 'skill', 'n': 2, 'f': ['Arcana', 'History', 'Nature', 'Religion'], 'e': 1},
    'Cleric|Nature Domain|Acolyte of Nature': {'t': 'skill', 'n': 1, 'f': ['Animal Handling', 'Nature', 'Survival']},
    'Cleric|Arcana Domain|Student of Arcana': {'t': 'skill', 'n': 1, 'f': ['Arcana', '@cls']},
    'Cleric|Order Domain|Bonus Proficiencies': {'t': 'skill', 'n': 1, 'f': ['Intimidation', 'Persuasion']},
    'Cleric|Peace Domain|Implement of Peace': {'t': 'skill', 'n': 1, 'f': ['Insight', 'Performance', 'Persuasion']},
    'Fighter|Battle Master|Student of War': {'t': 'skill', 'n': 1, 'f': 'cls'},
    'Fighter|Arcane Archer|Arcane Archer Lore': {'t': 'skill', 'fix': ['Arcana', 'Nature']},
    'Fighter|Cavalier|Bonus Proficiency': {'t': 'skill', 'n': 1, 'f': ['Animal Handling', 'History', 'Insight', 'Performance', 'Persuasion']},
    'Fighter|Samurai|Bonus Proficiency': {'t': 'skill', 'n': 1, 'f': ['History', 'Insight', 'Performance', 'Persuasion']},
    'Fighter|Banneret|Knightly Envoy': {'t': 'skill', 'n': 1, 'f': ['Insight', 'Intimidation', 'Persuasion', 'Performance']},
    'Monk|Warrior of Mercy|Implements of Mercy': {'t': 'skill', 'fix': ['Insight', 'Medicine']},
    'Monk|Way of Mercy|Implements of Mercy': {'t': 'skill', 'fix': ['Insight', 'Medicine']},
    'Monk|Way of the Drunken Master|Bonus Proficiencies': {'t': 'skill', 'fix': ['Performance']},
    'Ranger|Fey Wanderer|Otherworldly Glamour': {'t': 'skill', 'n': 1, 'f': ['Deception', 'Performance', 'Persuasion']},
    'Rogue|Scout|Survivalist': {'t': 'skill', 'fix': ['Nature', 'Survival'], 'e': 1},
    'Wizard|School of Enchantment|Enchanting Conversationalist': {'t': 'skill', 'n': 1, 'f': ['Deception', 'Intimidation', 'Persuasion']},
    'Wizard|Bladesinging|Training in War and Song': {'t': 'skill', 'n': 1, 'f': ['Acrobatics', 'Athletics', 'Performance', 'Persuasion']},
    # ── Expertise ──
    'Rogue|base|Expertise@1': {'t': 'exp', 'n': 2},
    'Rogue|base|Expertise@6': {'t': 'exp', 'n': 2},
    'Bard|base|Expertise@2': {'t': 'exp', 'n': 2},
    'Bard|base|Expertise@9': {'t': 'exp', 'n': 2},
    'Ranger|base|Deft Explorer': {'t': 'exp', 'n': 1},
    'Ranger|base|Expertise': {'t': 'exp', 'n': 2},
    'Wizard|base|Scholar': {'t': 'exp', 'n': 1, 'f': ['Arcana', 'History', 'Investigation', 'Medicine', 'Nature', 'Religion']},
    'Bard|base|Jack of All Trades': {'t': 'half'},
    # ── Saving Throws ──
    'Cleric|Knowledge Domain|Unfettered Mind': {'t': 'save', 'fix': ['INT']},
    'Fighter|Samurai|Elegant Courtier': {'t': 'save', 'fix': ['WIS']},
    'Monk|base|Disciplined Survivor': {'t': 'save', 'fix': ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']},
    'Ranger|Gloom Stalker|Iron Mind': {'t': 'save', 'fix': ['WIS']},
    'Rogue|base|Slippery Mind': {'t': 'save', 'fix': ['WIS', 'CHA']},
}
SKILLS = ['Acrobatics', 'Animal Handling', 'Arcana', 'Athletics', 'Deception', 'History', 'Insight', 'Intimidation',
          'Investigation', 'Medicine', 'Nature', 'Perception', 'Performance', 'Persuasion', 'Religion',
          'Sleight of Hand', 'Stealth', 'Survival']
SMALL = set('of the a an and or to in on with for from at by vs vs. into upon per as your its without over under'.split())


def is_name(n):  # wie fdIsName in der App
    core = re.sub(r'\([^)]*\)', ' ', n).strip()
    if not core or len(core) > 48 or re.search(r'[,;!?]', core): return False
    w = core.split()
    if len(w) > 7 or not re.match(r'^[A-Z0-9"“\'‘]', w[0]): return False
    return all(re.match(r'^[A-Z0-9"“\'‘(]', x) or (i > 0 and x in SMALL) for i, x in enumerate(w))


NAMED = re.compile(r'^((?:[^.:()]|\([^)]*\)){1,60}?)([.:]) (\S.*)$')


def parse_opts(desc):
    r = []
    for l in desc.split('\n'):
        l = l.strip()
        if l.startswith('• '): l = l[2:]
        m = NAMED.match(l)
        if m and is_name(m.group(1)) and m.group(1) not in r: r.append(m.group(1))
    return r


def opt_text(desc, o):  # wie fpOptText in der App
    L = desc.split('\n')
    rx = re.compile('^(?:• )?' + re.escape(o) + r'(?:[.:] |:$)')
    for i, l in enumerate(L):
        l = l.strip()
        if rx.match(l): return l
    w = o.split(' ')[0]
    return opt_text(desc, w) if w != o else ''


# App-Daten
tmp = os.path.join(tempfile.mkdtemp(), 'fp.json')
subprocess.check_call(['node', os.path.join(HERE, 'dump.js'), HTML, '{cd:CLASS_DATA,core:CLASS_CORE_TRAITS}', tmp], stdout=subprocess.DEVNULL)
D = json.load(open(tmp)); CD = D['cd']; CORE = D['core']

out, err, warn = {}, 0, 0
for key, e in SPEC.items():
    e = dict(e)
    base, _, at = key.partition('@')
    cls, grp, name = base.split('|')
    fs = CD[cls]['base'] if grp == 'base' else (CD[cls]['subclass'] or {}).get(grp)
    if fs is None: print('FEHLT Gruppe', key); err += 1; continue
    hits = [f for f in fs if f['name'] == name and (not at or f['lvl'] == int(at))]
    if len(hits) != 1: print(f'FEHLT/mehrdeutig ({len(hits)}x):', key); err += 1; continue
    f = hits[0]; e['l'] = f['lvl']
    # 5e.tools-Text aller gleichnamigen Features der Klasse
    j = json.load(open(os.path.join(SRC, f'class-{cls.lower()}.json')))
    src_txt = ' '.join(json.dumps(x) for x in j.get('classFeature', []) + j.get('subclassFeature', []) if x.get('name') == name)
    if e['t'] == 'opt':
        if 'o' not in e: e['o'] = parse_opts(f['desc'])
        if len(e['o']) < 2: print('zu wenige Optionen:', key, e['o']); err += 1
        for o in e['o']:
            if not e.get('nt') and not opt_text(f['desc'], o): print(f'  Option ohne Text in der App: {key} → {o}'); err += 1
            if o.lower() not in src_txt.lower() and o.split(' ')[0].lower() not in src_txt.lower():
                # Genie: Arten stehen im Einleitungs-Feature der Subklasse
                sub_txt = json.dumps(j.get('subclassFeature', []))
                if o.lower() in sub_txt.lower(): print(f'  (Option {o} nur in anderem Subklassen-Feature: {key})'); warn += 1
                else: print(f'  Option nicht in 5e.tools: {key} → {o}'); err += 1
        for l in e.get('lk', []):
            if not any(x['name'] == l for x in fs): print('  verknüpftes Feature fehlt:', key, l); err += 1
        for o, fx in e.get('fx', {}).items():
            if o not in e['o']: print('  fx-Option fehlt:', key, o); err += 1
    if e['t'] in ('skill',) or (e['t'] == 'exp' and 'f' in e):
        lst = e.get('fix', []) + ([] if isinstance(e.get('f'), str) else [x for x in e.get('f', []) if not x.startswith('@')])
        for s in lst:
            if s not in SKILLS: print('  kein Skill:', key, s); err += 1
            if s.lower() not in src_txt.lower(): print(f'  Skill nicht im 5e.tools-Text: {key} → {s}'); warn += 1
    out[key] = e
    print(f"{key:62s} L{e['l']:<2} {e['t']:5s} {e.get('o') or e.get('fix') or e.get('f') or ''}")

print(f'\n{len(out)} Einträge, Fehler {err}, Hinweise {warn}')
if WRITE:
    if err: sys.exit('Nicht geschrieben (Fehler).')
    s = open(HTML, encoding='utf-8').read()
    a, b = '// FEATURE_PICKS-START\n', '\n// FEATURE_PICKS-END'
    assert s.count(a) == 1 and s.count(b) == 1, 'Anker fehlen'
    i, k = s.index(a) + len(a), s.index(b)
    s = s[:i] + 'const FEATURE_PICKS=' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';' + s[k:]
    open(HTML, 'w', encoding='utf-8').write(s)
    print('FEATURE_PICKS geschrieben.')
