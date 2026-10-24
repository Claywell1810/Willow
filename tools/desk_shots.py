# PC-Ansicht (Paket AC, 25.10.2026): Bildschirmfotos im Querformat + Überlauf-Prüfung je Spalte
# Aufruf: python3 willow/tools/desk_shots.py HTML OUTDIR [breite] [höhe] [zoom-stufe] [tabs]
#   breite/höhe: 1920 1080 (Standard), 1366 768 (Laptop, 3 Spalten), 1280 720 (2 Spalten)
#   tabs: Spalten-Belegung mit Komma, z. B. info,zauber,skills (Standard) oder ausruestung,spelllist,notizen
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shot_fonts
from playwright.sync_api import sync_playwright
html, out = sys.argv[1], sys.argv[2]
W = int(sys.argv[3]) if len(sys.argv) > 3 else 1920
H = int(sys.argv[4]) if len(sys.argv) > 4 else 1080
zoom = sys.argv[5] if len(sys.argv) > 5 and sys.argv[5] != '-' else None
cols = (sys.argv[6] if len(sys.argv) > 6 else 'info,zauber,skills').split(',')
os.makedirs(out, exist_ok=True)
SETUP = """
() => {
  document.getElementById('charName').textContent='Testheld';
  const set=(id,v)=>{const e=document.getElementById(id); if(e) e.value=v;};
  set('lvl','7'); set('cls','Druid'); onClsChange(); const so=[...document.getElementById('subcls').options].map(o=>o.value).filter(Boolean); set('subcls', so.includes('Circle of the Stars (XPHB)')?'Circle of the Stars (XPHB)':(so[0]||'')); onSubclsChange();
  set('race', document.getElementById('race')?.options?.[3]?.value||'');
  Object.assign(st.attrs,{STR:10,DEX:14,CON:14,INT:12,WIS:18,CHA:8});
  st.weapons=[{name:'Quarterstaff',atk:'+5',dmg:'1d6+2',type:'Bludgeoning'}];
  st.slotMax=[4,3,3,1,0,0,0,0,0]; st.slotUsed=[1,0,0,0,0,0,0,0,0];
  const idx=n=>ZB_SPELLS.findIndex(s=>s.name===n);
  for(const n of ['Guidance','Healing Word','Moonbeam','Call Lightning']){const i=idx(n); if(i>=0){st.zbAdded.add(i); st.mySpells.push({name:ZB_SPELLS[i].name,grad:ZB_SPELLS[i].grad,school:ZB_SPELLS[i].school,prep:true,notes:''});}}
  if(typeof buildAttrs==='function') buildAttrs();
  autoSave();
}
"""
# Überstand: sichtbares Element ragt seitlich aus seiner Spalte (Panel) oder aus dem Fenster
OVER = """
() => {
  const bad=[];
  for(const p of document.querySelectorAll('.panel.on')){
    const pr=p.getBoundingClientRect();
    for(const e of p.querySelectorAll('*')){
      const r=e.getBoundingClientRect(); if(!r.width||!r.height) continue;
      const s=getComputedStyle(e); if(s.visibility==='hidden'||s.display==='none') continue;
      let sc=false; for(let q=e.parentElement;q&&q!==p;q=q.parentElement){if(/(auto|scroll|hidden)/.test(getComputedStyle(q).overflowX)){sc=true;break;}}
      if(!sc&&(r.right>pr.right+0.5||r.left<pr.left-0.5)) bad.push(p.id+' '+(e.id?'#'+e.id:'')+'.'+[...e.classList].join('.')+' '+e.tagName);
    }
  }
  return {desk:document.documentElement.dataset.desk||'', on:[...document.querySelectorAll('.panel.on')].map(p=>p.id+'@'+p.dataset.dk),
    sw:document.documentElement.scrollWidth, sh:document.documentElement.scrollHeight, nbad:bad.length, bad:bad.slice(0,10)};
}
"""
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=1)
    init = "try{localStorage.setItem('willow_desk_cols',%s);localStorage.setItem('w14_willow_desk_cols',%s)}catch(e){}" % ((json.dumps(json.dumps(cols)),) * 2)
    if zoom:
        init += f"try{{localStorage.setItem('willow_textsize','{zoom}');localStorage.setItem('w14_willow_textsize','{zoom}')}}catch(e){{}}"
    ctx.add_init_script(init)
    pg = ctx.new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + os.path.abspath(html)); pg.wait_for_timeout(700)
    shot_fonts.apply(pg)
    pg.evaluate(SETUP); pg.wait_for_timeout(500)
    res = pg.evaluate(OVER)
    res['errs'] = errs
    name = f'desk_{W}x{H}' + (f'_{zoom}' if zoom else '') + '_' + '-'.join(cols)
    pg.screenshot(path=f'{out}/{name}.png')
    b.close()
json.dump(res, open(f'{out}/{name}.json', 'w'), indent=1)
print(name, res)
