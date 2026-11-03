# Spec: fase-mongodb-mejora

## Requirements
- R1: `_id` debe ser `codigo_ine` en `municipios`, `alquiler_municipal`, `indicadores`.
- R2: `idw_vecinos` se almacena como texto/array, no entero.
- R3: `tiene_alquiler_oficial` se deriva de `metodo_imputacion='oficial'` o `nivel_geografico='municipal'`.
- R4: Colecciones huérfanas disponibles se cargan idempotentemente en Mongo.
- R5: Pipelines analíticos usan joins por `codigo_ine`.
- R6: Índices clave tienen `explain()` documentado.
- R7: Tests Mongo cubren nuevas colecciones y refactor.
