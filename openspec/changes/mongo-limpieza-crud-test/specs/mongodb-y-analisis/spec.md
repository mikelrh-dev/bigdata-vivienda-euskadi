# Delta for mongodb-y-analisis

## MODIFIED Requirements

### Requirement: PYMONGO-01 — Inserta, actualiza, elimina y comprueba

El sistema SHALL implementar inserción, actualización y borrado con PyMongo, de forma automatizada, y SHALL comprobar los resultados. Los loaders con drop SHALL usar el patrón staging + backup + rename de CARGA-SEGURA-01; los loaders idempotentes con upsert (municipios, anuncios) SHALL mantener replace_one/update_one con upsert. Los tests que borran o modifican datos (clean, demo CRUD) MUST NOT ejecutarse contra la base productiva; SHALL ejecutarse sobre la base de test vivienda_euskadi_test con colección temporal y sin skip por defecto. Deberá demostrar, cuando sean aplicables: insert_one/insert_many, find_one/find, update_one/update_many con $set/$unset/$inc/$rename/$push/$pull/$addToSet, delete_one/delete_many, matched_count/modified_count/deleted_count/inserted_id, ObjectId, fechas y tipos BSON, upsert, find_one_and_update y bulk_write.
(Previously: los tests destructivos se marcaban skipped sin MONGO_ALLOW_DESTRUCTIVE=1 y no probaban nada.)

#### Scenario: Los tests no mutan prod y no se saltan

- GIVEN una sesión de tests estándar sin MONGO_ALLOW_DESTRUCTIVE
- WHEN se ejecuta pytest
- THEN test_clean_mongo y test_crud_demo corren sobre vivienda_euskadi_test
- AND la base productiva conserva su recuento

#### Scenario: zfill canoniza floats de Fotocasa

- GIVEN un código como 20069.0 o "1001.0" desde una fuente float
- WHEN se normaliza con zfill_ine
- THEN se devuelve el código de 5 dígitos con int(float(x)) y zfill(5)

#### Scenario: Los métodos y contadores se demuestran

- GIVEN el código PyMongo del proyecto
- WHEN se revisa
- THEN aparecen los métodos aplicables (insert_one/many, find_one/find, update_one/many, delete, find_one_and_update, bulk_write, upsert)
- AND se comprueban contadores (matched/modified/deleted/inserted) u ObjectId/inserted_id cuando proceda

#### Scenario: Los resultados se comprueban

- GIVEN una operación de inserción
- WHEN termina
- THEN se consulta la base de datos y se verifica el recuento esperado

## ADDED Requirements

### Requirement: LIMPIEZA-CRUD-TEST-01 — Limpieza y CRUD comprobados sobre temporal

Las 4 operaciones de LIMPIEZA-01 y TRANSFORM-01 (canonicalize, mark_nulls, resolve_duplicates, convert_types) y el demo CRUD de PYMONGO-01 SHALL ejecutarse en tests sobre 3 documentos temporales con código sin zfill, duplicado portal e id_anuncio y precio string. Los tests SHALL asertar matched_count, modified_count, deleted_count y códigos canonizados, y SHALL dejar la base productiva intacta.

#### Scenario: Limpieza con contadores sobre temporal

- GIVEN 3 documentos temporales con código "1001", duplicado y precio string
- WHEN se ejecutan canonicalize, mark_nulls, resolve_duplicates y convert_types
- THEN quedan 2 documentos con códigos "01001" y "20069"
- AND canonicalize reporta matched_count 3 y modified_count 2
- AND resolve_duplicates reporta deleted 1 y convert_types convierte el precio string a Decimal128

#### Scenario: CRUD con contadores sobre temporal

- GIVEN la colección temporal de demo vacía
- WHEN se ejecuta demo_crud_operations
- THEN inserted_id existe, update_one reporta matched_count 1 y modified_count 1
- AND delete_one reporta 1 y delete_many reporta 2
- AND la colección temporal desaparece al terminar
