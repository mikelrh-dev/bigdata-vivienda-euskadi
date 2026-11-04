# Spec: mongo-consolidacion

## Requirements
- R1: El sistema SHALL cargar `certificados_energeticos` con 252 documentos y `_id=codigo_ine`.
- R2: El sistema SHALL derivar `codigo_ine` en `etxebide_promociones` desde `Cod_Prov`+`CODMUNI`.
- R3: El sistema SHALL aplicar `canonicalize_codigo_ine` y `mark_nulls` a `udalmap_extendido` y `etxebide_promociones`.
- R4: El sistema SHALL proveer agregaciones de ≥4 etapas que combinen `municipios+udalmap_extendido+osrm` y `etxebide_promociones por municipio/estado/tipología`.
- R5: El sistema SHALL crear índices justificados en colecciones nuevas y demostrar `explain()` COLLSCAN→IXSCAN.
- R6: La transformación VPO SHALL ocurrir en MongoDB y quedar persistida/documentada; el stock histórico no público SHALL documentarse como "sin dato".
- R7: Tests y docs SHALL cubrir nuevas colecciones/pipelines.

#### Scenario: Certificados cargados
- GIVEN `cert_energetico_municipal_252.csv`
- WHEN se ejecuta `load_certificados()`
- THEN `certificados_energeticos` tiene 252 docs con `_id` de 5 dígitos.

#### Scenario: Promociones con join
- GIVEN `etxebide_promociones` con `Cod_Prov`/`CODMUNI`
- WHEN se deriva `codigo_ine`
- THEN ≥95% docs tienen `codigo_ine` válido de 5 dígitos.

#### Scenario: Agregación combina fuentes
- GIVEN municipios + udalmap_extendido + osrm
- WHEN se ejecuta el pipeline
- THEN usa ≥4 etapas distintas y devuelve indicador por municipio.
