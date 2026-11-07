# Archive Report: Datos P0/P1 — outliers, staleness, paro y capas

**Change:** `2026-11-07-datos-p0-p1-staleness-paro-capas`
**Mode:** openspec
**Date:** 2026-11-07
**Verdict (verify):** GATE PASS

## Final state (at close)

- **pytest:** `177 passed, 1 skipped` (174 previas + 3 dedup). Evidencia literal de `verify-report.md` GATE (1).
- **Huella doble `run_analisis_mongo.py`:** `f26264b6c9ec024a27b36a99546dffdc71bb4cdd5aff61fc8519e15b17fa19d0` (prefijo `f26264b6`, sufijo `...19d0`), doble ejecución con SHA idéntico, 13 PNG + `mongo_*.csv` (7 ficheros: accesibilidad, alquiler, esfuerzo, modalidades, tier_confianza, vpo, vpo_terminadas — el delta dice 6; ver nota). Evidencia literal de GATE (2).
- **Manifests (regenerados en archive):** `extract/generar_manifest.py --write` → raw `354 entradas` + silver `188 entradas`; `--verify` → `0 errores` en ambos (354/188 OK, sin errores).
- **Mongo (GATE 3):** `anuncios 594`, `municipios 252`, `indicadores 252`, `alquiler_municipal 252`, `udalmap_empleo 252`; paro `252/252` (01003 0.28, 20037 1.45, 48916 3.26), `is_imputed true 0`; `precio_m2>50 0`, `precio_m2<3 0`; mediana winsorizada no nula 60; ranking `n_anuncios.min() >= 30`.
- **Tasks:** 17/17 checked, 0 sin marcar en `tasks.md` (Task Completion Gate PASS, sin reconciliación).
- **Restricciones:** sin Docker; HDFS solo raw; Kafka→HDFS, no Kafka→Mongo; `hdfs_utils.py` 0 changes; `data/raw` intacto salvo re-extract 18/21. Sin commit/push.
- **Review:** `reviewGate` ausente → archive procede bajo política ordinaria del repo.

## Specs synced (base = source of truth)

| Domain | Action | Details |
|--------|--------|---------|
| extraccion-datos | Updated | MODIFIED COMPLEMENTARIOS-01 (paro 252/252, M5) + ADDED OUTLIER-01 (M1) + ADDED DEDUP-01 (M6). Preservados: salarios/población base, PYTHON-01, GATE-JOIN-01, EXTRACCION-01/02, FORMATO-01, pisos (EXTRACCION-01 ubicación, PISOS-01, PISOS-02) |
| mongodb-y-analisis | Updated | MODIFIED AGREGACION-01 (mediana winsorizada + exclusión IQR, M1; preservados escenarios tier 4/3/57/188 y edge n_precio=0) + MODIFIED PISOS-04 (paro 252/252, M5; preservado Eustat 252/252) + ADDED CAPAS-01 (159/93/252, M7) |
| presentacion-de-resultados | Updated | MODIFIED CONCLUSION-01 Tiers (conciliación 62/252 vs n_precio=7 + ranking n>=30, M2/M3; preservada tabla A/B/C/D) + MODIFIED RESPUESTA-01 (sync 759→594/188/204, M4; preservados 4 robustos + matriz O1-O4) |

Requisitos exigidos presentes en base: OUTLIER-01, DEDUP-01, COMPLEMENTARIOS-01 M5, AGREGACION-01, CAPAS-01, CONCLUSION-01, RESPUESTA-01. Ningún requisito fuera del delta se eliminó.

## Gates finales

- Task Completion Gate: PASS (17/17 ticks, 0 `- [ ]`).
- Native Review Receipt Gate: `reviewGate` ausente → PASS (sin receipt que leer/bloquear).
- Mechanical Copy Contract: move vía shell `git mv` (fallback `mv`) con snapshot `cp -R` + readback `diff -r`. Salida verbatim: vacía (sin diferencias). `DIFF-EMPTY:PASS`. Source `openspec/changes/{change}` desaparecido tras el move.
- Verify GATE PASS: pytest 177/1 + SHA f26264b6 + manifests 354/188 + PARO 252 + ranking n>=30.

## Notas (jerarquía Final-State Authority)

- El delta dice «6 `mongo_*.csv`»; la evidencia de GATE (2) (snapshot intermedio) lista 7. El archive no altera el delta: registra 7 como ficheros existentes según verify, sin rescribir la spec.
- `verify-report.md` es snapshot intermedio (GATE PASS con P2 no bloqueantes). Los números finales de este report salen del gate + regeneración de manifests en archive (354/188, 0 errores).
- Trazabilidad: Gómez `verify-report.md` GATE (1)–(3) + regeneración local archive `--write/--verify` OK.

> Las contradicciones de snapshot intermedio no se resuelven retroeditando la spec. Directiva archive.

## Diff stat (base specs + manifests)

```
 docs/raw_manifest_sha256.txt                      |   4 +-
 openspec/specs/extraccion-datos/spec.md           | 100 ++++++++++++++++-
 openspec/specs/mongodb-y-analisis/spec.md         | 128 ++++++++++++++++++++--
 openspec/specs/presentacion-de-resultados/spec.md |  91 +++++++++++++--
 4 files changed, 304 insertions(+), 19 deletions(-)
```

Incluye el sync previo pisos 2026-11-07 (no commiteado) + este sync P0/P1. `data/procesado/manifest_sha256.txt` no modificado en este archive (ya 188 OK tras apply).

## Archive contents

- proposal.md ✅
- specs/ (extraccion-datos, mongodb-y-analisis, presentacion-de-resultados) ✅
- tasks.md ✅ (17/17)
- verify-report.md ✅ (GATE PASS)
- archive-report.md ✅ (este fichero, aditivo)
