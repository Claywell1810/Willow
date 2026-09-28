# monk_config.py — Klassen-Konfiguration für build_class.py (Monk)
# Tracker: nur Features mit Nutzungszahl/Rast, Werte aus dem Feature-Text (5e.tools).
# uses: Zahl | "str"/"dex"/"con"/"int"/"wis"/"cha" (Modifikator, min. 1) | "level" | "pb" | {Stufe: Anzahl} (Anleitung B2)
# Focus Points (Class Table): 2 (L2), 3 (L3) … 20 (L20) = Stufe → uses "level", minLvl 2 aus dem Feature; seit 27.09.2026 Pool-Zähler ('pool': True).
# Ki-/Focus-Kosten einzelner Features (Flurry of Blows, Stunning Strike, …) verbrauchen den Focus-Zähler und haben keinen eigenen Tracker.
CONFIG = {
    'class': 'Monk',
    'trackers': {
        'base': [
            {'feature': "Monk's Focus", 'id': 'mk_focuspoints', 'name': 'Focus Points', 'icon': '☯', 'uses': 'level', 'restore': 'short', 'tag': 'Passiv', 'pool': True},
            # „Once you use this feature, you can't use it again until you finish a Long Rest.\"
            {'feature': 'Uncanny Metabolism', 'id': 'mk_uncannymetabolism', 'icon': '💨', 'uses': 1, 'restore': 'long'},
        ],
        # Way of the Open Hand (PHB, an 2024-Klasse angepasst): „You must finish a long rest before you can use this feature again.\"
        'Way of the Open Hand': [
            {'feature': 'Wholeness of Body', 'id': 'mk_oh_wholeness', 'icon': '🧘', 'uses': 1, 'restore': 'long'},
        ],
        # „a number of times equal to your Wisdom modifier (minimum of once) … regain all expended uses … Long Rest\"
        'Warrior of the Open Hand': [
            {'feature': 'Wholeness of Body', 'id': 'mk_woh_wholeness', 'icon': '🧘', 'uses': 'wis', 'restore': 'long'},
        ],
        'Warrior of Mercy': [
            {'feature': 'Flurry of Healing and Harm', 'id': 'mk_wom_flurry', 'icon': '🩹', 'uses': 'wis', 'restore': 'long'},
            {'feature': 'Hand of Ultimate Mercy', 'id': 'mk_wom_ultimate', 'icon': '✨', 'uses': 1, 'restore': 'long'},
        ],
        'Way of Mercy': [
            {'feature': 'Hand of Ultimate Mercy', 'id': 'mk_wm_ultimate', 'icon': '✨', 'uses': 1, 'restore': 'long'},
        ],
        # Breath of the Dragon / Wings Unfurled: Übungsbonus-mal, Long Rest (ohne Nutzung: 2 ki für eine weitere)
        'Way of the Ascendant Dragon': [
            {'feature': 'Breath of the Dragon', 'id': 'mk_ad_breath', 'icon': '🐉', 'uses': 'pb', 'restore': 'long', 'tag': 'Aktion'},
            {'feature': 'Wings Unfurled', 'id': 'mk_ad_wings', 'icon': '🪽', 'uses': 'pb', 'restore': 'long'},
            {'feature': 'Aspect of the Wyrm', 'id': 'mk_ad_wyrm', 'icon': '🛡', 'uses': 1, 'restore': 'long'},
        ],
    },
    # Werte aus class-monk.json (XPHB): hd, proficiency, startingProficiencies, startingEquipment, multiclassing, page
    'traits': {
        'hd': 'd8',
        'primaryAbility': 'Dexterity and Wisdom',
        'hpLevel1': '8 + Con modifier',
        'hpPerLevel': 'd8 (or 5) + Con modifier',
        'savingThrows': ['Strength', 'Dexterity'],
        'armorTraining': 'None',
        'weaponProficiencies': 'Simple weapons, Martial weapons that have the Light property',
        'toolProficiencies': "One type of Artisan's Tools or Musical Instrument",
        'skillProficiencies': {'count': 2, 'from': ['Acrobatics', 'Athletics', 'History', 'Insight', 'Religion', 'Stealth']},
        'spellcastingAbility': '',
        'startingEquipment': [
            "(A) Spear, 5 Daggers, Artisan's Tools or Musical Instrument (chosen for the tool proficiency), Explorer's Pack, and 11 GP",
            '— or — (B) 50 GP',
        ],
        'multiclassingReq': 'Dexterity 13 and Wisdom 13',
        'multiclassingGains': 'None',
        'source': "PHB'24, page 100",
    },
}
