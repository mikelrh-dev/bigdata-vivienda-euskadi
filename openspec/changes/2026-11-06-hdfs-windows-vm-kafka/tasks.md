# Tasks: hdfs-windows-vm-kafka

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 150-250 |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | 1 change, 3 unidades (VM env / flujo raw / verificación) |
| Delivery strategy | commit-per-unit |

### Suggested Work Units

| Unit | Goal | Focused test command | Runtime harness | Rollback boundary |
|------|------|----------------------|-----------------|-------------------|
| 1 | VM venv + hdfs==2.7.3 + staging | `ssh ... "python3 --version && ~/.venv/bin/python -c 'import hdfs; print(hdfs.__version__)'"` | `~/kafka/bin/kafka-topics.sh --list` | Borrar `~/.venv` y `~/staging` |
| 2 | Flujo raw Windows>Kafka>VM>Hadoop | `pytest tests/test_hdfs.py -q` | `python scripts/gate_hdfs_vm.py` + SHA | Vaciar `/data/raw` en HDFS (childrenNum=0) |
| 3 | Trazabilidad y cierre | `pytest tests -q` | `docs/trazabilidad_vm.md` + `.md` movimientos | Revertir commits del change |

## Phase 1: Preparación VM

- [x] 1.1 `proposal.md` y delta `specs/almacenamiento-y-streaming` commiteados (ead0946).
- [x] 1.2 `design.md` con Mermaid y decisiones (manifiesto por Kafka, bytes por scp).
- [x] 1.3 Instalar venv en la VM (`python3 -m venv ~/.venv` + `pip install hdfs==2.7.3 requests python-dotenv`), verificar `import hdfs`.

## Phase 2: Productor y consumidor (solo raw)

- [x] 2.1 Restaurar `storage/kafka_producer.py` (anuncios) desde `archive/kafka_2026-11-06/` y crear `storage/kafka_raw_producer.py` (manifiesto {rel,size,sha} de `data/raw` sin legacy).
- [x] 2.2 Crear `storage/kafka_hdfs_uploader.py` (consumidor VM grupo `hdfs_vm`: lee manifiesto, hace `upload_raw_excluding_legacy` desde `~/staging/raw` y verifica `read_file_sha256`).
- [x] 2.3 Copiar `storage/` + `.env` centro + estado a la VM y `scp -r data/raw/ mikel@VM:/staging/raw/` (solo raw, no silver).

## Phase 3: Gate y cierre

- [x] 3.1 Ejecutar subset 10 (producción Windows con límite, consumo VM, put a HDFS y verificación SHA), luego full 352 si PASS.
- [x] 3.2 Recopilar toda salida VM en `docs/trazabilidad_vm.md` (Fecha/Objetivo/Máquina=VM/Comando/Salida/Conclusión) y en `docs/movimientos_hdfs_windows_vm.md` (bitácora + explicaciones).
- [x] 3.3 `pytest tests -q` verde y `verify-report.md` con evidencia literal.
- [ ] 3.4 Archivar el change y fusionar specs desplegados.
