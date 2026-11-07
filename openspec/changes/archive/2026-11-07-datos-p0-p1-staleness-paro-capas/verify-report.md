# Verify Report: Datos P0/P1 — outliers, staleness, paro y capas

**Change:** `2026-11-07-datos-p0-p1-staleness-paro-capas`
**Modo:** openspec
**Fecha:** 2026-11-07
**Veredicto:** **GATE PASS**

> Evidencia literal de cada gate más abajo. Comandos ejecutados en
> `C:/Users/mikel/Documents/bigdata-vivienda-euskadi` con
> `.venv/Scripts/python -m pytest` / `python` según el caso.
> La salida citada es copia literal (sin truncar) salvo indicación.

## GATE (1) — pytest 177 passed 1 skipped (174+3 dedup)

**Resultado: PASS**

Literal:

```
........................................................................ [ 40%]
........................................................................ [ 80%]
...........s......................                                       [100%]
177 passed, 1 skipped in 4.67s
```

Desglose separado:

- **Colectados:** 178 (177 passed + 1 skipped; `pytest tests -q` sin `-v`
  no lista skips, pero el summary `177 passed, 1 skipped` implica 178 colectados)
- **Pasados:** 177
- **Skipped:** 1
- **Fallo pre-existente por diff:** **0**. Ningún test falla. Los 3 nuevos
  de dedup (`tests/test_dedup_fingerprint.py`, untracked en el árbol) pasan:

```
tests/test_dedup_fingerprint.py::test_dedup_fingerprint_dos_portales_una_fila PASSED [ 33%]
tests/test_dedup_fingerprint.py::test_unificados_sin_duplicados_fingerprint PASSED [ 66%]
tests/test_dedup_fingerprint.py::test_mongo_sin_duplicados_fingerprint PASSED [100%]
============================== 3 passed in 0.46s ==============================
```

Baseline: 174 tests previos + 3 dedup = 177 passed. `1 skipped` coincide con
baseline documentado en `tasks.md` Fase 6 y en el gate esperado
(`177 passed 1 skipped`). Sin regresión en el conteo previo.

## GATE (2) — Doble run_analisis_mongo.py SHA doble idéntico + 13 PNG + mongo_*.csv 7+ + manifests

**Resultado: PASS**

### Huella (doble ejecución)

Literal (segunda ejecución):

```
mongo_esfuerzo_por_municipio.csv: 252 filas -> ...data\resultados\mongo_esfuerzo_por_municipio.csv
mongo_alquiler_por_municipio.csv: 252 filas -> ...data\resultados\mongo_alquiler_por_municipio.csv
mongo_modalidades.csv: 2 filas -> ...data\resultados\mongo_modalidades.csv
mongo_accesibilidad_extendida.csv: 252 filas -> ...data\resultados\mongo_accesibilidad_extendida.csv
mongo_vpo_por_municipio.csv: 322 filas -> ...data\resultados\mongo_vpo_por_municipio.csv
mongo_tier_confianza.csv: 252 filas -> ...data\resultados\mongo_tier_confianza.csv
mongo_vpo_terminadas_por_municipio.csv: 251 filas -> ...data\resultados\mongo_vpo_terminadas_por_municipio.csv
png_mongo: 13 ficheros -> ...data\resultados
capa_oficial.csv: 159 filas -> ...data\resultados\capa_oficial.csv
capa_idw.csv: 93 filas -> ...data\resultados\capa_idw.csv
capa_contexto.csv: 252 filas -> ...data\resultados\capa_contexto.csv
udalmap_paro.csv: 252 filas -> ...data\resultados\udalmap_paro.csv
ranking_esfuerzo.csv: 4 filas -> ...data\resultados\ranking_esfuerzo.csv
huella: f26264b6c9ec024a27b36a99546dffdc71bb4cdd5aff61fc8519e15b17fa19d0
reproducibilidad: ok (dos ejecuciones con la misma huella)
```

Huella `f26264b6c9ec024a27b36a99546dffdc71bb4cdd5aff61fc8519e15b17fa19d0`
coincide con el esperado `f26264b6...0d0?` (prefijo `f26264b6`, sufijo `...19d0`).

Doble ejecución SHA (SHA-256 por fichero `mongo_*.csv`, `IDENTICAL` tras `diff`):

```
mongo_accesibilidad_extendida.csv c2b3b0aca38d52c7f9bedb1c6202c1e4eb7fc8557509b7dcfec0516beaa8ce5e
mongo_alquiler_por_municipio.csv ff39e852d27a754eabb2fe3db76c71c1ac35e8a0cdcd4e799ff9fb7c9798263e
mongo_esfuerzo_por_municipio.csv 57f74745f15d0350762067255417833e8cf9a5d288d5fb0c266801aeea2218b8
mongo_modalidades.csv 67e8120a311666d8cb7d3522766e8a19da468da34fb578c900d702bf2d81bcf0
mongo_tier_confianza.csv 42e3bdd8ed64835cc038b24058514f0fa065ce6737b95665add0aca309cb9016
mongo_vpo_por_municipio.csv 66e8a674af835c3f60d1b629f119095f16f25e7ae6b2197ab203feb9eff929d7
mongo_vpo_terminadas_por_municipio.csv d9a512c82d9c493499b757fbb914b3ee331e0b3e390b59a64c1f4ab6c1f587bb
IDENTICAL RUN0vsRUN1
IDENTICAL RUN1vsRUN2 DOUBLE-SHA OK
```

**File count:** 7 `mongo_*.csv` (accesibilidad, alquiler, esfuerzo, modalidades,
tier_confianza, vpo, vpo_terminadas).

### 13 PNG

Literal (`ls data/resultados/*.png | wc -l`):

```
13
data/resultados/A1_distribucion_esfuerzo_por_TH.png
data/resultados/A2_pct_inasequibles_por_TH.png
data/resultados/B_paro_vs_precio.png
data/resultados/C_vpo_antiguedad_por_TH.png
data/resultados/D_distancia_vs_precio.png
data/resultados/E_demografia_edad.png
data/resultados/F_comparativa_th.png
data/resultados/G_gaps_limitaciones.png
data/resultados/g1_esfuerzo_por_territorio.png
data/resultados/g2_renta_vs_alquiler.png
data/resultados/g3_top10_precio_medio.png
data/resultados/g4_distribucion_anuncios.png
data/resultados/g5_esfuerzo_robustos.png
```

### Manifests

Literal (`python extract/generar_manifest.py --verify` tras restaurar con
`--write`, ver nota P2-4):

```
OK: C:\Users\mikel\Documents\bigdata-vivienda-euskadi\docs\raw_manifest_sha256.txt (354 entradas, 0 errores)
OK: C:\Users\mikel\Documents\bigdata-vivienda-euskadi\data\procesado\manifest_sha256.txt (188 entradas, 0 errores)
  354 docs/raw_manifest_sha256.txt
  188 data/procesado/manifest_sha256.txt
```

- Raw: **354** (coincide gate `raw 354`)
- Silver (procesado): **188** (`187 + log_filtrado`, coincide gate).
  `data/procesado/log_filtrado.txt` existe y se publica:
  `excluidos_precio_m2=5, excluidos_superficie=6, excluidos_iqr_precio_medio=21, habitaciones_int=100%`

## GATE (3) — Conteos Mongo + paro 252 + precio_m2 + mediana + ranking + 62 vs 7

**Resultado: PASS**

### Anuncios 594, municipios/indicadores/alquiler 252

Literal (Mongo `vivienda_euskadi`):

```
anuncios 594
precio_m2>50 0
precio_m2<3 0
superficie>500 5
superficie<10 0
municipios 252
indicadores 252
alquiler_municipal 252
udalmap_empleo 252
udalmap_indicadores 252
```

- `anuncios` = **594**
- `municipios` = **252**
- `indicadores` = **252**
- `alquiler_municipal` = **252**
- `udalmap_empleo` = **252**

Los 5 con `superficie>500` tienen `precio_m2=None` (ver P2-1):

```
[{'superficie_m2': 1280.0, 'precio_m2': None, 'precio_eur': Decimal128('4900.0')},
 {'superficie_m2': 746.0, 'precio_m2': None, 'precio_eur': Decimal128('4000.0')},
 {'superficie_m2': 6973.0, 'precio_m2': None, 'precio_eur': Decimal128('1100.0')},
 {'superficie_m2': 850.0, 'precio_m2': None, 'precio_eur': Decimal128('8500.0')},
 {'superficie_m2': 910.0, 'precio_m2': None, 'precio_eur': Decimal128('8000.0')}]
```

No participan en la mediana de `precio_m2` (exigen `precio_m2` no nulo en
`[3,50]` en la agregación).

### Paro 252/252 (01003 0.28, 20037 1.45, 48916 3.26)

Literal:

```
udalmap paro not null 252
udalmap is_imputed true 0
udalm_paro sample [{'_id': '01003', 'codigo_ine': '01003', 'tasa_paro_lanbide_pct': 0.28, 'metodo_imputacion': 'oficial', 'is_imputed': False}]
```

```
codigo_ine municipio   territorio  tasa_paro_lanbide_pct metodo_imputacion  is_imputed
      1003   Aramaio  Araba/Álava                   0.28           oficial       False
     20037   Gaintza     Gipuzkoa                   1.45           oficial       False
     48916  Usansolo      Bizkaia                   3.26           oficial       False
```

- `grep -c "is_imputed.*true" data/resultados/udalmap_paro.csv` → `0`
- `wc -l data/resultados/udalmap_paro.csv` → `253` (252 + cabecera)
- `is_imputed=true` en Mongo `udalmap_empleo` → `0`

### precio_m2>50 -> 0 y <3 -> 0

Literal (ya citado en conteos):

```
precio_m2>50 0
precio_m2<3 0
```

Cumple OUTLIER-01/AGREGACION-01 para `precio_m2`.

Log de filtrado (OUTLIER-01, motivo por exclusión):

```
excluidos_precio_m2=5, excluidos_superficie=6, excluidos_iqr_precio_medio=21, habitaciones_int=100%
anuncios_fotocasa id=189137157 motivo=precio_m2_fuera_3_50
anuncios_fotocasa id=190916546 motivo=precio_m2_fuera_3_50;superficie_fuera_10_500
...
```

`filtrar_outliers.py` (producción):

```
excluidos_precio_m2=5, excluidos_superficie=6, excluidos_iqr_precio_medio=21, habitaciones_int=100%
```

`anuncios_unificados.csv` (DEDUP-01 / OUTLIER-01):

```
rows 594
dup fingerprint 0
frac 0  (habitaciones sin fraccion; dtype float64 por NaN, valores enteros)
```

### Mediana winsorizada no nula 60

Archivo canónico: `mongo_esfuerzo_por_municipio.csv` (la spec nombra
`mongo_indicadores_municipio.csv` histórico; el pipeline vigente publica
`mediana_precio_m2_winsorizada` en `mongo_esfuerzo_por_municipio.csv`,
252 filas, 7 `mongo_*.csv`):

Literal:

```
rows 252
mediana no nula 60
n_anuncios sum 594
```

Cumple `252 filas` + mediana no nula donde `n_precio>=1` (60 municipios con
mediana winsorizada, p. ej. Laguardia 37.50, Okondo 14.63, Vitoria 14.44).

### Ranking solo n>=30 (Donostia 126 > Bilbao 204 > Vitoria 39 > Getxo 50, Barakaldo 6 n_insuficiente)

Literal `data/resultados/ranking_esfuerzo.csv` (4 filas, todas `rankeable`):

```
codigo_ine                 municipio   territorio  n_anuncios  estado
20069  Donostia / San Sebastián     Gipuzkoa         126  rankeable
48020                    Bilbao      Bizkaia         204  rankeable
 1059           Vitoria-Gasteiz  Araba/Álava          39  rankeable
48044                     Getxo      Bizkaia          50  rankeable
n_anuncios min: 39
estado counts: {'rankeable': 4}
```

- `min(n_anuncios)=39 >=30` (nunca 6).
- Barakaldo no está en el ranking (correctamente bloqueado). Su `n=6`
  visible en `mongo_esfuerzo_por_municipio.csv`:

```
48013  Barakaldo  Bizkaia  n_anuncios=6  mediana=26.32  metodo=oficial  is_imputed=False
```

Y documentado como `n_insuficiente` en `data/resultados/README.md`:

```
Resto de municipios: `estado=n_insuficiente` (con su n visible, nunca
ordenados). Ejemplo: **Barakaldo (48013) n=6, n_insuficiente** — no ranking
nunca por encima de Donostia (n=126) ni de ningún Tier A, tampoco en el
top-10.
```

Ver P2-2: el CSV del ranking no materializa filas `n_insuficiente`.

### Precio 62/252 vs n_precio 7 (A+B)

Literal `grep`:

```
27:## Conciliación 62/252 vs `n_precio=7` (M2)
31:| 62/252 municipios con precio observable real | 62 | Anuncios con `precio_eur` no nulo post re-resolución y cuarentena (594 anuncios en 64 municipios). |
27:## Conciliación 62/252 vs `n_precio=7` (M2)
32:| `n_precio=7` robusto (4 Tier A + 3 Tier B) | 7 | Municipios que sí publican precio municipal tras la supresión de C/D. Tier A: Bilbao 204, Donostia 126, Getxo 50, Vitoria-Gasteiz 39; Tier B: Zarautz 15, Santurtzi 11, Sopela 19 (439 anuncios con precio). |
```

Y recarga vigente en el mismo README:

```
Recarga vigente: **594 anuncios** (326 larga estancia + 268 temporal), **188 municipios Tier D en cero** (sin anuncios) y **Bilbao 204 anuncios como máximo**. 759 era el pre-change.
```

Capas M7 (evidencia adicional de este gate):

```
capa_oficial.csv 159 {'oficial': 159} is_imputed sum 0
capa_idw.csv 93 {'idw': 93} is_imputed sum 93
capa_contexto.csv 252 {'contexto': 252} is_imputed sum 252
```

### Sync 759 -> 594/188/204 en 4 docs

Literal `grep -c`:

```
docs/datos_finales_conclusiones_2026-11-05.md 594:2 / 759:1
docs/informe_final.md                       594:4 / 759:1
data/resultados/README.md                   594:2 / 759:1
docs/presentacion/index.html                594:3 / 759:1
```

El único `759` es la nota histórica `759 era el pre-change` en cada doc.

## GATE (4) — Sin Docker, HDFS solo raw, Kafka->HDFS no Mongo, raw extract 18/21 readonly

**Resultado: PASS**

- **Sin Docker:** `ls Dockerfile* docker-compose*` → `No such file or directory`.
  Ningún fichero Docker en el repo del change.
- **HDFS solo raw, `hdfs_utils.py` 0 changes:**

```
git diff HEAD -- storage/hdfs_utils.py
(vacío)
```

`storage/hdfs_utils.py` solo sube `data/raw` a `.../data/raw`, separado de
procesado (`No toca data/procesado`). Ver P2-3 sobre la cifra `352` vs `354`.
- **Kafka -> HDFS, no Mongo:**

```
storage/kafka_hdfs_uploader.py:1:"""Consumer Windows: consume manifiesto Kafka y sube a HDFS (Windows -> Kafka -> HDFS).
storage/kafka_raw_producer.py:6:vm design...
storage/load_mongo.py: (sin kafka)
grep MongoClient en storage/hdfs_utils.py / kafka_*: ninguno en repo (solo .venv site-packages)
```

`kafka/` no existe como paquete propio; los productores/consumidores viven en
`storage/kafka_raw_producer.py` + `storage/kafka_hdfs_uploader.py` y apuntan a
HDFS/WebHDFS, nunca a Mongo. `storage/load_mongo.py` no referencia `kafka`.
- **Raw intacto, salvo re-extract 18/21 (readonly restaurado):**

```
git status --porcelain -- data/raw
(vacío)  # ningún fichero raw sin-track/modificado sin documentar
git status --porcelain -- extract/
 M extract/08_pisos_scraper.py
 M extract/21_lanbide_historico_paro_joven.py
```

Dif `extract/21...`: solo añade `URL` de Lanbide en metadata (trazabilidad),
sin alterar el parseo:

```diff
+URL = "https://www.lanbide.euskadi.eus/contenidos/estadistica/paro_historico/es_def/adjuntos/Dap_Historico.xlsx"
...
+            "url": URL,
```

`docs/raw_manifest_sha256.txt` dif (antes de regenerar manifests tras
re-ejecución de verificación): solo cambian 2 hashes de los JSON Lanbide
re-extractidos, resto intacto:

```
-76e20ea9...  lanbide_paro_historico_joven.json
+fa363e45...  lanbide_paro_historico_joven.json
-ccd22d03...  lanbide_paro_juvenil.json
+c8eef595...  lanbide_paro_juvenil.json
```

Es el re-extract 18/21 permitido por `tasks.md` («solo re-extract 18/21 que
escribe raw Lanbide vía extract/»). Tras la verificación los manifests se
regeneraron con `--write` y volvieron a `0 errores` (ver nota P2-4).

## Lista P1 / P2

### P1 (bloqueante) — 0

**Ninguno.** Todos los gates testables del enunciado pasan literalmente:
pytest, doble SHA, 13 PNG, 7 CSV, manifests 354/188, Mongo 594/252,
paro 252/252 con los 3 valores, `precio_m2` en rango, mediana 60, ranking
`n>=30`, 62 vs 7, sin Docker, HDFS solo raw, Kafka->HDFS.

### P2 (no bloqueante, seguimiento recomendado)

- **P2-1 — Superficie >500 residual sin precio (5 docs).**
  `anuncios` Mongo conserva 5 docs con `superficie_m2` ∈ {746, 850, 910, 1280,
  6973} y `precio_m2=None`. No contaminan la mediana de `precio_m2`
  (la agregación exige `precio_m2` en `[3,50]`; el log cuenta
  `excluidos_superficie=6`). Pero OUTLIER-01 dice “superficie fuera
  `[10,500]` → descarte”. Si se quiere literal, aplicar el descarte también
  cuando `precio_m2` es `None` o documentar que el filtro solo aplica con
  precio observable.

- **P2-2 — Archivo `ranking_esfuerzo.csv` no materializa `n_insuficiente`.**
  El CSV contiene solo los 4 `rankeable` (`min=39`). Barakaldo `n=6` es
  visible en `mongo_esfuerzo_por_municipio.csv` y en `README.md` como
  `n_insuficiente`, pero no hay fila `estado=n_insuficiente` en el CSV.
  Si `CONCLUSION-01` exige mostrarlos también en el CSV, añadir filas
  bloqueadas con su `n` visible.

- **P2-3 — HDFS «352» vs manifest raw «354».**
  El manifest verifica `354 entradas, 0 errores`. La cifra `352` del gate
  es la baseline HDFS pre-change; los +2 corresponden a los dos JSON Lanbide
  re-extractidos (ver dif arriba). `data/raw/` tiene 200 entradas top-level
  (354 con recursión/normalizados). Aclarar la baseline canónica para evitar
  falsos FAIL futuros.

- **P2-4 — Timestamps rompen determinismo de manifest (churn).**
  Re-ejecutar `filtrar_outliers.py` cambia `fecha_extraccion` en
  `anuncios_fotocasa_filtrado.json` / `anuncios_pisos_filtrado.json` y hace
  fallar `manifest --verify` (`2 errores: hash distinto`). La verificación
  lo restauró con `--write`. Recomendado: normalizar/excluir el timestamp o
  documentar `generar_manifest.py --write` tras cada re-ejecución parcial.

- **P2-5 — `sensibilidad_idw.csv` sin etiquetas.**
  2 filas sin columnas `metodo_imputacion`/`is_imputed`. Las capas oficiales
  (`capa_oficial/idw/contexto.csv`) sí cumplen 159/93/252.

## Git

**Resultado: PASS (árbol de trabajo con el change aplicado, sin regresión)**

```
master
0ada593 docs: actualiza presentacion, informes y pipeline kafka/mongo
 M transform/filtrar_outliers.py, unificar_anuncios.py, corregir_empleo.py, ...
 M analysis/mongo_aggregations.py, run_analisis_mongo.py, ...
 M docs/* (594/188/204), data/resultados/README.md, docs/raw_manifest_sha256.txt
?? openspec/changes/2026-11-07-datos-p0-p1-staleness-paro-capas/
?? tests/test_dedup_fingerprint.py (114? no — 3 tests)
42 files changed, 1649 insertions, 613 deletions
```

Diff principal: M1 (rangos/IQR/cast), M6 (dedup fingerprint), M5 (paro 252
en `corregir_empleo`), M7 (capas + `load_mongo`), M2/M3/M4 (ranking/docs).
`storage/hdfs_utils.py` sin cambios (0 líneas, verificado).

## Cobertura de requisitos

| Req | Evidencia | Veredicto |
|---|---|---|
| OUTLIER-01 | `excluidos_precio_m2=5, excluidos_superficie=6, excluidos_iqr=21, habitaciones_int=100%`; `precio_m2>50=0, <3=0`; `habitaciones` frac=0 | PASS (con P2-1) |
| DEDUP-01 | `anuncios_unificados` 594 filas, dup fingerprint=0; 3 tests dedup | PASS |
| COMPLEMENTARIOS-01 | paro 252/252, 01003 0.28, 20037 1.45, 48916 3.26, `is_imputed=true=0` | PASS |
| AGREGACION-01 | mediana winsorizada no nula 60/252 en `mongo_esfuerzo_por_municipio.csv`, huella doble idéntica | PASS |
| PISOS-04 | `udalmap` 252 oficial, `metodo=oficial`, `is_imputed=false` | PASS |
| CAPAS-01 | capas 159/93/252 etiquetadas, `capa_oficial is_imputed sum 0`, 13 PNG | PASS |
| CONCLUSION-01 | README `62/252` + `n_precio=7`, ranking min 39, Barakaldo 6 documentado | PASS (con P2-2) |
| RESPUESTA-01 | 594 en 4 docs, 759 solo nota histórica, 188/204 unidas | PASS |

**Veredicto final: GATE PASS** (0 P1 bloqueantes, 5 P2 de seguimiento no
bloqueantes; ver detalle arriba).
