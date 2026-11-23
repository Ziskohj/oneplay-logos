#!/usr/bin/env python3
"""Construye la base de logos de OnePlay a partir de Picons (https://github.com/picons/picons).

Uso: construir.py --picons <copia de picons> --salida <raíz del repositorio> --render <programa render>

- Cada logo de Picons (`build-source/logos/<nombre>.<variante>.svg|png`) pasa a `logos/<nombre>.<variante>.png`, con su lado
  mayor a 512 píxeles como mucho y el fondo transparente. Variantes: `default` (la normal), `light` (para fondos oscuros) y
  `dark` (para fondos claros), como las usa Picons.
- Solo se rehace lo que ha cambiado en Picons (la huella de cada fichero, en `fuentes.json`); lo que Picons quita, se quita.
- `index.json`: los nombres de canal de Picons (`snp.index`, ya normalizados: minúsculas, sin espacios ni signos, «+» = «plus»,
  «&» = «and») → el logo, y las variantes de cada logo.
"""
import argparse, datetime, hashlib, json, os, subprocess, sys, tempfile
from PIL import Image

LADO = 512
VARIANTES = ('default', 'light', 'dark')

def huellas(picons):
    """La huella git de cada fichero de logos de Picons."""
    salida = subprocess.run(['git', '-C', picons, 'ls-files', '-s', 'build-source/logos'], check=True, capture_output=True, text=True).stdout
    resultado = {}
    for linea in salida.splitlines():
        cabeza, ruta = linea.split('\t', 1)
        resultado[ruta] = cabeza.split()[1]
    return resultado

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--picons', required=True); p.add_argument('--salida', required=True); p.add_argument('--render', required=True)
    a = p.parse_args()
    logos_dir = os.path.join(a.salida, 'logos'); os.makedirs(logos_dir, exist_ok=True)
    fuentes_path = os.path.join(a.salida, 'fuentes.json')
    antes = json.load(open(fuentes_path)) if os.path.exists(fuentes_path) else {}

    # Los logos de Picons: nombre.variante.extensión (si hay SVG y PNG de la misma variante, el SVG; el PNG, de repuesto por si
    # el SVG no se puede pintar).
    elegidos = {}
    repuestos = {}
    for ruta, huella in huellas(a.picons).items():
        fichero = os.path.basename(ruta)
        partes = fichero.split('.')
        if len(partes) != 3 or partes[1] not in VARIANTES or partes[2] not in ('svg', 'png'):
            continue
        clave = partes[0] + '.' + partes[1]
        if partes[2] == 'png':
            repuestos[clave] = (ruta, huella)
        if clave in elegidos and elegidos[clave][0].endswith('.svg'):
            continue
        elegidos[clave] = (ruta, huella)

    ahora = {}
    pendientes_svg, pendientes_png = [], []
    for clave, (ruta, huella) in elegidos.items():
        destino = clave + '.png'
        ahora[destino] = huella
        if antes.get(destino) == huella and os.path.exists(os.path.join(logos_dir, destino)):
            continue
        (pendientes_svg if ruta.endswith('.svg') else pendientes_png).append((os.path.join(a.picons, ruta), os.path.join(logos_dir, destino)))

    # Lo que Picons ya no tiene, fuera.
    for destino in set(antes) - set(ahora):
        try: os.remove(os.path.join(logos_dir, destino))
        except FileNotFoundError: pass

    fallos = set()
    if pendientes_svg:
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.txt') as lista:
            lista.write('\n'.join(f'{o}\t{d}' for o, d in pendientes_svg))
        salida = subprocess.run([a.render, lista.name, str(LADO)], capture_output=True, text=True).stdout
        os.remove(lista.name)
        for linea in salida.splitlines():
            if linea.startswith('fallo\t'):
                fallos.add(os.path.basename(linea.split('\t', 1)[1]).rsplit('.', 1)[0] + '.png')
    for origen, destino in pendientes_png:
        try:
            im = Image.open(origen).convert('RGBA')
            if max(im.size) > LADO:
                s = LADO / max(im.size)
                im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
            im.save(destino, optimize=True)
        except Exception:
            fallos.add(os.path.basename(destino))
    # Los PNG que salen del SVG, también comprimidos.
    for _, destino in pendientes_svg:
        if os.path.basename(destino) in fallos or not os.path.exists(destino):
            continue
        try:
            Image.open(destino).save(destino, optimize=True)
        except Exception:
            fallos.add(os.path.basename(destino))
    # Un SVG que no se puede pintar: su PNG, si Picons lo tiene.
    for f in list(fallos):
        clave = f[:-4]
        if clave in repuestos and elegidos.get(clave, ('',))[0].endswith('.svg'):
            ruta, huella = repuestos[clave]
            try:
                im = Image.open(os.path.join(a.picons, ruta)).convert('RGBA')
                if max(im.size) > LADO:
                    s = LADO / max(im.size)
                    im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
                im.save(os.path.join(logos_dir, f), optimize=True)
                ahora[f] = huella
                fallos.discard(f)
            except Exception:
                pass
    for f in fallos:
        ahora.pop(f, None)
        try: os.remove(os.path.join(logos_dir, f))
        except FileNotFoundError: pass

    # El índice: variantes de cada logo y nombres de canal → logo.
    variantes = {}
    for destino in ahora:
        nombre, variante = destino[:-4].split('.')
        variantes.setdefault(nombre, []).append(variante)
    for v in variantes.values():
        v.sort(key=VARIANTES.index)
    # Logos idénticos con otro nombre (Picons repite algunos): todos sus nombres, al primero. Así cada dibujo tiene UNA sola
    # dirección; varias direcciones con la misma imagen son, para la app, el cartel de un servidor («imagen no disponible»).
    igual_a = {}
    por_contenido = {}
    for nombre in sorted(variantes):
        firma = tuple((v, hashlib.sha256(open(os.path.join(logos_dir, f'{nombre}.{v}.png'), 'rb').read()).hexdigest())
                      for v in variantes[nombre])
        if firma in por_contenido:
            igual_a[nombre] = por_contenido[firma]
        else:
            por_contenido[firma] = nombre
    for nombre in igual_a:
        variantes.pop(nombre)
    nombres = {}
    with open(os.path.join(a.picons, 'build-source', 'snp.index'), encoding='utf-8', errors='ignore') as snp:
        for linea in snp:
            if '=' not in linea: continue
            canal, logo = linea.strip().split('=', 1)
            logo = igual_a.get(logo, logo)
            if logo in variantes and canal:
                nombres[canal] = logo
    for logo in variantes:
        nombres.setdefault(logo, logo)
    for repetido, logo in igual_a.items():
        nombres.setdefault(repetido, logo)
    indice = {'version': 1, 'fuente': 'picons', 'lado': LADO,
              'generado': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d'),
              'logos': dict(sorted(variantes.items())), 'nombres': dict(sorted(nombres.items()))}
    with open(os.path.join(a.salida, 'index.json'), 'w') as f:
        json.dump(indice, f, ensure_ascii=False, separators=(',', ':'))
    with open(fuentes_path, 'w') as f:
        json.dump(dict(sorted(ahora.items())), f, indent=0)
    print(f'logos: {len(ahora)} ficheros, {len(variantes)} distintos ({len(igual_a)} repetidos), {len(nombres)} nombres; rehechos: '
          f'{len(pendientes_svg)} SVG y {len(pendientes_png)} PNG; fallos: {len(fallos)}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
