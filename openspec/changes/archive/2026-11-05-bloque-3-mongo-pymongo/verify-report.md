```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:31a2ed898308d15d4ebe145eb8addbb5d129599c2af1b3a3c09e98725564ed79
verdict: pass
blockers: 0
critical_findings: 0
requirements: 8/8
scenarios: 9/9
test_command: .venv/Scripts/python.exe -m pytest tests -q
test_exit_code: 0
test_output_hash: sha256:58ad574d5ea532635eca4de88c68fbf73c874d6211483685e44ba74caeab114a
build_command: none
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Verification Report

**Change**: bloque-3-mongo-pymongo
**Version**: N/A
**Mode**: Standard (strict_tdd: false; no TDD module)
**Date**: 2026-11-05
**Branch/HEAD**: master @ 30de15c7af6ab6e921ee85896a9aee25b0a9b2b3
**Gate**: pytest 130, explain COLLSCAN>IXSCAN totalDocsExamined 1, 8 pipelines, CRUD matched/modified/deleted, consistencia test sin tocar prod por defecto

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 14 |
| Tasks complete | 14 |
| Tasks incomplete | 0 |

`tasks.md` has 14 `- [x]` and 0 `- [ ]`. Verified via `grep -c "^- \[x\]"` = 14 and `grep "^- \[ \]"` empty. The only unchecked boxes in the change are the 2 Open Questions in `design.md` and the 6 Success Criteria in `proposal.md`, which are not tasks.

### Build & Tests Execution
**Build**: ➖ Not available (Python repo, no build step; syntax/import surface covered by pytest collection).

**Tests**: ✅ 130 passed, 0 failed, 0 skipped.
```text
.venv/Scripts/python.exe -m pytest tests -q
........................................................................ [ 55%]
..........................................................               [100%]
130 passed in 6.55s
exit: 0
test_output_hash: sha256:58ad574d5ea532635eca4de88c68fbf73c874d6211483685e44ba74caeab114a (183 bytes, elapsed time varies between runs)
```
Repeated runs in this verification session: 6.83s, 7.15s and 6.55s, all `130 passed`, exit 0. No `MONGO_ALLOW_DESTRUCTIVE` set; tests use `vivienda_euskadi_test` and read-only prod counts.

**Coverage**: ➖ Not available (no coverage gate configured; no coverage command run)

### Read-only evidence (as ordered)
```text
wc -l docs/raw_manifest_sha256.txt data/procesado/manifest_sha256.txt
  353 docs/raw_manifest_sha256.txt
  184 data/procesado/manifest_sha256.txt
  537 total

grep -n "totalDocsExamined=1" docs/modelo_mongodb.md
130:- Después (con índice ESR): `IXSCAN`, `nReturned=1`, `totalDocsExamined=1`, `totalKeysExamined=1`.
132:Esto es `COLLSCAN -> IXSCAN` con `totalDocsExamined=1` tras el índice ESR...

mongosh --quiet vivienda_euskadi --eval 'db.getCollectionNames().length'
15

grep -n "except.*TypeError" analysis/mongo_indexes.py storage/load_mongo.py storage/clean_mongo.py
analysis/mongo_indexes.py:106:    except (TypeError, ValueError) as exc:
analysis/mongo_indexes.py:119:        except (TypeError, ValueError, InvalidOperation) as exc:
analysis/mongo_indexes.py:147:    except (TypeError, ValueError) as exc:
storage/load_mongo.py:47:    except (TypeError, ValueError, InvalidOperation) as exc:
storage/clean_mongo.py:369:    except (TypeError, ValueError, InvalidOperation) as exc:

git status --short data/raw
(empty)

git status --short
 M README.md
 M analysis/mongo_indexes.py
 M analysis/run_analisis_mongo.py
 M docs/README.md
 M docs/modelo_mongodb.md
 M storage/clean_mongo.py
 M storage/kafka_producer.py
 M storage/load_mongo.py
 M tests/test_kafka.py
 M tests/test_mongo_consistencia.py
 M tests/test_mongo_pymongo_pro.py
 M transform/run_all.py
 M transform/validar_renta.py
?? docs/analisis_vault_vs_rubrica.md
?? docs/trazabilidad_vm.md
?? openspec/changes/bloque-2-integracion-hdfs-kafka/
?? openspec/changes/bloque-3-mongo-pymongo/
?? plan/PLAN_10.md
?? scripts/gate_bloque2.py
?? scripts/hdfs_recuperacion_un_fichero.py
?? scripts/publish_adapter.py
?? scripts/upload_procesado.py

git diff --stat
 README.md                        |  1 +
 analysis/mongo_indexes.py        | 22 ++++++++----
 analysis/run_analisis_mongo.py   | 64 ++++++++++++++++++++++++++++-----
 docs/README.md                   |  4 +++
 docs/modelo_mongodb.md           | 78 ++++++++++++++++++++++++++++++++++++++++
 storage/clean_mongo.py           | 45 ++++++++++++++++++++++-
 storage/kafka_producer.py        | 25 +++++++------
 storage/load_mongo.py            | 11 ++++--
 tests/test_kafka.py              | 22 ++++++++++--
 tests/test_mongo_consistencia.py | 28 +++++++++++++++
 tests/test_mongo_pymongo_pro.py  | 49 +++++++++++++++++++++++++
 transform/run_all.py             |  2 +-
 transform/validar_renta.py       |  2 +-
 13 files changed, 319 insertions(+), 34 deletions(-)
```

Additional read-only live checks (same session):
```text
mongosh: ANUNCIOS 759, MUNICIPIOS 252, INDICADORES 252, MUN_BACKUP 252, IND_BACKUP 252, GEO424 424
wc -l data/resultados/mongo_*.csv:
  253 mongo_accesibilidad_extendida.csv (252+header)
  253 mongo_alquiler_por_municipio.csv
  253 mongo_esfuerzo_por_municipio.csv
    3 mongo_modalidades.csv (2+header)
  323 mongo_vpo_por_municipio.csv (322+header)
grep "^def pipeline" analysis/mongo_aggregations.py -> 8
ls data/ -> _hdfs_state procesado raw resultados (no carpeta nueva)
git diff -- data/raw data/procesado docs/raw_manifest_sha256.txt data/procesado/manifest_sha256.txt -> empty
```

### Spec Compliance Matrix
| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| INDICES-01 | Before/after con totalDocsExamined=1 | `tests/test_mongo_indices.py > test_indexes_explain_totalDocsExamined` | ✅ COMPLIANT |
| INDICES-01 | Geo, multikey y parcial documentados | `docs/modelo_mongodb.md` § Índices geo/multikey/parcial + test above | ✅ COMPLIANT |
| MODELO-01 | Preguntas literales en el doc | `docs/modelo_mongodb.md` §5 (7 literales) + `tests/test_mongo*.py` live counts | ✅ COMPLIANT |
| RESPALDO-01 | Backups, geo y listing | `tests/test_mongo.py` / `test_mongo_geo.py` + mongosh live 15/759/252/424 | ✅ COMPLIANT |
| RENTA-01 | Integración o justificación | `tests/test_mongo_orquestador.py` + `transform/run_all.py:255` + `pytest tests` 130 | ✅ COMPLIANT |
| LIMPIEZA-01 | Limpieza con contadores | `tests/test_mongo_pymongo_pro.py > test_anuncios_objectid` (canónica $unset) | ✅ COMPLIANT |
| TRANSACCIONES-01 | Commit/abort en test o READ | `tests/test_mongo_consistencia.py > test_atomicidad_documental` + `docs/modelo_mongodb.md` §11 | ✅ COMPLIANT |
| PYMONGO-01 | Errores no silenciados y CRUD con contadores | `tests/test_mongo_pymongo_pro.py` + `test_mongo_consistencia.py > test_load_all_no_silencia_indices` | ✅ COMPLIANT |
| AGREGACION-01 | Cinco CSV canónicos | `tests/test_mongo_pipeline.py` + `run_analisis_mongo.py` + 5 CSV on disk 252/252/2/252/322 | ✅ COMPLIANT |

**Compliance summary**: 9/9 scenarios compliant. 8/8 requirements covered by a passing test plus static evidence in `docs/modelo_mongodb.md` and source.

### Correctness (Static Evidence)
| Requirement | Status | Notes |
|------------|--------|-------|
| INDICES-01 | ✅ Implemented | `analysis/mongo_indexes.py:explain_before_after` / `_explain` with `explain(executionStats)`; modelo lines 130/132 + `run_analisis_mongo.py:234-235` print before/after; test asserts COLLSCAN→IXSCAN and totals. |
| MODELO-01 | ✅ Implemented | `docs/modelo_mongodb.md` §5 lines 148-154: 7 literal questions with justified answers; embedding/referencing decision justified. See WARNING W1 on grep pattern only. |
| RESPALDO-01 | ✅ Implemented | `storage/mongo.py:replace_collection` staging+`__backup`+rename, no direct `drop()` on prod; listing 15 incl. `municipios__backup`/`indicadores__backup`; geo 424 Point, rest `None` from silver. |
| RENTA-01 | ✅ Implemented | `transform/run_all.py:255` signed justification (not ETL silver, QA on demand, preserves manifest 353/184 and gate 130); no orchestrator step added. |
| LIMPIEZA-01 | ✅ Implemented | `storage/clean_mongo.py:clean_obsolete_fields` canonical `update_many(..., {"$unset": {...}})` returning `matched_count`/`modified_count`/`deleted_count` (`deleted_count=0`, 759 intact) in both collections. |
| TRANSACCIONES-01 | ✅ Implemented | READ justified §11 (standalone, no replica set → no multidocument commit/abort) + documentary atomicity via `marcar_calidad_municipio` (`find_one_and_update` + `ReturnDocument.AFTER`); abort probe ends `rechazado-standalone`/`abort-revertido`, prod 759 invariant, `MONGO_ALLOW_DESTRUCTIVE` unset. |
| PYMONGO-01 | ✅ Implemented | `_money` (`load_mongo.py:47`), `_to_decimal` (`clean_mongo.py:369`), `drop_demo_index`/`explain_*` (`mongo_indexes.py:106,119,147`) use `except (TypeError, ValueError[, InvalidOperation])` with `logger.warning`; `ensure_indexes` has no swallow, `load_all` re-raises `RuntimeError` with `logger.exception`, `DuplicateKeyError` propagates (test). |
| AGREGACION-01 | ✅ Implemented | 8 pipelines reused (`$group`/`$lookup`/`$unwind`), generalized `exportar_cinco_csv`/`exportar_csv` + `EXPORTS_5` with `exportar_tres_csv` delegating; 5 CSV in `data/resultados/` with counts 252/252/2/252/322. |

### Coherence (Design)
| Decision | Followed? | Notes |
|----------|-----------|-------|
| Índices medidos (COLLSCAN→IXSCAN totalDocsExamined=1, geo/multikey/parcial only if measured) | ✅ Yes | ESR measured; geo 2dsphere sparse + multikey documented with real queries; parcial evaluated/rejected (no real query) — matches Known Limits and Open Question. |
| Backups replace_collection (staging+backup+rename, no drop) | ✅ Yes | Documented and live (backups 252/252). |
| validar_renta justified exclusion | ✅ Yes | Signed at `run_all.py:249` (now line 255). |
| Limpieza canonical $unset+deleted_count, 759 intact | ✅ Yes | Test-only, prod 759 verified live. |
| Transacciones READ §11 + documentary atomicity | ✅ Yes | Standalone, no forced replica set. |
| Excepts typed + log | ✅ Yes | Scoped functions fixed; see WARNING W2 for residual generic excepts outside scope. |
| Agregación 5 CSV reusing 8 pipelines | ✅ Yes | No reimplementation in exporter. |
| HDFS/raw read-only, no new folder, no procesado upload | ✅ Yes | Manifests 353/184, `git status data/raw` empty, `ls data/` no new folder, traces show LISTSTATUS only, upload refused without `--dry-run`. |

### Trazabilidad VM (Bloque 3)
`docs/trazabilidad_vm.md` contains 4 Bloque 3 entries (lines 1377, 1401, 1422, 1437), each with the 6 required fields Fecha/Objetivo/Máquina/Comando/Salida/Conclusión:
- 1377 explain COLLSCAN→IXSCAN totalDocsExamined 1 (tarea 1.1, INDICES-01)
- 1401 listings 15 colecciones + geo 424 (tareas 2.1-2.2, RESPALDO-01)
- 1422 limpieza canónica $unset + commit/abort solo test (tareas 3.1/3.3, LIMPIEZA-01/TRANSACCIONES-01)
- 1437 gate final 130 passed, manifest 353/184, data/raw intacto (tareas 2.4/4.2)
✅ Compliant with the transversal rule.

### Issues Found
**CRITICAL**: None

**WARNING**:
- W1 (pattern, not content): The ordered command `grep "^ [0-9]\."` (with a leading space) returns 0 matches in `docs/modelo_mongodb.md`. The file numbers §5 questions as `1. ...` at column 0 (lines 148-154), so the canonical `tasks.md` pattern `grep -c "^[0-9]\."` returns 7, and all 7 literal questions are present. The requirement MODELO-01 is satisfied; only the delegated grep literal is off by a space. No code/doc change required; future verifications should use `^[0-9]\.`.
- W2 (residual generic excepts outside scoped functions): `storage/load_mongo.py:59,87` keep `except Exception: return {}` in `_lookup_csv` / `_lookup_fotocasa_geo` (CSV fallback, not silent `pass`) and `:568` logs + re-raises `RuntimeError` for `ensure_indexes`. These are outside the PYMONGO-01 scoped functions (`_money`, `_to_decimal`, `drop_demo_index`, `explain_*`, `ensure_indexes`) and do not reintroduce silent swallowing. No silent `except Exception: pass` remains in the three files. Optional future tightening (e.g. `(OSError, UnicodeDecodeError, EmptyDataError)`) is a suggestion, not a blocker.
- W3 (working-tree scope): `git diff --stat` shows 319 insertions across 13 files, including files outside the strict Bloque 3 file list (`README.md`, `docs/README.md`, `storage/kafka_producer.py`, `tests/test_kafka.py`, `transform/validar_renta.py` docstring). All are Bloque 2 carry-over / RA4 notes already traced in `trazabilidad_vm.md`; none touch `data/raw`, HDFS raw, manifests, or add a new folder. No commit (`git add`/`commit`) was performed, as ordered. Parent should commit with the correct block attribution.

**SUGGESTION**:
- S1: Resolve both Open Questions when possible: (a) parcial index — currently documented as evaluated/rejected, which is allowed; revisit only if a real measurable query appears. (b) profesora confirmation for uploading procesado to HDFS — still pending; Bloque 3 correctly does not upload.
- S2: `data/resultados/` CSVs are generated (not tracked in `git status`); keep regenerating via `python analysis/run_analisis_mongo.py` rather than hand-editing, as the traces do.

### Risks (remaining)
- Standalone MongoDB has no replica set: multidocument commit/abort is rejected; the design accepts READ §11 + documentary atomicity. Future replica-set deployments would need a real commit/abort test.
- Geo coverage is 424/759 by silver availability; the rest is `None` by design (sparse 2dsphere). Inventing coordinates would be a regression.
- `$unset` canonical cleanup is test-only; running it on prod would still preserve 759 (`deleted_count=0`) but is guarded by `MONGO_ALLOW_DESTRUCTIVE` and was not invoked on prod in this gate.
- Typed excepts with log are narrow by design; unexpected `DuplicateKeyError` still propagates (intended) — callers must handle it explicitly.
- HDFS limit respected in this verification: no writes to `data/raw` local or HDFS raw, no new folder, no procesado upload. The pending teacher confirmation remains the only HDFS gate for future upload.

### Verdict
**PASS WITH WARNINGS** — 14/14 tasks complete, 130 passed, 9/9 scenarios compliant across 8/8 requirements, HDFS/raw limit respected (manifests 353/184, `git status data/raw` empty, prod 759 invariant). Warnings W1-W3 are pattern/scope notes only and do not block Bloque 3 closure; no CRITICAL findings.

*Validator note*: `gentle-ai sdd-verify-validate` is not available in the installed gentle-ai 4.0.0 (`unknown command`), so no strict admission run was possible. This report was built from direct artifact inspection plus executed read-only evidence (pytest, mongosh, grep, git) and persisted per the ordered deliverable `openspec/changes/bloque-3-mongo-pymongo/verify-report.md`. No code was implemented and no `git add`/`commit` was performed.
