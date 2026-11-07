# Tasks: kafka-vm-broker

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 80-120 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | single PR |
| Delivery strategy | single-pr |
| Chain strategy | single-pr |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: single-pr
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Broker + topic + docs | PR 1 | kafka-topics --list y ss -tlnp | console-producer/consumer JSON | server.properties y ~/kafka-logs |

## Phase 1: Infraestructura persistente

- [x] 1.1 Crear ~/kafka-logs en la VM y verificar espacio en disco
- [x] 1.2 Actualizar log.dirs y advertised.listeners en server.properties

## Phase 2: Broker y topic

- [x] 2.1 Formatear storage KRaft y arrancar broker con -daemon
- [x] 2.2 Esperar 9094 abierto y crear topic anuncios_inmobiliarios (3 particiones)

## Phase 3: Smoke test

- [x] 3.1 Enviar JSON con kafka-console-producer
- [x] 3.2 Leer con kafka-console-consumer y verificar el mensaje

## Phase 4: Documentacion y verificacion

- [x] 4.1 Escribir docs/kafka_vm.md comando por comando con salidas
- [x] 4.2 Verificar desde Windows TCP 9094 y desde VM ss -tlnp
