# Design: mongo-hardening

## Approach
- `mongo.py`: filtro str nan antes de float().
- `clean_mongo.py`: canonicalize en Python con zfill_ine + update_one solo si cambia; clean_all agrega etxebide_promociones/certificados/udalmap_extendido/ecvi/solicitudes/osrm/udalmap.
- `load_mongo.py`: construir docs en memoria, drop+insert solo si docs>0; provenance con _provenance_from_raw_meta en base.
- `mongo_aggregations.py`: pipeline_top con $match/$sort/$limit; indicador_por_municipio con $match _id.
- Tests parametrizados 13 colecciones; test_clean usa _demo.
