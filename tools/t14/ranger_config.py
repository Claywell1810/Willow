# t14/ranger_config.py — Willow 2014 (Paket T2): keine Features mit Nutzungszahl (Primeval Awareness kostet Zauberplätze).
CONFIG = {
    'class': 'Ranger',
    'trackers': {},
    # Hunter's Prey: nur Giant Killer nutzt die Reaktion → Passiv
    'feature_tags': {'Hunter': {"Hunter's Prey": 'Passiv'}},
}
