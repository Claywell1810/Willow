#!/bin/bash
# t14_klassen.sh – Willow 2014: alle Klassen-Datenblöcke neu erzeugen (Paket T2, 18.10.2026; REFERENZ B30)
# Aufruf (aus dem Ordner ÜBER dem Klon, nach `bash willow/tools/setup.sh t14`):
#   bash willow/tools/t14_klassen.sh
# Reihenfolge (jeder Schritt liest den 2014-Build des vorigen):
#   1. build_class.py --t14       → tools/t14/CLASS_DATA, CLASS_TABLES, CLASS_CORE_TRAITS, SUBCLASS_LABELS (Configs tools/t14/<k>_config.py)
#   2. feature_picks.py --t14     → tools/t14/FEATURE_PICKS (SPEC14)
#   3. subclass_spells.py --t14   → tools/t14/SUBCLASS_SPELLS, CLASS_SPELL_EXTRA, ALWAYS_PREP (koppelt Landtyp an FEATURE_PICKS)
#   4. mc_convert.py / mc_slots.py --t14 → tools/t14/CLASS_MC_GAINS, MC_SLOTS
#   SUBCLASS_TABLES.js und FEATURE_STATBLOCKS.js sind fest leer (keine SRD-Subklasse mit eigener Zaubertabelle/Begleiter).
#   Danach: Build 2014/ (Arbeits-Build) und app_check.js --rules 2014.
set -e
W="$(cd "$(dirname "$0")/.." && pwd)"; A="$(dirname "$W")"; cd "$A"
[ -d src14 ] || { echo "src14/ fehlt: erst bash willow/tools/setup.sh t14"; exit 1; }
B() { python3 "$W/tools/build_2014.py" DnD_Character_App.html --out 2014 >/dev/null; }
python3 "$W/tools/build_class.py" --t14 src14
B; python3 "$W/tools/feature_picks.py" 2014/index.html src14 --t14 --write | tail -2
B; node "$W/tools/dump.js" 2014/index.html "{ZB:ZB_SPELLS.map(s=>({name:s.name,src:s.src,grad:s.grad,school:s.school,classes:s.classes})),MAP:CLASS_SPELL_MAP,SUBS:Object.fromEntries(Object.entries(CLASS_DATA).map(([k,v])=>[k,{list:v.subclassList,keys:Object.keys(v.subclass||{})}]))}" cd.json >/dev/null
python3 "$W/tools/subclass_spells.py" 2014/index.html src14 --t14 --write | tail -1
python3 "$W/tools/mc_convert.py" 2014/index.html src14 --t14 --write | tail -1
python3 "$W/tools/mc_slots.py" 2014/index.html src14 --t14 --write | tail -1
python3 "$W/tools/build_2014.py" DnD_Character_App.html --out 2014
echo "== Prüfen: node $W/tools/app_check.js 2014/index.html $W/2014/index.html --rules 2014"
