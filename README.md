# oneplay-logos

Logos de canales de televisión en alta resolución, con el fondo transparente, para la app **OnePlay**.

## Qué hay

- `logos/<canal>.<variante>.png`: cada logo con su lado mayor a 512 píxeles como mucho. Variantes, como en Picons:
  - `default`: la normal.
  - `light`: para fondos oscuros (si el canal la tiene).
  - `dark`: para fondos claros (si el canal la tiene).
- `index.json`: los nombres de canal (normalizados: minúsculas, sin espacios ni signos, «+» = «plus», «&» = «and») → el logo,
  y las variantes que tiene cada logo.
- `fuentes.json`: la huella del fichero de origen de cada logo, para convertir solo lo que cambia.
- En `index.json` también: `genericos` (palabra de una temática → su logo genérico), `cine` (las palabras de cine) y
  `paises` (el país de los logos oficiales añadidos a mano).

## De dónde salen

Del proyecto [Picons](https://github.com/picons/picons) (licencia GPL-3.0): sus logos en SVG se convierten a PNG con
[SwiftDraw](https://github.com/swhitty/SwiftDraw) (licencia Zlib) y los PNG se reducen a 512 píxeles. Por eso este repositorio
lleva la misma licencia, GPL-3.0 (ver `LICENSE`).

Se actualiza solo una vez por semana (GitHub Actions, `.github/workflows/actualizar.yml`): trae lo nuevo de Picons, convierte
lo que ha cambiado, quita lo que ya no está y sube los cambios. También se puede lanzar a mano desde la pestaña Actions.

Además, lo que añade OnePlay a mano (la tarea semanal no lo toca y lo vuelve a poner en el índice):

- `logos/generico/` y `extra/genericos.json`: los logos **genéricos**, uno por temática y palabra («PELÍCULAS», «COMEDY»,
  «HORREUR», «ФИЛЬМЫ», «أفلام», «영화», «फ़िल्में», «电影»…) para los canales que solo dicen una temática («PELÍCULAS 24/7») y
  para los huecos de eventos de un panel («Evento 05» en la categoría «Baloncesto»). En los idiomas en que escribe un
  panel, cada uno en su escritura. Diseño propio de OnePlay con los iconos de
  [Material Symbols](https://github.com/google/material-design-icons) (Apache 2.0) y la letra
  [Inter](https://github.com/rsms/inter) o, en las escrituras que Inter no tiene,
  [Noto Sans](https://github.com/notofonts) (las dos, SIL OFL 1.1). Se generan con `tools/genericos/coleccion.py`.
- `logos/extra/` y `extra/oficiales.json`: logos oficiales descargados de la web de cada canal, con su país.

Los logos son marcas de sus respectivos propietarios y se usan solo para identificar cada canal.

## Construirlo a mano

```sh
git clone --depth 1 --filter=blob:none --sparse https://github.com/picons/picons.git /tmp/picons
git -C /tmp/picons sparse-checkout set --no-cone /build-source/logos/ /build-source/snp.index
swift build -c release --package-path tools/render
python3 tools/construir.py --picons /tmp/picons --salida . --render tools/render/.build/release/render
```
