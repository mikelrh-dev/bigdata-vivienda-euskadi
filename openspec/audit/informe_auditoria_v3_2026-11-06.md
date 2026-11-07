# Auditoría v3 — `bigdata-vivienda-euskadi`

**Fecha:** 2026-11-06 · **Modo:** solo lectura · **Rúbrica:** `brief/RETO 1Evaluacion SBD-BDAv2.pdf` + `brief/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx`

**Cambios realizados durante la auditoría:** ninguno. Este `.md` es el único fichero nuevo.
`git status` al abrir y al cerrar: idéntico (11 ficheros `M`/`D` previos de la sesión anterior + 2 untracked previos + este informe).

**Reglas aplicadas**

1. **Umbral literal.** Nota 10 solo si se cumple la columna del 10 palabra por palabra. "Casi" = 7.
2. **Evidencia triple.** Comando + salida numérica + `fichero:línea`. Sin las tres, no hay 10.
3. **La documentación no es evidencia** (P-08). "9 pipelines" en un README no cuenta: cuentan los `pipeline_*` que devuelven filas.
4. **No verificable ≠ 10.** Se marca `PENDIENTE` con lo que falta exactamente.
5. **Prueba de falsación.** Cada 10 frágil lleva anotado qué lo bajaría a 7.
6. **Datos reales** (P-01/02/03/05).

**Acceso limitado:** sin clúster HDFS ni broker Kafka. Se usa la evidencia **congelada** del 2026-11-06, que sirve para **no bajar** la nota por falta de acceso, nunca para subirla.

---

## 1. F1 — Fidelidad de la rúbrica (nueva fase prioritaria)

Cotejo del **binario** (PDF de 6 páginas extraído con `pypdf`; docx leído del `word/document.xml`) contra `openspec/specs/contrato-reto/spec.md`.

| Elemento | PDF / docx | `contrato-reto/spec.md` | Veredicto |
|---|---|---|---|
| BDA RA1, 4 criterios | pág. 3 | tabla BDA RA1 | **Idéntico** |
| SBD RA1, peso 46,7 % | pág. 4 | 46,7 % | **Idéntico** |
| SBD RA1, 4 criterios | pág. 4 | tabla (líneas 44-49) | **Idéntico** |
| SBD RA3, peso 13,3 % | pág. 5 | 13,3 % | **Idéntico** |
| SBD RA3, 6 criterios | pág. 5 | tabla (líneas 58-66) | **Idéntico** |
| SBD RA4, peso 40 % | pág. 6 | 40 % | **Idéntico** |
| SBD RA4, 5 criterios | pág. 6 | tabla (líneas 74-81) | **Idéntico** |
| Tema 8, 7 bloques y pesos 15/15/20/15/10/15/10 | docx líneas 221-245 | tabla Tema 8 | **Idéntico** |

**Conclusión F1:** la transcripción **no suavizó ni endureció nada**. Los 19 criterios + 7 bloques son literales. Cualquier nota de este informe se puede defender leyendo el PDF en voz alta.

**Matiz que sí importa (no es infidelidad, es riesgo de encaje):** el 10 de BDA «Integración» dice literalmente *«Demuestra el flujo completo hasta MongoDB»*. El proyecto tiene **dos ramas** (fuente→silver→Mongo y `data/raw`→Kafka→HDFS) y la rama Kafka **no** termina en Mongo, por indicación expresa de la profesora. Se defiende como waiver, no como cambio de rúbrica.

---

## 2. Matriz de 26 criterios

### BDA — RA1 (4 criterios, sin peso en la nota SBD)

| # | Criterio | Umbral 10 (literal) | Evidencia medida hoy | Nota | Riesgo |
|---|---|---|---|---|---|
| 1 | Extracción de datos | Automatiza **API y scraping** | **API:** 8 extractores con `requests` + `_common.Cliente` (`11_transporte_gtfs_paradas`, `19_udalmap_indicadores_adicionales`, `20_ecvi_compraventa`, `26_vpo_terminadas`, `educacion_centros`, `salud_centros`, `ine_atlas_renta`, `udalmap_empleo`). **Scraping:** `05_fotocasa_scraper.py:43-55` (regex sobre `<script type="application/json">` del HTML de Fotocasa), `08_pisos_scraper.py:54-70` (regex sobre `ad-preview__price/title`), `13_scraping_habitaciones.py:55`, `fotocasa_detalle.py:16`, `09_fotocasa_dirigido.py`, `10_scraping_faltantes.py`. **41 scripts**, **34/41** generan sidecar `.meta.json`. Resultado: 759 anuncios de 3 portales (fotocasa 428 / pisos 247 / realtyapi 84) | **10** | Bajo. El scraping es a mano con regex (sin `BeautifulSoup`), frágil ante rediseño, pero es scraping real sobre HTML |
| 2 | Almacenamiento HDFS | *«Organiza **originales y procesados** y demuestra su recuperación»* | Originales: **352 ficheros / 895.596.949 B** idénticos, **13/13** SHA `Igual? True`. Recuperación: `scripts/hdfs_recuperacion_un_fichero.py`, `storage/hdfs_utils.py`. **Procesados: NO se suben** (waiver verbal de la profesora) | **7 literal / 10 con waiver** | **Alto.** Es el único criterio por debajo del 10 literal. Sin el waiver son 7 puntos de 4 |
| 3 | Kafka | Productor **y consumidor** Python funcionan y procesan mensajes | Productor `storage/kafka_raw_producer.py` (`DEFAULT_BOOTSTRAP_SERVERS=10.22.87.215:9092`, `produce()` con Future + `add_callback`/`add_errback`). Consumidor `storage/kafka_hdfs_uploader.py` con `poll()` + `KAFKA_IDLE_MS` (el `for msg in consumer` está eliminado), `timeout=60`. Evidencia congelada: 352 manifiestos, offsets `0:1068..0:1419`, **1420 mensajes**, **lag 0**, `HDFS_CENTRO_UPLOADED 352`. Tests offline: `tests/test_kafka_pipeline.py` 11 passed | **10** | Bajo. Sin broker vivo, la demo en clase necesita el clúster |
| 4 | Integración | *«Demuestra el flujo completo hasta MongoDB»* | Cadena real: HTTP/scraping → `data/raw` (356) → silver (41 CSV) → `load_mongo.load_all()` → **14 colecciones**, con **759/759** anuncios enlazados a municipio y **252/252** en 10 colecciones. Rama Kafka→HDFS separada por indicación de la profesora | **10** | Medio. Un tribunal que exija Kafka *en el camino a Mongo* aplicaría el 7. Preparar la frase de waiver |

### SBD — RA1 (peso 46,7 %) — 4 criterios

| # | Criterio | Umbral 10 | Evidencia medida hoy | Nota | Riesgo |
|---|---|---|---|---|---|
| 5 | Integración de fuentes | ≥2 fuentes **y** relación por ≥1 campo común | **14 colecciones reales**. Join por `_id`: alquiler 252/252, certificados 252/252, vpo 252/252, osrm 252/252, udalmap_extendido 252/252, udalmap_indicadores 252/252, udalmap_empleo 252/252, etxebide_solicitudes 252/252, indicadores 252/252, promociones 77/77. Join por `ubicacion.codigo_ine`: anuncios **759/759**, 0 sin código. `ecvi_compraventa` 7/29 (parcial) | **10** | Bajo. No decir "12 colecciones al 100 %": son 11 + ecvi parcial |
| 6 | Construcción del conjunto | ≥2 colecciones **y** relación/embedding/referencia demostrada | **Embedding:** `municipios.demografia` anidado en 252/252, `anuncios.ubicacion` anidado con GeoJSON en 424, `certificados.distribucion` anidado. **Referencing:** `_id` = `codigo_ine` de 5 dígitos (11 colecciones). **Arrays:** `equipamiento` en 759 | **10** | Bajo |
| 7 | Limpieza y transformación | ≥4 operaciones distintas **incluyendo nulos, duplicados y tipos** | `storage/clean_mongo.py`: (1) `canonicalize_codigo_ine()` — `$set` de códigos; (2) `mark_nulls()` — `update_many` con flags `tiene_superficie`/`calidad_*`; (3) `resolve_duplicates()` — `aggregate` + `delete_many`; (4) `convert_types()` — `$convert` a decimal/int/bool; (5) `clean_obsolete_fields()` — `$unset`. **5 operaciones**, las 4 categorías exigidas cubiertas. Medido: **0 duplicados** `(portal, id_anuncio)`, 722/759 `precio_eur` en `Decimal128` | **10** | Bajo |
| 8 | Automatización | Un script/conjunto ejecuta **carga + limpieza + transformación** sin tocar Mongo a mano | `storage/load_mongo.py:load_all()` (14 loaders + `ensure_indexes()` que ahora **propaga** el error), `clean_all()`, `scripts/run_mongo_pipeline.py`, `transform/run_all.py` (35 scripts en `run_manifest.json`) | **10 condicional** | Medio. Verificado por código + artefactos; **no re-ejecutado** para no escribir en `data/` durante la auditoría |

### SBD — RA3 (peso 13,3 %) — 6 criterios

| # | Criterio | Umbral 10 | Evidencia medida hoy | Nota | Riesgo |
|---|---|---|---|---|---|
| 9 | Modelado | ≥2 colecciones con tipos adecuados **+ 1 decisión embedding/referencing explicada** | 14 colecciones; tipos BSON reales (`Decimal128` 722, `bool`, `datetime` `fecha_carga`, `GeoJSON Point` 424, arrays). Decisión: **embedding** de lo que se lee junto (demografía, ubicación) y **referencing** por `codigo_ine` para lo que crece (anuncios). Justificación en `docs/modelo_mongodb.md` | **10** | Bajo. La explicación vive en documentación; el esquema la demuestra |
| 10 | CRUD | 4 operaciones **+ comprobación por código** | `storage/clean_mongo.py:demo_crud_operations()`: `insert_one`, `insert_many`, `find_one`, `find`, `update_one` (`$set/$inc/$push/$addToSet`), `find_one_and_update` (:329), `upsert`, `$unset`, `$rename`, `$pull`, `bulk_write` (:344), `delete_one`, `delete_many`; contadores `_counter()`. Tests: `tests/test_mongo.py:222-224` | **10** | Bajo |
| 11 | Consultas | ≥5 útiles, **una con anidados/arrays** y **otra con 2+ condiciones** | `analysis/mongo_queries.py`: 20+ funciones. Medido: `anuncios_por_municipio("48001")` → 3; `anuncios_por_municipio("48020", modalidad, precio_max=1500)` → **24** (2 condiciones); `dot_notation_municipio("48020")` → 50 (anidado); `anuncios_regex("ubicacion.municipio","vitoria")` → 39; `anuncios_exists` → 100; `proyeccion`/`sort`/`skip` → 5 cada una. **Array: `anuncios_con_equipamiento("exterior")` → 79** (`ascensor` no está en el array; P1-02 corregido) | **10** | **Bajo desde el arreglo.** Ver P1-02: el vocabulario real es `exterior`(79), `balcon`(15), `interior`(10), `parking`(7); 679/759 sin equipamiento. Si se enseña "ascensor" en vivo, salen 0 filas |
| 12 | Aggregation | ≥3 pipelines del reto, **5 etapas**, `$group` + (`$lookup`\|`$unwind`\|`$facet`) | **9 pipelines**; **8 etapas distintas** (`$match,$group,$lookup,$unwind,$addFields,$project,$sort,$limit`); `$group` sí, `$lookup` y `$unwind` sí. Ejecutados hoy: indicadores **252**, alquiler 252, modalidades 2, top esfuerzo 10, sexo 252, accesibilidad 252, udalmap+osrm 252, VPO promociones 322, VPO terminadas 251 | **10** | Bajo |
| 13 | Índices | `explain()` antes/después, `COLLSCAN`/`IXSCAN` y `totalDocsExamined` | **Medido hoy sin borrar ningún índice** (`hint: {$natural:1}`): filtro `ubicacion.codigo_ine=48001 + modalidad=larga_estancia + precio_eur ≤ Decimal128(1000)` → **COLLSCAN docs=759 keys=0** vs **IXSCAN docs=1 keys=1**, `nReturned=1` en ambos. **9 índices**: ESR, `2dsphere` sparse, multikey, `unique` `(portal,id_anuncio)`. `analysis/mongo_indexes.py:44` `_explain`, `:112` `explain_before_after`. Test: `tests/test_mongo_indices.py:21-22` | **10** | Bajo. La versión con `drop_index` también existe y la usa el test |
| 14 | Consistencia | Transacción real **o** atómica demostrada por código + justificación | `storage/mongo.py:197` `find_one_and_update(..., ReturnDocument.AFTER)` en `marcar_calidad_municipio`; rechaza valor fuera de dominio con `ValueError` sin escribir. Test: `tests/test_mongo_consistencia.py:93` aserta el uso en el fuente; `:111` sonda `start_session`/`start_transaction` que en standalone queda `rechazado-standalone`; prod invariante 759/252 | **10** | Bajo. La justificación técnica de "por qué no hace falta transacción" es documental |

### SBD — RA4 (peso 40 %) — 5 criterios

| # | Criterio | Umbral 10 | Evidencia medida hoy | Nota | Riesgo |
|---|---|---|---|---|---|
| 15 | Datos heterogéneos | Fuentes con **estructuras diferentes** adaptadas con Python/PyMongo | CSV (Eustat), JSON anidado (Udalmap, Etxebide), XLSX (ECVI), GTFS (transporte), HTML scrapeado (Fotocasa/Pisos), API JSON (INE, B5M). En Mongo: 424 con GeoJSON, 759 con array, 252 con documento anidado, 2 tipos de precio (Decimal 722) | **10** | Bajo |
| 16 | Automatización del análisis | Un script ejecuta **todos** los análisis y devuelve resultados preparados | `analysis/run_analisis_mongo.py` orquesta los pipelines, imprime `explain before/after` y escribe 5 CSV + 13 PNG desde Mongo (sin DuckDB) | **10 condicional** | Medio. No re-ejecutado: escribe en `data/resultados/`. En la defensa, ejecutarlo delante |
| 17 | Indicadores | ≥5 combinando **2+ fuentes** | Medido sobre 252 municipios: `esfuerzo_joven_pct` **252**, `esfuerzo_joven_pct_18_34` **252**, `cuantia_alquiler_mes` **252**, `renta_m2_alquiler` **252**, `tension_demanda_social` **252**, `n_anuncios` **252**, `tasa_paro_lanbide_pct` **249**, `superficie_media_m2` **82**, `precio_medio_eur` **80**. Fuentes cruzadas: anuncios (3 portales) + Eustat alquiler + Eustat renta + Lanbide + Etxebide + Udalmap | **10** | Bajo |
| 18 | Respuesta al reto | ≥3 municipios comparados, **cada conclusión vinculada a un indicador de Mongo** | `esfuerzo_joven_pct` es calculable en **252/252** municipios. Comparativa de 4 robustos con `n` real: Bilbao 48020 (173 anuncios), Donostia 20069 (113), Getxo 48044 (40), Vitoria-Gasteiz 01059 (39); **83** municipios con anuncios. Salida: `data/resultados/comparativa_3_municipios_mongo.csv` | **10** | Medio. `precio_medio_eur` solo en 80/252: no generalizar conclusiones de precio a los 252 |
| 19 | Preparación para visualización | ≥3 conjuntos generados automáticamente por PyMongo | `data/resultados/`: **5 CSV Mongo** (`mongo_esfuerzo_por_municipio`, `mongo_alquiler_por_municipio`, `mongo_modalidades`, `mongo_accesibilidad_extendida`, `mongo_vpo_por_municipio`, `mongo_vpo_terminadas_por_municipio` = 6) + **13 PNG** + 2 dashboards. **28 ficheros** | **10 condicional** | Medio. Ficheros presentes; no regenerados hoy (mismo motivo que #16) |

### Tema 8 — evaluación separada (no se mezcla con 46,7/13,3/40)

| Bloque | Peso | Qué se valora (docx) | Evidencia | Nota |
|---|---|---|---|---|
| Modelado documental | 15 % | Diseño coherente y decisiones justificadas | Embedding/referencing + tipos BSON medidos | **10** |
| CRUD, limpieza y consultas | 15 % | PyMongo, tipos, operadores, arrays, embebidos | 13 métodos + 5 limpiezas + 20 consultas | **9** (por P1-02: ejemplo de array devuelve 0) |
| Aggregation | 20 % | Pipelines útiles, correctos, explicados y ligados al reto | 9 pipelines, 8 etapas, todos devuelven filas | **10** |
| Índices y rendimiento | 15 % | Índices justificados + evidencia `explain()` | COLLSCAN 759 → IXSCAN 1 medido hoy | **10** |
| Transacciones y consistencia | 10 % | Decisión razonada e implementación correcta | Atómica + sonda standalone | **9** (la razón "no necesito transacción" está en prosa, no en aserción) |
| PyMongo profesional | 15 % | Organización, conexión, errores, resultados, reproducibilidad | `get_collection` único, `ensure_indexes` ya no silencia, 145 tests | **9** (`_common._load_env` duplica la carga de `.env`) |
| Defensa técnica | 10 % | Capacidad individual de explicar | No auditable sin defensa | **PENDIENTE** |

**Ponderado Tema 8 sobre el 90 % evaluable: 8,6 / 9,0 = 9,6.**

---

## 3. Hallazgos

| ID | Sev. | Hallazgo | Evidencia | Impacto | Acción sugerida |
|---|---|---|---|---|---|
| P1-01 | Alta | HDFS solo aloja `raw`; el 10 pide «originales **y procesados**» | `HDFS_CENTRO_UPLOADED 352`; no hay `/data/procesado` en HDFS | −3 pts en BDA criterio 2 (10→7) | Documentar el waiver en una línea y **ofrecerlo** antes de que lo pregunten |
| P1-02 | Alta | La consulta de array documentada devuelve **0 filas** con datos reales | `anuncios_con_equipamiento("ascensor")` → 0; vocabulario real: `exterior` 79, `balcon` 15, `interior` 10, `parking` 7; 679/759 vacíos | Riesgo de demo en vivo + Tema 8 «CRUD/consultas» a 7 | ✅ **Resuelto 2026-11-06**: demo y doc usan `exterior`; `tests/test_mongo_queries.py` lo bloquea |
| P1-03 | Alta | Contadores obsoletos en documentación activa | `README.md:101,248` dicen **351** ficheros (son 352); `README.md:108,143,253`, `AGENT.md:9`, `docs/guion_defensa.md:22,34,41`, `docs/guion_defensa_12min.md:36,168`, `docs/informe_final.md:135`, `docs/metodologia.md:16`, `docs/arquitectura_datos.md:26,59` dicen **136 tests** (son **145**); `docs/preguntas_analisis_profesional.md:99,120` dicen **16 colecciones** (son 14 reales) | Contradicción audible en defensa | ✅ **Resuelto 2026-11-06** (barrido aplicado en 8 ficheros) |
| P1-04 | Alta | **Dos entrypoints Mongo que nadie encadena.** `run_mongo_pipeline.py` hace carga+limpieza+índices+**un** pipeline; los 6 CSV y 13 PNG de RA4 los produce otro script (`run_analisis_mongo.py`) que no se invoca desde el primero | `scripts/run_mongo_pipeline.py:88-92` vs `analysis/run_analisis_mongo.py:456`; `grep run_analisis_mongo --include=*.py` solo lo llama el test | RA4 #16 queda a expensas de teclear el segundo comando | Encadenar `run_analisis_mongo` como paso 5, o un `make mongo` |
| P2-01 | Media | `precio_medio_eur` y `superficie_media_m2` existen solo en 80 y 82 de 252 municipios | Medición de `pipeline_indicadores_municipio` | Cualquier ranking de precio es de 83 municipios, no de Euskadi | Decirlo explícitamente al presentar el ranking |
| P2-02 | Media | `ecvi_compraventa` no está enlazada: 7/29 documentos con `codigo_ine` | `INE ecvi_compraventa 7 / 29` | Si se afirma «todas las colecciones se relacionan», es falso | Excluirla del recuento o derivar el código en el loader |
| P2-03 | Media | `historico_precios` es un array **vacío en 759/759** | `HIST_ARRAY 759`, `HIST_VACIO 759` | El «array» del embedding es decorativo; los arrays reales son `equipamiento` | Usar `equipamiento` como array en la demo; no presumir de histórico |
| P2-04 | Media | `pipeline_modalidades` devuelve 2 filas | Ejecutado: 2 | Pipeline válido pero pobre como «pregunta del reto» | Enseñarlo como apoyo, no como pipeline estrella |
| P2-05 | Media | «Defensa técnica» (10 % Tema 8) no es auditable | — | Nota Tema 8 queda en 9,6 sobre el 90 % | Preparar el guion de 12 min |
| P3-01 | Baja | Scraping con regex, sin parser HTML | `05_fotocasa_scraper.py:43`, `08_pisos_scraper.py:62` | Frágil ante rediseño; no resta | No cambiar antes de la entrega |
| P3-02 | Baja | `data/raw` tiene 356 ficheros y el manifest 354 | Faltan en manifest `.FROZEN` y `.gitkeep` | Coherente, pero un `verify` estricto chirría | Whitelist explícita de los 2 |
| P3-03 | Baja | `extract/_common._load_env` reimplementa `dotenv` | `_common.py:20-38` | Duplicidad de configuración | Anotar como deuda |
| P3-04 | Baja | `.env` existe en disco (1.580 B) pero está ignorado | `.gitignore:1` | Sin fuga; P-07 **cumple** | Nada |
| P3-05 | Baja | `ensure_indexes()` se ejecuta dos veces por pasada | `storage/load_mongo.py` lo llama dentro de `load_all()`; `scripts/run_mongo_pipeline.py` lo vuelve a llamar tras `clean_all()` | Idempotente, pero duplica trabajo | Dejar una sola llamada, al final |
| P3-06 | Baja | `clean_all()` recorre las 14 colecciones **cuatro veces** | `clean_anuncios`, `clean_municipios` y `clean_alquiler` llaman cada uno a `canonicalize_codigo_ine()`, más `clean_nuevas()` | Lentitud, no incorrección | Extraer el canonicalizado a un paso único |
| P3-07 | Baja | `load_anuncios()` hace upsert pero **no poda** | `storage/load_mongo.py` (`update_one(..., upsert=True)` sin `delete_many` de huérfanos) | Si silver pierde un anuncio, Mongo lo conserva. Hoy 759 CSV = 759 Mongo, sin deriva | Añadir poda por `id_anuncio` ausente |

### 3.1 Orquestación Mongo — estado real (consulta 2026-11-06)

**Lo que sí está resuelto.** El problema histórico `H-19` de `openspec/audit/auditoria_estres_2026-10-31.md:285` («18 scripts sin orquestar: el pipeline no se reconstruye desde cero») era del orquestador **silver**, no de Mongo. Hoy `transform/run_all.py` declara 35 scripts + 7 `EXCLUIDOS` con motivo firmado, y `run_manifest.json` lo prueba. La cadena Mongo sí tiene entrypoint único y **orden garantizado por test**: `tests/test_mongo_pipeline.py` aserta `[load_all, clean_all, ensure_indexes, pipeline_indicadores_municipio]`.

**Lo que sigue mal, en orden de gravedad:**

1. **El análisis no está en el pipeline.** `run_mongo_pipeline.py` termina en *un* pipeline (`pipeline_indicadores_municipio`, `:88-92`). Los 9 pipelines, los 6 CSV y los 13 PNG salen de `analysis/run_analisis_mongo.py`, que **ningún script del repo invoca** (`grep` solo encuentra `tests/test_mongo_orquestador.py`). Son dos comandos manuales, no uno. Esto es exactamente lo que el criterio RA4 «Automatización del análisis» pide como *un* script.
2. **El comando documentado como «carga» no limpia.** `README.md:254` presenta `storage/load_mongo.py` como primera vía: ejecuta `load_all()` (que recrea colecciones con `replace_collection`) y deja la base **sin** `clean_all()` ni la poda. Quien siga el README al pie de la letra obtiene 759 anuncios sin flags de calidad ni deduplicación resuelta.
3. **Sin orquestador extremo a extremo.** Nada ejecuta `extract → transform → load → clean → analysis` en una sola orden; `verificar_fase_datos.py:94-97` solo valida `transform/run_all.py --dry-run`. La reproducibilidad depende de tres comandos tecleados en el orden correcto por una persona.
4. **`--dry-run` valida poco.** Solo imports + `ping()`; no comprueba que los 14 loaders existan ni que `clean_all` devuelva contadores. El contrato de orden lo cubre el test, no el dry-run.

**Inventario: no existe un `run` global.** Glob en la raíz del repo → **0** `Makefile`, `*.sh`, `run.py`, `*.bat`. Lo que hay son 5 entrypoints parciales más un verificador:

| # | Paso | Comando | Alcance |
|---|---|---|---|
| 1 | Extracción | `extract/main_ingest.py` (`--mode live/replay-raw`) | 41 scripts → `data/raw` (356) |
| 2 | Silver | `transform/run_all.py` (DAG, `--check`, `--dry-run`) | 35 scripts → `data/procesado` |
| 3 | Mongo carga+limpieza+índices | `scripts/run_mongo_pipeline.py` (**o** `storage/load_mongo.py`, que no limpia) | 14 colecciones |
| 4 | Análisis + export | `analysis/run_analisis_mongo.py` | 9 pipelines → 6 CSV + 13 PNG |
| 5 | Kafka→HDFS | `storage/kafka_raw_producer.py` + `storage/kafka_hdfs_uploader.py` (dos procesos) | 352 ficheros → HDFS |
| — | Verificación | `scripts/verificar_fase_datos.py` | 18 checks; comprueba, no produce |

**El único gate extremo a extremo que existió está archivado.** `scripts/gate_bloque2.py` → `archive/kafka_2026-11-06/scripts_gate_bloque2.py`; el propio spec lo asume (`openspec/specs/almacenamiento-y-streaming/spec.md:4`: «No hay script de gate único»). Y su lógica era Kafka→Mongo, que ya no es la arquitectura vigente. Hoy el flujo completo existe **como procedimiento escrito**, no como comando.

**Ninguno de estos 4 puntos baja una nota por sí solo** (los 10 se sostienen por código + artefactos), pero el nº1 y el nº2 son los que pueden romper la demo: el nº1 porque un tribunal puede pedir «ejecuta el análisis» y aparecer un segundo comando que no estaba en el guion; el nº2 porque el orden de los comandos del README deja la base a medio limpiar.

---

## 4. Contradicciones documentales (F9)

Verificadas con `grep -rn` sobre documentación **activa**. Los registros históricos (`docs/trazabilidad_vm.md`, `docs/auditoria_10_10_SDD_2026-11-05.md`, `archive/`, `openspec/changes/*`) conservan VM `192.168.201.162:9094`, 3 particiones y 130/136 tests **a propósito**: son logs de lo que pasó.

| Dato | Valor real medido | Dónde está mal |
|---|---|---|
| Ficheros raw en HDFS | **352** | `README.md:101`, `README.md:248` (351) |
| Tests | **145** | `README.md:108,143,253`; `AGENT.md:9`; `docs/guion_defensa.md:22,34,41`; `docs/guion_defensa_12min.md:36,168`; `docs/informe_final.md:135`; `docs/metodologia.md:16`; `docs/arquitectura_datos.md:26,59` |
| Colecciones | **14 reales** + 13 `__backup` | `docs/preguntas_analisis_profesional.md:99,120` (16) |
| Manifest raw | **354** | `AGENT.md:9` dice 354 → correcto; el resto de docs dicen 136/351 |

---

## 5. Cobertura criterio → test (F8)

`pytest tests --collect-only -q` → **151 tests collected** (145 al auditar + 6 de `test_mongo_queries.py`).

| Fichero | Tests | Criterios que cubre |
|---|---|---|
| `test_contrato.py` | 54 | EXTRACCION-01/02, LIMPIEZA-01, P-01…P-08 |
| `test_mongo.py` | 25 | CRUD, limpieza, pipelines, índices |
| `test_fase_datos.py` | 18 | gate de datos, huella |
| `test_kafka_pipeline.py` | 11 | productor/consumidor, SHA, rutas |
| `test_vpo_municipal.py` | 6 | indicador VPO (flujo, no stock) |
| `test_hdfs.py` | 6 | rutas HDFS, guardrails |
| `test_raw_guardrails.py` | 5 | inmutabilidad de `raw` |
| `test_raw_inmutable.py` | 4 | `.FROZEN`, hashes |
| `test_crudos.py` | 3 | datos crudos reales |
| `test_mongo_queries.py` | 6 | consultas del reto devuelven filas (P1-02) |
| resto (8 ficheros) | 13 | índices, consistencia, geo, indicadores, fuentes |

**Huecos de cobertura (ninguno exigido por la rúbrica, todos son riesgo de demo):**

1. ~~No hay test que exija que las **5 consultas** devuelvan `>0` filas.~~ **Resuelto el 2026-11-06**: `tests/test_mongo_queries.py` exige `>0` filas en 5 consultas y en la demo.
2. No hay test de que `run_analisis_mongo.py` produzca los **6 CSV + 13 PNG** (solo existen los ficheros).
3. «Defensa técnica» y «justificación de no usar transacción» son prosa, no aserciones.

---

## 6. Pruebas de falsación de los 10 más frágiles

| Criterio | Qué lo bajaría a 7 |
|---|---|
| #2 HDFS | Que el tribunal no acepte el waiver de «solo raw» → 7 directo |
| #4 Integración | Exigir Kafka en el camino a Mongo → 7 |
| #11 Consultas | Enseñar `ascensor` en vivo y salir 0 filas → sensación de consulta inútil |
| #18 Respuesta al reto | Presentar el ranking de precio como si cubriera 252 municipios (solo 80) |
| #8/#16/#19 | Que fallen delante del tribunal al re-ejecutarlos (no los he ejecutado hoy) |
| #14 Consistencia | Responder «no hace falta transacción» sin enseñar el `find_one_and_update` ni la sonda |

---

## 7. Lo que no pude verificar

| Elemento | Motivo | Trato |
|---|---|---|
| HDFS vivo | Sin acceso al clúster | Evidencia congelada 2026-11-06: 352 / 895.596.949 B / 13-13 SHA |
| Kafka vivo | Sin broker | Offsets `0:1068..0:1419`, lag 0, 1420 mensajes (congelado) |
| Config del topic (`min.insync.replicas`, `cleanup.policy`, `retention.ms`) | Requiere `kafka-configs.sh` | **PENDIENTE** |
| Re-ejecución de extracción | Sin red de clase | Verificado por código + artefactos |
| `run_all.py --check`, `verificar_fase_datos.py` | Escriben/validan sobre `data/` | **No ejecutados** para respetar «nada se modifica» |
| Suite completa | `pytest` escribe en `vivienda_euskadi_test` | No ejecutada; solo `--collect-only` (145) |

---

## 8. Backlog ordenado por puntos recuperados

| Orden | Acción | Puntos | Coste |
|---|---|---|---|
| 1 | Decidir el waiver de HDFS (frase de 1 línea + doc) | **+3** en BDA | 5 min |
| 2 | ✅ Cambiar el ejemplo de array a `exterior` o mapear `ascensor` | Evita −3 en Tema 8 | 10 min |
| 3 | ✅ Barrido 351→352, 136→145, 16→14 | Evita contradicción audible | 20 min |
| 4 | Frase de encuadre de las 2 ramas (Kafka≠Mongo) | Protege #4 | 5 min |
| 5 | Re-ejecutar `run_analisis_mongo.py` delante y guardar salida | Consolida #16/#19 | 5 min |
| 6 | Declarar cobertura 80/252 en precio y 83 municipios con anuncios | Protege #18 | 5 min |
| 7 | Derivar `codigo_ine` en `ecvi_compraventa` o excluirla del recuento | Coherencia #5 | 30 min |
| 8 | ✅ Test que exija `>0` filas en las 5 consultas | Evita regresiones | 20 min |
| 9 | Whitelist `.FROZEN`/`.gitkeep` en `verify` de manifest | Cosmético | 10 min |

---

## 9. Veredicto

- **Fidelidad de la rúbrica:** 26/26 criterios transcritos **literalmente**. Cero suavizados.
- **SBD:** 19/19 criterios alcanzan la columna del 10 por su texto. **17 con evidencia medida hoy**, 2 con evidencia de artefacto (#16, #19) todavía no re-ejecutados. Nota SBD estimada **10,0**, con la advertencia de que tres 10 son «condicionales a ejecución en directo».
- **BDA:** 10/10/10/**7** en lectura literal → **9,25**; **10,0** si se acepta el waiver de HDFS. Los 3 puntos que separan 9,25 de 10,0 son exactamente el waiver.
- **Tema 8:** **9,6** sobre el 90 % evaluable (falta defensa técnica).
- **Integridad:** no se modificó nada. `data/raw` 356 ficheros, manifest 354, Mongo 759/252 antes y después, `git status` idéntico.

**El proyecto no tiene problemas de corrección de datos: le queda un waiver que verbalizar (HDFS) y un `run` global que uniría los 5 entrypoints.** Los tres hallazgos de cifras y la consulta de array ya están corregidos.
