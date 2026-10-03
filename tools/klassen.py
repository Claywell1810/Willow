#!/usr/bin/env python3
"""klassen.py – Klassenliste der App an EINER Stelle (Paket N, 03.10.2026).

Statt fester Listen in Skripten (früher je Skript „13 Klassen“) lesen alle Skripte die Klassen
aus der App: jede Zeile `CLASS_DATA["<Klasse>"]={` in der HTML ist eine Klasse.
Eine neue Klasse braucht dafür nur ihren Stub (`build_class.py … --stub`, Anleitung A4).

  from klassen import app_classes, sub_proposal
  app_classes('DnD_Character_App.html')  → ['Artificer', 'Barbarian', …] (alphabetisch)
  python3 willow/tools/klassen.py [DnD_Character_App.html] [--lower]   → Liste für setup.sh
"""
import re, sys


def app_classes(html='DnD_Character_App.html'):
    s = open(html, encoding='utf-8').read() if not html.lstrip().startswith('<') else html
    return sorted(set(re.findall(r'^CLASS_DATA\["([^"]+)"\]=\{', s, re.M)))


def sub_proposal(data, main):
    """Vorschlag für subclassList einer NEUEN Klasse: Subklassen der maßgeblichen Fassung (classSource = Quelle
    der Klasse), ohne Nachdrucke (`reprintedAs`), als „Name (QUELLE)“ in 5e.tools-Reihenfolge.
    Namen sind danach heilig (Savegames) – vor dem Schreiben prüfen."""
    out = []
    for s in data.get('subclass', []):
        if s.get('className') != main['name'] or s.get('classSource') != main['source'] or s.get('reprintedAs'):
            continue
        n = f"{s['name']} ({s['source']})"
        if n not in out: out.append(n)
    return out


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    c = app_classes(a[0] if a else 'DnD_Character_App.html')
    print(' '.join(x.lower() for x in c) if '--lower' in sys.argv else ' '.join(c))
