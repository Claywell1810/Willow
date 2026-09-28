# Wizard – Neubau mit build_class.py --rebuild (27.09.2026). Traits/Class Table bleiben in der HTML.
# Tracker-ids der handgebauten Fassung (wz_) sind heilig; neue ids ebenfalls mit wz_ + Subklassen-Kürzel.
# School of Conjuration/Enchantment/Necromancy/Transmutation (PHB) → AU-Fassung (Conjurer/Enchanter/Necromancer/Transmuter),
# Bladesinging (TCE) → FRHoF-Fassung (Bladesinger), Regel B6 „Nachdruck-Kette"; Anzeige über SUBCLASS_LABELS.
CONFIG = {
    'class': 'Wizard',
    'feature_tags': {
        'base': {'Spell Mastery': 'Passiv'},
        'Abjurer': {'Arcane Ward': 'Passiv'},
        'Illusionist': {'Improved Illusions': 'Passiv'},
        'School of Necromancy': {'Necromancy Spellbook': 'Passiv'},
        'School of Transmutation': {'Wondrous Alteration': 'Passiv'},
        'Chronurgy Magic': {'Arcane Abeyance': 'Passiv'},
        'Bladesinging': {'Extra Attack': 'Passiv', 'Song of Victory': 'Bonusaktion'},
        'Order of Scribes': {'Master Scrivener': 'Passiv'},
    },
    'trackers': {
        'base': [
            {'feature': 'Arcane Recovery', 'id': 'wz_arcanerecovery', 'icon': '📖', 'uses': 1, 'restore': 'long'},
            {'feature': 'Signature Spells', 'id': 'wz_signaturespells', 'icon': '✨', 'uses': 2, 'restore': 'short', 'tag': 'Aktion'},
        ],
        'Abjurer': [
            {'feature': 'Arcane Ward', 'id': 'wz_aj_arcaneward', 'icon': '🛡️', 'uses': 1, 'restore': 'long'},
        ],
        'Diviner': [
            {'feature': 'Portent', 'id': 'wz_dv_portent', 'icon': '🎲', 'uses': {3: 2, 14: 3}, 'restore': 'long'},
            {'feature': 'The Third Eye', 'id': 'wz_dv_thirdeye', 'icon': '👁️', 'uses': 1, 'restore': 'short'},
        ],
        'School of Divination': [
            {'feature': 'Portent', 'id': 'wz_sd_portent', 'icon': '🎲', 'uses': {3: 2, 14: 3}, 'restore': 'long'},
            {'feature': 'The Third Eye', 'id': 'wz_sd_thirdeye', 'icon': '👁️', 'uses': 1, 'restore': 'short'},
        ],
        'Illusionist': [
            {'feature': 'Illusory Self', 'id': 'wz_il_illusoryself', 'icon': '🎭', 'uses': 1, 'restore': 'short'},
            {'feature': 'Phantasmal Creatures', 'id': 'wz_il_phantasmalcreatures', 'icon': '👻', 'uses': 2, 'restore': 'long', 'tag': 'Aktion'},
        ],
        'School of Illusion': [
            {'feature': 'Illusory Self', 'id': 'wz_si_illusoryself', 'icon': '🎭', 'uses': 1, 'restore': 'short'},
        ],
        'School of Conjuration': [
            {'feature': 'Benign Transposition', 'id': 'wz_sc_benigntransposition', 'icon': '🌀', 'uses': 'int', 'restore': 'long'},
            {'feature': 'Splintered Summons', 'id': 'wz_sc_splinteredsummons', 'icon': '👥', 'uses': 1, 'restore': 'long'},
        ],
        'School of Enchantment': [
            {'feature': 'Hypnotic Presence', 'id': 'wz_se_hypnoticpresence', 'icon': '🌀', 'uses': 'int', 'restore': 'long'},
            {'feature': 'Split Enchantment', 'id': 'wz_se_splitenchantment', 'icon': '💞', 'uses': 'int', 'restore': 'long'},
            {'feature': 'Instinctive Charm', 'id': 'wz_se_instinctivecharm', 'icon': '💘', 'uses': 1, 'restore': 'long'},
        ],
        'School of Necromancy': [
            {'feature': 'Undead Thralls', 'id': 'wz_sn_undeadthralls', 'name': 'Undead Thralls: Animate Dead', 'icon': '💀',
             'uses': 1, 'restore': 'long', 'tag': 'Aktion'},
            {'feature': "Death's Master", 'id': 'wz_sn_deathsmaster', 'icon': '☠️', 'uses': 1, 'restore': 'long'},
        ],
        'School of Transmutation': [
            {'feature': 'Wondrous Alteration', 'id': 'wz_st_wondrousalteration', 'name': 'Wondrous Alteration: Alter Self', 'icon': '🦎',
             'uses': 1, 'restore': 'long', 'tag': 'Aktion'},
            {'feature': 'Empowered Transmutation', 'id': 'wz_st_empoweredtransmutation', 'icon': '⚗️', 'uses': 'int', 'restore': 'long'},
            {'feature': 'Shape-Shifter', 'id': 'wz_st_shapechanger', 'name': 'Shape-Shifter: Polymorph', 'icon': '🐾',
             'uses': 1, 'restore': 'long', 'tag': 'Aktion'},
        ],
        'School of Abjuration': [
            {'feature': 'Arcane Ward', 'id': 'wz_sa_arcaneward', 'icon': '🛡️', 'uses': 1, 'restore': 'long'},
        ],
        'War Magic': [
            {'feature': 'Power Surge', 'id': 'wz_wm_powersurge', 'icon': '⚡', 'uses': 'int', 'restore': 'long'},
        ],
        'Chronurgy Magic': [
            {'feature': 'Chronal Shift', 'id': 'wz_cm_chronalshift', 'icon': '⏳', 'uses': 2, 'restore': 'long'},
            {'feature': 'Momentary Stasis', 'id': 'wz_cm_momentarystasis', 'icon': '⏱️', 'uses': 'int', 'restore': 'long'},
            {'feature': 'Arcane Abeyance', 'id': 'wz_cm_arcaneabeyance', 'icon': '🫧', 'uses': 1, 'restore': 'short'},
        ],
        'Graviturgy Magic': [
            {'feature': 'Violent Attraction', 'id': 'wz_gm_violentattraction', 'icon': '🧲', 'uses': 'int', 'restore': 'long'},
            {'feature': 'Event Horizon', 'id': 'wz_gm_eventhorizon', 'icon': '🕳️', 'uses': 1, 'restore': 'long', 'conc': True},
        ],
        'Bladesinging': [
            {'feature': 'Bladesong', 'id': 'wz_bs_bladesong', 'icon': '🗡️', 'uses': 'int', 'restore': 'long'},
        ],
        'Order of Scribes': [
            {'feature': 'Awakened Spellbook', 'id': 'wz_os_awakenedspellbook', 'icon': '📘', 'uses': 1, 'restore': 'long'},
            {'feature': 'Manifest Mind', 'id': 'wz_os_manifestmind', 'icon': '📜', 'uses': 1, 'restore': 'long'},
            {'feature': 'Manifest Mind', 'id': 'wz_os_mindcasting', 'name': 'Manifest Mind: Spellcasting', 'icon': '📜',
             'uses': 'pb', 'restore': 'long', 'tag': 'Passiv'},
            {'feature': 'One with the Word', 'id': 'wz_os_onewiththeword', 'icon': '📕', 'uses': 1, 'restore': 'long'},
        ],
    },
}
