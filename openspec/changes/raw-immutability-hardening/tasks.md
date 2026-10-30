# Tasks: raw-immutability-hardening

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 500-800 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 → PR 2 → PR 3 |
| Delivery strategy | auto-chain |
| Chain strategy | stacked-to-main |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Guard + enriquecer defaults | PR 1 | `.venv/Scripts/python.exe -m pytest tests/test_raw_guardrails.py -q -k guard` | `python transform/enriquecer_codigo_ine.py` (silver) | transform/_raw_guard.py, enriquecer flags |
| 2 | f4 naming + geo temp + muni resolve | PR 2 | `.venv/Scripts/python.exe -m pytest tests/test_raw_guardrails.py -q -k "f4 or geo or muni"` | import modules smoke | f4/geo/muni files |
| 3 | Dedup + additive outputs + manifest/docs/tests | PR 3 | `.venv/Scripts/python.exe -m pytest tests -q` | `python transform/unificar_anuncios.py` | unificar/downstream/docs/tests |

## Phase 1: Foundation
- [x] 1.1 Create `transform/_raw_guard.py`: `assert_raw_writable(reason)` (non-empty after strip else ValueError; log via "raw_guard" INFO) plus optional `_audit_message`.
- [x] 1.2 Modify `transform/enriquecer_codigo_ine.py`: `main(force=False, silver=True, write_raw=False, reason=None)`; add CLI `--write-raw`, `--reason`; raw path only with guard + `_check_frozen` + deprecation warning; default silver.
- [x] 1.3 Keep `--silver` accepted as no-op compat.

## Phase 2: Raw writers & temp
- [x] 2.1 Modify `transform/f4_pisos_dirigido.py`: import guard, call `assert_raw_writable("f4 directed scrape lot")`, implement `_nombre_lote(raw_dir)` (seconds + uuid token, retry), expose for tests.
- [x] 2.2 Modify `extract/22_geo_areas_funcionales.py`: `TMP=Path(tempfile.gettempdir())/"geo_areas"` with `mkdir(parents=True, exist_ok=True)`; `RAW.mkdir(...)`; no `/tmp` literal; wrap side effects in `main()` under `__main__`.

## Phase 3: Resolution
- [x] 3.1 Modify `extract/entity_resolution.py`: keep canonical `norm()`; add normalized `MANUAL_MAP`; fold aliases into `_mapa()` via setdefault.
- [x] 3.2 Modify `transform/muni_resolve.py`: import `norm`, `MANUAL_MAP` from entity_resolution; build `NAME2CODE` with `norm()` keys; implement `resolver_codigo` (valid code, manual map, exact, fuzzy >=0.85, else None,None).

## Phase 4: Unification & additive outputs
- [x] 4.1 Modify `transform/unificar_anuncios.py`: tag `_source_order` (base 0/1/2, lots 10+sorted index), sort before dedup, dedup by `(portal,id_anuncio)`, print report + write `data/procesado/dedup_report.json`, final sort by `(portal,id_anuncio)`.
- [x] 4.2 Modify `transform/generar_fingerprint.py`: preserve all existing CSV columns when rewriting (superset).
- [x] 4.3 Modify `transform/enriquecer_equipamiento_realtyapi.py`: preserve all existing CSV columns when rewriting (superset).
- [x] 4.4 Modify `transform/rescatar_features_nlp.py`: preserve all existing CSV columns when rewriting (superset).

## Phase 5: Manifest & contract
- [x] 5.1 Reconcile `docs/raw_manifest_sha256.txt`: regenerate listing `data/raw/` excluding `.FROZEN`, `.gitkeep`, `ingestion_manifest.json`, sorted `<sha256>  <relpath>`.
- [x] 5.2 Create `docs/contrato_datos_raw.md`: layers, raw rules, manifest exclusions, `codigo_ine` schema, canonical columns, muni resolution, lots naming, temp dir, additive outputs.

## Phase 6: Tests
- [x] 6.1 Extend `tests/test_raw_inmutable.py`: add `test_raw_manifest_complete` and `test_raw_guard_reason`.
- [x] 6.2 Create `tests/test_raw_guardrails.py`: `test_no_transform_writes_raw`, `test_f4_filename_unique`, `test_geo_temp_not_tmp_root`, `test_muni_resolve_accented_slash`, `test_unificados_columns_superset`.
- [x] 6.3 Run `.venv/Scripts/python.exe -m pytest tests -q` (expect 59 + new green).

## Resultado de apply

- Suite: **66 passed, 0 failed** (59 previos + 7 nuevos).
- `data/raw/` verificado intacto tras ejecutar el enriquecimiento en modo silver
  (`test_raw_hashes_manifest` + `test_raw_manifest_complete` en verde).
- Manifest raw regenerado: 316 ficheros con hash (excluye `.FROZEN`, `.gitkeep`,
  `ingestion_manifest.json` y la copia legacy `manifest_sha256.txt`).
