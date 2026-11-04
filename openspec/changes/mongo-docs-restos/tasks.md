# Tasks: mongo-docs-restos

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 4 lineas fuente + artefactos SDD, <200 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR (sin commit en esta ronda) |
| Delivery strategy | single-pr |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | 4 fixes de texto + verificacion | PR 1 | .venv/Scripts/python.exe -m pytest tests/test_mongo_geo.py tests/test_mongo_comparativa.py -q | N/A: sin boundary runtime, solo texto y tests existentes | Revertir las 4 lineas |

## Phase 1: Ediciones

- [x] 1.1 Editar transform/generar_dashboard_completo.py linea 176: 4 robustos con nombres y n.
- [x] 1.2 Editar openspec/project.md linea 6: MongoDB fuera de pendientes, HDFS/Kafka pendientes.
- [x] 1.3 Editar openspec/specs/presentacion-de-resultados/spec.md linea 4: Estado Hecho alineado con RA4 v2.
- [x] 1.4 Editar docs/arquitectura_datos.md linea 4: enlace a archive/framework_auditoria_completo2/06_readiness_mongo_infra.md.

## Phase 2: Verificacion

- [x] 2.1 git grep 6 robustos fuera de archive/historial: sin resultados en fuente.
- [x] 2.2 git grep Mongo pendiente en README, arquitectura, modelo, preguntas, project y transform: sin resultados.
- [x] 2.3 Ejecutar .venv/Scripts/python.exe -m pytest tests/test_mongo_geo.py tests/test_mongo_comparativa.py -q y registrar exit code.
