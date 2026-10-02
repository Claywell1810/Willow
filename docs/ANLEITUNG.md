# Willow – Arbeitsanleitung (Kern)

Gemeinsame Arbeitsgrundlage für Simon und Claude. **Jeder neue Chat liest zuerst diese Datei** und arbeitet danach.

**Seit 28.09.2026 liegt alles im Repo** `Claywell1810/Willow` (offizielle Schreibweise; `claywell1810/willow` wird umgeleitet – `add_repo` mit Kleinschreibung aufrufen, damit der Klon `willow/` heißt), live unter `https://claywell1810.github.io/Willow`:

| Pfad | Inhalt | Lesen |
|---|---|---|
| `index.html` | die App – **einzige maßgebliche Version** (B1a) | nie mit Read, nur Ausschnitte per grep/sed |
| `docs/ANLEITUNG.md` | diese Datei: A1, A4, A6 (Kurzform), A7–A11, B1a | jede Sitzung ganz |
| `docs/REFERENZ.md` | Technik: A2, A3, A5, B1–B9, B11–B14 | gezielt, z. B. `grep -n "^## B9" -A60 willow/docs/REFERENZ.md` |
| `docs/ARCHIV.md` | Verlauf: A6 (Reihenfolge), Liste der Regressionstests, B10 (Änderungsprotokoll) | nur beim Nachforschen; B10 wird dort ergänzt |
| `docs/FIXLISTE.md` | offene Arbeitspakete und Punkte | bei Paket-Arbeit ganz |
| `docs/FIXLISTE_INFO.md` | Punkte „nur zur Info“/„nur auf Wunsch“, Verlauf, Erledigtes | nur bei Bedarf |
| `docs/ZAUBER_KATEGORIEN.md` | Zauber-Kategorien/Bilder (seit 01.10.2026): Kategorien, Regeln, Ablauf für neue Zauber (`tools/spell_cats.py`) | bei neuen Zaubern oder Änderungen an Kategorien |
| `tools/` | alle Skripte: `setup.sh`, `publish.sh`, `rep.py`, `app_check.js`, `dump.js`, Konverter, `feature_picks.py` (B12), `race_convert.py` (B13), 12 Configs, Foto-Skripte | nie ganz lesen, nur ausführen oder gezielt greppen |

Abschnitts-Nummern (A2, B9 …) sind unverändert; ein Verweis zeigt je nach Nummer in diese Datei, die Referenz oder das Archiv (Tabelle oben). Im Projekt (claude.ai) liegt nur noch der Wegweiser `claude/Workflow_Anleitung.md` (verweist hierher); Skripte und Doku werden **nicht** mehr per `project_read`/`project_write` übertragen.

**Sitzungsstart (immer, in dieser Reihenfolge):**
1. Repo holen: Werkzeug `add_repo` (owner `claywell1810`, repo `willow`, access `push`), dann dessen Klon-Anweisung (einmal klonen, langes Timeout).
2. Diese Datei lesen (`willow/docs/ANLEITUNG.md`), bei Paket-Arbeit zusätzlich `willow/docs/FIXLISTE.md`.
3. `bash willow/tools/setup.sh` mit dem, was die Sitzung braucht: `klassen`, `zauber`, `bestien`, `rassen`, `fotos` oder `alle` (B1a Schritt 1). Reine UI-/Code-Arbeit: ohne Angabe, bei Fotos `fotos`.

---

## A1. Grundprinzip

- **Eine Datei:** `index.html` im Repo, Arbeitskopie `DnD_Character_App.html` (~2,4 MB, Stand 01.10.2026). Code und alle Referenzdaten stecken darin.
- **Referenzdaten** (Zauber, Klassen, Rassen …) sind JS-Konstanten in der HTML. **Charakterdaten** liegen im Browser (localStorage). Beide Welten sind getrennt, verbunden nur über **Namen** (Klasse, Subklasse, Zauber, Feat).
- **Claude** holt Rohdaten selbst aus dem 5e.tools-GitHub (A3). **Simon** entscheidet und lädt nur im Rückfall Dateien hoch. **Claude** konvertiert, fügt ein, prüft und liefert die HTML.
- **Keine erfundenen Daten.** Fehlt die Quelle, wird nichts eingebaut.

## A4. Standard-Workflow: neue Klasse (eine Klasse = ein Chat)

**Simon, vorher:** Neuen Chat im Projekt öffnen, Modell nach A10 wählen, Vorlage A8. Nichts hochladen (außer im Rückfall, A3).

**Claude, feste Reihenfolge** (Skript-Aufrufe ohne Pfad = aus dem Arbeitsordner `python3 willow/tools/<skript>`, Configs `willow/tools/<k>_config.py`):

| # | Schritt | Details |
|---|---|---|
| 0 | Vorbereitung | Sitzungsstart (Kopf dieser Datei): `bash willow/tools/setup.sh klassen zauber` – Arbeitskopie + `ALT.html`, jsdom, `class-<k>.json` aller Klassen, `optionalfeatures.json`, `feats.json`, `items.json` und die Zauber-Quellen nach `src/`, 5e.tools-Commit wird angezeigt (HTML nie mit Read!). Neue Config als `willow/tools/<k>_config.py` anlegen |
| 1 | JSON auswerten | Features/Subklassen auflisten; Subklassen **immer in der neuesten Fassung** (B6) |
| 2–6 | `CLASS_DATA`, `CLASS_TABLES`, `CLASS_CORE_TRAITS` | `<klasse>_config.py` anlegen (Tracker, Traits; Vorlagen `cleric_config.py`, `fighter_config.py`, `paladin_config.py`, `ranger_config.py`, `sorcerer_config.py`, `rogue_config.py`, `monk_config.py`, `barbarian_config.py`, `warlock_config.py`), dann `python3 build_class.py DnD_Character_App.html src/class-<k>.json <k>_config.py` (B6); danach `SUBCLASS_LABELS` ergänzen (B3). **Bereits befüllte Klasse neu bauen:** zusätzlich `--rebuild` (B6), Config ohne `traits` genügt (Vorlagen `bard_config.py`, `druid_config.py`, `wizard_config.py`) |
| 7 | `ZB_SPELLS` | `python3 spell_merge.py DnD_Character_App.html src <Klasse> --dry`, prüfen, dann ohne `--dry` (B5). Danach neue Zauber einordnen: `python3 spell_cats.py DnD_Character_App.html src --dry` (`docs/ZAUBER_KATEGORIEN.md`). Klassen ohne eigene Liste (Fighter, Rogue, Monk, Barbarian …) → entfällt |
| 8 | `CLASS_SPELL_MAP`, `SL_CLASSES`, `SUBCLASS_SPELLS` | Klasse ergänzen, falls fehlend (Subklassen-Zauberer auf die genutzte Liste zeigen lassen, z. B. `'Fighter':['Wizard']`, `'Rogue':['Wizard']`). Klassen ganz ohne Zauber (Monk, Barbarian) → entfällt. **Nach jedem Klassen-Neubau oder neuen Subklassen:** `SUBCLASS_SPELLS` neu erzeugen (`subclass_spells.py`, B5a) |
| 9 | Prüfen | `node app_check.js NEU.html ALT.html` → muss „alles OK" sein; Tabelle der neuen Klasse plausibel; Klasse in die Liste von `rebuild_diff.py` aufnehmen (B8; `all.json` per `node willow/tools/dump.js DnD_Character_App.html "{cd:CLASS_DATA,ct:CLASS_TABLES}" all.json`); im Actions-Tab kurz prüfen, ob Nicht-Kampf-Passive der neuen Subklassen in die Ausschlussliste (= Gruppe „Weitere“) gehören (B1c) |
| 10 | Abschluss | Fertig-Checkliste A11 |

**Simon, danach:** Nichts hochladen. App auf dem Handy öffnen (ggf. einmal schließen und neu öffnen, damit das Update geladen wird) → Version in den Einstellungen (⚙) prüfen → alten Charakter laden → neue Klasse kurz anklicken.

## A6. Reihenfolge (Kurzform)

Alle 12 Klassen sind eingepflegt; Fixliste Sonnet/Opus-Teil, Combat-/Actions-Umbau, UI/Lesbarkeit und die Pakete A, B, C1–C4, D, I, G, H sind erledigt (Verlauf: `docs/ARCHIV.md`, Abschnitte A6 und „Ausgelagert“). **Als Nächstes: die Arbeitspakete in `docs/FIXLISTE.md` in dieser Reihenfolge: L → K → E → A2 → F → J → M → N (J auch zusammen mit F möglich); alle Opus Hoch.** Prompt: „Arbeite die Fixliste ab: Paket X.“ Ausnahme: Stört ein Fehler im Spiel, wird er vorgezogen.

## A7. Arbeitsregeln

1. HTML immer aus Willow laden (B1a), nie verwerfen ohne Rückfrage.
2. Keine Daten erfinden, nur 5e.tools-Daten (GitHub oder hochgeladen).
3. Gezielt ersetzen **per Python-Skript** (B1a), die HTML nie komplett neu schreiben. Read/Edit-Werkzeuge funktionieren bei dieser Datei nicht.
4. **Namen sind heilig:** Klassen-, Subklassen-, Zauber- und Feat-Namen nie ändern oder löschen (Savegames, B7). Tracker-`id`s ebenso (auch die Objekt-Keys `k` von Einzel-Trackern, B2). Ebenso die Farb-Keys der Themes (eigene Farben in ⚙ hängen daran, B1d). Bestien-Namen (`BST_DATA[].n`) ebenso (gespeicherte Bestien, B7).
5. `ZB_SPELLS`, `BG_EXTRA`, `FT_FEATS`, `BST_DATA` sind riesige Einzeilen → **nie komplett lesen**, nur per Skript/grep. (`SUBCLASS_SPELLS` und `SPELL_STATBLOCKS` ebenfalls je eine lange Zeile.)
6. Jede Änderung mit `app_check.js` gegen die alte Version prüfen (B8). Jeder behobene Fehler bekommt einen Regressionstest.
7. Am Ende die **Fertig-Checkliste** (A11) abarbeiten.
8. Ein Thema pro Chat. Antworten kurz.
9. **Kleine Fehler nebenbei** (falsche Stufe, fehlende Fassung, Lücke) nicht sofort beheben, sondern in `docs/FIXLISTE.md` eintragen und Simon kurz nennen.

## A8. Prompt-Vorlagen

- **Klasse:** „Pflege die Klasse **Warlock** nach A4 ein."
- **Nur Zauber:** „Ergänze die Zauber des **Warlock** in `ZB_SPELLS` nach B5."
- **Fehler:** „Im Tab **Actions** passiert: … Erwartet: …"
- **Lücke schließen:** „Ergänze die Class Table für den **Wizard**."
- **Arbeitspakete (Reihenfolge A6):** „Arbeite die Fixliste ab: Paket L.“ (einzelnen Charakter teilen) · „… Paket K.“ (Custom-Rasse) · „… Paket E.“ · „… Paket A2.“ · „Plane Paket F (Multiclass).“ (danach Bau in Teilen) · „… Paket J.“ (Character Info, nach oder mit F)
- **Neue [Sonnet]-Punkte der Fixliste:** „Arbeite die Fixliste ab, nur Sonnet-Teil."
- **Ausschlussliste (Gruppe „Weitere“):** „Verschiebe im Actions-Tab das Feature **X** nach ‚Weitere‘.“ (Opus Mittel, B1c)
- **Rückfall ohne GitHub:** zusätzlich „Anbei `class-warlock.json`."

Erledigte Prompt-Vorlagen (Sammel-Fixes, Combat, UI, Pakete A–D, G, H, I): `docs/ARCHIV.md`, Abschnitt „Ausgelagert“.

## A9. Projekt-Anweisungen (Text für die Projekteinstellungen)

> D&D 5e Charakterbogen-App: eine HTML-Datei, Vanilla JS, offline, localStorage, Dark-Theme, mobil.
> Vor jeder Arbeit claude/Workflow_Anleitung.md lesen und danach arbeiten.
> Die App liegt im GitHub-Repo claywell1810/willow (index.html) und wird nur dort gelesen und veröffentlicht.
> Keine Daten erfinden, nur 5e.tools-Daten. Änderungen per Python mit eindeutigen Ankern, nie neu schreiben. Klassen-/Subklassen-Namen nie ändern. Nach Änderungen testen. Antworten kurz.

## A10. Welches Modell für welche Aufgabe

**Seit 28.09.2026 (Entscheidung Simon): Opus 5.5 für alle Arbeit an der HTML, Sonnet nicht mehr.** Grund: Sonnet war in diesem Projekt klar schlechter; Nacharbeit kostet mehr Nutzungslimit, als der niedrigere Preis spart. Modell und Denkstufe beim Chat-Start wählen (oder mittendrin wechseln).

**Faustregel:** Etwas wird nach Vorlage wiederholt oder ist klar umrissen → **Opus 5.5 · Mittel**. Etwas wird zum ersten Mal gebaut (Umbau, Sonder-UI, Konverter) → **Opus 5.5 · Hoch**. Nur eine Frage → **Haiku** (oder Opus · Niedrig).

**Denkstufe:** Opus 5.5 startet auf **Mittel** – **Hoch muss beim Chat-Start selbst eingestellt werden.** **Xhigh und Max nicht nutzen** (deutlich teurer, kaum besser). Hoch lohnt sich vor allem bei langen Sitzungen mit vielen Schritten; bei klar umrissenen Änderungen ist Mittel gleich gut und günstiger. (Benchmark-Zahlen: `docs/ARCHIV.md`, „Ausgelagert“.)

**Marker in der Fixliste** (bleiben wegen der Historie so stehen): **[Sonnet] = Opus 5.5 · Mittel**, **[Opus] = Opus 5.5 · Hoch**. „Sonnet“ in A6, A8 und B10 beschreibt, womit damals gearbeitet wurde.

| Aufgabe | Modell |
|---|---|
| Konverter erweitern (neue entry-Typen, neue Sonderfälle) | Opus · Hoch |
| Code-Umbauten, neue Sonder-UI | Opus · Hoch |
| Schwierige Fehler, deren Ursache unklar ist | Opus · Hoch |
| Klasse einpflegen (Konverter existieren seit dem Cleric) | Opus · Mittel |
| Klasse neu bauen (`--rebuild`, Config vorhanden, z. B. nach 5e.tools-Update) | Opus · Mittel |
| Weitere Pool-Zähler/Einzel-Tracker nach Vorlage (`pool`/`sub` in der Config, B2) | Opus · Mittel |
| Zauber einer Klasse zusammenführen | Opus · Mittel |
| Subklassen-Zauber neu erzeugen (`subclass_spells.py`, B5a) | Opus · Mittel |
| Bestien / Zauber-Stat-Blöcke neu erzeugen (`bst_convert.py`, B11, z. B. nach 5e.tools-Update oder neuem Zauber) | Opus · Mittel |
| Ausschlussliste / Gruppe „Weitere“ ergänzen (`COMBAT_SKIP_NAMES`, B1c) | Opus · Mittel |
| Fixliste abarbeiten: Punkte mit [Sonnet] (Lücken, kleine Datenfehler) | Opus · Mittel |
| Fixliste abarbeiten: Punkte mit [Opus] (Sonder-UI, Code-Umbau) | Opus · Hoch |
| Kleine UI-Anpassungen, klar beschriebene Fehler | Opus · Mittel |
| Anleitung aktualisieren | Opus · Mittel |
| Regelfragen, „wie mache ich X", Erklärungen ohne Dateiarbeit | Haiku |

Für Arbeit an der HTML **kein Haiku** (Datei zu groß, zu viele Abhängigkeiten). **Kein Sonnet** mehr (s. o.). Fable/Mythos ist für dieses Projekt nicht nötig.

Das Prüfskript (B8) fängt Fehler unabhängig vom Modell ab. Meldet es Probleme, die auf Mittel nicht sauber gelöst werden: Denkstufe auf Hoch stellen und weitermachen. Wirft `class_extract.py` „Unbekannter entry-Typ" oder „TODO _mod", braucht der Konverter eine Erweiterung → Opus · Hoch (kleine, klar umrissene Erweiterungen wie `refFeat` beim Paladin, die Nachdruck-Regeln beim Sorcerer, der Item-`statblock` beim Rogue, die Speed-Zelle beim Monk oder die Bonus-Zelle beim Barbarian reichen auf Mittel). Dasselbe gilt für `bst_convert.py` („Unbekannter Tag“, „Speed: …“, „Spellcasting-Feld nicht unterstützt“, B11).

**Subagenten:** Lohnen sich hier nicht – jeder Agent müsste die ~2,4-MB-Datei neu einlesen. Wiederkehrende Abläufe stecken stattdessen in Skripten (`setup.sh`, `publish.sh`, `rep.py`, `build_class.py` …).

## A11. Fertig-Checkliste (Ende jeder Sitzung)

Claude arbeitet sie ab und meldet sie in der Schlussnachricht als Kurzliste (✔ / –).

1. **Prüfskript:** `node app_check.js NEU.html ALT.html` → „ERGEBNIS: alles OK".
2. **Gezielter Test:** Die geänderte Funktion selbst im simulierten Browser geprüft (nicht nur „lädt ohne Fehler"). Bei sichtbaren UI-Änderungen zusätzlich Bildschirmfotos in Handybreite (`ui_shots.py` mit echter Schrift, mindestens Normal 390 px und Large 430 px = Simons Handy, auf „Karten-Überstand“ achten; bei Farben `theme_shots.py`, B8) – **Simon sieht sie vor dem Veröffentlichen**.
3. **Fehler behoben?** → Regressionstest in `REGRESSION` ergänzt (B8), vorher mit fehlerhafter Version gegengeprüft (Test muss dort ✘ melden).
4. **Md-Update nötig?** Ja, wenn mindestens eins zutrifft:
   - Stand in A2 hat sich geändert (Klasse/Lücke gefüllt)
   - neuer Datenblock, neues Schema-Feld, neuer `special`-Marker (→ B-Teil)
   - neues/geändertes Skript (→ B8 bzw. neuer Abschnitt)
   - neue Stolperfalle beim Debuggen (→ B9)
   Immer: eine Zeile in B10 (`docs/ARCHIV.md`). Kleine UI-Anpassungen ohne diese Anlässe → **kein** Md-Update.
5. **Veröffentlichen (B1a Schritt 5):** `bash willow/tools/publish.sh "Nachricht"` – prüft, setzt `APP_VERSION` und `CACHE_NAME` auf denselben neuen Wert, committet, pusht und prüft die Größe. Nur Doku/Skripte geändert (Arbeitskopie = `ALT.html`) → Commit ohne neue App-Version, macht das Skript selbst.
6. **Fixliste:** neue Funde eingetragen, erledigte Punkte nach „Erledigt" verschoben.
7. **Skripte und Doku** (seit 28.09.2026 im Repo): geänderte Dateien in `willow/tools/` und `willow/docs/` gehen mit dem Commit aus Punkt 5 mit (`git add -A`). **Nichts ins Projekt schreiben** – dort liegt nur noch der Wegweiser `claude/Workflow_Anleitung.md` (nur ändern, wenn sich Sitzungsstart, Dateiliste oder `setup.sh`-Optionen ändern; dann per `project_write`). Doku wie die HTML nur per Python-`rep()` ändern (B1a Schritt 3), nie neu schreiben oder „zusammenfassen“.
8. **Schlussnachricht an Simon:** Commit-Kürzel + neue App-Version nennen. HTML-Download nur, wenn Simon ihn wünscht.

---

## B1a. HTML laden, bearbeiten, veröffentlichen (Pflicht-Methode)

**Quelle:** GitHub-Repo `Claywell1810/Willow`, Branch `main`. Dateien: `index.html` (die App; heißt wegen GitHub Pages zwingend so), `service-worker.js`, `manifest.json`, Icons. Claude hat Schreibzugriff (GitHub App, seit 26.09.2026).

**Warum nicht aus dem Projekt:** Die HTML ist ~2,4 MB, `ZB_SPELLS` allein eine ~500-KB-Zeile. Projekt-Abrufe und das Read-Werkzeug zeigen nur bis 256 KB, das Edit-Werkzeug setzt ein vollständiges Read voraus → beide für die HTML unbrauchbar.

**1. Laden** (seit 28.09.2026 mit `setup.sh`)
- Repo in die Sitzung holen: Werkzeug `add_repo` (owner `claywell1810`, repo `willow`, access `push`), danach dessen Klon-Anweisung befolgen (einmal klonen, langes Timeout), danach `register_repo_root` (falls vorhanden; fehlt das Werkzeug, einfach weiter).
- `bash willow/tools/setup.sh [klassen] [zauber] [bestien] [rassen] [fotos] [alle]` (aus dem Ordner über dem Klon): zeigt den Willow-Commit, legt `DnD_Character_App.html` und `ALT.html` an (Größe, Ende `</html>`), installiert jsdom, lädt die gewählten 5e.tools-Quellen nach `src/` (A3) und nennt den 5e.tools-Commit; `fotos` prüft Playwright/Chromium. Ohne Angabe nur Arbeitskopie + jsdom (reine UI-/Code-Arbeit).
- Rückfall ohne GitHub: Simon hängt die Datei im Chat an.

**2. Ansehen:** nur Ausschnitte per `grep -n … | cut -c1-200` oder `sed -n 'a,bp' … | cut -c1-200`.

**3. Ändern:** mit `willow/tools/rep.py` (seit 01.10.2026) – jede Ersetzung mit Eindeutigkeitsprüfung, alles oder nichts, `--dry` für den Trockenlauf:
```bash
python3 willow/tools/rep.py DnD_Character_App.html patch.py [--dry]   # patch.py: ERSETZ = [('ALT', 'NEU'), ('ALT2', 'NEU2', 2), …]
```
In eigenen Skripten (berechnete Ersetzungen, Blöcke verschieben):
```python
import sys; sys.path.insert(0, 'willow/tools'); from rep import Datei
d = Datei('DnD_Character_App.html'); d.rep('ALT', 'NEU'); d.save()   # d.s = aktueller Text
```
Gilt genauso für Doku-Dateien. Die alte Inline-Funktion `rep()` steht in `docs/ARCHIV.md` („Ausgelagert“); wer sie doch inline schreibt: `global s` nicht vergessen (B9).
Große Datenmengen (Features, Zauber) im Skript erzeugen und einfügen, nie als Text in den Chat kopieren (dafür gibt es `build_class.py`, `spell_merge.py`, `subclass_spells.py` und `bst_convert.py` in `willow/tools/`). **Aktuelle Daten der App** (Features, Tracker, Tabellen) für Analysen: `dump.js`-Muster – App in jsdom laden und `JSON.stringify({CD:CLASS_DATA,CT:CLASS_TABLES})` nach `cd.json` schreiben (B9). HTML-Blöcke verschieben: Start-/End-Anker per `s.index()` suchen (Eindeutigkeit prüfen), Block ausschneiden und vor dem Ziel-Anker einfügen (Actions 27.09.2026).

**4. Prüfen:** `node willow/tools/app_check.js DnD_Character_App.html ALT.html` → „alles OK".

**5. Veröffentlichen:** `bash willow/tools/publish.sh "Nachricht"` (aus dem Ordner über dem Klon, seit 01.10.2026). Das Skript
- bricht ab, wenn `origin/main` neuere Commits hat, und stellt den Remote auf `Claywell1810/Willow` um;
- bei geänderter Arbeitskopie (≠ `ALT.html`): `app_check.js` muss „alles OK“ melden, dann neue Version in `APP_VERSION` **und** `CACHE_NAME` (sonst kommt das Update auf dem Handy nie an), Kopie nach `willow/index.html`;
- sonst: Commit nur mit Doku/Skripten, ohne neue App-Version;
- `git add -A`, ein Commit, Push nach `main`, Größe von `index.html` auf GitHub (über den Commit-Hash) gegenprüfen.
Mehrzeilige Nachricht (mit Co-Authored-By-Zeilen) als ein Argument übergeben. Der frühere Handablauf steht in `docs/ARCHIV.md` („Ausgelagert“).

- Name (setzt `publish.sh`): `willow-app-<Datum>` + Buchstabe, pro Veröffentlichung am selben Tag a, b, c …; Datum = Tag der Veröffentlichung (nach Mitternacht neuer Tag, wieder mit a beginnen).
- **Ein Commit pro Veröffentlichung**, Nachricht auf Deutsch: was sich für Simon ändert. Bei UI-Arbeit in Teilschritten (A6 Punkt 9) darf eine Sitzung mehrere Veröffentlichungen haben, jede erst nach Simons OK zu den Fotos.
- **App-Version** steht in den Einstellungen (⚙) neben „Settings" (`const APP_VERSION`, seit `willow-app-2026-09-26b`).

