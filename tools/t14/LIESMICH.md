# tools/t14 – Datenblöcke für Willow 2014 (Paket T)

Je Datenblock eine Datei `<BLOCK>.js` mit genau einer Zeile `const <BLOCK>=…;` (2014-Fassung, nur SRD 5.1 aus `5etools-2014-src`).
`tools/build_2014.py` ersetzt damit beim Bauen die gleichnamige Zeile der 2024-App und schreibt `2014/index.html`.
Erzeugt werden die Dateien einmal von den Konvertern mit `--t14` (ab Paket T2), neu nur nach A12-Muster – nicht bei jeder Veröffentlichung.
Stand T1 (18.10.2026): noch leer → Willow 2014 läuft mit den 2024-Daten.
