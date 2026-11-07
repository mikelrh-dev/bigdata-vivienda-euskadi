# Proposal: kafka-vm-broker

## Intent

El broker Kafka 4.3.1 KRaft (combined) de la VM ZooKeeper está apagado y su
log.dirs apunta a /tmp/kraft-combined-logs volatil, que hoy no existe. Sin broker
no se pueden verificar KAFKA-01 ni INTEGRACION-01 del spec
almacenamiento-y-streaming, ni crear el topic anuncios_inmobiliarios.

## Scope

### In Scope

- Crear log.dirs persistente en la VM: ~/kafka-logs
- Ajustar ~/kafka/config/server.properties: log.dirs y advertised.listeners
  alcanzable desde Windows respectando KRaft
- Formatear storage KRaft, arrancar broker con kafka-server-start.sh -daemon
- Esperar 9094 abierto en la VM
- Crear topic anuncios_inmobiliarios con 3 particiones
- Smoke test con kafka-console-producer y kafka-console-consumer con JSON,
  sin tocar MongoDB
- Documentar comando por comando en docs/kafka_vm.md

### Out of Scope

- Productor y consumidor Python (kafka-python-ng) de KAFKA-01 nivel 10
- HDFS, rutas /raw y /procesado, hdfs_utils.py
- storage/*, .env, MongoDB, servidor Python en la VM
- ZooKeeper desempaquetado (KRaft no lo usa)

## Capabilities

### New Capabilities

- None. No se crea una capacidad nueva.

### Modified Capabilities

- almacenamiento-y-streaming: KAFKA-01 exige broker persistente antes de
  productor y consumidor; este cambio aporta la infraestructura, no el codigo
  Python.

## Approach

Comando por comando por SSH en la VM: mkdir ~/kafka-logs, edicion de
server.properties con sed, formateo con kafka-storage.sh random-uuid + format,
arranque en daemon y espera activa de 9094, creacion de topic y prueba
console con JSON. Verificacion desde Windows por conexion TCP a 9094 y por
ss -tlnp en la VM.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| ~/kafka/config/server.properties (VM) | Modified | log.dirs, advertised.listeners |
| ~/kafka-logs (VM) | New | Directorio persistente de logs KRaft |
| docs/kafka_vm.md (repo) | New | Ficha comando por comando con IP, puertos y salidas |
| openspec/changes/kafka-vm-broker/* | New | Proposal, delta spec, design, tasks, verify-report |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| advertised.listeners incorrecto rompe cliente Windows | Med | PLAINTEXT con 192.168.201.162, CONTROLLER en localhost |
| Format genera meta.properties nuevo y pierde datos | Low | No hay log.dirs previo; no hay datos que perder |
| Broker no arranca por RAM Java | Low | Java 17 ya probado en octubre; espera y ss -tlnp |

## Rollback Plan

Parar broker con kafka-server-stop.sh, revertir las dos lineas de
server.properties (log.dirs a /tmp/kraft-combined-logs y advertised a
localhost) y borrar ~/kafka-logs si se desea. No hay commit que revertir.

## Dependencies

- VM ZooKeeper 192.168.201.162, usuario mikel, SSH con
  /c/Users/mikel/.ssh/id_vm_hermes. Kafka 4.3.1 en ~/kafka, Java 17.

## Success Criteria

- [ ] ss -tlnp muestra 9094 en la VM y topic anuncios_inmobiliarios existe
  con 3 particiones en kafka-topics --describe
- [ ] Mensaje JSON producido con console-producer y leido con console-consumer
- [ ] docs/kafka_vm.md contiene cada comando con salida resumida
