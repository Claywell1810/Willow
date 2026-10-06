# Paket R5 – Fotos der ganzen App in einem Modus (Pergament prüfen): Kopf/Info, Actions (HP, Waffen, Features), alle Tabs,
# More, Charakterliste, Suche, ⚙ (Mode-Zeile), Würfel, Attribute, Level-Up – je mit geöffneter Karte.
# Aufruf aus dem Ordner über dem Klon: python3 willow/tools/design_r5_shots.py HTML OUTDIR [breite] [textgröße|alle] [mode]
#   breite 430 (Standard), textgröße normal|gross (Standard)|sehrgross|alle, mode light (Standard)|dark|auto (= System hell)
# Nur einzelne Fotos: NUR=kopf,actions python3 …
# → OUTDIR/<name>_<breite>_<textgröße>.png (Viewport-Fotos, 2×); Ausgabe: Überlauf + Karten-Überstand je Foto, data-mode, JS-Fehler.
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shot_fonts
from playwright.sync_api import sync_playwright
html, out = sys.argv[1], sys.argv[2]
W = int(sys.argv[3]) if len(sys.argv) > 3 else 430
ZS = ['normal', 'gross', 'sehrgross'] if len(sys.argv) > 4 and sys.argv[4] == 'alle' else [sys.argv[4] if len(sys.argv) > 4 else 'gross']
MODE = sys.argv[5] if len(sys.argv) > 5 else 'light'
os.makedirs(out, exist_ok=True)
SETUP = """() => {
  document.getElementById('charName').textContent='Willow';
  const s=(id,v)=>{const e=document.getElementById(id); if(e) e.value=v;};
  s('lvl','6'); s('cls','Druid'); onClsChange();
  const sc=document.getElementById('subcls'); s('subcls',[...sc.options].find(o=>/Moon/.test(o.value))?.value||''); onSubclsChange();
  const r=document.getElementById('race'); s('race',[...r.options].find(o=>/^Elf/.test(o.value))?.value||r.options[3].value); onRaceChange();
  Object.assign(st.attrs,{STR:12,DEX:14,CON:14,INT:10,WIS:17,CHA:8}); attrRefresh();
  st.hpAsk=[]; hpSync(); st.hpC=Math.round(hpMaxVal()*0.62); document.getElementById('hpC').textContent=st.hpC;
  document.getElementById('hpT').value=5; updBar();
  const it=n=>ITEM_DATA.find(x=>x.n===n);
  const mk=(k,n,q,c)=>{const d=it(n); return {id:1000+k,name:n,qty:q,wt:d&&d.w||0,cat:c,note:'',ref:d?d.n+'|'+d.s:undefined};};
  st.items=[mk(1,'Leather Armor',1,'Armor'),mk(2,'Scimitar',1,'Weapon'),mk(3,"Explorer's Pack",1,'Misc'),mk(4,'Potion of Healing',2,'Consumable')];
  const ms=it('Scimitar');
  st.weapons=[{name:'Scimitar',atk:'',dmg:'',type:'',ref:ms.n+'|'+ms.s,iid:1002},{name:'Produce Flame',atk:'+6',dmg:'1d8',type:'Fire'}];
  const now=Date.now();
  st.notes=[{id:'nt1',t:'Fire giant camp',x:'North of the river, three days on foot. The jarl wants the ember stone back.',c:['Places','Quests'],d:now-864e5*3,u:now-3600e3},
            {id:'nt2',t:'Aramil',x:'Elf bard in Neverwinter, owes us a favor.',c:['NPCs'],d:now-864e5*5,u:now-864e5*2}];
  st.savedBeasts=[BST_DATA.find(x=>x.n==='Wolf')].filter(Boolean);
  renderItems(); buildWeapons();
  try{buildNotes&&buildNotes()}catch(e){}
}"""
OVER = """(W) => { const bad=[]; for(const e of document.querySelectorAll('body *')){const r=e.getBoundingClientRect(); if(!r.width||!r.height) continue;
  const cs=getComputedStyle(e); if(cs.visibility==='hidden'||cs.display==='none') continue;
  let sc=false; for(let p=e.parentElement;p;p=p.parentElement){const q=getComputedStyle(p); if(/(auto|scroll|hidden)/.test(q.overflowX)&&p!==document.body&&p!==document.documentElement&&!p.classList.contains('app')&&!p.classList.contains('body')){sc=true;break;}}
  if(r.right>W+0.5&&!sc) bad.push((e.id?'#'+e.id:'')+'.'+[...e.classList].join('.')+' '+e.tagName+' r='+Math.round(r.right));} return bad.slice(0,6); }"""
Q = "const i=document.getElementById('webSearchIn');i.value=%r;onSearch('webSearchIn');srRender();"
# (Name, JS vor dem Foto, Element zum Hinscrollen oder None = oben, Panel für den Karten-Test)
STATES = [
  ('kopf', "switchTab('info')", None, 'tab-info'),
  ('info2', "switchTab('info')", '#coreTraitsSection', 'tab-info'),
  ('actions', "switchTab('zauber')", None, 'tab-zauber'),
  ('actions2', "switchTab('zauber');wpnEdit(1)", '#weaponList', 'tab-zauber'),
  ('actions3', "switchTab('zauber')", '#abilityList, #classFeatures, .ab-card', 'tab-zauber'),
  ('skills', "switchTab('skills')", '#skillsGrid', 'tab-skills'),
  ('items', "switchTab('ausruestung');document.querySelector('#itemList .item-card .item-top').click()", '#itemList', 'tab-ausruestung'),
  ('spelllist', "switchTab('spelllist');document.querySelector('#slList .zb-card .zb-top')?.click()", '#slList', 'tab-spelllist'),
  ('feats', "switchTab('feats')", '#tab-feats', 'tab-feats'),
  ('background', "switchTab('hintergrund');document.querySelector('#bgList .zb-card .zb-top')?.click()", '#bgList', 'tab-hintergrund'),
  ('beasts', "switchTab('bestien');const c=[...document.querySelectorAll('#tab-bestien .zb-card .zb-top')].pop();c&&c.click()", '#tab-bestien .zb-count', 'tab-bestien'),
  ('notes', "switchTab('notizen')", '#tab-notizen', 'tab-notizen'),
  ('log', "switchTab('log')", '#tab-log', 'tab-log'),
  ('more', "toggleMore()", None, None),
  ('charlist', "openCharList()", None, None),
  ('search', "localStorage.setItem('willow_search_mode','app');openWebSearch();" + Q % 'fire', None, None),
  ('settings', "openSettings()", None, None),
  ('settings2', "openSettings();const m=document.querySelector('#settingsColorPanels');m&&m.scrollIntoView()", None, None),
  ('dice', "openDice()", None, None),
  ('attr', "openAttr('WIS')", None, None),
  ('spells', "switchTab('zauber')", '#spSlots, #mySpells', 'tab-zauber'),
  ('levelup', "switchTab('zauber');const l=document.getElementById('lvl');l.value='7';l.dispatchEvent(new Event('input'));l.dispatchEvent(new Event('change'));", '#hpLvlAsk', 'tab-zauber'),
]
errs = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for z in ZS:
        for name, js, anchor, panel in STATES:
            if os.environ.get('NUR') and name not in os.environ['NUR'].split(','): continue
            ctx = b.new_context(viewport={'width': W, 'height': 900}, device_scale_factor=2, is_mobile=True, has_touch=True,
                                color_scheme='light' if MODE in ('light', 'auto') else 'dark')
            ctx.add_init_script(f"try{{localStorage.setItem('willow_textsize','{z}');localStorage.setItem('willow_mode','{MODE}')}}catch(e){{}}")
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
            md = pg.evaluate("() => document.documentElement.dataset.mode")
            pg.screenshot(path=f'{out}/{name}_{W}_{z}.png')
            print(f'{name}_{W}_{z}'.ljust(26), md, 'Überlauf', bad or '–', ' Karten', kar or '–')
            ctx.close()
    b.close()
print('JS-Fehler:', errs or '–')
