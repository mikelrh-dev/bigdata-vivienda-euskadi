# Informe Mongo v9 — 2026-11-10 (solo lectura)

**Unidad:** W3.2 (Mongo read-only) · **Ronda 3**
**Fecha:** 2026-11-10
**Instrumento:** `.venv` Python 3.12.10 + pymongo 4.19.0 → MongoDB **9.0.2** (standalone, wiredTiger) en `localhost:27017`, db `vivienda_euskadi`.
**Guardrails respetados:** no se ejecutó `load_all`, `clean_all`, `run_analisis_mongo` completo, `ensure_indexes`, `explain_before_after`, `replace_collection` ni el productor Kafka; no se instalaron dependencias; no hubo commit/push. **Único fichero escrito en el repo: este informe.**

---

## 0. Ejecutado vs solo leído

**Ejecutado (herramienta real, read-only):**

- `list_collection_names()`, `count_documents({})`, `estimated_document_count()`, `list_indexes()`, `$indexStats`, `hello`, `serverStatus`.
- Los **11 pipelines** con `$limit 2` (agregación read-only).
- `explain` con `verbosity="executionStats"` y `hint: {"$natural": 1}` (read-only) para simular el COLLSCAN sin dropear el índice.
- Agregados de duplicados y conteos por campo (`$exists`/`$ne: None`).

**Solo leído (sin ejecutar):**

- `analysis/mongo_aggregations.py`, `analysis/mongo_indexes.py`, `analysis/run_analisis_mongo.py`, `storage/mongo.py`, `storage/load_mongo.py`, `storage/clean_mongo.py`, `scripts/run_mongo_pipeline.py`, `tests/test_mongo_consistencia.py`.
- **No** se ejecutó el test de atomicidad (muta `vivienda_euskadi_test`).
- **No** se ejecutó `explain_before_after()` tal cual: ese helper **dropea y recrea** el índice (escritura). Se sustituyó por un equivalente read-only.

**Sondas (scratch, fuera del repo):** `probe_v9_conteos.py`, `probe_v9_pipelines.py`, `probe_v9_explain3.py`, `probe_v9_geo.py`, `probe_v9_flags.py`.

---

## 1. Conteos

### 1.1 Colecciones

| Elemento | Valor |
|---|---|
| Total colecciones | **30** |
| Vivas | **16** |
| `__backup` | **14** |
| `estimated_document_count` vs `count_documents` | **idénticos en las 30** (sin deletes pendientes) |

**Vivas (16):** `anuncios` 594 · `municipios` 252 · `vpo_municipal` 252 · `alquiler_municipal` 252 · `indicadores` 252 · `osrm_tiempos` 252 · `udalmap_empleo` 252 · `udalmap_indicadores` 252 · `udalmap_extendido` 252 · `certificados_energeticos` 252 · `etxebide_promociones` 406 · `etxebide_solicitudes` 5040 · `ecvi_compraventa` 29 · `emancipacion_juventud` 1 · `anuncios_habitaciones_unificados` 201 · `anuncios_habitaciones_unificados_bigdata` 201.

**`__backup` (14):** cada copia tiene **el mismo conteo que su base** (`anuncios` 594/594, `municipios` 252/252, `vpo_municipal` 252/252, `etxebide_solicitudes` 5040/5040, resto 252/252, `ecvi` 29/29, `emancipacion` 1/1). Integridad de backups **OK**.

### 1.2 Documentos con / sin dato

| Colección | Campo | Con dato | Sin dato |
|---|---|---:|---:|
| `anuncios` (594) | `ubicacion.codigo_ine` | 594 | 0 |
| | `portal` / `id_anuncio` / `modalidad` / `equipamiento` | 594 | 0 |
| | `precio_eur` | 561 | **33** |
| | `precio_m2` | 547 | **47** |
| | `superficie_m2` | 587 | 7 |
| | `habitaciones` | 579 | 15 |
| | `ubicacion.coordenadas` | 424 | **170** |
| `municipios` (252) | `nombre_canonico`, `territorio` | 252 | 0 |
| | `demografia.renta_joven_estimada_16_29` / `_18_34` | 252 | 0 |
| | `empleo.tasa_paro_lanbide_pct` | 252 | 0 |
| | `demanda_social.tension_demanda_social` | 252 | 0 |
| | `calidad_datos` | **0** | **252** |
| `vpo_municipal` (252) | `vpo_terminadas_por_mil` | 251 | **1** (Usansolo) |
| | `anio_fuente` | 252 | 0 |
| `alquiler_municipal` (252) | `cuantia_media_eur_mes_mediana`, `renta_media_eur_m2_mediana`, `metodo_imputacion` | 252 | 0 |

**Flags de calidad ausentes en prod (0/N):** `municipios.demografia.renta_joven_calidad` 0/252, `municipios.calidad_datos` 0/252, `certificados_energeticos.calidad_cert` 0/252, `etxebide_promociones.tiene_codigo_ine` 0/406, `etxebide_promociones.calidad_viviendas` 0/406. → `clean_all()` **no se ha ejecutado** tras la última carga (ver HM-03).

---

## 2. Los 11 pipelines con `$limit 2`

**Resultado: 11/11 OK, 2 filas cada uno.**

| # | Pipeline | n | s | Evidencia (muestra) |
|---|---|---:|---:|---|
| 1 | `pipeline_indicadores_municipio` | 2 | 0.27 | Bilbao 48020 n=204, filtrados=188, tier A, rankeable, esfuerzo 18-34=37,69 %; Donostia 20069 n=126, filtrados=116, 38,17 % |
| 2 | `pipeline_alquiler_por_municipio` | 2 | 0.02 | Donostia 1051 €/mes (14,9 €/m²); Berango 933 €/mes |
| 3 | `pipeline_modalidades` | 2 | 0.00 | `larga_estancia` 326 (1829,67 €); `temporal` 268 (1701,26 €) |
| 4 | `pipeline_top_municipios_por_esfuerzo` | 2 | 0.06 | Donostia 38,17 %; Bilbao 37,69 % |
| 5 | `pipeline_esfuerzo_por_sexo` | 2 | 0.02 | Sestao 52,36 % mujeres / 37,37 % hombres; Erandio 51,99 / 38,95 |
| 6 | `pipeline_accesibilidad_extendida` | 2 | 0.05 | Bilbao 0,8 min a Bilbao / 52,3 a Vitoria; Sondika 9,0 / 60,8 |
| 7 | `pipeline_udalmap_extendido_osrm` | 2 | 0.03 | Alegría-Dulantzi, Amurrio (udx + osrm embebidos) |
| 8 | `pipeline_vpo_por_municipio` | 2 | 0.04 | Hernani 28 promociones; Urnieta 6 |
| 9 | `pipeline_vpo_terminadas` | 2 | 0.02 | Berango 62,55 ‰; Zerain 28,78 ‰ |
| 10 | `pipeline_tier_por_municipio` | 2 | 0.02 | Bilbao 204 tier A (n_precio 190); Donostia 126 tier A (n_precio 121) |
| 11 | `pipeline_habitaciones_por_municipio` | 2 | 0.02 | Bilbao n=96 mediana 600 €; Donostia n=66 mediana 1200 € |

**Nota:** `pipeline_modalidades()` es el **único** que no acepta parámetro `limit`; se ejecutó su agregación canónica + `$limit: 2` (HM-07). Los otros 10 aceptan `limit`.

---

## 3. explain COLLSCAN / IXSCAN

**Método read-only:** `db.command("explain", {"find": "anuncios", "filter": …}, verbosity="executionStats")`; el "antes" se simula con `hint: {"$natural": 1}` (fuerza barrido completo). **No se dropeó el índice.**

| Filtro | Stage | Índice | nReturned | totalDocsExamined | totalKeysExamined |
|---|---|---|---:|---:|---:|
| `48020` + `larga_estancia` + `precio_eur ≤ 1000` | **IXSCAN** | `idx_anuncios_ine_modalidad_precio` | 8 | **8** | 8 |
| idem, forzado COLLSCAN | **COLLSCAN** | — | 8 | **594** | 0 |
| `20069` + `larga_estancia` + `≤ 1000` | **IXSCAN** | idem | 1 | **1** | 1 |
| idem, forzado COLLSCAN | **COLLSCAN** | — | 1 | **594** | 0 |
| `48001` + `larga_estancia` + `≤ 1000` (filtro por defecto del helper) | **IXSCAN** | idem | 0 | **0** | 0 |
| idem, forzado COLLSCAN | **COLLSCAN** | — | 0 | **594** | 0 |

**Índice ESR confirmado:** `keyPattern = {ubicacion.codigo_ine: 1, modalidad: 1, precio_eur: 1}` → Equality (`codigo_ine`), Equality (`modalidad`), Range (`precio_eur`). Con IXSCAN, `totalDocsExamined == nReturned` (8/8 y 1/1); con COLLSCAN, 594 (colección completa). La transición COLLSCAN→IXSCAN queda demostrada sin mutar la base.

**Observación:** el filtro por defecto de `explain_before_after()` (`48001`) devuelve **0 documentos**; con ese filtro la demo muestra IXSCAN con 0 examinados. La evidencia histórica v8 "IXSCAN 1" **no** se reproduce con el filtro por defecto; se reprodujo con `20069` (1 doc) y `48020` (8 docs) (HM-08).

---

## 4. Índices: lista, uso y justificación

### 4.1 Lista (solo vivas; los `__backup` tienen únicamente `_id_`)

| Colección | Índice | Clave | UNIQUE | SPARSE | ops ($indexStats) |
|---|---|---|---|---:|---:|
| `anuncios` | `idx_anuncios_ine_modalidad_precio` | `(ubicacion.codigo_ine, modalidad, precio_eur)` | no | no | **27** |
| `anuncios` | `idx_anuncios_geo` | `(ubicacion.coordenadas, 2dsphere)` | no | sí | **0** |
| `anuncios` | `idx_anuncios_portal_id` | `(portal, id_anuncio)` | **sí** | no | 4 |
| `anuncios` | `idx_anuncios_equipamiento` | `(equipamiento)` | no | no | **3** |
| `municipios` | `idx_municipios_territorio_nombre` | `(territorio, nombre_canonico)` | no | no | **1** |
| `alquiler_municipal` | `idx_alquiler_ine_distrito_nivel` | `(codigo_ine, distrito, nivel_geografico)` | no | no | **298** |
| `etxebide_promociones` | `idx_promo_ine_estado_tipo` | `(codigo_ine, estado_obra, tipologia)` | no | no | 5 |
| `certificados_energeticos` | `idx_cert_moda` | `(cert_moda)` | no | no | 38 |
| resto (8 vivas) | `_id_` | — | — | — | variables |

### 4.2 Justificación

- **`idx_anuncios_ine_modalidad_precio`** — **justificado.** Soporta el filtro del `explain` y los `$lookup` `municipios → anuncios` por `ubicacion.codigo_ine`. 27 ops.
- **`idx_anuncios_portal_id` (unique)** — **justificado.** Integridad de deduplicación: verificado **0 grupos duplicados** en `(portal, id_anuncio)` sobre 594/594 docs con ambos campos presentes.
- **`idx_alquiler_ine_distrito_nivel`** — **justificado.** 298 ops.
- **`idx_promo_ine_estado_tipo`** — **justificado.** Usado por `pipeline_vpo_por_municipio` (`$match codigo_ine` + `$group` por estado/tipología). 5 ops.
- **`idx_cert_moda`** — **justificado.** 38 ops.
- **`idx_anuncios_geo`** — **injustificado por uso actual.** Los 424 documentos con coordenadas son GeoJSON `Point` válidos (0 arrays legacy), pero **ninguno** de los 11 pipelines ejecuta `$near`/`$geoWithin`/`$geoIntersects`; 0 ops desde su creación (HM-04).
- **`idx_anuncios_equipamiento`** — **marginal.** 3 ops; ningún pipeline filtra por `equipamiento` (HM-05).
- **`idx_municipios_territorio_nombre`** — **marginal.** 1 op; los pipelines ordenan por territorio en memoria, no en Mongo.

---

## 5. Consistencia

### 5.1 `find_one_and_update` atómico

`storage/mongo.py:170-201` `marcar_calidad_municipio()`: `find_one_and_update({"_id": code}, {"$set": {"calidad_datos": calidad}}, return_document=ReturnDocument.AFTER)` sobre **un único documento**. La lectura-modificación-escritura es una sola operación atómica a nivel de documento; **no requiere transacción multidocumento ni replica set**. Validación de dominio (`CALIDAD_DATOS_VALIDOS`) con `ValueError` sin escribir.

- **Verificado por código + test** (`tests/test_mongo_consistencia.py:49-97`: assertions de documento posterior, municipio inexistente → `None`, valor inválido → `ValueError` sin escritura). **No ejecutado por mí** (muta `vivienda_euskadi_test`).
- **En prod el campo no existe:** `calidad_datos` 0/252. La función atómica **no tiene uso productivo**; solo se ejecuta en el test (HM-03/HM-06).

### 5.2 Transacción en standalone

**Topología verificada (ejecutado):**

| Campo | Valor |
|---|---|
| `hello.setName` | `null` |
| `hello.hosts` | `null` |
| `hello.isWritablePrimary` | `true` |
| `serverStatus.repl` | `null` |
| `serverStatus.storageEngine` | `wiredTiger` |
| `serverStatus.version` | `9.0.2` |

→ **standalone**, no replica set. Las transacciones multidocumento **no están disponibles** (las exige replica set/sharded desde MongoDB 4.0). El código **no las usa**: `grep start_session|with_transaction|start_transaction` → solo `tests/test_mongo_consistencia.py:112-113`, que espera explícitamente `rechazado-standalone`. La atomicidad del proyecto se sostiene en operaciones de un solo documento, que es la estrategia correcta en standalone.

### 5.3 `replace_collection` (heredado H-SA-02)

`storage/mongo.py:152-164`: `drop(staging) → insert_many(staging) → drop(backup) → $out(backup) → rename(staging, name, dropTarget=True)`.

- El **rename final es atómico** para la colección viva, pero la **secuencia completa no es transaccional** (no puede serlo en standalone).
- El `staging` no tiene índices: al renombrar con `dropTarget=True` se **pierde el índice único** `(portal, id_anuncio)` (y el resto). `load_all` lo recrea al final (`load_mongo.py:607-615`).
- `scripts/run_mongo_pipeline.py:70-73` ejecuta `load_all() → clean_all() → ensure_indexes()`: el índice único se crea **dentro de `load_all`, antes** del dedup de `clean_all` (`clean_mongo.py:164-219`). Si la carga trajera duplicados, `ensure_indexes()` fallaría con *duplicate key* y `load_all` propagaría el error. **Actualmente 0 duplicados → no se manifiesta.**
- Los 14 `__backup` conservan el estado previo al último swap (conteos idénticos a la base).

---

## 6. Hallazgos

| ID | Sev. | Título | Evidencia | Impacto |
|---|---|---|---|---|
| **HM-01** | **P2** | El entrypoint de análisis **no es read-only**: `explain_before_after()` y `explain_promo_before_after()` dropean y recrean índices; `run_analisis_mongo.main()` los ejecuta antes de los pipelines. | `analysis/mongo_indexes.py:97-104` (`drop_demo_index`), `:123-131` (drop+create), `:135-149` (promo drop+create); `analysis/run_analisis_mongo.py:1161-1173` | Cada ejecución del "análisis" **muta la base**: ventana sin el índice ESR (consultas concurrentes harían COLLSCAN) y recreación del índice de promociones. Contradice la naturaleza `analysis` del módulo. No es pérdida de datos (el índice se recrea). |
| **HM-02** | **P2** | Heredado **H-SA-02**: `replace_collection` no es atómico como secuencia; el índice único se pierde en el swap y `load_all` lo recrea al final, antes del dedup de `clean_all`. | `storage/mongo.py:152-164`; `storage/load_mongo.py:590-616`; `scripts/run_mongo_pipeline.py:70-73`; `storage/clean_mongo.py:164-219` | Ventana sin índice único tras cada carga; si hay duplicados, `ensure_indexes()` falla y `load_all` propaga el error. Hoy 0 duplicados. |
| **HM-03** | **P3** | Flags de calidad **ausentes en prod**: `clean_all()` no se ejecutó tras la última carga. | `renta_joven_calidad` 0/252, `calidad_datos` 0/252, `calidad_cert` 0/252, `tiene_codigo_ine` 0/406, `calidad_viviendas` 0/406 (probe `probe_v9_flags.py`) | La capa de calidad de Mongo no está aplicada; `docs/modelo_mongodb.md:76` describe `calidad_datos` como gobernado cuando en prod no existe. Los pipelines no dependen de esos flags. |
| **HM-04** | **P3** | `idx_anuncios_geo` (2dsphere) **sin uso**: 0 ops; ningún pipeline hace geo-queries. | `$indexStats` ops=0 desde 2026-11-10 06:22:02; 424 GeoJSON `Point` válidos (0 legacy) | Coste de almacenamiento/escritura sin beneficio medible. Válido pero injustificado. |
| **HM-05** | **P3** | `idx_anuncios_equipamiento` **casi sin uso**: 3 ops; ningún pipeline filtra por `equipamiento`. | `$indexStats` ops=3 | Coste marginal sin beneficio. |
| **HM-06** | **P3** | **Duplicación de datos**: `anuncios_habitaciones_unificados` y `anuncios_habitaciones_unificados_bigdata` tienen los **mismos 201 `_id`**; `_hab_col()` elige `bigdata` si tiene docs. | `anuncios_habitaciones.py` `_hab_col()`; probe: 201/201 ids comunes, unión 201 | Doble almacenamiento y ambigüedad de fuente: si las dos colecciones divergieran, los resultados cambiarían según cual esté no vacía. |
| **HM-07** | **P3** | `pipeline_modalidades()` es el **único** de los 11 que no acepta `limit`. | `analysis/mongo_aggregations.py:313-319` | Inconsistencia de API; para el `$limit 2` hubo que replicar la agregación. |
| **HM-08** | **P3** | El filtro por defecto de `explain_before_after()` (`48001`) devuelve **0 docs**; la demo COLLSCAN→IXSCAN con ese filtro muestra IXSCAN con 0 examinados. | `analysis/mongo_indexes.py:107-122`; probe: `48001` nReturned=0 | La evidencia histórica v8 "IXSCAN 1" no se reproduce con el filtro por defecto; se reprodujo con `20069` (1) y `48020` (8). |

**No hay P0/P1.** No se detuvo la ejecución.

---

## 7. Límites de este informe

- **No se ejecutó el test de atomicidad** (`test_mongo_consistencia.py`) porque muta `vivienda_euskadi_test`; la atomicidad se verifica por código + diseño del test, no por ejecución propia.
- **No se ejecutó `explain_before_after()` tal cual** (dropea índices); el "antes" es una simulación read-only con `hint: {"$natural": 1}`. El índice real nunca se dropeó.
- **`$indexStats` es acumulativo desde el último arranque/recreación del índice** (los de `anuncios` se crearon el 2026-11-10 06:22:02); los ops no son históricos absolutos.
- **HDFS/Kafka no se tocaron**; el baseline v9 ya documentó su caída de red.
- Los flags de calidad se midieron sobre el estado actual; no se infiere la secuencia temporal exacta de cargas/limpiezas, solo que el estado final no tiene flags.

---

## 8. Criterios cubiertos (según plan v9, W3.2)

`5` (integración de fuentes), `6`, `9`–`14`, `16`–`19`. La mapping literal a la rúbrica queda pendiente de W1.1/W1.2.
