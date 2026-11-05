# Proposal: bloque-2-integracion-hdfs-kafka

## Intent

HDFS-01, KAFKA-01 e INTEGRACION-01 quedan hoy en SHOULD para la evidencia en
vivo: el procesado solo está en local, Kafka Python solo está probado
offline y el flujo HDFS→Kafka→MongoDB no está encadenado. Sin esa evidencia
no se acredita el 10 de BDA-RA1.

## Scope

### In Scope

- 5. HDFS: entrypoint de subida con `--dry-run` que lista lo que subiría,
  procesado listo en local con SHA firmado y lista de ficheros; originales
  subidos a HDFS y recuperación con tamaño igual.
- 6. Kafka Python en vivo contra 9094: productor y consumidor que procesan
  los 759 anuncios, con upsert sin duplicar y reporte de procesados.
- 7. Gate extremo a extremo: sube raw a HDFS, publica 10 anuncios de prueba
  a Kafka, consume a Mongo con upsert y verifica `codigo_ine` en MongoDB.

### Out of Scope

- Subir el procesado a HDFS (solo dry-run listo en local hasta confirmación
  de la profesora).
- Cron, console-producer/consumer como vía productiva.
- Bloques 3 y 4 del plan (índices, modelado, conclusiones).

## Capabilities

### New Capabilities

- None. No se crea una capacidad nueva.

### Modified Capabilities

- almacenamiento-y-streaming: HDFS-01, KAFKA-01 e INTEGRACION-01 elevan su
  evidencia en vivo de SHOULD a SHALL con datos reales (dry-run HDFS, 759 en
  Kafka Python, gate con 10 de prueba hacia MongoDB).

## Approach

Comandos en VM y clúster centro con trazabilidad total en
`docs/trazabilidad_vm.md`: dry-run y LISTSTATUS WebHDFS con SHA, productor y
consumidor Python sobre el broker real con conteo de enviados/procesados y
offsets, y pipeline de gate que encadena HDFS→Kafka→MongoDB con campo común
`codigo_ine`.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| HDFS centro `/user/iabd-user15/bigdata_reto/vivienda_euskadi/data` | Modified | Originales subidos; procesado solo en dry-run |
| Topic `anuncios_inmobiliarios` (VM 192.168.201.162:9094) | Modified | 759 anuncios por productor Python |
| MongoDB localhost:27017 | Modified | Upsert de anuncios, verificado por `codigo_ine` |
| `docs/trazabilidad_vm.md` | Modified | Entrada por comando (fecha, objetivo, máquina, comando, salida, conclusión) |
| `openspec/changes/bloque-2-integracion-hdfs-kafka/*` | New | Proposal y spec delta de este cambio |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Upsert duplica o pierde anuncios si la clave no es estable | Med | Upsert por clave estable; verificar conteo 759 antes y después |
| Kafka→Mongo se rompe si el consumidor cae o Mongo está detenido | Med | Registrar el error, aislar la caída, consumidor reintentable |
| WebHDFS falla por certificado/TLS o proxy del clúster centro | Med | Dry-run y LISTSTATUS 200 antes de subir; traza en `trazabilidad_vm.md` |

## Rollback Plan

Detener productor/consumidor, no subir procesado, revertir upserts del gate
con 10 de prueba en MongoDB y dejar HDFS solo con originales. No hay commit
que revertir en esta fase (proposal).

## Dependencies

- HDFS centro http://10.22.87.215:50070, usuario iabd-user15.
- Kafka VM 192.168.201.162:9094, topic `anuncios_inmobiliarios`, 3 particiones.
- MongoDB localhost:27017: 252 municipios, 759 anuncios.
- Plan `plan/PLAN_10.md`, bloque 2 (pasos 5, 6 y 7).

## Success Criteria

- [x] Dry-run HDFS lista procesado listo en local con SHA; originales
  recuperables con tamaño igual.
- [x] Kafka Python: 759 enviados y 759 procesados, offsets mínimos 759.
- [x] Gate: 10 de prueba consultables en MongoDB por `codigo_ine`;
  anuncios totales al menos 759.
