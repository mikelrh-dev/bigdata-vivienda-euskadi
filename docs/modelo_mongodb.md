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

MongoDB hecho: 13 colecciones cargadas con PyMongo (`storage/load_mongo.py` vía `storage/load_mongo.py`), limpieza (`storage/clean_mongo.py`), índices (`analysis/mongo_indexes.py`, ESR/2dsphere/multikey con `explain()`), 8 pipelines en `analysis/mongo_aggregations.py` (`pipeline_indicadores_municipio`, `pipeline_alquiler_por_municipio`, `pipeline_modalidades`, `pipeline_top_municipios_por_esfuerzo`, `pipeline_esfuerzo_por_sexo`, `pipeline_accesibilidad_extendida`, `pipeline_udalmap_extendido_osrm`, `pipeline_vpo_por_municipio`).

Comandos: `.venv/Scripts/python.exe storage/load_mongo.py`, `.venv/Scripts/python.exe scripts/run_mongo_pipeline.py`, `.venv/Scripts/python.exe analysis/run_analisis_mongo.py`, `.venv/Scripts/python.exe -m pytest tests/test_mongo*.py -q` (en particular `tests/test_mongo_geo.py` y `tests/test_mongo_comparativa.py`).

CSVs en `data/resultados/`: `mongo_esfuerzo_por_municipio.csv` (252 filas), `mongo_alquiler_por_municipio.csv` (252), `mongo_modalidades.csv` (2), `comparativa_3_municipios_mongo.csv` (3: Bilbao 173, Donostia 113, Getxo 40). Robustos reales con n mayor o igual a 30: 4 (Bilbao, Donostia, Getxo, Vitoria-Gasteiz). GeoJSON: 424 Point en `anuncios.ubicacion.coordenadas` con índice 2dsphere.
