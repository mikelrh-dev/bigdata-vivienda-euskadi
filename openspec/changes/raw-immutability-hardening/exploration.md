# Exploration: raw-immutability-hardening

## Current State

Raw data lives in `data/raw/` and is protected only by convention: an empty
`.FROZEN` marker (mode 644, writable), a SHA-256 manifest
(`docs/raw_manifest_sha256.txt`, 317 entries) and two smoke tests in
`tests/test_raw_inmutable.py` (marker exists + hashes match). There is no
code-level guard: transforms can still write to `data/raw/` by default.

Concrete weak points (from audit + code review):

- `transform/enriquecer_codigo_ine.py` writes to `data/raw/` unless `--silver`
  is passed; default path touches raw and only aborts if `.FROZEN` exists
  (bypass with `--force`).
- `transform/f4_pisos_dirigido.py` writes directed-scrape lots to
  `data/raw/anuncios_pisos_dirigido_{YYYYMMDD}.json` (date only) -> same-day
  runs collide and overwrite.
- `extract/22_geo_areas_funcionales.py` defaults its temp dir to `/tmp`
  (non-existent on Windows) and writes its output to `data/raw/`.
- `transform/muni_resolve.py` builds `NAME2CODE` with accented/slash keys but
  looks up `norm()`-normalized (ascii, spaces) keys -> exact match is dead for
  accented/slash variants; only the fuzzy fallback can match.
- `transform/unificar_anuncios.py` dedups by `(portal, id_anuncio)` in input
  order (order-dependent, no priority), and several transforms
  (`generar_fingerprint.py`, `enriquecer_equipamiento_realtyapi.py`,
  `rescatar_features_nlp.py`) overwrite `anuncios_unificados.csv` with a
  reduced column set, clobbering the canonical wide table.
- Tests are smoke-level: no transform unit tests, no raw-write guardrail, no
  schema/contract checks. `test_raw_inmutable.py` only asserts marker + hashes.

Scope is intentionally limited to **raw acquisition + cleaning**. No
infra/Mongo/Kafka work.

## Affected Areas

- `extract/22_geo_areas_funcionales.py` — temp dir default + raw write.
- `extract/main_ingest.py` — manifest writer; only writer allowed to mutate raw
  inventory; should stay the single orchestrator.
- `transform/enriquecer_codigo_ine.py` — `_check_frozen`, default output dir.
- `transform/f4_pisos_dirigido.py` — date-only filename, raw lot write.
- `transform/muni_resolve.py` — dead exact lookup; `norm()` vs stored keys.
- `transform/unificar_anuncios.py` — dedup order, reduced-column rewrites by
  downstream transforms.
- `transform/generar_fingerprint.py`, `transform/enriquecer_equipamiento_realtyapi.py`,
  `transform/rescatar_features_nlp.py` — clobber `anuncios_unificados.csv`.
- `tests/test_raw_inmutable.py` — weak guardrail.
- `tests/test_contrato.py`, `tests/test_crudos.py` — smoke; no transform tests.
- `docs/raw_manifest_sha256.txt`, `data/raw/.FROZEN` — contract artifacts.

## Approaches

1. **Convention + static guardrail tests (recommended)**
   - Flip `enriquecer_codigo_ine.py` default to silver (`--silver` becomes
     default); raw writes require `--write-raw --reason <text>` and re-run the
     freeze procedure.
   - `f4_pisos_dirigido.py`: timestamped filename with seconds + run token; refuse
     to overwrite; keep append-only.
   - `22_geo_areas_funcionales.py`: project-local temp default (`tempfile`/
     `.tmp`), create dirs; keep raw output but document as acquisition.
   - `muni_resolve.py`: normalize map keys with `norm()` so exact lookup works;
     normalize `MANUAL_MAP` keys too; keep fuzzy fallback.
   - `unificar_anuncios.py`: deterministic dedup (sorted input, priority order,
     explicit duplicate report); downstream transforms must add columns, never
     drop, or write to separate files.
   - Add a shared `transform/_raw_guard.py` (`assert_raw_writable(reason)`) used
     by any transform that legitimately writes raw (f4).
   - Data contract doc (`docs/data_contract.md` or
     `openspec/specs/data-contract/spec.md`): raw layer rules, manifest, file
     inventory, schemas; processed layer outputs and their columns.
   - Guardrail tests: static scan of `transform/*.py` for raw writes (allow-list),
     muni_resolve accented/slash cases, f4 filename uniqueness, contract column
     superset for `anuncios_unificados.csv`.
   - Pros: low risk, no infra, additive tests, keeps 59 passing.
   - Cons: enforcement is test-based + opt-in flags, not OS-level; requires
     discipline for new scripts.

2. **OS-level read-only raw (chmod / attrib)**
   - Make `data/raw/` read-only at the filesystem level; extractors must flip
     the bit via a documented procedure.
   - Pros: stronger by-design guarantee.
   - Cons: fragile on Windows (attrib/ACLs), breaks `main_ingest.py` manifest
     writes and directed-scrape append-only lots, complicates CI; high friction.

3. **RawWriter abstraction + schema validation (pandera/pydantic)**
   - Central `RawWriter` that refuses writes when frozen; all extractors route
     through it; validate schemas on write.
   - Pros: strongest design, testable.
   - Cons: large refactor of 30+ extractors; out of scope for this phase; adds
     a dependency not currently in requirements.

## Recommendation

Approach 1. It delivers the requested hardening (by-design defaults + guardrail
tests + data contract) within the phase scope and without touching infra. Defer
Approach 3's full abstraction to a later phase if the guardrail tests prove
insufficient. Approach 2 is rejected due to Windows friction and conflict with
legitimate append-only acquisition writes.

Key design decisions:
- Raw is immutable **by default**; mutability is an explicit, reasoned opt-in
  (`--write-raw --reason`), never the default.
- Acquisition scripts (`extract/*`) are the only writers of new raw files;
  transforms write to `data/procesado/`.
- Directed-scrape lots remain append-only raw inputs but get unique, collision-free
  names and are listed in the manifest via `main_ingest.py --mode replay-raw`.
- `anuncios_unificados.json/csv` is the canonical cleaning output; derived
  features are additive columns or separate files, never reductions.
- `muni_resolve` and `entity_resolution` share one normalized key space.

## Risks

- Flipping `enriquecer_codigo_ine.py` default could surprise existing callers
  that rely on in-place raw enrichment; mitigate with a deprecation notice and
  keep `--force`/`--write-raw` for the documented re-freeze procedure.
- Static scan tests can be evaded by dynamic paths; mitigate by also checking
  for `RAW_DIR`/`data/raw` string literals and `open(..., "w")` patterns, plus
  code review.
- Manifest count drift (312 vs 317) must be reconciled before adding new lots,
  or the contract test will be noisy.
- `muni_resolve` change may alter dedup counts in `unificar_anuncios`; re-run
  and compare before/after to avoid silent regressions.
- Windows temp default fix must create parent dirs and handle `TMPDIR` override.

## Guardrail tests (proposed)

- `test_raw_manifest_complete`: every file under `data/raw/` (except `.FROZEN`,
  `.gitkeep`, `ingestion_manifest.json`) is in the manifest; no orphans.
- `test_no_transform_writes_raw`: AST/grep scan of `transform/*.py` for writes to
  `RAW_DIR`/`data/raw` outside an allow-list (`f4_pisos_dirigido.py` via guard).
- `test_f4_filename_unique`: directed-lot filename includes seconds + run token
  and is not date-only.
- `test_geo_temp_not_tmp_root`: `22_geo_areas_funcionales.py` resolves temp under
  project or `tempfile.gettempdir()`, never hard-coded `/tmp`.
- `test_muni_resolve_accented_slash`: accented/slash variants resolve to the
  canonical code.
- `test_unificados_columns_superset`: derived outputs never have fewer columns
  than the canonical `anuncios_unificados.csv`.

## Ready for Proposal

Yes. Next step: write the proposal + spec (data contract) + design + tasks for
`raw-immutability-hardening`, then implement with pytest guardrails.
