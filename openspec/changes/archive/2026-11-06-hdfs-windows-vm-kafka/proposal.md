# Proposal: hdfs-windows-vm-kafka

## Intent

Cambiar el flujo HDFS de "Windows directo a Hadoop" a "Windows > Kafka > VM > Hadoop" según la indicación de la profesora, manteniendo el resto (Mongo solo en local Windows, raw sin verificado -> web scraping, procesado NO se sube). Kafka participa como transporte entre Windows y VM; la VM hace el put a HDFS.

## Scope

### In Scope
- Flujo: Windows publica `data/raw/` por Kafka (`192.168.201.162:9094`, topic `anuncios_inmobiliarios`) y consumidor Python en la VM hace el put WebHDFS a `10.22.87.215:50070` con `upload_raw_excluding_legacy` (SHA + estado resumible).
- HDFS solo raw (sin procesado). Mongo solo local Windows (sin evolución). Kafka broker solo en la VM (KRaft 4.3.1, 9093/9094).
- Trazabilidad completa en `docs/trazabilidad_vm.md`: Fecha/Objetivo/Máquina=VM/Comando/Salida/Conclusión con offsets y LISTSTATUS.

### Out of Scope
- Subida de silver (`data/procesado`) a HDFS.
- Cambio de Mongo a VM/HDFS. Instalación Hadoop en la VM. `git push` sin orden explícita.

## Capabilities

### Modified Capabilities
- `almacenamiento-y-streaming`: HDFS-01 (flujo Windows>Kafka>VM>Hadoop), KAFKA-01 (broker VM, productor W, consumidor VM sube a HDFS), INTEGRACION-01 (flujo completo raw>VM>HDFS, no raw directo Windows>HDFS).
- `mongodb-y-analisis`: sin cambios (Mongo local only).

## Approach

1. Regenerar productor Windows y consumidor VM (desde `archive/kafka_2026-11-06/`).
2. En la VM: venv + `hdfs==2.7.3`, copia mínima `storage/hdfs_utils.py`, `.env` centro, estado.
3. Windows > Kafka > VM > HDFS: produce vía Kafka, consume en VM y put a `/user/iabd-user15/.../data/raw/`.
4. Verificar SHA byte-idéntico y offsets/LAG 0, log en trazabilidad.
5. Archivar lo anterior (gate 2026-11-06) como histórico.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `openspec/specs/almacenamiento-y-streaming/spec.md` | Modified | HDFS-01 flujo nuevo, KAFKA-01/INTEGRACION-01 |
| `storage/hdfs_utils.py` | Modified | Correr desde la VM (mismo centro) |
| `archive/kafka_2026-11-06/` | Modified | Base para regenerar (producer/consumer Windows>VM) |
| `docs/trazabilidad_vm.md` | Modified | Entradas con Máquina=VM |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| VM sin venv/pip/hdfs: 861 MB no subibles | High | Instalar venv antes de producir |
| Kafka topics con duplicados old (offsets 287/301/272 borrado) | Med | Topic nuevo o consumer group nuevo |
| SHA cambia si cambia binario | Low | Reuse `upload_raw_excluding_legacy` + `read_file_sha256` |

## Rollback Plan

Revertir commits del change; HDFS raw ya está vacío (childrenNum=0) y se puede re-subir desde Windows con el código actual.

## Dependencies

- VM con venv + hdfs==2.7.3, Kafka 4.3.1 KRaft (pid 1817), 861M raw.
- HDFS centro `10.22.87.215:50070` accesible desde la VM (HTTP 200 en 14 ms verificado).

## Success Criteria

- [ ] Flujo Windows>Kafka>VM>Hadoop documentado en spec y trazabilidad.
- [ ] VM sube raw a HDFS con SHA y estado resumible, LISTSTATUS 200 hijos y SHA igual a local.
- [ ] Lag 0 y offsets logueados.
- [ ] HDFS raw vacío no se toca salvo re-subida por este flujo.
