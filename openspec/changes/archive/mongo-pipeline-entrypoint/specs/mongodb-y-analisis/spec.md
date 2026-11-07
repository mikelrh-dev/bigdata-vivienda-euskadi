# Delta for mongodb-y-analisis

## ADDED Requirements

### Requirement: AUTOMATIZACION-PIPELINE-01 — Entrypoint único del pipeline MongoDB

El sistema SHALL proveer un entrypoint único en Python que encadene en orden `load_all`, `clean_all`, `ensure_indexes` y `pipeline_indicadores_municipio` sin intervención manual en MongoDB. El entrypoint SHALL imprimir los conteos de `load_all`, el total de `modified_count`, el total de `deleted_count` y el número de indicadores. Con `--dry-run` el entrypoint MUST NOT mutar producción y SHALL limitarse a validar imports y conexión con ping.

#### Scenario: El pipeline se ejecuta en orden sin tocar MongoDB a mano

- GIVEN los módulos `storage.load_mongo`, `storage.clean_mongo`, `analysis.mongo_indexes` y `analysis.mongo_aggregations` disponibles
- WHEN se ejecuta `main()` del entrypoint sin `--dry-run`
- THEN se llaman en orden `load_all`, `clean_all`, `ensure_indexes` y `pipeline_indicadores_municipio`
- AND se imprimen `load_all`, `modified_count`, `deleted_count` y el número de indicadores

#### Scenario: Dry-run valida sin mutar producción

- GIVEN MongoDB responde al ping
- WHEN se ejecuta el entrypoint con `--dry-run`
- THEN se validan los imports y la conexión con ping
- AND no se llama a `load_all`, `clean_all`, `ensure_indexes` ni a `pipeline_indicadores_municipio`
- AND la base productiva conserva su recuento

#### Scenario: El test prueba el entrypoint sin tocar producción

- GIVEN un test que sustituye las cuatro funciones por dobles con monkeypatch
- WHEN se ejecuta `test_pipeline_entrypoint_existe`
- THEN el test aserta el orden de llamada y la ausencia de mutación productiva
- AND exit code de pytest es 0

## MODIFIED Requirements

Ninguno. No se altera el comportamiento de loaders, limpieza, índices ni agregaciones existentes.

## REMOVED Requirements

Ninguno.

## RENAMED Requirements

Ninguno.
