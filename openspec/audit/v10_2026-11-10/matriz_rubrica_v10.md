# Matriz de rúbrica v10 — 19 criterios v2 + 7 Tema 8

**Fecha:** 2026-11-10 · **Modo:** solo lectura, evidencia ejecutada hoy
**Rúbrica:** `brief/RETO 1Evaluacion SBD-BDAv2.pdf` (76/76 celdas idénticas al contrato, 0 desviaciones literales)
**Escala:** niveles del PDF 0 / 3 / 7 / 10. La columna «Nota» es el nivel alcanzado, no una media inventada.

**Resumen:** BDA RA1 **37/40 (92,5 %)** · SBD RA1 **40/40** · SBD RA3 **60/60** · SBD RA4 **50/50** → **187/190 (98,4 %)**.
**SBD ponderado (46,7 + 13,3 + 40): 100,0 %.** BDA RA1 no tiene peso declarado en el PDF: no existe un porcentaje global único (H-07).

> Diferencia con la v9: la v9 puntuó C4 con 10. Esta v10 lo baja a **7** porque el nivel 10 literal exige «demuestra el flujo completo hasta MongoDB» y **no hay un comando único que lo ejecute de punta a punta hasta Mongo**: el gate offline no toca Mongo (solo lee ficheros y hace grep del loader), `--vivo` solo prueba TCP, y `run_mongo_pipeline` muta producción y no se ejecutó. La cadena existe por partes (extracción → silver → `load_all` → `clean_all` → agregación) y la rama Kafka termina en HDFS por decisión firmada. Se dan las dos lecturas: **7 literal / 10 con waiver aceptado**. Reverificado el 2026-11-10: **11/11 pipelines** ejecutados contra Mongo, `suma n_anuncios = 594`, explain COLLSCAN→IXSCAN, 13 CSV y 24 PNG generados en directorio temporal con huella reproducible (`0f15c729…76daa`).

---

## 1. BDA — RA1 (sin peso declarado en el PDF)

| # | Criterio (literal) | Nota | Evidencia ejecutada hoy | Qué falta para el 10 |
|---|---|---:|---|---|
| C1 | «Extracción de datos mediante Python» → 10: «Automatiza API y scraping» | **10** | 41 scripts en `extract/`; 11 con `requests`/`urlopen`; 6 con `BeautifulSoup`; `main_ingest.py` orquesta; 356 ficheros raw; manifest 354 SHA verificado | Nada. Riesgo menor: `zipfile.extractall` y `urlretrieve` sin timeout (P3) |
| C2 | «Almacenamiento HDFS» → 10: «Organiza originales y procesados y demuestra su recuperación» | **10** | **En vivo:** `LISTSTATUS` recursivo = **352 ficheros raw**; `OPEN` de `udalmap_vpo_terminadas.csv` devuelve **35.427 B con SHA idéntico** al local (`70a2937a…4706`). `data/procesado` en HDFS → **FileNotFoundException**, que es lo exigido: la profesora indicó **solo originales en HDFS**. Documentado en `README.md:108` y `arquitectura_datos.md:70` | Nada: el requisito aplicable es «originales en HDFS + recuperación demostrada», y se cumple |
| C3 | «Kafka» → 10: «Productor y consumidor Python funcionan y procesan mensajes» | **10** | **En vivo:** topic `vivienda_euskadi`, 1 partición; grupo `hdfs_centro`: `end_offset=352`, `committed=352`, **lag 0**; productor/consumidor Python en `storage/kafka_raw_producer.py` y `kafka_hdfs_uploader.py` | Nada. (El topic viejo `anuncios_inmobiliarios` conserva offset 1420: histórico, no vigente) |
| C4 | «Integración» → 10: «Demuestra el flujo completo hasta MongoDB» | **7** | Cadena por partes: `extract → raw → transform → silver → load_all → clean_all → pipeline`. Gate offline exit 0 (354 SHA + 188 silver + 14 colecciones + lag 0), pero **no ejecuta Mongo**; `run_mongo_pipeline --dry-run` solo hace `ping`; Kafka→HDFS no pasa por Mongo (decisión firmada) | Un único comando que ejecute extracción→carga→limpieza→agregación contra Mongo y lo demuestre (o un gate vivo real, no solo TCP) |

**BDA RA1: 10 + 10 + 10 + 7 = 37/40 (92,5 %).**

---

## 2. SBD — RA1 · peso 46,7 %

| # | Criterio (literal) | Nota | Evidencia ejecutada hoy | Qué falta para el 10 |
|---|---|---:|---|---|
| C5 | «Integración de fuentes» → 10: «Carga datos de 2 o más fuentes diferentes y las relaciona mediante al menos 1 campo común» | **10** | 14 colecciones vivas; `$lookup` `anuncios.ubicacion.codigo_ine → municipios._id`; 594 anuncios en 64 municipios; 252 municipios | **Reserva (H-03):** `municipios` **no expone `codigo_ine`** (`count_documents({"codigo_ine":{"$exists":true}}) = 0`); la relación va por `_id`. Técnicamente es campo común, pero un evaluador que busque `codigo_ine` no lo ve. Añadir el espejo `codigo_ine` en `municipios` |
| C6 | «Construcción del conjunto» → 10: «2 o más colecciones y demuestra al menos 1 relación, embedding o referencia» | **10** | 16 colecciones vivas + 14 `__backup`; `anuncios.ubicacion` anidado; `equipamiento[]`; `historico_precios[]`; referencing por `codigo_ine` | Nada |
| C7 | «Limpieza y transformación con PyMongo» → 10: «4 operaciones diferentes, incluyendo nulos/ausentes, duplicados y tipos/formato» | **10** | `storage/clean_mongo.py`: `canonicalize_codigo_ine`, `mark_nulls`, `resolve_duplicates`, `convert_types` (`$convert`), `clean_obsolete_fields`, `clean_null_markers` | Nada |
| C8 | «Automatización» → 10: «Un script o conjunto permite carga + limpieza + transformación, sin modificar manualmente MongoDB» | **10** | `scripts/run_mongo_pipeline.py`: `load_all → clean_all → ensure_indexes → pipeline_indicadores`; `--dry-run` validado (`ping=True`) | Nada. Matiz: no hay modo «todo read-only»; el pipeline completo muta prod por diseño |

**SBD RA1: 40/40 (100 %).**

---

## 3. SBD — RA3 · peso 13,3 %

| # | Criterio (literal) | Nota | Evidencia ejecutada hoy | Qué falta para el 10 |
|---|---|---:|---|---|
| C9 | «Modelado MongoDB» → 10: «decisión de embedding/referencing y explica por qué» | **10** | `openspec/archive/2026-11-10-docs/modelo_mongodb.md:24` §«Embedding vs referencing»; 7 preguntas del docx respondidas (`:150-156`); 1:N `municipios→anuncios`, 1:1 `alquiler`, N:M `promociones` | Nada. Solo actualizar cifras si cambian |
| C10 | «CRUD con PyMongo» → 10: «4 operaciones y comprueba mediante código que el resultado es el esperado» | **10** | `clean_mongo.demo_crud_operations`: insert_one/many, find, update_one, `$inc/$push/$addToSet`, upsert, `$unset/$rename/$pull`, bulk_write, delete_one/many, con contadores; `tests/test_mongo.py` verifica `delete_many==2` y `remaining` | Nada |
| C11 | «Consultas» → 10: «5 consultas útiles, una con anidados/arrays y otra con 2+ condiciones» | **10** | `analysis/mongo_queries.py` (292 líneas, 30 funciones): dot notation, `$elemMatch`, `$all`, `$size`, `$and/$or`, proyección, sort, skip/limit, `$regex`, `$type`, `$exists`; `test_mongo_queries` 6 tests | **Reserva (H-09):** `tests/test_mongo.py:132` tiene `assert "_id" not in d or True` (tautología). No invalida el criterio, pero el test de proyección no prueba nada |
| C12 | «Aggregation Pipeline» → 10: «3 pipelines, 5 etapas, `$group` y al menos una entre `$lookup`, `$unwind` o `$facet`» | **10** | 11 pipelines; etapas: `$match/$group/$lookup/$unwind/$addFields/$project/$sort/$limit/$sortArray/$filter/$map`; `$group` en `alquiler_por_municipio`, `modalidades`, `vpo_por_municipio`, `habitaciones`; `$lookup` + `$unwind` en varias | Nada. `$facet` no está implementado, pero la rúbrica admite `$lookup`/`$unwind` |
| C13 | «Índices y rendimiento» → 10: «compara explain() antes/después… identifica COLLSCAN/IXSCAN y totalDocsExamined» | **10** | **En vivo:** filtro `20069`; before `stage=COLLSCAN`, `nReturned=1`, `totalDocsExamined=594`; after `stage=IXSCAN`, `totalDocsExamined=1`, `totalKeysExamined=1`; 4 índices en `anuncios` (ESR, 2dsphere sparse, unique, multikey) | Nada |
| C14 | «Consistencia» → 10: «operación atómica y justifica por qué una transacción sería innecesaria» | **10** | `storage/mongo.py:170-200` `marcar_calidad_municipio` con `find_one_and_update` + `ReturnDocument.AFTER`; justificación en `modelo_mongodb.md:170-172` (standalone, sin replica set) | Nada |

**SBD RA3: 60/60 (100 %).**

---

## 4. SBD — RA4 · peso 40 %

| # | Criterio (literal) | Nota | Evidencia ejecutada hoy | Qué falta para el 10 |
|---|---|---:|---|---|
| C15 | «Datos heterogéneos» → 10: «fuentes con estructuras diferentes adaptadas mediante Python/PyMongo» | **10** | 7 formatos: CSV, JSON, XLSX, GeoJSON, ZIP, SHP, GTFS; normalización común, `_geo_point`, `ubicacion` anidada | Nada |
| C16 | «Automatización del análisis» → 10: «un script ejecuta todos los análisis principales y devuelve resultados preparados» | **10** | `analysis/run_analisis_mongo.py`: 11 pipelines, 8 CSV, 28+8 PNG, huella de reproducibilidad (2 pasadas), argparse «11 pipelines + 8 CSV» | Nada |
| C17 | «Indicadores» → 10: «5+ indicadores combinando 2+ fuentes» | **10** | Esfuerzo 18-34, esfuerzo por sexo, tensión social, paro Lanbide, precio/m² winsorizado, VPO terminadas, accesibilidad/tiempo a capital, habitaciones | **Reserva:** `tests/test_indicadores.py` solo lee el `.md`, no recalcula. El cálculo sí está en Mongo (11 pipelines) |
| C18 | «Respuesta al reto» → 10: «compara 3+ municipios y cada conclusión vinculada a un indicador calculado con MongoDB» | **10** | `comparativa_3_municipios_mongo.csv`: **4 filas** — Bilbao 204, Donostia 126, Getxo 50, Vitoria 39; esfuerzo 18-34 37,69 / 38,17 / 28,60 / 33,37; paro 9,71 / 5,82 / 6,40 / 8,89 | Nada. Solo declarar que Getxo vs Vitoria (11 anuncios) es orden frágil, ya escrito en la advertencia del CSV |
| C19 | «Preparación para visualización» → 10: «3+ conjuntos generados automáticamente mediante PyMongo» | **10** | `data/resultados`: **8 CSV `mongo_*`** + 28 PNG + 8 PNG de anexo; `EXPORTS_8` en `run_analisis_mongo.py` | **Reserva (H-10):** el test de artefactos 13 PNG/7 CSV se **skippea** (`test_pisos_ubicacion_real.py:202`). La evidencia está en disco, no en CI |

**SBD RA4: 50/50 (100 %).**

---

## 5. Tema 8 (evaluación separada, docx §16)

| # | Criterio | Peso | Nota | Evidencia | Hueco |
|---|---|---:|---:|---|---|
| T1 | Modelado documental | 15 % | **10** | 14 colecciones, embedding/referencing justificado, `_id`/tipos BSON, 7 preguntas respondidas | Mantener cifras al día |
| T2 | CRUD, limpieza y consultas | 15 % | **10** | `demo_crud_operations`, `clean_mongo` (6 ops), 30 consultas, tests con asserts | Arreglar el assert tautológico |
| T3 | Aggregation | 20 % | **10** | 11 pipelines, huella reproducible, 8 CSV | Nada |
| T4 | Índices y rendimiento | 15 % | **10** | 4 índices, explain real 594→1, justificación ESR/2dsphere/multikey/unique | Nada |
| T5 | Transacciones y consistencia | 10 % | **10** | Atómica documental + READ justificado en standalone | Nada |
| T6 | PyMongo profesional | 15 % | **8** | `MongoClient` único, `MONGO_URI`, `Decimal128`, cursores, `replace_collection` staging→rename, errores tipados | **H-04:** `get_client()` es `@lru_cache`, pero el docstring dice que lee `MONGO_URI` en cada llamada; un cambio de URI tras la primera conexión **no se aplica**. Además la suite no es hermética y el CI no levanta Mongo (H-08) |
| T7 | Defensa técnica | 10 % | **7** | Guion 10/12 min, 42 preguntas, checklist por criterio, reparto por persona | No es verificable por código; el checklist deja «ensayo individual» pendiente. Además hay que corregir `openspec/config.yaml` (Docker) antes de exponer |

**Tema 8 ponderado: (15×10 + 15×10 + 20×10 + 15×10 + 10×10 + 15×8 + 10×7) / 100 = 9,40/10 (94,0 %).**

---

## 6. Nota final y lectura

| Bloque | Puntos | Porcentaje |
|---|---:|---:|
| BDA RA1 (sin peso en el PDF) | 37/40 | 92,5 % |
| SBD RA1 (46,7 %) | 40/40 | 100,0 % |
| SBD RA3 (13,3 %) | 60/60 | 100,0 % |
| SBD RA4 (40 %) | 50/50 | 100,0 % |
| **Total bruto** | **187/190** | **98,4 %** |
| **SBD ponderado** | — | **100,0 %** |
| **Tema 8 ponderado** | — | **94,0 %** |

**Veredicto: PASS CON UNA RESERVA.** El proyecto acredita **18 de 19** criterios en el nivel máximo; solo **C4** queda en 7, y no por un fallo de ejecución sino porque no existe un comando único que recorra extracción → silver → Mongo → análisis. La cadena se verificó hoy por partes y funciona (11/11 pipelines, 594 anuncios cuadrados, explain real).

**Los tres puntos que un tribunal puede tumbar hoy:**

1. **C2** — «¿dónde están los procesados en HDFS?». Respuesta correcta: **la profesora pidió solo originales en HDFS**; se publican los 352 raw, la recuperación se demuestra con SHA idéntico y el silver vive en local por indicación expresa (`README.md:108`).
2. **C4** — «enséñame el flujo completo hasta Mongo». No hay un comando único que lo haga sin mutar producción; hay que ejecutar `run_mongo_pipeline.py` en vivo (muta) o aceptar la cadena por partes.
3. **H-05** — `openspec/config.yaml` sigue diciendo «HDFS y MongoDB en Docker… Kafka en una VM Ubuntu Server». Contradice la invariante «sin Docker» y la arquitectura vigente. Es el hallazgo más fácil de corregir y el más incómodo si se proyecta.
