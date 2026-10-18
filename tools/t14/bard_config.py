# t14/bard_config.py — Willow 2014 (Paket T2)
# Bardic Inspiration: „a number of times equal to your Charisma modifier (a minimum of once)“, Long Rest; ab L5 Font of
# Inspiration „when you finish a short or long rest“ (REST_SHORT_FROM bardicinspiration:5 in der App).
CONFIG = {
    'class': 'Bard',
    'trackers': {
        'base': [
            {'feature': 'Bardic Inspiration', 'id': 'bardicinspiration', 'icon': '🎵', 'uses': 'cha', 'restore': 'long',
             'append': ['Font of Inspiration', 'Superior Inspiration']},
            {'feature': 'Jack of All Trades', 'id': 'jackofalltrades', 'icon': '🎲', 'uses': None, 'restore': None},
            {'feature': 'Countercharm', 'id': 'countercharm', 'icon': '🛡', 'uses': None, 'restore': None},
        ],
        'College of Lore': [
            {'feature': 'Cutting Words', 'id': 'cuttingwords', 'icon': '✂', 'uses': None, 'restore': None},
        ],
    },
}
