#!/usr/bin/env python3
"""build_class.py — fügt CLASS_DATA/CLASS_TABLES/CLASS_CORE_TRAITS einer Klasse in die HTML ein.
Aufruf: python3 build_class.py DnD_Character_App.html src/class-cleric.json cleric_config.py
Die Klassen-Konfiguration (Tracker, Traits) liegt je Klasse in einer kleinen Python-Datei (CONFIG-dict).
Optional in der Config (seit 27.09.2026):
  'feature_tags': {Gruppe: {Feature-Name: Anzeige-Tag}}  → überschreibt die geratene Feature-Tag-Heuristik (Info-Tab + Tracker)
  Tracker-Feld 'conc': True                               → Konzentrations-Abzeichen „C" (nur bei echter Konzentration)
  Tracker-Feld 'pool': True                               → Pool-Zähler (Zahlenfeld mit Maximum statt Pips, z. B. Lay on Hands)
  Tracker-Feld 'sub': [{'k','l','uses'?,'minLvl'?}]       → Einzel-Tracker je Objekt (eigene Pip-Zeile je Rune/Arcanum/Phase;
                                                            'uses' fehlt = uses des Trackers)
  Tracker-Feld 'pick': {Stufe:Anzahl}                     → nur mit 'sub': so viele Objekte wählt der Charakter (Runes Known)
Neue Klasse, Schritt 0 (Paket N, 03.10.2026): Stub mit subclassList-Vorschlag (Subklassen der maßgeblichen Fassung ohne Nachdrucke)
  python3 build_class.py DnD_Character_App.html src/class-x.json x_config.py --stub   (Config darf noch fehlen)
Einzelne neue Subklasse einer befüllten Klasse (Paket N): an subclassList anhängen + Neubau in einem Aufruf
  python3 build_class.py DnD_Character_App.html src/class-druid.json druid_config.py --rebuild --add-sub "Circle of the Moon (XPHB)"
  (mehrfach möglich; Tracker der neuen Subklasse vorher in der Config ergänzen, sonst hat sie nur Features)
Neubau einer bereits befüllten Klasse (seit 27.09.2026, Bard/Druid/Wizard):
  python3 build_class.py DnD_Character_App.html src/class-druid.json druid_config.py --rebuild
  ersetzt nur den CLASS_DATA-Block; erhält special (z. B. Druid "beasts"), subclassList und vorhandene
  Subklassen-Keys (auch mit Kürzel, z. B. "Circle of Dreams (XGE)"). Tracker-ids stehen in der Config
  (alle alten ids müssen dort wieder vorkommen, sonst Abbruch). CLASS_TABLES und CLASS_CORE_TRAITS bleiben
  unverändert (werden von rebuild_diff.py gegen 5e.tools geprüft); 'traits' in der Config ist dann optional.
"""
import json, re, sys, math, runpy, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # Konverter liegen in tools/
from class_extract import extract, clean, Ctx, text

TAGKEY = {'Passiv': 'passiv', 'Aktion': 'aktion', 'Bonusaktion': 'bonus', 'Reaktion': 'reaktion'}


def apply_feature_tags(cfg, base, subs):
    """Anzeige-Tag einzelner Features überschreiben (Tag-Heuristik trifft Nebensätze). Gleiche Logik in rebuild_diff.py."""
    for grp, m in cfg.get('feature_tags', {}).items():
        src = base if grp == 'base' else subs[grp]
        for name, tg in m.items():
            assert tg in TAGKEY, (grp, name, tg)
            hits = [f for f in src if f['name'] == name]; assert hits, (grp, name)
            for f in hits: f['tag'] = tg


def build_trackers(cfg, base, subs):
    """Tracker (abilities) aus der Config. Gleiche Logik in rebuild_diff.py."""
    feat_by = {}  # erste Fundstelle gewinnt (Features wie Action Surge/Indomitable stehen mehrfach, Stufe 2/9 = Einstieg)
    for f in base: feat_by.setdefault(('base', f['name']), f)
    for k, v in subs.items():
        for f in v: feat_by.setdefault((k, f['name']), f)
    abil = {}
    for grp, items in cfg['trackers'].items():
        lst = []
        for t in items:
            f = feat_by[(grp, t['feature'])]
            desc = f['desc']
            for extra in t.get('append', []):  # Text eines späteren Features anhängen (z. B. Verbesserung)
                g = feat_by[(grp, extra)]
                desc += f"\n{g['name']} (Level {g['lvl']}): {g['desc']}"
            a = {'id': t['id'], 'name': t.get('name', f['name']), 'tag': TAGKEY[t.get('tag', f['tag'])], 'icon': t['icon'],
                 'uses': t['uses'], 'restore': t['restore'], 'desc': desc}
            if f['lvl'] > 1: a['minLvl'] = f['lvl']
            if t.get('conc'): a['conc'] = True
            if t.get('pool'): a['pool'] = True  # Pool-Zähler statt Pips (seit 27.09.2026)
            if t.get('sub'):  # Einzel-Tracker je Objekt (seit 27.09.2026)
                for x in t['sub']: assert set(x) <= {'k', 'l', 'uses', 'minLvl'} and 'k' in x and 'l' in x, x
                a['sub'] = t['sub']
                if t.get('pick'): a['pick'] = t['pick']
            lst.append(a)
        abil[grp] = lst
    return abil


def keep_keys(d, old_keys):
    """Extraktor-Key (Dropdown-Name ohne Kürzel) → vorhandener App-Key (B3: alte Keys mit Kürzel bleiben)."""
    out = {}
    for k, v in d.items():
        hit = [o for o in old_keys if o == k] or [o for o in old_keys if o.startswith(k + ' (')]
        assert len(hit) <= 1, (k, hit)
        out[hit[0] if hit else k] = v
    return out


if __name__ == '__main__':
    HTML, SRC, CFG = sys.argv[1:4]
    REBUILD = '--rebuild' in sys.argv[4:]
    STUB = '--stub' in sys.argv[4:]   # Paket N: Stub einer neuen Klasse anlegen (subclassList-Vorschlag aus 5e.tools)
    ADD_SUB = [sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == '--add-sub']   # Paket N: neue Subklasse „Name (QUELLE)“
    data = json.load(open(SRC))
    s = open(HTML, encoding='utf-8').read()
    if STUB:  # Paket N (03.10.2026): CLASS_DATA-Stub vor „// CLASS FEATURES DATA“; Config darf noch fehlen
        from class_extract import main_class
        from klassen import sub_proposal
        mc = main_class(data)
        name = runpy.run_path(CFG)['CONFIG']['class'] if os.path.exists(CFG) else mc['name']
        if f'CLASS_DATA["{name}"]=' in s: print('Stub/Klasse', name, 'schon vorhanden – nichts geändert'); sys.exit(0)
        lst = sub_proposal(data, mc)
        anchor = '\n// CLASS FEATURES DATA\n'; assert s.count(anchor) == 1, 'Anker // CLASS FEATURES DATA'
        s = s.replace(anchor, '\nCLASS_DATA[%s]={\nspecial:[],\nsubclassList:%s\n};' % (json.dumps(name), json.dumps(lst, ensure_ascii=False, separators=(',', ':'))) + anchor)
        open(HTML, 'w', encoding='utf-8').write(s)
        print(f'Stub {name} ({mc["source"]}) angelegt, subclassList ({len(lst)}):'); [print('  ', x) for x in lst]
        print('Namen sind ab jetzt heilig – Liste prüfen (ggf. im Stub kürzen), dann Config + Build (A4).')
        sys.exit(0)
    cfg = runpy.run_path(CFG)['CONFIG']
    if ADD_SUB:  # Paket N: neue Subklassen an subclassList anhängen (nur anhängen, nie umbenennen), dann Neubau
        assert REBUILD, '--add-sub nur zusammen mit --rebuild'
        i = s.index('CLASS_DATA["%s"]={\n' % cfg['class']); j = s.index('\n};', i)
        m0 = re.search(r'\nsubclassList:(\[[^\n]*\]),\n', s[i:j]); assert m0, 'subclassList nicht gefunden'
        lst = json.loads(m0.group(1)); keys = {re.sub(r'\s*\([^)]+\)\s*$', '', x).strip() for x in lst}
        for a in ADD_SUB:
            assert re.search(r' \([A-Za-z0-9\'-]+\)$', a), f'Form „Name (QUELLE)“ erwartet: {a}'
            k = re.sub(r'\s*\([^)]+\)\s*$', '', a).strip()
            if a in lst or k in keys: print('schon in subclassList:', a); continue
            lst.append(a); keys.add(k); print('subclassList +', a)
        s = s[:i] + s[i:j].replace(m0.group(0), '\nsubclassList:' + json.dumps(lst, ensure_ascii=False, separators=(',', ':')) + ',\n') + s[j:]

    def rep(alt, neu):
        global s
        n = s.count(alt); assert n == 1, f'Anker {n}x gefunden: {alt[:60]!r}'
        s = s.replace(alt, neu)

    J = lambda v: json.dumps(v, ensure_ascii=False)
    def obj(d):  # JS-Objekt im Stil der Datei: unquotierte Keys
        return '{' + ','.join(f'{k}:{J(v)}' for k, v in d.items()) + '}'

    cls_name = cfg['class']
    old_keys, old_ids, special = [], [], '[]'
    if REBUILD:  # befüllte Klasse: ganzen Block bis zur ersten Zeile "};" ersetzen
        i = s.index('CLASS_DATA["%s"]={\n' % cls_name); j = s.index('\n};', i) + 3
        stub = s[i:j]
        m = re.search(r'\nsubclassList:(\[[^\n]*\]),\n', stub); assert m, 'subclassList nicht gefunden'
        special = re.search(r'\nspecial:(\[[^\]\n]*\]),\n', stub).group(1)
        k0 = stub.index('\nsubclass:{')
        old_keys = re.findall(r'\n\s*"([^"]+)":\[', stub[k0:])
        old_ids = re.findall(r'\bid:"([^"]+)"', stub)
        assert stub.count('CLASS_DATA[') == 1 and stub.endswith('\n};'), 'Blockgrenzen unklar'
    else:
        # subclassList aus der HTML lesen (nicht ändern!)
        m = re.search(r'CLASS_DATA\["%s"\]=\{\nspecial:\[\],\nsubclassList:(\[[^\n]*\])\n\};' % cls_name, s)
        assert m, 'Stub nicht gefunden'
        stub = m.group(0)
    dropdown = json.loads(m.group(1))
    # optionalfeatures.json neben der Klassen-Datei (falls vorhanden): Texte für Manöver, Runen u. ä.
    OPTF = os.path.join(os.path.dirname(SRC), 'optionalfeatures.json')
    optf = json.load(open(OPTF))['optionalfeature'] if os.path.exists(OPTF) else None
    FEATS = os.path.join(os.path.dirname(SRC), 'feats.json')  # optional: Feat-Texte für refFeat (z. B. Paladin Blessed Warrior)
    feats = json.load(open(FEATS))['feat'] if os.path.exists(FEATS) else None
    ITEMS = os.path.join(os.path.dirname(SRC), 'items.json')  # optional: Gegenstands-Statblöcke (Rogue: Psychic Blade)
    items = json.load(open(ITEMS))['item'] if os.path.exists(ITEMS) else None
    cls, base, subs, srcs = extract(data, dropdown, optf, feats, items)
    apply_feature_tags(cfg, base, subs)

    # --- Tracker
    abil = build_trackers(cfg, base, subs)
    if REBUILD:
        subs, abil, srcs = keep_keys(subs, old_keys), keep_keys(abil, old_keys), keep_keys(srcs, old_keys)
        assert set(old_keys) <= set(subs), ('Subklassen-Key fehlt', set(old_keys) - set(subs))
        new_ids = [a['id'] for v in abil.values() for a in v]
        assert len(new_ids) == len(set(new_ids)), 'Tracker-id doppelt'
        assert set(old_ids) <= set(new_ids), ('Tracker-id fehlt', set(old_ids) - set(new_ids))

    L = []
    L.append(f'CLASS_DATA["{cls_name}"]={{')
    L.append('special:' + special + ',')
    L.append('subclassList:' + m.group(1) + ',')
    L.append('// Quelle: 5e.tools class-%s.json (%s); Subklassen neueste Fassung: %s' % (cls_name.lower(), cls['source'], ', '.join(f'{k}={v}' for k, v in srcs.items())))
    L.append('abilities:{')
    for grp, lst in abil.items():
        L.append(f'    {J(grp)}:[' if grp != 'base' else '    base:[')
        for a in lst: L.append('      ' + obj(a) + ',')
        L.append('    ],')
    L.append('},')
    L.append('base:[')
    for f in base: L.append('  ' + obj(f) + ',')
    L.append('],')
    L.append('subclass:{')
    for k, v in subs.items():
        L.append(f'  {J(k)}:[')
        for f in v: L.append('    ' + obj(f) + ',')
        L.append('  ],')
    L.append('}')
    L.append('};')
    rep(stub, '\n'.join(L))
    if REBUILD:  # Class Table und Traits bleiben (rebuild_diff.py prüft die Tabelle gegen 5e.tools)
        open(HTML, 'w', encoding='utf-8').write(s)
        print('OK (Neubau)', cls_name, 'base', len(base), 'subclasses', len(subs), 'tracker', sum(len(v) for v in abil.values()))
        sys.exit(0)

    # --- Class Table
    groups = cls['classTableGroups']
    extra, cols, slots = [], [], None
    for g in groups:
        if 'rowsSpellProgression' in g: slots = g['rowsSpellProgression']; continue
        for i, lab in enumerate(g['colLabels']):
            l = clean(lab); k = re.sub(r'[^a-z]', '', l.split()[0].lower())
            extra.append({'k': k, 'l': l}); cols.append((k, [r[i] for r in g['rows']]))
    feat_lv = {}
    for ref in cls['classFeatures']:
        r = ref['classFeature'] if isinstance(ref, dict) else ref
        p = r.split('|'); feat_lv.setdefault(int(p[3]), []).append('Subclass Feature' if p[0].lower() == 'subclass feature' else p[0])  # EFA: „Subclass feature“
    rows = []
    for lvl in range(1, 21):
        row = {'lvl': lvl, 'pb': math.ceil(lvl / 4) + 1, 'f': ', '.join(feat_lv.get(lvl, [])) or '—'}
        for k, vals in cols:
            v = vals[lvl - 1]
            if isinstance(v, dict) and v.get('type') == 'dice':  # Würfel-Zelle (Rogue: Sneak Attack) → „3d6"
                v = '+'.join(f"{x['number']}d{x['faces']}" for x in v['toRoll'])
            elif isinstance(v, dict) and v.get('type') == 'bonusSpeed':  # Speed-Zelle (Monk: Unarmored Movement) → „+10 ft.", 0 → „—"
                v = f"+{v['value']} ft." if v['value'] else 0
            elif isinstance(v, dict) and v.get('type') == 'bonus':  # Bonus-Zelle (Barbarian: Rage Damage) → „+2"
                v = f"+{v['value']}" if v['value'] else 0
            row[k] = v if v not in (0, None, '') else '—'
        row['slots'] = (list(slots[lvl - 1]) + [0] * 9)[:9] if slots else [0] * 9  # Halbzauberer: nur 5 Grade in der Quelle → auf 9 auffüllen
        rows.append(row)
    tbl = [f"  {J(cls_name).replace(chr(34), chr(39))}:{{",
           '    extra:[' + ','.join(obj(e) for e in extra) + '],',
           '    rows:[']
    tbl += ['      ' + obj(r) + ',' for r in rows]
    tbl += ['    ]', '  }']
    rep("const CLASS_TABLES={\n", "const CLASS_TABLES={\n" + '\n'.join(tbl) + ',\n')

    # --- Core Traits
    tr = cfg['traits']
    rep("const CLASS_CORE_TRAITS = {\n", "const CLASS_CORE_TRAITS = {\n  " + J(cls_name) + ": " + json.dumps(tr, ensure_ascii=False, indent=4).replace('\n', '\n  ') + ",\n")

    open(HTML, 'w', encoding='utf-8').write(s)
    print('OK', cls_name, 'base', len(base), 'subclasses', len(subs), 'tracker', sum(len(v) for v in abil.values()))
