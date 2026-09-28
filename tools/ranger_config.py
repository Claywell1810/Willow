# ranger_config.py — Klassen-Konfiguration für build_class.py (Ranger)
# Tracker: nur Features mit Nutzungszahl/Rast, Werte aus dem Feature-Text bzw. der Class Table.
# uses: Zahl | "str"/"dex"/"con"/"int"/"wis"/"cha" (Modifikator, min. 1) | "level" | "pb" | {Stufe: Anzahl} (Anleitung B2)
# Nicht getrackt: Hunter's Prey/Defensive Tactics (Auswahl bei Rast), Primal Companion (Ersatz nur über Zauberplatz),
#   Reaktionen ohne Nutzungslimit (Superior Hunter's Defense, Shadowy Dodge, Spectral Defense …).
CONFIG = {
    'class': 'Ranger',
    'trackers': {
        'base': [
            # Class Table „Favored Enemy": 2 (L1), 3 (L5), 4 (L9), 5 (L13), 6 (L17); Long Rest
            {'feature': 'Favored Enemy', 'id': 'favoredenemy', 'icon': '🎯', 'uses': {1: 2, 5: 3, 9: 4, 13: 5, 17: 6}, 'restore': 'long'},
            {'feature': 'Tireless', 'id': 'tireless', 'icon': '💪', 'uses': 'wis', 'restore': 'long'},
            {'feature': "Nature's Veil", 'id': 'naturesveil', 'icon': '🍃', 'uses': 'wis', 'restore': 'long'},
        ],
        'Gloom Stalker': [
            {'feature': 'Dread Ambusher', 'name': 'Dreadful Strike', 'id': 'gs_dreadfulstrike', 'icon': '🌑', 'uses': 'wis', 'restore': 'long'},
        ],
        'Horizon Walker': [
            {'feature': 'Detect Portal', 'id': 'hw_detectportal', 'icon': '🌀', 'uses': 1, 'restore': 'short'},
            {'feature': 'Ethereal Step', 'id': 'hw_etherealstep', 'icon': '👻', 'uses': 1, 'restore': 'short'},
        ],
        'Monster Slayer': [
            {'feature': "Hunter's Sense", 'id': 'ms_huntersense', 'icon': '👁', 'uses': 'wis', 'restore': 'long'},
            {'feature': "Magic-User's Nemesis", 'id': 'ms_magicusersnemesis', 'icon': '🚫', 'uses': 1, 'restore': 'short'},
        ],
        'Fey Wanderer': [
            {'feature': 'Fey Reinforcements', 'id': 'fw_feyreinforcements', 'icon': '🧚', 'uses': 1, 'restore': 'long'},
            {'feature': 'Misty Wanderer', 'id': 'fw_mistywanderer', 'icon': '✨', 'uses': 'wis', 'restore': 'long'},
        ],
        'Swarmkeeper': [
            {'feature': 'Writhing Tide', 'id': 'sk_writhingtide', 'icon': '🐝', 'uses': 'pb', 'restore': 'long'},
            {'feature': 'Swarming Dispersal', 'id': 'sk_swarmingdispersal', 'icon': '🌪', 'uses': 'pb', 'restore': 'long'},
        ],
        'Drakewarden': [
            {'feature': 'Drake Companion', 'id': 'dw_drakecompanion', 'icon': '🐉', 'uses': 1, 'restore': 'long'},
            {'feature': "Drake's Breath", 'id': 'dw_drakesbreath', 'icon': '🔥', 'uses': 1, 'restore': 'long'},
            {'feature': 'Perfected Bond', 'name': 'Reflexive Resistance', 'id': 'dw_reflexiveresistance', 'icon': '🛡', 'uses': 'pb', 'restore': 'long'},
        ],
    },
    # Werte aus class-ranger.json (XPHB): hd, proficiency, startingProficiencies, startingEquipment, multiclassing, page
    # Multiclassing PHB'24: 13 in beiden Hauptattributen (primaryAbility: dex + wis)
    'traits': {
        'hd': 'd10',
        'primaryAbility': 'Dexterity and Wisdom',
        'hpLevel1': '10 + Con modifier',
        'hpPerLevel': 'd10 (or 6) + Con modifier',
        'savingThrows': ['Strength', 'Dexterity'],
        'armorTraining': 'Light armor, Medium armor, Shields',
        'weaponProficiencies': 'Simple weapons, Martial weapons',
        'skillProficiencies': {'count': 3, 'from': ['Animal Handling', 'Athletics', 'Insight', 'Investigation', 'Nature', 'Perception', 'Stealth', 'Survival']},
        'spellcastingAbility': 'Wisdom',
        'startingEquipment': [
            "(A) Studded Leather Armor, Scimitar, Shortsword, Longbow, 20 Arrows, Quiver, Druidic Focus (sprig of mistletoe), Explorer's Pack, and 7 GP",
            '— or — (B) 150 GP',
        ],
        'multiclassingReq': 'Dexterity 13 and Wisdom 13',
        'multiclassingGains': 'Martial weapons, Light armor, Medium armor, Shields, one skill from the Ranger skill list',
        'source': "PHB'24, page 118",
    },
}
