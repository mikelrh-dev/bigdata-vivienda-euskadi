# Matriz del cambio VPO sin staging — v8

**Cambio:** `openspec/changes/2026-11-09-vpo-sin-staging/`  
**Baseline:** `HEAD=47065f699b5c71244a3d2439c2a74cfb74790a42`  
**Veredicto:** PASS técnico; sin regresión de datos.

## 1. Antes / después

| Elemento | Antes | Después |
|---|---|---|
| Descarga | `descargar() -> Path`, escribía `data/staging/vpo/indicator.csv` | `descargar() -> bytes`, sin escritura intermedia |
| Validación | `validar(path: Path)` leía el CSV de staging | `validar(payload: bytes)` lee en memoria |
| Promoción | `promover(origen: Path)` + `shutil.copyfile` | `promover(payload: bytes)` + `RAW_CSV.write_bytes` |
| Idempotencia | No existía no-op por SHA | Mismo SHA = `(ruta, False)` y no toca mtime; SHA distinto = abort |
| Raw ausente | Copiaba staging al raw | `assert_raw_writable` + write; devuelve `(ruta, True)` |
| CLI sin red | `--sin-descargar` leía staging | `--desde-raw` (alias `--sin-descargar`) lee el raw |
| `--promote` + `--desde-raw` | No aplicaba | Aborta explícitamente |
| Staging | `data/staging/vpo/indicator.csv` y entrada en `.gitignore` | Directorio eliminado; `.gitignore` sin entrada |

Cambios tracked: `.gitignore`, `extract/26_vpo_terminadas.py` y cuatro documentos de `openspec/changes/2026-11-05-cierre-suficiencia-auditoria/`.

## 2. Impacto por área

| Área | Evidencia | Resultado |
|---|---|---|
| Raw local | 35.427 B; SHA `70a2937a…1294706`; mtime `1793914427304130000` | Sin cambios |
| Manifest | 354 líneas; contiene el SHA del raw | Sin cambios |
| HDFS | `GETFILESTATUS` 200; `OPEN` 35.427 B; SHA idéntico; `fileCount=352` | Sin cambios |
| HDFS procesado | `GETCONTENTSUMMARY` 404 | Sin cambios; gap C2 |
| Downstream | `limpiar_vpo_municipal.py` en temp: 252 filas, 51.904 B, SHA `cfff40fe…484ce87` | Idéntico a producción |
| Mongo | `vpo_municipal` 252; 251 con dato; Usansolo sin dato | Sin cambios |
| Agregación | `pipeline_vpo_terminadas` -> 251 filas | Sin cambios |
| Kafka | 352 end offsets; 352 committed; lag 0 | Sin cambios; no depende de staging |
| Tests | 238 colectados; 236 passed; 2 skipped; focal VPO/raw 15 passed | Verde |
| Gates | `gate_extremo_a_extremo --offline` 0; `run_all --check` 0; gobernanza OK | Verde |
| `verificar_fase_datos` | Exit 1 por FAIL 07 conocido (paro-cero) | Ajeno al cambio |

## 3. Matriz de riesgo residual

| Riesgo | Probabilidad | Impacto | Mitigación actual | Estado |
|---|---|---|---|---|
| `promover()` con CSV ausente y marcador presente no regenera manifest | Baja (raw existe) | Alto si se recupera el CSV desde cero: `test_raw_inmutable` falla y HDFS queda viejo | La verificación prueba el write, pero no el manifest | **Abierto (H-08, P2)** |
| Se pierde `data/raw` completa (o `.FROZEN`) y el contrato dice que el marcador no es control | Baja | Bloquea la lista blanca y la recuperación total: `--promote` aborta antes de escribir | `_raw_guard` lanza `RawFrozenMissing`; el test de raw ausente conserva el marcador | **Abierto (H-09, P2)** |
| `validar()` acepta 252 códigos arbitrarios | Baja (raw ya existe) | Si no existiera raw, podría promover códigos fuera de `dim_municipios` | El parser posterior filtra a 252; no hay check en `validar` | **Abierto (H-10, P3)** |
| Documentación con cifras previas | Alta | Defensa incoherente | README y AGENT parcialmente actualizados; modelo/guiones no | **Abierto (H-02…H-07, P2)** |
| `data/procesado` 404 | Cierta | C2 = 7/10 | Excepción declarada con la profesora | **Waiver (H-01, P1)** |

## 4. Pruebas del cambio reproducidas

- `validar(raw)` = `(272, 0.0, 62.55)`.
- `promover(raw)` con el mismo SHA = `(ruta, False)`; SHA y mtime intactos.
- `promover(payload_distinto)` aborta con “raw inmutable”; el raw no cambia.
- `promover(payload)` con CSV ausente y `.FROZEN` presente en temp escribe 35.427 B y devuelve `True`; con el marcador ausente aborta.
- `--desde-raw` y `--sin-descargar` return 0.
- `--desde-raw --promote` aborta.
- Raw ausente con `--desde-raw` aborta.
- Descarga real devuelve el mismo SHA.
- No se crea `data/staging/` en ninguna rama.
- `rg "data/staging"` en código solo encuentra un comentario de `storage/kafka_raw_producer.py` sobre `~/staging/raw` de la VM, que **no** es el staging local del VPO.

## 5. Conclusión

El cambio cumple su objetivo: elimina un fichero intermedio sin cambiar bytes, sin tocar HDFS y sin alterar el silver. La deuda funcional es doble: el camino “CSV ausente con marcador” no regenera manifest, y la pérdida total de `data/raw` no se puede recuperar con `--promote` sin recrear `.FROZEN`. No afecta al estado actual porque el raw existe y el mismo SHA es no-op.
