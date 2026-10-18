#!/usr/bin/env python3
"""build_2014.py – baut Willow 2014 aus der 2024-App (Paket T1, 18.10.2026; „ein Code, zwei Builds“)

Aufruf (aus dem Ordner über dem Klon):
    python3 willow/tools/build_2014.py QUELLE.html [--out ORDNER] [--version willow14-app-…]

    QUELLE.html  meist DnD_Character_App.html (Arbeitskopie) oder willow/index.html
    --out        Zielordner (Standard willow/2014); geschrieben werden index.html, service-worker.js, manifest.json
    --version    APP_VERSION + CACHE_NAME der 2014-App; ohne Angabe bleibt die Version aus ORDNER/index.html
                 (gibt es keine: willow14-app-dev). Neue Versionen setzt publish.sh.

Was der Build ändert (alles andere ist gemeinsamer Code):
  1. const RULES='2024' → '2014' (damit R14=true und LS_PFX='w14_': Regel-Weichen, getrennter Speicher)
  2. APP_VERSION, Name auf dem Home-Bildschirm (apple-mobile-web-app-title), <title>
  3. Datenblöcke: jede Datei tools/t14/<BLOCK>.js ersetzt die Zeile `const <BLOCK>=…` der Quelle
     (Datei = genau eine Zeile `const <BLOCK>=…;`, erzeugt von den Konvertern mit --t14 ab Paket T2;
     in T1 noch leer → 2014-Build läuft mit den 2024-Daten)
  4. service-worker.js aus willow/service-worker.js mit eigenem CACHE_NAME, manifest.json aus willow/manifest.json
     mit eigenem Namen und eigener id/scope/start_url (Ordner 2014/ = eigene Installation)
Icons (2014/willow-icon-*.png, Banderole „2014“) erzeugt tools/t14_icon.py, nicht dieser Build.
"""
import glob, json, os, re, sys

W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # Klon (…/willow)
T14 = os.path.join(W, 'tools', 't14')


def fail(m):
    sys.exit('ABBRUCH build_2014: ' + m)


def one(s, alt, neu, was):
    n = s.count(alt)
    if n != 1:
        fail(f'{was}: Anker {n}× statt 1× gefunden ({alt[:60]!r})')
    return s.replace(alt, neu)


def version_of(html):
    m = re.search(r"const APP_VERSION = '([^']*)';", html)
    return m.group(1) if m else None


def build(src, out, version=None):
    s = open(src, encoding='utf-8').read()
    if not s.rstrip().endswith('</html>'):
        fail(f'{src} endet nicht mit </html>')
    if version is None:
        alt = os.path.join(out, 'index.html')
        version = (version_of(open(alt, encoding='utf-8').read()) if os.path.exists(alt) else None) or 'willow14-app-dev'
    if not version.startswith('willow14-app-'):
        fail(f'Version {version!r} muss mit willow14-app- beginnen (eigener Cache-Präfix, service-worker.js)')

    # 1) Regelwerk
    s = one(s, "const RULES='2024';", "const RULES='2014';", 'RULES')
    # 2) Version und Name
    s, n = re.subn(r"const APP_VERSION = '[^']*';", f"const APP_VERSION = '{version}';", s)
    if n != 1:
        fail(f'APP_VERSION {n}× gefunden')
    s = one(s, '<meta name="apple-mobile-web-app-title" content="Willow">', '<meta name="apple-mobile-web-app-title" content="Willow 2014">', 'Home-Name')
    s = one(s, '<title>D&D 5e Character Sheet</title>', '<title>D&D 5e Character Sheet (2014)</title>', 'title')
    # 3) Datenblöcke aus tools/t14/
    bl = []
    for f in sorted(glob.glob(os.path.join(T14, '*.js'))):
        name = os.path.basename(f)[:-3]
        neu = open(f, encoding='utf-8').read().strip()
        if '\n' in neu or not re.match(rf'const {re.escape(name)}\s*=', neu) or not neu.endswith(';'):
            fail(f'{f}: muss genau eine Zeile `const {name}=…;` sein')
        hits = [m for m in re.finditer(rf'^const {re.escape(name)}\s*=.*$', s, re.M)]
        if len(hits) != 1:
            fail(f'Block {name}: {len(hits)}× in der Quelle gefunden (Zeile `const {name}=…` muss eindeutig sein)')
        a, b = hits[0].span()
        s = s[:a] + neu + s[b:]
        bl.append(name)
    # 4) Schreiben
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(s)
    sw = open(os.path.join(W, 'service-worker.js'), encoding='utf-8').read()
    sw, n = re.subn(r'const CACHE_NAME = "[^"]*";', f'const CACHE_NAME = "{version}";', sw)
    if n != 1:
        fail('CACHE_NAME in service-worker.js nicht gefunden')
    open(os.path.join(out, 'service-worker.js'), 'w', encoding='utf-8').write(sw)
    mf = json.load(open(os.path.join(W, 'manifest.json'), encoding='utf-8'))
    mf.update({'name': 'Willow 2014 Character App', 'short_name': 'Willow 2014',
               'description': 'D&D 5e Charakterbogen (Regeln 2014, SRD 5.1)',
               'id': './', 'start_url': './', 'scope': './'})
    json.dump(mf, open(os.path.join(out, 'manifest.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'Willow 2014 gebaut: {out}/index.html ({len(s.encode())} Bytes), Version {version}, '
          f'Datenblöcke aus tools/t14: {", ".join(bl) if bl else "keine (2024-Daten)"}')
    return version


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0].startswith('-'):
        print(__doc__); sys.exit(2)
    src, out, ver = a[0], os.path.join(W, '2014'), None
    if '--out' in a: out = a[a.index('--out') + 1]
    if '--version' in a: ver = a[a.index('--version') + 1]
    build(src, out, ver)
