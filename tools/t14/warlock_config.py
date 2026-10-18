# t14/warlock_config.py — Willow 2014 (Paket T2)
# Pact Magic: Plätze laut Class Table (1 / 2 ab L2 / 3 ab L11 / 4 ab L17), „regain all expended spell slots when you finish a short or long rest“.
# Mystic Arcanum: je Grad 6/7/8/9 „once without expending a spell slot. You must finish a long rest before you can do so again.“
# Eldritch Master: „Once you regain spell slots with this feature, you must finish a long rest before you can do so again.“
# The Fiend: Dark One's Own Luck „can't use it again until you finish a short or long rest“; Hurl Through Hell „until you finish a long rest“.
CONFIG = {
    'class': 'Warlock',
    'trackers': {
        'base': [
            {'feature': 'Pact Magic', 'id': 'wl_pactslots', 'icon': '🔮', 'name': 'Pact Magic Slots', 'uses': {1: 1, 2: 2, 11: 3, 17: 4}, 'restore': 'short'},
            {'feature': 'Mystic Arcanum (6th level)', 'id': 'wl_mysticarcanum', 'icon': '📖', 'name': 'Mystic Arcanum', 'uses': 1, 'restore': 'long',
             'append': ['Mystic Arcanum (7th level)', 'Mystic Arcanum (8th level)', 'Mystic Arcanum (9th level)'],
             'sub': [{'k': '6', 'l': 'Level 6 Spell'}, {'k': '7', 'l': 'Level 7 Spell', 'minLvl': 13}, {'k': '8', 'l': 'Level 8 Spell', 'minLvl': 15}, {'k': '9', 'l': 'Level 9 Spell', 'minLvl': 17}]},
            {'feature': 'Eldritch Master', 'id': 'wl_eldritchmaster', 'icon': '🌙', 'uses': 1, 'restore': 'long'},
        ],
        'The Fiend': [
            {'feature': "Dark One's Own Luck", 'id': 'wl_fi_darkonesownluck', 'icon': '🎲', 'uses': 1, 'restore': 'short'},
            {'feature': 'Hurl Through Hell', 'id': 'wl_fi_hurlthroughhell', 'icon': '🔥', 'uses': 1, 'restore': 'long'},
        ],
    },
    # Pact Boon: Pact of the Chain „use its reaction“ ist nur eine Option → Passiv
    'feature_tags': {'base': {'Pact Boon': 'Passiv'}},
    # Eldritch Invocations: 5e.tools-Text verweist nur auf die Optionsseite → SRD-Invocations (optionalfeatures, Typ EI) anhängen
    'append_optf': {'Eldritch Invocations': 'EI'},
}
