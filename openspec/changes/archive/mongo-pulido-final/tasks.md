# Tasks: mongo-pulido-final

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 80-140 (incl. artefactos SDD) |
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
| 1 | Pulido MongoDB y dashboard | PR 1 | `.venv/Scripts/python.exe -m pytest tests/test_mongo_geo.py tests/test_mongo_comparativa.py -q` | `.venv/Scripts/python.exe transform/generar_dashboard_completo.py` | Los 3 ficheros y la carpeta del cambio |

## Phase 1: Artefactos SDD

- [x] 1.1 Crear proposal.md, design.md, tasks.md y deltas spec en `openspec/changes/mongo-pulido-final/`.

## Phase 2: Aplicación

- [x] 2.1 Ejecutar `transform/generar_dashboard_completo.py` y verificar que genera los PNGs del bloque A-G.
- [x] 2.2 Corregir la línea 96 de `data/resultados/dashboard_completo.html` de 6 robustos a 4 robustos con nombres y n.
- [x] 2.3 Actualizar `openspec/project.md`: línea 6 sin análisis pendientes y check en filas 30, 31 y 79.
- [x] 2.4 Actualizar `openspec/specs/mongodb-y-analisis/spec.md` línea 4 a Estado Hecho con RA3, INDICES-01 y TRANSACCIONES-01.

## Phase 3: Verificación

- [x] 3.1 grep sin 6 robustos en el HTML y sin Mongo pendiente en project.md.
- [x] 3.2 Ejecutar `.venv/Scripts/python.exe -m pytest tests/test_mongo_geo.py tests/test_mongo_comparativa.py -q` con exit 0.
- [x] 3.3 Escribir verify-report.md con los greps y el resultado de pytest.
