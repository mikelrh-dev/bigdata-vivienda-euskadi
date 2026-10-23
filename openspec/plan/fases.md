# Plan de implementación por fases

**Estado:** Planificado, no iniciado (salvo Fase 0 ya ejecutada)
**Fecha:** 2026-10-23
**Contrato:** [`../specs/contrato-reto/spec.md`](../specs/contrato-reto/spec.md) — la verdad
**Contexto:** [`../project.md`](../project.md) · Análisis amplio: [`../../plan/PLAN.md`](../../plan/PLAN.md)

---

## Purpose

Ordenar la implementación del contrato en fases autorizables. Cada fase es
una unidad independiente con entregable, requisitos del contrato que cierra
y riesgo declarado. Ninguna fase requiere haber ejecutado la anterior salvo
indicación expresa.

---

## Estado

| Fase | Entrega principal | Requisitos del contrato | Riesgo | Depende | Estado |
|---|---|---|---|---|---|
| 0 | Extracción + contrato + tests | EXTRACCION, FORMATO, PYTHON, COMPLEMENTARIOS (parcial) | bajo | — | ✅ Hecha |
| 1 | Script de salarios | COMPLEMENTARIOS-01, P-02 | bajo | — | ⬜ |
| 2 | docker-compose HDFS + MongoDB | habilita 8 requisitos | **medio** | — | ⬜ |
| 3 | Subida a HDFS + recuperación | HDFS-01 | bajo | 2 | ⬜ |
| 4 | Modelado + operaciones PyMongo | MODELO-01, PYMONGO-01 | bajo-medio | 2 | ⬜ |
| 5 | Limpieza y transformación | LIMPIEZA-01, TRANSFORM-01 | bajo | 4 | ⬜ |
| 6 | Aggregation Pipeline + indicadores | AGREGACION-01, CONSULTAS-01 | bajo-medio | 5 | ⬜ |
| 7 | Kafka (productor y consumidor) | KAFKA-01, INTEGRACION-01 | **medio-alto** | 4 + VM | ⬜ |
| 8 | Gráficos desde PyMongo | GRAFICOS-01, DATOS-PYMONGO-01, PRESENTACION-01 | bajo | 6 | ⬜ |
| 9 | Informe, arquitectura y demo | INTERPRETACION-01, CONCLUSION-01 | bajo | 6, 8 | ⬜ |

---

## Fase 0 — Extracción, contrato y verificación ✅

**Hecha.** Scripts `01`–`06` en `extract/`, 127 MB en `data/raw/`, contrato
OpenSpec creado y 11 tests en verde con 1 pendiente (salarios).

---

## Fase 1 — Salarios (cerrar el hueco de datos)

- **Objetivo:** cerrar el único criterio abierto del contrato.
- **Entrega:** `extract/07_ine_salarios.py` +
  `data/raw/ine_salarios_edad.json` + suite en verde.
- **Cierra:** `COMPLEMENTARIOS-01`, prohibición `P-02`.
- **Decisión abierta:** el salario del INE es nacional. ¿Se usa como
  referencia de España y se apoya en la renta por edad de Eustat (C.A.), o
  solo EPA?
- **Riesgo:** bajo. Misma API que `06_ine_api.py`.
- **Depende:** nada.

---

## Fase 2 — Infraestructura: Docker Compose (HDFS + MongoDB)

- **Objetivo:** levantar HDFS (NameNode + DataNode) y MongoDB en Docker.
- **Entrega:** `docker-compose.yml` + ambos servicios corriendo y conectados.
- **Habilita:** `HDFS-01`, `MODELO-01`, `PYMONGO-01`, `CONSULTAS-01`,
  `AGREGACION-01`, `LIMPIEZA-01`, `TRANSFORM-01`, `INTEGRACION-01`.
- **Riesgo:** medio. HDFS en Windows es lo más delicado.
- **Plan B si falla:** WSL2 o contenedor único namenode+datanode.
- **Opcional recomendado:** incluir Kafka en el mismo compose como
  entorno de pruebas local, para validar el productor/consumidor antes de
  tocar la VM.
- **Depende:** nada (Docker Desktop ya arranca).

---

## Fase 3 — HDFS: subida y recuperación

- **Objetivo:** subir originales y procesados, y demostrar que se recuperan.
- **Entrega:** `storage/hdfs_utils.py` + `/raw/` y `/procesado/` poblados +
  demostración de recuperación (bytes idénticos).
- **Cierra:** `HDFS-01` al nivel de 10 puntos.
- **Depende:** Fase 2.

---

## Fase 4 — MongoDB: modelado y operaciones PyMongo

- **Objetivo:** diseñar las colecciones, justificarlas y cargar los datos.
- **Entrega:** `storage/mongo_crud.py` + BD creada + insert/update/delete
  automatizados y comprobados.
- **Cierra:** `MODELO-01` (justifica modelo y relaciones),
  `PYMONGO-01` (inserta, actualiza, elimina, comprueba).
- **Diseño con Kafka en mente:** usar `upsert` desde el principio para que
  el consumidor reutilice la misma función (exige `KAFKA-01`).
- **Depende:** Fase 2.

---

## Fase 5 — Limpieza y transformación con PyMongo

- **Objetivo:** resolver duplicados, nulos y tipos; cruzar anuncio ↔
  municipio ↔ alquiler ↔ renta.
- **Entrega:** `transform/limpieza.py` + `transform/enrich.py`.
- **Cierra:** `LIMPIEZA-01` (incompletos, duplicados, incorrectos),
  `TRANSFORM-01` (transformaciones en MongoDB).
- **Depende:** Fase 4.

---

## Fase 6 — Aggregation Pipeline e indicadores

- **Objetivo:** encadenar ≥4 etapas y calcular los indicadores clave.
- **Entrega:** `analysis/pipeline_agregaciones.py` +
  `analysis/indicadores.py` + alquiler medio por municipio, % de esfuerzo,
  ranking de accesibilidad.
- **Cierra:** `AGREGACION-01` (≥4 etapas, indicadores complejos),
  `CONSULTAS-01` (campos anidados/arrays).
- **Depende:** Fase 5.

---

## Fase 7 — Kafka (productor y consumidor)

- **Objetivo:** Kafka en la VM + productor/consumidor Python + flujo a
  MongoDB.
- **Entrega:** `storage/kafka_producer.py` + `storage/kafka_consumer.py` +
  topic en la VM + simulación de anuncios nuevos.
- **Cierra:** `KAFKA-01` (productor y consumidor), `INTEGRACION-01` (flujo
  completo hasta MongoDB).
- **Riesgo:** medio-alto. Red Windows↔VM (IP, firewall, NAT).
- **Información necesaria:** características de la VM (¿Docker? ¿Java? ¿IP?
  ¿bridged o NAT? ¿IP fija?).
- **Orden recomendado:** (a) validar en Kafka local de la Fase 2, (b) mover
  a la VM cambiando solo la IP en `.env`. El código no cambia.
- **Depende:** Fase 4 (MongoDB). Independiente de Fases 5–6.

---

## Fase 8 — Visualización

- **Objetivo:** ≥3 tipos de gráfico generados desde consultas PyMongo.
- **Entrega:** `visualization/graficos.py` + gráficos en `data/resultados/`.
- **Cierra:** `GRAFICOS-01` (≥3 tipos adecuados),
  `DATOS-PYMONGO-01` (gráficos desde PyMongo),
  `PRESENTACION-01` (títulos, unidades, leyendas, comparar municipios).
- **Depende:** Fase 6.

---

## Fase 9 — Informe, arquitectura y demo

- **Objetivo:** cerrar los entregables de documentación y la demostración.
- **Entrega:** `plan/arquitectura.md` + `notebooks/informe.ipynb` +
  `docs/informe_resultados.md` + script de demo end-to-end.
- **Cierra:** `INTERPRETACION-01` (relaciona y explica),
  `CONCLUSION-01` (municipios y por qué, con datos).
- **Depende:** Fases 6 y 8.

---

## Criterios de decisión entre fases

1. **Contract-first:** cada fase empieza leyendo
   `openspec/specs/contrato-reto/spec.md`.
2. **Verificable:** una fase no se cierra hasta que su criterio sea
   comprobable (test o ejecución real).
3. **Commit por fase:** cada fase se commitea en git al terminar.
4. **Parar ante fallo:** si una fase falla, se busca plan B antes de seguir.
5. **Kafka no bloquea:** las Fases 1–6 y 8–9 son independientes de Kafka.

## Dependencias de Kafka (resumen)

Solo afectan a la **Fase 7** y al criterio `INTEGRACION-01`. Las Fases 1–6
y 8–9 se pueden ejecutar sin Kafka. Para que añadirlo después no obligue a
rehacer nada, la Fase 4 debe usar **upsert** y los anuncios deben quedar en
JSON publicable (ya lo están).
