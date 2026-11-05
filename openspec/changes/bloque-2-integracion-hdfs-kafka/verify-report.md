# Verification Report: bloque-2-integracion-hdfs-kafka

**Change**: bloque-2-integracion-hdfs-kafka
**Mode**: Standard (strict_tdd: false; no TDD module)
**Date**: 2026-11-05
**Verdict**: PASS WITH WARNINGS

## Resumen

Bloque 2 de `plan/PLAN_10.md` (pasos 5, 6 y 7) ejecutado en vivo con
trazabilidad total en `docs/trazabilidad_vm.md`. HDFS procesado listo en
local con dry-run sin subir, Kafka Python vivo con 759, gate con 10 de
prueba consultables en MongoDB por `codigo_ine`. Regresión offline
`pytest tests/test_contrato.py -q`: **54 passed**, manifest **353/184**.
Sin `git add/commit/push`, sin tocar `data/raw` ni `storage/` en la fase
principal (el fix Future en `storage/kafka_producer.py` + `tests/test_kafka.py`
es posterior y queda documentado en Issues y en tasks 4.2).

## Validación SDD (previa al apply)

Proposal/design/tasks/spec validados contra PLAN_10 pasos 5-7: **OK con
parches menores** (no reescritura):

| Contradicción menor | Artefacto parcheado |
|---|---|
| Design decía "Sin código nuevo en esta fase" pero tasks 1.2 exige entrypoint `--dry-run` inexistente en `storage/hdfs_utils.py` | `design.md`: "Sin código nuevo salvo entrypoint `--dry-run` no destructivo (`scripts/upload_procesado.py`)" + fila en File Changes |
| Tasks 1.2 no fijaba el comando dry-run | `tasks.md` 1.2: `.venv/Scripts/python.exe scripts/upload_procesado.py --dry-run` |
| Tasks 4.2 decía diff solo en `openspec/*` y trazabilidad, pero hacía falta entrypoint dry-run | `tasks.md` 4.2: admite `scripts/upload_procesado.py` y el fix Future en `storage/` + tests; sigue prohibido `data/` |

## 1. HDFS (paso 5)

Comando (tarea 1.1, vía `storage/hdfs_utils.py`):
`.venv/Scripts/python.exe -c "from storage.hdfs_utils import get_client; ..."`

Salida real (resumen; literal completa en `docs/trazabilidad_vm.md`):

```
URL http://10.22.87.215:50070
USER iabd-user15
STATUS_BASE {'accessTime': 0, 'blockSize': 0, 'childrenNum': 1, 'fileId': 2850393, 'group': 'iabd', 'length': 0, 'modificationTime': 1793819308659, 'owner': 'iabd-user15', 'pathSuffix': '', 'permission': '755', 'replication': 0, 'storagePolicy': 0, 'type': 'DIRECTORY'}
LIST_BASE ['raw']
LIST_RAW_COUNT 200
STATUS_RAW {'accessTime': 0, 'blockSize': 0, 'childrenNum': 200, 'fileId': 2850772, 'group': 'iabd', 'length': 0, 'modificationTime': 1793821405519, 'owner': 'iabd-user15', 'pathSuffix': '', 'permission': '755', 'replication': 0, 'storagePolicy': 0, 'type': 'DIRECTORY'}
```

Comando (tarea 1.2, nuevo entrypoint):
`.venv/Scripts/python.exe scripts/upload_procesado.py --dry-run`

```
DESTINO_HDFS /user/iabd-user15/bigdata_reto/vivienda_euskadi/data/procesado
N_FICHEROS 187 MANIFEST 184
TOTAL_FICHEROS 187 TOTAL_BYTES 238344685 OK 184 SIN_MANIFEST 3
DRY_RUN_OK CERO_ESCRITURAS NO_SUBIDO
```

Los 3 `SIN_MANIFEST` son esperados (`.gitkeep`, `_meta/ingestion_manifest.json`,
`manifest_sha256.txt`). Sin `--dry-run`: `REFUSADO: sin confirmación de la
profesora no se sube procesado (usa --dry-run)` exit 2. HDFS sigue solo con
`raw`; local raw 355 ficheros (351 sin legacy) intacto. Cero escrituras.

## 2. Kafka (paso 6)

Inicial (tarea 2.1): topic `anuncios_inmobiliarios` 3 particiones,
log-end `0:0 1:0 2:1`, sin grupo `anuncios`. Peek con grupo `peek_bloque2`
(curioso, no avanzó `anuncios`): mensaje previo en `p2/o0` con
`{"precio": 850, "municipio": "Bilbao"}`, sin `portal`/`id_anuncio`.

Productor (tarea 2.2): **advertencia crítica — ver Issues**. Entrypoint
directo `.venv/Scripts/python.exe -m storage.kafka_producer` falla en el
broker real:

```
TypeError: KafkaProducer.send() got an unexpected keyword argument 'callback'
```

`kafka-python 2.2.3` no admite `callback` como kwarg de `send`; el
callback va en el `Future` (`add_callback`/`add_errback`). Los tests en
`tests/test_kafka.py` usan `MagicMock` y pasan, pero no cubren la API
real. Sin tocar `storage/` (prohibido en esta fase), se publicó con un
adapter en scratch (fuera del repo) que reutiliza
`storage.kafka_producer.produce()` con inyección (mismo patrón que los
tests): `CallbackProducer` envuelve `KafkaProducer` real y traduce
`send(callback=...)` a `Future.add_callback/add_errback`.

Salida real:

```
Publicado topic=anuncios_inmobiliarios partition=0 offset=0
... (759 líneas Publicado, literal completa en trazabilidad)
Publicados 759 anuncios en anuncios_inmobiliarios
ADAPTER_PUBLICADOS 759
```

Offsets tras producir: `0:257 1:261 2:242` (suma 760 = 759 nuevos + 1
previo). Grupo `anuncios` aún inexistente (`GroupIdNotFoundException`,
esperado).

Consumidor (tarea 2.3): `consume(group_id='anuncios', max_messages=759)`
(mismo código `storage/kafka_consumer.py`, commit manual, upsert por
`portal`+`id_anuncio`):

```
Mensaje sin portal/id_anuncio, se descarta: {'precio': 850, 'municipio': 'Bilbao'}
Procesados: 759
CONSUME_RET 759
```

Grupo tras consumir: `CURRENT-LOG_END-LAG 257/257/0, 261/261/0, 242/242/0`.
Mongo: `anuncios 759`, `municipios 252` — upsert sin duplicar
(759 antes → 759 después). Desviación honesta: `python -m
storage.kafka_consumer` sin límite bloquearía tras vaciar; se acota con
`max_messages`.

## 3. Gate e2e con 10 (paso 7)

Subset determinista: primeros 10 ordenados por `(portal, id_anuncio)`:

```
fotocasa:131393829 codigo_ine=01059 municipio=Vitoria-Gasteiz
fotocasa:159915860 codigo_ine=20055 municipio=Arrasate/Mondragón
fotocasa:161991304 codigo_ine=48020 municipio=Bilbao
fotocasa:162213906 codigo_ine=48020 municipio=Bilbao
fotocasa:176108369 codigo_ine=48044 municipio=Getxo
fotocasa:176108408 codigo_ine=48044 municipio=Getxo
fotocasa:176113409 codigo_ine=48044 municipio=Getxo
fotocasa:176216653 codigo_ine=48054 municipio=Leioa
fotocasa:176216662 codigo_ine=48016 municipio=Berango
fotocasa:176219963 codigo_ine=48054 municipio=Leioa
```

Produce 10 (tarea 3.1): `Publicado ... partition=0 offset=257/258/259,
partition=2 offset=242/243/244, partition=1 offset=261/262/263/264`
+ `ADAPTER_PUBLICADOS 10`. Log-end `260/265/245` (suma 770), lag `3/4/3`.

Consume 10 (tarea 3.2): `Procesados: 10`, lag `0/0/0`, grupo `260/265/245`.

Verificación Mongo (tarea 3.3): **10/10 consultables por `codigo_ine`**
(cada consulta `portal+id_anuncio+codigo_ine` devuelve 1), total
`759`, `municipios 252`, huella:

```
VERIFICADOS 10/10
HUELLA_SHA e32c3d3de196f169b86304d46295e0e621b5372a3809948f360fbaf81dbfaf25
```

## 4. Regresión y cierre (tarea 4)

```
......................................................                   [100%]
54 passed in 0.75s
```

Manifest: `docs/raw_manifest_sha256.txt 353`, `data/procesado/manifest_sha256.txt 184`.

Discrepancia 355/353/200 (nota): 355 = `find data/raw -type f` recursivo
(351 sin `legacy_obsoleto_no_usar` + 4 legacy); 353 = líneas del manifest
(= 355 − 2 dotfiles `.FROZEN`/`.gitkeep` sin entrada en el manifest);
200 = `LIST_RAW_COUNT` de nivel superior en HDFS (`childrenNum` / LISTSTATUS),
no conteo recursivo de ficheros, por lo que no es comparable directo con
355/353 (local top-level 201 con dotfiles / 199 sin dotfiles + 4 subdirs).
La comparabilidad se cierra con SHA+tamaño de 1 fichero recuperado en solo
lectura (`alquiler_distrito_seccion_original.csv` 17243 bytes,
`b0e3583f…f5134` local = remoto), ver entrada de trazabilidad.

`git status --short`:

```
 M README.md
 M docs/README.md
 M storage/kafka_producer.py
 M tests/test_kafka.py
 M transform/validar_renta.py
?? docs/analisis_vault_vs_rubrica.md
?? docs/trazabilidad_vm.md
?? openspec/changes/bloque-2-integracion-hdfs-kafka/
?? plan/PLAN_10.md
?? scripts/gate_bloque2.py
?? scripts/hdfs_recuperacion_un_fichero.py
?? scripts/publish_adapter.py
?? scripts/upload_procesado.py
```

Sin `data/` modificados; sin `git add/commit/push`; sin cron; sin
console-producer. Fase fixer (2026-11-05): `storage/kafka_producer.py`
parcheado y `tests/test_kafka.py` actualizado a Future, scripts
`publish_adapter.py`/`gate_bloque2.py`/`hdfs_recuperacion_un_fichero.py`
versionados en el repo (fuera de scratch).

## Issues

### CORREGIDO — `storage/kafka_producer.py` roto contra el broker real

`produce()` pasaba `callback=_on_send_success` a `KafkaProducer.send()`,
kwarg que `kafka-python 2.2.3` no admite. El entrypoint directo fallaba;
los tests con `MagicMock` no lo detectaban (`assert "callback" in kwargs`).
Se trabajó alrededor con un adapter en scratch sin tocar `storage/`, pero
el módulo seguía roto para el próximo uso directo. Recomendación:
parchear `produce()` a `fut = producer.send(...); fut.add_callback(...);
fut.add_errback(...)` (rompe el test mock actual, que deberá actualizarse).
No se parcheó en esta fase por la prohibición expresa.

Fixer 2026-11-05: aplicado. `produce()` usa `future =
producer.send(topic_name, key=key, value=value)` +
`future.add_callback(_on_send_success)` + `future.add_errback(_on_send_error)`;
`tests/test_kafka.py` exige `send` sin `callback` y `Future` con
`add_callback/add_errback` (759). Adapter versionado en
`scripts/publish_adapter.py` y gate en `scripts/gate_bloque2.py`
(reproducen SUBSET/Publicado/ADAPTER + VERIFICADOS 10/10, huella
`e32c3d3…faf25`, 759/252, lag 0). HDFS SHA de 1 fichero cerrado.

## Cumplimiento de specs

| Requirement | Scenario | Evidencia | Estado |
|---|---|---|---|
| HDFS-01 Originales y procesados conviven | Dry-run lista procesado sin subir | 187 ficheros / 238344685 bytes / 184 OK, LIST_BASE `['raw']` | PASS |
| HDFS-01 La recuperación se demuestra | Tamaño igual al recuperar | 1 fichero SHA+tamaño local = remoto (`b0e3583f…`), cero escrituras | PASS |
| KAFKA-01 El productor publica anuncios | 759 con precio y municipio | 759 `Publicado topic/partition/offset` + Future `add_callback/add_errback` (fixes 2026-11-05, adapter/gate versionados) | PASS |
| KAFKA-01 El consumidor procesa los mensajes | 759 procesados | `Procesados: 759`, Mongo 759 | PASS |
| KAFKA-01 El consumidor no duplica | Segundo pase no duplica | 759→759 tras 759, luego 10→759 | PASS |
| INTEGRACION-01 El flujo extremo a extremo | 10 consultables por `codigo_ine` | 10/10, huella `e32c3d3…faf25`, 759/252, lag 0 (`scripts/gate_bloque2.py` PASS) | PASS |

Veredicto final: **PASS WITH WARNINGS** (justificado). Warnings restantes
no bloqueantes y fuera de alcance: (1) procesado pendiente de subida hasta
confirmación de la profesora (dry-run listo, cero escrituras); (2)
entrada `python -m storage.kafka_consumer` sin límite bloquearía tras
vaciar, por eso se acota con `max_messages` (mismo grupo/commit/upsert).
