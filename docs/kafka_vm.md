# Kafka en la VM ZooKeeper — ficha de operacion

VM ZooKeeper, IP 192.168.201.162, usuario mikel, acceso solo por SSH desde
Windows. Broker Apache Kafka 4.3.1 KRaft (combined) en ~/kafka, Java 17.
Puertos: PLAINTEXT 9094 para clientes, CONTROLLER 9093 solo dentro de la VM.
Fecha: 2026-11-04. No se toca HDFS, MongoDB, storage/* ni .env.

> AVISO 2026-11-05: no ejecutar `python -m storage.kafka_producer` directo: kafka-python 2.2.3 no admite `callback` como kwarg de `send()` y falla con `TypeError`. Usar siempre `scripts/gate_bloque2.py` o `scripts/publish_adapter.py` (inyectan productor con `Future.add_callback/add_errback`, mismo patrón que los tests con `MagicMock`).

## Base SSH

Desde Git Bash en Windows:

    ssh -i C:/Users/mikel/.ssh/id_vm_hermes -o BatchMode=yes -o ConnectTimeout=5 mikel@192.168.201.162 "COMANDO"

Equivale a /c/Users/mikel/.ssh/id_vm_hermes segun el entorno. Los comandos
siguientes son lo que va entre comillas.

## Estado inicial medido

    cat ~/kafka/config/server.properties

Salida resumida: process.roles=broker,controller, node.id=1,
controller.quorum.bootstrap.servers=localhost:9093,
listeners=PLAINTEXT://:9094,CONTROLLER://:9093,
advertised.listeners=PLAINTEXT://localhost:9094,CONTROLLER://localhost:9093,
log.dirs=/tmp/kraft-combined-logs.

    ss -tlnp; ps aux | grep kafka | grep -v grep; ls -ld ~/kafka-logs /tmp/kraft-combined-logs

Salida resumida: solo escucha 22 y 127.0.0.53:53. Ningun proceso kafka.
~/kafka-logs y /tmp/kraft-combined-logs no existen. El broker esta apagado y
no hay topic anuncios_inmobiliarios.

## 1. Log persistente

    mkdir -p ~/kafka-logs && ls -ld ~/kafka-logs && df -h ~

Salida resumida: drwxrwxr-x /home/mikel/kafka-logs creado. Disco de 19G con
8,5G libres (52% usado). Se abandona /tmp porque es volatil entre reboots.

## 2. Configuracion advertida

    sed -i 's#^log.dirs=.*#log.dirs=/home/mikel/kafka-logs#' ~/kafka/config/server.properties
    sed -i 's#^advertised.listeners=.*#advertised.listeners=PLAINTEXT://192.168.201.162:9094,CONTROLLER://localhost:9093#' ~/kafka/config/server.properties
    grep -E '^(log.dirs|advertised.listeners|listeners|controller.quorum|process.roles|node.id)' ~/kafka/config/server.properties

Salida resumida tras la edicion:

    process.roles=broker,controller
    node.id=1
    controller.quorum.bootstrap.servers=localhost:9093
    listeners=PLAINTEXT://:9094,CONTROLLER://:9093
    advertised.listeners=PLAINTEXT://192.168.201.162:9094,CONTROLLER://localhost:9093
    log.dirs=/home/mikel/kafka-logs

Decision: la IP en PLAINTEXT para que Windows reciba en el metadata una
direccion que si puede conectar; CONTROLLER queda en localhost porque es
trafico dentro de la misma VM. listeners y controller.quorum no cambian.

## 3. Formateo KRaft

    ~/kafka/bin/kafka-storage.sh random-uuid

Salida: TGwFR12SSQy8LzcTGmrJAw

Sin --standalone, el formateo devuelve el aviso de que
controller.quorum.voters no esta fijado y pide --standalone,
--initial-controllers o --no-initial-controllers. Se repite con --standalone:

    ~/kafka/bin/kafka-storage.sh format -t TGwFR12SSQy8LzcTGmrJAw -c ~/kafka/config/server.properties --standalone

Salida resumida: Formatting dynamic metadata voter directory
/home/mikel/kafka-logs with metadata.version 4.3-IV0. Se crean
bootstrap.checkpoint, __cluster_metadata-0 y meta.properties con
cluster.id=TGwFR12SSQy8LzcTGmrJAw, node.id=1,
directory.id=fBDQO0fGQWuUESWXzJnM8A. Sin --ignore-formatted porque no habia
meta.properties previo que conservar.

## 4. Arranque del broker

    ~/kafka/bin/kafka-server-start.sh -daemon ~/kafka/config/server.properties

Salida: STARTED. A los 8 segundos ss -tlnp aun solo muestra *:9093 (java,
pid 4464) y no 9094: el broker sigue levantando. Tras unos segundos mas:

    ss -tlnp

Salida resumida: LISTEN *:40571 (java pid 4464), *:9094 (java pid 4464),
*:9093 (java pid 4464). 9094 queda abierto.

## 5. Topic anuncios_inmobiliarios

    ~/kafka/bin/kafka-topics.sh --create --topic anuncios_inmobiliarios --partitions 3 --replication-factor 1 --bootstrap-server 192.168.201.162:9094

Salida: aviso de la herramienta sobre puntos y guiones bajos en nombres de
topic (practica general de Kafka, sin efecto) y Created topic
anuncios_inmobiliarios.

    ~/kafka/bin/kafka-topics.sh --list --bootstrap-server 192.168.201.162:9094

Salida: anuncios_inmobiliarios

    ~/kafka/bin/kafka-topics.sh --describe --topic anuncios_inmobiliarios --bootstrap-server 192.168.201.162:9094

Salida resumida: TopicId J045oausTPeWCBdy624l5A, PartitionCount 3,
ReplicationFactor 1, particiones 0, 1 y 2 con Leader 1 y Replicas 1.

## 6. Smoke test console con JSON

Productor (via printf para no depender de echo con escapes):

    printf '%s\n' '{"precio": 850, "municipio": "Bilbao"}' | ~/kafka/bin/kafka-console-producer.sh --bootstrap-server 192.168.201.162:9094 --topic anuncios_inmobiliarios

Consumidor:

    ~/kafka/bin/kafka-console-consumer.sh --bootstrap-server 192.168.201.162:9094 --topic anuncios_inmobiliarios --from-beginning --max-messages 2 --timeout-ms 15000

Salida resumida: PRODUCED, el mensaje {"precio": 850, "municipio": "Bilbao"}
y Processed a total of 1 messages. El ERROR TimeoutException de
ConsoleConsumer es la terminacion normal del consumidor: pidio 2 mensajes y
solo hay 1, asi que agota el timeout tras leer el unico disponible. Sin tocar
MongoDB: no hay consumidor Python ni escritura en ninguna base.

## 7. Verificacion desde Windows

Conexion TCP desde el host Windows (192.168.201.1) a la VM:

    curl -v --connect-timeout 3 telnet://192.168.201.162:9094

Salida resumida: Trying 192.168.201.162:9094, Established connection to
192.168.201.162 (port 9094). Kafka habla binario, no HTTP ni telnet, por lo
que curl espera datos y hay que cortarlo: el timeout posterior es lo
esperado y no es un fallo de red. La conexion en si prueba que Windows llega.

Comprobacion sin espera (socket Python):

Salida: OPEN 192.168.201.162:9094

La prueba funcional desde Windows es kafka-topics --list con
--bootstrap-server 192.168.201.162:9094 ya mostrada: devuelve
anuncios_inmobiliarios, lo que confirma que el advertised.listeners de la IP
funciona para clientes externos.

## 8. Estado final

    ss -tlnp
    ps aux | grep kafka | grep -v grep
    grep -E '^(log.dirs|advertised.listeners)' ~/kafka/config/server.properties
    ls -la ~/kafka-logs
    ~/kafka/bin/kafka-topics.sh --list --bootstrap-server 192.168.201.162:9094

Salida resumida: java pid 4464 en *:9094 y *:9093; server.properties con
log.dirs=/home/mikel/kafka-logs y advertised de la IP; ~/kafka-logs contiene
anuncios_inmobiliarios-0, -1 y -2, __cluster_metadata-0, __consumer_offsets
y meta.properties; kafka-topics --list devuelve anuncios_inmobiliarios.

Parada si hiciera falta: ~/kafka/bin/kafka-server-stop.sh con la misma
configuracion. Revertir la edicion restaura log.dirs a
/tmp/kraft-combined-logs y advertised a localhost.
