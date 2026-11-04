# Proposal: fuentes-validacion

## Intent

Validar con join real 3 fuentes candidatas antes de crear extractores: población fina 15-29 (Eustat), renta por edad municipal (Eustat) y stock Alokabide. Sin join no hay extractor.

## Scope

### In Scope
- Script scripts/validar_fuentes_nuevas.py con comprobaciones DuckDB sin escribir raw.
- Informe openspec/audit/validacion_fuentes_2026-11-04.md con cobertura por fuente.
- Tests de validación en tests/test_fuentes_validacion.py.

### Out of Scope
- Nuevos extractores de producción, Mongo, Kafka, HDFS, scraping Nivel2.

## Capabilities

### New Capabilities
- Ninguna.

### Modified Capabilities
- extraccion-datos: EXTRACCION-02 y COMPLEMENTARIOS-01 con gate de join previo.

## Approach

Comprobar sobre CSV existentes qué bandas y ambitos trae cada tabla, contar municipios alcanzados contra dim 252 y decidir alta/baja con evidencia.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| scripts/validar_fuentes_nuevas.py | New | Comprobaciones de cobertura |
| openspec/audit/validacion_fuentes_2026-11-04.md | New | Informe de validación |
| tests/test_fuentes_validacion.py | New | Tests del gate |
| openspec/specs/extraccion-datos/spec.md | Modified | DELTA de gate de join |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Falso positivo sin join | Med | Contar municipios con codigo_ine antes de prometer |
| Fuente no pública con esa granularidad | High | Marcar sin dato y no imputar |

## Rollback Plan

Borrar script, informe y test. Sin efecto sobre raw ni Mongo.

## Dependencies

- Ninguna externa, solo ficheros raw ya cargados.

## Success Criteria

- [ ] Cada fuente queda clasificada alta o baja con conteo de municipios.
- [ ] Ninguna promesa sin join queda como dato.
- [ ] pytest 109+ verde y verificar_fase_datos PASS.
