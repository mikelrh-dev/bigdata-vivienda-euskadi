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
modelo y las relaciones entre los datos.

#### Scenario: El modelo se justifica por escrito

- GIVEN las fuentes del contrato
- WHEN se diseña la base de datos
- THEN cada colección tiene un propósito y sus campos están justificados
- AND la relación anuncio ↔ municipio ↔ alquiler ↔ renta está descrita

#### Scenario: Los nombres de campo son coherentes

- GIVEN dos colecciones que comparten municipio
- WHEN se comparan
- THEN el campo de municipio usa el mismo nombre y formato en ambas

### Requirement: PYMONGO-01 — Inserta, actualiza, elimina y comprueba

El sistema SHALL implementar inserción, actualización y borrado con PyMongo,
de forma automatizada, y SHALL comprobar los resultados.

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

#### Scenario: Los resultados se comprueban

- GIVEN una operación de inserción
- WHEN termina
- THEN se consulta la base de datos y se verifica el recuento esperado

### Requirement: CONSULTAS-01 — Campos anidados y arrays

El sistema SHALL combinar condiciones y SHALL consultar sobre campos anidados
o arrays.

#### Scenario: Filtro sobre un campo anidado

- GIVEN anuncios con dirección anidada
- WHEN se consulta por municipio
- THEN solo devuelve los anuncios de ese municipio

#### Scenario: Filtro sobre un array

- GIVEN anuncios con un array de características
- WHEN se filtra por la presencia de una característica
- THEN solo devuelve los que la tienen

### Requirement: AGREGACION-01 — Cuatro etapas o más, indicadores complejos

El sistema SHALL encadenar al menos cuatro etapas distintas del Aggregation
Pipeline para obtener indicadores complejos.

#### Scenario: Cuatro etapas encadenadas

- GIVEN los datos cargados
- WHEN se ejecuta la agregación
- THEN usa al menos cuatro etapas distintas (`$match`, `$group`, `$sort`,
  `$project`, `$lookup`, `$facet`)
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
