# Tasks: 2026-11-15-regenerabilidad-y-orquestador-unico

## Phase 1: Mongo completo

- [x] 1.1 Añadir `load_habitaciones()` a `storage/load_mongo.py`.
  - Acceptance: carga 201 docs desde el CSV silver, `precio_eur` Decimal128.
  - Verify: `pytest tests/test_load_mongo.py -q`.
  - Files: `storage/load_mongo.py`
- [x] 1.2 Registrar las dos colecciones en `load_all()` y ajustar el test que fija 15.
  - Acceptance: `load_all` devuelve 17 claves.
  - Verify: `pytest tests/test_mongo_consistencia.py -q`.
  - Files: `storage/load_mongo.py`, `tests/test_mongo_consistencia.py`
- [x] 1.3 Guarda de vacío en `exportar_habitaciones_csv`.
  - Acceptance: pipeline vacío → error explícito, no CSV de solo cabecera.
  - Verify: test nuevo en `tests/test_verificar_reproducibilidad.py`.
  - Files: `analysis/run_analisis_mongo.py`, `tests/test_verificar_reproducibilidad.py`

## Phase 2: Orquestador único

- [x] 2.1 `--fase full` en `scripts/run_pipeline.py`.
  - Acceptance: expande a silver, quality, mongo, gold; mongo exige `--allow-mongo-write`.
  - Verify: `run_pipeline.py --fase full --dry-run` y sin el flag → rc 2.
  - Files: `scripts/run_pipeline.py`

## Phase 3: Prueba de reproducibilidad

- [x] 3.1 `docs/baseline_gold_sha256.json` con huella y SHA de los CSV canónicos.
- [x] 3.2 `scripts/verificar_reproducibilidad.py` con las cuatro comprobaciones.
  - Acceptance: rc 0 con Mongo; rc 2 sin Mongo; rc 1 si algo no cuadra.
  - Verify: ejecución real y `pytest tests/test_verificar_reproducibilidad.py -q`.
  - Files: `scripts/verificar_reproducibilidad.py`, `tests/test_verificar_reproducibilidad.py`

## Phase 4: Cierre

- [x] 4.1 Suite completa (`pytest tests`) y checks (`run_all --check`, `run_pipeline --check`).
- [x] 4.2 Escribir `verify-report.md`.
