# t14/wizard_config.py — Willow 2014 (Paket T2)
# Arcane Recovery: „once per day when you finish a short rest“ → 1, Long Rest (Hinweis bei der Short Rest, REST_MANUAL).
# Signature Spells: zwei Zauber je einmal „until you finish a short or long rest“ → 2, Short Rest.
# Overchannel (Evocation): „The first time you do so, you take no adverse effect … until you finish a long rest“ → 1, Long Rest.
CONFIG = {
    'class': 'Wizard',
    'trackers': {
        'base': [
            {'feature': 'Arcane Recovery', 'id': 'wz_arcanerecovery', 'icon': '📖', 'uses': 1, 'restore': 'long'},
            {'feature': 'Signature Spells', 'id': 'wz_signaturespells', 'icon': '✨', 'uses': 2, 'restore': 'short', 'tag': 'Aktion'},
        ],
        'School of Evocation': [
            {'feature': 'Overchannel', 'id': 'wz_ev_overchannel', 'icon': '💥', 'uses': 1, 'restore': 'long'},
        ],
    },
}
