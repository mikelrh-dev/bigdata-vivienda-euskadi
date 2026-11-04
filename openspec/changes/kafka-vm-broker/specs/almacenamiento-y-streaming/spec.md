# Delta for almacenamiento-y-streaming

## ADDED Requirements

### Requirement: KAFKA-INFRA-01 — Broker KRaft persistente y alcanzable

El sistema MUST tener el broker Kafka 4.3.1 KRaft (combined) arrancado en la
VM ZooKeeper con log.dirs persistente fuera de /tmp, listeners en 9093
(CONTROLLER) y 9094 (PLAINTEXT), y advertised.listeners alcanzable desde el
host Windows (192.168.201.162). El broker MUST exponer el topic
anuncios_inmobiliarios.

#### Scenario: Broker persistente en marcha

- GIVEN la VM con ~/kafka sin broker en escucha
- WHEN se crea ~/kafka-logs y se arranca con kafka-server-start.sh -daemon
- THEN ss -tlnp muestra 9094 en escucha en la VM
- AND log.dirs apunta a ~/kafka-logs y no a /tmp

#### Scenario: Advertised alcanzable desde Windows

- GIVEN el broker con advertised.listeners PLAINTEXT://192.168.201.162:9094
- WHEN un cliente Windows conecta a 192.168.201.162:9094
- THEN kafka-topics --list devuelve anuncios_inmobiliarios
- AND la conexion TCP a 9094 no se rechaza

#### Scenario: Topic y smoke test JSON

- GIVEN el broker en marcha
- WHEN se crea anuncios_inmobiliarios con 3 particiones y se envia JSON con
  console-producer
- THEN kafka-topics --describe muestra 3 particiones
- AND console-consumer lee el mensaje JSON sin tocar MongoDB
