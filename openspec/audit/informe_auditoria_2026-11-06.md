# Informe de auditoría completa — bigdata-vivienda-euskadi

**Fecha:** 2026-11-06
**Alcance:** proyecto completo; foco en BDA-RA1 (HDFS, Kafka, Integración) y SBD-RA1 (integración de fuentes, construcción, limpieza, automatización), con RA3 y RA4 verificados.
**Modo:** solo lectura sobre código, `data/raw`, `data/procesado`, HDFS, Kafka y Mongo de producción. Se ejecutó `pytest` (usa `vivienda_euskadi_test`) y `run_all.py --check` (no escribe).
**Skills aplicadas:** `code-review-and-quality`, `security-and-hardening`, `pdf-extraction`, `systemic-issue-triage`.

---

## 1. Veredicto ejecutivo

| Bloque | Nota | Estado |
|---|---|---|
| **BDA RA1** (4 criterios) | **7,75 / 10** | Extracción 10; HDFS 7; Kafka 7; Integración 7 |
| **SBD RA1** (4 criterios, peso 46,7 %) | **10 / 10** | Los 4 criterios en nivel 10 con evidencia |
| **SBD RA3** (6 criterios) | **10 / 10** | Modelado, CRUD, consultas, aggregation, índices y consistencia acreditados |
| **SBD RA4** (5 criterios, peso 40 %) | **10 / 10** | 4 municipios, 5 indicadores, 10 CSV y 13 PNG automáticos |

**Lectura honesta:** el proyecto está muy sólido en datos y MongoDB (SBD completo en 10). El bloque BDA de almacenamiento/streaming **no llega a 10**: HDFS solo tiene originales, Kafka no tiene consumidor desplegado que consuma de verdad, y el flujo no termina en MongoDB. Si se defiende hoy, esos tres criterios se puntúan 7.

**No se modificó nada durante la auditoría.** Después se eliminaron duplicados (`storage/kafka_producer.py` y copias muertas de la VM) y se reorganizó `vm/`; ver §12. El `pytest` ejecutado usó la base de test; producción sigue en 759 anuncios y 252 municipios.

---

## 2. Acceso verificado (en vivo)

| Comprobación | Resultado |
|---|---|
| `ssh -i C:/Users/mikel/.ssh/id_vm_hermes mikel@192.168.201.162` | `SSH_OK`, exit 0 |
| Broker | `LISTEN *:9093` y `*:9094`, java pid 1817 |
| Topic | `anuncios_inmobiliarios`, 3 particiones, RF 1, `min.insync.replicas=2` |
| Grupo `hdfs_vm` | offsets 124/121/117, **LAG 0**, 362 mensajes |
| HDFS WebHDFS | HTTP 200; base = `['raw']` |
| HDFS raw | **352 ficheros**, **895.596.949 bytes** |
| SHA extremo a extremo | 3/3 OK, incluido un CSV de 118.793.174 B |
| Mongo | 27 colecciones, `anuncios` 759, `municipios` 252 |

---

## 3. Evidencia por dimensión

### 3.1 Extracción — 10/10

| Hecho | Medido |
|---|---|
| Scripts con `main()` | 39 de 41 |
| Ficheros con API | 24 |
| Scrapers | Fotocasa y Pisos con `re` + JSON-LD; 0 con BeautifulSoup (no es obligatorio) |
| HTML crudo conservado | 101 ficheros |
| Raw por formato | 126 CSV, 101 HTML, 61 JSON, 49 ZIP, 6 XLSX, 2 GeoJSON |
| Respuesta original API | `eustat_*_raw.json`, `ine_*_raw.json` |
| Manifest raw | 354 líneas para 356 ficheros (352 sin legacy + 4 legacy) |

**Conclusión:** API **y** scraping automatizados, con original y parseado. Nivel 10 acreditado.

### 3.2 HDFS — 7/10

| Hecho | Medido |
|---|---|
| Ficheros locales sin legacy | 352 |
| Ficheros en HDFS | 352 |
| Faltantes / sobrantes | 0 / 0 |
| Tamaños distintos | 0 |
| Bytes local vs HDFS | 895.596.949 == 895.596.949 |
| SHA 3 muestras | `.FROZEN` (0 B), zip GTFS (347.791 B), CSV (118.793.174 B): **3/3 OK** |
| `procesado` en HDFS | **NO existe** (`HdfsError` en `data/procesado` y `/procesado`) |

**Conclusión:** guarda y recupera originales con SHA byte a byte, pero no organiza procesados. El 10 exige originales **y** procesados → **7**.

### 3.3 Kafka — 7/10

| Hecho | Medido |
|---|---|
| Broker | vivo, 4.3.1 KRaft, 9093/9094 |
| Topic | 3 particiones, RF 1 |
| Mensajes | 124 + 121 + 117 = **362** |
| Grupo `hdfs_vm` | LAG 0 |
| Productor | `kafka_raw_producer.py` con `send` + `add_callback`/`add_errback` + `flush` |
| Consumidor | **`kafka_hdfs_uploader.py` no consume Kafka** |
| Consumer en VM | no existe (`ls *consumer*` → no such file) |
| Gate | `scripts/gate_hdfs_vm.py` **no existe** |

El `upload()` real (idéntico en repo y VM):

```python
res = __import__("storage.hdfs_utils", ...).upload_raw_excluding_legacy(
    client=client, raw_dir=staging, hdfs_path=dest,
    state_dir=...,
) if False else {"uploaded": 0, "deduped": 0}
for f in sorted(p for p in staging.rglob("*") if p.is_file()):
    client.write(f"{dest}/{rel}", data=fp.read(), overwrite=True)
```

- No lee el topic, no descarta mensajes sin `type:"raw_manifest"`, no valida `rel`, no comprueba SHA del manifiesto, no aborta por mismatch.
- `is_valid_rel` y `verify_staging` existen pero **no se llaman**.
- El bloque `if False` es código muerto.
- No hay `~/bigdata_hdfs_vm/data/_hdfs_state/` en la VM: el estado resumible no se usó.

**Conclusión:** productor real y grupo consumidor con LAG 0, pero el consumidor desplegado no procesa mensajes. **7**, no 10.

### 3.4 Integración — 7/10

| Hecho | Medido |
|---|---|
| Cadena Windows → Kafka → VM → HDFS | viva y con SHA igual |
| Flujo hasta MongoDB | **no demostrado en la misma cadena** |
| Gate re-ejecutable | **no** (falta consumidor y `gate_hdfs_vm.py`) |
| Mongo local | 27 colecciones, análisis completo |

**Conclusión:** integra componentes (nivel 7), pero no demuestra el flujo completo hasta MongoDB que exige el 10. **7**.

### 3.5 SBD RA1 — 10/10

| Criterio | Evidencia |
|---|---|
| Integración de fuentes | `anuncios.ubicacion.codigo_ine` 759 docs, 83 códigos, **83/83** con match en `municipios._id`; `alquiler_municipal.codigo_ine` 252, **252/252** con match |
| Construcción del conjunto | 27 colecciones, `anuncios.ubicacion` anidado, `equipamiento[]` y `historico_precios[]`, `municipios.demografia` anidado, relaciones por `_id`/`codigo_ine` |
| Limpieza PyMongo | `clean_mongo.py`: `$set`, `$unset`, `update_many`, `delete_many`, `$convert`, contadores `matched/modified/deleted`; nulos, duplicados, tipos y formato |
| Automatización | `run_all.py`: 34 scripts en DAG, `--check` exit 0, `run_manifest.json` 35 entradas, **0 fallos**; `load_all()` + `run_analisis_mongo.py` |

### 3.6 SBD RA3 — 10/10

| Criterio | Evidencia |
|---|---|
| Modelado | `docs/modelo_mongodb.md:148-154` responde literalmente las 7 preguntas y justifica embedding vs referencing |
| CRUD | `insert_many`, `update_one`, `delete_one/many`, `find`; tests comprueban `inserted_id`, `matched_count`, `modified_count`, `deleted_count` |
| Consultas | `analysis/mongo_queries.py`: 30 funciones, 15 tipos de operador (`$gte/$lte/$in/$nin/$and/$or/$exists/$type/$elemMatch/$all/$size/$regex`), dot notation y arrays |
| Aggregation | 9 pipelines; etapas: `$match` 12, `$lookup` 15, `$group` 3, `$unwind` 5, `$sort` 9, `$project` 9, `$addFields` 16, `$limit` 9. Sin `$facet`, pero el 10 acepta `$lookup` **o** `$unwind` **o** `$facet` |
| Índices | `test_mongo_indices.py` pasa en vivo: `COLLSCAN` → `IXSCAN`, `totalDocsExamined` comparado; 5 índices en `anuncios` |
| Consistencia | `marcar_calidad_municipio` con `find_one_and_update` + `ReturnDocument.AFTER`; sonda de transacción en test DB acepta `abort-revertido`/`rechazado-standalone`; prod invariante en 759 |

### 3.7 SBD RA4 — 10/10

| Criterio | Evidencia |
|---|---|
| Datos heterogéneos | CSV, JSON, HTML, ZIP, XLSX, GeoJSON; anidados y arrays adaptados en `load_mongo.py` |
| Automatización del análisis | `analysis/run_analisis_mongo.py` ejecuta consultas, agregaciones, CSV y PNG sin pasos manuales |
| Indicadores | 5 non-legacy: esfuerzo 18-34, tensión social, paro Lanbide, precio m², VPO terminadas; 2+ fuentes |
| Respuesta al reto | 4 municipios comparados (Bilbao 173, Donostia 113, Getxo 40, Vitoria 39) con indicadores calculados en Mongo |
| Preparación visualización | 10 CSV + 13 PNG en `data/resultados/` |

### 3.8 Tema 8 (evaluación separada)

Modelado, CRUD, aggregation, índices, transacciones y PyMongo profesional: **10** con la evidencia anterior. La defensa técnica no es auditable desde el repositorio.

---

## 4. Hallazgos P1 (rompen rúbrica o reproducibilidad)

| ID | Hallazgo | Evidencia | Impacto |
|---|---|---|---|
| **P1-1** | El uploader no consume Kafka: sube todo `~/staging/raw` sin leer el topic | `storage/kafka_hdfs_uploader.py:47-75`; copia VM idéntica | KAFKA-01 no reproducible; el SHALL del delta no se cumple |
| **P1-2** | No hay `procesado` en HDFS | `HdfsError` en `data/procesado` y `/procesado` | HDFS se queda en 7 |
| **P1-3** | El flujo demostrado termina en HDFS, no en MongoDB | delta INTEGRACION-01; el gate sube a HDFS | Integración se queda en 7 |
| **P1-4** | `scripts/gate_hdfs_vm.py` citado en `tasks.md` no existe | `ls` → no such file | Gate no re-ejecutable |
| **P1-5** | No hay consumidor ni `_hdfs_state` en la VM | `ls ~/bigdata_hdfs_vm/*consumer*` y `_hdfs_state` → no such file | Estado resumible no acreditado |

---

## 5. Hallazgos P2 (degradan defensa o fiabilidad)

| ID | Hallazgo | Evidencia |
|---|---|---|
| P2-1 | Topic `RF=1` con `min.insync.replicas=2`: con `acks=all` el productor fallaría | `kafka-topics --describe` |
| P2-2 | `upload()` lee ficheros enteros en memoria (hasta 118 MB) | `kafka_hdfs_uploader.py:66-67` |
| P2-3 | `next(staging.rglob("*"))` sin `is_file()`: puede devolver directorio o `StopIteration` | `kafka_hdfs_uploader.py:69` |
| P2-4 | `municipios` no expone `codigo_ine`; el join usa `_id` | `count_documents({"codigo_ine":...}) = 0`; `_id` 5 dígitos 252/252 |
| P2-5 | Spec desplegado contradictorio: cabecera "PASS" vs texto "gate pendiente"; escenarios viejos que afirman que el consumidor escribe en Mongo | `openspec/specs/almacenamiento-y-streaming/spec.md:4`, `:78-96`, `:100-107` |
| P2-6 | Deriva documental de conteos: 136 tests en README/AGENT/project.md vs **134** reales; 356/352 raw | `pytest --collect-only` = 134 |
| P2-7 | README cita `storage/kafka_consumer.py` y `tests/test_kafka.py`, ambos archivados/inexistentes | `README.md:264`; `ls storage/` |
| P2-8 | `.env.example` no declara `KAFKA_BOOTSTRAP_SERVERS` ni `STAGING_RAW`, usados por el código | `.env.example` vs `storage/*.py` |
| P2-9 | `historico_precios` siempre `[]`; el array existe pero no acumula histórico | `load_mongo.py:287`; muestra Mongo |

---

## 6. Hallazgos P3 (ruido y deuda)

| ID | Hallazgo |
|---|---|
| P3-1 | `brief/.~lock.Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx#` sin ignorar en git |
| P3-2 | 13 colecciones `__backup` en producción |
| P3-3 | IPs internas hardcodeadas como defaults (`10.22.87.215`, `192.168.201.162`) |
| P3-4 | `MONGO_ALLOW_DESTRUCTIVE` solo por convención, sin gate en código |
| P3-5 | `archive/kafka_2026-11-06/` duplica productor, consumidor y gate viejos |
| P3-6 | `informe_final.md` dice 8 pipelines y el resto 9 (heredado, no re-verificado) |
| P3-7 | `G_gaps_limitaciones.png` con cifras tecleadas (heredado, no re-verificado) |

---

## 7. Sobrantes y faltantes

### 7.1 Sobrantes

- Lock de Word en `brief/` (P3-1).
- 13 colecciones `__backup` (P3-2).
- `archive/kafka_2026-11-06/` (P3-5).
- Código muerto en `kafka_hdfs_uploader.py`: bloque `if False`, `res` sin uso, `sample` sin uso, `is_valid_rel`/`verify_staging` sin llamar.
- `.audit_tmp/` generado y borrado durante la auditoría (no queda).

### 7.2 Faltantes

- Consumidor Kafka real en repo y VM (P1-1).
- `scripts/gate_hdfs_vm.py` (P1-4).
- `data/procesado` en HDFS (P1-2).
- `hdfs_upload_raw.json` en la VM (P1-5).
- `KAFKA_BOOTSTRAP_SERVERS` y `STAGING_RAW` en `.env.example` (P2-8).
- Campo `codigo_ine` explícito en `municipios` (P2-4).

---

## 8. Spec desplegado vs delta vs código

| Requisito | Delta | Código/realidad | Veredicto |
|---|---|---|---|
| HDFS-01 originales por Kafka + put VM | SHALL | 352/352, SHA 3/3 | ✅ originales |
| HDFS-01 procesados | SHOULD | ausente | ⚠️ no acredita 10 |
| HDFS-01 estado resumible VM | SHALL | no existe en VM | ❌ |
| KAFKA-01 broker solo VM, productor Windows | SHALL | broker VM, productor Windows | ✅ |
| KAFKA-01 consumidor VM que lee topic | SHALL | no consume | ❌ |
| KAFKA-01 descarte sin `type` y `rel` inválido | SHALL | no implementado en el flujo real | ❌ |
| KAFKA-01 mismatch SHA aborta | SHALL | no implementado en el flujo real | ❌ |
| INTEGRACION-01 flujo vivo con offsets/LISTSTATUS/SHA | SHALL | offsets y SHA sí; log histórico | ⚠️ parcial |
| INTEGRACION-01 GATE PASS con SHA 100 % + LAG 0 + LISTSTATUS | SHALL | LAG 0 y SHA 3/3; no re-ejecutable | ⚠️ |

---

## 9. Plan de reparación (NO ejecutado)

| # | Cambio | Fichero | Esfuerzo | Riesgo | Verificación |
|---|---|---|---|---|---|
| 1 | Consumidor real: `KafkaConsumer(group_id="hdfs_vm")`, filtro `type=="raw_manifest"`, `is_valid_rel`, `verify_staging`, aborto por SHA, `upload_raw_excluding_legacy` con estado | `storage/kafka_hdfs_uploader.py` | 2-3 h | 4/10 | topic de test + 3 casos: válido, sin type, SHA alterado |
| 2 | Gate reproducible con offsets, LISTSTATUS y SHA | `scripts/gate_hdfs_vm.py` | 1-2 h | 3/10 | ejecutar en vivo y comparar salida |
| 3 | Subir `data/procesado` a `/data/procesado` con SHA (si la profesora lo autoriza) | `scripts/upload_procesado.py` | 1 h | 5/10 | `LISTSTATUS` + SHA 3 muestras |
| 4 | Demostrar flujo hasta Mongo o firmar la excepción por escrito | `scripts/gate_*.py`, spec | 2-4 h | 6/10 | un dato de punta a punta consultable en Mongo |
| 5 | Corregir topic: `min.insync.replicas=1` o RF=3 | VM | 15 min | 2/10 | `kafka-configs --describe` |
| 6 | Añadir `codigo_ine` a `municipios` (espejo de `_id`) | `load_mongo.py` | 30 min | 2/10 | `count_documents({"codigo_ine":...})=252` |
| 7 | Actualizar conteos 136→134 y README de Kafka | README, AGENT, project.md, specs | 30 min | 1/10 | grep sin 136/`kafka_consumer` |
| 8 | `.gitignore` para `brief/.~lock.*` | `.gitignore` | 5 min | 1/10 | `git status` limpio |
| 9 | Declarar `KAFKA_BOOTSTRAP_SERVERS` y `STAGING_RAW` | `.env.example` | 5 min | 1/10 | comparación con `os.getenv` |

---

## 10. Limitaciones de esta auditoría

- No se probó el consumidor contra un topic de test (no se escribió en Kafka). La conclusión se basa en lectura del código y en la ausencia del consumidor en la VM.
- Los logs históricos de `docs/trazabilidad_vm.md` no se re-ejecutaron; se verificó el estado vivo actual.
- La defensa técnica del Tema 8 no es auditable desde el repositorio.
- Los hallazgos P3-6 y P3-7 vienen de la auditoría previa y no se re-verificaron en esta sesión.
- `pytest` se ejecutó (134 passed, 6,74 s) y usó `vivienda_euskadi_test`; producción quedó invariante (759/252).

---

## 11. Conclusión

- **SBD (RA1, RA3, RA4): 10/10** con evidencia reproducible.
- **BDA RA1: 7,75/10** — extracción 10, HDFS 7, Kafka 7, integración 7.
- El proyecto es defendible y completo en datos y MongoDB; el punto débil es el tramo Kafka→HDFS y el cierre hasta Mongo.
- Con los cambios 1, 2 y 3 del plan, HDFS y Kafka pueden subir a 10; Integración sube al cerrar el gate re-ejecutable y acoplar consumidor→put. **No se exige MongoDB como sink del flujo Kafka** (aclaración de la profesora, 2026-11-06).

---

## Addendum 2026-11-06 — aclaración de la profesora

1. **Mongo no es sink del flujo Kafka.** Se anula el hallazgo P1-3 en su forma original. INTEGRACION-01 se reevalúa contra Windows>Kafka>VM>HDFS.
2. **Sí existe consumidor vivo en la VM**, pero es efímero: pid 11710, heredoc `bash -c`, grupo `hdfs_vm`, `enable_auto_commit=False`; cuenta manifiestos `type=raw_manifest` y hace commit por mensaje. No está versionado y no ejecuta el put. P1-1 se redefine: consumidor efímero y desacoplado, no ausencia.
3. **HDFS sigue en 7.** Rúbrica PDF línea 77: «Organiza originales y procesados y demuestra su recuperación». `/data` solo tiene `raw`; `data/procesado` 188 ficheros (238.409.894 B), `manifest_sha256.txt` 185 líneas → 3 `SIN_MANIFEST`; `scripts/upload_procesado.py` rechaza subir sin confirmación (exit 2).
4. **Integración sigue en 7** hasta que el gate sea re-ejecutable y el consumidor ejecute el put; no por Mongo.
5. Resto sin cambios: Extracción 10; SBD-RA1, RA3 y RA4 10.

---

## 12. Reauditoría 2026-11-06 (post-limpieza)

**Cuándo:** 2026-11-06, tras eliminar `storage/kafka_producer.py` y las copias muertas de la VM, y reorganizar `vm/` en `ubuntu/` y `windows/`.
**Modo:** solo lectura sobre HDFS, Kafka y Mongo; `pytest` usó `vivienda_euskadi_test`; `upload_procesado.py --dry-run` no escribe.

### 12.1 Cambios desde la auditoría inicial

| Cambio | Evidencia |
|---|---|
| `storage/kafka_producer.py` eliminado (duplicado exacto del archivado) | `git diff --stat` → 144 deletions; sin imports vivos (`grep` → `NONE`) |
| VM pasa de 5 `.py` a 3 | `ls ~/bigdata_hdfs_vm` → `hdfs_utils.py`, `hdfs_verify.py`, `kafka_hdfs_uploader.py` |
| `vm/` reorganizado por máquina | `vm/ubuntu/` 6 docs; `vm/windows/` 1 doc; `vm/README.md` en la raíz; 13 enlaces, 0 rotos |

### 12.2 Evidencia viva

| Comprobación | Resultado |
|---|---|
| `pytest tests -q` | **134 passed**, 6,72 s, exit 0 |
| `transform/run_all.py --check` | 34 scripts, 0 fallos, exit 0 |
| `data/raw` | 356 ficheros (352 sin legacy) |
| `data/procesado` | 188 ficheros; manifest 185 líneas → **3 `SIN_MANIFEST`** |
| `upload_procesado.py --dry-run` | 188 ficheros, 238.409.894 B, 185 OK, 3 sin manifiesto, `CERO_ESCRITURAS`, exit 0 |
| `docs/raw_manifest_sha256.txt` | 354 líneas |
| VM `~/staging/raw` | 356 ficheros |
| VM `_hdfs_state` | **no existe** |
| Consumidor | vivo: bash pid 11710, `python3 -` pid 11711, grupo `hdfs_vm` |
| Kafka topic | 3 particiones, RF 1, `min.insync.replicas=2` |
| Grupo `hdfs_vm` | 124/121/117, **LAG 0** |
| HDFS `data` | `['raw']`; `procesado` → `HdfsError` |
| HDFS raw | **352 ficheros, 895.596.949 B**; 201 hijos top-level |
| Mongo | 27 colecciones; 759 anuncios, 252 municipios, 252 alquiler |
| Join anuncios | 83/83 (`ubicacion.codigo_ine` ↔ `municipios._id`) |
| Join alquiler | 252/252 (`codigo_ine` ↔ `municipios._id`) |
| `municipios.codigo_ine` | 0 documentos con el campo |
| `scripts/gate_hdfs_vm.py` | **no existe** |
| `storage/kafka_consumer.py` | **no existe** |
| Colecciones `__backup` | 13 |

### 12.3 Veredicto (sin cambios)

**BDA RA1: 7,75/10** — Extracción 10, HDFS 7, Kafka 7, Integración 7. **SBD RA1/RA3/RA4: 10/10**.

- **P1-1 se mantiene:** `kafka_hdfs_uploader.py` no consume Kafka; sube los 356 de staging (incluidos 4 legacy) si se ejecuta.
- **P1-2 se mantiene:** `procesado` no existe en HDFS; el `--dry-run` confirma 188 ficheros y 3 sin manifiesto.
- **P1-3 anulado** por la aclaración de la profesora: Mongo no es sink del flujo Kafka.
- **P1-4 se mantiene:** `scripts/gate_hdfs_vm.py` no existe.
- **P1-5 se redefine:** el consumidor existe, pero es un heredoc efímero (pid 11711), no versionado, y no ejecuta el put; `_hdfs_state` sigue ausente.

### 12.4 Deuda documental que sigue abierta

- `README.md:108,143,253` y `AGENT.md:9` dicen **136 tests**; el conteo real es **134**.
- `README.md:264` cita `storage/kafka_producer.py` (ya eliminado) y `storage/kafka_consumer.py` (no existe); `tests/test_kafka.py` está archivado.
- `openspec/specs/almacenamiento-y-streaming/spec.md:4` sigue diciendo «Gate ... PASS» mientras el texto de INTEGRACION-01 dice «gate pendiente» (`:100-107`); persisten escenarios viejos de Mongo (`:78-96`).
- `.env.example` sigue sin `KAFKA_BOOTSTRAP_SERVERS` ni `STAGING_RAW`.
- `brief/.~lock...` sigue sin ignorar en `.gitignore`.
- `archive/kafka_2026-11-06/` sigue duplicando productor, consumidor y gate viejos.

### 12.5 Conclusión

La limpieza mejora la trazabilidad de la VM y elimina código muerto, pero **no mueve la rúbrica BDA**: el tramo Kafka→HDFS sigue sin consumidor versionado que haga el put, `procesado` sigue fuera de HDFS y el gate sigue sin existir. Para subir HDFS/Kafka/Integración hay que ejecutar los cambios 1-3 del plan (consumidor real, gate y procesado), no solo documentar.
