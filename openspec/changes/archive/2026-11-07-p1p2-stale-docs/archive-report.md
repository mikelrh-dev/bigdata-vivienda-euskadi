# Archive Report: 2026-11-07-p1p2-stale-docs

**Change**: 2026-11-07-p1p2-stale-docs · **Archived to**: `openspec/changes/archive/2026-11-07-p1p2-stale-docs/`
**Date**: 2026-11-07 · **Mode**: openspec
**Verdict at close**: GATE PASS (final state, not a snapshot restatement)

## Reconciliation reason (stale checkboxes)

`tasks.md` checkboxes were still `[ ]` at archive time (verify-report P2-2). Per the
orchestrator's explicit instruction and verify-report proof, all 20 tasks
(1.1–1.5, 2.1–2.8, 3.1–3.4, 4.1–4.3) were marked `[x]` in archive. Evidence:
pytest `177 passed, 1 skipped`; `verificar_fase_datos.py` 354/594 with huella
SHA-256 `c5c498d3edd47cb27acb7f4df6725a7b0aee96800c25d8144c07de7f3d096729`;
manifests raw 354 + silver 188, 0 errors. No task is claimed done beyond this evidence.

## Final gates (literal evidence)

pytest (from verify-report, re-confirmed by manifest gate at archive):

```text
177 passed, 1 skipped in 7.61s
```

verificar_fase_datos.py (literal, exit 1 by design while FAIL 07 is known):

```text
PASS 01 manifest integro 354 ficheros
PASS 02 raw sin derivados legacy limpio
PASS 03 metadata cubre JSON 61/61
PASS 04 inventario cubre CSV 129/129
PASS 05 dim 252 + len5 252
PASS 06 n_anuncios 594/843 real=594
FAIL 07 FAIL conocido paro-cero (Aramaio 0.28, Gaintza 1.45, Usansolo 3.26) 3 ceros documentados con tasa no nula (no enmascarados, sin imputación)
PASS 08 sin brecha ocup-activ
PASS 09 canonico preservado 252 mun
PASS 10 tension cerrada
PASS 11 pytest bateria verde 27 passed in 1.68s
PASS 12 orquestador dry-run []
PASS 13 pob joven 252 + metodo 252
PASS 14 tipologia cerrada
PASS 15 transform no escribe raw solo lectura
PASS 16 cobertura auditable 252 mun
PASS 17 ingestion manifest 354 ficheros (354 ingestion local; 352 raw en HDFS)
PASS 18 nombres estables registrados 5 con ts
RESULTADO: PENDIENTE (ver FAIL)
HUELLA SHA-256: c5c498d3edd47cb27acb7f4df6725a7b0aee96800c25d8144c07de7f3d096729
```

Manifests at archive (literal, exit 0):

```text
OK: C:\Users\mikel\Documents\bigdata-vivienda-euskadi\docs\raw_manifest_sha256.txt (354 entradas)
OK: C:\Users\mikel\Documents\bigdata-vivienda-euskadi\data\procesado\manifest_sha256.txt (188 entradas)
OK: C:\Users\mikel\Documents\bigdata-vivienda-euskadi\docs\raw_manifest_sha256.txt (354 entradas, 0 errores)
OK: C:\Users\mikel\Documents\bigdata-vivienda-euskadi\data\procesado\manifest_sha256.txt (188 entradas, 0 errores)
```

Guardrails at close: 12 PNG únicos (13 emitidos), `data/resultados/g1*` absent,
`Docker Compose HDFS` count 0, stale counts only as explicit history
(845→759→594), `git diff -- data/raw` empty, no Docker, Kafka→HDFS not Mongo.

## Specs synced

| Domain | Action | Details |
|---|---|---|
| extraccion-datos | Updated | 1 added (VERIFICACION-01: 06 594/843, 07 Aramaio 0.28 / Gaintza 1.45 / Usansolo 3.26 alias 354/352, huella) |
| presentacion-de-resultados | Updated | 2 added (BOOTSTRAP-01 67/60/39/37, DOCS-01 759→594 + Nivel/Tier), 1 modified (chart_mapa_tier <2MB, dedupe g1/A1) |
| contrato-reto | Updated | 1 modified (ENTREGABLES-01 Docker contractual), 1 added (ARQUITECTURA-01) |

All pre-existing requirements in each base spec were preserved (verbatim merge,
no requirement deleted or renamed).

## Archive contents

- proposal.md ✅
- specs/ (3 deltas) ✅
- tasks.md ✅ (20/20 complete after reconciled ticks)
- verify-report.md ✅ (GATE PASS, with P2-1 residual g1 fallback tuple noted
  below — non-blocking; the file is deleted and the loop falls through to A1)
- archive-report.md ✅ (this file)

## Residual / next change (non-blocking)

- P2-1: `analysis/run_analisis_mongo.py:423` still lists
  `"g1_esfuerzo_por_territorio.png"` as first fallback in the g1/A1 loop.
  The file is deleted, so behavior is correct (falls through to A1), but the
  stale name remains in code. Remove in a follow-up; it was never part of this
  change's docs-only scope and does NOT block archive.
- Verificar exit 1 with `RESULTADO: PENDIENTE` is the correct signal until
  upstream Lanbide data changes. Do not mask or impute FAIL 07.

## Diff stat (uncommitted working tree at archive time, no commit/push)

Archive moved folder via `mv` (untracked source; `git mv` reports "source
directory is empty" for untracked trees). Mandatory readback — verbatim
`diff -r` between pre-move recursive snapshot and archived folder:

```text
(diff -r output: empty — DIFF-EMPTY OK)
```

An empty `diff -r` is the only passing evidence and it passed: the archived
tree is byte-identical to the source (this report is additive-only).

Uncommitted `git diff --stat` highlights (docs + script + SVG + 3 base specs;
manifests + tasks ticks land as working-tree modifications per constraints):

```text
 47 files changed, 2354 insertions(+), 653 deletions(-)
```

Plus: 3 newly created SVGs (chart_effort_vs_n, chart_mapa_tier, chart_tierB_range),
g1/A1 dedupe (12 PNGs remain), raw manifest 354 + silver manifest 188 (0 errors).
No Docker files; no `data/raw` diffs; no commit/push per constraints.
