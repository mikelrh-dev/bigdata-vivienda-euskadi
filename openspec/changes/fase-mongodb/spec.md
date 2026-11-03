# Spec: Fase MongoDB — modelado, PyMongo y análisis

## Objective

Implementar el bloque SBD-RA3 del reto contra la rúbrica: modelo documental
justificado, operaciones PyMongo automatizadas y comprobadas, consultas avanzadas,
Aggregation Pipeline, índices con `explain()` y decisión de transacciones. Fuente:
`data/procesado/` (silver). BD: `vivienda_euskadi` en MongoDB local.

## Tech Stack

Python 3.12 (`.venv`), PyMongo 4.x, pandas 2.2, pytest. Sin dependencias nuevas.

## Commands

```bash
.venv/Scripts/python.exe -m pytest tests/test_mongo.py -q
.venv/Scripts/python.exe storage/load_mongo.py
.venv/Scripts/python.exe analysis/mongo_aggregations.py
```

## Requirements

### Requirement: MONGO-MODELO-01 — Modelo justificado

El sistema SHALL crear colecciones con campos adecuados y justificar modelo y
relaciones. Al menos una decisión de embedding o referencing con tipos BSON y
patrones de acceso.

#### Scenario: Modelo documentado
- GIVEN las fuentes silver
- WHEN se diseña la BD
- THEN cada colección tiene propósito y campos justificados
- AND la relación anuncio↔municipio↔alquiler está descrita como decisión propia

### Requirement: MONGO-PYMONGO-01 — Operaciones automatizadas

El sistema SHALL implementar inserción, actualización y borrado con PyMongo de
forma automatizada y comprobar resultados (`inserted/modified/deleted`).

#### Scenario: Carga idempotente
- GIVEN un documento ya insertado
- WHEN se recarga
- THEN no se duplica
- AND se reporta el número procesado

### Requirement: MONGO-CONSULTAS-01 — Consultas avanzadas

El sistema SHALL combinar condiciones y consultar campos anidados/arrays,
incluyendo `$exists`, `$type`, proyecciones, ordenación, límite y regex cuando
tenga sentido.

#### Scenario: Filtro anidado
- GIVEN anuncios con `ubicacion.codigo_ine`
- WHEN se consulta por municipio
- THEN solo devuelve los de ese municipio

### Requirement: MONGO-AGG-01 — Aggregation ≥4 etapas

El sistema SHALL encadenar al menos cuatro etapas distintas para obtener
indicadores complejos por municipio.

#### Scenario: Pipeline ejecutable
- GIVEN datos cargados
- WHEN se ejecuta la agregación
- THEN usa ≥4 etapas distintas
- AND produce un indicador por municipio

### Requirement: MONGO-INDICES-01 — Índices con explain

El sistema SHALL diseñar al menos un índice justificado por consulta real y
demostrar su efecto con `explain("executionStats")` antes y después.

#### Scenario: Before/after
- GIVEN una consulta real
- WHEN se ejecuta explain antes y después de crear el índice
- THEN se comparan COLLSCAN/IXSCAN, nReturned, totalDocsExamined

### Requirement: MONGO-TRANS-01 — Transacciones

El sistema SHALL determinar si requiere atomicidad multidocumento e
implementarla si procede o justificar su ausencia.

#### Scenario: Decisión razonada
- GIVEN el modelo documental
- WHEN se revisa la necesidad de atomicidad
- THEN o bien se implementa transacción (commit/abort)
- OR se justifica atomicidad documental suficiente

## Success Criteria

1. 4+ colecciones cargadas con conteos esperados.
2. CRUD/limpieza con contadores verificados.
3. Consultas avanzadas demostradas.
4. ≥1 pipeline con ≥4 etapas.
5. ≥1 índice con mejora demostrable.
6. Decisión de transacciones documentada.
7. `pytest tests/test_mongo.py -q` en verde.
"""