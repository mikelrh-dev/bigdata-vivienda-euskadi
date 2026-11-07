# Tasks: mongo-orquestador-analisis

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 180-260 |
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
| 1 | Orquestador 8 pipelines + 3 CSV + tests | PR 1 | `.venv/Scripts/python.exe -m pytest tests/test_mongo_orquestador.py tests/test_mongo_geo.py -q` | `.venv/Scripts/python.exe analysis/run_analisis_mongo.py` | `analysis/run_analisis_mongo.py`, `tests/test_mongo_orquestador.py`, 3 CSV y carpeta del cambio |

## Phase 1: Artefactos SDD

- [x] 1.1 Crear proposal.md, delta spec, design.md y tasks.md en `openspec/changes/mongo-orquestador-analisis/`.

## Phase 2: Implementacion

- [x] 2.1 Crear `analysis/run_analisis_mongo.py` con `run_all_estandar` (8 pipelines en orden fijo), huella SHA-256 de dos ejecuciones y exportacion de 3 CSV con `utf-8-sig`.

## Phase 3: Tests

- [x] 3.1 Crear `tests/test_mongo_orquestador.py` con `test_orquestador_analisis_exporta_tres_conjuntos` en `tmp_path` (3 ficheros y reproducibilidad de `n`).
- [x] 3.2 Anadir `test_preparacion_visualizacion_tres_conjuntos` (cabeceras y coincidencia con los pipelines en memoria).

## Phase 4: Verificacion

- [x] 4.1 Ejecutar `.venv/Scripts/python.exe analysis/run_analisis_mongo.py` y registrar conteos 252/252/2 y huella.
- [x] 4.2 Ejecutar `.venv/Scripts/python.exe -m pytest tests/test_mongo_orquestador.py tests/test_mongo_geo.py -q` y registrar exit code real.
- [x] 4.3 Escribir `verify-report.md` con evidencia real. Sin commit.
