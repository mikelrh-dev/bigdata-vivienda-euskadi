# Tasks: fuentes-validacion

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 80-120 |
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
| 1 | Validación 3 fuentes + informe | PR 1 | .venv/Scripts/python -m pytest tests -q | scripts/validar_fuentes_nuevas.py | Borrar script, informe y test |

## Phase 1: Validación

- [x] 1.1 Crear scripts/validar_fuentes_nuevas.py con comprobaciones DuckDB sin escribir raw.
- [x] 1.2 Generar openspec/audit/validacion_fuentes_2026-11-04.md con cobertura por fuente.

## Phase 2: Tests

- [x] 2.1 Añadir tests/test_fuentes_validacion.py de gate de join.
- [x] 2.2 Verificar pytest y verificar_fase_datos sin regresión.
