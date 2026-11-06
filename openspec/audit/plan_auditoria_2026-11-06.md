# Plan de auditoría completa — bigdata-vivienda-euskadi

**Fecha:** 2026-11-06
**Alcance:** proyecto completo, con foco en `almacenamiento-y-streaming` (BDA-RA1 HDFS/Kafka/Integración) y su mapeo a SBD-RA1 Integración de fuentes.
**Modo:** solo lectura. No se modifica `data/`, `storage/`, `transform/`, `extract/`, `tests/` ni la VM durante la auditoría. Las reparaciones van en un plan aparte, tras aprobación.
**Fuente de verdad de la nota:** `brief/RETO 1Evaluacion SBD-BDAv2.pdf`, págs. 3-4 (BDA RA1 y SBD RA1), cotejadas literalmente en esta sesión.

---

## 0. Verificación de acceso (ejecutada, no supuesta)

| Comprobación | Comando | Resultado medido | Estado |
|---|---|---|---|
| VM responde | `ping 192.168.201.162` | 2/2 paquetes, 1-20 ms | ✅ |
| SSH con clave | `ssh -i C:/Users/mikel/.ssh/id_vm_hermes -o BatchMode=yes mikel@192.168.201.162 "hostname; whoami"` | `mikel` / `mikel`, exit 0 | ✅ |
| Kafka 9093/9094 | `ss -tlnp \| grep -E ':9093\|:9094'` (en VM) | `LISTEN *:9093` y `*:9094`, java pid 1817 | ✅ |
| Topic | `kafka-topics.sh --describe` | `anuncios_inmobiliarios`, 3 particiones, RF 1, `min.insync.replicas=2` | ✅ (config incoherente, ver P2-4) |
| Grupo consumidor | `kafka-consumer-groups.sh --all-groups --describe` | `hdfs_vm`, offsets 124/121/117, **LAG 0** | ✅ |
| HDFS WebHDFS | `GET /webhdfs/v1/.../data?op=LISTSTATUS` | HTTP 200, base = `['raw']` | ✅ |
| HDFS raw | `LISTSTATUS .../data/raw` | 201 entradas (198 ficheros, 3 dirs), 703.029.215 B en nivel raíz | ✅ |
| SHA extremo a extremo | `sha256sum` local vs descarga WebHDFS de `alquiler_municipal.json` | `6f5af1b3…f79574b` en ambos, 154.205 B | ✅ |
| Mongo local | `pymongo` a `localhost:27017` | `vivienda_euskadi`, 27 colecciones, `anuncios`=759, `municipios`=252, `alquiler_municipal`=252 | ✅ |

**Conclusión de acceso:** sí hay acceso de lectura y ejecución a la VM por SSH con la clave `id_vm_hermes`, y acceso a WebHDFS y Mongo local. La auditoría puede re-ejecutar comandos en vivo, no solo leer documentación.

---

## 1. Fuentes de verdad y criterio de puntuación

### 1.1 Rúbrica literal (PDF pág. 3 · BDA RA1)

| Criterio | 0 | 3 | 7 | 10 |
|---|---|---|---|---|
| Extracción de datos mediante Python | No obtiene datos | Una fuente manual | Automatiza una API o scraping | **Automatiza API y scraping** |
| Almacenamiento HDFS | No almacena | Crea directorios | Guarda y recupera archivos | **Organiza originales y procesados y demuestra su recuperación** |
| Kafka | No funciona | Crea un tópico | Envía mensajes con productor Python | **Productor y consumidor Python funcionan y procesan mensajes** |
| Integración | No hay integración | Componentes por separado | Integra 2+ componentes | **Demuestra el flujo completo hasta MongoDB** |

### 1.2 Rúbrica literal (PDF pág. 4 · SBD RA1, peso 46,7 %)

| Criterio | 0 | 3 | 7 | 10 |
|---|---|---|---|---|
| Integración de fuentes | No carga en MongoDB | 1 fuente | 2 fuentes diferentes | **2+ fuentes diferentes relacionadas por ≥1 campo común** |
| Construcción del conjunto | No hay estructura | Todo en una colección sin tratar | 2+ colecciones o anidados/arrays | **2+ colecciones y ≥1 relación, embedding o referencia** |
| Limpieza y transformación PyMongo | No limpia | 1 operación | ≥3 operaciones | **≥4 operaciones, incluyendo nulos/ausentes, duplicados y tipos/formato** |
| Automatización | Manual | Parcial | Repetible con pasos | **Repetible sin intervención manual** |

**Regla:** sin evidencia del umbral 10 (comando + número + fichero:línea), se puntúa 7. Lo no verificable se marca `PENDIENTE`, nunca se regala.

### 1.3 Excepciones declaradas por el alumno

- `data/raw` puede contener PDF/DOCX de la profesora y esos no se suben a HDFS. **Verificado:** hoy no hay ningún `.pdf` ni `.docx` dentro de `data/raw` (0 resultados), luego la excepción no está ocultando un hueco actual.
- `data/raw/legacy_obsoleto_no_usar` queda fuera del flujo. **Verificado:** 4 ficheros, correctamente excluidos por productor y uploader.
- Procesados en HDFS: el spec desplegado lo deja en SHOULD por decisión firmada. **Esto no cambia la rúbrica:** el 10 de HDFS exige originales **y** procesados.

---

## 2. Veredicto preliminar de rúbrica (evidencia ya medida)

| Criterio | Nota preliminar | Evidencia medida | Qué falta para el 10 |
|---|---|---|---|
| BDA · Extracción Python | **10 provisional** | `extract/` con clientes API y scrapers (auditoría 2026-11-06: 41 `.py`); re-verificar con `main()→0` y raw generado | Confirmar en fase F5 que hay ≥1 API y ≥1 scraping con log y sidecar |
| BDA · HDFS | **7** | Solo `raw` en HDFS; SHA local==remoto y 154.205 B en `alquiler_municipal.json`; base HDFS = `['raw']` (no existe `procesado`) | Subir `data/procesado` a ruta separada y demostrar recuperación con SHA/tamaño |
| BDA · Kafka | **7** | Productor real (offsets vivos) y grupo `hdfs_vm` con LAG 0; **pero** `storage/kafka_hdfs_uploader.py` no consume Kafka (ver P1-1) | Consumidor Python desplegado que realmente lea el topic, descarte y aborte por SHA |
| BDA · Integración | **7** | Cadena Windows→Kafka→VM→HDFS viva y con SHA igual; el flujo **no termina en MongoDB** | Demostrar el flujo completo hasta MongoDB (o justificarlo por escrito y asumir el 7) |
| SBD · Integración de fuentes | **10** | `anuncios` 759 (83 códigos, 83/83 con match), `alquiler_municipal` 252 (252/252 con match), `municipios` 252; campo común = código INE de 5 dígitos | Nada funcional; sí homogeneizar el nombre del campo (ver P2-3) |
| SBD · Construcción del conjunto | **10 provisional** | 27 colecciones, `anuncios.ubicacion` anidado, `historico_precios` array; relaciones por `_id`/`codigo_ine` | Confirmar en F4 que ≥1 relación está demostrada con consulta reproducible |
| SBD · Limpieza PyMongo | **PENDIENTE** | `load_mongo.py` + `clean_mongo.py` existen; hay que contar operaciones reales | Verificar ≥4 operaciones distintas (nulos, duplicados, tipos, formato) |
| SBD · Automatización | **PENDIENTE** | `transform/run_all.py`, `analysis/run_analisis_mongo.py` | Verificar ejecución sin pasos manuales y con logs |

**Lectura honesta:** si la entrega se defiende hoy, el bloque HDFS/Kafka/Integración está en **7/10 en cada criterio**, no en 10. El 10 de SBD-RA1 Integración de fuentes sí está acreditado. La nota global no es "todo 10".

---

## 3. Discrepancias spec desplegado vs delta (a auditar)

| # | Hallazgo | Evidencia | Impacto |
|---|---|---|---|
| S1 | Cabecera del spec dice `Gate extremo a extremo PASS`, pero el texto de INTEGRACION-01 dice que el flujo en vivo "queda en SHOULD porque hoy la integración está no encadenada (gate pendiente)" | `openspec/specs/almacenamiento-y-streaming/spec.md:4` vs `:100-107` | Contradicción interna; un evaluador puede leer lo segundo |
| S2 | El spec desplegado conserva escenarios viejos de KAFKA-01: "lo inserta en MongoDB" y "no duplica" | `spec.md:78-96` | Contradice el flujo nuevo "el consumidor VM NO escribe en Mongo" |
| S3 | El delta exige consumidor que descarte mensajes sin `type:"raw_manifest"` y aborte por mismatch SHA; el código desplegado no lo hace | delta KAFKA-01 vs `storage/kafka_hdfs_uploader.py:47-73` | Requisito SHALL incumplido por el artefacto |
| S4 | El delta exige estado resumible `hdfs_upload_raw.json` en la VM; en la VM no existe `~/bigdata_hdfs_vm/data/_hdfs_state/` | `ls` en VM, exit 2 | HDFS-01 "estado resumible" no acreditado en la VM |
| S5 | El spec desplegado mezcla "Planificación" nueva con Requirements viejos sin reconciliar | `spec.md:30-36` | Deuda documental que la auditoría debe resolver antes de defender |

---

## 4. Fases de la auditoría (orden de ejecución)

### F0 · Acceso y baseline (30 min)
- Confirmar SSH, Kafka, WebHDFS y Mongo (ya ejecutado, repetir al inicio por si cambia).
- `git status --porcelain`, `git log --oneline -5`, conteo de tests (`pytest --collect-only -q`).
- **Criterio de salida:** tabla de acceso con fecha/hora y PID del broker.

### F1 · Specs vs realidad (1 h)
- Leer delta archivado y spec desplegado; marcar cada SHALL y comprobar si el artefacto que lo implementa existe y hace lo que dice.
- Checklist mínimo: `HDFS-01`, `KAFKA-01`, `INTEGRACION-01`.
- **Criterio de salida:** matriz requisito → fichero:línea → ¿cumple? → evidencia.

### F2 · HDFS (1,5 h)
- `LISTSTATUS` recursivo de `/data/raw` y comparación con `find data/raw -type f` (352 sin legacy).
- Verificar 3 ficheros por muestreo (pequeño, mediano, >100 MB) con SHA local vs WebHDFS.
- Comprobar si existe `procesado` y, si no, registrar el 7 con evidencia.
- Comprobar cuota/espacio y `replication=3`.
- **Criterio de salida:** `N local == N HDFS`, `SHA 3/3`, `procesado` sí/no.

### F3 · Kafka (1,5 h)
- `kafka-topics --describe`, `--all-groups --describe`, `kafka-get-offsets`.
- Leer `storage/kafka_raw_producer.py` y `storage/kafka_hdfs_uploader.py`; probar el consumidor con un topic de prueba **sin escribir en HDFS** (dry-run o mock).
- Verificar descarte de mensaje sin `type` y aborto por SHA alterado.
- **Criterio de salida:** productor publica, consumidor consume, descarte y aborto probados; LAG 0.

### F4 · Mongo e integración (1,5 h)
- Repetir los joins medidos: `anuncios.ubicacion.codigo_ine` → `municipios._id` (83/83) y `alquiler_municipal.codigo_ine` → `municipios._id` (252/252).
- Contar operaciones de limpieza en `load_mongo.py`/`clean_mongo.py` (nulos, duplicados, tipos, formato) para el 10 de PyMongo.
- Comprobar que el flujo `gate` termina en Mongo o solo en HDFS.
- **Criterio de salida:** 2+ fuentes relacionadas demostradas con `$lookup` reproducible; veredicto Integración 7 vs 10.

### F5 · Extracción y transformación (1 h)
- `extract/`: ≥1 cliente API (`Cliente.get`) y ≥1 scraper (`html_fotocasa/` o equivalente), cada uno con `main()→0` y raw/sidecar.
- `transform/run_all.py --check`: nodos sin declarar, escritores in-place, huérfanos.
- **Criterio de salida:** API + scraping acreditados; DAG sin huecos.

### F6 · Sobrantes, documentación y reproducibilidad (1 h)
- Inventario de ficheros sobrantes (ver §5).
- Deriva documental: 134 vs 136 tests, 356/352, README que cita `storage/kafka_consumer.py` inexistente.
- Reproducir el gate desde cero en un entorno limpio (o declarar por qué no es reproducible).
- **Criterio de salida:** lista P1/P2/P3 cerrada y verificable.

### F7 · Seguridad y secretos (30 min)
- `git ls-files | grep -iE "\.env$|api.txt"` debe estar vacío salvo `.env.example`.
- Buscar credenciales hardcodeadas, IPs internas como defaults, `MONGO_ALLOW_DESTRUCTIVE` sin gate.
- **Criterio de salida:** 0 secretos versionados; riesgos de destructive documentados.

---

## 5. Inventario de sobrantes y faltantes (medido)

### 5.1 Sobrantes

| Elemento | Evidencia | Acción propuesta |
|---|---|---|
| `brief/.~lock.Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx#` | `git status` untracked; `git check-ignore` → NO_IGNORADO | Añadir `brief/.~lock.*` a `.gitignore` y borrar el lock |
| `archive/kafka_2026-11-06/` | Duplica productor, consumidor y gate viejos | Mantener como archivo histórico, no como código vivo |
| 13 colecciones `*__backup` en Mongo | `list_collection_names()` | Decidir si se conservan para defensa o se limpian |
| `storage/kafka_hdfs_uploader.py:56-60` | Bloque `if False`, variable `res` muerta, `sample` sin usar | Refactor o eliminación en el plan de reparación |
| `.audit_tmp/` (generado por esta auditoría) | `git status` | Borrar al cerrar la auditoría |

### 5.2 Faltantes

| Elemento | Evidencia | Impacto |
|---|---|---|
| Consumidor Kafka real en la VM | `ls ~/bigdata_hdfs_vm/*consumer*` → no existe; `upload()` no consume | P1: KAFKA-01 no reproducible |
| `storage/kafka_consumer.py` | Archivado; README:264 lo cita como vivo | Documentación engañosa |
| `data/procesado` en HDFS | `LISTSTATUS` base = `['raw']` | HDFS se queda en 7 |
| Estado `hdfs_upload_raw.json` en VM | No existe el directorio de estado | HDFS-01 resumible no acreditado |
| `KAFKA_BOOTSTRAP_SERVERS` y `STAGING_RAW` en `.env.example` | Código los usa; el template no los declara | Configuración incompleta |
| `codigo_ine` explícito en `municipios` | 0 documentos con el campo; el código está en `_id` | Riesgo de que el evaluador no vea el campo común (P2) |

---

## 6. Registro de errores potenciales

| ID | Severidad | Hallazgo | Evidencia | Cómo verificarlo |
|---|---|---|---|---|
| P1-1 | **Crítico** | El uploader desplegado no consume Kafka: sube todo `~/staging/raw` y no usa `is_valid_rel`/`verify_staging` | `storage/kafka_hdfs_uploader.py:47-73`; copia VM idéntica | Ejecutar `upload()` con topic vacío: sube igual → no depende de Kafka |
| P1-2 | **Crítico** | No hay procesados en HDFS → HDFS no puede ser 10 | `LISTSTATUS` base `['raw']` | `GET .../data/procesado` → 404 |
| P1-3 | **Crítico** | El flujo demostrado termina en HDFS, no en MongoDB → Integración no puede ser 10 | spec delta INTEGRACION-01; gate sube a HDFS | Buscar en el gate cualquier escritura Mongo; no la hay |
| P1-4 | **Crítico** | El gate no es re-ejecutable tal cual: falta el consumidor y el estado resumible | VM sin consumer ni `_hdfs_state` | `python -m storage.kafka_hdfs_uploader` en VM no consume |
| P2-1 | Alto | Topic con `replication.factor=1` y `min.insync.replicas=2`: con `acks=all` el productor fallaría | `kafka-topics --describe` | Producir con `acks='all'` y observar `NotEnoughReplicas` |
| P2-2 | Alto | `upload()` lee ficheros enteros en memoria (`f.read()`), incluido el de 114 MB | `kafka_hdfs_uploader.py:66-67` | Medir RSS durante subida; riesgo en VM de 8 GB |
| P2-3 | Alto | `municipios` no expone `codigo_ine`; el join usa `_id`, pero la rúbrica habla de "campo común" | `count_documents({"codigo_ine":...})=0`; `_id` 5 dígitos 252/252 | `$lookup` con `_id` funciona; con `codigo_ine` da 0 |
| P2-4 | Alto | `next(staging.rglob("*"))` sin `if f.is_file()`: puede devolver un directorio o lanzar `StopIteration` | `kafka_hdfs_uploader.py:69` | Ejecutar con staging vacío |
| P2-5 | Alto | Spec desplegado contradictorio (PASS vs "gate pendiente"; escenarios viejos de Mongo) | `spec.md:4`, `:78-96`, `:100-107` | Lectura literal |
| P3-1 | Medio | Deriva de conteos: 134 tests hoy vs 136 en auditoría previa; 356/352 raw | `pytest --collect-only` = 134 | Repetir conteo y fijar el número |
| P3-2 | Medio | README cita `storage/kafka_consumer.py` que ya no existe | `README.md:264`; `ls storage/` | `test -f` |
| P3-3 | Medio | Lock de Word sin ignorar | `git check-ignore` | `git status` |
| P3-4 | Medio | `MONGO_ALLOW_DESTRUCTIVE` solo por convención, sin gate en código | `storage/clean_mongo.py` | Grep del env y ejecución de `clean_mongo` |
| P3-5 | Bajo | IPs internas como defaults en código | `hdfs_utils.py`, `kafka_raw_producer.py` | Grep de `192.168`/`10.22` |

---

## 7. Entregables de la auditoría

1. **Este plan** (`openspec/audit/plan_auditoria_2026-11-06.md`).
2. **Informe de auditoría** con la matriz de rúbrica final (0/3/7/10 + evidencia) y los P1/P2/P3 confirmados o descartados.
3. **Anexo de evidencia en vivo**: salidas literales de SSH, `kafka-topics`, `LISTSTATUS`, `sha256sum`, `$lookup` y `pytest`.
4. **Plan quirúrgico de reparación** (fichero → cambio → esfuerzo → riesgo → verificación), separado del informe y sin ejecutar hasta aprobación.

## 8. Criterios de cierre (GATE de la auditoría)

- [ ] Acceso a VM/HDFS/Mongo re-verificado al inicio y al final.
- [ ] Cada criterio de rúbrica con nota y evidencia `comando + número + fichero:línea`.
- [ ] 100 % de los SHALL del delta comprobados uno a uno (cumple / no cumple / no verificable).
- [ ] Inventario de sobrantes y faltantes cerrado.
- [ ] Ningún P1 sin veredicto (confirmado o descartado con prueba).
- [ ] Cero modificaciones en `data/`, código o VM durante la auditoría.

## 9. Reglas de la auditoría (no negociables)

1. **No tocar** `data/raw` ni regenerar silver.
2. **No escribir** en HDFS, Kafka ni Mongo durante la auditoría; las pruebas de consumidor van con topic de prueba o mock.
3. **Nada de "parece correcto"**: todo hallazgo lleva comando y número.
4. **La rúbrica manda** sobre el spec: el spec puede declarar excepciones, la nota no.
5. **Si un requisito no es reproducible en vivo, se declara** y se puntúa por la evidencia disponible, nunca por la intención.
