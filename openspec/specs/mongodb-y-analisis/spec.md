# MongoDB y análisis — Especificación

**Capacidad:** `mongodb-y-analisis`
**Estado:** Hecho, alineado con RA3 (modelado, CRUD, consultas, aggregation, índices, consistencia) e INDICES-01 y TRANSACCIONES-01
**Criterios cubiertos:** rúbrica v2 SBD-RA1 (integración, limpieza y
transformación, automatización) y SBD-RA3 (modelado, CRUD, consultas,
aggregation, índices, consistencia). Respaldo Tema 8 (extensión propia, no
criterio v2 directo): DISTRIBUIDA-01, PYMONGO-PRO-01 y VALIDACION-01
**Contrato:** `../contrato-reto/spec.md`
**Trazabilidad docx:** `brief/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx` §5→MODELO-01, §6→PYMONGO-01/LIMPIEZA-01/TRANSFORM-01, §7→CONSULTAS-01, §8→AGREGACION-01, §9→INDICES-01, §10→DISTRIBUIDA-01, §11→TRANSACCIONES-01, §12→PYMONGO-PRO-01, §15/§16/§17→mapa y pesos (sin cambiar pesos)

---

## Purpose

Diseñar una base de datos MongoDB con un modelo justificado, insertar,
actualizar y eliminar documentos con PyMongo de forma automatizada y
comprobada, limpiar los datos, transformarlos con operaciones de MongoDB y
obtener indicadores con Aggregation Pipeline.

---

## Requirements

### Requirement: MODELO-01 — Modelo justificado y relaciones

El sistema SHALL responder en `docs/modelo_mongodb.md`, literalmente, las 7
preguntas docx §5: ¿qué información se consulta normalmente junta?; ¿qué
información cambia con frecuencia?; ¿qué arrays podrían crecer sin límite?;
¿hay información que se repite pero interesa conservar como fotografía
histórica?; ¿qué relaciones son 1:1, 1:N o N:M?; ¿qué campos se usarán para
relacionar información procedente de fuentes distintas?; ¿qué tipos BSON son
adecuados para fechas, importes, identificadores, booleanos o arrays?
(Previously: las 7 preguntas en SHOULD.)

#### Scenario: Preguntas literales en el doc

- GIVEN `docs/modelo_mongodb.md`
- WHEN se revisa el modelado
- THEN las 7 preguntas aparecen literales con su respuesta
- AND ≥1 decisión embedding/referencing queda justificada


### Requirement: PYMONGO-01 — CRUD con excepciones tipadas

El sistema SHALL sustituir `except Exception` por `except (TypeError,
ValueError)` con log en `_money` (`storage/load_mongo.py`) y en los
`except Exception: pass` de `ensure_indexes`/`explain_*`
(`analysis/mongo_indexes.py`), y SHALL comprobar `matched_count`,
`modified_count` y `deleted_count` en test.
(Previously: excepciones genéricas con `pass` silencioso.)

#### Scenario: Errores no silenciados y CRUD con contadores

- GIVEN un precio no numérico o un CRUD en `vivienda_euskadi_test`
- WHEN se procesa `_money` o se insertan/actualizan/borran documentos
- THEN `_money` devuelve `None` con log y el test comprueba los 3 contadores
- AND `pytest tests` sigue en 136 passed


### Requirement: CARGA-SEGURA-01 — Carga sin ventana vacía ni borrado irreversible

El sistema MUST construir los documentos completos antes de reemplazar una colección. Si los documentos están vacíos, MUST NOT modificar la colección original. El reemplazo MUST usar staging y backup: la original se clona a `<name>__backup` y los documentos nuevos van a `<name>__staging` antes del rename atómico. Los índices MUST recrearse tras el swap con ensure_indexes.

#### Scenario: Carga con CSV vacío aborta sin borrado

- GIVEN un CSV sin filas válidas
- WHEN se carga la colección
- THEN la carga devuelve 0
- AND la colección original conserva sus documentos

#### Scenario: El backup conserva la última carga buena

- GIVEN una colección cargada
- WHEN se recarga con documentos nuevos
- THEN existe `<name>__backup` con los documentos previos
- AND la colección activa tiene los documentos nuevos

#### Scenario: Insertar es idempotente

- GIVEN un documento ya insertado
- WHEN se vuelve a insertar
- THEN no se duplica

#### Scenario: Actualizar cambia el documento

- GIVEN un anuncio con precio antiguo
- WHEN llega el mismo anuncio con precio nuevo
- THEN el documento se actualiza
- AND se conserva el histórico o el motivo del cambio

#### Scenario: Eliminar es reversible en intención

- GIVEN documentos marcados como duplicados
- WHEN se ejecuta el borrado
- THEN desaparecen de la colección
- AND el número de documentos restantes se reporta

#### Scenario: Los métodos y contadores se demuestran

- GIVEN el código PyMongo del proyecto
- WHEN se revisa
- THEN aparecen los métodos aplicables (insert_one/many, find_one/find,
  update_one/many, delete, find_one_and_update, bulk_write, upsert)
- AND se comprueban contadores (matched/modified/deleted/inserted) u
  ObjectId/inserted_id cuando proceda

#### Scenario: Los resultados se comprueban

- GIVEN una operación de inserción
- WHEN termina
- THEN se consulta la base de datos y se verifica el recuento esperado

### Requirement: CONSULTAS-01 — Campos anidados y arrays

El sistema SHALL combinar condiciones y SHALL consultar sobre campos anidados
o arrays. Para el nivel 7 de la rúbrica v2, SHALL utilizar al menos 4 tipos
diferentes entre filtros, comparación, operadores lógicos, proyección, sort,
arrays o campos anidados. Para el nivel 10, SHALL realizar al menos 5
consultas útiles para el reto, incluyendo una con campos anidados o arrays y
otra combinando 2 o más condiciones. Deberá demostrar, cuando sean
aplicables, las familias de consulta del Tema 8: comparación ($gt, $gte, $lt, $lte, $ne, $in, $nin), lógica
($and, $or), estructuras complejas (dot notation sobre documentos embebidos y
consultas de arrays), arrays ($elemMatch, $all, $size), existencia y tipo
($exists, $type), presentación (proyecciones, ordenación, limitación,
paginación) y texto/patrones (regex u otros). No es obligatorio forzar
operadores sin sentido para los datos.

#### Scenario: Filtro sobre un campo anidado

- GIVEN anuncios con dirección anidada
- WHEN se consulta por municipio
- THEN solo devuelve los anuncios de ese municipio

#### Scenario: Filtro sobre un campo embebido con dot notation

- GIVEN anuncios con dirección embebida
- WHEN se consulta con notación punto (p. ej. direccion.municipio)
- THEN solo devuelve los documentos coincidentes

#### Scenario: Filtro sobre un array

- GIVEN anuncios con un array de características
- WHEN se filtra por la presencia de una característica
- THEN solo devuelve los que la tienen

#### Scenario: Filtro avanzado sobre arrays

- GIVEN anuncios con un array de características
- WHEN se filtra con $elemMatch, $all o $size cuando los datos lo permiten
- THEN solo devuelve los que cumplen la condición del array

#### Scenario: Existencia y tipo
- GIVEN documentos con campos heterogéneos
- WHEN se filtra con $exists o $type
- THEN se controla la calidad o heterogeneidad de los datos

#### Scenario: Presentación y texto
- GIVEN un conjunto de resultados
- WHEN se aplican proyecciones, ordenación, limitación/paginación o regex
- THEN la salida es legible y acotada a la necesidad real

#### Scenario: Al menos 4 tipos de consulta — nivel 7

- GIVEN los datos cargados
- WHEN se revisa la batería de consultas
- THEN se utilizan al menos 4 tipos diferentes entre filtros, comparación,
  operadores lógicos, proyección, sort, arrays o campos anidados

#### Scenario: Al menos 5 consultas útiles, 2 o más condiciones — nivel 10

- GIVEN los datos cargados
- WHEN se revisa la batería de consultas
- THEN existen al menos 5 consultas útiles para el reto
- AND al menos 1 consulta usa campos anidados o arrays
- AND al menos 1 consulta combina 2 o más condiciones

### Requirement: AGREGACION-01 — Pipelines a CSV canónico

El sistema SHALL emitir CSV canónicos en `data/resultados/` desde
`pipeline_indicadores_municipio` (252 filas),
`pipeline_alquiler_por_municipio` (252), `pipeline_modalidades` (2),
`pipeline_accesibilidad_extendida` y `pipeline_vpo_por_municipio`, con
`$group`/`$lookup`/`$unwind` donde los datos lo permitan.
(Previously: solo 3 CSV canónicos medidos.)

#### Scenario: Cinco CSV canónicos

- GIVEN las 9 pipelines de `analysis/mongo_aggregations.py`
- WHEN se ejecutan las 5 citadas
- THEN cada una escribe su CSV canónico en `data/resultados/`
- AND los recuentos medidos son 252, 252 y 2


### Requirement: LIMPIEZA-01 — Incompletos, duplicados, incorrectos

El sistema SHALL limpiar con `$unset` explícito y SHALL retornar
`deleted_count`, SHALL exponer una única función canónica
anuncio-por-municipio y SHALL mantener los 759 anuncios tras limpio.
(Previously: `$unset`/`deleted_count` sin función canónica única.)

#### Scenario: Limpieza con contadores

- GIVEN anuncios con campos obsoletos
- WHEN se ejecuta `clean_mongo`
- THEN aplica `$unset` y el resultado incluye `deleted_count`
- AND el recuento sigue en 759


### Requirement: TRANSFORM-01 — Transformaciones en MongoDB

El sistema SHALL aplicar las transformaciones mediante operaciones de MongoDB,
realizando al menos 3 operaciones diferentes (nivel 7) y al menos 4
operaciones diferentes para el nivel 10. Las 4 operaciones del nivel 10
SHALL incluir tratamiento de nulos/ausentes, duplicados y tipos/formato de
datos, de forma conjunta con LIMPIEZA-01 y demostrable en código PyMongo.

#### Scenario: La normalización ocurre en la base de datos

- GIVEN precios en unidades heterogéneas
- WHEN se transforman
- THEN el cálculo se hace con una operación de MongoDB
- AND el resultado queda persistido

#### Scenario: Al menos 4 transformaciones, con nulos, duplicados y tipos — nivel 10

- GIVEN los datos cargados
- WHEN se revisan las operaciones de transformación con PyMongo
- THEN existen al menos 4 operaciones diferentes
- AND al menos 1 trata nulos/ausentes
- AND al menos 1 trata duplicados
- AND al menos 1 normaliza tipos o formato de datos


### Requirement: INDICES-01 — Índices y explain()

El sistema SHALL demostrar con `explain("executionStats")`, para
`ubicacion.codigo_ine=48001` + `modalidad=larga_estancia` + `precio_eur $lte
Decimal128(1000)`, la transición COLLSCAN → IXSCAN con `nReturned` y
`totalDocsExamined=1` tras el índice ESR
`{ubicacion.codigo_ine:1, modalidad:1, precio_eur:1}`, y SHALL documentarlo en
`docs/modelo_mongodb.md` junto a geo 2dsphere sparse, multikey
(`equipamiento`) y parcial.
(Previously: ESR/geo/multikey/parcial en SHOULD sin evidencia.)

#### Scenario: Before/after con totalDocsExamined=1

- GIVEN el índice ESR eliminado
- WHEN se ejecutan `explain_before_after()` y `_explain()`
- THEN `before.stage` es `COLLSCAN` y `after.stage` es `IXSCAN`
- AND `after.totalDocsExamined` es 1 con `nReturned` documentado

#### Scenario: Geo, multikey y parcial documentados

- GIVEN `docs/modelo_mongodb.md`
- WHEN se revisan los índices
- THEN constan geo 2dsphere sparse, multikey `equipamiento` y parcial
- AND cada uno cita su consulta real justificativa


### Requirement: TRANSACCIONES-01 — Atomicidad multidocumento

El sistema SHALL demostrar commit/abort multidocumento en
`vivienda_euskadi_test` o SHALL justificar por READ (docx §11), y MUST NOT
tocar prod por defecto (solo `MONGO_ALLOW_DESTRUCTIVE=1`).
(Previously: solo atomicidad de un documento.)

#### Scenario: Commit/abort en test o READ

- GIVEN `vivienda_euskadi_test` o la decisión documentada
- WHEN se ejecuta la transacción o se revisa la justificación
- THEN el commit persiste, el abort revierte y prod conserva su recuento
- AND si no aplica, la justificación cita docx §11 y el ejemplo plausible


### Requirement: DISTRIBUIDA-01 — Arquitectura distribuida (conceptual)

Respaldo Tema 8 (extensión propia, no criterio v2 directo). El sistema SHALL
poder explicar replica sets y sharding y su relación con disponibilidad y
escalabilidad, aunque se ejecute en local.

#### Scenario: Conceptos explicables
<!-- Trazabilidad docx Tema 8 §10 Replica sets y sharding (P065-P066, tabla 8): concerns por separado y ARBITER; conceptual, sin exigir clúster -->
- GIVEN la solución en local
- WHEN se defiende
- THEN se explican PRIMARY/SECONDARY, oplog, elección/failover,
  readPreference, readConcern, writeConcern (incl. majority), ARBITER,
  mongos, config servers, shards y shard key (ranged vs hashed)
- AND se distinguen readPreference (de qué tipo de nodo se prefieren las
  lecturas), readConcern (qué garantía de lectura se solicita), writeConcern
  (cuándo se considera confirmada una escritura y qué implica majority) y
  ARBITER (participa en elecciones pero no almacena datos) como conceptos
  separados
- AND se identifica un candidato a shard key y sus riesgos

### Requirement: PYMONGO-PRO-01 — PyMongo profesional

Respaldo Tema 8 (extensión propia, no criterio v2 directo). El sistema SHALL
presentarse como proyecto Python mantenible, con conexión reutilizable y URI
configurable, estructura separada, manejo de errores, ObjectId, cursores,
upsert, find_one_and_update, bulk_write y README.

#### Scenario: Proyecto reproducible
<!-- Trazabilidad docx Tema 8 §12 Desarrollo profesional con PyMongo (P075, tabla 11): cursor find no es lista y MongoClient reutilizable sin repetir cadena en la línea de conexión -->
- GIVEN el código del proyecto
- WHEN se revisa
- THEN la conexión es reutilizable y la URI configurable
- AND el MongoClient es reutilizable sin repetir credenciales ni cadenas de
  conexión por el código
- AND find() se itera como cursor, no como lista, distinguiendo documento de
  cursor
- AND hay manejo de errores y comprobación de resultados
- AND el README permite reproducir la ejecución

### Requirement: VALIDACION-01 — Validación de esquema (si procede)

Respaldo Tema 8 (extensión propia, no criterio v2 directo). El sistema SHOULD
aplicar validación de esquema (JSON Schema) cuando aporte valor, y documentar
la decisión.

#### Scenario: Validación justificada
- GIVEN las colecciones
- WHEN se diseña la validación
- THEN o bien se aplica validación y se demuestra
- OR se justifica por qué no procede

### Requirement: RESPALDO-01 — Backups y geo en lectura pura

El sistema SHALL garantizar backups de `municipios` e `indicadores` vía
`replace_collection` (staging + `<name>__backup` + rename), SHALL documentar
los 424 Point GeoJSON de 759 anuncios desde silver, y SHALL verificarlo con
el listing de 16 colecciones, sin escrituras en prod.

#### Scenario: Backups, geo y listing

- GIVEN `vivienda_euskadi` con 759 anuncios y 252 municipios
- WHEN se listan las colecciones y se cuentan los Point
- THEN hay 16 colecciones, incluidos `municipios__backup` (252 previos) e `indicadores__backup`
- AND hay 424 Point reales, el resto `None` por falta de silver
### Requirement: RENTA-01 — `validar_renta` o justificación firmada

El sistema SHALL incluir `validar_renta.py` como paso de
`transform/run_all.py` o SHALL firmar su exclusión, y `pytest tests` SHALL
pasar con 136 tests.

#### Scenario: Integración o justificación

- GIVEN `validar_renta.py` en `EXCLUIDOS` de `run_all.py`
- WHEN se revisa el orquestador
- THEN es paso del pipeline o existe justificación firmada
- AND `pytest tests -q` reporta 136 passed

## MODIFIED Requirements

### Mapa de integración Tema 1–8 → requisito (docx §15)
<!-- Trazabilidad docx Tema 8 §15 Mapa de integración (tabla 13), §16 pesos y §17 checklist: se añade el mapa sin cambiar pesos; SHALL/SHOULD existentes se mantienen -->
| Tema (docx §15) | Contenido docx | Requisitos en este spec |
|---|---|---|
| 1. Fundamentos y CRUD | BSON, ObjectId, colecciones, documentos, CRUD, cursores y resultados PyMongo | PYMONGO-01, CARGA-SEGURA-01, CONSULTAS-01 (parcial), PYMONGO-PRO-01 (parcial) |
| 2. Consultas y modelado | Arrays, documentos embebidos, dot notation, embedding/referencing, validación si procede | MODELO-01, CONSULTAS-01, VALIDACION-01 (si procede) |
| 3. Aggregation | Pipelines con etapas encadenadas y acumuladores para obtener indicadores | AGREGACION-01 |
| 4. Índices y rendimiento | Índices simples/compuestos, explain(), COLLSCAN/IXSCAN y coste de los índices | INDICES-01 |
| 5. Arquitectura distribuida | Replica sets, failover, concerns, sharding y shard key | DISTRIBUIDA-01 |
| 6. Transacciones | Atomicidad, sesiones, commit/abort y decisión de cuándo una transacción es necesaria | TRANSACCIONES-01 |
| 7. PyMongo profesional | Conexión, estructura del proyecto, errores, ObjectId, cursores, resultados y operaciones avanzadas | PYMONGO-PRO-01 |
| 8. Proyecto integrador | Unir todas las decisiones anteriores en una solución propia y defendible | MODELO-01 + PYMONGO-01 + CARGA-SEGURA-01 + CONSULTAS-01 + AGREGACION-01 + LIMPIEZA-01 + TRANSFORM-01 + INDICES-01 + TRANSACCIONES-01 + DISTRIBUIDA-01 + PYMONGO-PRO-01 + VALIDACION-01 |

Pesos docx §16 (sin cambios en este spec): Modelado 15 %, CRUD/limpieza/consultas 15 %, Aggregation 20 %, Índices 15 %, Transacciones 10 %, PyMongo profesional 15 %, Defensa 10 %.
Checklist docx §17: verificado por los escenarios existentes (datos reales, modelo justificado, carga/limpieza PyMongo, consultas reales, pipelines, explain+índice, transacción razonada, replica sets/sharding, código reproducible, defensa).
