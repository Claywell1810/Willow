# warlock_config.py — Klassen-Konfiguration für build_class.py (Warlock)
# Tracker: nur Features mit Nutzungszahl/Rast, Werte aus dem Feature-Text bzw. der Class Table.
# uses: Zahl | "str"/"dex"/"con"/"int"/"wis"/"cha" (Modifikator, min. 1) | "level" | "pb" | {Stufe: Anzahl} (Anleitung B2)
# conc: True = Konzentrations-Abzeichen „C" am Tracker (nur bei echter Konzentration, B2/B9)
# Pakt-Magie: Slots aus der Class Table (Spalte Spell Slots: L1 1, L2 2, L11 3, L17 4), Short Rest.
#   Slot-Grad steht in der Class Table (Spalte Slot Level), die 9 Zauberplatz-Spalten entfallen (keine rowsSpellProgression).
# Healing Light: Pool = 1 + Warlock-Stufe (Feature ab Stufe 3 in beiden Fassungen) → {3:4 … 20:21}; seit 27.09.2026 Pool-Zähler ('pool': True).
# Mystic Arcanum (seit 27.09.2026, Einzel-Tracker 'sub'): je Zaubergrad 1× pro Long Rest; Grad 6 ab L11, 7 ab L13, 8 ab L15, 9 ab L17 (Feature-Text).
# Nicht getrackt: Eldritch Invocations, Genie's Wrath / Frightful Avatar / Radiant Soul u. ä. (einmal pro Zug), Features ohne Limit.
HEAL = {l: l + 1 for l in range(3, 21)}
ARCANUM = [{'k': '6', 'l': 'Level 6 Spell'}, {'k': '7', 'l': 'Level 7 Spell', 'minLvl': 13},
           {'k': '8', 'l': 'Level 8 Spell', 'minLvl': 15}, {'k': '9', 'l': 'Level 9 Spell', 'minLvl': 17}]
CONFIG = {
    'class': 'Warlock',
    'trackers': {
        'base': [
            {'feature': 'Pact Magic', 'name': 'Pact Magic Slots', 'id': 'wl_pactslots', 'icon': '🔮', 'uses': {1: 1, 2: 2, 11: 3, 17: 4}, 'restore': 'short'},
            {'feature': 'Magical Cunning', 'id': 'wl_magicalcunning', 'icon': '🌙', 'uses': 1, 'restore': 'long', 'append': ['Eldritch Master']},
            {'feature': 'Contact Patron', 'id': 'wl_contactpatron', 'icon': '📜', 'uses': 1, 'restore': 'long'},
            {'feature': 'Mystic Arcanum', 'id': 'wl_mysticarcanum', 'icon': '📖', 'uses': 1, 'restore': 'long', 'sub': ARCANUM},
        ],
        'The Archfey': [
            {'feature': 'Fey Presence', 'id': 'wl_af_feypresence', 'icon': '🧚', 'uses': 1, 'restore': 'short'},
            {'feature': 'Misty Escape', 'id': 'wl_af_mistyescape', 'icon': '🌫', 'uses': 1, 'restore': 'short'},
            {'feature': 'Dark Delirium', 'id': 'wl_af_darkdelirium', 'icon': '🌀', 'uses': 1, 'restore': 'short', 'conc': True},
        ],
        'The Fiend': [
            {'feature': "Dark One's Own Luck", 'id': 'wl_fi_darkonesownluck', 'icon': '🎲', 'uses': 1, 'restore': 'short'},
            {'feature': 'Hurl Through Hell', 'id': 'wl_fi_hurlthroughhell', 'icon': '🔥', 'uses': 1, 'restore': 'long'},
        ],
        'The Great Old One': [
            {'feature': 'Entropic Ward', 'id': 'wl_go_entropicward', 'icon': '🛡', 'uses': 1, 'restore': 'short'},
        ],
        'Archfey Patron': [
            {'feature': 'Steps of the Fey', 'id': 'wl_afp_stepsofthefey', 'icon': '🧚', 'uses': 'cha', 'restore': 'long'},
            {'feature': 'Beguiling Defenses', 'id': 'wl_afp_beguilingdefenses', 'icon': '🛡', 'uses': 1, 'restore': 'long'},
        ],
        'Fiend Patron': [
            {'feature': "Dark One's Own Luck", 'id': 'wl_fip_darkonesownluck', 'icon': '🎲', 'uses': 'cha', 'restore': 'long'},
            {'feature': 'Hurl Through Hell', 'id': 'wl_fip_hurlthroughhell', 'icon': '🔥', 'uses': 1, 'restore': 'long'},
        ],
        'Great Old One Patron': [
            {'feature': 'Clairvoyant Combatant', 'id': 'wl_gop_clairvoyantcombatant', 'icon': '👁', 'uses': 1, 'restore': 'short'},
        ],
        'Celestial Patron': [
            {'feature': 'Healing Light', 'id': 'wl_cep_healinglight', 'icon': '✨', 'uses': HEAL, 'restore': 'long', 'pool': True},
            {'feature': 'Searing Vengeance', 'id': 'wl_cep_searingvengeance', 'icon': '☀', 'uses': 1, 'restore': 'long'},
        ],
        'The Undying': [
            {'feature': 'Defy Death', 'id': 'wl_un_defydeath', 'icon': '💀', 'uses': 1, 'restore': 'long'},
            {'feature': 'Indestructible Life', 'id': 'wl_un_indestructiblelife', 'icon': '❤', 'uses': 1, 'restore': 'short'},
        ],
        'The Celestial': [
            {'feature': 'Healing Light', 'id': 'wl_ce_healinglight', 'icon': '✨', 'uses': HEAL, 'restore': 'long', 'pool': True},
            {'feature': 'Searing Vengeance', 'id': 'wl_ce_searingvengeance', 'icon': '☀', 'uses': 1, 'restore': 'long'},
        ],
        'The Hexblade': [
            {'feature': "Hexblade's Curse", 'id': 'wl_hb_hexbladescurse', 'icon': '🗡', 'uses': 1, 'restore': 'short'},
            {'feature': 'Accursed Specter', 'id': 'wl_hb_accursedspecter', 'icon': '👻', 'uses': 1, 'restore': 'long'},
        ],
        'The Fathomless': [
            {'feature': 'Tentacle of the Deeps', 'id': 'wl_fa_tentacleofthedeeps', 'icon': '🐙', 'uses': 'pb', 'restore': 'long'},
            {'feature': 'Grasping Tentacles', 'id': 'wl_fa_graspingtentacles', 'icon': '🌊', 'uses': 1, 'restore': 'long', 'conc': True},
            {'feature': 'Fathomless Plunge', 'id': 'wl_fa_fathomlessplunge', 'icon': '💧', 'uses': 1, 'restore': 'short'},
        ],
        'The Genie': [
            {'feature': "Genie's Vessel", 'name': 'Bottled Respite', 'id': 'wl_ge_bottledrespite', 'icon': '🏺', 'uses': 1, 'restore': 'long'},
            {'feature': 'Elemental Gift', 'id': 'wl_ge_elementalgift', 'icon': '🌬', 'uses': 'pb', 'restore': 'long'},
            {'feature': 'Limited Wish', 'id': 'wl_ge_limitedwish', 'icon': '⭐', 'uses': 1, 'restore': 'long'},
        ],
        'The Undead': [
            {'feature': 'Form of Dread', 'id': 'wl_ud_formofdread', 'icon': '💀', 'uses': 'cha', 'restore': 'long'},
            {'feature': 'Necrotic Husk', 'name': 'Unholy Resuscitation', 'id': 'wl_ud_unholyresuscitation', 'icon': '⚰', 'uses': 1, 'restore': 'short'},
        ],
    },
    # Anzeige-Tag einzelner Features überschreiben (seit 27.09.2026, Fixliste): Die Heuristik trifft Text einzelner Invocations
    # bzw. den Auslöser „Zauber mit einer Aktion\".
    'feature_tags': {
        'base': {'Eldritch Invocation Options': 'Passiv'},
        'Archfey Patron': {'Bewitching Magic': 'Passiv'},
    },
    # Werte aus class-warlock.json (XPHB): hd, proficiency, startingProficiencies, startingEquipment, multiclassing, page
    # Multiclassing PHB'24: 13 im Hauptattribut (primaryAbility: cha); Gains aus multiclassing.proficienciesGained (armor light)
    'traits': {
        'hd': 'd8',
        'primaryAbility': 'Charisma',
        'hpLevel1': '8 + Con modifier',
        'hpPerLevel': 'd8 (or 5) + Con modifier',
        'savingThrows': ['Wisdom', 'Charisma'],
        'armorTraining': 'Light armor',
        'weaponProficiencies': 'Simple weapons',
        'skillProficiencies': {'count': 2, 'from': ['Arcana', 'Deception', 'History', 'Intimidation', 'Investigation', 'Nature', 'Religion']},
        'spellcastingAbility': 'Charisma',
        'startingEquipment': [
            '(A) Leather Armor, Sickle, 2 Daggers, Arcane Focus (orb), Book (occult lore), Scholar\'s Pack, and 15 GP',
            '— or — (B) 100 GP',
        ],
        'multiclassingReq': 'Charisma 13',
        'multiclassingGains': 'Light armor',
        'source': "PHB'24, page 152",
    },
}
