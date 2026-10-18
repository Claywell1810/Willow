# t14/fighter_config.py — Willow 2014 (Paket T2)
# Second Wind: einmal je Short/Long Rest. Action Surge: 1, ab L17 zweimal je Rast (Short Rest). Indomitable: 1/2/3 (L9/13/17), Long Rest.
CONFIG = {
    'class': 'Fighter',
    'trackers': {
        'base': [
            {'feature': 'Second Wind', 'id': 'secondwind', 'icon': '❤', 'uses': 1, 'restore': 'short'},
            {'feature': 'Action Surge', 'id': 'actionsurge', 'icon': '⚡', 'uses': {2: 1, 17: 2}, 'restore': 'short',
             'append': ['Action Surge (two uses)']},
            {'feature': 'Indomitable', 'id': 'indomitable', 'icon': '🛡', 'uses': {9: 1, 13: 2, 17: 3}, 'restore': 'long',
             'append': ['Indomitable (two uses)', 'Indomitable (three uses)']},
        ],
    },
    # Fighting Style: „Protection … use your reaction“ ist nur eine Option → Passiv
    'feature_tags': {'base': {'Fighting Style': 'Passiv'}},
}
