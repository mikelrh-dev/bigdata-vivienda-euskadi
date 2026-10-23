# Almacenamiento y streaming — Especificación

**Capacidad:** `almacenamiento-y-streaming`
**Estado:** Pendiente
**Criterios cubiertos:** BDA-RA1 Almacenamiento HDFS (10), Kafka (10),
Integración (10)
**Contrato:** `../contrato-reto/spec.md`

---

## Purpose

Guardar los datos originales en HDFS organizados, simular la llegada de
anuncios nuevos con un productor y un consumidor Kafka en Python, y demostrar
el flujo completo hasta MongoDB.

---

## Requirements

### Requirement: HDFS-01 — Originales y procesados, con recuperación

El sistema SHALL almacenar en HDFS los datos originales y los procesados en
rutas separadas, y SHALL demostrar que puede recuperarlos.

#### Scenario: Originales y procesados conviven

- GIVEN los datos en `data/raw/`
- WHEN se suben a HDFS
- THEN `/raw/` contiene los originales tal cual llegaron
- AND `/procesado/` contiene la versión normalizada

#### Scenario: La recuperación se demuestra

- GIVEN un fichero ya subido
- WHEN se descarga de HDFS
- THEN el contenido coincide con el original
- AND el tamaño en bytes es el mismo

### Requirement: KAFKA-01 — Productor y consumidor en Python

El sistema SHALL tener un productor y un consumidor escritos en Python que
funcionen y procesen mensajes reales.

#### Scenario: El productor publica anuncios

- GIVEN los anuncios extraídos
- WHEN el productor se ejecuta
- THEN cada anuncio se publica como mensaje en el topic
- AND el mensaje es JSON con el precio y el municipio

#### Scenario: El consumidor procesa los mensajes

- GIVEN el topic con mensajes
- WHEN el consumidor se ejecuta
- THEN lee cada mensaje
- AND lo inserta en MongoDB
- AND reporta cuántos ha procesado

#### Scenario: El consumidor no duplica

- GIVEN un anuncio ya insertado
- WHEN llega el mismo anuncio por segunda vez
- THEN se actualiza en lugar de duplicarse

### Requirement: INTEGRACION-01 — Flujo completo hasta MongoDB

El sistema SHALL demostrar el recorrido completo desde el origen hasta
MongoDB, con los componentes conectados entre sí.

#### Scenario: El flujo extremo a extremo

- GIVEN una fuente, HDFS, Kafka y MongoDB en marcha
- WHEN se ejecuta el pipeline
- THEN un dato sale de la fuente
- AND pasa por HDFS y por Kafka
- AND termina consultable en MongoDB

#### Scenario: La caída de un componente se aísla

- GIVEN MongoDB detenido
- WHEN el consumidor intenta escribir
- THEN el error se registra
- AND el productor sigue publicando sin corromper el pipeline
