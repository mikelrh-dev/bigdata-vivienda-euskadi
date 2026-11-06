# Almacenamiento y streaming — Especificación

**Capacidad:** `almacenamiento-y-streaming`
**Estado:** Gate extremo a extremo PASS 2026-11-06 (HUELLA_SHA e32c3d3d..., GATE PASS en docs/trazabilidad_vm.md)
**Criterios cubiertos:** rúbrica v2 BDA-RA1 (HDFS, Kafka, integración: flujo
completo hasta MongoDB) con mapeo a SBD-RA1 Integración de fuentes (2 o más
fuentes relacionadas por un campo común)
**Contrato:** `../contrato-reto/spec.md`
**Fuente de verdad:** `brief/RETO 1Evaluacion SBD-BDAv2.pdf` — cotejo 2026-11-05 (BDA RA1, líneas 72-79; objetivos 3-5, líneas 23-25; requisitos BDA, líneas 33-36; entregable 2, línea 54; resultado final, líneas 58-66)

---

## Purpose

Guardar los datos originales en HDFS organizados, simular la llegada de
anuncios nuevos con un productor y un consumidor Kafka en Python, y demostrar
el flujo completo hasta MongoDB con al menos 2 fuentes diferentes
relacionadas por un campo común (mapeo a rúbrica v2 SBD-RA1 Integración de
fuentes).
_Evidencia PDF (sin requisitos nuevos):_ objetivo 3 «Almacenar en HDFS los
datos originales obtenidos» (PDF línea 23); objetivo 4 «Utilizar Apache Kafka
para simular la recepción de nuevos anuncios inmobiliarios» (PDF línea 24);
objetivo 5 «Guardar la información en MongoDB» (PDF línea 25); requisito BDA
«Almacenamiento de datos en HDFS» (PDF línea 34) y «Creación de un productor
y un consumidor Kafka utilizando Python» (PDF línea 35).

---

## Planificación 2026-11-06 (HDFS Windows>Kafka>VM>Hadoop, solo raw)

Flujo que marca la profesora: Windows (datos raw) > Kafka (broker solo en la VM) > consumidor Python en la VM > HDFS Hadoop centro (10.22.87.215:50070) en /data/raw/. Mongo solo en local Windows para análisis. Kafka NO escribe en Mongo en este flujo. Kafka solo está instalado en la VM (broker 4.3.1 KRaft); productor en Windows.

## Requirements

### Requirement: HDFS-01 — Originales y procesados, con recuperación

El sistema SHALL almacenar en HDFS los datos originales en rutas separadas y
SHALL demostrar que puede recuperarlos con tamaño en bytes igual. El sistema
SHOULD almacenar también los procesados en HDFS en ruta separada con
recuperación demostrable.
_Trazabilidad PDF BDA-RA1 (cotejo 2026-11-05):_ criterio Almacenamiento HDFS,
10 puntos «Organiza originales y procesados y demuestra su recuperación»
(PDF línea 77, tabla BDA RA1 líneas 72-79). Estado: SHALL acreditado para
originales y recuperación con tamaño igual; procesados queda en SHOULD porque
hoy el procesado está solo en local y está ausente en HDFS. No se eleva a
SHALL donde hoy no cumple.

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
funcionen en modo offline probado y procesen mensajes reales. El sistema
SHOULD tener productor/consumidor Python vivos sobre broker real.
_Trazabilidad PDF BDA-RA1 (cotejo 2026-11-05):_ criterio Kafka, 10 puntos
«Productor y consumidor Python funcionan y procesan mensajes» (PDF línea 78,
tabla BDA RA1 líneas 72-79). Estado: SHALL acreditado para código Python
offline; en vivo sobre broker real queda en SHOULD porque hoy Kafka Python en
vivo no está probado (solo tests offline). No se eleva a SHALL donde hoy no
cumple. Evidencia PDF adicional (sin requisitos nuevos): objetivo 4 (PDF
línea 24) y requisito BDA «Creación de un productor y un consumidor Kafka
utilizando Python» (PDF línea 35).

#### Scenario: El productor publica anuncios

- GIVEN los anuncios extraídos
- WHEN el productor se ejecuta
- THEN cada anuncio se publica como mensaje en el topic
- AND el mensaje es JSON con el precio y el municipio

#### Scenario: El consumidor procesa los mensajes

- GIVEN el topic con mensajes
- WHEN el consumidor se ejecuta
- THEN lee cada manifiesto raw_manifest
- AND hace put WebHDFS al Hadoop centro desde la VM (NO escribe en Mongo en este flujo)
- AND reporta cuántos ha procesado

#### Scenario: El consumidor no duplica

- GIVEN un anuncio ya insertado
- WHEN llega el mismo anuncio por segunda vez
- THEN se actualiza en lugar de duplicarse

### Requirement: INTEGRACION-01 — Flujo completo hasta MongoDB

El sistema SHALL cargar datos de 2 o más fuentes diferentes y SHALL
relacionarlos mediante al menos 1 campo común (criterio RA1 Integración de
fuentes v2). Para el nivel 7, SHALL cargar datos de 2 fuentes diferentes. El
campo común SHALL ser el mismo en ambas fuentes y SHALL permitir relacionar
los registros en MongoDB. El sistema SHOULD demostrar en vivo el flujo
completo desde el origen hasta MongoDB con los componentes encadenados entre
sí (flujo completo BDA-RA1).
_Trazabilidad PDF BDA-RA1 (cotejo 2026-11-05):_ criterio Integración, 10 puntos
«Demuestra el flujo completo hasta MongoDB» (PDF línea 79, tabla BDA RA1
líneas 72-79) y criterio SBD RA1 Integración de fuentes, 10 puntos «Carga
datos de 2 o más fuentes diferentes y las relaciona mediante al menos 1 campo
común» (PDF línea 91). Estado: SHALL acreditado para carga y relación de 2+
fuentes por campo común; flujo completo en vivo queda en SHOULD porque hoy la
integración está no encadenada (gate extremo a extremo real pendiente). No se
eleva a SHALL donde hoy no cumple. Evidencia PDF adicional (sin requisitos
nuevos): objetivo 5 «Guardar la información en MongoDB» (PDF línea 25);
entregable 2 «Datos: ficheros originales almacenados en HDFS y base de datos
MongoDB» (PDF línea 54); resultado final «Debéis demostrar, utilizando datos
reales, qué municipios de Euskadi ofrecen mejores posibilidades de
emancipación para una persona joven y explicar por qué» (PDF líneas 58-66).

#### Scenario: El flujo extremo a extremo

- GIVEN una fuente, HDFS, Kafka y MongoDB en marcha
- WHEN se ejecuta el pipeline
- THEN un dato sale de la fuente
- AND pasa por Kafka y la VM hace el put a HDFS
- AND queda recuperable en HDFS con SHA igual

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

---

## Evidencia PDF (objetivos, requisitos, entregables, resultado — sin SHALL nuevos)
- **Objetivo 3** (PDF línea 23): «Almacenar en HDFS los datos originales
  obtenidos». Evidencia para HDFS-01 (originales).
- **Objetivo 4** (PDF línea 24): «Utilizar Apache Kafka para simular la
  recepción de nuevos anuncios inmobiliarios». Evidencia para KAFKA-01.
- **Objetivo 5** (PDF línea 25): «Guardar la información en MongoDB».
  Evidencia para INTEGRACION-01.
- **Requisitos BDA** (PDF líneas 33-36): «Extracción de datos mediante API y
  scraping» (PDF línea 33), «Almacenamiento de datos en HDFS» (PDF línea 34),
  «Creación de un productor y un consumidor Kafka utilizando Python» (PDF
  línea 35), «Gestión de datos en formato JSON o CSV» (PDF línea 36, límite
  con FORMATO-01 en extraccion-datos).
- **Entregable 2** (PDF línea 54): «Datos: ficheros originales almacenados
  en HDFS y base de datos MongoDB». Evidencia para HDFS-01 e INTEGRACION-01.
- **Resultado final** (PDF líneas 58-66): demostrar con datos reales qué
  municipios ofrecen mejores posibilidades de emancipación y explicar por
  qué, con conclusiones respaldadas por los datos analizados. Contexto para
  INTEGRACION-01; no introduce requisitos nuevos en este spec.

## Mapa trazable PDF → requisito
| Requisito | PDF (líneas) | Criterio rubric / evidencia | Estado (2026-11-05) |
|---|---|---|---|
| HDFS-01 | Líneas 72-79 (BDA RA1, PDF línea 77); objetivos 3-5 líneas 23-25; requisitos líneas 33-36; entregable 2 línea 54 | BDA RA1 Almacenamiento HDFS 10 pts «Organiza originales y procesados y demuestra su recuperación» | SHALL: originales + recuperación con tamaño igual. SHOULD: procesados en HDFS (ausente hoy). |
| KAFKA-01 | Líneas 72-79 (PDF línea 78); objetivo 4 línea 24; requisito BDA línea 35 | BDA RA1 Kafka 10 pts «Productor y consumidor Python funcionan y procesan mensajes» | SHALL: Python offline probado. SHOULD: vivo sobre broker real (no probado hoy). |
| INTEGRACION-01 | Líneas 72-79 (PDF línea 79); SBD RA1 línea 91; objetivo 5 línea 25; entregable 2 línea 54; resultado final líneas 58-66 | BDA RA1 Integración 10 pts «Demuestra el flujo completo hasta MongoDB» + SBD RA1 Integración de fuentes 10 pts (2+ fuentes con campo común) | SHALL: 2+ fuentes con campo común. SHOULD: flujo completo en vivo (no encadenado hoy). |
