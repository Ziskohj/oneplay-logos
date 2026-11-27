#!/usr/bin/env python3
"""Los logos GENÉRICOS de OnePlay: uno por temática y palabra («PELÍCULAS», «COMEDY», «HORREUR», «영화», «أفلام»…), para los
canales que solo dicen una temática («PELÍCULAS 24/7», «24/7 HORROR MOVIES») y para los huecos de eventos de un panel
(«Evento 05» en la categoría «Baloncesto»). Diseño propio: el icono de Material Symbols (Apache 2.0) y la palabra en Inter o,
en las escrituras que Inter no tiene, en Noto Sans (las dos, SIL OFL 1.1), en blanco (`default`, tarjetas oscuras) y gris
oscuro (`dark`, tarjetas claras), dibujados en el lienzo de la tarjeta (3:4) para que la app los pinte tal cual.

Uso: coleccion.py <carpeta con temas.json y fuentes/> <salida>
  fuentes/: Inter.ttf (google/fonts, ofl/inter), Symbols.ttf y Symbols.codepoints (google/material-design-icons,
  variablefont/MaterialSymbolsRounded) y, de google/fonts (ofl/notosans…), las variables de cada escritura: Arabic.ttf,
  Hebrew.ttf, Devanagari.ttf, Bengali.ttf, Thai.ttf, KR.ttf, JP.ttf, SC.ttf y TC.ttf.
Deja <salida>/logos/generico/*.png y <salida>/genericos.json (lo que va en extra/genericos.json).

LAS CLAVES son las que calcula la app (`ChannelLogoDirectory`, en el núcleo), y tienen que salir IGUALES aquí:
- una palabra en alfabeto latino: `key` (minúsculas, sin tildes, solo a-z y 0-9). Se conserva además la clave de las primeras
  tarjetas, que cambiaba «ß» por «ss» y «ł» por «l»: las dos llevan al mismo logo.
- una palabra en otra escritura: `scriptKey` (minúsculas, descompuesta, sin las marcas que se combinan, solo letras, marcas y
  cifras, y unas pocas letras que se escriben de dos maneras igualadas).
`temas.json` puede llevar «_han»: {"JP": […], "TC": […]}, las palabras solo con caracteres chinos que se dibujan con la forma
japonesa o la del chino tradicional (las demás, con la del simplificado).
"""
import sys, json, re, unicodedata, os, hashlib
from PIL import Image, ImageDraw, ImageFont
S = sys.argv[1]; OUT = sys.argv[2]
F = S + '/fuentes'
temas = json.load(open(S + '/temas.json', encoding='utf-8'))
han = temas.pop('_han', {})
cp = {}
for l in open(F + '/Symbols.codepoints'):
    n, c = l.split(); cp[n] = chr(int(c, 16))
def fs(px):
    f = ImageFont.truetype(F + '/Symbols.ttf', px); f.set_variation_by_axes([1, 0, 48, 500]); return f
def escritura(texto):
    nombres = [unicodedata.name(c, '') for c in texto]
    def tiene(p): return any(p in n for n in nombres)
    if tiene('ARABIC'): return 'Arabic'
    if tiene('HEBREW'): return 'Hebrew'
    if tiene('DEVANAGARI'): return 'Devanagari'
    if tiene('BENGALI'): return 'Bengali'
    if tiene('THAI'): return 'Thai'
    if tiene('HANGUL'): return 'KR'
    if tiene('HIRAGANA') or tiene('KATAKANA'): return 'JP'
    if tiene('CJK'): return 'JP' if texto in han.get('JP', []) else 'TC' if texto in han.get('TC', []) else 'SC'
    return 'Inter'
def ft(px, peso, fuente='Inter'):
    f = ImageFont.truetype(f'{F}/{fuente}.ttf', px)
    if fuente == 'Inter': f.set_variation_by_axes([32, peso])
    else: f.set_variation_by_axes([peso] + [a['default'] for a in f.get_variation_axes()[1:]])
    return f
def plegado(t):   # `fold` del núcleo
    return ''.join(c for c in unicodedata.normalize('NFKD', t.lower()) if unicodedata.combining(c) == 0)
def clave_nucleo(t):   # `key` del núcleo
    return re.sub(r'[^a-z0-9]', '', plegado(t).replace('&', ' and ').replace('+', ' plus '))
def key(t):   # la de las primeras tarjetas: da nombre a sus ficheros y se conserva
    d = ''.join(c for c in unicodedata.normalize('NFKD', t.lower()) if not unicodedata.combining(c))
    d = d.replace('&', ' and ').replace('+', ' plus ').replace('ı', 'i').replace('ß', 'ss').replace('ł', 'l')
    return re.sub(r'[^a-z0-9]', '', d)
IGUALES = str.maketrans({'ς': 'σ', 'ی': 'ي', 'ى': 'ي', 'ک': 'ك', 'ـ': None})
def clave_escritura(t):   # `scriptKey` del núcleo
    return ''.join(c for c in plegado(t).translate(IGUALES) if unicodedata.category(c)[0] in 'LMN')
def es_latina(t):
    return all('LATIN' in unicodedata.name(c, '') for c in t if unicodedata.category(c)[0] == 'L')
W, H = 900, 1200
TEXTO_MAX = 760
def ancho(f, texto):
    b = f.getbbox(texto); return b[2] - b[0]
def palabra(texto, fuente):
    px = 118
    while True:
        f = ft(px, 800, fuente)
        if ancho(f, texto) <= TEXTO_MAX or px <= 56: return f
        px -= 4
def lineas(texto, fuente):
    """La palabra en una línea; si no cabe ni con la letra más pequeña, en dos (por el espacio del medio) o más pequeña."""
    f = palabra(texto, fuente)
    if ancho(f, texto) <= TEXTO_MAX: return [texto], f
    partes = texto.split(' ')
    if len(partes) >= 2:
        corte = min(range(1, len(partes)), key=lambda i: abs(len(' '.join(partes[:i])) - len(' '.join(partes[i:]))))
        dos = [' '.join(partes[:corte]), ' '.join(partes[corte:])]
        px = 92
        while px > 44 and max(ancho(ft(px, 800, fuente), l) for l in dos) > TEXTO_MAX: px -= 4
        return dos, ft(px, 800, fuente)
    px = 56
    while px > 36 and ancho(ft(px, 800, fuente), texto) > TEXTO_MAX: px -= 2
    return [texto], ft(px, 800, fuente)
def dibuja(icono, texto, color):
    im = Image.new('RGBA', (W, H), (0,0,0,0)); d = ImageDraw.Draw(im)
    d.text((W/2, H*0.43), cp[icono], font=fs(400), fill=color, anchor='mm')
    ls, f = lineas(texto, escritura(texto))
    if len(ls) == 1:
        d.text((W/2, H*0.72), texto, font=f, fill=color, anchor='mm')
    else:
        salto = f.size * 1.12
        for i, l in enumerate(ls):
            d.text((W/2, H*0.72 + (i - 0.5) * salto), l, font=f, fill=color, anchor='mm')
    return im.resize((384, 512), Image.LANCZOS)
os.makedirs(OUT + '/logos/generico', exist_ok=True)
genericos = {}; cine = []; logos = {}
for tema, datos in temas.items():
    for texto in datos['palabras']:
        if es_latina(texto):
            k = key(texto); claves = [k] + [c for c in [clave_nucleo(texto)] if c != k]
            nombre = f'generico/{tema}-{k}'
        else:
            k = clave_escritura(texto); claves = [k]
            # El nombre del fichero, en ASCII: la clave en otra escritura no vale para una dirección.
            nombre = f'generico/{tema}-x' + hashlib.sha1(k.encode('utf-8')).hexdigest()[:10]
        if not k: continue
        if k in genericos:
            # Otra forma de escribir una palabra que ya está («FUßBALL» tras «FUSSBALL»): su clave de la app, al mismo logo.
            for c in claves: genericos.setdefault(c, genericos[k])
            continue
        for variante, color in (('default', (255,255,255,255)), ('dark', (28,28,32,255))):
            dibuja(datos['icono'], texto, color).save(f'{OUT}/logos/{nombre}.{variante}.png', optimize=True)
        for c in claves: genericos.setdefault(c, nombre)
        logos[nombre] = ['default', 'dark']
        if datos.get('cine'): cine += claves
json.dump({'genericos': genericos, 'cine': sorted(set(cine)), 'logos': logos}, open(OUT + '/genericos.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print(len(genericos), 'claves,', len(logos), 'tarjetas,', len(logos)*2, 'ficheros')
