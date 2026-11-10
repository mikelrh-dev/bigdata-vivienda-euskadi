# Plan de auditoría v10 — rúbrica v2 (19) + Tema 8 (7), archivo por archivo

**Fecha:** 2026-11-10 · **Modo:** solo lectura · **Autor:** sesión de auditoría v10
**Fuente de verdad de la nota:** `brief/RETO 1Evaluacion SBD-BDAv2.pdf` (6 págs., SHA `6f75e97f…b185`), transcrito en `openspec/specs/contrato-reto/spec.md`.
**Fuente de verdad del Tema 8:** `brief/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx` §16 (pesos 15/15/20/15/10/15/10, evaluación separada).

---

## 0. Qué audita esta v10 y qué no

| Sí | No |
|---|---|
| Cumplimiento literal de los 19 criterios v2 y los 7 del Tema 8 | Reescribir la rúbrica o suavizar umbrales |
| Trazabilidad criterio → requisito → código → test → evidencia ejecutada | Aplicar fixes (se documentan, no se tocan) |
| Errores potenciales, deuda y mejoras, con severidad P0-P3 | Instalar dependencias, mutar Mongo/HDFS/Kafka/`data/` |
| Contradicciones entre contrato, specs, docs, README y código | Commit/push |

**Regla de oro:** un criterio vale 10 solo si existe **fichero + cifra + comando** que lo demuestre hoy, no una promesa. La evidencia histórica (v8) se acepta **solo** si se declara como tal y no hay forma de revalidarla; en esta v10 HDFS y Kafka **sí** respondieron y se revalidaron en vivo.

**Escala:** se puntúa con los cuatro niveles del PDF (0 / 3 / 7 / 10) y se expresa en una nota 0-10. No se inventan decimales intermedios salvo en los criterios del Tema 8, que el docx pondera.

---

## 1. Fases y gates

### Fase 0 — Baseline congelada (15 min)

| # | Unidad | Entrada | Comprobación | Salida |
|---|---|---|---|---|
| 0.1 | Estado git | `.git`, árbol | `git status --short`, `git log -5`, `git ls-files .env api.txt` | HEAD, tracked/untracked, secretos rastreados |
| 0.2 | Inventario | repo | `find` por extensión; `wc -l` de `extract/transform/storage/analysis/scripts/tests` | 184 `.py`, 1.406 ficheros, 1,1 GB `data/` |
| 0.3 | Conteos | `data/` | `find data/raw -type f \| wc -l` (356), `data/procesado` (191), `data/resultados` (58), `ls mongo_*.csv` (8) | cifras canónicas del día |
| 0.4 | Infra | red centro | `curl :50070` + `KafkaAdminClient :9092` + `ping()` Mongo | **Hoy: los tres OK** (HDFS 200, Kafka OK, Mongo True) |

**Gate G0:** baseline escrita; si un servicio cae, se anota como límite y **no** se degrada la nota por red.

### Fase 1 — Rúbrica y contrato (30 min)

| # | Unidad | Entrada | Comprobación | Salida |
|---|---|---|---|---|
| 1.1 | Reextracción | PDF v2 | 19 criterios, 4 tablas, 76 celdas, 3 pesos (46,7 / 13,3 / 40) | `rubrica_reextraida.md` (v9, reutilizable) |
| 1.2 | Cotejo literal | PDF vs contrato | 76/76 celdas idénticas; 0 diferencias | OK |
| 1.3 | Numeración | `spec.md:182-208` | 27 filas de mapeo vs 19 criterios canónicos | **H-06** (ambigüedad de trazabilidad) |
| 1.4 | Pesos | PDF | BDA RA1 **sin peso declarado** | **H-07** (no hay nota global única posible) |

**Gate G1:** 19/19 criterios con texto literal y requisito asignado.

### Fase 2 — Flujo del dato, archivo por archivo (4-5 h)

Se audita **en el orden en que el dato viaja**, no por carpetas. Para cada fichero: qué hace, qué criterio toca, qué evidencia produce, qué riesgo tiene.

#### 2.1 `config/` y raíz (5 ficheros)

| Fichero | Qué se verifica | Criterio |
|---|---|---|
| `config/fuentes.yaml` | 25 fuentes, URLs, cobertura, sin secretos | C1, C5, C15 |
| `.env.example` | todas las variables de `os.environ.get` declaradas; sin claves reales | C8, T6 |
| `.gitignore` | `.env` (l.1) y `api.txt` (l.61) ignorados; `/AGENT.md` (l.93) | P-07 |
| `requirements.txt` / `pyproject.toml` | versiones vs `.venv` (pytest 8.3.3 vs 9.1.1) | T6 |
| `openspec/config.yaml` | bloque `context`: dice «HDFS y MongoDB en Docker… Kafka en una VM Ubuntu Server» | **H-05** (contradice la invariante sin Docker) |

#### 2.2 `extract/` (41 `.py`) — C1, C5, C15, P-02/P-06

| Grupo | Ficheros | Qué se verifica |
|---|---|---|
| APIs | `01_eustat_api`, `02_eustat_alquiler`, `04_b5m_geo`, `06_ine_api`, `07_ine_salarios`, `09_realtyapi`, `16_serpavi_renta`, `18_lanbide_paro_juvenil`, `21_lanbide_historico_paro_joven`, `ine_atlas_renta` | `requests` con timeout/retry, paginación, JSON parseado, unit test de forma |
| Scraping | `05_fotocasa_scraper`, `08_pisos_scraper`, `09_fotocasa_dirigido`, `10_scraping_faltantes`, `13_scraping_habitaciones`, `fotocasa_detalle` | `BeautifulSoup/lxml`, selectores, rate-limit, HTML crudo guardado |
| Open data / ficheros | `03_euskadi_emancipacion`, `10_opendata_bizilagun_etxebide`, `11_transporte_gtfs_paradas`, `15_add_geojson`, `19_udalmap_*`, `20_ecvi_compraventa`, `22_geo_areas_funcionales`, `23_certificados_energeticos`, `24_etxebide_promociones`, `25_udalmap_extendido`, `26_vpo_terminadas`, `salud_centros`, `educacion_centros` | CSV/XLSX/GeoJSON/ZIP/SHP/GTFS; escritura en `data/raw` con guard |
| Orquestación / metadatos | `main_ingest`, `_common`, `normalizar_metadata`, `14_add_metadata_fingerprint`, `entity_resolution`, `euskadi_geo`, `generar_manifest`, `generar_ingestion_manifest` | grafo de extracción, fingerprint, manifest, procedencia |

**Evidencia v10:** 41 scripts; 11 con `requests`/`urlopen`; 6 con `BeautifulSoup`; 356 ficheros raw = 354 canónicos + `.FROZEN` + `.gitkeep`; manifest 354 SHA verificado por el gate.
**Riesgos a cazar:** `zipfile.extractall` (zip-slip), `urlretrieve` sin timeout, escritura no atómica, `data/` creado al importar, extractor que reescribe raw.

#### 2.3 `transform/` (42 `.py`, 34 en DAG) — C7, C15, C17, C18, P-02

| Grupo | Ficheros | Qué se verifica |
|---|---|---|
| Normalización | `normalizar_json_crudos`, `parsear_secciones`, `unificar_anuncios`, `rescatar_features_nlp`, `enriquecer_codigo_ine`, `muni_resolve`, `dim_municipios`, `_raw_guard` | `.FROZEN`, rutas, doble fuente de verdad `dim_municipios`, import-purity |
| Limpieza | `filtrar_outliers`, `limpiar_ecvi`, `limpiar_vpo_municipal`, `limpiar_eustat_demografia`, `corregir_empleo`, `validar_renta`, `imputar_nulos_fuentes`, `completar_alquiler_comarca` | outliers, nulos, IDW declarado, canónico 18-34 |
| Indicadores | `calcular_renta_joven`, `generar_vistas_mercado`, `generar_mercado_area_funcional`, `generar_poblacion_joven_municipal`, `aplicar_cobertura_mercado`, `generar_emancipacion_tier3_93`, `generar_municipios_faltantes_93` | 5+ indicadores, 2+ fuentes, Tier/Nivel ortogonales |
| Metadatos / DAG | `run_all`, `generar_manifest`, `auditar_lagunas_silver`, `generar_mapa_esquema`, `generar_figuras_N`, `generar_cert_energetico_municipal` | orden topológico, 34 nodos, salidas declaradas |

**Evidencia v10:** `run_all.py --check` exit 0 (34/34); silver 188 en manifest; 191 ficheros (3 extras: `.FROZEN`, `.gitkeep`, manifest).
**Riesgos a cazar:** DAG con input fantasma, `cat(NaN)→"alta"`, escrituras no atómicas, script que ejecuta pipeline al importar.

#### 2.4 `storage/` (7 `.py`) — C2, C3, C4, C7, C8, C9, T5, T6

| Fichero | Qué se verifica |
|---|---|
| `mongo.py` | `MongoClient` único (`lru_cache`), `MONGO_URI`, `Decimal128`, `replace_collection` staging→backup→rename, `marcar_calidad_municipio` atómico |
| `load_mongo.py` | 14 loaders idempotentes, `zfill_ine`, `fecha_carga`, `load_all` + `ensure_indexes` |
| `clean_mongo.py` | 6 operaciones: canonicalize, mark_nulls, resolve_duplicates, convert_types, clean_obsolete_fields, clean_null_markers; `demo_crud_operations` |
| `kafka_raw_producer.py` | publica `{rel,size,sha256}` por fichero, key estable, retries |
| `kafka_hdfs_uploader.py` | consume, descarta por SHA, sube a HDFS, commit manual |
| `kafka_topic.py` | 1 partición, RF 1, `ensure_topic` |
| `__init__.py` | superficie pública |

**Evidencia v10 en vivo:** Kafka topic `vivienda_euskadi` end 352 / committed 352 / **lag 0**; HDFS raw 352 ficheros, read-back de `udalmap_vpo_terminadas.csv` con SHA idéntico (`70a2937a…4706`, 35.427 B); `data/procesado` en HDFS **no existe** (404).
**Riesgos a cazar:** `lru_cache` que ignora cambios de `MONGO_URI`; `replace_collection` sin transacción; carga que silencia índices; duplicado `anuncios_habitaciones_unificados` vs `_bigdata`.

#### 2.5 `analysis/` (7 `.py`) — C9-C14, C16-C19, T1-T5

| Fichero | Qué se verifica |
|---|---|
| `mongo_queries.py` | 30 funciones: dot notation, `$elemMatch`, `$all`, `$size`, `$and/$or`, proyección, sort, skip/limit, `$regex`, `$type`, `$exists` |
| `mongo_aggregations.py` | 11 pipelines; etapas usadas: `$match/$group/$lookup/$unwind/$addFields/$project/$sort/$limit/$sortArray/$filter/$map`; `$group` + `$lookup` + `$unwind` (no `$facet`) |
| `mongo_indexes.py` | 4 índices en `anuncios` (ESR, 2dsphere sparse, unique portal+id, multikey equipamiento); explain read-only con `hint:{$natural:1}` |
| `run_analisis_mongo.py` | 11 pipelines, 8 CSV, 28+8 PNG, huella de reproducibilidad, 2 pasadas |
| `comparativa_mongo.py` | 4 Tier A: Bilbao 204 / Donostia 126 / Getxo 50 / Vitoria 39 |
| `sensibilidad.py` | análisis de sensibilidad IDW/oficial |
| `__init__.py` | superficie pública |

**Evidencia v10 en vivo:** explain `20069` → before **COLLSCAN** 594 docs, `totalDocsExamined=594`; after **IXSCAN** 1 doc, `totalDocsExamined=1`, `keys=1`.

#### 2.6 `scripts/` (7 `.py`) — C4, C8, C16, T6

| Fichero | Qué se verifica |
|---|---|
| `run_mongo_pipeline.py` | entrypoint único: `load_all → clean_all → ensure_indexes → pipeline_indicadores`; `--dry-run` |
| `gate_extremo_a_extremo.py` | 5 checks offline + 3 sondas vivas; **H-01**: `lag 0` y `duplicados 0` son tautológicos; **H-02**: `run_vivo()` muerto |
| `verificar_gobernanza.py` | 50 cabeceras, 46 IDs, 42 scripts, 34 DAG, 11 pipelines, 0 env sin declarar |
| `verificar_fase_datos.py` | 18 checks; FAIL 07 conocido (paro-cero) |
| `verificacion_crudos.py`, `upload_procesado.py`, `ensure_topic.py` | verificación de raw, subida de procesados (no usada), topic |

#### 2.7 `tests/` (30 ficheros, 237 tests) — todos

| Grupo | Ficheros | Qué se verifica |
|---|---|---|
| Contrato / datos | `test_contrato`, `test_fase_datos`, `test_crudos`, `test_indicadores`, `test_vpo_municipal` | escenarios del contrato, conteos, formatos |
| Raw / manifiestos | `test_raw_*` (4), `test_manifest_sha`, `test_dedup_fingerprint` | `.FROZEN`, SHA, inmutabilidad, fingerprint |
| Kafka / HDFS | `test_kafka_pipeline`, `test_kafka_bordes`, `test_kafka_topic`, `test_extremo_a_extremo` | fakes, offsets, SHA mismatch, idempotencia |
| Mongo | `test_mongo`, `test_mongo_queries`, `test_mongo_aggregations` (implícito), `test_mongo_indices`, `test_mongo_geo`, `test_mongo_consistencia`, `test_mongo_pymongo_pro`, `test_mongo_pipeline`, `test_mongo_orquestador`, `test_mongo_comparativa`, `test_clean_mongo`, `test_load_mongo`, `test_integracion_mongo` | C6-C14, C16-C19, T1-T6 |
| DAG / transform | `test_run_all`, `test_muni_resolve`, `test_tier_confianza`, `test_pisos_ubicacion_real` | orden, entity resolution, tiers |

**Evidencia v10:** `pytest tests -q` → exit 0, **235 passed, 2 skipped, 237 collected**.
**Riesgos a cazar:** tests que mutan prod, dependencia de cwd, ausencia de Mongo en CI, asserts tautológicos, valores vivos pinneados, 8 requisitos sin test.

#### 2.8 Documentación y contrato (437 `.md`)

| Bloque | Ficheros | Qué se verifica |
|---|---|---|
| Contrato | `openspec/specs/*/spec.md` (5) | 19 criterios, 46 requisitos, escenarios, prohibiciones |
| Docs vivos | `README.md`, `AGENT.md`, `openspec/project.md`, `docs/README.md` | cifras vigentes, invariantes, sin Docker, sin Kafka→Mongo |
| Docs de defensa | `openspec/archive/2026-11-10-docs/{modelo_mongodb,matriz_indicadores,guion_defensa,guion_defensa_12min,conclusiones_municipios,arquitectura_datos}.md` | coherencia con código y cifras |
| Vault | `vaultVivienda/vault-tecnico/06-Defensa/*` | checklist, preguntas, guion |
| Histórico | `openspec/audit/**`, `docs/archive/**` | fechado; no se usa como vigente |

**Gate G2:** todo criterio con evidencia localizada; toda cifra de doc contrastada contra código/Mongo/CSV.

### Fase 3 — Verificación dinámica (1 h)

| Check | Comando | Umbral |
|---|---|---|
| Suite | `.venv/Scripts/python.exe -m pytest tests -q` | exit 0; 235/2 |
| Gobernanza | `.venv/Scripts/python.exe scripts/verificar_gobernanza.py` | `TODO OK` |
| DAG | `.venv/Scripts/python.exe transform/run_all.py --check` | exit 0, 34/34 |
| Gate offline | `.venv/Scripts/python.exe scripts/gate_extremo_a_extremo.py --offline` | exit 0, 5 OK |
| Fase de datos | `.venv/Scripts/python.exe scripts/verificar_fase_datos.py` | 17/18, FAIL 07 declarado |
| Explain | `explain_before_after()` | COLLSCAN→IXSCAN, 594→1 |
| Mongo | conteos + índices + `codigo_ine` | 594/252/252, 4 índices |
| HDFS | `LISTSTATUS&user.name` + `OPEN` + SHA | 352, SHA igual |
| Kafka | `end_offsets` vs committed | lag 0 |

**Gate G3:** cada cifra de la matriz v10 tiene comando y salida.

### Fase 4 — Puntuación y hallazgos (1 h)

1. Cada criterio: cita literal → nivel alcanzado → nota → hueco exacto.
2. Cada hallazgo: severidad, `archivo:línea`, evidencia, impacto, recomendación.
3. Comparación con la matriz v9 para detectar **inflación o regresión** de nota.
4. Backlog ordenado por coste/impacto antes de la defensa.

### Fase 5 — Síntesis (30 min)

- `matriz_rubrica_v10.md` (19 + 7, con nota y hueco).
- `hallazgos_v10.csv` (P0-P3).
- Veredicto: PASS / PASS CON RESERVAS / FAIL + qué se dice y qué no se dice en la defensa.

---

## 2. Matriz de trazabilidad criterio → archivo → comando

| # | Criterio | Archivo principal | Comando / evidencia |
|---|---|---|---|
| 1 | Extracción API y scraping | `extract/*` | 41 scripts, 11 API, 6 scraping |
| 2 | HDFS originales/procesados/recuperación | `storage/kafka_hdfs_uploader.py`, HDFS | `LISTSTATUS` 352 + `OPEN` SHA |
| 3 | Kafka productor/consumidor | `storage/kafka_*` | end 352 / committed 352 / lag 0 |
| 4 | Flujo completo hasta Mongo | `scripts/run_mongo_pipeline.py` | gate offline + dry-run |
| 5 | 2+ fuentes con campo común | `storage/load_mongo.py` | 14 colecciones, `$lookup` |
| 6 | 2+ colecciones + relación | `docs/modelo_mongodb.md` | 16 vivas |
| 7 | 4+ limpiezas | `storage/clean_mongo.py` | 6 funciones |
| 8 | Automatización | `run_mongo_pipeline.py` | 4 pasos, `--dry-run` |
| 9 | Modelado justificado | `modelo_mongodb.md §Embedding` | 7 preguntas + decisión |
| 10 | CRUD 4 ops | `clean_mongo.demo_crud_operations` | contadores + asserts |
| 11 | 5 consultas | `analysis/mongo_queries.py` | 30 funciones |
| 12 | 3+ pipelines / 5 etapas | `analysis/mongo_aggregations.py` | 11 pipelines |
| 13 | explain antes/después | `analysis/mongo_indexes.py` | 594→1 |
| 14 | Atómica/transacción | `storage/mongo.py:170-200` | `find_one_and_update` |
| 15 | Datos heterogéneos | `extract/` + `transform/` | 7 formatos |
| 16 | Automatización análisis | `analysis/run_analisis_mongo.py` | 8 CSV + PNG |
| 17 | 5+ indicadores / 2+ fuentes | `matriz_indicadores.md` | 6+ indicadores |
| 18 | 3+ municipios | `comparativa_3_municipios_mongo.csv` | 4 filas |
| 19 | 3+ conjuntos para visualizar | `data/resultados/` | 8 CSV + 28 PNG |

---

## 3. Escala de severidad

| Nivel | Definición | Acción |
|---|---|---|
| **P0** | Rompe la demo o invalida una cifra central | Parar y reportar |
| **P1** | Criterio < 10 por un defecto corregible, o riesgo de mutar producción | Corregir antes de defender |
| **P2** | Incoherencia documental/contractual o evidencia que no prueba lo que dice | Corregir si hay tiempo; declarar si no |
| **P3** | Deuda menor, cifra histórica, estilo, duplicado | Backlog |

---

## 4. Entregables

1. `plan_auditoria_v10.md` (este documento).
2. `matriz_rubrica_v10.md` — 19 criterios + 7 Tema 8 con nota 0-10, cita literal, evidencia y hueco.
3. `hallazgos_v10.csv` — P0-P3 con archivo, evidencia, impacto y recomendación.

---

## 5. Riesgos y límites del propio plan

| Riesgo | Mitigación |
|---|---|
| Inflar la nota con evidencia histórica | Solo se acepta histórico si está fechado y no revalidable; hoy HDFS/Kafka se revalidaron |
| Confundir «existe el fichero» con «cumple el nivel 10» | Cada fila exige comando + cifra + hueco |
| Mutar producción al verificar | Todo read-only: `explain`, `count_documents`, `LISTSTATUS`, `end_offsets` |
| Docs movidos (`docs/` → `openspec/archive/`) | Se sigue la ruta real; se ignoran enlaces históricos |
| Nota global sin peso BDA | Se publica SBD ponderado (100 %) y BDA sobre 40, sin inventar un total |

---

## 6. Checklist de ejecución

- [x] G0 baseline y servicios
- [x] G1 rúbrica 19/19 literal + 3 pesos
- [x] G2 recorrido archivo por archivo de las 6 capas
- [x] G3 suite, gates, explain, HDFS, Kafka, Mongo
- [x] G4 matriz puntuada con huecos
- [x] G5 hallazgos P0-P3 y veredicto
