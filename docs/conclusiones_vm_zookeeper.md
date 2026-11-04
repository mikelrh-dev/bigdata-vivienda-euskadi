# VM ZooKeeper - Conclusiones de exploración en solo lectura

**Fecha:** 2026-11-04  
**Fuente:** rúbrica `brief/RETO 1Evaluacion SBD-BDAv2.pdf` y `brief/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx`  
**Alcance:** Solo lectura por SSH sin modificaciones. VM `192.168.201.162` Ubuntu 22.04.3 LTS jammy.

## Lo que hay

- Sistema: Linux mikel 5.15.0-198-generic, 2 CPU, 3,8 GiB RAM, disco 19G con 8,5G libre, uptime 1h 32m al sondear
- Java 17.0.20.1 y Python 3.10 sin pip en la VM
- Kafka instalado pero apagado: `~/kafka` con Kafka 4.3.1 KRaft combined y `~/kafka_2.13-4.2.2` desempaquetado. Config `server.properties` con `process.roles broker,controller`, `node.id 1`, `listeners PLAINTEXT 9094` y `CONTROLLER 9093`, `log.dirs /tmp/kraft-combined-logs` (volátil), sin escucha hoy en 9092/9093/9094
- ZooKeeper desempaquetado pero no usado: `apache-zookeeper-3.8.7-bin` y `zookeeper-lab` 3 nodos `zk1 2181`, `zk2 2182`, `zk3 2183`
- HDFS ausente por completo: sin Hadoop en home, `/opt`, `/usr/local` ni `/etc/hadoop`, sin docker en VM y Docker Desktop en Windows caído
- Repo: `storage` solo tiene `mongo.py`, `load_mongo.py` y `clean_mongo.py`. Faltan `hdfs_utils.py`, `kafka_producer.py` y `kafka_consumer.py`
- `.env` desactualizado: apunta a `192.168.1.100:9092` y `HDFS_URL localhost:9870`, no a `192.168.201.162:9094`
- Mongo hecho: 13 colecciones productivas y datos listos (raw 199 ficheros, procesado 118)

## Lo que falta para la rúbrica BDA

- **HDFS 10:** runtime Hadoop, rutas `/raw` y `/procesado`, subida y prueba de recuperación byte a byte con SHA
- **Kafka 10:** broker arrancado con `log.dirs` persistente y `advertised.listeners` alcanzable desde Windows, topic `anuncios_inmobiliarios`, productor Python JSON con precio y municipio y consumidor con upsert idempotente a Mongo
- **Integración 10:** orquestador fuente → HDFS → Kafka → Mongo consultable, con 2 fuentes relacionadas por código INE y prueba de caída de Mongo

## Conclusiones priorizadas

### 1. Desbloquear Kafka en la VM (Impacto 9, Riesgo 3)
Arrancar el binario existente ya probado en octubre, mover `log.dirs` fuera de `/tmp`, ajustar `.env` a `192.168.201.162:9094`, crear topic y probar con `console-producer` y `console-consumer`. Sin broker no se puede probar `KAFKA-01` ni `INTEGRACION-01`.

### 2. Decidir HDFS primero como diseño (Impacto 8, Riesgo 7)
Dos vías: Docker en Windows con `HDFS_URL localhost:9870` ya definida (solo hay que levantar Docker Desktop caído) o Hadoop pseudo-distribuido en VM con Java 17 y RAM ajustada. Implementar `storage/hdfs_utils.py` con put/get y comparativa SHA.

### 3. Cerrar con gate extremo a extremo (Impacto 9, Riesgo 2)
Crear `tests/test_contrato.py` para `HDFS-01`, `KAFKA-01` e `INTEGRACION-01` con subida a HDFS, publicación por Kafka, consumo a Mongo y verificación de código INE común. Es el único criterio que cierra el 10 en Integración.
