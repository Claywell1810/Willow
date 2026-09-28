# rogue_config.py — Klassen-Konfiguration für build_class.py (Rogue)
# Tracker: nur Features mit Nutzungszahl/Rast, Werte aus dem Feature-Text (5e.tools).
# uses: Zahl | "str"/"dex"/"con"/"int"/"wis"/"cha" (Modifikator, min. 1) | "level" | "pb" | {Stufe: Anzahl} (Anleitung B2)
CONFIG = {
    'class': 'Rogue',
    'trackers': {
        'base': [
            # „Once you use this feature, you can't use it again until you finish a Short or Long Rest.\"
            {'feature': 'Stroke of Luck', 'id': 'strokeofluck', 'icon': '🍀', 'uses': 1, 'restore': 'short'},
        ],
        'Arcane Trickster': [
            {'feature': 'Spell Thief', 'id': 'ta_spellthief', 'icon': '🪄', 'uses': 1, 'restore': 'long'},
        ],
        'Inquisitive': [
            {'feature': 'Unerring Eye', 'id': 'iq_unerringeye', 'icon': '👁', 'uses': 'wis', 'restore': 'long'},
        ],
        'Swashbuckler': [
            {'feature': 'Master Duelist', 'id': 'sw_masterduelist', 'icon': '🤺', 'uses': 1, 'restore': 'short'},
        ],
        'Phantom': [
            {'feature': 'Wails from the Grave', 'id': 'ph_wails', 'icon': '👻', 'uses': 'dex', 'restore': 'long'},
            {'feature': 'Voice of Death', 'id': 'ph_voiceofdeath', 'icon': '💀', 'uses': 1, 'restore': 'short'},
            {'feature': 'Ghost Walk', 'id': 'ph_ghostwalk', 'icon': '🌫', 'uses': 1, 'restore': 'long'},
        ],
        'Soulknife': [
            # Tabelle „Soulknife Energy Dice\": 4 (L3), 6 (L5), 8 (L9), 8 (L11), 10 (L13), 12 (L17); Short Rest: 1 zurück, Long Rest: alle
            {'feature': 'Psionic Power', 'id': 'sn_psionicdice', 'name': 'Psionic Energy Dice', 'icon': '🔮', 'uses': {3: 4, 5: 6, 9: 8, 13: 10, 17: 12}, 'restore': 'long', 'tag': 'Passiv'},
            {'feature': 'Psychic Veil', 'id': 'sn_psychicveil', 'icon': '🫥', 'uses': 1, 'restore': 'long'},
            {'feature': 'Rend Mind', 'id': 'sn_rendmind', 'icon': '🧠', 'uses': 1, 'restore': 'long'},
        ],
    },
    # Anzeige-Tag einzelner Features überschreiben (seit 27.09.2026, Fixliste): Devious Strikes ist eine Sneak-Attack-Option,
    # die Heuristik trifft „take an action\" aus dem Daze-Text.
    'feature_tags': {
        'base': {'Devious Strikes': 'Passiv'},
    },
    # Werte aus class-rogue.json (XPHB): hd, proficiency, startingProficiencies, startingEquipment, multiclassing, page
    'traits': {
        'hd': 'd8',
        'primaryAbility': 'Dexterity',
        'hpLevel1': '8 + Con modifier',
        'hpPerLevel': 'd8 (or 5) + Con modifier',
        'savingThrows': ['Dexterity', 'Intelligence'],
        'armorTraining': 'Light armor',
        'weaponProficiencies': 'Simple weapons, Martial weapons that have the Finesse or Light property',
        'toolProficiencies': "Thieves' Tools",
        'skillProficiencies': {'count': 4, 'from': ['Acrobatics', 'Athletics', 'Deception', 'Insight', 'Intimidation',
                                                     'Investigation', 'Perception', 'Persuasion', 'Sleight of Hand', 'Stealth']},
        'spellcastingAbility': '',
        'startingEquipment': [
            "(A) Leather Armor, 2 Daggers, Shortsword, Shortbow, 20 Arrows, Quiver, Thieves' Tools, Burglar's Pack, and 8 GP",
            '— or — (B) 100 GP',
        ],
        'multiclassingReq': 'Dexterity 13',
        'multiclassingGains': "Light armor, Thieves' Tools, one skill from the Rogue skill list",
        'source': "PHB'24, page 128",
    },
}
