# Delta for presentacion-de-resultados

## ADDED Requirements

### Requirement: COMPARATIVA-MONGO-01 — Comparativa de 3 municipios robustos generada desde Mongo

El sistema SHALL generar automaticamente la comparativa de los 3 municipios con mas anuncios (n_anuncios) entre los que tienen n>=30, desde `pipeline_indicadores_municipio`, con lookup de `tasa_paro_lanbide_pct` en `municipios.empleo`. La comparativa SHALL incluir codigo, nombre, n_anuncios, esfuerzo 18-34, esfuerzo 16-29, precio medio, cuantia de alquiler y paro. Los valores MUST proceder de MongoDB; si un valor falta SHALL quedar nulo, nunca inventado. La comparativa SHALL persistirse en `data/resultados/comparativa_3_municipios_mongo.csv`.

#### Scenario: Tres filas robustas con paro

- GIVEN MongoDB cargado con `municipios`, `anuncios` y `alquiler_municipal`
- WHEN se ejecuta `comparativa_tres_robustos()`
- THEN devuelve exactamente 3 filas ordenadas por n_anuncios descendente
- AND cada fila tiene n_anuncios >= 30
- AND cada fila tiene `tasa_paro_lanbide_pct` no nulo

#### Scenario: CSV reproducible sin valores inventados

- GIVEN la comparativa generada
- WHEN se escribe el CSV
- THEN el CSV tiene 3 filas de datos con las 8 columnas pedidas
- AND cada valor coincide con el devuelto por la funcion
- AND regenerar el CSV reproduce los mismos valores

#### Scenario: Informe cita la comparativa con advertencias

- GIVEN el CSV generado desde Mongo
- WHEN se redacta el informe
- THEN el informe contiene una tabla de 3 filas con los mismos valores
- AND una conclusion por municipio vinculada a esfuerzo, precio y paro
- AND advertencia de muestra pequena (solo 4 municipios con n>=30) y de proxy de renta joven

## MODIFIED Requirements

Ninguno. No se altera el comportamiento de `CONCLUSION-01` ni del resto de requisitos vigentes.

## REMOVED Requirements

Ninguno.

## RENAMED Requirements

Ninguno.
