#!/usr/bin/env python3
"""rebuild_diff.py — Neubauprobe: alle Konverter-Klassen mit dem aktuellen class_extract.py neu erzeugen und mit der App vergleichen (Anleitung B8).
Vorher App-Daten exportieren (seit 28.09.2026: node willow/tools/dump.js DnD_Character_App.html "{cd:CLASS_DATA,ct:CLASS_TABLES}" all.json;
  früher exp_all.js, im Arbeitsordner mit jsdom):
  const fs=require('fs'),{JSDOM,VirtualConsole}=require('jsdom');
  (async()=>{const dom=new JSDOM(fs.readFileSync('DnD_Character_App.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,virtualConsole:new VirtualConsole(),url:'http://localhost/'});
  await new Promise(r=>setTimeout(r,400));fs.writeFileSync('all.json',dom.window.eval('JSON.stringify({cd:CLASS_DATA,ct:CLASS_TABLES})'));process.exit(0)})();
Dann: python3 rebuild_diff.py  → „SUMME 0" = keine eingepflegte Klasse ändert sich.
Quellen in src/: class-<k>.json aller Klassen der Liste unten, optionalfeatures.json, feats.json, items.json.
Configs: <k>_config.py in tools/ (neben diesem Skript, seit 28.09.2026) (optional je Klasse). Liegt sie vor, werden 'feature_tags' angewandt und die Tracker
  (abilities: id, name, tag, icon, uses, restore, desc, minLvl, conc; seit 27.09.2026 auch pool, sub, pick – alle Felder)
  mit der App verglichen. Pflicht seit 27.09.2026 für
  barbarian, rogue, warlock, wizard, bard (feature_tags) – fehlt eine davon, meldet die Probe deren Tag-Abweichungen.
Seit 27.09.2026 (Neubau Bard/Druid/Wizard) sind alle 12 Klassen in der Vollprobe; Subklassen-Keys mit Kürzel
  (Druid "Circle of Dreams (XGE)" …) werden wie beim Einbau über keep_keys zugeordnet.
"""
import json,re,math,sys,os,runpy
T=os.path.dirname(os.path.abspath(__file__))  # tools/ (Konverter + Configs)
sys.path.insert(0,T)
from class_extract import extract, clean
from build_class import apply_feature_tags, build_trackers, keep_keys  # gleiche Logik wie beim Einbau
A=json.load(open('all.json'))
optf=json.load(open('src/optionalfeatures.json'))['optionalfeature']
feats=json.load(open('src/feats.json'))['feat']; items=json.load(open('src/items.json'))['item']
def table(cls):
    extra,cols,slots=[],[],None
    for g in cls['classTableGroups']:
        if 'rowsSpellProgression' in g: slots=g['rowsSpellProgression']; continue
        for i,lab in enumerate(g['colLabels']):
            l=clean(lab); k=re.sub(r'[^a-z]','',l.split()[0].lower()); extra.append({'k':k,'l':l}); cols.append((k,[r[i] for r in g['rows']]))
    fl={}
    for ref in cls['classFeatures']:
        r=ref['classFeature'] if isinstance(ref,dict) else ref; p=r.split('|'); fl.setdefault(int(p[3]),[]).append(p[0])
    rows=[]
    for lvl in range(1,21):
        row={'lvl':lvl,'pb':math.ceil(lvl/4)+1,'f':', '.join(fl.get(lvl,[])) or '—'}
        for k,vals in cols:
            v=vals[lvl-1]
            if isinstance(v,dict) and v.get('type')=='dice': v='+'.join(f"{x['number']}d{x['faces']}" for x in v['toRoll'])
            elif isinstance(v,dict) and v.get('type')=='bonusSpeed': v=f"+{v['value']} ft." if v['value'] else 0
            elif isinstance(v,dict) and v.get('type')=='bonus': v=f"+{v['value']}" if v['value'] else 0
            row[k]=v if v not in (0,None,'') else '—'
        row['slots']=(list(slots[lvl-1])+[0]*9)[:9] if slots else [0]*9
        rows.append(row)
    return {'extra':extra,'rows':rows}
norm=lambda o: json.loads(json.dumps(o))
def table_diffs(C,cls):
    t=table(cls); ct=A['ct'].get(C); d=[]
    if ct is None: return ['table fehlt']
    if norm(t)!=norm(ct):
        for i,(r1,r2) in enumerate(zip(t['rows'],ct['rows'])):
            if r1!=r2: d.append(f'table L{i+1}: {[(k,r1.get(k),r2.get(k)) for k in set(r1)|set(r2) if r1.get(k)!=r2.get(k)]}'); break
        if t['extra']!=ct['extra']: d.append(f'table extra {t["extra"]} vs {ct["extra"]}')
    return d
tot=0
for C in ['Cleric','Fighter','Paladin','Ranger','Sorcerer','Rogue','Monk','Barbarian','Warlock','Wizard','Bard','Druid']:
    cd=A['cd'][C]; data=json.load(open(f'src/class-{C.lower()}.json'))
    cls,base,subs,srcs=extract(data,cd['subclassList'],optf,feats,items)
    cp=os.path.join(T,f'{C.lower()}_config.py')
    cfg=runpy.run_path(cp)['CONFIG'] if os.path.exists(cp) else None
    if cfg: apply_feature_tags(cfg,base,subs)
    ab=norm(keep_keys(build_trackers(cfg,base,subs),cd['subclass'])) if cfg else None
    subs=keep_keys(subs,cd['subclass'])
    diffs=[]
    if cfg:
        ca=cd.get('abilities',{})
        for g in set(ab)|set(ca):
            x,y=ab.get(g,[]),ca.get(g,[])
            if [t['id'] for t in x]!=[t['id'] for t in y]: diffs.append(f'tracker {g}: ids {[t["id"] for t in x]} vs {[t["id"] for t in y]}'); continue
            for t1,t2 in zip(x,y):
                for kk in set(t1)|set(t2):
                    if t1.get(kk)!=t2.get(kk): diffs.append(f'tracker {g}/{t1["id"]}/{kk}')
    if [(f['lvl'],f['name']) for f in base]!=[(f['lvl'],f['name']) for f in cd['base']]: diffs.append('base: Feature-Liste anders')
    else:
        for a,b in zip(base,cd['base']):
            for k in ('desc','tag'):
                if a[k]!=b[k]: diffs.append(f'base/{a["name"]}/{k}')
    for k in set(subs)|set(cd['subclass']):
        a,b=subs.get(k),cd['subclass'].get(k)
        if a is None or b is None: diffs.append(f'sub {k}: fehlt {"neu" if a is None else "alt"}'); continue
        if [(f['lvl'],f['name']) for f in a]!=[(f['lvl'],f['name']) for f in b]: diffs.append(f'sub {k}: Feature-Liste anders'); continue
        for x,y in zip(a,b):
            for kk in ('desc','tag'):
                if x[kk]!=y[kk]: diffs.append(f'sub {k}/{x["name"]}/{kk}')
    diffs+=table_diffs(C,cls)
    tot+=len(diffs)
    print(f'{C:9} {len(diffs)} Abweichungen', *diffs[:12], sep='\n   ')
print('SUMME',tot)
