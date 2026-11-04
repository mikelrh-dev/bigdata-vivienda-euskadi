# Design: mongo-respuesta-tres-robustos

## Technical Approach

`analysis/comparativa_mongo.py` reutiliza `pipeline_indicadores_municipio()` de `analysis/mongo_aggregations.py`, que ya devuelve los municipios ordenados por n_anuncios descendente con esfuerzo 18-34, esfuerzo 16-29 (alias de `esfuerzo_joven_pct`), precio medio y cuantia. La funcion nueva filtra n>=30, toma los 3 primeros y para cada codigo hace `find_one` en `municipios` para leer `empleo.tasa_paro_lanbide_pct`. Conversiones a float tolerando `Decimal128` y `None`. `main()` escribe el CSV por defecto. strict_tdd false segun `openspec/config.yaml`: modo estandar, test contra Mongo real como `test_mongo_geo.py`.

## Architecture Decisions

| Opcion | Tradeoff | Decision |
|--------|----------|----------|
| Reutilizar `pipeline_indicadores_municipio` | Reescribir la agregacion duplicaria ~140 lineas y arriesga divergencia de esfuerzo | Elegida: reutilizar; filtrar y tomar 3 en Python |
| Paro con `find_one` por codigo | Una agregacion con `$lookup` a `municipios` sobre si misma es menos legible | Elegida: `find_one({_id: code})` y lectura de `empleo.tasa_paro_lanbide_pct`; None si falta |
| Test contra Mongo real | Mock ocultaria que el paro exista de verdad en los 3 | Elegida: test en vivo como `test_mongo_geo.py`; exige 3 filas, n>=30, paro no nulo |
| CSV con redondeo a 2 decimales | Los `Decimal128` imprimen con ruido | Elegida: `round(float, 2)` solo en CSV/informe; la funcion devuelve float sin redondear salvo CSV |

## Data Flow

    pipeline_indicadores_municipio() -> filtrar n>=30 -> top 3 por n_anuncios
        -> find_one municipios.empleo.tasa_paro_lanbide_pct por codigo
        -> filas (codigo, nombre, n, esfuerzo 18-34, esfuerzo 16-29, precio medio, cuantia, paro)
        -> CSV data/resultados/comparativa_3_municipios_mongo.csv + tabla en informe

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `analysis/comparativa_mongo.py` | Create | `comparativa_tres_robustos(min_n=30, top_n=3, output_path=None)` + `main()` |
| `data/resultados/comparativa_3_municipios_mongo.csv` | Create | Generado ejecutando el modulo |
| `docs/informe_capacidad_mongo.md` | Modify | Seccion con tabla de 3 filas, conclusiones y advertencias |
| `tests/test_mongo_comparativa.py` | Create | `test_comparativa_tres_robustos_n30` + comprobacion de CSV en tmp_path |

## Interfaces / Contracts

`comparativa_tres_robustos(min_n=30, top_n=3, output_path=None) -> list[dict]`: devuelve filas con claves `codigo_ine`, `nombre`, `n_anuncios`, `esfuerzo_joven_pct_18_34`, `esfuerzo_joven_pct_16_29`, `precio_medio_eur`, `cuantia_alquiler_mes`, `tasa_paro_lanbide_pct`. Con `output_path` escribe tambien el CSV. `main()` escribe el CSV por defecto e imprime las filas.

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Integracion en vivo | 3 filas, n>=30, paro no nulo | `test_comparativa_tres_robustos_n30` contra Mongo real |
| Integracion en vivo | CSV con 8 columnas y 3 filas | Escritura en `tmp_path` y lectura con `csv.DictReader` |
| Runtime real | Generacion del CSV de resultados | Ejecutar el modulo y leer el CSV generado |

## Threat Matrix

N/A — no hay routing, shell, subprocess, VCS/PR automation, clasificacion de ejecutables ni process integration. Solo lecturas PyMongo y escritura de CSV local.

## Migration / Rollout

No migration required. Solo lecturas sobre Mongo; el CSV es un artefacto nuevo.

## Open Questions

- Ninguna.
