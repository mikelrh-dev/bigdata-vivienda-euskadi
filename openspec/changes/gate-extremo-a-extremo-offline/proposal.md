# Proposal: Gate extremo a extremo offline

## Intent

El gate extremo a extremo no está automatizado: F10 queda parcial y depende
de ejecución manual. Se propone un gate reproducible offline hoy (sin red)
con modo vivo opt-in para mañana en clase, donde sí hay centro (HDFS/Kafka).

## Scope

### In Scope

- `test_e2e_offline`: extremo a extremo hermético con `tmp_path` + fakes.
- `test_integracion_mongo`: integración Mongo con mongomock o skip.
- `scripts/gate_extremo_a_extremo.py` con `--offline` (defecto) y `--vivo`
  (requiere `GATE_LIVE=1`).
- Umbrales: manifiesto 354 SHA, silver 188, 14 colecciones, 0 duplicados en
  reintentos, lag 0.
- CI: `.github/workflows/quality-gate.yml` (`pytest -q` + job manual vivo).

### Out of Scope

- Conectar hoy a HDFS/Kafka del centro (`10.22.87.215`): usuario offline.
- Tocar `data/raw` ni `.FROZEN`; escribir en Mongo/HDFS/Kafka reales hoy.
- Archivar el cambio: el paso vivo queda TODO explícito para mañana.

## Capabilities

### New Capabilities

- `gate-extremo-a-extremo`: gate offline automatizado + vivo opt-in con
  umbrales 354/188/14/0/lag 0 y guarda PENDA-01.

### Modified Capabilities

- None (no cambian requisitos existentes; solo se automatiza el gate).

## Approach

Gate en Python con argparse: defecto `--offline` (solo FS local read-only,
sin red). `--vivo` exige `GATE_LIVE=1`, si no aborta con código 2. En vivo
comprueba HDFS `10.22.87.215:50070` y Kafka `10.22.87.215:9092`; si aborta
por SHA se corrige y se reejecuta. Tests offline con fakes; integración Mongo
con `mongomock` (skip si no está).

| Area | Impact | Description |
|------|--------|-------------|
| `openspec/changes/gate-extremo-a-extremo-offline/` | New | proposal, spec, tasks |
| `tests/test_extremo_a_extremo.py` | New | e2e offline tmp_path+fakes |
| `tests/test_integracion_mongo.py` | New | mongomock/skip |
| `scripts/gate_extremo_a_extremo.py` | New | --offline/--vivo GATE_LIVE=1 |
| `pyproject.toml`, `Makefile` | New | si no existen |
| `.github/workflows/quality-gate.yml` | New | pytest -q + job manual |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Gate sin automatizar, F10 parcial | High | Riesgo 7/10 si no se automatiza: gate offline + vivo opt-in |
| Conectar al centro hoy (offline) | Med | Sin red en offline; vivo solo con GATE_LIVE=1 |
| Abort por SHA en vivo mañana | Med | Corregir manifiesto y reejecutar |
| Falso verde offline | Low | Umbrales estrictos 354/188/14/0/lag 0 |

## Rollback Plan

Borrar los 5 archivos nuevos y la carpeta `openspec/changes/gate-extremo-*`.
Ningún dato en `data/raw` se toca; rollback sin migraciones.

## Dependencies

- Mañana en clase: HDFS `10.22.87.215:50070`, Kafka `10.22.87.215:9092`,
  Mongo local `localhost:27017`.

## Success Criteria

- [ ] `pytest tests -q` pasa offline (o subset offline documentado).
- [ ] `python scripts/gate_extremo_a_extremo.py --offline` pasa en seco.
- [ ] `--vivo` sin `GATE_LIVE=1` aborta; con `=1` queda TODO para mañana.
