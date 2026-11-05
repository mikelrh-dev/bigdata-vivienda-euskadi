# Modelo de datos MongoDB — vivienda_euskadi

Base de datos: `vivienda_euskadi` (MongoDB local, `localhost:27017`).
Fuente silver: `data/procesado/`. Loader: `storage/load_mongo.py`.

## Colecciones

| Colección | Documentos | `_id` | Propósito |
|---|---|---|---|
| `municipios` | 252 | `codigo_ine` | Dimensión maestra municipal. |
| `anuncios` | 759 | `ObjectId` | Anuncios unificados (`ubicacion.codigo_ine` + `equipamiento[]`). |
| `alquiler_municipal` | 252 | `codigo_ine` | Alquiler oficial Eustat + imputación. |
| `indicadores` | 252 | `codigo_ine` | Variables analíticas base. |
| `ecvi_compraventa` | 29 | `{codigo_ine}_{trimestre}` | Compraventa por área funcional (F5). |
| `udalmap_indicadores` | 252 | `codigo_ine` | Udalmap adicional (B5/C3/C6/D5/E1-E3). |
| `udalmap_empleo` | 252 | `codigo_ine` | Empleo Udalmap corregido. |
| `osrm_tiempos` | 252 | `codigo_ine` | Tiempos OSRM a capitales (D3). |
| `emancipacion_juventud` | 1 | `resumen` | Emancipación CAE (G4, solo territorial). |
| `etxebide_solicitudes` | 5040 | `{codigo_ine}_{anio}` | Solicitudes Etxebide (C1). |
| `udalmap_extendido` | 252 | `codigo_ine` | 6 indicadores alto valor (123/150/30/38/67/15). |
| `etxebide_promociones` | 406 | `ID_PROM_idx` + `codigo_ine` derivado | Promociones VPO por municipio/estado/tipología (C1). Stock histórico no público → "sin dato". |
| `certificados_energeticos` | 252 | `codigo_ine` | Agregado municipal A-G + moda (C5). |

## Embedding vs referencing

- **Embed en `municipios`**: demografía, empleo, contexto vivienda, demanda social, transporte resumen. Se leen juntos y cambian poco.
- **Embed en `anuncios`**: `ubicacion`, `equipamiento[]`, `auditoria`, `historico_precios[]`.
- **Referenciar por `codigo_ine`**: `anuncios.ubicacion.codigo_ine`, `alquiler_municipal._id`, `certificados_energeticos._id`, `udalmap_extendido._id`, `osrm_tiempos._id -> municipios._id`; `etxebide_promociones.codigo_ine -> municipios._id` (derivado `Cod_Prov+CODMUNI`).
- **No denormalizar** indicadores calculados (`n_anuncios`, `esfuerzo_*`): se generan en aggregation (`analysis/mongo_aggregations.py`).

## Tipos BSON

- `_id` municipio: string 5 dígitos.
- Dinero: `Decimal128` (`precio_eur`).
- Contadores: `int`.
- Tasas/distancias: `double`.
- Booleanos: BSON bool.
- Fechas: `Date`; años: `int`.
- Arrays: `equipamiento: [string]`, `historico_precios: [object]`, `variantes: [string]`.
- Geo: GeoJSON Point en `ubicacion.coordenadas` (índice 2dsphere, sparse): 424 de 759 anuncios con `{"type":"Point","coordinates":[lon,lat]}` real desde `anuncios_fotocasa_enriquecido.csv` por `id_anuncio` (portal `fotocasa`); el resto `None` por falta de silver.

## Índices

- `anuncios`: `{ ubicacion.codigo_ine: 1, modalidad: 1, precio_eur: 1 }` (ESR).
- `anuncios`: `{ ubicacion.coordenadas: "2dsphere" }` (sparse).
- `anuncios`: `{ portal: 1, id_anuncio: 1 }` único.
- `anuncios`: `{ equipamiento: 1 }` multikey.
- `municipios`: `{ territorio: 1, nombre_canonico: 1 }`.
- `alquiler_municipal`: `{ codigo_ine: 1, distrito: 1, nivel_geografico: 1 }`.
- `etxebide_promociones`: `{ codigo_ine: 1, estado_obra: 1, tipologia: 1 }` (consultas C1 por municipio/estado/tipo).
- `certificados_energeticos`: `{ cert_moda: 1 }` (ranking C5 por clase).
- `udalmap_extendido`: `{ _id: 1 }` (joins D2/accesibilidad).

Efecto demostrado con `explain("executionStats")` en `analysis/mongo_indexes.py`
(COLLSCAN -> IXSCAN, reducción de `totalDocsExamined`).

## Shard key (conceptual)

Candidato: `ubicacion.codigo_ine` hashed para `anuncios` y `codigo_ine` hashed para
`etxebide_promociones`. Riesgo: solo 252 valores y distribución desigual (Bilbao/Donostia
concentran anuncios y promociones). A escala actual no es necesario; se documenta como
decisión conceptual. Replica sets: PRIMARY/SECONDARY, oplog, failover; sharding: mongos,
config servers, shards, ranged vs hashed shard key.

## Transacciones

No se requiere transacción multidocumento en el flujo principal. La carga usa
`update_one(..., upsert=True)` / `insert_many` tras `drop()` y el patrón
staging + backup + rename de `replace_collection`, todo atómico a nivel de
documento. Si se denormalizara una mediana municipal o el conteo VPO por municipio
en `municipios`, habría caso de transacción (commit/abort); el modelo evita esa
denormalización y calcula en agregación (`pipeline_vpo_por_municipio`).

La atomicidad documental queda demostrada por código en
`storage/mongo.py:marcar_calidad_municipio`, que actualiza el flag
`calidad_datos` de un municipio con `find_one_and_update` y
`ReturnDocument.AFTER`: lectura, modificación y escritura ocurren en una sola
operación atómica sobre un único documento y el documento devuelto ya incluye
el valor nuevo. El test `test_atomicidad_documental`
(`tests/test_mongo_consistencia.py`) lo verifica contra la base de test
`vivienda_euskadi_test`, sin tocar la base productiva.

No se fuerza replica set: la atomicidad de un único documento no lo exige
(en standalone local basta) y una transacción multidocumento real sí lo
requeriría; al no haber escritura multidocumento que deba ser toda o nada,
el replica set no aporta nada en este modelo. Ejemplo plausible que sí lo
justificaría: denormalizar en `municipios` el conteo de anuncios y la fecha
de última carga junto con el borrado de anuncios obsoletos en una misma
operación de negocio.

Además, `load_all` ya no silencia errores de índices: si `ensure_indexes`
falla (p. ej. clave duplicada), registra el error con `logging` y relanza
con mensaje en lugar de `except: pass` (`test_load_all_no_silencia_indices`).

## Validación de esquema

No se aplica JSON Schema validation: los datos provienen de un pipeline controlado
y la validación se hace en tests (`tests/test_mongo.py`: conteos por rangos,
`codigo_ine` 5 dígitos, `cert_moda == max(distribucion)`, `esfuerzo_joven_pct` alias,
provenance `fuente/anio_fuente`). Decisión justificada por simplicidad y porque los
campos son heterogéneos (sparse, `NumViviendas` vacío en origen).

## Limpieza

`storage/clean_mongo.py` aplica `update_many`, `$set`, `$unset`, `$convert`,
marcado explícito de nulos y resolución de duplicados, con contadores
(`matched_count`, `modified_count`, `deleted_count`).

## Pipelines y reproducibilidad (Tema 8, secciones 14 y 16)

MongoDB hecho: 16 colecciones cargadas con PyMongo (`storage/load_mongo.py` vía `storage/load_mongo.py`), limpieza (`storage/clean_mongo.py`), índices (`analysis/mongo_indexes.py`, ESR/2dsphere/multikey con `explain()`), 8 pipelines en `analysis/mongo_aggregations.py` (`pipeline_indicadores_municipio`, `pipeline_alquiler_por_municipio`, `pipeline_modalidades`, `pipeline_top_municipios_por_esfuerzo`, `pipeline_esfuerzo_por_sexo`, `pipeline_accesibilidad_extendida`, `pipeline_udalmap_extendido_osrm`, `pipeline_vpo_por_municipio`). La coleccion `vpo_municipal` (252) guarda el flujo oficial de VPO terminada del indicador 73; no es stock.

Comandos: `.venv/Scripts/python.exe storage/load_mongo.py`, `.venv/Scripts/python.exe scripts/run_mongo_pipeline.py`, `.venv/Scripts/python.exe analysis/run_analisis_mongo.py`, `.venv/Scripts/python.exe -m pytest tests/test_mongo*.py -q` (en particular `tests/test_mongo_geo.py` y `tests/test_mongo_comparativa.py`).

CSVs en `data/resultados/`: `mongo_esfuerzo_por_municipio.csv` (252 filas), `mongo_alquiler_por_municipio.csv` (252), `mongo_modalidades.csv` (2), `comparativa_3_municipios_mongo.csv` (4: Bilbao 173, Donostia 113, Getxo 40, Vitoria-Gasteiz 39). Robustos reales con n mayor o igual a 30: 4 (Bilbao, Donostia, Getxo, Vitoria-Gasteiz). GeoJSON: 424 Point en `anuncios.ubicacion.coordenadas` con índice 2dsphere.

## Evidencia explain antes/después (INDICES-01, Bloque 3)

Consulta real justificativa (ESR):

- `{"ubicacion.codigo_ine": "48001", "modalidad": "larga_estancia", "precio_eur": {"$lte": "Decimal128(1000)"}}`

Índice ESR medido (creado en `analysis/mongo_indexes.py:ensure_indexes` y `explain_before_after`):

- `{"ubicacion.codigo_ine": 1, "modalidad": 1, "precio_eur": 1}` (`idx_anuncios_ine_modalidad_precio`)

Salida registrada (`python -c "from analysis.mongo_indexes import explain_before_after"` y `python analysis/run_analisis_mongo.py`, MongoDB `localhost:27017` `vivienda_euskadi`):

- Antes (sin índice ESR): `COLLSCAN`, `nReturned=1`, `totalDocsExamined=759`, `totalKeysExamined=0`.
- Después (con índice ESR): `IXSCAN`, `nReturned=1`, `totalDocsExamined=1`, `totalKeysExamined=1`.

Esto es `COLLSCAN -> IXSCAN` con `totalDocsExamined=1` tras el índice ESR y `nReturned=1` documentado. La transición se reproduce con `explain_before_after()` (elimina el índice, ejecuta `explain("executionStats")`, crea el índice y vuelve a ejecutar `explain`). La salida de `analysis/run_analisis_mongo.py` imprime las dos líneas `explain before` / `explain after` y el filtro usado.

Se verifica también en `tests/test_mongo_indices.py::test_indexes_explain_totalDocsExamined` (`before.stage == COLLSCAN`, `after.stage == IXSCAN`, `before.totalDocsExamined > after.totalDocsExamined`).

## Índices geo, multikey y parcial (INDICES-01)

- Geo `2dsphere` sparse: `anuncios: {"ubicacion.coordenadas": "2dsphere"}` (sparse). Consulta real justificativa: `{"ubicacion.coordenadas": {"$near": {"$geometry": {"type": "Point", "coordinates": [-2.94, 43.26]}, "$maxDistance": 5000}}}` (anuncios próximos a un punto, p. ej. Bilbao) y conteos por `{"ubicacion.coordenadas": {"$type": "object"}}`. Sin el índice 2dsphere esa búsqueda `$near` no puede usar índice espacial; con él, `explain` muestra `IXSCAN` sobre la proyección geoespacial. El campo es GeoJSON Point con `coordinates: [lon, lat]` (ver § Tipos BSON y § Backups).
- Multikey en `equipamiento`: `anuncios: {"equipamiento": 1}` (multikey, porque `equipamiento` es un array de strings). Consulta real justificativa: `{"equipamiento": "ascensor"}` o `{"equipamiento": {"$all": [...]}}` / `{"$in": [...]}` (`analysis/mongo_queries.py:anuncios_con_equipamiento`, `anuncios_array_all`). Sin índice multikey, la búsqueda por un elemento del array sería `COLLSCAN`; con él, puede resolver el elemento indexado.
- Parcial: evaluado y rechazado para índice nuevo sin consulta real. Se evaluó un índice parcial del tipo `{"precio_eur": 1}` con `partialFilterExpression: {"precio_eur": {"$ne": null}}` o `{"ubicacion.coordenadas": "2dsphere"}` parcial solo para anuncios con geo, pero no se creó índice parcial nuevo porque no hay una consulta real medible con `explain` que lo exija sobre el conjunto actual (759 documentos): la consulta ESR y la geo ya quedan cubiertas por el compuesto ESR y el 2dsphere sparse. Decisión: parcial evaluado/rechazado documentado (Known Limits de `design.md`), no índice creado.

Palabra clave para búsqueda: `2dsphere` (geo), `multikey` (`equipamiento`), `parcial` (evaluado y rechazado).

## §5 Preguntas docx literales (MODELO-01)

Preguntas literales del docx §5 con respuesta justificada. Se vuelcan literalmente y se responde cada una; la decisión embedding/referencing queda en § Embedding vs referencing.

1. ¿qué información se consulta normalmente junta? Se embebe en `municipios` la demografía, el empleo, el contexto de vivienda y la demanda social porque se leen juntas en `pipeline_indicadores_municipio` y cambian poco; se embebe en `anuncios` la `ubicacion`, el `equipamiento[]` y la `auditoria` por el mismo motivo.
2. ¿qué información cambia con frecuencia? Los anuncios y su `historico_precios[]` cambian con frecuencia (precio, modalidad, superficie), por eso `anuncios` es la colección volátil y usa upsert por `(portal, id_anuncio)`, mientras `municipios` (dimensión) cambia poco.
3. ¿qué arrays podrían crecer sin límite? `historico_precios[]` en `anuncios` podría crecer sin límite si se acumula cada cambio de precio; está embebido hoy como lista vacía y se vigila (si supera un umbral, se extrae a colección propia aunque hoy no crece). `equipamiento[]` y `variantes[]` también son arrays, pero no crecen sin límite (`equipamiento` es un vocabulario cerrado).
4. ¿hay información que se repite pero interesa conservar como fotografía histórica? Sí: la procedencia (`fuente`, `anio_fuente`, `fecha_carga`) se repite en cada documento para conservar la fotografía histórica del silver de origen aunque el valor municipal cambie; se conserva como copia embebida deliberada y no se deduplica.
5. ¿qué relaciones son 1:1, 1:N o N:M? `municipios` 1:N `anuncios` (un municipio tiene muchos anuncios, `anuncios.ubicacion.codigo_ine -> municipios._id`); `municipios` 1:1 con `alquiler_municipal` y `indicadores` (mismo `_id=codigo_ine`); `etxebide_promociones` N:M con `municipios` vía `codigo_ine` derivado (muchos municipios, muchas promociones). No se usa N:M embebido: se referencia por `codigo_ine`.
6. ¿qué campos se usarán para relacionar información procedente de fuentes distintas? El `codigo_ine` de 5 dígitos como clave primaria de `municipios` y clave foránea canónica (`anuncios.ubicacion.codigo_ine`, `alquiler_municipal._id`, `etxebide_promociones.codigo_ine` derivado de `Cod_Prov+CODMUNI`, `osrm_tiempos._id`, `udalmap_extendido._id`), más `(portal, id_anuncio)` como identidad de anuncio para upsert entre portales.
7. ¿qué tipos BSON son adecuados para fechas, importes, identificadores, booleanos o arrays? Fechas: `Date`; importes: `Decimal128` (`precio_eur`); identificadores: `string` 5 dígitos para `codigo_ine` y `ObjectId` para `anuncios._id`; booleanos: BSON `bool`; arrays: BSON `array` (`equipamiento`, `historico_precios`, `variantes`) con índice multikey sobre `equipamiento`.

## Backups y geo (RESPALDO-01, Bloque 3)

Backups vía `replace_collection` (`storage/mongo.py`): staging + `<name>__backup` + rename; nunca `drop()` directo sobre prod. Secuencia exacta en `replace_collection`: limpiar y cargar `__staging` (`<name>__staging`); si ya existe `<name>`, volcarlo a `<name>__backup` con `$out` (previo a nuevo); renombrar `__staging` a `<name>` con `dropTarget=True`. Nunca se hace `drop()` directo sobre la colección productiva (eso dejaría ventana sin datos y perdería el backup). El loader usa `replace_collection` para `municipios`, `alquiler_municipal`, `indicadores` y resto de colecciones municipales; `anuncios` usa upsert por `(portal, id_anuncio)` porque llega por Kafka.

Listing de lectura pura (sin escrituras, `db.getCollectionNames()` sobre `vivienda_euskadi`, 2026-11-05): `alquiler_municipal, anuncios, certificados_energeticos, ecvi_compraventa, emancipacion_juventud, etxebide_promociones, etxebide_solicitudes, indicadores, indicadores__backup, municipios, municipios__backup, osrm_tiempos, udalmap_empleo, udalmap_extendido, udalmap_indicadores, vpo_municipal` (16 colecciones).

Con recuentos medidos el mismo día: `anuncios` 759, `municipios` 252, `indicadores` 252, `municipios__backup` 252 e `indicadores__backup` 252.

Geo: 424 Point GeoJSON reales en `anuncios.ubicacion.coordenadas` (`{"type":"Point","coordinates":[lon,lat]}`), el resto `None` por falta de silver. Origen: `anuncios_fotocasa_enriquecido.csv` por `id_anuncio` (portal `fotocasa`, 424 de 759). Medición: `db.anuncios.countDocuments({"ubicacion.coordenadas": {"$type": "object"}})` devuelve 424 y `db.anuncios.countDocuments({"ubicacion.coordenadas": null})` devuelve 335. El resto `None` es falta de silver (sin coordenadas), no error: el índice 2dsphere es sparse y admite documentos sin campo geo.

## §11 Transacciones — READ justificado en standalone

Máquina: MongoDB local standalone (sin replica set), `localhost:27017`. Decisión READ (docx `§11`, TRANSACCIONES-01): se documenta READ justificado en standalone porque sin replica set no hay commit/abort multidocumento. Forzar replica set sobre un standalone local no se hace en este Bloque: la atomicidad de un documento no lo exige.

Atomicidad documental de `marcar_calidad_municipio` (`storage/mongo.py`): la actualización es `find_one_and_update` con `ReturnDocument.AFTER` sobre un único documento, verifica el valor de dominio y devuelve el documento ya actualizado sin estado intermedio. El test `test_atomicidad_documental` lo verifica en `vivienda_euskadi_test`, con `MONGO_ALLOW_DESTRUCTIVE` sin definir (prod intacta por defecto, conteo 759 invariante).

Sonda commit/abort solo en `vivienda_euskadi_test`: la transacción multidocumento real sí exigiría replica set y no se fuerza; si el servidor standalone la rechaza, la sonda la captura, limpia la colección de prueba y deja prod en 759. Ejemplo plausible que sí justificaría commit/abort con replica set: denormalizar en `municipios` el conteo de anuncios y la fecha de última carga junto con el borrado de anuncios obsoletos en una misma operación de negocio (todo o nada).

## Limpieza canónica (LIMPIEZA-01)

Función canónica única `clean_obsolete_fields` en `storage/clean_mongo.py`: `update_many(..., {"$unset": {...}})` que retorna `matched_count` / `modified_count` / `deleted_count`; mismo contrato en ambas colecciones (`anuncios` y `municipios`). `$unset` no borra documentos (`deleted_count=0`, 759 intacto); el contador se comprueba en test sobre `vivienda_euskadi_test` sin tocar prod por defecto.

## Agregación a CSV canónico (AGREGACION-01)

5 pipelines a CSV canónico en `data/resultados/` reutilizando los 8 pipelines de `analysis/mongo_aggregations.py` con `$group`/`$lookup`/`$unwind` donde los datos lo permiten, sin reimplementar agregaciones en el exportador:

- `mongo_esfuerzo_por_municipio.csv` desde `pipeline_indicadores_municipio` (252 filas).
- `mongo_alquiler_por_municipio.csv` desde `pipeline_alquiler_por_municipio` (252).
- `mongo_modalidades.csv` desde `pipeline_modalidades` (2).
- `mongo_accesibilidad_extendida.csv` desde `pipeline_accesibilidad_extendida` (252).
- `mongo_vpo_por_municipio.csv` desde `pipeline_vpo_por_municipio` (322).

El exportador general es `exportar_cinco_csv` / `exportar_csv` (`analysis/run_analisis_mongo.py`); `exportar_tres_csv` se mantiene por compatibilidad y delega en el general con `EXPORTS_3`.

## Excepciones tipadas (PYMONGO-01)

`storage/load_mongo.py:_money`, `storage/clean_mongo.py:_to_decimal` y `analysis/mongo_indexes.py:drop_demo_index` / `explain_*` usan `except (TypeError, ValueError)` con `logger.warning` (más `InvalidOperation` para `Decimal128` y `OperationFailure` para `drop_index`). `DuplicateKeyError` sigue propagándose (no se captura) y `load_all` relanza con mensaje si `ensure_indexes` falla.

