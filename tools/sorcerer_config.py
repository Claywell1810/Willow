# sorcerer_config.py — Klassen-Konfiguration für build_class.py (Sorcerer)
# Tracker: nur Features mit Nutzungszahl/Rast, Werte aus dem Feature-Text bzw. der Class Table.
# uses: Zahl | "str"/"dex"/"con"/"int"/"wis"/"cha" (Modifikator, min. 1) | "level" | "pb" | {Stufe: Anzahl} (Anleitung B2)
# Sorcery Points = Stufe (Class Table L2–L20: 2…20), Long Rest; seit 27.09.2026 als Pool-Zähler ('pool': True).
# Einzel-Tracker ('sub', seit 27.09.2026): Lunar Sorcery – Waxing and Waning (je Mondphase ein Gratis-Zauber, 1/Long Rest)
#   und Lunar Phenomenon (je Mondphase 1/Long Rest). Lunar Embodiment zählt nur L3–L5 (ein Zauber der gewählten Phase),
#   ab L6 übernimmt Waxing and Waning („You can now cast one 1st-level spell from each lunar phase …") → uses {3:1, 6:0}.
# Nicht getrackt: Metamagic-Optionen und alles, was nur Sorcery Points kostet (Draconic Presence, Bend Luck, Bastion of Law,
#   Revelation in Flesh, Psionic Sorcery, Beasts of Ill Omen …), Wild Magic Surge (kein Limit), Zauber ohne Slot, die an andere Features hängen.
MOON = [{'k': 'full', 'l': 'Full Moon'}, {'k': 'new', 'l': 'New Moon'}, {'k': 'crescent', 'l': 'Crescent Moon'}]
CONFIG = {
    'class': 'Sorcerer',
    'trackers': {
        'base': [
            {'feature': 'Innate Sorcery', 'id': 'innatesorcery', 'icon': '🔥', 'uses': 2, 'restore': 'long', 'append': ['Sorcery Incarnate']},
            {'feature': 'Font of Magic', 'name': 'Sorcery Points', 'id': 'sorcerypoints', 'icon': '⭐', 'uses': 'level', 'restore': 'long', 'pool': True},
            {'feature': 'Sorcerous Restoration', 'id': 'sorcerousrestoration', 'icon': '🌙', 'uses': 1, 'restore': 'long'},
        ],
        'Wild Magic': [
            {'feature': 'Tides of Chaos', 'id': 'wm_tidesofchaos', 'icon': '🌀', 'uses': 1, 'restore': 'long'},
        ],
        'Draconic Sorcery': [
            {'feature': 'Dragon Wings', 'id': 'ds_dragonwings', 'icon': '🐉', 'uses': 1, 'restore': 'long'},
            {'feature': 'Dragon Companion', 'id': 'ds_dragoncompanion', 'icon': '🐲', 'uses': 1, 'restore': 'long'},
        ],
        'Wild Magic Sorcery': [
            {'feature': 'Tides of Chaos', 'id': 'wms_tidesofchaos', 'icon': '🌀', 'uses': 1, 'restore': 'long'},
            {'feature': 'Tamed Surge', 'id': 'wms_tamedsurge', 'icon': '🎲', 'uses': 1, 'restore': 'long'},
        ],
        'Aberrant Sorcery': [
            {'feature': 'Warping Implosion', 'id': 'as_warpingimplosion', 'icon': '🧠', 'uses': 1, 'restore': 'long'},
        ],
        'Clockwork Sorcery': [
            {'feature': 'Restore Balance', 'id': 'cs_restorebalance', 'icon': '⚙', 'uses': 'cha', 'restore': 'long'},
            {'feature': 'Trance of Order', 'id': 'cs_tranceoforder', 'icon': '📐', 'uses': 1, 'restore': 'long'},
            {'feature': 'Clockwork Cavalcade', 'id': 'cs_clockworkcavalcade', 'icon': '🔧', 'uses': 1, 'restore': 'long'},
        ],
        'Divine Soul': [
            {'feature': 'Favored by the Gods', 'id': 'dv_favoredbythegods', 'icon': '✨', 'uses': 1, 'restore': 'short'},
            {'feature': 'Unearthly Recovery', 'id': 'dv_unearthlyrecovery', 'icon': '💫', 'uses': 1, 'restore': 'long'},
        ],
        'Shadow Magic': [
            {'feature': 'Power of Shadow', 'id': 'sh_powerofshadow', 'icon': '🌑', 'uses': 1, 'restore': 'long'},
            {'feature': 'Umbral Form', 'id': 'sh_umbralform', 'icon': '👤', 'uses': 1, 'restore': 'long'},
        ],
        'Storm Sorcery': [
            {'feature': 'Wind Soul', 'id': 'st_windsoul', 'icon': '🌪', 'uses': 1, 'restore': 'short'},
        ],
        'Aberrant Mind': [
            {'feature': 'Warping Implosion', 'id': 'am_warpingimplosion', 'icon': '🧠', 'uses': 1, 'restore': 'long'},
        ],
        'Clockwork Soul': [
            {'feature': 'Restore Balance', 'id': 'cw_restorebalance', 'icon': '⚙', 'uses': 'pb', 'restore': 'long'},
            {'feature': 'Trance of Order', 'id': 'cw_tranceoforder', 'icon': '📐', 'uses': 1, 'restore': 'long'},
            {'feature': 'Clockwork Cavalcade', 'id': 'cw_clockworkcavalcade', 'icon': '🔧', 'uses': 1, 'restore': 'long'},
        ],
        'Lunar Sorcery': [
            {'feature': 'Lunar Embodiment', 'id': 'lu_lunarembodiment', 'icon': '🌕', 'uses': {3: 1, 6: 0}, 'restore': 'long'},
            {'feature': 'Lunar Boons', 'id': 'lu_lunarboons', 'icon': '🌘', 'uses': 'pb', 'restore': 'long'},
            {'feature': 'Waxing and Waning', 'id': 'lu_waxingwaning', 'icon': '🌗', 'uses': 1, 'restore': 'long', 'sub': MOON},
            {'feature': 'Lunar Phenomenon', 'id': 'lu_lunarphenomenon', 'icon': '🌙', 'uses': 1, 'restore': 'long', 'sub': MOON},
        ],
    },
    # Werte aus class-sorcerer.json (XPHB): hd, proficiency, startingProficiencies, startingEquipment, multiclassing, page
    # Multiclassing PHB'24: 13 im Hauptattribut (primaryAbility: cha); die Quelle nennt keine zusätzlichen Übungen
    'traits': {
        'hd': 'd6',
        'primaryAbility': 'Charisma',
        'hpLevel1': '6 + Con modifier',
        'hpPerLevel': 'd6 (or 4) + Con modifier',
        'savingThrows': ['Constitution', 'Charisma'],
        'armorTraining': 'None',
        'weaponProficiencies': 'Simple weapons',
        'skillProficiencies': {'count': 2, 'from': ['Arcana', 'Deception', 'Insight', 'Intimidation', 'Persuasion', 'Religion']},
        'spellcastingAbility': 'Charisma',
        'startingEquipment': [
            '(A) Spear, 2 Daggers, Arcane Focus (crystal), Dungeoneer\'s Pack, and 28 GP',
            '— or — (B) 50 GP',
        ],
        'multiclassingReq': 'Charisma 13',
        'multiclassingGains': 'None',
        'source': "PHB'24, page 138",
    },
}
