# tools/t14 – Datenblöcke für Willow 2014 (Paket T)

Je Datenblock eine Datei `<BLOCK>.js` mit genau einer Zeile `const <BLOCK>=…;` (2014-Fassung, nur SRD 5.1 aus `5etools-2014-src`).
`tools/build_2014.py` ersetzt damit beim Bauen die gleichnamige Zeile der 2024-App und schreibt `2014/index.html`.
Erzeugt werden die Dateien einmal von den Konvertern mit `--t14` (ab Paket T2), neu nur nach A12-Muster – nicht bei jeder Veröffentlichung.
Mehrzeilige 2024-Blöcke (CLASS_TABLES …) ersetzt der Build ebenso; `CLASS_DATA.js` ersetzt zusätzlich alle `CLASS_DATA["…"]=`-Anweisungen.

Stand T2 (18.10.2026): Klassen – `CLASS_DATA`, `CLASS_TABLES`, `CLASS_CORE_TRAITS`, `SUBCLASS_LABELS`, `FEATURE_PICKS`, `SUBCLASS_SPELLS`, `CLASS_SPELL_EXTRA`, `ALWAYS_PREP`, `CLASS_MC_GAINS`, `MC_SLOTS`, `SUBCLASS_TABLES`, `FEATURE_STATBLOCKS`. Neu erzeugen: `bash willow/tools/t14_klassen.sh`.
`<k>_config.py` = Klassen-Configs 2014 für `build_class.py --t14` (Tracker aus dem PHB-Text, `feature_tags`, `special`, `append_optf`).
Übrige Blöcke (Zauber, Bestien, Rassen, Backgrounds, Feats, Items, Zustände, Aktionen) noch 2024 → T3–T5.
