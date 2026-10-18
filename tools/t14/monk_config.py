# t14/monk_config.py — Willow 2014 (Paket T2)
# Ki: „Your access to this energy is represented by a number of ki points. Your monk level determines the number of points you
# have“; „When you finish a short or long rest, you regain all of your expended ki“ → Pool = Stufe (ab L2), Short Rest.
# Wholeness of Body (Open Hand): „you can't use this feature again until you finish a long rest“ → 1, Long Rest.
CONFIG = {
    'class': 'Monk',
    'trackers': {
        'base': [
            {'feature': 'Ki', 'id': 'mk_ki', 'icon': '☯', 'name': 'Ki Points', 'uses': 'level', 'restore': 'short', 'tag': 'Passiv', 'pool': True},
        ],
        'Way of the Open Hand': [
            {'feature': 'Wholeness of Body', 'id': 'mk_oh_wholeness', 'icon': '🧘', 'uses': 1, 'restore': 'long'},
        ],
    },
}
