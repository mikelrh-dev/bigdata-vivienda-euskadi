# MongoDB y análisis — Especificación

**Capacidad:** `mongodb-y-analisis`
**Estado:** Pendiente
**Criterios cubiertos:** SBD-RA3 Modelado (10), Operaciones PyMongo (10),
Consultas (10), Aggregation Pipeline (10), limpieza y transformaciones
**Contrato:** `../contrato-reto/spec.md`

---

## Purpose

Diseñar una base de datos MongoDB con un modelo justificado, insertar,
actualizar y eliminar documentos con PyMongo de forma automatizada y
comprobada, limpiar los datos, transformarlos con operaciones de MongoDB y
obtener indicadores con Aggregation Pipeline.

---

## Requirements

### Requirement: MODELO-01 — Modelo justificado y relaciones

El sistema SHALL crear colecciones con campos adecuados y SHALL justificar el
modelo y las relaciones entre los datos. La relación concreta entre entidades
(p. ej. anuncio ↔ municipio ↔ alquiler ↔ renta) es una decisión del equipo
según sus fuentes y patrones de acceso, no un requisito universal del reto.

#### Scenario: El modelo se justifica por escrito

- GIVEN las fuentes del contrato
- WHEN se diseña la base de datos
- THEN cada colección tiene un propósito y sus campos están justificados
- AND la relación entre las entidades del equipo está descrita como decisión
  propia, no como esquema único

#### Scenario: Se justifica embedding vs referencing

- GIVEN el modelo documental diseñado
- WHEN se documenta
- THEN se justifica al menos una decisión de embedding o de referencing
- AND se indican los tipos BSON adecuados (fechas, importes, ids, booleanos,
  arrays)
- AND se describen los patrones de acceso previstos que motivan la decisión

#### Scenario: Los nombres de campo son coherentes

- GIVEN dos colecciones que comparten municipio
- WHEN se comparan
- THEN el campo de municipio usa el mismo nombre y formato en ambas

### Requirement: PYMONGO-01 — Inserta, actualiza, elimina y comprueba

El sistema SHALL implementar inserción, actualización y borrado con PyMongo,
de forma automatizada, y SHALL comprobar los resultados. Deberá demostrar,
cuando sean aplicables: insert_one/insert_many, find_one/find, update_one/
update_many con $set/$unset/$inc/$rename/$push/$pull/$addToSet, delete_one/
delete_many, matched_count/modified_count/deleted_count/inserted_id, ObjectId,
fechas y tipos BSON, upsert, find_one_and_update y bulk_write.

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
o arrays. Deberá demostrar, cuando sean aplicables, las familias de consulta
del Tema 8: comparación ($gt, $gte, $lt, $lte, $ne, $in, $nin), lógica
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

### Requirement: AGREGACION-01 — Cuatro etapas o más, indicadores complejos

El sistema SHALL encadenar al menos cuatro etapas distintas del Aggregation
Pipeline para obtener indicadores complejos. Entre las etapas disponibles
están $match, $project, $set/$addFields, $unset, $group, $sort, $limit,
$skip, $count, $unwind, $lookup y $facet.

#### Scenario: Cuatro etapas encadenadas

- GIVEN los datos cargados
- WHEN se ejecuta la agregación
- THEN usa al menos cuatro etapas distintas (`$match`, `$group`, `$sort`,
  `$project`, `$lookup`, `$facet`, `$set`/`$addFields`, `$unset`,
  `$unwind`, `$count`, `$skip`, `$limit`)
- AND produce un indicador por municipio

#### Scenario: El indicador combina fuentes

- GIVEN alquiler y renta por municipio
- WHEN se calcula el indicador
- THEN combina ambas fuentes
- AND expresa el esfuerzo como porcentaje

### Requirement: LIMPIEZA-01 — Incompletos, duplicados, incorrectos

El sistema SHALL detectar y corregir datos incompletos, duplicados o
incorrectos.

#### Scenario: Los duplicados reales se resuelven

- GIVEN el mismo anuncio publicado dos veces
- WHEN se limpia
- THEN queda una sola copia
- AND el recuento de únicos es menor que el de brutos

#### Scenario: Los nulos se tratan de forma explícita

- GIVEN un anuncio sin superficie
- WHEN se limpia
- THEN el valor nulo se marca o se descarta, nunca se interpreta como cero

### Requirement: TRANSFORM-01 — Transformaciones en MongoDB

El sistema SHALL aplicar las transformaciones mediante operaciones de MongoDB.

#### Scenario: La normalización ocurre en la base de datos

- GIVEN precios en unidades heterogéneas
- WHEN se transforman
- THEN el cálculo se hace con una operación de MongoDB
- AND el resultado queda persistido


### Requirement: INDICES-01 — Índices y explain()

El sistema SHALL diseñar al menos un índice justificado por una consulta real
y SHALL demostrar su efecto con explain() antes y después.

#### Scenario: Análisis before/after
- GIVEN una consulta real del proyecto
- WHEN se ejecuta explain("executionStats") antes y después de crear el índice
- THEN se comparan COLLSCAN/IXSCAN, nReturned, totalDocsExamined y
  totalKeysExamined
- AND se explica la mejora y el coste en almacenamiento y escrituras

### Requirement: TRANSACCIONES-01 — Atomicidad multidocumento

El sistema SHALL determinar si existe una operación que requiera atomicidad
multidocumento y SHALL implementarla con sesiones/transacciones si procede, o
justificar su ausencia.

#### Scenario: Decisión razonada
- GIVEN el modelo documental
- WHEN se revisa la necesidad de atomicidad
- THEN o bien se implementa una transacción (commit/abort, manejo de errores)
- OR se justifica que la atomicidad documental basta y se propone un ejemplo
  plausible

### Requirement: DISTRIBUIDA-01 — Arquitectura distribuida (conceptual)

El sistema SHALL poder explicar replica sets y sharding y su relación con
disponibilidad y escalabilidad, aunque se ejecute en local.

#### Scenario: Conceptos explicables
- GIVEN la solución en local
- WHEN se defiende
- THEN se explican PRIMARY/SECONDARY, oplog, elección/failover, concerns,
  mongos, config servers, shards y shard key (ranged vs hashed)
- AND se identifica un candidato a shard key y sus riesgos

### Requirement: PYMONGO-PRO-01 — PyMongo profesional

El sistema SHALL presentarse como proyecto Python mantenible, con conexión
reutilizable y URI configurable, estructura separada, manejo de errores,
ObjectId, cursores, upsert, find_one_and_update, bulk_write y README.

#### Scenario: Proyecto reproducible
- GIVEN el código del proyecto
- WHEN se revisa
- THEN la conexión es reutilizable y la URI configurable
- AND hay manejo de errores y comprobación de resultados
- AND el README permite reproducir la ejecución

### Requirement: VALIDACION-01 — Validación de esquema (si procede)

El sistema SHOULD aplicar validación de esquema (JSON Schema) cuando aporte
valor, y documentar la decisión.

#### Scenario: Validación justificada
- GIVEN las colecciones
- WHEN se diseña la validación
- THEN o bien se aplica validación y se demuestra
- OR se justifica por qué no procede
