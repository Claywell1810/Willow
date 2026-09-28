# Druid – Neubau mit build_class.py --rebuild (27.09.2026). Traits/Class Table bleiben in der HTML, special ["beasts"] bleibt.
# Tracker-ids der handgebauten Fassung sind heilig; neue ids mit Präfix dr_.
# uses:null = verbraucht Wild Shape (kein eigener Zähler, B6). Subklassen-Keys mit Kürzel bleiben (keep_keys).
# 'pool': True = Pool-Zähler (Zahlenfeld mit Maximum statt Pips), seit 27.09.2026 für Balm of the Summer Court (d6-Pool = Stufe).
CONFIG = {
    'class': 'Druid',
    'trackers': {
        'base': [
            {'feature': 'Wild Shape', 'id': 'wildshape', 'icon': '🐺', 'uses': {2: 2, 6: 3, 17: 4}, 'restore': 'short'},
            {'feature': 'Wild Companion', 'id': 'wildcompanion', 'icon': '🦊', 'uses': None, 'restore': None},
            {'feature': 'Wild Resurgence', 'id': 'wildresurgence_ws', 'name': 'Wild Resurgence → Spell Slot', 'icon': '🔄',
             'uses': 1, 'restore': 'long'},
            {'feature': 'Archdruid', 'id': 'dr_naturemagician', 'name': 'Nature Magician', 'icon': '🌌', 'uses': 1, 'restore': 'long'},
        ],
        'Circle of the Land': [
            {'feature': "Land's Aid", 'id': 'landsaid', 'icon': '🌿', 'uses': None, 'restore': None},
            {'feature': 'Natural Recovery', 'id': 'naturalrecovery', 'icon': '🍃', 'uses': 1, 'restore': 'long'},
            {'feature': "Nature's Sanctuary", 'id': 'naturessanctuary', 'icon': '🌳', 'uses': None, 'restore': None},
        ],
        'Circle of the Moon': [
            {'feature': 'Moonlight Step', 'id': 'moonlightstep', 'icon': '🌙', 'uses': 'wis', 'restore': 'long'},
        ],
        'Circle of the Sea': [
            {'feature': 'Wrath of the Sea', 'id': 'wrathofthesea', 'icon': '🌊', 'uses': None, 'restore': None},
        ],
        'Circle of the Stars': [
            {'feature': 'Star Map', 'id': 'dr_st_starmap', 'name': 'Star Map: Guiding Bolt', 'icon': '🗺', 'uses': 'wis',
             'restore': 'long', 'tag': 'Aktion'},
            {'feature': 'Starry Form', 'id': 'starryform', 'icon': '⭐', 'uses': None, 'restore': None},
            {'feature': 'Cosmic Omen', 'id': 'cosmicomen', 'icon': '🔮', 'uses': 'wis', 'restore': 'long'},
        ],
        'Circle of Dreams': [
            {'feature': 'Balm of the Summer Court', 'id': 'balmsc', 'icon': '🌸', 'uses': 'level', 'restore': 'long', 'pool': True},
            {'feature': 'Hidden Paths', 'id': 'hiddenpaths', 'icon': '🌀', 'uses': 'wis', 'restore': 'long'},
            {'feature': 'Walker in Dreams', 'id': 'dr_dm_walkerindreams', 'icon': '💤', 'uses': 1, 'restore': 'long'},
        ],
        'Circle of the Shepherd': [
            {'feature': 'Spirit Totem', 'id': 'spirittotem', 'icon': '🦅', 'uses': 1, 'restore': 'short'},
            {'feature': 'Faithful Summons', 'id': 'fungalinfestation2', 'icon': '🐾', 'uses': 1, 'restore': 'long'},
        ],
        'Circle of Spores': [
            {'feature': 'Halo of Spores', 'id': 'haloofspores', 'icon': '🍄', 'uses': None, 'restore': None},
            {'feature': 'Symbiotic Entity', 'id': 'symbioticent', 'icon': '🌑', 'uses': None, 'restore': None},
            {'feature': 'Spreading Spores', 'id': 'spreadingspores', 'icon': '💨', 'uses': None, 'restore': None},
            {'feature': 'Fungal Infestation', 'id': 'fungalinfestation', 'icon': '☠', 'uses': 'wis', 'restore': 'long'},
        ],
        'Circle of Wildfire': [
            {'feature': 'Summon Wildfire Spirit', 'id': 'summonwildfire', 'icon': '🔥', 'uses': None, 'restore': None},
            {'feature': 'Cauterizing Flames', 'id': 'cauterizingflames', 'icon': '🕯', 'uses': 'pb', 'restore': 'long'},
            {'feature': 'Blazing Revival', 'id': 'blazingrevival', 'icon': '🌋', 'uses': 1, 'restore': 'long'},
        ],
    },
}
