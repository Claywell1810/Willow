# t14/cleric_config.py — Willow 2014 (Paket T2)
# Channel Divinity: „Beginning at 6th level, you can use your Channel Divinity twice between rests, and beginning at 18th level,
# you can use it three times“; „When you finish a short or long rest, you regain your expended uses.“ → 1/2/3, Short Rest (alle).
# Divine Intervention: nach Erfolg 7 Tage, sonst nach einem Long Rest (steht im Text) → 1, Long Rest.
CONFIG = {
    'class': 'Cleric',
    'trackers': {
        'base': [
            {'feature': 'Channel Divinity', 'id': 'channeldivinity', 'icon': '✨', 'uses': {2: 1, 6: 2, 18: 3}, 'restore': 'short'},
            {'feature': 'Divine Intervention', 'id': 'divineintervention', 'icon': '🙏', 'uses': 1, 'restore': 'long',
             'append': ['Divine Intervention Improvement']},
        ],
        'Life Domain': [
            {'feature': 'Channel Divinity: Preserve Life', 'id': 'ld_preservelife', 'icon': '💖', 'uses': None, 'restore': None},
        ],
    },
}
