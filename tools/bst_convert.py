# bst_convert.py – 5e.tools-Monster (bestiary-*.json) -> Stat-Block-Eintrag der App (BST_DATA / SPELL_STATBLOCKS)
# Aufruf:
#   python3 bst_convert.py bst DnD_Character_App.html src [--write]   # BST_DATA neu aus bestiary-xmm.json (Namen/Reihenfolge/type bleiben)
#   python3 bst_convert.py spells DnD_Character_App.html src [--write] # SPELL_STATBLOCKS aus {@creature}-Verweisen der Zauber
#   python3 bst_convert.py features DnD_Character_App.html src [--write] # FEATURE_STATBLOCKS aus der Liste FEATURES (Paket A2)
# Braucht in src/: bestiary-xmm.json, fluff-bestiary-xmm.json (bst); zusätzlich spells-*.json + bestiary-<quelle>.json (spells)
# Unbekannte Tags/Formen -> Fehler (Konverter erweitern, nicht raten).
import json, re, sys, os

ABIL = ['str', 'dex', 'con', 'int', 'wis', 'cha']
ABIL_LONG = {'str': 'Strength', 'dex': 'Dexterity', 'con': 'Constitution', 'int': 'Intelligence', 'wis': 'Wisdom', 'cha': 'Charisma'}
SIZE = {'T': 'Tiny', 'S': 'Small', 'M': 'Medium', 'L': 'Large', 'H': 'Huge', 'G': 'Gargantuan'}
AL = {'L': 'Lawful', 'N': 'Neutral', 'C': 'Chaotic', 'G': 'Good', 'E': 'Evil', 'U': 'Unaligned', 'A': 'Any Alignment'}
ATKR = {'m': 'Melee Attack Roll:', 'r': 'Ranged Attack Roll:', 'm,r': 'Melee or Ranged Attack Roll:'}
ATK14 = {'mw': 'Melee Weapon Attack:', 'rw': 'Ranged Weapon Attack:', 'ms': 'Melee Spell Attack:', 'rs': 'Ranged Spell Attack:',
         'mw,rw': 'Melee or Ranged Weapon Attack:', 'ms,rs': 'Melee or Ranged Spell Attack:',
         'm': 'Melee Attack:', 'r': 'Ranged Attack:', 'm,r': 'Melee or Ranged Attack:'}
ORD = {'1': 'First', '2': 'Second', '3': 'Third'}
# Tags, deren Anzeige = 3. Teil, sonst 1. Teil (5e.tools-Renderer)
PLAIN = {'spell', 'condition', 'variantrule', 'action', 'status', 'skill', 'sense', 'item', 'creature', 'damage', 'dice',
         'hazard', 'book', 'quickref', 'filter', 'i', 'b', 'u', 'note', 'language', 'disease', 'deity', 'classFeature',
         'class', 'race', 'feat', 'background', 'table', 'adventure', 'itemProperty', 'itemMastery', 'boon', 'reward',
         'optfeature', 'subclass', 'cult', 'vehicle', 'object', 'trap', 'psionic', 'charoption', 'area'}


def tag(m):
    t, a = m.group(1), (m.group(2) or '').strip()
    if t == 'atkr': return ATKR[a]
    if t == 'atk': return ATK14[a]
    if t == 'hit': a = a.replace('summonSpellLevel', "the spell's level"); return ('+' if not a.startswith('-') else '') + a
    if t == 'hitYourSpellAttack': return a or 'Bonus equals your spell attack modifier'
    if t == 'dcYourSpellSave': return a or 'your spell save DC'   # 5e.tools-Renderer (Eldritch Cannon, Paket M)
    if t == 'h': return 'Hit: '
    if t == 'm': return 'Miss: '
    if t == 'hom': return 'Hit or Miss: '
    if t == 'dc': return 'DC ' + a.split('|')[0]
    if t == 'actSave': return ABIL_LONG[a] + ' Saving Throw:'
    if t == 'actSaveFail': return (ORD[a] + ' Failure:') if a else 'Failure:'
    if t == 'actSaveSuccess': return 'Success:'
    if t == 'actSaveSuccessOrFail': return 'Failure or Success:'
    if t == 'actTrigger': return 'Trigger:'
    if t == 'actResponse': return 'Response:' if not a else 'Response—'
    if t == 'recharge': return '(Recharge ' + (a + '–6' if a and a != '6' else '6') + ')'
    if t == 'chance': p = a.split('|'); return p[2] if len(p) > 2 and p[2] else p[0] + ' percent'
    if t in ('scaledice', 'scaledamage'): p = a.split('|'); return p[2] if len(p) > 2 else p[0]
    if t in ('damage', 'dice', 'hit'):   # Beschwörungs-Platzhalter (5e.tools-Renderer)
        a = a.replace('summonSpellLevel', "the spell's level")
    if t in PLAIN:
        p = a.split('|')
        return p[2] if len(p) > 2 and p[2] else p[0]
    raise KeyError('Unbekannter Tag: {@' + t + ' ' + a + '}')


def clean(s):
    prev = None
    while prev != s:   # verschachtelte Tags von innen nach außen
        prev = s
        s = re.sub(r'\{@(\w+)(?: ([^{}]*))?\}', tag, s)
    if '{@' in s: raise ValueError('Tag-Rest: ' + s[:120])
    return re.sub(r'  +', ' ', s).strip()


def ent(e, out):
    """entries -> Zeilen (Absätze), Listen als '• '"""
    if isinstance(e, str): out.append(clean(e)); return
    ty = e.get('type', 'entries')
    if ty in ('entries', 'section', 'inset'):
        sub = []
        for x in e.get('entries', []): ent(x, sub)
        if e.get('name') and sub: sub[0] = clean(e['name']) + '. ' + sub[0]
        out.extend(sub)
    elif ty == 'list':
        for it in e['items']:
            if isinstance(it, str): out.append('• ' + clean(it))
            elif it.get('type') == 'item':
                body = []
                for x in ([it['entry']] if 'entry' in it else it.get('entries', [])): ent(x, body)
                nm = clean(it['name'])
                out.append('• ' + nm + ('' if nm.endswith((':', '.')) else '.') + ' ' + ' '.join(body))
            else:
                sub = []; ent(it, sub); out.extend('• ' + x for x in sub)
    elif ty == 'table':
        if e.get('caption'): out.append(clean(e['caption']) + ':')
        out.append(' | '.join(clean(str(c)) for c in e['colLabels']))
        for r in e['rows']: out.append('• ' + ' | '.join(clean(c if isinstance(c, str) else json.dumps(c)) for c in r))
    else:
        raise KeyError('Unbekannter entry-Typ: ' + ty)


def block(items):
    res = []
    for it in items or []:
        lines = []
        for x in it.get('entries', []): ent(x, lines)
        res.append(clean(it['name']) + ': ' + '\n'.join(lines) if it.get('name') else '\n'.join(lines))
    return res


def spellcasting(sc):
    """2024-Spellcasting (displayAs action/bonus/reaction/trait) -> ein Eintrag 'Name: Text'"""
    lines = []
    for x in sc.get('headerEntries', []): ent(x, lines)
    sp = lambda L: ', '.join(clean(s) for s in L)
    hid = set(sc.get('hidden') or [])
    for k in sc:
        if k in ('will', 'daily', 'spells', 'recharge', 'restLong', 'rest', 'legendary', 'weekly', 'charges') and k not in hid and k not in ('will', 'daily', 'spells'):
            raise KeyError('Spellcasting-Feld nicht unterstützt: ' + k + ' (' + sc['name'] + ')')
    sc = {k: v for k, v in sc.items() if k not in hid}
    if sc.get('will'): lines.append('• At Will: ' + sp(sc['will']))
    for k, v in (sc.get('daily') or {}).items():
        lines.append('• ' + k.rstrip('e') + '/Day' + (' Each' if k.endswith('e') else '') + ': ' + sp(v))
    for k, v in (sc.get('spells') or {}).items():   # 2014-Form (Slots)
        lab = 'Cantrips (at will)' if k == '0' else f'Level {k}' + (f" ({v['slots']} slots)" if v.get('slots') else '')
        lines.append('• ' + lab + ': ' + sp(v['spells']))
    for x in sc.get('footerEntries', []): ent(x, lines)
    return clean(sc['name']) + ': ' + '\n'.join(lines)


def speed(s):
    if isinstance(s, (int, str)): return f'{s} ft.'
    out = []
    for k in ('walk', 'burrow', 'climb', 'fly', 'swim'):
        v = s.get(k)
        if v is None: continue
        if isinstance(v, dict): v = f"{v['number']} ft. {v['condition']}".strip()
        elif v is True: v = 'equal to walking speed'
        else: v = f'{v} ft.'
        if k == 'fly' and s.get('canHover') and '(hover)' not in v: v += ' (hover)'
        out.append(v if k == 'walk' else k + ' ' + v)
    if s.get('choose'):
        c = s['choose']; out.append(' or '.join(c['from']) + f" {c['amount']} ft." + (' ' + c['note'] if c.get('note') else ''))
    for k in s:
        if k not in ('walk', 'burrow', 'climb', 'fly', 'swim', 'canHover', 'choose', 'alternate'): raise KeyError('Speed: ' + k)
    return ', '.join(out)


def dmglist(L, key):
    out = []
    for x in L or []:
        if isinstance(x, str): out.append(x.capitalize() if x.islower() else x)
        elif 'special' in x: out.append(clean(x['special']))
        else:
            inner = dmglist(x[key], key)
            s = (clean(x['preNote']) + ' ' if x.get('preNote') else '') + inner + (' ' + clean(x['note']) if x.get('note') else '')
            out.append(s)
    return ', '.join(out)


def mod(v): return (v - 10) // 2


def pb(cr):
    n = eval(cr) if '/' in str(cr) else float(cr)
    return 2 if n < 5 else 3 if n < 9 else 4 if n < 13 else 5 if n < 17 else 6 if n < 21 else 7 if n < 25 else 8 if n < 29 else 9


def typetxt(m):
    t = m['type']
    if isinstance(t, str): return t.capitalize()
    base = t['type']
    base = ' or '.join(x.capitalize() for x in base['choose']) if isinstance(base, dict) else base.capitalize()
    if t.get('swarmSize'): base = 'Swarm of ' + SIZE[t['swarmSize']] + ' ' + base + 's'
    if t.get('tags'): base += ' (' + ', '.join((x if isinstance(x, str) else x['tag']).title() for x in t['tags']) + ')'
    return base


def aligntxt(m):
    a = m.get('alignment')
    if not a: return ''
    if all(isinstance(x, str) for x in a):
        s = ' '.join(AL[x] for x in a) if a != ['N'] else 'Neutral'
    else:
        s = ' or '.join(' '.join(AL[y] for y in x['alignment']) for x in a)   # {alignment:[...]} Varianten
    return (m.get('alignmentPrefix') or '') + s


def acs(m):
    out = []
    for x in m['ac']:
        if isinstance(x, int): out.append(str(x))
        elif 'special' in x: out.append(clean(x['special']))
        else: out.append(str(x['ac']) + (' (' + ', '.join(clean(f) for f in x['from']) + ')' if x.get('from') else '') + (' ' + clean(x['condition']) if x.get('condition') else ''))
    return ', '.join(out)


def convert(m, fluff=None, keep_type=None):
    """Monster -> Eintrag. Alte Felder (n,type,size,cr,ac,hp,spd,str…cha,skills,sens,actions,traits,fluff) wie bisher, neue nur wenn gefüllt."""
    cr = m.get('cr', '')
    cr = cr['cr'] if isinstance(cr, dict) else cr
    hp = m['hp']
    hp = f"{hp['average']} ({hp['formula']})" if 'average' in hp else clean(hp['special'])
    senses = [clean(s) for s in (m.get('senses') or [])] + ([f"Passive Perception {m['passive']}"] if m.get('passive') is not None else [])
    t = m['type']; tb = t if isinstance(t, str) else t['type']
    e = {'n': m['name'], 'type': keep_type or (tb if isinstance(tb, str) else tb['choose'][0]),
         'size': '/'.join(m['size']), 'cr': str(cr), 'ac': acs(m), 'hp': hp, 'spd': speed(m['speed'])}
    for a in ABIL: e[a] = m[a]
    e['skills'] = ', '.join(k.title() + ' ' + v for k, v in (m.get('skill') or {}).items() if k != 'other')
    e['sens'] = ', '.join(senses)
    legsc = []
    trait, action, bonus, react = block(m.get('trait')), block(m.get('action')), block(m.get('bonus')), block(m.get('reaction'))
    for sc in m.get('spellcasting') or []:
        da = sc.get('displayAs', 'trait')
        if da == 'legendary': legsc.append(spellcasting(sc)); continue
        {'action': action, 'bonus': bonus, 'reaction': react, 'trait': trait}[da].append(spellcasting(sc))
    e['actions'] = action
    e['traits'] = trait
    e['fluff'] = fluff or ''
    # neue Felder (seit Paket A, 27.09.2026)
    e['tt'] = typetxt(m)
    al = aligntxt(m)
    if al: e['al'] = al
    if m.get('initiative') is not None or cr != '':
        ini = m.get('initiative') or {}
        v = ini['initiative'] if isinstance(ini, dict) and 'initiative' in ini else mod(m['dex']) + (ini.get('proficiency', 0) * pb(cr) if isinstance(ini, dict) and cr not in ('', None) else 0)
        if cr not in ('', None) or m.get('initiative') is not None: e['init'] = v
    if m.get('save'): e['saves'] = {k: v for k, v in m['save'].items()}
    for k, f in (('res', 'resist'), ('vuln', 'vulnerable')):
        if m.get(f): e[k] = dmglist(m[f], f)
    imm = [dmglist(m.get('immune'), 'immune'), dmglist(m.get('conditionImmune'), 'conditionImmune')]
    imm = '; '.join(x for x in imm if x)
    if imm: e['imm'] = imm
    if m.get('gear'): e['gear'] = ', '.join(clean('{@item ' + g + '}') if isinstance(g, str) else clean('{@item ' + g['item'] + '}') + (f" ({g['quantity']})" if g.get('quantity') else '') for g in m['gear'])
    if m.get('languages'): e['lang'] = ', '.join(clean(x) for x in m['languages'])
    if bonus: e['bonus'] = bonus
    if react: e['react'] = react
    if m.get('legendary'):
        n = m.get('legendaryActions', 3); lair = m.get('legendaryActionsLair')
        sn = m.get('shortName') or m['name'].lower()
        sn = sn if sn is True or not isinstance(sn, str) else sn
        sn = ('the ' + m['name'].lower()) if sn is True else (sn if m.get('isNamedCreature') else 'the ' + sn.lower())
        head = f'Legendary Action Uses: {n}' + (f' ({lair} in Lair)' if lair else '') + f'. Immediately after another creature’s turn, {sn} can expend a use to take one of the following actions. {sn[0].upper() + sn[1:]} regains all expended uses at the start of each of its turns.'
        if m.get('legendaryHeader'):
            h = []; [ent(x, h) for x in m['legendaryHeader']]; head = '\n'.join(h)
        e['legend'] = [head] + block(m['legendary']) + legsc
    if m.get('cr') and isinstance(m['cr'], dict) and m['cr'].get('lair'): e['crl'] = m['cr']['lair']
    return e


def convert_object(o):
    """Objekt aus objects.json (Eldritch Cannon, Paket M 03.10.2026) -> Eintrag wie convert(), ohne Attribute/CR/Speed.
    Feld obj:1 → sbHtml lässt die Attributszeile weg."""
    ac = o['ac']; ac = str(ac) if isinstance(ac, int) else acs({'ac': ac if isinstance(ac, list) else [ac]})
    hp = o['hp']; hp = str(hp) if isinstance(hp, int) else (f"{hp['average']} ({hp['formula']})" if 'average' in hp else clean(hp['special']))
    sz = o.get('size', []); sz = sz if isinstance(sz, list) else [sz]
    e = {'n': o['name'], 'type': 'object', 'size': '/'.join(sz), 'cr': '', 'ac': ac, 'hp': hp, 'spd': speed(o['speed']) if o.get('speed') else '',
         'obj': 1, 'tt': 'Object', 'actions': block(o.get('actionEntries')), 'traits': [], 'fluff': ''}
    imm = [dmglist(o.get('immune'), 'immune'), dmglist(o.get('conditionImmune'), 'conditionImmune')]
    imm = '; '.join(x for x in imm if x)
    if imm: e['imm'] = imm
    for k, f in (('res', 'resist'), ('vuln', 'vulnerable')):
        if o.get(f): e[k] = dmglist(o[f], f)
    return e


def load(src, *names):
    M = {}
    for n in names:
        p = os.path.join(src, n)
        if os.path.exists(p):
            for m in json.load(open(p, encoding='utf-8')).get('monster', []): M[(m['name'].lower(), m['source'])] = m
    return M


def resolve_copy(m, M):
    if '_copy' not in m: return m
    c = m['_copy']; base = resolve_copy(M[(c['name'].lower(), c['source'])], M)
    r = dict(base); r.update({k: v for k, v in m.items() if k != '_copy'})
    if c.get('_mod'): raise KeyError('_copy mit _mod nicht unterstützt: ' + m['name'])
    return r


def js_line(name, data):
    return f'const {name}=' + json.dumps(data, ensure_ascii=False) + ';'


def fluff_tag(F, name):
    f = F.get(name)
    if not f or 'entries' not in f: return ''
    for sec in f['entries']:
        for x in (sec.get('entries', []) if isinstance(sec, dict) else []):
            if isinstance(x, str) and x.startswith('{@i ') and x.endswith('}'): return clean(x)
    return ''


def replace_line(html, prefix, newline):
    i = html.index(prefix); assert html.count(prefix) == 1, prefix
    j = html.index('\n', i)
    return html[:i] + newline + html[j:]


def cmd_bst(html_p, src, write):
    html = open(html_p, encoding='utf-8').read()
    import subprocess
    old = dump(html_p, 'BST_DATA')
    M = load(src, 'bestiary-xmm.json')
    F = {f['name']: f for f in json.load(open(os.path.join(src, 'fluff-bestiary-xmm.json'), encoding='utf-8'))['monsterFluff']}
    new = []
    for b in old:
        m = resolve_copy(M[(b['n'].lower(), 'XMM')], M)
        new.append(convert(m, fluff_tag(F, b['n']), keep_type=b['type']))
    diff = sum(1 for a, b in zip(old, new) for k in a if a[k] != b.get(k))
    print(f'BST_DATA: {len(new)} Einträge, {diff} geänderte alte Felder, Fluff {sum(1 for x in new if x["fluff"])}')
    for a, b in zip(old, new):
        if a['fluff'] != b['fluff']: print('  Fluff abweichend:', a['n'], repr(a['fluff']), '->', repr(b['fluff']))
    rest = [x['n'] for x in new if '{@' in json.dumps(x)]
    assert not rest, rest
    if write:
        html = replace_line(html, 'const BST_DATA=', js_line('BST_DATA', new))
        open(html_p, 'w', encoding='utf-8').write(html); print('geschrieben')
    return new


# node-Einzeiler: Datenblock aus der App (jsdom) als JSON
DUMP = ("const fs=require('fs');const {JSDOM,VirtualConsole}=require('jsdom');"
        "const d=new JSDOM(fs.readFileSync(process.argv[1],'utf8'),{runScripts:'dangerously',pretendToBeVisual:true,virtualConsole:new VirtualConsole(),url:'http://localhost/'});"
        "setTimeout(()=>{fs.writeFileSync(process.argv[3],d.window.eval('JSON.stringify('+process.argv[2]+')'));process.exit(0)},500);")


def dump(html_p, expr):
    import subprocess, tempfile
    f = tempfile.mktemp(suffix='.json')
    subprocess.check_call(['node', '-e', DUMP, html_p, expr, f])
    return json.load(open(f, encoding='utf-8'))


def cmd_spells(html_p, src, write):
    import subprocess, glob
    zb = dump(html_p, 'ZB_SPELLS.map(s=>({name:s.name,src:s.src}))')
    SRC = {"PHB'24": 'XPHB'}
    S = {}
    for p in glob.glob(os.path.join(src, 'spells-*.json')):
        for s in json.load(open(p, encoding='utf-8'))['spell']: S[(s['name'], s['source'])] = s
    M = load(src, *[os.path.basename(p) for p in glob.glob(os.path.join(src, 'bestiary-*.json'))])
    out = {}
    # Zauber, deren {@creature}-Verweise nur Beispiele einer freien Wahl sind (Liste unvollständig) -> kein Stat-Block
    EXAMPLES = {'Summon Lesser Demons', 'Summon Greater Demon', 'Infernal Calling'}
    for z in zb:
        if z['name'] in EXAMPLES: continue
        s = S.get((z['name'], SRC.get(z['src'], z['src'])))
        if not s: continue
        txt = json.dumps(s.get('entries', []) + s.get('entriesHigherLevel', []))
        refs = []
        for r in re.findall(r'\{@creature ([^}]*)\}', txt):
            p = r.split('|'); key = (p[0].lower(), (p[1] if len(p) > 1 and p[1] else 'MM').upper())
            if key not in refs: refs.append(key)
        if not refs: continue
        blocks = []
        for k in refs:
            if k not in M: print('  FEHLT im Bestiarium:', z['name'], k); continue
            blocks.append(dict(convert(resolve_copy(M[k], M)), src=k[1]))
        if blocks: out[z['name']] = blocks
    print(f'SPELL_STATBLOCKS: {len(out)} Zauber, {sum(len(v) for v in out.values())} Stat-Blöcke')
    for k, v in out.items(): print('  ', k, '->', ', '.join(b['n'] + ' (' + b['src'] + ')' for b in v))
    if write:
        html = open(html_p, encoding='utf-8').read()
        html = replace_line(html, 'const SPELL_STATBLOCKS=', js_line('SPELL_STATBLOCKS', out))
        open(html_p, 'w', encoding='utf-8').write(html); print('geschrieben')
    return out

# ── Klassen-Features mit Kreatur (Paket A2, 03.10.2026) ──
# Kuratierte Liste: Schlüssel "Klasse|Gruppe|Feature" (Gruppe = 'base' oder Subklassen-Key, B3, wie FEATURE_PICKS).
# Einträge: "Name|Quelle" = Kreatur aus dem Bestiarium; "@Zauber" = Stat-Blöcke dieses Zaubers aus SPELL_STATBLOCKS (zur Laufzeit).
# Optional "via": Beschriftung der Gruppe (z. B. Invocation-Name). Beleg: der Kreatur-/Zaubername muss im Feature-Text der App stehen.
FEATURES = {
    'Ranger|Beast Master|Primal Companion': ['Beast of the Land|XPHB', 'Beast of the Sea|XPHB', 'Beast of the Sky|XPHB'],
    'Ranger|Drakewarden|Drake Companion': ['Drake Companion|FTD'],
    'Ranger|Fey Wanderer|Fey Reinforcements': ['@Summon Fey'],
    'Druid|Circle of Wildfire (TCE)|Summon Wildfire Spirit': ['Wildfire Spirit|TCE'],
    'Druid|Circle of Spores (TCE)|Fungal Infestation': ['Zombie|MM'],
    'Druid|base|Wild Companion': ['@Find Familiar'],
    'Bard|College of Creation|Animating Performance': ['Dancing Item|TCE'],
    'Paladin|base|Faithful Steed': ['@Find Steed'],
    'Sorcerer|Shadow Magic|Beasts of Ill Omen': ['@Summon Beast'],
    'Sorcerer|Draconic Sorcery|Dragon Companion': ['@Summon Dragon'],
    'Warlock|The Hexblade|Accursed Specter': ['Specter|MM'],
    'Warlock|Great Old One Patron|Create Thrall': ['@Summon Aberration'],
    'Warlock|base|Eldritch Invocation Options': [('Pact of the Chain', ['Imp|XMM', 'Pseudodragon|XMM', 'Quasit|XMM', 'Skeleton|XMM', 'Slaad Tadpole|XMM',
                                                                         'Sphinx of Wonder|XMM', 'Sprite|XMM', 'Venomous Snake|XMM']), '@Find Familiar'],
    'Wizard|School of Necromancy|Necromancy Spellbook': [('Undead Familiar', ['Skeleton|XMM', 'Zombie|XMM']), '@Find Familiar'],
    'Wizard|School of Necromancy|Undead Thralls': ['@Animate Dead'],
    'Wizard|Illusionist|Phantasmal Creatures': ['@Summon Beast', '@Summon Fey'],
    # Artificer (Paket M, 03.10.2026); "obj:Name|Quelle" = Objekt aus objects.json
    'Artificer|Battle Smith|Steel Defender': ['Steel Defender|EFA'],
    'Artificer|Artillerist|Eldritch Cannon': ['obj:Eldritch Cannon|EFA'],
    'Artificer|Reanimator|Reanimated Companion': ['Reanimated Companion|RHW'],
}
# Bewusst nicht (Prüfliste unten meldet sie als "nicht übernommen"): Beispiele/Erscheinungsbild statt Stat-Block
# (Wild Shape-Beispielformen, Wild Surge/Wild Magic Surge flumph/pixie/unicorn, Genie-Arten, Favored Enemy, Winter Walker),
# Fassungen, die die App nicht nutzt (Beast Master TCE, Hound of Ill Omen XGE, Vestige AU).


def cmd_features(html_p, src, write):
    import glob
    D = dump(html_p, '{cd:Object.fromEntries(Object.entries(CLASS_DATA).map(([c,v])=>[c,{base:v.base.map(f=>[f.name,f.desc]),'
                     'sub:Object.fromEntries(Object.entries(v.subclass).map(([k,l])=>[k,l.map(f=>[f.name,f.desc])]))}])),ss:Object.keys(SPELL_STATBLOCKS)}')
    M = load(src, *[os.path.basename(p) for p in glob.glob(os.path.join(src, 'bestiary-*.json'))])
    op = os.path.join(src, 'objects.json')
    OBJ = json.load(open(op, encoding='utf-8'))['object'] if os.path.exists(op) else []
    out, err = {}, []
    for key, items in FEATURES.items():
        c, g, n = key.split('|')
        cd = D['cd'].get(c)
        fl = cd and (cd['base'] if g == 'base' else cd['sub'].get(g))
        desc = next((d for nm, d in (fl or []) if nm == n), None)
        if desc is None: err.append('Feature fehlt in der App: ' + key); continue
        low = desc.lower(); res = []
        for it in items:
            via, L = it if isinstance(it, tuple) else (None, [it])
            if via and via.lower() not in low: err.append(f'{key}: "{via}" nicht im Text')
            for x in L:
                if x.startswith('@'):
                    if x[1:] not in D['ss']: err.append(f'{key}: Zauber ohne Stat-Block {x}')
                    elif x[1:].lower() not in low: err.append(f'{key}: Zauber nicht im Text {x}')
                    else: res.append({'sp': x[1:]})
                    continue
                if x.startswith('obj:'):   # Objekt aus objects.json (Paket M: Eldritch Cannon)
                    nm, q = x[4:].split('|')
                    o = next((y for y in OBJ if y['name'].lower() == nm.lower() and y['source'] == q), None)
                    if not o: err.append(f'{key}: FEHLT in objects.json {x}'); continue
                    if nm.lower() not in low: err.append(f'{key}: Objekt nicht im Text {x}')
                    res.append(dict(convert_object(o), src=q)); continue
                nm, q = x.split('|'); k = (nm.lower(), q)
                if k not in M: err.append(f'{key}: FEHLT im Bestiarium {x}'); continue
                if nm.lower() not in low: err.append(f'{key}: Kreatur nicht im Text {x}')
                e = dict(convert(resolve_copy(M[k], M)), src=q)
                if via: e['via'] = via
                res.append(e)
        out[key] = res
    # Prüfliste: {@creature}-Verweise in Klassen-Features/Invocations, die nicht übernommen sind (Hinweis, kein Fehler)
    have = {(b['n'].lower()) for v in out.values() for b in v if 'n' in b}
    for p in sorted(glob.glob(os.path.join(src, 'class-*.json'))) + [os.path.join(src, 'optionalfeatures.json')]:
        if not os.path.exists(p): continue
        J = json.load(open(p, encoding='utf-8'))
        for ft in J.get('classFeature', []) + J.get('subclassFeature', []) + J.get('optionalfeature', []):
            for r in set(re.findall(r'\{@creature ([^}|]*)', json.dumps(ft.get('entries', [])))):
                if r.lower() not in have:
                    print(f"  nicht übernommen: {ft.get('className', '')} {ft.get('subclassShortName', '')} {ft['source']} {ft['name']} -> {r}")
    if err:
        for e in err: print('FEHLER', e)
        sys.exit(1)
    print(f'FEATURE_STATBLOCKS: {len(out)} Features, {sum(1 for v in out.values() for b in v if "n" in b)} Stat-Blöcke, '
          f'{sum(1 for v in out.values() for b in v if "sp" in b)} Zauber-Verweise')
    for k, v in out.items(): print('  ', k, '->', ', '.join(b['n'] + ' (' + b['src'] + ')' if 'n' in b else '@' + b['sp'] for b in v))
    if '{@' in json.dumps(out): print('FEHLER Tag-Rest'); sys.exit(1)
    if write:
        html = open(html_p, encoding='utf-8').read()
        line = js_line('FEATURE_STATBLOCKS', out)
        if 'const FEATURE_STATBLOCKS=' in html: html = replace_line(html, 'const FEATURE_STATBLOCKS=', line)
        else:   # erstes Mal: neue Zeile direkt nach SPELL_STATBLOCKS
            i = html.index('const SPELL_STATBLOCKS='); assert html.count('const SPELL_STATBLOCKS=') == 1
            j = html.index('\n', i); html = html[:j + 1] + line + '\n' + html[j + 1:]
        open(html_p, 'w', encoding='utf-8').write(html); print('geschrieben')
    return out


if __name__ == '__main__':
    mode, html_p, src = sys.argv[1:4]
    {'bst': cmd_bst, 'spells': cmd_spells, 'features': cmd_features}[mode](html_p, src, '--write' in sys.argv)
