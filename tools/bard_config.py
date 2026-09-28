# Bard – Neubau mit build_class.py --rebuild (27.09.2026). Traits/Class Table bleiben in der HTML.
# Tracker-ids der handgebauten Fassung sind heilig; neue ids mit Präfix bd_.
# uses:null = verbraucht Bardic Inspiration (kein eigener Zähler, B6).
CONFIG = {
    'class': 'Bard',
    'feature_tags': {
        'College of Valor': {'Combat Inspiration': 'Passiv', 'Extra Attack': 'Passiv', 'Battle Magic': 'Bonusaktion'},
        'College of Dance': {'Dazzling Footwork': 'Passiv'},
        'College of Swords': {'Blade Flourish': 'Passiv'},
    },
    'trackers': {
        'base': [
            {'feature': 'Bardic Inspiration', 'id': 'bardicinspiration', 'icon': '🎵', 'uses': 'cha', 'restore': 'short',
             'append': ['Font of Inspiration', 'Superior Inspiration']},
            {'feature': 'Jack of All Trades', 'id': 'jackofalltrades', 'icon': '🎲', 'uses': None, 'restore': None},
            {'feature': 'Countercharm', 'id': 'countercharm', 'icon': '🛡', 'uses': None, 'restore': None},
        ],
        'College of Lore': [
            {'feature': 'Cutting Words', 'id': 'cuttingwords', 'icon': '✂', 'uses': None, 'restore': None},
        ],
        'College of Glamour': [
            {'feature': 'Beguiling Magic', 'id': 'bd_gl_beguilingmagic', 'icon': '💫', 'uses': 1, 'restore': 'long'},
            {'feature': 'Mantle of Inspiration', 'id': 'mantleofinspiration', 'icon': '✨', 'uses': None, 'restore': None},
            {'feature': 'Mantle of Majesty', 'id': 'mantleofmajesty', 'icon': '👑', 'uses': 1, 'restore': 'long', 'conc': True},
            {'feature': 'Unbreakable Majesty', 'id': 'unbreakablemajesty', 'icon': '🌟', 'uses': 1, 'restore': 'short'},
        ],
        'College of Swords': [
            {'feature': 'Blade Flourish', 'id': 'bladeflourish', 'icon': '⚔', 'uses': None, 'restore': None},
        ],
        'College of Whispers': [
            {'feature': 'Psychic Blades', 'id': 'psychicblades', 'icon': '🔪', 'uses': None, 'restore': None},
            {'feature': 'Words of Terror', 'id': 'bd_wh_wordsofterror', 'icon': '🗣', 'uses': 1, 'restore': 'short'},
            {'feature': 'Mantle of Whispers', 'id': 'mantleofwhispers', 'icon': '👤', 'uses': 1, 'restore': 'short'},
            {'feature': 'Shadow Lore', 'id': 'shadowlore', 'icon': '🌑', 'uses': 1, 'restore': 'long'},
        ],
        'College of Creation': [
            {'feature': 'Performance of Creation', 'id': 'performanceofcreation', 'icon': '🎨', 'uses': 1, 'restore': 'long'},
            {'feature': 'Animating Performance', 'id': 'animatingperformance', 'icon': '💃', 'uses': 1, 'restore': 'long'},
        ],
        'College of Eloquence': [
            {'feature': 'Unsettling Words', 'id': 'unsettlingwords', 'icon': '💬', 'uses': None, 'restore': None},
            {'feature': 'Infectious Inspiration', 'id': 'infectiousinspiration', 'icon': '💡', 'uses': 'cha', 'restore': 'long'},
        ],
        'College of Spirits': [  # RHW-Fassung: Tales from Beyond → Spirits from Beyond, Spirit Session → Spiritual Manifestation
            {'feature': 'Spirits from Beyond', 'id': 'talesfrombeyond', 'icon': '👻', 'uses': None, 'restore': None},
            {'feature': 'Empowered Channeling', 'id': 'spiritsession', 'name': 'Spiritual Manifestation', 'icon': '🕯',
             'uses': 1, 'restore': 'long', 'tag': 'Aktion'},
        ],
    },
}
