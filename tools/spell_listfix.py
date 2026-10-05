#!/usr/bin/env python3
"""spell_listfix.py — Zauber-Texte mit verlorener Listen-Struktur aus 5e.tools neu setzen (Fixliste 05.10.2026)

Alte, aus dem CSV-Export übernommene Texte haben Listeneinträge ohne Trenner („…cube.You double…“) oder mit
doppeltem Leerzeichen („…time.  Altered Eyes. …“). Das Skript rendert betroffene Zauber mit spell_convert.render
neu (Listen als „• …“-Absätze) und übernimmt den neuen Text NUR, wenn er ohne Leerraum und „•“ buchstabengleich
zum alten ist – also nur die Struktur ändert, nie den Inhalt. Abweichungen werden gemeldet und nicht geschrieben.

Aufruf (aus dem Ordner über dem Klon, Quellen per `setup.sh zauber`):
  python3 willow/tools/spell_listfix.py DnD_Character_App.html src [--write]
"""
import json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spell_convert import load_all, render, zsrc

KAPUTT = re.compile(r'[a-z0-9)\]”"]\.[A-Z][a-z]|\.  [A-Z]')
norm = lambda t: re.sub(r'\s+|•|\|', '', t or '')   # Tabellen: Spalten jetzt mit „ | “

html, ddir = sys.argv[1:3]; write = '--write' in sys.argv
# --auch "Name,Name": Abweichung geprüft und gewollt (z. B. Tippfehler in 5e.tools inzwischen korrigiert)
auch = set(sys.argv[sys.argv.index('--auch') + 1].split(',')) if '--auch' in sys.argv else set()
s = open(html, encoding='utf-8').read()
m = re.search(r'const ZB_SPELLS=(\[.*?\]);\n', s)
assert m and s.count('const ZB_SPELLS=') == 1
zb = json.loads(m.group(1))
spells, _ = load_all(ddir)
by = {(x['name'], zsrc(x['source'])): x for x in spells}
fix, bad, miss = [], [], []
for e in zb:
    if not KAPUTT.search(e.get('desc') or ''): continue
    sp = by.get((e['name'], e['src']))
    if not sp: miss.append(f"{e['name']} ({e['src']})"); continue
    neu = '\n\n'.join(render(sp['entries'], []))
    if norm(neu) != norm(e['desc']) and e['name'] not in auch:
        a, b = norm(e['desc']), norm(neu); i = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
        bad.append(f"{e['name']} ({e['src']}): alt …{a[max(0, i-15):i+25]}… neu …{b[max(0, i-15):i+25]}…"); continue
    if neu != e['desc']: e['desc'] = neu; fix.append(e['name'])
print(f'neu gesetzt: {len(fix)}', ', '.join(fix))
print(f'Inhalt weicht ab (nicht geschrieben, prüfen, ggf. --auch): {len(bad)}'); [print('  ' + x) for x in bad]
print(f'nicht in 5e.tools gefunden: {len(miss)}', ', '.join(miss))
if write and fix:
    neu_s = s[:m.start(1)] + json.dumps(zb, ensure_ascii=False, separators=(',', ':')) + s[m.end(1):]
    open(html, 'w', encoding='utf-8').write(neu_s)
    print(html, 'geschrieben', len(neu_s) - len(s), 'Bytes')
