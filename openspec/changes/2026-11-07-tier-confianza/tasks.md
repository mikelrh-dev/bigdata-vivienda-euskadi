# Tasks: 2026-11-07-tier-confianza

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 350–450 |
| 400-line budget risk | Medium |
| Chained PRs recommended | Yes |
| Suggested split | PR1 pipeline+comparativa → PR2 dim+tests → PR3 artefactos+docs |
| Delivery strategy | single-pr |
| Chain strategy | feature-branch-chain |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: Medium

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | `pipeline_tier_por_municipio` + comparativa Tier A | PR1 (base `tier-confianza`) | `pytest tests/test_tier_confianza.py -q` | `python analysis/run_analisis_mongo.py --salida data/resultados` | revertir `mongo_aggregations.py` + `comparativa_mongo.py` |
| 2 | dim `tier`+`tier_etiqueta` + tests 4/3/57/188 | PR2 (base PR1) | `pytest tests/test_tier_confianza.py tests/test_mongo_pipeline.py -q` | N/A (dim = catálogo, sin runtime) | revertir `dim_municipios.py` + `aplicar_cobertura_mercado.py` |
| 3 | Regenerar PNG/CSV + sync docs + gates | PR3 (base PR2) | `pytest tests -q` | doble `run_analisis_mongo.py` SHA | revertir `data/resultados/` + `docs/` |

## Phase 1: Pipeline Mongo (AGREGACION-01)

- [x] 1.1 Añadir `pipeline_tier_por_municipio()` en `analysis/mongo_aggregations.py`: `$group` por `codigo_ine` desde `anuncios` + `$lookup` a `municipios`, calcular `n_anuncios`, `n_precio`, `min_precio`, `max_precio`, `n_precio_temporal`, `n_precio_larga`; derivar `tier` A≥30 / B 10–29 / C 1–9 / D 0; devolver 252 filas.
- [x] 1.2 Exportar 6º CSV `data/resultados/mongo_tier_confianza.csv` en `analysis/run_analisis_mongo.py`: añadir pipeline a `PIPELINE_ORDER`, definir `EXPORT_TIER_CONFANZA`, extender `EXPORTS_6` (y `exportar_seis_csv`).
- [x] 1.3 Filtrar `analysis/comparativa_mongo.py` a Tier A `n>=30` (mantener `comparativa_cuatro_robustos` como top-4 Tier A); añadir advertencia `delta`/`advertencia` en CSV: "solo Tier A sustenta ranking; B/C/D no ranking".

## Phase 2: dim_municipios (TIER-01)

- [x] 2.1 En `transform/dim_municipios.py` (enricher post-catálogo, sin imputación): añadir columnas `tier` y `tier_etiqueta` derivadas de `n_anuncios` (A/B/C/D); no tocar raw, no imputar comarcal/IDW.
- [x] 2.2 En `transform/aplicar_cobertura_mercado.py`: aplicar `tier`/`tier_etiqueta` DESPUÉS de `dim_municipios.py` base, usando `max()` si hay conflicto de escritura; mantener `tipologia_mercado`/`n_anuncios_raw` intactos. Verificar orden DAG en `transform/run_all.py`.

## Phase 3: Tests (CONCLUSION-01, PISOS-05)

- [x] 3.1 Crear `tests/test_tier_confianza.py` con: conteos 4/3/57/188 = 252 desde Mongo; Tier C/D con `n_precio=0` y min/max nulos, sin precio municipal; `n_precio_temporal != n_precio_larga` en los 3 Tier B (Sopela/Zarautz/Santurtzi); sin promoción comarcal/IDW (nunca `n<30` sube a Tier A); doble ejecución con SHA idéntico.
- [x] 3.2 Actualizar `tests/test_mongo_comparativa.py` si corrige columnas; mantener compatibilidad `comparativa_tres_robustos(top_n=3)`.

## Phase 4: Artefactos y docs (env gates)

- [x] 4.1 Regenerar `data/resultados/`: 13 PNG + 6 CSV (incl. `mongo_tier_confianza.csv`) + `dim_municipios` con `tier` vía `python analysis/run_analisis_mongo.py`; verificar doble SHA idéntico.
- [x] 4.2 Sync docs `docs/README.md`, `docs/conclusiones_municipios.md` (frase literal "252 contextual sobre 159", `grep -c` ≥ 1), `docs/guion_defensa*.md`, `docs/metodologia.md`: sustituir L1/L2/L3 por Tier A (fuerte) / B (indicativo min-max+mediana+`n_precio`, temporal≠larga) / C (sin precio municipal) / D (sin dato + contexto oficial), textual contextual.
- [x] 4.3 Gates finales: `pytest tests -q` → 166 passed + 1 skipped; doble `run_analisis_mongo.py` con huella SHA idéntica; manifests raw 354 + procesado 187 actualizados. Sin Docker; HDFS solo raw (352); Kafka→HDFS, nunca Kafka→Mongo.
