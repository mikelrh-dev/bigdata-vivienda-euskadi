# Tasks: renta-joven-18-34

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 220-320 |
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
| 1 | Renta 18-34 + esfuerzo + poblacion est | PR 1 | .venv/Scripts/python -m pytest tests -q | run_all y load_mongo | Revert de campos nuevos |

## Phase 1: Contrato y parametros

- [x] 1.1 Enmendar openspec/specs/contrato-reto/spec.md con canonico 18-34.
- [x] 1.2 Actualizar config/parametros_estudio.yaml con ratio 18-34.

## Phase 2: Calculos

- [x] 2.1 Anadir ratios 18-34/18-24/25-34 ponderados por anchura en calcular_renta_joven.py.
- [x] 2.2 Generar esfuerzo_joven_pct_18_34 y subgrupos manteniendo legacy en analisis_variables_base.
- [x] 2.3 Calcular poblacion_18_34_est etiquetada en generar_poblacion_joven_municipal.

## Phase 3: Carga y verification

- [x] 3.1 Cargar campos nuevos en Mongo con alias legacy.
- [x] 3.2 Verificar pytest y verificar_fase_datos sin regresion.
