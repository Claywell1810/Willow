# t14/paladin_config.py — Willow 2014 (Paket T2)
# Divine Sense: „a number of times equal to 1 + your Charisma modifier“, Long Rest → uses '1+cha' (abMaxUses).
# Lay on Hands: „pool of healing power … total number of hit points equal to your paladin level × 5“, Long Rest → Pool level*5.
# Cleansing Touch: „a number of times equal to your Charisma modifier (a minimum of once)“, Long Rest.
# Channel Divinity (Oath of Devotion): „Once you use your Channel Divinity, you must finish a short or long rest to use it again“ → 1, Short Rest.
# Holy Nimbus: „Once you use this feature, you can't use it again until you finish a long rest“ → 1, Long Rest.
CONFIG = {
    'class': 'Paladin',
    'trackers': {
        'base': [
            {'feature': 'Divine Sense', 'id': 'pl_divinesense', 'icon': '👁', 'uses': '1+cha', 'restore': 'long'},
            {'feature': 'Lay on Hands', 'id': 'layonhands', 'icon': '🤲', 'uses': 'level*5', 'restore': 'long', 'pool': True},
            {'feature': 'Cleansing Touch', 'id': 'pl_cleansingtouch', 'icon': '🫧', 'uses': 'cha', 'restore': 'long'},
        ],
        'Oath of Devotion': [
            {'feature': 'Channel Divinity', 'id': 'channeldivinity', 'icon': '✨', 'uses': 1, 'restore': 'short'},
            {'feature': 'Holy Nimbus', 'id': 'dv_holynimbus', 'icon': '☀', 'uses': 1, 'restore': 'long'},
        ],
    },
    # Fighting Style (Protection-Reaktion nur eine Option) und Sacred Oath (Einleitung) → Passiv
    'feature_tags': {'base': {'Fighting Style': 'Passiv', 'Sacred Oath': 'Passiv'}},
}
