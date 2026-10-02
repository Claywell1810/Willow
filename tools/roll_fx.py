#!/usr/bin/env python3
"""roll_fx.py — Würfel-Regeln für Zustände und Effekte (Paket E Teil 3, 02.10.2026; REFERENZ B19)

Aufruf (aus dem Ordner über dem Klon; braucht nur die App):
    python3 willow/tools/roll_fx.py DnD_Character_App.html [--write]

Erzeugt den Block zwischen `// ROLL_FX-START` und `// ROLL_FX-END` (erstes Einfügen: direkt nach `// EFFECT_DATA-END`):
  const ROLL_FX={cond:{Name:[Regel,…]}, fx:{Name:[Regel,…]}}
  Regel = {w, m, ab?, sk?, on?, once?, note?} oder {c}
    w  = Würfe (mit Leerzeichen): d20 (Angriff, Rettungswurf, Attributswurf) | atk | watk (nur Waffen) | save | check
         (auch Initiative, XPHB: Initiative = Dexterity check) | init | dmg | wdmg (nur Waffen) | ac | spd
    m  = '+1d4', '-2' … | 'v' (Zahl/Würfel aus dem Wert des Effekts, Rückfall d) | 'adv' | 'dis' | 'fail' | 'ex' (−2 × Exhaustion)
         | ac: 'min17' (AC mindestens 17), 'base13' (Grund-AC 13 + DEX ohne Rüstung) | spd: 'x2', 'half'
    ab = nur diese Attribute (Liste) oder '*' = vom Wirker gewählt (an, wenn Note/From das Attribut nennt)
    sk = nur dieser Skill oder '*' = gewählter Skill (an, wenn Note/From den Skill nennt)
    on = 0: nur angeboten (Chip aus), z. B. Bedingung im Text („while the source of fear is within line of sight“)
    once = 1: Einmal-Effekt (Knopf „used – remove“ im Würfel-Dialog)
    c  = Zustand mit eigenen Regeln (Paralyzed → Incapacitated; Hold Person → Paralyzed)
Keine Daten erfinden: jede Regel braucht einen Beleg, der wörtlich im Regeltext der App steht (COND_DATA, ZB_SPELLS
in der Fassung aus EFFECT_DATA, CLASS_DATA); fehlt er, bricht das Skript ab. Neue Einträge: Zeile in COND/FX ergänzen.
"""
import json, os, re, subprocess, sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
R = lambda w, m, beleg, **k: (dict({'w': w, 'm': m}, **k), beleg)
C = lambda c, beleg: ({'c': c}, beleg)

# Zustände (Text: COND_DATA, XPHB)
COND = {
    'Blinded': [R('atk', 'dis', 'your attack rolls have Disadvantage'),
                R('check', 'fail', 'automatically fail any ability check that requires sight', on=0, note='requires sight')],
    'Deafened': [R('check', 'fail', 'automatically fail any ability check that requires hearing', on=0, note='requires hearing')],
    'Exhaustion': [R('d20', 'ex', 'the roll is reduced by 2 times your Exhaustion level')],
    'Frightened': [R('check atk', 'dis', 'Disadvantage on ability checks and attack rolls while the source of fear is within line of sight',
                     note='source of fear in sight')],
    'Grappled': [R('atk', 'dis', 'Disadvantage on attack rolls against any target other than the grappler', on=0,
                   note='target other than the grappler')],
    'Incapacitated': [R('init', 'dis', "If you're Incapacitated when you roll Initiative, you have Disadvantage on the roll")],
    'Invisible': [R('init', 'adv', "If you're Invisible when you roll Initiative, you have Advantage on the roll"),
                  R('atk', 'adv', 'your attack rolls have Advantage', note='unless the target can see you')],
    'Paralyzed': [C('Incapacitated', 'You have the Incapacitated condition'),
                  R('save', 'fail', 'automatically fail Strength and Dexterity saving throws', ab=['STR', 'DEX'])],
    'Petrified': [C('Incapacitated', 'You have the Incapacitated condition'),
                  R('save', 'fail', 'automatically fail Strength and Dexterity saving throws', ab=['STR', 'DEX'])],
    'Poisoned': [R('atk check', 'dis', 'Disadvantage on attack rolls and ability checks')],
    'Prone': [R('atk', 'dis', 'You have Disadvantage on attack rolls')],
    'Restrained': [R('atk', 'dis', 'your attack rolls have Disadvantage'),
                   R('save', 'dis', 'Disadvantage on Dexterity saving throws', ab=['DEX'])],
    'Stunned': [C('Incapacitated', 'You have the Incapacitated condition'),
                R('save', 'fail', 'automatically fail Strength and Dexterity saving throws', ab=['STR', 'DEX'])],
    'Unconscious': [C('Incapacitated', 'You have the Incapacitated and Prone conditions'),
                    C('Prone', 'You have the Incapacitated and Prone conditions'),
                    R('save', 'fail', 'automatically fail Strength and Dexterity saving throws', ab=['STR', 'DEX'])],
}

# Effekte (Namen wie EFFECT_DATA; Text: ZB_SPELLS in der Fassung aus EFFECT_DATA bzw. CLASS_DATA)
FX = {
    'Bless': [R('atk save', '+1d4', 'adds 1d4 to the attack roll or save')],
    'Bane': [R('atk save', '-1d4', 'subtract 1d4 from the attack roll or save')],
    'Guidance': [R('check', '+1d4', 'adds 1d4 to any ability check using the chosen skill', sk='*', note='chosen skill')],
    'Enhance Ability': [R('check', 'adv', 'Advantage on ability checks using the chosen ability', ab='*', note='chosen ability')],
    'Hex': [R('check', 'dis', 'Disadvantage on ability checks made with the chosen ability', ab='*', note='chosen ability')],
    'Warding Bond': [R('save', '+1', '+1 bonus to AC and saving throws'), R('ac', '+1', '+1 bonus to AC and saving throws')],
    'Pass without Trace': [R('check', '+10', '+10 bonus to Dexterity (Stealth) checks', sk='Stealth')],
    'Magic Weapon': [R('watk', 'v', '+1 bonus to attack rolls and damage rolls', d='+1'),
                     R('wdmg', 'v', '+1 bonus to attack rolls and damage rolls', d='+1')],
    'Elemental Weapon': [R('watk', '+1', '+1 bonus to attack rolls'), R('wdmg', '+1d4', 'deals an extra 1d4 damage of the chosen type')],
    "Crusader's Mantle": [R('wdmg', '+1d4', 'extra 1d4 Radiant damage when hitting with a weapon')],
    'Divine Favor': [R('wdmg', '+1d4', 'your attacks with weapons deal an extra 1d4 Radiant damage')],
    'Haste': [R('save', 'adv', 'Advantage on Dexterity saving throws', ab=['DEX']), R('ac', '+2', '+2 bonus to Armor Class'),
              R('spd', 'x2', "target's Speed is doubled")],
    'Slow': [R('save', '-2', '-2 penalty to AC and Dexterity saving throws', ab=['DEX']),
             R('ac', '-2', '-2 penalty to AC and Dexterity saving throws'), R('spd', 'half', "affected target's Speed is halved")],
    'Ray of Enfeeblement': [R('d20', 'dis', 'Disadvantage on Strength-based D20 Tests', ab=['STR']),
                            R('dmg', '-1d8', 'subtracts 1d8 from all its damage rolls')],
    'Mind Sliver': [R('save', '-1d4', 'subtract 1d4 from the next saving throw', once=1)],
    'Vicious Mockery': [R('atk', 'dis', 'Disadvantage on the next attack roll', once=1)],
    'Frostbite': [R('watk', 'dis', 'disadvantage on the next weapon attack roll', once=1)],
    'Beacon of Hope': [R('save', 'adv', 'Advantage on Wisdom saving throws', ab=['WIS'])],
    'Holy Aura': [R('save', 'adv', 'Advantage on all saving throws')],
    'Foresight': [R('d20', 'adv', 'Advantage on D20 Tests')],
    'Circle of Power': [R('save', 'adv', 'Advantage on saving throws against spells and other magical effects', on=0,
                          note='vs. spells and magical effects')],
    'Aura of Purity': [R('save', 'adv', 'Advantage on saving throws to avoid or end effects that include the Blinded, Charmed, Deafened, Frightened, Paralyzed, Poisoned, or Stunned condition',
                         on=0, note='vs. Blinded, Charmed, Deafened, Frightened, Paralyzed, Poisoned, Stunned')],
    'Invisibility': [C('Invisible', 'has the Invisible condition')],
    'Greater Invisibility': [C('Invisible', 'has the Invisible condition')],
    'Hold Person': [C('Paralyzed', 'have the Paralyzed condition')],
    "Tasha's Hideous Laughter": [C('Prone', 'it has the Prone and Incapacitated conditions'),
                                 C('Incapacitated', 'it has the Prone and Incapacitated conditions')],
    'Shield of Faith': [R('ac', '+2', '+2 bonus to AC')],
    'Shield': [R('ac', '+5', '+5 bonus to AC')],
    'Barkskin': [R('ac', 'min17', 'has an Armor Class of 17 if its AC is lower than that')],
    'Mage Armor': [R('ac', 'base13', "base AC becomes 13 plus its Dexterity modifier")],
    'Longstrider': [R('spd', '+10', "Speed increases by 10 feet")],
    'Bardic Inspiration': [R('d20', 'v', 'add the number rolled to the d20', on=0, once=1, note='after a failed D20 Test')],
    'Emboldening Bond': [R('d20', '+1d4', 'add the number rolled to an attack roll, an ability check, or a saving throw', on=0,
                           note='once per turn')],
    'Aura of Protection': [R('save', 'v', 'bonus to saving throws equal to your Charisma modifier')],
}


def dump(html):
    out = 'roll_fx_dump.json'
    subprocess.check_call(['node', os.path.join(TOOLS, 'dump.js'), html,
                           "{cond:COND_DATA,ef:EFFECT_DATA,zb:ZB_SPELLS.filter(s=>EFFECT_DATA.some(e=>e.k==='s'&&e.n===s.name&&e.s===s.src)).map(s=>({n:s.name,d:s.desc})),"
                           "cd:Object.fromEntries(EFFECT_DATA.filter(e=>e.k==='f').map(e=>{const c=CLASS_DATA[e.c];let f=(c.base||[]).find(x=>x&&x.name===e.n);"
                           "if(!f)for(const k in c.subclass||{}){f=(c.subclass[k]||[]).find(x=>x&&x.name===e.n);if(f)break;}return [e.n,f?f.desc:'']}))}",
                           out], stdout=subprocess.DEVNULL)
    d = json.load(open(out, encoding='utf-8'))
    os.remove(out)
    return d


W_OK = {'d20', 'atk', 'watk', 'save', 'check', 'init', 'dmg', 'wdmg', 'ac', 'spd'}
M_OK = re.compile(r"^([+-]\d*d?\d+|v|adv|dis|fail|ex|min17|base13|x2|half)$")


def build(html):
    d = dump(html)
    fehler = []
    texte_fx = {s['n']: s['d'] for s in d['zb']}
    texte_fx.update(d['cd'])
    namen_fx = {e['n'] for e in d['ef']}

    def pruefe(gruppe, name, liste, text):
        regeln = []
        for regel, beleg in liste:
            if beleg not in text:
                fehler.append(f'Beleg nicht im Text: {gruppe} {name} – {beleg!r}')
                continue
            if 'c' in regel:
                if regel['c'] not in COND:
                    fehler.append(f'Zustand ohne Regeln: {name} → {regel["c"]}')
            else:
                if not set(regel['w'].split()) <= W_OK or not M_OK.match(regel['m']):
                    fehler.append(f'Regel ungültig: {name} {regel}')
            regeln.append(regel)
        return regeln

    cond = {}
    for n, liste in COND.items():
        if n not in d['cond']:
            fehler.append(f'Zustand fehlt in COND_DATA: {n}')
            continue
        cond[n] = pruefe('cond', n, liste, d['cond'][n])
    fx = {}
    for n, liste in FX.items():
        if n not in namen_fx:
            fehler.append(f'Effekt fehlt in EFFECT_DATA: {n}')
            continue
        if not texte_fx.get(n):
            fehler.append(f'Kein Regeltext: {n}')
            continue
        fx[n] = pruefe('fx', n, liste, texte_fx[n])
    return {'cond': cond, 'fx': fx}, fehler


def main():
    html = sys.argv[1]
    write = '--write' in sys.argv
    daten, fehler = build(html)
    for g in ('cond', 'fx'):
        for n, rs in daten[g].items():
            print(f'  {g} {n}: ' + '; '.join(r['c'] if 'c' in r else f"{r['w']} {r['m']}" + (' (aus)' if r.get('on') == 0 else '') for r in rs))
    if fehler:
        print('FEHLER:', *fehler, sep='\n  ')
        sys.exit(1)
    block = '// ROLL_FX-START (tools/roll_fx.py; Würfel-Regeln für Zustände/Effekte, Belege aus COND_DATA/ZB_SPELLS/CLASS_DATA)\n' + \
        'const ROLL_FX=' + json.dumps(daten, ensure_ascii=False, separators=(',', ':')) + ';\n// ROLL_FX-END\n'
    s = open(html, encoding='utf-8').read()
    m = re.search(r'// ROLL_FX-START.*?// ROLL_FX-END\n', s, re.S)
    if m:
        neu = s[:m.start()] + block + s[m.end():]
    else:
        k = s.count('// EFFECT_DATA-END\n')
        if k != 1:
            sys.exit(f'Anker // EFFECT_DATA-END {k}x gefunden')
        i = s.index('// EFFECT_DATA-END\n') + len('// EFFECT_DATA-END\n')
        neu = s[:i] + block + s[i:]
    print(f"{len(daten['cond'])} Zustände, {len(daten['fx'])} Effekte, Block {len(block)} Bytes", '– unverändert' if neu == s else '')
    if write and neu != s:
        open(html, 'w', encoding='utf-8').write(neu)
        print('geschrieben')


if __name__ == '__main__':
    main()
