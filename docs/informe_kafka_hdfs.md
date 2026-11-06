# Informe Kafka + HDFS — Qué hemos hecho (2026-11-06)

Fecha: 2026-11-06
Rama: `master` (`d96b810`), repo `C:/Users/mikel/Documents/bigdata-vivienda-euskadi`
VM: `192.168.201.162` (Ubuntu Server 22.04.3, usuario `mikel`, SSH con `~/.ssh/id_vm_hermes`)
HDFS: clúster centro `http://10.22.87.215:50070`, usuario `iabd-user15`

Este informe resume lo hecho hoy para entender la parte de Kafka y HDFS.
La trazabilidad completa de comandos y salidas está en `docs/trazabilidad_vm.md`.

---

## 1. Mapa rápido (qué es cada pieza)

| Pieza | Dónde vive | Para qué sirve en el proyecto |
|---|---|---|
| VM | `192.168.201.162` (Ubuntu Server) | Aloja el broker Kafka. Es donde tú entras por SSH. |
| Kafka broker | VM `~/kafka`, KRaft 4.3.1, Java 17 | Cola de mensajes que simula "acaban de llegar anuncios nuevos". |
| Topic | `anuncios_inmobiliarios` (3 particiones, RF=1) | Canal por donde viajan los anuncios como JSON. |
| HDFS | `10.22.87.215:50070` (clúster centro, NO la VM) | "Caja fuerte" de ficheros originales: `/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw/`. |
| MongoDB | Windows `localhost:27017`, `vivienda_euskadi` | Base donde el consumidor inserta los anuncios y donde se analizan (esfuerzo, paro, etc.). |
| Código Python | Windows repo (`.venv` Python 3.12) | Productor, consumidor, subida HDFS, gate e2e. La VM no tiene el repo. |

Idea clave: la VM solo tiene el broker. Todo el código (`.py`), la configuración
(`config/`, `.env`, `requirements.txt`, `openspec/`) y el análisis viven en
Windows. Windows habla con Kafka por TCP `192.168.201.162:9094`, con HDFS por
WebHDFS `10.22.87.215:50070` y con Mongo por `localhost:27017`.

```
Fuentes (Eustat, INE, Fotocasa/Pisos por scraping)
  -> extract/ (Python) -> data/raw/ (originales inmutables)
  -> HDFS centro /raw/  (almacén)
  -> Kafka anuncios_inmobiliarios (simulación streaming)
  -> MongoDB anuncios (upsert idempotente)
  -> analysis/ 9 pipelines -> CSV/PNG en data/resultados/
```

---

## 2. HDFS: qué se comprobó (solo lectura)

- TCP `10.22.87.215:50070` OPEN.
- WebHDFS `LISTSTATUS` GET sobre `/user/iabd-user15/bigdata_reto/vivienda_euskadi/data` devuelve solo hijo `raw`.
- `LISTSTATUS` sobre `/data/raw` = 200 entradas top-level (197 ficheros + 3 dirs `gtfs, html_fotocasa, shp_euskadi`), bytes top 702.993.788.
- `LISTSTATUS` sobre `/data/procesado` = `FileNotFoundException` (no existe).
- Recuperación acreditada: `GETFILESTATUS` de `raw/alquiler_municipal.json` = 154205 bytes = tamaño local, SHA `6f5af1b3...` = `docs/raw_manifest_sha256.txt:2`.

Código relevante:

- `storage/hdfs_utils.py:35-36` `DEFAULT_HDFS_URL="http://10.22.87.215:50070"`, `DEFAULT_HDFS_USER="iabd-user15"`.
- `storage/hdfs_utils.py:117-153` `upload_raw_excluding_legacy()` sube `data/raw/` entero excluyendo `legacy_obsoleto_no_usar`, con estado resumible en `data/_hdfs_state/hdfs_upload_raw.json`.
- `storage/hdfs_utils.py:161-168` `read_file_sha256()`, `:171` `ping()`, `:180` `delete_recursive()`.
- `tests/test_hdfs.py` 6 passed (`FakeHDFSClient`, SHA byte-idéntico).

### Por qué `data/procesado` (silver) no se sube

- Silver: 188 ficheros, 228M, manifest 185 líneas, BOM, `run_manifest.json` con 35 scripts ordenados.
- Raw: 356 ficheros, 861M, manifest 354 líneas, `.FROZEN`.
- Decisión firmada 2026-11-05 (`docs/arquitectura_datos.md` última línea): solo-raw.

Razón: raw es la fuente inmutable; silver es derivado y regenerable con
`transform/run_all.py`. Subir un derivado que cambia en cada análisis crea
divergencia HDFS vs local (se vio con huella de esfuerzo `831e69...` vs real `731d16...`).
Entregable PDF: "Datos: ficheros originales almacenados en HDFS y base de datos MongoDB"
(linea 118 contrato). Originales = raw.

Rúbrica 10 HDFS: "Organiza originales y procesados y demuestra su recuperación"
(spec.md:36). Originales sí están (10 SHALL). Procesados quedan en SHOULD
(según `openspec/specs/almacenamiento-y-streaming/spec.md:34-42`, "hoy el procesado
está solo en local"). Es degradado a SHOULD por decisión del proyecto, no penalización nueva.

---

## 3. Kafka: estado al llegar (VM reiniciada)

- TCP probado desde Windows (socket Python):
  - HDFS `10.22.87.215:50070` OPEN.
  - Kafka `192.168.201.162:9094` CERRADO (connection refused).
  - SSH `192.168.201.162:22` OPEN.
- SSH con clave `id_vm_hermes`:
  - `hostname` = `mikel`, `uptime` = 4 min (reinicio reciente).
  - `ss -tlnp` sin LISTEN 9093/9094, sin proceso java/kafka.
  - Instalación intacta: `~/kafka` (4096, 8 entradas), `~/kafka-logs` (56 entradas, con `anuncios_inmobiliarios-0/1/2`, `bootstrap.checkpoint`, `meta.properties`), `server.properties` con `advertised.listeners=PLAINTEXT://192.168.201.162:9094,CONTROLLER://localhost:9093` y `log.dirs=/home/mikel/kafka-logs`, Java 17.

Conclusión: los datos del topic y la config sobrevivieron al reinicio; solo faltaba arrancar el binario (el pid 1832 de la trazabilidad ya no existía).

---

## 4. Cómo se levantó Kafka (arranque)

Comando (desde Windows, Git Bash o PowerShell, vía SSH BatchMode):

```bash
ssh -i C:/Users/mikel/.ssh/id_vm_hermes -o BatchMode=yes -o ConnectTimeout=6 -o StrictHostKeyChecking=no mikel@192.168.201.162 "~/kafka/bin/kafka-server-start.sh -daemon ~/kafka/config/server.properties"
```

Verificación dentro de la VM:

```bash
ss -tlnp | grep -E ':9093|:9094'
ps aux | grep kafka | grep -v grep
```

Resultado (tras ~8-10 s):

- `LISTEN *:9093 (java pid 1817)`, `LISTEN *:9094 (java pid 1817)`.
- TCP desde Windows `192.168.201.162:9094` OPEN.

El arranque es solo ese comando. No hizo falta repetir la parte inicial de la ficha
(`mkdir ~/kafka-logs`, `sed log.dirs/advertised`, `kafka-storage.sh format`)
porque ya quedó guardada en `server.properties` y `~/kafka-logs`.

---

## 5. Cómo se comprobó mano a mano (rúbrica)

Rúbrica implicada:

- BDA RA1 Kafka 10 pts (contrato spec.md:37, PDF línea 78): "Productor y consumidor Python funcionan y procesan mensajes".
- BDA RA1 Integración 10 pts (spec.md:38, PDF línea 79): "Demuestra el flujo completo hasta MongoDB".
- Requisitos: `KAFKA-01` (productor/consumidor Python vivos) e `INTEGRACION-01` (gate encadenado).

### Paso 1 — Broker vivo (dentro de la VM)

```bash
ss -tlnp | grep -E ':9093|:9094'
```

Salida:

```
LISTEN *:9093 (java pid 1817)
LISTEN *:9094 (java pid 1817)
```

### Paso 2 — Topic y particiones (dentro de la VM)

```bash
~/kafka/bin/kafka-topics.sh --describe --topic anuncios_inmobiliarios --bootstrap-server 192.168.201.162:9094
```

Salida (resumen):

```
Topic: anuncios_inmobiliarios  PartitionCount: 3  ReplicationFactor: 1
Partition 0 Leader: 1  Partition 1 Leader: 1  Partition 2 Leader: 1
min.insync.replicas=2
```

### Paso 3 — Mensajes reales (dentro de la VM)

```bash
~/kafka/bin/kafka-console-consumer.sh --bootstrap-server 192.168.201.162:9094 --topic anuncios_inmobiliarios --from-beginning --max-messages 2 --timeout-ms 15000
```

Salida (2 JSON):

```json
{"portal": "fotocasa", "id_anuncio": "159915860", "modalidad": "larga_estancia", "precio_eur": 995.0, "superficie_m2": 93.0, "habitaciones": 3.0, "codigo_ine": "20055", "municipio": "Arrasate/Mondragón"}
{"portal": "fotocasa", "id_anuncio": "176108408", "modalidad": "larga_estancia", "precio_eur": 1250.0, "superficie_m2": 145.0, "habitaciones": null, "codigo_ine": "48044", "municipio": "Getxo"}
Processed a total of 2 messages
```

Eso acredita avance: mensajes JSON con precio y municipio, que es lo que exige `KAFKA-01`.
El aviso `KIP-848` que sale antes es informativo, no error.

### Paso 4 — Publicar 10 de prueba (Windows, CMD o PowerShell)

```cmd
cd C:\Users\mikel\Documents\bigdata-vivienda-euskadi
.venv\Scripts\python.exe scripts\publish_adapter.py --limit 10
```

Salida (10 mensajes, offsets 278-292). El adapter reproduce determinísticamente
los primeros 10 ordenados por `(portal, id_anuncio)` vía `storage.kafka_producer.produce()`
con `Future.add_callback/add_errback (kafka-python 2.2.3)`. No se usa
`python -m storage.kafka_producer` directo porque en `kafka-python 2.2.3` `send()` no
admite `callback=` como kwarg y falla con `TypeError` (aviso `docs/kafka_vm.md:8`).

### Paso 5 — Gate completo (Windows)

```cmd
.venv\Scripts\python.exe scripts\gate_bloque2.py
```

Salida (primera corrida con adapter previo, por eso `GATE FAIL`):

```
HDFS_LEG LIST_BASE ['raw']  LIST_RAW_COUNT 200  STATUS_RAW childrenNum=200
CERO_ESCRITURAS NO_SUBIDO_RAW  CERO_ESCRITURAS NO_SUBIDO_PROCESADO
SUBSET 10 ... HUELLA_ESPERADA e32c3d3de196f169b86304d46295e0e621b5372a3809948f360fbaf81dbfaf25
PRODUCIDOS 10  Procesados: 10  CONSUME_RET 10
... 10 líneas OK CONSULTA_POR_CODIGO_INE 1 doc(s) ...
LAG p0 0  LAG p1 4  LAG p2 6  LAG_TOTAL 10
VERIFICADOS 10/10  HUELLA_SHA e32c3d3d...  TOTAL 759  MUNICIPIOS 252
GATE FAIL
```

Por qué FAIL: el gate exige `LAG_TOTAL 0` y `exit 0` solo si 10/10 + total>=759 + lag 0.
El adapter previo dejó 10 sin consumir (p1 4 + p2 6); el gate consumió 10 (sus propios
10 o los backlog), pero el lag quedó en 10. No es bug: Mongo verificó 10/10.

### Paso 6 — Vaciar lag y re-lanzar gate

```cmd
.venv\Scripts\python.exe -c "from storage.kafka_consumer import consume; print(consume(max_messages=10))"
.venv\Scripts\python.exe scripts\gate_bloque2.py
```

Salida (corrida final):

```
PRODUCIDOS 10  Procesados: 10  CONSUME_RET 10
... 10 líneas OK ...
LAG p0 CURRENT 287 LOG_END 287 LAG 0
LAG p1 CURRENT 301 LOG_END 301 LAG 0
LAG p2 CURRENT 272 LOG_END 272 LAG 0
LAG_TOTAL 0
VERIFICADOS 10/10
HUELLA_SHA e32c3d3de196f169b86304d46295e0e621b5372a3809948f360fbaf81dbfaf25
TOTAL 759
MUNICIPIOS 252
GATE PASS
```

### Paso 7 — Mongo a mano (solo lectura)

```cmd
.venv\Scripts\python.exe -c "from storage.mongo import get_collection; print(get_collection('anuncios').count_documents({})); print(get_collection('municipios').count_documents({}))"
```

```
759
252
```

No sube a 769 aunque republicaste: el consumidor hace upsert por `portal:id_anuncio`.

---

## 6. Duplicar en Kafka: ¿es mala práctica?

- Kafka es append-only: republicar el mismo anuncio añade mensajes y offsets (p. ej. 278-292, luego 293-300...). El topic crece.
- Mongo no se duplica: `storage/kafka_consumer.py:66-70` `update_one(..., upsert=True)` por `portal:id_anuncio` (idempotente, Decimal128, `zfill_ine`). Si llega el mismo, actualiza el doc existente.
- El subset de 10 se usa justo para no ensuciar de más. En producción se filtraría por "no está ya en Mongo" o se compactaría el topic; en gate de rúbrica basta 10/10.

---

## 7. Ficheros que importan para la defensa

| Fichero | Rol |
|---|---|
| `storage/kafka_producer.py` | Productor: `read_anuncios`, `row_to_anuncio`, `serialize_anuncio` (clave `portal:id_anuncio`, valor JSON), `produce()` con `flush + Future.add_callback/add_errback`. |
| `storage/kafka_consumer.py` | Consumidor: `upsert_anuncio` idempotente, `consume()` con `enable_auto_commit=False` y commit manual, reporta procesados. |
| `scripts/publish_adapter.py` | Publicación versionada (subset determinista de N primeros por `portal,id_anuncio`). |
| `scripts/gate_bloque2.py` | Gate e2e: HDFS-leg lectura (cero escrituras) > subset 10 > produce 10 > consume 10 (grupo `anuncios`) > verifica en Mongo por `portal+id+codigo_ine` > `GATE PASS/FAIL`. |
| `docs/kafka_vm.md` | Ficha de operación (configuración, arranque, smoke test con `console-producer/consumer`). |
| `docs/trazabilidad_vm.md` | Evidencia literal con Fecha/Objetivo/Máquina/Comando/Salida/Conclusión (Bloque 2026-11-06 con `GATE PASS`). |
| `tests/test_kafka.py` | 3 passed: serialización bytes con precio/municipio, productor 759 con flush/Future sin `callback` kwarg, upsert idempotente en `vivienda_euskadi_test`. |

---

## 8. Deuda y notas (no bloquean el 10)

- `min.insync.replicas=2` con RF=1 en `server.properties` + topic RF=1: contradictorio, puede causar `NOT_ENOUGH_REPLICAS` en producción real. No bloqueó el gate por upsert idempotente. Queda documentado como limitación.
- HDFS `raw 200` top-level vs manifest local 354/185: deriva de 2-4 ficheros (`.FROZEN/.gitkeep`, `Moreda de Álava` con error URL-encoding en LISTSTATUS recursivo). Reconciliable con `sha256sum -c`.
- Consumidor `__main__` sin `max_messages` bloquearía tras vaciar; mitigado con `consume(max_messages=10)` en gate.

---

## 9. Resumen para defensa (frases de 10 segundos)

- "HDFS es el almacén central (10.22.87.215:50070): solo subo originales, con recuperación SHA byte-idéntica; silver queda local y se regenera."
- "Kafka es simulación streaming en la VM (192.168.201.162:9094): productor y consumidor Python funcionan, topic 3 particiones, mensajes JSON con precio y municipio."
- "El flujo completo está probado en vivo con gate: 10 producidos, 10 consumidos, 10/10 en Mongo por código INE, lag 0, 759 anuncios y 252 municipios."
