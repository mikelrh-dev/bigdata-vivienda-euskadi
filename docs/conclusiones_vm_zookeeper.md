# VM ZooKeeper - Conclusiones de exploración en solo lectura

**Fecha:** 2026-11-04  
**Fuente:** rúbrica `brief/RETO 1Evaluacion SBD-BDAv2.pdf` y `brief/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx`  
**Alcance:** Solo lectura por SSH sin modificaciones. VM `192.168.201.162` Ubuntu 22.04.3 LTS jammy.

## Lo que hay

- Sistema: Linux mikel 5.15.0-198-generic, 2 CPU, 3,8 GiB RAM, disco 19G con 8,5G libre, uptime 1h 32m al sondear
- Java 17.0.20.1 y Python 3.10 sin pip en la VM
- Kafka instalado pero apagado: `~/kafka` con Kafka 4.3.1 KRaft combined y `~/kafka_2.13-4.2.2` desempaquetado. Config `server.properties` con `process.roles broker,controller`, `node.id 1`, `listeners PLAINTEXT 9094` y `CONTROLLER 9093`, `log.dirs /tmp/kraft-combined-logs` (volátil), sin escucha hoy en 9092/9093/9094
- ZooKeeper desempaquetado pero no usado: `apache-zookeeper-3.8.7-bin` y `zookeeper-lab` 3 nodos `zk1 2181`, `zk2 2182`, `zk3 2183`
- HDFS en clúster central de Hadoop, no en Windows ni en la VM local. En la VM no hay Hadoop ni Docker, pero eso no es bloqueante: el runtime, las rutas `/raw` y `/procesado` y la prueba de recuperación se hacen contra el clúster del centro vía WebHDFS. Decisión previa al siguiente loop: conectar `storage/hdfs_utils.py` al endpoint del centro con su host, puerto y credenciales según `.env`.
- Repo: `storage` solo tiene `mongo.py`, `load_mongo.py` y `clean_mongo.py`. Faltan `hdfs_utils.py`, `kafka_producer.py` y `kafka_consumer.py`
- `.env` desactualizado: apunta a `192.168.1.100:9092` y `HDFS_URL localhost:9870`, no a `192.168.201.162:9094`
- Mongo hecho: 15 colecciones y datos listos (raw 355 ficheros, procesado 187)

## Lo que falta para la rúbrica BDA

- **HDFS 10:** conexión a Hadoop en clúster central, rutas `/raw` y `/procesado`, subida y prueba de recuperación byte a byte con SHA vía WebHDFS. No se instala Hadoop en Windows ni en la VM.
- **Kafka 10:** broker arrancado con `log.dirs` persistente y `advertised.listeners` alcanzable desde Windows, topic `anuncios_inmobiliarios`, productor Python JSON con precio y municipio y consumidor con upsert idempotente a Mongo
- **Integración 10:** orquestador fuente → HDFS → Kafka → Mongo consultable, con 2 fuentes relacionadas por código INE y prueba de caída de Mongo

## Conclusiones priorizadas

### 1. Desbloquear Kafka en la VM (Impacto 9, Riesgo 3)
Arrancar el binario existente ya probado en octubre, mover `log.dirs` fuera de `/tmp`, ajustar `.env` a `192.168.201.162:9094`, crear topic y probar con `console-producer` y `console-consumer`. Sin broker no se puede probar `KAFKA-01` ni `INTEGRACION-01`.

### 2. Conectar HDFS al clúster central (Impacto 8, Riesgo 3)
No se instala Hadoop ni en Windows ni en la VM. El clúster del centro ya está disponible, así que el trabajo es implementar `storage/hdfs_utils.py` contra WebHDFS con el endpoint del centro definido en `.env`, con put de `data/raw` a `/raw` y `data/procesado` a `/procesado` más get y comparativa SHA. Queda pendiente capturar host, puerto y auth del centro para cerrar el diseño.

### 3. Cerrar con gate extremo a extremo (Impacto 9, Riesgo 2)
Crear `tests/test_contrato.py` para `HDFS-01`, `KAFKA-01` e `INTEGRACION-01` con subida a HDFS, publicación por Kafka, consumo a Mongo y verificación de código INE común. Es el único criterio que cierra el 10 en Integración.
