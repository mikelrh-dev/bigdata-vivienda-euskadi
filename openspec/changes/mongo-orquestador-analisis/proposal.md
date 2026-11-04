# Proposal: mongo-orquestador-analisis

## Intent

El reto v2 nivel 10 exige un script que ejecute todos los analisis principales y devuelva resultados preparados. Hoy `analysis/mongo_aggregations.py` define 8 pipelines pero `run_all` solo ejecuta uno, sin exportacion a CSV desde PyMongo, y el dashboard usa DuckDB.

## Scope

### In Scope

- Crear `analysis/run_analisis_mongo.py` con `run_all_estandar` que importe y ejecute en orden fijo los 8 pipelines, compare hash de dos ejecuciones y exporte 3 CSV desde PyMongo a `data/resultados/`.
- Crear `tests/test_mongo_orquestador.py` con `test_orquestador_analisis_exporta_tres_conjuntos` y `test_preparacion_visualizacion_tres_conjuntos`.
- Artefactos SDD en `openspec/changes/mongo-orquestador-analisis/`.

### Out of Scope

- No tocar `analysis/comparativa_mongo.py`, `docs/*`, `storage/*`, `transform/*` ni tests existentes.
- No cambiar los 8 pipelines ni usar DuckDB para estos CSV.
- No commit.

## Capabilities

### New Capabilities

- Ninguna.

### Modified Capabilities

- `presentacion-de-resultados`: requisitos ADDED `AUTOMATIZACION-ANALISIS-01` (orquestador de los 8 pipelines) y `PREPARACION-VISUALIZACION-01` (3 CSV desde PyMongo).

## Approach

Modulo orquestador que importa los 8 pipelines por nombre, los ejecuta en orden fijo, calcula huella SHA-256 de la serializacion ordenada de dos ejecuciones y escribe 3 CSV con `csv.DictWriter` y `utf-8-sig`, sin valores tecleados. Los tests ejecutan en `tmp_path` y asertan existencia, cabeceras, conteos y huella reproducible.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `analysis/run_analisis_mongo.py` | Create | `run_all_estandar`, huella, exportacion de 3 CSV y `main` |
| `tests/test_mongo_orquestador.py` | Create | Dos tests de orquestador y preparacion |
| `openspec/changes/mongo-orquestador-analisis/` | Create | proposal, spec, design, tasks, verify-report |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Orden de claves no determinista | Low | Serializacion con `sort_keys=True` para la huella |
| `Decimal128` no serializable en JSON/CSV | Med | Conversion explicita a texto numerico antes de escribir |
| Test muta `data/resultados` | Low | Tests exportan en `tmp_path`, nunca en la ruta real |

## Rollback Plan

Borrar `analysis/run_analisis_mongo.py`, `tests/test_mongo_orquestador.py`, los 3 CSV generados y la carpeta del cambio. Ningun modulo existente se modifica.

## Dependencies

- MongoDB local con base `vivienda_euskadi` cargada (252 municipios).

## Success Criteria

- [ ] `.venv/Scripts/python.exe -m pytest tests/test_mongo_orquestador.py tests/test_mongo_geo.py -q` exit 0.
- [ ] Los 3 CSV tienen 252, 252 y 2 filas y dos ejecuciones dan la misma huella.
