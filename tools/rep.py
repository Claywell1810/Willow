#!/usr/bin/env python3
"""rep.py – gezielte Ersetzungen mit Eindeutigkeitsprüfung (seit 01.10.2026, Anleitung B1a Schritt 3)

Ersetzt die inline geschriebene rep()-Funktion (und damit den `s=s`-Fallstrick aus B9).
Alles-oder-nichts: Passt ein Anker nicht, wird gar nichts geschrieben.

1) Als Kommando mit Patch-Datei (Python-Datei mit einer Liste ERSETZ):
     python3 willow/tools/rep.py DnD_Character_App.html patch.py [--dry]
   patch.py:
     ERSETZ = [
         ('ALTER TEXT', 'NEUER TEXT'),
         (r'''mehrzeilig
     alt''', r'''mehrzeilig
     neu'''),
         ('kommt 3x vor', 'neu', 3),      # dritter Wert = erwartete Anzahl, ersetzt alle
     ]

2) Als Modul in eigenen Skripten (z. B. wenn Ersetzungen berechnet werden):
     import sys; sys.path.insert(0, 'willow/tools'); from rep import Datei
     d = Datei('DnD_Character_App.html')
     d.rep('ALT', 'NEU')                 # Anker muss genau 1x vorkommen
     d.rep('ALT2', 'NEU2', n=2)          # oder genau n-mal
     d.s                                  # aktueller Text (für index()/Blöcke verschieben)
     d.save()                             # schreibt nur, wenn sich etwas geändert hat
   Mit Datei(p, dry=True) wird nichts geschrieben, nur angezeigt.

Ausgabe je Ersetzung: Zeile des Ankers und Anfang des neuen Texts, am Ende die Größenänderung.
"""
import sys


def _kurz(t, n=90):
    t = t.replace('\n', '⏎')
    return t if len(t) <= n else t[:n] + '…'


class AnkerFehler(Exception):
    pass


class Datei:
    def __init__(self, pfad, dry=False, leise=False):
        self.pfad, self.dry, self.leise = pfad, dry, leise
        with open(pfad, encoding='utf-8') as f:
            self.orig = f.read()
        self.s = self.orig
        self.anzahl = 0

    def rep(self, alt, neu, n=1):
        if alt == neu:
            raise AnkerFehler(f'alt == neu: {_kurz(alt)!r}')
        k = self.s.count(alt)
        if k != n:
            raise AnkerFehler(f'Anker {k}x gefunden (erwartet {n}x): {_kurz(alt)!r}')
        zeile = self.s.count('\n', 0, self.s.index(alt)) + 1
        self.s = self.s.replace(alt, neu)
        self.anzahl += 1
        if not self.leise:
            print(f'  ✔ Z.{zeile}{f" ({n}x)" if n != 1 else ""}: {_kurz(alt, 60)!r} → {_kurz(neu, 60)!r}')

    def save(self):
        diff = len(self.s.encode('utf-8')) - len(self.orig.encode('utf-8'))
        if self.s == self.orig:
            print(f'{self.pfad}: keine Änderung')
            return False
        if self.pfad.endswith('.html') and not self.s.rstrip().endswith('</html>'):
            raise AnkerFehler('Ergebnis endet nicht mit </html> – nichts geschrieben')
        if self.dry:
            print(f'{self.pfad}: TROCKENLAUF, {self.anzahl} Ersetzung(en), {diff:+d} Bytes – nichts geschrieben')
            return False
        with open(self.pfad, 'w', encoding='utf-8') as f:
            f.write(self.s)
        print(f'{self.pfad}: {self.anzahl} Ersetzung(en) geschrieben, {diff:+d} Bytes')
        return True


def main(argv):
    args = [a for a in argv if a != '--dry']
    if len(args) != 2:
        print(__doc__)
        return 2
    pfad, patch = args
    ns = {}
    with open(patch, encoding='utf-8') as f:
        exec(compile(f.read(), patch, 'exec'), ns)
    liste = ns.get('ERSETZ')
    if not isinstance(liste, list) or not liste:
        print(f'{patch}: keine Liste ERSETZ gefunden')
        return 2
    d = Datei(pfad, dry='--dry' in argv)
    try:
        for e in liste:
            d.rep(*e)
        d.save()
    except AnkerFehler as ex:
        print(f'  ✘ {ex}\nABBRUCH: nichts geschrieben.')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
