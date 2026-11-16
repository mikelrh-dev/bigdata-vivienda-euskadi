# Diseño — VPO: unidades, escala y lectura

## Decisión 1 — Serie VPO: escala común + zoom

La figura `S_serie_vpo_2004_2024.png` deja de tener un panel de Araba con
escala propia. Pasa a dos paneles que muestran el mismo dato:

- **Panel izquierdo:** los cuatro territorios en una escala común (0–44 ‰).
  Araba/Álava se ve a su altura real; CAE, Bizkaia y Gipuzkoa quedan abajo.
- **Panel derecho:** zoom 0–14 ‰ de CAE, Bizkaia y Gipuzkoa. No es una escala
  distinta para una entidad: es una ampliación declarada del panel izquierdo.

La figura anota `40,1 ‰ = 4,01 %`, `11,5 ‰ = 1,15 %`, `2,7 ‰ = 0,27 %` y
`3,8 ‰ = 0,38 %`. El pie declara: «‰ = por mil; 1 ‰ = 0,1 %; cada punto
acumula los cinco años anteriores; denominador: población media del quinquenio;
incluye VPO + VVSS».

## Decisión 2 — H5: tasa, no conteo

El título pasa de «Los 15 municipios con más VPO terminada» a «Los 15
municipios con mayor tasa de VPO terminada (‰)». Se añade una nota en el panel:
«Tasa por 1.000 habitantes; no es número de viviendas». El dato disponible en
`pipeline_vpo_terminadas` es la tasa, no el conteo absoluto; no se inventa el
conteo.

## Decisión 3 — Una sola fórmula y una sola conversión

La fórmula canónica se escribe una vez:

> `(VPO + VVSS terminadas en el quinquenio / población media del quinquenio) × 1.000`

Las conversiones se derivan de la tasa, no se teclean:

- `pct = tasa_por_mil / 10`
- `pct_anual = pct / 5`

Los tokens de memoria se calculan en `docs/memoria/build.py --refresh` desde
`data/raw/udalmap_vpo_terminadas.csv`. Así la memoria no contiene cifras
manuales.

## Decisión 4 — Etxebide: registros, no solicitudes

`etxebide_solicitudes.csv` tiene 5.040 filas = 252 municipios × 20 años; cada
fila es una tasa `etxebide_solicitudes_por_mil`. Donde el deck o el guion
decían «5.040 solicitudes» pasa a decir «5.040 registros municipio-año» o
«5.040 documentos». No se estima el número de solicitudes: el CSV no trae el
numerador.

## Regeneración

1. `python transform/generar_figuras_N.py` — serie VPO y sincronización.
2. `python analysis/run_analisis_mongo.py` — H5 desde Mongo.
3. `python scripts/sincronizar_figuras.py` — copias gold → deck/memoria.
4. `python docs/memoria/build.py --refresh --build --pdf` — memoria.
5. Exportar el deck a PDF con Chrome headless.
6. `python scripts/verificar_cifras_deck.py` y `python scripts/verificar_vintage_figuras.py`.

## Riesgos

- El panel izquierdo con escala común comprime las series pequeñas; el zoom
  derecho conserva el detalle. Si el zoom se lee como otra escala, el pie lo
  declara.
- El H5 no puede mostrar viviendas absolutas porque el pipeline no las expone;
  se corrige el título, no se inventa el dato.
- La memoria depende de `_facts.json` para otras cifras; este cambio solo añade
  tokens derivados del CSV raw de VPO.
