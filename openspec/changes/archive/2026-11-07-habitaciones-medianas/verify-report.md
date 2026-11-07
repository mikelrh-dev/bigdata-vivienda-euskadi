# Verify Report 2026-11-07-habitaciones-medianas — Habitaciones medianas

**Fecha (UTC+1):** 2026-11-08  
**Change:** `openspec/changes/2026-11-07-habitaciones-medianas/` (`proposal.md`, `specs/mongodb-y-analisis/spec.md` — HAB-01, `specs/presentacion-de-resultados/spec.md` — `chart_habitaciones_medianas`, `tasks.md` §§1-4)  
**Ámbito de la verificación (fuera de los dos `tasks.md`):** solo sobre el árbol de trabajo actual de `C:\Users\mikel\Documents\bigdata-vivienda-euskadi` (rama `main`, HEAD `0ada593`). No se edita `tasks.md` ni las specs; se redacta este `verify-report.md`.

## Veredicto

### GATE PASS — implementación de datos + gráfico (con 4× P1 de redacción de la spec pendientes, que **no** bloquean el código pero sí bloquean la conformidad literal con el texto actual de `proposal/spec/tasks`)

### GATE FAIL — conformidad literal palabra-por-palabra con el texto vigente de `proposal.md` / `specs/.../spec.md` / `tasks.md` (sección «Hallazgos P1»)

Ambas lecturas se dan para no ocultar la diferencia: **lo implementado y regenerado es verde y reproducible; lo redactado en la spec no siempre coincide con lo que el dato real dice** (200 ≠ 201; 60 ≠ 62; 2 diffs de manifiesto de raw; PNG 13 emitidos vs 12 canónicos). La salida de los P1 es, en su totalidad, de **corrección de texto / fragilidad pre-existente**, no de falta de cumplimiento de código en `pipeline_habitaciones_por_municipio` / `chart_habitaciones_medianas`.

---

## (1) GATE — `pytest` vía `.venv/Scripts/python -m pytest tests -q`: **177 passed, 1 skipped** (antes y después del doble run, restaurando el estado canónico de PNG)

### Comando y salida literal (re-ejecutado el 2026-11-08; `.venv` `Python 3.12.10`, `pytest-9.1.1`)

```
.venv/Scripts/python -m pytest tests -q
........................................................................ [ 40%]
........................................................................ [ 80%]
...........s......................                                       [100%]
177 passed, 1 skipped in 5.44s
```

Verificación con detalle del skip:

```
.venv/Scripts/python -m pytest tests -q -rs
...
SKIPPED [1] tests\test_pisos_ubicacion_real.py:245: skip separado: MONGO_ALLOW_DESTRUCTIVE!=1
177 passed, 1 skipped in 5.57s
```

- Esperado en `tasks.md` §4: *«esperado 177 passed, 1 skipped (actual confirmado 2026-11-08)»* — coincide **literalmente** en conteo, porcentaje e identidad del skip (test destructivo `MONGO_ALLOW_DESTRUCTIVE`, separado por diseño).
- **Fallos pre-existentes atribuidos por diff, no por `git stash`:** la primera ejecución fueron `177 passed, 1 skipped` **sin ningún fallo**; por tanto no hay fallo con el que atribuir. Tras el doble `run_analisis_mongo.py` (§2), el disco pasa a **13 PNG** (emite `g1` además de `A1`) y la re-ejecución entonces da temporalmente:

```
FAILED tests/test_pisos_ubicacion_real.py::test_resultados_13png_7csv - AssertionError: assert 13 == 12
1 failed, 176 passed, 1 skipped
```

Ese `1 failed` es **pre-existente y ajeno a habitaciones** (ver P1-3): el propio test y `README.md:166` declaran la convención *«12 PNG únicos (13 emitidos; g1 duplicado de A1 eliminado sin renumerar)»* (`g1` y `A1` byte-idénticos, SHA `25948f0f6bf37862f71fc3892a58e1036f08e7dd407ac6e2d200e4461b48e8f9`, 21 327 bytes; `run_analisis_mongo.py:440` emite ambos). Tras eliminar el duplicado `g1_esfuerzo_por_territorio.png` (canónico) la suite vuelve a `177 passed, 1 skipped`. No se pudo recurrir a `git stash` porque el árbol está sucio con renombres masivos a `archive/` (120 ficheros) y `data/resultados/*` está git-ignorado (`git ls-files data/resultados/` solo devuelve `.gitkeep`); por ello la atribución se hace **por inspección de diff y por la propia declaración del test/README**, según la norma aplicable del `verification-gate`.

---

## (2) Doble `run_analisis_mongo.py` + SHA doble + 9 filas + PNG/SVG — idéntico

### Ejecución literal (dos ejecuciones externas; el propio orquestador imprime la huella interna de dos ejecuciones)

```
.venv/Scripts/python analysis/run_analisis_mongo.py
explain before: stage=COLLSCAN nReturned=0 totalDocsExamined=594 totalKeysExamined=0
explain after: stage=IXSCAN nReturned=0 totalDocsExamined=0 totalKeysExamined=0
explain filtro: {'ubicacion.codigo_ine': '48001', 'modalidad': 'larga_estancia', 'precio_eur': {'$lte': Decimal128('1000')}}
mongo_esfuerzo_por_municipio.csv: 252 filas -> ...\data\resultados\mongo_esfuerzo_por_municipio.csv
mongo_alquiler_por_municipio.csv: 252 filas -> ...\data\resultados\mongo_alquiler_por_municipio.csv
mongo_modalidades.csv: 2 filas -> ...\data\resultados\mongo_modalidades.csv
mongo_accesibilidad_extendida.csv: 252 filas -> ...\data\resultados\mongo_accesibilidad_extendida.csv
mongo_vpo_por_municipio.csv: 322 filas -> ...\data\resultados\mongo_vpo_por_municipio.csv
mongo_tier_confianza.csv: 252 filas -> ...\data\resultados\mongo_tier_confianza.csv
mongo_vpo_terminadas_por_municipio.csv: 251 filas -> ...\data\resultados\mongo_vpo_terminadas_por_municipio.csv
mongo_habitaciones_por_municipio.csv: 9 filas -> ...\data\resultados\mongo_habitaciones_por_municipio.csv
png_mongo: 13 ficheros -> ...\data\resultados
capa_oficial.csv: 159 filas -> ... / capa_idw.csv: 93 / capa_contexto.csv: 252 / udalmap_paro.csv: 252 / ranking_esfuerzo.csv: 4
pipelines: ['pipeline_indicadores_municipio', 'pipeline_alquiler_por_municipio', 'pipeline_modalidades', 'pipeline_top_municipios_por_esfuerzo', 'pipeline_esfuerzo_por_sexo', 'pipeline_accesibilidad_extendida', 'pipeline_udalmap_extendido_osrm', 'pipeline_vpo_por_municipio', 'pipeline_vpo_terminadas', 'pipeline_tier_por_municipio', 'pipeline_habitaciones_por_municipio']
n={'pipeline_indicadores_municipio': 252, 'pipeline_alquiler_por_municipio': 252, 'pipeline_modalidades': 2, 'pipeline_top_municipios_por_esfuerzo': 4, 'pipeline_esfuerzo_por_sexo': 252, 'pipeline_accesibilidad_extendida': 252, 'pipeline_udalmap_extendido_osrm': 252, 'pipeline_vpo_por_municipio': 322, 'pipeline_vpo_terminadas': 251, 'pipeline_tier_por_municipio': 252, 'pipeline_habitaciones_por_municipio': 9}
huella: 0f15c729901693ba5cc925d5241140c2bb83251ff0763b813f30865dcff76daa
reproducibilidad: ok (dos ejecuciones con la misma huella)
```

Segunda ejecución externa idéntica (`huella` y stdout iguales).

### SHA256 literal — doble run idéntico (externo, ficheros en `data/resultados/`)

| Fichero | SHA256 (completo, ambas ejecuciones) | Longitud |
|---|---|---|
| `mongo_habitaciones_por_municipio.csv` | `35bcd8699c67bff4ae9b9ab0d6601f7d27e47f78099861b6db2b26a7866e5696` | 400 |
| `mongo_tier_confianza.csv` | `b8411b77fdfa8df60b06618883dc05ee6bd04699b319b3dbb6b28ee9a8103015` | 19 469 |
| `mongo_esfuerzo_por_municipio.csv` | `7f813fd61ee6800dacd24a230aaef43a8d97e9dbe1abd0300fa1da5b974f75a3` | 64 125 |
| `mongo_alquiler_por_municipio.csv` | `ff39e852d27a754eabb2fe3db76c71c1ac35e8a0cdcd4e799ff9fb7c9798263e` | 11 164 |
| Huella interna `huella_resultados` (11 pipelines) | `0f15c729901693ba5cc925d5241140c2bb83251ff0763b813f30865dcff76daa` | — |

Coinciden **literalmente** con los prefijos esperados de la petición (`35bcd869…`, `b84111…`, `7f81…`, `0f15c729…`) y con la precondición de `tasks.md`: `diff` entre las dos capturas SHA = `DOBLE RUN SHA IDENTICO OK`.

### `mongo_habitaciones_por_municipio.csv` — 9 filas, pero **suma correcta `n=201` / `n_precio=200` (no 201)** (ver P1-1)

Encabezado literal (con BOM UTF-8, como el resto de `mongo_*.csv`):

```
municipio,n,n_precio,min_precio_eur,max_precio_eur,mediana_precio_eur,codigo_ine
```

Contenido re-ordenado por `n` descendente (`codigo_ine` normalizado, no texto; 9 filas, 9 `codigo_ine` únicos):

| municipio | codigo_ine | n | n_precio | min | max | mediana |
|---|---|---|---|---|---|---|
| Bilbao | 48020 | 96 | 96 | 400 | 3400 | 600 |
| Donostia - San Sebastián | 20069 | 66 | 66 | 470 | 7700 | 1200 |
| Vitoria - Gasteiz | 01059 | 12 | 12 | 240 | **109000** | 400 |
| Barakaldo | 48013 | 11 | 11 | 350 | 2000 | 500 |
| Getxo | 48044 | 8 | 8 | 400 | 2700 | 700 |
| Irun | 20045 | 3 | 3 | 400 | 500 | 450 |
| Errenteria | 20067 | 2 | 2 | 385 | 2500 | 2500 |
| Durango | 48027 | 2 | **1** | 1650 | 1650 | 1650 |
| Eibar | 20030 | 1 | 1 | 390 | 390 | 390 |
| **Total** | | **201** | **200** | | | |

Fuente cruda que lo acredita (procesado, 201 filas, Variantes por texto 60+6 Donostia y 10+2 Vitoria confirmando la necesidad de agrupar por `codigo_ine`):

```
data/procesado/anuncios_habitaciones_unificados.csv → 201 filas
Durango 48027 en procesado: (1) precio_eur='1650' (fotocasa 186587570), (2) precio_eur='' (fotocasa 187607209, None)
→ Durango n=2, n_precio=1; el anuncio sin precio no entra en min/max/mediana («mediana cruda, sin imputar», correcto)
```

La pipeline `pipeline_habitaciones_por_municipio` (`analysis/mongo_aggregations.py`) agrupa por `codigo_ine` con `$group`, calcula `n_precio = sum(precio_eur != None)`, `precios = push (solo precio != None)`, mediana con `$arrayElemAt[floor(n_precio/2)]` sobre precios ordenados (mediana «alta» del centro en n par — Errenteria n=2 → 2500, ver P2-3). No hay winsorización ni imputación comarcal/IDW.

### 13 PNG regenerados (+ 12 canónicos tras dedup) y 4ª gráfica SVG

- Emisión de `run_analisis_mongo.py` (`png_mongo: 13 ficheros`): `A1 A2 B C D E F G g1 g2 g3 g4 g5` — lista literal tras la ejecución: `A1_distribucion_esfuerzo_por_TH.png, A2_pct_inasequibles_por_TH.png, B_paro_vs_precio.png, C_vpo_antiguedad_por_TH.png, D_distancia_vs_precio.png, E_demografia_edad.png, F_comparativa_th.png, G_gaps_limitaciones.png, g1_esfuerzo_por_territorio.png, g2_renta_vs_alquiler.png, g3_top10_precio_medio.png, g4_distribucion_anuncios.png, g5_esfuerzo_robustos.png`
- Estado canónico entregado (tras eliminar el duplicado `g1` byte-idéntico a `A1`, según README/test): **12 PNG**. Antes del primer doble run el disco ya estaba en 12 (por eso `177 passed` inmediato).
- `docs/presentacion/assets/` — **11 SVG**, de los que **4 son `chart_*`**: `chart_effort_vs_n.svg, chart_habitaciones_medianas.svg, chart_mapa_tier.svg, chart_tierB_range.svg`. La **4ª gráfica** es `chart_habitaciones_medianas.svg` (`def chart_habitaciones_medianas(habitaciones, tier)` en `build_presentacion.py`).
- `build_presentacion.py` se ejecutó vía `.venv/Scripts/python docs/presentacion/build_presentacion.py`:

```
tramos: {'< 25 %': 54, '25-30 %': 65, '> 30 %': 40} | idw: 93
OK index.html (29525 bytes) y 11 SVG en ...\docs\presentacion\assets
oficial: 26,61 % · 40/159 > 30
global: 25,37 % · 47/252 > 30
decor: topo + trama de 594 anuncios
```

- Etiquetado visual de `chart_habitaciones_medianas.svg` (`<text>` extraídos del SVG):

```
Bilbao (n=96 · firme) / Donostia-San Sebastián (n=66 · firme) / Vitoria-Gasteiz (n=12 · indicativo) / Barakaldo (n=11 · indicativo) / Getxo (n=8 · indicativo) / Irun (n=3 · indicativo) / Errenteria (n=2 · indicativo) / Durango (n=1 · indicativo) / Eibar (n=1 · indicativo)
600 (n_precio=96) min–max 400–3400 / 1200 (n_precio=66) min–max 470–7700 / 400 (n_precio=12) min–max 240–109000 / 500 (n_precio=11) min–max 350–2000 / 700 (n_precio=8) min–max 400–2700 / 450 (n_precio=3) min–max 400–500 / 2500 (n_precio=2) min–max 385–2500 / 1650 (n_precio=1) min–max 1650–1650 / 390 (n_precio=1) min–max 390–390
leyenda de serie: habitaciones / residencia temporal / residencia larga
pie: 'firme solo Bilbao (96) y Donostia (66) n≥30 · resto indicativo n_insuficiente, sin ranking'
pie: 'temporal y larga nunca se promedian · habitaciones: mediana + min–max + n_precio'
```

Solo Bilbao y Donostia `n_precio ≥ 30` son firmes; el resto es `indicativo`/`n_insuficiente`, sin ranking (el SVG contiene la palabra `ranking` solo en la leyenda «sin ranking»). Para Bilbao/Donostia la residencia también se dibuja por separado con su `n_precio` (p. ej. `1550 (n_precio=122)` temporal / `1700 (n_precio=68)` larga); para el resto dice `sin precio municipal` (por Tier C/D). Vitoria max 109 000 se conserva tal cual (outlier crudo, sin winsorizar — coherente con la spec, pero a anotar para el lector, P2-4).

- `index.html` y `index.template.html` incluyen la gráfica:

```
<img src="assets/chart_habitaciones_medianas.svg" alt="Comparación residencia vs habitaciones por municipio">
<figcaption>mediana residencia temporal y larga por separado + mediana habitaciones con min–max y n_precio · solo Bilbao y Donostia firmes</figcaption>  (sección «Habitación vs vivienda entera», slide 9/15)
```

La función lee ambos CSV desde `data/resultados/` y no hay valores tecleados (`mongo_habitaciones_por_municipio.csv` + `mongo_tier_confianza.csv`).

- PDF: `docs/presentacion/presentacion.pdf` está modificado vs `HEAD` (`5 056 418 → 7 686 509 bytes`; `/Image 231 → 279`, `/XObject 83 → 103`; timestamp `2026-11-08 00:35`, posterior al SVG `00:35` y regenerado con el comando Chrome headless documentado en `docs/presentacion/README.md`, no por `build_presentacion.py`). La inclusión textual no es extraíble por fuentes subset (descompresión de 108 streams, 25 773 305 bytes con 0 menciones legibles de `habitaciones/Bilbao/Donostia` en texto plano) — se trata como verificación indirecta + P2-2.

---

## (3) Tier intacto (252, A4/B3/C57/D188) y pipeline nº 11 sin tocar los 10 anteriores

### `mongo_tier_confianza.csv` — intacto **a hash y a distribución**

```
252 filas. tier = {'D': 188, 'C': 57, 'A': 4, 'B': 3}
territorio = {'Bizkaia': 113, 'Gipuzkoa': 88, 'Araba/Álava': 51}
n_anuncios suma 594 = A419 + B45 + C130 + D0 (Bilbao 204, Donostia 126, Getxo 50, Vitoria-Gasteiz 39 — únicos Tier A)
n_precio suma 439 = A398 + B41; solo 7 filas n_precio>0 (Tier A/B), 245 filas en 0 (C/D, sin precio municipal)
```

Distribution `A4/B3/C57/D188` and 252 rows coincide with scenario *Tier y precio intactos* de HAB-01 y con el hash esperado `b8411b77…`. No hay ranking Tier <30: `n_precio=0` con min/max/mediana vacíos en C/D, `tier_etiqueta` 4 `fuerte` / 3 `indicativo` / 57 `sin precio municipal` / 188 `sin dato (+ contexto oficial)`.

Nota de línea base de git (importante): `data/resultados/*` es `.gitignore` (`git ls-files` solo `.gitkeep`); en `HEAD:0ada593` la pipeline Tier `pipeline_tier_por_municipio` aún **no existe** (9 pipelines) y `mongo_tier_confianza.csv` no está versionado. La página actual por tanto **no se puede difuminar Tier contra `HEAD`**; se verificó contra el **hash y la distribución esperados** + el contenido literal del CSV. Toda la intervención de habitaciones sobre lo anterior
se probó como **aditiva**: el hash de Tier tras el doble run es byte-idéntico al esperado, luego habitaciones no alteró su salida.

### `precio municipal 62/252` — **desviación literal (60 sobre 252 ahora)** (ver P1-2)

`mongo_esfuerzo_por_municipio.csv` (SHA `7f813fd…` esperado) hoy da:

```
precio_medio_eur no-nulo: 60 / 252 (no 62)
n_anuncios>0: 64; 4 con anuncios pero n_anuncios_filtrados=0 y precio null tras el filtro M1: 01002 Amurrio, 20040 Hernani, 48003 Amorebieta-Etxano, 48083 Ortuella
n_precio>0: 7 (solo Tier A/B)
```

Los documentos (`README.md:146`, `docs/conclusiones_municipios.md:32`, `openspec/specs/mongodb-y-analisis/spec.md:426`) afirman `62/252` «post 2026-11-07» antes del filtro W/M1 del `pipeline_indicadores_municipio` presente en el árbol apilado. Si se exige **62 literal**, el gate en esa lectura es FAIL; el código de habitaciones no es la causa (ver P1-2).

### Pipeline nº 11 — orden literal, sin reordenar los 10 anteriores

`PIPELINE_ORDER` en `analysis/run_analisis_mongo.py` (hoy):

```
"pipeline_indicadores_municipio"      (1)
"pipeline_alquiler_por_municipio"     (2)
"pipeline_modalidades"                (3)
"pipeline_top_municipios_por_esfuerzo" (4)
"pipeline_esfuerzo_por_sexo"          (5)
"pipeline_accesibilidad_extendida"    (6)
"pipeline_udalmap_extendido_osrm"     (7)
"pipeline_vpo_por_municipio"          (8)
"pipeline_vpo_terminadas"             (9)
"pipeline_tier_por_municipio"         (10)
"pipeline_habitaciones_por_municipio" (11)  ← nuevo
```

Los primeros 10 son **exactamente** la lista de `tasks.md` §2 (9 clásicas + `pipeline_tier_por_municipio`), sin desplazamiento ni reorden. `CSV_POR_PIPELINE = EXPORTS_7 + ("mongo_habitaciones_por_municipio.csv", "pipeline_habitaciones_por_municipio")` (`EXPORT_HABITACIONES`, `exportar_habitaciones_csv`). `pipeline_habitaciones_por_municipio` es función pública en `analysis/mongo_aggregations.py` (no hay `__all__` en el módulo, como en el resto). Advertencia de línea base (P2-6): en `HEAD` eran **9** pipelines; Tier entró como nº 10 en el mismo árbol apilado antes de habitaciones, junto con cambios M1 a `pipeline_indicadores_municipio` / `pipeline_top_municipios_por_esfuerzo` / `pipeline_vpo_por_municipio` **ajenos a habitaciones** (ver diffs en el apartado Detalle de diffs). Habitaciones como incremento es puramente aditivo.

---

## (4) Arquitectura — sin Docker, HDFS solo raw (352), Kafka → HDFS (nunca Kafka → Mongo), raw y ranking

- **Sin Docker (nuevo):** `git diff HEAD --name-only` no contiene ningún `Dockerfile` / `docker-compose*` (búsqueda `docker` = 0) y no existe `docker-compose.yml` ni `Dockerfile` en la raíz (los únicos `Dockerfile*` en el árbol están dentro de `.venv/.../typeshed/stubs/`). La mención de Docker en `.env` («MongoDB (Docker en Windows)» / «HDFS (Docker en Windows)») es **pre-existente**, no introducida por habitaciones; habitaciones no crea ni re-quiere Docker para funcionar (Mongo local + `.venv`).
- **HDFS solo raw (352 ficheros):** doc-evidencia (`README.md:101/108/136/254`, `docs/arquitectura_datos.md`, `AGENT.md:9`): HDFS solo `data/raw` en `/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw` (352 ficheros publicados **sin legacy**: 356 en disco local − 4 legacy); `data/procesado/` (188) no se sube por decisión firmada 2026-11-05. Manifiesto local `docs/raw_manifest_sha256.txt` **354 entradas** (= 356 en disco − `.FROZEN` − `.gitkeep`, incluye los 4 legacy; HDFS 352 = sin legacy). **No se hizo consulta live a HDFS** (`10.22.87.215:50070`) en esta verificación (ver P2-5).
- **Kafka → HDFS, nunca Kafka → Mongo:** `storage/kafka_hdfs_uploader.py` (`mongo 0 / hdfs 21`, grupo `hdfs_centro`, topic `anuncios_inmobiliarios`, broker centro, solo `type: raw_manifest`, put WebHDFS) y `storage/kafka_raw_producer.py` (`mongo 0`). El único consumidor Kafka → Mongo vive en `archive/kafka_2026-11-06/storage_kafka_consumer.py` (archivador, fuera del flujo activo y del diff). El cambio de habitaciones **no añade ningún conector Kafka → Mongo** (diff sin nombres Kafka).
- **Raw — integridad intacta; «0 diffs vs HEAD» no literal (2 diffs ajenos, P1-4):** `git diff HEAD -- docs/raw_manifest_sha256.txt` muestra **2 líneas** cambiadas: `lanbide_paro_historico_joven.json 76e20ea9 → fa363e45` y `lanbide_paro_juvenil.json ccd22d03 → c8eef595`. La integridad contra el disco actual es completa (`tests/test_raw_inmutable.py`: 4 passed; manifiesto 354 = disco 354, 0 errores). El origen de los 2 diffs es `extract/21_lanbide_historico_paro_joven.py` (modificado en el árbol apilado), no habitaciones.
- **Tier sin ranking <30:** `pipeline_indicadores_municipio` y `pipeline_top_municipios_por_esfuerzo` filtran `n_anuncios ≥ 30` (`$match {$gte: 30}`); `ranking_esfuerzo.csv` = **4 filas, todas `rankeable`**: Donostia 126, Bilbao 204, Vitoria-Gasteiz 39, Getxo 50 (Barakaldo n=6 explícitamente fuera). `mongo_tier_confianza.csv` no ordena municipios <30 (Tier B `indicativo`, C/D sin precio). Habitaciones respeta la misma regla: `firme` solo si `n_precio ≥ 30` (Bilbao 96, Donostia 66), resto `indicativo`/`n_insuficiente`.

---

## Cobertura de escenarios de spec

### HAB-01 (`specs/mongodb-y-analisis/spec.md`)

| Scenario | Estado | Evidencia |
|---|---|---|
| Nueve filas con suma 201 | **Parcial — suma real `n=201`, `n_precio=200`** (P1-1) | CSV 9 filas, `n` 96/66/12/11/8/3/2/2/1; Durango `n_precio=1` |
| Doble ejecución idéntica | **Cumple** | SHA doble idéntico `35bcd869…`; huella `0f15c729…` `reproducibilidad: ok` |
| n<30 sin ranking ni imputación | **Cumple** | Eibar `n_precio=1`, `n_insuficiente`, sin ranking; sin imputación comarcal/IDW; `pytest 177/1` |
| Tier y precio intactos | **Cumple a hash/distribución; desviación literal 62→60** (P1-2) | Tier 252 A4/B3/C57/D188 SHA `b8411b77…` |

### `chart_habitaciones_medianas` (`specs/presentacion-de-resultados/spec.md`)

| Scenario | Estado | Evidencia |
|---|---|---|
| Tres series con n_precio visible | **Cumple** (SVG + `index.html`) | 3 series separadas, `n_precio` + min–max en cada barra; `index.html` + plantilla con `<img>` |
| Solo Bilbao y Donostia firmes | **Cumple** | `firme solo Bilbao (96) y Donostia (66) n≥30`; resto `indicativo` |
| Eibar indicativo sin imputación | **Cumple** | Eibar `390 (n_precio=1) min–max 390–390`, `indicativo`, sin imputación |

---

## Hallazgos

### P1 (deben corregirse en texto / decisiones antes de archivar el change como cumplido literalmente)

- **P1-1 — La spec afirma `suma n_precio = 201`; el dato real es `n=201`, `n_precio=200`.** `proposal.md:4,10,38,54`, `spec.md:17 (Scenario Nueve filas)` y `tasks.md §1/§4` deben corregirse a `n=201 / n_precio=200 (Durango 1 sin precio)` o reinterpretarse como `n=201`. El código es correcto: `n_precio` excluye `precio_eur = None` (1 anuncio Durango `187607209`). Es el **único punto en el que la implementación es correcto y la spec es incorrecta**. No se ha corregido la spec en esta verificación por alcance (estrictamente informe); el archivado exige esa enmienda.
- **P1-2 — «Precio 62/252» no se sostiene en el árbol actual (60/252).** Tras el filtro M1/IQR de `pipeline_indicadores_municipio` (cambio apilado ajeno a habitaciones), 4 municipios con anuncios quedan sin precio (`n_anuncios_filtrados=0`): 64 → 60. La frase «62/252 intacto» en `proposal.md:5,20,57`, HAB-01 y `README` queda obsoleta o exige redefinir *precio observable* (frente a `n_precio=7` de Tier). Si el criterio de aceptación literal es 62, el gate es FAIL; a hash/distribución Tier, es PASS. Exige decidir y re-emitir la cifra canónica.
- **P1-3 — Fragilidad PNG 12 vs 13 (test rojo tras cualquier doble run fiel).** `run_analisis_mongo.py` emite 13 (incluye `g1` duplicado de `A1`, SHA `25948f0f…`); `tests/test_pisos_ubicacion_real.py::test_resultados_13png_7csv` y `README.md:166` exigen 12 únicas. Cualquier regeneración completa (como la exigida por `tasks.md §4`) rompe la suite hasta eliminar `g1` a mano. Corrección recomendada: que la pipeline **deje de emitir el duplicado** (`run_analisis_mongo.py:440` `for nombre in ("g1_...", "A1_...")`) o que el test acepte 13 con dedup. Hoy el verde `177` depende de un borrado manual.
- **P1-4 — «Raw 0 diffs» no literal (2 diffs de manifiesto vs `HEAD`).** Los 2 hashes `lanbide_*` cambiaron por `extract/21_lanbide_historico_paro_joven.py` (ajeno a habitaciones). La integridad raw (`test_raw_*`) es verde; la conformidad «0 diffs» exigiría revertir o aislar ese cambio del árbol apilado. En la revisión de habitaciones aislada, habitaciones **no** toca `data/raw` (sin diffs de raw atribuibles al cambio).

### P2 (útiles / no bloqueantes para habitaciones)

- **P2-1 — El SVG no es byte-determinista entre builds** (`dc:date` de matplotlib + ids aleatorios): SHA `e4800177…` → `81bb286e…` → `47816517…` en builds consecutivos, aunque los `<text>` son idénticos. La reproducibilidad exigible con hash byte-exacto vale para los CSV (`35bcd869…` etc.) pero no para el SVG; debe leerse como «contenido determinista» para gráficas.
- **P2-2 — PDF sin verificación textual:** por fuentes subset de Chrome no se puede buscar «habitaciones» en el PDF descompiendo streams. La evidencia es indirecta (fuente `index.html` con el `<img>`, crecimiento `5,05 → 7,68 MB`, `/Image 231 → 279`, slide 9/15 «Habitación vs vivienda entera» con `chart_habitaciones_medianas.svg`). Recomendable una comprobación visual (captura de la slide 9 o render de página) antes de cerrar.
- **P2-3 — Definición de mediana en n par:** `floor(n/2)` (mediana alta), p. ej. Errenteria (385, 2500) → 2500; con n=2 la mediana coincide con el máximo. Es coherente con la pipeline Tier, pero el gráfico no lo declara; el lector puede leer «2500» como media típica.
- **P2-4 — Outliers crudos (sin winsorizar) visibles:** Vitoria max `109 000 EUR` (probablemente error de campo) permanece en el rango min–max aunque la mediana (400) no se ve afectada. La spec lo exige («cruda, sin winsorizar»), pero conviene un pie/footnote en el deck.
- **P2-5 — HDFS 352 no verificado en vivo:** confirmado solo documentalmente (README/arquitectura/manifiesto). Sin consulta a `10.22.87.215:50070` no se hace afirmación de estado en tiempo real de HDFS.
- **P2-6 — Árbol apilado vs línea base Git:** `HEAD` tiene 9 pipelines; el árbol tiene 11 + cambios M1 a indicadores/top/vpo/transform/extract. La afirmación «sin tocar los 10 actuales» solo es verificable contra el baseline de trabajo (hash + orden literal, §3), no contra `HEAD`. Para un cierre auditable se necesita un commit previo que congele «los 10» y un diff aislado de habitaciones (hoy imposibles por `data/resultados/*` ignorado y renombres masivos).
- **P2-7 — Etiqueta `n` ambiguo en el gráfico:** las etiquetas de municipio usan `n = n_precio` (Durango `n=1`), mientras que `tasks.md` habla de Durango 2 (es su `n`). El brazo `n_precio=1 min–max 1650–1650` lo aclara, pero la yuxtaposición `n`/`n_precio` puede confundir.

---

## Detalle de diffs (para atribución pre-existente)

`git -C . diff --stat HEAD` (relevante a habitaciones; resto del árbol apilado se omite):

```
analysis/mongo_aggregations.py          | 287 ++++ (Tier + Habitaciones nuevas; M1 en indicadores/top/vpo — apilado ajeno)
analysis/run_analisis_mongo.py          | 170 ++++ (PIPELINE_ORDER 9→11, EXPORT_TIER + EXPORT_HABITACIONES, extras)
docs/presentacion/build_presentacion.py | 428 ++++ (chart_habitaciones_medianas nuevo + chart_effort_vs_n/mapa_tier/B_range)
docs/presentacion/index.template.html   | 106 ++++ (sección habitaciones + gráficas)
```

- `PIPELINE_ORDER` HEAD (9): `indicadores, alquiler, modalidades, top_esfuerzo, esfuerzo_sexo, accesibilidad, udalmap, vpo_municipio, vpo_terminadas` → HOY (11): los 9 + `tier` (10) + `habitaciones` (11), mismo orden de los 9.
- `pipeline_habitaciones_por_municipio` (+ `pipeline_tier_por_municipio` + `_tier_expr` + helpers): **adición neta** al final del módulo (≈190 líneas), sin modificar cuerpos existentes de Tier. Las modificaciones a `pipeline_indicadores_municipio` (winsor p1-99, IQR, filtro M1, Tier-in-indicadores), `pipeline_top_municipios_por_esfuerzo` (`n≥30`) y `pipeline_vpo_por_municipio` (`promociones_con_viviendas`) pertenecen al apilado **AGREGACION-01/M3** anterior a habitaciones y no los re-auditó este change (fuera de alcance), pero explican P1-2.

## Ficheros (re)gados por esta verificación

- `data/resultados/mongo_habitaciones_por_municipio.csv` (9 filas, SHA `35bcd869…`), `mongo_tier_confianza.csv` (252, `b8411b77…`), `mongo_esfuerzo_por_municipio.csv` (`7f813fd…`), `mongo_alquiler_por_municipio.csv` (`ff39e852…`) y resto de `mongo_*.csv`/PNGs regenerados por el doble run ( estado canónico restaurado a 12 PNG tras dedup `g1`).
- `docs/presentacion/assets/chart_habitaciones_medianas.svg` (reescrito en cada `build_presentacion.py`; SHA varía por timestamp, contenido verificado) + `index.html` (29525 bytes declarados por el build; fichero en disco 30228 bytes a la última lectura — incluir la magnitud exacta en el cierre).
- **Este informe:** `openspec/changes/2026-11-07-habitaciones-medianas/verify-report.md`.

## Qué no cubre este gate

- Estado en vivo de HDFS/Mongo/Kafka (`10.22.87.215`): no se contactó HDFS en esta verificación; Mongo sí se ejerció (pipelines + `explain COLLSCAN → IXSCAN`).
- Comprobación visual píxel a píxel del slide de habitaciones en el PDF (P2-2) y de la salida impresa de 13,33×7,5 in.
- Auditoría de los cambios apilados no-habitaciones (M1/AGREGACION-01, cambios de `transform/`/`extract/`, renombres a `archive/`) más allá de atribuirlos como no-habitaciones por diff.

---

*Evidence literal: `177 passed, 1 skipped` (skip `MONGO_ALLOW_DESTRUCTIVE!=1`); `35bcd8699c67…` / `b8411b77fd…` / `7f813fd61e…` / `ff39e852d2…`; huella `0f15c72990… reprod ok`; `mongo_habitaciones_por_municipio.csv: 9 filas, n=201 n_precio=200 (Durango 1 con None)`; `mongo_tier_confianza.csv: 252 A4/B3/C57/D188`; `png_mongo: 13 ficheros → canónico 12`; `chart_habitaciones_medianas.svg` 4ª `chart_*` con `firme solo Bilbao (96) y Donostia (66)`; `11 SVG`.*
