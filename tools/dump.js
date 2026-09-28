// dump.js – Datenblock(e) der App als JSON exportieren (seit 28.09.2026, ersetzt die ad-hoc-Skripte dump.js/exp_all.js)
// Aufruf: node willow/tools/dump.js DnD_Character_App.html "<JS-Ausdruck>" ausgabe.json
// Beispiele:
//   rebuild_diff.py:    node willow/tools/dump.js DnD_Character_App.html "{cd:CLASS_DATA,ct:CLASS_TABLES}" all.json
//   subclass_spells.py: node willow/tools/dump.js DnD_Character_App.html "{ZB:ZB_SPELLS.map(s=>({name:s.name,src:s.src,grad:s.grad,school:s.school,classes:s.classes})),MAP:CLASS_SPELL_MAP,SUBS:Object.fromEntries(Object.entries(CLASS_DATA).map(([k,v])=>[k,{list:v.subclassList,keys:Object.keys(v.subclass||{})}]))}" cd.json
// Schreibt immer in eine Datei (Pipe-Ausgabe über 64 KB wird abgeschnitten, Anleitung B9).
const fs = require('fs'), { JSDOM, VirtualConsole } = require('jsdom');
const [, , html, expr, out] = process.argv;
if (!html || !expr || !out) { console.log('Aufruf: node dump.js HTML "<Ausdruck>" ausgabe.json'); process.exit(2); }
const dom = new JSDOM(fs.readFileSync(html, 'utf8'), { runScripts: 'dangerously', pretendToBeVisual: true, virtualConsole: new VirtualConsole(), url: 'http://localhost/' });
setTimeout(() => { fs.writeFileSync(out, dom.window.eval('JSON.stringify(' + expr + ')')); console.log(out, fs.statSync(out).size, 'Bytes'); process.exit(0); }, 500);
