# Desviaciones rúbrica vs contrato — auditoría v9 (W1.3)

**Fecha:** 2026-11-10 · **Unidad:** W1.3 · **Naturaleza:** solo lectura · **Autor del artefacto:** subagente v9
**Entrada:** `brief/RETO 1Evaluacion SBD-BDAv2.pdf`, `brief/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx`, `openspec/specs/contrato-reto/spec.md`, `rubrica_reextraida.md` (R1), `mapa_requisitos.md` (R1), `matriz_rubrica_v8.md`, `informe_extract.md` (R1)
**Guardrails respetados:** no se modificó código, datos, Mongo, HDFS ni Kafka; no se instalaron dependencias; no hubo commit/push. Única escritura en el repo: este informe. Los scripts de sonda y las extracciones viven en el scratch de Hermes.

---

## 1. Resumen ejecutivo

- **PDF → contrato: 95/95 celdas literales.** Las 19 celdas de la columna de 10 puntos aparecen en negrita en el contrato (`**…**`); el contenido es idéntico. No hay diferencias de redacción.
- **docx §16 → contrato: 14 exactas + 7 con el punto final eliminado.** El contrato suprime el `.` final de las 7 celdas «Qué se valora». Su propia nota de trazabilidad dice «Sin diferencias literales» (`spec.md:98`), lo cual es **falso** en lo formal.
- **Pesos:** el PDF declara 3 pesos (SBD RA1 46,7 % · RA3 13,3 % · RA4 40 %) y **ninguno para BDA RA1**; el docx §16 declara 7 pesos (15/15/20/15/10/15/10, suma 100). El contrato (`spec.md:12`) enumera **4 RAs y 3 pesos**: reproduce la laguna del PDF.
- **Numeración:** la tabla «Mapeo criterio → requisito» del contrato (`spec.md:182-208`) tiene **27 filas** con numeración distinta de la canónica 1-19. 20 filas cubren los 19 criterios v2; 7 no son criterios v2 (4 RA4 v1 superados + 3 requisitos/objetivos del PDF).
- **Trazabilidad:** los 19 criterios y los 7 de Tema 8 tienen requisito y evidencia con `fichero:línea` (§6). 0 huérfanos.
- **Hallazgos: P0 = 0 · P1 = 0 · P2 = 2 · P3 = 4.** Ningún P0/P1: no se detuvo la auditoría.

---

## 2. Cotejo literal PDF → contrato

Instrumento: extracción del PDF con `read_file` (auto-extracción, **123 líneas**), verificada además con `pdftotext -layout` (178 líneas) y `pypdf` por página (290 líneas). Comparación programática normalizando mayúsculas, espacios y guiones (`compare_w13b.py`, scratch).

| Sección | Contrato | PDF (read_file) | Celdas | Resultado |
|---|---|---|---|---|
| BDA RA1 | `spec.md:33-38` | 74-79 | 20 | 20/20 OK |
| SBD RA1 | `spec.md:46-51` | 89-94 | 20 | 20/20 OK |
| SBD RA3 | `spec.md:59-66` | 102-109 | 30 | 30/30 OK |
| SBD RA4 | `spec.md:74-80` | 117-123 | 25 | 25/25 OK |
| **Total** | | | **95** | **95/95 OK** |

**Única diferencia formal:** el contrato envuelve en `**…**` las 19 celdas de la columna de 10 puntos (`spec.md:35-38, 48-51, 61-66, 76-80`); el PDF no usa negrita. No es una diferencia de contenido. Las notas de trazabilidad del PDF (`spec.md:40, 53, 68, 82`) que dicen «Sin diferencias literales» son **correctas**.

**Requisitos adicionales del PDF** (`spec.md:110-125`, 10 fragmentos): 10/10 literalmente presentes en el PDF (objetivos 1-2, requisitos BDA/SBD, entregable, resultado final).

---

## 3. Cotejo literal docx §16 → contrato

Instrumento: `python-docx` (tabla `Criterio | Peso | Qué se valora`, docx líneas 190-200 en extracción `python-docx`; 228-252 en extracción `read_file`). Comparación exacta celda a celda (`compare_w13b.py`).

| Criterio (Tema 8) | Peso | «Qué se valora» |
|---|---|---|
| Modelado documental | 15 % | contrato sin `.` final; docx con `.` |
| CRUD, limpieza y consultas | 15 % | contrato sin `.` final; docx con `.` |
| Aggregation | 20 % | contrato sin `.` final; docx con `.` |
| Índices y rendimiento | 15 % | contrato sin `.` final; docx con `.` |
| Transacciones y consistencia | 10 % | contrato sin `.` final; docx con `.` |
| PyMongo profesional | 15 % | contrato sin `.` final; docx con `.` |
| Defensa técnica | 10 % | contrato sin `.` final; docx con `.` |

**Resultado: 14/21 exactas + 7 sólo-punto-final + 0 divergencias de contenido.** Las 7 diferencias están en la columna «Qué se valora» (`spec.md:90-96`). La cabecera del contrato añade `(Tema 8)` a la primera columna (`spec.md:88`), anotación que no existe en el docx.

**Contradicción interna:** `spec.md:98` afirma «Tema 8 sección 16 literal en docx líneas 228-252. … Sin diferencias literales.» Las 7 supresiones de punto final lo desmienten.

---

## 4. Pesos

| Fuente | Pesos | Suma | BDA RA1 |
|---|---|---|---|
| **PDF** (págs. 4-6) | SBD RA1 46,7 % · RA3 13,3 % · RA4 40 % | **100,0 %** (SBD) | **no declarado** |
| **docx §16** | 15/15/20/15/10/15/10 | **100 %** | no aplica (evaluación separada) |
| **contrato** `spec.md:12` | 46,7 % / 13,3 % / 40 % | — | **laguna reproducida** (4 RAs, 3 pesos) |

- El PDF tiene 3 líneas «Peso en la 1.ª evaluación» (págs. 4, 5, 6) y **ninguna** en la sección BDA (pág. 3). Verificado con `compare_w13b.py` y lectura de la pág. 3.
- El contrato declara el peso en cada sección (`spec.md:44` 46,7 % · `spec.md:57` 13,3 % · `spec.md:72` 40 %), que es correcto; el problema es el resumen de `spec.md:12`, que enumera 4 RAs y da 3 pesos sin advertir que el primer weight listado corresponde a SBD RA1, no a BDA RA1.
- El docx §16 declara sus propios pesos y el contrato los declara como evaluación separada (`spec.md:86`): correcto, no se suman.

---

## 5. Numeración: 27 filas del contrato vs 19 canónicos

La tabla `spec.md:182-208` tiene 27 filas. Crosswalk completo (fila del contrato → criterio canónico PDF):

| Fila contrato | Etiqueta del contrato | Criterio canónico | ¿Es criterio v2? |
|---|---|---|---|
| 1 | Extracción: API y scraping | **C1** | sí |
| 2 | HDFS: originales, procesados, recuperación | **C2** | sí |
| 3 | Kafka: productor y consumidor | **C3** | sí |
| 4 | Integración: flujo completo a MongoDB | **C4** | sí |
| 5 | Modelado: justifica modelo y relaciones | **C9** | sí |
| 6 | PyMongo: inserta, actualiza, elimina, comprueba | **C10** | sí |
| 7 | Consultas: campos anidados o arrays | **C11** | sí |
| 8 | Agregación v2 | **C12** | sí |
| 9 | RA4 v1 Gráficos | — (superado) | **no** (RA4 v1) |
| 10 | RA4 v1 Datos | — (superado) | **no** (RA4 v1) |
| 11 | RA4 v1 Presentación | — (superado) | **no** (RA4 v1) |
| 12 | RA4 v1 Interpretación | — (superado) | **no** (RA4 v1) |
| 13 | Salarios / población / indicadores | — (objetivo 2 PDF) | **no** |
| 14 | Formato JSON o CSV | — (requisito BDA PDF) | **no** |
| 15 | Limpieza: incompletos, duplicados, incorrectos | **C7** | sí (como requisito PDF) |
| 16 | Transformaciones en MongoDB | **C7** | sí (como requisito PDF) |
| 17 | Resultado final: municipios y por qué | **C18** | sí (como resultado PDF) |
| 18 | Todo en Python | — (requisito PDF) | **no** |
| 19 | RA1 Integración de fuentes v2 | **C5** | sí |
| 20 | RA1 Construcción conjunto v2 | **C6** | sí |
| 21 | RA1 Automatización v2 | **C8** | sí |
| 22 | RA3 Índices v2 | **C13** | sí |
| 23 | RA3 Consistencia v2 | **C14** | sí |
| 24 | RA4 Datos heterogéneos v2 | **C15** | sí |
| 25 | RA4 Automatización del análisis v2 | **C16** | sí |
| 26 | RA4 Indicadores v2 | **C17** | sí |
| 27 | RA4 Preparación visualización v2 | **C19** | sí |

**Lectura:** 20 filas cubren los 19 criterios v2 (C7 usa dos filas, 15 y 16); 7 filas no son criterios v2. La numeración del contrato **no** es la canónica: contrato «5 Modelado» = C9, contrato «19 RA1 Integración de fuentes» = C5, contrato «9-12» no existen en la rúbrica v2. El mapa canónico 1-19 está en `rubrica_reextraida.md` y `mapa_requisitos.md` (R1).

---

## 6. Líneas de trazabilidad: criterio → requisito → evidencia

Requisitos de `mapa_requisitos.md` (R1, ejecutado). Evidencia primaria con `fichero:línea` (verificada por `grep`/`read_file` en esta sesión).

### 6.1 Rúbrica PDF (C1-C19)

| # | Criterio (nivel 10) | Requisito | Evidencia (fichero:línea) |
|---|---|---|---|
| **C1** | Extracción de datos mediante Python | `EXTRACCION-01`, `EXTRACCION-02` | `extract/_common.py:71-134` (`Cliente` con timeout/reintentos); `extract/main_ingest.py:191-230` (`_live`); APIs `extract/01_eustat_api.py:50-71`, `extract/06_ine_api.py:51-56`; scrapers `extract/05_fotocasa_scraper.py:157-205`, `extract/08_pisos_scraper.py:54-105`; `extract/26_vpo_terminadas.py:39-103` |
| **C2** | Almacenamiento HDFS | `HDFS-01`, `RAW-01` | `storage/kafka_hdfs_uploader.py:56-60` (`get_hdfs_url`/`get_hdfs_user`), `:84-90` (`verify_local` tamaño+SHA), `:92-116` (`consume`); `scripts/upload_procesado.py`; `scripts/gate_extremo_a_extremo.py:58,164,180`. HDFS raw 352 (histórico v8; v9 red caída) |
| **C3** | Kafka | `KAFKA-01`, `RAW-01` | `storage/kafka_raw_producer.py:49-65` (`produce`, `KafkaProducer`); `storage/kafka_topic.py:45` (`ensure_topic`); `storage/kafka_hdfs_uploader.py:92-116` (`KafkaConsumer`, commit) |
| **C4** | Integración | `INTEGRACION-01` | `scripts/gate_extremo_a_extremo.py:164` (`run_offline`), `:180` (`run_vivo`); `storage/load_mongo.py:99,234` (`load_municipios`, `load_anuncios`); `analysis/run_analisis_mongo.py:49-62` (`PIPELINE_ORDER`) |
| **C5** | Integración de fuentes | `INTEGRACION-01`, `MODELO-01` | `storage/load_mongo.py:231,297` (`replace_collection` municipios/anuncios); `analysis/mongo_aggregations.py:295` (`$lookup` anuncios→municipios por `codigo_ine`); `transform/dim_municipios.py`, `transform/unificar_anuncios.py` |
| **C6** | Construcción del conjunto de datos | `MODELO-01` | `docs/modelo_mongodb.md:6` (Colecciones), `:24` (Embedding vs referencing); `storage/load_mongo.py:99-472` (14 colecciones) |
| **C7** | Limpieza y transformación con PyMongo | `LIMPIEZA-01`, `TRANSFORM-01` | `storage/clean_mongo.py:32` (`canonicalize_codigo_ine`), `:104` (`mark_nulls`), `:164` (`resolve_duplicates`), `:222` (`convert_types`); `storage/mongo.py:152` (`replace_collection`) |
| **C8** | Automatización | `INTEGRACION-01`, `LIMPIEZA-01`, `TRANSFORM-01`, `CARGA-SEGURA-01` | `transform/run_all.py:52` (`SCRIPTS`), `:286` (`_orden_topologico`), `:433` (`main`); `scripts/run_mongo_pipeline.py`; `storage/load_mongo.py:235-236` (staging + `__backup` + rename) |
| **C9** | Modelado MongoDB | `MODELO-01` | `docs/modelo_mongodb.md:24` (Embedding vs referencing), `:144-152` (§5 preguntas docx con respuesta); `storage/mongo.py:170-197` (`marcar_calidad_municipio`, `find_one_and_update` + `ReturnDocument.AFTER`) |
| **C10** | CRUD con PyMongo | `PYMONGO-01` | `storage/mongo.py:152-168` (`insert_many`), `storage/clean_mongo.py:104-160` (`update_many`), `:164-216` (`delete_many`), `storage/mongo.py:197` (`find_one_and_update`); `tests/test_mongo.py` (asserts `inserted_id`/`matched_count`/`deleted_count`) |
| **C11** | Consultas | `CONSULTAS-01` | `analysis/mongo_queries.py:31` (igualdad), `:81` (dot notation), `:104` (`$all`), `:110` (`$elemMatch`), `:118` (`$size`), `:124` (`$exists`), `:130` (`$type`), `:136` (regex), `:144` (comparación), `:159` (`$and`), `:165` (`$or`), `:171` (proyección), `:178` (sort/limit), `:186` (paginación) |
| **C12** | Aggregation Pipeline | `AGREGACION-01` | `analysis/mongo_aggregations.py:23` (`pipeline_indicadores_municipio`), `:285` (alquiler), `:313` (modalidades), `:322` (top esfuerzo), `:395` (esfuerzo sexo), `:422` (accesibilidad), `:472` (udalmap+osrm), `:488` (vpo); `analysis/run_analisis_mongo.py:49-62` (11 pipelines) |
| **C13** | Índices y rendimiento | `INDICES-01` | `analysis/mongo_indexes.py:62` (`ensure_indexes`), `:107` (`explain_before_after`), `:135` (`explain_promo_before_after`), `:44-56` (`_explain` COLLSCAN/IXSCAN/`totalDocsExamined`) |
| **C14** | Consistencia | `TRANSACCIONES-01` | `storage/mongo.py:170-197` (atómica `find_one_and_update` + `ReturnDocument.AFTER`); `docs/modelo_mongodb.md:65` (Transacciones), `:166` (§11 READ justificado en standalone); `tests/test_mongo_consistencia.py:49` |
| **C15** | Datos heterogéneos | `DATOS-HETEROGENEOS-01` | `extract/_common.py:148-164` (`leer_csv_seguro`), `:185-214` (`guardar_json`); `extract/normalizar_metadata.py:56-109`; `extract/entity_resolution.py:42-85`; `transform/unificar_anuncios.py` (3 portales); 7 formatos (CSV, JSON, XLSX, GeoJSON, ZIP, SHP, GTFS) |
| **C16** | Automatización del análisis | `AUTOMATIZACION-ANALISIS-01` | `analysis/run_analisis_mongo.py:49-62` (`PIPELINE_ORDER`), `:131` (`run_all_estandar`), `:190` (`exportar_csv`), `:397` (`exportar_png_desde_mongo`), `:1161` (`main`) |
| **C17** | Indicadores | `INDICADORES-01` | `docs/matriz_indicadores.md:7-11` (5 indicadores con fuente+limitación); `analysis/mongo_aggregations.py:23` (`pipeline_indicadores_municipio`), `:295` (`$lookup`) |
| **C18** | Respuesta al reto | `CONCLUSION-01`, `RESPUESTA-01`, `CONCLUSION-02`, `PISOS-05`, `BOOTSTRAP-01`, `DOCS-01` | `docs/conclusiones_municipios.md:7-10` (Bilbao 204, Donostia 126, Getxo 50, Vitoria 39), `:16-19` (frase por municipio con esfuerzo/precio/paro); `data/resultados/comparativa_3_municipios_mongo.csv` |
| **C19** | Preparación para visualización | `PREPARACION-VISUALIZACION-01`, `chart_*`, `DOCS-01` | `data/resultados/mongo_*.csv` (8 ficheros); `analysis/run_analisis_mongo.py:190` (`exportar_csv`), `:397` (`exportar_png_desde_mongo`); `presentacion-de-resultados/spec.md:306,317,339,378` (4 `chart_*`) |

### 6.2 Tema 8 (docx §16)

| # | Criterio | Peso | Requisito | Evidencia |
|---|---|---|---|---|
| **T1** | Modelado documental | 15 % | `MODELO-01` | `docs/modelo_mongodb.md:144-152` (§5 preguntas literales), `:24` |
| **T2** | CRUD, limpieza y consultas | 15 % | `PYMONGO-01`, `LIMPIEZA-01`, `TRANSFORM-01`, `CONSULTAS-01`, `VALIDACION-01` | `analysis/mongo_queries.py` (30 funciones); `storage/clean_mongo.py` |
| **T3** | Aggregation | 20 % | `AGREGACION-01`, `HAB-01` | `analysis/mongo_aggregations.py`; `analysis/run_analisis_mongo.py:49-62` |
| **T4** | Índices y rendimiento | 15 % | `INDICES-01` | `analysis/mongo_indexes.py:62,107,135` |
| **T5** | Transacciones y consistencia | 10 % | `TRANSACCIONES-01` | `storage/mongo.py:170-197`; `docs/modelo_mongodb.md:65,166` |
| **T6** | PyMongo profesional | 15 % | `PYMONGO-PRO-01`, `CARGA-SEGURA-01`, `RESPALDO-01`, `VERIFICACION-01` | `storage/mongo.py:54` (`get_client` reutilizable), `:23` (URI configurable); `storage/load_mongo.py:235-236` |
| **T7** | Defensa técnica | 10 % | `ENTREGABLES-01`, `CONCLUSION-01`, `DISTRIBUIDA-01`, `ARQUITECTURA-01` | `docs/guion_defensa.md`; `docs/guion_defensa_12min.md`; `docs/modelo_mongodb.md` |

**Trazabilidad inversa:** los 19 criterios y los 7 de Tema 8 tienen al menos un requisito (0 huérfanos), verificado en `mapa_requisitos.md` §5.

---

## 7. Impacto de cada desviación sobre la nota y la defensa

### 7.1 BDA RA1 sin peso (H-W1.3-1)

- **Nota.** El PDF pondera solo SBD (46,7 + 13,3 + 40 = 100 %). Con las notas v8 (SBD 150/150; BDA 37/40), el SBD ponderado es **100,0 %** y BDA es **37/40 = 92,5 %** en su propia escala. El «187/190 (98,4 %)» de `matriz_rubrica_v8.md:3` es un **promedio de puntos brutos**: pondera implícitamente BDA con 4/19 (21,05 %) y cada RA SBD por número de criterios. No es la nota ponderada del PDF.
- **Escenarios:** si BDA se pondera 0 %, total = 100 %; si se pondera 21,05 % (su peso bruto), total = 98,4 %; si se repartiera el 100 % entre 4 RAs (25 % cada una), total = 0,25×92,5 + 0,75×100 = **98,1 %**.
- **Defensa.** Presentar «98,4 %» como la nota es defendible solo si se explica que es puntos brutos. Lo honesto es declarar: **SBD ponderado 100 %; BDA 37/40 (92,5 %); el PDF no declara peso para BDA**. Si el tribunal pregunta por un único porcentaje, la respuesta es que el PDF no lo permite sin aclaración de la entidad evaluadora.
- **Riesgo:** medio. Un tribunal que espere un porcentaje único puede leer el 98,4 % como una nota ponderada y contrastarla con el PDF.

### 7.2 Numeración 27 filas vs 19 (H-W1.3-2)

- **Nota.** No cambia la nota; cambia la trazabilidad.
- **Defensa.** Si el tribunal usa la numeración del contrato, «criterio 5» es **Modelado** (C9), no Integración de fuentes (C5); «criterio 19» es Preparación visualización (C19) en ambos sistemas, pero «criterio 9» no existe en la rúbrica v2. Mitigación: citar siempre **PDF pág. + criterio canónico 1-19** y referenciar el crosswalk de §5.
- **Riesgo:** medio. Un desliz de numeración en defensa puede comparar criterios distintos.

### 7.3 docx §16: 7 puntos finales suprimidos (H-W1.3-3)

- **Nota.** Ninguno (puntuación).
- **Defensa.** Ninguno relevante; pero la nota `spec.md:98` que dice «Sin diferencias literales» es falsa en lo formal y un tribunal escéptico que coteje el docx lo detectará. Mitigación: corregir la nota o declarar la supresión.
- **Riesgo:** bajo.

### 7.4 Referencias de línea dependientes del instrumento (H-W1.3-4)

- **Nota.** Ninguno.
- **Defensa.** Las referencias de línea del contrato (PDF y docx) solo son reproducibles con la auto-extracción de `read_file`. Un tribunal que abra el PDF o el docx con otro instrumento verá números distintos y puede dudar de la trazabilidad. Mitigación: citar **página + sección** y, cuando se cite línea, nombrar el instrumento.
- **Riesgo:** bajo-medio.

### 7.5 Solapamiento PDF ↔ docx §16 (H-W1.3-5)

- **Nota.** No cambia la nota, pero sí la contabilización: la misma evidencia (p. ej. `docs/modelo_mongodb.md`) puntúa en **C9 (13,3 %)** y en **T1 (15 %)**. Además, **T6 (PyMongo profesional)** y **T7 (Defensa técnica)** no tienen equivalente en las 19 tablas, y **C1-C6, C15-C19** no tienen equivalente en el docx.
- **Defensa.** Declarar que el docx §16 es **evaluación separada** (ya lo hace `spec.md:86`) y no presentar el SBD como «el 100 % del reto».
- **Riesgo:** bajo-medio (doble cómputo si alguien suma ambos).

### 7.6 Mapeo partido en dos tablas (H-W1.3-6)

- **Nota.** Ninguno.
- **Defensa.** El contrato tiene el mapeo PDF en `spec.md:182-208` (27 filas) y el mapeo docx en `spec.md:222-267` (por secciones). No existe una tabla canónica única 1-19 en el contrato; la sintetiza `mapa_requisitos.md` (R1). Mitigación: usar el mapa de R1 como tabla canónica.
- **Riesgo:** bajo.

---

## 8. Hallazgos

**Recuento: P0 = 0 · P1 = 0 · P2 = 2 · P3 = 4.** Ningún P0/P1: no se detuvo la auditoría.

| ID | Severidad | Título | Evidencia | Impacto |
|---|---|---|---|---|
| **H-W1.3-1** | **P2** | El PDF no declara peso para BDA RA1; el contrato reproduce la laguna (4 RAs, 3 pesos) sin advertirla | PDF pág. 3 sin línea «Peso» (págs. 4-6 con 46,7/13,3/40); `spec.md:12`; `matriz_rubrica_v8.md:3-4` (187/190) | No se puede calcular la nota ponderada completa. SBD ponderado = 100 %; BDA = 37/40 (92,5 %). El 98,4 % de v8 es puntos brutos, no ponderados |
| **H-W1.3-2** | **P2** | La tabla «Mapeo criterio → requisito» del contrato tiene 27 filas con numeración distinta de la canónica 1-19; 7 filas no son criterios v2 | `spec.md:182-208`; crosswalk en §5; ej. contrato «5 Modelado» = C9; contrato «9-12» = RA4 v1 | Riesgo de trazabilidad y de defensa: cruzar números entre contrato y rúbrica compara criterios distintos |
| **H-W1.3-3** | **P3** | La transcripción del docx §16 suprime el punto final en 7 celdas; la nota que dice «Sin diferencias literales» es falsa | `spec.md:90-96` vs docx §16 (celdas con `.` final); `spec.md:98` | Menor: no cambia contenido ni nota; la nota de trazabilidad queda desmentida |
| **H-W1.3-4** | **P3** | Las referencias de línea del contrato (PDF y docx) solo son reproducibles con la auto-extracción de `read_file`; `pdftotext`/`pypdf`/`python-docx` dan números distintos | PDF: 123 (read_file) vs 178 (pdftotext) vs 290 (pypdf); docx: 266 (read_file) vs 215 (python-docx); §2, §3 | Menor: la trazabilidad exige nombrar el instrumento o citar página/sección |
| **H-W1.3-5** | **P3** | Solapamiento y vacíos entre los criterios del PDF y los del docx §16 | PDF 4 tablas vs docx §16; T6/T7 sin equivalente PDF; C1-C6/C15-C19 sin equivalente docx | La misma evidencia puntúa dos veces con pesos distintos; T6/T7 solo puntúan en el docx |
| **H-W1.3-6** | **P3** | El contrato parte el mapeo en dos tablas con distinto alcance (27 filas PDF + mapa docx por secciones), sin tabla canónica 1-19 | `spec.md:182-208` vs `spec.md:222-267`; `mapa_requisitos.md` §5 sintetiza el canónico | Menor: el lector debe reconstruir el canónico desde el mapa de R1 |

---

## 9. Ejecutado vs solo leído

**Ejecutado (herramienta real, read-only):**
- `pdftotext -layout` del PDF → 178 líneas (ISO-8859); `pypdf.PdfReader` → 6 páginas, metadata, extracción por página → 290 líneas.
- `python-docx` → extracción ordenada de párrafos y tablas del docx (215 líneas) + extracción de la tabla §16.
- `sha256sum` del PDF (`6f75e97f…b185`, coincide con R1) y del docx (`2e1a64d0…d41f`).
- `read_file` del PDF (auto-extracción, 123 líneas) y del docx (auto-extracción, 266 líneas): confirman que las referencias de línea del contrato apuntan a este instrumento.
- `compare_w13.py` / `compare_w13b.py` (scratch): 95/95 celdas PDF OK (19 con negrita); 14 exactas + 7 punto-final en docx; 3 pesos PDF; 7 pesos docx; 10/10 requisitos adicionales del PDF.
- `grep`/`sed` de evidencia `fichero:línea` para los 19 criterios y 7 de Tema 8 (storage/, analysis/, transform/, extract/, docs/, data/resultados/).
- `ls` de `extract/`, `storage/`, `analysis/`, `scripts/`, `data/resultados/mongo_*.csv`.

**Solo leído (sin ejecutar):** `rubrica_reextraida.md`, `mapa_requisitos.md`, `informe_extract.md`, `00_baseline_v9.md`, `plan_ejecucion_v9_rondas_2026-11-10.md`, `AGENT.md`, `matriz_rubrica_v8.md`, las 5 specs, `docs/guion_defensa.md`, `docs/conclusiones_municipios.md`, `docs/matriz_indicadores.md`, `docs/modelo_mongodb.md`.

**No ejecutado (guardrails):** ningún test, ningún pipeline, `load_all`/`clean_all`/`run_analisis_mongo`, Mongo, HDFS, Kafka, productor, commit/push, instalación.

---

## 10. Bloqueos

**Ninguno.** No se encontró P0/P1. La tarea se completó sin tocar código, datos, Mongo, HDFS ni Kafka.

**Límites:**
- El cotejo literal se hizo normalizando mayúsculas, espacios y guiones; no se comparó tipografía (tamaños, fuentes) del PDF. La negrita del contrato sí se detectó y se aísla como diferencia formal.
- Las referencias de línea se validaron contra la auto-extracción de `read_file` (el instrumento que usa el contrato), no contra un PDF/docx con numeración física estable.
- No se auditó si cada requisito cumple realmente su criterio (eso es W2.x/W3.x); aquí sólo se coteja la rúbrica con el contrato y se señala la evidencia donde se acredita.

---

## 11. Entrega

- **report_path:** `openspec/audit/v9_2026-11-10/desviaciones_rubrica_contrato.md` (este fichero).
- **criteria_covered:** 19/19 rúbrica PDF (C1-C19) + 7/7 Tema 8 (T1-T7). Cotejo literal PDF 95/95; docx §16 14 exactas + 7 punto-final.
- **findings:** H-W1.3-1 (P2, BDA RA1 sin peso; contrato reproduce la laguna), H-W1.3-2 (P2, 27 filas vs 19 canónicos), H-W1.3-3 (P3, 7 puntos finales suprimidos en docx §16), H-W1.3-4 (P3, referencias de línea dependientes del instrumento), H-W1.3-5 (P3, solapamiento PDF ↔ docx §16), H-W1.3-6 (P3, mapeo partido en dos tablas).
- **executed:** `pdftotext`, `pypdf`, `python-docx`, `sha256sum`, `read_file` (PDF/docx/contrato), `compare_w13.py`/`compare_w13b.py`, greps de evidencia.
- **read_only:** contrato, PDF, docx, specs, matriz v8, informes R1, baseline, plan, AGENT.md.
- **blockers:** ninguno.
