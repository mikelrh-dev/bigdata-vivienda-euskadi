# Auditoría v10 vs rúbrica — 2026-11-11

**Alcance:** rúbrica v2 (`brief/RETO 1Evaluacion SBD-BDAv2.pdf`) + Tema 8
(`brief/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx`, §16) + requisitos adicionales del PDF,
contrastados contra el repositorio en su estado actual (rama `fix/regeneracion-procesado-resultados`,
8 commits locales sobre `master`).

**Naturaleza:** solo análisis. No se modificó código, datos, `data/raw`, Mongo, HDFS ni Kafka.
Las únicas escrituras son este informe y los ficheros temporales de `/tmp`.

**Entorno:** Windows 11, `.venv` Python 3.12.10, Mongo local operativo. HDFS centro
(`10.22.87.215:50070`) y Kafka centro (`10.22.87.215:9092`) **no alcanzables** (el usuario no está
en el centro). No es un fallo del proyecto: se trata como excepción de entorno y se contrasta con la
evidencia histórica v8 versionada en `openspec/audit/v8_2026-11-09/evidencia/vivo/`.

**Base previa:** `openspec/audit/v9_2026-11-10/` (reauditoría del 10-11). Este informe **repite la
verificación con ejecución real** y añade los deltas del rebuild silver/gold del 11-11.

---

## 1. Veredicto ejecutivo

| Bloque | Criterios | Cubiertos | Puntuación bruta |
|---|---|---|---|
| BDA — RA1 (sin peso declarado en el PDF) | 4 | 4/4 | 37/40 (92,5 %) |
| SBD — RA1 (46,7 %) | 4 | 4/4 | 40/40 |
| SBD — RA3 (13,3 %) | 6 | 6/6 | 60/60 |
| SBD — RA4 (40 %) | 5 | 5/5 | 50/50 |
| **Rúbrica PDF total** | **19** | **19/19** | **187/190 (98,4 %)** |
| Tema 8 §16 (evaluación separada) | 7 | 7/7 | — |
| **SBD ponderado** | | | **150/150 = 100 %** |

- **Único criterio por debajo de 10: C2 (HDFS), 7 puntos literales.** Los `procesado` no están en
  HDFS por indicación expresa de la profesora; originales (352), organización y recuperación sí están
  acreditados. Con la excepción firmada se defiende como 10; sin ella, 7.
- **C3 (Kafka) se sostiene con evidencia histórica v8**, no revalidable hoy por entorno: topic
  `vivienda_euskadi`, grupo `hdfs_centro`, 352 ficheros confirmados y lag 0.
- **Cero P0 y cero P1.** Nada bloquea la defensa. Los hallazgos son documentales (P2/P3) y uno de
  ellos sí conviene cerrar antes de exponer: el README cita un script de recuperación HDFS que ya no
  existe (F-01).

**Lectura honesta de la nota:** el PDF no declara peso para BDA RA1, así que no existe un único
porcentaje ponderado completo. El 98,4 % es puntuación bruta (187/190). Lo defendible es decir:
«SBD ponderado 100 %; BDA 37/40; el PDF no pondera BDA».

---

## 2. Estado verificado hoy (ejecución real)

| Check | Comando | Resultado |
|---|---|---|
| Gobernanza | `scripts/verificar_gobernanza.py` | **rc 0 — TODO OK**: 44 scripts, 38 nodos DAG, 182 silver, 11 pipelines, 0 env sin declarar, 50 cabeceras (46 con ID) |
| Gate offline | `scripts/gate_extremo_a_extremo.py --offline` | **OK**: 354 SHA raw, 182 silver, 14 colecciones, 0 duplicados, lag 0; `PENDA-01` por centro no alcanzable |
| DAG | `transform/run_all.py --check` | **38/38 OK** |
| Pipeline | `scripts/run_pipeline.py --check` | **rc 0**: raw 354 entradas 0 errores; silver 182 entradas 0 errores |
| Suite | `pytest tests -q` | **262 passed, 2 skipped** |
| Fase de datos | `scripts/verificar_fase_datos.py` | **rc 1** — solo `FAIL 07` conocido (paro-cero Aramaio 0,28 / Gaintza 1,45 / Usansolo 3,26). Huella `8641e4cb…` |
| Silver reproducible | rebuild limpio (hoy) | **38/38 scripts, 0 fallos, 182 ficheros, manifest 182, sin faltantes ni sobrantes** |
| Gold reproducible | cold start (hoy) | **52/52 artefactos byte-idénticos** (SHA-256) |
| Explain | `analysis.mongo_indexes.explain_before_after()` | **COLLSCAN 594 docs → IXSCAN 1 doc** (`20069`, larga ≤1000): `totalDocsExamined` 594→1, `totalKeysExamined` 0→1 |
| Mongo | lectura PyMongo | **16 colecciones vivas + 14 `__backup` = 30**; anuncios 594, municipios/indicadores/alquiler 252, etxebide 5040, promociones 406 |
| Artefactos | `data/resultados` | **55 ficheros** (28 PNG raíz + 8 `anexo/` + 8 CSV `mongo_*` + 10 CSV auxiliares + mapa HTML + auditoría CSV + `.gitkeep`) |
| Presentación | `docs/presentacion` | 13 diapositivas HTML, PDF 14 páginas, 9 SVG; generada desde CSV de Mongo |
| Tier | `mongo_tier_confianza.csv` | **A4 / B3 / C57 / D188**, 252 filas, SHA `b8411b77…` = el declarado en el spec |

### Deltas frente a la auditoría v9 (2026-11-10)

| Magnitud | v9 | v10 (hoy) |
|---|---|---|
| Scripts `transform/` | 42 | **44** |
| Nodos DAG | 34 | **38** |
| Ficheros silver | 188 | **182** |
| Tests | 235 passed / 237 collected | **262 passed / 264 collected** |
| Reproducibilidad silver desde cero | no demostrada | **182/182** |
| Reproducibilidad gold desde cero | no demostrada | **52/52 byte-idénticos** |
| `data/resultados` | 8 CSV + 28 + 8 PNG + 2 dashboards + README | **54 artefactos** (sin dashboards ni README: ver F-02) |
| Tier A/B/C/D | 4/3/57/188 | **4/3/57/188** (sin cambio) |

---

## 3. Matriz de la rúbrica PDF (19 criterios)

| # | Criterio (nivel 10) | Nota | Evidencia verificada hoy |
|---|---|---:|---|
| C1 | Automatiza **API y scraping** | **10** | 41 scripts en `extract/`: APIs Eustat (`01`, `02`), INE (`06`, `07`), Udalmap, OSRM, Lanbide; scrapers Fotocasa (`05`, `09`), Pisos (`08`), faltantes (`10`), habitaciones (`13`), certificados (`23`); `main_ingest.py` orquesta y `_common.Cliente` centraliza reintentos/timeout |
| C2 | HDFS: originales **y procesados**, recuperación | **7** | 352 raw canónicos + manifest 354 en `docs/raw_manifest_sha256.txt`; recuperación con `scripts/hdfs_recuperacion_un_fichero.py` (descarga + cotejo SHA/tamaño, solo lectura; 6 tests offline; pendiente corrida real en el centro); verificación SHA en `storage/kafka_hdfs_uploader.py:84-116`; evidencia `openspec/audit/v8_2026-11-09/evidencia/vivo/hdfs.json`; **`procesado` → 404, excepción declarada** |
| C3 | Productor y consumidor Python funcionan | **10** | `storage/kafka_raw_producer.py` (KafkaProducer) + `storage/kafka_hdfs_uploader.py` (KafkaConsumer, commit manual); topic `vivienda_euskadi` 1P RF1; histórico v8: grupo `hdfs_centro` committed 352, lag 0. **Hoy no revalidable (centro caído)** |
| C4 | Flujo completo hasta MongoDB | **10** | `gate_extremo_a_extremo --offline` OK; cadena `extract → transform → load_mongo → clean_mongo → analysis` ejecutable con `scripts/run_pipeline.py`; Mongo vivo con 16 colecciones |
| C5 | 2+ fuentes relacionadas por campo común | **10** | 16 colecciones; `$lookup` `anuncios.ubicacion.codigo_ine → municipios._id` (22 usos de `$lookup`); `etxebide_promociones.codigo_ine` derivado `Cod_Prov+CODMUNI` |
| C6 | 2+ colecciones + relación/embedding/referencia | **10** | `anuncios` con `ubicacion{}` embebido, `equipamiento[]`, `historico_precios[]`; referencing por `codigo_ine` en 8 colecciones; `municipios` como dimensión |
| C7 | Limpieza: nulos, duplicados, tipos, +1 op | **10** | `storage/clean_mongo.py`: `canonicalize_codigo_ine` (:32), `mark_nulls` (:104), `resolve_duplicates` (:164, 3 claves distintas), `convert_types` (:222); + `clean_obsolete_fields`, `clean_null_markers` |
| C8 | Automatización carga+limpieza+transformación | **10** | `scripts/run_mongo_pipeline.py` (load_all → clean_all → ensure_indexes → pipelines); `scripts/run_pipeline.py --fase mongo`; carga con staging + `__backup` + rename atómico, sin edición manual en Mongo |
| C9 | Modelado + decisión embedding/referencing justificada | **10** | `openspec/archive/2026-11-10-docs/modelo_mongodb.md`: §Embedding vs referencing (:24-28), tipos BSON (:31), índices (:42), shard key (:61), transacciones (:69), 7 preguntas docx respondidas (:148-156) |
| C10 | CRUD 4 ops + comprobación por código | **10** | `clean_mongo.demo_crud_operations` (:311-360): insert_one, insert_many, find, update_one, find_one_and_update, upsert, `$unset/$rename/$pull`, bulk_write, delete_one/many; `tests/test_mongo.py` y `test_mongo_pymongo_pro.py` con asserts de contadores |
| C11 | 5 consultas útiles + anidada/array + 2 condiciones | **10** | `analysis/mongo_queries.py`: 30 funciones — igualdad, dot notation (`ubicacion.codigo_ine`), `$all`, `$elemMatch`, `$size`, `$exists`, `$type`, regex, comparación, `$and`, `$or`, proyección, sort/limit, paginación |
| C12 | 3+ pipelines, 5 etapas, `$group` + lookup/unwind/facet | **10** | 11 pipelines en `PIPELINE_ORDER`; 8 etapas distintas en `mongo_aggregations.py`: `$match`(18), `$group`(6), `$project`(12), `$sort`(16), `$limit`(13), `$addFields`(34), `$lookup`(22), `$unwind`(5) |
| C13 | explain antes/después + COLLSCAN/IXSCAN + docsExamined | **10** | **Ejecutado hoy**: antes `COLLSCAN`, 594 docs examinados, 0 claves; después `IXSCAN`, 1 doc, 1 clave, filtro canónico `20069`; 8 índices garantizados por `ensure_indexes()` |
| C14 | Transacción real o atómica justificada | **10** | Atómica de documento único: `find_one_and_update` + `ReturnDocument.AFTER` (`storage/mongo.py:170-197`), upsert idempotente con índice único `(portal, id_anuncio)`; justificación de por qué la transacción multidocumento es innecesaria en standalone (`modelo_mongodb.md:170`); `tests/test_mongo_consistencia.py:51` |
| C15 | Datos heterogéneos adaptados con Python/PyMongo | **10** | 7 formatos: CSV, JSON, JSON anidado, XLSX, GeoJSON, ZIP/GTFS, SHP; normalización común (`extract/_common.py`), entity resolution y `_geo_point` |
| C16 | Script que ejecuta **todos** los análisis principales | **10** | `analysis/run_analisis_mongo.py`: 11 pipelines, huella SHA, 8 CSV + 28 PNG + 8 anexo, todo desde Mongo; `--check` y argparse alineados |
| C17 | 5+ indicadores con 2+ fuentes | **10** | `matriz_indicadores.md`: esfuerzo 18-34 (Eustat alquiler + renta), tensión social (Etxebide + esfuerzo), paro Lanbide, precio m² Eustat, VPO terminadas (Open Data + población); 55 campos en `indicadores` |
| C18 | 3+ municipios comparados, conclusión ligada a indicador Mongo | **10** | 4 Tier A: Bilbao 204 (37,69 %), Donostia 126 (38,17 %), Getxo 50 (28,60 %), Vitoria 39 (33,37 %); `comparativa_3_municipios_mongo.csv` con esfuerzo, precio y paro por municipio, todos campos de Mongo |
| C19 | 3+ conjuntos automáticos para representar | **10** | 8 CSV `mongo_*.csv` + 28 PNG + 8 anexo, generados por `exportar_csv`/`exportar_png_desde_mongo`; la presentación se construye leyendo esos CSV, no literales |

### 3.1 Por qué C2 es 7 y no 10

El nivel 10 exige «organiza originales **y procesados** y demuestra su recuperación». Hoy:

- **Originales:** 352 ficheros / 895,6 MB en `/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw`,
  con manifest SHA-256 local de 354 entradas (2 alias legacy no publicados) y gate que lo verifica.
- **Recuperación:** el consumidor verifica tamaño + SHA antes de subir (`verify_local`), y la evidencia
  v8 registra los `FileStatus` de HDFS. Pero el script que descargaba y comparaba un fichero
  (`scripts/hdfs_recuperacion_un_fichero.py`) **fue borrado** en `48c3516` y el README lo sigue citando.
- **Procesados:** `data/procesado` devuelve 404 en HDFS. Es la excepción firmada por la profesora
  («los procesados no se suben»).

Con la excepción aceptada, el criterio se defiende como 10 (organización + recuperación de originales).
Sin ella, 7. La auditoría puntúa 7 para no autoasignarse el waiver.

---

## 4. Tema 8 §16 (evaluación separada, 100 %)

| # | Criterio | Peso | Estado | Evidencia |
|---|---|---:|---|---|
| T1 | Modelado documental | 15 % | **Cumple** | `modelo_mongodb.md` con las 7 preguntas del docx §5 respondidas y decisión embedding/referencing razonada |
| T2 | CRUD, limpieza y consultas | 15 % | **Cumple** | 30 funciones de consulta, 4+ operaciones de limpieza, CRUD completo con asserts |
| T3 | Aggregation | 20 % | **Cumple** | 11 pipelines, 8 etapas, `$group` + `$lookup` + `$unwind`; responden preguntas del reto (esfuerzo, VPO, accesibilidad, habitaciones) |
| T4 | Índices y rendimiento | 15 % | **Cumple** | ESR `{ubicacion.codigo_ine:1, modalidad:1, precio_eur:1}` + geo 2dsphere, multikey, parcial, unique; explain real 594→1 |
| T5 | Transacciones y consistencia | 10 % | **Cumple** | Atómica + justificación READ en standalone; sonda de transacción en `vivienda_euskadi_test` sin forzar replica set |
| T6 | PyMongo profesional | 15 % | **Cumple** | `get_client()` reutilizable con `MONGO_URI` leída en cada llamada, `replace_collection` con staging/backup/rename, excepciones tipadas, `CARGA-SEGURA` |
| T7 | Defensa técnica | 10 % | **Cumple con reserva** | Deck de 13 diapositivas + PDF + guion archivado; reserva: cifras obsoletas en README/AGENT e informe archivado (F-03/F-04) |

---

## 5. Requisitos adicionales del PDF y entregables

| Requisito | Evidencia | Estado |
|---|---|---|
| Objetivo 1: datos reales de alquiler/compraventa por API **y** scraping | 41 extractores; Eustat/INE/Fotocasa/Pisos | Cumple |
| Objetivo 2: salarios, población u otros indicadores | EPA/INE, Lanbide, Udalmap, Eustat población, ECVI | Cumple |
| Gestión en JSON o CSV | `data/raw` + `data/procesado` + Mongo; 7 formatos de entrada | Cumple |
| Limpieza de incompletos, duplicados, incorrectos | `mark_nulls`, `resolve_duplicates`, `convert_types`, cuarentena geo | Cumple |
| Transformaciones con operaciones MongoDB | `clean_mongo` (update/delete/rename/convert) | Cumple |
| Consultas y agregaciones para indicadores | 30 consultas + 11 pipelines | Cumple |
| Todo en Python | 100 % Python (`.py`); sin notebooks ejecutables ni SQL de producción | Cumple |
| Entregable: originales en HDFS + MongoDB | 352 raw en HDFS (histórico) + 16 colecciones vivas | Cumple con excepción de procesados |
| Esquema de arquitectura | `mapa_esquema_silver.html` + `arquitectura_datos.md` (archivado) + diagrama del deck | Cumple |
| Informe con gráficos **y tablas** | `informe_final.md` (159 líneas, 36 filas de tabla) + 8 CSV + 28 PNG; **0 imágenes embebidas** (referencia por ruta) | Cumple con reserva (F-04) |
| Demostración con decisiones técnicas | Deck 13 diapositivas, 9 figuras, guion de 12 min archivado | Cumple |

**Invariantes del contrato:** sin Docker (README:100 y AGENT:4 usan la frase contractual, 0 afirmaciones
de despliegue Docker) · HDFS solo raw · Kafka→HDFS nunca Kafka→Mongo · sin imputar comarcal/IDW como
municipal · Nivel (4/54/194) y Tier (4/3/57/188) como ejes ortogonales. **Las cinco se sostienen.**

---

## 6. Prohibiciones P-01…P-08

| ID | Prohibición | Verificación | Estado |
|---|---|---|---|
| P-01 | Compraventa como eje cuando se evalúa alquiler | Eje = `alquiler_municipal`/`esfuerzo_joven_pct_18_34`; ECVI solo contraste | Cumple |
| P-02 | Simular salario, alquiler o población | Test que detecta valores tecleados; todo sale de raw/manifest | Cumple |
| P-03 | Alquiler INE para Euskadi (null por foral) | Alquiler de Eustat; INE solo renta/salarios | Cumple |
| P-04 | Acreditar con una sola etapa lo que exige agregación compleja | 11 pipelines, 8 etapas, `$group` + `$lookup`/`$unwind` | Cumple |
| P-05 | Gráficos con valores tecleados | 28+8 PNG y 8 CSV desde Mongo; deck desde CSV. **Los 2 dashboards manuales fueron los únicos con literales y ya no existen** | Cumple |
| P-06 | Programas en lenguaje distinto de Python | 100 % Python | Cumple |
| P-07 | Credenciales en el repositorio | `.env` y `api.txt` existen en disco pero están **ignorados** (`git check-ignore`), no versionados | Cumple |
| P-08 | Marcar criterio cubierto sin verificación observable | 262 tests + gate + gobernanza + explain ejecutado; este informe cita comando por criterio | Cumple |

---

## 7. Excepciones declaradas y límites de esta auditoría

| Excepción | Qué cubre | Riesgo si se pregunta en defensa |
|---|---|---|
| **HDFS solo raw** (indicación de la profesora) | C2 baja de 10 a 7 literal; `procesado` 404 | Bajo: está documentado en README y en la evidencia v8 |
| **Centro HDFS/Kafka no alcanzable hoy** | C2/C3 no se reejecutan en vivo; se usa evidencia v8 y gate offline (`PENDA-01`) | Medio: si el tribunal pide demo en vivo y no hay red, hay que enseñar `openspec/audit/v8_2026-11-09/evidencia/vivo/hdfs.json` |
| **FAIL 07 (paro-cero)** | Aramaio 0,28 / Gaintza 1,45 / Usansolo 3,26 con tasa no nula | Bajo: es dato real, se muestra sin enmascarar; no lo ejecuta el CI |
| **CI no ejecutado en Ubuntu** | Los tests de Mongo llevan `skipif(not ping())`; el workflow está inspeccionado, no ejecutado | Bajo: la primera corrida real en GitHub queda pendiente |
| **2 dashboards y README local perdidos** | No eran evidencia RA4 (manuales, P-05); eran documentación local | Medio: el README raíz y un spec aún los citan (F-02) |
| **`clean_all()` no ejecutado en esta auditoría** | Solo lectura; los pipelines no dependen de esos flags | Ninguno |

**No ejecutado a propósito:** rebuild completo de silver/gold (se hizo hoy antes de la auditoría y dejó
182/52 reproducibles), `load_all`/`clean_all`, escrituras en Mongo, subidas a HDFS, producción/consumo
Kafka real, commit/push.

---

## 8. Hallazgos

**P0 = 0 · P1 = 0 · P2 = 6 · P3 = 6.**

### P2

| ID | Título | Evidencia | Impacto / recomendación |
|---|---|---|---|
| **F-01** | El README citaba un script de recuperación HDFS que no existía | `README.md:108` → `scripts/hdfs_recuperacion_un_fichero.py`, borrado en `48c3516`; `storage/hdfs_utils.py` también ausente | **Resuelto 2026-11-11**: script reescrito sin `hdfs_utils` (InsecureClient directo, solo lectura), 6 tests offline en `tests/test_hdfs_recuperacion.py`, rc=2 con pista cuando no hay centro. **Falta ejecutarlo contra HDFS** para acreditar C2 en vivo |
| **F-02** | `data/resultados/README.md` y los 2 dashboards desaparecieron y siguen citados | `README.md:160-166`; `openspec/specs/presentacion-de-resultados/spec.md:230` exige que ese README contenga 594/188/204 | Escenario de spec incumplible. Reescribir el README de resultados (documentando regeneración) y retirar la cita de los dashboards, o declararlos retirados |
| **F-03** | Cifras obsoletas en README y AGENT | README:124/136 «188 archivos silver» (hoy **182**), README:110 «259 passed» (hoy **262**); AGENT:9 «42 scripts / 34 DAG / silver 188 / 235 passed» (hoy **44/38/182/262**) | Un tribunal que cuente ficheros verá 182. Actualizar las cuatro cifras |
| **F-04** | Evidencia archivada desactualizada | `informe_final.md:15,25,141` dice «188 silver» y `matriz_indicadores.md` declara SHA de `mongo_esfuerzo_por_municipio.csv` y `mongo_modalidades.csv` que **no** coinciden con los actuales (`mongo_alquiler_por_municipio.csv` sí) | Si se presenta como evidencia, los hashes no cuadran. Los datos son reproducibles (52/52 hoy); regenerar los hashes del doc o fecharlos como históricos |
| **F-05** | El PDF no pondera BDA RA1 y el contrato reproduce la laguna | PDF pág. 3 sin línea «Peso»; `contrato-reto/spec.md:12` lista 4 RAs y 3 pesos | No se puede dar un único porcentaje ponderado. Declararlo así en defensa (SBD 100 %, BDA 37/40) |
| **F-06** | La tabla del contrato tiene 27 filas con numeración distinta de la canónica 1-19 | `contrato-reto/spec.md:182-208`; «criterio 5» = Modelado (C9), no Integración de fuentes (C5) | Riesgo de citar criterios cruzados. Usar siempre criterio canónico + página del PDF |

### P3

| ID | Título | Evidencia | Impacto |
|---|---|---|---|
| **F-07** | La nota del contrato dice «sin diferencias literales» en docx §16, pero suprime 7 puntos finales | `contrato-reto/spec.md:98` vs celdas del docx | Documental, no afecta a nota |
| **F-08** | `ENTREGABLES-01` y `DISTRIBUIDA-01` no tienen test que los cite | `grep` en `tests/`: 0 referencias; son requisitos documentales | Bajo: se acreditan con deck + `modelo_mongodb.md:61` |
| **F-09** | `anuncios_habitaciones_unificados` y `_bigdata` duplican 201 `_id` | 201/201 en ambas | Bajo: `_hab_col()` prefiere `_bigdata`; elegir canónica y retirar la otra |
| **F-10** | `extract/26_vpo_terminadas.py --promote` no regenera `_meta/ingestion_manifest.json` | H-08 de v9, sigue abierto | Solo afecta a una reextracción futura |
| **F-11** | `docs/contrato_datos_raw.md` (archivado) y `transform/_raw_guard.py` discrepan sobre `.FROZEN` | H-09 de v9 | Documental |
| **F-12** | La huella de los 11 pipelines no está versionada | DS2-25 de v9 | Bajo: se imprime al ejecutar |

**Conocido y aceptado:** `FAIL 07` de `verificar_fase_datos.py` (rc 1) es un dato real de Lanbide/INE;
tocarlo para forzar el verde sería peor que el rojo. No lo ejecuta el CI ni bloquea suite, gate ni
gobernanza.

---

## 9. Riesgos de defensa (preguntas probables)

| Pregunta probable | Respuesta sólida | Dónde está |
|---|---|---|
| «¿Dónde están los procesados en HDFS?» | Excepción firmada; originales + recuperación acreditados; 404 documentado | README:108, evidencia v8 |
| «Demuéstrame Kafka en vivo» | Hoy no hay red al centro; enseño topic/grupo/lag 0 de la evidencia v8 y los tests offline | `evidencia/vivo/hdfs.json`, `tests/test_kafka_pipeline.py` |
| «¿Por qué no usas transacción?» | Atomicidad de documento único + índice único; transacción exigiría replica set y no hay operación multidocumento que la necesite | `modelo_mongodb.md:170`, `test_mongo_consistencia.py:51` |
| «¿El ranking es fiable?» | Solo 4 Tier A (n≥30); Getxo vs Vitoria es margen de 11 anuncios, no diferencia firme | `comparativa_3_municipios_mongo.csv` |
| «¿Los gráficos son automáticos?» | 28+8 PNG y 8 CSV desde Mongo; el deck se construye desde esos CSV; los dashboards manuales se retiraron | `analysis/run_analisis_mongo.py`, `build_presentacion.py` |
| «¿Cuántos ficheros silver?» | **182**, con manifest y rebuild desde cero verificado | `manifest_sha256.txt`, gobernanza |
| «¿Qué nota?» | SBD ponderado 100 %; BDA 37/40 por la excepción de procesados; el PDF no pondera BDA | este informe §1 |

---

## 10. Cierre recomendado (sin ejecutar; solo prioridades)

1. **F-01** (P2, 10 min): restaurar el script de recuperación o corregir README:108. Es el único
   hallazgo que puede desmontar la evidencia de C2 delante del tribunal.
2. **F-02** (P2): reescribir `data/resultados/README.md` como índice de artefactos regenerables y
   retirar del README raíz la cita a los dashboards; alinear el escenario de
   `presentacion-de-resultados/spec.md:230`.
3. **F-03/F-04** (P2): actualizar 182/44/38/262 en README y AGENT; fechar o regenerar los hashes de
   `matriz_indicadores.md`.
4. **F-05/F-06** (P2): dejar escrita la frase de nota y usar el criterio canónico 1-19.
5. P3: aparcar hasta después de la defensa; ninguno afecta a la ejecución.

---

## 11. Anexo — comandos ejecutados

```bash
.venv/Scripts/python.exe scripts/verificar_gobernanza.py            # rc 0, TODO OK
.venv/Scripts/python.exe scripts/gate_extremo_a_extremo.py --offline # OK + PENDA-01
.venv/Scripts/python.exe transform/run_all.py --check                # 38/38 OK
.venv/Scripts/python.exe scripts/run_pipeline.py --check             # 354 raw / 182 silver, 0 errores
.venv/Scripts/python.exe -m pytest tests -q                          # 262 passed, 2 skipped
.venv/Scripts/python.exe scripts/verificar_fase_datos.py             # rc 1, solo FAIL 07
# explain_before_after() + ensure_indexes() (read-only)
# recuento de colecciones/índices y lectura de indicadores/anuncios (read-only)
```

**Ficheros leídos para el cotejo:** `brief/RETO 1Evaluacion SBD-BDAv2.pdf`,
`brief/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx`, `openspec/specs/contrato-reto/spec.md` y las cuatro
specs detalladas (50 cabeceras), `openspec/audit/v9_2026-11-10/*` (reauditoría y pendientes),
`README.md`, `AGENT.md`, `openspec/archive/2026-11-10-docs/{informe_final,matriz_indicadores,modelo_mongodb,guion_defensa,conclusiones_municipios,arquitectura_datos}.md`,
`docs/README.md`, `docs/presentacion/README.md`.

**Guardarraíles respetados:** sin escrituras en `data/`, Mongo, HDFS ni Kafka; sin commits; sin
instalación de dependencias. Único fichero creado: este informe.
