# Tasks: demo-png-pipeline-vpo

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 150-250 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Delivery strategy | single-pr |

## Phase 1: PNG desde Mongo

- [x] 1.1 Guardar la figura en `BytesIO` y escribir con `Path.write_bytes`.
  - Verify: 13 PNG generados sin `OSError`.
- [x] 1.2 Regenerar los 13 PNG.
  - Verify: 13 ficheros, 0 con tamaño <1 KB.

## Phase 2: noveno pipeline

- [x] 2.1 `pipeline_vpo_terminadas` en `analysis/mongo_aggregations.py`.
- [x] 2.2 Registrar en `PIPELINE_ORDER` (9) y docstrings.
- [x] 2.3 Test de ejecución real: 251 filas.
  - Verify: `pytest tests -q` → 136 passed.

## Phase 3: docs de defensa

- [x] 3.1 Guion: VPO de flujo, sensibilidad, 354/185, 136 tests, 9 pipelines.
- [x] 3.2 `datos_finales`: VPO de flujo junto al stock sin dato.
- [x] 3.3 Huella nueva en todas las citas vivas.

## Phase 4: demo y gate

- [x] 4.1 Secuencia completa cronometrada (≈15 s).
- [x] 4.2 `pytest`, `--verify`, `run_all --check`, gate 18/18.
- [x] 4.3 `verify-report.md`.
