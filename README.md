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

## De dónde salen

Del proyecto [Picons](https://github.com/picons/picons) (licencia GPL-3.0): sus logos en SVG se convierten a PNG con
[SwiftDraw](https://github.com/swhitty/SwiftDraw) (licencia Zlib) y los PNG se reducen a 512 píxeles. Por eso este repositorio
lleva la misma licencia, GPL-3.0 (ver `LICENSE`).

Se actualiza solo una vez por semana (GitHub Actions, `.github/workflows/actualizar.yml`): trae lo nuevo de Picons, convierte
lo que ha cambiado, quita lo que ya no está y sube los cambios. También se puede lanzar a mano desde la pestaña Actions.

Los logos son marcas de sus respectivos propietarios y se usan solo para identificar cada canal.

## Construirlo a mano

```sh
git clone --depth 1 --filter=blob:none --sparse https://github.com/picons/picons.git /tmp/picons
git -C /tmp/picons sparse-checkout set --no-cone /build-source/logos/ /build-source/snp.index
swift build -c release --package-path tools/render
python3 tools/construir.py --picons /tmp/picons --salida . --render tools/render/.build/release/render
```
