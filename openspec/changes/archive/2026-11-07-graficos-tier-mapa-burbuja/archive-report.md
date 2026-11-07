# Archive report: 2026-11-07-graficos-tier-mapa-burbuja

Archivado: 2026-11-07 (move mecánico a `openspec/changes/archive/2026-11-07-graficos-tier-mapa-burbuja/`).
Change: gráficos Tier B / mapa coroplético / burbuja esfuerzo-n. GATE PASS en `verify-report.md` (sin P1). Sin commit/push (restricción del operador).

## Tasks — gate de completitud

- `tasks.md`: 19/19 con `[x]`, 0 sin marcar. Ticks ya presentes en el artefacto persistido; sin reconciliación excepcional (apply/verify aportan la prueba, ver abajo).
- Prohibiciones transversales vigentes: sin Docker; HDFS solo raw inmutable; Kafka → HDFS, nunca a Mongo; sin imputación de precios; sin valores tecleados; n<30 nunca rankea.

## Evidencia literal del gate (verify-report.md, 2026-11-07)

Tests (`.venv/Scripts/python -m pytest tests -q`):

```
177 passed, 1 skipped in 7.11s
```

Doble SHA de `python analysis/run_analisis_mongo.py` (tres lecturas idénticas; re-verificado en archive):

```
b8411b77fdfa8df60b06618883dc05ee6bd04699b319b3dbb6b28ee9a8103015 *data/resultados/mongo_tier_confianza.csv
7f813fd61ee6800dacd24a230aaef43a8d97e9dbe1abd0300fa1da5b974f75a3 *data/resultados/mongo_esfuerzo_por_municipio.csv
```

Salida del propio script: `reproducibilidad: ok (dos ejecuciones con la misma huella)`, `huella: 3e54ee4927729c008e7fa38e64190ca85b662ae464aa2096c76dcaa0903bb45b`.

Artefactos regenerados (re-contados en archive):

- 13 PNG en `data/resultados/` (`ls data/resultados/*.png | wc -l` → `13`)
- 7 `mongo_*.csv` en `data/resultados/` (6 canónicos + `mongo_vpo_terminadas_por_municipio.csv`)
- 3 SVG nuevos en `docs/presentacion/assets/`: `chart_tierB_range.svg`, `chart_mapa_tier.svg`, `chart_effort_vs_n.svg`
- `presentacion.pdf`: 13 páginas, 7,87 MB

Tier B (desde `mongo_tier_confianza.csv`):

| Municipio | n_anuncios | temporal (mediana, n) | larga (mediana, n) |
|---|---|---|---|
| Sopela | 19 | 1500 (n=9) | 1500 (n=8) |
| Zarautz | 15 | 1200 (n=9) | 1800 (n=6) |
| Santurtzi | 11 | 1250 (n=5) | 1900 (n=4) |

Tier A (desde `mongo_esfuerzo_por_municipio.csv`, `tier == 'A'`, 4 filas):

| Municipio | n_anuncios | n_precio | esfuerzo_joven_pct_18_34 |
|---|---|---|---|
| Bilbao | 204 | 190 | 37.69 |
| Donostia / San Sebastián | 126 | 121 | 38.17 |
| Getxo | 50 | 48 | 28.60 |
| Vitoria-Gasteiz | 39 | 39 | 33.37 |

Distribución: `{'D': 188, 'C': 57, 'A': 4, 'B': 3}` → **4/3/57/188 = 252**. Sin literales (`grep -n "1500\|1800\|37\.69\|38\.17" docs/presentacion/build_presentacion.py` → sin coincidencias).

## Gates finales

| Gate | Resultado | Evidencia |
|---|---|---|
| Tests | PASS | `177 passed, 1 skipped in 7.11s` |
| Doble SHA | PASS | `b8411b77…` tier + `7f813fd6…` esfuerzo (full arriba) |
| Artefactos | PASS | 13 PNG + 7 CSV + 3 SVG + PDF 13 págs |
| Pipeline tier | PASS | Tier B 19/15/11 con min/max/mediana temporal/larga + n; Tier A 4 filas con esfuerzo |
| Libertades | PASS | Sin Docker; HDFS solo raw; Kafka → HDFS, no Mongo; `data/raw` 0 diffs |
| P1 bloqueantes | ninguno | P2-1…P2-4 no bloqueantes (ruta PNG, mapa 5,9 MB, working tree sucio, duplicado g1/A1) |

`verify-report` GATE: **PASS**, sin P1. `reviewGate` ausente (sin revisión nativa para este candidato): archive procede bajo política ordinaria del repo.

## Specs sincronizadas (antes del move)

| Dominio | Acción | Detalle |
|---|---|---|
| `presentacion-de-resultados` | Actualizada (`openspec/specs/presentacion-de-resultados/spec.md`) | 3 requisitos ADDED: `chart_tierB_range`, `chart_mapa_tier`, `chart_effort_vs_n` (con sus escenarios + "Sin valores inventados"); resto del spec intacto |
| `mongodb-y-analisis` | Actualizada (`openspec/specs/mongodb-y-analisis/spec.md`) | `AGREGACION-01` MODIFIED: +`min/max/mediana_precio_temporal`, +`min/max/mediana_precio_larga`, +`esfuerzo_joven_pct_18_34` con nombres canónicos; 3 escenarios nuevos (Tier B / Tier A / Edge n<30); resto del spec intacto |

## Diff stat (sincronización, `git diff --stat -- openspec/specs/`)

```
 openspec/specs/extraccion-datos/spec.md           | 100 ++++++++++++++-
 openspec/specs/mongodb-y-analisis/spec.md         | 148 ++++++++++++++++++++--
 openspec/specs/presentacion-de-resultados/spec.md | 130 ++++++++++++++++++-
 3 files changed, 361 insertions(+), 17 deletions(-)
```

Nota: el cambio en `extraccion-datos/spec.md` es deriva pre-existente del working tree (P2-3 del verify-report), no de este change. Las líneas de este change son las 3 secciones nuevas en `presentacion-de-resultados` (39 líneas) y la extensión de `AGREGACION-01` + 3 escenarios en `mongodb-y-analisis`.

## Move mecánico (Step 3) — evidencia `diff -r`

```
source gone: OK
DIFF-R EMPTY: PASS
```

Snapshot pre-move con `cp -R`, move con `mv` (carpeta untracked; `git mv` no aplicable), `diff -r` snapshot vs. archive vacío. `archive-report.md` es aditivo y queda fuera de la comparación. Directorio activo `openspec/changes/2026-11-07-graficos-tier-mapa-burbuja/` ya no existe.

## Contenido del archivo

- `proposal.md` ✅ · `specs/` (2 deltas) ✅ · `tasks.md` (19/19) ✅ · `verify-report.md` ✅ · `archive-report.md` ✅
