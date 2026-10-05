# Paket R4 – Fotos der übrigen Tabs und Fenster in Handybreite (Skills, Items, Spell List, Feats, Background, Beasts,
# Notes, Log, ⚙, Würfel, Attribute, Level-Up, Startausrüstung), je mit geöffneter Karte.
# Aufruf aus dem Ordner über dem Klon: python3 willow/tools/design_r4_shots.py HTML OUTDIR [breite] [textgröße|alle] [design]
#   breite 430 (Standard), textgröße normal|gross (Standard)|sehrgross|alle, design leder (Standard)|klassisch
# Nur einzelne Fotos: NUR=items2,dice python3 …
# → OUTDIR/<name>_<breite>_<textgröße>.png (Viewport-Fotos, 2×); Ausgabe: Überlauf + Karten-Überstand je Foto, JS-Fehler.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shot_fonts
from playwright.sync_api import sync_playwright
html, out = sys.argv[1], sys.argv[2]
W = int(sys.argv[3]) if len(sys.argv) > 3 else 430
ZS = ['normal', 'gross', 'sehrgross'] if len(sys.argv) > 4 and sys.argv[4] == 'alle' else [sys.argv[4] if len(sys.argv) > 4 else 'gross']
DS = sys.argv[5] if len(sys.argv) > 5 else 'leder'
os.makedirs(out, exist_ok=True)
SETUP = """() => {
  document.getElementById('charName').textContent='Willow';
  const s=(id,v)=>{const e=document.getElementById(id); if(e) e.value=v;};
  s('lvl','6'); s('cls','Druid'); onClsChange();
  const sc=document.getElementById('subcls'); s('subcls',[...sc.options].find(o=>/Moon/.test(o.value))?.value||''); onSubclsChange();
  const r=document.getElementById('race'); s('race',[...r.options].find(o=>/^Elf/.test(o.value))?.value||r.options[3].value); onRaceChange();
  Object.assign(st.attrs,{STR:12,DEX:14,CON:14,INT:10,WIS:17,CHA:8}); attrRefresh();
  const it=n=>ITEM_DATA.find(x=>x.n===n), id=1000;
  const mk=(k,n,q,c)=>{const d=it(n); return {id:id+k,name:n,qty:q,wt:d&&d.w||0,cat:c,note:'',ref:d?d.n+'|'+d.s:undefined};};
  st.items=[mk(1,'Leather Armor',1,'Armor'),mk(2,'Scimitar',1,'Weapon'),mk(3,"Explorer's Pack",1,'Misc'),mk(4,'Potion of Healing',2,'Consumable')].filter(x=>x.ref||x.name);
  renderItems();
  st.savedBeasts=[BST_DATA.find(x=>x.n==='Wolf')].filter(Boolean);
}"""
OVER = """(W) => { const bad=[]; for(const e of document.querySelectorAll('body *')){const r=e.getBoundingClientRect(); if(!r.width||!r.height) continue;
  const cs=getComputedStyle(e); if(cs.visibility==='hidden'||cs.display==='none') continue;
  let sc=false; for(let p=e.parentElement;p;p=p.parentElement){const q=getComputedStyle(p); if(/(auto|scroll|hidden)/.test(q.overflowX)&&p!==document.body&&p!==document.documentElement&&!p.classList.contains('app')&&!p.classList.contains('body')){sc=true;break;}}
  if(r.right>W+0.5&&!sc) bad.push((e.id?'#'+e.id:'')+'.'+[...e.classList].join('.')+' '+e.tagName+' r='+Math.round(r.right));} return bad.slice(0,6); }"""
# (Name, JS vor dem Foto, Element zum Hinscrollen oder None = oben, Panel für den Karten-Test)
STATES = [
  ('skills', "switchTab('skills')", '#tab-skills', 'tab-skills'),
  ('skills2', "switchTab('skills')", '#skillsGrid', 'tab-skills'),
  ('items', "switchTab('ausruestung')", '#tab-ausruestung', 'tab-ausruestung'),
  ('items2', "switchTab('ausruestung');document.querySelector('#itemList .item-card .item-top').click()", '#itemList', 'tab-ausruestung'),
  ('itemadd', "switchTab('ausruestung');const i=document.getElementById('itemName');i.value='rope';itOnInput()", '.item-add-row', 'tab-ausruestung'),
  ('spelllist', "switchTab('spelllist')", '#tab-spelllist', 'tab-spelllist'),
  ('spelllist2', "switchTab('spelllist');document.querySelector('#slList .zb-card .zb-top')?.click()", '#slList', 'tab-spelllist'),
  ('feats', "switchTab('feats')", '#tab-feats', 'tab-feats'),
  ('feats2', "switchTab('feats');document.querySelector('#featList .zb-card .zb-top, #ftList .zb-card .zb-top, #tab-feats .feat-card .zb-top, #tab-feats .zb-card .zb-top')?.click()", '#tab-feats .zb-count', 'tab-feats'),
  ('background', "switchTab('hintergrund');document.querySelector('#bgList .zb-card .zb-top')?.click()", '#bgList', 'tab-hintergrund'),
  ('beasts', "switchTab('bestien')", '#tab-bestien', 'tab-bestien'),
  ('beasts2', "switchTab('bestien');document.querySelector('#tab-bestien .zb-count')&&0;const c=[...document.querySelectorAll('#tab-bestien .zb-card .zb-top, #tab-bestien .bst-card .zb-top')].pop();c&&c.click()", '#tab-bestien .zb-count', 'tab-bestien'),
  ('notes', "switchTab('notizen')", '#tab-notizen', 'tab-notizen'),
  ('log', "switchTab('log')", '#tab-log', 'tab-log'),
  ('info_equip', "switchTab('info');const b=document.getElementById('coreTraitsBody');if(b&&b.style.display==='none')document.querySelector('#coreTraitsSection .filter-toggle')?.click()", '#coreTraitsSection .se', 'tab-info'),
  ('levelup', "switchTab('zauber');const l=document.getElementById('lvl');l.value='7';l.dispatchEvent(new Event('input'));l.dispatchEvent(new Event('change'));", '#hpLvlAsk', 'tab-zauber'),
  ('settings', "openSettings()", None, None),
  ('settings2', "openSettings();const m=document.querySelector('#settingsModal > div');m&&(m.scrollTop=9999)", None, None),
  ('dice', "openDice()", None, None),
  ('attr', "openAttr('STR')", None, None),
]
errs = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for z in ZS:
        for name, js, anchor, panel in STATES:
            if os.environ.get('NUR') and name not in os.environ['NUR'].split(','): continue
            ctx = b.new_context(viewport={'width': W, 'height': 900}, device_scale_factor=2, is_mobile=True, has_touch=True)
            ctx.add_init_script(f"try{{localStorage.setItem('willow_textsize','{z}');localStorage.setItem('willow_design','{DS}')}}catch(e){{}}")
            pg = ctx.new_page(); pg.on('pageerror', lambda e, n=name: errs.append(n + ': ' + str(e)))
            pg.goto('file://' + os.path.abspath(html)); pg.wait_for_timeout(600)
            shot_fonts.apply(pg)
            pg.evaluate(SETUP)
            try:
                pg.evaluate('() => {' + js + '}')
            except Exception as e:
                errs.append(name + ': ' + str(e)[:200])
            pg.wait_for_timeout(250)
            pg.add_style_tag(content='.toast{visibility:hidden!important}')
            if anchor:
                pg.evaluate("(a) => { const e=document.querySelector(a); const y=e?e.getBoundingClientRect().top+scrollY-70:0; window.scrollTo(0, a.startsWith('#tab-')?0:Math.max(0,y)); }", anchor)
            pg.wait_for_timeout(200)
            bad = pg.evaluate(OVER, W)
            kar = pg.evaluate(shot_fonts.CARD_CHECK, panel) if panel else None
            pg.screenshot(path=f'{out}/{name}_{W}_{z}.png')
            print(f'{name}_{W}_{z}'.ljust(26), 'Überlauf', bad or '–', ' Karten', kar or '–')
            ctx.close()
    b.close()
print('JS-Fehler:', errs or '–')
