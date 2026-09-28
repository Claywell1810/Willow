# paladin_config.py — Klassen-Konfiguration für build_class.py (Paladin)
# Tracker: nur Features mit Nutzungszahl/Rast oder Verbrauch einer anderen Ressource (uses None), Werte aus dem Feature-Text.
# uses: Zahl | "str"/"dex"/"con"/"int"/"wis"/"cha" (Modifikator, min. 1) | "level" | "level*5" (Faktor × Stufe) | "pb" | {Stufe: Anzahl} (Anleitung B2)
# 'pool': True = Pool-Zähler (Zahlenfeld mit Maximum statt Pips), seit 27.09.2026 für Lay on Hands (5 × Paladin-Stufe HP).
NONE = {'uses': None, 'restore': None}  # verbraucht Channel Divinity → kein eigener Zähler
CONFIG = {
    'class': 'Paladin',
    'trackers': {
        'base': [
            # Lay on Hands: „healing pool that replenishes when you finish a Long Rest … equal to five times your Paladin level"
            {'feature': 'Lay on Hands', 'id': 'layonhands', 'icon': '🤲', 'uses': 'level*5', 'restore': 'long', 'pool': True},
            # Class Table „Channel Divinity": 2 (L3), 3 (L11); Short Rest: 1 Nutzung zurück, Long Rest: alle
            {'feature': 'Channel Divinity', 'id': 'channeldivinity', 'icon': '✨', 'uses': {3: 2, 11: 3}, 'restore': 'short'},
            {'feature': "Paladin's Smite", 'id': 'paladinssmite', 'icon': '⚔', 'uses': 1, 'restore': 'long'},
            {'feature': 'Faithful Steed', 'id': 'faithfulsteed', 'icon': '🐴', 'uses': 1, 'restore': 'long'},
            {'feature': 'Abjure Foes', 'id': 'abjurefoes', 'icon': '😨', **NONE},
        ],
        'Oath of Devotion': [
            {'feature': 'Sacred Weapon', 'id': 'dv_sacredweapon', 'icon': '🗡', **NONE},
            {'feature': 'Holy Nimbus', 'id': 'dv_holynimbus', 'icon': '☀', 'uses': 1, 'restore': 'long'},
        ],
        'Oath of the Ancients': [
            {'feature': "Nature's Wrath", 'id': 'an_natureswrath', 'icon': '🌿', **NONE},
            {'feature': 'Undying Sentinel', 'id': 'an_undyingsentinel', 'icon': '🌳', 'uses': 1, 'restore': 'long'},
            {'feature': 'Elder Champion', 'id': 'an_elderchampion', 'icon': '🍃', 'uses': 1, 'restore': 'long'},
        ],
        'Oath of Vengeance': [
            {'feature': 'Vow of Enmity', 'id': 'vg_vowofenmity', 'icon': '🎯', **NONE},
            {'feature': 'Avenging Angel', 'id': 'vg_avengingangel', 'icon': '👼', 'uses': 1, 'restore': 'long'},
        ],
        'Oathbreaker': [
            {'feature': 'Dread Lord', 'id': 'ob_dreadlord', 'icon': '💀', 'uses': 1, 'restore': 'long'},
        ],
        'Oath of the Crown': [
            {'feature': 'Exalted Champion', 'id': 'cr_exaltedchampion', 'icon': '👑', 'uses': 1, 'restore': 'long'},
        ],
        'Oath of Conquest': [
            {'feature': 'Invincible Conqueror', 'id': 'cq_invincibleconqueror', 'icon': '🏰', 'uses': 1, 'restore': 'long'},
        ],
        'Oath of Glory': [
            {'feature': 'Inspiring Smite', 'id': 'gl_inspiringsmite', 'icon': '💫', **NONE},
            {'feature': 'Peerless Athlete', 'id': 'gl_peerlessathlete', 'icon': '🏃', **NONE},
            {'feature': 'Glorious Defense', 'id': 'gl_gloriousdefense', 'icon': '🛡', 'uses': 'cha', 'restore': 'long'},
            {'feature': 'Living Legend', 'id': 'gl_livinglegend', 'icon': '🌟', 'uses': 1, 'restore': 'long'},
        ],
        'Oath of the Watchers': [
            {'feature': 'Mortal Bulwark', 'id': 'wt_mortalbulwark', 'icon': '👁', 'uses': 1, 'restore': 'long'},
        ],
    },
    # Werte aus class-paladin.json (XPHB): hd, proficiency, startingProficiencies, startingEquipment, multiclassing, page
    # Multiclassing PHB'24: 13 in beiden Hauptattributen (primaryAbility: str + cha)
    'traits': {
        'hd': 'd10',
        'primaryAbility': 'Strength and Charisma',
        'hpLevel1': '10 + Con modifier',
        'hpPerLevel': 'd10 (or 6) + Con modifier',
        'savingThrows': ['Wisdom', 'Charisma'],
        'armorTraining': 'Light armor, Medium armor, Heavy armor, Shields',
        'weaponProficiencies': 'Simple weapons, Martial weapons',
        'skillProficiencies': {'count': 2, 'from': ['Athletics', 'Insight', 'Intimidation', 'Medicine', 'Persuasion', 'Religion']},
        'spellcastingAbility': 'Charisma',
        'startingEquipment': [
            "(A) Chain Mail, Shield, Longsword, 6 Javelins, Holy Symbol, Priest's Pack, and 9 GP",
            '— or — (B) 150 GP',
        ],
        'multiclassingReq': 'Strength 13 and Charisma 13',
        'multiclassingGains': 'Martial weapons, Light armor, Medium armor, Shields',
        'source': "PHB'24, page 108",
    },
}
