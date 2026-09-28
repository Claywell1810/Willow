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
      w.eval('st.slotMax[0]=4;st.slotUsed[0]=0'); w.buildSlots();
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
      w.buildSlots(); if (d.querySelectorAll('#spSlots .slbtn').length !== 18) return 'Zauberplatz-Knöpfe ohne .slbtn';
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
      const ms = d.getElementById('msn_' + (w.eval('st.mySpells.length') - 1));
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
      if (opened !== 'https://www.google.com/search?q=D%26D%205e%20Fireball') return 'Such-URL: ' + opened;
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
      if (names.join('|') !== 'Celestial Resistance|Darkvision|Healing Hands|Light Bearer|Celestial Revelation') return 'Aasimar-Karten: ' + names.join('|');
      if (!body.querySelector('.fd ul') || body.querySelectorAll('.fd ul li').length !== 3) return 'Aasimar-Verwandlungen nicht als Liste';
      set('race', 'Elf'); w.buildRaceLore();
      if (body.querySelectorAll('.fd p').length < 6) return 'Elf: Folgeabsätze fehlen';
      w.eval("st.bg='Acolyte'"); w.buildBgLore();
      const bg = d.getElementById('bgLoreBody');
      if (bg.innerHTML.includes('**') || !bg.querySelector('.bg-cap') || bg.querySelector('.bg-cap').textContent !== 'Feature: Shelter of the Faithful') return 'Background-Überschrift';
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
    const blocks = ['ZB_SPELLS', 'CLASS_DATA', 'CLASS_TABLES', 'CLASS_CORE_TRAITS', 'CLASS_SPELL_MAP', 'SL_CLASSES', 'SUBCLASS_SPELLS', 'CLASS_SPELL_EXTRA', 'RACE_DATA', 'BG_DATA', 'BG_EXTRA', 'FT_FEATS', 'BST_DATA', 'SPELL_STATBLOCKS', 'CLASS_THEMES', 'CLASS_RUNES', 'TEXT_IDS'];
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
        if (del.length) bad(`${b}: gelöscht: ${del.slice(0, 10).join(', ')}${del.length > 10 ? ' …' : ''}`);
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
      }
    }
  }
  console.log(fail ? `\nERGEBNIS: ${fail} Problem(e)` : '\nERGEBNIS: alles OK');
  process.exit(fail ? 1 : 0);
})();
