# Proposal: integracion-indicadores-10

## Intent

Cerrar los dos criterios que quedan en 7/10 tras la auditoría 2026-11-06 sin subir procesado a HDFS (decisión solo-raw vigente de 2026-11-05): INTEGRACION-01 (flujo completo en vivo sin gate logueado) e INDICADORES-01 (4 indicadores distintos + 1 legacy contado como 5º). Cualquier comando o salida ejecutada en la VM (192.168.201.162) o local contra Mongo/Kafka/HDFS se recopila en `docs/trazabilidad_vm.md` con formato Fecha/Objetivo/Máquina/Comando/Salida/Conclusión.

## Scope

### In Scope
- INTEGRACION-01: ejecutar en vivo `scripts/gate_bloque2.py` (producción 10, consumo grupo `anuncios`, verificación por `codigo_ine` en Mongo) y loguear salida completa en `docs/trazabilidad_vm.md`. Elevar SHOULD a SHALL solo si el gate da `GATE PASS`.
- INDICADORES-01: declarar 5 indicadores distintos de 2+ fuentes sin contar el legacy 16-29 (promover VPO terminadas ‰ como 5º, desde `vpo_municipal` + población de `dim_municipios`), regenerar huellas y `data/resultados` si el conteo cambia, test de conteo 5 no-legacy.
- Transversal: corregir `README.md:159` (G auto desde Mongo, 5 CSV no 4) si el cambio lo deja stale; documentar `min.insync.replicas=2` vs RF=1 como limitación si sigue.

### Out of Scope
- Subida de `data/procesado` (silver) a HDFS. Se mantiene solo-raw (188 ficheros, 228M, regenerable). HDFS-01 queda en SHALL para originales + SHOULD procesados.
- Novos extractores, nuevos pipelines que cambien cifras canónicas, `git push` sin orden explícita.

## Capabilities

### Modified Capabilities
- `almacenamiento-y-streaming`: INTEGRACION-01 y KAFKA-01 (vivo acreditado con gate).
- `presentacion-de-resultados`: INDICADORES-01 (5 distintos non-legacy), PREPARACION-VISUALIZACION-01 (huellas regeneradas).

## Approach

1. Propose/Spec/Design/Tasks (este change).
2. Ejecutar gate en vivo, capturar salida a `docs/trazabilidad_vm.md`.
3. Servir de repo-patrón para indicador: VPO ‰ ya existe como colección/pipeline; solo falta declararlo como indicador y auditar conteo/huella.
4. Verificar con `pytest` suite completa + `verificar_fase_datos.py`.
5. Archivar.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `openspec/changes/2026-11-06-integracion-indicadores-10/` | New | propuesta, deltas, diseño, tasks, verify-report |
| `openspec/specs/almacenamiento-y-streaming/spec.md` | Modified | INTEGRACION-01 SHALL si gate PASS + KAFKA-01 SHOULD>SHALL vivo |
| `openspec/specs/presentacion-de-resultados/spec.md` | Modified | INDICADORES-01 5 distintos non-legacy |
| `docs/trazabilidad_vm.md` | Modified | entradas Bloque 2 con Fecha/Objetivo/Máquina/Comando/Salida/Conclusión |
| `docs/matriz_indicadores.md`, `data/resultados/*` | Modified | conteo 5, huellas regeneradas |
| `tests/` | Modified | test conteo 5 indicadores y gate (sin destructivos) |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Gate produce 10 y altera conteos (759>769) | Med | test que gate usa upsert por `portal:id_anuncio`; total>=759 ya exigido; documentar offsets en trazabilidad |
| Promover VPO cuenta como indicador si falta etapa | Low | verificar pipeline `vpo_municipal` con `$group/$lookup/$unwind` ya existe; test cuenta fuentes |
| Huella esfuerzo cambia | Low | regenerar huella real desde Mongo y documentar; no teclear |

## Rollback Plan

Revertir commits de este change. Mongo/Kafka son upserts idempotentes; el gate produce mensajes, no borra. La trazabilidad solo añade entradas, no reescribe pasadas.

## Dependencies

- VM 192.168.201.162 broker 4.3.1 KRaft vivo (pid 1817 a 2026-11-06 14:12).
- Mongo `localhost:27017/vivienda_euskadi` (252/759).
- `.venv/Scripts/python.exe -m pytest tests -q`.

## Success Criteria

- [ ] Gate e2e `GATE PASS` con salida completa en `docs/trazabilidad_vm.md`.
- [ ] INDICADORES-01 con 5 indicadores distintos non-legacy, verificables en `docs/matriz_indicadores.md` y test.
- [ ] `pytest tests -q` verde y `verificar_fase_datos.py` exit 0.
- [ ] HDFS procesado explícitamente fuera de alcance (sin subir silver).
