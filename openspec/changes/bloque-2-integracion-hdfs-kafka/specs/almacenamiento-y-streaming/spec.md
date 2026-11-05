# Delta for almacenamiento-y-streaming

## MODIFIED Requirements

### Requirement: HDFS-01 — Originales y procesados, con recuperación

El sistema SHALL almacenar en HDFS los datos originales en rutas separadas y
SHALL demostrar que puede recuperarlos con tamaño en bytes igual. El sistema
SHALL dejar el procesado listo en local con SHA firmado, lista de ficheros y
entrypoint de subida con `--dry-run` que liste lo que subiría.
(Previously: procesados queda en SHOULD porque hoy no está en HDFS.)

#### Scenario: Originales y procesados conviven

- GIVEN los datos en `data/raw/` y el procesado listo en local con SHA
- WHEN se ejecuta el entrypoint con `--dry-run` y se suben los originales
- THEN `/raw/` contiene los originales tal cual llegaron
- AND el dry-run lista el procesado que subiría sin subirlo aún

#### Scenario: La recuperación se demuestra

- GIVEN un fichero ya subido a HDFS
- WHEN se descarga de HDFS
- THEN el contenido coincide con el original
- AND el tamaño en bytes es el mismo

### Requirement: KAFKA-01 — Productor y consumidor en Python

El sistema SHALL tener un productor y un consumidor escritos en Python vivos
sobre el broker real que procesen los 759 anuncios. El consumidor SHALL
hacer upsert sin duplicar y SHALL reportar cuántos ha procesado.
(Previously: vivo sobre broker real queda en SHOULD porque solo hay tests
offline.)

#### Scenario: El productor publica anuncios

- GIVEN los 759 anuncios extraídos
- WHEN el productor Python se ejecuta contra el broker real
- THEN cada anuncio se publica como mensaje JSON en el topic
- AND el mensaje incluye precio y municipio

#### Scenario: El consumidor procesa los mensajes

- GIVEN el topic con 759 mensajes
- WHEN el consumidor Python se ejecuta
- THEN lee cada mensaje y lo inserta en MongoDB con upsert
- AND reporta 759 procesados

#### Scenario: El consumidor no duplica

- GIVEN un anuncio ya insertado
- WHEN llega el mismo anuncio por segunda vez
- THEN se actualiza en lugar de duplicarse

### Requirement: INTEGRACION-01 — Flujo completo hasta MongoDB

El sistema SHALL cargar datos de 2 o más fuentes diferentes y SHALL
relacionarlos mediante al menos 1 campo común; el campo común SHALL ser el
mismo en ambas fuentes. El sistema SHALL demostrar en vivo el flujo completo
encadenado HDFS→Kafka→MongoDB con 10 anuncios de prueba consultables por
`codigo_ine`.
(Previously: flujo completo en vivo queda en SHOULD porque no está
encadenado.)

#### Scenario: El flujo extremo a extremo

- GIVEN HDFS, Kafka y MongoDB en marcha
- WHEN el gate publica 10 anuncios de prueba y los consume a MongoDB
- THEN un dato sale de la fuente, pasa por HDFS y por Kafka
- AND termina consultable en MongoDB por `codigo_ine`

#### Scenario: Dos fuentes relacionadas por campo común — nivel 10

- GIVEN 2 o más fuentes diferentes cargadas
- WHEN se relacionan los datos en MongoDB
- THEN al menos 1 campo común une los registros de ambas fuentes
- AND el conjunto integrado es consultable en MongoDB

#### Scenario: Dos fuentes diferentes — nivel 7

- GIVEN 2 fuentes diferentes
- WHEN se cargan los datos en MongoDB
- THEN ambas fuentes quedan cargadas y distinguibles por origen

#### Scenario: La caída de un componente se aísla

- GIVEN MongoDB detenido
- WHEN el consumidor intenta escribir
- THEN el error se registra
- AND el productor sigue publicando sin corromper el pipeline
