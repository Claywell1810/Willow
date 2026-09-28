# barbarian_config.py — Klassen-Konfiguration für build_class.py (Barbarian)
# Tracker: nur Features mit Nutzungszahl/Rast, Werte aus dem Feature-Text (5e.tools).
# uses: Zahl | "str"/"dex"/"con"/"int"/"wis"/"cha" (Modifikator, min. 1) | "level" | "pb" | {Stufe: Anzahl} (Anleitung B2)
# Rages (Class Table): 2 (L1), 3 (L3), 4 (L6), 5 (L12), 6 (L17). Short Rest: 1 Nutzung zurück, Long Rest: alle (steht im desc).
# Pro-Rage-Nutzungen (Fanatical Focus, Travel Along the Tree), Relentless Rage (DC-Zähler) und Rage-Kosten einzelner Features haben keinen Tracker.
CONFIG = {
    'class': 'Barbarian',
    'trackers': {
        'base': [
            {'feature': 'Rage', 'id': 'bb_rage', 'icon': '🔥', 'uses': {'1': 2, '3': 3, '6': 4, '12': 5, '17': 6}, 'restore': 'short'},
            # „When you roll Initiative, you can regain all expended uses of Rage … until you finish a Long Rest.\"
            {'feature': 'Persistent Rage', 'id': 'bb_persistentrage', 'icon': '♾', 'uses': 1, 'restore': 'long', 'tag': 'Passiv'},
        ],
        # „Once you use this feature, you can't use it again until you finish a Long Rest unless you expend a use of your Rage.\"
        'Path of the Berserker': [
            {'feature': 'Intimidating Presence', 'id': 'bb_bk_intimidating', 'icon': '😱', 'uses': 1, 'restore': 'long'},
        ],
        'Path of the Ancestral Guardian': [
            {'feature': 'Consult the Spirits', 'id': 'bb_ag_consult', 'icon': '👻', 'uses': 1, 'restore': 'short', 'tag': 'Aktion'},
        ],
        # Pool aus d12 (4 / 5 bei L6 / 6 bei L12 / 7 bei L17), Long Rest
        'Path of the Zealot': [
            {'feature': 'Warrior of the Gods', 'id': 'bb_zl_warrior', 'icon': '🎲', 'uses': {'3': 4, '6': 5, '12': 6, '17': 7}, 'restore': 'long'},
            {'feature': 'Zealous Presence', 'id': 'bb_zl_presence', 'icon': '📣', 'uses': 1, 'restore': 'long'},
            {'feature': 'Rage of the Gods', 'id': 'bb_zl_rageofgods', 'icon': '👼', 'uses': 1, 'restore': 'long'},
        ],
        'Path of the Beast': [
            {'feature': 'Infectious Fury', 'id': 'bb_bs_fury', 'icon': '🦠', 'uses': 'pb', 'restore': 'long'},
            {'feature': 'Call the Hunt', 'id': 'bb_bs_hunt', 'icon': '🐺', 'uses': 'pb', 'restore': 'long'},
        ],
        'Path of Wild Magic': [
            {'feature': 'Magic Awareness', 'id': 'bb_wm_awareness', 'icon': '🔮', 'uses': 'pb', 'restore': 'long'},
            {'feature': 'Bolstering Magic', 'id': 'bb_wm_bolstering', 'icon': '✨', 'uses': 'pb', 'restore': 'long'},
        ],
    },
    # Anzeige-Tag einzelner Features überschreiben (Tag-Heuristik trifft „Reaction\" aus Nebensätzen; gilt auch für Tracker dieser Features).
    # Seit 27.09.2026 (Fixliste): Form of the Beast/Infectious Fury = Passiv, Rage of the Gods = mit der Rage aktiviert (Bonusaktion).
    'feature_tags': {
        'Path of the Beast': {'Form of the Beast': 'Passiv', 'Infectious Fury': 'Passiv'},
        'Path of the Zealot': {'Rage of the Gods': 'Bonusaktion'},
    },
    # Werte aus class-barbarian.json (XPHB): hd, proficiency, startingProficiencies, startingEquipment, multiclassing, page
    'traits': {
        'hd': 'd12',
        'primaryAbility': 'Strength',
        'hpLevel1': '12 + Con modifier',
        'hpPerLevel': 'd12 (or 7) + Con modifier',
        'savingThrows': ['Strength', 'Constitution'],
        'armorTraining': 'Light armor, Medium armor, Shields',
        'weaponProficiencies': 'Simple weapons, Martial weapons',
        'skillProficiencies': {'count': 2, 'from': ['Animal Handling', 'Athletics', 'Intimidation', 'Nature', 'Perception', 'Survival']},
        'spellcastingAbility': '',
        'startingEquipment': [
            '(A) Greataxe, 4 Handaxes, Explorer\'s Pack, and 15 GP',
            '— or — (B) 75 GP',
        ],
        'multiclassingReq': 'Strength 13',
        'multiclassingGains': 'Martial weapons, Shields',
        'source': "PHB'24, page 50",
    },
}
