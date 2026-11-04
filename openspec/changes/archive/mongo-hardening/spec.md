# Spec: mongo-hardening

## Requirements
- R1: `to_float` SHALL devolver None para "nan"/NaN, nunca NaN a Mongo.
- R2: `canonicalize_codigo_ine` SHALL garantizar 5 digitos con zfill, no solo $toString.
- R3: `load_*` SHALL ser idempotente sin ventana vacia (no drop antes de docs listos).
- R4: `clean_all` SHALL reportar las 13 colecciones.
- R5: Top/esfuerzo e indicador por municipio SHALL usar $sort/$limit en Mongo.
- R6: Colecciones base SHALL llevar fuente/anio_fuente/fecha_extraccion.
- R7: Tests SHALL cubrir codigo_ine 13/13 sin mutar DB real.

#### Scenario: NaN no entra
- GIVEN "nan"/nan
- WHEN to_float
- THEN None.

#### Scenario: Araba conserva cero
- GIVEN codigo_ine 1001 int
- WHEN canonicalize
- THEN "01001".
