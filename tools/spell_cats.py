# spell_cats.py – Zauber-Kategorien (Bilder in My Spells), seit 01.10.2026
# Erklärung: docs/ZAUBER_KATEGORIEN.md
# Aufruf (aus dem Ordner über dem Klon, nach `setup.sh zauber`):
#   python3 willow/tools/spell_cats.py DnD_Character_App.html src [--dry]
# Liest ZB_SPELLS-Namen aus der HTML (Namen bleiben unverändert), 5e.tools-Daten aus src/spells-*.json,
# ordnet jeden Zauber per REGELN zu, KORREKTUREN (Liste unten) gehen vor. Schreibt die Zeile
#   const SPELL_CATS={"Name":"kat" | "dmg:typ", …};
# in die HTML (ersetzt sie, falls vorhanden, sonst direkt vor der Zeile `const BG_DATA=`).
# --dry: nur Übersicht + Liste „neu ohne Korrektur“ ausgeben, nichts schreiben.
import json, glob, re, sys

# ── Kategorien (Schlüssel ↔ Anzeige; Bilder stehen in der App: SPELL_CAT_ICONS) ──────────────
CATS = {
  'dmg':    'Schaden',
  'ctrl':   'Kontrolle',
  'buff':   'Stärkung / Buffs',
  'debuff': 'Schwächung / Debuffs',
  'prot':   'Schutz',                 # Kategorie „Schutz & Heilung“, Bild 🛡️
  'heal':   'Heilung',                # Kategorie „Schutz & Heilung“, Bild 💚
  'summon': 'Beschwörung',
  'move':   'Bewegung & Positionierung',
  'info':   'Information & Kommunikation',
  'social': 'Täuschung & soziale Einflussnahme',
  'util':   'Hilfsmagie',                # bis 01.10.2026 „Alltag & Erkundung / Utility“ (🧰)
}
DMG_TYPES = ['acid','bludgeoning','cold','fire','force','lightning','necrotic','piercing','poison','psychic','radiant','slashing','thunder']

# ── Korrekturen: Hauptzweck nach Durchsicht (Claude/Simon). Wert = Kategorie oder "dmg:<typ>" / "dmg:multi"
# Neue Einträge alphabetisch; Begründung nur bei nicht offensichtlichen Fällen als Kommentar.
KORREKTUREN = {
  "Alter Self": "buff",
  "Alustriel\"s Mooncloak": "prot",
  "Antimagic Field": "prot",
  "Armor of Agathys": "prot",
  "Astral Projection": "move",
  "Awaken": "util",
  "Beast Bond": "info",
  "Bigby\"s Hand": "dmg:force",
  "Blink": "prot",
  "Blur": "prot",
  "Cacophonic Shield": "prot",
  "Catnap": "util",
  "Ceremony": "util",
  "Compulsion": "ctrl",
  "Confusion": "ctrl",
  "Conjure Animals": "summon",
  "Conjure Celestial": "summon",
  "Conjure Constructs": "summon",
  "Conjure Elemental": "summon",
  "Conjure Fey": "summon",
  "Conjure Minor Elementals": "summon",
  "Conjure Woodland Beings": "summon",
  "Contact Other Plane": "info",
  "Contingency": "util",
  "Control Water": "ctrl",
  "Creation": "util",
  "Crown of Madness": "ctrl",
  "Crusader\"s Mantle": "buff",
  "Dancing Lights": "util",
  "Darkvision": "buff",
  "Dimension Door": "move",
  "Dispel Evil and Good": "prot",
  "Divine Favor": "buff",
  "Dominate Beast": "ctrl",
  "Dominate Monster": "ctrl",
  "Dominate Person": "ctrl",
  "Draconic Transformation": "buff",
  "Dream": "info",
  "Dream of the Blue Veil": "move",
  "Druid Grove": "prot",
  "Earthbind": "ctrl",
  "Elemental Bane": "debuff",
  "Elemental Weapon": "buff",
  "Enemies Abound": "ctrl",
  "Enervation": "dmg:necrotic",
  "Ensnaring Strike": "ctrl",
  "Enthrall": "social",
  "Etherealness": "move",
  "Evard\"s Black Tentacles": "ctrl",
  "Expeditious Retreat": "move",
  "Faerie Fire": "debuff",
  "Feign Death": "util",
  "Finger of Death": "dmg:necrotic",
  "Fire Shield": "prot",
  "Fizban\"s Platinum Shield": "prot",
  "Fog Cloud": "ctrl",
  "Forbiddance": "prot",
  "Forcecage": "ctrl",
  "Fount of Moonlight": "buff",
  "Gaseous Form": "move",
  "Geas": "social",
  "Grasping Vine": "ctrl",
  "Greater Invisibility": "buff",
  "Greater Restoration": "heal",
  "Guardian of Nature": "buff",
  "Gust of Wind": "ctrl",
  "Hallow": "prot",
  "Heroism": "buff",
  "Holy Aura": "prot",
  "Holy Weapon": "buff",
  "Hunger of Hadar": "ctrl",
  "Ice Storm": "dmg:cold",
  "Intellect Fortress": "prot",
  "Investiture of Flame": "buff",
  "Investiture of Ice": "buff",
  "Investiture of Stone": "buff",
  "Investiture of Wind": "buff",
  "Jim\"s Glowing Coin": "util",
  "Jump": "move",
  "Kinetic Jaunt": "move",
  "Lesser Restoration": "heal",
  "Levitate": "move",
  "Longstrider": "move",
  "Maelstrom": "ctrl",
  "Magic Circle": "prot",
  "Mass Polymorph": "util",
  "Maximilian\"s Earthen Grasp": "ctrl",
  "Maze": "ctrl",
  "Meld into Stone": "util",
  "Mental Prison": "ctrl",
  "Meteor Swarm": "dmg:fire",
  "Mind Sliver": "dmg:psychic",
  "Mirage Arcane": "social",
  "Mirror Image": "prot",
  "Mislead": "social",
  "Modify Memory": "social",
  "Mold Earth": "util",
  "Mordenkainen\"s Faithful Hound": "prot",
  "Mordenkainen\"s Private Sanctum": "prot",
  "Motivational Speech": "buff",
  "Nathair\"s Mischief": "ctrl",
  "Negative Energy Flood": "dmg:necrotic",
  "Otto\"s Irresistible Dance": "ctrl",
  "Pass without Trace": "buff",
  "Polymorph": "ctrl",
  "Prismatic Wall": "prot",
  "Protection from Energy": "prot",
  "Protection from Evil and Good": "prot",
  "Protection from Poison": "prot",
  "Remove Curse": "heal",
  "Reverse Gravity": "ctrl",
  "Sequester": "prot",
  "Shadow of Moil": "prot",
  "Shapechange": "util",
  "Shield of Faith": "prot",
  "Shillelagh": "buff",
  "Silence": "ctrl",
  "Silvery Barbs": "debuff",
  "Simulacrum": "summon",
  "Skill Empowerment": "buff",
  "Slow": "ctrl",
  "Soul Cage": "util",
  "Spare the Dying": "heal",
  "Speak with Plants": "info",
  "Spider Climb": "move",
  "Spike Growth": "ctrl",
  "Spirit Guardians": "dmg:radiant",
  "Stinking Cloud": "ctrl",
  "Stoneskin": "prot",
  "Storm Sphere": "dmg:lightning",
  "Swift Quiver": "buff",
  "Symbol": "ctrl",
  "Synaptic Static": "dmg:psychic",
  "Tasha\"s Hideous Laughter": "ctrl",
  "Tasha\"s Otherworldly Guise": "buff",
  "Teleport": "move",
  "Temple of the Gods": "prot",
  "Tenser\"s Transformation": "buff",
  "Thaumaturgy": "util",
  "Thunder Step": "move",
  "Transmute Rock": "ctrl",
  "True Polymorph": "util",
  "Vampiric Touch": "dmg:necrotic",
  "Wall of Force": "ctrl",
  "Wall of Sand": "ctrl",
  "Wall of Stone": "ctrl",
  "Warding Wind": "prot",
  "Water Walk": "move",
  "Web": "ctrl",
  "Whirlwind": "ctrl",
  "Wind Walk": "move",
  "Wind Wall": "prot",
  "Wish": "util",
  "Wither and Bloom": "dmg:necrotic",
  "Wrath of Nature": "ctrl",
  "Zephyr Strike": "move",
}

SCH = {'A':'abj','C':'con','D':'div','E':'enc','V':'evo','I':'ill','N':'nec','T':'tra'}
CTRL = {'restrained','paralyzed','stunned','incapacitated','prone','grappled','petrified','unconscious'}
DEB = {'frightened','blinded','poisoned','deafened','exhaustion'}

def txt(e):
    if isinstance(e, str): return e
    if isinstance(e, list): return ' '.join(txt(x) for x in e)
    if isinstance(e, dict): return ' '.join(txt(e.get(k, '')) for k in ('entries', 'items', 'entry'))
    return ''

def dmg_key(d):
    if not d: return 'dmg:multi'
    return 'dmg:' + d[0] if len(d) == 1 else 'dmg:multi' if len(d) >= 3 else 'dmg:' + d[0]

def regel(s):
    """Grobzuordnung aus den 5e.tools-Markierungen (miscTags, damageInflict, conditionInflict, Schule, Text)."""
    m = set(s.get('miscTags', [])); dmg = s.get('damageInflict', []); con = set(s.get('conditionInflict', []))
    sch = SCH.get(s.get('school'), '')
    t = re.sub(r'\{@\w+ ([^|}]*)[^}]*\}', r'\1', txt(s.get('entries', []))).lower()
    willing = re.search(r'willing creature|creatures? of your choice|creature you touch|you touch a creature|up to (three|\w+) creatures', t)
    buffcue = re.search(r'\badds?\b[^.]{0,25}\d*d\d+ to|speed is doubled|bonus to ac|\+\d bonus|advantage on|resistance to|hit point maximum increases', t)
    if 'SMN' in m: return 'summon'
    if 'HL' in m or 'THP' in m: return 'heal'
    if willing and buffcue and not dmg: return 'buff'
    if re.search(r'curse|subtracts? (a )?\d*d\d|disadvantage on (attack|ability|saving)', t) and not s.get('spellAttack') and sch in ('nec', 'enc'): return 'debuff'
    if dmg and (s.get('spellAttack') or s.get('savingThrow') or 'AAD' in m): return dmg_key(dmg)
    if con & CTRL or ('DFT' in m and not dmg): return 'ctrl'
    if 'charmed' in con: return 'social'
    if con & DEB: return 'debuff'
    if dmg: return dmg_key(dmg)
    if 'TP' in m or 'PS' in m or 'FMV' in m or re.search(r'fly(ing)? speed|your speed|walking speed increases|teleport', t): return 'move'
    if 'MAC' in m or sch == 'abj': return 'prot'
    if re.search(r'(subtract|disadvantage on (attack|saving|ability)|penalty)', t) and s.get('savingThrow'): return 'debuff'
    if 'ADV' in m or re.search(r'add (a )?d\d|bonus to|advantage on', t): return 'buff'
    if sch == 'div' or re.search(r'telepathic|message|language', t): return 'info'
    if sch in ('ill', 'enc'): return 'social'
    return 'util'

def gueltig(v):
    return v in CATS or (v.startswith('dmg:') and (v[4:] in DMG_TYPES or v[4:] == 'multi'))

def main():
    html, srcdir = sys.argv[1], sys.argv[2]; dry = '--dry' in sys.argv
    S = {}
    for f in sorted(glob.glob(srcdir + '/spells-*.json')):
        for s in json.load(open(f, encoding='utf-8')).get('spell', []): S.setdefault(s['name'], []).append(s)
    h = open(html, encoding='utf-8').read()
    a = h.index('const ZB_SPELLS='); line = h[a:h.index('\n', a)]
    names = re.findall(r'\{"name":"((?:[^"\\]|\\.)*)"', line)
    names = [json.loads('"' + n + '"') for n in names]
    out, ohne, neu = {}, [], []
    for n in names:
        if n in KORREKTUREN:
            out[n] = KORREKTUREN[n]; continue
        L = S.get(n)
        if not L: ohne.append(n); out[n] = 'util'; continue
        s = next((x for x in L if x.get('source') == 'XPHB'), L[0])
        out[n] = regel(s); neu.append(n)
    bad = [k for k, v in KORREKTUREN.items() if not gueltig(v)]
    assert not bad, f'ungültige Korrektur: {bad}'
    from collections import Counter
    print(f'{len(out)} Zauber, {len(KORREKTUREN)} Korrekturen, ohne 5e.tools-Eintrag: {ohne}')
    print(Counter(v.split(":")[0] for v in out.values()))
    import os
    gp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'spell_cats_geprueft.txt')
    geprueft = {l.strip() for l in open(gp, encoding='utf-8') if l.strip() and not l.startswith('#')}
    offen = [n for n in names if n not in geprueft]
    if offen:
        print(f'NEU, noch nicht geprüft ({len(offen)}) – Kategorie prüfen, ggf. in KORREKTUREN, dann in spell_cats_geprueft.txt eintragen:')
        print(', '.join(f'{n}={out[n]}' for n in offen))
    else:
        print('alle Zauber geprüft')
    if dry: return
    row = 'const SPELL_CATS=' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';'
    if 'const SPELL_CATS=' in h:
        b = h.index('const SPELL_CATS='); h = h[:b] + row + h[h.index('\n', b):]
    else:
        assert h.count('\nconst BG_DATA=') == 1
        h = h.replace('\nconst BG_DATA=', '\n// SPELL_CATS (tools/spell_cats.py, docs/ZAUBER_KATEGORIEN.md): Kategorie je Zauber für das Bild in My Spells\n' + row + '\nconst BG_DATA=', 1)
    open(html, 'w', encoding='utf-8').write(h); print('geschrieben')

if __name__ == '__main__':
    main()
