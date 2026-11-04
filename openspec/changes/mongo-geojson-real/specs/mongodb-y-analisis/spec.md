# Delta for mongodb-y-analisis

## ADDED Requirements

### Requirement: GEOJSON-01 — GeoJSON Point real en anuncios

El sistema MUST almacenar en `anuncios.ubicacion.coordenadas` un GeoJSON `Point` real con orden `[lon, lat]` cuando la fuente silver aporta `latitud` y `longitud` válidas para ese anuncio. La fuente MUST ser `data/procesado/anuncios_fotocasa_enriquecido.csv` por campo `id_anuncio`, solo para anuncios con `portal == "fotocasa"`. El sistema MUST NOT inventar, derivar por centroide ni copiar coordenadas de otro anuncio. Cuando falte la entrada o el valor sea vacío, nulo o no numérico, el sistema MUST guardar `None` y el índice `2dsphere` sparse MUST excluir ese documento sin error.

#### Scenario: Anuncio fotocasa con coordenadas silver válidas

- GIVEN un anuncio unificado con `portal == "fotocasa"` y `id_anuncio` presente en el silver enriquecido con `latitud` y `longitud` numéricas dentro de rango
- WHEN se ejecuta `load_anuncios()`
- THEN `ubicacion.coordenadas` es `{"type": "Point", "coordinates": [lon, lat]}` con `lon` y `lat` finitos de tipo numérico
- AND -90 <= lat <= 90 y -180 <= lon <= 180 con orden GeoJSON lon primero

#### Scenario: Anuncio sin silver o portal distinto de fotocasa

- GIVEN un anuncio con `portal` distinto de `fotocasa` o con `id_anuncio` sin coincidencia en el silver
- WHEN se ejecuta `load_anuncios()`
- THEN `ubicacion.coordenadas` es `None`
- AND el documento no rompe la carga ni el índice sparse

#### Scenario: Coordenada inválida o fuera de rango

- GIVEN una fila silver con `latitud` o `longitud` vacía, no numérica, `NaN`, infinita o fuera del rango válido
- WHEN se construye el punto con `_geo_point`
- THEN el resultado es `None`
- AND no se almacena ningún Point inválido en MongoDB

#### Scenario: Test de GeoJSON real con conteo vivo

- GIVEN MongoDB vivo cargado vía `load_anuncios()`
- WHEN se ejecuta `test_anuncios_geojson_real`
- THEN el conteo de Point válidos es mayor que 0
- AND el conteo de valores no `None` que no sean Point válidos es 0
