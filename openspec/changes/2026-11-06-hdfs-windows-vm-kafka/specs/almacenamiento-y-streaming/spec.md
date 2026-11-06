# Delta: almacenamiento-y-streaming (HDFS-01, KAFKA-01, INTEGRACION-01)

## MODIFIED Requirements

### Requirement: HDFS-01 — Originales vía Kafka Windows>VM>Hadoop

El sistema SHALL almacenar en HDFS (`10.22.87.215:50070`) los datos originales en rutas separadas y SHALL demostrar recuperación con tamaño en bytes igual. El flujo SHALL ser: Windows publica `data/raw/` por Kafka (`192.168.201.162:9094`, broker solo en la VM) y consumidor Python en la VM hace el put WebHDFS con `storage/hdfs_utils.py` (producción que genera `raw/` con SHA y estado resumible). NO se sube directo Windows>HDFS. El destino SHALL ser `/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw` (861 MB). Procesados (`data/procesado`) SHOULD no subirse (solo local). Toda salida VM SHALL recopilarse en `docs/trazabilidad_vm.md` (Fecha/Objetivo/Máquina=VM/Comando/Salida/Conclusión).

#### Scenario: Windows > Kafka > VM > Hadoop

- GIVEN `data/raw/` en Windows
- WHEN se publica por Kafka y el consumidor VM hace el put WebHDFS
- THEN HDFS `/raw/` contiene los originales tal cual
- AND `read_file_sha256` coincide byte a byte con el local
- AND la VM queda logueada en `docs/trazabilidad_vm.md` con Máquina=VM, offsets y LISTSTATUS

### Requirement: KAFKA-01 — Broker solo en la VM, productor W / consumidor VM

El sistema SHALL tener el broker Kafka solo en la VM (`~/kafka`, 4.3.1 KRaft, 9093/9094). Producer Python corre en Windows y publica a `192.168.201.162:9094`. Consumer Python corre en la VM: lee el topic y hace el put a HDFS (no a Mongo). Mongo SHALL ser local en Windows; el consumidor NO SHALL escribir en Mongo en este flujo.

#### Scenario: Kafka participa Windows>VM

- GIVEN el broker en `192.168.201.162:9094` y topic `anuncios_inmobiliarios`
- WHEN el productor Windows publica `data/raw/` y el consumidor VM consume
- THEN `ss -tlnp` muestra LISTEN 9093/9094, `kafka-topics --describe` 3 particiones, y el consumidor VM sube a HDFS con SHA igual

### Requirement: INTEGRACION-01 — Flujo completo Windows>Kafka>VM>HDFS

El sistema SHALL demostrar en vivo el flujo completo Windows>Kafka>VM>HDFS con todos los componentes encadenados según rúbrica PDF BDA RA1 Integración línea 79 "Demuestra el flujo completo hasta MongoDB" (el Mongo de este flujo es el análisis local, no el sink de este change; el sink de este change es HDFS). El gate extremo a extremo SHALL imprimir offsets, LISTSTATUS y SHA y loguear la salida completa en `docs/trazabilidad_vm.md`.

#### Scenario: Flujo extremo a extremo Kafka>HDFS

- GIVEN Kafka en la VM, HDFS centro accesible desde la VM
- WHEN se ejecuta el gate Windows>Kafka>VM>HDFS
- THEN un `data/raw` sale de Windows, pasa por Kafka, la VM lo sube a HDFS y queda recuperable con SHA igual
