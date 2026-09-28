# fighter_config.py — Klassen-Konfiguration für build_class.py (Fighter)
# Tracker: nur Features mit Nutzungszahl/Rast oder Verbrauch einer anderen Ressource (uses None), Werte aus dem Feature-Text.
# uses: Zahl | "str"/"dex"/"con"/"int"/"wis"/"cha" (Modifikator, min. 1) | "level" | "pb" | {Stufe: Anzahl} (Anleitung B2)
# conc: True = Konzentrations-Abzeichen „C" am Tracker (nur bei echter Konzentration, B2/B9)
# Rune Knight (seit 27.09.2026, Einzel-Tracker 'sub'): je Rune „Once you invoke this rune, you can't do so again until you finish
#   a short or long rest", ab L15 zweimal (Master of Runes) → uses {3:1, 15:2}; Hill/Storm Rune „Level 7+" (optionalfeatures.json);
#   'pick' = Runes Known (Rune Carver: 2 L3, 3 L7, 4 L10, 5 L15) – der Spieler markiert seine Runen.
NONE = {'uses': None, 'restore': None}  # verbraucht eine andere Ressource (Second Wind, Indomitable) → kein eigener Zähler
RUNES = [{'k': 'cloud', 'l': 'Cloud Rune'}, {'k': 'fire', 'l': 'Fire Rune'}, {'k': 'frost', 'l': 'Frost Rune'},
         {'k': 'stone', 'l': 'Stone Rune'}, {'k': 'hill', 'l': 'Hill Rune', 'minLvl': 7}, {'k': 'storm', 'l': 'Storm Rune', 'minLvl': 7}]
CONFIG = {
    'class': 'Fighter',
    'trackers': {
        'base': [
            # Class Table „Second Wind": 2 (L1), 3 (L4), 4 (L10); Short Rest: 1 Nutzung zurück, Long Rest: alle
            {'feature': 'Second Wind', 'id': 'secondwind', 'icon': '❤', 'uses': {1: 2, 4: 3, 10: 4}, 'restore': 'short'},
            {'feature': 'Tactical Mind', 'id': 'tacticalmind', 'icon': '🧠', **NONE},
            {'feature': 'Action Surge', 'id': 'actionsurge', 'icon': '⚡', 'uses': {2: 1, 17: 2}, 'restore': 'short'},
            {'feature': 'Indomitable', 'id': 'indomitable', 'icon': '🛡', 'uses': {9: 1, 13: 2, 17: 3}, 'restore': 'long'},
        ],
        'Battle Master': [
            {'feature': 'Combat Superiority', 'id': 'bm_superiority', 'name': 'Superiority Dice', 'icon': '🎲', 'uses': {3: 4, 7: 5, 15: 6}, 'restore': 'short'},
            {'feature': 'Know Your Enemy', 'id': 'bm_knowyourenemy', 'icon': '👁', 'uses': 1, 'restore': 'long'},
        ],
        'Arcane Archer': [
            {'feature': 'Arcane Shot', 'id': 'aa_arcaneshot', 'icon': '🏹', 'uses': 'int', 'restore': 'short'},
            {'feature': 'Magical Ammunition', 'id': 'aa_magicalammo', 'icon': '✨', 'uses': 1, 'restore': 'short'},
        ],
        'Cavalier': [
            {'feature': 'Unwavering Mark', 'id': 'cv_unwaveringmark', 'icon': '🐎', 'uses': 'str', 'restore': 'long', 'tag': 'Bonusaktion'},
            {'feature': 'Warding Maneuver', 'id': 'cv_wardingmaneuver', 'icon': '🛡', 'uses': 'con', 'restore': 'long'},
        ],
        'Samurai': [
            {'feature': 'Fighting Spirit', 'id': 'sa_fightingspirit', 'icon': '🔥', 'uses': 3, 'restore': 'long'},
            {'feature': 'Strength before Death', 'id': 'sa_strengthbeforedeath', 'icon': '⚔', 'uses': 1, 'restore': 'long'},
        ],
        'Echo Knight': [
            {'feature': 'Unleash Incarnation', 'id': 'ec_unleashincarnation', 'icon': '👥', 'uses': 'con', 'restore': 'long'},
            {'feature': 'Reclaim Potential', 'id': 'ec_reclaimpotential', 'icon': '💠', 'uses': 'con', 'restore': 'long'},
        ],
        'Psi Warrior': [
            # Tabelle „Psi Warrior Energy Dice": 4 (L3), 6 (L5), 8 (L9), 10 (L13), 12 (L17); Short Rest: 1 zurück, Long Rest: alle
            {'feature': 'Psionic Power', 'id': 'pw_psionicdice', 'name': 'Psionic Energy Dice', 'icon': '🔮', 'uses': {3: 4, 5: 6, 9: 8, 13: 10, 17: 12}, 'restore': 'long', 'tag': 'Passiv'},
            {'feature': 'Psionic Power', 'id': 'pw_telekineticmovement', 'name': 'Telekinetic Movement', 'icon': '🌀', 'uses': 1, 'restore': 'short', 'tag': 'Aktion'},
            {'feature': 'Telekinetic Adept', 'id': 'pw_psipoweredleap', 'name': 'Psi-Powered Leap', 'icon': '🦅', 'uses': 1, 'restore': 'short'},
            {'feature': 'Bulwark of Force', 'id': 'pw_bulwarkofforce', 'icon': '🛡', 'uses': 1, 'restore': 'long'},
            # Telekinesis per Feature: Konzentration bleibt Pflicht („while you maintain Concentration on it") → „C" (27.09.2026)
            {'feature': 'Telekinetic Master', 'id': 'pw_telekineticmaster', 'icon': '🪨', 'uses': 1, 'restore': 'long', 'conc': True},
        ],
        'Rune Knight': [
            {'feature': 'Rune Carver', 'id': 'rk_runes', 'icon': 'ᚱ', 'uses': {3: 1, 15: 2}, 'restore': 'short',
             'append': ['Master of Runes'], 'sub': RUNES, 'pick': {3: 2, 7: 3, 10: 4, 15: 5}},
            {'feature': "Giant's Might", 'id': 'rk_giantsmight', 'icon': '⛰', 'uses': 'pb', 'restore': 'long'},
            {'feature': 'Runic Shield', 'id': 'rk_runicshield', 'icon': '🔰', 'uses': 'pb', 'restore': 'long'},
        ],
        'Banneret': [
            {'feature': 'Group Recovery', 'id': 'bn_grouprecovery', 'icon': '🚩', 'uses': 1, 'restore': 'short'},
            {'feature': 'Shared Resilience', 'id': 'bn_sharedresilience', 'icon': '🤝', **NONE},
        ],
    },
    # Werte aus class-fighter.json (XPHB): hd, proficiency, startingProficiencies, startingEquipment, multiclassing, page
    'traits': {
        'hd': 'd10',
        'primaryAbility': 'Strength or Dexterity',
        'hpLevel1': '10 + Con modifier',
        'hpPerLevel': 'd10 (or 6) + Con modifier',
        'savingThrows': ['Strength', 'Constitution'],
        'armorTraining': 'Light armor, Medium armor, Heavy armor, Shields',
        'weaponProficiencies': 'Simple weapons, Martial weapons',
        'skillProficiencies': {'count': 2, 'from': ['Acrobatics', 'Animal Handling', 'Athletics', 'History', 'Insight',
                                                     'Intimidation', 'Persuasion', 'Perception', 'Survival']},
        'spellcastingAbility': '',
        'startingEquipment': [
            "(A) Chain Mail, Greatsword, Flail, 8 Javelins, Dungeoneer's Pack, and 4 GP",
            "— or — (B) Studded Leather Armor, Scimitar, Shortsword, Longbow, 20 Arrows, Quiver, Dungeoneer's Pack, and 11 GP",
            '— or — 155 GP',
        ],
        'multiclassingReq': 'Strength or Dexterity 13',
        'multiclassingGains': 'Martial weapons, Light armor, Medium armor, Shields',
        'source': "PHB'24, page 90",
    },
}
