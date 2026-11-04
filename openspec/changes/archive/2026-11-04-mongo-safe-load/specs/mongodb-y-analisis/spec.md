# Delta for mongodb-y-analisis

## ADDED Requirements

### Requirement: CARGA-SEGURA-01 — Carga sin ventana vacía ni borrado irreversible

El sistema MUST construir los documentos completos antes de reemplazar una colección. Si los documentos están vacíos, MUST NOT modificar la colección original. El reemplazo MUST usar staging y backup: la original se clona a `<name>__backup` y los documentos nuevos van a `<name>__staging` antes del rename atómico. Los índices MUST recrearse tras el swap con ensure_indexes.

#### Scenario: Los daños se construyen antes del reemplazo

- GIVEN un CSV silver válido
- WHEN se carga la colección
- THEN los documentos se verifican en staging
- AND la colección original permanece intacta hasta el rename

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

## MODIFIED Requirements

### Requirement: PYMONGO-01 — Inserta, actualiza, elimina y comprueba

El sistema SHALL implementar inserción, actualización y borrado con PyMongo, de forma automatizada, y SHALL comprobar los resultados. Los loaders con drop SHALL usar el patrón staging + backup + rename de CARGA-SEGURA-01; los loaders idempotentes con upsert (municipios, anuncios) SHALL mantener replace_one/update_one con upsert. Los tests que borran o modifican datos (clean, demo CRUD) MUST NOT ejecutarse por defecto contra la base productiva; requieren MONGO_ALLOW_DESTRUCTIVE=1 explícito.
(Previously: cualquier loader con drop podía borrar antes de construir.)

#### Scenario: Insertar es idempotente

- GIVEN un documento ya insertado
- WHEN se vuelve a insertar
- THEN no se duplica

#### Scenario: Los tests no mutan prod por defecto

- GIVEN una sesión de tests estándar
- WHEN se ejecuta pytest sin MONGO_ALLOW_DESTRUCTIVE=1
- THEN test_clean_mongo y test_crud_demo se marcan skipped
- AND la base productiva conserva su recuento

#### Scenario: zfill canoniza floats de Fotocasa

- GIVEN un código como 20069.0 o "1001.0" desde una fuente float
- WHEN se normaliza con zfill_ine
- THEN se devuelve el código de 5 dígitos con int(float(x)) y zfill(5)
