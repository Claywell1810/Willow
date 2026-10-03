# artificer_config.py — Klassen-Konfiguration für build_class.py (Artificer, Paket M 03.10.2026)
# Fassung: 5e.tools class-artificer.json, Klasse EFA (Eberron: Forge of the Artificer, 2025er-Regeln; TCE hat reprintedAs EFA),
# Subklassen EFA (Alchemist, Armorer, Artillerist, Battle Smith, Cartographer) + Reanimator (RHW).
# Tracker: nur Features mit Nutzungszahl/Rast im Text; Werte aus dem Feature-Text bzw. der Class Table.
# uses: Zahl | "int" (Modifikator, min. 1) | "int*2" (2 × Modifikator, min. 2; seit Paket M) | {Stufe: Anzahl} (Anleitung B2)
CONFIG = {
    'class': 'Artificer',
    # Tag-Heuristik trifft Nebensätze: Steel Defender „take its Reaction on its own“ → Befehl ist eine Bonusaktion
    'feature_tags': {'Battle Smith': {'Steel Defender': 'Bonusaktion'}},
    'trackers': {
        'base': [
            # „a number of times equal to your Intelligence modifier (minimum of once) … when you finish a Long Rest"
            {'feature': "Tinker's Magic", 'id': 'af_tinkersmagic', 'icon': '🔧', 'uses': 'int', 'restore': 'long'},
            # Drain / Transmute: je „Once you use this feature, you can't do so again until you finish a Long Rest" (Charge = Zauberplatz)
            {'feature': 'Magic Item Tinker', 'id': 'af_magicitemtinker', 'icon': '🔋', 'uses': 1, 'restore': 'long',
             'sub': [{'k': 'drain', 'l': 'Drain Magic Item'}, {'k': 'transmute', 'l': 'Transmute Magic Item'}]},
            # „a number of times equal to your Intelligence modifier (minimum of once) … Long Rest"; L14 Refreshed Genius: Short Rest +1
            {'feature': 'Flash of Genius', 'id': 'af_flashofgenius', 'icon': '💡', 'uses': 'int', 'restore': 'long'},
            # „used a number of times equal to twice your Intelligence modifier (minimum of twice)"; neu gespeichert nach Long Rest
            {'feature': 'Spell-Storing Item', 'id': 'af_spellstoringitem', 'icon': '🔮', 'uses': 'int*2', 'restore': 'long'},
        ],
        'Alchemist': [
            # zwei Elixiere je Long Rest, „a total of three at level 5, four at level 9, and five at level 15"
            {'feature': 'Experimental Elixir', 'id': 'al_experimentalelixir', 'icon': '🧪', 'uses': {3: 2, 5: 3, 9: 4, 15: 5}, 'restore': 'long'},
            {'feature': 'Restorative Reagents', 'id': 'al_restorativereagents', 'icon': '💊', 'uses': 'int', 'restore': 'long', 'tag': 'Aktion'},
            # Conjured Cauldron: „Once you use this feature, you can't use it again until you finish a Long Rest"
            {'feature': 'Chemical Mastery', 'id': 'al_chemicalmastery', 'icon': '⚗', 'uses': 1, 'restore': 'long', 'tag': 'Aktion'},
        ],
        'Armorer': [
            # Dreadnaught – Giant Stature: „a number of times equal to your Intelligence modifier (minimum of once) … Long Rest"
            {'feature': 'Armor Model', 'id': 'arm_armormodel', 'icon': '🛡', 'uses': 'int', 'restore': 'long',
             'sub': [{'k': 'giantstature', 'l': 'Giant Stature (Dreadnaught)'}]},
            # Guardian-Reaktion und Infiltrator-Flug: je „Intelligence modifier (minimum of once) … Long Rest"
            {'feature': 'Perfected Armor', 'id': 'arm_perfectedarmor', 'icon': '⚙', 'uses': 'int', 'restore': 'long',
             'sub': [{'k': 'guardian', 'l': 'Guardian (Reaction)'}, {'k': 'infiltrator', 'l': 'Infiltrator (Bonus Action)'}]},
        ],
        'Artillerist': [
            # „Once you create a cannon, you can't do so again until you finish a Long Rest or expend a spell slot"
            {'feature': 'Eldritch Cannon', 'id': 'art_eldritchcannon', 'icon': '💥', 'uses': 1, 'restore': 'long'},
        ],
        'Battle Smith': [
            {'feature': 'Arcane Jolt', 'id': 'bs_arcanejolt', 'icon': '⚡', 'uses': 'int', 'restore': 'long'},
        ],
        'Cartographer': [
            # Illuminated Cartography (Faerie Fire ohne Platz): „Intelligence modifier (minimum of once) … Long Rest"
            {'feature': 'Mapping Magic', 'id': 'ct_mappingmagic', 'icon': '🗺', 'uses': 'int', 'restore': 'long', 'tag': 'Aktion'},
            # Unerring Path (Find the Path): „Once you use this benefit, you can't use it again until you finish a Long Rest"
            {'feature': 'Superior Atlas', 'id': 'ct_superioratlas', 'icon': '🧭', 'uses': 1, 'restore': 'long', 'tag': 'Aktion'},
        ],
        'Reanimator': [
            # Jolt to Life: „a number of times equal to your Intelligence modifier … Long Rest"
            {'feature': "Reanimator's Skill Set", 'id': 'rn_reanimatorsskillset', 'icon': '⚡', 'uses': 'int', 'restore': 'long', 'tag': 'Aktion'},
            {'feature': 'Reanimated Companion', 'id': 'rn_reanimatedcompanion', 'icon': '🧟', 'uses': 1, 'restore': 'long'},
            # Facilitated Revival (Raise Dead ohne Platz): „can't use it again until you finish a Long Rest"
            {'feature': 'Refined Reanimation', 'id': 'rn_refinedreanimation', 'icon': '💀', 'uses': 1, 'restore': 'long', 'tag': 'Aktion'},
        ],
    },
    # Werte aus class-artificer.json (EFA): hd, proficiency, startingProficiencies, startingEquipment, multiclassing, page
    'traits': {
        'hd': 'd8',
        'primaryAbility': 'Intelligence',
        'hpLevel1': '8 + Con modifier',
        'hpPerLevel': 'd8 (or 5) + Con modifier',
        'savingThrows': ['Constitution', 'Intelligence'],
        'armorTraining': 'Light armor, Medium armor, Shields',
        'weaponProficiencies': 'Simple weapons',
        'toolProficiencies': "Thieves' Tools, Tinker's Tools, one type of Artisan's Tools of your choice",
        'skillProficiencies': {'count': 2, 'from': ['Arcana', 'History', 'Investigation', 'Medicine', 'Nature', 'Perception', 'Sleight of Hand']},
        'spellcastingAbility': 'Intelligence',
        'startingEquipment': [
            "(A) Studded Leather Armor, Dagger, Thieves' Tools, Tinker's Tools, Dungeoneer's Pack, and 16 GP",
            '— or — (B) 150 GP',
        ],
        'multiclassingReq': 'Intelligence 13',
        'multiclassingGains': "Light armor, Medium armor, Shields, Tinker's Tools, one skill from the Artificer skill list",
        'source': 'EFA, page 7',
    },
}
