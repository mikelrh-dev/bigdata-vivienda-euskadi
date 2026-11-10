# Informe W2.3 — storage/ + analysis/ + scripts/ (21 `.py`) — auditoría v9

**Fecha:** 2026-11-10 · **Unidad:** W2.3 · **Naturaleza:** solo lectura · **Autor del artefacto:** subagente v9
**Entrada:** `storage/*.py` (7), `analysis/*.py` (7), `scripts/*.py` (7); `transform/run_all.py` y `.github/workflows/quality-gate.yml` como contexto de gates.
**Guardrails respetados:** no se modificó código, datos, Mongo, HDFS ni Kafka; no se ejecutó `load_all`/`clean_all`/`run_analisis_mongo` completo ni el productor Kafka; no se instalaron dependencias; no hubo commit/push. Única escritura en el repo: este informe. Sondas en `C:\Users\mikel\AppData\Local\hermes\cache\scratch`.

---

## 1. Alcance y método

- **AST/compile:** `ast.parse` + `compile()` en memoria de los 21 ficheros (sin `compileall` para no crear `__pycache__`). 21/21 OK.
- **Imports/entrypoints:** extraídos por AST (funciones top-level, clases, bloque `if __name__ == "__main__"`).
- **Sondas read-only:** consultas Mongo de solo lectura (`estimated_document_count`, `count_documents`, `distinct`, `index_information`, `aggregate` de agregación) y lectura de CSV locales.
- **Gates ejecutados (read-only):** `verificar_gobernanza.py`, `gate_extremo_a_extremo.py --offline`, `transform/run_all.py --check`, `run_mongo_pipeline.py --dry-run`, `upload_procesado.py --dry-run`.
- **No ejecutado:** `load_all`, `clean_all`, `run_analisis_mongo`, productor/consumidor Kafka, gate vivo (`GATE_LIVE=1`).

---

## 2. Inventario (21 ficheros)

| Fichero | Líneas | Imports clave | Entrypoint | Docstring |
|---|---:|---|---|---|
| `storage/__init__.py` | 3 | — | — | `Storage helpers` |
| `storage/mongo.py` | 201 | `pymongo`, `bson`, `dotenv` | — (librería) | MongoDB helpers |
| `storage/load_mongo.py` | 624 | `pandas`, `bson`, `storage.mongo` | `__main__` → `load_all()` | Load silver into MongoDB (idempotent) |
| `storage/clean_mongo.py` | 427 | `pymongo`, `bson`, `storage.mongo` | `__main__` → `clean_all()` + demo | PyMongo cleaning/transformations |
| `storage/kafka_raw_producer.py` | 87 | `kafka`, `dotenv` | `__main__` → `produce()` | Productor Kafka de manifiesto raw |
| `storage/kafka_hdfs_uploader.py` | 193 | `hdfs`, `kafka`, `dotenv` | `__main__` → `consume()` | Consumer Windows → HDFS |
| `storage/kafka_topic.py` | 85 | `kafka.admin`, `dotenv` | `__main__` → `ensure_topic()` | Creación idempotente del topic |
| `analysis/__init__.py` | 0 | — | — | (vacío) |
| `analysis/mongo_aggregations.py` | 728 | `bson`, `storage.mongo` | `__main__` → `run_all()` | 11 pipelines de agregación |
| `analysis/mongo_indexes.py` | 174 | `pymongo.errors`, `bson` | `__main__` → `run_all()` | Índices + `explain()` |
| `analysis/mongo_queries.py` | 293 | `bson`, `storage.mongo` | `__main__` → `run_all()` | Consultas avanzadas |
| `analysis/run_analisis_mongo.py` | 1221 | `analysis.mongo_aggregations`, `matplotlib`, `numpy` | `__main__` → `main()` | Orquestador 11 pipelines → 8 CSV + 32 PNG |
| `analysis/comparativa_mongo.py` | 174 | `analysis.mongo_aggregations`, `storage.mongo` | `__main__` → `main()` | Comparativa Tier A (n≥30) |
| `analysis/sensibilidad.py` | 127 | `numpy`, `pandas` | `__main__` → `main()` | IDW vs oficial + bootstrap |
| `scripts/verificar_gobernanza.py` | 80 | `ast`, `re` | `__main__` → `main()` | Guarda de gobernanza |
| `scripts/gate_extremo_a_extremo.py` | 228 | `hashlib`, `socket` | `__main__` → `main()` | Gate E2E (offline/vivo) |
| `scripts/run_mongo_pipeline.py` | 85 | `storage.*`, `analysis.*` | `__main__` → `main()` | Entrypoint carga+limpieza+índices+agregación |
| `scripts/ensure_topic.py` | 31 | `storage.kafka_topic` | `__main__` → `main()` | Asegura el topic |
| `scripts/upload_procesado.py` | 94 | `hashlib` | `__main__` → `main()` | Subida procesado (solo `--dry-run`) |
| `scripts/verificacion_crudos.py` | 60 | `pandas` | **sin guard** (módulo) | Verificación fase crudos |
| `scripts/verificar_fase_datos.py` | 180 | `pandas`, `subprocess` | `__main__` → `main()` | Gate 18 checks fase datos |

**Total:** 21 ficheros, ~4.600 líneas. 20/21 con `if __name__ == "__main__"`; `scripts/verificacion_crudos.py` ejecuta en import (ver H-SA-14).

---

## 3. PyMongo: conexión, operaciones, transacciones, atomicidad, errores

### 3.1 Conexión

- `storage/mongo.py:53-58` — `get_client()` con `@lru_cache(maxsize=1)` y `serverSelectionTimeoutMS=5000`; `MONGO_URI` tiene prioridad sobre `MONGO_HOST`/`MONGO_PORT` (`:23-32`).
- `get_db`/`get_test_db`/`get_collection` (`:61-70`); `ping()` (`:73-78`) captura toda excepción y devuelve `False`.
- **Hallazgo menor:** el docstring de `get_mongo_uri` dice «Read at call time so monkeypatch of MONGO_URI is visible to get_client()», pero `lru_cache(maxsize=1)` fija el cliente tras la primera llamada; la visibilidad del monkeypatch depende de que los tests llamen `mongo.get_client.cache_clear()` (`tests/test_mongo_pymongo_pro.py:20,30,33,43`). No es un bug funcional, pero la documentación exagera. Ver H-SA-05.

### 3.2 Operaciones (conteo AST/regex)

| Operación | Ocurrencias | Dónde |
|---|---:|---|
| `get_collection(...)` | 17+22+13+9+1 | `clean_mongo`, `mongo_queries`, `mongo_aggregations`, `mongo_indexes`, `comparativa` |
| `update_many` | 17 | `clean_mongo.py:108-252` |
| `update_one` | 8 | `clean_mongo.py:51,62,73,85,98` |
| `delete_many` | 4 | `clean_mongo.py:181,197,215,355` |
| `insert_many` | 1+1 | `mongo.py:159`, `clean_mongo.py:319` |
| `insert_one` | 1 | `clean_mongo.py:316` |
| `find_one_and_update` | 3 | `mongo.py:197`, `clean_mongo.py:329` |
| `bulk_write` | 1 | `clean_mongo.py:344` (`ordered=False`) |
| `count_documents` | 4+7 | `clean_mongo.py`, `mongo_queries.py` |
| `estimated_document_count` | 1 | `mongo_aggregations.py:669` |
| `create_index` | 10 | `mongo_indexes.py:67-93` (8 reales + 2 demos) |
| `drop()` | 2+2 | `mongo.py:158,161`, `clean_mongo.py:313,358` |
| `rename()` | 1 | `mongo.py:163` |

### 3.3 Transacciones y atomicidad

- **No hay transacciones:** `start_session`, `start_transaction`, `with_transaction`, `session=` → 0 ocurrencias en los 21 ficheros.
- **Operación atómica documental:** `marcar_calidad_municipio` (`storage/mongo.py:170-201`) usa `find_one_and_update` con `ReturnDocument.AFTER` sobre un único documento; el docstring (`:176-187`) justifica técnicamente por qué una transacción multidocumento es innecesaria (Tema 8 §11, TRANSACCIONES-01). **Cumple C14.**
- **Swap de colección no atómico:** `replace_collection` (`storage/mongo.py:152-164`) hace `drop(staging) → insert_many(staging) → $out(name→backup) → rename(staging→name, dropTarget=True)`. La secuencia completa no es atómica; hay una ventana entre el `$out` y el `rename` y, dentro de `rename` con `dropTarget=True`, entre el drop del destino y el renombrado. Un fallo en ese punto deja la colección viva ausente. El backup previo mitiga la pérdida de datos, pero no la caída. Ver H-SA-04.
- **`load_all` llama `ensure_indexes` antes de `clean_all`:** `storage/load_mongo.py:607-615` crea los índices (incluido el único `idx_anuncios_portal_id`) al final de la carga, pero el dedup (`resolve_duplicates`) ocurre en `clean_all`, que `scripts/run_mongo_pipeline.py:70-72` ejecuta **después**. Si la fuente tuviera duplicados `(portal, id_anuncio)`, `create_index(unique=True)` fallaría y `load_all` elevaría `RuntimeError`. Con los datos actuales no hay duplicados (ver §3.5), pero el orden es frágil. Ver H-SA-04.

### 3.4 Manejo de errores

- `storage/mongo.py:73-78` — `ping()` traga todas las excepciones (devuelve `False`): aceptable para un health-check.
- `storage/load_mongo.py:607-615` — `ensure_indexes` fallido → `logger.exception` + `raise RuntimeError` (no silencia).
- `storage/load_mongo.py:14-17` — `InvalidOperation` importado con fallback a `ValueError` (compatibilidad).
- `storage/load_mongo.py:39-49` — `_money` registra warning y devuelve `None` en precio no numérico (no propaga).
- `storage/load_mongo.py:57-61,86-90` — `_lookup_csv`/`_lookup_fotocasa_geo` capturan `OSError`/`ParserError`/`UnicodeDecodeError` y devuelven `{}`.
- `storage/clean_mongo.py:23-29` — `_counter` normaliza `matched/modified/deleted/upserted` con `getattr(..., 0)`.
- `storage/clean_mongo.py:407-421` — alias canónicos (`clean_mongo_canonical`, `limpiar_obsoletos`, `clean`, `limpiar`, `run_cleaning`, `main`) que todos apuntan a la misma implementación.
- `analysis/mongo_indexes.py:97-104,140-145` — `drop_demo_index`/`explain_promo_before_after` capturan `OperationFailure` y `TypeError/ValueError`.
- `analysis/run_analisis_mongo.py:1172-1205` — `main()` captura excepciones de `explain`, `vpo_terminadas`, `habitaciones`, `png_mongo` y `extras`, y **devuelve 0** aunque fallen. Ver H-SA-07.

### 3.5 Verificación read-only de invariantes (ejecutado)

| Comprobación | Resultado |
|---|---|
| `anuncios` con `portal` nulo | **0** |
| `anuncios` con `id_anuncio` nulo | **0** |
| `anuncios` duplicados por `(portal, id_anuncio)` | **0 grupos** |
| `alquiler_municipal` docs / `codigo_ine` distintos | **252 / 252** (0 duplicados) |
| CSV `alquiler_municipal_completo.csv` filas / únicos | **252 / 252** |
| CSV `dim_municipios_enriquecido.csv` | 252 / 252 |
| CSV `analisis_variables_base.csv` | 252 / 252 |
| CSV `vpo_municipal.csv` | 252 / 252 |
| CSV `cert_energetico_municipal_252.csv` | 252 / 252 |
| `anuncios` sin `ubicacion.codigo_ine` | 0 |
| Índices presentes | `anuncios` 4, `municipios` 1, `alquiler_municipal` 1, `etxebide_promociones` 1, `certificados_energeticos` 1 |

**Conclusión:** con los datos vigentes, el `_id = codigo_ine` de `load_alquiler`/`load_indicadores`/`load_vpo_municipal`/`load_certificados` no colisiona y el índice único de `anuncios` es seguro. El riesgo es latente para los JSON (`ecvi` `code_trimestre`, `etxebide_solicitudes` `code_anio`, `udalmap*` `code`), que no se verificaron uno a uno. Ver H-SA-13.

---

## 4. Aggregation: 11 pipelines, etapas, `$lookup`/`$unwind`/`$group`, índices y `explain()`

### 4.1 Los 11 pipelines (`PIPELINE_ORDER`, `analysis/run_analisis_mongo.py:49-61`)

| # | Pipeline | Fuente | Etapas principales |
|---|---|---|---|
| 1 | `pipeline_indicadores_municipio` | `municipios` | `$match`, `$lookup`(anuncios), `$addFields`(×7), `$project`, `$sort` |
| 2 | `pipeline_alquiler_por_municipio` | `alquiler_municipal` | `$match`, `$group`, `$lookup`(municipios), `$unwind`, `$project`, `$sort` |
| 3 | `pipeline_modalidades` | `anuncios` | `$match`, `$group`, `$sort`, `$project` |
| 4 | `pipeline_top_municipios_por_esfuerzo` | `municipios` | `$match`, `$lookup`(anuncios), `$addFields`, `$match`(n≥30), `$lookup`(alquiler), `$sort`, `$limit` |
| 5 | `pipeline_esfuerzo_por_sexo` | `municipios` | `$match`, `$lookup`(alquiler), `$addFields`, `$project`, `$sort` |
| 6 | `pipeline_accesibilidad_extendida` | `municipios` | `$match`, `$lookup`(×4), `$addFields`, `$project`, `$sort` |
| 7 | `pipeline_udalmap_extendido_osrm` | `municipios` | `$match`, `$lookup`(udalmap_extendido), `$unwind`(preserve), `$lookup`(osrm), `$project`, `$sort` |
| 8 | `pipeline_vpo_por_municipio` | `etxebide_promociones` | `$match`, `$group`, `$lookup`(municipios), `$unwind`(preserve), `$lookup`(indicadores), `$unwind`(preserve), `$project`, `$sort` |
| 9 | `pipeline_vpo_terminadas` | `vpo_municipal` | `$match`, `$lookup`(municipios), `$unwind`(preserve), `$project`, `$sort` |
| 10 | `pipeline_tier_por_municipio` | `municipios` | `$match`, `$lookup`(anuncios), `$addFields`(×3), `$project`, `$sort` |
| 11 | `pipeline_habitaciones_por_municipio` | `anuncios_habitaciones_*` | `$match`, `$group`, `$addFields`(×2), `$project`, `$sort` |

**Etapas distintas usadas (conteo AST):** `$match` 15, `$lookup` 17, `$addFields` 31, `$project` 11, `$sort` 11, `$limit` 11, `$group` 4, `$unwind` 5, `$sortArray` 3, `$filter` 4, `$switch` 2. **11 etapas distintas**, con `$group` y `$lookup`/`$unwind` presentes. **Cumple C12** (≥3 pipelines, ≥5 etapas, `$group` + `$lookup`/`$unwind`).

### 4.2 Índices (`analysis/mongo_indexes.py:62-94`)

8 índices creados por `ensure_indexes()`:

| Índice | Campos | Nota |
|---|---|---|
| `idx_anuncios_ine_modalidad_precio` | `ubicacion.codigo_ine`, `modalidad`, `precio_eur` | ESR; prefijo usable por los `$lookup` |
| `idx_anuncios_geo` | `ubicacion.coordenadas` (2dsphere, sparse) | |
| `idx_anuncios_portal_id` | `portal`, `id_anuncio` (unique) | requiere dedup previo |
| `idx_anuncios_equipamiento` | `equipamiento` | |
| `idx_municipios_territorio_nombre` | `territorio`, `nombre_canonico` | |
| `idx_alquiler_ine_distrito_nivel` | `codigo_ine`, `distrito`, `nivel_geografico` | |
| `idx_promo_ine_estado_tipo` | `codigo_ine`, `estado_obra`, `tipologia` | |
| `idx_cert_moda` | `cert_moda` | |

### 4.3 `explain()` (`analysis/mongo_indexes.py:107-149`)

- `explain_before_after` **elimina** `idx_anuncios_ine_modalidad_precio`, ejecuta `explain` (COLLSCAN), lo **recrea** y ejecuta `explain` (IXSCAN). `_explain` usa `db.command("explain", {"find": ...}, verbosity="executionStats")` (`:44-59`) y `_winning_stage` recursivo (`:18-41`).
- **Hallazgo:** es una mutación de producción (drop→create) con una ventana sin índice; si `create_index` falla tras el drop, el índice queda ausente. Ver H-SA-06.
- `explain_promo_before_after` (`:135-149`) repite el patrón sobre `idx_promo_ine_estado_tipo`.
- `index_report` (`:152-158`) invoca ambas demos (doble drop/create).
- **Cumple C13** (COLLSCAN→IXSCAN con `totalDocsExamined`), con la reserva de la mutación.

### 4.4 Observaciones de modelado

- **Mediana "upper median" para n par:** `mongo_aggregations.py:571-576` (`_mediana`), `:704-708` (habitaciones) y `:56` (winsorizada) usan `$arrayElemAt[…, floor(n/2)]`, que para n par devuelve el elemento central superior, no la media de los dos centrales. Definición consistente en todos los pipelines, pero no es la mediana estadística. Ver H-SA-09.
- **`pipeline_alquiler_por_municipio` es redundante:** con 252 `codigo_ine` únicos, `$group` siempre produce `n_registros=1` y `$unwind` no descarta nada. Ver H-SA-15.
- **`pipeline_indicadores_municipio` usa `$match: {}`** (`:69`) y carga los 594 anuncios en arrays por municipio; con 252 municipios es manejable, pero es un patrón O(n·m) que no escala.

---

## 5. Gates

### 5.1 `scripts/verificar_gobernanza.py` (ejecutado → `TODO OK`, exit 0)

| Check | Resultado |
|---|---|
| 46 requisitos con ID único | OK |
| 42 scripts `transform/`, 34 nodos DAG | OK |
| 188 entradas en `manifest_sha256.txt` | OK |
| 0 env sin declarar | OK *(pero con ciego, ver H-SA-01)* |
| 11 pipelines en `PIPELINE_ORDER` | OK |

- El scan de env (`:60-67`) solo captura `getenv('X')` y `environ['X']`. **No captura `os.environ.get('X')`.**
- Evidencia del ciego: `scripts/gate_extremo_a_extremo.py:195` usa `os.environ.get("GATE_LIVE")` y `transform/_raw_guard.py:68` usa `os.environ.get("RAW_GUARD_AUDIT_LOG")`; **ninguna de las dos está declarada en `.env.example`** (`grep` → 0 coincidencias). El gate declara «0 env sin declarar» cuando hay al menos 2 usadas sin declarar. Ver H-SA-01.

### 5.2 `scripts/gate_extremo_a_extremo.py --offline` (ejecutado → `OK`, exit 0)

| Check | Resultado |
|---|---|
| Manifiesto raw 354 SHA | OK (verifica SHA de cada fichero) |
| Silver 188 | OK |
| 14 colecciones | OK (verifica que aparecen en `storage/load_mongo.py`) |
| 0 duplicados en reintentos | OK (**simulado**, no real) |
| lag 0 | OK (**tautología**: `EXPECTED_LAG == 0`) |

- `--vivo` requiere `GATE_LIVE=1` (`:194-199`); sonda HDFS/Kafka/Mongo con `tcp_probe` (`:156-161`).
- `run_vivo()` (`:180-182`) está **muerta** (devuelve `[]`; el modo vivo se implementa inline en `main`).
- `PENDA-01` se imprime siempre (`:217-218`). Honesto.
- Ver H-SA-10 (código muerto) y H-SA-11 (checks simulados/tautológicos).

### 5.3 `transform/run_all.py --check` (ejecutado → exit 0)

- DAG declarativo de 34 nodos (`:52-231`), orden topológico de Kahn (`:286-319`), `_check` por staleness (`:392-402`).
- Resultado: los 34 scripts `OK` / `SIN-DECLARAR` (0 `DESACTUALIZADO`, 0 `FALTA`).
- Los scripts fuera del pipeline están en `EXCLUIDOS` con motivo obligatorio (`:234-243`).
- No forma parte de los 21, pero es el gate que `verificar_gobernanza` y `verificar_fase_datos` invocan.

### 5.4 `scripts/run_mongo_pipeline.py` (ejecutado `--dry-run` → `ping=True`, exit 0)

- Orden real: `load_all()` → `clean_all()` → `ensure_indexes()` → `pipeline_indicadores_municipio()` (`:70-73`).
- `--dry-run` solo valida imports y `ping()` (`:65-69`), no muta.
- `ensure_indexes()` tras `clean_all` es redundante (ya lo hace `load_all`). Ver H-SA-04.
- Sin manejo de excepciones: un fallo de `load_all`/`clean_all` propaga traza. Aceptable para operador, pero sin `--dry-run` parcial.

### 5.5 `.github/workflows/quality-gate.yml`

- `pytest_offline` (`:18-30`): `pip install -r requirements.txt pytest mongomock`; `python -m pytest tests -q` con `GATE_LIVE=0`.
- `gate_vivo_manual` (`:33-43`): `workflow_dispatch` + `gate_vivo == true`; `python scripts/gate_extremo_a_extremo.py --vivo` con `GATE_LIVE=1`. **No instala dependencias** (el gate solo usa stdlib: correcto).
- **Hallazgos:** (a) CI no ejecuta `verificar_gobernanza.py`, `run_all.py --check` ni `run_mongo_pipeline.py --dry-run`; (b) `gate_vivo_manual` sonda `10.22.87.215` desde un runner público de GitHub, donde la IP privada es inalcanzable → el job nunca puede pasar en CI. Ver H-SA-11.

---

## 6. Escrituras, secretos, timeouts, rutas absolutas

### 6.1 Escrituras

| Fichero | Escribe en | Mecanismo |
|---|---|---|
| `storage/mongo.py:152-164` | Mongo (staging/backup/rename) | `replace_collection` |
| `storage/mongo.py:197-201` | Mongo (`municipios`) | `find_one_and_update` |
| `storage/load_mongo.py` (15 `load_*`) | Mongo | `replace_collection` |
| `storage/clean_mongo.py` | Mongo | `update_many`/`delete_many`/`drop`/`bulk_write` |
| `storage/kafka_hdfs_uploader.py:167` | HDFS | `client.write(..., overwrite=True)` |
| `storage/kafka_raw_producer.py:71` | Kafka | `producer.send` |
| `storage/kafka_topic.py:65-73` | Kafka | `admin.create_topics` |
| `analysis/run_analisis_mongo.py` | `data/resultados` | 8 CSV + 32 PNG |
| `analysis/comparativa_mongo.py:146-161` | `data/resultados` | 1 CSV |
| `analysis/sensibilidad.py:116-117` | `data/resultados` | 2 CSV |
| `scripts/upload_procesado.py` | **ninguna** (solo `--dry-run`) | verificado: `DRY_RUN_OK CERO_ESCRITURAS` |
| `scripts/verificar_*.py` | **ninguna** | read-only |

### 6.2 Secretos

- **Sin credenciales hardcodeadas.** El scan regex (`password|passwd|pwd|secret|api[_-]?key|token|mongodb://`) sobre los 21 ficheros no halló secretos. `MONGO_URI` se lee de env (`storage/mongo.py:29-32`).
- `.env.example` declara `IDEALISTA_API_KEY=` y `REALTYAPI_KEY=` **vacías** (comentario: «Déjala vacía si no la tienes»). No hay fuglas.
- Las IPs internas `10.22.87.215` aparecen como **defaults** sobreescritubles por env (`storage/kafka_*.py`, `scripts/gate_extremo_a_extremo.py:58-60`), no como secretos.

### 6.3 Timeouts

| Componente | Timeout | Evidencia |
|---|---|---|
| Mongo | `serverSelectionTimeoutMS=5000` | `storage/mongo.py:57-58` |
| HDFS | `HDFS_TIMEOUT_S=60` | `storage/kafka_hdfs_uploader.py:41,104` |
| Kafka poll | `POLL_MS=1000` | `storage/kafka_hdfs_uploader.py:39,124` |
| Kafka idle | `DEFAULT_IDLE_MS=10_000` | `storage/kafka_hdfs_uploader.py:40,66` |
| Gate TCP | `timeout=5.0` | `scripts/gate_extremo_a_extremo.py:156` |
| KafkaProducer/Consumer/Admin | **sin timeout explícito** (defaults de `kafka-python-ng`) | `storage/kafka_raw_producer.py:65`, `storage/kafka_hdfs_uploader.py:105-111`, `storage/kafka_topic.py:63` |

### 6.4 Rutas absolutas

- `/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw` (`storage/kafka_hdfs_uploader.py:37`) y `/user/iabd-user15/.../procesado` (`scripts/upload_procesado.py:24`): defaults HDFS sobreescritibles (`HDFS_URL`/`HDFS_USER`, `dest`).
- No hay rutas `C:\Users\...` en código; todas las rutas locales se derivan de `Path(__file__).resolve().parents[1]`.
- `transform/run_all.py:39-43` usa `PROJECT_ROOT` relativo al fichero. Correcto.

---

## 7. Mapeo a criterios (2, 3, 4, 10–14, 16–19)

Fuente de verdad: `openspec/audit/v9_2026-11-10/rubrica_reextraida.md` (PDF v2).

| # | Criterio (PDF) | Veredicto | Evidencia (fichero:línea) |
|---|---|---|---|
| **2** | Almacenamiento HDFS (guarda y recupera; organiza originales/procesados) | **Cumple con reservas** | Escritura: `storage/kafka_hdfs_uploader.py:104-167` (`InsecureClient`, `makedirs`, `write`). Procesado: `scripts/upload_procesado.py:53-90` (solo dry-run, 0 escrituras). **No hay read-back de HDFS**; la recuperación no se demuestra en código. HDFS no reachable en v9 (baseline §7). |
| **3** | Kafka (productor y consumidor Python procesan mensajes) | **Cumple con reservas** | Productor: `storage/kafka_raw_producer.py:49-79`. Consumidor: `storage/kafka_hdfs_uploader.py:92-185` (poll, commit manual, `type == raw_manifest`). Topic: `storage/kafka_topic.py:45-80`. Sin evidencia en vivo (red caída); tests con fakes. |
| **4** | Integración (flujo completo hasta MongoDB) | **Cumple con reservas** | Cadena dividida: `kafka_raw_producer` → `kafka_hdfs_uploader` (Kafka→HDFS) y `storage/load_mongo.py:590-616` (silver→Mongo) → `analysis/run_analisis_mongo.py:1161-1216` (Mongo→CSV/PNG). No hay un script único que ejecute el flujo completo de extremo a extremo. |
| **10** | CRUD con PyMongo (4 ops + comprobación en código) | **Cumple** | insert: `storage/mongo.py:159`, `storage/clean_mongo.py:316-320`; update: `storage/clean_mongo.py:108-252`, `storage/mongo.py:197`; delete: `storage/clean_mongo.py:181,197,215,355`; find: `analysis/mongo_queries.py:31-263`. Verificación: `_counter` (`storage/clean_mongo.py:23-29`) y `demo_crud_operations` (`:311-359`). |
| **11** | Consultas (5 útiles, anidada/array, 2+ condiciones) | **Cumple** | 28 funciones en `analysis/mongo_queries.py:31-263`: igualdad (`:31`), comparación (`:144`), lógicas (`:159,165`), proyección (`:171`), sort/limit (`:178`), arrays (`:93-121`), nested (`:81`), regex (`:136`), exists/type (`:124,130`), distinct (`:191`). |
| **12** | Aggregation Pipeline (3+ pipelines, 5 etapas, `$group` + `$lookup`/`$unwind`) | **Cumple** | 11 pipelines (`analysis/run_analisis_mongo.py:49-61`); 11 etapas distintas (`mongo_aggregations.py`); `$group` 4, `$lookup` 17, `$unwind` 5. |
| **13** | Índices y rendimiento (`explain` antes/después, COLLSCAN/IXSCAN, `totalDocsExamined`) | **Cumple con reservas** | 8 índices (`analysis/mongo_indexes.py:62-94`); `explain_before_after` (`:107-132`) compara COLLSCAN→IXSCAN con `totalDocsExamined`. Reserva: la demo **muta** el índice en prod (drop→create). |
| **14** | Consistencia (atómica + justificación o transacción) | **Cumple** | `find_one_and_update` atómico (`storage/mongo.py:170-201`) con justificación técnica en el docstring (`:176-187`). Sin transacciones (0 ocurrencias). |
| **16** | Automatización del análisis (script ejecuta todos los análisis y devuelve resultados) | **Cumple** | `analysis/run_analisis_mongo.py:131-146` (11 pipelines), `:1161-1216` (exporta 8 CSV + 32 PNG + 5 extras). Huella SHA-256 reproducible (`:148-157`). |
| **17** | Indicadores (5+, 2+ fuentes) | **Cumple** | `pipeline_indicadores_municipio` (`mongo_aggregations.py:23-282`): `n_anuncios`, `precio_medio_eur`, `superficie_media_m2`, `mediana_precio_m2_winsorizada`, `esfuerzo_joven_pct*`, `tasa_paro_lanbide_pct`, `tension_demanda_social`, combinando `anuncios`+`municipios`+`alquiler_municipal`. |
| **18** | Respuesta al reto (3+ municipios, conclusión ↔ indicador) | **Cumple** | `analysis/comparativa_mongo.py:66-130`: 4 municipios Tier A (Bilbao 204, Donostia 126, Getxo 50, Vitoria-Gasteiz 39) con `esfuerzo_joven_pct_18_34`, `precio_medio_eur`, `cuantia_alquiler_mes`, `tasa_paro_lanbide_pct` desde Mongo. Advertencias de margen (`:24-26`). |
| **19** | Preparación para visualización (3+ conjuntos automáticos) | **Cumple** | 8 CSV (`run_analisis_mongo.py:101-102`) + 32 PNG (`:397-1146`) + 5 extras (`:267-361`), todos desde los 11 pipelines. |

---

## 8. Hallazgos

**Recuento: P0 = 0 · P1 = 0 · P2 = 2 · P3 = 17.** Ningún P0/P1: no se detuvo la auditoría.

| ID | Sev. | Título | Evidencia | Impacto |
|---|---|---|---|---|
| **H-SA-01** | **P2** | El gate de gobernanza no captura `os.environ.get(...)`; declara «0 env sin declarar» cuando hay al menos 2 usadas sin declarar (`GATE_LIVE`, `RAW_GUARD_AUDIT_LOG`) | `scripts/verificar_gobernanza.py:60-67` (regex solo `getenv`/`environ[...]`); `scripts/gate_extremo_a_extremo.py:195`; `transform/_raw_guard.py:68`; `.env.example` sin ambas | La cabecera del gate es incorrecta; dos variables de entorno quedan sin documentar. Integridad del gate |
| **H-SA-02** | **P2** | `replace_collection` no es atómico en su conjunto y `load_all` crea el índice único antes de `clean_all` (dedup): orden frágil + ventana de caída de la colección viva | `storage/mongo.py:152-164`; `storage/load_mongo.py:607-615`; `scripts/run_mongo_pipeline.py:70-72` | Un fallo durante `rename(dropTarget=True)` puede dejar la colección viva ausente; un duplicado en la fuente hace fallar `load_all` antes de poder limpiarlo. Mitigado por el backup `__backup` y por la ausencia actual de duplicados |
| **H-SA-03** | P3 | Referencias stale «9 pipelines + 5 CSV» cuando el orquestador ejecuta 11 pipelines y exporta 8 CSV (H-11) | `analysis/run_analisis_mongo.py:70,132,370,1151,1156` vs `:49-61` y `:101-102` | Documentación/CLI engañosa; no afecta ejecución |
| **H-SA-04** | P3 | Docstring cita 759 (histórico) y menciona `MONGO_ALLOW_DESTRUCTIVE=1`, que no existe en código (solo docstring + assert de test) | `storage/clean_mongo.py:386-387`; `grep MONGO_ALLOW_DESTRUCTIVE` → `tests/test_mongo_consistencia.py:104` (assert env != "1") | Cifra stale (H-12) + falsa sensación de guarda destructiva. La protección real es por convención/test |
| **H-SA-05** | P3 | `get_client` con `lru_cache(maxsize=1)` contradice el docstring que promete visibilidad del monkeypatch de `MONGO_URI`; los tests lo resuelven con `cache_clear()` | `storage/mongo.py:53-58`; `tests/test_mongo_pymongo_pro.py:20,30,33,43` | Menor: el monkeypatch solo funciona si se limpia la caché; documento engañoso |
| **H-SA-06** | P3 | `explain_before_after` (y `index_report`) **eliminan y recrean** el índice ESR de producción durante el análisis; ventana sin índice si `create_index` falla | `analysis/mongo_indexes.py:107-132,135-149,152-158`; invocado desde `run_analisis_mongo.py:1166-1173` | Mutación de prod en una ruta de "análisis"; riesgo de índice ausente |
| **H-SA-07** | P3 | `run_analisis_mongo.main()` traga excepciones de PNG/extras y devuelve 0 aunque fallen | `analysis/run_analisis_mongo.py:1193-1211` | El gate del orquestador no refleja fallos de exportación; se reporta «ok» con artefactos ausentes |
| **H-SA-08** | P3 | `canonicalize_codigo_ine` hace `update_one` por documento (N+1, ~2.600 round-trips) | `storage/clean_mongo.py:46-100` | Rendimiento; con 594+252×8 docs es lento pero funcional |
| **H-SA-09** | P3 | La «mediana» implementada es la mediana superior para n par (`$arrayElemAt[floor(n/2)]`), no la mediana estadística | `analysis/mongo_aggregations.py:56,571-576,704-708` | Definición estadística; afecta a `mediana_precio_m2_winsorizada`, `mediana_precio*`, `mediana_precio_eur`. Consistente, pero no es la mediana estándar |
| **H-SA-10** | P3 | Código muerto: `_money` en `mongo_aggregations.py:12`, `run_vivo` en `gate_extremo_a_extremo.py:180`, `dim_map` en `verificacion_crudos.py:25`, bucle no-op en `verificar_fase_datos.py:133-134`, `exportar_cinco_csv` sin llamadores, `mongo.close()` sin llamador interno | los ficheros citados | Deuda de mantenimiento; no afecta ejecución |
| **H-SA-11** | P3 | CI solo ejecuta `pytest`; no corre gobernanza, `run_all --check` ni `run_mongo_pipeline --dry-run`; el job vivo sonda una IP privada desde runner público | `.github/workflows/quality-gate.yml:17-43` | Cobertura de gates incompleta; `gate_vivo_manual` no puede pasar en GitHub Actions |
| **H-SA-12** | P3 | El consumidor Kafka→HDFS no verifica en HDFS tras escribir (sin read-back); C2 «demuestra su recuperación» no está evidenciado en código | `storage/kafka_hdfs_uploader.py:154-167` (verifica SHA local, escribe, no relee) | La recuperación de HDFS no se demuestra; el gate offline solo valida manifiestos locales |
| **H-SA-13** | P3 | Riesgo latente de colisión de `_id` en cargas JSON (`ecvi` `code_trimestre`, `etxebide_solicitudes` `code_anio`, `udalmap*` `code`) sin validación; un duplicado aborta la colección entera | `storage/load_mongo.py:383-430,459-499` | Los CSV verificados son únicos (252/252); los JSON no se verificaron uno a uno. `insert_many` sin `ordered=False` aborta todo |
| **H-SA-14** | P3 | `scripts/verificacion_crudos.py` ejecuta en import (sin `if __name__ == "__main__"`), con `raise SystemExit` a nivel de módulo | `scripts/verificacion_crudos.py:1-60` | Import secundario; no es reutilizable como librería |
| **H-SA-15** | P3 | `pipeline_alquiler_por_municipio`: `$group` con 252 `codigo_ine` únicos siempre da `n_registros=1`; `$unwind` es redundante | `analysis/mongo_aggregations.py:285-310` + sonda (252/252) | Redundancia; no afecta resultados |
| **H-SA-16** | P3 | Productor Kafka sin `acks`/`retries`/`enable_idempotence` explícitos (defaults de `kafka-python-ng`) | `storage/kafka_raw_producer.py:65` | En clúster RF=1 el riesgo es bajo; no hay garantía explícita |
| **H-SA-17** | P3 | Título H2 con cifras hardcodeadas `A4/B3/C57/D188` (hoy correctas, verificadas por agregación) | `analysis/run_analisis_mongo.py:711`; verificado: A=4, B=3, C=57, D=188 | Se vuelve stale si cambian los datos; el gráfico sí se calcula |
| **H-SA-18** | P3 | `convert_types` usa `$convert` a bool con `onError: False`: valores inválidos se coerced a `False` sin aviso | `storage/clean_mongo.py:246-252` | Enmascara datos malos como `False`; no registra el fallo |
| **H-SA-19** | P3 | `verificar_fase_datos.py` duplica `import re` (`:125`, `:155`) y tiene un bucle no-op (`:133-134`) | el fichero citado | Menor; limpieza |

---

## 9. Ejecutado vs solo leído

**Ejecutado (herramienta real, read-only):**
- `ast.parse` + `compile()` en memoria de los 21 ficheros (21/21 OK); imports/entrypoints por AST.
- Sondas Mongo read-only: `estimated_document_count`, `count_documents`, `distinct`, `index_information`, agregación de tiers.
- Lectura de CSV locales (`alquiler_municipal_completo`, `dim_municipios_enriquecido`, `analisis_variables_base`, `vpo_municipal`, `cert_energetico_municipal_252`).
- Gates: `verificar_gobernanza.py` (TODO OK), `gate_extremo_a_extremo.py --offline` (OK), `transform/run_all.py --check` (exit 0), `run_mongo_pipeline.py --dry-run` (ping=True), `upload_procesado.py --dry-run` (0 escrituras).
- `grep`/`ls`/`wc` sobre los 21 ficheros y `.env.example`, `requirements.txt`, `.github/workflows/quality-gate.yml`.

**Solo leído (sin ejecutar):** el contenido de los 21 `.py` (se auditaron por lectura y AST, no por ejecución); `transform/run_all.py`; `.github/workflows/quality-gate.yml`; `.env.example`; `requirements.txt`.

**No ejecutado (guardrails):** `load_all`, `clean_all`, `run_analisis_mongo`, productor/consumidor Kafka, gate vivo (`GATE_LIVE=1`), instalación de dependencias, commit/push.

---

## 10. Límites de este informe

- HDFS y Kafka no son alcanzables en v9 (baseline §7): C2 y C3 no se revalidan en vivo; se usan el código y los tests como evidencia, no una ejecución real.
- No se ejecutaron los 11 pipelines sobre Mongo (guardrail); el análisis de agregación es estático + sondas de conteo. La corrección de las etapas se verificó por lectura y AST, no por `explain()` de cada pipeline.
- No se verificó byte a byte `data/raw` ni el contenido de los JSON de silver; solo conteos de unicidad de los CSV que alimentan los `_id`.
- Las sondas están en `C:\Users\mikel\AppData\Local\hermes\cache\scratch` (fuera del repo); el repo quedó intacto.
