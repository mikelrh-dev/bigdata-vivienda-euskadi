# Tasks: mongo-respuesta-tres-robustos

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
| 1 | Comparativa 3 robustos + CSV + informe + test | PR 1 | `.venv/Scripts/python.exe -m pytest tests/test_mongo_comparativa.py tests/test_mongo_geo.py -q` | `.venv/Scripts/python.exe -m analysis.comparativa_mongo` | `analysis/comparativa_mongo.py`, CSV, test, seccion del informe y carpeta del cambio |

## Phase 1: Artefactos SDD

- [x] 1.1 Crear proposal.md, delta spec, design.md y tasks.md en `openspec/changes/mongo-respuesta-tres-robustos/`.

## Phase 2: Implementacion

- [x] 2.1 Crear `analysis/comparativa_mongo.py` con `comparativa_tres_robustos` y `main` que escribe el CSV.

## Phase 3: Resultados e informe

- [x] 3.1 Generar `data/resultados/comparativa_3_municipios_mongo.csv` ejecutando el modulo.
- [x] 3.2 Anadir tabla de 3 filas, conclusion por municipio y advertencias a `docs/informe_capacidad_mongo.md`.

## Phase 4: Tests y verificacion

- [x] 4.1 Crear `tests/test_mongo_comparativa.py` con `test_comparativa_tres_robustos_n30`.
- [x] 4.2 Ejecutar `.venv/Scripts/python.exe -m pytest tests/test_mongo_comparativa.py tests/test_mongo_geo.py -q` y registrar exit code.
- [x] 4.3 Escribir `verify-report.md`. Sin commit.
