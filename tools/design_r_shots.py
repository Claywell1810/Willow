# Paket R – Fotos zum Design-Test (design_r_test.py): je Klasse × Modus der obere Teil des Actions-Tabs (430 px)
import sys, os
sys.path.insert(0, 'willow/tools'); import shot_fonts
from playwright.sync_api import sync_playwright
from PIL import Image
W = int(sys.argv[1]) if len(sys.argv) > 1 else 430
CASES = [('Druid', 'Willow', 'Guide'), ('Wizard', 'Aldric', 'Sage'), ('Rogue', 'Vex', 'Criminal')]
os.makedirs('shots2', exist_ok=True)
errs = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for mode in ('dark', 'light'):
        for cls, name, bg in CASES:
            ctx = b.new_context(viewport={'width': W, 'height': 900}, device_scale_factor=2, is_mobile=True, has_touch=True)
            ctx.add_init_script(f"try{{localStorage.setItem('willow_mode','{mode}')}}catch(e){{}}")
            pg = ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto('file://' + os.path.abspath('TEST2.html')); pg.wait_for_timeout(700)
            shot_fonts.apply(pg)
            pg.evaluate(f"""() => {{
              document.getElementById('charName').textContent='{name}';
              const s=(id,v)=>{{const e=document.getElementById(id); if(e) e.value=v;}};
              s('lvl','6'); s('cls','{cls}'); onClsChange();
              const sc=document.getElementById('subcls'); s('subcls', sc.options[1]?.value||''); onSubclsChange();
              const r=document.getElementById('race'); s('race',[...r.options].find(o=>/^Human/.test(o.value))?.value||r.options[3].value); onRaceChange();
              s('bg','{bg}'); st.hpC=7; document.getElementById('hpC').textContent=7; updBar();
              switchTabAll('zauber'); if(typeof toggleTabs==='function') toggleTabs(); hxUpd();
            }}""")
            pg.wait_for_timeout(400)
            f = f'shots2/{mode}_{cls}.png'; pg.screenshot(path=f, full_page=False); ctx.close()
    b.close()
print('Fehler:', errs)
for mode in ('dark', 'light'):
    ims = [Image.open(f'shots2/{mode}_{c}.png') for c, _, _ in CASES]
    w, h = ims[0].size; out = Image.new('RGB', (w * 3 + 40, h), (0, 0, 0))
    for i, im in enumerate(ims): out.paste(im, (i * (w + 20), 0))
    out.save(f'design2_{mode}.png')
