# Proposal: 2026-11-10-defensa-v9-p0

## Intent

C13 (13,3 %) y T4 (15 %) sin evidencia: `anuncios` tiene solo `_id_` (`incidente_p0_mongo.md:25`), el `explain` real es COLLSCAN 594 (`doc_sweep_2.md:45`) y el guion afirma IXSCAN. La suite y el análisis dropean índices de prod (`plan_fixes_v9.md:66-74`) y el incidente está mal atribuido (`plan_fixes_v9.md:25`). Restaurar los 4 índices y blindar la demo.

## Scope

### In Scope
- P0: restaurar los 4 índices (`ensure_indexes()`); análisis read-only y tests aislados; guion y atribución corregidos.
- P1: barrido H-02…H-07/H-14/H-15/DS1-*/DS2-*; manifiestos D-01/D-11; gate H-SA-01/H-M1; flags HM-03.

### Out of Scope
- P2 (T-01, T-04, T-05, H-SA-02, F-01, D-02, D-03, H-T1, H-SA-11); recarga Mongo, extract, HDFS/Kafka (red caída), CI, commit/push.

## Capabilities

### New Capabilities
- `aislamiento-tests`: tests que cargan/consultan Mongo SHALL usar `mongomock`/`mongo_tmp` o `skipif(not ping())`; SHALL NOT ejecutar `load_anuncios()` ni demos de `explain` sobre prod.

### Modified Capabilities
- `mongodb-y-analisis` (`INDICES-01`): la demo COLLSCAN→IXSCAN SHALL NOT dropear/recrear índices en prod; el "antes" SHALL forzar barrido completo read-only.
- `presentacion-de-resultados` (`CONCLUSION-01`): el guion SHALL describir el modelo con terminología correcta (referencing por `codigo_ine`) y cifras verificables (IXSCAN real, 24 índices).

## Approach

1. Con autorización y coordinación con el agente paralelo: `ensure_indexes()` y verificar `list_indexes()` → 4 índices.
2. `analysis/mongo_indexes.py` sin drop/create; `test_mongo_geo.py` con `mongo_tmp`; ajustar `test_mongo.py`/`test_mongo_indices.py`; `run_analisis_mongo.py` sin demo mutante.
3. Guion y docs con cifras canónicas; regenerar manifiestos; cerrar gate.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `analysis/mongo_indexes.py:107-158` | Modified | `explain_*` read-only |
| `tests/test_mongo_geo.py:13`, `test_mongo.py:290,333`, `test_mongo_indices.py:17,33,49`, `run_analisis_mongo.py:1164-1173` | Modified | mongomock/skipif |
| `docs/guion_defensa.md:9,10,33,44,51`, `guion_defensa_12min.md:36,143-146,175,222` | Modified | IXSCAN real, referencing, 24 índices |
| `incidente_p0_mongo.md:9-13`, `verificacion_dinamica.md:154` | Modified | atribución |
| `docs/`, `README.md`, `AGENT.md`, `project.md`, manifiestos, `verificar_gobernanza.py`, `.env.example` | Modified | barrido P1 |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Restore muta datos | Low | `ensure_indexes()` idempotente |
| Agente paralelo rede_dropa | Med | coordinar y reverificar |
| "Antes" no reporta COLLSCAN | Low | registrar stage real |

## Rollback Plan

`git checkout --` de tests/docs; Mongo no se toca (restauración idempotente).

## Dependencies

Autorización de escritura en Mongo y coordinación con el agente paralelo (`plan_fixes_v9.md:28,221`).

## Success Criteria

- [ ] `anuncios` con 4 índices; `explain` IXSCAN real.
- [ ] `pytest tests -q` verde sin deseleccionar tests.
- [ ] Guion sin cifras erróneas (759/10/14/177/24).
- [ ] Manifiestos consistentes; gate TODO OK.

## Proposal question round

- ¿Escritura en Mongo autorizada para `ensure_indexes()` y coordinación con el agente paralelo?
- ¿Filtro canónico del explain: `20069` (1 doc) o `48020` (8)?
- ¿Barrido P1 incluido o diferido?
- Suposición: no se recarga Mongo ni se tocan datos.
