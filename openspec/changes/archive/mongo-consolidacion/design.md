# Design: mongo-consolidacion

## Approach
- `load_certificados()`: lee `data/procesado/cert_energetico_municipal_252.csv`, `_id=codigo_ine`, ints para conteos, `cert_moda` string, `fecha_carga`. Upsert idempotente. Fuente agregada verificada (raw completo demasiado pesado para Mongo doc-a-doc).
- `load_etxebide_promociones()`: refactor — deriva `codigo_ine = Cod_Prov.zfill(2)+CODMUNI.zfill(3)`, valida contra dim (5 dígitos), conserva `_id=ID_PROM_idx`. Añade `codigo_ine`, `num_viviendas int`, `fecha_carga`.
- `clean_mongo.py`: extiende `canonicalize` a `udalmap_extendido/etxebide_promociones/ecvi/solicitudes/osrm/emancipacion/certificados`; `mark_nulls` para campos nuevos (cert moda, promo estado/tipología).
- `mongo_aggregations.py`: fix `pipeline_accesibilidad_extendida` (ejecutar aggregate, no devolver lista de etapas); añade `pipeline_vpo_por_municipio()` (`$match/$group/$lookup/$project/$sort` + `$facet` opcional) y `pipeline_udalmap_extendido_osrm()`.
- `mongo_indexes.py`: índices `certificados(_id)`, `udalmap_extendido(_id)`, `etxebide_promociones(codigo_ine,EstadoObra,Tipologia)`; `explain_before_after` para promo por municipio.
- Docs: actualizar `modelo_mongodb.md` (12 col.), reescribir `informe_capacidad_mongo.md` (reclasifica C5/D2/C1/B5/C3/C6/D5/E1-E3).
