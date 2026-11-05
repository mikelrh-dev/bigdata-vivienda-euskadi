# Tasks: bloque-3-mongo-pymongo

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 80-150 (solo docs + excepts tipados + exportador CSV) |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single PR (Bloque 3) |
| Delivery strategy | single-pr |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: single-pr
400-line budget risk: Low

Regla transversal: cada comando VM/Mongo se registra en `docs/trazabilidad_vm.md` (Fecha/Objetivo/Maquina/Comando/Salida/Conclusión). Cero escrituras en `data/raw` ni HDFS (verificar con `git status --short data/raw` vacío).

## Phase 1: Índices y modelado (PLAN_10 8-9)

- [x] 1.1 `analysis/mongo_indexes.py`: ejecutar `explain_before_after()` sin índice ESR y con él; guardar salida (COLLSCAN antes, IXSCAN después, `nReturned`, `totalDocsExamined=1`).
  - ✅ `python analysis/run_analisis_mongo.py` muestra `COLLSCAN → IXSCAN` con `totalDocsExamined=1`.
- [x] 1.2 `docs/modelo_mongodb.md`: anexar evidencia explain de 1.1 (consulta `ubicacion.codigo_ine=48001` + `modalidad=larga_estancia` + `precio_eur $lte Decimal128(1000)`, índice ESR `{ubicacion.codigo_ine:1, modalidad:1, precio_eur:1}`).
  - ✅ `grep -n "totalDocsExamined=1" docs/modelo_mongodb.md` no vacío.
- [x] 1.3 `docs/modelo_mongodb.md`: documentar geo 2dsphere sparse, multikey `equipamiento` y parcial, cada uno con su consulta real justificativa; parcial sin consulta real queda como evaluado/rechazado.
  - ✅ `grep -c "2dsphere\|multikey\|parcial" docs/modelo_mongodb.md` ≥ 3.
- [x] 1.4 `docs/modelo_mongodb.md`: volcar las 7 preguntas docx §5 literales con respuesta justificada (MODELO-01).
  - ✅ `grep -c "^[0-9]\." docs/modelo_mongodb.md` ≥ 7 en la sección §5.

## Phase 2: Backups/geo y validar_renta (PLAN_10 10-11)

- [x] 2.1 `docs/trazabilidad_vm.md` + Mongo shell: listing `db.getCollectionNames()` de `vivienda_euskadi` (lectura pura); registrar 15 colecciones incl. `municipios__backup` e `indicadores__backup`.
  - ✅ `mongosh --quiet vivienda_euskadi --eval 'db.getCollectionNames().length'` → `15`.
- [x] 2.2 `docs/modelo_mongodb.md`: documentar backups vía `replace_collection` (staging + `__backup` + rename, nunca `drop()` directo) y geo 424 Point reales / resto `None` desde silver.
  - ✅ `mongosh --quiet vivienda_euskadi --eval 'db.anuncios.countDocuments({"ubicacion.geo":{"$type":"object"}})'` → `424`.
- [x] 2.3 `transform/run_all.py:249`: firmar justificación de exclusión de `validar_renta.py` en `EXCLUIDOS` (no es transformación; QA bajo demanda), sin añadir paso al orquestador.
  - ✅ `grep -n -A3 "validar_renta" transform/run_all.py` muestra justificación firmada.
- [x] 2.4 Gate orquestador: suite completa verde tras 2.3.
  - ✅ `pytest tests -q` → `130 passed`.

## Phase 3: Limpieza, transacciones y excepts (PLAN_10 12-14)

- [x] 3.1 `storage/clean_mongo.py`: función canónica única con `update_many(..., {"$unset": {...}})` que retorna `matched_count`/`modified_count`/`deleted_count`; mismo contrato en ambas colecciones.
  - ✅ `python -m pytest tests/test_mongo_pymongo_pro.py -q` pasa y conteo 759 intacto.
- [x] 3.2 `docs/modelo_mongodb.md` §11: documentar READ justificado en standalone (sin replica set: no hay commit/abort multidocumento) + atomicidad documental de `marcar_calidad_municipio`.
  - ✅ `grep -n "§11\|READ" docs/modelo_mongodb.md` no vacío.
- [x] 3.3 `tests/test_mongo_consistencia.py`: sonda commit/abort solo en `vivienda_euskadi_test`; abortar deja conteo 759 prod invariante (prod intacta por defecto).
  - ✅ `python -m pytest tests/test_mongo_consistencia.py -q` pasa; `MONGO_ALLOW_DESTRUCTIVE` sin definir.
- [x] 3.4 `storage/load_mongo.py` (`_money`, `_to_decimal`) y `analysis/mongo_indexes.py` (`drop_demo_index`, `explain_*`): sustituir `except Exception: pass` por `except (TypeError, ValueError)` con log; `DuplicateKeyError` sigue propagándose.
  - ✅ `python -m pytest tests/test_mongo_pymongo_pro.py tests/test_mongo_indices.py -q` pasa.

## Phase 4: Agregación y gate final (PLAN_10 15)

- [x] 4.1 `analysis/mongo_aggregations.py` + `analysis/run_analisis_mongo.py`: generalizar `exportar_tres_csv` a 5 CSV canónicos reutilizando los 8 pipelines (`$group`/`$lookup`/`$unwind`), sin reimplementar agregaciones.
  - ✅ `python analysis/run_analisis_mongo.py` genera 5 CSV con recuentos 252/252/2 + 2 nuevos.
- [x] 4.2 Gate Bloque 3: suite completa + `git status` limpio en `data/raw` (sin escrituras HDFS).
  - ✅ `pytest tests -q` → `130 passed` y `git status --short data/raw` vacío.
