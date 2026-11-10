# Informe de auditoría estática — `extract/` (41 `.py`) · v9 2026-11-10

**Unidad:** W2.1 · **Criterios:** C1 (Extracción Python: API **y** scraping) y C15 (Datos heterogéneos adaptados)
**Naturaleza:** solo lectura. No se modificó código, datos, Mongo, HDFS ni Kafka; no hubo commit/push; no se instalaron dependencias.
**Entrada:** `extract/*.py` (41 ficheros, 6.755 líneas) · **Baseline:** `00_baseline_v9.md` · **Rúbrica:** `rubrica_reextraida.md`
**Repo:** `bigdata-vivienda-euskadi` @ `47065f6` (rama `master`), verificado con `git rev-parse` y `git status`.

---

## 1. Veredicto resumido

| Criterio | Veredicto | Nota v8 (histórico) | Cambio |
|---|---|---|---|
| **C1** Extracción Python (API y scraping) | **CUMPLE con reservas** | 10/10 | Se mantiene la automatización (41 scripts, 22 con `Cliente`, 11 con `requests` directo, `main_ingest.py` orquesta). **Reserva nueva:** la capa no es re-ejecutable sin intervención (F-01, F-02). |
| **C15** Datos heterogéneos adaptados | **CUMPLE** | 10/10 | 7 formatos (CSV, JSON, XLSX, GeoJSON, ZIP, SHP, GTFS) y normalización común (`guardar_json`, `leer_csv_seguro`, `normalizar_metadata`, `entity_resolution`). Sin hallazgos que lo tumben. |

**Hallazgo dominante:** F-01 (P1) — regresión del 2026-10-31 que hace que **20 de 41 llamadas `guardar_json` lancen `ValueError`** al escribir en `data/raw`. No se ha tocado nada.

---

## 2. Hallazgos

### F-01 · P1 · Regresión de metadatos: 20/41 `guardar_json` no pasarían la validación de raw

**Evidencia.** `extract/_common.py:199-205` eleva `ValueError` si faltan campos de `REQUIRED_METADATA` y el destino está en `raw`:

```python
faltan = [k for k in REQUIRED_METADATA if meta.get(k) in (None, "", [])]
if faltan and _es_raw(destino):
    raise ValueError(f"{destino.name}: metadata incompleta para raw, faltan {faltan}. ...")
```

`REQUIRED_METADATA` (`_common.py:172-173`) exige `fuente`, `url`, `fecha_extraccion`, `n_registros`, `hash_sha256`, `version_parser`. La validación es estricta en raw a propósito (FORMATO-01 / WP-07).

**16 llamadas definitivas** (no dependen de ninguna variable) que lanzarían:

| Fichero:línea | Defecto |
|---|---|
| `extract/03_euskadi_emancipacion.py:62` | sin argumento `metadata=` (falta `fuente` y `url`) |
| `extract/05_fotocasa_scraper.py:254` | falta `url` |
| `extract/08_pisos_scraper.py:232` | falta `url` |
| `extract/09_fotocasa_dirigido.py:101` | falta `url` |
| `extract/09_realtyapi.py:240` | falta `url` |
| `extract/10_scraping_faltantes.py:132` y `:142` | falta `url` |
| `extract/13_scraping_habitaciones.py:357` y `:402` | falta `url` |
| `extract/19_udalmap_indicadores_adicionales.py:143` | falta `url` |
| `extract/euskadi_geo.py:142` | falta `url` |
| `extract/fotocasa_detalle.py:80` y `:82` | falta `url` |
| `extract/ine_atlas_renta.py:164` y `:224` | falta `url` |
| `extract/udalmap_empleo.py:147` | falta `url` |

**4 llamadas condicionales** que heredan la metadata del fichero de entrada y también fallan con el raw vigente: `12_enriquecer_json_anidado.py:92`, `14_add_metadata_fingerprint.py:128`, `15_add_geojson.py:126`, `fotocasa_detalle.py:93`. Las entradas (`anuncios_fotocasa.json`, `anuncios_pisos.json`) carecen de `url` en su bloque `metadata` — comprobado leyendo los JSON.

**Procedencia (ejecutado):** `git blame -L 168,214 -- extract/_common.py` → `guardar_json` nació en `5166d32` (2026-10-23) sin validación; `bc6866ec` (2026-10-31, WP-07/FORMATO-01) añadió `REQUIRED_METADATA` y el `raise`. Los extractores escritos antes del 31 no se actualizaron.

**Evidencia de que no es hipotético.** Los ficheros raw existentes prueban la precedencia: `data/raw/emancipacion_juventud_resumen.json` es un **dict desnudo** (sin envoltura `{"metadata","datos"}`) y `anuncios_fotocasa.json` / `anuncios_pisos.json` tienen `metadata` sin `url`. Es decir, se generaron con la versión pre-31.

**Impacto.**
- `python extract/main_ingest.py --mode live` registraría `FAIL` en la mayoría de extractores (el orquestador aísla el fallo, pero el manifiesto quedaría lleno de `FAIL`).
- Contradice la hipótesis **H18 (reproducibilidad)** del plan y roza el falsador de **C1** («un extractor clave exija intervención manual»).
- **No hay pérdida de datos**: el raw está congelado y la metadata canónica se recupera con `extract/normalizar_metadata.py` (sidecars en `data/procesado/_meta/`, con `FUENTES_LEGACY` para `emancipacion_juventud_resumen.json` y `b5m_catalogo.json`). El defecto es de **re-ejecución**, no de integridad.

**Severidad P1** (reproducibilidad del 62 % de los puntos de escritura; no P0: sin corrupción, sin seguridad, sin datos).

---

### F-02 · P2 · Raw congelado en read-only: la re-ejecución tumbba antes por `PermissionError`

**Evidencia (ejecutado con `os.stat`/`os.access`).** De 72 destinos de escritura bajo `data/raw` declarados en los scripts, **72 existen y son read-only** (`stat.S_IWRITE=False`), 8 existen y son escrituribles, 10 no existen. P. ej. `anuncios_fotocasa.json` y `anuncios_fotocasa_detalle.json` → `S_IWRITE=False`, mtime 2026-10-29 08:48; `udalmap_vpo_terminadas.csv` → `S_IWRITE=True` (promovido el 2026-11-05, posterior al congelado).

**Consecuencia.** Al re-ejecutar, el primer `write_text`/`write_bytes`/`to_csv` sobre un fichero congelado lanza `PermissionError` **antes** de llegar a la validación de metadatos de F-01. Solo `23_certificados_energeticos.py:30-32` (salta existentes) y `26_vpo_terminadas.py:114-122` (comparación de SHA) tienen camino de re-ejecución limpio.

**Impacto.** La inmutabilidad del bronce está bien aplicada a nivel de fichero, pero el código no declara un modo «raw ya congelado, no reescribir». No es corrupción: es una segunda vía por la que la re-ejecución manual es imposible.

---

### F-03 · P2 · `_common.py` crea el árbol `data/*` relativo al *cwd* en importar

**Evidencia.** `extract/_common.py:38-44`:

```python
DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
RAW_DIR = DATA_DIR / "raw"
...
for _d in (RAW_DIR, PROCESADO_DIR, RESULTADOS_DIR):
    _d.mkdir(parents=True, exist_ok=True)
```

`DATA_DIR` es **relativo** y el `mkdir` se ejecuta en importación, sin `chdir`. **Ejecutado:** importar `_common` con cwd = scratch creó `data/raw`, `data/procesado`, `data/resultados` en el scratch. `main_ingest.py:30` hace `os.chdir(PROJECT_ROOT)`, pero los 40 demás scripts no.

**Impacto.** Cualquier extractor lanzado desde otro directorio escribe (o intenta escribir) en un `data/` paralelo fuera del repo, y `_es_raw()` (`_common.py:177-182`) deja de referirse al raw real. También crea `data/procesado` y `data/resultados` sin guard.

---

### F-04 · P2 · `main_ingest.py` escribe en `data/raw` sin `assert_raw_writable`

**Evidencia.** `extract/main_ingest.py:217-222` y `:284-289` escriben `RAW_DIR / "ingestion_manifest.json"` directamente, sin llamar a `transform/_raw_guard.py:76 assert_raw_writable`. El guard existe y se usa en `transform/enriquecer_codigo_ine.py:137`, `transform/f4_pisos_dirigido.py:59` y `extract/26_vpo_terminadas.py:127`.

**Agravante (inconsistencia entre manifestos).** `generar_manifest.py:30` excluye `ingestion_manifest.json` del inventario de raw; `generar_ingestion_manifest.py:25` **no** lo excluye. El manifiesto canónico (`docs/raw_manifest_sha256.txt`, 354 entradas) no lo contiene (verificado).

**Impacto.** El orquestador —el único punto que escribe en raw al final de una pasada— queda fuera del registro de auditoría del bronce. El manifiesto ni siquiera es una fichero de datos: es control.

---

### F-05 · P2 · `fotocasa_detalle.py` reescribe un fichero de datos del bronce (no append)

**Evidencia.** `extract/fotocasa_detalle.py:93` vuelve a escribir `RAW_DIR / "anuncios_fotocasa.json"` (fusión aditiva de campos de detalle) y `:80` lo hace cada 50 fichas. Sin `assert_raw_writable`. Es la única escritura que **mutación** un raw ya existente en lugar de crear uno nuevo.

**Impacto.** Hoy está bloqueada por el read-only (F-02). Si se descongelara el bronce, este script modificaría el original sin dejar constancia en `logs/raw_guard_audit.log`. Es el caso más cercano al falsador H3 del plan («un `open(...,"w")` sobre `data/raw` sin `assert_raw_writable`»).

---

### F-06 · P2 · `subprocess.run` sin `timeout` en el orquestador

**Evidencia.** `extract/main_ingest.py:152-157` ejecuta cada extractor con `subprocess.run([sys.executable, str(script)], cwd=..., capture_output=True, text=True)` y **sin `timeout=`**. Comprobado: la palabra `timeout` no aparece en la llamada.

**Impacto.** Un extractor que se cuelgue (red lenta, `urlretrieve` sin timeout —F-07—) bloquea `main_ingest` indefinidamente. El log queda sin la línea `▶ <script>` final ni manifiesto parcial.

---

### F-07 · P2 · `urllib.request.urlretrieve` sin timeout en 4 descargas

**Evidencia.** `urllib.request.urlretrieve` no acepta `timeout`:
- `extract/16_serpavi_renta.py:34` (XLSX ~68 MB)
- `extract/18_lanbide_paro_juvenil.py:31` (XLSX)
- `extract/22_geo_areas_funcionales.py:56` (ZIP)
- `extract/23_certificados_energeticos.py:35` (6 CSVs; además `sys.exit(1)` en el primer fallo, `:40`)

**Impacto.** Descargas grandes que pueden quedarse colgadas sin límite; en `23` un fallo aborta el lote completo. Contrasta con `ine_atlas_renta.py:93`, que sí usa `requests.get(..., timeout=300, stream=True)`.

---

### F-08 · P2 · `zipfile.extractall` sin validación de rutas (zip-slip)

**Evidencia.** `extract/22_geo_areas_funcionales.py:58-59`:

```python
with zipfile.ZipFile(ZIP_PATH) as z:
    z.extractall(EXTRACT_DIR)
```

El ZIP viene de una URL externa (`:22`). No se comprueba que los miembros permanezcan dentro de `EXTRACT_DIR`. También escribe en `Path(tempfile.gettempdir()) / "geo_areas"` (`:18`), directorio fijo compartido (colisión entre ejecuciones concurrentes).

**Impacto.** Vulnerabilidad de path traversal de baja explotabilidad (fuente institucional `geo.euskadi.eus`, no se verifica la firma del ZIP). Relevancia real baja, pero es el patrón que `security-and-hardening` marca como «nunca `extractall` sobre entrada externa».

---

### F-09 · P2 · Escrituras no atómicas en todo el repositorio de extracción

**Evidencia (ejecutado).** Ninguno de los 41 ficheros usa `os.replace`, `NamedTemporaryFile`, `mkstemp` o `fsync`. Todos escriben en sitio con `write_text` / `write_bytes` / `to_csv` / `open("w")`.

**Impacto.** Un fallo a mitad de escritura (red, `PermissionError`, `KeyboardInterrupt`) deja el destino truncado o vacío. En raw hoy lo impide el read-only; en `data/procesado` y en los 10 destinos aún ausentes, no.

---

### F-10 · P2 · `_n_registros` traga excepciones y devuelve 0

**Evidencia.** `extract/main_ingest.py:82-122`: cuatro bloques `except Exception: return 0` (CSV, JSON, XLSX, ZIP) y uno general en `:120`.

**Impacto.** El manifiesto de ingesta registraría `n_registros: 0` en ficheros que sí tienen datos, sin que el extractor falle. El manifiesto deja de ser una evidencia fiable de recuento.

---

### F-11 · P3 · Detalles menores (lote)

| # | Fichero:línea | Detalle |
|---|---|---|
| F-11a | `14_add_metadata_fingerprint.py:73` | `hashlib.md5` para `property_fingerprint`. No es seguridad (no se usa para verificar), pero es un hash débil y no criptográfico. |
| F-11b | `fotocasa_detalle.py:83`, `ine_atlas_renta.py:171,229` | `__import__("datetime")` en lugar de importar `datetime`. Funciona; estilo. |
| F-11c | `ine_atlas_renta.py:211` | `"anio_fuente": 2022` hardcodeado en la rama Atlas; si el año del Atlas cambia, el campo miente (el `anio_renta` de la misma fila sí es dinámico). |
| F-11d | `entity_resolution.py:17-19` | Doble resolución de `RAW_DIR` (prueba `parent.parent/data` y si no existe usa `parent/data/raw`). Dos constantes para un concepto; en el repo actual gana la primera. |
| F-11e | `22_geo_areas_funcionales.py:70` | `json.load(open(...))` sin context manager (fuga de file handle). |
| F-11f | `main_ingest.py:311` | `parser.parse_known_args()` ignora argumentos desconocidos en vez de fallar. |
| F-11g | `21_lanbide_historico_paro_joven.py:15` | Importa `leer_csv_seguro` y no lo usa. |
| F-11h | `main_ingest.py:30` | `os.chdir(PROJECT_ROOT)` como efecto secundario de importación (mutación global de cwd). |

---

## 3. Evidencia positiva (lo que sí cumple)

- **41/41 parsean.** `ast.parse` sobre los 41 ficheros: **0 errores de sintaxis**. No se ejecutó `compileall` (evitaría escribir `__pycache__`); `ast.parse` es el equivalente sin efectos.
- **39/41 con entrypoint.** `if __name__ == "__main__"` + `def main()`; los dos restantes son librerías (`_common.py`, `entity_resolution.py`). 14 con `argparse`.
- **HTTP centralizado y correcto.** `extract/_common.py:71-134` `Cliente`: `timeout=60` por defecto (`:107`), 4 reintentos con backoff exponencial (`:110-129`), pausa educada entre peticiones (`:92-98`) y logging de cada reintento. Lo usan 22 ficheros.
- **Todas las llamadas `requests.*` directas** (11 ficheros) llevan `timeout` **y** `raise_for_status`: `11:75`, `19:81`, `20:34,66`, `26:101`, `educacion_centros:54`, `ine_atlas_renta:93`, `salud_centros:71`, `udalmap_empleo:53`.
- **Sin secretos.** Escaneo `password|secret|api_key|token|credential|Authorization|Bearer`: solo `REALTYAPI_KEY` leído de `.env`/entorno (`09_realtyapi.py:48,213`). 0 valores hardcodeados.
- **Sin `except:` desnudos.** Los 5 `except …: pass` de `10_opendata_bizilagun_etxebide.py:48,59,64,94,99` son guardas legítimas de `pd.isna()`/`.item()`; los `continue` son saltos de bucle legítimos. Ningún `except` vacío que trague errores.
- **Sin primitivas peligrosas.** 0 `eval`, 0 `exec`, 0 `shell=True`, 0 `pickle`, 0 `os.system`.
- **Todo el tráfico es `https://`.** 0 URLs `http://` planas; 0 `verify=False`.
- **`sys.path` sin rutas hardcodeadas.** Los 35 `sys.path.insert` usan `Path(__file__).resolve()`; ninguna ruta absoluta de máquina (`C:\`, `/home`, `/Users`) en código.
- **Modelo de escritura segura.** `26_vpo_terminadas.py`: `raise_for_status` (`:102`), `timeout=90` (`:101`), validación en memoria con umbrales (`:60-97`), comprobación de SHA antes de escribir (`:114-122`), gate `--promote` (`:167`) y `assert_raw_writable` (`:127`).
- **Guard del bronce existente y probado.** `transform/_raw_guard.py` exige `.FROZEN` (`:84-87`) y registra en `logs/raw_guard_audit.log` (`:90-96`); hay tests `tests/test_raw_guardrails.py`, `test_raw_guard_runtime.py`, `test_raw_inmutable.py`.

---

## 4. Mapeo a criterios (fichero:línea)

### C1 — Extracción Python (API **y** scraping), nivel 10: «Automatiza API y scraping»

| Elemento | Evidencia |
|---|---|
| **APIs automatizadas** | `01_eustat_api.py:50-71` (GET+POST bankupx), `06_ine_api.py:51-56` (wstempus), `07_ine_salarios.py:50-54`, `10_ovj_salario.py:32-35` (Irekia), `16_serpavi_renta.py:22-35` (MIVAU), `17_osrm_tiempos.py:36-48` (OSRM), `18_lanbide_paro_juvenil.py:20-32`, `19_udalmap_indicadores_adicionales.py:77-83`, `20_ecvi_compraventa.py:31-38`, `22_geo_areas_funcionales.py:22-56`, `24_etxebide_promociones.py:23-32`, `25_udalmap_extendido.py:38-62`, `26_vpo_terminadas.py:39-103`, `educacion_centros.py:23-56`, `salud_centros.py:22-73`, `ine_atlas_renta.py:26-94` |
| **Scrapers automatizados** | `05_fotocasa_scraper.py:157-205` (JSON embebido en HTML), `08_pisos_scraper.py:54-105` (regex sobre HTML), `13_scraping_habitaciones.py:153-186,269-315`, `09_fotocasa_dirigido.py:65-97`, `10_scraping_faltantes.py:87-126`, `11_transporte_gtfs_paradas.py:199-214` (GTFS/ZIP), `fotocasa_detalle.py:53-79` |
| **Orquestador** | `main_ingest.py:191-230` (`_live`), `:194` glob `[0-9][0-9]_*.py`, `:41-49` `AUX_SCRIPTS` (7), `:147-188` aislamiento de fallos por subprocess, `:262-297` modo `replay-raw` sin red |
| **Falsador del plan** | «Que un extractor clave exija intervención manual o que `main_ingest` no orqueste». **`main_ingest` sí orquesta** (evidencia arriba). **Pero** F-01/F-02 hacen que la re-ejecución requiera intervención. Matizado, no tumbado. |

### C15 — Datos heterogéneos, nivel 10: «Integra datos de fuentes con estructuras diferentes y los adapta mediante Python/PyMongo»

| Elemento | Evidencia |
|---|---|
| **Formatos distintos** (ejecutado, conteo de ficheros) | JSON 20 · CSV 10 · XLSX 6 · GeoJSON 6 · ZIP 5 · SHP 2 · GTFS 1 |
| **Normalización común** | `extract/_common.py:148-164` `leer_csv_seguro` (`dtype=str`, `utf-8-sig`, `codigo_ine` zfill 5); `_common.py:185-214` `guardar_json` (envoltura `{metadata, datos}` + SHA); `extract/normalizar_metadata.py:56-109` (esquema único + alias); `extract/entity_resolution.py:42-85` (nombre → `codigo_ine` canónico) |
| **Adaptación por fuente** | `02_eustat_alquiler.py:74-125` (CSV con secciones por territorio), `10_opendata_bizilagun_etxebide.py:134-205` (XLSX multi-hoja) y `:209-275` (CSV con sección «Detalle por municipios»), `11_transporte_gtfs_paradas.py:112-196` (stop → municipio por point-in-polygon o alias), `16_serpavi_renta.py:37-75` (LOCF entre años), `22_geo_areas_funcionales.py:29-50` (shapefile → polígonos) |
| **Falsador del plan** | «Que cada fuente se cargue sin normalización común». **No ocurre**: hay cuatro capas de normalización compartidas. Criterio **cumple**. |

---

## 5. Ejecutado vs solo leído

**Ejecutado (herramienta real):**
- `ast.parse` sobre los 41 `.py` (0 errores) + conteo de imports/funciones/clases.
- Sondas Python propias (en `scratch`, no en el repo): matriz de higiene de red, `except` vacíos, secreto, rutas absolutas, `sys.path`, primitivas peligrosas, permisos `os.stat`/`os.access`, destinos de escritura vs. raw, atomicidad, cobertura de formatos.
- Sonda de metadata: AST sobre las 41 llamadas `guardar_json` → 16 definitivas + 4 condicionales que fallan.
- `git blame -L 168,214 -- extract/_common.py` (procedencia de la validación), `git status --short`, `git rev-parse`.
- `ls`/`find`/`wc -l` sobre `extract/` y `data/raw`.
- Lectura de los JSON de raw (`emancipacion_juventud_resumen.json`, `anuncios_fotocasa.json`, `anuncios_pisos.json`) para contrastar la metadata.

**Solo leído (sin ejecutar):** los 41 ficheros vía `read_file`; `00_baseline_v9.md`, `plan_reauditoria_v9_2026-11-10.md`, `plan_ejecucion_v9_rondas_2026-11-10.md`, `rubrica_reextraida.md`, `mapa_requisitos.md`, `AGENT.md`, `transform/_raw_guard.py`.

**No ejecutado (guardrails):** `main_ingest.py` en modo `live`, ningún extractor, `load_all`/`clean_all`, Mongo, HDFS, Kafka, `compileall` (para no escribir `__pycache__`).

---

## 6. Bloqueos y límites

- **Ninguno para esta unidad.** La auditoría es estática; la caída de la red centro (HDFS 50070 / Kafka 9092) no afecta.
- **Límite:** no se ejecutó ningún extractor, por lo que F-01 es una **predicción por lectura del código** (validada por la procedencia `git blame` y por los ficheros raw existentes que carecen de `url`), no una captura de la excepción en vivo. Para convertirla en evidencia ejecutada haría falta escribir en raw, lo que está prohibido.
- **Límite:** el `read-only` de raw se comprobó con `os.access`/`os.stat` del usuario actual; si la congelación se hace con ACLs distintas en otro entorno, F-02 podría no aplicar (F-01, que es de código, sí).

---

## 7. Impacto, riesgo e opciones

**Impacto (0-10): 7/10** — cambia una afirmación de defensa («la extracción es re-ejecutable») y afecta al 62 % de los puntos de escritura; no afecta a la nota de C1/C15, que se acreditan con el código y con el raw ya producido.
**Riesgo (0-10): 3/10** — probabilidad de que alguien re-ejecute `main_ingest --mode live` y lo haga chocar contra el bronce congelado; coste bajo (fallo visible, sin corrupción).

**Opciones (ninguna ejecutada):**
1. **Alinear la validación con la realidad (recomendada):** hacer que `guardar_json` **avise** en raw (como ya hace fuera de raw) o que los extractores pasen `url` — son 20 llamadas, la mayoría con el mismo `metadata={...}`; se pueden corregir en lote.
2. **Declarar el modo congelado:** añadir a `_common` una bandera `RAW_FROZEN` que haga `guardar_json` saltar (no escribir) cuando el destino exista y el SHA coincida, igual que hace `26_vpo_terminadas.py:114-122`. Así `main_ingest --mode live` pasaría a ser un «verificar», no un «re-escribir».
3. **Mover el manifiesto de ingesta fuera de raw:** escribir `ingestion_manifest.json` en `data/procesado/_meta/` (donde ya vive `generar_ingestion_manifest.py`) y retirarlo de `RAW_DIR`. Elimina F-04 y la inconsistencia de exclusiones.
4. **Correcciones de robustez (lote aparte):** `timeout` en `subprocess.run`; sustituir `urlretrieve` por `requests.get(stream=True)`; validar `extractall`; escritura atómica (`os.replace`); quitar los `except Exception: return 0` de `_n_registros`.

**Respecto a F-01:** al ser P1, este informe **se detiene y reporta**; no se ha aplicado ningún fix.

---

## 8. Cobertura

| Métrica | Valor |
|---|---|
| `.py` en `extract/` | 41/41 revisados |
| Parseados sin error | 41/41 |
| Llamadas de red inventariadas | 22 (`Cliente`) + 11 (`requests` directo) + 4 (`urlretrieve`) + 2 (`urllib.urlopen`) |
| Destinos de escritura bajo raw | 72 existentes read-only · 8 escribibles · 10 ausentes |
| Llamadas `guardar_json` | 41 (20 fallan, 21 correctas) |
| Hallazgos | 1 P1 · 9 P2 · 8 P3 |
| Modificaciones en el repo por esta unidad | **0** (verificado con `git status` tras el trabajo; el árbol staged/modified es el de partida) |
