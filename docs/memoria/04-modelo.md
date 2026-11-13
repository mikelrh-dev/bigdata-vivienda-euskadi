<!-- cap: 4 | titulo: Modelo MongoDB | criterios: C9, C10, C14 | estado: borrador -->
# 4. Modelo MongoDB

> **Objetivo.** Justificar el modelo documento a documento y demostrar que las operaciones son correctas e idempotentes.

## 4.1 La regla: lo que se lee junto se embebe, lo que crece se referencia

`municipios` se lee entero para pintar una ficha y cambia poco: demografía, empleo, demanda social, vivienda y transporte van embebidos. `anuncios` crece cada día y se consulta por municipio, modalidad y precio: se referencia con `ubicacion.codigo_ine`. La decisión no es estética; evita duplicar en cada anuncio un bloque de contexto que no cambia.

## 4.2 Colecciones y clave natural

El sistema tiene {{mongo.vivas}} colecciones vivas y {{mongo.backup}} de respaldo, {{mongo.total}} en total. La clave natural es el código INE: el `_id` de `municipios` es `"48020"`, no un ObjectId. No hay un campo `codigo_ine` duplicado dentro de `municipios`; el `_id` ya lo es. En `anuncios`, la referencia es `ubicacion.codigo_ine`.

## 4.3 Tipos y estructuras

Los importes son números, las fechas son fechas y los códigos son cadenas de cinco dígitos. Los arrays (`equipamiento[]`, `historico_precios[]`) se tratan con `$unwind` cuando el análisis lo necesita, sin aplanarlos en la carga. Los documentos anidados conservan la forma de la fuente para no perder información.

## 4.4 Índices

Hay {{mongo.indices_creados}} índices creados de {{mongo.indices_definidos}} definidos. Los dos que faltan pertenecen al pipeline 2026 y se declaran como deuda en el capítulo 7. Cada índice responde a una consulta real: `anuncios` por INE, modalidad y precio; `municipios` por territorio y nombre; `alquiler` por distrito y nivel.

## 4.5 CRUD, atomicidad y respaldo

El código cubre las cuatro operaciones de PyMongo y comprueba el resultado: insert, update, delete y find. La carga no necesita una transacción multi-documento porque cada colección se reemplaza con `replace_collection`, que es atómica a nivel de colección. Esa es la justificación técnica de no usar transacciones, no una omisión.

<!-- Figura 4.1: modelo de colecciones y relación por codigo_ine. Se genera en HTML/CSS. -->
