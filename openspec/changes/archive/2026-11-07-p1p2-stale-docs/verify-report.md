# Verification Report: 2026-11-07-p1p2-stale-docs (P1/P2 stale docs)

Change: `2026-11-07-p1p2-stale-docs` · Mode: openspec · Date: 2026-11-07
Artifacts reviewed: `proposal.md`, `specs/extraccion-datos/spec.md` (VERIFICACION-01),
`specs/presentacion-de-resultados/spec.md` (BOOTSTRAP-01, DOCS-01, chart_mapa_tier),
`specs/contrato-reto/spec.md` (ENTREGABLES-01, ARQUITECTURA-01), `tasks.md`.
No code touched during verification.

## GATE verdict: PASS

The declared gate (pytest + `verificar_fase_datos.py` + stale sweep + map/PNG/manifest checks)
reproduces exactly the expected results, including the documented known FAIL 07
(not masked, no imputation). One process note (tasks.md checkboxes still `[ ]`)
and one minor residual reference (g1 fallback tuple in `run_analisis_mongo.py`)
are recorded below as P2/warnings; neither breaks the gate.

## 1. Tests — PASS

Command: `.venv/Scripts/python -m pytest tests -q` → exit 0.

```text
........................................................................ [ 40%]
........................................................................ [ 80%]
...........s......................                                       [100%]
177 passed, 1 skipped in 7.61s
```

Matches expected 177 passed / 1 skipped (178 collected / battery green with the
new 177 figure in docs).

## 2. `scripts/verificar_fase_datos.py` — PASS (with known FAIL 07, by design)

Command: `.venv/Scripts/python scripts/verificar_fase_datos.py` → exit 1
(expected: FAIL 07 is a documented known failure, not masked).

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

- VERIFICACION-01 / 06: `06 n_anuncios 594/843 real=594` — PASS with real=594.
- VERIFICACION-01 / 07: FAIL conocido names the three paro-zero non-null cases
  (Aramaio 0.28, Gaintza 1.45, Usansolo 3.26) and states they are not masked and
  no comarcal value is imputed.
- Check 17 alias: `354 ingestion local; 352 raw en HDFS` — local ingestion count vs
  canonical HDFS raw count distinguished (354/352), check PASS.
- Huella SHA-256 reproducible printed: `c5c498d3edd47cb27acb7f4df6725a7b0aee96800c25d8144c07de7f3d096729`.
- `RESULTADO: PENDIENTE (ver FAIL)` correctly distinguishes PENDIENTE from OK
  while 07 is FAIL conocido.

## 3. Spec compliance

| Spec | Requirement | Evidence | Status |
|---|---|---|---|
| extraccion-datos VERIFICACION-01 | 06 `594/843`, `real=594`; `grep -c "759/843"` → 0 | `PASS 06 n_anuncios 594/843 real=594`; stale sweep below shows no `759` in the script | COMPLIANT |
| extraccion-datos VERIFICACION-01 | FAIL 07 names Aramaio 0.28 / Gaintza 1.45 / Usansolo 3.26, not masked, no imputation | Literal FAIL 07 line above | COMPLIANT |
| extraccion-datos VERIFICACION-01 | PASS prints `RESULTADO` + SHA-256 huella | `RESULTADO: PENDIENTE` + `HUELLA SHA-256: c5c498d3…` | COMPLIANT |
| presentacion-de-resultados BOOTSTRAP-01 | `n_anuncios_larga_vivienda` 67/60/39/37, IC95 Bilbao 33.75–40.95, Getxo 27.54–31.77 ≠ Tier 204/126/50/39 | `data/resultados/bootstrap_robustos.csv`: Bilbao 67, Donostia 60, Getxo 39, Vitoria-Gasteiz 37; IC95 Bilbao 33.75–40.95, Getxo 27.54–31.77; Tier values 204/126/50/39 in metodologia/guiones | COMPLIANT |
| presentacion-de-resultados DOCS-01 | 759→594 in `build_presentacion.py` + `docs/presentacion/README.md` | `grep -c "594"` = 1 in each; no `759` as current figure in either | COMPLIANT |
| presentacion-de-resultados DOCS-01 | Orthogonal Nivel/Tier phrase (Nivel 4/54/194 vs Tier 4/3/57/188) | Present in `docs/metodologia.md:17`, `docs/guion_defensa.md:16`, `docs/guion_defensa_12min.md:114` | COMPLIANT |
| presentacion-de-resultados chart_mapa_tier | SVG <2 MB, dedupe g1/A1, 252/252 intact | SVG 151.657–152.005 bytes (149 KB) <2 MB; texts: `Tier por municipio (A/B/C/D) · 252/252 clasificados`, `Tier A · 4`, `Tier B · 3`, `Tier C · 57`, `Tier D · 188`, `oficial 159 (borde sólido)`, `IDW 93 (borde discontinuo)`, `contexto 252`, `252 contextual sobre 159`. 12 unique PNGs, no hash duplicates, `g1*` absent | COMPLIANT (see P2-1 residual reference) |
| contrato-reto ENTREGABLES-01 | Contractual Docker text only; `grep -c "Docker Compose HDFS"` → 0 | Only hits are the contractual phrase in `README.md:100` and `AGENT.md:4`; count = 0; no `Dockerfile`/`docker-compose.yml` | COMPLIANT |
| contrato-reto ARQUITECTURA-01 | No Docker; HDFS raw only; Kafka→HDFS never Mongo; no comarcal/IDW as municipal; orthogonal Nivel/Tier | README: Kafka producer of manifest + consumer uploads to HDFS, `Kafka no escribe en Mongo` (2 explicit statements); HDFS raw only; orthogonal phrase present; no Dockerfile | COMPLIANT |

## 4. Stale sweep (P1-2 + P2) — only explicit history remains

`grep -rn "759\|174\|187\|249\|354"` over `README.md`, `AGENT.md`,
`docs/metodologia.md`, both guiones, `docs/presentacion/build_presentacion.py`,
`docs/presentacion/README.md` returns only 2 hits, both explicit history:

```text
AGENT.md:18: ... (759>0, cifra histórica pre-v5; vigente 594/843).
docs/metodologia.md:56: ... cadena histórica 845→759→594 ...
```

No stale `174/187/249/354` as current figures. `grep -in "docker" README.md AGENT.md`
returns only the contractual phrase; `grep -c "Docker Compose HDFS" README.md` = 0.

## 5. PNG / manifests / guardrails

- `ls data/resultados/*.png | wc -l` → `12`; `sha256sum data/resultados/*.png` shows
  no duplicates; `data/resultados/g1*` absent (g1/A1 dedupe done, A1 kept canonical).
  Docs record `12 PNG únicos (13 emitidos; g1 duplicado de A1 eliminado sin renumerar)`.
- `docs/raw_manifest_sha256.txt` → 354 lines; ingestion manifest `n_ficheros: 354`,
  check 01 + check 17 PASS (354 local / 352 HDFS raw alias).
- `dim_municipios.csv`: 252 rows, `sum(n_anuncios)=594`, `sum(n_anuncios_raw)=843`,
  Tier Counter `D:188, C:57, A:4, B:3` (=252). Silver scope intact (no re-runs).
- `git diff -- data/raw` → empty (0 diffs in `data/raw`). No `Dockerfile` /
  `docker-compose.yml`. Kafka→HDFS, never Mongo (README explicit).

## 6. Issues

### P1 — none blocking. The only FAIL (07) is the documented known failure.

### P2 / warnings

- **P2-1 (minor residual reference):** `analysis/run_analisis_mongo.py:423` still
  lists `"g1_esfuerzo_por_territorio.png"` as first fallback in the g1/A1 loop.
  The file is deleted, so the loop falls through to `A1_distribucion_esfuerzo_por_TH.png`;
  behavior is correct but the stale name remains in code. Recommend removing the
  g1 name from the tuple in a follow-up.
- **P2-2 (process):** `tasks.md` checkboxes are still `[ ]` although all gate evidence
  above passes. Recommend marking tasks 1.1–1.5, 2.1–2.8, 3.1–3.4, 4.1–4.3 complete
  on commit (not done here: this verification touched no code/tasks).
- **P2-3 (note):** `verificar_fase_datos.py` exits 1 by design while FAIL 07 is known;
  `RESULTADO: PENDIENTE` (not OK) is the correct signal until upstream data changes.
  Do not mask or impute.

## Verdict

**GATE PASS** — pytest 177 passed / 1 skipped; verificar gate matches expected output
(PASS 01 354, 06 594/843, FAIL 07 conocido Aramaio 0.28 / Gaintza 1.45 / Usansolo 3.26
unmasked, 17 alias 354/352, huella SHA-256 printed); 12 unique PNGs; SVG 149 KB with
252/252, Tier A4/B3/C57/D188, oficial 159 / IDW 93 / contexto 252 and `252 contextual sobre 159`;
`Docker Compose HDFS` count 0; stale counts only as explicit history; raw 354 manifest
0 diffs, no Docker, Kafka→HDFS not Mongo.
