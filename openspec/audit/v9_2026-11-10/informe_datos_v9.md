# Informe de datos v9 — 2026-11-10 (W3.3)

**Fecha:** 2026-11-10 · **Unidad:** W3.3 (datos + sonda HDFS/Kafka) · **Naturaleza:** solo lectura
**Entrada:** `data/raw/`, `data/procesado/`, `data/resultados/`, `docs/raw_manifest_sha256.txt`, `data/procesado/manifest_sha256.txt`
**Guardrails respetados:** no se modificó código, datos, Mongo, HDFS ni Kafka; no se instalaron dependencias; no hubo commit/push. Única escritura: este informe.
**Criterios cubiertos:** 2 (Almacenamiento HDFS), 3 (Kafka), 19 (Preparación para visualización).
**P0/P1:** 0. No se detuvo la auditoría.

---

## 0. Ejecutado vs solo leído

**Ejecutado (herramienta real, read-only):**
- `git status --porcelain`, `git rev-parse HEAD`, `git branch --show-current`.
- `find` / `ls` / `du` / `wc` / `file` / `od` / `head` / `tail` / `grep` / `sed`.
- SHA-256 reales de los 354 ficheros raw y de los 188 silver (Python `hashlib`, por bloques).
- Escaneo de nulos de los 129 CSV raw con `csv.reader` (filas, celdas, nulos por columna).
- `pandas.read_csv` sobre los 8 `mongo_*` y sobre `dim_municipios` / comparativa.
- Consultas read-only a Mongo (`localhost:27017`): `list_collection_names`, `estimated_document_count`, `find_one`, `count_documents`, `aggregate` (sin `explain`, sin writes).
- Sondas de red: `curl` (WebHDFS + UI), TCP socket a 50070/9092, `KafkaProducer` (kafka-python 2.2.3).
- Cruce de 4 metafuentes raw: `docs/raw_manifest_sha256.txt`, `_meta/ingestion_manifest.json`, `_meta/csvs_index.json`, `_meta/index.json`.

**Solo leído (sin ejecutar):** `AGENT.md`, `00_baseline_v9.md`, `plan_ejecucion_v9_rondas_2026-11-10.md`, `rubrica_reextraida.md`, `transform/_raw_guard.py`, `analysis/run_analisis_mongo.py`, `analysis/mongo_aggregations.py`, `storage/load_mongo.py`, `tests/test_clean_mongo.py`, `tests/test_mongo_consistencia.py`, `tests/test_pisos_ubicacion_real.py`, `data/resultados/README.md`, evidencia histórica v7/v8.

**No ejecutado:** `load_all`, `clean_all`, `run_analisis_mongo` completo, productor/consumidor Kafka, gate vivo (`GATE_LIVE=1`), ninguna escritura en `data/`. No se instaló ninguna dependencia (se usó `.venv` existente: Python 3.12.10, pymongo 4.19.0, pandas 3.1.0, kafka-python 2.2.3).

---

## 1. Raw: 354 SHA vs manifiesto

### 1.1 Integridad (OK)

Comando (Python `hashlib`, read-only):

```
manifest lines parsed: 354
dup names: {}
dup sha (alias): 7 grupos (347 contenidos únicos para 354 entradas)
disk canonical files: 354
in manifest NOT on disk: []
on disk NOT in manifest: []
HASH MISMATCHES: 0
EXTRA disk files: 0
```

- `data/raw/` tiene **356 ficheros** = **354 canónicos + `.FROZEN` + `.gitkeep`** (los dos marcadores de 0 bytes).
- Los **354 SHA del manifiesto coinciden con el disco: 354/354 OK, 0 discrepancias, 0 ficheros huérfanos**.
- Extensión: 129 `csv`, 101 `html`, 61 `json`, 49 `zip`, 6 `xlsx`, 2 `geojson`, 1 `txt`, 1 `shx`, 1 `shp`, 1 `prj`, 1 `dbf`, 1 `cpg`, 1 `.gitkeep`, 1 `.FROZEN`.

### 1.2 Tamaños

```
total raw bytes: 901772849 = 860.0 MiB
(root)                    198 files   670.5 MiB
gtfs                       48 files   102.5 MiB
html_fotocasa             101 files    73.8 MiB
shp_euskadi                 5 files     7.3 MiB
legacy_obsoleto_no_usar     4 files     5.9 MiB
```

Más grandes: `certificados_energeticos_bizkaia_completo.csv` (118,8 MB), `distancias_b5m_gipuzkoa.json` (92,0 MB), `certificados_energeticos_gipuzkoa_completo.csv` (73,0 MB), `serpavi_renta_municipal.xlsx` (71,2 MB).

### 1.3 El CSV VPO con SHA `70a2937a…` (OK, con forma no canónica)

```
VPO exists: True  size: 35427
VPO sha256: 70a2937a3026b01c5e73ff641241c2fad0a77c3b995d2863034fba2da1294706
VPO in manifest with same sha: True
file: ISO-8859 text, with CRLF line terminators
```

- `data/raw/udalmap_vpo_terminadas.csv` — SHA idéntico al manifiesto y al histórico v8 (`raw_open.sha256` en `openspec/audit/v8_2026-11-09/evidencia/vivo/hdfs.json`).
- **No es un CSV UTF-8 estándar:** latin-1/ISO-8859, CRLF, separador `;`, decimales con coma, y **286 líneas** = 33 de preámbulo + 1 cabecera + **252 filas de municipio** (secciones `Resumen de datos`, `Detalle por comarcas`, `Detalle por municipios`).
- Un consumidor que haga `pd.read_csv()` sin `encoding='latin-1'` y `sep=';'` falla (`UnicodeDecodeError` en byte 0xfa y `Expected 1 fields in line 5, saw 22`). No es un defecto del dato (el parser del repo lo trata), pero es una trampa documentada.

### 1.4 `.FROZEN`

```
.FROZEN size: 0        (mtime 2026-10-29 11:41)
.gitkeep size: 0       (mtime 2026-10-29 11:29)
```

- El marcador existe y es **vacío**: no registra fecha, autor ni motivo. Es puramente existencial.
- `transform/_raw_guard.py:84` exige que el marcador **exista** para autorizar una escritura (`assert_raw_writable`).
- **Los raw tienen mtimes posteriores al marcador:** 310 ficheros el 2026-10-29, 41 el 2026-11-03, 1 el 2026-11-05, 4 el 2026-11-07. El `.FROZEN` no congela por fecha, solo por presencia → no permite demostrar cuándo se congeló ni que no hubo escrituras posteriores.
- No hay ningún `.bak`/`backup`/`copia` en `data/` (0 ficheros): la hipótesis T-15 (`.bak_f0` en raw) no ha materializado.

### 1.5 Nulos en raw (criterio 19, evidencia de calidad)

Escaneo de los 129 CSV raw con `csv.reader`:

```
scanned rows: 735698   cells: 8244243   null cells: 40660 (0.49%)
files with nulls: 95 / 129
errors: 0
```

Casos relevantes:

| Fichero | Filas | Columna | Nulos | Nota |
|---|---:|---|---:|---|
| `alquiler_seccion.csv` | 1569 | `territorio` | **1569 (100 %)** | Columna entera vacía |
| `anuncios_fotocasa.csv` | 471 | `trastero` / `parking` / `terraza` / `barrio` / `ascensor` / `distrito` | 432 / 383 / 329 / 237 / 152 / 114 | Equipamiento mayoritariamente ausente |
| `educacion_centros.csv` | 1309 | `web` / `fax` | 1049 / 277 | — |
| `ine_69301.csv` | 4407 | `anyo` / `valor` | 476 / 476 | — |
| `serpavi_renta_municipal.csv` | 249 | `renta_m2_mes_eur` y 4 más | 89 | — |
| `ecvi_*.csv` (varios) | 65–100 | columna **sin nombre** | 274–2660 | Columna adicional vacía (índice sin cabecera) |

No se imputó ni se filtró nada: solo recuento.

---

## 2. Silver: 188 entradas

```
manifest entries: 188
dup names: {}
dup sha: 4 grupos (184 contenidos únicos)
disk files (excl manifest/.gitkeep): 189
in manifest NOT on disk: []
on disk NOT in manifest: ['_meta/ingestion_manifest.json']
HASH MISMATCHES: 0
```

- **188/188 SHA OK, 0 discrepancias.**
- Composición del manifiesto: **66 `_meta/` + 122 raíz = 188**.
- Disco: **67 `_meta/` + 124 raíz = 191** = 188 manifiesto + `manifest_sha256.txt` + `.gitkeep` + **`_meta/ingestion_manifest.json`**.
- Extensiones: 144 `json`, 42 `csv`, 1 `txt`, 1 `geojson`, 1 `md`. Total: **238,541,913 B (227,5 MiB)**.
- 4 pares de contenido idéntico: `anuncios_pisos_enriquecido_geo_normalizado.json` == `…_meta_normalizado.json`, `anuncios_pisos_geo_normalizado.json` == `…_meta_normalizado.json`, `anuncios_pisos_habitaciones_geo_normalizado.json` == `…_meta_normalizado.json`, `anuncios_realtyapi_enriquecido.json` == `anuncios_realtyapi_normalizado.json`.

### 2.1 T-02 a nivel dato: `dim_municipios` tiene dos fuentes de verdad

```
data/raw/dim_municipios.csv      22820 B  sha 77d0feb6905157d9f0dae6f50f5c948c66b11e8d981d43ccf2ee3676cb58c313
data/procesado/dim_municipios.csv 30555 B  sha 261ad2c766737fc670a1a88f8081f18b8914517e868f9fccbd2a3fa61cdbf611
  identical: False
```

- Raw: **252 filas × 9 columnas**, sin nulos.
- Procesado: **252 filas × 12 columnas**, sin nulos; añade `tier`, `tier_etiqueta`, `n_anuncios_raw` y **redefine `n_anuncios`**.
- Dirección de dependencia (por `grep`): `transform/dim_municipios.py:288` escribe `procesado/dim_municipios.csv`; `transform/aplicar_cobertura_mercado.py` es el «SEGUNDO y último escritor autorizado» y añade `n_anuncios_raw`; `transform/limpiar_eustat_demografia.py:17` lee la versión **raw**; `transform/generar_distancias.py:27-30` lee la versión **procesado** con fallback a raw. Es decir: **el raw es la fuente y el procesado la derivada, pero ambas conviven con el mismo nombre** y hay transformadores que leen cada una. Riesgo de que una futura ejecución use la versión equivocada.

---

## 3. Los 8 CSV `mongo_*` (criterio 19)

### 3.1 Filas, columnas y nulos

| Fichero | Filas | Columnas | Celdas nulas | Columnas con nulos |
|---|---:|---:|---:|---:|
| `mongo_accesibilidad_extendida.csv` | 252 | 13 | 0 | 0 |
| `mongo_alquiler_por_municipio.csv` | 252 | 7 | 0 | 0 |
| `mongo_esfuerzo_por_municipio.csv` | 252 | 32 | 576 | 3 |
| `mongo_habitaciones_por_municipio.csv` | 9 | 7 | 0 | 0 |
| `mongo_modalidades.csv` | 2 | 3 | 0 | 0 |
| `mongo_tier_confianza.csv` | 252 | 20 | 2695 | 11 |
| `mongo_vpo_por_municipio.csv` | 322 | 9 | 322 | 1 |
| `mongo_vpo_terminadas_por_municipio.csv` | 251 | 5 | 0 | 0 |

Total: **1592 filas**. Los recuentos de líneas `wc -l` del baseline (253/253/253/253/3/253/323/252) coinciden con filas+1 cabecera.

Nulos concretos:
- `mongo_esfuerzo_por_municipio.csv`: `precio_medio_eur`, `superficie_media_m2`, `mediana_precio_m2_winsorizada` con **192 nulos de 252** (solo 60 municipios con precio).
- `mongo_tier_confianza.csv`: 11 columnas de precio con **245 nulos de 252** (solo 7 municipios con precio).
- `mongo_vpo_por_municipio.csv`: `viviendas` con **322 nulos de 322 (100 %)**.

### 3.2 BOM en los 8 ficheros

```
data/resultados/mongo_accesibilidad_extendida.csv: efbbbf
data/resultados/mongo_alquiler_por_municipio.csv:   efbbbf
data/resultados/mongo_esfuerzo_por_municipio.csv:   efbbbf
data/resultados/mongo_habitaciones_por_municipio.csv: efbbbf
data/resultados/mongo_modalidades.csv:              efbbbf
data/resultados/mongo_tier_confianza.csv:           efbbbf
data/resultados/mongo_vpo_por_municipio.csv:        efbbbf
data/resultados/mongo_vpo_terminadas_por_municipio.csv: efbbbf
```

Los **8/8** arrancan con BOM UTF-8 (`EF BB BF`): la primera cabecera se lee como `﻿n_promociones`, `﻿municipio`, etc.Rompe consumidores estrictos y comparaciones de nombres de columna.

### 3.3 Comparativa 204 / 126 / 50 / 39 (OK, validada en Mongo)

`data/resultados/comparativa_3_municipios_mongo.csv`:

| codigo_ine | nombre | n_anuncios | tier | delta | esfuerzo 18-34 | precio_medio |
|---|---|---:|---|---:|---:|---:|
| 48020 | Bilbao | **204** | A | 78 | 37,69 | 1716,69 |
| 20069 | Donostia / San Sebastián | **126** | A | 76 | 38,17 | 2465,32 |
| 48044 | Getxo | **50** | A | 11 | 28,60 | 1536,04 |
| 01059 | Vitoria-Gasteiz | **39** | A | — | 33,37 | 1406,13 |

Validación read-only contra Mongo:
- `indicadores` (`_id` 48020/20069/48044/01059) → `n_anuncios` = **204 / 126 / 50 / 39**. Coincide.
- `mongo_esfuerzo_por_municipio.csv` → mismos 204/126/50/39; **suma de `n_anuncios` sobre 252 municipios = 594** = `anuncios.estimated_document_count()`. Cierra.
- `n_anuncios_filtrados` suma **534** (60 anuncios excluidos por filtros).
- El propio CSV declara la fragilidad: «solo Tier A (n>=30…) sustenta ranking firme… Getxo 50 vs Vitoria-Gasteiz 39 = 11 anuncios (margen estrecho)».

### 3.4 Anomalías puntuales

- `mongo_vpo_por_municipio.csv`: **77 municipios** (`codigo_ine` y `municipio` únicos = 77); estados Terminada 274, En Curso 31, En Convenio 16, En Proyecto 1. `viviendas` 100 % nulo.
- `mongo_vpo_terminadas_por_municipio.csv`: **251 filas** (Usansolo/48916 ausente, como documenta `pipeline_vpo_terminadas`); 40 con valor > 0 y 211 a cero; territorios Bizkaia 112, Gipuzkoa 88, Araba/Álava 51.
- `mongo_habitaciones_por_municipio.csv`: **9 filas**; Vitoria-Gasteiz con `min=240`, `max=109000`, `mediana=400` (el máximo es un outlier crudo: el pipeline no winsoriza). Nombres con espacios (`Vitoria - Gasteiz`, `Donostia - San Sebastián`) vs sin espacios en otros CSV; `codigo_ine` con ceros iniciales aquí (`01059`) vs entero en `mongo_vpo_por_municipio.csv` (`1002`).
- **Los 8 CSV no están documentados en `data/resultados/README.md`**: la tabla «CSV desde MongoDB» lista solo 7; `mongo_habitaciones_por_municipio.csv` falta (solo aparece el PNG `H6_habitaciones_mediana_rango.png`).
- Mtime de los 8: **2026-11-08 15:00**.

---

## 4. Sonda HDFS y Kafka (criterios 2 y 3)

**Conclusión: ambos centros no responden. Se documenta la caída; no se trata como fallo del proyecto.**

### 4.1 Ejecutado en vivo (2026-11-10)

```
HDFS WebHDFS GETFILESTATUS: curl (28) Connection timed out after 12015 ms; http_code=000; exit 28
HDFS NameNode UI:            curl (28) Connection timed out after 12007 ms; http_code=000; exit 28
TCP 10.22.87.215:50070:      FAIL TimeoutError: timed out (8.00s)
TCP 10.22.87.215:9092:       FAIL TimeoutError: timed out (8.00s)
KafkaProducer(bootstrap_servers='10.22.87.215:9092'): NoBrokersAvailable after 8.06 s
```

### 4.2 Evidencia histórica clasificada (no revalidable)

- **v8** (`openspec/audit/v8_2026-11-09/evidencia/vivo/hdfs.json`): `data/raw` `fileCount=352`, `length=895,597,494`, `directoryCount=6`; `data/procesado` → **404 FileNotFoundException**; `udalmap_vpo_terminadas.csv` `length=35427`, `sha256=70a2937a…` (idéntico al local).
- **v8** (`…/vivo/kafka_retry2.json`): topic `vivienda_euskadi`, 1 partición, `beginning=0`, `end=352`, `committed=352` → **lag 0**, `ok: true`.
- **v7** (`openspec/audit/v7_2026-11-09/evidencia/hdfs_live.json`): `raw` n=201, `total_bytes=703,029,760`; `procesado` 404. **Es inconsistente con v8** (201/703 MB vs 352/895,6 MB): se cita como histórico, no como revalidación.

### 4.3 Brecha local↔HDFS (solo verificable con el histórico)

- Local: **354 canónicos**. HDFS (v8): **352 ficheros**. Hay **2 ficheros de diferencia** que no se pueden identificar ahora (la lista v8 de 201 nombres está truncada en el JSON). No se infla ni degrada la nota por la caída de red.

---

## 5. Contexto Mongo (read-only, para criterio 19)

```
total collections: 30 | vivas: 16 | backup: 14 (__backup)
anuncios 594 · municipios 252 · vpo_municipal 252 · indicadores 252 · etxebide_promociones 406
```

- `anuncios.fecha_carga`: **los 594 documentos tienen `2026-11-10 07:37`** (un único minuto). `anuncios__backup` tiene `2026-11-10 06:22:02`. Es decir, **la colección de producción se recargó dos veces hoy**, dentro de la ventana de auditoría. El conteo es estable (594) y coincide con el baseline, pero **la evidencia Mongo no proviene de una instantánea congelada**.
- `etxebide_promociones.num_viviendas`: campo presente, **0 de 406 documentos con valor no nulo**. Explica el 100 % de nulos de `viviendas` en `mongo_vpo_por_municipio.csv`.
- `anuncios.modalidad`: larga_estancia 326, temporal 268. `motivo_exclusion` no nulo: `iqr_excluido` 14, `precio_m2_fuera_3_50` 4, `superficie_fuera_10_500` 4, combinado 1.
- `indicadores.fecha_carga` = 2026-11-07 16:32:08; los 8 CSV son del 2026-11-08 15:00 y la recarga de `anuncios` es del 2026-11-10 07:37 → **los CSV preceden a la última recarga** (los conteos siguen cuadrando).

---

## 6. Cuatro metafuentes raw: grado de frescura

| Fuente | Entradas | SHA vs disco | Frescura |
|---|---:|---|---|
| `docs/raw_manifest_sha256.txt` | 354 | **354/354 OK** | vigente |
| `data/procesado/_meta/csvs_index.json` | 129 CSV | **129/129 OK** | vigente |
| `data/procesado/_meta/ingestion_manifest.json` | 354 | **352/354** | obsoleto en 2 |
| `data/procesado/_meta/index.json` | 61 | **0/61** | extracción (2026-10-23…11-03) |

Discrepancias exactas:

```
ingestion_manifest vs docs manifest:
  lanbide_paro_historico_joven.json  docs fa363e45f911  ingestion 76e20ea9dcbc
  lanbide_paro_juvenil.json          docs c8eef5953b87  ingestion ccd22d03d23b4
  (ambas modificadas en disco el 2026-11-07 17:23; ingestion generado el 2026-11-05T21:34:16)
```

- `ingestion_manifest.json` es el registro de la ingesta del 2026-11-05 y **no se regeneró tras la actualización de los dos `lanbide_paro_*` del 2026-11-07**. El manifiesto de `docs/` sí está al día (coincide con el disco).
- `index.json` es el registro de extracción original (`fecha_extraccion` 2026-10-23 a 2026-11-03); su `hash_sha256` **no cuadra con el raw actual en ninguna de las 61 entradas** (verificado con BOM y re-codificación: no es un artefacto de codificación). Probablemente hashea el payload fuente, no el wrapper raw; en cualquier caso, **no sirve como manifiesto del raw vigente**.

---

## 7. Hallazgos

**Recuento: P0 = 0 · P1 = 0 · P2 = 5 · P3 = 8.** Ningún P0/P1: no se detuvo la auditoría.

| ID | Sev. | Título | Evidencia | Impacto |
|---|---|---|---|---|
| **D-01** | **P2** | Dos manifiestos raw discrepando en 2 ficheros (`lanbide_paro_historico_joven.json`, `lanbide_paro_juvenil.json`) | `docs/raw_manifest_sha256.txt` (fa363e45 / c8eef595) vs `_meta/ingestion_manifest.json` (76e20ea9 / ccd22d03); disco = docs; ingestion generado 2026-11-05, ficheros tocados 2026-11-07 17:23 | Doble fuente de verdad: un consumidor que lea `ingestion_manifest.json` valida 2 ficheros contra un SHA que ya no es el real |
| **D-02** | **P2** | `_meta/index.json` no hashea el raw vigente (0/61) | `hash_sha256` vs `docs` manifiesto: 0 coincidencias; `fecha_extraccion` 2026-10-23…11-03 | El hash de procedencia no es verificable contra el fichero; ambigüedad entre hash del payload fuente y del wrapper raw |
| **D-03** | **P2** | `dim_municipios` duplicado raw vs procesado con esquemas distintos (T-02) | raw 252×9 sha `77d0feb6` vs procesado 252×12 sha `261ad2c7`; `dim_municipios.py:288` escribe procesado, `aplicar_cobertura_mercado.py` lo reescribe, `limpiar_eustat_demografia.py:17` lee raw, `generar_distancias.py:27` lee procesado | Riesgo de que una ejecución use la versión equivocada; la derivada convive con la fuente con el mismo nombre |
| **D-04** | **P2** | Cobertura de metadatos de URL en raw: 23/354 | 61 JSON raw, 59 con `metadata`, **23 con `metadata.url`**; 331 sin URL estructurada; `_meta/index.json` 61 entradas, 23 con URL | F-01: la procedencia de 331 ficheros no es recuperable desde metadatos estructurados |
| **D-05** | **P2** | Nulos relevantes en raw: `alquiler_seccion.territorio` 100 % nulo y columna sin nombre en `ecvi_*` | escaneo 129 CSV: 40 660 nulos / 8 244 243 celdas (0,49 %); `alquiler_seccion.csv` 1569/1569; `ecvi_*` con columna vacía sin cabecera | Columnas que se propagan a silver/resultados como todo-nulo o sin nombre; riesgo de silenciar el problema |
| **D-06** | **P3** | `.FROZEN` es un marcador vacío, sin fecha, y hay raw con mtime posterior | `.FROZEN` 0 bytes (2026-10-29 11:41); raw con mtimes 2026-11-03/05/07; `_raw_guard.py:84` solo comprueba existencia | No permite demostrar cuándo se congeló ni que no hubo escrituras posteriores |
| **D-07** | **P3** | 7 pares de contenido duplicado en raw (347 únicos para 354 entradas) | `anuncios_pisos_*_geo.json` == `…_meta.json` (3 pares), `legacy_obsoleto_no_usar/` duplica 3 ficheros, `gtfs/gtfs_ekialdebus.zip` == `lurraldebus_ekialdebus.zip` | El manifiesto avala duplicados; confusión sobre cuál es el canónico |
| **D-08** | **P3** | BOM UTF-8 en los 8 CSV `mongo_*` | `head -c 3` → `efbbbf` en los 8 | La primera cabecera se contamina con U+FEFF; rompe consumidores estrictos |
| **D-09** | **P3** | `mongo_vpo_por_municipio.csv` con `viviendas` 100 % nulo (limitación declarada) | 322/322 nulos; `etxebide_promociones.num_viviendas` 0/406 no nulos; `mongo_aggregations.py:488-505` lo devuelve `None` a propósito; el gráfico H12 lo titula «viviendas sin dato (null)» | No es un bug, pero el CSV envía una columna muerta como si fuera un resultado; conviene documentarlo en el README |
| **D-10** | **P3** | `mongo_habitaciones_por_municipio.csv`: outlier 109 000 €, nombres con espacios y `codigo_ine` con ceros; no está en el README | 9 filas; Vitoria-Gasteiz min 240 / max 109000 / mediana 400; `Vitoria - Gasteiz`; `01059`; `data/resultados/README.md` lista 7 de 8 CSV | Consumidor puede citar un máximo falso; el 8.º CSV es indocumentado |
| **D-11** | **P3** | `_meta/ingestion_manifest.json` no está en el manifiesto silver | 189 ficheros en disco vs 188 entradas; el extra es `_meta/ingestion_manifest.json` | El manifiesto silver no cubre el 100 % del directorio |
| **D-12** | **P3** | `anuncios` recargado 2 veces hoy (06:22 y 07:37) durante la auditoría | `anuncios.fecha_carga` = 2026-11-10 07:37 (594 docs); `anuncios__backup` = 06:22:02 | La evidencia Mongo no es una instantánea congelada; el conteo sí es estable |
| **D-13** | **P3** | Los 8 CSV (2026-11-08) preceden a la recarga de `anuncios` (2026-11-10) | mtime CSV 2026-11-08 15:00; `anuncios` 2026-11-10 07:37; `indicadores` 2026-11-07 16:32 | Si la recarga cambia datos, los CSV quedan desactualizados; hoy los conteos cuadran (594) |

---

## 8. Criterios cubiertos

### Criterio 2 — Almacenamiento HDFS
- **Organización local (OK):** 354 canónicos + `.FROZEN` + `.gitkeep`; manifiesto 354/354 SHA verificados; 4 metafuentes caracterizadas.
- **Recuperación (no revalidable en vivo):** HDFS `10.22.87.215:50070` no responde (timeout 12 s). Evidencia histórica v8: `data/raw` `fileCount=352`, `length=895,597,494`; VPO recuperado con SHA idéntico; **`data/procesado` 404**.
- **Brecha:** HDFS 352 vs local 354 (2 ficheros), no identificables sin red. Se documenta como limitación, no como fallo del proyecto.

### Criterio 3 — Kafka
- **No revalidable en vivo:** `10.22.87.215:9092` no responde (TCP timeout; `NoBrokersAvailable` a los 8,06 s).
- **Evidencia histórica v8:** topic `vivienda_euskadi`, 1 partición, `end_offsets=352`, `committed=352`, lag 0, `ok: true`.
- **Código vigente (solo leído):** `storage/kafka_raw_producer.py`, `storage/kafka_hdfs_uploader.py`, `storage/kafka_topic.py`; el topic viejo `anuncios_inmobiliarios` está eliminado (2026-11-06).

### Criterio 19 — Preparación para visualización
- **8 CSV `mongo_*` generados automáticamente** (1592 filas) + comparativa 204/126/50/39 validada contra `indicadores` y contra el total 594.
- **Defectos que restan robustez:** BOM en los 8, columna `viviendas` 100 % nula, outlier en `habitaciones`, 8.º CSV indocumentado.
- Los CSV se generan desde `analysis/run_analisis_mongo.py`; `run_all_estandar()` es determinista (huella SHA reproducible) y `test_sha_doble_identico` lo verifica.

---

## 9. Límites de este informe

- **HDFS y Kafka están caídos:** los criterios 2 y 3 no se revalidan en vivo; se usa el histórico v8/v7 como evidencia clasificada. No se infiere ni se degrada nota por la caída de red.
- El escaneo de nulos raw cubre los **129 CSV**; los `xlsx`, `zip`, `shp` y `html` no se analizaron a nivel de celdas (solo se inventariaron y se compararon por SHA).
- La comparativa 204/126/50/39 se validó contra `indicadores` y contra la suma 594; no se reprodujeron los 11 pipelines.
- Las consultas a Mongo son read-only; no se ejecutó `explain()` en vivo (se usa el histórico v8: IXSCAN 68/68).
- El estado de git (19 staged / 15 modified / untracked) es el de partida y **no se tocó**.
