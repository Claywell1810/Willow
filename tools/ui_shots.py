# Bildschirmfotos aller Tabs in Handybreite + Überlauf-Prüfung
# Aufruf: python3 ui_shots.py HTML OUTDIR [zoom-stufe] [breite]   (zoom-stufe: normal|gross|sehrgross oder -, breite: 390 Standard, 430 = Simons Handy)
# Seit 02.10.2026 mit echten Schriften (shot_fonts.py, setup.sh fotos) und Prüfung „Karten-Überstand“ je Tab (Kind ragt über eine gerahmte Karte).
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shot_fonts   # echte Schriften + Karten-Überstand (02.10.2026)
from playwright.sync_api import sync_playwright
html, out = sys.argv[1], sys.argv[2]
zoom = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != '-' else None
W = int(sys.argv[4]) if len(sys.argv) > 4 else 390   # Breite in px: 390 (iPhone 12–15), 430 (Pro Max/Plus = Simons Handy), 375 (SE/mini)
os.makedirs(out, exist_ok=True)
TABS = ['info', 'skills', 'zauber', 'spelllist', 'ausruestung', 'feats', 'hintergrund', 'bestien', 'notizen', 'log']
SETUP = """
() => {
  document.getElementById('charName').textContent='Testheld';
  const set=(id,v)=>{const e=document.getElementById(id); if(e) e.value=v;};
  set('lvl','7'); set('cls','Druid'); onClsChange(); set('subcls','Circle of the Stars (XPHB)'); onSubclsChange();
  set('race', document.getElementById('race')?.options?.[3]?.value||'');
  Object.assign(st.attrs,{STR:10,DEX:14,CON:14,INT:12,WIS:18,CHA:8});
  st.weapons=[{name:'Quarterstaff',atk:'+5',dmg:'1d6+2',type:'Bludgeoning'}];
  st.slotMax=[4,3,3,1,0,0,0,0,0]; st.slotUsed=[1,0,0,0,0,0,0,0,0];
  const idx=n=>ZB_SPELLS.findIndex(s=>s.name===n);
  for(const n of ['Guidance','Healing Word','Moonbeam','Call Lightning']){const i=idx(n); if(i>=0){st.zbAdded.add(i); st.mySpells.push({name:ZB_SPELLS[i].name,grad:ZB_SPELLS[i].grad,school:ZB_SPELLS[i].school,prep:true,notes:''});}}
  st.items=[{id:1,name:'Druidic Focus',qty:1,wt:1,cat:(typeof ITEM_CATS!=='undefined'&&ITEM_CATS[0]&&(ITEM_CATS[0].id||ITEM_CATS[0].k||ITEM_CATS[0]))||'misc',note:''}];
  st.abUses={wildshape:1};
  if(typeof buildAttrs==='function') buildAttrs();
}
"""
OVER = """
(W) => {
  const bad=[];
  const inScroller=e=>{for(let p=e.parentElement;p;p=p.parentElement){const s=getComputedStyle(p);if(/(auto|scroll|hidden)/.test(s.overflowX)&&p!==document.body&&p!==document.documentElement&&!p.classList.contains('app')&&!p.classList.contains('body'))return true;}return false;};
  for(const e of document.querySelectorAll('body *')){
    const r=e.getBoundingClientRect(); if(!r.width||!r.height) continue;
    const st=getComputedStyle(e); if(st.visibility==='hidden'||st.display==='none') continue;
    if(r.right>W+0.5 && !inScroller(e)) bad.push((e.id?('#'+e.id):'')+'.'+[...e.classList].join('.')+' '+e.tagName+' r='+Math.round(r.right));
  }
  const labels=[...document.querySelectorAll('.bnav-label')].map(l=>l.getBoundingClientRect().height);
  const lh=parseFloat(getComputedStyle(document.querySelector('.bnav-label')).lineHeight)||0;
  return {sw:document.documentElement.scrollWidth, bw:document.body.scrollWidth, bad:bad.slice(0,15), nbad:bad.length, bnav:labels, bnavH:document.getElementById('bottomNav')?.getBoundingClientRect().height};
}
"""
res = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': W, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
    if zoom:
        ctx.add_init_script(f"try{{localStorage.setItem('willow_textsize','{zoom}')}}catch(e){{}}")
    pg = ctx.new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + os.path.abspath(html)); pg.wait_for_timeout(700)
    shot_fonts.apply(pg)
    pg.evaluate(SETUP)
    for t in TABS:
        pg.evaluate(f"switchTabAll('{t}')"); pg.wait_for_timeout(250)
        if t == 'zauber':
            pg.evaluate("st.abGrpClosed=st.abGrpClosed||{};st.abGrpClosed.stats=false;buildAbilities();const c=document.querySelector('#abList .ab-card .ab-top'); if(c) c.click();")
        if t == 'spelllist':
            pg.evaluate("const c=document.querySelector('#slList .zb-card .zb-top'); if(c) c.click();")
        pg.evaluate('window.scrollTo(0,0)'); pg.wait_for_timeout(150)
        res[t] = pg.evaluate(OVER, W)
        res[t]['karten'] = pg.evaluate(shot_fonts.CARD_CHECK, 'tab-' + t)
        if t == 'zauber':  # untere Leiste sichtbar (wird für die Ganzseiten-Fotos ausgeblendet; vor R2 fehlte sie deshalb in nav.png)
            pg.add_style_tag(content='.bottom-nav{visibility:visible!important}'); pg.screenshot(path=f'{out}/nav.png')
        pg.add_style_tag(content='.bottom-nav,.dice-fab,.toast{visibility:hidden!important}')
        h = pg.evaluate('document.documentElement.scrollHeight')
        pg.screenshot(path=f'{out}/{t}.png', full_page=True, clip={'x': 0, 'y': 0, 'width': W, 'height': min(h, 1700)})
        if t == 'zauber':  # Class Features und Zauberplätze extra
            y = pg.evaluate("document.getElementById('abilitiesSection').getBoundingClientRect().top+scrollY")
            pg.screenshot(path=f'{out}/zauber2.png', full_page=True, clip={'x': 0, 'y': y, 'width': W, 'height': min(h - y, 1500)})
    pg.add_style_tag(content='.bottom-nav,.dice-fab{visibility:visible!important}')
    pg.evaluate('openSettings()'); pg.wait_for_timeout(250)
    res['settings'] = pg.evaluate(OVER, W)
    pg.screenshot(path=f'{out}/settings.png')
    res['errs'] = errs
    b.close()
json.dump(res, open(f'{out}/check.json', 'w'), indent=1)
for k, v in res.items():
    if k == 'errs': print('JS-Fehler:', v); continue
    print(k.ljust(12), 'scrollW', v['sw'], v['bw'], 'überlauf', v['nbad'], v['bad'][:4], 'bnav', [round(x) for x in v['bnav']], round(v['bnavH'] or 0), ('Karten-Überstand ' + str(v['karten'])) if v.get('karten') else '')
