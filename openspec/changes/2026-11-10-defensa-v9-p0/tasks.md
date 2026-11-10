# Tasks: 2026-11-10-defensa-v9-p0

## Review Workload Forecast

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

**~400-480 líneas → supera 400: chained PRs.**

- PR 1 (P0): test `.venv/Scripts/python.exe -m pytest tests/test_mongo_indices.py tests/test_mongo_geo.py -q`; harness `ensure_indexes()` + `list_indexes()` → 4; rollback `git checkout --` tests/docs.
- PR 2 (P1): test `.venv/Scripts/python.exe scripts/verificar_gobernanza.py`; harness `grep -rn` cifras canónicas; rollback `git checkout --` docs/manifiestos.
- PR 3 (HM-03, solo con autorización): test `pytest tests -q`; harness `clean_all()`; rollback no tocar prod.

## Phase 1: Restauración de índices

- [x] 1.1 `ensure_indexes()` (`analysis/mongo_indexes.py:62-94`) con autorización y coordinación. Verificación: `list_indexes()` → 4 índices en `anuncios`, 24 en 16 vivas.
- [x] 1.2 Re-verificar `list_indexes()` (`plan_fixes_v9.md:28`); repetir si mutó.

## Phase 2: Análisis read-only

- [x] 2.1 `explain_before_after` (`analysis/mongo_indexes.py:107-132`): "antes" `hint:{"$natural":1}` (COLLSCAN 594), "después" índice ESR; filtro `20069`. Verificación: `before.stage=COLLSCAN`, `after.stage=IXSCAN`, `totalDocsExamined=1`.
- [x] 2.2 `explain_promo_before_after` (`:135-149`) e `index_report` (`:152-158`): sin `create_index`. Verificación: `list_indexes()` invariante.
- [x] 2.3 `main()` (`analysis/run_analisis_mongo.py:1163-1173`) read-only. Verificación: `list_indexes()` idéntico antes/después.

## Phase 3: Aislamiento de tests

- [x] 3.1 `tests/test_mongo_geo.py:13`: envolver `load_anuncios()` con `mongo_tmp` (`tests/test_load_mongo.py:37-43`) o `get_test_db()`. Verificación: `pytest tests/test_mongo_geo.py -q` sin tocar prod.
- [x] 3.2 `tests/test_mongo.py:290,296-298,333` y `tests/test_mongo_indices.py:17,33,49`: quitar `ensure_indexes()`/`create_index`. Verificación: `pytest tests/test_mongo.py tests/test_mongo_indices.py -q`.
- [x] 3.3 `skipif(not ping())` si no se puede aislar. Verificación: `MONGO_HOST=127.0.0.1 MONGO_PORT=1 pytest tests -q` → skips.
- [x] 3.4 Suite hermética: `.venv/Scripts/python.exe -m pytest tests -q` verde sin `-k`/`--deselect`; `list_indexes()`/recuentos idénticos.

## Phase 4: Guion y atribución

- [x] 4.1 `docs/guion_defensa.md:9,10,33,44,51`: IXSCAN con filtro `20069` (1 doc; `48020` → 8; `48001` → 0), referencing por `codigo_ine`, 24 índices; no tocar `guion_defensa_12min.md:144` (R-3). Verificación: `grep -n "759\|embedding" docs/guion_defensa.md` limpio.
- [x] 4.2 `incidente_p0_mongo.md:9-13`: mutador `test_mongo_geo.py:13`, no `test_load_mongo.py` (`:37-43`). Verificación: coincide con `plan_fixes_v9.md:25`.
- [x] 4.3 `verificacion_dinamica.md:154`: corregir P1-1 (loaders parcheados en `test_mongo_consistencia.py:131-144`). Verificación: coherente con el código.

## Phase 5: Barrido documental

- [x] 5.1 `grep -rn` de 759/177/10/14/5-6/12 en `docs/`, `README.md`, `AGENT.md`, `openspec/project.md`, `analysis/run_analisis_mongo.py:1151`, `storage/clean_mongo.py:386`, `mongodb-y-analisis/spec.md`.
- [x] 5.2 Sustituir por 594; 424/594 y 170; 16+14; 11; 8; 204/126/50/39; 235+2; IXSCAN con filtro; 28+8 PNG; borrar `HTMLEOF` (`docs/README.md:36`). Verificación: `grep -rn` limpio.
- [x] 5.3 Documentar en `docs/modelo_mongodb.md` geo 2dsphere sparse, multikey `equipamiento` y parcial, con consulta real.

## Phase 6: Manifiestos, gate y flags

- [x] 6.1 Regenerar `data/procesado/_meta/ingestion_manifest.json` con `extract/generar_ingestion_manifest.py` (D-01). Verificación: SHA `lanbide_paro_*` = `docs/raw_manifest_sha256.txt`. **Verificado**: los 5 ficheros `lanbide_paro_*` del acta (354) coinciden byte a byte con el manifest raw.
- [x] 6.2 Declarar `ingestion_manifest.json` excluido en `data/procesado/manifest_sha256.txt` (D-11). Verificación: 188 entradas. **Verificado**: `EXCLUIDOS` de `extract/generar_manifest.py` ya lo excluye; el manifest tiene 188 entradas y 0 menciones.
- [x] 6.3 `scripts/verificar_gobernanza.py:36,44,64`: regex 46→50 (`chart_*`) y escáner `os.environ.get`; declarar `GATE_LIVE`/`RAW_GUARD_AUDIT_LOG` en `.env.example` (H-SA-01/H-M1). Verificación: gate → TODO OK, 0 env sin declarar. **Verificado**: 50 cabeceras (46 con ID), 0 env sin declarar.
- [x] 6.4 HM-03: se documenta la limitación (D8); NO se ejecuta `clean_all()`. Los pipelines de análisis no dependen de los flags y la única escritura destructiva pendiente queda fuera de este cambio.

## Limitaciones

- **R-4:** al aislar `test_mongo_geo.py` se pierde la aserción geo real 424/594 (`verificacion_rubrica_fixes.md:83,124`). Mitigación: lectura read-only en el gate o documentar en `informe_mongo_v9.md`.
- HDFS/Kafka no conectados; el flujo es Windows>Kafka>HDFS y nunca pasa por Mongo.
- Commits local-only; nunca push.

## Evidencia

**Ejecutado:** `pytest tests -q` (exit 0, 235 passed + 2 skipped, índices y recuentos idénticos antes/después), `scripts/verificar_gobernanza.py` (TODO OK), `scripts/gate_extremo_a_extremo.py --offline`, `transform/run_all.py --check`, explain read-only y sondas de SHA.
**Solo leído:** proposal, deltas, design, `plan_fixes_v9.md`, `verificacion_rubrica_fixes.md`, `config.yaml`.
**No ejecutado:** `clean_all()` (HM-03, solo documentado), `ensure_indexes()` (ya restaurado en la sesión previa), recarga de Mongo, HDFS/Kafka en vivo (red del centro no alcanzable). Sin push.
