# Verify report: hdfs-windows-vm-kafka

Fecha: 2026-11-06
Change: 2026-11-06-hdfs-windows-vm-kafka (solo raw, sin silver, sin Mongo en flujo)

## Evidencia
- venv --user en VM: pip 26.3, hdfs 2.7.3, kafka-python 2.2.3 (sin sudo).
- Bytes: scp 532K subset + 861M full a ~/staging/raw (356 ficheros).
- Kafka: 10 (offsets 0-3) + 352 (115-123) = 362 manifests, LAG 0 grupo hdfs_vm (124/121/117).
- VM put: 10/10 y 352/352 sin FAIL, LIST 201 top-level, alquiler_municipal.json 154205 SHA 6f5af1b3... (local==remoto).
- pytest: 134 passed.
- docs/movimientos_hdfs_windows_vm.md y docs/trazabilidad_vm.md actualizados.

## Veredicto
GATE PASS Windows>Kafka>VM>Hadoop con solo raw. Modos: Kafka lleva manifiesto, scp lleva bytes.
