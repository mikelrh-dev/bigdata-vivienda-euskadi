# Informe de auditoría v7 — 2026-11-09

## Veredicto

**APTO CON UNA RESERVA: 187 / 190 (98,4 %).**

- BDA RA1: **37/40** — HDFS se queda en 7 por no tener procesados en el clúster.
- SBD RA1: **40/40**.
- SBD RA3: **60/60**.
- SBD RA4: **50/50**.

No hay P0. Hay **1 P1** (HDFS procesados) y varios P2/P3 de documentación desfasada. La reserva es de rúbrica, no de integridad: los datos, la cadena y los tests están vivos y reproducen.

## Qué se ha ejecutado (no heredado)

| Comprobación | Resultado |
|---|---|
| `pytest tests -q` | 238 colectados, 2 skipped, 0 failed, exit 0 |
| `verificar_gobernanza.py` | TODO OK: 46 requisitos, 45/34 scripts, 188 silver, 0 env, 11 pipelines |
| `run_all.py --check` | exit 0 (34/34) |
| `gate_extremo_a_extremo.py --offline` | OK: 354 raw, 188 silver, 14 colecciones, 0 duplicados, lag 0 |
| `verificar_fase_datos.py` | exit 1: FAIL 07 conocido (paro-cero Aramaio/Gaintza/Usansolo) |
| Mongo | 30 colecciones; 594 anuncios; 252 municipios; 252 alquiler; 252 VPO |
| 11 pipelines | 11/11 ejecutan en lectura (limit 2) y devuelven claves esperadas |
| HDFS | 352 ficheros raw, 6 directorios, 895,6 MB; lectura real de un CSV; `procesado` 404 |
| Kafka | topic `vivienda_euskadi` 1P/1R; offsets 0→352; grupo `hdfs_centro` committed 352; lag 0 |
| `explain` | `IXSCAN` 8 docs examinados vs `COLLSCAN` 594 |
| Funciones | 814 inventariadas; 298 del camino crítico revisadas; 280 tests auditados; 236 clasificadas estáticamente |
| Escrituras en `data/` | 0 ficheros nuevos hoy; solo se creó `openspec/audit/v7_2026-11-09/` |

## Las 5 conclusiones que importan

### 1. El proyecto cumple 18 de 19 criterios al nivel de 10
La extracción combina API y scraping; hay 16 colecciones vivas y la relación `anuncios → municipios` casa 594/594 por `codigo_ine`; la limpieza tiene exactamente las 4 operaciones que pide la rúbrica (canonización, nulos, duplicados, tipos); el CRUD está demostrado con asserts; hay 30 consultas y 11 pipelines con `$lookup`, `$unwind` y `$group`; el `explain` es real; la atomicidad está probada y justificada; y hay 5 indicadores con 4 municipios comparados.

### 2. HDFS es el único criterio que no llega al 10
La rúbrica del 10 exige «organiza originales **y** procesados y demuestra su recuperación». En el clúster hay **352 ficheros raw** y se recuperan por WebHDFS, pero `data/procesado` devuelve **404**. Además, `scripts/upload_procesado.py:62` **rechaza subir** sin `--dry-run`: es un script de lista, no de subida. Eso es 7/10 (guarda y recupera) con salvedad, no 10.

### 3. Kafka sí está vivo, no solo en tests
El topic `vivienda_euskadi` existe con 1 partición y 1 réplica; hay **352 mensajes** (coinciden con los 352 ficheros raw) y el grupo `hdfs_centro` tiene **committed 352**, es decir, el consumidor procesó todo y el lag es 0. No se re-ejecutó el productor para no mutar el topic; la evidencia es el estado real del clúster más el código y los tests.

### 4. El `explain` demuestra el índice, pero el README exagera
Medido: sin índice, `COLLSCAN` examina **594** documentos; con el índice ESR, `IXSCAN` examina **8**. El README dice «IXSCAN 1». El criterio se cumple igual (compara, identifica etapas y `totalDocsExamined`), pero la cifra «1» no se reproduce con el filtro probado: es un P3 de documentación.

### 5. La documentación va por detrás del código
Hay desfases que no cambian la nota pero sí la defensa:
- `docs/modelo_mongodb.md` dice **759 anuncios**, **14 colecciones + 13 backups** y **10 pipelines**; hoy son **594**, **16 vivas + 14 backups** y **11**.
- El mismo documento da la comparativa como **Bilbao 173 / Donostia 113 / Getxo 40**; el CSV real da **204 / 126 / 50 / 39**.
- El README dice `IXSCAN 1` y el modelo `totalDocsExamined=759`; la medición real es **8 examinados sobre 594**.
- `run_analisis_mongo.py` se describe en el CLI como «9 pipelines + 5 CSV»; hace **11 + 8**.
- `clean_mongo.py` docstring dice «759 en prod»; hoy son **594**.

## Puntos fuertes defendibles

1. **Trazabilidad real**: `codigo_ine` une 594 anuncios con 252 municipios; el `$lookup` da 594/594 con match.
2. **Limpieza honesta**: no solo borra; marca nulos como `missing`, resuelve duplicados por `(portal,id_anuncio)` y por `property_fingerprint`, y convierte tipos con `$convert`.
3. **Reproducibilidad**: el orquestador ejecuta los pipelines dos veces y compara huella; los tests fijan 594 anuncios y 252 municipios.
4. **Consistencia bien resuelta**: en standalone no se fuerza una transacción; se demuestra atomicidad documental con `find_one_and_update` y se justifica por qué una transacción multi-documento no hace falta.
5. **Indicadores con fuente**: cada uno tiene fórmula, fuente y limitación declarada; no hay valores inventados.

## Qué haría falta para el 10 en HDFS

| Opción | Efecto | Requisito |
|---|---|---|
| Subir `data/procesado` a HDFS y recuperar un fichero | C2 → 10 | Autorización de escritura en HDFS y de la profesora; hoy `upload_procesado.py` no sube, habría que añadir la vía real |
| Waiver escrito de la profesora aceptando «solo raw» | C2 se queda en 7, pero pasa a `CUMPLE CON SALVEDAD` defendible | Documento firmado; no cambia la nota literal |
| No hacer nada | 187/190 con reserva | Es la situación actual |

## Límites de esta auditoría

- **No se re-ejecutó el productor Kafka** (habría escrito mensajes) ni `run_analisis_mongo.py` completo (habría reescrito `data/resultados`). Se ejecutaron los 11 pipelines en lectura y se verificaron los 8 CSV existentes.
- **No se ejecutó `load_all`/`clean_all` contra producción** (mutan Mongo). Se usó `--dry-run` y los tests contra `vivienda_euskadi_test`.
- **PDF**: `pdfplumber` no está instalado; se extrajo con `pypdf` (6 páginas, 8.394 caracteres) y se cotejó con `openspec/specs/contrato-reto/spec.md`.
- **Cobertura función a función**: 814 funciones inventariadas; 298 del camino crítico leídas en profundidad; 280 tests auditados por asserts; 236 funciones de soporte clasificadas estáticamente. No se ha hecho lectura semántica línea a línea de las 22.911 líneas.
- **Mongo**: una sola foto; los conteos se mantuvieron estables (594/252) durante la sesión.
- **Infra viva**: HDFS y Kafka respondieron; no se probó escritura en HDFS ni producción de mensajes.

## Evidencia

- `evidencia/pytest.txt`, `pytest_collect.txt`, `gobernanza.txt`, `staleness.txt`, `gate_offline.txt`, `fase_datos.txt`
- `evidencia/mongo_snapshot.json`, `pipelines_live.json`, `queries_live.json`
- `evidencia/hdfs_live.json`, `hdfs_summary.json`
- `evidencia/kafka_live.json`, `kafka_offsets.json`
- `evidencia/infra_probe.json`, `rubrica_pdf.txt`, `tema8_docx.txt`
- `inventario_funciones.csv` (814 filas)
- `matriz_rubrica_v7.md`, `hallazgos_v7.csv`
