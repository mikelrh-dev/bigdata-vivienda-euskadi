# Design: kafka-vm-broker

## Technical Approach

Arrancar el binario Kafka 4.3.1 ya instalado en ~/kafka sin reinstalar nada.
El formateo KRaft es necesario porque no existe ningun log.dirs previo
(/tmp/kraft-combined-logs no existe tras reboot). Tras arrancar, crear el topic
y probar con las herramientas console que vienen en bin/.

## Architecture Decisions

| Decision | Options | Tradeoff |
|----------|---------|----------|
| log.dirs | ~/kafka-logs (elegido) vs /tmp/kraft-combined-logs | /tmp se pierde en reboot; ~/kafka-logs sobrevive y cumple la ficha persistente |
| Advertised PLAINTEXT | 192.168.201.162:9094 (elegido) vs localhost:9094 | localhost solo llega dentro de la VM; la IP llega desde Windows y tambien desde la VM |
| CONTROLLER advertised | localhost:9093 (elegido) | El controller es intra-VM; anunciarlo en localhost es correcto en KRaft combined |
| Arranque | kafka-server-start.sh -daemon (elegido) vs service/systemd | No hay unidad systemd; -daemon es lo pedido y deja el broker en segundo plano |

## Data Flow

    Windows (cliente) --TCP 192.168.201.162:9094--> Broker KRaft (VM)
    VM console-producer --JSON--> Topic anuncios_inmobiliarios
    Topic --> console-consumer (from-beginning) --> stdout

## File Changes

| File | Action | Description |
|------|--------|-------------|
| ~/kafka/config/server.properties (VM) | Modify | log.dirs y advertised.listeners |
| ~/kafka-logs (VM) | Create | Directorio de datos KRaft |
| docs/kafka_vm.md (repo) | Create | Ficha comando por comando |
| openspec/changes/kafka-vm-broker/* | Create | Proposal, spec, design, tasks, verify |

## Interfaces / Contracts

- Bootstrap Windows: 192.168.201.162:9094 (PLAINTEXT, sin SASL ni SSL)
- Controller: localhost:9093 (solo VM)
- Topic: anuncios_inmobiliarios, 3 particiones, factor de replica 1
- Mensaje de smoke: JSON con precio y municipio, sin clave ni esquema

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Infra | 9094 en escucha, topic con 3 particiones | ss -tlnp y kafka-topics --describe |
| Smoke | JSON entra y sale por console | console-producer + console-consumer |
| Reachability | Windows conecta a 9094 | TCP desde el host + kafka-topics --list |

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file
classification, or process-integration boundary.

## Migration / Rollout

No migration required. Si el broker ya tenia meta.properties, el comando
format con --ignore-formatted lo conserva; si no, se genera un cluster.id
nuevo porque no hay datos previos.

## Open Questions

- None. El Python productor/consumidor queda para otro cambio.
