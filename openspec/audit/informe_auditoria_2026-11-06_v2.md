# Informe de auditoría completa (v2) — bigdata-vivienda-euskadi

**Fecha:** 2026-11-06
**Modo:** solo lectura estricto. Única escritura: este fichero.
**Alcance:** código vivo (`storage/`, `scripts/`, `extract/`, `transform/`, `analysis/`, `tests/`), datos locales, HDFS, Kafka y MongoDB; documentación activa.
**Fuente de verdad:** `openspec/specs/contrato-reto/spec.md` (rúbrica v2). Si el código y el contrato discrepan, manda el contrato.
**Regla aplicada:** ningún hallazgo sin comando + número. Lo no verificable se marca `PENDIENTE`, nunca se regala.

---

## 1. Resumen ejecutivo

| Bloque | Nota | Lectura |
|---|---|---|
| BDA RA1 · Extracción Python | **10 provisional** | 41 scripts, 39 con `main()`, 8 con `requests` (API), 101 HTML crudos de portal. Matiz: 0 usos de BeautifulSoup. |
| BDA RA1 · HDFS | **7** | 352/352 ficheros, bytes idénticos, 0 diferencias. **No existe `data/procesado`**, que el 10 exige junto a los originales. |
| BDA RA1 · Kafka | **10** | Productor y consumidor Python reales sobre el broker del centro, lag 0, 352 manifiestos procesados y commiteados (evidencia en vivo de hoy). |
| BDA RA1 · Integración | **7** | La cadena termina en HDFS; no hay ningún eslabón que escriba en MongoDB. |
| SBD RA1 · Fuentes / conjunto / limpieza / automatización | **10** | `$lookup` 759/759 y 252/252; 14 colecciones reales; índices y `explain` IXSCAN; `run_all.py` documentado. |
| SBD RA3 · MongoDB | **10 con evidencia parcial** | Índices + `IXSCAN` verificados; operación atómica en `storage/mongo.py:marcar_calidad_municipio`. |
| SBD RA4 · Análisis | **10 provisional** | 7 scripts en `analysis/`, 27 ficheros en `data/resultados/`; no recontados los 5 indicadores uno a uno. |

**Veredicto honesto:** el bloque de datos y MongoDB está sólido y acreditable. El bloque BDA de almacenamiento/streaming se queda en **7 por dos motivos estructurales, no por bugs**: HDFS sin procesados y flujo que no desemboca en MongoDB. Kafka **sí** sube a 10 tras la migración al centro y el arreglo del consumidor.

**Hallazgos:** 4 P1, 5 P2, 5 P3, 2 `PENDIENTE`.

---

## 2. Baseline y prueba de cero cambios

| Comprobación | Antes | Después |
|---|---|---|
| `git status --short` | `M storage/kafka_hdfs_uploader.py` | igual + este informe (untracked) |
| Kafka `log_end` / `committed` p0 | 1420 / 1420 | 1420 / 1420 |
| HDFS ficheros / bytes | 352 / 895.596.949 | 352 / 895.596.949 |
| Mongo `anuncios` / `municipios` | 759 / 252 | 759 / 252 |

No se escribió en HDFS, Kafka ni Mongo; no se ejecutó ningún test que escriba (solo `--collect-only`, con `PYTHONDONTWRITEBYTECODE=1` y `-p no:cacheprovider`).

---

## 3. D2 · Kafka

### 3.1 Identidad y topología (medido)

| Hecho | Valor |
|---|---|
| Cluster | `_SkY85viRcCny6RracjOrw`, controller `1001` |
| Brokers | **1**: `hadoop-master1.tartangalh.eus:9092` (el servidor del centro, misma máquina que WebHDFS) |
| Topic | `anuncios_inmobiliarios`, `is_internal=False` |
| Particiones | **1** (p0, leader 1001, replicas `[1001]`, ISR `[1001]`) |
| Offsets | `log_end=1420`, `committed=1420`, **lag 0** |
| Mensajes / ficheros | 1420 / 352 → **ratio 4,03** |
| Grupos de consumidores en el cluster | **21** (cluster compartido con otros alumnos; `hdfs_centro` es el nuestro) |

### 3.2 Código (revisión contra el contrato)

| Requisito | Evidencia | Estado |
|---|---|---|
| Productor Python publica | `storage/kafka_raw_producer.py:54` `KafkaProducer(...)`, `:60` `send(key=rel, value=manifest)`, `:63` `flush()` | cumple |
| Consumidor Python consume | `storage/kafka_hdfs_uploader.py:105-111` `KafkaConsumer(...)`, `:123-134` bucle `poll` + iteración por lotes | cumple |
| Descarta mensajes sin `type:raw_manifest` | `:141-145` (`skipped += 1` + commit) | cumple |
| Valida `rel` (sin `..`, sin absoluta, sin legacy) | `:64-81` + uso en `:149` | cumple |
| Aborta por mismatch SHA/tamaño | `:154-156` → `SystemExit("ABORT SHA/SIZE MISMATCH ...")` | cumple |
| Commit manual (at-least-once controlado) | `:112-119` `_commit`, `:170` commit tras cada subida | cumple, con coste (ver P2-2) |
| Termina al vaciar el topic | `:121-130` salida por `KAFKA_IDLE_MS` (10 s) | cumple (era el bug del atasco) |

### 3.3 `PENDIENTE`

`describe_configs` de `kafka-python-ng` devolvió una **lista**, no un diccionario, y la extracción de `min.insync.replicas` / `cleanup.policy` / `retention.ms` no se pudo cerrar. **No se afirma nada sobre la configuración del topic.** Comando para cerrarlo (solo lectura):

```bash
kafka-configs.sh --bootstrap-server 10.22.87.215:9092 --entity-type topics \
  --entity-name anuncios_inmobiliarios --describe
```

---

## 4. D3 · HDFS y D6 · datos

| Hecho | Medido |
|---|---|
| Ficheros en `.../data/raw` | **352** |
| Bytes en HDFS | **895.596.949** |
| Ficheros locales (sin legacy) | **352** — mismos bytes |
| Faltan en HDFS / sobran / tamaños distintos | **0 / 0 / 0** |
| `data/` childrenNum | 1 (`['raw']`) |
| `raw` childrenNum | 201 (197 ficheros en raíz + 4 directorios) |
| Propietario / permisos | `iabd-user15:iabd`, `755` |
| `data/procesado` | **no existe** (`HdfsError`) |
| `.FROZEN` | 0 bytes (marcador vacío) |
| `legacy_obsoleto_no_usar` | 4 ficheros, excluidos por productor y uploader |
| PDF/DOCX en `data/raw` | 0 |

### 4.1 Reconciliación del manifiesto (`docs/raw_manifest_sha256.txt`)

354 líneas frente a 352 ficheros. La diferencia está **explicada al 100 %**, no es un hueco:

- 348 `rel` coinciden nombre a nombre.
- 6 `rel` del manifiesto no existen en disco: **4 son `legacy_obsoleto_no_usar/*`** y **2 están mal codificados** (`Araba_pagina_1.html` y `Gerrikaitz_pagina_1.html`).
- 4 ficheros locales no están en el manifiesto: `.FROZEN`, `.gitkeep` y las dos rutas reales que el manifiesto guarda truncadas (`html_fotocasa/Moreda de Álava/Moreda Araba_pagina_1.html`, `html_fotocasa/Munitibar-Arbatzegi Gerrikaitz_pagina_1.html`).

**Consecuencia (P3-1):** el manifiesto no sirve como fuente de integridad por nombre hasta arreglar esas 2 rutas con caracteres no ASCII.

### 4.2 Hash extremo a extremo

`scripts/hdfs_verify.py` compara SHA-256 local vs descarga WebHDFS. Verificados hoy **13/13 `Igual? True`** (3 individuales + lote de 10), incluidos `.FROZEN`/`.gitkeep` (0 B), `shp_euskadi/` y `html_fotocasa/`. El resto se cubre con conteo + igualdad de bytes totales (895.596.949 en ambos lados).

---

## 5. D4 · Integración extremo a extremo

Cadena real medida:

```
data/raw (352) --producer--> Kafka 10.22.87.215:9092 --consumer--> WebHDFS 10.22.87.215:50070 (352)
```

- Cada eslabón está acreditado con offsets y conteos (ver D2/D3).
- **Ningún punto del camino escribe en MongoDB**: `grep -rn "KafkaConsumer|KafkaProducer"` sobre código activo devuelve solo los dos ficheros de `storage/`; ni uno importa `pymongo`.
- El consumidor anterior que hacía upsert (`storage/kafka_consumer.py`) **no existe**: está en `archive/kafka_2026-11-06/`.

**Consecuencia (P1-2):** el criterio "flujo completo hasta MongoDB" **no está demostrado**. Se puntúa 7, no 10, y no es un bug: es una decisión de arquitectura (solo-raw) que la rúbrica no contempla.

---

## 6. D5 · MongoDB (solo lectura)

| Hecho | Medido |
|---|---|
| Colecciones | **27** = 14 reales + **13 `__backup`** |
| `anuncios` | 759 |
| `municipios` | 252 |
| `alquiler_municipal` | 252 |
| Join `anuncios.ubicacion.codigo_ine → municipios._id` | **759/759 con match** |
| Join `alquiler_municipal.codigo_ine → municipios._id` | **252/252 con match** |
| `municipios.codigo_ine` | **0 documentos** (el INE vive en `_id`) |
| Índices `anuncios` | `_id_`, `idx_anuncios_geo`, `idx_anuncios_portal_id`, `idx_anuncios_equipamiento`, `idx_anuncios_ine_modalidad_precio` |
| Índices `municipios` / `alquiler_municipal` | `idx_municipios_territorio_nombre` / `idx_alquiler_ine_distrito_nivel` |
| `explain` de `{"ubicacion.codigo_ine": "48020"}` | `FETCH` sobre **`IXSCAN`** (usa índice, no COLLSCAN) |

**Consecuencia (P2-3):** el "campo común" que exige la rúbrica se cumple técnicamente por `_id` (5 dígitos INE), pero un evaluador que busque `codigo_ine` en `municipios` no lo verá.

---

## 7. D1 · Contrato vs código

| Criterio (rúbrica literal) | Nota | Evidencia |
|---|---|---|
| Extracción: automatiza API **y** scraping | 10 provisional | 41 `.py`, 39 con `main()`; 8 con `requests`; 11 módulos referencian fotocasa/pisos/idealista; 101 HTML crudos en `data/raw`; respuesta original de API (`*_raw.json`) |
| HDFS: originales **y** procesados | **7** | 352/352 + SHA OK, pero `data/procesado` = 404 |
| Kafka: productor y consumidor funcionan | **10** | offsets 1068→1419, `HDFS_CENTRO_UPLOADED 352`, `committed=1420`, `lag=0` |
| Integración: flujo completo hasta MongoDB | **7** | termina en HDFS (D4) |
| SBD RA1: 2+ fuentes relacionadas | 10 | 759/759 y 252/252 |
| SBD RA1: 2+ colecciones + relación/embedding | 10 | 14 colecciones, `anuncios.ubicacion` anidado |
| SBD RA1: ≥4 operaciones de limpieza | 10 | `clean_mongo.py` + `load_mongo.py` (no recontadas hoy una a una) |
| SBD RA1: automatización sin pasos manuales | 10 | `transform/run_all.py` (34 scripts), `load_mongo.py`, `run_mongo_pipeline.py` |
| SBD RA3: índices + `explain` | 10 | `IXSCAN` medido hoy |
| SBD RA3: atómico o transacción | 10 | `storage/mongo.py:marcar_calidad_municipio` (`find_one_and_update` + `ReturnDocument.AFTER`) |
| SBD RA4: ≥5 indicadores, ≥3 municipios, resultados auto | 10 provisional | 7 scripts en `analysis/`, 27 ficheros en `data/resultados/` |

---

## 8. D7 · Tests y calidad

| Hecho | Medido |
|---|---|
| Tests colectados | **134** (`pytest --collect-only`, exit 0, 1,59 s) |
| Ficheros de test | 17 |
| Tests del pipeline Kafka/HDFS | **solo `tests/test_hdfs.py`** (con `FakeHDFSClient`) |
| `storage/` sin cobertura | `kafka_raw_producer.py`, `kafka_hdfs_uploader.py`, `hdfs_utils.upload_raw_excluding_legacy` (solo fake) |
| Código muerto | `hdfs_utils._sha_local` (definido, sin uso) |
| Lógica duplicada | verificación SHA en `hdfs_utils.read_file_sha256` y en `uploader.verify_local` |

Deriva de conteos: informes previos citan **136** tests; hoy son **134**.

---

## 9. D8 · Documentación (afirmaciones que hoy son falsas)

| Fichero:línea | Afirma | Realidad medida |
|---|---|---|
| `AGENT.md:4` | "Kafka VM `192.168.201.162:9094` … topic 3 particiones" | centro `10.22.87.215:9092`, **1 partición** |
| `README.md:104` | "broker 4.3.1 KRaft en 9094, topic 3 particiones" | igual que arriba |
| `README.md:191,249,264` | `VM_HOST=192.168.201.162`, `VM_KAFKA_PORT=9094` | ninguna `.py` lee esas variables |
| `README.md:264` | "`storage/kafka_producer.py` y `storage/kafka_consumer.py` … `tests/test_kafka.py`" | **no existen** (los reales son `kafka_raw_producer.py` y `kafka_hdfs_uploader.py`; el test está en `archive/`) |
| `README.md:102,254,299` | "16 colecciones" | **14 reales** (+13 `__backup`) |
| `demo-mapa/README.md:29-30,58` | Kafka VM 9094, 3 particiones, 16 colecciones | centro, 1 partición, 14 |
| `demo-mapa/compositions/pipeline-mapa.html:347,352,353` | "3 particiones", broker 9094 | centro, 1 partición |
| `scratchpad/build_mapa.py:448,453,454` | idem (genera el HTML) | idem |
| `docs/guion_defensa.md:5` | "Kafka VM … pid 1832" | broker del centro; ese pid no aplica |
| `.env.example:10-11` | `VM_HOST`, `VM_KAFKA_PORT` | sin uso; **faltan** `KAFKA_BOOTSTRAP_SERVERS`, `KAFKA_GROUP_ID`, `KAFKA_IDLE_MS` |
| `AGENT.md:4` | "extracción `requests`/`beautifulsoup4`/`lxml`" | **0 usos de BeautifulSoup** en `extract/` |

Variables de entorno: usadas y no declaradas → `KAFKA_BOOTSTRAP_SERVERS`, `KAFKA_GROUP_ID`, `KAFKA_IDLE_MS`, `MONGO_ALLOW_DESTRUCTIVE`, `RAW_GUARD_AUDIT_LOG`. Declaradas y no usadas → `VM_HOST`, `VM_KAFKA_PORT`, `HDFS_BASE_PATH`, `IDEALISTA_API_KEY`.

---

## 10. D9 · Seguridad

| Comprobación | Resultado |
|---|---|
| Ficheros sensibles versionados (`.env`, `api.txt`, `*.pem`, `id_rsa`) | **ninguno** |
| `.env` ignorado | sí (`.gitignore:1`) |
| Credenciales hardcodeadas en `.py` activos | **0 matches** |
| IPs internas como default | sí (`10.22.87.215` en `storage/`): riesgo bajo, no secreto |
| `MONGO_ALLOW_DESTRUCTIVE` | convención de nombre, sin gate en código (P3) |

---

## 11. D10 · Reproducibilidad

Procedimiento real, verificado hoy en vivo:

```cmd
.venv\Scripts\python.exe storage\kafka_raw_producer.py      REM 352 manifiestos -> Kafka centro
.venv\Scripts\python.exe storage\kafka_hdfs_uploader.py     REM consume, valida SHA, put WebHDFS
```

- **El orden es obligatorio.** Con `auto_offset_reset='earliest'` y lag 0, ejecutar solo el consumidor sube **0 ficheros** y termina en 10 s (`SIN_MENSAJES`). Cualquier documento que presente el consumidor como paso independiente induce a error.
- Prerrequisitos no declarados en ningún doc: estar en la red del centro (9092 y 50070 abiertos).

---

## 12. Registro de hallazgos

| ID | Sev. | Hallazgo | Evidencia | Veredicto |
|---|---|---|---|---|
| P1-1 | **P1** | HDFS sin `data/procesado`: el criterio HDFS no puede ser 10 | `status(data/procesado)` → `HdfsError` | confirmado |
| P1-2 | **P1** | El flujo no desemboca en MongoDB: Integración = 7 | grep: ningún `.py` del camino importa pymongo | confirmado |
| P1-3 | **P1** | Estado resumible **obsoleto**: `data/_hdfs_state/hdfs_upload_raw.json` tiene 351 entradas con mtime 2026-11-04, anteriores al borrado de HDFS. `python -m storage.hdfs_utils` deduplicaría 351 y subiría 1, sin error, dejando HDFS incompleto | `json.load` → 351; `upload_raw_excluding_legacy:117-153` | confirmado (riesgo latente) |
| P1-4 | **P1** | Documentación activa describe infraestructura inexistente (VM/9094/3 particiones) y módulos borrados (`kafka_producer.py`, `kafka_consumer.py`, `test_kafka.py`) | D8 | confirmado |
| P2-1 | P2 | Sin deduplicación en el camino Kafka: 1420 mensajes para 352 ficheros (4,03×), `overwrite=True` y topic sin compactar | D2 + `:167` | confirmado |
| P2-2 | P2 | Coste por fichero: commit síncrono por mensaje (352 commits) y el fichero se lee dos veces en memoria (118 MB × 2 = pico ~236 MB) | `:154-159` `verify_local` + `read()` | confirmado por código |
| P2-3 | P2 | `municipios` no expone `codigo_ine`; el join va por `_id` | `count_documents({"codigo_ine":…})=0` | confirmado |
| P2-4 | P2 | `.env.example` desalineado (5 usadas sin declarar, 4 declaradas sin uso) | D8 | confirmado |
| P2-5 | P2 | Único cambio sin commit: `storage/kafka_hdfs_uploader.py` (+91/−58), que es justo el arreglo del consumidor | `git diff --stat` | confirmado |
| P3-1 | P3 | Manifiesto con 2 rutas mal codificadas (no ASCII) y sin dotfiles: inutilizable como integridad por nombre | D3.1 | confirmado |
| P3-2 | P3 | 13 colecciones `__backup` en producción (48 % del namespace); README/demo dicen 16 colecciones | D5, D8 | confirmado |
| P3-3 | P3 | `beautifulsoup4` y `lxml` declaradas y no usadas; `AGENT.md` afirma extracción con BeautifulSoup | grep 0 matches | confirmado |
| P3-4 | P3 | Sin tests del pipeline Kafka/HDFS; 134 tests frente a los 136 citados | D7 | confirmado |
| P3-5 | P3 | Código muerto (`_sha_local`) y doble verificación SHA en dos módulos | D7 | confirmado |
| P3-6 | P3 | `MONGO_ALLOW_DESTRUCTIVE` sin gate real en código | D9 | confirmado |
| — | PENDIENTE | Configuración del topic (`min.insync.replicas`, `cleanup.policy`, retención) | `describe_configs` devolvió lista; extracción fallida | no verificado |
| — | PENDIENTE | Recuento individual de los 9 pipelines y de los 5 indicadores | solo conteos agregados | no verificado |

---

## 13. Gate de cierre

- [x] Acceso a Kafka/HDFS/Mongo verificado al inicio y al final.
- [x] Cada criterio de rúbrica con nota y evidencia.
- [x] HDFS: 352/352, 0 diferencias, 0 tamaños distintos.
- [x] Kafka: identidad del broker, offsets y lag medidos.
- [x] Mongo: joins reproducidos y `explain` ejecutado.
- [x] 16 hallazgos con veredicto; 2 declarados `PENDIENTE` con comando de cierre.
- [x] Cero modificaciones: baseline reproducido tras la auditoría.
- [ ] Configuración del topic: pendiente del comando de §3.3.

---

## 14. Conclusión

El proyecto está **sano en datos**: 895.596.949 bytes idénticos entre `data/raw` y HDFS, 759/759 y 252/252 de matching por código INE, índices usados de verdad (`IXSCAN`) y una cadena Kafka real con lag 0. Los problemas que quedan **no son de corrección sino de encaje con la rúbrica y de documentación**:

1. HDFS solo tiene originales: sin `data/procesado`, ese criterio no pasa de 7.
2. La cadena termina en HDFS: sin escritura en MongoDB, Integración no pasa de 7.
3. La documentación activa (README, AGENT.md, demo, guion) describe la infraestructura de la VM, que ya no existe, y módulos borrados: es el riesgo más alto de cara a la defensa.
4. El estado resumible de `hdfs_utils` quedó obsoleto tras el borrado de `raw`: si alguien usa ese camino, subirá 1 fichero y dirá que deduplicó 351.

Kafka, que era el bloque atascado al inicio, **hoy es el criterio más sólido de BDA**: productor y consumidor reales, offsets commiteados y SHA verificado fichero a fichero.
