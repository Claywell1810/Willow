#!/bin/bash
# publish.sh – Veröffentlichen in einem Aufruf (seit 01.10.2026, Anleitung B1a Schritt 5)
# Aufruf (aus dem Ordner ÜBER dem Klon, meist /home/claude):
#   bash willow/tools/publish.sh "Commit-Nachricht"
# Ablauf:
#   - Repo-Stand prüfen (bricht ab, wenn origin/main neuere Commits hat)
#   - Arbeitskopie DnD_Character_App.html ≠ ALT.html → App-Veröffentlichung:
#       app_check.js muss „alles OK“ melden, dann neue Version (willow-app-JJJJ-MM-TT + Buchstabe,
#       Datum Europe/Berlin, am selben Tag nächster Buchstabe) in APP_VERSION UND CACHE_NAME,
#       Arbeitskopie nach willow/index.html
#   - sonst (nur Doku/Skripte): Commit ohne neue App-Version
#   - Willow 2014 (Paket T1, 18.10.2026): tools/build_2014.py baut aus willow/index.html (+ tools/t14/*.js) neu; weicht das Ergebnis
#     von willow/2014/ ab, muss app_check.js --rules 2014 „alles OK“ melden, dann eigene Version willow14-app-JJJJ-MM-TT + Buchstabe
#     (APP_VERSION + CACHE_NAME in 2014/), alles im selben Commit
#   - git add -A, ein Commit, Push nach main, Größe auf GitHub gegenprüfen
# Mehrzeilige Nachricht (z. B. mit Co-Authored-By-Zeilen) einfach als ein Argument übergeben.
set -e
W="$(cd "$(dirname "$0")/.." && pwd)"          # Klon (…/willow)
A="$(dirname "$W")"                             # Arbeitsordner (Eltern des Klons)
cd "$A"
MSG="$1"
[ -n "$MSG" ] || { echo "Aufruf: bash willow/tools/publish.sh \"Commit-Nachricht\""; exit 2; }
G() { git -C "$W" "$@"; }

# 1) Repo aktuell? (Remote auf die offizielle Schreibweise, sonst meldet GitHub bei jedem Push „repository moved“)
U="$(G remote get-url origin)"
if [ "${U,,}" = "https://github.com/claywell1810/willow" ] || [ "${U,,}" = "https://github.com/claywell1810/willow.git" ]; then
  G remote set-url origin https://github.com/Claywell1810/Willow
fi
G fetch -q origin main
if [ -n "$(G rev-list HEAD..origin/main 2>/dev/null)" ]; then
  echo "ABBRUCH: origin/main hat neuere Commits als der Klon. Erst abgleichen (git -C willow pull --rebase), Arbeitskopie prüfen."
  exit 1
fi

# 2) App-Veröffentlichung oder nur Doku?
APP=0
if [ -f DnD_Character_App.html ] && [ -f ALT.html ] && ! cmp -s DnD_Character_App.html ALT.html; then APP=1; fi

if [ $APP = 1 ]; then
  echo "== Prüfskript"
  OUT="$(node "$W/tools/app_check.js" DnD_Character_App.html ALT.html 2>&1)" || true
  if ! grep -q "ERGEBNIS: alles OK" <<<"$OUT"; then
    tail -25 <<<"$OUT"; echo "ABBRUCH: app_check.js meldet Probleme, nichts veröffentlicht."; exit 1
  fi
  echo "   alles OK"
  HEUTE="willow-app-$(TZ=Europe/Berlin date +%Y-%m-%d)"
  ALTV="$(grep -o "const APP_VERSION = '[^']*';" "$W/index.html" | sed "s/.*'\(.*\)'.*/\1/")"
  if [[ "$ALTV" == "$HEUTE"? ]]; then
    L="${ALTV: -1}"; [ "$L" = z ] && { echo "ABBRUCH: Buchstabe z erreicht"; exit 1; }
    V="$HEUTE$(echo "$L" | tr 'a-y' 'b-z')"
  else
    V="${HEUTE}a"
  fi
  grep -q "const APP_VERSION = '[^']*';" DnD_Character_App.html || { echo "ABBRUCH: APP_VERSION nicht gefunden"; exit 1; }
  grep -q 'const CACHE_NAME = "[^"]*";' "$W/service-worker.js" || { echo "ABBRUCH: CACHE_NAME nicht gefunden"; exit 1; }
  sed -i "s/const APP_VERSION = '[^']*';/const APP_VERSION = '$V';/" DnD_Character_App.html
  cp DnD_Character_App.html "$W/index.html"
  sed -i "s/const CACHE_NAME = \"[^\"]*\";/const CACHE_NAME = \"$V\";/" "$W/service-worker.js"
  echo "== Version $ALTV → $V (APP_VERSION + CACHE_NAME)"
else
  echo "== Arbeitskopie unverändert → nur Doku/Skripte, keine neue App-Version"
fi

# 2b) Willow 2014 (Paket T1): Build aus der 2024-App, eigene Version nur bei Änderung
APP14=0; V14=""
rm -rf NEU2014
# Vergleichs-Build mit der Version des Repo-Stands, sonst weicht er immer ab (Version „dev“) und jede Doku-Veröffentlichung
# bekäme eine neue 2014-Version (Fund 19.10.2026, Commit 02a803e)
CUR14=""; [ -f "$W/2014/index.html" ] && CUR14="$(grep -o "const APP_VERSION = '[^']*';" "$W/2014/index.html" | sed "s/.*'\(.*\)'.*/\1/" || true)"
python3 "$W/tools/build_2014.py" "$W/index.html" --out NEU2014 ${CUR14:+--version "$CUR14"} >/dev/null || { echo "ABBRUCH: build_2014.py fehlgeschlagen"; exit 1; }
for f in index.html service-worker.js manifest.json; do cmp -s "NEU2014/$f" "$W/2014/$f" || APP14=1; done
if [ $APP14 = 1 ]; then
  echo "== Willow 2014: Prüfskript"
  ALT14=""; [ -f "$W/2014/index.html" ] && ALT14="$W/2014/index.html"
  OUT="$(node "$W/tools/app_check.js" NEU2014/index.html $ALT14 --rules 2014 2>&1)" || true
  if ! grep -q "ERGEBNIS: alles OK" <<<"$OUT"; then
    tail -25 <<<"$OUT"; echo "ABBRUCH: app_check.js (2014) meldet Probleme, nichts veröffentlicht (2024-Arbeitskopie ist schon nach willow/ kopiert: git -C willow checkout index.html service-worker.js)."; exit 1
  fi
  echo "   alles OK"
  H14="willow14-app-$(TZ=Europe/Berlin date +%Y-%m-%d)"
  A14=""   # erste 2014-Veröffentlichung: keine alte Version (if statt &&, sonst bricht set -e ab – Fund 18.10.2026)
  if [ -n "$ALT14" ]; then A14="$(grep -o "const APP_VERSION = '[^']*';" "$ALT14" | sed "s/.*'\(.*\)'.*/\1/" || true)"; fi
  if [[ "$A14" == "$H14"? ]]; then
    L="${A14: -1}"; [ "$L" = z ] && { echo "ABBRUCH: Buchstabe z erreicht (2014)"; exit 1; }
    V14="$H14$(echo "$L" | tr 'a-y' 'b-z')"
  else
    V14="${H14}a"
  fi
  python3 "$W/tools/build_2014.py" "$W/index.html" --out "$W/2014" --version "$V14"
  echo "== Willow 2014: Version ${A14:-–} → $V14"
else
  echo "== Willow 2014 unverändert"
fi
rm -rf NEU2014

# 3) Commit + Push
G add -A
if G diff --cached --quiet; then echo "Nichts zu committen."; exit 0; fi
G diff --cached --stat | tail -15
G -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -qm "$MSG"
PO="$(G push -q origin HEAD:main 2>&1)" || { echo "$PO"; echo "ABBRUCH: Push fehlgeschlagen (Commit liegt nur lokal)"; exit 1; }
grep -v "repository moved\|new location\|Claywell1810/Willow.git\|^remote: *$\|^$" <<<"$PO" || true
H="$(G log -1 --format=%h)"
echo "== Commit $H gepusht"

# 4) Größe gegenprüfen (über den Commit-Hash, damit kein veralteter raw-Cache stört)
if [ $APP14 = 1 ]; then
  L14=$(wc -c < "$W/2014/index.html")
  G14=$(curl -sS "https://raw.githubusercontent.com/Claywell1810/Willow/$H/2014/index.html" | wc -c)
  echo "   2014/index.html lokal $L14 Bytes, GitHub (Commit $H) $G14 Bytes $([ "$L14" = "$G14" ] && echo ✔ || echo '✘ ABWEICHUNG') – Version $V14"
fi
if [ $APP = 1 ]; then
  LOK=$(wc -c < "$W/index.html")
  GH=$(curl -sS "https://raw.githubusercontent.com/Claywell1810/Willow/$H/index.html" | wc -c)
  echo "   index.html lokal $LOK Bytes, GitHub (Commit $H) $GH Bytes $([ "$LOK" = "$GH" ] && echo ✔ || echo '✘ ABWEICHUNG')"
  echo "== Fertig: Commit $H, Version $V"
  cp DnD_Character_App.html ALT.html   # neue Basis: weitere Doku-Commits in derselben Sitzung ohne neue App-Version (Fund 02.10.2026)
else
  echo "== Fertig: Commit $H (keine neue App-Version)"
fi
