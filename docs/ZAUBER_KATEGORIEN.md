# Zauber-Kategorien (Bilder in My Spells)

Seit 01.10.2026 (Wunsch Simon). Jeder Zauber in My Spells zeigt links ein Bild in einem runden Rahmen, wie die Feature-Karten im Actions-Tab. Das Bild steht für den **Hauptzweck** des Zaubers.

**Wichtig:** Die Kategorie ist **keine 5e.tools-Angabe**, sondern eine Einordnung nach Hauptzweck. Grundlage sind die 5e.tools-Markierungen und der Zaubertext; Fehlgriffe der Regeln stehen in einer festen Korrekturliste. Viele Zauber können mehreres, gezeigt wird nur der Hauptzweck.

## Kategorien und Bilder

| Schlüssel | Kategorie | Bild | Was fällt darunter? | Beispiele |
|---|---|---|---|---|
| `dmg:<typ>` | Schaden | nach Schadenstyp (s. u.) | Einzelziele oder mehrere Gegner verletzen | Fireball 🔥, Magic Missile ✴️ |
| `ctrl` | Kontrolle | ⛓️ | Gegner festhalten, behindern, Handlungen einschränken | Entangle, Hold Person, Web |
| `buff` | Stärkung / Buffs | 💪 | Verbündete stärker, schneller, besser machen | Bless, Haste, Guidance |
| `debuff` | Schwächung / Debuffs | 🥀 | Gegner schwächen, Erfolgschancen senken | Bane, Bestow Curse, Faerie Fire |
| `prot` | Schutz & Heilung – Schutz | 🛡️ | Schaden verhindern, Abwehr, Schutzzonen | Shield, Counterspell, Mage Armor |
| `heal` | Schutz & Heilung – Heilung | 💚 | Lebenspunkte wiederherstellen, Zustände entfernen | Cure Wounds, Healing Word, Lesser Restoration |
| `summon` | Beschwörung | 🐾 | Zusätzliche Wesen oder Helfer ins Spiel bringen | Summon Beast, Find Familiar, Conjure Animals |
| `move` | Bewegung & Positionierung | 🌀 | Teleportieren, fliegen, Kreaturen versetzen | Misty Step, Fly, Vortex Warp |
| `info` | Information & Kommunikation | 🔮 | Magie erkennen, Wissen gewinnen, Nachrichten | Detect Magic, Sending, Speak with Animals |
| `social` | Täuschung & soziale Einflussnahme | 🎭 | Wahrnehmung verändern, täuschen, Personen beeinflussen | Disguise Self, Suggestion, Charm Person |
| `util` | Hilfsmagie | 🪄 | Praktische Magie für Probleme außerhalb des Kampfes: Zaubertricks, Erschaffen und Formen, Öffnen, Unterschlupf, Sonderfälle (Wish, Time Stop) | Druidcraft, Mending, Light, Knock, Rope Trick |

„Schutz & Heilung“ ist eine Kategorie mit zwei Bildern, weil Shield und Healing Word sich im Spiel sehr unterscheiden.

**Schadenstypen** (alle 13 aus D&D 5e):
🔥 fire · ❄️ cold · ⚡ lightning · 💥 thunder · 🧪 acid · ☠️ poison · 💀 necrotic · ☀️ radiant · ✴️ force · 🧠 psychic · 🗡️ slashing · 🏹 piercing · 🔨 bludgeoning · 🌈 `multi` = drei oder mehr Typen bzw. frei wählbar (Chromatic Orb, Chaos Bolt …). Bei zwei Typen wird der thematisch passende gewählt (Ice Storm ❄️, Flame Strike 🔥), ggf. per Korrektur.

**Rahmenfarbe** = Zeit wie bei den Features: rot Action, gold Bonus Action, blau Reaction, neutral alles andere (1 Minute, 1 Stunde …). Einstellbar in ⚙ unter „Icons (Features & Spells)“ (gilt auch für die Feature-Icons und die Gruppenpunkte im Actions-Tab).

## Wo steht was?

| Ort | Inhalt |
|---|---|
| `tools/spell_cats.py` | Regeln (`regel()`), Korrekturliste `KORREKTUREN`, schreibt `const SPELL_CATS` in die HTML |
| `tools/spell_cats_geprueft.txt` | Namen aller Zauber, deren Kategorie schon geprüft ist |
| HTML `const SPELL_CATS={"Name":"kat"}` | Ergebnis (eine Zeile direkt vor `const BG_DATA=`), Namen = `ZB_SPELLS[].name` |
| HTML `SPELL_CAT_ICONS`, `SPELL_CAT_NAMES`, `spellIconHtml()` | Bilder, Namen (Tooltip, englisch) und Anzeige; bei `setPrep` in `buildMySpells`-Nähe |

## Regeln (Reihenfolge, die erste passende gewinnt)

Grundlage: 5e.tools `spells-*.json` (XPHB-Fassung, sonst erste Fassung). Markierungen: `miscTags` (SMN Beschwörung, HL Heilung, THP Temp HP, TP Teleport, PS Ebenenwechsel, FMV erzwungene Bewegung, MAC verändert AC, ADV Vorteil, DFT schwieriges Gelände, AAD Zusatzschaden), `damageInflict`, `conditionInflict`, `spellAttack`, `savingThrow`, Schule.

1. SMN → Beschwörung
2. HL oder THP → Heilung
3. Ziel „willing creature/creatures of your choice …“ + Verstärkung („adds 1d4 to“, „+2 bonus“, „advantage on“, „resistance to“ …) ohne Schaden → Buff
4. „curse“, „subtract 1d4“, „disadvantage on attack/saving“ bei Nekromantie/Verzauberung ohne Angriffswurf → Debuff
5. Schaden mit Angriffswurf/Rettungswurf/Zusatzschaden → Schaden (Typ)
6. Zustände restrained/paralyzed/stunned/incapacitated/prone/grappled/petrified/unconscious oder schwieriges Gelände → Kontrolle
7. charmed → Täuschung & sozial
8. frightened/blinded/poisoned/deafened/exhaustion → Debuff
9. sonstiger Schaden → Schaden
10. TP/PS/FMV oder „fly speed“, „your speed“, „teleport“ → Bewegung
11. MAC oder Bannmagie (Abjuration) → Schutz
12. „subtract“, „disadvantage …“ mit Rettungswurf → Debuff
13. ADV, „bonus to“, „advantage on“ → Buff
14. Erkenntnismagie (Divination), „telepathic“, „message“, „language“ → Information
15. Illusion/Verzauberung → Täuschung & sozial
16. sonst → Hilfsmagie

Die Regeln treffen etwa drei Viertel; die Durchsicht vom 01.10.2026 hat 156 Zauber korrigiert (`KORREKTUREN`).

## Ablauf: neue Zauber einordnen (z. B. nach `spell_merge.py`)

1. `bash willow/tools/setup.sh zauber`
2. `python3 willow/tools/spell_cats.py DnD_Character_App.html src --dry` – zeigt „NEU, noch nicht geprüft“ mit dem Vorschlag der Regeln.
3. Jeden neuen Zauber prüfen (Text lesen: Was ist der Hauptzweck?). Falsch → Eintrag in `KORREKTUREN` (Name exakt wie in `ZB_SPELLS`). Richtig → nichts tun.
4. Namen in `tools/spell_cats_geprueft.txt` eintragen (alphabetisch).
5. Ohne `--dry` ausführen → schreibt `SPELL_CATS`. Prüfskript: Test „Zauber-Kategorien“ meldet Zauber ohne gültige Kategorie.

## Ablauf: Kategorie ändern

Eintrag in `KORREKTUREN` ergänzen oder ändern (z. B. `"Darkness": "ctrl"`), Skript ohne `--dry` ausführen, prüfen, veröffentlichen. Gültige Werte: die Schlüssel oben bzw. `dmg:<typ>`/`dmg:multi`; das Skript bricht bei ungültigen Werten ab.

## Bild ändern

Nur in der HTML: `SPELL_CAT_ICONS` (per Python-`rep()`, B1a). Kategorienamen im Tooltip: `SPELL_CAT_NAMES`. Diese Tabelle hier mitändern.
