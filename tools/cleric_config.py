# cleric_config.py — Klassen-Konfiguration für build_class.py (Cleric)
# Tracker: nur Features mit Nutzungszahl/Rast oder Channel-Divinity-Verbrauch (Werte aus dem Feature-Text).
# uses: Zahl | "wis" | "cha" | "level" | "pb" (Übungsbonus) | {Stufe: Anzahl} (je Stufe, s. Anleitung B2)
CD = {'uses': None, 'restore': None}  # verbraucht Channel Divinity → kein eigener Zähler
CONFIG = {
    'class': 'Cleric',
    'trackers': {
        'base': [
            {'feature': 'Channel Divinity', 'id': 'channeldivinity', 'icon': '✨', 'uses': {2: 2, 6: 3, 18: 4}, 'restore': 'short'},
            {'feature': 'Divine Intervention', 'id': 'divineintervention', 'icon': '🙏', 'uses': 1, 'restore': 'long', 'append': ['Greater Divine Intervention']},
        ],
        'Knowledge Domain': [
            {'feature': 'Mind Magic', 'id': 'kd_mindmagic', 'icon': '🧠', **CD},
            {'feature': 'Divine Foreknowledge', 'id': 'kd_divineforeknowledge', 'icon': '🔮', 'uses': 1, 'restore': 'long'},
        ],
        'Life Domain': [
            {'feature': 'Preserve Life', 'id': 'ld_preservelife', 'icon': '💖', **CD},
        ],
        'Light Domain': [
            {'feature': 'Radiance of the Dawn', 'id': 'lt_radiancedawn', 'icon': '🌅', **CD},
            {'feature': 'Warding Flare', 'id': 'lt_wardingflare', 'icon': '💥', 'uses': 'wis', 'restore': 'long', 'append': ['Improved Warding Flare']},
            {'feature': 'Corona of Light', 'id': 'lt_coronaoflight', 'icon': '☀', 'uses': 'wis', 'restore': 'long'},
        ],
        'Nature Domain': [
            {'feature': 'Channel Divinity: Charm Animals and Plants', 'id': 'nd_charmanimals', 'icon': '🌿', **CD},
        ],
        'Tempest Domain': [
            {'feature': 'Wrath of the Storm', 'id': 'td_wrathofstorm', 'icon': '⚡', 'uses': 'wis', 'restore': 'long'},
            {'feature': 'Channel Divinity: Destructive Wrath', 'id': 'td_destructivewrath', 'icon': '🌩', **CD},
        ],
        'Trickery Domain': [
            {'feature': 'Invoke Duplicity', 'id': 'tr_invokeduplicity', 'icon': '🎭', **CD},
        ],
        'War Domain': [
            {'feature': 'War Priest', 'id': 'wd_warpriest', 'icon': '⚔', 'uses': 'wis', 'restore': 'short'},
            {'feature': 'Guided Strike', 'id': 'wd_guidedstrike', 'icon': '🎯', **CD},
        ],
        'Death Domain': [
            {'feature': 'Channel Divinity: Touch of Death', 'id': 'dd_touchofdeath', 'icon': '💀', **CD},
        ],
        'Arcana Domain': [
            {'feature': 'Modify Magic', 'id': 'ad_modifymagic', 'icon': '🔯', **CD},
            {'feature': 'Dispelling Recovery', 'id': 'ad_dispellingrecovery', 'icon': '🌀', 'uses': 1, 'restore': 'short'},
        ],
        'Forge Domain': [
            {'feature': 'Blessing of the Forge', 'id': 'fd_blessingforge', 'icon': '🔨', 'uses': 1, 'restore': 'long'},
            {'feature': "Channel Divinity: Artisan's Blessing", 'id': 'fd_artisansblessing', 'icon': '⚒', **CD},
        ],
        'Grave Domain': [
            {'feature': 'Path to the Grave', 'id': 'gd_pathtograve', 'icon': '⚰', **CD},
            {'feature': "Sentinel at Death's Door", 'id': 'gd_sentinel', 'icon': '🛡', 'uses': 'wis', 'restore': 'long'},
            {'feature': 'Divine Reaper', 'id': 'gd_divinereaper', 'icon': '☠', 'uses': 1, 'restore': 'short'},
        ],
        'Order Domain': [
            {'feature': "Channel Divinity: Order's Demand", 'id': 'od_ordersdemand', 'icon': '⚖', **CD},
            {'feature': 'Embodiment of the Law', 'id': 'od_embodimentlaw', 'icon': '📜', 'uses': 'wis', 'restore': 'long'},
        ],
        'Peace Domain': [
            {'feature': 'Emboldening Bond', 'id': 'pd_emboldeningbond', 'icon': '🤝', 'uses': 'pb', 'restore': 'long'},
            {'feature': 'Channel Divinity: Balm of Peace', 'id': 'pd_balmofpeace', 'icon': '🕊', **CD},
        ],
        'Twilight Domain': [
            {'feature': 'Eyes of Night', 'id': 'tw_eyesofnight', 'icon': '👁', 'uses': 1, 'restore': 'long'},
            {'feature': 'Channel Divinity: Twilight Sanctuary', 'id': 'tw_twilightsanctuary', 'icon': '🌆', **CD},
            {'feature': 'Steps of Night', 'id': 'tw_stepsofnight', 'icon': '🌘', 'uses': 'pb', 'restore': 'long'},
        ],
    },
    # Werte aus class-cleric.json (XPHB): hd, proficiency, startingProficiencies, startingEquipment, multiclassing, page
    'traits': {
        'hd': 'd8',
        'primaryAbility': 'Wisdom',
        'hpLevel1': '8 + Con modifier',
        'hpPerLevel': 'd8 (or 5) + Con modifier',
        'savingThrows': ['Wisdom', 'Charisma'],
        'armorTraining': 'Light armor, Medium armor, Shields',
        'weaponProficiencies': 'Simple weapons',
        'skillProficiencies': {'count': 2, 'from': ['History', 'Insight', 'Medicine', 'Persuasion', 'Religion']},
        'spellcastingAbility': 'Wisdom',
        'startingEquipment': [
            "(A) Chain Shirt, Shield, Mace, Holy Symbol, Priest's Pack, and 7 GP",
            '— or — 110 GP',
        ],
        'multiclassingReq': 'Wisdom 13',
        'multiclassingGains': 'Light armor, Medium armor, Shields',
        'source': "PHB'24, page 68",
    },
}
