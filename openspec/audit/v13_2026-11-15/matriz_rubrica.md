# Matriz de rúbrica — auditoría v13 (2026-11-15)

Criterios extraídos **literalmente** del PDF (`pymupdf`, 6 páginas) y del DOCX (§16, 14 tablas),
no de la transcripción del repo. El `contrato-reto/spec.md` coincide sin diferencias en los 19
criterios y en los 7 de Tema 8; los pesos también (SBD 46,7 / 13,3 / 40; Tema 8 15/15/20/15/10/15/10).

Escala de anclas: 10 = evidencia reproducible hoy y contraprueba superada · 9 = ídem con cosmética
pendiente · 7–8 = funciona con laguna declarada · 5–6 = existe pero no cumple la literalidad ·
3–4 = parcial · 0–2 = no existe o es falso.

## BDA — RA1 (el PDF no declara peso)

| # | Criterio (nivel 10) | Nota | Ancla | Evidencia verificada | Confianza |
|---|---|---:|---|---|---|
| C1 | Automatiza **API y scraping** | **10** | 10 | 41 scripts en `extract/`; cliente común con timeout/retry; scrapers Fotocasa/Pisos + fuentes API (Eustat, INE, OSRM); `main_ingest` orquesta | Alta |
| C2 | HDFS: **originales y procesados** + recuperación | **7** | 7 | 353 objetos históricos (351 canónicas + `.FROZEN` + `.gitkeep`); `/data/procesado` 404 con waiver; recuperación **no demostrable hoy** (DNS/tcp timeout) | Alta |
| C3 | Productor y consumidor Python **procesan mensajes** | **10** | 10 | `kafka_raw_producer.py` + `kafka_hdfs_uploader.py` con commit `offset+1`; evidencia v8 352/352 lag 0; tests offline. No revalidado en vivo (red del centro) | Media |
| C4 | Flujo completo **hasta MongoDB** | **7** | 7 | Cadena por partes OK, pero `run_vivo()` devuelve `[]`, `check_lag()` es una constante y `check_duplicados()` simula un `dict`: el E2E se sostiene en narrativa, no en verificación | Alta |

**BDA = 34/40.**

## SBD — RA1 (46,7 %)

| # | Criterio (nivel 10) | Nota | Ancla | Evidencia | Confianza |
|---|---|---:|---|---|---|
| C5 | 2+ fuentes con **campo común** | **10** | 10 | 16 loaders + `load_all`; `$lookup` por `codigo_ine`; `anuncios` 594/594 con `ubicacion.codigo_ine` | Alta |
| C6 | 2+ colecciones con relación/embedding/referencia | **10** | 10 | Embedding (`ubicacion`, `equipamiento`, `historico_precios`) + referencing por `codigo_ine`; 17 vivas | Alta |
| C7 | Limpieza: nulos, duplicados, tipos **+1** | **10** | 10 | `canonicalize_codigo_ine`, `mark_nulls`, `resolve_duplicates`, `convert_types`, `clean_obsolete_fields`, `clean_null_markers` | Alta |
| C8 | Automatización carga+limpieza+transformación | **10** | 10 | `run_mongo_pipeline.py` (load → clean → indexes → pipeline); staging + `__backup` + rename | Alta |

**SBD RA1 = 40/40.**

## SBD — RA3 (13,3 %)

| # | Criterio (nivel 10) | Nota | Ancla | Evidencia | Confianza |
|---|---|---:|---|---|---|
| C9 | Modelado + **decisión embedding/referencing justificada** | **10** | 10 | `modelo_mongodb.md`: embedding vs referencing, tipos BSON y las 7 preguntas del docx §5 | Alta |
| C10 | CRUD 4 ops + **comprobación por código** | **10** | 10 | `demo_crud_operations` con `matched/modified/deleted_count`; deuda: un assert tautológico en `tests/test_mongo.py` | Media-alta |
| C11 | 5+ consultas, anidada/array, 2+ condiciones | **10** | 10 | 30 funciones: dot notation, `$elemMatch`, `$all`, `$size`, `$exists`, `$type`, `$regex`, `$and/$or`, sort/skip/limit | Alta |
| C12 | 3+ pipelines que respondan al reto, 5 etapas, `$group` + lookup/unwind/facet | **10** | 10 | 11 pipelines; 8 etapas distintas (`match` 20, `lookup` 18, `addFields` 36, `project` 13, `sort` 13, `limit` 12, `group` 4, `unwind` 5); `$facet` no existe y no es obligatorio | Alta |
| C13 | Índices + `explain()` antes/después con COLLSCAN/IXSCAN y totalDocsExamined | **10** | 10 | Ejecutado hoy: `anuncios` tiene `idx_anuncios_ine_modalidad_precio`, `2dsphere`, `portal+id`, `equipamiento`; plan `FETCH/IXSCAN`, 126 claves / 126 docs | Alta |
| C14 | Transacción real **o** atómica justificada | **10** | 10 | `find_one_and_update` + índice único; justificación de standalone; sonda en `vivienda_euskadi_test` | Alta |

**SBD RA3 = 60/60.**

## SBD — RA4 (40 %)

| # | Criterio (nivel 10) | Nota | Ancla | Evidencia | Confianza |
|---|---|---:|---|---|---|
| C15 | Datos heterogéneos adaptados con Python/PyMongo | **10** | 10 | 7 formatos (CSV, JSON, JSON anidado, XLSX, GeoJSON, ZIP/GTFS, SHP) normalizados a un esquema común | Alta |
| C16 | Script que ejecuta **todos** los análisis | **10** | 10 | `run_analisis_mongo.py`: 11 pipelines, huella gold `983fa53f…`, 24 CSV | Alta |
| C17 | 5+ indicadores de **2+ fuentes** | **10** | 10 | esfuerzo, tensión social, VPO, accesibilidad/OSRM, habitaciones, esfuerzo por sexo, sensibilidad IDW. **Matiz:** tres columnas publicadas son el mismo número (H-03) | Media-alta |
| C18 | 3+ municipios con conclusión ligada a indicador Mongo | **10** | 10 | 4 Tier A (Donostia 126, Bilbao 204, Vitoria 39, Getxo 50) + `comparativa_3_municipios_mongo.csv` | Alta |
| C19 | 3+ conjuntos automáticos listos para representar | **10** | 10 | 24 CSV + 31 PNG, todos desde Mongo; 8 en `anexo/` | Alta |

**SBD RA4 = 50/50.** **SBD = 150/150 (100 % ponderado).** **Total rúbrica = 184/190 (96,8 %).**

## Tema 8 §16 (evaluación separada, no se suma a SBD)

| # | Criterio | Peso | Nota | Evidencia / objeción |
|---|---|---:|---:|---|
| T1 | Modelado documental | 15 % | **10** | 17 colecciones, decisión justificada, 7 preguntas respondidas |
| T2 | CRUD, limpieza y consultas | 15 % | **10** | 4 ops, 6 limpiezas, 30 consultas |
| T3 | Aggregation | 20 % | **10** | 11 pipelines, 8 etapas, reproducible |
| T4 | Índices y rendimiento | 15 % | **10** | ESR + `2dsphere` + único + multikey; IXSCAN 126/126 |
| T5 | Transacciones y consistencia | 10 % | **10** | Atómica documental + justificación de standalone |
| T6 | PyMongo profesional | 15 % | **8** | `lru_cache` contra el docstring; CI con `mongomock`; `addopts=-q` oculta el resumen de tests |
| T7 | Defensa técnica | 10 % | **7** | Deck con 295/293 tests (real 300/298); 0,988 sin declarar subconjunto; alias de consultas |

**Tema 8 ponderado = 9,40/10** (idéntico a v12: las notas no cambian, cambia la evidencia que las
sostiene y la lista de objeciones que el tribunal puede usar).

## Criterios que bajan respecto a v11

Ninguno. C2 y C4 siguen en 7 por las mismas dos razones (entorno y gate no-op), ahora con la
comprobación de que el gate **no** cambió y de que `run_vivo()` sigue vacío.
