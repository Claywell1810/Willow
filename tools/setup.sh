#!/bin/bash
# setup.sh – Sitzungsstart für Willow in einem Aufruf (seit 28.09.2026, Anleitung A4/B1a)
# Aufruf (aus dem Ordner ÜBER dem Klon, meist /home/claude):
#   bash willow/tools/setup.sh              # nur Arbeitskopie + jsdom (UI-/Code-Arbeit)
#   bash willow/tools/setup.sh klassen      # + class-*.json aller Klassen der App (klassen.py), optionalfeatures/feats/items/items-base.json, book-xphb.json nach src/
#   bash willow/tools/setup.sh zauber       # + spells/index.json, alle spells-*.json, gendata-Lookup nach src/
#   bash willow/tools/setup.sh bestien      # + Bestiarium (+ objects.json) für BST_DATA, SPELL_STATBLOCKS, FEATURE_STATBLOCKS (+ spells)
#   bash willow/tools/setup.sh rassen       # + races.json, spells-xphb/phb.json (race_convert.py, RACE_PICKS)
#   bash willow/tools/setup.sh effekte      # + conditionsdiseases/variantrules/items-base.json (cond_convert.py, armor_convert.py, effect_convert.py, Paket E)
#   bash willow/tools/setup.sh neu          # + Quellen für neu_check.py (Paket N): alle Klassen aus class/index.json nach src/neu/, backgrounds.json, dazu klassen/zauber/rassen/bestien
#   bash willow/tools/setup.sh fotos        # + Playwright/Chromium prüfen, echte Schriften (ui_shots.py, theme_shots.py)
#   bash willow/tools/setup.sh alle         # alles
# Mehrere Angaben gehen zusammen: bash willow/tools/setup.sh klassen zauber
set -e
W="$(cd "$(dirname "$0")/.." && pwd)"          # Klon (…/willow)
A="$(dirname "$W")"                             # Arbeitsordner (Eltern des Klons)
cd "$A"
B=https://raw.githubusercontent.com/5etools-mirror-3/5etools-src/main/data
has() { for x in "$@"; do for a in $ARGS; do [ "$a" = "$x" ] || [ "$a" = alle ] || { [ "$a" = neu ] && [ "$x" != fotos ] && [ "$x" != effekte ]; } && return 0; done; done; return 1; }   # neu = alle Datenquellen außer effekte/fotos
ARGS="$*"

echo "== Willow: $(git -C "$W" log -1 --format='%h %ci %s')"
# Arbeitskopie nicht überschreiben, wenn sie schon Änderungen enthält (zweiter Aufruf in derselben Sitzung, z. B. später „fotos“; B9)
if [ -f DnD_Character_App.html ] && [ -f ALT.html ] && ! cmp -s DnD_Character_App.html ALT.html; then
  echo "   Arbeitskopie hat Änderungen → bleibt erhalten (neu laden: DnD_Character_App.html löschen und setup.sh erneut aufrufen)"
else
  cp "$W/index.html" DnD_Character_App.html
  cp "$W/index.html" ALT.html
  echo "   Arbeitskopie DnD_Character_App.html + ALT.html ($(wc -c < DnD_Character_App.html) Bytes, Ende: $(tail -c 7 DnD_Character_App.html))"
fi

if [ ! -d node_modules/jsdom ]; then npm i jsdom@24 --silent >/dev/null 2>&1 && echo "   jsdom installiert"; else echo "   jsdom vorhanden"; fi

get() { mkdir -p src; [ -s "src/$(basename "$1")" ] || curl -sSf -o "src/$(basename "$1")" "$B/$1"; }
if has klassen zauber bestien rassen effekte; then
  echo "== 5e.tools main: $(git ls-remote https://github.com/5etools-mirror-3/5etools-src refs/heads/main | cut -c1-8)"
fi
if has klassen; then
  # Paket N (03.10.2026): Klassen aus der App (CLASS_DATA-Zeilen, tools/klassen.py) statt fester Liste; neue Klasse: erst Stub (A4)
  KL="$(python3 "$W/tools/klassen.py" DnD_Character_App.html --lower)"
  for k in $KL; do get "class/class-$k.json"; done
  get optionalfeatures.json; get feats.json; get items.json; get items-base.json; get book/book-xphb.json
  echo "   Klassen-Quellen in src/ ($(echo $KL | wc -w) Klassen + optionalfeatures/feats/items + book-xphb für mc_slots.py)"
fi
if has zauber bestien; then
  get spells/index.json; get generated/gendata-spell-source-lookup.json
  for f in $(python3 -c "import json;print(' '.join(json.load(open('src/index.json')).values()))"); do get "spells/$f"; done
  echo "   Zauber-Quellen in src/ ($(ls src/spells-*.json | wc -l) Dateien)"
fi
if has rassen; then
  get races.json; get spells/spells-xphb.json; get spells/spells-phb.json
  echo "   Rassen-Quellen in src/ (races.json + spells-xphb/phb)"
fi
if has effekte; then
  get conditionsdiseases.json; get variantrules.json; get items-base.json
  echo "   Effekt-Quellen in src/ (conditionsdiseases.json, variantrules.json, items-base.json)"
fi
if has bestien; then
  get bestiary/fluff-bestiary-xmm.json
  for q in xmm xphb tce xge bmt efa mm phb ftd rhw; do get "bestiary/bestiary-$q.json"; done
  get objects.json   # Objekt-Stat-Blöcke (Artificer Eldritch Cannon, Paket M)
  echo "   Bestiarium in src/"
fi
if has neu; then
  # Paket N: 5e.tools-Klassenliste + jede Klasse nach src/neu/ (nicht nach src/ – mc_convert/mc_slots/subclass_tables lesen alle src/class-*.json)
  mkdir -p src/neu; [ -s src/neu/index.json ] || curl -sSf -o src/neu/index.json "$B/class/index.json"
  for f in $(python3 -c "import json;print(' '.join(json.load(open('src/neu/index.json')).values()))"); do [ -s "src/neu/$f" ] || curl -sSf -o "src/neu/$f" "$B/class/$f"; done
  get backgrounds.json; get fluff-backgrounds.json   # bg_convert.py --add braucht beide
  echo "   Neu-Prüfung: $(ls src/neu/class-*.json | wc -l) Klassen in src/neu/, (fluff-)backgrounds.json → python3 $W/tools/neu_check.py DnD_Character_App.html src"
fi
if has fotos; then
  python3 -c "import playwright" 2>/dev/null || pip install --break-system-packages -q playwright
  ls /opt/pw-browsers >/dev/null 2>&1 || python3 -m playwright install chromium >/dev/null
  # echte App-Schriften für die Fotos (Google Fonts ist hier nicht erreichbar; Ersatzschrift ist schmaler → Überstände unsichtbar, 02.10.2026)
  [ -d node_modules/@fontsource/cinzel ] && [ -d node_modules/@fontsource/crimson-pro ] || npm i @fontsource/cinzel @fontsource/crimson-pro --silent >/dev/null 2>&1
  echo "   Playwright bereit, Schriften: $([ -d node_modules/@fontsource/cinzel ] && echo 'Cinzel + Crimson Pro' || echo 'FEHLEN')"
fi
echo "== Prüfskript: node $W/tools/app_check.js DnD_Character_App.html ALT.html"
