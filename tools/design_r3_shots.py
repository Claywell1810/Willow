# Paket R3 – Fotos Actions-Tab oben (HP-Block, Effects, Weapons) in Handybreite, alle Textgrößen
# Aufruf aus dem Ordner über dem Klon: python3 willow/tools/design_r3_shots.py HTML OUTDIR [breite …]
# → OUTDIR/<breite>_<textgröße>.png (Normal/Large/X-Large) + Klassik 430 Large; Ausgabe: Überlauf + Karten-Überstand je Foto.
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shot_fonts
from playwright.sync_api import sync_playwright
html, out = sys.argv[1], sys.argv[2]
WS = [int(x) for x in sys.argv[3:]] or [390, 430]
os.makedirs(out, exist_ok=True)
SETUP = """() => {
  document.getElementById('charName').textContent='Willow';
  const s=(id,v)=>{const e=document.getElementById(id); if(e) e.value=v;};
  s('lvl','6'); s('cls','Druid'); onClsChange();
  const sc=document.getElementById('subcls'); s('subcls',[...sc.options].find(o=>/Moon/.test(o.value))?.value||sc.options[1]?.value||''); onSubclsChange();
  const r=document.getElementById('race'); s('race',[...r.options].find(o=>/^Elf/.test(o.value))?.value||r.options[3].value); onRaceChange();
  Object.assign(st.attrs,{STR:12,DEX:14,CON:14,INT:10,WIS:17,CHA:8}); attrRefresh();
  st.hpAsk=[]; hpSync(); st.hpC=Math.round(hpMaxVal()*0.62); document.getElementById('hpC').textContent=st.hpC;
  document.getElementById('hpT').value=5; updBar();
  st.dsS=[1,0,0]; st.dsF=[0,0,0];
  const ms=ITEM_DATA.find(x=>x.n==='Scimitar'), id=Date.now();
  st.items=(st.items||[]).concat([{id,name:'Scimitar',qty:1,wt:3,cat:'Weapon',note:'',ref:ms.n+'|'+ms.s}]);
  st.weapons=[{name:'Scimitar',atk:'',dmg:'',type:'',ref:ms.n+'|'+ms.s,iid:id},{name:'Produce Flame',atk:'+6',dmg:'1d8',type:'Fire'},{name:'',atk:'',dmg:'',type:''}];
  if(typeof hdSetUsed==='function'){const h=hdInfo(); if(h) hdSetUsed(h.die,2);}
  if(typeof applyState==='function'){} buildWeapons(); buildHitDice();
  ['dsS','dsF'].forEach(k=>document.getElementById(k).querySelectorAll('.dspip').forEach((p,j)=>p.classList.toggle('f',!!st[k][j])));
  switchTabAll('zauber'); window.scrollTo(0,0);
}"""
OVER = """(W) => { const bad=[]; for(const e of document.querySelectorAll('#tab-zauber *')){const r=e.getBoundingClientRect(); if(!r.width||!r.height) continue;
  if(r.right>W+0.5) bad.push((e.id?'#'+e.id:'')+'.'+[...e.classList].join('.')+' '+e.tagName+' r='+Math.round(r.right));} return bad.slice(0,8); }"""
res, errs = {}, []
with sync_playwright() as p:
    b = p.chromium.launch()
    runs = [(w, z, 'leder') for w in WS for z in ('normal', 'gross', 'sehrgross')] + [(430, 'gross', 'klassisch')]
    for W, z, ds in runs:
        ctx = b.new_context(viewport={'width': W, 'height': 900}, device_scale_factor=2, is_mobile=True, has_touch=True)
        ctx.add_init_script(f"try{{localStorage.setItem('willow_textsize','{z}');localStorage.setItem('willow_design','{ds}')}}catch(e){{}}")
        pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('file://' + os.path.abspath(html)); pg.wait_for_timeout(700)
        shot_fonts.apply(pg)
        pg.evaluate(SETUP); pg.wait_for_timeout(300)
        k = f'{W}_{z}' + ('' if ds == 'leder' else '_classic')
        res[k] = {'ueberlauf': pg.evaluate(OVER, W), 'karten': pg.evaluate(shot_fonts.CARD_CHECK, 'tab-zauber')}
        pg.add_style_tag(content='.bottom-nav,.dice-fab,.toast{visibility:hidden!important}')
        y = pg.evaluate("document.getElementById('hpPanel').getBoundingClientRect().top+scrollY-8")
        y2 = pg.evaluate("(()=>{const e=document.getElementById('weaponList').closest('.act-panel');return e.getBoundingClientRect().bottom+scrollY+8})()")
        pg.screenshot(path=f'{out}/{k}.png', full_page=True, clip={'x': 0, 'y': y, 'width': W, 'height': min(y2 - y, 2400)})
        ctx.close()
    b.close()
for k, v in res.items(): print(k.ljust(22), 'Überlauf', v['ueberlauf'] or '–', ' Karten', v['karten'] or '–')
print('JS-Fehler:', errs or '–')
