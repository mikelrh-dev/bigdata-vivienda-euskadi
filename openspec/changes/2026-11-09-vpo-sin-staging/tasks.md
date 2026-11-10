# Tasks: vpo-sin-staging

## Phase 1: Contrato

- [x] 1.1 Crear proposal, spec delta, design y tasks.
  - Acceptance: el cambio define el flujo sin staging y la inmutabilidad.
  - Verify: revisión de los cuatro documentos.
  - Files: `openspec/changes/2026-11-09-vpo-sin-staging/`.

## Phase 2: Implementación

- [x] 2.1 Reescribir `extract/26_vpo_terminadas.py` sin `STAGING_DIR`.
  - Acceptance: descarga en memoria, `validar(bytes)`, `--desde-raw`.
  - Verify: `python extract/26_vpo_terminadas.py --desde-raw` → exit 0.
  - Files: `extract/26_vpo_terminadas.py`.

- [x] 2.2 Proteger `--promote` contra sobrescritura.
  - Acceptance: mismo SHA no-op; SHA distinto aborta; raw intacto.
  - Verify: sonda directa de `promover()` con ambos casos.
  - Files: `extract/26_vpo_terminadas.py`.

- [x] 2.3 Eliminar `data/staging/` y su entrada en `.gitignore`.
  - Acceptance: `find data/staging` no devuelve nada.
  - Verify: `git check-ignore data/staging` no devuelve coincidencia.
  - Files: `.gitignore`, `data/staging/`.

- [x] 2.4 Actualizar docs que citaban staging como paso del flujo.
  - Acceptance: no queda una instrucción de descargar/validar en staging; las menciones restantes son solo “no se crea”.
  - Verify: `rg "se descarga a .*data/staging|GIVEN el CSV validado en .*data/staging" openspec/changes/2026-11-05-cierre-suficiencia-auditoria` (sin coincidencias).
  - Files: `design.md`, `specs/vpo-municipal/spec.md`, `proposal.md`, `tasks.md`.

## Phase 3: Verificación

- [x] 3.1 Verificar raw local y manifest.
  - Acceptance: SHA `70a2937a…1294706`, tamaño 35.427 B, mtime sin cambios.
  - Verify: `sha256sum`, `stat`, `pytest tests/test_raw_inmutable.py`.
  - Resultado: PASS; mtime `1793914427` antes y después.

- [x] 3.2 Verificar HDFS raw.
  - Acceptance: `GETFILESTATUS` 200, `OPEN` 35.427 B, mismo SHA.
  - Verify: WebHDFS con `user.name=iabd-user15`.
  - Resultado: PASS; `length=35427`, SHA idéntico.

- [x] 3.3 Verificar suite y gates.
  - Acceptance: 236 passed, 2 skipped; raw inmutabilidad OK.
  - Verify: `pytest tests -q`, `pytest tests/test_raw_guardrails.py -q`.
  - Resultado: PASS; suite exit 0, gobernanza TODO OK, `run_all --check` exit 0.
