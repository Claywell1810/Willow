#!/usr/bin/env python3
# t14_icon.py – Icons für Willow 2014 (Paket T1, 18.10.2026): Willow-Icon + Banderole „2014“ unten
# Aufruf (aus dem Ordner über dem Klon): python3 willow/tools/t14_icon.py
# Quelle willow/willow-icon-512.png → willow/2014/willow-icon-512.png und -192.png
# Schrift Cinzel (npm i @fontsource/cinzel, liegt nach setup.sh fotos unter node_modules/)
import os, sys
from PIL import Image, ImageDraw, ImageFont
W = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = os.path.join(os.path.dirname(W), 'node_modules/@fontsource/cinzel/files/cinzel-latin-700-normal.woff2')
if not os.path.exists(FONT):
    sys.exit('Schrift fehlt: npm i @fontsource/cinzel (im Ordner über dem Klon)')
src = Image.open(os.path.join(W, 'willow-icon-512.png')).convert('RGBA')
S = src.size[0]
GOLD, GOLD2, RED, RED2 = (226, 192, 104, 255), (138, 111, 46, 255), (96, 18, 22, 255), (60, 10, 14, 255)
band = Image.new('RGBA', src.size, (0, 0, 0, 0))
dr = ImageDraw.Draw(band)
y0, y1 = int(S * .735), int(S * .885)            # Banderole im unteren Drittel (über der Robe)
for y in range(y0, y1):                          # leichter Verlauf oben hell → unten dunkel
    t = (y - y0) / (y1 - y0)
    dr.line([(0, y), (S, y)], fill=tuple(int(RED[i] * (1 - t) + RED2[i] * t) for i in range(3)) + (240,))
lw = max(2, S // 110)
dr.rectangle([0, y0, S, y0 + lw], fill=GOLD); dr.rectangle([0, y1 - lw, S, y1], fill=GOLD)
dr.rectangle([0, y0 + 2 * lw, S, y0 + 2 * lw + max(1, lw // 2)], fill=GOLD2)
dr.rectangle([0, y1 - 2 * lw - max(1, lw // 2), S, y1 - 2 * lw], fill=GOLD2)
font = ImageFont.truetype(FONT, int((y1 - y0) * .78))
txt = '2014'
bx = dr.textbbox((0, 0), txt, font=font)
tx, ty = (S - (bx[2] - bx[0])) / 2 - bx[0], (y0 + y1) / 2 - (bx[1] + bx[3]) / 2
dr.text((tx + S / 170, ty + S / 170), txt, font=font, fill=(20, 4, 6, 200))   # Schatten
dr.text((tx, ty), txt, font=font, fill=GOLD)
out = Image.alpha_composite(src, band)
out.putalpha(src.getchannel('A'))   # Ecken wie im Original (abgerundeter Rahmen)
# Goldrahmen links/rechts über die Banderole zurückholen (äußere 4 % aus dem Original)
fr = int(S * .045)
for box in [(0, y0, fr, y1), (S - fr, y0, S, y1)]:
    out.paste(src.crop(box), box[:2])
os.makedirs(os.path.join(W, '2014'), exist_ok=True)
out.save(os.path.join(W, '2014', 'willow-icon-512.png'), optimize=True)
out.resize((192, 192), Image.LANCZOS).save(os.path.join(W, '2014', 'willow-icon-192.png'), optimize=True)
print('2014/willow-icon-512.png + -192.png geschrieben')
