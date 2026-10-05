# Paket R6 – Fotos der Suche (🔍 „In App / Web“) in Handybreite: leeres Fenster, Treffer gruppiert, eine Kategorie,
# aufgeklappter Treffer (fremdes Feature, Katalog-Item), nichts gefunden, Web-Modus, Sprungziele (Spell List, Info, Notes).
# Aufruf aus dem Ordner über dem Klon: python3 willow/tools/design_r6_shots.py HTML OUTDIR [breite] [textgröße|alle] [design]
#   breite 430 (Standard), textgröße normal|gross (Standard)|sehrgross|alle, design leder (Standard)|klassisch
# Nur einzelne Fotos: NUR=all,web python3 …
# → OUTDIR/<name>_<breite>_<textgröße>.png (Viewport-Fotos, 2×); Ausgabe: Überlauf je Foto, JS-Fehler.
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
  Object.assign(st.attrs,{STR:12,DEX:14,CON:14,INT:10,WIS:17,CHA:8}); attrRefresh();
  const it=n=>ITEM_DATA.find(x=>x.n===n);
  const mk=(k,n,q,c)=>{const d=it(n); return {id:1000+k,name:n,qty:q,wt:d&&d.w||0,cat:c,note:'',ref:d?d.n+'|'+d.s:undefined};};
  st.items=[mk(1,'Leather Armor',1,'Armor'),mk(2,'Scimitar',1,'Weapon'),{id:1003,name:'Fire-scarred lantern',qty:1,wt:2,cat:'Misc',note:'From the burned temple'}];
  const now=Date.now();
  st.notes=[{id:'nt1',t:'Fire giant camp',x:'North of the river, three days on foot. The jarl wants the ember stone back.',c:['Places','Quests'],d:now-864e5*3,u:now-3600e3},
            {id:'nt2',t:'Aramil',x:'Elf bard in Neverwinter, owes us a favor.',c:['NPCs'],d:now-864e5*5,u:now-864e5*2}];
  renderItems();
  try{localStorage.setItem('willow_websearch',JSON.stringify(['Wild Shape rules','Fireball']))}catch(e){}
}"""
OVER = """(W) => { const bad=[]; for(const e of document.querySelectorAll('body *')){const r=e.getBoundingClientRect(); if(!r.width||!r.height) continue;
  const cs=getComputedStyle(e); if(cs.visibility==='hidden'||cs.display==='none') continue;
  let sc=false; for(let p=e.parentElement;p;p=p.parentElement){const q=getComputedStyle(p); if(/(auto|scroll|hidden)/.test(q.overflowX)&&p!==document.body&&p!==document.documentElement&&!p.classList.contains('app')&&!p.classList.contains('body')){sc=true;break;}}
  if(r.right>W+0.5&&!sc) bad.push((e.id?'#'+e.id:'')+'.'+[...e.classList].join('.')+' '+e.tagName+' r='+Math.round(r.right));} return bad.slice(0,6); }"""
Q = "const i=document.getElementById('webSearchIn');i.value=%r;onSearch('webSearchIn');srRender();"
TAP = "const k=_srRes.findIndex(x=>%s);if(k>=0)srTap(k);"
# (Name, JS vor dem Foto)
STATES = [
  ('empty', "localStorage.setItem('willow_search_mode','app');openWebSearch()"),
  ('all', "openWebSearch();" + Q % 'fire'),
  ('cat', "openWebSearch();" + Q % 'fire' + "srCatSet('spell')"),
  ('feature', "openWebSearch();" + Q % 'extra attack' + TAP % "x.e.k==='feature'&&x.e.cls==='Barbarian'"),
  ('item', "openWebSearch();" + Q % 'longsword' + TAP % "x.e.n==='Longsword'"),
  ('none', "openWebSearch();" + Q % 'xyzzy'),
  ('web', "localStorage.setItem('willow_search_mode','web');openWebSearch();" + Q % 'grappling rules'),
  ('go_spell', "openWebSearch();" + Q % 'fireball' + "srGo(_srRes.find(x=>x.e.n==='Fireball'))"),
  ('go_feature', "openWebSearch();" + Q % 'wild shape' + "srGo(_srRes.find(x=>x.e.n==='Wild Shape'))"),
  ('go_note', "openWebSearch();" + Q % 'jarl' + "srGo(_srRes.find(x=>x.e.k==='note'))"),
]
errs = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for z in ZS:
        for name, js in STATES:
            if os.environ.get('NUR') and name not in os.environ['NUR'].split(','): continue
            ctx = b.new_context(viewport={'width': W, 'height': 860}, device_scale_factor=2, is_mobile=True, has_touch=True)
            ctx.add_init_script(f"try{{localStorage.setItem('willow_textsize','{z}');localStorage.setItem('willow_design','{DS}')}}catch(e){{}}")
            pg = ctx.new_page(); pg.on('pageerror', lambda e, n=name: errs.append(n + ': ' + str(e)))
            pg.goto('file://' + os.path.abspath(html)); pg.wait_for_timeout(600)
            shot_fonts.apply(pg)
            pg.evaluate(SETUP)
            try:
                pg.evaluate('() => {' + js + '}')
            except Exception as e:
                errs.append(name + ': ' + str(e)[:200])
            pg.wait_for_timeout(name.startswith('go_') and 700 or 250)
            pg.add_style_tag(content='.toast{visibility:hidden!important}' + ('' if name.startswith('go_') else '.sr-hit{animation:none}'))
            if name.startswith('go_'):   # Glanz einfrieren, damit das Foto die Markierung zeigt
                pg.add_style_tag(content='.sr-hit{animation-play-state:paused!important;animation-delay:-.3s!important}')
                pg.evaluate("() => { const e=document.querySelector('.sr-hit'); if(e) window.scrollTo(0, Math.max(0, e.getBoundingClientRect().top+scrollY-70)); }")
            pg.evaluate("() => document.activeElement && document.activeElement.blur()")
            pg.wait_for_timeout(200)
            bad = pg.evaluate(OVER, W)
            pg.screenshot(path=f'{out}/{name}_{W}_{z}.png')
            print(f'{name}_{W}_{z}'.ljust(26), 'Überlauf', bad or '–')
            ctx.close()
    b.close()
print('JS-Fehler:', errs or '–')
