# Tasks: gate-extremo-a-extremo-offline

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 400-550 (gate + 2 tests + CI/config) |
| 400-line budget risk | Medium |
| Chained PRs recommended | No (single slice, gate nuevo aislado) |
| Suggested split | single PR offline; vivo como TODO separado |
| Delivery strategy | single-pr |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Medium

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Gate offline + tests + CI | PR 1 | `pytest tests/test_extremo_a_extremo.py tests/test_integracion_mongo.py -q` | `python scripts/gate_extremo_a_extremo.py --offline` | Borrar gate, tests nuevos, CI, pyproject/Makefile |
| 2 | Vivo en clase | TODO mañana | `GATE_LIVE=1 python scripts/gate_extremo_a_extremo.py --vivo` | HDFS 10.22.87.215:50070, Kafka :9092 | N/A (ejecución, no código) |

## Fase 0: Propuesta y spec (offline)

- [x] 0.1 Crear `openspec/changes/gate-extremo-a-extremo-offline/proposal.md`
- [x] 0.2 Crear `spec.md` + delta `specs/gate-extremo-a-extremo/spec.md`
- [x] 0.3 Crear `tasks.md` (este archivo) con fases 0-4

## Fase 1: Gate offline (sin red)

- [x] 1.1 Crear `scripts/gate_extremo_a_extremo.py` con `--offline` (defecto, sin red)
- [x] 1.2 Añadir chequeo umbrales: 354 SHA raw, 188 silver, 14 colecciones, 0 duplicados, lag 0
- [x] 1.3 Añadir guarda `--vivo` (=`GATE_LIVE=1`, sin flag exit 2) y PENDA-01 sin red
- [x] 1.4 Crear `pyproject.toml` / `Makefile` si no existen (targets test, gate)

## Fase 2: Tests offline

- [x] 2.1 Crear `tests/test_extremo_a_extremo.py` (tmp_path + fakes, hermético)
- [x] 2.2 Crear `tests/test_integracion_mongo.py` (mongomock/skip, sin centro)
- [x] 2.3 Crear `.github/workflows/quality-gate.yml` (pytest -q + job manual vivo)

## Fase 3: Verificación offline

- [x] 3.1 Correr `pytest tests -q` (o subset offline) con `.venv/Scripts/python.exe`
- [x] 3.2 Correr `scripts/gate_extremo_a_extremo.py --offline` en seco
- [x] 3.3 Arreglar cualquier fallo antes de cerrar Fase 3

## Fase 4: Vivo mañana en clase (TODO — NO ejecutado hoy)

- [ ] 4.1 TODO mañana: ejecutar `GATE_LIVE=1 python scripts/gate_extremo_a_extremo.py --vivo` (HDFS 10.22.87.215:50070, Kafka 10.22.87.215:9092)
- [ ] 4.2 TODO mañana: si aborta por SHA, corregir manifiesto y reejecutar el vivo
- [ ] 4.3 TODO mañana: archivar el cambio tras verificar el vivo

## Nota archive-parcial (2026-11-08)

- NO archivar el cambio hoy: Fase 4 queda como TODO explícito para mañana.
- Pendiente mañana: ejecutar `--vivo` con HDFS `10.22.87.215:50070` y Kafka
  `10.22.87.215:9092`, y corregir si aborta por SHA.
