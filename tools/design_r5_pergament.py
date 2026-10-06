# Paket R5 – Pergament (Light) + ⚙ Mode. Aufruf aus /home/claude: python3 SCRATCH/r5_patch.py
import sys, json, re, urllib.parse
sys.path.insert(0, 'willow/tools'); from rep import Datei
d = Datei('DnD_Character_App.html')

LIGHT = {"bg0": "#efe5ce", "bg1": "#f6efdf", "bg2": "#fcf9f0", "bg3": "#f0e7d3", "gold": "#74490f", "gold2": "#6a4310",
         "purple": "#7a2e1c", "purple2": "#9c7436", "purple3": "#ecdcb8", "text": "#2a1c0f", "text2": "#4e3a22", "text3": "#6a4614",
         "desc": "#33241a", "muted": "#665236", "border": "rgba(110,72,28,.38)", "border2": "rgba(110,72,28,.2)",
         "green": "#276134", "red": "#9a2a1f", "blue": "#2a5a8c"}

# ---------- JS: Palette, Modus, getrennte eigene Farben ----------
s = d.s
i = s.index('const WILLOW_PAL={"dark": {'); j = s.index('\n', i)
old = s[i:j]; assert old.endswith('}};')
d.rep(old, old[:-2] + ', "light": ' + json.dumps(LIGHT) + '};')
d.rep("""function willowMode(){let m='dark';try{m=localStorage.getItem('willow_mode')||'dark'}catch(e){}return WILLOW_PAL[m]?m:'dark';}""",
"""// Paket R5 (06.10.2026): ⚙ „Mode“ pro Gerät – willow_mode = dark (Standard) | light (Pergament) | auto (folgt dem System); im Design Classic immer dark
function willowModeSet(){let m='dark';try{m=localStorage.getItem('willow_mode')||'dark'}catch(e){}return (m==='light'||m==='auto')?m:'dark';}
function willowMode(){if(willowDesign()==='klassisch')return 'dark';let m=willowModeSet();
  if(m==='auto'){try{m=window.matchMedia&&matchMedia('(prefers-color-scheme: light)').matches?'light':'dark'}catch(e){m='dark'}}
  return WILLOW_PAL[m]?m:'dark';}""")
d.rep("""function markDesign(){const v=willowDesign();document.querySelectorAll('#dsRow .fbtn').forEach(b=>b.classList.toggle('on',b.dataset.ds===v));}""",
"""function markDesign(){const v=willowDesign();document.querySelectorAll('#dsRow .fbtn').forEach(b=>b.classList.toggle('on',b.dataset.ds===v));markMode();}
function markMode(){const v=willowModeSet();document.querySelectorAll('#mdRow .fbtn').forEach(b=>b.classList.toggle('on',b.dataset.md===v));
  const w=document.getElementById('mdWrap');if(w)w.style.display=willowDesign()==='klassisch'?'none':'';}
function setMode(v){
  v=(v==='light'||v==='auto')?v:'dark';
  try{localStorage.setItem('willow_mode',v);}catch(e){}
  applyTheme(document.getElementById('cls')?.value||'');
  markMode();
  if(document.getElementById('settingsModal')?.style.display==='flex')buildSettingsUI();
}
try{window.matchMedia&&matchMedia('(prefers-color-scheme: light)').addEventListener('change',()=>{if(willowModeSet()==='auto'&&willowDesign()!=='klassisch'){applyTheme(document.getElementById('cls')?.value||'');if(document.getElementById('settingsModal')?.style.display==='flex')buildSettingsUI();}});}catch(e){}""")
d.rep("""const SETTINGS_LS = 'dnd5e_theme_overrides';""",
"""const SETTINGS_LS = 'dnd5e_theme_overrides';
const SETTINGS_LS_LIGHT = 'dnd5e_theme_overrides_light';   // Paket R5: eigene Farben für Pergament getrennt (gleiche Keys wie COLOR_LABELS)
function themeLs(){return willowMode()==='light'?SETTINGS_LS_LIGHT:SETTINGS_LS;}""")
d.rep("""  try{ return JSON.parse(localStorage.getItem(SETTINGS_LS)||'{}'); }catch(e){ return {}; }""",
      """  try{ return JSON.parse(localStorage.getItem(themeLs())||'{}'); }catch(e){ return {}; }""")
d.rep("""function saveThemeOverrides(ov){ try{localStorage.setItem(SETTINGS_LS, JSON.stringify(ov));}""",
      """function saveThemeOverrides(ov){ try{localStorage.setItem(themeLs(), JSON.stringify(ov));}""")
d.rep("""function resetAllThemes(){
  localStorage.removeItem(SETTINGS_LS);""", """function resetAllThemes(){
  localStorage.removeItem(themeLs());   // Paket R5: nur die Farben des aktuellen Modus""")

# ---------- ⚙ Mode-Zeile ----------
d.rep("""          <button class="fbtn" data-ds="klassisch" onclick="setDesign('klassisch')">Classic</button>
        </div>""", """          <button class="fbtn" data-ds="klassisch" onclick="setDesign('klassisch')">Classic</button>
        </div>
        <div id="mdWrap"><!-- Paket R5: Mode nur im Design Leather -->
        <div class="set-h">Mode</div>
        <div class="set-p">Dark = leather, Light = parchment, Auto = follows your phone's setting. Saved on this device.</div>
        <div class="ts-row" id="mdRow">
          <button class="fbtn" data-md="dark" onclick="setMode('dark')">Dark</button>
          <button class="fbtn" data-md="light" onclick="setMode('light')">Light</button>
          <button class="fbtn" data-md="auto" onclick="setMode('auto')">Auto</button>
        </div>
        </div>""")
d.rep("""<div class="set-p">Customize accent colors per class. Changes are saved automatically.</div>""",
      """<div class="set-p">Customize accent colors per class (Dark and Light each keep their own). Changes are saved automatically.</div>""")

# ---------- Frühstart: auto und Classic auflösen ----------
d.rep("""<script>try{var _md=localStorage.getItem('willow_mode');document.documentElement.dataset.mode=(_md==='light'||_md==='dark')?_md:'dark';}catch(e){document.documentElement.dataset.mode='dark';}</script>""",
"""<script>try{var _md=localStorage.getItem('willow_mode');if(_md==='auto')_md=window.matchMedia&&matchMedia('(prefers-color-scheme: light)').matches?'light':'dark';if(localStorage.getItem('willow_design')==='klassisch')_md='dark';document.documentElement.dataset.mode=_md==='light'?'light':'dark';}catch(e){document.documentElement.dataset.mode='dark';}</script>""")

# ---------- CSS-Block willowPergament ----------
def uri(svg): return 'url("data:image/svg+xml,' + urllib.parse.quote(svg, safe='/') + '")'
PARCH = uri("<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'>"
    "<filter id='a' x='0' y='0' width='100%' height='100%'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2' stitchTiles='stitch'/>"
    "<feColorMatrix values='0 0 0 0 .4 0 0 0 0 .27 0 0 0 0 .12 1.2 0 0 0 -.6'/></filter>"
    "<filter id='f' x='0' y='0' width='100%' height='100%'><feTurbulence type='fractalNoise' baseFrequency='.06 .32' numOctaves='3' seed='3' stitchTiles='stitch'/>"
    "<feColorMatrix values='0 0 0 0 .45 0 0 0 0 .32 0 0 0 0 .16 2.2 0 0 0 -1.15'/></filter>"
    "<filter id='b' x='0' y='0' width='100%' height='100%'><feTurbulence type='fractalNoise' baseFrequency='.006' numOctaves='3' seed='9' stitchTiles='stitch'/>"
    "<feColorMatrix values='0 0 0 0 .55 0 0 0 0 .38 0 0 0 0 .15 1.2 0 0 0 -.55'/></filter>"
    "<rect width='100%' height='100%' filter='url(#a)' opacity='.2'/><rect width='100%' height='100%' filter='url(#f)' opacity='.22'/><rect width='100%' height='100%' filter='url(#b)' opacity='.14'/></svg>")
L = 'html[data-mode="light"]'
pal = ';'.join(f'--{k}:{v}' for k, v in LIGHT.items())
SH = 'rgba(90,58,18,'   # brauner Schatten statt Schwarz
HL = 'rgba(255,253,245,'  # Lichtkante
BTN = f'background-image:linear-gradient(180deg,{HL}.8),rgba(140,95,35,.1));box-shadow:inset 0 1px 0 {HL}.75),0 1px 2px {SH}.3)'
BTNA = f'background-image:linear-gradient(180deg,rgba(140,95,35,.16),{HL}.35));box-shadow:inset 0 2px 4px {SH}.3)'
INP_SH = f'box-shadow:inset 0 1px 3px {SH}.22)'
INP_F = f'border-color:var(--gold);outline:none;box-shadow:inset 0 1px 3px {SH}.22),0 0 0 2px color-mix(in srgb,var(--gold) 22%,transparent)'
INSET = f'background:color-mix(in srgb,var(--bg3) 65%,var(--bg1));background-image:none;border:1px solid color-mix(in srgb,var(--gold) 26%,transparent);box-shadow:inset 0 1px 4px {SH}.22),0 1px 0 {HL}.6)'
BS = ['.btn-s', '.rest-btn', '.ws-btn', '.char-btn', '.rl-act', '.rl-wbtn', '.dice-preset-btn', '.filter-toggle', '.ms-prep button', '.dmg-btn',
      '.hpa-b', '.hpa-all', '.it-btn', '.sk-roll-ic', '.nta-expand', '.wr-roll']
NOT = ':not(.btn-p):not(.btn-d):not(.danger):not(.on):not(.item-del)'
INPS = ['.ifield input', '.ifield select', '.cr-in', '.at-in', '.fx-in', '.dice-custom-row input', '.rest-act input', '.item-add-row input', '.item-add-row select',
        '.search-wrap input', '.spell-notes textarea', '.dmg-amt', '.char-sel', '.wr-in', '.nta', '.sk-misc input', '.item-detail textarea', '.item-detail-row input',
        '.set-sel', '.hpa-in']
HEADS = ['.hx-t0', '#tab-zauber .act-panel > .sec-top', '.panel:not(#tab-info):not(#tab-zauber) > .sec',
         '.panel:not(#tab-info):not(#tab-zauber) > div:not(.act-panel) > .sec', '.set-h:not(.set-cl)', '.ws-head', '.hx-cls', '.hx-sub', '.hpx-main #hpC']
GOLDB = ['.btn-p', '.dice-custom-row button', '.it-btn.on', '.zb-addbtn:not(.done)', '.se-add:not(:disabled)']
J = lambda sels, suf='': ','.join(f'{L} {x}{suf}' for x in sels)
CSS = f"""<style id="willowPergament">
/* ── Paket R5 (06.10.2026): Pergament (hell) – wirkt nur bei html[data-mode="light"] (⚙ Mode Light/Auto, nur im Design Leather; Classic = immer dark).
   Tinte statt Leuchten: Lichtkanten statt Glanz, braune statt schwarze Schatten, keine Glüh-Effekte. Light-Regeln nur hier (REFERENZ B1d „Design R5“). ── */
{L}{{color-scheme:light;{pal};
  --tex:{PARCH};--tex-size:300px;
  --stitch:color-mix(in srgb,var(--frame) 36%,transparent);--edge:color-mix(in srgb,var(--frame) 46%,transparent);
  --card-hi:linear-gradient(180deg,{HL}.6),rgba(140,95,35,.05));
  --card-sh:inset 0 1px 0 {HL}.65),0 1px 2px {SH}.22);
  --btn-bd:color-mix(in srgb,var(--gold) 42%,transparent);
  --inp:#fffdf7;--inp-bd:color-mix(in srgb,var(--gold) 36%,transparent);
  --ink:#fbf3e0}}
/* Kopf + Leiste */
{L} .hdr.hx-bar{{background-color:color-mix(in srgb,var(--bg1) 94%,#8a5a20)}}
{L} .hx-hero{{background:var(--tex) 0 0/var(--tex-size),radial-gradient(120% 120% at 85% 10%,color-mix(in srgb,var(--frame) 10%,transparent),transparent 60%),
  radial-gradient(160% 140% at 50% 50%,transparent 50%,{SH}.12)),var(--bg1);box-shadow:inset 0 -1px 0 {SH}.18)}}
{L} .hx-vig .s1{{fill:#3a2412;opacity:.22}}{L} .hx-vig .s2{{fill:#3a2412;opacity:.12}}
{L} .hx-vig .br{{stroke:#3a2412;opacity:.32}}
{L} .hx-vig .st{{fill:var(--frame);opacity:.45}}{L} .hx-vig .moon{{fill:var(--frame);opacity:.28}}
{L} .hx-vig .lit{{fill:color-mix(in srgb,var(--frame) 45%,#c8861e);filter:none;opacity:.85}}
{L} .hx-vig .halo{{fill:#c8861e;opacity:.08}}{L} .hx-vig .mist{{fill:var(--frame);opacity:.05}}
{L} .hx-rune{{background:radial-gradient(circle at 50% 35%,#fffdf6,var(--bg2) 80%);
  box-shadow:0 0 0 1px {SH}.45),0 0 0 5px var(--bg1),0 0 0 6px color-mix(in srgb,var(--frame) 55%,transparent),0 4px 10px {SH}.3)}}
{L} .hx-rune .emb{{filter:drop-shadow(0 1px 0 {HL}.8))}}
{L} .hx-name.name-in{{text-shadow:0 1px 0 {HL}.8)}}
@supports (-webkit-background-clip:text) or (background-clip:text){{
  {L} .hx-name.name-in{{background:linear-gradient(180deg,color-mix(in srgb,var(--gold) 72%,#c8902e) 0%,var(--gold) 55%,color-mix(in srgb,var(--gold) 75%,#000) 100%);
    -webkit-background-clip:text;background-clip:text;text-shadow:none;filter:drop-shadow(0 1px 0 {HL}.85))}}}}
{L} .hx-name:empty{{background:none;filter:none}}
{J(HEADS)}{{text-shadow:0 1px 0 {HL}.65)}}
/* Karten, Fenster, Leiste */
{L} .act-panel{{box-shadow:inset 0 0 22px rgba(140,95,35,.06),0 1px 6px {SH}.14)}}
{L} .set-sheet,{L} .dice-sheet{{box-shadow:0 10px 30px rgba(60,38,10,.45)}}
{L} .sk-list > .sk-row:last-child,{L} .sk-list .sk-row:has(+ .sk-grp){{box-shadow:0 2px 4px {SH}.18)}}
{L} .item-detail{{background:color-mix(in srgb,var(--bg3) 55%,transparent)}}
/* Knöpfe: Lichtkante statt Glanz */
{J(BS, NOT)}{{{BTN}}}
{J(BS, NOT + ':active')},{L} .dmg-btn:active{{{BTNA}}}
{J(GOLDB)}{{background:linear-gradient(180deg,color-mix(in srgb,var(--gold) 80%,#fff),var(--gold) 60%,color-mix(in srgb,var(--gold) 85%,#000));
  border:1px solid color-mix(in srgb,var(--gold) 70%,#000);color:var(--ink);-webkit-text-fill-color:var(--ink);text-shadow:0 -1px 0 rgba(40,20,0,.35);
  box-shadow:inset 0 1px 0 rgba(255,240,200,.35),0 1px 3px {SH}.35)}}
{L} .btn-d,{L} .char-btn.danger,{L} .it-btn.item-del{{background-image:linear-gradient(180deg,color-mix(in srgb,var(--red) 8%,{HL}.7)),color-mix(in srgb,var(--red) 10%,transparent));
  box-shadow:inset 0 1px 0 {HL}.6),0 1px 2px {SH}.25)}}
{L} .fbtn.on,{L} .ts-row .fbtn.on{{background:linear-gradient(180deg,color-mix(in srgb,var(--gold) 30%,{HL}.5)),color-mix(in srgb,var(--gold) 22%,transparent));
  border-color:var(--gold);box-shadow:inset 0 1px 2px {SH}.25)}}
{L} .wr-roll{{background-color:var(--bg2)}}
/* Eingaben + eingelassene Kästen */
{J(INPS)}{{{INP_SH}}}
{J(INPS, ':focus')}{{{INP_F}}}
{L} .hpx-temp.hpbox,{L} #tab-zauber .ds-box,{L} .dmg-box,{L} .wr{{{INSET}}}
{L} .hpx-bar.hpbar-w{{background:linear-gradient(180deg,#d6c29a,#ece0c2);box-shadow:inset 0 2px 3px {SH}.3)}}
/* Tinte statt Leuchten */
{L} .bnav-btn.on .bnav-icon{{filter:none}}
{L} .ci-rune{{box-shadow:0 1px 3px {SH}.25)}}
{L} .sp-conc.active{{box-shadow:0 1px 2px {SH}.3)}}
{L} .die-shape.crit{{box-shadow:0 0 0 2px color-mix(in srgb,var(--green) 40%,transparent)}}
{L} .die-shape.fail{{box-shadow:0 0 0 2px color-mix(in srgb,var(--red) 40%,transparent)}}
</style>
"""
d.rep("""</style>
<script>try{if(localStorage.getItem('willow_design')==='klassisch')""", "</style>\n" + CSS + """<script>try{if(localStorage.getItem('willow_design')==='klassisch')""")
d.save()
print('ok', len(CSS))
