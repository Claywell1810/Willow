# t14/druid_config.py — Willow 2014 (Paket T2)
# Wild Shape: „You can use this feature twice. You regain expended uses when you finish a short or long rest.“ → 2, Short Rest (alle).
# Natural Recovery (Circle of the Land): „You can't use this feature again until you finish a long rest.“ → 1, Long Rest.
CONFIG = {
    'class': 'Druid',
    'special': ['beasts'],   # Beasts-Tab (Wild Shape; 2014-Bestien und CR-Grenzen ab Paket T3)
    'trackers': {
        'base': [
            {'feature': 'Wild Shape', 'id': 'wildshape', 'icon': '🐺', 'uses': 2, 'restore': 'short'},
        ],
        'Circle of the Land': [
            {'feature': 'Natural Recovery', 'id': 'naturalrecovery', 'icon': '🍃', 'uses': 1, 'restore': 'long'},
        ],
    },
}
