# Modelo de datos MongoDB — vivienda_euskadi

Base de datos: `vivienda_euskadi` (MongoDB local, `localhost:27017`).
Fuente silver: `data/procesado/`. Loader: `storage/load_mongo.py`.

## Colecciones

| Colección | Documentos | `_id` | Propósito |
|---|---|---|---|
| `municipios` | 252 | `codigo_ine` (string 5 dígitos) | Dimensión maestra municipal (demografía, empleo, vivienda, transporte, demanda). |
| `anuncios` | 759 | `ObjectId` | Anuncios de alquiler unificados (portales). |
| `alquiler_municipal` | 252 | `ObjectId` | Alquiler municipal oficial (y secciones si se cargan). |
| `indicadores` | 252 | `ObjectId` | Variables analíticas base por municipio. |

## Embedding vs referencing

- **Embed en `municipios`**: demografía, empleo, contexto vivienda, demanda social, transporte resumen. Se leen juntos y cambian poco.
- **Embed en `anuncios`**: `ubicacion`, `equipamiento[]`, `auditoria`, `historico_precios[]`.
- **Referenciar por `codigo_ine`**: `anuncios.ubicacion.codigo_ine -> municipios._id`; `alquiler_municipal.codigo_ine -> municipios._id`.
- **No denormalizar** indicadores calculados (`n_anuncios`, `esfuerzo_*`): se generan en aggregation (`analysis/mongo_aggregations.py`).

## Tipos BSON

- `_id` municipio: string 5 dígitos.
- Dinero: `Decimal128` (`precio_eur`).
- Contadores: `int`.
- Tasas/distancias: `double`.
- Booleanos: BSON bool.
- Fechas: `Date`; años: `int`.
- Arrays: `equipamiento: [string]`, `historico_precios: [object]`, `variantes: [string]`.
- Geo: GeoJSON Point en `ubicacion.coordenadas` (índice 2dsphere, sparse).

## Índices

- `anuncios`: `{ ubicacion.codigo_ine: 1, modalidad: 1, precio_eur: 1 }` (ESR).
- `anuncios`: `{ ubicacion.coordenadas: "2dsphere" }` (sparse).
- `anuncios`: `{ portal: 1, id_anuncio: 1 }` único.
- `anuncios`: `{ equipamiento: 1 }` multikey.
- `municipios`: `{ territorio: 1, nombre_canonico: 1 }`.
- `alquiler_municipal`: `{ codigo_ine: 1, distrito: 1, nivel_geografico: 1 }`.

Efecto demostrado con `explain("executionStats")` en `analysis/mongo_indexes.py`
(COLLSCAN -> IXSCAN, reducción de `totalDocsExamined`).

## Shard key (conceptual)

Candidato: `ubicacion.codigo_ine` hashed para `anuncios`. Riesgo: solo 252 valores y
distribución desigual. A escala actual no es necesario; se documenta como decisión
conceptual. Replica sets: PRIMARY/SECONDARY, oplog, failover; sharding: mongos,
config servers, shards, ranged vs hashed shard key.

## Transacciones

No se requiere transacción multidocumento en el flujo principal. La carga usa
`update_one(..., upsert=True)`, atómica a nivel de documento. Si se denormalizara
una mediana municipal habría caso de transacción; el modelo evita esa
denormalización. Atomicidad documental suficiente.

## Validación de esquema

No se aplica JSON Schema validation: los datos provienen de un pipeline controlado
y la validación se hace en tests (`tests/test_mongo.py`). Decisión justificada por
simplicidad y porque los campos son heterogéneos (sparse).

## Limpieza

`storage/clean_mongo.py` aplica `update_many`, `$set`, `$unset`, `$convert`,
marcado explícito de nulos y resolución de duplicados, con contadores
(`matched_count`, `modified_count`, `deleted_count`).
