#!/usr/bin/env python3
"""item_convert.py — Gegenstände und Startausrüstung (Paket O2, 03.10.2026)

Aufruf (aus dem Ordner über dem Klon; braucht src/items-base.json, src/items.json, src/class-<k>.json
aller Klassen der App und src/backgrounds.json → `bash willow/tools/setup.sh klassen neu`):
    python3 willow/tools/item_convert.py DnD_Character_App.html src [--write]

Erzeugt zwischen `// ITEM_DATA-START` und `// ITEM_DATA-END` (erstes Einfügen: vor `// ARMOR_DATA-START`):

ITEM_DATA = [{…}] – nicht-magische Gegenstände aus 5e.tools (O-E4), Schlüssel `n|s` (ITEM_MAP):
  n Name, s Quelle, c Kategorie (= Key von ITEM_CATS), t Typ (5e.tools itemType, z. B. „Melee Weapon“),
  w Gewicht in lb (O-E1), v Preis in cp,
  Waffen: wc simple/martial, d Schaden, d2 Versatile-Schaden, dt Schadensart, p Eigenschaften (Keys in ITEM_RULES.p),
          r Reichweite, am Munitionsart, m Mastery (Keys in ITEM_RULES.m), pn/mn Zusatz je Eigenschaft/Mastery
          (z. B. Lance pn {"2H|XPHB":"unless mounted"}),
  Rüstung: at L/M/H/S (wie ARMOR_DATA.c), ac, str Mindest-Stärke, st 1 = Nachteil auf Stealth,
  pk Pack-Inhalt [{i:"Backpack|XPHB",q:1} | {sp:"Freitext",q}] (O-E2), gv Gruppen-Varianten ["Amulet|XPHB",…]
  (Holy Symbol, Arcane Focus, Musical Instrument …), x kurzer Text (5e.tools entries).
  Umfang: alle Gegenstände mit rarity „none“ aus items-base.json + items.json + itemGroup, ohne `_copy`, ohne Münzen ($C)
  und ohne Nachdrucke (`reprintedAs`, XPHB bevorzugt) – Nachdrucke nur, wenn START_EQUIP oder ein Pack/eine
  Gruppe sie nennt (alte PHB-Backgrounds behalten ihre PHB-Gegenstände).
ITEM_RULES = {p:{"F|XPHB":{n,t}}, m:{"Sap":"…"}} – Eigenschaften und Mastery-Texte (items-base.json).
START_EQUIP = {cls:{"Wizard":[Gruppe…]}, bg:{"Acolyte":[Gruppe…]}} – Klassen (maßgebliche Fassung, main_class)
  und alle Backgrounds aus BG_DATA (ohne Ausrüstung: []). Gruppe = {k:"_"|"choice", o:{A:[…],B:[…]}}
  (k "_" = fest, o hat dann nur "_"; Wahl-Keys wie in 5e.tools: A/B(/C) bzw. a/b(/c/d)). Einträge:
    {i:"Dagger|XPHB", q:2, dn:"Anzeigename", cv:1500}   Gegenstand (q fehlt = 1; cv = enthält Geld in cp, z. B. Pouch)
    {cp:500}                                             Geld in cp → Münzfelder (O3)
    {sp:"Spellbook", q, wv}                              Freitext (wv = Wert in cp)
    {ch:["Gaming Set|XPHB"], dn}                         Wahl aus der/den Gruppe(n) (5e.tools equipmentType/-Types)
Geld je Wahl A/B wird gegen den 5e.tools-Text („… 7 GP; or (B) 110 GP“) geprüft; bei Abweichung gilt der Text
(Meldung KORREKTUR; Stand 03.10.2026: Cleric A 7000 cp → 700 cp, Mulhorandi Tomb Raider A „Waterskin 26 GP“ → +26 GP).
Ohne --write nur Bericht. Unbekannte Felder/Typen → Abbruch mit FEHLER (nichts erfinden).
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from class_extract import main_class, text, clean, render  # noqa: E402
from klassen import app_classes  # noqa: E402
from bg_convert import grab  # noqa: E402

CAT = {'M': 'Weapon', 'R': 'Weapon',
       'LA': 'Armor', 'MA': 'Armor', 'HA': 'Armor', 'S': 'Armor',
       'AT': 'Tool', 'T': 'Tool', 'GS': 'Tool', 'INS': 'Tool',
       'A': 'Consumable', 'AF': 'Consumable', 'FD': 'Consumable', 'P': 'Consumable', 'EXP': 'Consumable'}
ARM = {'LA': 'L', 'MA': 'M', 'HA': 'H', 'S': 'S'}
DMG = {'A': 'Acid', 'B': 'Bludgeoning', 'C': 'Cold', 'F': 'Fire', 'O': 'Force', 'L': 'Lightning', 'N': 'Necrotic',
       'P': 'Piercing', 'I': 'Poison', 'Y': 'Psychic', 'R': 'Radiant', 'S': 'Slashing', 'T': 'Thunder'}
# 5e.tools equipmentType → Gruppe, aus der gewählt wird (XPHB-Fassung, 2024 bevorzugt)
ETYPE = {'toolArtisan': "Artisan's Tools|XPHB", 'instrumentMusical': 'Musical Instrument|XPHB',
         'setGaming': 'Gaming Set|XPHB'}
MAGIC = ('bonusWeapon', 'bonusAc', 'bonusSpellAttack', 'reqAttune', 'charges', 'attachedSpells', 'wondrous')


def src_of(ref):
    """'dagger|xphb' → ('dagger', 'xphb'); ohne Quelle = DMG (5e.tools-Vorgabe für Gegenstände, z. B. ammoType „modern bullet“)."""
    p = ref.split('|')
    return p[0].strip().lower(), (p[1].strip().lower() if len(p) > 1 and p[1].strip() else 'dmg')


class Items:
    def __init__(self, src):
        b = json.load(open(os.path.join(src, 'items-base.json'), encoding='utf-8'))
        it = json.load(open(os.path.join(src, 'items.json'), encoding='utf-8'))
        self.base = b
        self.all = {}
        for i in b['baseitem'] + it['item'] + it['itemGroup']:
            k = (i['name'].lower(), i['source'].lower())
            assert k not in self.all, ('doppelt', k)
            self.all[k] = i
        self.tname = {}
        for t in b['itemType']:  # XPHB-Namen bevorzugt
            if t['abbreviation'] not in self.tname or t['source'] == 'XPHB': self.tname[t['abbreviation']] = t.get('name')

    def get(self, ref):
        k = src_of(ref)
        if k not in self.all: sys.exit(f'FEHLER: Gegenstand {ref} nicht in items(-base).json')
        return self.all[k]

    @staticmethod
    def key(i):
        return i['name'] + '|' + i['source']


def mundane(i):
    # Münzen ($C) nicht: Geld steht in den Münzfeldern (cur_pp … cur_cp)
    return i.get('rarity') == 'none' and '_copy' not in i and not any(k in i for k in MAGIC) \
        and str(i.get('type', '')).split('|')[0] != '$C'


def conv(i, I):
    """5e.tools-Gegenstand → ITEM_DATA-Eintrag."""
    t = str(i.get('type', '')).split('|')[0]
    e = {'n': i['name'], 's': i['source'], 'c': CAT.get(t) or ('Consumable' if i.get('poison') else 'Misc')}
    if t:
        if t not in I.tname: sys.exit(f'FEHLER: Typ {t} ({I.key(i)}) unbekannt')
        if I.tname[t]: e['t'] = I.tname[t]
    if i.get('weight'): e['w'] = i['weight']
    if i.get('value'): e['v'] = i['value']
    if i.get('weaponCategory'): e['wc'] = i['weaponCategory']
    if i.get('dmg1'):
        e['d'] = i['dmg1']
        if i.get('dmgType') not in DMG: sys.exit(f'FEHLER: Schadensart {i.get("dmgType")} ({I.key(i)})')
        e['dt'] = DMG[i['dmgType']]
    if i.get('dmg2'): e['d2'] = i['dmg2']
    if i.get('property'):
        e['p'] = [prop_key(p if isinstance(p, str) else p['uid']) for p in i['property']]
        pn = {prop_key(p['uid']): p['note'] for p in i['property'] if isinstance(p, dict) and p.get('note')}
        if pn: e['pn'] = pn
    if i.get('range'): e['r'] = i['range']
    if i.get('ammoType'): e['am'] = I.get(i['ammoType'])['name']
    if i.get('mastery'):
        e['m'] = [(m if isinstance(m, str) else m['uid']).split('|')[0] for m in i['mastery']]
        mn = {m['uid'].split('|')[0]: m['note'] for m in i['mastery'] if isinstance(m, dict) and m.get('note')}
        if mn: e['mn'] = mn
    if t in ARM:
        e['at'] = ARM[t]
        if 'ac' in i: e['ac'] = i['ac']
        if i.get('strength'): e['str'] = int(i['strength'])
        if i.get('stealth'): e['st'] = 1
    if i.get('packContents'):
        pk = []
        for x in i['packContents']:
            if isinstance(x, str): pk.append({'i': x})
            elif 'item' in x: pk.append({'i': x['item'], 'q': x.get('quantity', 1)})
            elif 'special' in x: pk.append({'sp': x['special'], 'q': x.get('quantity', 1)})
            else: sys.exit(f'FEHLER: Pack-Eintrag {x} ({I.key(i)})')
        for x in pk:
            if 'i' in x: x['i'] = I.key(I.get(x['i']))
            if x.get('q') == 1: del x['q']
        e['pk'] = pk
    if i.get('items'):
        e['gv'] = [I.key(I.get(x)) for x in i['items']]
    if i.get('entries'):
        x = re.sub(r':\. ', ': ', text(i['entries'], None))  # Werkzeug-Listen „Ability:“ → „• Ability: Dexterity“
        if x: e['x'] = x
    return e


def prop_key(p):
    a, _, s = p.partition('|')
    return a + '|' + (s or 'PHB')


def equip_entry(x, I, need):
    """Ein Eintrag der 5e.tools-Startausrüstung → START_EQUIP-Eintrag."""
    if isinstance(x, str): x = {'item': x}
    known = {'item', 'quantity', 'displayName', 'containsValue', 'value', 'special', 'worthValue', 'equipmentType', 'equipmentTypes'}
    if set(x) - known: sys.exit(f'FEHLER: unbekanntes Feld in Startausrüstung: {x}')
    if 'item' in x:
        k = I.key(I.get(x['item'])); need.add(k)
        e = {'i': k}
    elif 'value' in x:
        return {'cp': x['value']}
    elif 'special' in x:
        e = {'sp': x['special']}
        if 'worthValue' in x: e['wv'] = x['worthValue']
    elif 'equipmentType' in x or 'equipmentTypes' in x:
        ts = [x['equipmentType']] if 'equipmentType' in x else x['equipmentTypes']
        if set(ts) - set(ETYPE): sys.exit(f'FEHLER: equipmentType {ts} ohne Zuordnung (ETYPE)')
        e = {'ch': [ETYPE[t] for t in ts]}; need.update(e['ch'])
    else:
        sys.exit(f'FEHLER: Startausrüstung ohne item/value/special/equipmentType: {x}')
    if x.get('quantity', 1) != 1: e['q'] = x['quantity']
    if x.get('displayName'):
        dn = x['displayName']
        m = re.match(r'^(.+?),?\s+\d+\s*GP$', dn)  # Geld im Anzeigenamen (5e.tools-Datenfehler) → fix_money ergänzt es
        if m: dn = m.group(1); WARN.append(f'Anzeigename „{x["displayName"]}“ → „{dn}“ (Geld kommt aus dem Text)')
        if dn.lower() != (k.split('|')[0].lower() if 'item' in x else ''): e['dn'] = dn
    if x.get('containsValue'): e['cv'] = x['containsValue']
    return e


WARN = []
MONEY = re.compile(r'(\d[\d,]*)\s*(GP|SP|CP|PP|EP)\b', re.I)
CPV = {'pp': 1000, 'gp': 100, 'ep': 50, 'sp': 10, 'cp': 1}


def text_money(txt):
    """'(A) … 7 GP; or (B) 110 GP' → {'A': 700, 'B': 11000} (Geld je Wahl im 5e.tools-Text)."""
    parts = re.split(r'\(([A-Za-z])\)\s*', txt)
    return {k: sum(int(n.replace(',', '')) * CPV[u.lower()] for n, u in MONEY.findall(seg)) for k, seg in zip(parts[1::2], parts[2::2])}


def fix_money(name, G, txt):
    """Geld je Wahl (A/B) gegen den 5e.tools-Text prüfen. Weicht es ab, gilt der Text (Datenfehler in
    defaultData/startingEquipment, z. B. Cleric 7000 cp statt 7 GP) – Meldung KORREKTUR, nichts erfunden."""
    if not txt or len(G) != 1 or G[0]['k'] != 'choice': return
    t = text_money(txt)
    for o, L in G[0]['o'].items():
        if o not in t: continue
        cur = sum(e.get('cp', 0) for e in L)
        if cur == t[o]: continue
        cps = [e for e in L if 'cp' in e]
        if len(cps) == 1 and t[o]: old = cps[0]['cp']; cps[0]['cp'] = t[o]
        elif not cps and t[o]: old = 0; L.append({'cp': t[o]})
        else: sys.exit(f'FEHLER: {name} ({o}) Geld {cur} cp ≠ Text {t[o]} cp')
        WARN.append(f'{name} ({o}): {old} cp → {t[o]} cp laut 5e.tools-Text')


def bg_equip_text(b):
    for e in b.get('entries', []):
        if isinstance(e, dict) and e.get('type') == 'list':
            for it in e.get('items', []):
                if clean(it.get('name', '')).lower().startswith('equipment'):
                    return ' '.join(render(it.get('entry') or it.get('entries', []), None, []))
    return ''


def equip(blocks, I, need):
    out = []
    for blk in blocks:
        keys = list(blk)
        if keys == ['_']: k = '_'
        elif len(keys) >= 2 and '_' not in keys: k = 'choice'
        else: sys.exit(f'FEHLER: Gruppe mit Keys {keys}')
        out.append({'k': k, 'o': {o: [equip_entry(x, I, need) for x in blk[o]] for o in keys}})
    return out


def build(html, src):
    I = Items(src)
    s = open(html, encoding='utf-8').read()
    need = set()
    se = {'cls': {}, 'bg': {}}
    for c in app_classes(html):
        f = os.path.join(src, f'class-{c.lower()}.json')
        if not os.path.exists(f): sys.exit(f'FEHLER: {f} fehlt (setup.sh klassen)')
        m = main_class(json.load(open(f, encoding='utf-8')))
        dd = (m.get('startingEquipment') or {}).get('defaultData')
        if not dd: sys.exit(f'FEHLER: {c} ({m["source"]}) ohne startingEquipment.defaultData')
        se['cls'][c] = equip(dd, I, need)
        fix_money(c, se['cls'][c], ' '.join(clean(x) for x in m['startingEquipment'].get('entries', []) if isinstance(x, str)))
    a, z = grab(s, 'BG_DATA'); bgd = json.loads(s[a:z])
    bgs = {(b['name'], b['source']): b for b in json.load(open(os.path.join(src, 'backgrounds.json'), encoding='utf-8'))['background']}
    ohne = []
    for d in bgd:
        b = bgs.get((d['n'], d['src']))
        if not b: sys.exit(f'FEHLER: Background {d["n"]}|{d["src"]} nicht in backgrounds.json')
        se['bg'][d['n']] = equip(b.get('startingEquipment') or [], I, need)
        fix_money(d['n'], se['bg'][d['n']], bg_equip_text(b))
        if not se['bg'][d['n']]: ohne.append(d['n'])

    # Umfang: Katalog (nicht-magisch, ohne Nachdrucke) + alles, was START_EQUIP/Packs/Gruppen nennen (rekursiv)
    keys = {I.key(i) for i in I.all.values() if mundane(i) and not i.get('reprintedAs')}
    todo = list(need | keys); data = {}
    while todo:
        k = todo.pop()
        if k in data: continue
        i = I.get(k)
        if i.get('rarity') != 'none': sys.exit(f'FEHLER: {k} ist magisch (rarity {i.get("rarity")}) – O-E4')
        data[k] = conv(i, I)
        todo += [x['i'] for x in data[k].get('pk', []) if 'i' in x] + data[k].get('gv', [])
    items = sorted(data.values(), key=lambda e: (e['n'].lower(), e['s'] != 'XPHB', e['s']))

    used_p = {p for e in items for p in e.get('p', [])}
    props = {prop_key(p['abbreviation'] + '|' + p['source']): p for p in I.base['itemProperty']}
    rp = {}
    for k in sorted(used_p):
        p = props.get(k)
        if not p: sys.exit(f'FEHLER: Eigenschaft {k} nicht in itemProperty')
        ent = p.get('entries') or []
        nm = ent[0].get('name') if ent and isinstance(ent[0], dict) else (p.get('name') or k.split('|')[0]).title()
        body = text(ent[0].get('entries', []), None) if ent and isinstance(ent[0], dict) else ''
        rp[k] = {'n': nm, 't': body}
    used_m = {m for e in items for m in e.get('m', [])}
    rm = {}
    for m in I.base['itemMastery']:
        if m['name'] in used_m and m['source'] == 'XPHB': rm[m['name']] = text(m['entries'], None)
    if used_m - set(rm): sys.exit(f'FEHLER: Mastery ohne Text: {used_m - set(rm)}')
    return items, {'p': rp, 'm': rm}, se, ohne, need


def main():
    html, src = sys.argv[1], sys.argv[2]
    items, rules, se, ohne, need = build(html, src)
    J = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':'))
    block = ('// ITEM_DATA-START (tools/item_convert.py, 5e.tools items-base.json/items.json, class-*.json, backgrounds.json; Paket O2)\n'
             'const ITEM_DATA=' + J(items) + ';\n'
             'const ITEM_MAP=Object.fromEntries(ITEM_DATA.map(i=>[i.n+"|"+i.s,i]));\n'
             'const ITEM_RULES=' + J(rules) + ';\n'
             'const START_EQUIP=' + J(se) + ';\n'
             '// ITEM_DATA-END\n')
    from collections import Counter
    print(f'ITEM_DATA: {len(items)} Gegenstände ({len(J(items)) // 1024} KB) –',
          ', '.join(f'{k} {v}' for k, v in sorted(Counter(e["c"] for e in items).items())))
    print('  Quellen:', ', '.join(f'{k} {v}' for k, v in Counter(e['s'] for e in items).most_common()))
    print(f'  Packs {sum("pk" in e for e in items)}, Gruppen {sum("gv" in e for e in items)}, Waffen {sum("d" in e for e in items)}, '
          f'Rüstung {sum("at" in e for e in items)}, mit Text {sum("x" in e for e in items)}')
    print(f'ITEM_RULES: {len(rules["p"])} Eigenschaften, {len(rules["m"])} Mastery')
    print(f'START_EQUIP: {len(se["cls"])} Klassen, {len(se["bg"])} Backgrounds (ohne Ausrüstung: {", ".join(ohne) or "keine"}), '
          f'{len(need)} verschiedene Gegenstände/Gruppen ({len(J(se)) // 1024} KB)')
    for w in WARN: print('  KORREKTUR', w)
    s = open(html, encoding='utf-8').read()
    m = re.search(r'// ITEM_DATA-START.*?// ITEM_DATA-END\n', s, re.S)
    if m:
        neu = s[:m.start()] + block + s[m.end():]
    else:
        if s.count('// ARMOR_DATA-START') != 1: sys.exit('Anker // ARMOR_DATA-START fehlt')
        i = s.index('// ARMOR_DATA-START')
        neu = s[:i] + block + s[i:]
    print(f'Block {len(block) // 1024} KB', '– unverändert' if neu == s else '')
    if '--write' in sys.argv and neu != s:
        open(html, 'w', encoding='utf-8').write(neu)
        print('geschrieben:', html)


if __name__ == '__main__':
    main()
