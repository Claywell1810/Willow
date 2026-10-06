# Paket W – Kopf + Ability Scores je Klasse fotografieren: python3 willow/tools/design_w_shots.py HTML OUTDIR PAL.json [breite] [Klasse,…]
# REAL=1: Klassen-Themes der App (PAL.json nur für die Klassenliste); sonst PAL-Werte als eigene Farben. MODE=light|dark.
import sys, os, json
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import shot_fonts
from playwright.sync_api import sync_playwright
html, out = sys.argv[1], sys.argv[2]; pal=json.load(open(sys.argv[3])); W=int(sys.argv[4]) if len(sys.argv)>4 else 390
NUR=sys.argv[5].split(',') if len(sys.argv)>5 else None
os.makedirs(out, exist_ok=True)
NAMES={'':'No Class','Artificer':'Tink','Barbarian':'Grok','Bard':'Lyra','Cleric':'Seraphine','Druid':'Willow','Fighter':'Kevin','Monk':'Shen','Paladin':'Aldric','Ranger':'Faen','Rogue':'Vex','Sorcerer':'Ember','Warlock':'Mordra','Wizard':'Elminor'}
SETUP="""([c,n]) => {
  document.getElementById('charName').textContent=n;
  const s=(id,v)=>{const e=document.getElementById(id); if(e) e.value=v;};
  s('lvl','6'); s('cls',c); onClsChange();
  const sc=document.getElementById('subcls'); if(sc&&sc.options.length>1){s('subcls',sc.options[1].value); onSubclsChange();}
  const r=document.getElementById('race'); s('race',[...r.options].find(o=>/^Human/.test(o.value))?.value||r.options[3].value); onRaceChange();
  st.attrSrc={STR:{base:15},DEX:{base:10},CON:{base:13},INT:{base:12},WIS:{base:16},CHA:{base:8}}; attrSync(); attrRefresh();
  applyTheme(c); window.scrollTo(0,0);
}"""
with sync_playwright() as p:
    b=p.chromium.launch()
    for c in pal:
        if NUR and (c or 'none') not in NUR: continue
        ctx=b.new_context(viewport={'width':W,'height':860},device_scale_factor=2,is_mobile=True,has_touch=True,color_scheme='dark')
        ov=json.dumps({c:pal[c]})
        MODE=os.environ.get('MODE','dark'); ctx.add_init_script("try{localStorage.setItem('willow_textsize','normal');localStorage.setItem('willow_mode','%s');%s}catch(e){}"%(MODE,'' if os.environ.get('REAL') else "localStorage.setItem('dnd5e_theme_overrides',%s)"%json.dumps(ov)))
        pg=ctx.new_page(); pg.on('pageerror',lambda e:print('ERR',e))
        pg.goto('file://'+os.path.abspath(html)); pg.wait_for_timeout(500); shot_fonts.apply(pg)
        pg.evaluate(SETUP,[c,NAMES.get(c,'Hero')]); pg.wait_for_timeout(300)
        pg.add_style_tag(content='.toast{visibility:hidden!important}')
        pg.screenshot(path=f"{out}/{c or 'none'}.png"); ctx.close()
    b.close()
