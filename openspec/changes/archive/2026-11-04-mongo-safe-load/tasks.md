# Tasks: mongo-safe-load

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 220-300 |
| 400-line budget risk | Medium |
| Chained PRs recommended | No |
| Suggested split | single PR |
| Delivery strategy | single-pr |
| Chain strategy | single-pr |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: single-pr
400-line budget risk: Medium

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | mongo-safe-load completo | PR 1 | `.venv/Scripts/python -m pytest tests/test_mongo.py -q` | carga de prueba de una colección con CSV vacío y verificación de conteos en vivo | Revert de storage/mongo.py, storage/load_mongo.py, tests/test_mongo.py |

## Phase 1: Fundação

- [x] 1.1 Añadir `MONGO_TEST_DB` y helper `replace_collection` con staging y backup en `storage/mongo.py`.
- [x] 1.2 Corregir `zfill_ine` para floats con `int(float(x))` y zfill(5) en `storage/mongo.py`.

## Phase 2: Core Implementation

- [x] 2.1 Migrar las 11 cargas con `coll.drop()` a `replace_collection` en `storage/load_mongo.py`.
- [x] 2.2 Llamar a `ensure_indexes` tras `load_all` con import diferido en `storage/load_mongo.py`.

## Phase 3: Tests

- [x] 3.1 Guarda `MONGO_ALLOW_DESTRUCTIVE=1` en `test_clean_mongo` y `test_crud_demo` en `tests/test_mongo.py`.
- [x] 3.2 Añadir `test_zfill_float` con 1001.0, "1001.0" y 20069.0 en `tests/test_mongo.py`.

## Phase 4: Verification

- [x] 4.1 Suite `pytest tests -q` sin mutar prod por defecto y 108 collected.
- [x] 4.2 Carga de prueba: CSV vacío no borra la original; conteos 13/13 intactos tras swap.
