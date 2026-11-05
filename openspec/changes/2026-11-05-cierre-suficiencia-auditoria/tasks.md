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

### Suggested Work Units

| Unit | Goal | Focused test command | Runtime harness | Rollback boundary |
|------|------|----------------------|-----------------|-------------------|
| 1 | Gold, manifests y docs coherentes | `pytest tests/test_fase_datos.py tests/test_raw_inmutable.py -q` | `generar_manifest.py --verify` | Revertir gold, manifests y docs |
| 2 | Un solo esfuerzo (mediana) | `pytest tests/test_mongo_pipeline.py tests/test_contrato.py -q` | `python analysis/run_analisis_mongo.py` | Revertir transform + CSV |
| 3 | VPO municipal oficial | `pytest tests/test_vpo_municipal.py -q` | `python -m storage.load_mongo` | Borrar raw nuevo + colección + manifests |
| 4 | Sensibilidad, informe y limpieza | `pytest tests -q` | `python analysis/sensibilidad.py` | Revertir analysis/ y docs |

## Phase 1: D1 — manifest y gold en verde

- [x] 1.1 Regenerar `dim_municipios_enriquecido.csv` (252 filas).
- [x] 1.2 Regenerar ambos manifests: `--verify` exit 0 (353/184 al inicio).
- [x] 1.3 `run_all.py --check` exit 0.
- [x] 1.4 `auditoria_lagunas_silver.csv` regenerado (40 CSV).

## Phase 2: D3 — cifras de docs

- [x] 2.1 `metodologia.md`: VPO, duplicados (86/845, 10,18 %), 169 sin anuncios.
- [x] 2.2 Colecciones corregidas (15 entonces, 16 tras VPO) en README,
      arquitectura, modelo e informe de capacidad.
- [x] 2.3 Tests 83/130 → 136 en arquitectura, README y AGENT.md.
- [x] 2.4 `informe_capacidad_mongo` C1 a Parcial, con flujo VPO.
- [x] 2.5 `data/resultados/README.md` con los artefactos reales.
- [x] 2.6 Sin restos de "83,73", "13 colecciones" ni "83 passed" en docs vivos.

## Phase 3: D2 — una definición de esfuerzo

- [x] 3.1 Mediana canónica en `generar_analisis_variables_base.py`.
- [x] 3.2 Cadena completa regenerada (base, renta joven, tensión, gold).
- [x] 3.3 Mongo recargado: 252/759/5040/406 + 252 VPO.
- [x] 3.4 5 CSV + PNG regenerados; huella nueva `d7e6732…`.
- [x] 3.5 Δ VPO vs canónico: máximo 0,0495 pp (redondeo); tensión 76/103/73
      actualizada en matriz y metodología.

## Phase 4: VPO municipal oficial

- [x] 4.1 `extract/26_vpo_terminadas.py` con staging y `--promote`.
- [x] 4.2 `transform/limpiar_vpo_municipal.py` con filtro a 252 vivos.
- [x] 4.3 `load_vpo_municipal` en `storage/load_mongo.py`.
- [x] 4.4 `tests/test_vpo_municipal.py`: 6 tests (252, rango, año, robustos,
      sin dato de Usansolo, sin stock inventado).
- [x] 4.5 Contadores raw/silver (354/185), ingestion manifest y docs.

## Phase 5: sensibilidad y bootstrap

- [x] 5.1 `analysis/sensibilidad.py`: oficial 159 vs 252.
- [x] 5.2 Bootstrap 10.000 remuestreos, semilla 42, calibrado al canónico.
- [x] 5.3 `sensibilidad_idw.csv` y `bootstrap_robustos.csv` citados en el informe.

## Phase 6: informe y limpieza

- [x] 6.1 `docs/informe_final.md` con cifras trazables.
- [x] 6.2 `docs/diccionario_columnas.md` (D4); nombre histórico de la
      comparativa documentado (D5, sin renombrar).
- [ ] 6.3 Archivar changes: **diferido** (15 changes sin merge de delta en
      `openspec/specs/`; archivarlos perdería requisitos).
- [x] 6.4 `verify-report.md` con evidencia literal y desviaciones.

## Phase 7: Gate

- [x] 7.1 `pytest` 136 passed, manifests 354/185 con 0 errores,
      `run_all --check` exit 0, gate 18/18.
