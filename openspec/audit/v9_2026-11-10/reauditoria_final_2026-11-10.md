# Reauditoría final v9 — 2026-11-10

**Naturaleza:** verificación ejecutada tras cerrar el cambio `2026-11-10-defensa-v9-p0`.
**Entorno:** Mongo local operativo. HDFS centro (`10.22.87.215:50070`) y Kafka centro (`10.22.87.215:9092`) **no alcanzables** porque el usuario no está en el centro; no es un fallo del proyecto (se usa el histórico v8 y el gate offline lo declara `PENDA-01`).

---

## 1. Checks ejecutados

| Check | Comando | Resultado |
|---|---|---|
| Gobernanza | `scripts/verificar_gobernanza.py` | **exit 0** — 50 cabeceras (46 con ID canónico), 42 scripts, 34 DAG, 188 silver, 0 env sin declarar, 11 pipelines |
| Suite | `pytest tests -q` | **exit 0** — 235 passed + 2 skipped (237 collected) |
| Invarianza de prod | `list_indexes()` + recuentos antes/después | **idénticos** — 594 docs, 30 colecciones, 4 índices de negocio en `anuncios` |
| Explain | `explain_before_after()` | before **COLLSCAN** 594 docs; after **IXSCAN** 1 doc (`nReturned=1`, `keys=1`), filtro `20069` |
| DAG | `transform/run_all.py --check` | **exit 0** (34/34) |
| Gate offline | `scripts/gate_extremo_a_extremo.py --offline` | **exit 0** — 354 SHA + 188 silver + 14 colecciones + 0 duplicados + lag 0; `PENDA-01` |
| Fase de datos | `scripts/verificar_fase_datos.py` | **exit 1 solo por FAIL 07** conocido (paro-cero Aramaio 0,28 / Gaintza 1,45 / Usansolo 3,26), documentado sin enmascarar |
| Manifiestos | SHA `lanbide_paro_*` acta vs raw | **OK** (5/5) |
| Artefactos | `data/resultados` | 8 CSV `mongo_*` + 28 PNG + 8 PNG de anexo |
| Mongo | `pymongo` read-only | 594 anuncios, 252 municipios/indicadores/alquiler, 424 Point GeoJSON de 594 |

---

## 2. Rúbrica PDF (19 criterios)

**Cumplimiento: 19/19 con al menos un requisito y evidencia viva. Nota bruta 187/190 (98,4 %); SBD ponderado 100 %; BDA 37/40 (92,5 %).** El PDF no declara peso para BDA RA1 (H-R1), así que no existe un único porcentaje ponderado completo.

| # | Criterio | Nota | Evidencia verificada |
|---|---|---:|---|
| C1 | Extracción Python (API y scraping) | 10 | 41 scripts en `extract/`; APIs Eustat/INE/Udalmap; scrapers Fotocasa/Pisos/habitaciones; `main_ingest.py` orquesta |
| C2 | HDFS originales/procesados/recuperación | **7** | Raw 352 en HDFS y recuperación con SHA (histórico v8); `procesado` en HDFS sigue 404 → excepción declarada, no 10 literal |
| C3 | Kafka productor y consumidor | 10 | Topic `vivienda_euskadi` 1 partición, grupo `hdfs_centro` committed 352, lag 0 (histórico v8; hoy red no alcanzable) |
| C4 | Integración flujo completo a MongoDB | 10 | `gate_extremo_a_extremo --offline` OK; `extract → transform → load_mongo → Mongo → analysis` |
| C5 | Integración de fuentes (2+ y campo común) | 10 | 14 colecciones de negocio; `$lookup` `anuncios → municipios` por `ubicacion.codigo_ine` |
| C6 | Construcción (2+ colecciones + relación) | 10 | `municipios` con embedding; `anuncios` con `ubicacion` anidada, `equipamiento[]`, `historico_precios[]`; referencing por `codigo_ine` |
| C7 | Limpieza PyMongo (4+ ops) | 10 | `canonicalize_codigo_ine`, `mark_nulls`, `resolve_duplicates`, `convert_types` |
| C8 | Automatización carga+limpieza+transformación | 10 | `scripts/run_mongo_pipeline.py`; `load_all → clean_all → ensure_indexes → pipeline` |
| C9 | Modelado (+ embedding/referencing justificado) | 10 | `docs/modelo_mongodb.md` corregido: embedding en `municipios`; referencing por `codigo_ine` para `anuncios`/`etxebide_promociones` |
| C10 | CRUD 4 ops + comprobación | 10 | `demo_crud_operations` + asserts de `inserted_id`, counts, update y delete |
| C11 | Consultas (5 útiles, anidada/array, 2+ condiciones) | 10 | `mongo_queries.py`: dot notation, `$elemMatch`, `$and/$or`, proyección, sort |
| C12 | Aggregation (3+ pipelines, 5 etapas) | 10 | 11 pipelines con `$lookup`, `$unwind`, `$group`, `$match`, `$addFields`, `$project`, `$sort`, `$limit` |
| C13 | Índices (explain antes/después) | 10 | **Verificado en vivo**: índice ESR restaurado; COLLSCAN 594 → IXSCAN 1, `totalDocsExamined` 594 → 1 |
| C14 | Consistencia (atómica justificada o transacción) | 10 | `find_one_and_update` + `ReturnDocument.AFTER`; transacción justificada en standalone; test con valor nuevo |
| C15 | Datos heterogéneos | 10 | 7 formatos (CSV, JSON, XLSX, GeoJSON, ZIP, SHP, GTFS); normalización común y `_geo_point` |
| C16 | Automatización del análisis | 10 | `run_analisis_mongo.py`: 11 pipelines, huella, 8 CSV + 28+8 PNG; argparse ya dice 11 + 8 |
| C17 | Indicadores (5+, 2+ fuentes) | 10 | `docs/matriz_indicadores.md`: esfuerzo 18–34, tensión, paro Lanbide, precio m2, VPO |
| C18 | Respuesta al reto (3+ municipios) | 10 | 4 robustos Bilbao 204 / Donostia 126 / Getxo 50 / Vitoria 39, cada conclusión con indicador Mongo |
| C19 | Preparación para visualización (3+ conjuntos) | 10 | 8 CSV `mongo_*` + 28 PNG + 8 anexo, regenerables desde Mongo |

**Único criterio por debajo de 10: C2 (7).** No es una regresión: HDFS `procesado` nunca existió y está declarado como excepción; los originales y su recuperación sí están acreditados.

---

## 3. Tema 8 (7 criterios, docx §16)

| # | Criterio | Estado | Evidencia |
|---|---|---|---|
| T1 | Modelado documental | Cumple | `docs/modelo_mongodb.md` con 7 preguntas y decisión embedding/referencing |
| T2 | CRUD, limpieza y consultas | Cumple | `mongo_queries.py` (30 funciones), `clean_mongo.py`, tests con asserts |
| T3 | Aggregation | Cumple | 11 pipelines con etapas variadas y huella reproducible |
| T4 | Índices y rendimiento | Cumple | Explain real verificado (COLLSCAN 594 → IXSCAN 1) |
| T5 | Transacciones y consistencia | Cumple | Atómica + justificación READ en standalone |
| T6 | PyMongo profesional | Cumple | `get_client` reutilizable, URI configurable, carga segura con staging/backup/rename |
| T7 | Defensa técnica | Cumple con reserva | Guion corregido; quedan 3 líneas pre-existentes que contradicen el contrato (ver §4) |

---

## 4. Fallos potenciales y residuales

**No hay P0/P1. El proyecto funciona: suite, gate offline, gobernanza, DAG y explain pasan.**

| Sev. | Hallazgo | Estado | Impacto / recomendación |
|---|---|---|---|
| **P2** | `openspec/project.md:30` dice «MongoDB (Docker Desktop)» y `:38` dibuja `Kafka → MongoDB` | **Abierto (fuera de alcance declarado)** | Contradice `ARQUITECTURA-01` (sin Docker; Kafka→HDFS, nunca Mongo). Riesgo si el tribunal lee el project.md. Corregir en una ronda documental posterior |
| **P2** | `docs/guion_defensa.md:5` presenta HDFS/Kafka como disponibles («lag 0») | **Abierto (fuera de alcance declarado)** | Hoy no hay red al centro. Añadir la reserva «evidencia histórica v8; revalidación pendiente» antes de la defensa |
| **P2** | `INDICES-01` del spec principal aún describe «GIVEN el índice eliminado» | **Pendiente de archive** | El delta de este cambio ya fija el hint read-only; el spec principal se sincroniza al archivar el cambio. No afecta al código |
| **P2** | H-08: `extract/26_vpo_terminadas.py` no regenera el manifest al promover un raw nuevo | **Abierto (P2 diferido)** | Solo afecta a una extracción futura con fuente cambiada; el raw actual está congelado y su SHA verificado |
| **P2** | H-09: `docs/contrato_datos_raw.md` vs `.FROZEN` de `transform/_raw_guard.py` | **Abierto (P2 diferido)** | Incoherencia documental sobre cómo se marca el raw; no afecta a la ejecución |
| **P3** | H-10: `validar()` de VPO no comprueba pertenencia a `dim_municipios` | **Abierto (P3)** | El join posterior descarta códigos ajenos; conviene añadirlo si se reextrae |
| **P3** | HM-06: `anuncios_habitaciones_unificados` y `_bigdata` duplican 201 `_id` | **Abierto (decisión pendiente)** | Elegir la canónica y retirar la otra; no afecta a los 11 pipelines |
| **P3** | DS2-25: huella de los 11 pipelines no registrada en el repo | **Abierto** | Requiere ejecutar `run_analisis_mongo` completo (fuera del alcance de este cambio) |
| **P3** | R-4: al aislar `test_mongo_geo.py` se pierde la aserción sobre el geo real de prod | **Mitigado** | 424/594 verificados por sonda read-only y documentados; el test ya no muta prod |
| **P3** | Cifras `759` en documentos históricos (`docs/auditoria_10_10_SDD_2026-11-05.md`, `docs/analisis_vault_vs_rubrica.md:4,24`) | **Aceptado como histórico** | Están fechados o describen el vault auditado; no se presentan como vigentes. `docs/reglas_limpieza.md:54` sí se corrigió a 594 |
| **Conocido** | FAIL 07 de `verificar_fase_datos.py` (paro-cero Aramaio 0,28 / Gaintza 1,45 / Usansolo 3,26) | **Documentado, sin enmascarar** | Es un dato real del INE/Lanbide; no se toca para forzar el gate |
| **Entorno** | HDFS/Kafka centro no alcanzables | **No es fallo** | El usuario no está en el centro; el gate offline sigue en OK y C2/C3 se sostienen con el histórico v8 |

---

## 5. Veredicto

- **Rúbrica PDF: 19/19 cubiertos** (C2 en 7 por `procesado` HDFS; resto en 10).
- **Tema 8: 7/7 cubiertos**, con reserva documental en T7.
- **Código y datos:** suite verde, prod intacta, explain real, gobernanza TODO OK, gate offline OK, DAG OK.
- **Sin P0/P1.** Los residuales son documentales o P2/P3 ya declarados; ninguno bloquea la defensa, pero los dos primeros (project.md y guion:5) conviene corregirlos antes de la exposición.
