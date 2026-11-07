# Verification Report: kafka-vm-broker

**Fecha:** 2026-11-04
**Comandos de verificacion:**
- En VM (SSH mikel@192.168.201.162): ss -tlnp, ps aux | grep kafka,
  kafka-topics --list, kafka-topics --describe, console-producer/consumer
- Desde Windows: TCP 192.168.201.162:9094 + curl telnet
- Repo: .venv/Scripts/python.exe -m pytest tests -q

**Resultado de infraestructura:** PASS. Broker java pid 4464 en *:9094 y
*:9093; topic anuncios_inmobiliarios con 3 particiones; JSON de smoke
leido (Processed a total of 1 messages).
**Resultado repo:** 123 passed, 1 failed en 7.66s. El unico fallo es
tests/test_contrato.py::test_p08_contrato_cubre_los_criterios (criterio
"Operaciones PyMongo" sin transcribir). Es preexistente y ajeno a este cambio:
git diff sobre openspec/specs/contrato-reto/spec.md y tests/test_contrato.py
esta vacio y este cambio no toca storage ni .env.

## Cumplimiento de specs

| Spec | Estado | Evidencia |
|---|---|---|
| KAFKA-INFRA-01: broker persistente en marcha | PASS | server.properties log.dirs=/home/mikel/kafka-logs; ~/kafka-logs con meta.properties, anuncia 3 particiones en disco; ss -tlnp muestra 9094 |
| KAFKA-INFRA-01: advertised alcanzable desde Windows | PASS | advertised PLAINTEXT://192.168.201.162:9094; kafka-topics --list con bootstrap 192.168.201.162:9094 devuelve anuncios_inmobiliarios; TCP desde Windows OPEN; curl establece conexion a 9094 |
| KAFKA-INFRA-01: topic y smoke JSON | PASS | kafka-topics --describe PartitionCount 3; producer envio {"precio": 850, "municipio": "Bilbao"}; consumer from-beginning lo leyo; sin tocar MongoDB |

## Reauditoria antes y despues

| Metrica | Antes | Despues | Veredicto |
|---|---|---|---|
| Proceso broker | apagado, sin escucha | java pid 4464 en 9093 y 9094 | Mejorado |
| log.dirs | /tmp/kraft-combined-logs (no existe) | /home/mikel/kafka-logs (existe, con datos) | Mejorado |
| advertised.listeners | localhost:9094 | 192.168.201.162:9094 | Mejorado |
| Topics | 0 (anuncios ausente) | anuncios_inmobiliarios, 3 particiones | Mejorado |
| Mensajes | 0 | 1 JSON de smoke leido por console | Mejorado |
| storage/, .env, HDFS, Mongo | sin tocar | sin tocar | Sin regresion |

Sin ficheros de datos modificados: las metricas de data-audit sobre
data/raw y data/procesado no aplican por cambio de infraestructura.

## Tareas

Las 8 tareas de tasks.md estan completas y marcadas [x]. Ficheros: en la VM
~/kafka/config/server.properties (dos lineas), ~/kafka-logs (nuevo), en el
repo docs/kafka_vm.md y openspec/changes/kafka-vm-broker/ (proposal, design,
specs, tasks, verify-report). No se hizo commit.

## Issues

- CRITICAL: ninguno para este cambio. La infraestructura queda arrancada y
  el smoke pasa en vivo.
- WARNING: pytest tiene 1 fallo preexistente en test_contrato.py P-08 ajeno
  a kafka-vm-broker (deriva entre test y spec de contrato). No bloquea este
  cambio pero impide un gate verde completo del repo.
- Nota: el ERROR TimeoutException de console-consumer es la terminacion
  normal al pedir 2 mensajes habiendo 1. El Python productor/consumidor de
  KAFKA-01 nivel 10 sigue fuera de alcance y declarado en la proposal.

## Veredicto

PASS WITH WARNINGS. La infraestructura Kafka pedida funciona con salidas
reales; queda el warning del fallo preexistente de test_contrato.py para
otro cambio. Sin archive: no se fusionan deltas ni se commitea.
