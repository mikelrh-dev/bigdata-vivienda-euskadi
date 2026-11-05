# Proposal: bloque-3-mongo-pymongo

## Intent

Cerrar RA3/Tema 8 (PLAN_10 8-15) con evidencia ejecutada y pegada. Hoy explain, §5, backups/geo, CRUD y pipelines existen en código pero `docs/modelo_mongodb.md` es parcial y las 7 preguntas siguen SHOULD.

## Scope

### In Scope

- 8. Índices: explain COLLSCAN y IXSCAN con `nReturned`/`totalDocsExamined=1` (ESR, geo, multikey, parcial) en `docs/modelo_mongodb.md`. Lectura pura.
- 9. Modelado: 7 preguntas docx §5 literales en `docs/modelo_mongodb.md`.
- 10. Backups/geo: `municipios` e `indicadores` backup + geo 424 desde silver; lectura pura (15 colecciones), sin tocar prod.
- 11. `validar_renta` en `transform/run_all.py` o justificación firmada; pytest 130.
- 12. `clean_mongo`: `$unset` + `deleted_count`; canónica anuncio-por-municipio sin romper 759.
- 13. Consistencia: commit/abort en `vivienda_euskadi_test` o READ justificado (§11); prod intacta por defecto.
- 14. Excepts: `_money` y `ensure_indexes` a `TypeError`/`ValueError` con log.
- 15. Aggregation: 5 pipelines (`indicadores_municipio`, `alquiler_por_municipio`, `modalidades`, `accesibilidad_extendida`, `vpo_por_municipio`) a CSV canónico, sin duplicar esfuerzo.

### Out of Scope

- Sin tocar `data/raw` local ni raw HDFS; sin subir procesado (pendiente confirmación profesora).
- Sin tocar prod por defecto (solo `vivienda_euskadi_test`); sin carpeta nueva.
- Bloque 4 (16-18) fuera.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- mongodb-y-analisis: INDICES-01, MODELO-01, TRANSACCIONES-01, LIMPIEZA-01, PYMONGO-01, AGREGACION-01: SHOULD→SHALL (explain, §5, commit/abort, CSV).

## Approach

Cambios mínimos en `storage/`, `analysis/`, `transform/`, tests; evidencia en `docs/modelo_mongodb.md`; todo comando VM/Mongo en `docs/trazabilidad_vm.md`; gate Bloque 3.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `docs/modelo_mongodb.md` | Modified | Explain, 7 preguntas, backups, geo 424 |
| `storage/load_mongo.py`, `analysis/mongo_indexes.py` | Modified | `_money`, `ensure_indexes`: excepts tipados + log |
| `storage/clean_mongo.py` | Modified | `$unset`, `deleted_count`, función canónica |
| `transform/run_all.py` | Modified | Paso `validar_renta` o justificación firmada |
| `analysis/mongo_aggregations.py` | Modified | 5 pipelines a CSV canónico |
| `tests/test_mongo*.py` | Modified | CRUD con contadores, commit/abort en test |
| `docs/trazabilidad_vm.md` | Modified | Entrada por comando VM/Mongo |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Transacción exige replica set (standalone no la soporta) | High | Test DB; si no aplica, justificación READ (§11) |
| Tocar prod por accidente | High | Prod intacta por defecto (`MONGO_ALLOW_DESTRUCTIVE=1` para mutar) |
| `$unset`/`deleted_count` altera conteos 759 | Med | Verificar 759 antes/después |
| Excepts tipados ocultan errores | Med | Log + pytest 130 verde |
| `validar_renta` alarga `run_all` | Low | Justificación firmada (PLAN_10) |

## Rollback Plan

Revertir código (sin commit); regenerar CSV; test DB desechable; raw/HDFS intactos.

## Dependencies

- MongoDB localhost:27017 (`vivienda_euskadi` 759 / `vivienda_euskadi_test`).
- PLAN_10 8-15; Bloque 2 verificado (759, gate `e32c3d3…faf25`); pytest 130.

## Success Criteria

- [ ] `pytest tests` 130 passed.
- [ ] Explain COLLSCAN y IXSCAN con `totalDocsExamined=1` en `docs/modelo_mongodb.md`.
- [ ] 8 pipelines `$group`/`$lookup`/`$unwind`; 5 CSV canónicos.
- [ ] CRUD con `matched`/`modified`/`deleted` en test.
- [ ] Commit/abort en test sin tocar prod por defecto.
- [ ] `git status` sin `data/raw`; procesado sin subir a HDFS.
