# t14/sorcerer_config.py — Willow 2014 (Paket T2)
# Font of Magic: „You have 2 sorcery points, and you gain more as you reach higher levels, as shown in the Sorcery Points column“
# (= Stufe ab L2), „You regain all spent sorcery points when you finish a long rest“ → Pool level, Long Rest.
# Sorcerous Restoration (L20): 4 Punkte bei jedem Short Rest, ohne Limit → kein Tracker (Text).
CONFIG = {
    'class': 'Sorcerer',
    'trackers': {
        'base': [
            {'feature': 'Font of Magic', 'id': 'sorcerypoints', 'icon': '⭐', 'name': 'Sorcery Points', 'uses': 'level', 'restore': 'long', 'pool': True},
        ],
    },
    # Metamagic: „Quickened Spell … bonus action“ ist nur eine Option → Passiv (alle drei Stufen)
    'feature_tags': {'base': {'Metamagic': 'Passiv'}},
}
