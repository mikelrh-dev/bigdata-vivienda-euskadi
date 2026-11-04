# Proposal: renta-joven-18-34

## Intent

Adoptar 18-34 como canonico de renta y emancipacion (OVJ y Gaztelagun 18-35) sin falsificar paro ni poblacion municipal. Migrar aditivo.

## Scope

### In Scope
- Contrato y calculos: renta_18_34, _18_24, _25_34 con ponderacion explicita CAE
- Campos nuevos en paralelo conservando _16_29 como legacy
- Recalculo de esfuerzo_*_18_34 y poblacion_18_34_est etiquetada
- Dashboards y Mongo con alias legacy

### Out of Scope
- Paro 30-34 y poblacion fina de 5 anos (sin fuente con bandas fines)
- Salario municipal por edad y emancipacion municipal (fuera de fuentes)
- Stock VPO historico

## Capabilities

### New Capabilities
- Ninguna.

### Modified Capabilities
- contrato-reto: indicador canonico pasa a renta_18_34 con subgrupos CAE
- mongodb-y-analisis: esfuerzo y poblacion con nuevos campos

## Approach

Enmendar contrato primero, anadir campos nuevos sin renombrar legacy, recalcular run_all y Mongo, verificar. Paro con bandas reales.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| openspec/specs/contrato-reto/spec.md | Modified | Canonico 18-34 |
| config/parametros_estudio.yaml | Modified | Formula 18plus con ratio 18-34 |
| transform/calcular_renta_joven.py | Modified | Ratios 18-34/18-24/25-34 |
| transform/generar_analisis_variables_base.py | Modified | Esfuerzo 18-34 y subgrupos |
| transform/generar_poblacion_joven_municipal.py | Modified | Poblacion 18-34 est |
| storage/load_mongo.py | Modified | Cargar nuevos campos |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Falacia ecologica con escalar unico | High | Etiquetado CAE, no municipal por edad |
| Cambio de nivel del esfuerzo | Med | Mantener legacy y recalcular umbrales |
| Rotura de 9 scripts y tests | High | Alias legacy y verificacion completa |
| Ponderacion ambigua | Med | Fijar ponderada por anchura en contrato |

## Rollback Plan

Revertir commit; legacy _16_29 conservado en Mongo y silver hasta archive.

## Dependencies

- Ninguna externa, Eustat bandas quinquenales CAE ya en raw

## Success Criteria

- [ ] Contrato dice 18-34 y subgrupos CAE origen
- [ ] Campos _18_34 coexisten con _16_29
- [ ] pytest 109+ verde y verificar_fase_datos PASS
- [ ] Mongo tiene esfuerzo_18_34 sin borrar legacy
