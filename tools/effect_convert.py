#!/usr/bin/env python3
"""effect_convert.py — Schnellauswahl für „Effects & Conditions“ (Paket E Teil 2, 02.10.2026)

Aufruf (aus dem Ordner über dem Klon; braucht src/variantrules.json aus `setup.sh effekte`):
    python3 willow/tools/effect_convert.py DnD_Character_App.html src [--write]

Erzeugt den Block zwischen `// EFFECT_DATA-START` und `// EFFECT_DATA-END` (erstes Einfügen: direkt nach
`// COND_DATA-END`):
  const EFFECT_DATA=[{n, k, s|c, t, v, o?, d?}, …]   kuratierte häufige Buffs/Debuffs
     n = Name, k = 's' Zauber (Text aus ZB_SPELLS, Fassung s) | 'f' Klassen-Feature (Text aus CLASS_DATA[c]),
     t = 'b' Buff | 'd' Debuff, v = Wert-Hinweis (Kurzform aus dem Regeltext), o = Wert-Optionen,
     d = Dauer in Minuten (nur Features; Zauber nehmen `dauer` aus ZB_SPELLS)
  const EFFECT_RULES={Name: Text}                     Regeltexte ohne eigenen Datenblock (Heroic Inspiration, XPHB)
Keine Daten erfinden: jeder Wert-Hinweis braucht einen Beleg `chk`, der wörtlich im Regeltext der App steht;
fehlt er, bricht das Skript ab. Die Bardic-Inspiration-Würfel kommen aus CLASS_TABLES.Bard (Spalte `bardic`).
Zauber-/Feature-Texte werden NICHT kopiert, die App liest sie zur Laufzeit (ZB_SPELLS/CLASS_DATA).
Neue Einträge: Zeile in LISTE ergänzen (Name, Art, Buff/Debuff, Wert, Beleg), Skript laufen lassen.
"""
import json, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from class_extract import render, Ctx  # noqa: E402

TOOLS = os.path.dirname(os.path.abspath(__file__))

# (Name, Art, Klasse/None, Buff/Debuff, Wert-Hinweis, Beleg im Regeltext, Dauer in Minuten für Features)
LISTE = [
    # Buffs – Zauber
    ('Bless', 's', None, 'b', '+1d4 attacks & saves', 'adds 1d4 to the attack roll or save', None),
    ('Guidance', 's', None, 'b', '+1d4 checks (chosen skill)', 'adds 1d4 to any ability check using the chosen skill', None),
    ('Resistance', 's', None, 'b', '−1d4 damage (chosen type)', 'reduces the total damage taken by 1d4', None),
    ('Shield of Faith', 's', None, 'b', '+2 AC', '+2 bonus to AC', None),
    ('Haste', 's', None, 'b', '+2 AC · Speed ×2', '+2 bonus to Armor Class', None),
    ('Aid', 's', None, 'b', '+5 HP max', 'increase by 5', None),
    ('Heroism', 's', None, 'b', 'Temp HP each turn', 'Temporary Hit Points equal to your spellcasting ability modifier', None),
    ('Longstrider', 's', None, 'b', '+10 ft Speed', 'Speed increases by 10 feet', None),
    ('Barkskin', 's', None, 'b', 'AC at least 17', 'Armor Class of 17', None),
    ('Warding Bond', 's', None, 'b', '+1 AC & saves', '+1 bonus to AC and saving throws', None),
    ('Mage Armor', 's', None, 'b', 'AC 13 + DEX', 'base AC becomes 13 plus its Dexterity modifier', None),
    ('Pass without Trace', 's', None, 'b', '+10 Stealth', '+10 bonus to Dexterity (Stealth)', None),
    ('Enhance Ability', 's', None, 'b', 'Advantage (chosen ability)', 'Advantage on ability checks using the chosen ability', None),
    ('Beacon of Hope', 's', None, 'b', '', None, None),
    ('Protection from Evil and Good', 's', None, 'b', '', None, None),
    ('Death Ward', 's', None, 'b', '', None, None),
    ('Freedom of Movement', 's', None, 'b', '', None, None),
    ('Fly', 's', None, 'b', 'Fly Speed 60 ft', 'Fly Speed of 60 feet', None),
    ('Invisibility', 's', None, 'b', '', None, None),
    ('Greater Invisibility', 's', None, 'b', '', None, None),
    ('Darkvision', 's', None, 'b', 'Darkvision 150 ft', 'Darkvision with a range of 150 feet', None),
    ('Spider Climb', 's', None, 'b', '', None, None),
    ('Water Breathing', 's', None, 'b', '', None, None),
    ('Stoneskin', 's', None, 'b', 'Resistance B/P/S', 'Resistance to Bludgeoning, Piercing, and Slashing', None),
    ('Protection from Energy', 's', None, 'b', 'Resistance (chosen type)', 'Resistance to one damage type of your choice', None),
    ('Magic Weapon', 's', None, 'b', '+1 attack & damage', '+1 bonus to attack rolls and damage rolls', None),
    ('Elemental Weapon', 's', None, 'b', '+1 attack · +1d4 damage', 'deals an extra 1d4 damage', None),
    ('Crusader\'s Mantle', 's', None, 'b', '+1d4 Radiant on hit', 'extra 1d4 Radiant damage', None),
    ('Circle of Power', 's', None, 'b', '', None, None),
    ('Aura of Life', 's', None, 'b', '', None, None),
    ('Aura of Purity', 's', None, 'b', '', None, None),
    ('Heroes\' Feast', 's', None, 'b', '', None, None),
    ('Sanctuary', 's', None, 'b', '', None, None),
    ('Foresight', 's', None, 'b', '', None, None),
    ('Holy Aura', 's', None, 'b', '', None, None),
    ('Mind Blank', 's', None, 'b', '', None, None),
    # Buffs – eigene Zauber, die als Zustand wirken
    ('Shield', 's', None, 'b', '+5 AC', '+5 bonus to AC', None),
    ('Blur', 's', None, 'b', 'Attacks vs you: Disadvantage', 'Disadvantage on attack rolls against you', None),
    ('Divine Favor', 's', None, 'b', '+1d4 Radiant on hit', 'extra 1d4 Radiant damage', None),
    ('Armor of Agathys', 's', None, 'b', '5 Temp HP', 'You gain 5 Temporary Hit Points', None),
    # Buffs – Features anderer Charaktere
    ('Bardic Inspiration', 'f', 'Bard', 'b', '+1d6', 'add the number rolled to the d20', 60),
    ('Aura of Protection', 'f', 'Paladin', 'b', '+CHA mod to saves', 'bonus to saving throws equal to your Charisma modifier', None),
    ('Aura of Courage', 'f', 'Paladin', 'b', 'Immune to Frightened', 'Immunity to the Frightened condition', None),
    ('Emboldening Bond', 'f', 'Cleric', 'b', '+1d4 once per turn', 'roll a d4 and add the number rolled', 10),
    # Debuffs
    ('Bane', 's', None, 'd', '−1d4 attacks & saves', 'subtract 1d4 from the attack roll or save', None),
    ('Slow', 's', None, 'd', '−2 AC & DEX saves · Speed ½', '-2 penalty to AC and Dexterity saving throws', None),
    ('Faerie Fire', 's', None, 'd', 'Attacks vs you: Advantage', 'Attack rolls against an affected creature or object have Advantage', None),
    ('Hex', 's', None, 'd', 'Disadvantage (chosen ability checks)', 'Disadvantage on ability checks made with the chosen ability', None),
    ('Bestow Curse', 's', None, 'd', '', None, None),
    ('Ray of Enfeeblement', 's', None, 'd', '−1d8 damage rolls', 'subtracts 1d8 from all its damage rolls', None),
    ('Mind Sliver', 's', None, 'd', '−1d4 next save', 'subtract 1d4 from the next saving throw', None),
    ('Vicious Mockery', 's', None, 'd', 'Disadvantage next attack', 'Disadvantage on the next attack roll', None),
    ('Guiding Bolt', 's', None, 'd', 'Next attack vs you: Advantage', 'the next attack roll made against it before the end of your next turn has Advantage', None),
    ('Shining Smite', 's', None, 'd', 'Attacks vs you: Advantage', 'attack rolls against it have Advantage', None),
    ('Starry Wisp', 's', None, 'd', 'Can\'t be Invisible', 'can\'t benefit from the Invisible condition', None),
    ('Chill Touch', 's', None, 'd', 'Can\'t regain HP', 'can\'t regain Hit Points', None),
    ('Frostbite', 's', None, 'd', 'Disadvantage next weapon attack', 'disadvantage on the next weapon attack roll', None),
    ('Blindness/Deafness', 's', None, 'd', '', None, None),
    ('Hold Person', 's', None, 'd', '', None, None),
    ('Tasha\'s Hideous Laughter', 's', None, 'd', '', None, None),
    ('Contagion', 's', None, 'd', '', None, None),
    ('Polymorph', 's', None, 'd', '', None, None),
]
REGELN = (('Heroic Inspiration', 'XPHB'),)


def dump(html):
    out = 'effect_dump.json'
    subprocess.check_call(['node', os.path.join(TOOLS, 'dump.js'), html,
                           "{zb:ZB_SPELLS.map(s=>({name:s.name,src:s.src,desc:s.desc,dauer:s.dauer})),cd:CLASS_DATA,bard:CLASS_TABLES.Bard}",
                           out], stdout=subprocess.DEVNULL)
    d = json.load(open(out, encoding='utf-8'))
    os.remove(out)
    return d


def feature(cd, cls, name):
    c = cd.get(cls) or {}
    for f in c.get('base') or []:
        if f.get('name') == name:
            return f
    for feats in (c.get('subclass') or {}).values():
        for f in feats if isinstance(feats, list) else []:
            if f.get('name') == name:
                return f
    return None


def build(html, src_dir):
    d = dump(html)
    fehler, liste = [], []
    for n, k, c, t, v, chk, dur in LISTE:
        e = {'n': n, 'k': k, 't': t}
        if k == 's':
            vs = [s for s in d['zb'] if s['name'] == n]
            sp = next((s for s in vs if s['src'] == "PHB'24"), vs[0] if vs else None)
            if not sp:
                fehler.append(f'Zauber fehlt in ZB_SPELLS: {n}')
                continue
            e['s'] = sp['src']
            text = sp['desc']
        else:
            f = feature(d['cd'], c, n)
            if not f:
                fehler.append(f'Feature fehlt in CLASS_DATA.{c}: {n}')
                continue
            e['c'] = c
            text = f['desc']
            if dur:
                e['d'] = dur
        if v:
            if not chk or chk not in text:
                fehler.append(f'Beleg nicht im Text: {n} – {chk!r}')
                continue
            e['v'] = v
        if n == 'Bardic Inspiration':
            dice = []
            for r in d['bard']['rows']:
                x = r.get('bardic')
                if x and x not in dice:
                    dice.append(x)
            if not dice:
                fehler.append('CLASS_TABLES.Bard ohne Spalte bardic')
            e['o'] = ['+' + x for x in dice]
            e['v'] = e['o'][0]
        liste.append(e)
    vr = json.load(open(os.path.join(src_dir, 'variantrules.json'), encoding='utf-8'))
    ctx = Ctx({'classFeature': [], 'subclassFeature': []})
    regeln = {}
    for n, q in REGELN:
        r = next((x for x in vr['variantrule'] if x['name'] == n and x['source'] == q), None)
        if not r:
            fehler.append(f'Regel fehlt: {n} ({q})')
            continue
        regeln[n] = '\n'.join(x for x in render(r['entries'], ctx, []) if x.strip())
        if '{@' in regeln[n]:
            fehler.append(f'Tag nicht aufgelöst: {n}')
    return liste, regeln, fehler


def main():
    html, src = sys.argv[1], sys.argv[2]
    write = '--write' in sys.argv
    liste, regeln, fehler = build(html, src)
    for e in liste:
        print(f"  {e['t']} {e['k']} {e['n']}: {e.get('v', '')}{'  ' + str(e['o']) if 'o' in e else ''}")
    for n, t in regeln.items():
        print(f'  Regel {n}: {t[:80]!r}')
    if fehler:
        print('FEHLER:', *fehler, sep='\n  ')
        sys.exit(1)
    block = '// EFFECT_DATA-START (tools/effect_convert.py; Texte zur Laufzeit aus ZB_SPELLS/CLASS_DATA, Regeln aus 5e.tools variantrules.json)\n' + \
        'const EFFECT_DATA=' + json.dumps(liste, ensure_ascii=False, separators=(',', ':')) + ';\n' + \
        'const EFFECT_RULES=' + json.dumps(regeln, ensure_ascii=False, separators=(',', ':')) + ';\n// EFFECT_DATA-END\n'
    s = open(html, encoding='utf-8').read()
    m = re.search(r'// EFFECT_DATA-START.*?// EFFECT_DATA-END\n', s, re.S)
    if m:
        neu = s[:m.start()] + block + s[m.end():]
    else:
        k = s.count('// COND_DATA-END\n')
        if k != 1:
            sys.exit(f'Anker // COND_DATA-END {k}x gefunden')
        i = s.index('// COND_DATA-END\n') + len('// COND_DATA-END\n')
        neu = s[:i] + block + s[i:]
    print(f'{len(liste)} Einträge, {len(regeln)} Regeln, Block {len(block)} Bytes', '– unverändert' if neu == s else '')
    if write and neu != s:
        open(html, 'w', encoding='utf-8').write(neu)
        print('geschrieben')


if __name__ == '__main__':
    main()
