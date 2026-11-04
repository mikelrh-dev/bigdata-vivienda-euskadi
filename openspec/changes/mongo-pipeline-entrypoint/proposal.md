# Proposal: mongo-pipeline-entrypoint

## Intent

El criterio RA1 Automatización nivel 10 exige un script que ejecute carga, limpieza y transformación sin tocar MongoDB a mano. Hoy load_mongo, clean_mongo, mongo_indexes y mongo_aggregations existen por separado, sin entrypoint único que los encadene en orden.

## Scope

### In Scope
- Crear `scripts/run_mongo_pipeline.py` con `main` que llama en orden `load_all`, `clean_all`, `ensure_indexes` y `pipeline_indicadores_municipio`, imprime conteos y soporta `--dry-run` sin mutar producción.
- Crear `tests/test_mongo_pipeline.py` con `test_pipeline_entrypoint_existe` que verifica el entrypoint con mock/monkeypatch sin tocar producción.
- Artefactos SDD del cambio en `openspec/changes/mongo-pipeline-entrypoint/`.

### Out of Scope
- No tocar `storage/load_mongo.py`, `storage/mongo.py`, `storage/clean_mongo.py`, `docs/*` ni `tests/test_mongo.py`.
- No cambiar loaders, limpieza, índices ni agregaciones existentes.
- No ejecutar el pipeline completo contra producción en esta ronda: solo pytest con mock y dry-run con ping.

## Capabilities

### New Capabilities
- Ninguna.

### Modified Capabilities
- `mongodb-y-analisis`: nuevo requisito ADDED `AUTOMATIZACION-PIPELINE-01` para el entrypoint único carga más limpieza más índices más agregación.

## Approach

Script CLI que inserta la raíz del repo en `sys.path`, importa las cuatro funciones en tiempo de importación (validación de imports), y en `main(argv)` ejecuta la cadena en orden salvo `--dry-run`. El test carga el módulo por ruta con `importlib`, sustituye las cuatro funciones por espías con monkeypatch, aserta orden y ausencia de mutación.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `scripts/run_mongo_pipeline.py` | Create | Entrypoint único con `main`, `--dry-run` con ping e impresión de conteos |
| `tests/test_mongo_pipeline.py` | Create | `test_pipeline_entrypoint_existe` con monkeypatch y `test_dry_run_no_muta_prod` |
| `openspec/changes/mongo-pipeline-entrypoint/` | Create | proposal, delta spec, design, tasks, verify-report |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| `sys.path` no incluye la raíz al ejecutar como script | Med | Insertar la raíz en `sys.path` antes de importar `storage`/`analysis` |
| `clean_all` devuelve dict anidado sin total directo | Low | Sumar recursivamente `modified_count` y `deleted_count` |
| El test toca producción | Low | Monkeypatch completo de las cuatro funciones y de `ping`; conteo productivo solo lector |

## Rollback Plan

Borrar `scripts/run_mongo_pipeline.py`, `tests/test_mongo_pipeline.py` y la carpeta `openspec/changes/mongo-pipeline-entrypoint/`. Ningún módulo existente se modifica, producción no se toca.

## Dependencies

- MongoDB local en `localhost:27017` con base `vivienda_euskadi` para el ping de `--dry-run`.

## Success Criteria

- [ ] `.venv/Scripts/python.exe -m pytest tests/test_mongo_pipeline.py -q` pasa con exit code 0.
- [ ] `.venv/Scripts/python.exe scripts/run_mongo_pipeline.py --dry-run` pasa con exit code 0, valida imports y ping, y no muta producción.
