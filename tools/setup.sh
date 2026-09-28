#!/bin/bash
# setup.sh – Sitzungsstart für Willow in einem Aufruf (seit 28.09.2026, Anleitung A4/B1a)
# Aufruf (aus dem Ordner ÜBER dem Klon, meist /home/claude):
#   bash willow/tools/setup.sh              # nur Arbeitskopie + jsdom (UI-/Code-Arbeit)
#   bash willow/tools/setup.sh klassen      # + 12 class-*.json, optionalfeatures/feats/items.json nach src/
#   bash willow/tools/setup.sh zauber       # + spells/index.json, alle spells-*.json, gendata-Lookup nach src/
#   bash willow/tools/setup.sh bestien      # + Bestiarium für BST_DATA und SPELL_STATBLOCKS (+ spells)
#   bash willow/tools/setup.sh fotos        # + Playwright/Chromium prüfen (ui_shots.py, theme_shots.py)
#   bash willow/tools/setup.sh alle         # alles
# Mehrere Angaben gehen zusammen: bash willow/tools/setup.sh klassen zauber
set -e
W="$(cd "$(dirname "$0")/.." && pwd)"          # Klon (…/willow)
A="$(dirname "$W")"                             # Arbeitsordner (Eltern des Klons)
cd "$A"
B=https://raw.githubusercontent.com/5etools-mirror-3/5etools-src/main/data
has() { for x in "$@"; do for a in $ARGS; do [ "$a" = "$x" ] || [ "$a" = alle ] && return 0; done; done; return 1; }
ARGS="$*"

echo "== Willow: $(git -C "$W" log -1 --format='%h %ci %s')"
cp "$W/index.html" DnD_Character_App.html
cp "$W/index.html" ALT.html
echo "   Arbeitskopie DnD_Character_App.html + ALT.html ($(wc -c < DnD_Character_App.html) Bytes, Ende: $(tail -c 7 DnD_Character_App.html))"

if [ ! -d node_modules/jsdom ]; then npm i jsdom@24 --silent >/dev/null 2>&1 && echo "   jsdom installiert"; else echo "   jsdom vorhanden"; fi

get() { mkdir -p src; [ -s "src/$(basename "$1")" ] || curl -sSf -o "src/$(basename "$1")" "$B/$1"; }
if has klassen zauber bestien; then
  echo "== 5e.tools main: $(git ls-remote https://github.com/5etools-mirror-3/5etools-src refs/heads/main | cut -c1-8)"
fi
if has klassen; then
  for k in barbarian bard cleric druid fighter monk paladin ranger rogue sorcerer warlock wizard; do get "class/class-$k.json"; done
  get optionalfeatures.json; get feats.json; get items.json
  echo "   Klassen-Quellen in src/ (12 Klassen + optionalfeatures/feats/items)"
fi
if has zauber bestien; then
  get spells/index.json; get generated/gendata-spell-source-lookup.json
  for f in $(python3 -c "import json;print(' '.join(json.load(open('src/index.json')).values()))"); do get "spells/$f"; done
  echo "   Zauber-Quellen in src/ ($(ls src/spells-*.json | wc -l) Dateien)"
fi
if has bestien; then
  get bestiary/fluff-bestiary-xmm.json
  for q in xmm xphb tce xge bmt efa mm phb ftd; do get "bestiary/bestiary-$q.json"; done
  echo "   Bestiarium in src/"
fi
if has fotos; then
  python3 -c "import playwright" 2>/dev/null || pip install --break-system-packages -q playwright
  ls /opt/pw-browsers >/dev/null 2>&1 || python3 -m playwright install chromium >/dev/null
  echo "   Playwright bereit"
fi
echo "== Prüfskript: node $W/tools/app_check.js DnD_Character_App.html ALT.html"
