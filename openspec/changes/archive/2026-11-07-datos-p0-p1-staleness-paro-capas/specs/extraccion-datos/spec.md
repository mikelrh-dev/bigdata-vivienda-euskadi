# extraccion-datos — Delta

## Purpose

Cerrar huecos P0/P1 en la capa de extracción: (M1) limpieza dura de outliers que hoy contamina `precio_m2` (rango 0,16–83,33) y `habitaciones` (float); (M6) deduplicación dura por `property_fingerprint` para eliminar duplicados cross-portal antes de subir a Mongo; (M5) completar el paro Lanbide de 249 a 252 municipios mediante los extractores 18/21 sin imputar ningún valor. Estado: propuesta (delta desde base Desplegada). Sin tocar `data/raw`: el raw sigue inmutable y solo HDFS lo ve; Kafka sigue yendo solo a HDFS, nunca a Mongo. Sin Docker.

## MODIFIED Requirements

### Requirement: COMPLEMENTARIOS-01 — Paro Lanbide 252/252 sin imputación (M5)

El sistema SHALL completar `tasa_paro_lanbide_pct` para los tres municipios que faltaban (01003/20037/48916) ejecutando los extractores Lanbide 18 y 21 y el paso `corregir_empleo`, hasta alcanzar 252/252 municipios. Para el paro municipal SHALL NOT imputar valores comarcales ni IDW: el dato es oficial Lanbide normalizado o es nulo con motivo documentado. `metodo_imputacion` SHALL ser `oficial` y `is_imputed` SHALL ser `false` en el 100 % de las filas de paro.

#### Scenario: Paro completo tras extractores 18/21

- GIVEN paro Lanbide en 249/252 municipios con 01003/20037/48916 nulos
- WHEN se ejecuta `python extract/18_lanbide.py && python extract/21_lanbide.py && python transform/corregir_empleo.py`
- THEN `tasa_paro_lanbide_pct` es no nulo en 252/252 municipios
- AND `python -m storage.load_mongo` carga `udalmap` con `is_imputed=false` en paro: salida `252 filas, 252 oficiales, 0 imputadas`

#### Scenario: Municipio sin fuente oficial no inventa paro

- GIVEN un municipio donde Lanbide 18/21 no devuelve registro y no hay normalizado
- WHEN se completa el paro
- THEN `tasa_paro_lanbide_pct=None`, `metodo_imputacion=ninguno`, `is_imputed=false`
- AND `grep -c "is_imputed.*true" data/resultados/udalmap_paro.csv` = 0 (salida: 0)

## ADDED Requirements

### Requirement: OUTLIER-01 — Limpieza dura de outliers en extracción (M1)

El sistema SHALL filtrar `precio_m2` al rango [3, 50] €/m² y `superficie_m2` al rango [10, 500] m² en `transform/filtrar_outliers.py` y `transform/generar_anuncios_residencial_filtrado.py`. SHALL excluir del `precio_medio` los valores fuera del rango intercuartílico (IQR) aunque ya estén dentro de [3, 50], y SHALL castear `habitaciones` a entero. `precio_m2` y `superficie_m2` fuera de rango SHALL descartarse con motivo, nunca recortarse ni winsorizarse en esta capa (la winsorización de mediana vive en AGREGACION-01 de `mongodb-y-analisis`). Cada exclusión se SHALL contar por motivo y publicarse en el log de filtrado.

#### Scenario: Filtro de rangos y exclusión IQR

- GIVEN un anuncio con `precio_m2=0,16` y otro con `precio_m2=83,33` y otro con `habitaciones=2,5`
- WHEN corre `python transform/generar_anuncios_residencial_filtrado.py`
- THEN el primero y el segundo se excluyen con motivo `precio_m2_fuera_3_50`, el tercero entra con `habitaciones=2` entero
- AND `python transform/filtrar_outliers.py` emite salida: `excluidos_precio_m2=2, excluidos_superficie=0, excluidos_iqr_precio_medio=N, habitaciones_int=100%`

#### Scenario: Precio dentro de rango pero fuera de IQR no entra en la media

- GIVEN precio `precio_m2` dentro de [3, 50] pero por encima de Q3+1,5·IQR
- WHEN se calcula el precio medio municipal
- THEN esa observación se excluye del precio medio y queda contada como `iqr_excluido`
- AND `grep -c iqr_excluido log_filtrado.txt` ≥ 1 (salida: N ≥ 1)

### Requirement: DEDUP-01 — Dedup dura por `property_fingerprint` (M6)

El sistema SHALL deduplicar en `transform/unificar_anuncios.py` por `property_fingerprint` (generado en `transform/generar_fingerprint.py`): el primer anuncio de cada huella conserva, el resto se descarta con motivo `duplicado_fingerprint`. SHALL NOT sobrevivir ningún duplicado cross-portal en la salida unificada. El conteo de descartados por fingerprint SHALL registrarse en el log y ser verificable con `pytest tests -q`.

#### Scenario: Duplicado cross-portal eliminado

- GIVEN dos anuncios de portales distintos con idéntico `property_fingerprint` (misma vivienda)
- WHEN corre `python transform/unificar_anuncios.py`
- THEN en `data/procesado/anuncios_unificados.csv` hay 1 sola fila con ese fingerprint y el descartado lleva motivo `duplicado_fingerprint`
- AND `python -c "import pandas as pd; d=pd.read_csv('data/procesado/anuncios_unificados.csv'); print(d['property_fingerprint'].duplicated().sum())"` → salida: `0`

#### Scenario: Sin duplicados tras la carga

- GIVEN la salida unificada sin duplicados
- WHEN se carga con `python -m storage.load_mongo`
- THEN `anuncios` en Mongo no contiene dos documentos con el mismo fingerprint
- AND `pytest tests -q` sigue en verde con el test de dedup incluido
