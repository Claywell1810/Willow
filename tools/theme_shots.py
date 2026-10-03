# Theme-Galerie: je Klasse Ausschnitt Actions-Tab (Class Features, eine Karte offen)
# Aufruf: python3 theme_shots.py HTML OUTDIR
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shot_fonts   # echte Schriften (02.10.2026)
from playwright.sync_api import sync_playwright
html, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
CL = [('', ''), ('Artificer', 'Battle Smith (EFA)'), ('Barbarian', 'Path of the Berserker (PHB)'), ('Bard', 'College of Lore (PHB)'), ('Cleric', 'Life Domain (PHB)'),
      ('Druid', 'Circle of the Stars (XPHB)'), ('Fighter', 'Champion (PHB)'), ('Monk', 'Warrior of the Open Hand (XPHB)'),
      ('Paladin', 'Oath of Devotion (PHB)'), ('Ranger', 'Hunter (PHB)'), ('Rogue', 'Thief (PHB)'), ('Sorcerer', 'Draconic Sorcery (XPHB)'),
      ('Warlock', 'Fiend Patron (XPHB)'), ('Wizard', 'Evoker (XPHB)')]
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2)
    pg.goto('file://' + os.path.abspath(html)); pg.wait_for_timeout(700)
    shot_fonts.apply(pg)
    for c, sub in CL:
        pg.evaluate("""([c,sub])=>{const set=(i,v)=>{document.getElementById(i).value=v};set('lvl','6');set('cls',c);onClsChange();
          set('subcls',sub);onSubclsChange();if(typeof applyTheme==='function')applyTheme(c);switchTabAll('zauber');
          st.abUses={};buildAbilities();const t=[...document.querySelectorAll('#abList .ab-card:not(.ab-feat) .ab-top')][0]||document.querySelector('#abList .ab-card .ab-top');if(t)t.click();}""", [c, sub])
        pg.add_style_tag(content='.bottom-nav,.dice-fab,.toast{visibility:hidden!important}')
        pg.wait_for_timeout(200)
        y = pg.evaluate("document.getElementById('abilitiesSection').getBoundingClientRect().top+scrollY")
        pg.screenshot(path=f'{out}/{c or "Default"}.png', full_page=True, clip={'x': 0, 'y': y, 'width': 390, 'height': 640})
    b.close()
