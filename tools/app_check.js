// app_check.js — Prüfskript für DnD_Character_App.html
// Aufruf:  node app_check.js NEU.html [ALT.html]
// Voraussetzung: npm i jsdom@24  (einmalig pro Sitzung)
// Prüft: 1) JS-Syntax  2) App lädt ohne Fehler, jede Klasse/Subklasse/Stufe rendert
//        2b) Regressionstests (Liste REGRESSION unten erweitern)
//        3) (mit ALT) Datenblöcke: nichts gelöscht, Änderungen aufgelistet
const fs = require('fs'), vm = require('vm');
const [, , NEW, OLD] = process.argv;
if (!NEW) { console.log('Aufruf: node app_check.js NEU.html [ALT.html]'); process.exit(2); }
let fail = 0;
const bad = m => { fail++; console.log('  ✘ ' + m); };

// 1) Syntax
const scripts = p => [...fs.readFileSync(p, 'utf8').matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n');
try { new vm.Script(scripts(NEW)); console.log('1) Syntax: OK'); }
catch (e) { console.log('1) Syntax: FEHLER – ' + e.message); process.exit(1); }

// ─── REGRESSIONSTESTS ───────────────────────────────────────────────────────
// Jeder behobene Fehler bekommt hier einen Testfall (neuester unten).
// Format: { name, datum, run: ({w,d,set,vis,CD,sel}) => true | 'Fehlertext' }
//   set(id,wert)   Formularfeld setzen      vis(id)   Element sichtbar?
//   sel(cls,sub,lvl) Klasse/Subklasse/Stufe wählen und Anzeige neu aufbauen
//   w = window (Zugriff auf App-Funktionen), d = document, CD = CLASS_DATA
// Anzeige-Menge eines Trackers: Pips, bei Pool-Zählern (pool:true, seit 27.09.2026) das Maximum aus „/ N"
const abAmt = (d, n) => { const c = [...d.querySelectorAll('#abList .ab-card')].find(x => x.querySelector('.ab-name').textContent.trim().startsWith(n)); if (!c) return 0; const m = c.querySelector('.ab-pmax'); return m ? parseInt(m.textContent.replace(/\D/g, '')) : c.querySelectorAll('.ab-pip').length; };
const REGRESSION = [
  { name: 'Subklassen-Tracker greifen auch bei Dropdown-Namen mit Quellen-Kürzel', datum: '26.09.2026',
    run: ({ d, sel, CD }) => {
      const ab = CD.Bard?.abilities?.['College of Lore']; if (!ab) return 'Testdaten fehlen (Bard/College of Lore)';
      sel('Bard', 'College of Lore (PHB)', '20');
      const txt = d.getElementById('abList')?.textContent || '';
      return ab.every(a => txt.includes(a.name)) || 'Lore-Tracker fehlen: ' + ab.map(a => a.name).filter(n => !txt.includes(n)).join(', ');
    } },
  { name: 'Beasts-Tab nur bei special:["beasts"] (ohne gespeicherte Bestien)', datum: '26.09.2026',
    run: ({ w, sel, vis }) => {
      w.eval('st.savedBeasts=[]');
      sel('Bard', '', '5'); if (vis('tabBestien')) return 'bei Bard sichtbar';
      sel('Druid', '', '5'); if (!vis('tabBestien')) return 'bei Druid unsichtbar';
      return true;
    } },
  { name: 'Tracker-uses je Stufe ({Stufe:Anzahl}) und "pb" (Cleric)', datum: '26.09.2026',
    run: ({ d, sel, CD }) => {
      if (!CD.Cleric?.abilities?.base) return 'Testdaten fehlen (Cleric)';
      const pips = n => { const c = [...d.querySelectorAll('#abList .ab-card')].find(x => x.querySelector('.ab-name').textContent.trim().startsWith(n)); return c ? c.querySelectorAll('.ab-pip').length : 0; };
      const want = [[2, 2, 2], [6, 3, 3], [18, 4, 6]];   // Stufe, Channel Divinity, Emboldening Bond (= Übungsbonus)
      for (const [l, cd, pb] of want) {
        sel('Cleric', 'Peace Domain (TCE)', l);
        if (pips('Channel Divinity') !== cd) return `L${l}: Channel Divinity ${pips('Channel Divinity')} statt ${cd}`;
        if (l >= 3 && pips('Emboldening Bond') !== pb) return `L${l}: Emboldening Bond ${pips('Emboldening Bond')} statt ${pb}`;
      }
      return true;
    } },
  { name: 'Subklassen-Dropdown: Anzeige neue Quelle, Wert bleibt alter Name (Savegames)', datum: '26.09.2026',
    run: ({ w, d, sel }) => {
      sel('Cleric', 'Life Domain (PHB)', 5);
      const s = d.getElementById('subcls'), o = [...s.options].find(x => x.value === 'Life Domain (PHB)');
      if (!o) return 'Wert "Life Domain (PHB)" fehlt im Dropdown';
      if (o.textContent !== 'Life Domain (XPHB)') return 'Anzeige ist "' + o.textContent + '"';
      if (s.value !== 'Life Domain (PHB)') return 'gewählter Wert ist "' + s.value + '"';
      if (!d.getElementById('subclsLoreTitle').textContent.includes('(XPHB)')) return 'Lore-Titel ohne neue Quelle';
      if ([...s.options].find(x => x.value === 'Nature Domain (PHB)')?.textContent !== 'Nature Domain (PHB)') return 'Nature Domain falsch umbenannt';
      return true;
    } },
  { name: 'Fighter: Tracker-uses "con"/"str" (min. 1) und Stufen; Class Table ohne Zauberplatz-Spalten', datum: '26.09.2026',
    run: ({ w, d, sel, CD }) => {
      if (!CD.Fighter?.abilities?.base) return 'Testdaten fehlen (Fighter)';
      const pips = n => { const c = [...d.querySelectorAll('#abList .ab-card')].find(x => x.querySelector('.ab-name').textContent.trim().startsWith(n)); return c ? c.querySelectorAll('.ab-pip').length : 0; };
      w.eval('st.attrs.CON=16;st.attrs.STR=8');
      sel('Fighter', 'Cavalier (XGE)', 17);
      if (pips('Warding Maneuver') !== 3) return 'Warding Maneuver ' + pips('Warding Maneuver') + ' statt 3 (CON 16)';
      if (pips('Unwavering Mark') !== 1) return 'Unwavering Mark ' + pips('Unwavering Mark') + ' statt 1 (STR 8, min. 1)';
      if (pips('Action Surge') !== 2) return 'Action Surge L17 ' + pips('Action Surge') + ' statt 2';
      if (pips('Second Wind') !== 4) return 'Second Wind L17 ' + pips('Second Wind') + ' statt 4';
      w.buildClassTable && w.buildClassTable();
      const t = d.getElementById('clsTableBody').textContent;
      if (t.includes('Spell Slots')) return 'Fighter-Tabelle zeigt Zauberplatz-Spalten';
      if (!t.includes('Weapon')) return 'Fighter-Tabelle ohne Weapon Mastery';
      sel('Cleric', '', 5); w.buildClassTable && w.buildClassTable();
      if (!d.getElementById('clsTableBody').textContent.includes('Spell Slots')) return 'Cleric-Tabelle ohne Zauberplatz-Spalten';
      return true;
    } },
  { name: 'Paladin: Halbzauberer-Tabelle (Slots auf 9 aufgefüllt), Channel Divinity/Glory-Tracker je Stufe', datum: '26.09.2026',
    run: ({ w, d, sel, CD }) => {
      if (!CD.Paladin?.abilities?.base) return 'Testdaten fehlen (Paladin)';
      const pips = n => { const c = [...d.querySelectorAll('#abList .ab-card')].find(x => x.querySelector('.ab-name').textContent.trim().startsWith(n)); return c ? c.querySelectorAll('.ab-pip').length : 0; };
      w.eval('st.attrs.CHA=16');
      sel('Paladin', 'Oath of Glory (TCE)', 2);
      if (pips('Channel Divinity') !== 0) return 'Channel Divinity L2 sichtbar (' + pips('Channel Divinity') + ')';
      sel('Paladin', 'Oath of Glory (TCE)', 11);
      if (pips('Channel Divinity') !== 3) return 'Channel Divinity L11 ' + pips('Channel Divinity') + ' statt 3';
      sel('Paladin', 'Oath of Glory (TCE)', 15);
      if (pips('Glorious Defense') !== 3) return 'Glorious Defense ' + pips('Glorious Defense') + ' statt 3 (CHA 16)';
      const rows = CD.Paladin && w.eval('CLASS_TABLES.Paladin.rows');
      if (!rows || rows.length !== 20 || rows.some(r => r.slots.length !== 9)) return 'Paladin-Tabelle: Zeilen/Slots nicht 20×9';
      if (rows[4].slots[1] !== 2 || rows[19].slots[4] !== 2) return 'Slots falsch (L5 Grad 2 / L20 Grad 5)';
      w.buildClassTable && w.buildClassTable();
      if (!d.getElementById('clsTableBody').textContent.includes('Spell Slots')) return 'Paladin-Tabelle ohne Zauberplatz-Spalten';
      return true;
    } },
  { name: 'Ranger: Halbzauberer-Tabelle (20×9 Slots), Favored Enemy/Tireless/Swarmkeeper-Tracker je Stufe, Zauberliste', datum: '26.09.2026',
    run: ({ w, d, sel, CD }) => {
      if (!CD.Ranger?.abilities?.base) return 'Testdaten fehlen (Ranger)';
      const pips = n => { const c = [...d.querySelectorAll('#abList .ab-card')].find(x => x.querySelector('.ab-name').textContent.trim().startsWith(n)); return c ? c.querySelectorAll('.ab-pip').length : 0; };
      w.eval('st.attrs.WIS=16');
      sel('Ranger', 'Swarmkeeper (TCE)', 4);
      if (pips('Favored Enemy') !== 2) return 'Favored Enemy L4 ' + pips('Favored Enemy') + ' statt 2';
      sel('Ranger', 'Swarmkeeper (TCE)', 17);
      if (pips('Favored Enemy') !== 6) return 'Favored Enemy L17 ' + pips('Favored Enemy') + ' statt 6';
      if (pips('Tireless') !== 3) return 'Tireless ' + pips('Tireless') + ' statt 3 (WIS 16)';
      if (pips('Writhing Tide') !== 6) return 'Writhing Tide ' + pips('Writhing Tide') + ' statt 6 (Übungsbonus)';
      sel('Ranger', 'Swarmkeeper (TCE)', 9);
      if (pips('Tireless') !== 0) return 'Tireless L9 sichtbar';
      const rows = w.eval('CLASS_TABLES.Ranger.rows');
      if (!rows || rows.length !== 20 || rows.some(r => r.slots.length !== 9)) return 'Ranger-Tabelle: Zeilen/Slots nicht 20×9';
      if (rows[0].slots[0] !== 2 || rows[4].slots[1] !== 2 || rows[19].slots[4] !== 2) return 'Slots falsch (L1 Grad 1 / L5 Grad 2 / L20 Grad 5)';
      w.buildClassTable && w.buildClassTable();
      if (!d.getElementById('clsTableBody').textContent.includes('Favored')) return 'Ranger-Tabelle ohne Favored Enemy';
      const zb = w.eval("ZB_SPELLS.filter(z=>z.classes.includes('Ranger')).length");
      if (zb < 60 || !w.eval("ZB_SPELLS.some(z=>z.name==='Hunter\\'s Mark'&&z.classes.includes('Ranger'))")) return 'Ranger-Zauber fehlen (' + zb + ')';
      if (!w.eval('SL_CLASSES').includes('Ranger')) return 'Ranger fehlt im Spell-List-Filter';
      return true;
    } },
  { name: 'Sorcerer: Sorcery Points = Stufe, Innate Sorcery 2, Restore Balance "cha"/"pb", 20×9-Slots-Tabelle, Zauberliste, Shadow-Magic-Anzeige', datum: '26.09.2026',
    run: ({ w, d, sel, CD }) => {
      if (!CD.Sorcerer?.abilities?.base) return 'Testdaten fehlen (Sorcerer)';
      const pips = n => { const c = [...d.querySelectorAll('#abList .ab-card')].find(x => x.querySelector('.ab-name').textContent.trim().startsWith(n)); return c ? c.querySelectorAll('.ab-pip').length : 0; };
      w.eval('st.attrs.CHA=16');
      sel('Sorcerer', 'Clockwork Sorcery (XPHB)', 1);
      if (abAmt(d, 'Sorcery Points') !== 0) return 'Sorcery Points L1 sichtbar (' + abAmt(d, 'Sorcery Points') + ')';
      if (pips('Innate Sorcery') !== 2) return 'Innate Sorcery ' + pips('Innate Sorcery') + ' statt 2';
      sel('Sorcerer', 'Clockwork Sorcery (XPHB)', 7);
      if (abAmt(d, 'Sorcery Points') !== 7) return 'Sorcery Points L7 ' + abAmt(d, 'Sorcery Points') + ' statt 7';
      if (pips('Sorcerous Restoration') !== 1) return 'Sorcerous Restoration L7 fehlt';
      if (pips('Restore Balance') !== 3) return 'Restore Balance (Clockwork Sorcery) ' + pips('Restore Balance') + ' statt 3 (CHA 16)';
      sel('Sorcerer', 'Clockwork Soul (TCE)', 20);
      if (abAmt(d, 'Sorcery Points') !== 20) return 'Sorcery Points L20 ' + abAmt(d, 'Sorcery Points') + ' statt 20';
      if (pips('Restore Balance') !== 6) return 'Restore Balance (Clockwork Soul) ' + pips('Restore Balance') + ' statt 6 (Übungsbonus)';
      const rows = w.eval('CLASS_TABLES.Sorcerer.rows');
      if (!rows || rows.length !== 20 || rows.some(r => r.slots.length !== 9)) return 'Sorcerer-Tabelle: Zeilen/Slots nicht 20×9';
      if (rows[0].slots[0] !== 2 || rows[19].slots[8] !== 1) return 'Slots falsch (L1 Grad 1 / L20 Grad 9)';
      w.buildClassTable && w.buildClassTable();
      const t = d.getElementById('clsTableBody').textContent;
      if (!t.includes('Sorcery') || !t.includes('Spell Slots')) return 'Sorcerer-Tabelle ohne Sorcery Points/Zauberplätze';
      const zb = w.eval("ZB_SPELLS.filter(z=>z.classes.includes('Sorcerer')).length");
      if (zb < 150 || !w.eval("ZB_SPELLS.some(z=>z.name==='Fireball'&&z.classes.includes('Sorcerer'))")) return 'Sorcerer-Zauber fehlen (' + zb + ')';
      if (!w.eval('SL_CLASSES').includes('Sorcerer')) return 'Sorcerer fehlt im Spell-List-Filter';
      sel('Sorcerer', 'Shadow Magic (XGE)', 6);
      const o = [...d.getElementById('subcls').options].find(x => x.value === 'Shadow Magic (XGE)');
      if (!o || o.textContent !== 'Shadow Magic (RHW)') return 'Shadow-Magic-Anzeige ist "' + (o && o.textContent) + '"';
      if (!d.getElementById('subclsLoreTitle').textContent.includes('(RHW)')) return 'Shadow-Magic-Lore-Titel ohne RHW';
      return true;
    } },
  { name: 'Rogue: Class Table (Sneak Attack, keine Zauberplätze), Tracker je Stufe/Attribut, Psychic Blade, Phantom-Anzeige, Wizard-Zauber', datum: '26.09.2026',
    run: ({ w, d, sel, CD }) => {
      if (!CD.Rogue?.abilities?.base) return 'Testdaten fehlen (Rogue)';
      const pips = n => { const c = [...d.querySelectorAll('#abList .ab-card')].find(x => x.querySelector('.ab-name').textContent.trim().startsWith(n)); return c ? c.querySelectorAll('.ab-pip').length : 0; };
      w.eval('st.attrs.DEX=16;st.attrs.WIS=8');
      sel('Rogue', 'Phantom (TCE)', 3);
      if (pips('Wails from the Grave') !== 3) return 'Wails from the Grave ' + pips('Wails from the Grave') + ' statt 3 (DEX 16)';
      if (pips('Stroke of Luck') !== 0) return 'Stroke of Luck L3 sichtbar';
      sel('Rogue', 'Phantom (TCE)', 20);
      if (pips('Stroke of Luck') !== 1) return 'Stroke of Luck L20 fehlt';
      if (pips('Ghost Walk') !== 1) return 'Ghost Walk L20 fehlt';
      sel('Rogue', 'Soulknife (TCE)', 5);
      if (pips('Psionic Energy Dice') !== 6) return 'Psionic Energy Dice L5 ' + pips('Psionic Energy Dice') + ' statt 6';
      sel('Rogue', 'Soulknife (TCE)', 17);
      if (pips('Psionic Energy Dice') !== 12) return 'Psionic Energy Dice L17 ' + pips('Psionic Energy Dice') + ' statt 12';
      if (pips('Rend Mind') !== 1) return 'Rend Mind L17 fehlt';
      if (!JSON.stringify(CD.Rogue.subclass.Soulknife).includes('Finesse, Thrown (range 60/120)')) return 'Psychic Blade ohne Eigenschaften';
      sel('Rogue', 'Inquisitive (XGE)', 13);
      if (pips('Unerring Eye') !== 1) return 'Unerring Eye ' + pips('Unerring Eye') + ' statt 1 (WIS 8, min. 1)';
      const rows = w.eval('CLASS_TABLES.Rogue.rows');
      if (!rows || rows.length !== 20) return 'Rogue-Tabelle: nicht 20 Zeilen';
      if (rows[0].sneak !== '1d6' || rows[19].sneak !== '10d6') return 'Sneak Attack falsch (L1 ' + rows[0].sneak + ' / L20 ' + rows[19].sneak + ')';
      w.buildClassTable && w.buildClassTable();
      const t = d.getElementById('clsTableBody').textContent;
      if (t.includes('Spell Slots')) return 'Rogue-Tabelle zeigt Zauberplatz-Spalten';
      if (!t.includes('Sneak Attack')) return 'Rogue-Tabelle ohne Sneak Attack';
      const o = [...d.getElementById('subcls').options].find(x => x.value === 'Phantom (TCE)');
      if (!o || o.textContent !== 'Phantom (RHW)') return 'Phantom-Anzeige ist "' + (o && o.textContent) + '"';
      if (JSON.stringify(w.eval('CLASS_SPELL_MAP.Rogue')) !== '["Wizard"]') return 'CLASS_SPELL_MAP.Rogue ≠ Wizard';
      return true;
    } },
  { name: 'Monk: Focus Points = Stufe (erst ab L2), Uncanny Metabolism, Wholeness "wis" (min. 1), Breath "pb", Class Table (Martial Arts/Focus/Unarmored Movement, keine Zauberplätze), beide Subklassen-Fassungen', datum: '26.09.2026',
    run: ({ w, d, sel, CD }) => {
      if (!CD.Monk?.abilities?.base) return 'Testdaten fehlen (Monk)';
      const pips = n => { const c = [...d.querySelectorAll('#abList .ab-card')].find(x => x.querySelector('.ab-name').textContent.trim().startsWith(n)); return c ? c.querySelectorAll('.ab-pip').length : 0; };
      w.eval('st.attrs.WIS=16');
      sel('Monk', 'Warrior of the Open Hand (XPHB)', 1);
      if (abAmt(d, 'Focus Points') !== 0) return 'Focus Points L1 sichtbar (' + abAmt(d, 'Focus Points') + ')';
      sel('Monk', 'Warrior of the Open Hand (XPHB)', 6);
      if (abAmt(d, 'Focus Points') !== 6) return 'Focus Points L6 ' + abAmt(d, 'Focus Points') + ' statt 6';
      if (pips('Uncanny Metabolism') !== 1) return 'Uncanny Metabolism fehlt';
      if (pips('Wholeness of Body') !== 3) return 'Wholeness of Body (Warrior of the Open Hand) ' + pips('Wholeness of Body') + ' statt 3 (WIS 16)';
      w.eval('st.attrs.WIS=8'); sel('Monk', 'Warrior of the Open Hand (XPHB)', 6);
      if (pips('Wholeness of Body') !== 1) return 'Wholeness of Body ' + pips('Wholeness of Body') + ' statt 1 (WIS 8, min. 1)';
      sel('Monk', 'Way of the Open Hand (PHB)', 6);
      if (pips('Wholeness of Body') !== 1) return 'Wholeness of Body (Way of the Open Hand) ' + pips('Wholeness of Body') + ' statt 1';
      sel('Monk', 'Way of the Ascendant Dragon (FTD)', 5);
      if (pips('Breath of the Dragon') !== 3) return 'Breath of the Dragon L5 ' + pips('Breath of the Dragon') + ' statt 3 (Übungsbonus)';
      sel('Monk', 'Way of the Ascendant Dragon (FTD)', 20);
      if (abAmt(d, 'Focus Points') !== 20) return 'Focus Points L20 ' + abAmt(d, 'Focus Points') + ' statt 20';
      const keys = Object.keys(CD.Monk.subclass);
      if (!keys.includes('Way of the Open Hand') || !keys.includes('Warrior of the Open Hand')) return 'Subklassen-Keys beider Fassungen fehlen';
      if (!JSON.stringify(CD.Monk.subclass['Way of the Open Hand']).includes('three times your monk level')) return 'Way of the Open Hand nicht in PHB-Fassung';
      const rows = w.eval('CLASS_TABLES.Monk.rows');
      if (!rows || rows.length !== 20) return 'Monk-Tabelle: nicht 20 Zeilen';
      if (rows[0].martial !== '1d6' || rows[19].martial !== '1d12') return 'Martial Arts falsch (L1 ' + rows[0].martial + ' / L20 ' + rows[19].martial + ')';
      if (rows[19].focus !== 20 || rows[1].focus !== 2) return 'Focus Points in der Tabelle falsch';
      if (rows[0].unarmored !== '—' || rows[17].unarmored !== '+30 ft.') return 'Unarmored Movement falsch (L1 ' + rows[0].unarmored + ' / L18 ' + rows[17].unarmored + ')';
      w.buildClassTable && w.buildClassTable();
      const t = d.getElementById('clsTableBody').textContent;
      if (t.includes('Spell Slots')) return 'Monk-Tabelle zeigt Zauberplatz-Spalten';
      if (!t.includes('Martial') || !t.includes('Focus') || !t.includes('Unarmored') || !t.includes('+30 ft.')) return 'Monk-Tabelle ohne Martial Arts/Focus Points/Unarmored Movement';
      return true;
    } },
  { name: 'Barbarian: Rages je Stufe (2 → 6), Rage Damage "+2" → "+4", Class Table ohne Zauberplätze, Persistent Rage erst ab L15, Zealot-Pool, Beast "pb", beide Anzeige-Labels', datum: '26.09.2026',
    run: ({ w, d, sel, CD }) => {
      if (!CD.Barbarian?.abilities?.base) return 'Testdaten fehlen (Barbarian)';
      const pips = n => { const c = [...d.querySelectorAll('#abList .ab-card')].find(x => x.querySelector('.ab-name').textContent.trim().startsWith(n)); return c ? c.querySelectorAll('.ab-pip').length : 0; };
      sel('Barbarian', 'Path of the Zealot (XGE)', 1);
      if (pips('Rage') !== 2) return 'Rage L1 ' + pips('Rage') + ' statt 2';
      if (pips('Persistent Rage') !== 0) return 'Persistent Rage L1 sichtbar';
      sel('Barbarian', 'Path of the Zealot (XGE)', 3);
      if (pips('Rage') !== 3) return 'Rage L3 ' + pips('Rage') + ' statt 3';
      if (pips('Warrior of the Gods') !== 4) return 'Warrior of the Gods L3 ' + pips('Warrior of the Gods') + ' statt 4';
      sel('Barbarian', 'Path of the Zealot (XGE)', 17);
      if (pips('Rage') !== 6) return 'Rage L17 ' + pips('Rage') + ' statt 6';
      if (pips('Warrior of the Gods') !== 7) return 'Warrior of the Gods L17 ' + pips('Warrior of the Gods') + ' statt 7';
      if (pips('Persistent Rage') !== 1) return 'Persistent Rage L17 fehlt';
      sel('Barbarian', 'Path of the Beast (TCE)', 10);
      if (pips('Rage') !== 4) return 'Rage L10 ' + pips('Rage') + ' statt 4';
      if (pips('Infectious Fury') !== 4) return 'Infectious Fury L10 ' + pips('Infectious Fury') + ' statt 4 (Übungsbonus)';
      const rows = w.eval('CLASS_TABLES.Barbarian.rows');
      if (!rows || rows.length !== 20) return 'Barbarian-Tabelle: nicht 20 Zeilen';
      if (rows[0].rages !== '2' || rows[19].rages !== '6') return 'Rages falsch (L1 ' + rows[0].rages + ' / L20 ' + rows[19].rages + ')';
      if (rows[0].rage !== '+2' || rows[8].rage !== '+3' || rows[15].rage !== '+4') return 'Rage Damage falsch (L1 ' + rows[0].rage + ' / L9 ' + rows[8].rage + ' / L16 ' + rows[15].rage + ')';
      w.buildClassTable && w.buildClassTable();
      const t = d.getElementById('clsTableBody').textContent;
      if (t.includes('Spell Slots')) return 'Barbarian-Tabelle zeigt Zauberplatz-Spalten';
      if (!t.includes('Rage') || !t.includes('Weapon') || !t.includes('+4')) return 'Barbarian-Tabelle ohne Rages/Rage Damage/Weapon Mastery';
      const lab = v => { const o = [...d.getElementById('subcls').options].find(x => x.value === v); return o && o.textContent; };
      if (lab('Path of the Berserker (PHB)') !== 'Path of the Berserker (XPHB)') return 'Berserker-Anzeige ist "' + lab('Path of the Berserker (PHB)') + '"';
      if (lab('Path of the Zealot (XGE)') !== 'Path of the Zealot (XPHB)') return 'Zealot-Anzeige ist "' + lab('Path of the Zealot (XGE)') + '"';
      if (lab('Path of the Totem Warrior (PHB)') !== 'Path of the Totem Warrior (PHB)') return 'Totem-Warrior-Anzeige falsch umbenannt';
      return true;
    } },
  { name: 'Warlock: Pakt-Slots je Stufe (1/2/3/4), Magical Cunning ab L2, Contact Patron ab L9, "cha"/"pb"/Pool-Tracker, Class Table (Pakt-Spalten, keine 9 Zauberplatz-Spalten), Zauberliste, Undead-Anzeige', datum: '26.09.2026',
    run: ({ w, d, sel, CD }) => {
      if (!CD.Warlock?.abilities?.base) return 'Testdaten fehlen (Warlock)';
      const pips = n => { const c = [...d.querySelectorAll('#abList .ab-card')].find(x => x.querySelector('.ab-name').textContent.trim().startsWith(n)); return c ? c.querySelectorAll('.ab-pip').length : 0; };
      w.eval('st.attrs.CHA=16');
      sel('Warlock', 'Archfey Patron (XPHB)', 1);
      if (pips('Pact Magic Slots') !== 1) return 'Pact Magic Slots L1 ' + pips('Pact Magic Slots') + ' statt 1';
      if (pips('Magical Cunning') !== 0) return 'Magical Cunning L1 sichtbar';
      sel('Warlock', 'Archfey Patron (XPHB)', 3);
      if (pips('Pact Magic Slots') !== 2) return 'Pact Magic Slots L3 ' + pips('Pact Magic Slots') + ' statt 2';
      if (pips('Magical Cunning') !== 1) return 'Magical Cunning L3 fehlt';
      if (pips('Steps of the Fey') !== 3) return 'Steps of the Fey ' + pips('Steps of the Fey') + ' statt 3 (CHA 16)';
      if (pips('Contact Patron') !== 0) return 'Contact Patron L3 sichtbar';
      sel('Warlock', 'Archfey Patron (XPHB)', 11);
      if (pips('Pact Magic Slots') !== 3) return 'Pact Magic Slots L11 ' + pips('Pact Magic Slots') + ' statt 3';
      if (pips('Contact Patron') !== 1) return 'Contact Patron L11 fehlt';
      sel('Warlock', 'Celestial Patron (XPHB)', 17);
      if (pips('Pact Magic Slots') !== 4) return 'Pact Magic Slots L17 ' + pips('Pact Magic Slots') + ' statt 4';
      if (abAmt(d, 'Healing Light') !== 18) return 'Healing Light L17 ' + abAmt(d, 'Healing Light') + ' statt 18 (1 + Stufe)';
      sel('Warlock', 'The Fathomless (TCE)', 5);
      if (pips('Tentacle of the Deeps') !== 3) return 'Tentacle of the Deeps L5 ' + pips('Tentacle of the Deeps') + ' statt 3 (Übungsbonus)';
      const rows = w.eval('CLASS_TABLES.Warlock.rows');
      if (!rows || rows.length !== 20) return 'Warlock-Tabelle: nicht 20 Zeilen';
      if (rows[0].spell !== 1 || rows[1].spell !== 2 || rows[10].spell !== 3 || rows[16].spell !== 4) return 'Spell Slots in der Tabelle falsch';
      if (rows[0].slot !== 1 || rows[8].slot !== 5 || rows[19].slot !== 5) return 'Slot Level in der Tabelle falsch';
      if (rows[0].invocations !== 1 || rows[19].invocations !== 10) return 'Invocations in der Tabelle falsch';
      w.buildClassTable && w.buildClassTable();
      const b = d.getElementById('clsTableBody');
      if (b.querySelector('.ct-grp')) return 'Warlock-Tabelle zeigt die 9 Zauberplatz-Spalten';
      const t = b.textContent;
      if (!t.includes('Invocations') || !t.includes('Slot') || !t.includes('Prepared')) return 'Warlock-Tabelle ohne Pakt-Spalten';
      const zb = w.eval("ZB_SPELLS.filter(z=>z.classes.includes('Warlock')&&z.src===\"PHB'24\").length");
      if (zb < 91 || !w.eval("ZB_SPELLS.some(z=>z.name==='Eldritch Blast'&&z.classes.includes('Warlock'))")) return 'Warlock-Zauber fehlen (' + zb + ' PHB\'24)';
      if (!w.eval('SL_CLASSES').includes('Warlock')) return 'Warlock fehlt im Spell-List-Filter';
      const lab = v => { const o = [...d.getElementById('subcls').options].find(x => x.value === v); return o && o.textContent; };
      if (lab('The Undead (VRGR)') !== 'The Undead (RHW)') return 'Undead-Anzeige ist "' + lab('The Undead (VRGR)') + '"';
      if (lab('The Hexblade (XGE)') !== 'The Hexblade (XGE)') return 'Hexblade-Anzeige falsch umbenannt';
      return true;
    } },
  { name: 'Fixliste Sonnet: Wild Shape 2/3/4, Wizard/Bard Class Table (20×9 Slots, Bardic Die), Wizard-Tracker, Tags', datum: '27.09.2026',
    run: ({ w, d, sel, CD }) => {
      const pips = n => { const c = [...d.querySelectorAll('#abList .ab-card')].find(x => x.querySelector('.ab-name').textContent.trim().startsWith(n)); return c ? c.querySelectorAll('.ab-pip').length : 0; };
      const cards = n => [...d.querySelectorAll('#abList .ab-card')].filter(x => x.querySelector('.ab-name').textContent.trim().startsWith(n)).length;
      for (const [l, n] of [[2, 2], [6, 3], [16, 3], [17, 4]]) { sel('Druid', 'Circle of the Land (PHB)', l); if (pips('Wild Shape') !== n) return `Wild Shape L${l} ${pips('Wild Shape')} statt ${n}`; }
      sel('Druid', 'Circle of the Land (PHB)', 1); if (cards('Wild Shape') !== 0) return 'Wild Shape L1 sichtbar';
      const rw = w.eval('CLASS_TABLES.Wizard.rows'), rb = w.eval('CLASS_TABLES.Bard.rows');
      if (!rw || rw.length !== 20 || rw.some(r => r.slots.length !== 9)) return 'Wizard-Tabelle: nicht 20×9';
      if (rw[0].cantrips !== 3 || rw[0].prepared !== 4 || rw[0].slots[0] !== 2 || rw[19].prepared !== 25 || rw[19].slots[8] !== 1) return 'Wizard-Werte falsch';
      if (!rw[0].f.includes('Arcane Recovery') || rw[2].f !== 'Wizard Subclass') return 'Wizard-Features je Stufe falsch (' + rw[2].f + ')';
      if (!rb || rb.length !== 20 || rb[0].bardic !== '1d6' || rb[4].bardic !== '1d8' || rb[19].bardic !== '1d12') return 'Bard: Bardic Die falsch';
      if (rb[0].cantrips !== 2 || rb[0].prepared !== 4 || rb[0].slots[0] !== 2 || rb[19].slots[8] !== 1) return 'Bard-Werte falsch';
      for (const c of ['Wizard', 'Bard']) { sel(c, '', 5); w.buildClassTable && w.buildClassTable(); const t = d.getElementById('clsTableBody').textContent; if (!t.includes('Spell Slots') || !t.includes('Prepared')) return c + '-Tabelle wird nicht angezeigt'; if (t.includes('[object')) return c + '-Tabelle mit [object]'; }
      sel('Bard', '', 5); if (!d.getElementById('clsTableBody').textContent.includes('Bardic')) return 'Bard-Tabelle ohne Bardic Die';
      w.eval('st.attrs.INT=16');
      sel('Wizard', 'Diviner (XPHB)', 1); if (pips('Arcane Recovery') !== 1) return 'Arcane Recovery fehlt';
      if (cards('Portent') !== 0) return 'Portent L1 sichtbar';
      sel('Wizard', 'Diviner (XPHB)', 14); if (pips('Portent') !== 3) return 'Portent L14 ' + pips('Portent') + ' statt 3';
      sel('Wizard', 'Diviner (XPHB)', 3); if (pips('Portent') !== 2) return 'Portent L3 ' + pips('Portent') + ' statt 2';
      sel('Wizard', 'Diviner (XPHB)', 20); if (pips('Signature Spells') !== 2) return 'Signature Spells L20 ' + pips('Signature Spells');
      sel('Wizard', 'Chronurgy Magic (EGW)', 6); if (pips('Momentary Stasis') !== 3) return 'Momentary Stasis ' + pips('Momentary Stasis') + ' statt 3 (INT 16)';
      if (pips('Chronal Shift') !== 2) return 'Chronal Shift ' + pips('Chronal Shift') + ' statt 2';
      // seit Neubau 27.09.2026: Bladesinging = FRHoF-Fassung, Bladesong = INT-Modifikator (TCE: Übungsbonus)
      sel('Wizard', 'Bladesinging (TCE)', 5); if (pips('Bladesong') !== 3) return 'Bladesong ' + pips('Bladesong') + ' statt 3 (INT 16)';
      const tagOf = (cls, grp, name) => { const src = grp === 'base' ? CD[cls].base : CD[cls].subclass[grp]; return src.find(f => f.name === name)?.tag; };
      if (tagOf('Rogue', 'base', 'Devious Strikes') !== 'Passiv') return 'Devious Strikes nicht Passiv';
      if (tagOf('Barbarian', 'Path of the Beast', 'Form of the Beast') !== 'Passiv') return 'Form of the Beast nicht Passiv';
      if (tagOf('Warlock', 'base', 'Eldritch Invocation Options') !== 'Passiv') return 'Invocation Options nicht Passiv';
      if (tagOf('Warlock', 'Archfey Patron', 'Bewitching Magic') !== 'Passiv') return 'Bewitching Magic nicht Passiv';
      const abTag = (cls, grp, id) => CD[cls].abilities[grp].find(a => a.id === id)?.tag;
      if (abTag('Barbarian', 'Path of the Zealot', 'bb_zl_rageofgods') !== 'bonus') return 'Rage of the Gods nicht bonus';
      if (abTag('Barbarian', 'Path of the Beast', 'bb_bs_fury') !== 'passiv') return 'Infectious Fury nicht passiv';
      return true;
    } },
  // Neubau 27.09.2026: Unbreakable Majesty (XPHB), Animating Performance (TCE) und Spirit Totem (XGE) haben laut 5e.tools-Text
  // KEINE Konzentration (vorher aus handgeschriebenen Kurztexten übernommen) → erwartet ohne „C".
  { name: 'Konzentrations-Abzeichen "C" nur bei echter Konzentration (Rage ohne, Mantle of Majesty mit)', datum: '27.09.2026',
    run: ({ d, sel }) => {
      const conc = n => { const c = [...d.querySelectorAll('#abList .ab-card')].find(x => x.querySelector('.ab-name').textContent.trim().startsWith(n)); return c ? !!c.querySelector('.sp-conc') : null; };
      sel('Barbarian', 'Path of the Berserker (PHB)', 5); if (conc('Rage') !== false) return 'Rage: ' + conc('Rage') + ' (erwartet ohne C)';
      sel('Bard', 'College of Glamour (XGE)', 14);
      if (conc('Mantle of Majesty') !== true) return 'Mantle of Majesty ohne C'; if (conc('Unbreakable Majesty') !== false) return 'Unbreakable Majesty: ' + conc('Unbreakable Majesty') + ' (erwartet ohne C)';
      sel('Bard', 'College of Creation (TCE)', 14); if (conc('Animating Performance') !== false) return 'Animating Performance: ' + conc('Animating Performance') + ' (erwartet ohne C)';
      sel('Druid', 'Circle of the Stars (XPHB)', 3); if (conc('Starry Form') !== false) return 'Starry Form: ' + conc('Starry Form') + ' (erwartet ohne C)';
      sel('Druid', 'Circle of the Shepherd (XGE)', 3); if (conc('Spirit Totem') !== false) return 'Spirit Totem: ' + conc('Spirit Totem') + ' (erwartet ohne C)';
      return true;
    } },
  { name: 'Opus-Check Sonnet-Fixes: Wizard-Tracker (Shape-Shifter, Arcane Abeyance, Phantasmal Creatures, Manifest Mind 1 + PB), "C" bei Telekinetic Master/Event Horizon, Barbarian-Info-Tags', datum: '27.09.2026',
    run: ({ w, d, sel, CD }) => {
      const card = n => [...d.querySelectorAll('#abList .ab-card')].find(x => x.querySelector('.ab-name').textContent.trim().startsWith(n));
      const pips = n => { const c = card(n); return c ? c.querySelectorAll('.ab-pip').length : 0; };
      const conc = n => { const c = card(n); return c ? !!c.querySelector('.sp-conc') : null; };
      // seit Neubau 27.09.2026: Transmutation = AU-Fassung (Shape-Shifter statt Shapechanger), Abjuration ab Stufe 3
      sel('Wizard', 'School of Transmutation (PHB)', 10); if (pips('Shape-Shifter') !== 1) return 'Shape-Shifter fehlt';
      sel('Wizard', 'School of Abjuration (PHB)', 3); if (pips('Arcane Ward') !== 1) return 'Arcane Ward (PHB) fehlt';
      sel('Wizard', 'Chronurgy Magic (EGW)', 10); if (pips('Arcane Abeyance') !== 1) return 'Arcane Abeyance fehlt';
      sel('Wizard', 'Illusionist (XPHB)', 6); if (pips('Phantasmal Creatures') !== 2) return 'Phantasmal Creatures ' + pips('Phantasmal Creatures') + ' statt 2';
      sel('Wizard', 'Order of Scribes (TCE)', 9);
      if (pips('Manifest Mind: Spellcasting') !== 4) return 'Manifest Mind: Spellcasting ' + pips('Manifest Mind: Spellcasting') + ' statt 4 (Übungsbonus)';
      const mm = [...d.querySelectorAll('#abList .ab-card')].find(x => x.querySelector('.ab-name').textContent.trim() === 'Manifest Mind');
      if (!mm || mm.querySelectorAll('.ab-pip').length !== 1) return 'Manifest Mind (Beschwören) nicht 1';
      sel('Wizard', 'Graviturgy Magic (EGW)', 14); if (conc('Event Horizon') !== true) return 'Event Horizon ohne C';
      sel('Fighter', 'Psi Warrior (TCE)', 18); if (conc('Telekinetic Master') !== true) return 'Telekinetic Master ohne C';
      const ab = (g, id) => CD.Wizard.abilities[g].find(a => a.id === id);
      if (ab('Diviner', 'wz_dv_portent').tag !== 'passiv' || ab('School of Divination', 'wz_sd_portent').tag !== 'passiv') return 'Portent nicht passiv';
      const tagOf = (grp, name) => CD.Barbarian.subclass[grp].find(f => f.name === name)?.tag;
      if (tagOf('Path of the Zealot', 'Rage of the Gods') !== 'Bonusaktion') return 'Rage of the Gods (Info) nicht Bonusaktion';
      if (tagOf('Path of the Beast', 'Infectious Fury') !== 'Passiv') return 'Infectious Fury (Info) nicht Passiv';
      return true;
    } },
  { name: 'Service Worker wird registriert (Offline + Updates), Reload nur bei Worker-Wechsel', datum: '27.09.2026',
    run: ({ d }) => {
      const js = [...d.querySelectorAll('script')].map(s => s.textContent).join('\n');
      if (!js.includes("navigator.serviceWorker.register('./service-worker.js')")) return 'Registrierung des Service Workers fehlt';
      if (!/controllerchange[\s\S]{0,200}swHadCtrl/.test(js)) return 'Reload bei Update fehlt oder ohne Schutz (swHadCtrl)';
      return true;
    } },
  { name: 'Neubau Bard/Druid/Wizard: 2024-Stufen der Alt-Subklassen, neueste Fassungen, alte Keys/ids/special erhalten', datum: '27.09.2026',
    run: ({ w, d, sel, CD }) => {
      const card = n => [...d.querySelectorAll('#abList .ab-card')].find(x => x.querySelector('.ab-name').textContent.trim().startsWith(n));
      const pips = n => { const c = card(n); return c ? c.querySelectorAll('.ab-pip').length : 0; };
      const lab = v => { const o = [...d.getElementById('subcls').options].find(x => x.value === v); return o && o.textContent; };
      const ids = c => Object.values(CD[c].abilities || {}).flat().map(a => a.id);
      // Druid: Keys mit Kürzel bleiben, special bleibt, Alt-Subklassen ab Stufe 3
      if (!CD.Druid.subclass['Circle of Dreams (XGE)'] || !CD.Druid.subclass['Circle of Spores (TCE)']) return 'Druid-Keys mit Kürzel fehlen';
      if (JSON.stringify(CD.Druid.special) !== '["beasts"]') return 'Druid special verloren';
      if (CD.Druid.subclass['Circle of Dreams (XGE)'][0].lvl !== 3) return 'Circle of Dreams beginnt nicht auf Stufe 3';
      sel('Druid', 'Circle of Dreams (XGE)', 2); if (card('Balm of the Summer Court')) return 'Balm of the Summer Court L2 sichtbar';
      sel('Druid', 'Circle of Dreams (XGE)', 3); if (abAmt(d, 'Balm of the Summer Court') !== 3) return 'Balm L3 ' + abAmt(d, 'Balm of the Summer Court') + ' statt 3';
      sel('Druid', 'Circle of Wildfire (TCE)', 10); if (pips('Cauterizing Flames') !== 4) return 'Cauterizing Flames L10 ' + pips('Cauterizing Flames') + ' statt 4 (Übungsbonus)';
      for (const id of ['wildshape', 'wildcompanion', 'wildresurgence_ws', 'balmsc', 'fungalinfestation2', 'summonwildfire']) if (!ids('Druid').includes(id)) return 'Druid-Tracker-id fehlt: ' + id;
      // Bard: Glamour XPHB, Spirits RHW, Dance Inspiring Movement L6, Superior Inspiration
      if (!CD.Bard.subclass['College of Glamour'].some(f => f.name === 'Beguiling Magic')) return 'Glamour nicht XPHB (Beguiling Magic fehlt)';
      if (!CD.Bard.subclass['College of Spirits'].some(f => f.name === 'Spirits from Beyond')) return 'Spirits nicht RHW';
      if (CD.Bard.subclass['College of Dance'].find(f => f.name === 'Inspiring Movement')?.lvl !== 6) return 'Inspiring Movement nicht Stufe 6';
      if (!CD.Bard.base.some(f => f.name === 'Superior Inspiration' && f.lvl === 18)) return 'Superior Inspiration fehlt';
      sel('Bard', 'College of Spirits (VRGR)', 3);
      if (lab('College of Glamour (XGE)') !== 'College of Glamour (XPHB)' || lab('College of Spirits (VRGR)') !== 'College of Spirits (RHW)') return 'Bard-Anzeige-Labels falsch';
      if (!card('Spirits from Beyond')) return 'Spirits from Beyond (id talesfrombeyond) fehlt';
      for (const id of ['bardicinspiration', 'cuttingwords', 'talesfrombeyond', 'spiritsession', 'mantleofmajesty']) if (!ids('Bard').includes(id)) return 'Bard-Tracker-id fehlt: ' + id;
      // Wizard: Alt-Schulen ab Stufe 3, AU-/FRHoF-Fassungen mit Label
      sel('Wizard', 'School of Evocation (PHB)', 3);
      if (CD.Wizard.subclass['School of Evocation'][0].lvl !== 3) return 'School of Evocation beginnt nicht auf Stufe 3';
      sel('Wizard', 'School of Abjuration (PHB)', 2); if (card('Arcane Ward')) return 'Arcane Ward (PHB) L2 sichtbar';
      if (lab('School of Necromancy (PHB)') !== 'School of Necromancy (AU)' || lab('Bladesinging (TCE)') !== 'Bladesinging (FRHoF)') return 'Wizard-Anzeige-Labels falsch';
      if (lab('School of Evocation (PHB)') !== 'School of Evocation (PHB)') return 'Evocation-Anzeige falsch umbenannt';
      for (const id of ['wz_arcanerecovery', 'wz_st_shapechanger', 'wz_sc_benigntransposition', 'wz_bs_bladesong', 'wz_os_mindcasting']) if (!ids('Wizard').includes(id)) return 'Wizard-Tracker-id fehlt: ' + id;
      return true;
    } },
  { name: 'Pool-Zähler (Lay on Hands, Sorcery/Focus Points, Healing Light, Balm) und Einzel-Tracker (Runen, Mystic Arcanum, Lunar Sorcery); Tracker-Klicks werden gespeichert', datum: '27.09.2026',
    run: ({ w, d, sel, CD }) => {
      const card = n => [...d.querySelectorAll('#abList .ab-card')].find(x => x.querySelector('.ab-name').textContent.trim().startsWith(n));
      const val = n => { const i = card(n)?.querySelector('.ab-pval'); return i ? +i.value : null; };
      const rows = n => [...(card(n)?.querySelectorAll('.ab-sub') || [])].map(r => [r.querySelector('.ab-sublbl').textContent, r.querySelectorAll('.ab-pip').length]);
      w.eval("st.abUses={};st.abPick={};document.getElementById('charName').textContent='Regressionstest'");
      // Pool-Zähler: Paladin Lay on Hands = 5 × Stufe, Zahlenfeld statt Pips
      sel('Paladin', 'Oath of Devotion (PHB)', 5);
      const loh = card('Lay on Hands'); if (!loh) return 'Lay on Hands fehlt';
      if (abAmt(d, 'Lay on Hands') !== 25 || val('Lay on Hands') !== 25) return 'Lay on Hands L5 nicht 25/25';
      if (loh.querySelector('.ab-pip')) return 'Lay on Hands zeigt Pips';
      w.abPoolAdj('layonhands', -1, 25); if (val('Lay on Hands') !== 24 || w.eval('st.abUses.layonhands') !== 1) return 'Pool −1 wirkt nicht';
      w.abPoolSet('layonhands', '10', 25); if (val('Lay on Hands') !== 10 || w.eval('st.abUses.layonhands') !== 15) return 'Pool-Eingabe 10 wirkt nicht';
      w.abPoolSet('layonhands', '99', 25); if (val('Lay on Hands') !== 25) return 'Pool über Maximum';
      w.abPoolAdj('layonhands', -1, 25); w.abPoolAdj('layonhands', 1, 25); w.abPoolAdj('layonhands', 1, 25); if (val('Lay on Hands') !== 25) return 'Pool +1 über Maximum';
      w.abPoolSet('layonhands', '7', 25);
      const saved = JSON.parse(w.localStorage.getItem('dnd5e_chars') || '{}').Regressionstest;
      if (!saved || saved.abUses?.layonhands !== 18) return 'Pool-Wert nicht gespeichert (autoSave)';
      sel('Paladin', 'Oath of Devotion (PHB)', 20); if (abAmt(d, 'Lay on Hands') !== 100) return 'Lay on Hands L20 nicht 100';
      for (const [c, sub, l, n, m] of [['Sorcerer', 'Lunar Sorcery (DSotDQ)', 7, 'Sorcery Points', 7], ['Monk', 'Warrior of Mercy (XPHB)', 6, 'Focus Points', 6], ['Warlock', 'The Celestial (XGE)', 5, 'Healing Light', 6], ['Druid', 'Circle of Dreams (XGE)', 4, 'Balm of the Summer Court', 4]]) {
        sel(c, sub, l); if (!card(n)?.querySelector('.ab-pval') || abAmt(d, n) !== m) return `${n} L${l} kein Pool ${m} (${abAmt(d, n)})`;
      }
      // Einzel-Tracker: Mystic Arcanum je Grad (L11 → 6, L17 → 6–9), je 1× pro Long Rest
      sel('Warlock', 'Fiend Patron (XPHB)', 10); if (card('Mystic Arcanum')) return 'Mystic Arcanum L10 sichtbar';
      sel('Warlock', 'Fiend Patron (XPHB)', 13); if (JSON.stringify(rows('Mystic Arcanum')) !== '[["Level 6 Spell",1],["Level 7 Spell",1]]') return 'Mystic Arcanum L13: ' + JSON.stringify(rows('Mystic Arcanum'));
      sel('Warlock', 'Fiend Patron (XPHB)', 17); if (rows('Mystic Arcanum').length !== 4) return 'Mystic Arcanum L17 nicht 4 Grade';
      card('Mystic Arcanum').querySelectorAll('.ab-sub')[1].querySelector('.ab-pip').click();
      if (w.eval("st.abUses['wl_mysticarcanum.7']") !== 1) return 'Arcanum Grad 7 nicht verbraucht';
      if (JSON.parse(w.localStorage.getItem('dnd5e_chars') || '{}').Regressionstest?.abUses?.['wl_mysticarcanum.7'] !== 1) return 'Pip-Klick nicht gespeichert (autoSave in togAbUse)';
      // .used = verbraucht (seit 27.09.2026 leerer Kreis; gefüllt = .avail)
      if (!card('Mystic Arcanum').querySelectorAll('.ab-sub')[1].querySelector('.ab-pip.used') || card('Mystic Arcanum').querySelectorAll('.ab-sub')[0].querySelector('.ab-pip.used')) return 'Arcanum-Pip falsch markiert';
      // Rune Knight: je Rune 1× (ab L15 2×), Hill/Storm ab L7, Auswahl nach Runes Known
      sel('Fighter', 'Rune Knight (TCE)', 3);
      if (JSON.stringify(rows('Rune Carver').map(r => r[0])) !== '["Cloud Rune","Fire Rune","Frost Rune","Stone Rune"]') return 'Runen L3: ' + JSON.stringify(rows('Rune Carver'));
      if (!card('Rune Carver').textContent.includes('Gewählt 0/2')) return 'Runen-Auswahl-Hinweis fehlt';
      sel('Fighter', 'Rune Knight (TCE)', 7); if (rows('Rune Carver').length !== 6 || rows('Rune Carver').some(r => r[1] !== 1)) return 'Runen L7: ' + JSON.stringify(rows('Rune Carver'));
      w.togAbPick('rk_runes', 'fire', 3); w.togAbPick('rk_runes', 'storm', 3); w.togAbPick('rk_runes', 'cloud', 3); w.togAbPick('rk_runes', 'hill', 3);
      if (JSON.stringify(w.eval('st.abPick.rk_runes')) !== '["fire","storm","cloud"]') return 'Runen-Auswahl: ' + JSON.stringify(w.eval('st.abPick.rk_runes'));
      if (!card('Rune Carver').classList.contains('ab-picked') || card('Rune Carver').querySelectorAll('.ab-sub.unpicked').length !== 3) return 'nicht gewählte Runen nicht markiert';
      sel('Fighter', 'Rune Knight (TCE)', 15); if (rows('Rune Carver').some(r => r[1] !== 2)) return 'Runen L15 nicht 2×';
      // Lunar Sorcery: Embodiment 1 Zauber (L3–5), ab L6 je Phase (Waxing and Waning), L18 Lunar Phenomenon je Phase
      sel('Sorcerer', 'Lunar Sorcery (DSotDQ)', 3); if (abAmt(d, 'Lunar Embodiment') !== 1 || card('Waxing and Waning')) return 'Lunar Sorcery L3 falsch';
      sel('Sorcerer', 'Lunar Sorcery (DSotDQ)', 6); if (abAmt(d, 'Lunar Embodiment') !== 0) return 'Lunar Embodiment L6 noch mit Pip';
      if (JSON.stringify(rows('Waxing and Waning')) !== '[["Full Moon",1],["New Moon",1],["Crescent Moon",1]]') return 'Waxing and Waning L6: ' + JSON.stringify(rows('Waxing and Waning'));
      if (card('Lunar Phenomenon')) return 'Lunar Phenomenon L6 sichtbar';
      sel('Sorcerer', 'Lunar Sorcery (DSotDQ)', 18); if (rows('Lunar Phenomenon').length !== 3) return 'Lunar Phenomenon L18 nicht 3 Phasen';
      // Aufgeklappte Karte bleibt nach Pip-Klick offen; Reset leert auch Einzel-Tracker, Auswahl bleibt
      w.togAb('lu_lunarphenomenon'); card('Lunar Phenomenon').querySelector('.ab-sub .ab-pip').click();
      if (!d.getElementById('ab_lu_lunarphenomenon').classList.contains('on')) return 'Karte nach Klick zugeklappt';
      w.restoreAllUses(); if (Object.keys(w.eval('st.abUses')).length) return 'Reset leert Einzel-Tracker nicht';
      if (w.eval('st.abPick.rk_runes').length !== 3) return 'Reset löscht Runen-Auswahl';
      return true;
    } },
  { name: 'Zauber-Auswahl: Spell List filtert standardmäßig nach der Klasse (CLASS_SPELL_MAP), Blessed/Druidic Warrior ab L2, Subklassen-Zauber, Magical Secrets ab L10, „All" zeigt alles', datum: '27.09.2026',
    run: ({ w, d, sel }) => {
      if (w.eval('typeof SUBCLASS_SPELLS') === 'undefined' || w.eval('typeof slMySpellCtx') === 'undefined') return 'Klassenfilter fehlt (SUBCLASS_SPELLS/slMySpellCtx)';
      if (w.eval('typeof zbRender') !== 'undefined') return 'toter Code zbRender noch vorhanden';
      if (w.eval('slFClass') !== 'mine') return 'Standard-Filter nicht „meine Klasse"';
      const ZB = JSON.parse(w.eval('JSON.stringify(ZB_SPELLS.map(s=>({name:s.name,grad:s.grad,classes:s.classes||[]})))')), SS = JSON.parse(w.eval('JSON.stringify(SUBCLASS_SPELLS)'));
      const on = (c, s) => s.classes.includes(c);
      const list = () => { w.slRender(); return new Map([...d.querySelectorAll('#slList .zb-card')].map(c => [c.querySelector('.zb-name').textContent, (c.querySelector('.sl-via')?.textContent || '').replace('✦ ', '')])); };
      // Paladin: eigene Liste + Oath-of-Devotion-Zauber; Cleric-Cantrips erst ab L2 (Blessed Warrior)
      const pal = ZB.filter(s => on('Paladin', s)), dev = SS.Paladin['Oath of Devotion'].spells.filter(n => !ZB.some(s => s.name === n && on('Paladin', s)));
      const clc = ZB.filter(s => s.grad === 0 && on('Cleric', s) && !on('Paladin', s));
      if (!dev.length || !clc.length) return 'Testdaten fehlen (Devotion-Zusatzzauber/Cleric-Cantrips)';
      sel('Paladin', 'Oath of Devotion (PHB)', 1); let L = list();
      if (L.size !== pal.length + dev.length) return `Paladin L1: ${L.size} Zauber statt ${pal.length} + ${dev.length}`;
      if (L.get(dev[0]) !== 'Oath of Devotion') return dev[0] + ' ohne Herkunft „Oath of Devotion" (' + L.get(dev[0]) + ')';
      if (clc.some(s => L.has(s.name))) return 'Cleric-Cantrip schon auf L1';
      sel('Paladin', 'Oath of Devotion (PHB)', 2); L = list();
      if (clc.some(s => L.get(s.name) !== 'Blessed Warrior')) return 'Blessed Warrior: Cleric-Cantrips fehlen auf L2';
      if (ZB.some(s => s.grad > 0 && on('Cleric', s) && !on('Paladin', s) && !dev.includes(s.name) && L.has(s.name))) return 'Paladin sieht Cleric-Zauber über Grad 0';
      if (!d.getElementById('slClassBadge').textContent.includes('Paladin')) return 'Filter-Anzeige ohne Klasse';
      // Ranger: Druid-Cantrips (Druidic Warrior), Gloom-Stalker-Zauber außerhalb der Ranger-Liste
      sel('Ranger', 'Gloom Stalker (XGE)', 3); L = list();
      const drc = ZB.find(s => s.grad === 0 && on('Druid', s) && !on('Ranger', s));
      if (L.get(drc.name) !== 'Druidic Warrior') return 'Druidic Warrior: ' + drc.name + ' fehlt';
      if (L.get('Disguise Self') !== 'Gloom Stalker') return 'Gloom Stalker: Disguise Self fehlt (' + L.get('Disguise Self') + ')';
      // Warlock/Hexblade: Expanded Spell List (Shield)
      sel('Warlock', 'The Hexblade (XGE)', 5); L = list(); if (L.get('Shield') !== 'The Hexblade') return 'Hexblade: Shield fehlt';
      // Fighter → Wizard-Liste
      sel('Fighter', 'Champion (PHB)', 5); L = list();
      if (!L.has('Fireball') || L.has('Cure Wounds') || L.size !== ZB.filter(s => on('Wizard', s)).length) return 'Fighter zeigt nicht die Wizard-Liste';
      // Bard: Magical Secrets (Cleric/Druid/Wizard) erst ab L10
      const ws = ZB.find(s => s.grad > 0 && on('Wizard', s) && !on('Bard', s)).name;
      sel('Bard', 'College of Valor (PHB)', 9); if (list().has(ws)) return 'Magical Secrets schon auf L9 (' + ws + ')';
      sel('Bard', 'College of Valor (PHB)', 10); if (list().get(ws) !== 'Magical Secrets') return 'Magical Secrets L10: ' + ws + ' fehlt';
      // Monk ohne Subklassen-Zauber: kein „★"-Knopf, alles sichtbar; Warrior of Shadow: Darkness
      sel('Monk', 'Warrior of the Open Hand (XPHB)', 5); L = list();
      if (L.size !== ZB.length || d.getElementById('slMineBtn').style.display !== 'none') return 'Monk ohne Zauber: ' + L.size + ' statt alle / Knopf sichtbar';
      sel('Monk', 'Warrior of Shadow (XPHB)', 5); L = list(); if (L.get('Darkness') !== 'Warrior of Shadow' || L.size >= ZB.length) return 'Warrior of Shadow: Darkness fehlt';
      // Ein Klick auf „All" zeigt alle Zauber, „Clear all" kehrt zu „meine Klasse" zurück
      sel('Cleric', 'Life Domain (PHB)', 5); if (list().size >= ZB.length) return 'Cleric nicht gefiltert';
      d.querySelector('#slClassRow .fbtn[data-val="all"]').click();
      if (d.querySelectorAll('#slList .zb-card').length !== ZB.length) return '„All" zeigt nicht alle Zauber';
      w.slClearAllFilters(); if (w.eval('slFClass') !== 'mine' || d.querySelectorAll('#slList .zb-card').length >= ZB.length) return '„Clear all" nicht zurück auf meine Klasse';
      return true;
    } },
  { name: 'Combat-Tab-Umbau: Kampfwerte-Karte (CLASS_TABLES, Unarmored AC), Features nach Aktion/Bonusaktion/Reaktion/Passiv, Ausschlussliste, keine Dopplung mit Trackern', datum: '27.09.2026',
    run: ({ w, d, sel }) => {
      const cs = () => d.getElementById('combatStats');
      if (!cs()) return 'Kampfwerte-Karte fehlt (#combatStats)';
      const chip = l => { const c = [...cs().querySelectorAll('.cst-chip')].find(x => x.querySelector('.cst-l').textContent === l); return c ? c.querySelector('.cst-v').textContent : null; };
      const grps = () => [...d.querySelectorAll('#abList .ab-grp')].map(g => g.dataset.grp);
      const inGrp = (k, n) => { const b = d.querySelector(`#abList .ab-grp-box[data-grp="${k}"]`); return !!b && [...b.querySelectorAll('.ab-name')].some(x => x.textContent.trim() === n); };
      // seit Actions-Umbau (27.09.2026) stehen ausgeschlossene Features in der Gruppe „Weitere" → hier nicht mitzählen
      const cnt = n => [...d.querySelectorAll('#abList .ab-name')].filter(x => !x.closest('.ab-grp-box[data-grp="weitere"]') && x.textContent.trim() === n).length;
      w.eval('st.attrs.DEX=16;st.attrs.WIS=14;st.attrs.CON=12');
      // Monk L7: Martial Arts 1d8, Unarmored AC 10+3+2, Gruppen in fester Reihenfolge
      sel('Monk', 'Warrior of the Open Hand (XPHB)', 7);
      if (cs().style.display === 'none') return 'Kampfwerte-Karte unsichtbar';
      if (chip('Martial Arts') !== '1d8' || chip('Focus Points') !== '7' || chip('Unarmored Movement') !== '+15 ft.' || chip('Prof. Bonus') !== '+3') return 'Monk L7 Kampfwerte falsch: ' + cs().textContent;
      if (chip('Unarmored AC') !== '15') return 'Monk Unarmored AC ' + chip('Unarmored AC') + ' statt 15 (DEX 16, WIS 14)';
      if (JSON.stringify(grps()) !== '["bonus","reaktion","passiv","weitere"]') return 'Monk-Gruppen: ' + JSON.stringify(grps());
      if (!inGrp('reaktion', 'Deflect Attacks') || !inGrp('passiv', 'Evasion') || !inGrp('passiv', 'Stunning Strike') || !inGrp('bonus', 'Martial Arts')) return 'Monk-Features fehlen/falsche Gruppe';
      if (cnt('Ability Score Improvement') || cnt('Monk Subclass') || cnt("Monk's Focus")) return 'Ausschlussliste/Tracker-Dopplung wirkt nicht (ASI, Monk Subclass, Monk\'s Focus)';
      if (cnt('Focus Points') !== 1) return 'Focus Points ' + cnt('Focus Points') + '× statt 1×';
      // Rogue L5: Sneak Attack 3d6, Uncanny Dodge Reaktion, Thieves' Cant/Expertise ausgeblendet
      sel('Rogue', 'Thief (PHB)', 5);
      if (chip('Sneak Attack') !== '3d6' || chip('Unarmored AC') !== null) return 'Rogue L5 Kampfwerte falsch: ' + cs().textContent;
      if (!inGrp('reaktion', 'Uncanny Dodge') || !inGrp('bonus', 'Cunning Action') || !inGrp('passiv', 'Sneak Attack')) return 'Rogue-Features fehlen/falsche Gruppe';
      if (cnt("Thieves' Cant") || cnt('Expertise') || cnt('Second-Story Work')) return 'Rogue: Nicht-Kampf-Features sichtbar';
      // Fighter L17: mehrfache Features nur einmal, Zauberplätze nur bei Zauberern
      sel('Fighter', 'Champion (PHB)', 17);
      if (cnt('Action Surge') !== 1 || cnt('Indomitable') !== 1 || cnt('Extra Attack') !== 1) return 'Fighter: mehrfache Features doppelt';
      if (cs().querySelector('.cst-slot')) return 'Fighter zeigt Zauberplätze';
      if (chip('Second Wind') !== '4') return 'Fighter Second Wind ' + chip('Second Wind');
      // Warlock L5: Pakt-Slots aus der Class Table, Eldritch Master nur im Tracker (angehängt)
      sel('Warlock', 'Fiend Patron (XPHB)', 5);
      if (chip('Spell Slots') !== '2' || chip('Slot Level') !== '3') return 'Warlock Pakt-Slots falsch: ' + cs().textContent;
      if (cnt('Eldritch Invocation Options') || cnt('Pact Magic')) return 'Warlock: Invocation Options/Pact Magic doppelt';
      sel('Warlock', 'Fiend Patron (XPHB)', 20); if (cnt('Eldritch Master')) return 'Eldritch Master doppelt (steht im Tracker Magical Cunning)';
      // Wizard L5: Zauberplätze 4/3/2, Spells-Listen/Savant ausgeblendet, Sculpt Spells sichtbar
      sel('Wizard', 'Evoker (XPHB)', 6);
      if ([...cs().querySelectorAll('.cst-slot')].map(x => x.textContent).join(',') !== '1st4,2nd3,3rd3') return 'Wizard L6 Zauberplätze: ' + [...cs().querySelectorAll('.cst-slot')].map(x => x.textContent);
      if (cnt('Evocation Savant') || cnt('Spellcasting') || cnt('Ritual Adept') || !cnt('Sculpt Spells')) return 'Wizard: Ausschlussliste falsch';
      sel('Cleric', 'Life Domain (PHB)', 3); if (cnt('Life Domain Spells') || cnt('Domain Spells')) return 'Cleric: Domain Spells sichtbar';
      // Barbarian: Unarmored AC mit CON, Gruppe zuklappen
      sel('Barbarian', 'Path of the Berserker (PHB)', 5);
      if (chip('Unarmored AC') !== '14' || chip('Rage Damage') !== '+2') return 'Barbarian Kampfwerte falsch: ' + cs().textContent;
      w.togAbGrp('passiv');
      if (d.querySelector('#abList .ab-grp-box[data-grp="passiv"]').style.display !== 'none') return 'Gruppe lässt sich nicht zuklappen';
      w.togAbGrp('passiv');
      if (d.querySelector('#abList .ab-grp-box[data-grp="passiv"]').style.display === 'none') return 'Gruppe lässt sich nicht aufklappen';
      // Feature-Karte aufklappen, bleibt nach Tracker-Klick offen
      const f = [...d.querySelectorAll('#abList .ab-card.ab-feat')].find(x => x.querySelector('.ab-name').textContent.trim() === 'Danger Sense');
      if (!f) return 'Danger Sense fehlt';
      f.querySelector('.ab-top').click();
      w.togAbUse('bb_rage', 0, 3);
      const f2 = [...d.querySelectorAll('#abList .ab-card.ab-feat')].find(x => x.querySelector('.ab-name').textContent.trim() === 'Danger Sense');
      if (!f2.querySelector('.ab-body').classList.contains('on')) return 'Feature-Karte nach Tracker-Klick zugeklappt';
      w.restoreAllUses();
      return true;
    } },
  { name: 'Actions-Umbau: Gruppe „Weitere" (ausgeschlossene Features, startet zu, Zustand pro Charakter gespeichert), Class Features vor Spellcasting, Tab „Actions", Pips/Zauberplätze zeigen Verfügbares', datum: '27.09.2026',
    run: ({ w, d, sel }) => {
      const box = k => d.querySelector(`#abList .ab-grp-box[data-grp="${k}"]`);
      const names = k => [...(box(k)?.querySelectorAll('.ab-name') || [])].map(x => x.textContent.trim());
      w.eval("st.abUses={};st.abGrpClosed={};document.getElementById('charName').textContent='Regressionstest'");
      // 1) „Weitere" am Ende, enthält die ausgeschlossenen Features, startet zugeklappt, Zustand wird gespeichert
      sel('Rogue', 'Thief (PHB)', 5);
      const g = [...d.querySelectorAll('#abList .ab-grp')].map(x => x.dataset.grp);
      if (g[g.length - 1] !== 'weitere') return 'Gruppe „Weitere" fehlt oder nicht am Ende: ' + JSON.stringify(g);
      for (const n of ["Thieves' Cant", 'Expertise', 'Ability Score Improvement']) if (!names('weitere').includes(n)) return n + ' fehlt in „Weitere"';
      if (names('passiv').includes('Expertise')) return 'Expertise noch in Passiv';
      if (box('weitere').style.display !== 'none') return '„Weitere" startet nicht zugeklappt';
      w.togAbGrp('weitere');
      if (box('weitere').style.display === 'none') return '„Weitere" lässt sich nicht aufklappen';
      let sv = JSON.parse(w.localStorage.getItem('dnd5e_chars') || '{}').Regressionstest;
      if (!sv || sv.abGrpClosed?.weitere !== false) return 'Gruppen-Zustand nicht gespeichert (st.abGrpClosed)';
      w.togAbGrp('passiv');
      sv = JSON.parse(w.localStorage.getItem('dnd5e_chars') || '{}').Regressionstest;
      if (sv.abGrpClosed?.passiv !== true) return 'Zuklappen „Passiv" nicht gespeichert';
      w.eval('applyState(JSON.parse(localStorage.getItem("dnd5e_chars")).Regressionstest)'); w.buildAbilities();
      if (box('passiv').style.display !== 'none' || box('weitere').style.display === 'none') return 'Gruppen-Zustand nach Laden nicht übernommen';
      w.togAbGrp('passiv');
      // 2) Reihenfolge: Class Features vor Spellcasting
      const ab = d.getElementById('abilitiesSection'), sp = d.getElementById('subpanel-meinezauber');
      if (!(ab.compareDocumentPosition(sp) & 4)) return 'Class Features steht nicht vor Spellcasting';
      if (!(d.getElementById('weaponList').compareDocumentPosition(ab) & 4)) return 'Class Features steht vor Weapons';
      // 3) Tab heißt „Actions" (oben und unten), data-tab bleibt „zauber"
      if (d.querySelector('.tab[data-tab="zauber"]')?.textContent.trim() !== 'Actions') return 'oberer Tab heißt nicht „Actions"';
      if (d.querySelector('.bnav-btn[data-tab="zauber"] .bnav-label')?.textContent.trim() !== 'Actions') return 'untere Leiste heißt nicht „Actions"';
      // 4) Pips: alle gefüllt = alles verfügbar; Tippen auf gefüllten Kreis verbraucht, auf leeren gibt zurück
      sel('Barbarian', 'Path of the Berserker (PHB)', 5);
      const rage = () => [...d.querySelectorAll('#abList .ab-card:not(.ab-feat)')].find(x => x.querySelector('.ab-name').textContent.trim() === 'Rage');
      const av = () => rage().querySelectorAll('.ab-pip.avail').length;
      if (rage().querySelectorAll('.ab-pip').length !== 3 || av() !== 3) return 'Rage L5: ' + av() + ' von 3 gefüllt (erwartet alle)';
      rage().querySelectorAll('.ab-pip')[0].click();
      if (av() !== 2 || w.eval('st.abUses.bb_rage') !== 1) return 'Tipp auf gefüllten Kreis: ' + av() + ' gefüllt, Verbrauch ' + w.eval('st.abUses.bb_rage');
      if (!rage().querySelectorAll('.ab-pip')[2].classList.contains('used') || !rage().querySelectorAll('.ab-pip')[0].classList.contains('avail')) return 'Verfügbare Kreise nicht links';
      rage().querySelectorAll('.ab-pip')[2].click();
      if (av() !== 3 || w.eval('st.abUses.bb_rage') !== 0) return 'Tipp auf leeren Kreis gibt nicht zurück';
      w.eval('st.slotAdj=[4,0,0,0,0,0,0,0,0];st.slotUsed[0]=0'); w.buildSlots(); // seit Paket D: Barbarian ohne Plätze + Korrektur 4
      const sl = () => d.querySelectorAll('#spSlots .slvl')[0];
      if (sl().querySelectorAll('.slpip.av').length !== 4) return 'Zauberplätze Grad 1 nicht alle gefüllt';
      sl().querySelectorAll('.slpip')[1].click();
      if (sl().querySelectorAll('.slpip.av').length !== 3 || w.eval('st.slotUsed[0]') !== 1) return 'Zauberplatz-Tipp verbraucht nicht';
      sl().querySelectorAll('.slpip')[3].click();
      if (sl().querySelectorAll('.slpip.av').length !== 4 || w.eval('st.slotUsed[0]') !== 0) return 'Zauberplatz-Tipp auf leeren Kreis gibt nicht zurück';
      return true;
    } },
  { name: 'Actions: Karte „Combat Stats" unter Hit Points (vor Weapons), startet zugeklappt, Zustand gespeichert; kein Spell-List-Link oben im Tab', datum: '27.09.2026',
    run: ({ w, d, sel }) => {
      w.eval("st.abGrpClosed={};document.getElementById('charName').textContent='Regressionstest'");
      if (d.querySelector("#tab-zauber button[onclick*=\"switchTab('spelllist')\"]")) return 'Spell-List-Link noch im Actions-Tab';
      if (!d.querySelector('.tab[data-tab="spelllist"]')) return 'Spell List nicht mehr über die Tab-Leiste erreichbar';
      const cs = d.getElementById('combatStats'), hp = [...d.querySelectorAll('#tab-zauber .sec')].find(x => x.textContent.trim() === 'Hit Points');
      if (!hp || !(hp.compareDocumentPosition(cs) & 4)) return 'Combat Stats steht nicht unter Hit Points';
      if (!(cs.compareDocumentPosition(d.getElementById('weaponList')) & 4)) return 'Combat Stats steht nicht vor Weapons';
      sel('Monk', 'Warrior of the Open Hand (XPHB)', 7);
      const body = () => cs.querySelector('.cst-body');
      if (!body() || body().style.display !== 'none') return 'Combat Stats startet nicht zugeklappt';
      cs.querySelector('.cst-head').click();
      if (body().style.display === 'none') return 'Combat Stats lässt sich nicht aufklappen';
      if (JSON.parse(w.localStorage.getItem('dnd5e_chars') || '{}').Regressionstest?.abGrpClosed?.stats !== false) return 'Zustand Combat Stats nicht gespeichert';
      sel('Monk', 'Warrior of the Open Hand (XPHB)', 8); if (body().style.display === 'none') return 'Combat Stats nach Stufenwechsel wieder zu';
      return true;
    } },
  { name: 'UI/Lesbarkeit: keine Schrift unter 11px (Typo-Skala), Textgröße in ⚙ (pro Gerät), HP-Karten ohne feste Breite, Zauberplatz-Knöpfe groß', datum: '27.09.2026',
    run: ({ w, d, sel }) => {
      const html = d.documentElement.outerHTML;
      const tiny = [...html.matchAll(/font-size:\s*(\d+(?:\.\d+)?)px/g)].filter(m => +m[1] < 11).length;
      if (tiny) return tiny + '× Schriftgröße unter 11px';
      const cs = w.getComputedStyle(d.documentElement);
      if (cs.getPropertyValue('--fs-2xs').trim() !== '11px' || cs.getPropertyValue('--fs-txt').trim() !== '15px') return 'Typo-Variablen fehlen';
      if (typeof w.setTextSize !== 'function' || !d.getElementById('tsRow')) return 'Textgröße-Einstellung fehlt';
      w.openSettings(); if (!d.querySelector('#tsRow .fbtn.on[data-ts="normal"]')) return 'Standard nicht „Normal" markiert';
      w.setTextSize('gross');
      if (d.documentElement.dataset.ts !== 'gross' || w.localStorage.getItem('willow_textsize') !== 'gross' || !d.querySelector('#tsRow .fbtn.on[data-ts="gross"]')) return 'Stufe „Large" nicht gesetzt/gespeichert';
      w.setTextSize('normal'); if ('ts' in d.documentElement.dataset || w.localStorage.getItem('willow_textsize') !== 'normal') return 'Zurück auf „Normal" klappt nicht';
      w.closeSettings && w.closeSettings();
      if (!/data-ts="sehrgross"\]\{zoom:1\.3/.test(html) || !html.includes("localStorage.getItem('willow_textsize')")) return 'Zoom-CSS oder Frühstart-Skript fehlt';
      if (/id="hp[MT]"[^>]*width:44px/.test(html)) return 'HP-Eingabe mit fester Breite (Temp ragt über den Rand)';
      w.eval('slotEdit=true'); w.buildSlots(); if (d.querySelectorAll('#spSlots .slbtn').length !== 18) return 'Zauberplatz-Knöpfe ohne .slbtn (Modus ✎ Adjust, Paket D)'; w.eval('slotEdit=false'); w.buildSlots();
      return true;
    } },
  { name: 'Farben: Beschreibungen hell (--desc), Labels/Highlight hellgold, --muted für Leiste/Platzhalter, eigene Farben gehen vor, Farbauswahl gruppiert', datum: '27.09.2026',
    run: ({ w, d, sel }) => {
      if (typeof w.themeBase !== 'function') return 'themeBase fehlt';
      sel('Barbarian', 'Path of the Berserker (PHB)', 5); w.applyTheme('Barbarian');
      const v = k => d.documentElement.style.getPropertyValue('--' + k).trim().toLowerCase();
      const T = w.eval('CLASS_THEMES.Barbarian');
      if (v('purple') !== '#ecd592' || v('text3') !== '#b8a06a') return 'Highlight/Labels nicht hellgold: ' + v('purple') + ' / ' + v('text3');
      if (v('muted') !== T.text3.toLowerCase()) return '--muted ≠ alter text3';
      if (v('desc') !== w.hexMix(T.text, T.text2, .2)) return '--desc falsch: ' + v('desc');
      const css = [...d.querySelectorAll('style')].map(x => x.textContent).join('');
      for (const c of ['.ab-desc{', '.feat-desc{', '.desc-text{', '.bg-desc{']) { const i = css.indexOf(c); if (i < 0 || !css.slice(i, css.indexOf('}', i)).includes('var(--desc)')) return c + ' ohne --desc'; }
      const i = css.indexOf('.bnav-btn{'); if (!css.slice(i, css.indexOf('}', i)).includes('var(--muted)')) return 'Leiste inaktiv nicht --muted';
      w.localStorage.setItem('dnd5e_theme_overrides', JSON.stringify({ Barbarian: { text3: '#123456', desc: '#abcdef' } })); w.applyTheme('Barbarian');
      if (v('text3') !== '#123456' || v('desc') !== '#abcdef') return 'eigene Farben gehen nicht vor';
      w.localStorage.removeItem('dnd5e_theme_overrides'); w.applyTheme('Barbarian');
      w.openSettings();
      const g = [...d.querySelectorAll('#settingsColorPanels .clr-grp summary')].map(x => x.textContent.trim());
      if (JSON.stringify(g) !== '["Backgrounds","Text","Accents","Status"]') return 'Farbgruppen: ' + JSON.stringify(g);
      if ((d.getElementById('settingsColorPanels').textContent.match(/#[0-9a-f]{6}/gi) || []).length !== 16) return 'nicht 16 Farbfelder';
      w.closeSettings();
      return true;
    } },
  { name: 'Text-Formatierer: Absätze, Listen, Blocknamen, Tabellen, Tabellenwerte der Stufe; HTML-sicher; überall eingesetzt', datum: '27.09.2026',
    run: ({ w, d, sel }) => {
      if (typeof w.fmtDesc !== 'function') return 'fmtDesc fehlt';
      const box = h => { const x = d.createElement('div'); x.innerHTML = h; return x; };
      // Grundformen
      let x = box(w.fmtDesc('Erster Absatz.\nNumber of Uses. Zwei Mal.\nYou gain the following benefits:\n• Eins\n• Zwei'));
      if (x.querySelectorAll('.fd > p').length !== 3) return 'Absätze: ' + x.querySelectorAll('.fd > p').length + ' statt 3';
      if (x.querySelector('.fd-n')?.textContent !== 'Number of Uses.') return 'Blockname nicht fett: ' + x.querySelector('.fd-n')?.textContent;
      if (x.querySelectorAll('li').length !== 2) return 'Liste nicht erkannt';
      if (box(w.fmtDesc('You gain two uses. Then more.')).querySelector('.fd-n')) return 'Satzanfang fälschlich als Blockname';
      if (box(w.fmtDesc('<img src=x onerror=alert(1)>')).querySelector('img')) return 'Text nicht escaped';
      // Tabellen: Kopfzeile + „• a | b", Überschrift + „• Schlüssel: Wert"
      x = box(w.fmtDesc('Beast Shapes:\nDruid Level | Known Forms\n• 2 | 4\n• 4 | 6'));
      if (x.querySelector('.fd-cap')?.textContent !== 'Beast Shapes' || x.querySelectorAll('.fd-tbl th').length !== 2 || x.querySelectorAll('.fd-tbl td').length !== 4) return 'Pipe-Tabelle falsch';
      x = box(w.fmtDesc('Runes Known:\n• 3rd: 2\n• 7th: 3\nDanach.'));
      if (!x.querySelector('.fd-kv') || x.querySelectorAll('.fd-kv tr').length !== 2 || x.querySelector('.fd-k').textContent !== '3rd') return 'Schlüssel/Wert-Tabelle falsch';
      // Fortsetzungszeile gehört zum vorigen Listenpunkt
      x = box(w.fmtDesc('• Cloud Rune. ' + 'x'.repeat(90) + '\nIn addition, more.\n• Fire Rune. y'));
      if (x.querySelectorAll('li').length !== 2 || !x.querySelector('li .fd-cont')) return 'Fortsetzungszeile nicht im Listenpunkt';
      // Tabellenwerte im Feature-Text (Monk L7: Martial Arts 1d8)
      sel('Monk', 'Warrior of the Open Hand (XPHB)', 7);
      w.togAb('f_b_martial_arts');
      const ma = d.getElementById('ab_f_b_martial_arts');
      if (!ma) return 'Martial-Arts-Karte fehlt';
      if (ma.querySelector('.fd-tv')?.textContent !== 'Level 7: 1d8') return 'Tabellenwert Martial Arts: ' + ma.querySelector('.fd-tv')?.textContent;
      if (!ma.querySelector('.fd-n') || ma.querySelector('.ab-desc').style.whiteSpace) return 'Actions-Karte nicht formatiert';
      if (!d.getElementById('clsLoreBody').querySelector('.fd .fd-tv')) return 'Info-Tab ohne Tabellenwert';
      d.getElementById('lvl').value = '11'; d.getElementById('lvl').dispatchEvent(new w.Event('input'));
      if (![...d.getElementById('clsLoreBody').querySelectorAll('.fd-tv')].some(t => t.textContent === 'Level 11: 1d10')) return 'Info-Tab nach Stufenwechsel nicht aktualisiert';
      // Druid Wild Shape: Tabelle „Beast Shapes" in der Tracker-Karte, Info-Tab ohne pre-line
      sel('Druid', 'Circle of the Moon (PHB)', 5);
      const ws = [...d.querySelectorAll('#abList .ab-card:not(.ab-feat)')].find(c => c.querySelector('.ab-name').textContent.trim() === 'Wild Shape');
      if (!ws || !ws.querySelector('.ab-desc .fd-tbl th')) return 'Wild Shape ohne Tabelle';
      if (d.getElementById('clsLoreBody').innerHTML.includes('pre-line')) return 'Info-Tab noch mit pre-line';
      // Zauber (Spell List) und Feats nutzen den Formatierer
      if (!w.formatSpellDesc('Set the Trigger. Text.').includes('fd-n')) return 'Zauber-Text nicht formatiert';
      const css = [...d.querySelectorAll('style')].map(s => s.textContent).join('');
      if (/\.ab-desc\{[^}]*pre-line/.test(css)) return '.ab-desc noch mit pre-line';
      const js = [...d.querySelectorAll('script')].map(s => s.textContent).join('\n');
      if (!js.includes('desc.innerHTML=fmtDesc(ft.d)') || !js.includes('<div class="feat-desc">${fmtDesc(f.desc)}</div>')) return 'Feats nicht formatiert';
      return true;
    } },
  { name: 'UI-Kleinkram: Würfel-Knopf in der unteren Leiste (kein .dice-fab, kein Tab-Wechsel), Skills-Icon 🎯', datum: '27.09.2026',
    run: ({ w, d, sel }) => {
      if (d.querySelector('.dice-fab')) return 'schwebender Würfel-Knopf noch vorhanden';
      const btns = [...d.querySelectorAll('#bottomNav .bnav-btn')];
      if (btns.length !== 5) return 'untere Leiste hat ' + btns.length + ' statt 5 Knöpfe';
      const labels = btns.map(b => b.querySelector('.bnav-label').textContent.trim());
      if (JSON.stringify(labels) !== '["Info","Skills","Würfel","Items","Actions"]') return 'Reihenfolge/Beschriftung: ' + JSON.stringify(labels);
      const diceBtn = btns[2];
      if (diceBtn.dataset.tab) return 'Würfel-Knopf hat data-tab (würde Tab wechseln)';
      if (diceBtn.getAttribute('onclick') !== "openDice('',0)") return 'Würfel-Knopf ruft nicht openDice auf';
      const skillsIcon = btns[1].querySelector('.bnav-icon').textContent;
      if (skillsIcon !== '🎯') return 'Skills-Icon ist „' + skillsIcon + '“ statt 🎯';
      const css = [...d.querySelectorAll('style')].map(x => x.textContent).join('');
      const i = css.indexOf('.bnav-dice .bnav-icon{');
      if (i < 0) return '.bnav-dice .bnav-icon Regel fehlt';
      const rule = css.slice(i, css.indexOf('}', i));
      if (!rule.includes('width:48px') || !rule.includes('margin:-16px')) return 'Würfel-Knopf ist nicht angehoben/vergrößert: ' + rule;
      sel('Druid', '', 5);
      diceBtn.click();
      if (!d.getElementById('diceModal').classList.contains('on')) return 'Würfel-Dialog öffnet sich nicht';
      if ([...d.querySelectorAll('.bnav-btn.on')].some(b => b === diceBtn)) return 'Würfel-Knopf wird als aktiver Tab markiert';
      const infoTab = d.querySelector('.tab[data-tab="info"]');
      if (!infoTab.classList.contains('on')) return 'Würfel-Knopf hat den Tab gewechselt';
      w.closeDice();
      return true;
    } },
  { name: 'Spell List: Seitenrand wie andere Tabs (kein </div> schließt .body vorzeitig), kein Leerraum über „← My Spells“', datum: '27.09.2026',
    run: ({ w, d, sel }) => {
      for (const id of ['tab-bestien', 'tab-feats', 'tab-spelllist', 'tab-notizen', 'tab-log']) {
        const el = d.getElementById(id);
        if (!el || el.parentElement.className !== 'body') return id + ' ist kein Kind von .body (.body wird vorher geschlossen)';
      }
      sel('Druid', 'Circle of the Stars (XPHB)', 5);
      w.switchTabAll('spelllist');
      const sw = d.querySelector('#tab-spelllist .search-wrap').getBoundingClientRect ? d.querySelector('#tab-spelllist .search-wrap') : null;
      const cs = w.getComputedStyle(d.getElementById('tab-spelllist').parentElement);
      if (cs.paddingLeft !== '14px') return '.body-Padding fehlt (' + cs.paddingLeft + ')';
      return true;
    } },
  { name: 'Paket A: Bestien sauber aus 5e.tools (keine {@-Reste, keine abgeschnittenen Texte), Stat-Block-Anzeige, gespeicherte Bestien mit aktuellen Daten, Zauber mit Stat-Block', datum: '27.09.2026',
    run: ({ w, d, sel }) => {
      if (typeof w.sbHtml !== 'function' || w.eval('typeof SPELL_STATBLOCKS') === 'undefined') return 'Stat-Block-Anzeige fehlt (sbHtml/SPELL_STATBLOCKS)';
      const B = JSON.parse(w.eval('JSON.stringify(BST_DATA)'));
      if (B.length !== 133) return 'BST_DATA hat ' + B.length + ' statt 133 Einträge';
      const raw = JSON.stringify(B);
      if (raw.includes('{@')) return (raw.match(/\{@/g) || []).length + '× {@-Rest in BST_DATA';
      if (B.some(b => [...b.actions, ...(b.bonus || []), ...(b.react || [])].some(a => /: (m|r|m,r) \d/.test(a)))) return 'Angriffe noch als „m 3“';
      const by = n => B.find(b => b.n === n);
      if (!by('Owl').actions[0].includes('Melee Attack Roll: +3, reach 5 ft. Hit: 1 Slashing damage.')) return 'Owl Talons: ' + by('Owl').actions[0];
      if (!by('Baboon').traits[0].endsWith('condition.')) return 'Baboon Pack Tactics abgeschnitten: ' + by('Baboon').traits[0].slice(-40);
      const web = by('Giant Spider').actions.find(a => a.startsWith('Web (Recharge 5–6):'));
      if (!web || !web.includes('Dexterity Saving Throw: DC 13') || !web.includes('Failure:') || !web.endsWith('Poison and Psychic damage).')) return 'Giant Spider Web falsch/abgeschnitten';
      if (!by('Unicorn').legend || !by('Unicorn').bonus) return 'Unicorn ohne Legendary/Bonus Actions';
      // Karte im Beasts-Tab: Stat-Block, englisch, 6 Attribute in einer Reihe, Abschnitte mit Überschrift
      w.switchTab('bestien');
      const card = [...d.querySelectorAll('#bstList .zb-card')].find(c => c.querySelector('.zb-name').textContent === 'Owl');
      if (!card) return 'Owl-Karte fehlt';
      const det = card.querySelector('.zb-detail');
      if (det.textContent.includes('Sinne') || !det.textContent.includes('Senses')) return 'Label „Sinne“ statt „Senses“';
      if (det.querySelectorAll('.sb-abrow .sb-ab').length !== 6) return 'Attribute nicht als Reihe (6 Kästen)';
      const secs = [...det.querySelectorAll('.sb-sec')].map(x => x.textContent);
      if (JSON.stringify(secs) !== '["Traits","Actions"]') return 'Abschnitte: ' + JSON.stringify(secs);
      if (!det.querySelector('.sb-en') || det.querySelector('.sb-en').textContent !== 'Flyby.') return 'Trait-Name nicht hervorgehoben';
      if (d.getElementById('bstList').innerHTML.includes('{@')) return '{@ im Beasts-Tab';
      // Gespeicherte Bestie mit altem (kaputtem) Text zeigt die aktuellen Daten
      w.eval(`st.savedBeasts=[{n:'Owl',type:'beast',size:'T',cr:'0',ac:'11',hp:'1',spd:'5 ft.',str:3,dex:13,con:8,int:2,wis:12,cha:7,skills:'',sens:'',actions:['Talons: m 3, reach 5 ft. {@h}1 Slashing damage.'],traits:[],fluff:''}]`);
      w.buildSavedBeasts();
      const sv = d.getElementById('bstSavedList').innerHTML;
      if (sv.includes('{@') || !sv.includes('Melee Attack Roll')) return 'gespeicherte Bestie zeigt alten Text';
      w.eval('st.savedBeasts=[]'); w.buildSavedBeasts();
      // Zauber mit Stat-Block: Spell List und My Spells
      const SS = JSON.parse(w.eval('JSON.stringify(SPELL_STATBLOCKS)'));
      for (const [sp, cr] of [['Summon Fey', 'Fey Spirit'], ['Summon Shadowspawn', 'Shadow Spirit'], ['Find Steed', 'Otherworldly Steed'], ['Phantom Steed', 'Riding Horse'], ['Create Undead', 'Ghoul'], ['Tiny Servant', 'Tiny Servant'], ['Spirit of Death', 'Reaper Spirit'], ['Giant Insect', 'Giant Insect'], ['Animate Objects', 'Animated Object']])
        if (!(SS[sp] || []).some(b => b.n === cr)) return sp + ' ohne Stat-Block ' + cr;
      if (JSON.stringify(SS).includes('{@') || JSON.stringify(SS).includes('summonSpellLevel')) return 'Tag-Rest in SPELL_STATBLOCKS';
      w.switchTab('spelllist');
      const i = w.eval("ZB_SPELLS.findIndex(s=>s.name==='Summon Fey')");
      w.eval("slFClass='all'"); w.slRender();
      const sc = d.getElementById('sld_' + i);
      if (!sc || !sc.querySelector('details.sb-det') || !sc.querySelector('details.sb-det summary').textContent.includes('Fey Spirit')) return 'Spell List: Stat-Block Fey Spirit fehlt';
      if (!sc.querySelector('.sb-abrow')) return 'Spell List: Stat-Block ohne Attribute';
      const j = w.eval("ZB_SPELLS.findIndex(s=>s.name==='Fireball')");
      if (d.getElementById('sld_' + j)?.querySelector('.sb-det')) return 'Fireball mit Stat-Block';
      w.eval("st.mySpells.push({name:'Summon Fey',grad:3,school:'Conjuration',prep:false,notes:''})"); w.buildMySpells();
      const ms = d.getElementById('msn_' + w.eval("st.mySpells.findIndex(s=>s.name==='Summon Fey')"));   // Index per Name (Paket H: Always Prepared kann Einträge anhängen)
      if (!ms || !ms.querySelector('.sb-det')) return 'My Spells: Stat-Block fehlt';
      w.eval('st.mySpells.pop()'); w.buildMySpells();
      return true;
    } },
  { name: 'Paket B: Expand-Knopf einzeilig, Attribute oben + Character Info zuklappbar (pro Charakter), Combat Stats (Prof. Bonus, 1st/2nd…), Death Saves/Inspiration getrennt, Websuche per Lupe', datum: '28.09.2026',
    run: ({ w, d, sel }) => {
      const css = [...d.querySelectorAll('style')].map(x => x.textContent).join('\n');
      const ft = (css.match(/\.filter-toggle\{[^}]*\}/) || [''])[0];
      if (!ft.includes('white-space:nowrap') || !ft.includes('flex-shrink:0')) return '.filter-toggle bricht noch um';
      const info = d.getElementById('tab-info'), ag = d.getElementById('attrGrid'), cb = d.getElementById('charInfoBody');
      if (!(ag.compareDocumentPosition(cb) & 4)) return 'Attribute stehen nicht über Character Info';
      if (!(d.getElementById('ac').compareDocumentPosition(cb) & 4)) return 'AC/Initiative/Speed nicht über Character Info';
      if (!info.contains(d.getElementById('charInfoBtn'))) return 'Knopf für Character Info fehlt';
      w.resetUI();
      if (cb.style.display === 'none' || w.eval('st.charInfoClosed') !== false) return 'Character Info startet nicht offen';
      w.togCharInfo();
      if (cb.style.display !== 'none' || !w.eval('collectState().charInfoClosed')) return 'Zuklappen wirkt/speichert nicht';
      const snap = w.eval('collectState()'); w.resetUI();
      if (cb.style.display === 'none') return 'resetUI klappt nicht wieder auf';
      w.applyState(snap);
      if (cb.style.display !== 'none' || d.getElementById('charInfoBtn').textContent !== '▾ Expand') return 'Zustand nicht geladen';
      w.applyState({ attrs: {} });
      if (cb.style.display === 'none') return 'alter Save ohne Feld: nicht offen';
      sel('Druid', '', 7);
      const cs = d.getElementById('combatStats');
      if (!cs.textContent.includes('Prof. Bonus') || ![...cs.querySelectorAll('.cst-slot b')].map(b => b.textContent).join(',').startsWith('1st,2nd,3rd,4th')) return 'Combat Stats Beschriftung: ' + cs.textContent;
      if (d.querySelectorAll('.ds-row .ds-box').length !== 2 || d.querySelectorAll('#dsS .dspip').length !== 3 || !d.getElementById('ins2')) return 'Death Saves/Inspiration-Aufbau';
      w.togIns(1); if (!d.getElementById('ins1').classList.contains('f')) return 'togIns wirkt nicht'; w.togIns(1);
      let opened = null; w.open = u => { opened = u; };
      w.localStorage.removeItem('willow_websearch');
      if (!d.getElementById('webSearchBtn')) return 'Lupe fehlt';
      w.openWebSearch(); d.getElementById('webSearchIn').value = 'Fireball'; w.runWebSearch();
      if (opened !== 'https://www.startpage.com/do/search?q=D%26D%205e%20Fireball') return 'Such-URL (Startpage statt google.com, sonst öffnet iOS die Google-App): ' + opened;
      if (JSON.parse(w.localStorage.getItem('willow_websearch'))[0] !== 'Fireball') return 'letzte Suche nicht gemerkt';
      w.openWebSearch(); if (d.querySelectorAll('#webSearchRecent .ws-chip').length !== 1) return 'letzte Suchen nicht angezeigt';
      w.closeWebSearch();
      return true;
    } },
  { name: 'Text-Formatierer auch für Rassen-Traits und Background-Texte (Aasimar-Verwandlungen als Liste in Celestial Revelation, keine **-Reste)', datum: '28.09.2026',
    run: ({ w, d, set }) => {
      set('race', 'Aasimar'); w.onRaceChange && w.onRaceChange(); w.buildRaceLore();
      const body = d.getElementById('raceLoreBody');
      const names = [...body.querySelectorAll('div[style*="Cinzel"]')].map(x => x.textContent);
      if (names.join('|') !== 'Size|Celestial Resistance|Darkvision|Healing Hands|Light Bearer|Celestial Revelation')  /* Size-Karte seit Paket C3 */ return 'Aasimar-Karten: ' + names.join('|');
      if (!body.querySelector('.fd ul') || body.querySelectorAll('.fd ul li').length !== 3) return 'Aasimar-Verwandlungen nicht als Liste';
      set('race', 'Elf'); w.buildRaceLore();
      if (body.querySelectorAll('.fd p').length < 6) return 'Elf: Folgeabsätze fehlen';
      // seit 28.09.2026 (Paket C1) mit SCAG-Background: der XPHB-Acolyte hat kein Feature mehr (vorher fälschlich der PHB-Text)
      w.eval("st.bg='Cloistered Scholar'"); w.buildBgLore();
      const bg = d.getElementById('bgLoreBody');
      if (bg.innerHTML.includes('**') || !bg.querySelector('.bg-cap') || !bg.querySelector('.bg-cap').textContent.startsWith('Feature: ')) return 'Background-Überschrift';
      if (bg.querySelectorAll('.fd p').length < 2 || bg.innerHTML.includes('<br>')) return 'Background-Absätze nicht über fmtDesc';
      w.eval("st.bg=''"); set('race', '');
      return true;
    } },
  { name: 'Paket C1: st.picks + calcGrants – Klassen-Saves automatisch, Klassen-/Background-Skill-Wahl, Doppel-Hinweis mit Ersatz, Attributs-Abzeichen (nicht aufgerechnet), alte Saves/manuelle Skills unverändert, kein Übertrag beim Charakterwechsel, BG_DATA vollständig', datum: '28.09.2026',
    run: ({ w, d, sel }) => {
      if (typeof w.calcGrants !== 'function' || typeof w.pickUI !== 'function') return 'calcGrants/pickUI fehlen';
      const sk = n => [...d.querySelectorAll('#skillsGrid .sk-row')].find(r => r.querySelector('.sk-name').firstChild.textContent === n);
      const sv = l => [...d.querySelectorAll('#savesGrid .sk-row')].find(r => r.querySelector('.sk-name').firstChild.textContent === l);
      const pip = r => r.querySelector('.sk-pip').className.replace('sk-pip', '').trim();
      const bdg = r => [...r.querySelectorAll('.sk-bdg')].map(b => b.textContent).join(',');
      // Daten: alle Background-Skills bekannt, Faction Agent/Planar Philosopher vollständig (5e.tools)
      const SK = w.eval('SKILLS.map(s=>s.n)'), BG = w.eval('BG_DATA');
      for (const b of BG) { const sp = w.bgSkillSpec(b); for (const x of [...sp.fest, ...sp.wahl.flatMap(v => v.from)]) if (!SK.includes(x)) return `Skill unbekannt: ${b.n} „${x}"`; if (b.s.some(x => x.includes('...'))) return 'abgeschnitten: ' + b.n; }
      if (w.bgSkillSpec(BG.find(b => b.n === 'Faction Agent')).wahl[0].from.length !== 13 || w.bgSkillSpec(BG.find(b => b.n === 'Planar Philosopher')).wahl[0].from.length !== 12) return 'Faction Agent/Planar Philosopher unvollständig';
      // alter Save ohne picks: lädt unverändert, manuelle Ebene bleibt
      w.resetUI();
      w.applyState({ attrs: { STR: 10, DEX: 14, CON: 10, INT: 16, WIS: 10, CHA: 10 }, saveP: { DEX: true }, skillP: { Stealth: 'e', Arcana: 'p' }, _f_cls: '', _f_prof: '2' });
      if (JSON.stringify(w.eval('st.picks')) !== '{}') return 'alter Save: picks nicht leer';
      if (pip(sk('Stealth')) !== 'e' || pip(sk('Arcana')) !== 'p' || bdg(sk('Arcana')) !== '' || pip(sv('Dexterity')) !== 'p' || pip(sv('Intelligence')) !== '') return 'alter Save: manuelle Werte verändert';
      // Klasse: Saves automatisch mit Abzeichen, Antippen nimmt sie nicht weg
      sel('Wizard', '', 1);
      if (pip(sv('Intelligence')) !== 'p' || bdg(sv('Intelligence')) !== 'Class' || pip(sv('Wisdom')) !== 'p' || pip(sv('Dexterity')) !== 'p') return 'Wizard-Saves';
      if (sv('Intelligence').querySelector('.sk-bon').textContent !== '+5') return 'Save-Bonus INT: ' + sv('Intelligence').querySelector('.sk-bon').textContent;
      sv('Intelligence').click(); if (pip(sv('Intelligence')) !== 'p') return 'Antippen nimmt Klassen-Save weg';
      // Klassen-Skill-Wahl über Chips (Info-Tab)
      const chip = (root, o) => [...d.querySelectorAll(root + ' .pk-chip')].find(c => c.dataset.o === o);
      if (!d.getElementById('coreTraitsList').textContent.includes('Choose 2 (0/2)') || d.getElementById('coreTraitsPend').textContent !== '● Choose') return 'offene Klassen-Wahl nicht gezeigt';
      if (!d.getElementById('pkHints').textContent.includes('Class skills 0/2')) return 'Hinweis im Skills-Tab fehlt';
      chip('#coreTraitsList', 'History').click(); chip('#coreTraitsList', 'Investigation').click(); chip('#coreTraitsList', 'Nature').click();
      if (JSON.stringify(w.eval("st.picks['cls:Wizard:skills']")) !== '["History","Investigation"]') return 'Klassen-Wahl: ' + JSON.stringify(w.eval('st.picks'));
      if (pip(sk('History')) !== 'p' || bdg(sk('History')) !== 'Class' || d.getElementById('coreTraitsPend').textContent !== '' || d.getElementById('pkHints').textContent !== '') return 'Klassen-Skill nicht wirksam';
      if (JSON.stringify(w.eval('st.skillP')) !== '{"Stealth":"e","Arcana":"p"}') return 'manuelle Skills verändert';
      // Antippen bei Auto-p: nur manuelle Ebene → Expertise
      sk('History').click(); if (pip(sk('History')) !== 'e' || w.eval("st.skillP.History") !== 'e') return 'Antippen Auto-Skill → e';
      sk('History').click(); if (pip(sk('History')) !== 'p' || w.eval("'History' in st.skillP")) return 'Antippen zurück → p';
      // Background Sage: History doppelt → Hinweis + Ersatzwahl; Attributswahl als Abzeichen
      w.bgSelect('Sage');
      if (bdg(sk('History')) !== 'Class,Background' || bdg(sk('Arcana')) !== 'Background') return 'Background-Skills: ' + bdg(sk('History'));
      const dup = [...d.querySelectorAll('#pkHints .pk-dup')].find(x => x.textContent.includes('twice'));
      if (!dup || !dup.textContent.includes('History twice (Class + Background)') || !dup.textContent.includes('2024')) return 'Doppel-Hinweis (2024) fehlt';
      if (dup.querySelector('.pk-chip')) return '2024-Background: Ersatzwahl darf nicht erscheinen (Regel nur PHB 2014)';
      const ab = v => [...d.querySelectorAll('#bgLoreBody .pk-chip')].find(c => c.dataset.v === v);
      if (!d.getElementById('bgLorePend').textContent) return 'offene Attributswahl nicht markiert';
      ab('+2/+1').click(); ab('INT:+2').click(); ab('WIS:+1').click();
      const aB = k => { const c = d.getElementById('a_' + k).closest('.acard').querySelector('.a-bdg'); return c ? c.textContent : ''; };
      if (aB('INT') !== '+2 BG' || aB('WIS') !== '+1 BG' || aB('CON') !== '' || w.eval('st.attrs.INT') !== 16) return 'Attributs-Abzeichen / Wert verändert';
      if (d.getElementById('bgLorePend').textContent) return 'Attributswahl fertig, Marker bleibt';
      ab('+1/+1/+1').click(); if (aB('CON') !== '+1 BG' || aB('INT') !== '+1 BG') return '+1/+1/+1';
      // 2014-Background (Cloistered Scholar, History fest): Ersatzwahl nach PHB 2014
      w.bgSelect('Cloistered Scholar');
      const dup14 = [...d.querySelectorAll('#pkHints .pk-dup')].find(x => x.textContent.includes('twice'));
      if (!dup14 || !dup14.textContent.includes('PHB 2014')) return 'Doppel-Hinweis (2014) fehlt';
      if (chip('#pkHints', 'Investigation') || !chip('#pkHints', 'Medicine')) return 'Ersatzwahl bietet schon geübte Skills an';
      chip('#pkHints', 'Medicine').click();
      if (bdg(sk('Medicine')) !== 'Replacement' || pip(sk('Medicine')) !== 'p') return 'Ersatz nicht wirksam';
      // Klassenwechsel und zurück: Wahl bleibt, wird nur nicht ausgewertet
      sel('Fighter', '', 1); if (bdg(sk('Investigation')) !== '' || pip(sv('Strength')) !== 'p' || pip(sv('Intelligence')) !== '') return 'Fighter: fremde Wahl ausgewertet';
      sel('Wizard', '', 1); if (bdg(sk('Investigation')) !== 'Class') return 'Wechsel zurück: Wahl verloren';
      // Speichern/Laden, Charakterwechsel ohne Übertrag
      const snap = w.eval('collectState()'); if (!snap.picks || !snap.picks['bg:Sage:ability']) return 'picks nicht gespeichert';
      w.resetUI(); if (JSON.stringify(w.eval('st.picks')) !== '{}') return 'resetUI: picks bleiben';
      w.applyState(snap); if (bdg(sk('Medicine')) !== 'Replacement') return 'Laden: Ersatz fehlt';
      w.applyState({ attrs: {}, _f_cls: 'Wizard' }); if (JSON.stringify(w.eval('st.picks')) !== '{}' || bdg(sk('Investigation')) !== '') return 'Charakterwechsel übernimmt fremde picks';
      w.resetUI();
      return true;
    } },
  { name: 'Background-Text nur aus derselben Quelle: XPHB-Sage ohne 2014-„Feature: Researcher“, PHB-Backgrounds behalten ihr Feature', datum: '28.09.2026',
    run: ({ w, d }) => {
      const body = d.getElementById('bgLoreBody');
      w.eval("st.bg='Sage'"); w.buildBgLore();
      if (body.textContent.includes('Researcher')) return 'XPHB-Sage zeigt 2014-Feature';
      w.eval("st.bg='Cloistered Scholar'"); w.buildBgLore();
      if (!body.querySelector('.bg-cap') || !body.querySelector('.bg-cap').textContent.startsWith('Feature')) return 'SCAG-Background ohne Feature';
      w.eval("st.bg=''"); w.buildBgLore();
      return true;
    } },
  { name: 'Background-Text vollständig aus 5e.tools (Languages, Equipment, Abschnitte, Tabellen) in Info- und Background-Tab; Strixhaven-/Ravnica-Zauber auf „★ My Class“ nur mit Zauberliste', datum: '01.10.2026',
    run: ({ w, d, sel }) => {
      const body = d.getElementById('bgLoreBody');
      w.eval("st.bg='Quandrix Student'"); w.buildBgLore();
      const t = body.textContent, caps = [...body.querySelectorAll('.bg-cap')].map(x => x.textContent);
      for (const x of ['Languages:', 'Equipment:', 'Vortex Warp', 'Personality Trait', 'Quandrix Trinkets']) if (!t.includes(x)) return 'Info-Tab ohne ' + x;
      if (!caps.includes('Building a Quandrix Character')) return 'Abschnitt „Building a Quandrix Character“ fehlt';
      const tb = [...body.querySelectorAll('table.fd-tbl')].find(x => x.textContent.includes('Entangle'));
      if (!tb || !tb.querySelector('th') || tb.querySelector('th').textContent !== 'Spell Level' || tb.querySelectorAll('tr').length !== 6) return 'Tabelle Quandrix Spells falsch';
      w.eval("st.bg='Sage'"); w.buildBgLore();
      if (!body.textContent.includes('Equipment: Choose A or B') || body.textContent.includes('Researcher')) return 'XPHB-Sage: Equipment fehlt oder 2014-Feature';
      w.eval("st.bg='Folk Hero'"); w.buildBgLore();
      if (!body.textContent.includes('Defining Event') || !body.textContent.includes('Rustic Hospitality')) return 'Folk Hero: Specialty-Tabelle oder Feature fehlt';
      // Background-Tab: Karte zeigt den Text
      w.eval("st.bg='Quandrix Student'"); w.bgRenderMy();
      const my = d.querySelector('#bgMyCard .bg-full');
      if (!my || !my.textContent.includes('Vortex Warp')) return 'Background-Tab: Text fehlt in „My Background“';
      // Zauber: Druid mit Quandrix Student → Vortex Warp über „Quandrix Student“, Barbarian ohne Liste → nicht
      sel('Druid', '', 3);
      const zb = n => w.eval(`ZB_SPELLS.find(s=>s.name===${JSON.stringify(n)})`);
      if (w.slMyVia(w.slMySpellCtx(), zb('Vortex Warp')) !== 'Quandrix Student') return 'Vortex Warp nicht auf der Druid-Liste';
      if (w.slMyVia(w.slMySpellCtx(), zb('Entangle')) !== '') return 'Entangle (Druid-Liste) falsch markiert';
      w.eval("st.bg=''");
      if (w.slMyVia(w.slMySpellCtx(), zb('Vortex Warp')) !== null) return 'ohne Background trotzdem auf der Liste';
      w.eval("st.bg='Quandrix Student'"); sel('Barbarian', '', 3);
      if (w.slMyVia(w.slMySpellCtx(), zb('Vortex Warp')) !== null) return 'Barbarian (ohne Zauberliste) bekommt Background-Zauber';
      // My Spells: Herkunfts-Abzeichen nur für Zauber über Zusatzquelle
      sel('Druid', '', 3);
      w.eval("st.mySpells=[{name:'Vortex Warp',grad:2,school:'Conjuration',prep:true},{name:'Entangle',grad:1,school:'Conjuration',prep:true}]"); w.buildMySpells();
      const via = n => { const c = [...d.querySelectorAll('#mySpells .spell-card')].find(x => x.querySelector('.spell-name').textContent === n); return c ? (c.querySelector('.sp-via') || {}).textContent || '' : 'fehlt'; };
      if (via('Vortex Warp') !== '✦ Quandrix Student') return 'My Spells: Vortex Warp ohne Abzeichen „Quandrix Student“ (' + via('Vortex Warp') + ')';
      if (via('Entangle') !== '') return 'My Spells: Entangle (Druid-Liste) mit Abzeichen';
      w.eval("st.bg=''"); w.buildMySpells();
      if (via('Vortex Warp') !== '') return 'My Spells: Abzeichen bleibt ohne Background';
      w.eval("st.mySpells=[]"); w.buildBgLore(); w.resetUI();
      return true;
    } },
  { name: 'Backgrounds und Feats aus AU/RHW/EFA ergänzt: 12 neue Backgrounds, 4 durch Nachdruck ersetzt (Name gleich), 40 Feats inkl. Dark Gift, Origin Feat findbar', datum: '01.10.2026',
    run: ({ w, d }) => {
      const bg = n => w.eval(`BG_DATA.find(b=>b.n===${JSON.stringify(n)})`), ft = n => w.eval(`FT_FEATS.find(f=>f.n===${JSON.stringify(n)})`);
      if (w.eval('BG_DATA.length') !== 132 || w.eval('new Set(BG_DATA.map(b=>b.n)).size') !== 132) return 'BG_DATA nicht 132 eindeutige Namen';
      const ft1 = bg('Familiar Trainer'); if (!ft1 || ft1.f !== 'Familiar Friend' || ft1.a !== 'CON, INT, WIS' || ft1.src !== 'AU') return 'Familiar Trainer falsch';
      for (const [n, q] of [['Haunted One', 'RHW'], ['Investigator', 'RHW'], ['Archaeologist', 'EFA'], ['House Agent', 'EFA']]) if (!bg(n) || bg(n).src !== q) return n + ' nicht ' + q;
      for (const b of w.eval('BG_DATA')) { if (b.f && !w.eval(`FT_FEATS.some(f=>f.n.toLowerCase()===${JSON.stringify(b.f.toLowerCase())})`)) return 'Origin Feat fehlt in FT_FEATS: ' + b.n + ' → ' + b.f; if (!w.eval(`!!BG_EXTRA_MAP[${JSON.stringify(b.n + '|' + b.src)}]`)) return 'BG_EXTRA fehlt: ' + b.n; }
      if (!ft('Survivor') || ft('Survivor').cat !== 'O' || !ft('Mist Walker') || ft('Mist Walker').cat !== 'DG') return 'RHW-Feats fehlen';
      if (ft('Abjuration Adept').pre !== 'Level 4, Spellcasting or Pact Magic Feature' || !ft('Abjuration Adept').d.includes('Spell Slot Level | Spell')) return 'Abjuration Adept: Voraussetzung/Tabelle';
      if (w.eval("FT_CATS.DG") !== 'Dark Gift' || !w.eval("typeof FEAT_SPELLS!=='undefined'&&!!FEAT_SPELLS['Abjuration Adept']")) return 'Dark Gift-Kategorie oder FEAT_SPELLS fehlt';
      const body = d.getElementById('bgLoreBody');
      w.eval("st.bg='Mist Wanderer'"); w.buildBgLore();
      if (!body.textContent.includes('Dark Gift feat of your choice')) return 'Mist Wanderer: Feat-Zeile (Dark Gift) fehlt';
      w.eval("st.bg='Familiar Trainer'"); w.buildBgLore();
      if (!body.textContent.includes('Equipment:')) return 'Familiar Trainer ohne Text';
      w.eval("st.bg=''"); w.buildBgLore();
      return true;
    } },
  { name: 'Paket C2: Feature-Auswahl (Primal Order · Magician mit +WIS auf Arcana/Nature, Storm Aura → Storm Soul, wechselbar mit ↻), Expertise nur auf geübte Skills (Rogue L1/L6), Jack of All Trades (½), Bonus-Skills und Saves aus Features, nur ab Feature-Stufe und bei passender Subklasse', datum: '29.09.2026',
    run: ({ w, d, sel, set }) => {
      if (typeof w.fpHtml !== 'function' || !w.eval('typeof FEATURE_PICKS==="object"&&Object.keys(FEATURE_PICKS).length>40')) return 'FEATURE_PICKS/fpHtml fehlen';
      // Daten: jeder Schlüssel trifft genau ein Feature, jede Option (außer nt) hat Text im desc
      const bad = w.eval(`Object.entries(FEATURE_PICKS).map(([k,e])=>{const [c,g,n0]=k.split('|'),[n,at]=n0.split('@');const cd=CLASS_DATA[c];const fs=cd&&(g==='base'?cd.base:(cd.subclass||{})[g]);if(!fs)return k+': Gruppe';const h=fs.filter(f=>f.name===n&&(!at||f.lvl===+at));if(h.length!==1)return k+': '+h.length+'x';if(h[0].lvl!==e.l)return k+': Stufe';if(e.t==='opt'&&!e.nt){const o=e.o.find(o=>!fpOptText(h[0].desc,o));if(o)return k+': ohne Text '+o;}return '';}).filter(x=>x)`);
      if (bad.length) return 'Daten: ' + bad.join('; ');
      const sk = n => [...d.querySelectorAll('#skillsGrid .sk-row')].find(r => r.querySelector('.sk-name').firstChild.textContent === n);
      const sv = l => [...d.querySelectorAll('#savesGrid .sk-row')].find(r => r.querySelector('.sk-name').firstChild.textContent === l);
      const pip = r => r.querySelector('.sk-pip').className.replace('sk-pip', '').trim();
      const bdg = r => [...r.querySelectorAll('.sk-bdg')].map(b => b.textContent).join(',');
      const bon = r => r.querySelector('.sk-bon').textContent;
      const card = n => [...d.querySelectorAll('#abList .ab-card')].find(c => c.querySelector('.ab-name').firstChild.textContent === n);
      const chip = (root, o) => root && [...root.querySelectorAll('.pk-chip')].find(c => c.dataset.o === o);
      w.resetUI();
      w.applyState({ attrs: { STR: 10, DEX: 14, CON: 10, INT: 10, WIS: 16, CHA: 8 }, _f_prof: '2' });
      // Druid L1: Primal Order – Chips in der Actions-Karte, Wahl im Titel, Text der Wahl, andere Optionen aufklappbar
      sel('Druid', '', 1);
      const po = card('Primal Order'); if (!po) return 'Karte Primal Order fehlt';
      if (!po.textContent.includes('Choose 1 (0/1)')) return 'offene Wahl nicht gezeigt';
      chip(po, 'Magician').click();
      if (JSON.stringify(w.eval("st.picks['feat:Druid|base|Primal Order']")) !== '["Magician"]') return 'Wahl nicht gespeichert';
      const po2 = card('Primal Order');
      if (po2.querySelector('.ab-name').textContent.trim() !== 'Primal Order · Magician') return 'Titel: ' + po2.querySelector('.ab-name').textContent;
      if (!po2.querySelector('.fp-sel') || !po2.querySelector('.fp-sel').textContent.startsWith('Magician:') || po2.querySelector('.fp-sel').textContent.includes('Warden')) return 'Text der Wahl';
      const more = po2.querySelector('details.fp-more'); if (!more || !more.textContent.includes('Warden')) return '„Other options“ fehlt';
      if (!d.getElementById('clsLoreBody').textContent.includes('Primal Order · Magician')) return 'Info-Tab zeigt Wahl nicht';
      if (bdg(sk('Arcana')) !== 'Magician +3' || bon(sk('Arcana')) !== '+3' || bdg(sk('Nature')) !== 'Magician +3' || bdg(sk('History')) !== '') return 'Magician-Bonus: ' + bdg(sk('Arcana')) + ' ' + bon(sk('Arcana'));
      w.eval('st.attrs.WIS=8'); w.buildSkills(); if (bdg(sk('Arcana')) !== 'Magician +1') return 'Magician min. +1';
      w.eval('st.attrs.WIS=16');
      chip(card('Primal Order'), 'Warden').click(); w.buildSkills();
      if (bdg(sk('Arcana')) !== '' || card('Primal Order').querySelector('.ab-name').textContent.trim() !== 'Primal Order · Warden') return 'Wechsel auf Warden';
      // Stufe: Elemental Fury (L7) wirkt erst ab L7, Expertise/Saves ebenso
      // Barbarian Storm Herald: Storm Aura wählen → Storm Soul (verknüpft) zeigt die Wahl; ↻ im Kopf
      sel('Barbarian', 'Path of the Storm Herald (XGE)', 6);
      const sa = card('Storm Aura'); if (!sa || !sa.textContent.includes('↻ Level up')) return 'Storm Aura ohne ↻';
      chip(sa, 'Sea').click();
      const ss = card('Storm Soul'); if (!ss || ss.querySelector('.ab-name').textContent.trim() !== 'Storm Soul · Sea' || !ss.querySelector('.fp-sel').textContent.includes('lightning')) return 'Storm Soul verknüpft: ' + (ss && ss.querySelector('.ab-name').textContent);
      sel('Barbarian', 'Path of the Berserker (PHB)', 6); if (card('Storm Soul')) return 'fremde Subklasse';
      // Rogue: Expertise nur aus geübten Skills; L6-Expertise erst ab L6; Slippery Mind ab L15
      sel('Rogue', '', 5);
      const ex = card('Expertise'); if (!ex) return 'Karte Expertise fehlt';
      if (!ex.textContent.includes('No eligible skill proficiency')) return 'Expertise ohne geübte Skills';
      const ct = d.getElementById('coreTraitsList');
      ['Stealth', 'Perception', 'Acrobatics', 'Insight'].forEach(o => chip(ct, o).click());
      const ex2 = card('Expertise'); if (chip(ex2, 'Arcana') || !chip(ex2, 'Stealth')) return 'Expertise-Optionen';
      chip(ex2, 'Stealth').click(); chip(card('Expertise'), 'Perception').click();
      if (pip(sk('Stealth')) !== 'e' || bdg(sk('Stealth')) !== 'Class,Expertise' || bon(sk('Stealth')) !== '+6') return 'Expertise nicht wirksam: ' + pip(sk('Stealth')) + ' ' + bdg(sk('Stealth')) + ' ' + bon(sk('Stealth'));
      if (card('Expertise').textContent.includes('Level 6')) return 'L6-Expertise vor Stufe 6';
      sel('Rogue', '', 6); if (!card('Expertise').textContent.includes('Level 6')) return 'L6-Expertise fehlt';
      if (pip(sv('Wisdom')) !== '') return 'Slippery Mind vor L15';
      sel('Rogue', '', 15); if (pip(sv('Wisdom')) !== 'p' || bdg(sv('Wisdom')) !== 'Slippery Mind') return 'Slippery Mind';
      // Scout: Survivalist fest Nature + Survival mit Expertise
      sel('Rogue', 'Scout (XGE)', 3); if (pip(sk('Survival')) !== 'e' || bdg(sk('Survival')) !== 'Survivalist') return 'Survivalist';
      // Bard L2: Jack of All Trades = halber Übungsbonus auf nicht geübte Skills, ohne Abzeichen
      set('prof', '2'); sel('Bard', '', 2);
      if (pip(sk('History')) !== 'h' || bon(sk('History')) !== '+1' || bdg(sk('History')) !== '') return 'Jack of All Trades: ' + pip(sk('History')) + ' ' + bon(sk('History'));
      sel('Bard', '', 1); if (pip(sk('History')) !== '') return 'Jack of All Trades vor L2';
      // Speichern/Laden, Charakterwechsel
      const snap = w.eval('collectState()'); if (!snap.picks['feat:Rogue|base|Expertise@1']) return 'feat-picks nicht gespeichert';
      w.applyState({ attrs: {}, _f_cls: 'Rogue', _f_lvl: '6' }); if (bdg(sk('Stealth')).includes('Expertise')) return 'Charakterwechsel übernimmt feat-picks';
      w.resetUI();
      return true;
    } },
  { name: 'Paket C3: Rassen – Wahl (Elven Lineage mit Tabelle, Keen Senses, Draconic Ancestry, Size, Half-Elf-Boni) in st.picks, Werte-Zeile (Speed/Size/Darkvision/Resistenz), Rassen-Skills mit Abzeichen, Vorteile an Saves, Dwarven Toughness, RACE_DATA-Fehler behoben', datum: '29.09.2026',
    run: ({ w, d, set }) => {
      if (!w.eval('typeof RACE_PICKS==="object"&&Object.keys(RACE_PICKS).length===12') || typeof w.rcCard !== 'function') return 'RACE_PICKS/rcCard fehlen';
      const sk = n => [...d.querySelectorAll('#skillsGrid .sk-row')].find(r => r.querySelector('.sk-name').firstChild.textContent === n);
      const sv = l => [...d.querySelectorAll('#savesGrid .sk-row')].find(r => r.querySelector('.sk-name').firstChild.textContent === l);
      const pip = r => r.querySelector('.sk-pip').className.replace('sk-pip', '').trim();
      const bdg = r => [...r.querySelectorAll('.sk-bdg')].map(b => b.textContent).join(',');
      const body = d.getElementById('raceLoreBody'), stats = () => d.getElementById('raceStats').textContent;
      const rcard = n => [...body.children].find(c => { const h = c.querySelector('div[style*="Cinzel"]'); return h && h.textContent.split(' · ')[0] === n; });
      const chip = (root, o) => root && [...root.querySelectorAll('.pk-chip')].find(c => c.dataset.o === o);
      const race = r => { set('race', r); w.onRaceChange(); };
      w.resetUI();
      w.applyState({ attrs: { STR: 10, DEX: 10, CON: 10, INT: 10, WIS: 14, CHA: 10 }, _f_prof: '2', _f_lvl: '3' });
      // Elf: offene Wahl, Tabelle „Elven Lineages“ (fehlte im Trait-Text), Drow → Darkvision 120, Zauber nach Stufe
      race('Elf');
      if (d.getElementById('raceLorePend').textContent !== '● Choose') return 'offene Rassen-Wahl nicht markiert';
      const el = rcard('Elven Lineage'); if (!el || !el.querySelector('.fd-tbl') || !el.textContent.includes('Elven Lineages')) return 'Tabelle Elven Lineages fehlt';
      if (!stats().includes('Darkvision 60 ft') || !stats().includes('Elven Lineage: choose')) return 'Werte-Zeile Elf: ' + stats();
      chip(rcard('Elven Lineage'), 'Drow').click();
      if (JSON.stringify(w.eval("st.picks['race:Elven Lineage']")) !== '["Drow"]') return 'Lineage nicht gespeichert';
      const dr = rcard('Elven Lineage');
      if (dr.querySelector('div[style*="Cinzel"]').textContent !== 'Elven Lineage · Drow') return 'Titel: ' + dr.querySelector('div[style*="Cinzel"]').textContent;
      if (!stats().includes('Darkvision 120 ft')) return 'Drow Darkvision: ' + stats();
      const sp = [...dr.querySelectorAll('.rc-sp')].map(x => x.className + ':' + x.textContent);
      if (sp.join('|') !== 'rc-sp:Level 1Dancing Lights|rc-sp:Level 3Faerie Fire|rc-sp off:Level 5Darkness') return 'Zauber nach Stufe: ' + sp.join('|');
      chip(rcard('Elven Lineage'), 'WIS').click();
      if (!rcard('Elven Lineage').querySelector('.rc-dc') || rcard('Elven Lineage').querySelector('.rc-dc').textContent !== 'Spell save DC 12 · Spell attack +4 (WIS)') return 'DC-Zeile';
      // Keen Senses → Perception geübt mit Abzeichen „Elf“; Wood Elf → Speed 35, Feld 30 = Hinweis
      chip(rcard('Keen Senses'), 'Perception').click();
      if (pip(sk('Perception')) !== 'p' || bdg(sk('Perception')) !== 'Elf') return 'Keen Senses: ' + pip(sk('Perception')) + ' ' + bdg(sk('Perception'));
      if (d.getElementById('raceLorePend').textContent !== '') return 'Marker bleibt nach vollständiger Wahl';
      chip(rcard('Elven Lineage'), 'Wood Elf').click();
      if (!stats().includes('Speed 35 ft') || !d.querySelector('#raceStats .rc-chip.warn') || stats().includes('Darkvision 120')) return 'Wood Elf: ' + stats();
      // Rassenwechsel: fremde Wahl wirkt nicht, bleibt aber gespeichert
      race('Dwarf');
      if (pip(sk('Perception')) !== '' || !w.eval("st.picks['race:Keen Senses']")) return 'Rassenwechsel: Keen Senses';
      if (!d.getElementById('saveAdv').textContent.includes('Poisoned') || !stats().includes('Resistance: Poison')) return 'Dwarf: Vorteil/Resistenz';
      if (d.getElementById('hpMHint').textContent !== 'Dwarven Toughness +3') return 'Dwarven Toughness: ' + d.getElementById('hpMHint').textContent;
      race('Gnome'); if (bdg(sv('Intelligence')) !== 'Adv' || bdg(sv('Strength')) !== '') return 'Gnomish Cunning an Saves';
      // Dragonborn: Farbe → Resistenz und Breath Weapon mit Schadensart
      race('Dragonborn'); chip(rcard('Draconic Ancestry'), 'Red').click();
      if (!stats().includes('Resistance: Fire') || rcard('Breath Weapon').querySelector('div[style*="Cinzel"]').textContent !== 'Breath Weapon · Fire') return 'Dragonborn: ' + stats();
      // Human: Size-Wahl (war fälschlich „S“), Skillful
      race('Human'); if (!stats().includes('Size: Small or Medium')) return 'Human Size offen: ' + stats();
      chip(rcard('Size'), 'Medium').click(); if (!stats().includes('Medium')) return 'Human Size';
      // Half-Orc (PHB): Intimidation fest, +2 STR/+1 CON nur als Abzeichen; Half-Elf: +2 CHA fest, +1/+1 Wahl
      race('Half-Orc');
      if (pip(sk('Intimidation')) !== 'p' || bdg(sk('Intimidation')) !== 'Half-Orc') return 'Menacing';
      const ab = k => [...d.querySelectorAll('#attrGrid .acard')].find(c => c.querySelector('input').id === 'a_' + k);
      if (ab('STR').querySelector('.a-bdg').textContent !== '+2 Race' || ab('CON').querySelector('.a-bdg').textContent !== '+1 Race' || w.eval('st.attrs.STR') !== 10) return 'Half-Orc-Boni';
      race('Half-Elf'); if (!body.textContent.includes('+2 CHA (fixed), +1 to 2 others')) return 'Half-Elf ASI-Karte';
      chip(rcard('Ability Score Increase'), 'DEX').click(); chip(rcard('Ability Score Increase'), 'WIS').click();
      if (ab('DEX').querySelector('.a-bdg').textContent !== '+1 Race' || ab('CHA').querySelector('.a-bdg').textContent !== '+2 Race') return 'Half-Elf-Boni';
      if (w.eval('RACE_DATA["Half-Elf"].ability') !== '+2 cha, +1 to two others' || w.eval('RACE_DATA.Tiefling.size') !== 'S/M') return 'RACE_DATA-Fehler';
      // Speichern/Laden, alter Save ohne Rassen-picks, Charakterwechsel
      const snap = w.eval('collectState()'); if (!snap.picks['race:Elven Lineage'] || !snap.picks['race:Ability Score Increase']) return 'race-picks nicht gespeichert';
      w.applyState({ attrs: {}, _f_race: 'Elf' }); if (pip(sk('Perception')) !== '' || !stats().includes('Elven Lineage: choose')) return 'Charakterwechsel übernimmt race-picks';
      w.resetUI();
      return true;
    } },
  { name: 'Paket C4: Rassen im Actions-Tab – Tracker (rc_-ids, PB/1×, ab Stufe, Aktionsart je Giant-Ancestry-Boon), Lineage-Zauber 1×/Long Rest ab L3/L5, Passiv/Weitere-Karten, Werte aus dem Text (DC, Schaden), Spell-List ★ mit Rassen-Zaubern, Verbrauch gespeichert; Aasimar-Optionsnamen (Heavenly Wings …)', datum: '29.09.2026',
    run: ({ w, d, set, sel }) => {
      if (typeof w.rcTrackers !== 'function' || !w.eval('RACE_PICKS.Orc.tr&&RACE_PICKS.Elf.ch[0].o[0].inn')) return 'Rassen-Tracker fehlen (rcTrackers/RACE_PICKS.tr)';
      const race = r => { set('race', r); w.onRaceChange(); };
      const card = n => [...d.querySelectorAll('#abList .ab-card')].find(c => c.querySelector('.ab-name').firstChild.textContent === n);
      const grp = c => c && c.closest('.ab-grp-box').dataset.grp;
      const pips = c => c ? c.querySelectorAll('.ab-top .ab-pip').length : -1;
      const chip = (root, o) => root && [...root.querySelectorAll('.pk-chip')].find(c => c.dataset.o === o);
      w.resetUI();
      w.applyState({ attrs: { STR: 10, DEX: 10, CON: 14, INT: 10, WIS: 10, CHA: 10 }, _f_prof: '3', _f_lvl: '5' });
      sel('Barbarian', '', 5);
      if (d.querySelector('#abList [id^="ab_rc_"],#abList [id^="ab_f_r_"]')) return 'Rassen-Karten ohne Rasse';
      // Orc L5: Adrenaline Rush PB=3 (Bonusaktion, Short Rest), Relentless Endurance 1× (Passiv), Darkvision unter Passiv
      race('Orc');
      const ar = card('Adrenaline Rush');
      if (!ar || grp(ar) !== 'bonus' || pips(ar) !== 3 || !ar.textContent.includes('Short/Long Rest') || !ar.querySelector('.ab-tag').textContent.includes('Orc')) return 'Adrenaline Rush: ' + (ar ? grp(ar) + ' ' + pips(ar) : 'fehlt');
      if (!ar.querySelector('.rc-dc') || ar.querySelector('.rc-dc').textContent !== 'Temp HP 3') return 'Adrenaline Rush Temp HP';
      if (pips(card('Relentless Endurance')) !== 1 || grp(card('Relentless Endurance')) !== 'passiv' || grp(card('Darkvision')) !== 'passiv') return 'Orc Relentless/Darkvision';
      // Pip-Klick speichert Verbrauch unter der rc_-id, Reset setzt zurück
      ar.querySelector('.ab-pip.avail').click();
      if (w.eval('st.abUses.rc_adrenalinerush') !== 1 || card('Adrenaline Rush').querySelectorAll('.ab-pip.avail').length !== 2) return 'Pip-Klick nicht gespeichert';
      // Dragonborn: Breath Weapon Aktion mit DC (8+CON+PB; PB = Feld „Prof.“ wie C3, Pips nach Stufe) und Schaden L5 = 2d10, Schadensart nach Wahl; Draconic Flight ab L5; Wahl-Trait unter Weitere
      race('Dragonborn'); chip(d.getElementById('raceLoreBody'), 'Red') ? chip(d.getElementById('raceLoreBody'), 'Red').click() : null;
      const bw = card('Breath Weapon');
      if (!bw || grp(bw) !== 'aktion' || pips(bw) !== 3 || bw.querySelector('.fp-suf').textContent !== ' · Fire') return 'Breath Weapon: ' + (bw ? grp(bw) + ' ' + pips(bw) + bw.querySelector('.fp-suf').textContent : 'fehlt');
      if (bw.querySelector('.rc-dc').textContent !== 'Save DC 13 (CON) · Damage 2d10') return 'Breath Weapon Werte: ' + bw.querySelector('.rc-dc').textContent;
      if (!card('Draconic Flight') || grp(card('Draconic Flight')) !== 'bonus' || grp(card('Draconic Ancestry')) !== 'weitere') return 'Draconic Flight / Ancestry';
      set('lvl', '4'); w.buildAbilities();
      if (card('Draconic Flight') || card('Breath Weapon').querySelector('.rc-dc').textContent !== 'Save DC 13 (CON) · Damage 1d10' || pips(card('Breath Weapon')) !== 2) return 'Stufe 4: Draconic Flight/Schaden';
      // Goliath: Aktionsart je Boon
      set('lvl', '5'); race('Goliath');
      const ga = () => card('Giant Ancestry');
      if (!ga() || grp(ga()) !== 'passiv' || pips(ga()) !== 3 || !card('Large Form')) return 'Giant Ancestry/Large Form';
      chip(ga(), "Stone's Endurance").click();
      if (grp(ga()) !== 'reaktion' || ga().querySelector('.fp-suf').textContent !== " · Stone's Endurance") return 'Stone\'s Endurance nicht als Reaktion';
      // Elf: Lineage-Zauber erst ab L3/L5, je 1×/Long Rest; Keen Senses unter Weitere
      race('Elf');
      const ln = () => card('Elven Lineage');
      if (!ln() || ln().querySelectorAll('.ab-sub').length || grp(card('Keen Senses')) !== 'weitere' || grp(card('Trance')) !== 'passiv') return 'Elf vor der Wahl';
      chip(ln(), 'Drow').click();
      const subs = () => [...ln().querySelectorAll('.ab-sub')].map(x => x.querySelector('.ab-sublbl').textContent + ':' + x.querySelectorAll('.ab-pip').length);
      if (subs().join('|') !== 'Faerie Fire:1|Darkness:1' || ln().querySelector('.fp-suf').textContent !== ' · Drow') return 'Drow L5: ' + subs().join('|');
      set('lvl', '3'); w.buildAbilities(); if (subs().join('|') !== 'Faerie Fire:1') return 'Drow L3: ' + subs().join('|');
      set('lvl', '2'); w.buildAbilities(); if (subs().length) return 'Drow L2: ' + subs().join('|');
      // Spell List ★: Barbarian-Elf (keine Klassenzauber) sieht Drow-Zauber bis zur Stufe mit Herkunft
      set('lvl', '3'); w.slRender && w.slRender();
      const ctx = w.slMySpellCtx();
      if (!ctx.avail || w.slMyVia(ctx, { name: 'Faerie Fire', classes: [] }) !== 'Elf: Drow' || w.slMyVia(ctx, { name: 'Darkness', classes: [] }) !== null) return 'Spell-List ★ Rassen-Zauber';
      // Gnome Forest: Speak with Animals PB/Long Rest; Tiefling/Aasimar: feste Cantrips im ★-Filter
      race('Gnome'); chip(card('Gnomish Lineage'), 'Forest Gnome').click();
      if ([...card('Gnomish Lineage').querySelectorAll('.ab-sub .ab-pip')].length !== 2) return 'Forest Gnome Speak with Animals (PB 2 bei L3)';
      race('Aasimar'); if (w.slMyVia(w.slMySpellCtx(), { name: 'Light', classes: [] }) !== 'Aasimar: Light Bearer') return 'Light Bearer im ★-Filter';
      if (card('Healing Hands').querySelector('.rc-dc').textContent !== 'Roll 3d4' || !card('Celestial Revelation')) return 'Aasimar-Tracker';
      // Nebenfund C4: Optionsnamen der Verwandlungen (fehlten im RACE_DATA-Text), bleiben in derselben Karte
      const crn = [...card('Celestial Revelation').querySelectorAll('.fd-n')].map(x => x.textContent).join('|');
      if (crn !== 'Heavenly Wings.|Inner Radiance.|Necrotic Shroud.') return 'Celestial Revelation Optionsnamen: ' + crn;
      // Speichern/Laden
      const snap = w.eval('collectState()'); if (snap.abUses.rc_adrenalinerush !== 1) return 'rc-Verbrauch nicht im Save';
      w.resetUI();
      return true;
    } },
  { name: 'Paket D: Zauberplätze aus der Class Table (Stufe, Subklasse EK/AT), −/+ als Korrektur, Grade mit 0 fehlen, Warlock Pakt-Kachel, alte Saves', datum: '29.09.2026',
    run: ({ w, d, set, sel }) => {
      w.resetUI(); w.eval("document.getElementById('charName').textContent='Regressionstest D'");
      w.applyState({ slotMax: [4, 3, 3, 3, 2, 1, 1, 1, 1], slotUsed: [0, 0, 3, 0, 0, 0, 0, 0, 0], _f_lvl: '5' }); // alter Save: slotMax von Hand, kein slotAdj
      sel('Wizard', '', 5);
      const tiles = () => [...d.querySelectorAll('#spSlots .slvl')].map(t => t.querySelector('.slvl-lbl').textContent + ':' + t.querySelectorAll('.slpip').length + '/' + t.querySelectorAll('.slpip.av').length).join('|');
      if (tiles() !== '1st Level:4/4|2nd Level:3/3|3rd Level:2/0') return 'Wizard L5: ' + tiles();
      if (w.eval('st.slotUsed[2]') !== 3 || w.eval('st.slotMax.join()') !== '4,3,2,0,0,0,0,0,0') return 'Verbrauch gekürzt statt nur begrenzt angezeigt';
      d.querySelectorAll('#spSlots .slvl')[2].querySelectorAll('.slpip')[1].click();
      if (w.eval('st.slotUsed[2]') !== 1) return 'Tipp auf leeren Kreis (Verbrauch über Maximum): ' + w.eval('st.slotUsed[2]');
      if (d.querySelectorAll('#spSlots .slbtn').length) return '−/+ sichtbar ohne ✎ Adjust';
      w.togSlotEdit(); d.querySelectorAll('#spSlots .slvl')[0].querySelectorAll('.slbtn')[1].click(); w.togSlotEdit();
      if (w.eval('st.slotAdj[0]') !== 1 || tiles().split('|')[0] !== '1st Level:5/5' || !d.querySelector('#spSlots .sl-adj .sl-hint').textContent.includes('Table 4 · +1')) return 'Korrektur +1: ' + tiles();
      set('lvl', '9'); w.buildAbilities();
      if (w.eval('st.slotMax.join()') !== '5,3,3,3,1,0,0,0,0') return 'Stufe 9 mit Korrektur: ' + w.eval('st.slotMax.join()');
      w.eval('st.slotAdj=[0,0,0,0,0,0,0,0,0]'); sel('Barbarian', '', 5);
      if (d.querySelectorAll('#spSlots .slvl').length || !d.querySelector('#spSlots .sl-none')) return 'Barbarian: Plätze statt Hinweis';
      sel('Warlock', '', 5);
      const pk = d.querySelector('#spSlots .sl-pact');
      if (!pk || pk.querySelector('.slvl-lbl').textContent !== 'Pact · 3rd' || pk.querySelectorAll('.slpip').length !== 2 || d.querySelectorAll('#spSlots .slvl').length !== 1) return 'Warlock-Pakt-Kachel';
      pk.querySelector('.slpip').click();
      if (w.eval('st.abUses.wl_pactslots') !== 1) return 'Pakt-Kreis verbraucht nicht wl_pactslots';
      // Eldritch Knight / Arcane Trickster: Plätze aus SUBCLASS_TABLES (5e.tools XPHB), auch Class Table und Combat Stats
      sel('Fighter', 'Eldritch Knight (PHB)', 7);
      if (w.eval('st.slotMax.join()') !== '4,2,0,0,0,0,0,0,0') return 'Eldritch Knight L7: ' + w.eval('st.slotMax.join()');
      if (!/Spell Slots/.test(d.getElementById('combatStats').textContent)) return 'Combat Stats ohne EK-Plätze';
      w.buildClassTable();
      if (d.getElementById('clsTableTitle').textContent !== 'Fighter Table · Eldritch Knight' || !d.getElementById('clsTableBody').textContent.includes('SpellsPrepared') || d.querySelectorAll('#clsTableBody tr:nth-child(2) th').length !== 3 + 3 + 4 || !d.getElementById('clsTableBody').textContent.includes('Spell Slots per Spell Level')) return 'Class Table ohne EK-Spalten';
      sel('Rogue', 'Arcane Trickster (PHB)', 13);
      if (w.eval('st.slotMax.join()') !== '4,3,2,0,0,0,0,0,0') return 'Arcane Trickster L13: ' + w.eval('st.slotMax.join()');
      sel('Rogue', 'Thief (PHB)', 13);
      if (w.eval('st.slotMax.join()') !== '0,0,0,0,0,0,0,0,0') return 'Thief mit Plätzen';
      const snap = w.eval('collectState()'); if (!Array.isArray(snap.slotAdj) || snap.hdUsed !== 0) return 'slotAdj/hdUsed nicht im Save';
      w.resetUI(); return true;
    } },
  { name: 'Paket D: Short Rest (restore short voll, „regain one“ +1, Font of Inspiration erst L5), Long Rest (HP, Temp, Hit Dice, Plätze, Tracker, Free Casts, Death Saves), Hit Dice würfeln/eintippen, Log', datum: '29.09.2026',
    run: ({ w, d, set, sel }) => {
      w.resetUI(); w.eval("document.getElementById('charName').textContent='Regressionstest D'");
      w.applyState({ attrs: { STR: 10, DEX: 10, CON: 14, INT: 10, WIS: 16, CHA: 16 }, _f_lvl: '6', _f_hpM: '40', hpC: 12 });
      sel('Cleric', '', 6); w.autoSave();
      if (d.getElementById('hdBox').style.display === 'none' || d.getElementById('hdLbl').textContent !== 'Hit Dice · d8' || d.querySelectorAll('#hdPips .hdpip.av').length !== 6) return 'Hit-Dice-Anzeige';
      const cdMax = w.eval("abMaxUses(CLASS_DATA.Cleric.abilities.base.find(a=>a.id==='channeldivinity').uses,6)");
      w.eval(`st.abUses={channeldivinity:${cdMax}};st.slotUsed=[2,1,0,0,0,0,0,0,0]`);
      w.openRest('short');
      const box = d.getElementById('restBox');
      if (!d.getElementById('restModal').classList.contains('on') || !box.textContent.includes('Channel Divinity+1')) return 'Short-Rest-Dialog: ' + box.textContent.slice(0, 200);
      w.hdSpend('9'); if (w.eval('st.hdUsed') !== 0) return 'Wurf über Würfelgröße angenommen';
      w.hdSpend('5'); if (w.eval('st.hpC') !== 19 || w.eval('st.hdUsed') !== 1) return 'Eigener Wurf 5 + CON 2: HP ' + w.eval('st.hpC');
      w.eval('st.attrs.CON=4'); w.hdSpend('1'); if (w.eval('st.hpC') !== 20) return 'Mindestens 1 HP je Würfel'; w.eval('st.attrs.CON=14');
      const hp0 = w.eval('st.hpC'); w.hdSpend(null); const g = w.eval('st.hpC') - hp0;
      if (g < 3 || g > 10 || w.eval('st.hdUsed') !== 3) return 'App-Wurf: +' + g;
      w.doShortRest();
      if (w.eval('st.abUses.channeldivinity') !== cdMax - 1) return 'Channel Divinity nicht +1';
      if (w.eval('st.slotUsed.join()') !== '2,1,0,0,0,0,0,0,0') return 'Short Rest füllt Zauberplätze';
      if (w.eval('st.hdUsed') !== 3 || d.getElementById('restModal').classList.contains('on')) return 'Hit Dice nach Short Rest / Dialog offen';
      const log = w.eval('st.log').map(e => e.m);
      if (!log.some(m => /^Short Rest: Channel Divinity \+1/.test(m)) || !log.some(m => /^Hit Die spent: d8 5 \+ 2 CON → \+7 HP/.test(m))) return 'Log: ' + log.slice(-4).join(' / ');
      // Bard: Font of Inspiration erst ab L5
      sel('Bard', '', 4); w.eval('st.abUses={bardicinspiration:2}'); w.doShortRest();
      if (w.eval('st.abUses.bardicinspiration') !== 2) return 'Bard L4: Short Rest füllt Bardic Inspiration';
      set('lvl', '5'); w.buildAbilities(); w.doShortRest();
      if (w.eval('st.abUses.bardicinspiration')) return 'Bard L5: Font of Inspiration greift nicht';
      if (!d.querySelector('#abList').textContent.includes('Short/Long Rest')) return 'Label Bardic Inspiration';
      // Warlock: Pakt-Plätze voll beim Short Rest
      sel('Warlock', '', 5); w.eval("st.abUses={wl_pactslots:2,wl_magicalcunning:0}"); w.openRest('short');
      if (!box.textContent.includes('Pact Magic Slotsfull') || !box.textContent.includes('Magical Cunning')) return 'Warlock Short-Rest-Dialog: ' + box.textContent;
      w.doShortRest(); if (w.eval('st.abUses.wl_pactslots')) return 'Pakt-Plätze nicht zurück';
      // Long Rest
      sel('Wizard', '', 5);
      w.eval("st.hpC=3;st.hdUsed=4;st.slotUsed=[3,1,2,0,0,0,0,0,0];st.abUses={wz_arcanerecovery:1};st.dsS=[1,0,0];st.dsF=[1,1,0];st.mySpells=[{name:'Shield',grad:1,school:'Abjuration',prep:true,freeMax:1,freeUsed:1}];document.getElementById('hpT').value=5");
      w.openRest('long'); if (!box.textContent.includes('Hit Points3 → 40') || !box.textContent.includes('Hit Dice1 → 5')) return 'Long-Rest-Dialog: ' + box.textContent;
      w.doLongRest();
      if (w.eval('st.hpC') !== 40 || d.getElementById('hpT').value !== '0' || w.eval('st.hdUsed') !== 0 || w.eval('st.slotUsed.join()') !== '0,0,0,0,0,0,0,0,0' || Object.keys(w.eval('st.abUses')).length || w.eval('st.mySpells[0].freeUsed') || w.eval('st.dsS.join()+st.dsF.join()') !== '0,0,00,0,0') return 'Long Rest unvollständig';
      if (d.querySelector('#dsF .dspip.f')) return 'Death-Save-Kreise nicht geleert';
      if (d.body.innerHTML.includes('onclick="restoreAllUses()"')) return 'alter Reset-Knopf noch da';
      w.resetUI(); return true;
    } },
  { name: 'Paket D: „Cast“ in My Spells – Grad ab Zaubergrad, Platz/Pakt-Platz/Mystic Arcanum/Free Cast/Ritual, Konzentration, Log', datum: '29.09.2026',
    run: ({ w, d, set, sel }) => {
      w.resetUI(); w.eval("document.getElementById('charName').textContent='Regressionstest D'");
      w.applyState({ _f_lvl: '5' }); sel('Wizard', '', 5); w.autoSave();
      const add = n => w.eval(`(()=>{const s=ZB_SPELLS.find(x=>x.name===${JSON.stringify(n)});st.mySpells.push({name:s.name,grad:s.grad,school:s.school,prep:true});return st.mySpells.length-1})()`);
      const fb = add('Fireball'), dm = add('Detect Magic'), fh = add('Fly'), bl = add('Fire Bolt');
      w.buildMySpells();
      if (d.querySelectorAll('#mySpells .sp-cast').length !== 4) return 'Cast-Knöpfe fehlen';
      const keys = i => w.castOptions(i).map(o => o.k + (o.dis ? '-' : '')).join(',');
      if (keys(fb) !== 's2') return 'Fireball Optionen: ' + keys(fb);
      if (keys(dm) !== 's0,s1,s2,ritual') return 'Detect Magic Optionen: ' + keys(dm);
      if (keys(bl) !== 'cantrip') return 'Cantrip: ' + keys(bl);
      w.openCast(fb); d.querySelector('#restBox .cast-opt').click();
      if (w.eval('st.slotUsed[2]') !== 1 || d.getElementById('restModal').classList.contains('on')) return 'Fireball verbraucht keinen Platz 3. Grad';
      w.openCast(fh); w.doCast('s2');
      if (w.eval('st.slotUsed[2]') !== 2 || w.eval('st.concActive') !== fh) return 'Fly: Platz/Konzentration';
      if (keys(fb) !== 's2-') return 'leerer Grad nicht ausgegraut: ' + keys(fb);
      w.openCast(fb); if (!d.getElementById('restBox').textContent.includes('No slot of level 3 or higher left')) return 'Hinweis ohne Platz'; w.closeRest();
      w.doCast && (w.eval(`_castIdx=${dm}`), w.doCast('ritual'));
      if (w.eval('st.slotUsed.join()') !== '0,0,2,0,0,0,0,0,0') return 'Ritual verbraucht Platz';
      const log = w.eval('st.log').map(e => e.m);
      if (!log.includes('Spell cast: Fireball (level 3 slot)') || !log.includes('Spell cast: Detect Magic (Ritual)')) return 'Log: ' + log.slice(-3).join(' / ');
      // Warlock L13: Pakt-Platz 5. Grad, Mystic Arcanum 6/7
      w.eval('st.mySpells=[]'); sel('Warlock', '', 13);
      const hp = add('Hold Monster'), ch = add('Circle of Death');
      if (keys(hp) !== 'pact' || keys(ch) !== 'arc') return 'Warlock: ' + keys(hp) + ' / ' + keys(ch);
      w.eval(`_castIdx=${ch}`); w.doCast('arc');
      if (w.eval("st.abUses['wl_mysticarcanum.6']") !== 1 || keys(ch) !== 'arc-') return 'Mystic Arcanum nicht verbraucht';
      w.eval(`_castIdx=${hp}`); w.doCast('pact');
      if (w.eval('st.abUses.wl_pactslots') !== 1) return 'Pakt-Platz nicht verbraucht';
      w.resetUI(); return true;
    } },
  { name: 'Paket I: Free-Cast-Punkte gefüllt = verfügbar und vor „Cast“, Hit-Points-Raster, Details mit Abstand, Freifläche unten, Skill-Namensblock', datum: '30.09.2026',
    run: ({ w, d, sel }) => {
      sel('Druid', 'Circle of the Stars (XPHB)', 7);
      w.eval("st.mySpells=[{name:'Shield',grad:1,school:'Abjuration',prep:'free',notes:'',freeMax:2,freeUsed:1},{name:'Healing Word',grad:1,school:'Abjuration',prep:true,notes:''}]"); w.buildMySpells();
      const row = d.getElementById('fcu_0'); if (!row) return 'Free-Cast-Punkte fehlen';
      if (row.querySelectorAll('.fc-pip.avail').length !== 1 || row.querySelectorAll('.fc-pip').length !== 2) return 'gefüllt ≠ verfügbar (' + row.querySelectorAll('.fc-pip.avail').length + ')';
      const nx = row.nextElementSibling; if (!nx || !nx.classList.contains('sp-cast')) return 'Free-Cast-Punkte stehen nicht vor „Cast“';
      row.querySelector('.fc-pip').click(); if (w.eval('st.mySpells[0].freeUsed') !== 2) return 'gefüllten Punkt antippen verbraucht nicht';
      d.getElementById('fcu_0').querySelector('.fc-pip').click(); if (w.eval('st.mySpells[0].freeUsed') !== 1) return 'leeren Punkt antippen gibt nicht zurück';
      const css = [...d.querySelectorAll('style')].map(x => x.textContent).join('\n');
      if (!/\.spell-notes\{display:none;padding:10px 11px/.test(css)) return '.spell-notes ohne Abstand oben';
      const g = d.querySelector('.hp-grid .hp-inner'); if (!g || !g.querySelector('.hp-row') || !g.querySelector('.ds-row') || !g.querySelector('.rest-row')) return 'Hit Points nicht in gemeinsamem Raster';
      if (!/\.ds-death,\.hd-box\{grid-column:span 2/.test(css)) return 'Death Saves/Hit Dice nicht über 2 Spalten';
      if (d.getElementById('logList').getAttribute('style')) return 'Log hat noch Sonderabstand';
      if (typeof w.measureNav !== 'function' || !/\.body::after\{[^}]*var\(--nav-h/.test(css)) return 'Freifläche unten nicht an Leistenhöhe gekoppelt';
      if (!/\.sk-name\{[^}]*flex-wrap:wrap/.test(css) || !/\.sk-attr,\.sk-bon\{flex-shrink:0\}/.test(css)) return 'Skill-Zeile: Abzeichen brechen nicht im Namensblock um';
      w.eval('st.mySpells=[]'); w.resetUI(); return true;
    } },
  { name: 'Paket G: Log erfasst alles (Notizen zusammengefasst, Always Prepared, Waffenfelder, Tracker-Namen, Bestien, unbekannte Felder) + Undo/Redo', datum: '01.10.2026',
    run: ({ w, d, sel }) => {
      w.resetUI(); w.eval("document.getElementById('charName').textContent='Regressionstest G'");
      sel('Cleric', '', 6); w.autoSave(); w.eval('st.log=[]');
      const L = () => w.eval('st.log').map(e => e.m);
      const typ = (id, v) => { const el = d.getElementById(id); el.value = v; el.dispatchEvent(new w.Event('input', { bubbles: true })); };
      // Notizen: Tippen = ein Eintrag mit Details
      typ('n_notes', 'D'); typ('n_notes', 'Dra'); typ('n_notes', 'Drache im Norden');
      let log = w.eval('st.log');
      const nt = log.filter(e => /^Notes/.test(e.m));
      if (nt.length !== 1 || nt[0].m !== 'Notes: + "Drache im Norden"' || !nt[0].d || nt[0].d.b !== 'Drache im Norden') return 'Notizen: ' + JSON.stringify(nt);
      // Always Prepared (prep:'free')
      w.eval("st.mySpells=[{name:'Bless',grad:1,school:'Enchantment',prep:true,notes:''}]"); w.autoSave();
      w.togPrep(0);
      if (!L().includes('Spell "Bless": Prepared → Always Prepared')) return 'Always Prepared fehlt: ' + L().slice(-2).join(' / ');
      // Waffenfelder, Tracker-Namen, Bestie, unbekanntes Feld, Auswahl-Name
      w.eval("st.weapons=[{name:'Mace',atk:'+5',dmg:'1d6+3',type:'Bludgeoning'}]"); w.autoSave();
      w.eval("st.weapons[0].atk='+6'"); w.autoSave();
      if (!L().includes('Weapon "Mace" Attack: "+5" → "+6"')) return 'Waffenfeld: ' + L().slice(-2).join(' / ');
      w.eval("st.abUses={channeldivinity:1}"); w.autoSave();
      if (!L().includes('Channel Divinity used: 0 → 1')) return 'Tracker-Name: ' + L().slice(-1);
      w.eval("st.savedBeasts=[BST_DATA.find(b=>b.n==='Wolf')]"); w.autoSave();
      if (!L().includes('+ Beast: Wolf')) return 'Bestie: ' + L().slice(-1);
      w.eval("st.zzNeuesFeld=3"); w.autoSave();
      if (!L().includes('zzNeuesFeld: — → 3')) return 'unbekanntes Feld: ' + L().slice(-1);
      w.eval("delete st.zzNeuesFeld"); w.autoSave();
      w.eval("st.picks['feat:Cleric|base|Divine Order']=['Protector']"); w.autoSave();
      if (!L().includes('Choice Divine Order (Cleric): "—" → "Protector"')) return 'Auswahl-Name: ' + L().slice(-1);
      // Undo/Redo
      const ub = d.getElementById('undoBtn'), rb = d.getElementById('redoBtn');
      if (!ub || !rb || ub.disabled || !rb.disabled) return 'Undo-Knöpfe Zustand';
      w.eval('st.hpC=7'); w.autoSave(); w.eval('st.hpC=3'); w.autoSave();
      w.doUndo(); if (w.eval('st.hpC') !== 7 || d.getElementById('hpC').textContent !== '7') return 'Undo HP: ' + w.eval('st.hpC');
      if (rb.disabled) return 'Redo nicht aktiv';
      if (!L().some(m => m.startsWith('↶ Undone: HP: 3 → 7'))) return 'Undo-Log: ' + L().slice(-1);
      w.doRedo(); if (w.eval('st.hpC') !== 3) return 'Redo HP: ' + w.eval('st.hpC');
      w.doUndo(); w.doUndo(); if (w.eval('st.hpC') !== 10) return 'zweites Undo: ' + w.eval('st.hpC');
      // Tippen = ein Schritt
      typ('n_notes', 'A'); typ('n_notes', 'AB'); typ('n_notes', 'ABC');
      w.doUndo(); if (d.getElementById('n_notes').value !== 'Drache im Norden') return 'Tipp-Folge nicht ein Schritt: ' + d.getElementById('n_notes').value;
      if (rb.disabled) return 'Redo nach Undo leer';
      w.eval('st.hpC=12'); w.autoSave(); if (!rb.disabled) return 'neue Änderung leert Redo nicht';
      // Charakterwechsel leert
      w.resetUI(); if (!ub.disabled || !rb.disabled) return 'Verlauf nach resetUI nicht leer';
      const de = L().filter(m => /[„äöüß]|Rückgängig|verbraucht|Zauber|Waffe|Auswahl/.test(m)); if (de.length) return 'Log nicht englisch: ' + de.slice(0, 3).join(' / ');
      w.eval('st.mySpells=[];st.weapons=[];st.savedBeasts=[];st.picks={}'); w.resetUI(); return true;
    } },
  { name: 'Toast bricht um statt über den Rand zu laufen (Undo-Meldung, Foto Simon)', datum: '01.10.2026',
    run: ({ d }) => {
      const css = [...d.querySelectorAll('style')].map(x => x.textContent).join('\n');
      const m = /\.toast\{[^}]*\}/.exec(css); if (!m) return '.toast fehlt';
      if (/white-space:nowrap/.test(m[0]) || !/max-width:calc\(100vw \/ var\(--zf,1\) - 32px\)/.test(m[0])) return 'Toast: ' + m[0].slice(0, 120);
      return true;
    } },
  { name: 'Paket H: Always Prepared automatisch (Klasse/Subklasse nach Stufe, Abzeichen, gesperrt, Wegfall mit Notiz, manuell, Landtyp-Wahl, ein Log-/Undo-Schritt)', datum: '01.10.2026',
    run: ({ w, d, sel }) => {
      w.resetUI(); w.eval("document.getElementById('charName').textContent='Regressionstest H'");
      const M = () => w.eval('st.mySpells'), F = n => M().find(x => x.name === n), L = () => w.eval('st.log').map(e => e.m);
      const typ = (id, v) => { const el = d.getElementById(id); el.value = v; el.dispatchEvent(new w.Event('input', { bubbles: true })); };
      sel('Cleric', '', 3); w.eval("st.mySpells=[{name:'Bless',grad:1,school:'Enchantment',prep:true,notes:''},{name:'Shield of Faith',grad:1,school:'Abjuration',prep:'free',notes:''}]"); w.autoSave(); w.eval('st.log=[]');
      sel('Cleric', 'Life Domain (PHB)', 3); w.autoSave();
      for (const n of ['Aid', 'Bless', 'Cure Wounds', 'Lesser Restoration']) { const x = F(n); if (!x || x.prep !== 'free' || x.auto !== 'Life Domain') return 'L3 fehlt/falsch: ' + n + ' ' + JSON.stringify(x); }
      if (F('Revivify')) return 'Revivify schon auf Stufe 3';
      if (M().filter(x => x.name === 'Bless').length !== 1 || F('Bless').autoPrev !== true) return 'Bless doppelt oder autoPrev fehlt';
      w.buildMySpells();
      const card = n => [...d.querySelectorAll('#mySpells .spell-card')].find(c => c.querySelector('.spell-name')?.textContent === n);
      if (card('Aid')?.querySelector('.ap-bdg')?.textContent !== 'Life Domain') return 'Abzeichen Aid';
      if (card('Shield of Faith')?.querySelector('.ap-bdg.ap-man')?.textContent !== 'manual') return 'Abzeichen manual';
      if (card('Aid').querySelector('button[onclick^="delMySpell"]')?.style.display !== 'none') return 'Remove bei Automatik sichtbar';
      const ia = M().findIndex(x => x.name === 'Aid'); w.togPrep(ia); w.delMySpell(ia);
      if (F('Aid')?.prep !== 'free') return 'Automatik nicht gesperrt';
      // Stufe 5 per Eingabe: neue Zauber im selben Log-/Undo-Schritt wie die Stufe
      typ('lvl', '5');
      if (!F('Revivify') || !F('Mass Healing Word')) return 'Stufe 5: Revivify/Mass Healing Word fehlen';
      if (!L().includes('+ Spell: Revivify (✦ Life Domain)')) return 'Log: ' + L().slice(-3).join(' / ');
      w.doUndo(); if (d.getElementById('lvl').value !== '3' || F('Revivify')) return 'Undo Stufe+Zauber nicht ein Schritt';
      w.doRedo(); if (!F('Revivify')) return 'Redo';
      // Wegfall: Notiz bleibt (als normaler Zauber), ohne Notiz weg, vorher manuell → alter Zustand
      w.eval("st.mySpells.find(x=>x.name==='Aid').notes='Gruppe'");
      sel('Cleric', 'Light Domain (PHB)', 5); w.autoSave();
      const aid = F('Aid'); if (!aid || aid.prep !== false || aid.auto || aid.autoNew) return 'Aid mit Notiz: ' + JSON.stringify(aid);
      if (F('Cure Wounds') || F('Revivify')) return 'Life-Zauber ohne Notiz nicht entfernt';
      const bl = F('Bless'); if (!bl || bl.prep !== true || bl.auto || 'autoPrev' in bl) return 'Bless nicht zurück: ' + JSON.stringify(bl);
      if (F('Burning Hands')?.auto !== 'Light Domain' || F('Fireball')?.prep !== 'free') return 'Light Domain fehlt';
      // Druid: Basis ab Stufe, Circle of the Land über die Landtyp-Wahl
      w.eval('st.mySpells=[];st.picks={}'); sel('Druid', 'Circle of the Land (PHB)', 3); w.autoSave();
      if (F('Speak with Animals')?.auto !== 'Druid' || F('Find Familiar')?.prep !== 'free') return 'Druid-Basis fehlt';
      if (F('Blur') || F('Fog Cloud')) return 'Land-Zauber ohne Wahl';
      w.eval("st.picks['feat:Druid|Circle of the Land|Circle of the Land Spells']=['Arid Land']"); w.pkRefresh();
      if (F('Blur')?.auto !== 'Circle of the Land' || !/Arid Land/.test(F('Blur').autoInfo)) return 'Arid Land: ' + JSON.stringify(F('Blur'));
      w.eval("st.picks['feat:Druid|Circle of the Land|Circle of the Land Spells']=['Polar Land']"); w.pkRefresh();
      if (F('Blur') || F('Fog Cloud')?.prep !== 'free') return 'Landwechsel';
      // Alter Spielstand: vorhandener Eintrag wird erkannt, nicht doppelt
      const snap = w.eval("(()=>{const s=collectState();s.mySpells=[{name:\"Hunter's Mark\",grad:1,school:'Divination',prep:false,notes:''}];s._f_cls='Ranger';s._f_subcls='';s._f_lvl='2';return s})()");
      w.applyState(snap);
      if (M().filter(x => x.name === "Hunter's Mark").length !== 1 || F("Hunter's Mark").auto !== 'Ranger') return 'Alter Spielstand: ' + JSON.stringify(M());
      w.eval('st.mySpells=[];st.picks={}'); w.resetUI(); return true;
    } },
  { name: 'Paket H2: Feat-Zauber (feste automatisch, Wahl im Feats-Tab, Variante, Stufe, Entfernen, Log)', datum: '01.10.2026',
    run: ({ w, d, sel }) => {
      w.resetUI(); w.eval("document.getElementById('charName').textContent='Regressionstest H2'");
      const M = () => w.eval('st.mySpells'), F = n => M().find(x => x.name === n), L = () => w.eval('st.log').map(e => e.m);
      sel('Fighter', '', 4); w.autoSave(); w.eval('st.log=[]');
      const ft = n => w.eval(`FT_FEATS.find(f=>f.n===${JSON.stringify(n)})`);
      w.ftToggle('Fey-Touched', ft('Fey-Touched').d);
      if (F('Misty Step')?.auto !== 'Fey-Touched' || F('Misty Step').prep !== 'free') return 'Misty Step: ' + JSON.stringify(F('Misty Step'));
      if (!L().includes('+ Spell: Misty Step (✦ Fey-Touched)')) return 'Log Feat+Zauber: ' + L().slice(-3).join(' / ');
      const card = () => [...d.querySelectorAll('#ftMyList .zb-card')].find(c => c.querySelector('.zb-name')?.textContent === 'Fey-Touched');
      if (!card()?.querySelector('.pk-pend') || !card().querySelector('.zb-detail.on .fs-box')) return 'Wahl-Hinweis/Box fehlt';
      const chip = (c, o) => [...c.querySelectorAll('.fs-box .pk-chip')].find(b => b.dataset.o === o);
      if (!chip(card(), 'Charm Person') || chip(card(), 'Magic Missile')) return 'Optionen Enchantment/Divination falsch';
      chip(card(), 'Charm Person').click();
      if (F('Charm Person')?.auto !== 'Fey-Touched') return 'Gewählter Zauber fehlt';
      if (card().querySelector('.pk-pend')) return 'Hinweis bleibt nach Wahl';
      if (!L().some(m => m.startsWith('Choice Fey-Touched spells'))) return 'Log Wahl: ' + L().slice(-2).join(' / ');
      // Variante: Magic Initiate (Wizard) – 2 Cantrips + 1 Zauber
      w.ftToggle('Magic Initiate', ft('Magic Initiate').d);
      const mi = () => [...d.querySelectorAll('#ftMyList .zb-card')].find(c => c.querySelector('.zb-name')?.textContent === 'Magic Initiate');
      chip(mi(), 'Wizard Spells').click();
      chip(mi(), 'Fire Bolt').click(); chip(mi(), 'Mage Hand').click(); chip(mi(), 'Shield').click();
      for (const n of ['Fire Bolt', 'Mage Hand', 'Shield']) if (F(n)?.auto !== 'Magic Initiate') return 'Magic Initiate: ' + n;
      if (mi().querySelector('.pk-pend')) return 'Magic Initiate noch offen';
      // Ritual Caster: Stufe zählt (2 ab L1, +1 ab L5)
      w.ftToggle('Ritual Caster', ft('Ritual Caster').d);
      const rc = () => [...d.querySelectorAll('#ftMyList .zb-card')].find(c => c.querySelector('.zb-name')?.textContent === 'Ritual Caster');
      if (rc().querySelectorAll('.fs-box .pk').length !== 1 || !/From level 5/.test(rc().textContent)) return 'Ritual Caster Stufen';
      if ([...rc().querySelectorAll('.fs-box .pk-chip')].some(b => b.dataset.o === 'Shield')) return 'Ritual-Filter';
      // Entfernen: Zauber weg
      w.ftToggle('Fey-Touched', '');
      if (F('Misty Step') || F('Charm Person')) return 'Zauber nach Entfernen des Feats noch da';
      if (F('Shield')?.auto !== 'Magic Initiate') return 'falscher Feat entfernt';
      w.eval('st.mySpells=[];st.feats=[];st.picks={}'); w.resetUI(); return true;
    } },
  { name: 'My Spells: Always Prepared mit Prepared nach Grad (zuerst, dann alphabetisch), Zeile zweizeilig (Name + Abzeichen darunter)', datum: '01.10.2026',
    run: ({ w, d }) => {
      w.eval("st.mySpells=[{name:'Thunderwave',grad:1,school:'Evocation',prep:true,notes:''},{name:'Shield',grad:1,school:'Abjuration',prep:'free',notes:''},{name:'Guidance',grad:0,school:'Divination',prep:true,notes:''},{name:'Bless',grad:1,school:'Enchantment',prep:true,notes:''},{name:'Entangle',grad:1,school:'Conjuration',prep:false,notes:''}]");
      w.eval('window._apS=apSync;apSync=()=>false'); w.buildMySpells();
      const hd = [...d.querySelectorAll('#mySpells .zb-divider')].map(e => e.textContent);
      if (hd.join('|') !== '✦ Prepared|◦ Unprepared') return 'Abschnitte: ' + hd.join('|');
      const nm = [...d.querySelectorAll('#mySpells .spell-name')].map(e => e.textContent).join(',');
      if (nm !== 'Guidance,Shield,Bless,Thunderwave,Entangle') return 'Reihenfolge: ' + nm;
      const c = d.querySelectorAll('#mySpells .spell-card')[1];
      if (!c.querySelector('.spell-l > .spell-name') || !c.querySelector('.spell-l > .spell-tags .ap-bdg') || !c.querySelector('.spell-tags .sp-info')) return 'Zeile nicht zweizeilig (Name/Abzeichen)';
      if (c.querySelector('.spell-tags .sp-cast, .spell-tags .spell-prep')) return 'Cast/✦ in der Abzeichen-Zeile';
      w.eval('apSync=window._apS;st.mySpells=[]'); w.buildMySpells(); return true;
    } },
  { name: 'Feats: Tabellen aus 5e.tools im Text (Strixhaven Spells, Fast Crafting, Mythal-Touched Magic, Dragonmark-Zauber …)', datum: '01.10.2026',
    run: ({ w, d }) => {
      const tb = (n, src) => { const x = d.createElement('div'); x.innerHTML = w.eval(`fmtDesc(FT_FEATS.find(f=>f.n===${JSON.stringify(n)}&&f.src===${JSON.stringify(src)}).d)`); return x; };
      const sx = tb('Strixhaven Initiate', 'SCC'), t = sx.querySelector('table.fd-tbl');
      if (!t || t.querySelectorAll('th').length !== 3 || t.querySelectorAll('tr').length !== 6 || !t.textContent.includes('Witherbloom')) return 'Strixhaven-Tabelle fehlt/falsch';
      if (!tb('Crafter', 'XPHB').textContent.includes("Woodcarver's Tools")) return 'Fast-Crafting-Tabelle fehlt';
      if (!tb('Mythal Touched', 'FRHoF').textContent.includes('18-19')) return 'Mythal-Touched-Tabelle fehlt';
      if (!tb('Mark of Healing', 'EFA').textContent.includes('Prayer of Healing')) return 'Dragonmark-Zauber fehlen';
      return true;
    } },
  // { name: '…', datum: 'TT.MM.JJJJ', run: ({w,d,set,vis,CD,sel}) => { …; return true; } },
];
// ────────────────────────────────────────────────────────────────────────────

const { JSDOM, VirtualConsole } = require('jsdom');
async function load(p) {
  const errs = [], vc = new VirtualConsole();
  vc.on('jsdomError', e => errs.push(e.message)); vc.on('error', e => errs.push(String(e)));
  const dom = new JSDOM(fs.readFileSync(p, 'utf8'), { runScripts: 'dangerously', pretendToBeVisual: true, virtualConsole: vc, url: 'http://localhost/' });
  await new Promise(r => setTimeout(r, 400));
  return { w: dom.window, d: dom.window.document, errs };
}
const get = (w, name) => { try { return w.eval(`typeof ${name}!=='undefined'?JSON.stringify(${name}):null`); } catch { return null; } };

(async () => {
  // 2) Laufzeittest
  const { w, d, errs } = await load(NEW);
  const CD = JSON.parse(get(w, 'CLASS_DATA') || '{}');
  const CT = JSON.parse(get(w, 'CLASS_TABLES') || '{}'), TR = JSON.parse(get(w, 'CLASS_CORE_TRAITS') || '{}');
  console.log('2) Laufzeit: Klasse | Subkl. | Features L20 | Karten L20 | Class Table | Traits | Beasts-Tab');
  const set = (id, v) => { const el = d.getElementById(id); if (el) el.value = v; };
  const vis = id => { const el = d.getElementById(id); return !!el && el.style.display !== 'none'; };
  for (const cls of Object.keys(CD)) {
    set('lvl', '20'); set('cls', cls); w.onClsChange && w.onClsChange();
    const opts = [...d.getElementById('subcls').options].map(o => o.value).filter(Boolean);
    let subsWithFeat = 0;
    for (const sub of opts) {
      for (const lvl of ['1', '5', '20']) {
        set('lvl', lvl); set('subcls', sub);
        try { w.onSubclsChange ? w.onSubclsChange() : (w.buildAbilities && w.buildAbilities()); } catch (e) { bad(`${cls}/${sub}/L${lvl}: ${e.message}`); }
      }
      const k = CD[cls].subclass && (CD[cls].subclass[sub] ? sub : sub.replace(/\s*\([^)]+\)\s*$/, '').trim());
      if (k && CD[cls].subclass[k]) subsWithFeat++;
    }
    // seit Combat-Tab-Umbau (27.09.2026): Karten statt direkter Kinder zählen (Gruppen-Köpfe/-Boxen)
    const base = (CD[cls].base || []).length, ab = vis('abilitiesSection') ? d.querySelectorAll('#abList .ab-card').length : 0;
    console.log(`   ${cls.padEnd(9)} | ${String(opts.length).padStart(2)} (${subsWithFeat} mit Features) | ${String(base).padStart(3)} | ${String(ab).padStart(3)} | ${cls in CT ? 'ja ' : '—  '} | ${cls in TR ? 'ja' : '— '} | ${vis('tabBestien') ? 'an' : 'aus'}`);
  }
  if (errs.length) errs.forEach(e => bad('JS-Fehler: ' + e)); else console.log('   JS-Fehler: keine');

  // 2b) Regressionstests (frisch geladene App, damit kein Zustand aus Schritt 2 stört)
  console.log(`2b) Regressionstests (${REGRESSION.length})`);
  const R = await load(NEW);
  const rset = (id, v) => { const el = R.d.getElementById(id); if (el) el.value = v; };
  const rvis = id => { const el = R.d.getElementById(id); return !!el && el.style.display !== 'none'; };
  const sel = (cls, sub, lvl) => {
    rset('lvl', String(lvl)); rset('cls', cls); R.w.onClsChange && R.w.onClsChange();
    rset('subcls', sub || ''); R.w.onSubclsChange ? R.w.onSubclsChange() : (R.w.buildAbilities && R.w.buildAbilities());
  };
  for (const t of REGRESSION) {
    let res; try { res = await t.run({ w: R.w, d: R.d, set: rset, vis: rvis, CD, sel }); } catch (e) { res = 'Ausnahme: ' + e.message; }
    if (res === true) console.log(`   ✔ ${t.name}`); else bad(`${t.name} (${t.datum}): ${res}`);
  }
  if (R.errs.length) R.errs.forEach(e => bad('JS-Fehler in Regressionstests: ' + e));

  // 3) Datenvergleich
  if (OLD) {
    console.log('3) Datenvergleich alt → neu');
    const o = await load(OLD);
    const blocks = ['ZB_SPELLS', 'BG_SPELLS', 'CLASS_DATA', 'CLASS_TABLES', 'CLASS_CORE_TRAITS', 'CLASS_SPELL_MAP', 'SL_CLASSES', 'SUBCLASS_SPELLS', 'CLASS_SPELL_EXTRA', 'ALWAYS_PREP', 'FEAT_SPELLS', 'RACE_DATA', 'BG_DATA', 'BG_EXTRA', 'FT_FEATS', 'BST_DATA', 'SPELL_STATBLOCKS', 'RACE_PICKS', 'SUBCLASS_TABLES', 'CLASS_THEMES', 'CLASS_RUNES', 'TEXT_IDS'];
    for (const b of blocks) {
      const A = get(o.w, b), B = get(w, b);
      if (A === null && B === null) continue;
      if (A === null) { console.log(`   ${b}: neu hinzugekommen`); continue; }
      if (B === null) { bad(`${b}: FEHLT in neuer Version`); continue; }
      if (A === B) { console.log(`   ${b}: unverändert`); continue; }
      const a = JSON.parse(A), n = JSON.parse(B);
      if (Array.isArray(a)) {
        const key = x => typeof x === 'object' ? (x.name || x.n) + '|' + (x.src || x.s || '') : String(x);
        const ma = new Map(a.map(x => [key(x), x])), mb = new Map(n.map(x => [key(x), x]));
        const del = [...ma.keys()].filter(k => !mb.has(k)), add = [...mb.keys()].filter(k => !ma.has(k));
        const chg = [...ma.keys()].filter(k => mb.has(k) && JSON.stringify(ma.get(k)) !== JSON.stringify(mb.get(k)));
        console.log(`   ${b}: +${add.length} neu, ~${chg.length} geändert, -${del.length} gelöscht`);
        if (chg.length) console.log('      geändert (max 5): ' + chg.slice(0, 5).join(', '));
        // Name bleibt, nur die Quelle wechselt (Nachdruck, z. B. Haunted One VRGR → RHW): kein Verlust für Savegames, nur melden (01.10.2026)
        const nm = k => k.split('|')[0], namesB = new Set([...mb.keys()].map(nm));
        const moved = del.filter(k => namesB.has(nm(k))), lost = del.filter(k => !namesB.has(nm(k)));
        if (moved.length) console.log(`      Quelle gewechselt (Name bleibt): ${moved.join(', ')}`);
        if (lost.length) bad(`${b}: gelöscht: ${lost.slice(0, 10).join(', ')}${lost.length > 10 ? ' …' : ''}`);
      } else {
        const del = Object.keys(a).filter(k => !(k in n)), add = Object.keys(n).filter(k => !(k in a));
        const chg = Object.keys(a).filter(k => k in n && JSON.stringify(a[k]) !== JSON.stringify(n[k]));
        console.log(`   ${b}: Keys +[${add.join(', ')}] ~[${chg.join(', ')}]`);
        if (del.length) bad(`${b}: Keys gelöscht: ${del.join(', ')}`);
        // Unter-Keys von CLASS_DATA (Subklassen-Namen = Savegame-Bezug) dürfen nie verschwinden
        if (b === 'CLASS_DATA') for (const c of chg) {
          for (const part of ['subclass', 'abilities']) {
            const lost = Object.keys(a[c][part] || {}).filter(k => !(k in (n[c][part] || {})));
            if (lost.length) bad(`CLASS_DATA.${c}.${part}: Keys gelöscht: ${lost.join(', ')}`);
            const lostSub = (a[c].subclassList || []).filter(x => !(n[c].subclassList || []).includes(x));
            if (part === 'subclass' && lostSub.length) bad(`CLASS_DATA.${c}.subclassList: entfernt: ${lostSub.join(', ')}`);
          }
          // Tracker-ids (verbrauchte Nutzungen im Savegame) und special dürfen nie verschwinden (seit 27.09.2026)
          const idsOf = x => Object.values(x.abilities || {}).flat().map(t => t.id);
          const lostIds = idsOf(a[c]).filter(i => !idsOf(n[c]).includes(i));
          if (lostIds.length) bad(`CLASS_DATA.${c}: Tracker-ids gelöscht: ${lostIds.join(', ')}`);
          const lostSp = (a[c].special || []).filter(x => !(n[c].special || []).includes(x));
          if (lostSp.length) bad(`CLASS_DATA.${c}.special: entfernt: ${lostSp.join(', ')}`);
        }
        // Rassen-Tracker-ids (rc_…, Paket C4) dürfen ebenso nie verschwinden
        if (b === 'RACE_PICKS') for (const c of chg) {
          const lostIds = (a[c].tr || []).map(t => t.id).filter(i => !(n[c].tr || []).some(t => t.id === i));
          if (lostIds.length) bad(`RACE_PICKS.${c}: Tracker-ids gelöscht: ${lostIds.join(', ')}`);
        }
      }
    }
  }
  console.log(fail ? `\nERGEBNIS: ${fail} Problem(e)` : '\nERGEBNIS: alles OK');
  process.exit(fail ? 1 : 0);
})();
