# Proposal: 2026-11-15-regenerabilidad-y-orquestador-unico

## Intent

La auditoría v12 y la revisión de la cadena dejaron tres huecos:

1. `load_all()` carga 15 de las 17 colecciones vivas: `anuncios_habitaciones_unificados` y
   `anuncios_habitaciones_unificados_bigdata` no tienen loader, así que no son regenerables.
   Peor: si faltan, `exportar_habitaciones_csv` escribe un CSV sin filas sin fallar.
2. No existe un comando único que restaure todo menos raw: `--fase all` excluye Mongo a propósito.
3. No hay forma de demostrar «todo desde raw es regenerable» sin ejecutar una reconstrucción
   destructiva. La huella `983fa53f…` vive en un informe, no en un artefacto comprobable.

## Scope

### In Scope

- `load_habitaciones()` en `storage/load_mongo.py` y registro de las dos colecciones en `load_all`.
- Guarda de pipeline vacío en `exportar_habitaciones_csv`.
- Fase `full` en `scripts/run_pipeline.py` = `silver,quality,mongo,gold` (exige `--allow-mongo-write`).
- `scripts/verificar_reproducibilidad.py` + `docs/baseline_gold_sha256.json`.
- Ajuste del test que fija 15 colecciones.

### Out of Scope

- Reconstrucción end-to-end en sandbox (`--sandbox`): exigiría redirigir datos y BD.
- Gate `--vivo` real, fallback `noredirect` y verificación HDFS/Kafka: van en el change del lunes.
- Unificar las dos colecciones de habitaciones (deuda P3-19).
- Commit/push.

## Success Criteria

- [ ] `load_all()` devuelve 17 colecciones y coincide con `list_collection_names()` del Mongo local.
- [ ] `exportar_habitaciones_csv` falla si el pipeline nº 11 devuelve 0 filas.
- [ ] `run_pipeline.py --fase full --dry-run` lista silver, quality, mongo y gold en ese orden.
- [ ] `verificar_reproducibilidad.py` sale 0 con huella `983fa53f…` y 2 si no hay Mongo.
- [ ] Suite completa en verde (293 + los añadidos, 2 skipped).

## Rollback Plan

Revertir `storage/load_mongo.py`, `analysis/run_analisis_mongo.py`, `scripts/run_pipeline.py`,
el test ajustado y eliminar el script y el baseline. No toca datos, silver, Mongo ni HDFS.
