# Tasks: mongo-pipeline-entrypoint

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 150-220 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | single PR |
| Delivery strategy | single-pr |
| Chain strategy | single-pr |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: single-pr
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Entrypoint único con dry-run y test con mock | PR 1 | `.venv/Scripts/python.exe -m pytest tests/test_mongo_pipeline.py -q` | `.venv/Scripts/python.exe scripts/run_mongo_pipeline.py --dry-run` | `scripts/run_mongo_pipeline.py`, `tests/test_mongo_pipeline.py` y carpeta del cambio |

## Phase 1: Artefactos SDD

- [x] 1.1 Crear proposal.md, delta spec, design.md y tasks.md en `openspec/changes/mongo-pipeline-entrypoint/`.

## Phase 2: Implementación

- [x] 2.1 Crear `scripts/run_mongo_pipeline.py` con `main` que llama en orden `load_all`, `clean_all`, `ensure_indexes` y `pipeline_indicadores_municipio`, imprime conteos y soporta `--dry-run` con ping sin mutar producción.

## Phase 3: Tests

- [x] 3.1 Crear `tests/test_mongo_pipeline.py` con `test_pipeline_entrypoint_existe` que aserta orden con monkeypatch sin tocar producción.
- [x] 3.2 Añadir `test_dry_run_no_muta_prod` que aserta que `--dry-run` no llama a ninguna función de carga.

## Phase 4: Verificación

- [x] 4.1 Ejecutar `.venv/Scripts/python.exe -m pytest tests/test_mongo_pipeline.py -q` y registrar exit code y salida reales.
- [x] 4.2 Ejecutar `.venv/Scripts/python.exe scripts/run_mongo_pipeline.py --dry-run` y registrar exit code y salida reales.
- [x] 4.3 Escribir `verify-report.md` con evidencia real. Sin commit.
