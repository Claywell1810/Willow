#!/bin/bash
# t14_zauber.sh – Willow 2014: Zauber- und Bestien-Datenblöcke neu erzeugen (Paket T3, 18.10.2026; REFERENZ B30)
# Aufruf (aus dem Ordner ÜBER dem Klon, nach `bash willow/tools/setup.sh t14 zauber`):
#   bash willow/tools/t14_zauber.sh
# Reihenfolge (jeder Schritt liest den 2014-Build des vorigen):
#   1. spell_merge.py --t14          → tools/t14/ZB_SPELLS (319 SRD-Zauber, PHB-Texte, SRD-Namen), CLASS_SPELL_MAP ({})
#   2. spell_cats.py --t14           → tools/t14/SPELL_CATS (Kategorien wie Willow 2024, über PHB-Namen; braucht src/ für XPHB)
#   3. spell_rolls.py --t14          → tools/t14/SPELL_ROLLS (Würfel aus der PHB-Fassung)
#   4. bst_convert.py spells --t14   → tools/t14/SPELL_STATBLOCKS (nur SRD-Kreaturen aus bestiary-mm.json)
#   5. bst_convert.py bst --t14      → tools/t14/BST_DATA (96 SRD-Bestien MM 2014; Wild Shape 2014 = Filter im Beasts-Tab)
#   Danach: Build 2014/ (Arbeits-Build) und app_check.js --rules 2014.
set -e
W="$(cd "$(dirname "$0")/.." && pwd)"; A="$(dirname "$W")"; cd "$A"
[ -d src14 ] || { echo "src14/ fehlt: erst bash willow/tools/setup.sh t14 zauber"; exit 1; }
[ -d src ] || { echo "src/ fehlt (XPHB-Zauber für spell_cats.py): erst bash willow/tools/setup.sh t14 zauber"; exit 1; }
B() { python3 "$W/tools/build_2014.py" DnD_Character_App.html --out 2014 >/dev/null; }
B; python3 "$W/tools/spell_merge.py" 2014/index.html src14 --t14 | tail -3
B; python3 "$W/tools/spell_cats.py" 2014/index.html src14 --t14 | tail -2
python3 "$W/tools/spell_rolls.py" 2014/index.html src14 --t14 --write | tail -1
python3 "$W/tools/bst_convert.py" spells 2014/index.html src14 --t14 --write | tail -1
python3 "$W/tools/bst_convert.py" bst 2014/index.html src14 --t14 --write | tail -1
python3 "$W/tools/build_2014.py" DnD_Character_App.html --out 2014
echo "== Prüfen: node $W/tools/app_check.js 2014/index.html $W/2014/index.html --rules 2014"
