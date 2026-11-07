# Proposal: mongo-respuesta-tres-robustos

## Intent

El nivel 10 de Respuesta exige comparar 3 municipios/zonas con conclusion vinculada a indicadores calculados en Mongo. Hoy ningun script genera la comparativa con paro y ningun informe la cita desde Mongo. Solo hay 4 municipios con n>=30 anuncios; la comparativa debe ser la de los 3 mas robustos por n_anuncios, con esfuerzo, precio y paro, sin inventar valores.

## Scope

### In Scope

- `analysis/comparativa_mongo.py` con `comparativa_tres_robustos`: top 3 por n_anuncios desde `pipeline_indicadores_municipio`, lookup de `tasa_paro_lanbide_pct` en `municipios.empleo`, CSV con codigo, nombre, n, esfuerzo 18-34, esfuerzo 16-29, precio medio, cuantia y paro.
- Tabla de 3 filas y conclusion por municipio en `docs/informe_capacidad_mongo.md`, con advertencia de muestra pequena y proxy de renta.
- `tests/test_mongo_comparativa.py` con `test_comparativa_tres_robustos_n30`: 3 filas, n>=30, paro no nulo.
- Artefactos SDD en `openspec/changes/mongo-respuesta-tres-robustos/`.

### Out of Scope

- No tocar `analysis/run_analisis_mongo.py`, `storage/*`, `transform/*` ni `tests/test_mongo_orquestador.py`.
- No ranking de los 252 municipios ni afirmaciones causales: solo los 3 robustos.
- No commit.

## Capabilities

### New Capabilities

- Ninguna.

### Modified Capabilities

- `presentacion-de-resultados`: nuevo requisito ADDED `COMPARATIVA-MONGO-01` que concreta `CONCLUSION-01` con la comparativa generada desde Mongo (esfuerzo, precio, cuantia y paro).

## Approach

Funcion Python que reutiliza `pipeline_indicadores_municipio()` ya ordenada por n_anuncios, filtra n>=30, toma 3 y hace `find_one` por codigo para leer `empleo.tasa_paro_lanbide_pct`. Escribe CSV con valores tal cual salen de Mongo (None si falta, nunca inventados). El informe cita la tabla generada.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `analysis/comparativa_mongo.py` | Create | `comparativa_tres_robustos` + `main` que escribe CSV |
| `data/resultados/comparativa_3_municipios_mongo.csv` | Create | 3 filas generadas desde Mongo |
| `docs/informe_capacidad_mongo.md` | Modify | Tabla de 3 filas + conclusion por municipio y advertencias |
| `tests/test_mongo_comparativa.py` | Create | `test_comparativa_tres_robustos_n30` contra Mongo real |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Solo 4 municipios con n>=30: el 4. (Vitoria, 39) queda fuera del top 3 | High | Declararlo en el informe: comparativa de robustez, no ranking fino |
| Paro nulo en alguno de los 3 | Low | 249/252 con paro valido en vivo; el test lo exige no nulo |
| Esfuerzo basado en proxy de renta joven | Med | Advertencia explicita en informe: esfuerzo 18-34 y 16-29 con renta estimada, no salario real |

## Rollback Plan

Borrar `analysis/comparativa_mongo.py`, `data/resultados/comparativa_3_municipios_mongo.csv`, `tests/test_mongo_comparativa.py` y la carpeta del cambio. Revertir la seccion anadida al informe.

## Dependencies

- MongoDB local `localhost:27017`, base `vivienda_euskadi`, colecciones `municipios`, `anuncios`, `alquiler_municipal`.

## Success Criteria

- [ ] `.venv/Scripts/python.exe -m pytest tests/test_mongo_comparativa.py tests/test_mongo_geo.py -q` exit 0.
- [ ] CSV con 3 filas, n>=30, paro no nulo, valores de Mongo.
- [ ] Informe con tabla de 3 filas y conclusion por municipio con advertencias.
