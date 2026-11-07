# Proposal: 2026-11-07-pisos-re-resolver-ubicacion

## Intent

- Corregir ubicación real de pisos.com: 187/245 (76%) en L2 usan `municipio_busqueda` (= búsqueda, no ubicación).
- Baseline: L1 4 robustos ≥30 sin pisos (Bilbao 173, Donostia 113, Getxo 40, Vitoria 39); L2 16 con 10-29. Eustat 252/252, Lanbide 249/252 intactos.

## Scope

### In Scope

- Re-resolver pisos: subtítulo/título → variantes `dim_municipios` + gazetteer barrio→municipio.
- Fuera de Euskadi a cuarentena reversible; NUNCA `municipio_busqueda` como ubicación.
- Re-ejecutar `unificar_anuncios` + `aplicar_cobertura_mercado`; Mongo staging+backup+rename; 13 PNG + 6 CSV.
- Tests: re-resolución, cuarentena, n≥30 sin imputación comarcal/IDW.

### Out of Scope

- Sin Docker; HDFS solo raw; Kafka→HDFS, NO Kafka→Mongo.
- Sin nuevas fuentes; sin tocar Eustat/Lanbide.
- Sin ranking municipal con n<30.

## Capabilities

### New Capabilities

- Ninguna.

### Modified Capabilities

- `extraccion-datos` (EXTRACCION-01): subtítulo/título como evidencia de ubicación real.
- `mongodb-y-analisis` (LIMPIEZA/TRANSFORM/CARGA-SEGURA): re-resolver, cuarentena, recarga segura, `n_anuncios` real.
- `presentacion-de-resultados` (AUTOMATIZACION/PREPARACION): 13 PNG + 6 CSV desde Mongo.

## Approach

1. `transform_pisos`/`resolver_codigo`: subtítulo/título manda; `codigo_ine` no vale sin coincidencia textual; gazetteer + cuarentena.
2. Re-ejecutar `unificar_anuncios.py` → `aplicar_cobertura_mercado.py` (base `dim_municipios` → enricher).
3. Recargar Mongo vía `load_mongo`; regenerar `data/resultados` con `run_analisis_mongo.py`; doble ejecución SHA igual.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `extract/08_pisos_scraper.py:163-169` | Modified | Conservar subtítulo/título; mantener `es_busqueda_no_ubicacion=True` |
| `transform/unificar_anuncios.py:130` | Modified | `transform_pisos` lee subtítulo/título, no `municipio_busqueda` |
| `transform/muni_resolve.py:37-43` | Modified | No propagar `VALID_CODES`; gazetteer barrio→municipio |
| `transform/aplicar_cobertura_mercado.py` | Modified | Cuarentena fuera-Euskadi; cobertura por ubicación real |
| `storage/load_mongo.py` | Modified | staging+backup+rename, recrear índices |
| `data/resultados/` | Modified | 13 PNG + 6 CSV `mongo_*.csv` desde Mongo |
| `tests/test_pisos_ubicacion_real.py` | Created | 245 re-resueltos, cuarentena, NUNCA búsqueda |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Barrio ambiguo / gazetteer incompleto | Med | Cuarentena motivada, nunca búsqueda; log de no-resueltos |
| Fuera-Euskadi mal clasificado | Low | Cuarentena reversible; informe antes de recargar |
| Recarga pierde 252/252 o índices | Med | staging+backup+rename; abortar si vacío |
| Pisos mal reinstalados inflan L1/L2 | High | n≥30 fuerte, sin imputación. Beneficio 9/10, no-hacer 10/10, impl. 6/10 |

## Rollback Plan

- Mongo: rename desde `<name>__backup`. Datos: `git checkout --`; cuarentena reversible.

## Dependencies

- `data/procesado/dim_municipios.csv` (252); `.venv`; MongoDB local.

## Success Criteria

- [x] 0 pisos por `municipio_busqueda`; 245 re-resueltos o en cuarentena motivada.
- [x] Fuera-Euskadi conteada y reversible.
- [x] `pytest tests -q` en verde (151 + nuevos).
- [x] 13 PNG + 6 CSV regenerados, doble ejecución SHA igual, sin regresión 252/252 y 249/252.

## Proposal question round — Aprobado

- **Aprobado**: objetivo, reglas, edge-cases y tradeoff cerrados en Scope/Approach.
