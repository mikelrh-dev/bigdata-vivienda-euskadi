# Proposal: mongo-consolidacion

## Intent
Consolidar la capa MongoDB (solo datos): cerrar C5 con certificados, dar pipelines/índices/clean a las colecciones nuevas (udalmap_extendido, etxebide_promociones), resolver C1 vía agregación Mongo y re-baselinar el informe de capacidad. Sin HDFS/Kafka/RA4.

## Scope
### In Scope
- Loader `certificados_energeticos` (252, `_id=codigo_ine`) desde `cert_energetico_municipal_252.csv`.
- Enriquecer `etxebide_promociones` con `codigo_ine` derivado (`Cod_Prov`+`CODMUNI`).
- Clean extendido: `canonicalize_codigo_ine` + `mark_nulls` para colecciones nuevas.
- Pipelines: `udalmap_extendido+osrm`, `etxebide_promociones por municipio/estado/tipología`, fix `pipeline_accesibilidad_extendida` (debe ejecutar `aggregate`).
- Índices compuestos + `explain()` documentado para nuevas colecciones.
- Informe capacidad Mongo actualizado + `modelo_mongodb.md` + tests.

### Out of Scope
- Udalmap ampliado 10-15 (valor marginal), Padrón INE joven (opcional futuro), HDFS/Kafka, gráficos RA4, nuevas extracciones externas.

## Capabilities
### Modified Capabilities
- `mongodb-y-analisis`: nuevas colecciones consultables, agregaciones e índices.

## Approach
Loaders idempotentes con upsert, agregaciones en Mongo (no en CSV) para VPO, clean con contadores, explain before/after.

## Risks
- `CODMUNI` sin match a dim (derivar + validar, resto "sin dato").
- Raw inmutable: solo lectura de `data/raw` y `data/procesado`, escritura solo en Mongo.

## Rollback Plan
Revertir commit; recargar Mongo desde silver (`storage.load_mongo`).

## Success Criteria
- [ ] `pytest tests/test_mongo.py -q` verde.
- [ ] `certificados_energeticos`=252, `etxebide_promociones`=406 con `codigo_ine`.
- [ ] Pipelines nuevas + explain documentado.
- [ ] Informe capacidad reclasifica C5/D2/C1.
