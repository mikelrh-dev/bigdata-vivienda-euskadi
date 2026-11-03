# Auditoría frontera Pandas → MongoDB — ¿overkill analítico? (2026-11-01)

Contexto: fase de Datos cerrada (Pandas). Silver de alta calidad (limpio, unificado,
imputado, con distancias). La rúbrica exige capacidades NATIVAS de MongoDB: modelo
(Embedding/Referencing), CRUD complejo PyMongo (limpieza, $set, $unset) y Aggregation
Pipeline de ≥4 etapas. MODO: solo análisis, sin cambios.

## 0. Veredicto

La Silver calcula los indicadores finales (esfuerzo, medianas, rankings). Si eso entra a
Mongo tal cual, el pipeline se queda en `$match` + `$sort` decorativo y se pierde el 20%
de Aggregation + parte del 15% de CRUD. Hay que desplazar la frontera: Pandas entrega
registros normalizados con identidad e integridad; Mongo calcula.

## 1. Frontera de transformación (Pandas vs Mongo)

Se QUEDA en Pandas (pre-requisito, no overkill):

- Normalización de tipos + `codigo_ine` 5 dígitos + UTF-8-sig. Sin esto Mongo hereda
  basura y el `$lookup` no casa. Higiénico, no puntuable.
- Dedup por `(portal, id_anuncio)` + `property_fingerprint`. Integridad + idempotencia
  del `upsert` Kafka. Quitarlo sería un tiro en el pie.
- Cuarentena dura (lo físicamente imposible: `superficie<10`, `pm2>100`, `codigo_ine`
  fuera de dim). Criterio de aceptación del productor, defendible.
- Nulos con flag + motivo (`motivo_precio_nulo`, `geo_invalida`, R1/R6/R8/R9).
  El flag es el parte de trabajo del `update_many`, no el trabajo hecho.

Se MUDA a PyMongo (hoy en Pandas = puntos perdidos):

| Hoy en `transform/` | Debe hacerse en Mongo con | Por qué puntúa |
|---|---|---|
| `filtrar_outliers.py` + `es_outlier_iqr`/`precio_m2_calc` en `unificar_anuncios.py` | `update_many` + `$set`/`$addFields` al cargar | CRUD-complejo (15%): `$set`, `$unset`, `matched/modified_count` |
| `imputar_nulos_fuentes.py` (medianas por provincia) | `update_many` con pipeline o `$set` tras `$group` previo | Limpieza PyMongo explícita de la rúbrica |
| `aplicar_cobertura_mercado.py` (`groupby codigo_ine → n_anuncios`, `fuente_mix`) | `$group` en pipeline | Aggregation real sobre brutos |
| `generar_mercado_area_funcional.py` (`groupby area_norm`) | `$group` por `area_funcional` + `$lookup` | Encadena 4+ etapas |
| `generar_analisis_variables_base.py:91-93` (`esfuerzo_hogar/joven_pct`, `alquiler_anual`) | `$addFields` con `$divide`/`$multiply` | El "indicador complejo" del 10 |
| `alquiler_municipal_completo.csv` (p25/p75/mediana/media + IDW) | NO cargar como tal; cargar grano fino y agregar con `$group` + `$percentile` | Si entra pre-agregada, el `$group` no demuestra nada |
| `parsear_secciones.py` (resumen min/max intra-municipal) | `$group` + `$min`/`$max` | Agregación genuina |

Regla de oro: si un CSV de `data/procesado/` ya responde una pregunta de negocio,
es masticado. Mongo recibe ingredientes, cocina respuestas.

Matiz sobre A1 (IQR en Pandas, 2026-11-01): no revertir; en el JSON queda como
`auditoria` (advisory/trazabilidad). En defensa decir explícito: "el flag IQR de
ingesta es diagnóstico; el cálculo calificable se rehace en Mongo".

## 2. Modelo BSON propuesto (3 colecciones)

**`municipios`** (252 docs, `_id = codigo_ine` string). Embebido: `nombre_canonico`,
`territorio`, `tipologia_mercado`, renta (objeto eustat/atlas/origen), empleo (tasas),
`distancias` (bilbao/donostia/vitoria km + capital_mas_cercana),
`localizacion: {type:"Point", coordinates:[lon,lat]}`. Justificación: se consulta
siempre junto, cambia poco, tamaño acotado; `_id = codigo_ine` facilita `$lookup`
y es shard-key candidato.

**`anuncios`** (759 docs, índice único `(portal, id_anuncio)`). Embebido: `ubicacion`
(codigo_ine, municipio, barrio, coordenadas GeoJSON), `equipamiento` (array, aunque
vacío — consultable con `$size`/`$all`), `auditoria` (flags ingesta),
`historico_precios: [{precio, fecha}]` — NO existe hoy y es oro: Kafka publica cambio
→ `$push` + `$set`; demuestra `$push`/`$set` y justifica análisis de atomicidad
(DOCX §11). Referenciado: solo `ubicacion.codigo_ine` (de ahí vive el `$lookup`).

**`alquiler_oficial`** (grano distrito/sección, NO el `completo` pre-agregado).
Separarla de `municipios` FUERZA el `$lookup` estrella; si se embebe, el pipeline se
queda sin lookup y se pierden puntos de "anidados + arrays + combinaciones". El IDW
y p25/p75 se generan dentro de Mongo o se documentan como fallback.

NO cargar: `analisis_variables_base.csv` (es el informe en CSV), `dim_municipios`
enriquecido redundante, `_filtrado` por portal (vistas, no entidades), dashboards
(salen de PyMongo — RA4 exige datos "directamente de consultas PyMongo").

## 3. Aggregations a migrar (Pandas/DuckDB → pipeline ≥4 etapas)

Pipeline 1 — ranking tasa de esfuerzo: `$match {larga_estancia, precio válido}` →
`$addFields {precio_m2}` → `$lookup municipios` → `$unwind` → `$lookup
alquiler_oficial` → `$group {_id, mediana_pm2 ($percentile), n, renta ($first)}` →
`$addFields {esfuerzo}` → `$sort` → `$limit`. 9 etapas, anidados + arrays + 2 lookups.

Pipeline 2 — temporal vs larga: `$match` → `$group {_id: {muni, modalidad}}` →
`$facet` → `$project` comparativa. Sustituye `groupby tipo_alquiler`.

Pipeline 3 — área funcional + accesibilidad: `$lookup` → `$group` por
`area_funcional` → `$sort` → `$project`; con `$geoNear` (índice `2dsphere`) gana
cruce espacial real y justifica índice + `explain()` IXSCAN (15% Índices).

Pipeline 4 (CRUD) — limpieza calificable: `update_many` nulos (`$set` + motivo),
`delete_many` justificado de lote prueba, comprobación `modified/deleted_count`;
fechas `Date`, importes `Decimal128` si se quiere nota alta.

## 4. Plan táctico: 3 directrices Pandas → Kafka

D1. Kafka publica el JSON canónico de `anuncios_unificados`, pelado de agregados:
1 anuncio = identidad (`portal`, `id_anuncio`, `property_fingerprint`) + `ubicacion`
completa + precio/superficie/habitaciones en bruto + `modalidad` + `equipamiento` +
`auditoria` solo con flags de ingesta. PROHIBIDO publicar `n_anuncios`, `esfuerzo_*`,
medianas o tipologías. Consumer: `update_one({portal, id_anuncio}, {$set, $push},
upsert=True)` → idempotencia reenviando el lote (Kafka 10).

D2. Dimensiones por colección propia, no en el mensaje. Renta/paro/distancias van en
carga inicial a `municipios` + `alquiler_oficial`. Si la renta viaja en el mensaje
Kafka, se mata el `$lookup` y sus puntos.

D3. Lista de cálculos prohibidos en Pandas (pasan al sprint Mongo): `precio_m2`
oficial, IQR calificable, `n_anuncios`, `fuente_mix`, agregados área funcional,
`esfuerzo_*`, `alquiler_anual`, p25/p75/medianas, resúmenes min/max de sección. La
silver actual queda como REFERENCIA de validación (contrastar cifras Mongo), no como
entrada.

## Decisiones (autorizadas 2026-11-01; Mongo NO iniciado, solo silver preparada)

1. `analisis_variables_base.csv`: INFORME DE REFERENCIA y validación cruzada. NO entra
   en Mongo. Sirve para comprobar que el pipeline Mongo da los mismos números, sin
   que el tribunal pueda decir que no se calculó en Mongo.
2. `alquiler_oficial`: grano fino original (Eustat distrito/sección: raw
   `alquiler_municipal.csv` 253 filas + `alquiler_seccion.csv` 1569 filas/159 mun).
   Los 93 sin dato se imputan con fallback DENTRO de la pipeline Mongo o se
   documentan. Mongo agrupa con `$group` obligatoriamente.
3. `historico_precios`: SÍ, array vacío desde el Día 1. Añadido a silver
   (`unificar_anuncios.py`, clave `historico_precios: []` en los 3 builders) para
   que el productor Kafka lo publique y el consumer practique `$push` + `$set`.
   D1 + D2 + D3 autorizadas.

## Contrato del loader Mongo (valla en código, no en papel — aplicar en sprint Mongo)

Doctrina: la silver es ORÁCULO de validación (implementación independiente y simple
que verifica a la compleja), no entrada ciega. El loader implementa allowlist con
proyección explícita + `assert` de que ningún `esfuerzo_*`, mediana o tipología entra
calculado. Si alguien carga de más, el test falla.

- `anuncios_unificados.json` → colección `anuncios`. ENTRAN: `portal`, `id_anuncio`,
  `property_fingerprint`, `precio_eur`, `superficie_m2`, `habitaciones`, `banos`,
  `titulo`, `subtitulo`, `modalidad`, `ubicacion.*`, `equipamiento`,
  `historico_precios`, `geo_invalida`, `es_outlier_superficie`. SE IGNORAN (recalcular
en Mongo): `auditoria.precio_m2_calc`, `auditoria.es_outlier_iqr` (diagnóstico).
  `auditoria.motivo_precio_nulo` SÍ entra como parte de limpieza documentada.
- `dim_municipios.csv` → colección `municipios`. ENTRAN: `codigo_ine` (como `_id`),
  `nombre_canonico`, `territorio`, `nombre_normalizado`, `variantes`,
  `tiene_alquiler_oficial`, `tiene_fianzas_emal`. SE EXCLUYEN: `n_anuncios`,
  `n_anuncios_raw`, `tipologia_mercado` (los genera el pipeline: `$group` + `$switch`).
- Grano fino alquiler → colección `alquiler_oficial`. ENTRAN: raw
  `alquiler_municipal.csv` (253 filas/distrito) + `alquiler_seccion.csv` (1569).
  NO entra `alquiler_municipal_completo.csv` ni `alquiler_seccion_resumen.csv`.
- Renta/empleo/distancias → embebidos en `municipios` desde sus silver de grano
  base (Eustat/Lanbide/B5M), nunca desde `analisis_variables_base.csv`.
- `analisis_variables_base.csv` = ORÁCULO. No se carga. Test futuro:
  `pipeline_mongo.esfuerzo == csv.esfuerzo` por municipio (tolerancia redondeo).
