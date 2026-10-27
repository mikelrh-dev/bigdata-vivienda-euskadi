# Módulos Enchufables según la Fase

Solo tienes que copiar el bloque de la fase que estés cerrando y pegarlo donde dice `[PEGAR AQUÍ EL MÓDULO DE LA FASE CORRESPONDIENTE]` en la plantilla maestra.

## Módulo A: Tras arreglar Extracción y Normalización (Cierre Fase 1)
> **Cuándo usarlo:** Justo cuando tu agente termine las tareas de normalización y limpieza en `extract/` y `transform/`.

```markdown
Audita el cierre de Extracción y Entity Resolution (`extraccion-datos/spec.md`):
1. **Integridad de `codigo_ine`:** Verifica qué porcentaje de registros en `anuncios_fotocasa.json`, `anuncios_pisos.json`, `anuncios_realtyapi.json` y `alquiler_municipal.csv` tienen asignado un `codigo_ine` válido de 5 dígitos que cruce al 100% con `eustat_renta_municipal.json` y el nuevo fichero de paro/empleo municipal.
2. **Calidad de Pisos.com y Fotocasa:** Comprueba cuántos anuncios de Pisos.com tienen `superficie_m2` y `habitaciones` no nulos, y verifica que `data/raw/html_fotocasa/` contiene los HTML crudos (`EXTRACCION-01`).
3. **Cobertura Geográfica 3 Territorios:** Verifica que el nuevo GeoJSON cubre los 251 municipios de Euskadi (Álava, Bizkaia, Gipuzkoa) en proyección `EPSG:4326` y que las distancias Haversine no tienen `NaN`.
4. **Suite de Tests:** Ejecuta `pytest` y confirma 0 `xfail` y 0 `skip`.
```

## Módulo B: Auditoría de Infraestructura HDFS + Kafka + MongoDB (Fases 2, 3 y 7)
> **Cuándo usarlo:** Cuando levantes el `docker-compose.yml`, subas datos a HDFS y pruebes el productor/consumidor de Kafka.

```markdown
Audita la capa de Almacenamiento y Streaming (`almacenamiento-y-streaming/spec.md`):
1. **HDFS (`HDFS-01` nivel 10 pts):** Comprueba que existen las rutas separadas `/raw/` y `/procesado/` en HDFS, y haz una prueba de descarga comparando el hash SHA256 o tamaño exacto en bytes contra el archivo local.
2. **Idempotencia en Kafka -> MongoDB (`KAFKA-01` y `PYMONGO-01`):** Envía dos veces el mismo lote de anuncios por el productor de Kafka (simulando un cambio de precio en 3 anuncios) y verifica en MongoDB que:
   - El conteo total de documentos NO se ha duplicado.
   - Los 3 anuncios modificados han actualizado su precio y conservan el precio anterior en un array `historico_precios`.
3. **Aislamiento de fallos (`INTEGRACION-01`):** Verifica que el consumidor registra logs claros y usa `upsert` sin corromper la colección.
```

## Módulo C: Auditoría de MongoDB, Limpieza y Aggregation Pipeline (Fases 4, 5 y 6)
> **Cuándo usarlo:** Cuando tengas las colecciones cargadas en MongoDB y hayas escrito las consultas y agregaciones.

```markdown
Audita el Modelado y Análisis en MongoDB (`mongodb-y-analisis/spec.md`):
1. **Anti-Trampa `TRANSFORM-01`:** Verifica que la limpieza de nulos (`superficie_m2: None` no convertido a `0`) y el cálculo de `precio_eur_m2` se ejecutan mediante operaciones nativas de MongoDB/PyMongo (`update_many` con pipeline de actualización) y quedan persistidos en la BD.
2. **Consultas Complejas (`CONSULTAS-01`):** Comprueba que existen y devuelven datos reales al menos 2 consultas que combinen filtros sobre campos anidados (ej. `direccion.municipio` o coordenadas GeoJSON) y arrays (ej. `caracteristicas` o `historico_precios`).
3. **Profundidad del Aggregation Pipeline (`AGREGACION-01` nivel 10 pts):** Audita el pipeline principal para confirmar que encadena al menos 4 etapas distintas (`$match`, `$lookup`, `$unwind`, `$group`, `$project`, `$sort` o `$facet`), que no pierde municipios clave en el `$lookup` y que distingue entre municipios con muestra representativa ($n \ge 5$ anuncios) y municipios donde solo aplica el dato oficial de Eustat.
```

## Módulo D: Auditoría Final de Gráficos, Informe y Defensa (Fases 8 y 9)
> **Cuándo usarlo:** Antes de entregar el proyecto y preparar la demo.

```markdown
Audita la Visualización y Conclusiones (`presentacion-de-resultados/spec.md`):
1. **Cero Hardcoding (`DATOS-PYMONGO-01` y `P-05`):** Inspecciona el código de `visualization/` y `notebooks/` para garantizar que TODOS los gráficos leen directamente del cursor/resultado de PyMongo, sin un solo número o lista de municipios escrita a mano en el código.
2. **Adecuación y Formato (`GRAFICOS-01` y `PRESENTACION-01`):** Verifica que hay al menos 3 tipos distintos (barras para ranking, dispersión para renta vs. alquiler/esfuerzo, boxplot para distribución por territorio/municipio, y mapa coroplético de los 251 municipios), todos con título, unidades (€/mes, €/m², %) y leyenda.
3. **Rigor Estadístico de la Conclusión (`CONCLUSION-01` e `INTERPRETACION-01`):** Revisa que las conclusiones nombran municipios concretos respaldados por su tasa de esfuerzo (%), tasa de paro y distancia a polos de empleo, y que advierten explícitamente cuando un municipio tiene pocos anuncios en portales privados.
```
