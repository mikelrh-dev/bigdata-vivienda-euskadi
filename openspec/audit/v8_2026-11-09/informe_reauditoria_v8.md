# Reauditoría v8 — bigdata-vivienda-euskadi

**Fecha:** 2026-11-09  
**Alcance:** reauditoría completa tras eliminar `data/staging/` del flujo VPO. Solo análisis: no se ha modificado código, datos, Mongo, HDFS ni Kafka.  
**Baseline:** `HEAD=47065f699b5c71244a3d2439c2a74cfb74790a42`, rama `master`, 6 ficheros tracked modificados y el cambio `2026-11-09-vpo-sin-staging/` sin commit.  
**Inventario:** 1.482 ficheros, 1,18 GB; 625 tracked y 857 no tracked. 193 `.py`, 432 `.md`, 317 `.json`, 115 `.html`, 49 `.zip`.

## Veredicto

- **Cambio VPO sin staging: PASS técnico.** No hay ninguna escritura en `data/staging/`, el raw local conserva bytes, SHA y mtime, HDFS conserva el mismo objeto y el downstream produce exactamente el mismo silver.
- **Auditoría global: 187/190 (98,4 %).** Se mantiene el baseline v7. El único criterio por debajo de 10 es **C2 HDFS = 7/10** por `data/procesado` 404, ya cubierto por la excepción declarada con la profesora.
- **No hay P0.** Hay **1 P1 conocido** (H-01, HDFS procesado), **8 P2** (deuda documental y dos gaps latentes) y **4 P3** de higiene.
- **No hay regresión de código introducida por el cambio VPO.** Los dos gaps latentes importantes son: (a) `promover()` con el CSV ausente y `.FROZEN` presente escribe el CSV pero no regenera el manifest; (b) si se pierde `data/raw` completa, el guard aborta por falta de `.FROZEN`, y el contrato además dice que ese marcador ya no controla.
- **Riesgo principal para la defensa:** la documentación activa sigue mezclando cifras de antes y después del cambio (759/594, 14+13/16+14, 10/11 pipelines, 4/5/8 CSV, 173/204, IXSCAN 1/68). El código y los datos son correctos; los documentos no.

## 1. Qué cambió el cambio VPO

| Fichero | Antes | Después |
|---|---|---|
| `extract/26_vpo_terminadas.py` | Descargaba a `data/staging/vpo/indicator.csv`, validaba el fichero y copiaba con `shutil.copyfile` | Descarga en memoria (`bytes`), valida en memoria y escribe el raw solo con `--promote` |
| `.gitignore` | Ignoraba `data/staging/` | Sin entrada; `data/staging/` eliminado |
| `promover()` | Recibía una ruta de staging | Recibe el payload; mismo SHA = no-op, SHA distinto = abort, CSV ausente + marcador = guard + write, pérdida total = abort |
| CLI | `--sin-descargar` leía staging | `--desde-raw` (alias `--sin-descargar`) lee el raw existente |
| Tests | No había prueba de pérdida total | La verificación prueba CSV ausente en `tempfile`, pero conserva `.FROZEN` |

El cambio **no** toca el parser downstream, el manifest ni HDFS. Es una simplificación del transporte intermedio, no un cambio de contrato de datos.

## 2. Evidencia de datos e infraestructura

### Raw local

| Comprobación | Resultado |
|---|---|
| Fichero | `data/raw/udalmap_vpo_terminadas.csv` |
| Tamaño | 35.427 B |
| SHA-256 | `70a2937a3026b01c5e73ff641241c2fad0a77c3b995d2863034fba2da1294706` |
| mtime | `1793914427304130000` (sin cambios) |
| Manifest | 354 líneas; contiene exactamente el mismo SHA |
| Ficheros raw | 356 (excluye `.FROZEN` y `.gitkeep`) |
| `data/staging` | No existe |

### HDFS

| Comprobación | Resultado |
|---|---|
| `GETFILESTATUS` raw | 200; `length=35427` |
| `OPEN` raw | 35.427 B; SHA idéntico al local |
| `GETCONTENTSUMMARY` raw | `fileCount=352`, `directoryCount=6` |
| `data/procesado` | **404 FileNotFoundException** |

El SHA es la comparación correcta. El `modificationTime` de HDFS (`1794238191317`) es el de la subida, no el mtime local; no se usa como igualdad de contenido.

### Kafka

| Comprobación | Resultado |
|---|---|
| Broker | `10.22.87.215:9092`, topic `vivienda_euskadi` |
| Particiones | 1 |
| Beginning offset | 0 |
| End offset | **352** |
| Grupo `hdfs_centro` committed | **352** |
| Lag | **0** |

La sonda fue read-only: no produjo, no consumió mensajes y no hizo commit.

### MongoDB

| Comprobación | Resultado |
|---|---|
| Colecciones totales | 30 (16 vivas + 14 `__backup`) |
| `anuncios` | 594 |
| `vpo_municipal` | 252 documentos; 251 con dato; Usansolo sin dato |
| Índice ESR | `idx_anuncios_ine_modalidad_precio` presente |
| `explain` de la consulta de Bilbao (`48020`, larga estancia, precio > 0) | `IXSCAN`; **68 examinados / 68 devueltos** |
| `mongo_vpo_terminadas_por_municipio.csv` | 251 filas de datos |
| `comparativa_3_municipios_mongo.csv` | Bilbao 204, Donostia 126, Getxo 50, Vitoria-Gasteiz 39 |

## 3. Impacto del cambio VPO, fichero a fichero

| Área | Ficheros | Efecto verificado |
|---|---|---|
| Extractor | `extract/26_vpo_terminadas.py` | Sin staging; `validar(bytes)`; `promover(payload)`; `--desde-raw`; no escribe raw sin `--promote` |
| Ignore | `.gitignore` | Ya no ignora staging; no hay directorio que ignorar |
| Downstream | `transform/limpiar_vpo_municipal.py` | 252 filas, 51.904 B, SHA `cfff40fefd0fbf87565136b0c44471c6f9ddfb9465905adc1594b1ea2484ce87`, idéntico a producción |
| Carga | `storage/load_mongo.py` | No depende de staging; `vpo_municipal` sigue en 252/251 |
| Agregación | `analysis/mongo_aggregations.py` | `pipeline_vpo_terminadas` no lee staging; el CSV sigue en 251 filas |
| HDFS | `data/raw` remoto | 352 ficheros; el CSV VPO conserva SHA; `data/procesado` sigue 404 |
| Kafka | `storage/kafka_raw_producer.py`, `kafka_hdfs_uploader.py` | 352/352, lag 0; no hay dependencia del staging VPO |
| Tests | `tests/` | 238 colectados; 236 passed, 2 skipped; focal VPO/raw 15 passed |
| Gate | `scripts/gate_extremo_a_extremo.py --offline` | OK: 354 SHA + 188 silver + 14 nombres + 0 duplicados + lag 0 |
| Gobernanza | `scripts/verificar_gobernanza.py` | TODO OK: 46 requisitos, 45 scripts/34 DAG, 11 pipelines |
| Staleness | `transform/run_all.py --check` | 34/34 OK |
| Fase de datos | `scripts/verificar_fase_datos.py` | Exit 1 solo por FAIL 07 conocido; no es del cambio VPO |

**Conclusión:** el cambio elimina un intermediario sin alterar el contrato de bytes. No rompe la inmutabilidad del raw ni la copia HDFS. El efecto lateral es que el camino “CSV ausente con marcador” no regenera manifest; si falta el directorio completo, no se puede reconstruir sin recrear `.FROZEN`.

## 4. Hallazgos priorizados

| ID | Sev. | Tema | Hallazgo | Impacto | Acción propuesta |
|---|---|---|---|---|---|
| H-01 | **P1** | C2 HDFS | `data/procesado` devuelve 404 y el script de subida solo hace `--dry-run` | C2 = 7/10; se sostiene solo por la excepción declarada | Subir procesado o formalizar waiver escrito |
| H-02 | P2 | C9/C12 | `docs/modelo_mongodb.md` sigue con 759 anuncios, 14+13 colecciones, 424/759 geo, 10 pipelines, 5 CSV, 173/113/40 y explain 759/1 | Riesgo directo de defensa; no baja el criterio | Actualizar el modelo a 594, 16+14, 11 pipelines, 8 CSV, 204/126/50/39 y 68/68 |
| H-03 | P2 | C13 | `IXSCAN 1` aparece en `README.md`, `AGENT.md`, `docs/arquitectura_datos.md`, `docs/guion_defensa.md`, `docs/guion_defensa_12min.md` y `docs/modelo_mongodb.md` | El índice funciona, pero la cifra reproducible actual es 68/68 para la consulta de Bilbao | Sustituir por la medición actual y explicar que el número depende del filtro |
| H-04 | P2 | C12/C16/C19 | Documentos activos mezclan 10/9 pipelines con 11, 4/5/6 CSV con 8 y 14+13 con 16+14 | Defensa inconsistente; los datos no cambian | Corregir `docs/matriz_indicadores.md`, `docs/informe_final.md`, `docs/informe_capacidad_mongo.md`, `docs/preguntas_analisis_profesional.md`, `docs/guion_defensa_12min.md` |
| H-05 | P2 | C18 | La comparativa documentada sigue en Bilbao 173 / Donostia 113 / Getxo 40 / Vitoria 39 | La conclusión vigente es 204/126/50/39; riesgo de citar cifras falsas | Actualizar tabla y texto de comparativa |
| H-06 | P2 | C19 | `docs/README.md` afirma que la única evidencia RA4 válida son 4 CSV; `README.md` y `EXPORTS_8` dicen 8 | El índice oculta 4 evidencias que sí existen | Actualizar el índice a los 8 `mongo_*` |
| H-07 | P2 | Contexto | `openspec/project.md` sigue con 136 tests, 185 silver, 9 pipelines, 5 CSV, 759 anuncios y “VM/gate pendiente” | `AGENT.md` lo usa como detalle; un evaluador puede leer el estado antiguo | Actualizar o marcar como histórico con fecha |
| H-08 | P2 | C1/C2 | `promover()` con CSV ausente y `.FROZEN` presente escribe el CSV pero no regenera `docs/raw_manifest_sha256.txt`; no hay llamada a `extract/generar_manifest.py`. Si falta el directorio/marcador, aborta antes de escribir | Si se recupera el CSV desde cero, `test_raw_inmutable` falla y HDFS queda desalineado | Llamar a `generar_manifest --write` tras una escritura nueva o añadir test que lo exija |
| H-09 | P2 | C1 | `docs/contrato_datos_raw.md` dice que `.FROZEN` “ya no es un mecanismo de control”, pero `_raw_guard.assert_raw_writable` lanza `RawFrozenMissing` si falta; el test de raw ausente conserva el marcador. Si se pierde `data/raw` completa, `--promote` no reconstruye | Recuperación total bloqueada; contradicción contrato/código | Alinear contrato y guard y probar la pérdida total del directorio |
| H-10 | P3 | C1 | `validar()` solo exige 252 códigos de 5 dígitos y valores 0–100; no comprueba pertenencia a `dim_municipios` | Un payload con 252 códigos arbitrarios pasa; el parser posterior los descarta, pero el raw podría quedar contaminado si no existiera | Validar contra los 252 códigos de `dim_municipios` o contra el conjunto vivo |
| H-11 | P3 | C16 | El argparse de `analysis/run_analisis_mongo.py` dice “9 pipelines + 5 CSV”; ejecuta 11 + 8 | Higiene y riesgo de defensa | Actualizar la descripción |
| H-12 | P3 | C10 | El docstring de `storage/clean_mongo.py` cita 759 en producción; el valor vigente es 594 | Comentario obsoleto | Actualizar el comentario |
| H-13 | P3 | Estructura | `docs/archive/scratchpad/bom.json` tiene BOM y no parsea como JSON estricto | Fichero de scratchpad, no activo | Reescribir sin BOM o excluirlo del escaneo |

**Recuento:** P0 = 0; P1 = 1; P2 = 8; P3 = 4. El detalle machine-readable está en `hallazgos_v8.csv`.

## 5. Rúbrica

La reauditoría no añade criterios nuevos. Se revalidaron los 19 criterios con la evidencia viva de esta sesión:

| Bloque | Criterios | Nota |
|---|---|---:|
| BDA RA1 | 1–4 | 37/40 |
| SBD RA1 | 5–8 | 40/40 |
| SBD RA3 | 9–14 | 60/60 |
| SBD RA4 | 15–19 | 50/50 |
| **Total** | **19** | **187/190 (98,4 %)** |

El detalle está en `matriz_rubrica_v8.md`. C2 sigue en 7 por HDFS procesado; el resto en 10. La deriva documental de H-02…H-09 **no baja la nota** porque los criterios se acreditan con código, tests y datos, no con la cifra del documento; sí es riesgo de defensa.

## 6. Cobertura

Se inventariaron **1.482 ficheros**. La cobertura real fue:

- **Código:** 193 `.py`, 29.767 líneas y 960 funciones; AST/`compileall` sin errores de parseo. Revisión semántica directa de los módulos del flujo VPO, raw guard, carga, agregación y análisis.
- **Tests:** suite completa y focal VPO/raw; no se ejecutaron `load_all`, `clean_all`, `run_analisis_mongo` completo ni productor Kafka.
- **Datos:** raw y silver VPO verificados byte a byte; HDFS, Kafka y Mongo verificados en vivo; el resto de `data/` inventariado y hasheado, no abierto semánticamente.
- **Documentación:** 432 `.md`; 63 documentos activos escaneados, 253 coincidencias de cifras obsoletas, 0 enlaces internos rotos. Se leyeron en detalle los documentos de defensa, modelo, contrato, matriz y los guiones.
- **Estructura:** 317 `.json`, 205 `.csv`, 4 `.yaml`, 115 `.html`, 49 `.zip`, 46 `.png`; un único error de parseo: BOM en `docs/archive/scratchpad/bom.json`.
- **Ficheros no auditados semánticamente:** binarios, ZIP, PDF, vídeos, HTML manuales y datos históricos de `archive/`; se registran como `inventariado`/`hash_only` en `cobertura_archivos_v8.csv`.

## 7. Checks ejecutados

| Check | Resultado |
|---|---|
| `python -m compileall` | Exit 0 |
| `pytest tests -q` | Exit 0; 238 colectados, 236 passed, 2 skipped |
| `pytest` focal VPO/raw | 15 passed |
| `scripts/verificar_gobernanza.py` | TODO OK |
| `transform/run_all.py --check` | 34/34 OK; exit 0 |
| `scripts/gate_extremo_a_extremo.py --offline` | OK; exit 0 |
| `git diff --check` | Sin errores |
| `scripts/verificar_fase_datos.py` | Exit 1 solo por FAIL 07 conocido |
| CLI VPO (mismo SHA, SHA distinto, raw ausente, descarga real, `--desde-raw`, `--promote`) | Comportamiento esperado; no se creó staging |
| Downstream VPO en temp | 252 filas; SHA idéntico a producción |
| HDFS / Kafka / Mongo | Lecturas correctas; sin escrituras |

## 8. Límites de esta auditoría

- No se aplicaron fixes: los hallazgos quedan documentados, no corregidos.
- No se ejecutó `load_all`, `clean_all`, el análisis completo ni el productor Kafka; se usaron lecturas y dobles/temporales.
- La prueba de CSV ausente usó `tempfile` y conservó `.FROZEN`; no se borró ni se tocó `data/raw`.
- La pérdida total del directorio se simuló con un marcador temporal ausente; el `.FROZEN` real no se modificó.
- La sonda Kafka fue de offsets; no se consumieron mensajes ni se hizo commit.
- La documentación se escaneó por patrones; las 253 coincidencias no se revisaron una a una, pero sí los documentos activos de defensa y modelo.
- El `git status` sigue mostrando los cambios del usuario y los artefactos de auditoría; **no se hizo commit ni push**.

## 9. Recomendación

**Para el cambio VPO:** se puede dar por cerrado técnicamente. No hay razón para revertirlo ni para volver a staging.

**Antes de la defensa:** corregir primero H-02…H-07 (una sola pasada de documentación) y decidir H-08/H-09 (manifest y `.FROZEN`). H-10…H-13 pueden esperar.

**Para release:** H-01 sigue siendo el único P1 y ya tiene waiver; si no se va a subir `procesado`, conviene que el waiver esté enlazado desde el README y desde el guion, no solo en el histórico de auditoría.
