# Tasks: cierre-suficiencia-auditoria

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 400-600 |
| 400-line budget risk | Medium |
| Chained PRs recommended | Yes (4 units) |
| Suggested split | D1+D3 / D2 / VPO / análisis+informe |
| Delivery strategy | auto-chain |
| Chain strategy | commit-per-unit |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: commit-per-unit
400-line budget risk: Medium

### Suggested Work Units

| Unit | Goal | Focused test command | Runtime harness | Rollback boundary |
|------|------|----------------------|-----------------|-------------------|
| 1 | Gold, manifests y docs coherentes | `pytest tests/test_fase_datos.py tests/test_raw_inmutable.py -q` | `generar_manifest.py --verify` | Revertir gold, manifests y docs |
| 2 | Un solo esfuerzo (mediana) | `pytest tests/test_mongo_pipeline.py tests/test_contrato.py -q` | `python analysis/run_analisis_mongo.py` | Revertir transform + CSV |
| 3 | VPO municipal oficial | `pytest tests/test_vpo_municipal.py -q` | `python -m storage.load_mongo` | Borrar raw nuevo + colección + manifests |
| 4 | Sensibilidad, informe y limpieza | `pytest tests -q` | `python analysis/sensibilidad.py` | Revertir analysis/ y docs |

## Phase 1: D1 — manifest y gold en verde

- [ ] 1.1 Regenerar `dim_municipios_enriquecido.csv` con `transform/construir_dim_gold.py`.
  - Verify: `python transform/construir_dim_gold.py` → "252 filas".
- [ ] 1.2 Regenerar ambos manifests y verificar.
  - Verify: `python extract/generar_manifest.py --write && python extract/generar_manifest.py --verify` → exit 0.
- [ ] 1.3 Confirmar staleness.
  - Verify: `python transform/run_all.py --check` → exit 0.
- [ ] 1.4 Regenerar `auditoria_lagunas_silver.csv` (40 ficheros, 50 cols en base).
  - Verify: `python transform/auditar_lagunas_silver.py` y conteo de filas = 40.

## Phase 2: D3 — cifras de docs

- [ ] 2.1 `metodologia.md`: VPO (100 % sin dato), duplicados (845→759, 86, 10,18 %), 169 sin anuncios.
- [ ] 2.2 13→15 colecciones en README, arquitectura, modelo e informe de capacidad.
- [ ] 2.3 83→130 passed en arquitectura.
- [ ] 2.4 `informe_capacidad_mongo` C1 a Parcial.
- [ ] 2.5 `data/resultados/README.md` con los 21 artefactos.
- [ ] 2.6 `grep -rn "83[.,]73\|13 colecciones\|83 passed"` sin resultados.

## Phase 3: D2 — una definición de esfuerzo

- [ ] 3.1 Cambiar a mediana en `generar_analisis_variables_base.py` y documentar.
- [ ] 3.2 Recorrer cadena: `run_all.py --group analisis_base`, `--group analisis`.
- [ ] 3.3 Recargar Mongo (`python -m storage.load_mongo`) y verificar 252/759/5040.
- [ ] 3.4 Regenerar 5 CSV + PNG y anotar huella nueva.
- [ ] 3.5 Verificar Δ VPO vs canónico = 0 y actualizar cifras de tensión en docs.

## Phase 4: VPO municipal oficial

- [ ] 4.1 `extract/26_vpo_terminadas.py`: descarga a staging y promoción con guard.
- [ ] 4.2 `transform/limpiar_vpo_municipal.py`: parser → `vpo_municipal.csv`.
- [ ] 4.3 `storage/load_mongo.py::load_vpo_municipal` + `load_all`.
- [ ] 4.4 `tests/test_vpo_municipal.py`: 252, rango, códigos, sin nulos.
- [ ] 4.5 Actualizar contadores raw (353→354) y docs de VPO.

## Phase 5: sensibilidad y bootstrap

- [ ] 5.1 `analysis/sensibilidad.py`: oficial 159 vs 252.
- [ ] 5.2 Bootstrap 10.000 remuestreos de la mediana de los 4 robustos.
- [ ] 5.3 Salidas en `data/resultados/` y cita en el informe.

## Phase 6: informe y limpieza

- [ ] 6.1 `docs/informe_final.md` con anexos de huella, explain, tests y conteos.
- [ ] 6.2 Diccionario de columnas canónicas (D4) y nombre de comparativa (D5).
- [ ] 6.3 Archivar changes implementados (D6).
- [ ] 6.4 `verify-report.md` del change con evidencia literal.

## Phase 7: Gate

- [ ] 7.1 `pytest tests -q`, `generar_manifest.py --verify`, `run_all.py --check` y `git status` sin `data/raw` inesperado.
