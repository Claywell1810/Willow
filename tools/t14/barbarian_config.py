# t14/barbarian_config.py — Willow 2014 (Paket T2): Tracker aus dem Feature-Text der PHB-Fassung (5etools-2014-src, nur SRD)
# Rages (Class Table): 2 (L1), 3 (L3), 4 (L6), 5 (L12), 6 (L17), „Unlimited“ (L20, steht im Text); „Once you have raged the
# number of times shown … you must finish a long rest before you can rage again.“ → Long Rest, kein Short-Rest-Rückgewinn.
# Paket AA1 (19.10.2026): L20 'unl' = unbegrenzt (abMaxUses liefert 'unl', Actions-Tab zeigt „Unlimited“ statt Kreisen).
# Path of the Berserker: Intimidating Presence ohne Tageslimit (nur 24 h je Ziel) → kein Tracker.
CONFIG = {
    'class': 'Barbarian',
    'trackers': {
        'base': [
            {'feature': 'Rage', 'id': 'bb_rage', 'icon': '🔥', 'uses': {'1': 2, '3': 3, '6': 4, '12': 5, '17': 6, '20': 'unl'}, 'restore': 'long'},
        ],
    },
}
