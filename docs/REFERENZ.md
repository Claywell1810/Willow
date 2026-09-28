# Willow – Referenz (Technik zum Nachschlagen)

Teil der Arbeitsanleitung (Kern: `docs/ANLEITUNG.md`, Verlauf: `docs/ARCHIV.md`). Nicht ganz lesen, sondern gezielt, z. B. `grep -n "^## B6" -A40 willow/docs/REFERENZ.md` oder nach Stichwort.

**Pfade seit 28.09.2026:** Alle Skripte liegen in `willow/tools/`. Aufrufe unten ohne Pfad (`python3 build_class.py …`, `node app_check.js …`) bedeuten aus dem Arbeitsordner `python3 willow/tools/build_class.py …` usw.; Configs liegen als `willow/tools/<k>_config.py` (`rebuild_diff.py` findet sie dort selbst). Statt eigener `dump.js`/`exp_all.js` gibt es `node willow/tools/dump.js HTML "<Ausdruck>" datei.json` (Beispiele im Kopf des Skripts). Quellen lädt `setup.sh` (A3).

---

## A2. Welcher Tab lebt von welchen Daten (Stand)

Der Tab **„Actions“** (bis 27.09.2026 „Combat“; intern weiter `data-tab="zauber"`, Panel `tab-zauber`) wird unten kurz „Actions“ genannt.

| Tab / Bereich | Datenblock | Quelle | Befüllt für |
|---|---|---|---|
| Info: Klassen-Features | `CLASS_DATA[k].base`, `.subclass` | `class-<k>.json` | alle 12, **alle per Konverter** (Bard, Druid, Wizard seit 27.09.2026 neu gebaut, B6 `--rebuild`) |
| Info: Subklassen-Dropdown | `CLASS_DATA[k].subclassList` | vorhanden | alle 12 |
| Info: Class Table | `CLASS_TABLES` | `class-<k>.json` | **alle 12** (Wizard und Bard seit 27.09.2026, Fixliste Sonnet) |
| Info: Class Traits | `CLASS_CORE_TRAITS` | `class-<k>.json` | alle 12 |
| Info: Rasse | `RACE_DATA` | `races.json` | 12 Rassen (PHB/XPHB) |
| Actions: Karte „Combat Stats“ (seit 27.09.2026) | `CLASS_TABLES[k].rows[lvl-1]` (Übungsbonus, alle `extra`-Spalten, Zauberplätze) + Feature-Text (Unarmored AC) | – (keine eigenen Daten) | alle 12 (B1c) |
| Actions: Class Features | `CLASS_DATA[k].abilities` (Tracker) **und** `CLASS_DATA[k].base`/`.subclass` (Features der Stufe, seit 27.09.2026) | `class-<k>.json` + `<k>_config.py` | **alle 12**. Steht seit 27.09.2026 **vor** Spellcasting. Gruppiert nach Aktion/Bonusaktion/Reaktion/Passiv/**Weitere** (Nicht-Kampf-Features über Ausschlussliste, Gruppe startet zugeklappt), Tracker und Features in einer Liste, zugeklappte Gruppen pro Charakter gespeichert (B1c). Tracker: drei Arten: Pips (Standard; **gefüllt = verfügbar** seit 27.09.2026), **Pool-Zähler** (`pool:true`, Zahlenfeld mit −/+: Lay on Hands, Sorcery Points, Focus Points, Healing Light, Balm of the Summer Court) und **Einzel-Tracker** (`sub`, eine Pip-Zeile je Objekt: Rune Knight Runen mit Auswahl, Mystic Arcanum je Grad, Lunar Sorcery je Mondphase), B2 |
| Actions: Zauberplätze | keine (Charakterwert, manuell) | – | – (Maximum je Grad steht seit 27.09.2026 in „Combat Stats“; Kreise gefüllt = verfügbar seit 27.09.2026; Warlock: Pakt-Slots zusätzlich als Tracker „Pact Magic Slots“, A5) |
| Actions / Spell List: Zauber | `ZB_SPELLS` | 5e.tools-JSON (B5) | s. unten |
| Spell List / My Spells: Kreaturen-Stat-Blöcke (seit 28.09.2026) | `SPELL_STATBLOCKS` (Schlüssel = Zaubername) | `{@creature}`-Verweise in `spells-*.json` → `bestiary-*.json` (`bst_convert.py spells`, B11) | 26 Zauber, 48 Stat-Blöcke (alle Summon-Zauber, Find Steed, Find Familiar, Animate Dead, Create Undead …), aufklappbar unter „At Higher Levels“ |
| Spell List: Klassen-Filter | `SL_CLASSES` (Knöpfe), `CLASS_SPELL_MAP` (Standard „★ Meine Klasse“) | – | **Seit 27.09.2026 (B5a):** Standard-Filter = Klasse des Charakters über `CLASS_SPELL_MAP` (Druid, Wizard, Cleric, Bard, Warlock, Paladin, Ranger, Sorcerer; Fighter/Rogue → Wizard), Knopf „★ <Klasse>“ vor „All“; ein Klick auf „All“ zeigt alle Zauber. Zauber kommen weiter über „+ Add to Sheet“ oder manuell (`addSpellManual`) aufs Blatt. Der frühere tote Code (`zbRender` u. a.) ist entfernt. |
| Spell List: Subklassen-/Zusatzzauber | `SUBCLASS_SPELLS`, `CLASS_SPELL_EXTRA` | `additionalSpells` in `class-<k>.json` bzw. `feats.json` (`subclass_spells.py`, B5a) | 81 Subklassen (602 feste Zauber + Auswahl-Filter), Klassen-Zusätze: Paladin Blessed Warrior, Ranger Druidic Warrior (je ab L2), Bard Magical Secrets (ab L10), Druid Wild Companion (ab L2); im Filter „★“ mit Abzeichen „✦ Herkunft“ |
| Beasts | `BST_DATA` + `special:["beasts"]` | Bestiarium XMM (`bestiary-xmm.json`, `fluff-bestiary-xmm.json`; `bst_convert.py bst`, B11) | 133 Bestien, nur Druid; seit 28.09.2026 vollständig aus 5e.tools neu erzeugt, Anzeige als Stat-Block (`sbHtml`) |
| Background | `BG_DATA`, `BG_EXTRA` | `backgrounds.json` | 120 |
| Feats | `FT_FEATS` | `feats.json` | 218 |
| Items | nur Kategorien `ITEM_CATS` | manuell | – |
| Theme / Rune | `CLASS_THEMES`, `CLASS_RUNES` | selbst definiert | alle 12 (Grundwerte seit 27.09.2026 über `themeBase`, B1d) |
| Info: Subklassen-Anzeige | `SUBCLASS_LABELS` | geprüft gegen 5e.tools | Cleric, Druid, Bard, Fighter, Paladin, Ranger, Sorcerer, Rogue, Barbarian, Warlock, Wizard (Monk: keine Abweichung nötig) |
| Einstellungen: App-Version | `APP_VERSION` | = `CACHE_NAME` (B1a) | – |
| Einstellungen: Text Size, Farben | – (Anzeige, B1d) | – | Text Size pro Gerät, Farben pro Klassen-Theme |
| Alle langen Texte (Features, Tracker, Zauber, Feats) | `desc`/`d`/`higher` über `fmtDesc` (seit 27.09.2026, B1e) | – (nur Anzeige) | Info-Tab, Actions, Spell List/My Spells, Feats; nicht Rassen/Background; Stat-Blöcke eigene Anzeige (`sbHtml`, B11) |

**Zauber in `ZB_SPELLS` (533):** Wizard 364, Druid 179, Bard 168, **Cleric 133 = vollständig** (am 26.09.2026 gegen 5e.tools geprüft), **Paladin 56 = vollständig** (alle 51 PHB'24-Paladin-Zauber laut gendata, dazu Ergänzungsbücher; 26.09.2026), **Ranger 72 = vollständig** (alle 61 PHB'24-Ranger-Zauber laut gendata, dazu Ergänzungsbücher; 26.09.2026), **Sorcerer 231 = vollständig** (alle 150 PHB'24-Sorcerer-Zauber laut gendata, dazu Ergänzungsbücher; 26.09.2026), **Warlock 140 = vollständig** (alle 91 PHB'24-Warlock-Zauber laut gendata, dazu Ergänzungsbücher; 27.09.2026). Fighter, Rogue, Monk und Barbarian haben keine eigene Zauberliste (gendata: 0), Eldritch Knight und Arcane Trickster nutzen die Wizard-Liste. `classes` enthält nur die Klassen, die bereits eingepflegt wurden – nicht alle Klassen eines Zaubers. Quellen: PHB'24 + Ergänzungsbücher (B5), **kein PHB'14**.

## A3. Datenquellen

**Primär: Claude lädt direkt aus GitHub** – Repo `5etools-mirror-3/5etools-src`, Branch `main`.
Basis-URL: `https://raw.githubusercontent.com/5etools-mirror-3/5etools-src/main/data/`

| Was | Pfad unter `data/` |
|---|---|
| Klasse komplett (Features, Subklassen, Tabelle, Traits) | `class/class-<klasse>.json` (klein geschrieben, z. B. `class-cleric.json`) |
| Optionale Features (Manöver, Runen, Arcane Shots, Invocations, Metamagie …) | `optionalfeatures.json` → nach `src/` legen, `build_class.py` nutzt es automatisch (B6) |
| Feats (nur nötig, wenn ein Klassen-Feature ein Feat direkt einbindet, z. B. Paladin „Blessed Warrior"; auch für `subclass_spells.py`) | `feats.json` → nach `src/` legen, `build_class.py` nutzt es automatisch (B6) |
| Gegenstände (nur nötig, wenn ein Klassen-Feature einen Gegenstand als Statblock einbindet, z. B. Rogue/Soulknife „Psychic Blade") | `items.json` → nach `src/` legen, `build_class.py` nutzt es automatisch (B6) |
| Zauber je Quelle | `spells/index.json` (Liste) → alle `spells/spells-*.json` laden (per Skript: `index.json` lesen, jede Datei mit curl holen, alles flach nach `src/`) |
| Welche Klasse welchen Zauber hat | `generated/gendata-spell-source-lookup.json` |
| Rassen / Hintergründe / Feats | `races.json`, `backgrounds.json`, `feats.json` |
| Bestien | `bestiary/bestiary-xmm.json` + `bestiary/fluff-bestiary-xmm.json` (Tagline für `fluff`) → `bst_convert.py bst` (B11) |
| Kreaturen für Zauber-Stat-Blöcke | `bestiary/index.json` (Quelle → Datei), benötigt: `bestiary-xmm/-xphb/-tce/-xge/-bmt/-efa/-mm/-phb/-ftd.json`, dazu alle `spells-*.json` → `bst_convert.py spells` (B11) |
| Buch-Kürzel und Erscheinungsdatum (z. B. AU = Arcana Unleashed, 15.09.2026) | `books.json` |
| Fluff (Beschreibungs-/Flavortexte) | `fluff-backgrounds.json` (**genutzt** für `BG_EXTRA`), `bestiary/fluff-bestiary-xmm.json` (**genutzt**: kursive Tagline als `BST_DATA[].fluff`, 14 Kreaturen), `class/fluff-class-<k>.json` (Klassen- und Subklassen-Lore, noch nicht genutzt), `fluff-races.json`, `fluff-feats.json`. `spells/fluff-spells-*.json` enthält **nur Bilder, keinen Text** → für die App irrelevant. |

- Laden per `curl -sS -o <datei> <URL>` in den Arbeitsordner, **nur per Skript verarbeiten**, nie komplett in den Kontext lesen.
- Genutzten Repo-Stand festhalten: `git ls-remote https://github.com/5etools-mirror-3/5etools-src refs/heads/main` → Commit-Kürzel in B10 notieren.
- Das Repo `5etools-2014-src` enthält die alten 2014-Daten; nur auf Simons Wunsch.

**Zauber: entschieden (Cleric-Chat, 26.09.2026) → JSON aus GitHub** mit `spell_convert.py`/`spell_merge.py` (B5). CSV-Upload entfällt.

**Rückfall (GitHub nicht erreichbar):** Simon lädt hoch – `class-<klasse>.json`, `optionalfeatures.json` (und ggf. `feats.json`, `items.json`) und die `spells-*.json` + `gendata-spell-source-lookup.json` aus dem GitHub.

## A5. Sonderfälle

- `special` schaltet Sonder-UI frei. Existiert: `beasts` (Druid). `build_class.py --rebuild` übernimmt `special` aus dem bestehenden Block.
- **Nicht-Zauberer** (Barbarian, Fighter, Monk, Rogue): erledigt seit dem Fighter – `buildClassTable` blendet die 9 Zauberplatz-Spalten aus, wenn alle `slots` 0 sind; `build_class.py` setzt dann `slots:[0,…]`. Rogue ✔: Spalte „Sneak Attack" (Würfel-Zellen, B6). Monk ✔: Spalten „Martial Arts" (Würfel), „Focus Points", „Unarmored Movement" (Speed-Zellen `bonusSpeed` → „+10 ft.", B6). Barbarian ✔: Spalten „Rages", „Rage Damage" (Bonus-Zellen `bonus` → „+2", B6), „Weapon Mastery". Die Zauber-Tabelle des Arcane Trickster (Drittel-Zauberer: Cantrips/Prepared/Slots) steht nur im Feature-Text, nicht als Class Table (Fixliste). Der Spellcasting-Bereich im Actions-Tab bleibt auch bei Nicht-Zauberern immer sichtbar (Entscheidung Simon 27.09.2026: Subklassen und Feats wie Magic Initiate bringen Zauber).
- **Halbzauberer** (Paladin ✔, Ranger ✔): 5e.tools liefert nur 5 Slot-Grade → `build_class.py` füllt auf 9 auf (seit dem Paladin). Prepared Spells als Spalte, kein Cantrip-Feld.
- **Warlock ✔ (Pakt-Magie):** Die XPHB-Klasse hat **keine** `rowsSpellProgression`; die Pakt-Slots stehen als normale Spalten in `classTableGroups` („Spell Slots" → Key `spell`, „Slot Level" → Key `slot`, dazu `invocations`, `cantrips`, `prepared`). `build_class.py` braucht dafür keine Änderung: `slots` bleibt 0 → die 9 Zauberplatz-Spalten entfallen, die Pakt-Spalten erscheinen als `extra`. Im Actions-Tab zusätzlich ein Tracker „Pact Magic Slots" (`uses:{1:1,2:2,11:3,17:4}`, `restore:"short"`, Werte aus der Spalte Spell Slots); seit 27.09.2026 zeigt die Karte „Combat Stats“ Spell Slots und Slot Level der Stufe. **Mystic Arcanum** seit 27.09.2026 als Einzel-Tracker `wl_mysticarcanum` (eine Zeile je Grad 6/7/8/9, ab L11/13/15/17, je 1× pro Long Rest).
- **Sorcerer ✔** (Sorcery Points = `uses:"level"`, Innate Sorcery 2/Long Rest), **Monk ✔** (Focus Points = `uses:"level"`, ab Stufe 2, Short Rest): seit 27.09.2026 als **Pool-Zähler** (`pool:true`, Zahlenfeld statt bis zu 20 Pips). **Barbarian ✔** (Rage `uses:{1:2,3:3,6:4,12:5,17:6}`, Zealot-Pool `{3:4,6:5,12:6,17:7}`): Nutzungen als Pips. Stufenabhängige Anzahl mit `uses:{Stufe:Anzahl}` (B2); `"level"` für Punkte = Stufe; Attributs-Modifikator mit `"str"`, `"con"` usw. **Warlock/Celestial Healing Light** (Würfel-Pool 1 + Stufe): `uses:{3:4 … 20:21}` (in der Config per Schleife erzeugt), `pool:true`. **Druid/Circle of Dreams Balm of the Summer Court** (Würfel-Pool = Stufe): `uses:"level"`, `pool:true`.
- **Pool-Ressourcen** (seit 27.09.2026, `pool:true`): **Paladin Lay on Hands** = 5 × Stufe HP (`uses:"level*5"`, id `layonhands`, Long Rest). Anzeige = Rest mit −/+ und Eingabefeld; gespeichert wird wie bei Pips der Verbrauch (`st.abUses[id]`), deshalb konnten Sorcery/Focus Points/Healing Light/Balm ohne Savegame-Bruch umgestellt werden.
- **Pro-Objekt-Nutzungen** (seit 27.09.2026, `sub`): **Fighter/Rune Knight** `rk_runes` (Feature Rune Carver + Master of Runes; 6 Runen, Hill/Storm ab L7; je Rune 1× pro Short/Long Rest, ab L15 2×; `pick` = Runes Known 2/3/4/5 – der Spieler markiert seine Runen mit ☆/★, zugeklappt sind nur die gewählten sichtbar), **Warlock Mystic Arcanum** (s. o.), **Sorcerer/Lunar Sorcery** `lu_waxingwaning` (ab L6 je Mondphase ein Gratis-Zauber) und `lu_lunarphenomenon` (ab L18 je Mondphase 1× pro Long Rest); Lunar Embodiment zählt nur L3–5 (`uses:{3:1,6:0}`).
- **Ranger Beast Master:** `beasts` (Bestiarium) wurde **nicht** für die Subklasse eingebaut – der Primal Companion nutzt eigene Stat-Blöcke (Beast of the Land/Sea/Sky), die nicht in `BST_DATA` stehen; Sonder-UI wäre eigene Sitzung (Fixliste Paket A2; Stat-Block-Anzeige `sbHtml` und `bst_convert.py` sind seit 28.09.2026 vorhanden, B11).
- **Wizard/Bard/Druid (früher handgebaut):** Seit 27.09.2026 mit `build_class.py --rebuild` aus 5e.tools neu gebaut (B6). Die Class Tables (Wizard/Bard am 27.09.2026 aus `classTableGroups` eingefügt, Druid handgebaut) und die Traits blieben unverändert; `rebuild_diff.py` bestätigt, dass die Tabellen dem Konverter-Ergebnis entsprechen. Die Druid-Subklassen-Keys mit Kürzel („Circle of Dreams (XGE)“ …) und alle alten Tracker-`id`s (auch ohne Präfix, z. B. `bardicinspiration`, `wildshape`, `fungalinfestation2`) bleiben erhalten; neue Tracker bekommen Präfixe (`bd_`, `dr_`, `wz_`).
- **Zauber außerhalb der Klassenliste** (seit 27.09.2026, B5a): Blessed Warrior (Paladin → Cleric-Cantrips), Druidic Warrior (Ranger → Druid-Cantrips), Magical Secrets (Bard → Cleric/Druid/Wizard ab L10) und alle immer vorbereiteten/erweiterten Subklassen-Zauber stehen im Spell-List-Filter „★ Meine Klasse“ mit Abzeichen „✦ Herkunft“.
- Grundsatz: erst Standard-Daten einpflegen, Sonder-UI in eigener Sitzung.

## B1. Dateiaufbau (Anker per grep finden, Zeilennummern ändern sich)

| Anker | Inhalt |
|---|---|
| `:root{` (erster Style-Block) | Farb-Variablen, Typo-Skala `--fs-2xs … --fs-txt`, `--desc`, `--muted`, `--zf` (B1d) |
| `/* ── UI / Lesbarkeit (27.09.2026)` (Ende des Style-Blocks) | Tipp-Flächen, enge Stellen, Zoom-Stufen `html[data-ts=…]`, `.ts-row`, `.clr-grp` (B1d); direkt danach das Frühstart-Skript für die Textgröße |
| `/* ── Stat-Block (Paket A, 27.09.2026)` (letzter Block vor `</style>`, nach dem Text-Formatierer-CSS) | CSS `.sb*` der Stat-Block-Anzeige (B11) |
| `const ZB_SPELLS=[` | alle Zauber, eine Zeile |
| `const CLASS_TABLES={` | Level-Tabellen |
| `const CLASS_SPELL_MAP=` / `const SL_CLASSES=` | Zauberfilter (B5a) |
| `// SUBCLASS_SPELLS-START` … `// SUBCLASS_SPELLS-END` | `SUBCLASS_SPELLS` + `CLASS_SPELL_EXTRA`, erzeugt von `subclass_spells.py` (B5a), direkt vor `// SPELL LIST` |
| `const CLASS_DATA={};` + `function clsSpecial` | Registry-Kopf |
| `const SUBCLASS_LABELS={` | Dropdown-Anzeige der Subklassen-Fassung (B3) |
| `CLASS_DATA["<Klasse>"]={` | ein Block pro Klasse (Barbarian, Druid, Cleric, Fighter, Monk, Paladin, Ranger, Sorcerer, Rogue, Warlock, Wizard, Bard), endet mit der ersten Zeile `};`; Stub = nur `special` + `subclassList` (keine Stubs mehr übrig) |
| `const RACE_DATA=` / `const CLASS_CORE_TRAITS` | Rassen, Klassen-Traits |
| `const BG_DATA=` / `const BG_EXTRA=` / `const FT_FEATS=` / `const BST_DATA=` | Browser-Daten; direkt nach der `BST_DATA`-Zeile die Zeile `const SPELL_STATBLOCKS=` (B11) |
| `const SIZE_MAP=` + `// ── STAT-BLOCK (Paket A, 27.09.2026) ──` | Größen-Kürzel; danach `SB_LBL`, `sbLbl`, `sbEntry`, `sbMod`, `sbHtml`, `spellStatBlocks` (B11), dann `bstMakeCard`, `bstToggle`, `buildSavedBeasts` |
| `const TEXT_IDS` | gespeicherte Formularfelder |
| `const CLASS_THEMES=` / `const CLASS_RUNES=` | Optik je Klasse; direkt danach `THEME_GOLD_HI`, `hexMix`, `themeBase`, `applyTheme` (B1d) |
| `// ── TEXT-FORMATIERER (UI/Lesbarkeit 27.09.2026) ──` | `FD_SMALL`, `fdEsc`, `fdIsName`, `FD_NAMED`, `fdTV`, `fdNamed`, `fdInline`, `fmtDesc` (B1e); direkt danach `formatSpellDesc` (ruft nur noch `fmtDesc`). CSS `.fd*` im Block `/* ── Text-Formatierer fmtDesc` am Ende des Style-Blocks |
| `// Textgröße (UI/Lesbarkeit 27.09.2026)` | `TEXT_SIZES`, `getTextSize`, `markTextSize`, `setTextSize` (vor `const APP_VERSION`) |
| `const APP_VERSION` | sichtbare App-Version (Abschnitt `// SETTINGS`); danach `COLOR_LABELS`, `COLOR_GROUPS`, `colorGrpOpen`, `openSettings`, `buildColorPanel` |
| `// ── COMBAT-TAB (Umbau 27.09.2026) ──` | direkt vor `function buildAbilities`: `COMBAT_SKIP_NAMES`, `COMBAT_SKIP_KEEP`, `combatSkip`, `clsSubKey`, `combatFeatures`, `combatUnarmoredAC`, `buildCombatStats`, `abGrpIsClosed`, `togAbGrp` (B1c) |
| HTML-Kommentare im Panel `tab-zauber` | `<!-- COMBAT STATS … -->`, `<!-- HIT POINTS -->`, `<!-- CLASS FEATURES -->`, `<!-- Spellcasting -->`, `<!-- BEASTS -->` (Reihenfolge seit 27.09.2026 so, B1c) |
| `<!-- SETTINGS MODAL -->` | ⚙-Dialog: Abschnitte TEXT SIZE (`#tsRow`), DATA, COLOR SCHEME (`#settingsColorPanels`) |
| Renderer | `buildClassTable` (Class Table), `buildClsLore` (Klassen-Features), `buildSubclsLore` (Subklassen-Features), `buildAbilities` + `abMaxUses` (Actions-Tab: Tracker + Feature-Karten, gruppiert; Pool-Zähler, Einzel-Tracker), `buildCombatStats` (Karte `#combatStats`), `buildSlots` + `togSlot` (Zauberplätze, Knöpfe `.slbtn`), Handler `togAb`, `togAbGrp`, `togAbUse`, `abPoolAdj`, `abPoolSet`, `togAbPick`, `restoreAllUses`, CSS `.ab-pool`/`.ab-subs`/`.ab-grp`/`.ab-feat`/`.cst-*`, `.ab-pip.avail`/`.slpip.av` (gefüllt = verfügbar), `onClsChange`/`onSubclsChange` (Dropdowns); Spell List: `slBuildFilters`, `slRender`, `slMakeCard`, `slMySpellCtx`/`slMyVia`/`slFilterHit` (Filter „★ Meine Klasse“), CSS `.sl-via`; Texte: `fmtDesc` (alle langen Texte, B1e), `formatSpellDesc` = Hülle für `fmtDesc` (alte CSS `.sdesc*` ungenutzt); Stat-Blöcke: `sbHtml`, `spellStatBlocks` (in `slMakeCard` und `buildMySpells`), `bstMakeCard` (B11); untere Leiste **`.bnav-dice`** (Würfel-Knopf zwischen Skills und Items, seit 27.09.2026, B1f) |

## B1c. Actions-Tab (bis 27.09.2026 „Combat“)

Der Tab heißt seit 27.09.2026 **„Actions“** (oberer Tab-Knopf `.tab[data-tab="zauber"]` und untere Leiste `.bnav-btn[data-tab="zauber"] .bnav-label`, Icon ⚔️). **Nur die Beschriftung** ist neu: `data-tab="zauber"`, Panel `#tab-zauber`, `switchTabAll('zauber')` und die Code-Namen (`combat…`, `COMBAT_SKIP_NAMES`, Karte „Combat Stats“) bleiben (Tests, B8).

Reihenfolge im Tab (seit 27.09.2026, `willow-app-2026-09-27j`): Hit Points/Death Saves → **Combat Stats** (zugeklappt) → Weapons → **Class Features** → Spellcasting/Spell Slots/My Spells → Beasts. Der frühere Link „📖 Spell List →“ oben im Tab ist entfernt (Spell List über die obere Tab-Leiste). Spellcasting bleibt immer sichtbar (auch bei Nicht-Zauberern, Entscheidung Simon). Keine eigenen Daten; alles wird aus vorhandenen Blöcken berechnet. `buildAbilities()` baut beides neu (ruft `buildCombatStats` auf) und läuft bei Klasse/Subklasse/Stufe, Tab-Wechsel und jedem Tracker-Klick.

**Karte „Combat Stats“** (`#combatStats`, `buildCombatStats(cls, subcls, lvl)`; seit `…27j` unter Hit Points, **startet zugeklappt**: Kopf `.cst-head` antippen → `togAbGrp('stats')`, Inhalt `.cst-body`, Zustand wie die Gruppen in `st.abGrpClosed.stats`, fehlt = zu):
- Zeile `CLASS_TABLES[cls].rows` mit `lvl` = Stufe → Chip „Proficiency Bonus“ (`pb`), dann **jede `extra`-Spalte** mit Label `l` und Wert (leer, `—` oder 0 → kein Chip). Neue Spalten erscheinen automatisch.
- Zauberplätze je Grad (`slots` > 0) als kleine Reihe „Spell Slots 1·4 2·3 …“ (Nicht-Zauberer/Warlock: keine).
- **Unarmored AC** (`combatUnarmoredAC`): Regex über die Feature-Texte der Stufe (`base Armor Class`/`your AC equals N plus/+ your <Attribut> [and <Attribut>] modifier`, nicht bei „… if“ wie Circle Forms) + `getAbilityMod`; trifft Unarmored Defense (Monk DEX+WIS, Barbarian DEX+CON), Draconic Resilience (13+DEX bzw. 10+DEX+CHA), Dazzling Footwork (10+DEX+CHA). Nur Anzeige, der AC-Wert des Charakters bleibt manuell.

**Class Features** (`#abList`, `buildAbilities`):
- Gruppen in fester Reihenfolge **Aktion · Bonusaktion · Reaktion · Passiv · Weitere** (Kopf `.ab-grp` mit Anzahl, antippen = zuklappen über `togAbGrp(k)`; Inhalt `.ab-grp-box[data-grp]`). Leere Gruppen entfallen. Innerhalb: nach Stufe, Klasse vor Subklasse.
- **Zugeklappt-Zustand pro Charakter** (seit 27.09.2026): `st.abGrpClosed = {aktion:false, weitere:true, …}`, gelesen über `abGrpIsClosed(k)` (fehlt der Key → nur „Weitere“ ist zu). `togAbGrp` schreibt den Wert und ruft `autoSave()`.
- **Tracker-Karten** (Gruppe = Tracker-`tag`); **Feature-Karten** (`.ab-card.ab-feat`, Icon je Gruppe ⚔️/⚡/🛡️/✧/📜, Zeile „Level N [· Subklasse]“, Text beim Antippen, id `ab_f_<b|s>_<name>`) aus `combatFeatures(cls, subcls, lvl, trB, trS)`: alle Features aus `base` bzw. `subclass[key]` mit `lvl` ≤ Stufe (Gruppe = Feature-`tag`), **ohne**
  1. Features mit Tracker-Karte: gleicher Name **oder** die ersten 200 Zeichen des Feature-Texts stehen im Tracker-`desc` (so auch umbenannte Tracker wie Monk's Focus → Focus Points und angehängte Verbesserungen wie Eldritch Master, Font of Inspiration, Master of Runes); Klasse nur gegen Klassen-Tracker, Subklasse nur gegen Subklassen-Tracker;
  2. Gleicher Name mehrfach (Indomitable 9/13/17, Action Surge 2/17 …) → eine Karte, Text der höchsten erreichten Stufe, „Level“ = erste Fundstelle.
- **Gruppe „Weitere“** (seit 27.09.2026, vorher ausgeblendet): Nicht-Kampf-Passive (`combatSkip`, nur `tag:"Passiv"`, Feld `more` im Ergebnis von `combatFeatures`): Namen in `COMBAT_SKIP_NAMES` (ASI, Epic Boon, Spellcasting, Expertise, Bonus Proficiencies, Thieves' Cant, Druidic, Scholar, Ritual Adept, Memorize Spell, Magical Secrets, Eldritch Invocation Options, Sprach-/Skill-/Werkzeug-Features u. a.) sowie Muster „… Subclass“, „… Savant“, „… Spells“ (außer `COMBAT_SKIP_KEEP`: Beast Spells, Sculpt Spells, Share Spells), „Tenets of …“. CSS `.ab-grp-dot.weitere`, `.ab-icon.weitere`.
- Info-Tab (`buildClsLore`/`buildSubclsLore`) zeigt weiter **alle** Features.
- Ausschlussliste (= Gruppe „Weitere“) ergänzen = Name in `COMBAT_SKIP_NAMES` (Anker `const COMBAT_SKIP_NAMES=new Set([`) per Python-Ersetzung; Feature-Namen exakt wie in `CLASS_DATA` (Groß-/Kleinschreibung, Sonderzeichen wie „—“).

**Kreise zeigen Verfügbares** (seit 27.09.2026, nur Anzeige):
- Tracker-Pips (`pipRow` in `buildAbilities`, auch Einzel-Tracker `sub`): `.ab-pip.avail` (gefüllt) für `i < max − verbraucht`, sonst `.ab-pip.used` (leer). `togAbUse(id, i, max)`: gefüllten Kreis antippen → Verbrauch +1, leeren → −1 (nicht mehr positionsabhängig).
- Zauberplätze (`buildSlots`): `.slpip.av` (gefüllt) für `j < slotMax − slotUsed`, sonst `.slpip.u`. `togSlot(i, j)` genauso ±1.
- Gespeichert bleibt der **Verbrauch** (`st.abUses`, `st.slotUsed`) → keine Savegame-Änderung. Death Saves und Inspiration unverändert (dort „gefüllt = eingetreten“). Pool-Zähler zeigten schon vorher den Rest.

## B1d. Anzeige: Schriftskala, Tipp-Flächen, Textgröße, Farben (seit 27.09.2026)

Nur Anzeige, keine Daten. Entstanden in A6 Punkt 9 (`17eaa3a`/`…27k`, `3f17987`/`…27l`).

**Typo-Skala** (`:root`): `--fs-2xs:11px` · `--fs-xs:12px` · `--fs-sm:13px` · `--fs-md:14px` · `--fs-txt:15px` (Fließtext/Beschreibungen). Alle früheren festen Größen 8–15 px (CSS, HTML-Inline, JS-Vorlagen) sind darauf umgestellt (8/9/10 → 2xs, 11 → xs, 12 → sm, 13 → md, 14/15 → txt). **Neue Schriftgrößen unter 16 px immer als Variable schreiben** (`font-size:var(--fs-sm)`), nie `px` unter 11 (Regressionstest). 16 px und größer bleiben `px` (Eingabefelder brauchen 16 px, sonst zoomt iOS beim Tippen).

**Tipp-Flächen:** Kleine Kreise behalten ihre sichtbare Größe; ein unsichtbarer Rand `::after{content:'';position:absolute;inset:…}` vergrößert die Tipp-Fläche (`.ab-pip`, `.fc-pip`, `.slpip`, `.dspip`, `.inspip`, `.delbtn`, Collapse-Knöpfe `.sec .filter-toggle`, `.expbtn`). Größen: `.hbtn` 30 px (Zauberplätze `.hbtn.slbtn` 28 px), `.ab-pbtn` 32 px, `.spell-prep` 26 px. Alles im Block `/* ── UI / Lesbarkeit (27.09.2026)` am Ende des Style-Blocks (Nachträge überschreiben die Grundregeln weiter oben).

**Textgröße (⚙ „Text Size“):** Normal / Large / X-Large = `html` ohne Attribut / `html[data-ts="gross"]` (`zoom:1.15`) / `html[data-ts="sehrgross"]` (`zoom:1.3`), dazu `--zf` = Faktor. Gespeichert **pro Gerät** in localStorage `willow_textsize` (`normal|gross|sehrgross`, nicht im Charakter). Ein Mini-Skript direkt nach `</style>` setzt das Attribut vor dem ersten Zeichnen (kein Flackern). Funktionen `getTextSize`, `setTextSize(v)`, `markTextSize()` (Knöpfe `#tsRow .fbtn[data-ts]`, `.on` = aktiv; `openSettings` ruft `markTextSize`). Enge Stellen bei großer Schrift: `.attr-grid`, `.stat3`, `.slot-g` mit `auto-fill`/`minmax(96px,1fr)` (3 → 2 Spalten), HP-Karten `.hp-row` brechen um (Temp in eigene Zeile), Spell-List-Abzeichen in eigener Zeile (`.zb-top` `flex-wrap`, Name + ▾ oben).

**Farben:** Grundwerte je Klassen-Theme über `themeBase(cls)` (= `CLASS_THEMES[cls]` + Ergänzungen), genutzt von `applyTheme`, `buildSettingsUI`, `buildColorPanel`, `applyThemeFrom`. `CLASS_THEMES` selbst ist unverändert.
- `purple` („Highlight“) = `THEME_GOLD_HI` `#ecd592`, `text3` („Small Labels“) = `THEME_GOLD_LBL` `#b8a06a` – in **allen** Themes hellgold (Wunsch Simon).
- `desc` („Description Text“) = `hexMix(text, text2, .2)` → fast weiß mit Theme-Tönung. Genutzt von `.ab-desc`, `.feat-desc`, `.desc-text`, `.bg-desc`, `.higher-box p` und Inline-Beschreibungen (Info-Tab-Features, Class Traits, Feats, Bestien).
- `muted` („Muted (Nav, Placeholders)“) = der alte `text3` des Themes: inaktive untere Leiste `.bnav-btn`, Platzhalter, Leere-Liste-Hinweise („No weapons added.“ …), „Collapse Nav“, leere Tabellenzellen.
- Eigene Farben aus ⚙ (`dnd5e_theme_overrides`, Keys wie `COLOR_LABELS`) gehen immer vor. Keys nie umbenennen.
- ⚙-Farbauswahl in Gruppen `COLOR_GROUPS` (Backgrounds · Text · Accents · Status) als `<details class="clr-grp">`; offen bleibt, was in `colorGrpOpen` steht (Start: Text), auch nach dem Neuaufbau beim Speichern.
- **Beim Einsatz neuer Farben:** Beschreibungen `var(--desc)`, Labels `var(--text3)`, Nebensachen/Platzhalter `var(--muted)`, Hervorhebung `var(--purple)`, Akzent/Namen `var(--gold)`.

## B1e. Text-Formatierer `fmtDesc` (seit 27.09.2026)

Nur Anzeige, die Daten (`desc`, `d`, `higher`) bleiben unverändert. Entstanden in A6 Punkt 9.3 (`ca5eed7`/`…27m`).

**Aufruf:** `fmtDesc(text, ctx?)` → HTML `<div class="fd">…</div>`, Text HTML-sicher escaped (`fdEsc`). `ctx = {cls, lvl}` nur dort, wo Klasse und Stufe feststehen (Info-Tab-Features, Actions-Karten).
**Eingesetzt in:** `buildClsLore`, `buildSubclsLore` (Info-Tab, mit `ctx`), `buildAbilities` (Tracker- und Feature-Karten `.ab-desc`, mit `ctx`), `buildFeatsInfo`, `buildFeats` (`.feat-desc`), Feat-Datenbank (`ftMakeCard`, `desc.innerHTML=fmtDesc(ft.d)`), Zauber über `formatSpellDesc` (Spell List und My Spells) und „At Higher Levels“ (`fmtDesc(higher)` statt `<p>`). **Nicht:** Rassen-Traits (eigene Karten je „• Name: …“), Background (`renderBgText`, `**fett**`), Stat-Blöcke (eigene Anzeige `sbHtml`/`sbEntry`, B11). Kein `white-space:pre-line` mehr an diesen Stellen (Regressionstest).

**Zeilenregeln** (Text wird an `\n` bzw. `\n\n` in Zeilen zerlegt):
- `• …` → Listenpunkt (`<ul>`, eigener Punkt per `::before` in `--text3`). Absätze **zwischen** zwei Listenpunkten gehören zum vorigen Punkt (`p.fd-cont`), wenn dieser lang (> 80 Zeichen) oder benannt ist (Runen, Wild-Shape-Regeln).
- **Blockname** am Zeilenanfang: `Name. Text` oder `Name: Text`, auch mit Klammer (`Poison (Cost: 1d6): …`, `Name (Level 5+). …`) → `<b class="fd-n">` (fett-kursiv, `--text`). Name = höchstens 7 Wörter/48 Zeichen, kein Komma, jedes Wort groß oder aus `FD_SMALL` (of, the, a, and, to, in, …, your, its) – so wird „You gain two uses.“ **nicht** fett. Gilt auch für Zauber-Abschnitte (vorher eigene Überschrift `.sdesc-head`, jetzt einheitlich, Entscheidung Simon).
- **Überschrift** = kurze Zeile mit `:` am Ende und Namensform („Beast Shapes:“, „Life Domain Spells:“) → `.fd-cap` (Cinzel, `--text3`). Folgen nur Zeilen `• Schlüssel: Wert` (Schlüssel ≤ 16 Zeichen, ohne Punkt) → zweispaltige Tabelle `.fd-kv` (Schlüssel `td.fd-k`, fett, nicht umbrechend). „You gain the following benefits:“ bleibt Absatz.
- **Tabellen** aus Zeilen mit ` | ` (mit oder ohne `• `): erste Zeile ohne `• ` = Kopfzeile (`th`), z. B. Beast Shapes, Creating Spell Slots, Psi Warrior Energy Dice, Genie Expanded Spells, Chaos Bolt. Wrapper `.fd-tw` mit `overflow-x:auto` (breite Tabellen scrollen, kein Seitenüberlauf).
- Alte CSV-Zauber: Listenpunkte mit doppeltem Leerzeichen werden wie früher in `formatSpellDesc` als Liste gezeigt. Zusammengeklebte CSV-Tabellen (Confusion, Prismatic Spray) sind nicht zerlegbar (Fixliste).

**Tabellenwerte im Text** (`fdTV`, nur mit `ctx`): „the \<Label\> column of the \<Klasse\> Features table“ → danach Kästchen `.fd-tv` „Level 7: 1d8“ aus `CLASS_TABLES[cls].rows[lvl-1][extra.k]` (Label = `extra.l` ohne HTML). Nur wenn die Klasse im Text = `ctx.cls` und der Wert nicht leer ist. Trifft 28 Stellen (Cantrips, Prepared Spells, Rages, Rage Damage, Martial Arts, Focus Points, Sneak Attack, Wild Shape, Channel Divinity, Second Wind, Sorcery Points, Favored Enemy, Invocations, Bardic Die, Weapon Mastery). Der Info-Tab wird deshalb auch bei Stufenwechsel neu gebaut (`#lvl` `oninput`/`onchange` rufen zusätzlich `buildClsLore();buildSubclsLore()`).

**CSS** (Block `/* ── Text-Formatierer fmtDesc` direkt vor `</style>`, nach dem UI-Block): `.fd p` Abstand `.6em`, `.fd ul`/`li`, `.fd-n`, `.fd-cap`, `.fd-tw`, `.fd-tbl` (`th` Cinzel `--text3` auf `--bg3`, Zebra-Zeilen), `.fd-tv` (Kästchen in `--purple`), `.higher-box .fd p`. Farben/Größen nur über Variablen (B1d).

**Neue Textstellen:** `fmtDesc(text)` statt `${desc}` einsetzen, kein `pre-line`; Container gibt Farbe (`--desc`) und Größe (`--fs-txt`) vor. Namen/Überschriften erkennt der Formatierer nur aus der Textform – ein falsch erkannter Name wird über die Namensregeln in `fdIsName` behoben, nie über die Daten.

## B1f. Untere Leiste, Würfel-Knopf (seit 27.09.2026)

Nur Anzeige, keine Daten. Entstanden in A6 Punkt 9.4 (`a9fd1bb`/`…27n`).

Die untere Leiste (`#bottomNav`) zeigt fünf `.bnav-btn`: **Info · Skills · Würfel · Items · Actions** (`data-tab`: `info`/`skills`/–/`ausruestung`/`zauber`). Der Würfel-Knopf ist der einzige **ohne** `data-tab` (`class="bnav-btn bnav-dice"`, `onclick="openDice('',0)"`) – er öffnet den Würfel-Dialog direkt und wechselt keinen Tab. Vorher gab es dafür einen schwebenden Knopf `.dice-fab` (rechts unten, verdeckte Pool-„+“ und Kartenränder); der ist entfernt. Skills hat seit der Verschiebung das Icon **🎯** (vorher 🎲, das jetzt am Würfel-Knopf steht).

Der Würfel-Knopf ist optisch hervorgehoben (Wunsch Simon: „zentral, darf hervorstehen“): `.bnav-dice .bnav-icon` ist 48 px, kreisförmig, `margin:-16px auto 2px` (ragt über die Leiste), Hintergrund `var(--purple3)`, Rand `var(--purple)`, Schatten. `.bnav-dice:active .bnav-icon` verkleinert sich beim Antippen. Änderungen daran nur in diesem CSS-Block (Anker `/* DICE ROLLER */` direkt vor `.dice-modal{`).

Beim Verschieben des Buttons wurde nebenbei ein Strukturfehler behoben: eine überflüssige `</div>` schloss `.body` (den Wrapper mit dem 14-px-Seitenrand) vorzeitig direkt nach den Actions-Custom-Features, wodurch die fünf folgenden Panels (`tab-bestien`, `tab-feats`, `tab-spelllist`, `tab-notizen`, `tab-log`) zu Geschwistern von `.app` statt Kindern von `.body` wurden – ohne Seitenrand und mit verschobenem Abstand nach oben (bei Spell List am auffälligsten: großer Leerraum über „← My Spells“). Die überflüssige `</div>` ist entfernt; alle Panels sind jetzt wieder Kinder von `.body`.

## B2. `CLASS_DATA` – Schema

```js
CLASS_DATA["Cleric"]={
special:[],                               // Sonder-UI-Marker, z. B. ["beasts"]
subclassList:["Life Domain (PHB)", …],    // Dropdown, MIT Quellen-Kürzel — vorhanden, nicht ändern
// Quelle: … (Kommentarzeile von build_class.py: welche Fassung je Subklasse)
abilities:{                               // Actions-Tracker (optional)
  base:[
    {id:"channeldivinity", name:"Channel Divinity", tag:"aktion", icon:"✨",
     uses:{"2":2,"6":3,"18":4}, restore:"short", desc:"…", minLvl:2},
  ],
  "Life Domain":[ … ],                    // Subklassen-Tracker, Key-Regel B3
},
base:[                                    // Info-Tab, Stufe 1–20 (seit 27.09.2026 auch Actions-Tab, B1c)
  {lvl:1, name:"Spellcasting", desc:"…", tag:"Passiv"},
],
subclass:{                                // Key-Regel B3
  "Life Domain":[ {lvl:3, name:"…", desc:"…", tag:"Passiv"} ],
}
};
```

| Feld | Werte |
|---|---|
| Feature-`tag` (base/subclass) | Anzeige-Text: `"Passiv"`, `"Aktion"`, `"Bonusaktion"`, `"Reaktion"` (bestimmt seit 27.09.2026 auch die Gruppe im Actions-Tab) |
| Tracker-`tag` (abilities) | Schlüssel: `"passiv"`, `"aktion"`, `"bonus"`, `"reaktion"` (steuert Icon-Farbe und Gruppe im Actions-Tab) |
| `uses` | Zahl · `"str"`/`"dex"`/`"con"`/`"int"`/`"wis"`/`"cha"` (= Modifikator, min. 1; alle sechs seit dem Fighter) · `"level"` (= Stufe) · `"level*N"` (= N × Stufe, seit 27.09.2026; Lay on Hands `"level*5"`) · `"pb"` (= Übungsbonus) · `{Stufe:Anzahl}` (höchste erreichte Stufe gilt, z. B. `{2:2,6:3,18:4}`; unterhalb der ersten Stufe = 0 Pips) · `null` (kein Zähler, z. B. Optionen, die Channel Divinity/Second Wind/Indomitable/Bardic Inspiration/Wild Shape verbrauchen) |
| `restore` | `"short"`, `"long"`, `null` — nur Anzeige-Text; der Rast-Knopf setzt alle Zähler zurück |
| `minLvl` | ab dieser Stufe sichtbar (fehlt = ab 1) |
| `conc` | `true` = Konzentrations-Abzeichen „C" am Tracker (nur bei echter Konzentration setzen; seit 27.09.2026, vorher Text-Heuristik, B9) |
| `pool` | `true` = **Pool-Zähler** (seit 27.09.2026): Zahlenfeld mit „/ Maximum", −/+ und Direkteingabe statt Pips; für große Punkte-/Würfel-/HP-Pools (Lay on Hands, Sorcery Points, Focus Points, Healing Light, Balm of the Summer Court). Gespeichert wird wie bei Pips der **Verbrauch** (`st.abUses[id]`), angezeigt der Rest. |
| `sub` | **Einzel-Tracker** (seit 27.09.2026): `[{k:"fire", l:"Fire Rune", uses?, minLvl?}, …]` → eine Pip-Zeile je Objekt unter dem Kartenkopf; `uses` fehlt = `uses` des Trackers (auch `{Stufe:Anzahl}`), `minLvl` = Objekt erst ab dieser Stufe. Verbrauch unter `st.abUses["<id>.<k>"]`. `k` ist wie die `id` heilig. Genutzt: `rk_runes` (Rune Knight), `wl_mysticarcanum`, `lu_waxingwaning`, `lu_lunarphenomenon`. |
| `pick` | nur mit `sub`, `uses`-Format (meist `{Stufe:Anzahl}`): so viele Objekte wählt der Charakter (☆/★ vor der Zeile, `st.abPick[id]=[k,…]`); ist etwas gewählt, zeigt die zugeklappte Karte nur die gewählten Objekte. Genutzt: Rune Knight Runes Known `{3:2,7:3,10:4,15:5}`. |
| `id` | eindeutig, klein, ohne Leerzeichen — **nie ändern** (verbrauchte Nutzungen hängen dran). Nicht mit `f_` beginnen (Präfix der Feature-Karten im Actions-Tab, B1c). Subklassen-Tracker mit Kürzel-Präfix (`ld_`, `tw_`, `bm_`, `pw_`, `gl_`, `gs_`, `hw_`, `ms_`, `fw_`, `sk_`, `dw_`, Fighter/Rune Knight `rk_` (`rk_runes`, `rk_giantsmight`, `rk_runicshield`), Paladin: `layonhands` (seit 27.09.2026), Sorcerer: `wm_`, `ds_`, `wms_`, `as_`, `cs_`, `dv_`, `sh_`, `st_`, `am_`, `cw_`, `lu_` (`lu_waxingwaning`, `lu_lunarphenomenon` seit 27.09.2026), Rogue: `ta_`, `iq_`, `sw_`, `ph_`, `sn_`, Monk: alle mit `mk_` (`mk_focuspoints`, `mk_oh_`, `mk_woh_`, `mk_wom_`, `mk_wm_`, `mk_ad_`), Barbarian: alle mit `bb_` (`bb_rage`, `bb_persistentrage`, `bb_bk_`, `bb_ag_`, `bb_zl_`, `bb_bs_`, `bb_wm_`), Warlock: alle mit `wl_` (`wl_pactslots`, `wl_magicalcunning`, `wl_contactpatron`, `wl_mysticarcanum` (seit 27.09.2026), `wl_af_`, `wl_fi_`, `wl_go_`, `wl_afp_`, `wl_fip_`, `wl_gop_`, `wl_cep_`, `wl_un_`, `wl_ce_`, `wl_hb_`, `wl_fa_`, `wl_ge_`, `wl_ud_`), Wizard: alle mit `wz_` (`wz_arcanerecovery`, `wz_signaturespells`, `wz_aj_`, `wz_sa_`, `wz_dv_`, `wz_sd_`, `wz_il_`, `wz_si_`, `wz_sc_`, `wz_se_`, `wz_sn_`, `wz_st_`, `wz_wm_`, `wz_cm_`, `wz_gm_`, `wz_bs_`, `wz_os_`), Bard: alte ids ohne Präfix (`bardicinspiration`, `cuttingwords` …), neue mit `bd_` (`bd_gl_`, `bd_wh_`), Druid: alte ids ohne Präfix (`wildshape`, `balmsc`, `fungalinfestation2` = Faithful Summons …), neue mit `dr_` (`dr_naturemagician`, `dr_st_`, `dr_dm_`) …) |
| `desc` | Klartext, Absätze mit `\n`, Aufzählung mit `• ` |

`abMaxUses(uses, lvl)` in der HTML wertet `uses` (und `pick`) aus.

## B3. Subklassen-Keys

- Dropdown-Namen tragen Quellen-Kürzel: `"Circle of the Moon (PHB)"`.
- Lookup: erst exakter Name, sonst Name **ohne** ` (XYZ)`. Beides funktioniert (Helfer `clsSubKey(obj, subcls)` seit 27.09.2026 für den Actions-Tab).
- **Konvention für neue Einträge:** Key **ohne** Kürzel (`"Life Domain"`).
- Ausnahme: gibt es eine Subklasse doppelt (PHB und XPHB mit verschiedenen Features), Key **mit** Kürzel.
- Bestehende Keys mit Kürzel (z. B. `"Circle of Dreams (XGE)"`) bleiben, wie sie sind (`build_class.py --rebuild` ordnet sie über `keep_keys` zu).
- Der gespeicherte Wert im Dropdown bleibt der alte Name (Namen sind heilig). **Angezeigt** wird über `SUBCLASS_LABELS` (neben `clsSpecial`) die Quelle der tatsächlich hinterlegten Fassung, z. B. Wert „Life Domain (PHB)" → Anzeige „Life Domain (XPHB)". Helfer: `subclsLabel(cls, sub)`.
- Eintrag in `SUBCLASS_LABELS` **nur**, wenn die Daten nachweislich diese Fassung sind (Feature-Namen und -Stufen gegen 5e.tools geprüft). Beim Einpflegen einer Klasse ergänzen: alle Subklassen, deren `subclassSources` (Kommentarzeile von `build_class.py`) von der Dropdown-Quelle abweicht (Sorcerer: nur „Shadow Magic (XGE)" → „Shadow Magic (RHW)"; Rogue: Arcane Trickster/Assassin/Thief (PHB) und Soulknife (TCE) → XPHB, Phantom (TCE) → RHW; die XGE-Subklassen bleiben; **Barbarian:** „Path of the Berserker (PHB)" → XPHB, „Path of the Zealot (XGE)" → XPHB, alle anderen stimmen überein; **Warlock:** nur „The Undead (VRGR)" → „The Undead (RHW)" (Daten = Undead Patron RHW), alle anderen stimmen überein; **Bard** (Neubau 27.09.2026): Lore/Valor (PHB) → XPHB, „College of Glamour (XGE)" → XPHB, „College of Spirits (VRGR)" → RHW; **Druid:** Land/Moon (PHB) → XPHB, Dreams/Shepherd (XGE) und Spores/Wildfire (TCE) stimmen überein; **Wizard:** School of Conjuration/Enchantment/Necromancy/Transmutation (PHB) → AU, „Bladesinging (TCE)" → FRHoF, alle anderen stimmen überein). **Monk:** Alle 14 Dropdown-Einträge stimmen mit der Quelle der Daten überein (Kommentarzeile) → kein Eintrag nötig.
- `SUBCLASS_SPELLS` (B5a) nutzt dieselben Keys wie `CLASS_DATA[k].subclass` und dieselbe Fassung (aus der Kommentarzeile).

## B4. `CLASS_TABLES` und `CLASS_CORE_TRAITS`

```js
CLASS_TABLES['Cleric']={
  extra:[{k:'channel',l:'Channel Divinity'},{k:'cantrips',l:'Cantrips'},{k:'prepared',l:'Prepared Spells'}],
  rows:[
    {lvl:1, pb:2, f:'Spellcasting, Divine Order', channel:'—', cantrips:3, prepared:4, slots:[2,0,0,0,0,0,0,0,0]},
    // … 20 Zeilen; f = Feature-Namen kommagetrennt, '—' wenn keins
  ]
};
```
- Wird von `build_class.py` aus `classTableGroups` erzeugt (Spalten-Key = erstes Wort des Labels, klein; Barbarian: `rages`, `rage` (= Rage Damage), `weapon`; Warlock: `invocations`, `cantrips`, `prepared`, `spell` (= Spell Slots der Pakt-Magie), `slot` (= Slot Level); Bard: `bardic` (Bardic Die als „1d6"), `cantrips`, `prepared`; Druid: `wild`, `cantrips`, `prepared`). Werte 0 → `'—'`. `slots` = genau 9 Zahlen (Halbzauberer: Quelle liefert 5 → wird mit 0 aufgefüllt; Warlock: keine `rowsSpellProgression` → alle 0). Würfel-Zellen (`type:"dice"`, Rogue Sneak Attack, Monk Martial Arts, Bard Bardic Die) werden zu `"3d6"`, Speed-Zellen (`type:"bonusSpeed"`, Monk Unarmored Movement) zu `"+10 ft."` (0 → `'—'`), Bonus-Zellen (`type:"bonus"`, Barbarian Rage Damage) zu `"+2"`.
- Nicht-Zauberer und Warlock: `slots` alle 0 → `buildClassTable` lässt Kopfzeile „Spell Slots per Spell Level" und die 9 Spalten weg (Fighter: nur Second Wind, Weapon Mastery; Rogue: nur Sneak Attack; Monk: Martial Arts, Focus Points, Unarmored Movement; Barbarian: Rages, Rage Damage, Weapon Mastery; Warlock: Invocations, Cantrips, Prepared Spells, Spell Slots, Slot Level).
- Seit 27.09.2026 liest auch der Actions-Tab (Karte „Combat Stats“, B1c) die `extra`-Spalten, `pb` und `slots` der aktuellen Stufe. Labels `l` dort ohne HTML schreiben.
- Wizard, Bard (27.09.2026, ohne `build_class.py` eingefügt) und Druid (handgebaut, andere Schreibweise mit Leerzeichen) werden von `--rebuild` **nicht** angefasst; `rebuild_diff.py` bestätigt, dass sie dem Konverter-Ergebnis entsprechen.

```js
CLASS_CORE_TRAITS["Cleric"]={
  hd:"d8", primaryAbility:"Wisdom",
  hpLevel1:"8 + Con modifier", hpPerLevel:"d8 (or 5) + Con modifier",
  savingThrows:["Wisdom","Charisma"],
  armorTraining:"…", weaponProficiencies:"…", toolProficiencies:"…",   // toolProficiencies weglassen, wenn keine
  skillProficiencies:{count:2, from:["History","Insight", …]},
  spellcastingAbility:"Wisdom",            // Nicht-Zauberer: ""
  startingEquipment:["(A) …","— or — … GP"],
  multiclassingReq:"Wisdom 13", multiclassingGains:"…",
  source:"PHB'24, page …"
};
```
Traits stehen in `<klasse>_config.py` unter `traits`, Werte aus den Feldern `hd`, `proficiency`, `startingProficiencies`, `startingEquipment`, `multiclassing`, `page` der XPHB-Klasse (Bard/Druid/Wizard: Traits nur in der HTML, Configs ohne `traits`). Die XPHB-Klasse hat **keine** `multiclassing.requirements`; Regel PHB'24: 13 im Hauptattribut (`primaryAbility`), z. B. Fighter „Strength or Dexterity 13" (deckt sich mit den PHB'14-`requirements`); Paladin (`primaryAbility` str **und** cha) „Strength 13 and Charisma 13"; Ranger (dex **und** wis) „Dexterity 13 and Wisdom 13"; Monk (dex **und** wis) „Dexterity 13 and Wisdom 13", `multiclassing` in der Quelle leer → `multiclassingGains: "None"`, `armorTraining: "None"`; Sorcerer „Charisma 13" (`multiclassing` in der Quelle leer → `multiclassingGains: "None"`, `armorTraining: "None"` wie beim Wizard); Rogue „Dexterity 13", Gains aus `multiclassing.proficienciesGained` („Light armor, Thieves' Tools, one skill from the Rogue skill list"); Barbarian „Strength 13", Gains „Martial weapons, Shields" (`proficienciesGained`: weapons martial, armor shield; d12, `armorTraining` „Light armor, Medium armor, Shields"); Warlock „Charisma 13", Gains „Light armor" (`proficienciesGained`: armor light; d8, `armorTraining` „Light armor", PHB'24 S. 152).

## B5. `ZB_SPELLS` – Format und Merge

Ein Eintrag (Feldnamen deutsch, Werte englisch):
```json
{"name":"Acid Splash","src":"PHB'24","grad":0,"school":"Evocation","zeit":"Action",
 "reichweite":"60 feet","dauer":"Instantaneous","komp":"V, S","classes":["Wizard"],
 "desc":"…","higher":"Cantrip Upgrade. …"}
```

| Feld | JSON-Feld | Format |
|---|---|---|
| `name` | `name` | unverändert |
| `src` | `source` | `PHB'24` für XPHB, sonst Kürzel (`XGE`, `TCE`, `FTD` …) |
| `grad` | `level` | Zahl 0–9 (Cantrip = 0) |
| `school` | `school` + `meta.ritual` | `Evocation`; Ritual: `Evocation (ritual)` |
| `zeit` | `time` | `Action`, `Bonus`, `Reaction`, `1 Min.`, `10 Min.`, `1 Hr.`, `8 Hr.` … |
| `reichweite` | `range` | `60 feet`, `Self` (auch für Kegel/Sphäre/Linie), `Touch`, `Sight`, `1 mile` … |
| `dauer` | `duration` | `Instantaneous`, `Concentration, up to 1 minute`, `Until dispelled`; mehrere: `… or … (see below)` |
| `komp` | `components` | `V, S, M (…)`, Royalty: `R (<Grad> gp)` |
| `classes` | gendata `class` + `classVariant` | nur eingepflegte Klassen (A2) |
| `desc` | `entries` | Absätze mit `\n\n`, benannte Blöcke `Name. Text`, Listen `• `, Tabellen zeilenweise mit ` | `, Zitate `“…”` + `— Autor` |
| `higher` | `entriesHigherLevel` | `Using a Higher-Level Spell Slot. …` / `Cantrip Upgrade. …`, Präfix „At Higher Levels." entfernt; leer `""` |

**Entscheidung (26.09.2026): Zauber kommen aus dem 5e.tools-JSON.** Abnahmetest `python3 spell_convert.py src zb_old.json` gegen den CSV-Bestand (501):
- `grad`, `school`, `zeit`, `reichweite`, `komp`: 501/501 identisch.
- `desc`/`higher`: 427 feldgenau; Rest nur Formatierung (CSV hatte Absätze uneinheitlich mit zwei Leerzeichen, Listen ohne `• `, Tabellen ohne Trenner zusammengeklebt) und 7 Errata/Tippfehler, die im aktuellen 5e.tools korrigiert sind (Enthrall jetzt Concentration, Transport via Plants 1 minute, „ends its turn" u. ä.).
- Bestandseinträge werden **nicht** umformatiert (Merge-Regel), neue Einträge kommen im JSON-Format (lesbare Tabellen).

**Merge-Regeln** (`spell_merge.py`)
- Schlüssel = `name` + `src`.
- Existiert → nur Klasse in `classes` ergänzen, sonst nichts anfassen.
- Neu → kompletter Eintrag anhängen, `classes:[Klasse]`.
- Nie löschen, nie umbenennen (Charaktere speichern Zauber per Name).
- Klassenzugehörigkeit: gendata `class` **und** `classVariant` (optionale Klassenlisten aus XGE/TCE), egal welche Klassen-Quelle.
- Quellen = `DEFAULT_SOURCES` in `spell_convert.py`: XPHB, XGE, TCE, FTD, FRHoF, AI, SCC, BMT, IDRotF, AAG, SatO, EGW, GGR, EFA. **Nicht:** PHB'14, AU, LLK, AitFR-AVT (wie der CSV-Bestand). Zauber mit `reprintedAs` (z. B. XGE → XPHB) werden übersprungen.
- Abweichung nur auf Simons Wunsch (z. B. AU-Zauber: Cleric hätte 4 zusätzliche – Dueling Ground, Grave Ground, Reweave Fate, Spirit Lantern; Ranger 2 AU-Zauber; Sorcerer 17 AU-Zauber; Warlock 23 AU- und 2 LLK-Zauber übersprungen, Liste in der Fixliste).
- Vollständigkeitsprobe nach dem Merge: Anzahl XPHB-Zauber der Klasse laut gendata = Anzahl `PHB'24` mit der Klasse in `ZB_SPELLS` (Paladin 51/51, Ranger 61/61, Sorcerer 150/150, Warlock 91/91).
- **Nach einem Merge neuer Zauber:** `bst_convert.py spells --write` neu laufen lassen, falls neue Zauber Kreaturen beschwören (B11).

## B5a. Spell-List-Filter „★ Meine Klasse“ (seit 27.09.2026)

**Oberfläche** (Tab Spell List, `slBuildFilters`/`slRender`): Klassen-Knöpfe „★ <Klasse>“ (id `slMineBtn`, Wert `mine`, **Standard**), „All“, dann `SL_CLASSES`. `slFClass` startet mit `'mine'`; „Clear all“ setzt wieder auf `'mine'`. Hat der Charakter keine eigenen Zauber (keine Klasse, Barbarian, Monk ohne Subklassen-Zauber), ist der ★-Knopf ausgeblendet und `mine` zeigt alles. Der Filter wird nicht gespeichert (bei jedem App-Start wieder ★).

**Was „meine Klasse“ umfasst** (`slMySpellCtx()` liest `cls`, `subcls`, `lvl`; `slMyVia(ctx, spell)`):
1. Feste Zusatzzauber (Subklasse bzw. Klassen-Zusatz ab `lvl`) → Abzeichen „✦ <Herkunft>“ (z. B. „✦ Oath of Devotion“, „✦ Gloom Stalker“), auch wenn der Zauber ohnehin auf der Klassenliste steht (zeigt „immer vorbereitet“).
2. Eigene Klassenliste: `ZB_SPELLS[].classes` ∩ `CLASS_SPELL_MAP[cls]` (Fighter/Rogue → Wizard) → ohne Abzeichen.
3. Filter-Zusätze (`grad`, `cls`, `school`, `src`; `slFilterHit`) → Abzeichen, z. B. „✦ Blessed Warrior“.

**Daten** (Block zwischen `// SUBCLASS_SPELLS-START` und `// SUBCLASS_SPELLS-END`, nicht von Hand ändern):
```js
const SUBCLASS_SPELLS={"Cleric":{"Life Domain":{"src":"XPHB","spells":["Aid","Bless",…]},
  "Arcana Domain":{"src":"AU","spells":[…],"filters":[{"grad":[0,6,7,8,9],"cls":["Wizard"]}]}}, …};
const CLASS_SPELL_EXTRA={"Paladin":[{"via":"Blessed Warrior","lvl":2,"grad":[0],"cls":["Cleric"]}],
  "Bard":[{"via":"Magical Secrets","lvl":10,"grad":[1,…,9],"cls":["Cleric","Druid","Wizard"]}], …};
```
- Keys = `CLASS_DATA[k].subclass`-Keys (B3); Zaubernamen exakt wie in `ZB_SPELLS` (Verbindung nur über den Namen).
- Subklassen-Zusätze gelten **ohne Stufenprüfung** (sobald die Subklasse gewählt ist); Klassen-Zusätze ab `lvl`.

**Erzeugen: `tools/subclass_spells.py`**
```bash
node dump.js DnD_Character_App.html          # cd.json mit ZB (Namen/Klassen), MAP, SUBS (Keys) – dump.js-Muster B9
python3 subclass_spells.py DnD_Character_App.html src [--show] [--write]
```
- Braucht `src/class-<k>.json` **aller 12 Klassen** und `src/feats.json`. `dump.js` für dieses Skript: `JSON.stringify({ZB:ZB_SPELLS.map(s=>({name:s.name,src:s.src,grad:s.grad,school:s.school,classes:s.classes})),MAP:CLASS_SPELL_MAP,SUBS:Object.fromEntries(Object.entries(CLASS_DATA).map(([k,v])=>[k,{list:v.subclassList,keys:Object.keys(v.subclass||{})}]))})`.
- **Fassung je Subklasse** aus der Kommentarzeile `// Quelle: 5e.tools class-<k>.json … neueste Fassung: Key=SRC, …` (von `build_class.py`), also dieselbe wie bei den Features. Gesucht wird Name + Quelle (2024-Anpassung `classSource XPHB` zuerst; `_copy` erbt `additionalSpells` vom Original); Nachdrucke unter neuem Namen über `reprintedAs` (Format `Kurzname|Klasse|KlassenQuelle|Quelle`, Suche über `shortName`).
- Aus 5e.tools `additionalSpells` (`prepared`, `known`, `expanded`, `innate`, beliebig verschachtelt: Stufen-Keys, `s1`…, `_`, `daily`, `resource`, mehrere Varianten wie Land-Typen/Genie-Arten → Vereinigung): Strings `name|quelle#c` → Name; `choose`/`all`-Filter (`level=…|class=…|school=…|source=…`) → `filters`. Filter nur über die eigene Klassenliste (Wizard-Schulen, Eldritch Knight/Arcane Trickster → Wizard) entfallen, Klassen-Zusätze, die schon auf der Klassenliste stehen, ebenso.
- Klassen-Ebene: Feats aus `FEAT_EXTRA` (Paladin → Blessed Warrior, Ranger → Druidic Warrior; Stufe = Feature „Fighting Style“ der XPHB-Klasse) und `additionalSpells` der XPHB-Klasse (`via` = Feature-Name der Stufe, dessen Text den Zauber bzw. die Klasse nennt).
- **Zauber, die nicht in `ZB_SPELLS` stehen, werden gemeldet, nicht eingefügt** (Quellenregel B5; Stand 27.09.2026: nur Hexblade „branding smite“, Fixliste).
- `--show` listet die Filter je Subklasse, `--write` ersetzt den Block (Anker eindeutig, sonst Abbruch). Neu erzeugen nach jedem Klassen-Neubau, neuen Subklassen oder Zauber-Merge.
- Stand 27.09.2026 (5e.tools `b9061583`): 81 Subklassen, 602 feste Zauber; Filter bei Bard College of Lore, Cleric Nature/Death/Arcana Domain, Sorcerer Divine Soul (ganze Cleric-Liste), Wizard Chronurgy/Graviturgy (EGW); Klassen-Zusätze Paladin, Ranger, Bard (Magical Secrets L10), Druid (Wild Companion → Find Familiar L2).

## B6. 5e.tools-Klassen-JSON aufbereiten (`class_extract.py`, `build_class.py`)

Struktur `class-<k>.json`: `class[]`, `classFeature[]`, `subclass[]`, `subclassFeature[]`. Referenzen: `Name|Klasse|KlassenQuelle|Stufe|FeatureQuelle` bzw. `Name|Klasse|KlassenQuelle|SubKurz|SubQuelle|Stufe|FeatureQuelle` (leere Quelle = PHB bzw. SubQuelle).

**Aufruf:** `python3 build_class.py DnD_Character_App.html src/class-<k>.json <k>_config.py`
- liest `subclassList` aus dem Stub der HTML, ruft `class_extract.extract` auf, ersetzt den Stub durch den vollen Block, fügt `CLASS_TABLES` und `CLASS_CORE_TRAITS` vorn ein. Funktioniert nur auf einem Stub (bereits befüllte Klasse → Anker fehlt → Abbruch).
- **Neubau einer befüllten Klasse (seit 27.09.2026):** `python3 build_class.py DnD_Character_App.html src/class-<k>.json <k>_config.py --rebuild` ersetzt nur den Block `CLASS_DATA["<K>"]={` … erste Zeile `};`. Übernimmt aus dem alten Block `special` (Druid `["beasts"]`), `subclassList` und die Subklassen-Keys (`keep_keys`: Extraktor-Key → vorhandener Key, auch mit Kürzel wie „Circle of Dreams (XGE)"); bricht ab, wenn ein alter Subklassen-Key oder eine alte Tracker-`id` fehlt oder eine `id` doppelt vorkommt. `CLASS_TABLES` und `CLASS_CORE_TRAITS` bleiben unverändert (Config ohne `traits` genügt). Genutzt für Bard, Druid, Wizard, am 27.09.2026 außerdem Paladin, Sorcerer, Monk, Warlock, Druid, Fighter (Pool-/Einzel-Tracker); geht ebenso für jede andere Klasse (z. B. nach einem 5e.tools-Update). **Danach `subclass_spells.py` neu laufen lassen (B5a).**
- Liegt `optionalfeatures.json` bzw. `feats.json` bzw. `items.json` im selben Ordner wie `class-<k>.json`, werden sie automatisch geladen (B6 Regeln).
- `<k>_config.py`: `CONFIG = {'class', 'trackers', 'traits'}`. Tracker je Gruppe (`base` oder Subklassen-Key **ohne** Kürzel, `--rebuild` ordnet zu) mit `feature` (Name im Extrakt), `id`, `icon`, `uses`, `restore`, optional `append` (Text eines Verbesserungs-Features anhängen, z. B. Sorcery Incarnate an Innate Sorcery, Eldritch Master an Magical Cunning, Font of Inspiration/Superior Inspiration an Bardic Inspiration, Master of Runes an Rune Carver), `tag` (Anzeige-Text, z. B. `'Bonusaktion'`)/`name` (überschreiben; Ranger: Dread Ambusher → „Dreadful Strike", Perfected Bond → „Reflexive Resistance"; Sorcerer: Font of Magic → „Sorcery Points"; Rogue: Psionic Power → „Psionic Energy Dice"; Monk: Monk's Focus → „Focus Points"; Warlock: Pact Magic → „Pact Magic Slots", Genie's Vessel → „Bottled Respite", Necrotic Husk → „Unholy Resuscitation"; Bard: Empowered Channeling → „Spiritual Manifestation"; Druid: Wild Resurgence → „Wild Resurgence → Spell Slot", Archdruid → „Nature Magician", Star Map → „Star Map: Guiding Bolt"; Wizard: Shape-Shifter → „Shape-Shifter: Polymorph" u. ä.). `desc` und `minLvl` kommen automatisch aus dem Feature (der Actions-Tab erkennt darüber, welches Feature schon eine Tracker-Karte hat, B1c). Dasselbe Feature darf mehrere Tracker speisen (Fighter: Psionic Power → „Psionic Energy Dice" und „Telekinetic Movement"; Wizard: Manifest Mind → „Manifest Mind" und „Manifest Mind: Spellcasting"). Vorlagen: alle 12 `<k>_config.py`. Optional (seit 27.09.2026): `'feature_tags': {Gruppe: {Feature-Name: 'Passiv'|'Aktion'|'Bonusaktion'|'Reaktion'}}` überschreibt die Tag-Heuristik für Info-Tab **und** Tracker (Barbarian, Rogue, Warlock, Bard, Wizard), Tracker-Feld `'conc': True` setzt das Konzentrations-„C" (Fighter Telekinetic Master, Warlock Dark Delirium/Grasping Tentacles, Bard Mantle of Majesty, Wizard Event Horizon), `'pool': True` = Pool-Zähler (Vorlagen `paladin_config.py`, `sorcerer_config.py`, `monk_config.py`, `warlock_config.py`, `druid_config.py`), `'sub': [{'k','l','uses'?,'minLvl'?}]` = Einzel-Tracker je Objekt und `'pick': {Stufe:Anzahl}` = Auswahl (Vorlagen `fighter_config.py` RUNES, `warlock_config.py` ARCANUM, `sorcerer_config.py` MOON). `apply_feature_tags`/`build_trackers`/`keep_keys` liegen in `build_class.py` und werden von `rebuild_diff.py` importiert.
- Steht ein Feature mehrfach in der Klasse (Fighter: Action Surge 2/17, Indomitable 9/13/17; Warlock: Mystic Arcanum 11/13/15/17), nimmt der Tracker die **erste** Fundstelle (`minLvl` = Einstiegsstufe); die Steigerung kommt über `uses:{Stufe:Anzahl}` bzw. `sub[].minLvl`.

**Regeln im Extraktor**
- **Klasse:** XPHB-Fassung; Features aus `class.classFeatures`, Einträge „Subclass Feature" entfallen (wie Druid). Das Stufe-3-Feature „<Klasse> Subclass" bleibt als normales Feature stehen (Cleric, Rogue, Monk, Barbarian, Warlock, Wizard, Bard, Druid …). Mehrfach gelistete Features (gleicher Text auf mehreren Stufen) bleiben mehrfach, wie in der 5e.tools-Tabelle.
- **Subklassen = neueste Fassung für die 2024-Klasse:** nur Subklassen mit `classSource XPHB`, davon die ohne `reprintedAs`. Alt-Subklassen (PHB'14, XGE, TCE, DMG …) nutzt 5e.tools als `_copy` mit **angepassten Stufen** (1→3, 2→3, Stufe-8-Feature Divine Strike/Potent Spellcasting entfällt); genau diese Fassung wird übernommen. Die Anpassung erbt das `reprintedAs` des Originals (so wird z. B. „Life Domain (PHB)" von „Life Domain" XPHB abgelöst). **Nachdruck unter neuem Namen** (Sorcerer, Monk, Warlock, Wizard): Findet sich kein Kandidat ohne `reprintedAs`, schaut der Extraktor aufs Nachdruck-Ziel. Steht das Ziel **selbst im Dropdown** (Draconic Bloodline → Draconic Sorcery, Wild Magic → Wild Magic Sorcery, Aberrant Mind → Aberrant Sorcery, Clockwork Soul → Clockwork Sorcery; Monk: Way of the Open Hand → Warrior of the Open Hand, Way of Shadow → Warrior of Shadow, Way of the Four Elements → Warrior of the Elements, Way of Mercy → Warrior of Mercy; Barbarian: Path of the Totem Warrior → Path of the Wild Heart; Warlock: The Archfey → Archfey Patron, The Fiend → Fiend Patron, The Great Old One → Great Old One Patron, The Celestial → Celestial Patron; Wizard: School of Abjuration/Divination/Evocation/Illusion → Abjurer/Diviner/Evoker/Illusionist), bleibt die alte Fassung (5e.tools-Anpassung) – sonst gäbe es zwei identische Einträge. Steht es **nicht** im Dropdown (Shadow Magic XGE → Shadow Sorcery RHW; Warlock: The Undead VRGR → Undead Patron RHW; Bard: College of Spirits VRGR → RHW; Wizard: School of Conjuration/Enchantment/Necromancy/Transmutation → Conjurer/Enchanter/Necromancer/Transmuter AU, Bladesinging TCE → Bladesinger FRHoF), folgt er der Kette; der Key bleibt der Dropdown-Name, `SUBCLASS_LABELS` zeigt die neue Quelle (B3). Neuere Nachdrucke gewinnen (Cleric: Knowledge=FRHoF, Grave=RHW, Arcana=AU, Life/Light/Trickery/War=XPHB; Fighter: Battle Master/Champion/Eldritch Knight/Psi Warrior=XPHB, Arcane Archer=AU, Banneret=FRHoF; Paladin: Devotion/Ancients/Vengeance/Glory=XPHB, Oathbreaker=DMG, Crown=SCAG, Conquest/Redemption=XGE, Watchers=TCE; Ranger: Beast Master/Hunter/Gloom Stalker/Fey Wanderer=XPHB, Horizon Walker/Monster Slayer=XGE, Swarmkeeper=TCE, Drakewarden=FTD; Sorcerer: Draconic Sorcery/Wild Magic Sorcery/Aberrant Sorcery/Clockwork Sorcery=XPHB, Draconic Bloodline/Wild Magic=PHB (2014-Text, Stufen angepasst), Divine Soul/Storm Sorcery=XGE, Aberrant Mind/Clockwork Soul=TCE, Lunar Sorcery=DSotDQ, Shadow Magic=RHW; Rogue: Arcane Trickster/Assassin/Thief/Soulknife=XPHB, Inquisitive/Mastermind/Scout/Swashbuckler=XGE (2014-Text, Stufen angepasst), Phantom=RHW; Monk: Warrior of the Open Hand/Shadow/the Elements/Mercy=XPHB, Way of the Open Hand/Shadow/the Four Elements=PHB (2014-Text, Stufen angepasst), Way of Mercy/Astral Self=TCE, Long Death=SCAG, Drunken Master/Kensei/Sun Soul=XGE, Ascendant Dragon=FTD; Barbarian: Berserker/Wild Heart/World Tree/Zealot=XPHB, Totem Warrior=PHB (2014-Text, Stufen angepasst), Battlerager=SCAG, Ancestral Guardian/Storm Herald=XGE, Beast/Wild Magic=TCE, Giant=BGG; Warlock: Archfey/Fiend/Great Old One/Celestial Patron=XPHB, The Archfey/Fiend/Great Old One=PHB und The Celestial=XGE (2014-Text, Stufen angepasst), The Undying=SCAG, The Hexblade=XGE, The Fathomless/Genie=TCE, The Undead=RHW; Bard: Lore/Valor/Dance/Glamour=XPHB, Swords/Whispers=XGE, Creation/Eloquence=TCE, Spirits=RHW; Druid: Land/Moon/Sea/Stars=XPHB, Dreams/Shepherd=XGE, Spores/Wildfire=TCE; Wizard: Abjurer/Diviner/Evoker/Illusionist=XPHB, School of Abjuration/Divination/Evocation/Illusion=PHB (2014-Text, Stufen angepasst), School of Conjuration/Enchantment/Necromancy/Transmutation=AU, War Magic=XGE, Chronurgy/Graviturgy=EGW, Bladesinging=FRHoF, Order of Scribes=TCE).
- **Einleitungs-Feature** (Name = Subklassenname): Flavor-Text und Götter-Tabellen entfallen; enthaltene Refs werden eigene Features; Zauber-Tabelle alter Subklassen → Feature „Domain Spells" (bzw. Tabellen-Caption, Warlock: „Expanded Spell List", Druid Spores/Wildfire: „Circle Spells").
- **Text aus `entries`:** rekursiv; benannte Blöcke → `Name. …`, `list`/`options` → `• `, `table` → `• Spalte1: Spalte2` (2 Spalten) bzw. `|`-Zeilen, Fußnoten angehängt, `refClassFeature`/`refSubclassFeature` inline als `Name: Text` (z. B. Divine Spark in Channel Divinity). Zeilen „1st-level … feature" (groß/klein egal, z. B. „14th-Level Lunar Sorcery Feature") entfallen.
- **`refOptionalfeature`** (Manöver, Runen, Arcane Shots, Eldritch Invocations …): mit `optionalfeatures.json` als `• Name (Level N+). Text` (Stufe aus `prerequisite`), ohne nur `• Name`. In `options` kein doppeltes `• `.
- **`refFeat`** (Paladin Fighting Style → Blessed Warrior): mit `feats.json` als `• Name. Text`, ohne nur `• Name`.
- **`statblock` mit `tag:"item"`** (Rogue/Soulknife → Psychic Blade): mit `items.json` als eine Zeile `• Name: Simple Melee weapon; 1d6 Psychic damage; Finesse, Thrown (range 60/120); Vex mastery (…).` (Waffenkategorie, Schaden, Eigenschaften, Mastery); ohne `items.json` nur `• Name`. Eigenschafts- und Schadenskürzel stehen in `PROP`/`DMG` in `class_extract.py` – unbekannte Kürzel → KeyError, dann erweitern.
- **Tags entfernen:** `{@tag Text|Quelle|Anzeige}` → Anzeige-Text, sonst erster Teil; Sonderfälle `dc`, `hit`, `chance`, `atk`, `classFeature`, `quickref`, `deity`. Unbekannte entry-Typen → Fehler (Konverter erweitern, nicht raten).
- **Feature-`tag`:** früheste Fundstelle im Text (groß/klein egal): „Bonus Action" → `Bonusaktion`, „Reaction" → `Reaktion`, „Magic action/an action/your action" → `Aktion`, sonst `Passiv`. Trifft das daneben (Psionic Power, Monk's Focus, Eldritch Invocation Options), im Tracker `tag` in der Config überschreiben (Barbarian: Persistent Rage → „Passiv", Consult the Spirits → „Aktion"); für Info-Tab-Features `feature_tags` in der Config (27.09.2026: Devious Strikes, Form of the Beast, Infectious Fury, Rage of the Gods, Eldritch Invocation Options, Bewitching Magic; Neubau: Bard Combat Inspiration/Extra Attack/Battle Magic/Dazzling Footwork/Blade Flourish, Wizard Spell Mastery/Arcane Ward (Abjurer)/Improved Illusions/Necromancy Spellbook/Wondrous Alteration/Arcane Abeyance/Extra Attack/Song of Victory/Master Scrivener). Seit dem Combat-Tab-Umbau bestimmt der `tag` auch die Gruppe im Actions-Tab (B1c) – ein falscher Tag zeigt sich also dort.
- **Tabellen-Zellen in `build_class.py`:** `dice` → „1d6" (Summe der Würfel), `bonusSpeed` → „+10 ft." bzw. `—` bei 0, `bonus` → „+2"; andere Objekt-Zellen fehlen noch (dann erweitern).
- **Tracker:** nur Features mit Nutzungszahl/Rast im Text oder mit Verbrauch einer anderen Ressource (`uses:null`); Werte aus Text/Class Table übernehmen, nicht schätzen. **Pool-Ressourcen** (Punkte/Würfel/HP, groß oder stufenabhängig: Lay on Hands, Sorcery/Focus Points, Healing Light, Balm) mit `pool:true`; kleine Würfel-Pools (Zealot Warrior of the Gods, max. 7) bleiben Pips. **Pro-Objekt-Nutzungen** (jede Rune einzeln, Mystic Arcanum je Grad, je Mondphase) mit `sub` (seit 27.09.2026). Features, die nur Sorcery Points/Focus Points kosten, nicht. Ebenso „einmal pro Rage" (Barbarian: Fanatical Focus, Travel Along the Tree), „einmal pro Zug" und Zähler mit steigendem DC (Relentless Rage). **`conc` nur, wenn der 5e.tools-Text Konzentration nennt** (B9). Features ohne Tracker erscheinen seit 27.09.2026 trotzdem im Actions-Tab (als Feature-Karte, B1c).

## B7. Savegames (localStorage `dnd5e_chars`)

- Objekt `{Charaktername: {…Zustand, log:[…]}}`.
- Formularfelder aus `TEXT_IDS` (u. a. `cls`, `subcls`, `race`, `lvl`, `bg`) als Text.
- Zauber: `st.mySpells = [{name, grad, school, prep, notes, freeMax…}]` → Verbindung zu `ZB_SPELLS` nur über `name`. `st.zbAdded` (Set der `ZB_SPELLS`-Indizes, „✓ On Sheet“) wird vom Spell-List-Tab genutzt – trotz Präfix `zb` kein toter Code.
- Feats: `st.feats` per `name`. Tracker-Verbrauch: `st.abUses[id]` (Pips **und** Pool-Zähler = verbrauchte Menge; Einzel-Tracker unter `st.abUses["<id>.<k>"]`, z. B. `"rk_runes.fire"`, `"wl_mysticarcanum.7"`). Auswahl bei Einzel-Trackern mit `pick`: `st.abPick[id] = [k, …]` (seit 27.09.2026; der Reset-Knopf lässt sie stehen). Zauberplätze: `st.slotMax`, `st.slotUsed` (Verbrauch; seit 27.09.2026 zeigen die Kreise den Rest, B1c). Bestien: `st.savedBeasts` (Liste der **ganzen** Bestien-Objekte vom Speicherzeitpunkt; seit 28.09.2026 zeigt `buildSavedBeasts` trotzdem immer die aktuellen Daten aus `BST_DATA`, Nachschlag per Name `n`, Rückfall auf das gespeicherte Objekt). Attribute: `st.attrs` (`STR` … `CHA`).
- **Zugeklappte Gruppen im Actions-Tab:** `st.abGrpClosed = {<gruppe>: true|false}` (seit 27.09.2026, pro Charakter; fehlt = „Weitere“ und die Karte „Combat Stats“ (`stats`) zu).
- Der Spell-List-Filter (`slFClass` usw.) wird **nicht** gespeichert. Ebenso nicht: aufgeklappte Karten und aufgeklappte Stat-Blöcke.
- **Gerätebezogen, nicht im Charakter:** `dnd5e_theme_overrides` (eigene Farben je Klassen-Theme, Keys wie `COLOR_LABELS`, seit 27.09.2026 auch `desc`, `muted`) und `willow_textsize` (`normal|gross|sehrgross`, seit 27.09.2026, B1d).
- `applyState` setzt erst Defaults, dann den Save → neue Felder sind abwärtskompatibel (`st.abPick`/`st.abGrpClosed` fehlen in alten Saves → Defaults `{}`). **Neue `st`-Felder immer in alle drei Default-Blöcke aufnehmen** (`applyState`, `resetUI`, Neuanlage; Anker `abUses:{},abPick:{},abGrpClosed:{},savedBeasts:[]`), sonst bleibt beim Charakterwechsel der Wert des vorigen Charakters stehen (B9). **Umbenennen/Löschen von Namen ist es nicht.**
- Ein Tracker darf beim Neubau ein anderes Feature bekommen, solange die `id` bleibt (Bard `talesfrombeyond` → Spirits from Beyond, `spiritsession` → Spiritual Manifestation; Wizard `wz_st_shapechanger` → Shape-Shifter): Alte Saves behalten dann nur den Pip-Stand. Ebenso darf ein Tracker von Pips auf `pool:true` wechseln (Sorcery Points u. a., 27.09.2026): Der gespeicherte Verbrauch bleibt gültig.

## B8. Prüfskript `tools/app_check.js`

```bash
npm i jsdom@24                         # einmal pro Sitzung
node app_check.js NEU.html ALT.html    # ALT optional
```
1. JS-Syntax.
2. Lädt die App (simulierter Browser), schaltet jede Klasse × Subklasse × Stufe 1/5/20 durch, meldet JS-Fehler. Tabelle: Subklassen (mit Features), Features, Karten im Actions-Tab bei L20 (seit 27.09.2026 `.ab-card` statt direkter Kinder von `#abList`, inkl. Gruppe „Weitere“), Class Table, Traits, Beasts-Tab.
2b. **Regressionstests** aus der Liste `REGRESSION` (oben im Skript), in frisch geladener App.
3. Vergleicht alle Datenblöcke alt/neu (seit 27.09.2026 auch `SUBCLASS_SPELLS`, `CLASS_SPELL_EXTRA`; seit 28.09.2026 `SPELL_STATBLOCKS`): neu/geändert/gelöscht. **Gelöschte Zauber, Bestien, Klassen- oder Subklassen-Keys, Tracker-`id`s oder `special`-Marker = Fehler** (ids/special seit 27.09.2026).

Ergebnis muss „ERGEBNIS: alles OK" sein, sonst nicht ausliefern.

**Regressionstest ergänzen** (neuester unten in `REGRESSION`):
```js
{ name: 'Was nicht wieder kaputtgehen darf', datum: 'TT.MM.JJJJ',
  run: ({w, d, set, vis, CD, sel}) => {
    sel('Bard', 'College of Lore (PHB)', 5);          // Klasse, Subklasse, Stufe wählen
    const ok = d.getElementById('abList').textContent.includes('Cutting Words');
    return ok || 'Beschreibung, was fehlt';           // true = bestanden
  } },
```
Helfer: `sel(cls, sub, lvl)` wählt und rendert neu · `set(id, wert)` setzt ein Feld · `vis(id)` prüft Sichtbarkeit · `w.eval('…')` greift auf App-Variablen zu (z. B. `st`, `st.attrs.CON=16`) · `CD` = `CLASS_DATA` · global `abAmt(d, name)` = Menge eines Trackers (Pips bzw. bei Pool-Zählern das Maximum „/ N"; seit 27.09.2026 für Sorcery/Focus Points, Healing Light, Balm statt `pips()`). Speichern prüfen: `w.eval("document.getElementById('charName').textContent='Regressionstest'")`, dann `JSON.parse(w.localStorage.getItem('dnd5e_chars')).Regressionstest`; Laden prüfen: `w.eval('applyState(JSON.parse(localStorage.getItem("dnd5e_chars")).Regressionstest)')`. Spell List prüfen: `w.slRender()`, dann `#slList .zb-card` (Name `.zb-name`, Herkunft `.sl-via`); Zauber-Stat-Block: `#sld_<index>` enthält `details.sb-det`, My Spells `#msn_<i>`. Beasts prüfen: `w.switchTab('bestien')`, dann `#bstList .zb-card` (Stat-Block `.sb`, Attribute `.sb-abrow .sb-ab`, Abschnitte `.sb-sec`), gespeicherte Bestien `#bstSavedList` nach `w.buildSavedBeasts()`. Actions-Tab prüfen: `#combatStats .cst-chip` (Label `.cst-l`, Wert `.cst-v`), Gruppen `#abList .ab-grp[data-grp]` bzw. `.ab-grp-box[data-grp="passiv"]`/`[data-grp="weitere"]`, Feature-Karten `.ab-card.ab-feat`. Pips: `.ab-pip` zählt alle Kreise (= Maximum), `.ab-pip.avail` = gefüllt/verfügbar, `.ab-pip.used` = leer/verbraucht; Zauberplätze `#spSlots .slvl .slpip.av` / `.slpip.u`. Farben: `d.documentElement.style.getPropertyValue('--desc')` nach `w.applyTheme(cls)`; CSS-Regeln über den Text der `<style>`-Elemente. Untere Leiste: `#bottomNav .bnav-btn` (Beschriftung `.bnav-label`, Symbol `.bnav-icon`), Eltern-Kette eines Panels über `d.getElementById('tab-…').parentElement.className`. **jsdom rechnet kein Layout** (keine Breiten, kein `zoom`) → Überlauf nur mit `ui_shots.py` prüfen.
Neuen Test immer gegen eine Kopie **mit** dem alten Fehler laufen lassen: Er muss dort ✘ melden, sonst prüft er nichts. Bei einer neuen Klasse genügt dafür `node app_check.js ALT.html` (ohne die Klasse): Der Test meldet „Testdaten fehlen". Bei einer Korrektur bestehender Daten: `node app_check.js ALT.html` (die unveränderte Version) muss ✘ melden (Fixliste Sonnet: Wild Shape L6, Rage mit „C"; Neubau: Circle of Dreams Stufe 3; Pool-/Einzel-Tracker: „Lay on Hands fehlt", Kopie ohne `autoSave` in `togAbUse`: „Pip-Klick nicht gespeichert"; Zauber-Auswahl: „Klassenfilter fehlt"; Combat-Tab: „Kampfwerte-Karte fehlt"; Actions: „Gruppe ‚Weitere‘ fehlt“; UI: „107× Schriftgröße unter 11px“, „themeBase fehlt“; Text-Formatierer: „fmtDesc fehlt“; Sonnet-Kleinkram: „schwebender Würfel-Knopf noch vorhanden“, „tab-bestien ist kein Kind von .body“; Paket A: „Stat-Block-Anzeige fehlt (sbHtml/SPELL_STATBLOCKS)“).

**Sichtprüfung (seit 27.09.2026): `tools/ui_shots.py` und `tools/theme_shots.py`** (Playwright + Chromium; `python3 -m playwright install chromium`, falls nötig; Browser liegen meist unter `/opt/pw-browsers`).
```bash
python3 ui_shots.py DnD_Character_App.html OUTDIR [normal|gross|sehrgross]   # alle Tabs + ⚙, Testcharakter Druid L7
python3 theme_shots.py DnD_Character_App.html OUTDIR                          # Actions-Ausschnitt je Klassen-Theme (13)
```
- `ui_shots.py`: 390 px breit (Faktor 2), je Tab ein Foto (erste ~1700 px, Actions zusätzlich `zauber2.png` ab Class Features, `nav.png` = untere Leiste, `settings.png`), **Überlauf-Prüfung**: jedes sichtbare Element, dessen rechter Rand über 390 px liegt und das nicht in einem Scroll-Container steckt (→ `check.json`, Ausgabe „überlauf N“); dazu Höhe der Leisten-Beschriftungen (einzeilig) und Höhe der Leiste (seit dem angehobenen Würfel-Knopf 71/83/93 px in Normal/Large/X-Large). Die untere Leiste wird für die Ganzseiten-Fotos ausgeblendet (sonst mitten im Bild). Die dritte Angabe setzt die Textgröße über `localStorage.willow_textsize`. **Pflicht bei UI-Änderungen: alle drei Stufen ohne Überlauf.**
- Vorher/Nachher-Bilder für Simon: Fotos der alten (`ALT.html`) und neuen Version mit PIL nebeneinander setzen (je 390 px breit, Überschrift darüber) und mit SendUserFile schicken; erst nach Simons OK veröffentlichen. Für einzelne Karten (Text-Formatierer 27.09.2026, Stat-Blöcke 28.09.2026): kleines Playwright-Skript, das je Fall Klasse/Stufe setzt, die Karte aufklappt (`togAb('<id>')`, Feature-Karten `f_b_<name>`; Bestien: `switchTab('bestien')`, Karte über `.zb-name` suchen und `.zb-top` klicken; Zauber: `switchTab('spelllist')`, `slTog(ZB_SPELLS.findIndex(…))`, `details.open=true`) bzw. `#clsLoreBody` sichtbar schaltet (startet zugeklappt, `display:none`) und `element.screenshot()` macht. Überlauf dabei mit `getBoundingClientRect().right > 390.5` über alle Kinder prüfen (alle Karten aufgeklappt, alle drei Textgrößen). Für die untere Leiste: Viewport-Foto ohne `clip` machen und mit PIL zuschneiden (`clip` außerhalb des Viewports schlägt fehl).
- Einzelne Stellen: Seite `file:///…/DnD_Character_App.html` öffnen, Klasse per `onClsChange()`/`onSubclsChange()` setzen, Actions-Tab mit `switchTabAll('zauber')` öffnen (Tab-Buttons: `data-tab="zauber"` = Actions), Spell List: `switchTab('spelllist')`, Filter per Klick auf `#slGradRow .fbtn[data-val="1"]` usw. (Variablen direkt setzen ändert die Knopf-Markierung nicht). Google Fonts sind im Sandbox-Netz gesperrt (Ersatzschrift, egal).

Bisherige Tests: Liste in `docs/ARCHIV.md` (Abschnitt „B8 – bisherige Regressionstests“, seit 28.09.2026 ausgelagert).

**Konverter-Neubauprobe `tools/rebuild_diff.py`** (seit 26.09.2026): baut **alle 12 Klassen** (seit 27.09.2026 auch Wizard, Bard, Druid) mit dem aktuellen `class_extract.py` (+ Tabellen-Logik aus `build_class.py`) im Speicher neu und vergleicht Features (Name, Stufe, `desc`, `tag`) und Class Table mit der App. Subklassen-Keys mit Kürzel werden über `keep_keys` zugeordnet.
```bash
node exp_all.js      # exportiert CLASS_DATA + CLASS_TABLES der App nach all.json (Skript steht als Kopf in rebuild_diff.py)
python3 rebuild_diff.py   # braucht src/class-<k>.json aller 12 Klassen + optionalfeatures/feats/items.json
```
Pflicht **nach jeder Konverter-Änderung**: Ergebnis muss „SUMME 0" sein, sonst betrifft die Änderung schon eingepflegte Klassen (dann bewusst neu bauen oder Änderung eingrenzen). Neue Klassen in die Liste im Skript aufnehmen; neue Tabellen-Zelltypen dort ebenfalls ergänzen. Braucht `build_class.py` (Import) und liest `<k>_config.py`, falls vorhanden: dann werden `feature_tags` angewandt und die **Tracker** (alle Felder, auch `pool`, `sub`, `pick`) verglichen. Pflicht-Configs: `barbarian_config.py`, `rogue_config.py`, `warlock_config.py`, `bard_config.py`, `wizard_config.py` (sonst Tag-Abweichungen); für den Tracker-Vergleich einer Klasse deren Config dazulegen. Stand 27.09.2026: SUMME 0 (alle 12, mit 10 Configs).

## B9. Bekannte Stolperfallen

Wächst mit jedem Debugging. Vor Code-Arbeit kurz lesen.

- **Riesige Einzeilen** (`ZB_SPELLS`, `BG_EXTRA`, `FT_FEATS`, `BST_DATA`, auch `CLASS_THEMES`, `SUBCLASS_SPELLS`, `SPELL_STATBLOCKS`): Ausgabe von grep/sed immer mit `cut -c1-200` kürzen, sonst ist der Kontext sofort voll.
- **Regex über die HTML täuscht:** Ein Regex nach Klassennamen trifft auch verschachtelte Keys. Welche Keys ein Datenblock hat, immer zur Laufzeit prüfen: in jsdom `w.eval('Object.keys(CLASS_TABLES)')`. `ZB_SPELLS` für Analysen per jsdom als JSON exportieren (`zb_old.json`); `CLASS_DATA`/`CLASS_TABLES` ebenso als `cd.json` (kleines `dump.js`: `new JSDOM(html,{runScripts:'dangerously'})`, 500 ms warten, `w.eval('JSON.stringify({CD:CLASS_DATA,CT:CLASS_TABLES})')`) – so lassen sich Features/Tags/Tracker per Python auswerten, ohne die HTML zu lesen.
- **Node-Ausgabe über 64 KB per Pipe wird abgeschnitten** (28.09.2026): `process.stdout.write(big); process.exit(0)` in einem von Python per `subprocess.check_output` gestarteten `node -e` liefert nur die ersten 65 536 Zeichen („JSONDecodeError … char 65532“), weil `process.exit` vor dem Leeren der Pipe beendet. Große JSON-Exporte immer mit `fs.writeFileSync(datei, …)` in eine Datei schreiben (so `dump()` in `bst_convert.py`).
- **Zahlenformat in der HTML:** `build_class.py` schreibt Arrays mit Leerzeichen (`slots:[2, 0, 0, …]`); Regex für Testkopien mit `, 0` statt `,0`. Die handgebaute Druid-Tabelle schreibt `slots:[2,0,0,…]` ohne Leerzeichen.
- **Subklassen-Namen:** Dropdown mit Kürzel, Daten-Keys meist ohne (B3). Jeder neue Lookup braucht den Fallback „Kürzel abschneiden" (`clsSubKey`).
- **Zwei `tag`-Konventionen** (B2): Features = Anzeige-Text, Tracker = Schlüssel. Nicht „vereinheitlichen". In `<k>_config.py` wird `tag` als Anzeige-Text angegeben, `build_class.py` übersetzt. Der Actions-Tab übersetzt Feature-Tags selbst (`Aktion`→`aktion`, `Bonusaktion`→`bonus`, `Reaktion`→`reaktion`, sonst `passiv`; Ausschlussliste → `weitere`).
- **Tags korrigieren:** bei Konverter-Klassen (seit dem Neubau alle 12) über `feature_tags` in der Config **und** in der HTML (sonst meldet `rebuild_diff.py` Abweichungen) – am einfachsten Config ändern und die Klasse mit `--rebuild` neu bauen. Von Hand: In der HTML steht `tag:"…"` **nach** dem langen `desc` des Features; Anker = `{lvl:N,name:"…"` und das nächste `tag:"alt"` dahinter ersetzen (Eindeutigkeit des Ankers prüfen, Abstand begrenzen). Tracker-Tags: Anker `{id:"…"`.
- **Handgeschriebene Kurztexte waren unzuverlässig** (Neubau 27.09.2026): Die alten Bard-/Druid-Tracker hatten Zusammenfassungen statt 5e.tools-Text; daraus entstanden falsche „C"-Marker (Unbreakable Majesty, Animating Performance, Spirit Totem) und falsche `uses` (Cutting Words/Unsettling Words/Mantle of Inspiration als CHA-Zähler statt BI-Verbrauch, Cauterizing Flames ohne Zähler). Tracker-Werte immer aus dem Feature-Text der aktuellen Quelle ableiten. **Gleiches galt für den alten `BST_DATA`-Bestand** (vor 28.09.2026): Tags nur halb übersetzt („m 3“, `{@h}`), Traits/Actions nach ~150 Zeichen abgeschnitten → Bestien nie von Hand reparieren, sondern mit `bst_convert.py` neu erzeugen (B11).
- **Feature-Namen exakt wie im Extrakt** (Groß-/Kleinschreibung): „Lay on Hands", nicht „Lay On Hands" – sonst KeyError in `build_trackers`. Im Zweifel in `cd.json` nachsehen. Gilt auch für `COMBAT_SKIP_NAMES` (B1c).
- **Class Table:** Zauberplatz-Spalten nur, wenn irgendein `slots`-Wert > 0 (A5). Halbzauberer liefern nur 5 Slot-Grade (B4). Tabellenzellen können Objekte sein (`type:"dice"`, `type:"bonusSpeed"`, `type:"bonus"`), nicht nur Zahlen/Strings – `build_class.py` wandelt sie in Text um; ein neuer Zellentyp landet sonst als `[object Object]` in der Tabelle **und** in der Karte „Combat Stats“ (Prüfen: `CLASS_TABLES.<k>.rows[n]`).
- **Warlock-Spalte „Spell Slots" ≠ Zauberplatz-Kopfzeile:** Die Pakt-Spalte heißt wie die Kopfzeile der 9 Zauberplatz-Spalten („Spell Slots per Spell Level"). Tests „keine Zauberplatz-Spalten" beim Warlock deshalb auf das Element `.ct-grp` prüfen, nicht auf den Text „Spell Slots". In „Combat Stats“ ist „Spell Slots“ beim Warlock ein Chip (`.cst-chip`), bei Zauberern die Grad-Reihe (`.cst-slot`).
- **Mehrfache Features** (Action Surge, Indomitable, ASI, Mystic Arcanum) haben denselben Namen → Lookups nach Namen nehmen die erste Fundstelle (B6); der Actions-Tab fasst sie zu einer Karte zusammen (B1c).
- **Actions-Tab: `#abList` enthält seit 27.09.2026 Gruppen-Köpfe (`.ab-grp`) und -Boxen (`.ab-grp-box`)**, die Karten liegen eine Ebene tiefer, und neben Tracker-Karten gibt es Feature-Karten (`.ab-card.ab-feat`, ohne Pips). Seit „Actions“ stehen auch die ausgeschlossenen Features als Karten in `.ab-grp-box[data-grp="weitere"]` → Tests, die „Feature X darf nicht erscheinen“ prüfen, müssen „Weitere“ ausnehmen (`!x.closest('.ab-grp-box[data-grp="weitere"]')`). Tests, die per `startsWith(name)` die erste Karte suchen, können eine Feature-Karte mit ähnlichem Namen treffen – für Tracker ggf. `:not(.ab-feat)` nutzen. Tracker ↔ Feature werden über Namen **oder** Text erkannt (erste 200 Zeichen des Feature-`desc` im Tracker-`desc`); wer einen Tracker-`desc` von Hand kürzt, bekommt das Feature doppelt.
- **Handler ohne `input`-Event** (Buttons mit `onclick`) lösen kein Speichern/Log aus → neue Buttons brauchen `autoSave()`. **Bis 27.09.2026 betraf das auch die Tracker** (`togAbUse`, `restoreAllUses`): Pip-Klicks wurden erst beim nächsten Tippen in ein Feld gespeichert. Seitdem rufen `togAbUse`, `abPoolAdj`, `abPoolSet`, `togAbPick`, `restoreAllUses` und (seit Actions, weil der Zustand jetzt pro Charakter gespeichert wird) `togAbGrp` `autoSave()` auf (Regressionstest).
- **`applyState`/`resetUI`/Neuanlage nutzen `Object.assign(st, Defaults, Save)`:** Felder, die in den Defaults fehlen, bleiben vom **vorigen Charakter** stehen, wenn der neue Save sie nicht hat. So blieb bis 27.09.2026 `st.abPick` (Runen-Auswahl) beim Charakterwechsel hängen. Seit Actions stehen `abPick:{}` und `abGrpClosed:{}` in allen drei Default-Blöcken; neue `st`-Felder dort ebenfalls ergänzen (B7).
- **Pips zeigen seit 27.09.2026 den Rest, nicht den Verbrauch:** `.ab-pip.avail`/`.slpip.av` = gefüllt = verfügbar, `.used`/`.u` = leer. Tippen ist nicht mehr positionsabhängig (gefüllt → −1, leer → +1). Gespeichert bleibt der Verbrauch. Death Saves (`dsS`/`dsF`) und Inspiration (`ins`) sind absichtlich **nicht** umgedreht.
- **Pool-Zähler zeigt den Rest, speichert den Verbrauch** (`st.abUses[id]`): Neue Pool-Tracker brauchen nichts Besonderes; ein Wechsel Pips ↔ Pool bricht keine Saves. Steigt das Maximum (Stufenaufstieg), bleibt der Verbrauch → Rest wächst mit.
- **`buildAbilities` baut die Liste komplett neu:** Aufgeklappte Karten (`.ab-body.on`, auch Feature-Karten `ab_f_…`) werden vorher gemerkt und wieder geöffnet (seit 27.09.2026); neue Klick-Handler, die `buildAbilities()` aufrufen, bekommen das automatisch.
- **jsdom:** Nach dem Laden ~400 ms warten, bevor getestet wird; `onClsChange()`/`onSubclsChange()` nach dem Setzen der Dropdowns selbst aufrufen. jsdom rechnet **kein Layout** (Breiten 0, `zoom` wirkungslos) → Überlauf und Aussehen nur mit Playwright (`ui_shots.py`). Reine CSS-Änderungen (z. B. der angehobene Würfel-Knopf) testet `app_check.js` nur über den Text der `<style>`-Regel.
- **Schriftgrößen (seit 27.09.2026):** nur noch über `--fs-*` unter 16 px (B1d). Ein neues `font-size:10px` lässt den Regressionstest scheitern. Beim Patchen von Stellen, die vorher `font-size:13px` o. ä. hatten: Der Anker enthält jetzt `var(--fs-md)` usw.
- **CSS `zoom` (Textgröße) skaliert in Chromium auch `vh`:** `max-height:88vh` wird bei 130 % zu ~114 % der Bildschirmhöhe. Deshalb `calc(88vh / var(--zf))` (Würfel-Dialog, Notiz-Dialog); neue `vh`-Höhen genauso schreiben. `getBoundingClientRect` liefert unter `zoom` Werte in Bildschirm-Pixeln (390 bleibt die Breite), `document.body.scrollWidth` dagegen in CSS-Pixeln (339 bzw. 300 bei Large/X-Large). Neue Raster mit festen Spalten (`repeat(3,1fr)`) bei X-Large prüfen (effektiv nur ~272 px Inhaltsbreite) – lieber `repeat(auto-fill,minmax(…))`. Ausnahme: die sechs Attribut-Kästen im Stat-Block (`.sb-abrow`, `repeat(6,minmax(0,1fr))`, Wunsch Simon „in einer Reihe“) passen auch bei X-Large (geprüft 28.09.2026); „Save +12“ darf dort umbrechen.
- **Späte CSS-Nachträge:** Der Block `/* ── UI / Lesbarkeit (27.09.2026)` steht am Ende des Style-Blocks und überschreibt Grundregeln (z. B. `.hbtn`, `.slpip`, `.fbtn`). Wer eine Grundregel oben ändert und sich wundert, dass nichts passiert: unten nachsehen.
- **Farben (seit 27.09.2026):** `--text3` ist jetzt **Gold** (Labels) und `--purple` **helles Gold** (Highlight) – für Platzhalter, inaktive Leiste und Leere-Liste-Hinweise `--muted` nehmen, für Beschreibungen `--desc` (B1d). Grundwerte kommen aus `themeBase`, nicht direkt aus `CLASS_THEMES`; wer `CLASS_THEMES[cls]` direkt liest, bekommt die alten Werte ohne `desc`/`muted`.
- **Texte nie mehr roh einsetzen** (seit 27.09.2026): `${f.desc}` in `innerHTML` ist ungeschützt und zeigt keine Struktur → immer `fmtDesc(f.desc, …)` (B1e). Tests, die Text in Karten suchen, finden ihn weiter über `textContent`; Blocknamen stehen jetzt in `.fd-n`, Tabellenwerte `.fd-tv` hängen am Text dran (bei `textContent`-Vergleichen beachten). Eine Zeile wie „Liste:“ gilt als Überschrift (`.fd-cap`), nicht als Absatz.
- (**Bis 28.09.2026**, seitdem liegen Skripte und Doku im Repo `tools/`/`docs/` und werden per Git übertragen) **`project_write` mit `local_path`** verlangt eine Datei **im Arbeitsverzeichnis** (bei geklontem Repo `willow/`): Dateien nach `willow/_proj/` kopieren und `_proj/` in `.git/info/exclude` eintragen (nicht committen). `local_path` **absolut** angeben (`/home/claude/willow/_proj/…`), ein relativer Pfad wurde am 27.09.2026 nicht gefunden.
- (**Bis 28.09.2026**, seitdem liegen Skripte und Doku im Repo `tools/`/`docs/` und werden per Git übertragen) **Md nie „zusammenfassen“ beim Zurückschreiben** (27.09.2026): `project_write` ersetzt die ganze Datei, eine frühere Fassung ist danach nicht mehr abrufbar. Abschnitte, die sich nicht ändern, wörtlich übernehmen – nie durch „unverändert, siehe frühere Fassung“ ersetzen. Sicherster Weg: `project_read`-Antwort per Skript auf die Platte legen (Trick unten) und nur gezielt per Python-`rep()` ändern; danach Länge alt/neu vergleichen.
- **HTML „nur 256 KB sichtbar" ist ein Werkzeug-Limit, keine kaputte Datei.** HTML aus Willow laden, per Python ändern (B1a), nie mit Read/Edit.
- (**Bis 28.09.2026**, seitdem liegen Skripte und Doku im Repo `tools/`/`docs/` und werden per Git übertragen) **Pfade variieren je Sitzung:** HTML aus Willow, Skripte per `project_read` aus dem Projekt holen und mit Write auf die Platte legen, nicht auf alte Pfade verlassen. `project_read` liefert auch große Dateien nur inline (kein lokaler Pfad) → jede Datei kostet Kontext (die drei Skripte `class_extract.py`, `build_class.py`, `app_check.js` machen zusammen ~45 KB, `app_check.js` allein inzwischen ~78 KB); nur holen, was gebraucht wird (die Md selbst nur lesen, nicht doppelt). Für reine Datenkorrekturen ohne Konverter und für reine UI-Umbauten reichen `app_check.js`, `ui_shots.py` und ein eigenes Patch-Skript. Für `rebuild_diff.py` genügen die Pflicht-Configs (B8), Kommentare/Traits darin sind für die Probe entbehrlich. Trick gegen Abschreibfehler: den `content`-String aus der `project_read`-Antwort (JSON-kodiert, mit `\n`/`\"`) als Heredoc in eine Datei legen und mit `python3 -c "import json;open('x','w').write(json.load(open('x.raw')))"` dekodieren.
- **Nutzungslimit mitten in der Sitzung:** Der Arbeitsordner (HTML, Skripte, `src/`) bleibt erhalten, solange der Container läuft; beim Weitermachen zuerst `ls` + `git fetch` prüfen statt neu anzufangen.
- **Service-Worker-Cache:** Die installierte App liefert immer zuerst die gespeicherte Version. Ohne neuen `CACHE_NAME` kommt ein Update auf dem Handy nie an (B1a Schritt 5). **Seit 27.09.2026 (`4030ce4`):** Die `index.html` registriert den Worker wieder (Block `// SERVICE WORKER` am Skriptende; fehlte seit dem Upload vom 03.06.2026 – nur früher installierte Geräte hatten ihn noch). Der Worker lädt beim Installieren mit `cache: "reload"` (sonst kann GitHubs 10-Minuten-Browser-Cache die alte `index.html` in den neuen Cache schreiben), und bei `controllerchange` lädt die Seite einmal neu (nur bei Update, nicht bei Erstinstallation) → neue Version erscheint beim ersten Öffnen. Registrierung und Reload nicht entfernen (Regressionstest).
- **Dateiname in Willow ist `index.html`** (GitHub Pages, Service Worker und Manifest erwarten ihn). Lokal heißt die Arbeitskopie `DnD_Character_App.html`.
- **Nicht vergessen zu pushen = nächster Chat arbeitet auf altem Stand.** Deshalb A11 Punkt 5.
- **Lange Chats:** Ältere Tool-Ausgaben werden gekürzt. Werte vor Verwendung neu prüfen statt aus dem Gedächtnis.
- **5e.tools-Subklassen gibt es mehrfach** (Original, `_copy` für die 2024-Klasse, Nachdrucke). Nie die erste Fundstelle nehmen – Auswahl nach B6. Namen können sich ändern (SCAG „Purple Dragon Knight (Banneret)" → FRHoF „Banneret"; XGE „Shadow Magic" → RHW „Shadow Sorcery"; VRGR „The Undead" → RHW „Undead Patron"; PHB „School of Necromancy" → AU „Necromancer"; TCE „Bladesinging" → FRHoF „Bladesinger"); maßgeblich ist der Dropdown-Name ohne Kürzel. Neue Bücher (z. B. AU = Arcana Unleashed, 15.09.2026) können nach einem 5e.tools-Update weitere Nachdrucke bringen → `rebuild_diff.py` zeigt das als Abweichung.
- **`reprintedAs` hat bei Subklassen nur 4 Teile** (`Kurzname|Klasse|KlassenQuelle|Quelle`, z. B. `Shadow|Sorcerer|XPHB|RHW`) → Ziel über `shortName` + `source` suchen, nicht über `name` (`subclass_spells.py`, 27.09.2026).
- **`_copy` erbt `reprintedAs` des Originals** – das ist gewollt (sonst zwei Kandidaten bei Cleric/Fighter/Paladin/Ranger/Druid/Bard: „AssertionError … Life Domain (PHB) … PHB, XPHB"). Nachdrucke unter neuem Namen regelt der Rückfall in B6. **Nach jeder Extraktor-Änderung** alle eingepflegten Klassen gegenprüfen: Subklassen-Fassungen müssen der Kommentarzeile `// Quelle: … neueste Fassung: …` in der HTML entsprechen (Opus-Check Sorcerer: erste Fassung des Rückfalls hätte alle anderen Klassen gebrochen).
- **`classes` in `ZB_SPELLS` ist kein vollständiges Klassen-Verzeichnis** (nur eingepflegte Klassen). Aussagen wie „Klasse X lückenhaft" immer gegen gendata prüfen (so war „Cleric lückenhaft" falsch).
- **`restore` ist nur ein Label**; „Short Rest: 1 Nutzung zurück" (Channel Divinity, Second Wind, Psionic Energy Dice, Rage, Wild Shape) und „gegen Sorcery Points/Pact-Magic-Slot/Zauberplatz zurückkaufen" lassen sich nicht abbilden → steht im `desc` (bei Pool-Zählern mit „+" von Hand, bei Pips leeren Kreis antippen). Bardic Inspiration zeigt „Short" (ab L5 laut Font of Inspiration).
- **Alt-Subklassen (DMG/SCAG/XGE/TCE/EGW/PHB'14) behalten ihre 2014-Formulierung** („Starting at 7th level, the paladin …"), nur die Stufen sind angepasst – das ist 5e.tools-Stand, kein Fehler (Ranger: Horizon Walker, Monster Slayer; Sorcerer: Draconic Bloodline, Wild Magic, Divine Soul, Storm Sorcery; Rogue: Inquisitive, Mastermind, Scout, Swashbuckler; Monk: Way of the Open Hand/Shadow/Four Elements, Long Death, Drunken Master, Kensei, Sun Soul, Way of Mercy, Astral Self, Ascendant Dragon – 2014-Ki-Punkte, „ki point" statt „Focus Point"; Barbarian: Totem Warrior, Battlerager, Ancestral Guardian, Storm Herald, Beast, Wild Magic, Giant; Warlock: The Archfey, The Fiend, The Great Old One, The Celestial, The Undying, The Hexblade, The Fathomless, The Genie – „Starting at 1st level" im Text trotz Stufe 3; Bard: Swords, Whispers, Creation, Eloquence; Druid: Dreams, Shepherd, Spores, Wildfire; Wizard: School of Abjuration/Divination/Evocation/Illusion, War Magic, Chronurgy, Graviturgy, Order of Scribes).
- **Dropdown ≠ neueste Subklassen:** 5e.tools kennt für den Ranger auch Winter Walker (FRHoF) und Hollow Warden (RHW), für den Sorcerer Spellfire Sorcery (FRHoF), Shadow Sorcery (RHW) und Pyromancer (PSK), für den Monk Warrior of the Mystic Arts (AU), für den Warlock Vestige Patron (AU), für den Bard College of the Moon (FRHoF); sie stehen nicht im Dropdown (Stub vorhanden, Namen heilig) und wurden nicht ergänzt.
- **Monk-Dropdown enthält beide Fassungen** (Way of the Open Hand (PHB) **und** Warrior of the Open Hand (XPHB) usw.): zwei getrennte Keys in `CLASS_DATA.Monk.subclass`, beide befüllt. Nicht zusammenlegen (Savegames). Gleiches beim **Warlock** (The Archfey (PHB) **und** Archfey Patron (XPHB) usw.) und beim **Wizard** (School of Abjuration (PHB) **und** Abjurer (XPHB) usw.).
- **Zauber-Filter: Nur der Spell-List-Tab ist Oberfläche.** Der frühere zweite Zauber-Browser (`zbRender`, `zbBuildFilters`, `zbMakeCard`, `zbTog`, `zbAdd`, Elemente `zbQ`/`zbList`) war toter Code und ist seit 27.09.2026 entfernt; `CLASS_SPELL_MAP` wirkt jetzt über `slMySpellCtx` (B5a). `st.zbAdded` bleibt (wird von `slAdd`/`delMySpell` genutzt).
- **Konzentrations-Abzeichen „C" am Tracker** kommt seit 27.09.2026 **nur noch** aus dem Feld `conc:true` (`buildAbilities`: `isConc=ab.conc===true`; eine gespeicherte Markierung `st.concActiveFeature` auf einem Tracker ohne `conc` wird ignoriert). Vorher Text-Heuristik („concentration" im `desc`), die auch bei Verneinungen anschlug (Rage). Neue Tracker mit echter Konzentration brauchen `conc:true` (Config-Feld `'conc': True`). Gesetzt bei: Mantle of Majesty, Dark Delirium, Grasping Tentacles, Event Horizon, Telekinetic Master. Nicht bei Fey Reinforcements/Dragon Companion (Konzentration dort abwählbar), Starry Form, Spirit Totem, Unbreakable Majesty, Animating Performance (laut Text keine Konzentration). Feature-Karten im Actions-Tab haben kein „C“.
- **Tracker-`id` `channeldivinity` gibt es bei Cleric und Paladin** (je Klasse getrennt, ein Charakter hat nur eine Klasse → unkritisch). Neue `id`s trotzdem mit eigenem Präfix wählen (Monk: `mk_`, Barbarian: `bb_`, Warlock: `wl_`, Wizard: `wz_`, Bard: `bd_`, Druid: `dr_`).
- **`uses:{Stufe:Anzahl}` unterhalb der ersten Stufe = 0 Pips** (`abMaxUses`) → Karte ohne Zähler sichtbar, sofern kein `minLvl` gesetzt ist; bei Features, die erst später beginnen (Wild Shape ab L2), `minLvl` mitsetzen (kommt beim Konverter automatisch aus der Feature-Stufe). Absichtlich genutzt bei Lunar Embodiment `{3:1,6:0}` (ab L6 Karte ohne Zähler).
- **Subklassen-Key ≠ Quelle bei Barbarian:** „Path of the Berserker (PHB)" und „Path of the Zealot (XGE)" im Dropdown zeigen die XPHB-Fassung (Labels, B3); „Path of the Totem Warrior (PHB)" ist der 2014-Text mit angepassten Stufen (Spirit Seeker/Totem Spirit auf Stufe 3).
- **`build_class.py --rebuild` sucht das Blockende als erste Zeile `};`** nach `CLASS_DATA["<K>"]={`. Steht im Block eine Zeile, die mit `};` beginnt (z. B. verschachteltes Objekt am Zeilenanfang), bricht der Neubau mit „Blockgrenzen unklar" ab bzw. schneidet falsch → vorher `grep -n` prüfen.
- **Sitzung über Mitternacht:** App-Version nach dem Datum der Veröffentlichung benennen (Warlock: begonnen 26.09., veröffentlicht als `willow-app-2026-09-27a`; Paket A: begonnen 27.09., veröffentlicht als `willow-app-2026-09-28a`).
- **Regex-Strings in Python-Patch-Skripten:** In normalen (nicht `r'…'`) Python-Strings wird `\\s` zu `\s` im JS – für JS-Regex-Literale im Patch doppelt escapen oder Raw-Strings nutzen, sonst landet `s*` statt `\s*` in der HTML (Combat-Tab-Umbau 27.09.2026 geprüft).
- **Python-`rep()` mit `global s`, nie mit Default-Argument `s=s`** (27.09.2026): `def rep(alt,neu,s=s)` bindet `s` einmalig beim Definieren an den ursprünglichen Inhalt; jeder weitere Aufruf rechnet wieder gegen diesen alten Stand, und nur die letzte Ersetzung überlebt – ohne Fehlermeldung. Immer die Vorlage aus B1a Schritt 3 nehmen und nach mehreren Ersetzungen per `grep` prüfen, ob alle angekommen sind.
- **Überzähliges `</div>` verschiebt alles danach** (27.09.2026): Eine zusätzliche `</div>` nach `<!-- CUSTOM FEATURES -->` schloss `.body` vorzeitig; die Panels `tab-bestien`, `tab-feats`, `tab-spelllist`, `tab-notizen`, `tab-log` hingen dadurch direkt an `.app` (ohne 14-px-Seitenrand, Spell List mit großem Leerraum oben). Bei „Tab X hat keinen Seitenrand, andere schon“ zuerst die Eltern-Kette prüfen (`el.parentElement.className`, Regressionstest), nicht die CSS-Regeln. Verschachtelung zählen: kleines Python-Skript, das `<div`/`</div>` zählt und an jedem HTML-Kommentar die Tiefe ausgibt (Achtung: `.app` schließt ebenfalls vor `<nav>`).
- **Monster-Tags in 5e.tools** (28.09.2026, `bst_convert.py`): 2024-Kreaturen nutzen `{@atkr m}` („Melee Attack Roll:“), `{@actSave dex}` + `{@dc 13}`, `{@actSaveFail}` (ggf. mit Zahl: „Second Failure:“), `{@recharge 5}` → „(Recharge 5–6)“; 2014-Kreaturen `{@atk mw}`; Beschwörungs-Geister (XPHB/TCE) `{@atk m}`, `{@hitYourSpellAttack …}` und `summonSpellLevel` in `{@damage}`/`{@hit}` → „the spell's level“. Spellcasting-Blöcke haben `hidden` (z. B. `["daily"]`) – versteckte Listen nicht anzeigen, sonst stehen Zauber doppelt (Unicorn's Blessing). `displayAs` bestimmt den Abschnitt (action/bonus/reaction/legendary, fehlt = trait).
- **Ranger-Begleiter nutzen `summonClassLevel`** (noch nicht in `bst_convert.py`, Fixliste Paket A2): vor dem Einbau am 5e.tools-Renderer prüfen, wie der Platzhalter angezeigt wird.

## B11. Stat-Blöcke: `BST_DATA`, `SPELL_STATBLOCKS`, `bst_convert.py`, `sbHtml` (seit 28.09.2026)

Entstanden in Paket A (`402df00`/`…28a`). Daten kommen nur aus dem 5e.tools-Bestiarium; die Anzeige ist für Bestien und Zauber-Kreaturen dieselbe.

**Eintrag** (Bestie oder Zauber-Kreatur; alte Felder wie vor Paket A, neue nur wenn gefüllt):
```js
{"n":"Owl","type":"beast","size":"T","cr":"0","ac":"11","hp":"1 (1d4 - 1)","spd":"5 ft., fly 60 ft.",
 "str":3,"dex":13,"con":8,"int":2,"wis":12,"cha":7,"skills":"Perception +5, Stealth +5",
 "sens":"Darkvision 120 ft., Passive Perception 15",
 "actions":["Talons: Melee Attack Roll: +3, reach 5 ft. Hit: 1 Slashing damage."],
 "traits":["Flyby: The owl doesn't provoke Opportunity Attacks when it flies out of an enemy's reach."],
 "fluff":"", "tt":"Beast", "al":"Unaligned", "init":1}
```
| Feld | Inhalt |
|---|---|
| `n` | Name (heilig: Schlüssel für `st.savedBeasts`, B7) |
| `type` | Filter-Typ im Beasts-Tab (`beast`/`fey`/`celestial`); bei `bst` wird der **alte** Wert übernommen |
| `size` | `T`/`S`/`M`/`L`/`H`/`G` (`SIZE_MAP`), mehrere mit `/` |
| `cr` | Zeichenkette (`"1/4"`); bei Beschwörungs-Geistern `""` (keine CR-Zeile) |
| `ac`, `hp`, `spd` | Text (Beschwörungen: „12 + the spell's level“, „30 + 10 for each spell level above 3“) |
| `str` … `cha` | Zahlen |
| `skills`, `sens` | Text; `sens` endet mit „Passive Perception N“ |
| `traits`, `actions` | Liste `"Name: Text"`, Text mit `\n` (Absätze) und `• ` (Listen, z. B. Spellcasting „• At Will: …“, „• 1/Day Each: …“) |
| `fluff` | kursive Tagline aus `fluff-bestiary-xmm.json` (14 Kreaturen), sonst `""` |
| `tt` | Typzeile („Celestial (Angel)“, „Swarm of Tiny Beasts“, „Celestial or Fiend (Titan)“) |
| `al` | Gesinnung („Unaligned“, „Lawful Good“) |
| `init` | Initiative-Modifikator (Zahl; DEX-Mod. + `initiative.proficiency` × Übungsbonus der CR, wie 5e.tools); Anzeige „+1 (11)“ |
| `saves` | `{dex:"+5", …}` nur geübte Rettungswürfe; Anzeige im Attribut-Kasten „Save +5“ |
| `res`, `vuln`, `imm` | Text; `imm` = Schadens- und Zustands-Immunitäten, getrennt durch „; “ |
| `gear`, `lang` | Text |
| `bonus`, `react` | Listen wie `actions` (Bonus Actions, Reactions) |
| `legend` | Liste: erstes Element = Kopfsatz („Legendary Action Uses: 3. …“, ohne Namen), danach `"Name: Text"` |
| `crl` | CR mit Hort (falls vorhanden) |
| `src` | nur in `SPELL_STATBLOCKS`: Quelle der Kreatur (`XPHB`, `TCE`, `XMM`, `MM` …) |

**`SPELL_STATBLOCKS`** = `{Zaubername: [Eintrag, …]}` (eine Zeile direkt nach `BST_DATA`). Schlüssel exakt wie `ZB_SPELLS[].name`. `ZB_SPELLS` selbst bleibt unverändert.

**Anzeige** (Abschnitt `// ── STAT-BLOCK (Paket A, 27.09.2026) ──` nach `SIZE_MAP`):
- `sbHtml(b)` → `<div class="sb">`: Typzeile `.sb-sub` (Größe + `tt` + `al`), `.sb-fluff`, Zeilen `.sb-ln` (AC · Initiative, HP, Speed, danach Skills, Vulnerabilities, Resistances, Immunities, Gear, Senses, Languages, CR), sechs Attribut-Kästen `.sb-abrow > .sb-ab` (Label, Wert, Modifikator, ggf. Save), Abschnitte `.sb-sec` (Traits, Actions, Bonus Actions, Reactions, Legendary Actions). Fehlende alte Felder (`tt`/`al` in alten gespeicherten Objekten) → Rückfall aus `type`.
- `sbEntry(text, ohneName)`: trennt `Name: ` ab (Name kursiv-fett `.sb-en`), Zeilen → `<p>`, `• ` → `<ul class="sb-ul">` (Listen-Name „Fuming.“ ebenfalls `.sb-en`); `sbLbl` setzt feste Labels kursiv (`.sb-l`, Regex `SB_LBL`: „Melee Attack Roll:“, „Hit:“, „Dexterity Saving Throw:“, „Failure:“, „Success:“, „Trigger:“, „At Will:“, „1/Day Each:“ …). Text immer über `fdEsc` (HTML-sicher). **Nicht** `fmtDesc` (der würde „Melee Attack Roll:“ als Blockname fett setzen).
- `spellStatBlocks(name)` → Überschrift „Stat Block“ bzw. „Stat Blocks (N)“ (`.sb-hd`) + je Kreatur `<details class="sb-det">` (Kopf „📜 Name QUELLE“, zu Beginn zugeklappt, `onclick` stoppt das Zuklappen der Zauberkarte). Eingesetzt in `slMakeCard` (nach „At Higher Levels“) und `buildMySpells` (nach `higherHtml`).
- `bstMakeCard(b)` nutzt `sbHtml(b)`; Kopf (Name, Typ, CR, Größe) und Knöpfe „🐾 Add to My Beasts“/„📖 5e.tools →“ unverändert. `buildSavedBeasts` rendert `BST_DATA.find(x=>x.n===b.n)||b`.
- CSS: Block `/* ── Stat-Block (Paket A, 27.09.2026)` am Ende des Style-Blocks; nur Variablen (B1d).

**Erzeugen: `tools/bst_convert.py`**
```bash
npm i jsdom@24                                                   # für den Export aus der App (dump())
python3 bst_convert.py bst    DnD_Character_App.html src [--write]   # BST_DATA neu (Namen/Reihenfolge/type aus der App)
python3 bst_convert.py spells DnD_Character_App.html src [--write]   # SPELL_STATBLOCKS neu
```
- `bst`: liest die aktuellen Namen aus der App, sucht jeden in `bestiary-xmm.json` (Name + `XMM`), Tagline aus `fluff-bestiary-xmm.json`; bricht ab, wenn ein `{@`-Rest bleibt. Ausgabe: Anzahl geänderter alter Felder und Fluff-Abweichungen. Neue Bestien kämen durch Ergänzen der Namensliste hinzu (nur auf Simons Wunsch).
- `spells`: für jeden Zauber in `ZB_SPELLS` (Quelle `PHB'24` → `XPHB`) die `{@creature Name|Quelle}`-Verweise in `entries`/`entriesHigherLevel` (Quelle leer = `MM`), Kreatur aus allen `src/bestiary-*.json`. **`EXAMPLES`** (Summon Lesser Demons, Summon Greater Demon, Infernal Calling) werden übersprungen: Dort sind die Kreaturen nur Beispiele einer freien Wahl. Fehlt eine Kreatur im Bestiarium, meldet das Skript „FEHLT im Bestiarium“. Stand 28.09.2026: 26 Zauber, 48 Stat-Blöcke; Homunculus Servant (EFA) fehlt, weil der Zauber nicht in `ZB_SPELLS` steht.
- `convert(m, fluff, keep_type)` wandelt jeden 5e.tools-Monster-Eintrag um (auch für spätere Begleiter, Fixliste Paket A2). Unbekannte Tags (`Unbekannter Tag`), entry-Typen, Speed-Felder oder Spellcasting-Felder → Fehler, Konverter erweitern (Tag-Regeln B9 „Monster-Tags“). `_copy` wird aufgelöst (ohne `_mod`, sonst Fehler).
- `--write` ersetzt die ganze Zeile `const BST_DATA=` bzw. `const SPELL_STATBLOCKS=` (Anker eindeutig). Danach `app_check.js` (Datenvergleich: keine Bestie darf fehlen).
- **Neu laufen lassen:** nach einem 5e.tools-Update (Bestiarium), nach einem Zauber-Merge (B5) oder wenn neue Kreaturen-Zauber dazukommen.
