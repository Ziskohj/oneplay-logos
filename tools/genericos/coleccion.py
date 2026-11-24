#!/usr/bin/env python3
"""Los logos GENÉRICOS de OnePlay: uno por temática y palabra («PELÍCULAS», «COMEDY», «HORREUR»…), para los canales que solo
dicen una temática («PELÍCULAS 24/7», «24/7 HORROR MOVIES»). Diseño propio: el icono de Material Symbols (Apache 2.0) y la
palabra en Inter (SIL OFL 1.1), en blanco (`default`, tarjetas oscuras) y gris oscuro (`dark`, tarjetas claras), dibujados en
el lienzo de la tarjeta (3:4) para que la app los pinte tal cual.

Uso: coleccion.py <carpeta con temas.json y fuentes/> <salida>
  fuentes/: Inter.ttf (google/fonts, ofl/inter), Symbols.ttf y Symbols.codepoints (google/material-design-icons,
  variablefont/MaterialSymbolsRounded).
Deja <salida>/logos/generico/*.png y <salida>/genericos.json (lo que va en extra/genericos.json).
"""
import sys, json, re, unicodedata, os
from PIL import Image, ImageDraw, ImageFont
S = sys.argv[1]; OUT = sys.argv[2]
F = S + '/fuentes'
temas = json.load(open(S + '/temas.json'))
cp = {}
for l in open(F + '/Symbols.codepoints'):
    n, c = l.split(); cp[n] = chr(int(c, 16))
def fs(px):
    f = ImageFont.truetype(F + '/Symbols.ttf', px); f.set_variation_by_axes([1, 0, 48, 500]); return f
def ft(px, peso):
    f = ImageFont.truetype(F + '/Inter.ttf', px); f.set_variation_by_axes([32, peso]); return f
def key(t):
    d = ''.join(c for c in unicodedata.normalize('NFKD', t.lower()) if not unicodedata.combining(c))
    d = d.replace('&', ' and ').replace('+', ' plus ').replace('ı', 'i').replace('ß', 'ss').replace('ł', 'l')
    return re.sub(r'[^a-z0-9]', '', d)
W, H = 900, 1200
TEXTO_MAX = 760
def palabra(texto):
    px = 118
    while True:
        f = ft(px, 800)
        b = f.getbbox(texto)
        if b[2] - b[0] <= TEXTO_MAX or px <= 56: return f
        px -= 4
def dibuja(icono, texto, color):
    im = Image.new('RGBA', (W, H), (0,0,0,0)); d = ImageDraw.Draw(im)
    d.text((W/2, H*0.43), cp[icono], font=fs(400), fill=color, anchor='mm')
    d.text((W/2, H*0.72), texto, font=palabra(texto), fill=color, anchor='mm')
    return im.resize((384, 512), Image.LANCZOS)
os.makedirs(OUT + '/logos/generico', exist_ok=True)
genericos = {}; cine = []; logos = {}
for tema, datos in temas.items():
    for texto in datos['palabras']:
        k = key(texto)
        if k in genericos: continue
        nombre = f'generico/{tema}-{k}'
        for variante, color in (('default', (255,255,255,255)), ('dark', (28,28,32,255))):
            dibuja(datos['icono'], texto, color).save(f'{OUT}/logos/{nombre}.{variante}.png', optimize=True)
        genericos[k] = nombre
        logos[nombre] = ['default', 'dark']
        if datos.get('cine'): cine.append(k)
json.dump({'genericos': genericos, 'cine': sorted(cine), 'logos': logos}, open(OUT + '/genericos.json', 'w'), ensure_ascii=False, indent=1)
print(len(genericos), 'palabras,', len(logos)*2, 'ficheros')
