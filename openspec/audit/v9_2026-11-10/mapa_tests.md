# Mapa de tests v9 — `tests/` (30 ficheros) · 2026-11-10

**Unidad:** W2.4 · **Criterios:** todos (19 rúbrica + 7 Tema 8) · **Naturaleza:** solo lectura
**Entrada:** `tests/*.py` (30 ficheros, 4.045 líneas) · **Baseline:** `00_baseline_v9.md` · **Rúbrica:** `rubrica_reextraida.md` · **Mapa de requisitos:** `mapa_requisitos.md` · **Contexto:** `informe_extract.md`, `informe_transform.md`, `informe_storage_analysis_scripts.md`
**Guardrails respetados:** no se modificó código, datos, Mongo, HDFS ni Kafka; no se instalaron dependencias; no hubo commit/push. Única escritura en el repo: este informe. Sondas en `C:\Users\mikel\AppData\Local\hermes\cache\scratch`.

---

## 1. Resumen ejecutivo

- **30 ficheros, 192 funciones `test_*`, 237 tests colectados** (`pytest --collect-only -q`), **698 asserts**, 9 fixtures, 12 funciones parametrizadas, 21 marcadores/skips.
- **La suite no es hermética.** Al ejecutar con Mongo inalcanzable (`MONGO_HOST=127.0.0.1 MONGO_PORT=1`) fallan **40 tests** (31 ERROR + 9 FAILED). El workflow CI (`.github/workflows/quality-gate.yml:18-30`) no levanta servicio Mongo → el job `pytest_offline` no puede pasar en GitHub. Hallazgo **H-T1**.
- **La suite muta producción Mongo.** `tests/test_mongo.py:290,333` y `tests/test_mongo_indices.py:17,33` llaman a `explain_before_after`/`explain_promo_before_after`, que hacen **drop→create** de los índices `idx_anuncios_ine_modalidad_precio` e `idx_promo_ine_estado_tipo` sobre la colección viva. Hallazgo **H-T2**.
- **Dependencia del cwd.** Al coleccionar desde fuera de la raíz del repo, `test_muni_resolve.py` y `test_pisos_ubicacion_real.py` dan **2 ERROR de colección** (`FileNotFoundError: data\raw\dim_municipios.csv`): importan `muni_resolve`, que ejecuta `_load_dim()` en importación con ruta relativa. Es evidencia ejecutada de **T-01/T-05**. Hallazgo **H-T3**.
- **Los hallazgos P2 de R1/R2 no tienen test que los reproduzca o prevenga.** F-01, T-01, T-05, T-06, H-SA-01, H-SA-02, T-02, T-03, T-04, T-09, H-SA-09 y H-SA-12 están **sin cubrir** (H-SA-02, H-SA-13 y H-SA-18 solo parcialmente). La suite verde (235/2) da una confianza que los hechos no sostienen. Hallazgo **H-T4**.
- **8 requisitos canónicos no tienen ningún test:** ENTREGABLES-01, DISTRIBUIDA-01, VALIDACION-01, CAPAS-01, HAB-01, PISOS-05, BOOTSTRAP-01, DOCS-01. El criterio T7 (defensa técnica) tampoco. Hallazgo **H-T8**.
- **Ningún P0/P1.** No se detuvo la auditoría.

---

## 2. Método y evidencia

**Ejecutado (herramienta real, read-only):**

| Comando | Resultado |
|---|---|
| `ast.parse` sobre los 30 `tests/*.py` (sonda en scratch) | 30/30 parsean, 0 errores de sintaxis |
| `pytest tests --collect-only -q` | **237** tests colectados (conteo por fichero en §3) |
| `pytest tests -q -rs` (con 6 tests mutadores deseleccionados, ver §5.1) | **2 skipped**, 0 failed |
| `MONGO_HOST=127.0.0.1 MONGO_PORT=1 pytest tests -q --tb=no` | **31 ERROR + 9 FAILED** (40 tests exigen Mongo vivo) |
| `cd scratch && pytest <repo>/tests --collect-only -q` | **2 ERROR de colección** (`test_muni_resolve.py`, `test_pisos_ubicacion_real.py`) |
| Sonda Mongo read-only (`ping`, `estimated_document_count`, `count_documents`, `list_indexes`) | ping=True; `anuncios` 594; 77 con `equipamiento`; 5 índices presentes |
| `grep` de `guardar_json`, `REQUIRED_METADATA`, `_es_raw`, `.env`, `habitaciones`, `bootstrap`, `capas`, `chart_` en `tests/` | solo coincidencias accesorias (ver §6) |
| `ls` de condiciones de skip de `test_contrato.py` | `data/raw/alquiler_municipal.csv` y `data/raw/renta_municipal_completa.json` **existen** → esos skips no disparan |

**Solo leído (sin ejecutar):** los 30 ficheros de test vía `read_file`/AST; `informe_extract.md`, `informe_transform.md`, `informe_storage_analysis_scripts.md`, `rubrica_reextraida.md`, `mapa_requisitos.md`, `00_baseline_v9.md`, `AGENT.md`, `.github/workflows/quality-gate.yml`, `requirements.txt`, `pyproject.toml`, `analysis/mongo_indexes.py`, `storage/mongo.py`, `transform/muni_resolve.py`.

**No ejecutado (guardrails):** los 6 tests que escriben en Mongo o mutan índices de producción (`test_mongo.py::test_clean_mongo`, `::test_crud_demo`, `::test_indexes_explain`, `::test_explain_promo`, `test_mongo_indices.py::test_indexes_explain_totalDocsExamined`, `test_mongo_consistencia.py::test_atomicidad_documental`). Se deseleccionaron en la pasada de suite para no mutar Mongo. Tampoco se ejecutó ningún pipeline, extractor, `load_all`/`clean_all`, productor Kafka, gate vivo, ni se instaló nada.

---

## 3. Inventario AST (30 ficheros)

| Fichero | Líneas | Tests (func) | Asserts | Fixtures | Skips | Param | Mongo | Red | cwd |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `test_clean_mongo.py` | 113 | 4 | 24 | 1 | 0 | 0 | 1 (mongomock) | 0 | 0 |
| `test_contrato.py` | 398 | 24 (54) | 49 | 0 | 12 | 6 | 0 | 0 | 0 |
| `test_crudos.py` | 32 | 3 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| `test_dedup_fingerprint.py` | 73 | 3 | 7 | 0 | 1 | 0 | 1 | 0 | 0 |
| `test_extremo_a_extremo.py` | 91 | 7 | 9 | 0 | 0 | 0 | 0 | 0 | 0 |
| `test_fase_datos.py` | 274 | 18 | 55 | 0 | 0 | 0 | 0 | 0 | 0 |
| `test_indicadores.py` | 33 | 1 | 5 | 0 | 0 | 0 | 0 | 0 | 0 |
| `test_integracion_mongo.py` | 52 | 3 | 4 | 1 | 0 | 0 | 1 (mongomock) | 0 | 0 |
| `test_kafka_bordes.py` | 179 | 4 | 17 | 0 | 0 | 0 | 0 | 0 | 0 |
| `test_kafka_pipeline.py` | 344 | 11 | 65 | 0 | 0 | 0 | 0 | 0 | 0 |
| `test_kafka_topic.py` | 120 | 6 | 28 | 0 | 0 | 0 | 0 | 0 | 0 |
| `test_load_mongo.py` | 133 | 6 (11) | 17 | 1 | 0 | 1 | 1 (mongomock) | 0 | 0 |
| `test_manifest_sha.py` | 96 | 5 | 11 | 0 | 0 | 0 | 0 | 0 | 0 |
| `test_mongo.py` | 349 | 25 | 107 | 1 | 1 | 0 | 23 | 0 | 0 |
| `test_mongo_comparativa.py` | 64 | 2 | 25 | 0 | 0 | 0 | 0 | 0 | 0 |
| `test_mongo_consistencia.py` | 163 | 2 | 23 | 0 | 0 | 0 | 9 | 0 | 0 |
| `test_mongo_geo.py` | 45 | 1 | 5 | 0 | 0 | 0 | 1 | 0 | 0 |
| `test_mongo_indices.py` | 49 | 1 | 17 | 0 | 0 | 0 | 0 | 0 | 0 |
| `test_mongo_orquestador.py` | 105 | 2 | 28 | 0 | 0 | 0 | 0 | 0 | 0 |
| `test_mongo_pipeline.py` | 117 | 2 | 12 | 0 | 0 | 0 | 1 | 0 | 0 |
| `test_mongo_pymongo_pro.py` | 109 | 2 | 29 | 0 | 0 | 0 | 4 | 0 | 0 |
| `test_mongo_queries.py` | 64 | 6 | 11 | 1 | 0 | 0 | 0 | 0 | 0 |
| `test_muni_resolve.py` | 108 | 7 (14) | 15 | 0 | 0 | 4 | 0 | 0 | 1 |
| `test_pisos_ubicacion_real.py` | 262 | 16 | 49 | 0 | 5 | 0 | 3 | 0 | 0 |
| `test_raw_guard_runtime.py` | 75 | 4 (7) | 3 | 1 | 0 | 1 | 0 | 0 | 0 |
| `test_raw_guardrails.py` | 222 | 5 | 17 | 0 | 0 | 0 | 0 | 0 | 0 |
| `test_raw_inmutable.py` | 93 | 4 | 6 | 0 | 0 | 0 | 0 | 0 | 0 |
| `test_run_all.py` | 100 | 5 | 12 | 1 | 0 | 0 | 0 | 0 | 0 |
| `test_tier_confianza.py` | 125 | 7 | 31 | 1 | 1 | 0 | 0 | 0 | 0 |
| `test_vpo_municipal.py` | 57 | 6 | 11 | 1 | 1 | 0 | 0 | 0 | 0 |
| **Total** | **4.045** | **192 (237)** | **698** | **9** | **21** | **12** | — | **0** | **1** |

**Lectura del inventario:**

- **Red:** 0 tests usan `requests`/`urllib`. Todo el componente Kafka/HDFS se prueba con fakes (`types.SimpleNamespace`, `monkeypatch`) o `mongomock`. Bien.
- **Mongo:** 23 conexiones reales en `test_mongo.py`, más 9 en `test_mongo_consistencia.py` y 4 en `test_mongo_pymongo_pro.py`. Sin embargo **solo 3 ficheros tienen guard `skipif` por Mongo ausente** (`test_tier_confianza.py:27`, `test_dedup_fingerprint.py:62`, `test_pisos_ubicacion_real.py:230,243`).
- **cwd:** 1 sólo uso explícito (`test_muni_resolve.py:87` `monkeypatch.chdir(tmp_path)`), pero hay 2 importaciones de módulo con efecto secundario que dependen del cwd (§5.4).
- **Asserts:** 698 en 192 funciones (3,6 por función). Hay un assert tautológico (§5.2) y varios de desigualdad débil (`>= 0`, `> 0`) que no fijan valor.

---

## 4. Mapa test → requisito → criterio

### 4.1 Por fichero

| Fichero | Tests | Requisitos que cubre | Criterios | Evidencia (docstring / test) |
|---|---:|---|---|---|
| `test_clean_mongo.py` | 4 | LIMPIEZA-01, TRANSFORM-01, PYMONGO-01 | C7, C10, T2 | «clean_mongo con mongomock»; `test_canonicalize_codigo_ine_contadores_y_noop` |
| `test_contrato.py` | 54 | EXTRACCION-01/02, FORMATO-01, COMPLEMENTARIOS-01, PYTHON-01, GATE-JOIN-01, EXTRACCION-03, OUTLIER-01, RENTA-01, PISOS-03, VERIFICACION-01 | C1, C5, C7, C15, C17, C18; P-06/P-07/P-08 | «Cada test corresponde a un requisito o prohibición del contrato»; `test_p06/p07/p08` |
| `test_crudos.py` | 3 | EXTRACCION-01, FORMATO-01, COMPLEMENTARIOS-01, DEDUP-01 | C1, C7, C15 | `test_codigo_ine_5_digitos`, `test_temporal_larga_no_mezclados` |
| `test_dedup_fingerprint.py` | 3 | DEDUP-01 | C7 | docstring «M6 DEDUP-01»; `test_dedup_fingerprint_dos_portales_una_fila` |
| `test_extremo_a_extremo.py` | 7 | VERIFICACION-01, RAW-01, CARGA-SEGURA-01 | C2, C8, T6 | `test_umbrales_normativos`, `test_manifiesto_*` |
| `test_fase_datos.py` | 18 | EXTRACCION-01/02/03, PISOS-01/02/03, OUTLIER-01, DEDUP-01, COMPLEMENTARIOS-01, RENTA-01, VERIFICACION-01 | C1, C5, C7, C15, C17, C18 | docstrings WP-01…WP-19; `test_wp18_metadata_salario` |
| `test_indicadores.py` | 1 | INDICADORES-01 | C17 | «verifica la matriz 2026-11-06» — **solo lee `docs/matriz_indicadores.md`** |
| `test_integracion_mongo.py` | 3 | INTEGRACION-01, MODELO-01 | C4, C5, C6 | mongomock; `test_insert_y_find` |
| `test_kafka_bordes.py` | 4 | KAFKA-01, HDFS-01, RAW-01 | C2, C3 | fakes; `test_consume_sha_mismatch_aborta_systemexit` |
| `test_kafka_pipeline.py` | 11 | KAFKA-01, HDFS-01, RAW-01 | C2, C3 | fakes; `test_produce_publica_con_key_rel_y_api_future` |
| `test_kafka_topic.py` | 6 | KAFKA-01 | C3 | FakeAdmin; `test_ensure_crea_con_1_particion_rf1_capy` |
| `test_load_mongo.py` | 11 | CARGA-SEGURA-01, PYMONGO-PRO-01, TRANSFORM-01 | C8, C7, T6 | mongomock; `test_idempotente_dos_cargas_mismo_conteo` |
| `test_manifest_sha.py` | 5 | RAW-01, VERIFICACION-01 | C2, T6 | tmp_path; `test_mismatch_detecta_cambio` |
| `test_mongo.py` | 25 | MODELO-01, PYMONGO-01, CONSULTAS-01, AGREGACION-01, INDICES-01, LIMPIEZA-01, TRANSFORM-01, RESPALDO-01 | C6–C14, C17, T2–T4 | `test_crud_demo`, `test_aggregation_stages`, `test_indexes_explain` |
| `test_mongo_comparativa.py` | 2 | CONCLUSION-01, RESPUESTA-01, CONCLUSION-02 | C18 | `test_comparativa_cuatro_robustos_tier_a_delta` |
| `test_mongo_consistencia.py` | 2 | TRANSACCIONES-01, PYMONGO-PRO-01, CARGA-SEGURA-01 | C14, T5, T6 | `test_atomicidad_documental` |
| `test_mongo_geo.py` | 1 | DATOS-HETEROGENEOS-01, MODELO-01 | C15, C6 | `test_anuncios_geojson_real` |
| `test_mongo_indices.py` | 1 | INDICES-01 | C13, T4 | `test_indexes_explain_totalDocsExamined` (muta índice prod) |
| `test_mongo_orquestador.py` | 2 | AUTOMATIZACION-ANALISIS-01, PREPARACION-VISUALIZACION-01 | C16, C19 | `test_orquestador_analisis_exporta_tres_conjuntos` |
| `test_mongo_pipeline.py` | 2 | INTEGRACION-01, CARGA-SEGURA-01, LIMPIEZA-01, TRANSFORM-01, AGREGACION-01 | C4, C8, C7, C12 | spies; `test_pipeline_entrypoint_existe` |
| `test_mongo_pymongo_pro.py` | 2 | PYMONGO-PRO-01, PYMONGO-01 | T6, C10 | `test_mongo_uri_configurable`, `test_anuncios_objectid` |
| `test_mongo_queries.py` | 6 | CONSULTAS-01 | C11, T2 | `test_consulta_dos_condiciones_devuelve_filas` |
| `test_muni_resolve.py` | 14 | EXTRACCION-03, PISOS-01, PISOS-02 | C7, C15 | `test_vacio_es_cuarentena_sin_subtitulo` |
| `test_pisos_ubicacion_real.py` | 16 | EXTRACCION-03, PISOS-01/02/03/04, CARGA-SEGURA-01, RESPALDO-01 | C7, C8, C15, C17, T6 | `test_cuarentena_excluida_de_dim_y_conteos`, `test_backup_presente_sin_perdidas` |
| `test_raw_guard_runtime.py` | 7 | RAW-01 | T6 | tmp_path; `test_audit_log_se_escribe` |
| `test_raw_guardrails.py` | 5 | RAW-01, ARQUITECTURA-01, GATE-JOIN-01, PISOS-01 | C2, T6 | AST; `test_no_transform_writes_raw` |
| `test_raw_inmutable.py` | 4 | RAW-01, VERIFICACION-01 | C2, T6 | `test_raw_hashes_manifest` |
| `test_run_all.py` | 5 | CARGA-SEGURA-01, TRANSFORM-01, AUTOMATIZACION-ANALISIS-01 | C8, C16 | DAG sintético; `test_orden_topologico_respeta_dag` |
| `test_tier_confianza.py` | 7 | CONCLUSION-02, INDICADORES-01, AGREGACION-01 | C18, C17, C12 | `test_conteos_4_3_57_188_total_252` |
| `test_vpo_municipal.py` | 6 | COMPLEMENTARIOS-01, PISOS-04, INDICADORES-01 | C17, T6 | `test_sin_dato_declarado_no_imputado` |

### 4.2 Mapa inverso: criterio → tests

| Criterio | Tests que lo acreditan | ¿Cubierto? |
|---|---|---|
| **C1** Extracción API y scraping | `test_contrato` (extracción real/sin duplicar/3 fuentes), `test_crudos`, `test_fase_datos` WP-01/03/10 | ✅ |
| **C2** HDFS originales/procesados/recuperación | `test_extremo_a_extremo`, `test_manifest_sha`, `test_raw_inmutable`, `test_kafka_pipeline` (ruta/verify_local) | ✅ (recuperación no demostrada: H-SA-12) |
| **C3** Kafka productor y consumidor | `test_kafka_pipeline`, `test_kafka_bordes`, `test_kafka_topic` | ✅ |
| **C4** Integración flujo completo a Mongo | `test_integracion_mongo`, `test_mongo_pipeline` | ✅ (parcial: no E2E real) |
| **C5** Integración de fuentes (2+ y campo común) | `test_contrato::test_extraccion_tres_fuentes_independientes`, `test_fase_datos` | ✅ |
| **C6** Construcción del conjunto (2+ colecciones + relación) | `test_integracion_mongo`, `test_mongo_geo`, `test_mongo` | ✅ |
| **C7** Limpieza y transformación PyMongo (4+ ops) | `test_clean_mongo`, `test_mongo`, `test_load_mongo`, `test_contrato`, `test_fase_datos`, `test_muni_resolve`, `test_pisos_ubicacion_real` | ✅ |
| **C8** Automatización (carga+limpieza+transformación) | `test_extremo_a_extremo`, `test_load_mongo`, `test_mongo_pipeline`, `test_pisos_ubicacion_real`, `test_run_all` | ✅ |
| **C9** Modelado MongoDB (embedding/referencing explicado) | `test_mongo` (dot notation/anidados), `test_mongo_geo`, `test_integracion_mongo` | ⚠️ **parcial**: no hay test de la decisión de embedding/referencing |
| **C10** CRUD con PyMongo (4 ops comprobadas) | `test_mongo::test_crud_demo`, `test_mongo_pymongo_pro`, `test_clean_mongo` | ✅ |
| **C11** Consultas (5 útiles, anidada/array, 2+ condiciones) | `test_mongo_queries`, `test_mongo` | ✅ (con 1 assert tautológico, §5.2) |
| **C12** Aggregation (3+ pipelines, 5 etapas, `$group`+`$lookup`/`$unwind`) | `test_mongo::test_aggregation_stages`, `test_mongo_orquestador`, `test_tier_confianza` | ✅ |
| **C13** Índices y rendimiento (`explain` antes/después) | `test_mongo_indices`, `test_mongo::test_indexes_explain`, `::test_explain_promo` | ✅ (muta prod: H-T2) |
| **C14** Consistencia (atómica + justificación) | `test_mongo_consistencia::test_atomicidad_documental` | ✅ |
| **C15** Datos heterogéneos | `test_contrato`, `test_crudos`, `test_fase_datos`, `test_mongo_geo`, `test_pisos_ubicacion_real` | ✅ |
| **C16** Automatización del análisis | `test_mongo_orquestador`, `test_run_all` | ✅ |
| **C17** Indicadores (5+, 2+ fuentes) | `test_indicadores` (solo doc), `test_fase_datos` WP-12/15/19, `test_tier_confianza`, `test_vpo_municipal` | ⚠️ **parcial**: `test_indicadores` no verifica cálculo |
| **C18** Respuesta al reto (3+ municipios, conclusión↔indicador) | `test_mongo_comparativa`, `test_tier_confianza` | ✅ |
| **C19** Preparación para visualización (3+ conjuntos) | `test_mongo_orquestador` (3 CSV en tmp_path); `test_pisos_ubicacion_real::test_resultados_13png_7csv` (**SKIPPED**) | ⚠️ **parcial**: el test de artefactos no se ejecuta |

**Tema 8:**

| Criterio | Tests | ¿Cubierto? |
|---|---|---|
| **T1** Modelado documental 15 % | `test_mongo`, `test_mongo_geo`, `test_integracion_mongo` | ⚠️ parcial (no test de la justificación escrita) |
| **T2** CRUD, limpieza y consultas 15 % | `test_clean_mongo`, `test_load_mongo`, `test_mongo_queries`, `test_contrato` | ✅ |
| **T3** Aggregation 20 % | `test_mongo::test_aggregation_stages`, `test_mongo_orquestador`, `test_tier_confianza` | ✅ |
| **T4** Índices y rendimiento 15 % | `test_mongo_indices`, `test_mongo::test_indexes_explain` | ✅ |
| **T5** Transacciones y consistencia 10 % | `test_mongo_consistencia` | ✅ |
| **T6** PyMongo profesional 15 % | `test_mongo_pymongo_pro`, `test_load_mongo`, `test_raw_guard*`, `test_extremo_a_extremo` | ✅ |
| **T7** Defensa técnica 10 % | — | ❌ **sin test** (es defensa oral/doc; no automatizable) |

### 4.3 Requisitos sin test

| Requisito | Criterio | Estado |
|---|---|---|
| ENTREGABLES-01 | — (apoya C18/C19) | ❌ sin test |
| DISTRIBUIDA-01 | T7 (parcial) | ❌ sin test (solo docs) |
| VALIDACION-01 | T2 (parcial) | ❌ sin test |
| CAPAS-01 | C17/C19 | ❌ sin test (`grep capas/metodo_imputacion/is_imputed` → 0) |
| HAB-01 | C12/C17 | ❌ sin test (`grep habitaciones` solo sale en `convert_types` y nombres de fichero) |
| PISOS-05 | C18 | ❌ sin test |
| BOOTSTRAP-01 | C18 | ❌ sin test (`grep bootstrap` solo Kafka) |
| DOCS-01 | C19 | ❌ sin test |

**8 de 46 requisitos canónicos (17 %) no tienen ningún test.** Los 4 `chart_*` tampoco (C19).

---

## 5. Mutaciones, asserts triviales, skips y dependencias ocultas

### 5.1 Tests que mutan producción

| Test | Mutación | Evidencia |
|---|---|---|
| `tests/test_mongo.py::test_indexes_explain` | **drop→create** del índice `idx_anuncios_ine_modalidad_precio` en `anuncios` (prod) | `tests/test_mongo.py:290` → `analysis/mongo_indexes.py:124-131` |
| `tests/test_mongo.py::test_explain_promo` | **drop→create** del índice `idx_promo_ine_estado_tipo` en `etxebide_promociones` (prod) | `tests/test_mongo.py:333` → `analysis/mongo_indexes.py:141-148` |
| `tests/test_mongo_indices.py::test_indexes_explain_totalDocsExamined` | ambas mutaciones anteriores, dos veces | `tests/test_mongo_indices.py:17,33` |
| `tests/test_mongo.py::test_clean_mongo`, `::test_crud_demo` | escriben en `vivienda_euskadi_test` (no prod) con `patch.object(clean_mongo, "get_collection", …)` | `tests/test_mongo.py:154-164` |
| `tests/test_mongo_consistencia.py::test_atomicidad_documental` | escribe en `vivienda_euskadi_test`; verifica prod invariante | `tests/test_mongo_consistencia.py:52-97` |
| `tests/test_pisos_ubicacion_real.py::test_carga_vacia_no_toca_origen` | `replace_collection("anuncios__probe", [])` → **no escribe** (`storage/mongo.py:153-154` retorna 0 antes de tocar la BD) | verificado por lectura del código |

**No hay ningún test que escriba en `data/` del repo**: todas las escrituras de los tests van a `tmp_path` o a `mongomock`. Verificado por AST (las 8-9 escrituras detectadas son `tmp_path`/`mongomock`/`open` de lectura).

### 5.2 Asserts triviales o débiles

| Evidencia | Problema |
|---|---|
| `tests/test_mongo.py:128` — `assert "_id" not in d or True` | **tautología**: siempre verdadero; no verifica la proyección de C11 |
| `tests/test_mongo.py:134` — `assert dec == sorted(dec, reverse=True)` | compara la lista consigo misma (aunque `dec` venga de la consulta, no fija orden contra un valor independiente) |
| `tests/test_pisos_ubicacion_real.py:161` — `all((r.get("geo_invalida") or "").lower() in ("true","1") …)` | acepta `""` como válido por el `or ""`; no estricto |
| `tests/test_mongo.py:246` — `assert 0 <= e <= 500` | rango amplio que no detecta errores de escala gruesos |
| `grep` de `assert … is not None` / `> 0` | 3 asserts de forma `> 0`/`>= 1` y 8 `== True`/`is True`; no son tautológicos, pero sí de baja precisión |

### 5.3 Skips

**Ejecutado:** la pasada deseleccionando los 6 tests mutadores da **2 skipped** (coincide con el baseline 235 passed / 2 skipped):

| Skip | Disparador | ¿Injustificado? |
|---|---|---|
| `tests/test_pisos_ubicacion_real.py:202` — «artefactos de data/resultados no versionados (solo .gitkeep en git): conteo local no hardcodeado» | `git ls-files data/resultados` vacío | **Sí, enmascara**: el test de 13 PNG/7 CSV nunca corre en CI; C19 queda sin verificación de artefactos |
| `tests/test_pisos_ubicacion_real.py:255` — `skipif MONGO_ALLOW_DESTRUCTIVE != "1"` | variable no definida en CI | **Sí, enmascara**: `test_carga_vacia_no_toca_origen` (CARGA-SEGURA-01) nunca corre |

**Skips condicionales que hoy NO disparan** (verificado con `ls`): `test_contrato.py:103` (`data/raw/alquiler_municipal.csv` existe), `:246`, `:261`, `:276`, `:289`, `:352`, `:387`, `:390`. El único skip «por datos» que podría disparar en otro entorno es `test_vpo_municipal.py:21` (`data/procesado/vpo_municipal.csv` existe hoy).

**Skipif por Mongo:** `test_tier_confianza.py:27`, `test_dedup_fingerprint.py:62`, `test_pisos_ubicacion_real.py:230,243`. **No cubren** a los otros 9 ficheros que necesitan Mongo (§5.4).

### 5.4 Dependencias ocultas

| Dependencia | Evidencia ejecutada | Impacto |
|---|---|---|
| **Mongo local vivo** | `MONGO_HOST=127.0.0.1 MONGO_PORT=1 pytest tests -q --tb=no` → **31 ERROR + 9 FAILED** | 40 tests fallan sin Mongo; CI (sin servicio) no pasa |
| **cwd = raíz del repo** | `cd scratch && pytest <repo>/tests --collect-only -q` → **2 ERROR** (`test_muni_resolve.py`, `test_pisos_ubicacion_real.py`), `FileNotFoundError: data\raw\dim_municipios.csv` | la suite no se puede coleccionar desde otro directorio |
| **`data/` presente** | `test_contrato`, `test_crudos`, `test_fase_datos`, `test_pisos_ubicacion_real`, `test_vpo_municipal` leen raw/silver/resultados | sin datos, fallan o saltan; no hay fixture que los genere |
| **`git` presente** | `test_contrato.py:147` (`git ls-files`), `test_pisos_ubicacion_real.py:194` | skip si falta |
| **paquetes** | `mongomock` (CI lo instala), `kafka-python-ng`, `pymongo`, `pandas` | `mongomock` no está en `requirements.txt` (lo añade el workflow) |

**Causa de la dependencia de cwd (cadena probada):**

1. `tests/test_muni_resolve.py:21` → `import muni_resolve as mr` (módulo).
2. `tests/test_pisos_ubicacion_real.py:27` → `from muni_resolve import …` (módulo).
3. `transform/muni_resolve.py:53` → `CODE2NAME, NAME2CODE, VALID_CODES = _load_dim()` **en importación**.
4. `transform/muni_resolve.py:20` → `RAW = os.path.join("data", "raw")` **relativo al cwd**.
5. `_load_dim()` abre `RAW/dim_municipios.csv` → `FileNotFoundError` si el cwd no es la raíz.

Es la evidencia ejecutada de **T-01** (rutas relativas) + **T-05** (ejecución en importación). No existe ningún test que vigile esta propiedad.

---

## 6. Cobertura de los hallazgos previos

### 6.1 Hallazgos priorizados por la tarea

| Hallazgo | ¿Tiene test? | Evidencia |
|---|---|---|
| **F-01** regresión metadata (`guardar_json` exige `url` en raw) | ❌ **No** | `grep guardar_json` en `tests/` → solo `test_raw_guardrails.py:28` (lista de nombres para AST). `grep REQUIRED_METADATA\|_es_raw` → 0. `test_fase_datos.py:185-194` solo verifica 2 sidecars (`ovj_salario_joven_2024.json`, `emancipacion_juventud_resumen.json`), no las 20 llamadas que fallan |
| **T-01** rutas `data/` relativas al cwd | ❌ **No** (al contrario: la suite lo sufre) | `transform/muni_resolve.py:20`; errores de colección en §5.4 |
| **T-05** 7 scripts ejecutan su pipeline al importar | ❌ **No** | `tests/test_muni_resolve.py:21` y `tests/test_pisos_ubicacion_real.py:27` importan `muni_resolve` con `_load_dim()` en módulo (`muni_resolve.py:53`); ningún test vigila import-purity |
| **T-06** `_raw_guard` es registro, no bloqueo | ❌ **No** | `test_raw_guard_runtime.py` verifica que escribe en `logs/raw_guard_audit.log`; `test_raw_inmutable.py:81-93` verifica `ValueError` por reason vacío. Ninguno comprueba que el guard **no impide** la escritura ni que un `open(...,"w")` sobre raw prosiga |
| **H-SA-01** el gate no captura `os.environ.get` | ❌ **No** | `grep "\.env" tests/` → solo `test_contrato.py:153` (prohibidos `.env`/`api.txt` en `git ls-files`) y `MONGO_ALLOW_DESTRUCTIVE`. Ningún test coteja `.env.example` con los `os.environ.get` reales |
| **H-SA-02** `replace_collection` no atómico | ⚠️ **Parcial** | `test_pisos_ubicacion_real.py:257-262` verifica que `replace_collection(name, [])` no toca prod (camino vacío). No hay test del swap `drop→$out→rename` ni de fallo a mitad |

### 6.2 Resto de hallazgos R1/R2

| Hallazgo | ¿Test? | Nota |
|---|---|---|
| F-02 raw read-only (permisos) | ❌ | `test_raw_inmutable.py` verifica `.FROZEN` + manifiesto, no `os.access`/permisos |
| F-03 `_common` crea `data/*` en importar | ❌ | sin test |
| F-04 `main_ingest` escribe raw sin guard | ❌ | `test_raw_guardrails.py:131` solo escanea `transform/` |
| F-05 `fotocasa_detalle` reescribe raw | ❌ | sin test |
| F-06 `subprocess.run` sin timeout | ❌ | sin test |
| F-07 `urlretrieve` sin timeout | ❌ | sin test |
| F-08 `zipfile.extractall` (zip-slip) | ❌ | `test_raw_guardrails.py:163` solo verifica que no haya literal `/tmp` |
| F-09 escrituras no atómicas | ❌ | sin test |
| F-10 `_n_registros` traga excepciones | ❌ | sin test |
| T-02 doble fuente de verdad `dim_municipios` | ❌ | `test_contrato.py:201` lee la copia **frozen de raw**; `test_crudos.py:10` también raw; `test_fase_datos.py` lee procesado. Ninguno coteja ambas |
| T-03 input fantasma en el DAG | ❌ | `test_run_all.py` usa un DAG sintético; `test_fase_datos.py:108` solo verifica disco ⊆ declarado |
| T-04 escrituras no atómicas en `transform/` | ❌ | sin test |
| T-09 `cat(NaN)` → «alta» | ❌ | `test_fase_datos.py:79-83` verifica 0 NaN en `tension` y categorías permitidas, pero no el caso `NaN → alta` |
| H-SA-06 `explain_before_after` muta prod | ⚠️ | los tests **ejercitan** la mutación; no la vigilan (H-T2) |
| H-SA-09 mediana superior para n par | ❌ | sin test |
| H-SA-11 CI solo ejecuta pytest | ❌ | sin test |
| H-SA-12 HDFS sin read-back | ❌ | `test_kafka_pipeline.py:259` verifica SHA local antes de subir; no relee HDFS |
| H-SA-13 colisión de `_id` en JSON | ⚠️ | `test_load_mongo.py` idempotencia + `test_mongo.py` índice único; no el caso JSON |
| H-SA-18 `$convert` bool → `False` | ⚠️ | `test_clean_mongo.py` / `test_mongo.py` verifican contadores, no la coerción de bool inválido |

**Conclusión:** de los 6 hallazgos priorizados, **5 no tienen test** y 1 es parcial. De los 18 restantes, **12 no tienen test** y 4 son parciales. La suite no reproduce ni previene los defectos que R1/R2 documentaron.

---

## 7. Hallazgos

**Recuento: P0 = 0 · P1 = 0 · P2 = 4 · P3 = 4.** Ningún P0/P1: no se detuvo la auditoría.

| ID | Sev. | Título | Evidencia | Impacto |
|---|---|---|---|---|
| **H-T1** | **P2** | La suite no es hermética: 40 tests exigen Mongo local y CI no lo provee | `MONGO_HOST=127.0.0.1 MONGO_PORT=1 pytest tests -q --tb=no` → 31 ERROR + 9 FAILED; `.github/workflows/quality-gate.yml:18-30` (sin servicio Mongo); guards `skipif` solo en 3 ficheros (`test_tier_confianza.py:27`, `test_dedup_fingerprint.py:62`, `test_pisos_ubicacion_real.py:230,243`) | El job `pytest_offline` no puede pasar en GitHub; la suite no es ejecutable en un entorno limpio; dependencia oculta de la máquina del desarrollador |
| **H-T2** | **P2** | Los tests mutan producción Mongo: drop→create de índices ESR | `tests/test_mongo.py:290,333`; `tests/test_mongo_indices.py:17,33` → `analysis/mongo_indexes.py:124-131,141-148` | Ventana sin índice en `anuncios`/`etxebide_promociones`; si `create_index` falla o el test se interrumpe, el índice prod queda ausente. La suite no es read-only pese al guardrail de auditoría |
| **H-T3** | **P2** | Dependencia del cwd: 2 módulos no coleccionan fuera de la raíz (T-01/T-05 sin cubrir) | `cd scratch && pytest <repo>/tests --collect-only -q` → 2 ERROR; `tests/test_muni_resolve.py:21`, `tests/test_pisos_ubicacion_real.py:27` → `transform/muni_resolve.py:20,53` | La suite depende de lanzarse desde la raíz; any test nuevo que importe un módulo con efecto secundario hereda el fallo. Evidencia ejecutada de dos hallazgos P2 de R2 |
| **H-T4** | **P2** | Los hallazgos P2 de R1/R2 no tienen tests que los reproduzcan o prevengan | §6: 5 de 6 priorizados sin cubrir; 12 de 18 restantes sin cubrir | La suite verde (235/2) no aporta garantía sobre los defectos documentados; falsa confianza en la defensa |
| **H-T5** | **P3** | Assert tautológico en `test_mongo.py:128` | `assert "_id" not in d or True` | Cobertura ilusoria de la proyección en C11; el test pasaría aunque la proyección fallara |
| **H-T6** | **P3** | Skips que enmascaran verificaciones | `tests/test_pisos_ubicacion_real.py:202` (artefactos no versionados) y `:255` (`MONGO_ALLOW_DESTRUCTIVE!=1`) | C19 y CARGA-SEGURA-01 quedan sin ejecutar en CI; los 2 «skip» del baseline son exactamente estos |
| **H-T7** | **P3** | Los tests pinnean valores vivos del datos | `test_tier_confianza.py:45` (`4/3/57/188`), `:54` (`204/126/50/39`), `test_mongo_comparativa.py:53`, `test_mongo_orquestador.py:52` (`251`), `test_mongo.py:305` (`406`), `test_crudos.py:26` (`167/304`), `test_vpo_municipal.py:39` (`48916`) | Cualquier regeneración legítima de datos rompe la suite; también codifica cifras que ya no son canónicas si los datos cambian |
| **H-T8** | **P3** | 8 requisitos canónicos y T7 sin test | §4.3: ENTREGABLES-01, DISTRIBUIDA-01, VALIDACION-01, CAPAS-01, HAB-01, PISOS-05, BOOTSTRAP-01, DOCS-01; `grep habitaciones/bootstrap/capas/chart_` → 0 relevante | El 17 % de los requisitos no tiene verificación ejecutable; CAPAS-01/HAB-01 son enduredcimientos propios del contrato |

---

## 8. Ejecutado vs solo leído

**Ejecutado (herramienta real, read-only):**

- `ast.parse` sobre los 30 `tests/*.py` (sonda en scratch) → 30/30 OK.
- `pytest tests --collect-only -q` → 237 tests (conteo por fichero en §3).
- `pytest tests -q -rs` con los 6 tests mutadores deseleccionados → **2 skipped**, 0 failed.
- `MONGO_HOST=127.0.0.1 MONGO_PORT=1 pytest tests -q --tb=no` → **31 ERROR + 9 FAILED**.
- `cd scratch && pytest <repo>/tests --collect-only -q` → **2 ERROR de colección**.
- Sonda Mongo read-only: `ping=True`, `anuncios=594`, 77 con `equipamiento`, 5 índices (`_id_`, `idx_anuncios_ine_modalidad_precio`, `idx_anuncios_geo`, `idx_anuncios_portal_id`, `idx_anuncios_equipamiento`).
- `grep` de `guardar_json`, `REQUIRED_METADATA`, `_es_raw`, `.env`, `habitaciones`, `bootstrap`, `capas`, `chart_`, `os.environ.get` en `tests/`.
- `ls` de las condiciones de skip de `test_contrato.py`.

**Solo leído (sin ejecutar):** los 30 `.py` de `tests/`; `informe_extract.md`, `informe_transform.md`, `informe_storage_analysis_scripts.md`, `rubrica_reextraida.md`, `mapa_requisitos.md`, `00_baseline_v9.md`, `AGENT.md`, `plan_ejecucion_v9_rondas_2026-11-10.md`, `.github/workflows/quality-gate.yml`, `requirements.txt`, `pyproject.toml`, `analysis/mongo_indexes.py`, `storage/mongo.py`, `transform/muni_resolve.py`.

**No ejecutado (guardrails):** los 6 tests que mutan Mongo/índices; ningún pipeline, extractor, `load_all`/`clean_all`, `run_analisis_mongo`, productor Kafka, gate vivo; ninguna instalación; ningún commit/push. No se escribió en `data/`, Mongo, HDFS ni Kafka.

---

## 9. Bloqueos y límites

- **Ningún P0/P1.** La auditoría no se detuvo.
- **Límite:** no se ejecutó la suite completa con Mongo para no mutar producción (los 6 tests mutadores se deseleccionaron). El recuento de 235/2 del baseline se toma como histórico; la pasada deseleccionada (231 tests) confirma 2 skipped y 0 failed.
- **Límite:** la red centro (HDFS 50070 / Kafka 9092) no se sondea en esta unidad; los tests de Kafka/HDFS son con fakes y no validan contra el centro.
- **Límite:** el `pytest` de `.venv` es 9.1.1 mientras `requirements.txt` fija `pytest==8.3.3`; la versión ejecutada no es la declarada (no se instaló nada).
- **Límite:** los 6 tests deseleccionados siguen existiendo; su efecto (mutación de índices, escritura en `vivienda_euskadi_test`) se documenta por lectura del código, no por ejecución.

---

## 10. Entrega

- **report_path:** `openspec/audit/v9_2026-11-10/mapa_tests.md` (este fichero).
- **criteria_covered:** 19/19 criterios con al menos un test (C9, C17 y C19 en parcial; C13 con mutación de prod) + 7/7 Tema 8 con test (T7 sin test, T1 parcial). 8 de 46 requisitos canónicos sin test.
- **findings:** H-T1 (P2, suite no hermética/40 tests sin Mongo y CI sin servicio), H-T2 (P2, tests mutan índices prod), H-T3 (P2, dependencia del cwd / T-01-T-05), H-T4 (P2, hallazgos R1/R2 sin tests), H-T5 (P3, assert tautológico), H-T6 (P3, skips que enmascaran), H-T7 (P3, valores vivos pinneados), H-T8 (P3, 8 requisitos y T7 sin test).
- **executed:** AST 30/30; `pytest --collect-only` 237; `pytest -q -rs` (6 deseleccionados) 2 skipped/0 failed; `pytest` con Mongo muerto 31 ERROR + 9 FAILED; colección desde scratch 2 ERROR; sonda Mongo read-only; greps y `ls`.
- **read_only:** tests, informes R1/R2, specs, baseline, plan, AGENT.md, workflow, requirements, `mongo_indexes.py`, `storage/mongo.py`, `muni_resolve.py`.
- **blockers:** ninguno.
