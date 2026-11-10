# Informe de auditoría estática — `transform/` (42 `.py`) · v9 2026-11-10

**Unidad:** W2.2 · **Criterios:** C6 (Construcción del conjunto de datos), C7 (Limpieza y transformación con PyMongo), C15 (Datos heterogéneos)
**Naturaleza:** solo lectura. No se modificó código, datos, Mongo, HDFS ni Kafka; no hubo commit/push; no se instalaron dependencias. Única escritura: este informe.
**Entrada:** `transform/*.py` (42 ficheros, 6.472 líneas) · **Baseline:** `00_baseline_v9.md` · **Rúbrica:** `rubrica_reextraida.md` · **Contexto R1:** `informe_extract.md`
**Repo:** `bigdata-vivienda-euskadi` @ `47065f6` (rama `master`), verificado con `git rev-parse`.

---

## 1. Veredicto resumido

| Criterio | Veredicto | Nota v8 (histórico) | Cambio |
|---|---|---|---|
| **C6** Construcción del conjunto de datos (2+ colecciones + relación/embedding/referencia) | **CONTRIBUYE, no acredita por sí solo** | — | `transform/` construye el modelo relacional que alimenta Mongo: `unificar_anuncios.py` embebe `ubicacion` y relating con `dim_municipios` por `codigo_ine`; `construir_dim_gold.py:32-33` une 3 tablas. **Pero las colecciones Mongo las crean `storage/` y `analysis/`** (W2.3): el criterio habla de «colecciones», no de CSV silver. |
| **C7** Limpieza y transformación con PyMongo (4+ ops: nulos, duplicados, tipos) | **CUMPLE con reservas** | — | Las 4+ operaciones existen y son trazables (nulos, duplicados, tipos, entity resolution, outliers). **Reserva:** el criterio dice «con PyMongo»; la limpieza de `transform/` es **pandas**. La limpieza PyMongo vive en `storage/clean_mongo.py`. |
| **C15** Datos heterogéneos (fuentes con estructuras distintas adaptadas con Python/PyMongo) | **CUMPLE** | 10/10 | 6+ formatos (CSV `;`/latin-1/utf-8-sig, JSON envuelto y desnudo, GeoJSON, GTFS/ZIP, XLSX derivada) y adaptación explícita por fuente. Sin hallazgos que lo tumben. |

**Hallazgo dominante:** T-02 (P2) — **doble fuente de verdad** para `dim_municipios`: 9 scripts leen la copia congelada en `data/raw` (oct 29) mientras el pipeline produce la copia vigente en `data/procesado` (nov 7). Hoy los 252 códigos coinciden (verificado), pero la copia raw está congelada y no seguirá nunca a la procesado.

**Recuento de hallazgos:** P0 = 0 · P1 = 0 · **P2 = 12** · **P3 = 10**. No se detuvo la auditoría.

---

## 2. Hallazgos

### T-01 · P2 · Rutas `data/` relativas al cwd + `_common.py` crea el árbol en importar (propaga R1 F-03)

**Evidencia.** `extract/_common.py:38-44` define `DATA_DIR = Path(os.getenv("DATA_DIR", "data"))` (relativo) y ejecuta `mkdir` sobre `raw/procesado/resultados` **en importación**, sin `chdir`. Diez scripts de `transform/` importan `_common` y por tanto heredan el efecto:

| Fichero:línea | Import de `_common` |
|---|---|
| `transform/parsear_secciones.py:12` | `from _common import RAW_DIR, get_logger` |
| `transform/corregir_empleo.py:12` | `RAW_DIR, get_logger, guardar_json` |
| `transform/dim_municipios.py:19` | `RAW_DIR, get_logger, guardar_json, leer_csv_seguro` |
| `transform/completar_alquiler_comarca.py:16` | `RAW_DIR, get_logger` |
| `transform/enriquecer_codigo_ine.py:24` | `RAW_DIR, get_logger` |
| `transform/f4_pisos_dirigido.py:13` | `RAW_DIR, Cliente, get_logger, guardar_json` |
| `transform/filtrar_outliers.py:30` | `RAW_DIR, get_logger, guardar_json` |
| `transform/generar_distancias.py:12` | `RAW_DIR, get_logger` |
| `transform/muni_resolve.py:18` | `entity_resolution` (que a su vez usa `_common`) |
| `transform/validar_renta.py:13` | `RAW_DIR, get_logger` |

Además, **10 scripts** construyen rutas con `os.path.join("data", …)` relativo al cwd: `limpiar_ecvi.py:5-6`, `limpiar_eustat_demografia.py:6-7`, `normalizar_json_crudos.py:6-7`, `imputar_nulos_fuentes.py:14-15`, `unificar_anuncios.py:7-8`, `rescatar_features_nlp.py:5-6`, `enriquecer_gtfs_conectividad.py:5-6`, `enriquecer_equipamiento_realtyapi.py:5,15`, `generar_fingerprint.py:5`, `muni_resolve.py:20,25`.

**Mitigación parcial (ejecutado).** `transform/run_all.py:40` hace `os.chdir(PROJECT_ROOT)` y `:373` lanza los hijos con `cwd=str(PROJECT_ROOT)`, por lo que **vía orquestador la ruta es correcta**. El fallo aparece al ejecutar cualquier script suelto desde otro directorio (el uso documentado en los propios docstrings) o al importar `_common`.

**Impacto.** Un script lanzado desde otro cwd escribe (o intenta escribir) en un `data/` paralelo fuera del repo; `_es_raw()` (`_common.py:177-182`) deja de referirse al raw real y la validación de metadata de R1 F-01 se aplica sobre el árbol equivocado.

---

### T-02 · P2 · Doble fuente de verdad: `dim_municipios` congelado en raw vs. vigente en procesado

**Evidencia (ejecutado).** `data/raw/dim_municipios.csv` (22.820 B, **oct 29 08:54**, read-only, **en el manifest raw**: `docs/raw_manifest_sha256.txt` entradas `77d0feb6…` y `5e9f069b…`) y `data/procesado/dim_municipios.csv` (30.555 B, **nov 7 17:25**). Comparación de códigos: **252 = 252, conjuntos idénticos** (verificado con `csv.DictReader`). Por tanto **hoy no hay divergencia de datos**, pero las dos copias existen y el pipeline solo actualiza la de procesado.

**9 scripts leen la copia de raw** (congelada, no regenerable por el pipeline):

| Fichero:línea | Lectura |
|---|---|
| `transform/limpiar_eustat_demografia.py:17` | `os.path.join(RAW, "dim_municipios.csv")` |
| `transform/completar_alquiler_comarca.py:28` | `RAW_DIR / "dim_municipios.json"` |
| `transform/f4_pisos_dirigido.py:41` | `RAW_DIR / "dim_municipios.json"` |
| `transform/generar_distancias.py:30` | `RAW_DIR / "dim_municipios.csv"` (fallback) |
| `transform/generar_f4_pisos_objetivo.py:44` | `os.path.join(RAW, "dim_municipios.json")` |
| `transform/generar_fotocasa_dirigido_informe.py:23` | `os.path.join(RAW, "dim_municipios.json")` |
| `transform/muni_resolve.py:27` | `os.path.join(RAW, "dim_municipios.csv")` (fallback) |
| `transform/unificar_anuncios.py:364` | `os.path.join(RAW, "dim_municipios.csv")` (fallback) |
| `transform/validar_renta.py:25` | `RAW_DIR / "dim_municipios.csv"` (fallback) |

**Contraste (buena práctica, minoría).** `muni_resolve.py:25`, `unificar_anuncios.py:362`, `generar_distancias.py:27`, `generar_vistas_mercado.py:24-31` y `validar_renta.py:23-25` **prefieren `data/procesado` y usan raw solo como fallback**. No hay una regla única.

**Caso adicional (latente, hoy byte-idéntico).** `generar_analisis_variables_base.py:69` lee `RAW / "distancias_capitales_252.csv"` (oct 29) mientras `generar_distancias.py:40` escribe `PROC / "distancias_capitales_252.csv"` (nov 7). Verificado: **mismo SHA-256** (`9b840cb6ff1f…`) en ambas copias, por lo que no hay divergencia actual. Si `generar_distancias` cambia, el análisis seguiría leyendo la copia congelada.

**Impacto.** Si la dim procesado se corrige (nuevo municipio, nombre canónico, variante), los 9 scripts que leen raw no lo verán: mapeos nombre→`codigo_ine` obsoletos, coberturas incoherentes entre tablas y `--check` que no lo detecta. Es el mismo patrón de «dos constantes para un concepto» que `read-only-repo-analysis` marca como deuda silenciosa.

---

### T-03 · P2 · Declaración del DAG inconsistente con el código: input fantasma `raw:udalmap_empleo_corregido.csv`

**Evidencia.** `transform/run_all.py:133-139` declara como entrada de `generar_analisis_variables_base.py`:
```
"raw:udalmap_empleo_corregido.csv"
```
Pero **ese fichero no existe en `data/raw`** (verificado: `raw:NO  proc:2026-11-07 17:25:10`) y el código lee la copia de procesado: `generar_analisis_variables_base.py:71` → `ud = loadcsv(PROC / "udalmap_empleo_corregido.csv")` (comentario `:70` «WP-04/C-03: se lee la copia de PROCESADO, no el duplicado congelado de raw»).

**Agravante (ejecutado).** `run_all.py --check` devuelve **exit 0 y `generar_analisis_variables_base.py: 1 salidas al día`**. El chequeo es ciego porque `_resolver` (`run_all.py:252`) devuelve `[root / patron]` **exista o no**, y `_estado` (`:357-360`) solo marca «entradas inexistentes» si `_resolver(ref)` es falsy (nunca lo es para rutas sin glob). El `run_manifest.json` lista además un input que no existe.

**Impacto.** El chequeo de staleness no sigue la entrada real (`proc:udalmap_empleo_corregido.csv`); si `corregir_empleo.py` regenera el fichero, `--check` puede no advertir que `analisis_variables_base.csv` quedó desactualizado. Es un falso sentido de cobertura.

---

### T-04 · P2 · Ninguna escritura atómica en `transform/` (49 llamadas, 0 primitivas)

**Evidencia (ejecutado).** Escaneo AST + regex sobre los 42 ficheros: **0** ocurrencias de `os.replace`, `NamedTemporaryFile`, `mkstemp`, `fsync` o `tempfile`. Las 49 operaciones de escritura son `to_csv` / `write_text` / `to_json` / `savefig` / `open("w")` en destino.

**Reescrituras in-place de silver compartido** (las más expuestas):

| Fichero:línea | Destino |
|---|---|
| `transform/aplicar_cobertura_mercado.py:107` | `data/procesado/dim_municipios.csv` (segundo escritor autorizado) |
| `transform/deduplicar_alquiler_enriquecido.py:48,64` | `alquiler_municipal_enriquecido.csv` / `.json` |
| `transform/unificar_anuncios.py:334,422,423,495,521` | `dedup_report.json`, `cuarentena_pisos.*`, `anuncios_unificados.*` |
| `transform/generar_fingerprint.py:26,61` | `anuncios_unificados.json` / `.csv` |
| `transform/rescatar_features_nlp.py:58,92` | `anuncios_unificados.json` / `.csv` |
| `transform/enriquecer_equipamiento_realtyapi.py:47,78,91` | `anuncios_unificados.json` / `.csv` |
| `transform/run_all.py:412` | `data/procesado/run_manifest.json` |

**Impacto.** Un fallo a mitad de escritura (red, `PermissionError`, `KeyboardInterrupt`, disco lleno) deja el destino truncado o vacío, sin rollback. `anuncios_unificados.*` y `dim_municipios.csv` son hubs que leen varios pasos del DAG: corromperlos degrada en cascada. Es el mismo patrón que R1 F-09, ahora en la capa silver.

---

### T-05 · P2 · 7 scripts ejecutan su pipeline al importarlos (sin guard `if __name__ == "__main__"`)

**Evidencia (ejecutado).** 9 de 42 ficheros no tienen `__name__ == "__main__"`. De ellos, **7 escriben en `data/procesado` en módulo** (no dentro de `main()`):

| Fichero:línea | Efecto en import |
|---|---|
| `transform/asignar_area_funcional_ecvi.py:53` | `out.to_csv(dest, …)` |
| `transform/enriquecer_equipamiento_realtyapi.py:47` | `open(path, "w", …)` + `json.dump` |
| `transform/generar_analisis_variables_base.py:204` | `base.to_csv(dest, …)` |
| `transform/generar_emancipacion_tier3_93.py:108` | `out.to_csv(dest, …)` |
| `transform/generar_fingerprint.py:26` | `open(path, "w", …)` |
| `transform/generar_municipios_faltantes_93.py:52` | `out.to_csv(dest, …)` |
| `transform/generar_poblacion_joven_municipal.py:81` | `out.to_csv(dest, …)` |

Además `transform/muni_resolve.py:53` ejecuta `_load_dim()` **en importación** (lee `data/procesado/dim_municipios.csv` y construye `CODE2NAME/NAME2CODE/VALID_CODES` a nivel de módulo). `_raw_guard.py` es el noveno sin guard, pero solo define constantes (seguro).

**Impacto.** Importar cualquiera de esos 7 muta silver como efecto secundario; rompe el contrato importar≠ejecutar y complica tests o reutilización. `generar_analisis_variables_base.py` es el caso más grave: un `import` dispara un merge de 8 fuentes y una escritura.

---

### T-06 · P2 · `_raw_guard` es un registro de auditoría, no un bloqueo; solo 2 de 42 scripts lo usan

**Evidencia.** `transform/_raw_guard.py:76-96` `assert_raw_writable(reason)`:
1. exige `reason` no vacío (`:82-83`);
2. verifica que **exista** `.FROZEN` (`:84-87`);
3. escribe en `logs/raw_guard_audit.log` (`:90-96`).

**No comprueba `os.access`/writability ni impide la escritura.** La prevención real en `enriquecer_codigo_ine.py` es otra función: `_check_frozen(force)` (`:41-48`) que aborta con `SystemExit(2)` si `.FROZEN` existe y no hay `--force`. Orden en `main()`: `assert_raw_writable(reason)` (`:137`) **antes** de `_check_frozen(force)` (`:139`), es decir, el log registra una intención que luego se aborta.

**Solo 2 ficheros importan el guard:** `enriquecer_codigo_ine.py:27-29` y `f4_pisos_dirigido.py:16-18`. Los demás 40 no lo referencian.

**Impacto.** El nombre `assert_raw_writable` sobreestima la garantía: un lector puede creer que raw queda protegido por el guard cuando en realidad solo queda **log**. La inmutabilidad real hoy la aplican: (a) los permisos read-only de `data/raw` (F-02 de R1), (b) `_check_frozen`, (c) que el DAG no incluye ninguna escritura en raw. El guard es un auditor, no un gate.

---

### T-07 · P2 · `subprocess.run` sin `timeout` en el orquestador (R1 F-06 se reproduce)

**Evidencia.** `transform/run_all.py:371-377`:
```python
proc = subprocess.run(
    [sys.executable, str(script)],
    cwd=str(PROJECT_ROOT),
    capture_output=True,
    text=True,
    env=env,
)
```
Sin `timeout=`. Comprobado: la palabra `timeout` no aparece en la llamada.

**Impacto.** Un transform que se cuelgue (GTFS grande, `pandas` con memoria, espera de red en `enriquecer_codigo_ine`) bloquea `run_all` indefinidamente; el manifiesto final (`:491`) no se escribe y no hay forma de saber qué pasos completaron. Mismo defecto que R1 F-06 en `extract/main_ingest.py`.

---

### T-08 · P2 · `run_all.py` muta el cwd global en importación y escribe el manifiesto sin atomicidad

**Evidencia.** `transform/run_all.py:39-40`:
```python
PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)
```
El `chdir` es un efecto secundario de importación (patrón idéntico a R1 F-11h en `extract/main_ingest.py:30`). Por otro lado `run_all.py:405-414` escribe `data/procesado/run_manifest.json` con `write_text` directo (sin `os.replace`).

**Impacto.** Importar `run_all` cambia el directorio de trabajo del proceso llamador. El manifiesto de ejecución (evidencia de auditoría del silver) puede quedar truncado si el proceso muere durante la escritura.

---

### T-09 · P2 · `calcular_tension_social.cat()` clasifica `NaN` como «alta» (latente)

**Evidencia.** `transform/calcular_tension_social.py:65-72`:
```python
def cat(v):
    if v < 33: return "baja"
    if v < 66: return "media"
    return "alta"
```
Con `v = NaN`, ambas comparaciones son `False` y devuelve `"alta"`. `tension_demanda_social` (`:63`) es `((p_sol + p_esf) / 2)`, que es `NaN` si `esf` es `NaN` (ambos `esfuerzo_joven_pct` y `esfuerzo_max_pct` nulos).

**Estado actual (ejecutado).** `data/procesado/dim_municipios_tension.csv`: 252 filas, **0 `tension_demanda_social` NaN**, categorías `media 103 / alta 76 / baja 73`. En `dim_municipios_renta.csv`, `esfuerzo_joven_pct` y `esfuerzo_max_pct` tienen **0 NaN**. **El defecto no se manifiesta hoy**, pero cualquier municipio que pierda ambas fuentes de esfuerzo pasaría a `tension_categoria = "alta"` sin aviso.

**Impacto.** Mala clasificación silenciosa del indicador de tensión social (C17) en un escenario plausible (municipio sin alquiler y sin renta). Corrección trivial: `if pd.isna(v): return "sin_dato"`.

---

### T-10 · P2 · Cifras hardcodeadas en un título de figura y conversión insegura

**Evidencia.** `transform/generar_figuras_N.py:259`:
```python
fig.suptitle("H2 Tier confianza A/B/C/D por Territorio Histórico (TH) — A4/B3/C57/D188", fontsize=11)
```
Las cifras reales se leen de `mongo_tier_confianza.csv` (`:237-243`) y se pintan en el gráfico (`:247-249`), pero el `suptitle` las **teclea**. Si los datos cambian, el título miente mientras el gráfico es correcto.

**Agravante.** `generar_figuras_N.py:62`: `df["codigo5"] = df["_id"].astype(int).astype(str).str.zfill(5)`. Si `_id` tiene `NaN`, `.astype(int)` lanza `ValueError` (no hay guarda).

**Impacto.** Riesgo de defensa: una cifra literal en un PNG que no se regenera con los datos es exactamente el tipo de contradicción que se lee en voz alta. El script está EXCLUIDO del DAG (`run_all.py:241`) y genera 9 PNG en `data/resultados`.

---

### T-11 · P2 · Docstrings que afirman escribir en `data/raw` cuando escriben en `data/procesado`

**Evidencia.**

| Fichero:línea | Docstring | Escritura real |
|---|---|---|
| `transform/dim_municipios.py:7` | «Salida: data/raw/dim_municipios.json y .csv» | `PROC_DIR` = `data/procesado` (`:22`, `:276-299`) |
| `transform/corregir_empleo.py:6` | «Genera data/raw/udalmap_empleo_corregido.csv/.json» | `PROC_DIR` = `data/procesado` (`:17`, `:94-95`) |
| `transform/parsear_secciones.py:6` | «Genera data/raw/alquiler_seccion.csv» | `PROC_DIR` = `data/procesado` (`:15`, `:66`) |

**Impacto.** Un lector que confíe en el docstring busca los ficheros en el bronce congelado y no los encuentra; peor, puede creer que el pipeline escribe en raw (prohibido) y cuestionar la gobernanza. Es documentación activamente engañosa, no solo obsoleta.

---

### T-12 · P2 · Periodos/trimestres/años hardcodeados en las limpiezas

**Evidencia.**

| Fichero:línea | Valor hardcodeado |
|---|---|
| `transform/limpiar_ecvi.py:25` | `row[0] == "2026" and row[1] == "II"` |
| `transform/limpiar_ecvi.py:77,110,150` | `"trimestre": "2026T2"` |
| `transform/generar_municipios_faltantes_93.py:38` | `pob["periodo__etiqueta"] == "2024/01/01"` |
| `transform/enriquecer_gtfs_conectividad.py:83` | `ref_date = datetime.date(2026, 10, 26)` |

**Contraste (buena práctica).** `generar_poblacion_joven_municipal.py:27-29` implementa el patrón correcto: si el periodo preferido no existe, usa el máximo disponible y lo registra en la salida (`metodo`, `:77`). `calcular_renta_joven.py:40` filtra `periodo == "2024"` con fallback documentado y flag (`flag_ratio_fiscal`).

**Impacto.** Al actualizar la fuente (trimestre siguiente, año nuevo), `limpiar_ecvi.py` no encuentra la fila objetivo y usa `data[-1]` (`:27`) — **trimestre equivocado con etiqueta `2026T2` fija**; `generar_municipios_faltantes_93.py` queda con 0 filas. Fallo silencioso o dato mal etiquetado.

---

### T-13 · P3 · Código muerto y no-ops (lote)

| # | Fichero:línea | Detalle |
|---|---|---|
| T-13a | `transform/dim_municipios.py:162-164` | Bucle `for r in registros:` cuyo cuerpo es `pass`; no hace nada. |
| T-13b | `transform/enriquecer_gtfs_conectividad.py:59-64` | `def service_active_on(...)` con cuerpo `pass` (stub); la lógica real está inline en `main()` (`:141-153`). |
| T-13c | `transform/generar_cert_energetico_municipal.py:123` | `merged["municipio"] = merged["municipio"]` (auto-asignación no-op). |
| T-13d | `transform/filtrar_outliers.py:155` | `elif True:` — condicional muerto (siempre verdadero). |
| T-13e | `transform/auditar_lagunas_silver.py:25` | `CURATED_VITAL_CSVS = sorted(p.name for p in CSV_DIR.glob("*.csv"))` en nivel de módulo: escaneo del filesystem al importar; si `data/procesado` no existe, la lista queda vacía y el script escribe un CSV de auditoría sin filas. |

---

### T-14 · P3 · `guardar_json` sin `url` en destinations de procesado (latente, no F-01)

**Evidencia.** `transform/corregir_empleo.py:95-99` y `transform/dim_municipios.py:276-285` llaman a `guardar_json` con `metadata=` que no incluye `url`. `_common.py:199-205` solo eleva `ValueError` si el destino es raw (`_es_raw`); en procesado emite un **aviso** (`:206-209`). Verificado: `_common.guardar_json` autocompleta `n_registros`, `fecha_extraccion`, `version_parser` y `hash_sha256` (`:191-198`), así que los únicos campos que el llamador debe dar son `fuente` y `url`.

**Estado.** `f4_pisos_dirigido.py:62-70` sí escribe en raw con `guardar_json` y **sí** incluye `fuente` y `url` → **no reproduce R1 F-01**. Los dos llamadores de procesado son seguros **solo mientras el destino siga siendo procesado**; si alguna vez se mueven a raw, fallarán en ejecución.

**Impacto.** Bajo hoy; es deuda acoplada a la decisión de destino.

---

### T-15 · P3 · El camino legado `--write-raw` crearía `.bak_f0` dentro de `data/raw`

**Evidencia.** `transform/enriquecer_codigo_ine.py:61-65` `_backup()` define `bak = ruta.with_suffix(ruta.suffix + ".bak_f0")`, es decir, **junto al fichero original**. En modo plata (`silver=True`, el por defecto) `destino != ruta` y no se llama (`:88-89`, `:119-120`). Pero con `--write-raw --force` (`:133-148`) `dest_dir = RAW_DIR` y `destino == ruta`, por lo que se copiaría `anuncios_fotocasa.csv` → `anuncios_fotocasa.csv.bak_f0` **dentro del bronce congelado**.

**Estado (ejecutado).** `find data/raw -name '*.bak_f0'` → **0 ficheros**. El camino nunca se ha ejecutado.

**Impacto.** Si se usara el opt-in legado, contaminaría `data/raw` (ficheros nuevos no registrados en `docs/raw_manifest_sha256.txt`) y rompería la inmutabilidad que F-02/T-06 defienden. El guard `assert_raw_writable` no cubre los `.bak_f0`.

---

### T-16 · P3 · Manejo de errores e implicaciones menores (lote)

| # | Fichero:línea | Detalle |
|---|---|---|
| T-16a | `transform/enriquecer_gtfs_conectividad.py:39` | `json.load(open(...))` sin context manager (fuga de file handle). Patrón repetido en `generar_f4_pisos_objetivo.py:48,57`, `generar_fotocasa_dirigido_informe.py:26,34,50`. |
| T-16b | `transform/enriquecer_gtfs_conectividad.py:79-80` | `except Exception: pass` al cargar población: si falla, `pop_map` queda vacío y `paradas_por_1000_hab` sale `None` sin aviso. |
| T-16c | `transform/rescatar_features_nlp.py:42-43` | `except Exception: pass` al recalcular `precio_m2_calc`: silencioso, pero es una guarda legítima. |
| T-16d | `transform/imputar_nulos_fuentes.py:50-59` | Imputa también `anio_renta` y `n_declaraciones` con mediana (no son medidas) y **no** registra qué filas fueron imputadas en esas columnas (solo el target lleva `metodo_imputacion_serpavi`). |
| T-16e | `transform/filtrar_outliers.py` vs `generar_anuncios_residencial_filtrado.py` | Dos implementaciones de la misma lógica IQR/outliers (`filtrar_outliers.py:105-129` y `generar_anuncios_residencial_filtrado.py:59-72`). Duplicación con riesgo de divergencia. |
| T-16f | `transform/generar_cert_energetico_municipal.py:63-78` | Mapeo manual nombre→INE O(n·m) con reglas de substring (`arrasate`, `donostia`, `vitoria`). Frágil; verificado que la salida queda en 252 filas. |
| T-16g | `transform/calcular_renta_joven.py:165-170`, `transform/generar_mercado_area_funcional.py:65` | Divisiones sin guard de denominador nulo/positivo → potencial `±inf` en CSV. El skill `exploratory-data-analysis` marca explícitamente que `isna()` no captura `±inf`. Hoy no hay inf en las salidas verificadas. |
| T-16h | `transform/auditar_lagunas_silver.py:21` | `MUNS_TOTAL = 252` hardcodeado; si la dim cambia, el `%` de cobertura miente. |
| T-16i | `transform/generar_municipios_faltantes_93.py:1` | El propio nombre del fichero y del destino (`municipios_faltantes_93.csv`) fijan 93; el script no verifica que salgan 93. |

---

## 3. Evidencia positiva (lo que sí cumple)

- **42/42 parsean.** `ast.parse` + `compile()` en memoria sobre los 42 ficheros: **0 errores de sintaxis**. No se ejecutó `compileall` (evitaría escribir `__pycache__`); `compile()` es el equivalente sin efectos.
- **DAG declarativo y consistente en número.** `transform/run_all.py:52-231` registra **34 scripts**; `EXCLUIDOS` (`:234-243`) lista **8** con motivo obligatorio; 34 + 8 = **42**. Orden por Kahn sobre `in`/`out` (`:286-319`) con aviso de ciclo (`:312-314`). `run_all.py --check` → **exit 0**, los 34 `OK` (ejecutado).
- **`PIPELINE_ORDER` no está en `transform/`.** Se definió en `analysis/run_analisis_mongo.py:49` (11 pipelines, W2.3). En `transform/` el orden es el DAG `SCRIPTS`/`EXCLUIDOS`, no una tupla `PIPELINE_ORDER`.
- **Tratamiento de nulos explícito y trazable.** `imputar_nulos_fuentes.py:31-47` (mediana provincial → regional + `serpavi_imputado` + `metodo_imputacion_serpavi`); `calcular_tension_social.py:44-50` (mediana + `etx_imputado`); `corregir_empleo.py:54-58` (0 exacto → `NaN` con `tasa_paro_valida` y `paro_registrado_cero`); `limpiar_vpo_municipal.py:75-79` («sin dato no es cero»: nulo explícito).
- **Deduplicación determinista y registrada.** `unificar_anuncios.py:310-330` (primero `portal+id_anuncio`, luego `property_fingerprint`, con `dedup_report.json` `:334-337`); `deduplicar_alquiler_enriquecido.py:28-37` (clave de 4 campos, actualiza `n_registros`); `dim_municipios.py:80`; `generar_vistas_mercado.py:227-235`.
- **Tipado disciplinado.** `codigo_ine` con `zfill(5)` en 25 ficheros; `pd.to_numeric(errors="coerce")` explícito (no inferencia) en 18 ficheros; `_habitaciones_int` (`unificar_anuncios.py:35-40`, `filtrar_outliers.py:78-82`); `astype("Int64")` para enteros con nulos (`generar_poblacion_joven_municipal.py:57`, `generar_emancipacion_tier3_93.py:100-102`).
- **Buenas barreras en los límites.** `unificar_anuncios.py:78-97` `_es_lote_valido` (schema guard de lotes dirigidos, con `metadata.n_anuncios` vs `len(datos)`); `corregir_empleo.py:34-44` valida rangos 0-100 / ≥0 con `assert`; `limpiar_vpo_municipal.py:89-96` valida 252 municipios y rango 0-100 ‰; `construir_dim_gold.py:35-36` valida 252 y unicidad; `validar_renta.py:27-29` valida 252 y igualdad de conjuntos con la dim.
- **Sin secretos.** Escaneo `password|secret|api_key|token|credential|Authorization|Bearer`: solo apariciones de `RealtyAPI` como **fuente de datos** (`dim_municipios.py:5,184`, `unificar_anuncios.py:1,217-273`, `enriquecer_equipamiento_realtyapi.py`). 0 valores hardcodeados; `REALTYAPI_KEY` se lee de `.env` en `extract/09_realtyapi.py` (fuera de `transform/`).
- **Sin rutas absolutas de máquina.** Escaneo `[A-Za-z]:\ |/home/|/Users/|/root/|/tmp/`: **0 coincidencias**. Los 14 `sys.path.insert` (11 ficheros) usan `Path(__file__).resolve()`.
- **Sin primitivas peligrosas.** 0 `eval`, 0 `exec`, 0 `shell=True`, 0 `pickle`, 0 `os.system`, 0 `verify=False`.
- **Guard del bronce presente y operativo.** `_raw_guard.py` exige `.FROZEN` (`:84-87`) y escribe en `logs/raw_guard_audit.log` (`:90-96`); el marcador existe (0 bytes) y el log tiene 8 entradas (ejecutado). Los dos únicos scripts que escriben en raw (`f4_pisos_dirigido.py:62`, `enriquecer_codigo_ine.py:123,199` en modo legado) pasan por `assert_raw_writable`.
- **Manifiestos: `transform/` no escribe los manifiestos.** `docs/raw_manifest_sha256.txt` (354 SHA) y `data/procesado/manifest_sha256.txt` (188 entradas) los generan/consumen `scripts/` (`verificar_gobernanza.py:56-58`, `gate_extremo_a_extremo.py:53-55`, `upload_procesado.py:23`). `run_all.py:255-263,405-414` escribe su propio `run_manifest.json` con SHA-256 de entradas y salidas (verificado: 55.932 B, nov 7).
- **Preferencia procesado→raw documentada.** `generar_distancias.py:26-30`, `generar_vistas_mercado.py:22-31`, `muni_resolve.py:24-27`, `unificar_anuncios.py:362-364`, `validar_renta.py:22-25` prefieren la dim de procesado y usan raw solo como fallback con aviso.

---

## 4. Mapeo a criterios (fichero:línea)

### C6 — Construcción del conjunto de datos, nivel 10: «Utiliza 2 o más colecciones y demuestra al menos 1 relación, embedding o referencia entre datos»

| Elemento | Evidencia |
|---|---|
| **Embedding** | `transform/unificar_anuncios.py:159-166` incrusta `ubicacion` (`codigo_ine`, `municipio`, `provincia`, `barrio`, `coordenadas`) en cada anuncio; `:199-206` idem para Pisos; `:241-248` para RealtyAPI. |
| **Referencia por campo común** | `transform/unificar_anuncios.py:343-349` normaliza `ubicacion.codigo_ine` como clave canónica; `transform/dim_municipios.py:151-159` construye la dimensión con `codigo_ine`; `transform/aplicar_cobertura_mercado.py:40-67` cruza `anuncios_unificados` con `dim_municipios` por `codigo_ine` y recalcula `n_anuncios`. |
| **Relación de 3 tablas** | `transform/construir_dim_gold.py:32-33` hace `dim.merge(renta).merge(tension)` por `codigo_ine`; `:36` afirma unicidad. |
| **Visión de las 2+ «colecciones»** | `transform/generar_mapa_esquema.py:85-134` construye un grafo de tablas silver unidas por `codigo_ine`/`id_anuncio` y lo exporta a HTML. |
| **Falsador del plan** | «Que no exista estructura de datos funcional». **No ocurre**: hay dim + hechos + relaciones. **Matiz:** el criterio habla de **colecciones Mongo**; `transform/` produce CSV/JSON silver. Las colecciones y el `$lookup`/`$unwind` están en `storage/` y `analysis/` (W2.3). **Veredicto: `transform/` aporta el modelo relacional; la acreditación completa de C6 es trans-capa.** |

### C7 — Limpieza y transformación con PyMongo, nivel 10: «Realiza al menos 4 operaciones diferentes, incluyendo tratamiento de nulos/ausentes, duplicados y tipos/formato de datos»

| Operación | Evidencia |
|---|---|
| **1. Nulos/ausentes** | `imputar_nulos_fuentes.py:31-47`; `calcular_tension_social.py:44-50`; `corregir_empleo.py:54-58`; `limpiar_vpo_municipal.py:75-79`; `generar_municipios_faltantes_93.py:18-21`. |
| **2. Duplicados** | `unificar_anuncios.py:310-330` (portal+id y fingerprint, con informe); `deduplicar_alquiler_enriquecido.py:28-37`; `dim_municipios.py:80`; `generar_distancias.py:39,71-77`; `generar_vistas_mercado.py:227-235`. |
| **3. Tipos/formato** | `codigo_ine` `zfill(5)` en 30+ ficheros; `pd.to_numeric(errors="coerce")` en `corregir_empleo.py:37,42`, `limpiar_eustat_demografia.py:28,61`, `calcular_renta_joven.py:133-135`, `generar_analisis_variables_base.py:137-139`; `_habitaciones_int` en `unificar_anuncios.py:35-40`; `astype("Int64")` en `generar_poblacion_joven_municipal.py:57`. |
| **4. Entity resolution / normalización** | `muni_resolve.py:163-309` (subtítulo/título/gazetteer con cuarentena); `enriquecer_codigo_ine.py:68-128` (añade `codigo_ine` + `nombre_canonico`); `dim_municipios.py:78-103` (nombre→INE canónico). |
| **5. Filtrado de outliers** | `filtrar_outliers.py:85-204` (límites duros + IQR por segmento, con `motivo_exclusion` y flags); `generar_anuncios_residencial_filtrado.py:59-156`. |
| **Falsador del plan** | «No realiza limpieza». **No ocurre**: hay 5 familias de operaciones. **Matiz:** el criterio dice «con **PyMongo**»; la limpieza de `transform/` es **pandas**. La limpieza en PyMongo está en `storage/clean_mongo.py` (W2.3). **Veredicto: operaciones sobrecumplidas; medio dividido entre capas.** |

### C15 — Datos heterogéneos, nivel 10: «Integra datos procedentes de fuentes con estructuras diferentes y los adapta mediante Python/PyMongo»

| Elemento | Evidencia |
|---|---|
| **Formatos distintos** | CSV con `;` y latin-1 (`limpiar_vpo_municipal.py:32-41`), CSV con 4 filas de cabecera y bloques (`limpiar_ecvi.py:8-21`), JSON envuelto `{metadata,datos}` y desnudo (`normalizar_json_crudos.py:30-45`), GeoJSON (`generar_distancias.py:64-84`, `enriquecer_gtfs_conectividad.py:38-48`), GTFS/ZIP con 5 tablas (`enriquecer_gtfs_conectividad.py:93-178`), XLSX derivada a CSV (`limpiar_eustat_demografia.py:22,55`). |
| **Adaptación por fuente** | `unificar_anuncios.py:135-257` (tres portales → esquema único con `modalidad`, `equipamiento`, `ubicacion`); `parsear_secciones.py:37-55` (forward-fill de municipio/distrito + 12 métricas); `dim_municipios.py:128-159` (variantes de nombre de 3 portales → INE canónico); `generar_cert_energetico_municipal.py:43-83` (3 territorios → 252 con moda A-G). |
| **Trazabilidad del origen** | `calcular_renta_joven.py:194-199` (`renta_joven_origen` por fila: Eustat/INE_Atlas/imputado); `completar_alquiler_comarca.py:100-141` (`metodo_imputacion` oficial/idw + `idw_vecinos`); `generar_emancipacion_tier3_93.py:86` (`origen_alquiler`). |
| **Falsador del plan** | «Que cada fuente se cargue sin normalización común». **No ocurre**: hay 5 capas de normalización compartidas. Criterio **cumple**. |

---

## 5. Ejecutado vs solo leído

**Ejecutado (herramienta real, read-only):**
- `ast.parse` + `compile()` en memoria sobre los 42 `.py` (0 errores) + conteo de imports, entrypoints, firmas.
- Sondas Python propias en scratch (`probe_transform_1..4.py`): matriz de imports, entrypoints, escrituras, destinos, guards, secretos, rutas absolutas, primitivas peligrosas, `except`, `subprocess`/`sys.path`/`chdir`, patrones de nulos/dedup/tipos, primitivas de atomicidad, resolución de destinos de escritura.
- `transform/run_all.py --check` → **exit 0**, 34/34 `OK` (solo staleness, no ejecuta transforms).
- Comparación de `data/raw/dim_municipios.csv` vs `data/procesado/dim_municipios.csv`: 252 = 252, conjuntos idénticos (`csv.DictReader`).
- `sha256sum` de `data/raw/distancias_capitales_252.csv` y `data/procesado/distancias_capitales_252.csv` → **idénticos** (`9b840cb6ff1f…`).
- `stat`/`ls` sobre `data/raw` (read-only), `data/procesado`, `.FROZEN`, manifiestos; `wc -l` de `manifest_sha256.txt` (188), `cert_energetico_municipal_252.csv` (253 = 252+cabecera), `transporte_paradas_municipio_enriquecido.csv` (253), `anuncios_unificados.csv` (595 = 594+cabecera) y `json` (594 registros).
- `find data/raw -name '*.bak_f0'` → 0; `grep` de `dim_municipios` en el manifest raw (2 entradas); `tail` de `logs/raw_guard_audit.log` (8 líneas).
- `pandas` read-only sobre `dim_municipios_tension.csv` y `dim_municipios_renta.csv` para probar el caso `NaN` de T-09.
- `git rev-parse`, `git status --short`, `git diff --stat -- transform/` (verificación de no-modificación).

**Solo leído (sin ejecutar):** los 42 ficheros vía `read_file`; `extract/_common.py`; `transform/_raw_guard.py`; `00_baseline_v9.md`, `plan_ejecucion_v9_rondas_2026-11-10.md`, `rubrica_reextraida.md`, `informe_extract.md`, `AGENT.md`; `analysis/run_analisis_mongo.py` (solo `grep` de `PIPELINE_ORDER`).

**No ejecutado (guardrails):** ningún transform (`clean_all`/`run_all` completo), `load_all`, `run_analisis_mongo`, Mongo, HDFS, Kafka, `compileall` (para no escribir `__pycache__`), productor Kafka, gate vivo, instalación de dependencias, commit/push.

---

## 6. Bloqueos y límites

- **Ningún P0/P1.** La auditoría no se detuvo.
- **Límite:** no se ejecutó ningún transform, por lo que T-03 (input fantasma), T-04 (atomicidad) y T-09 (`cat(NaN)`) son **predicciones por lectura del código** respaldadas por evidencia ejecutada indirecta (`--check` exit 0, ausencia de `os.replace`, 0 NaN en la salida vigente). Para convertirlas en evidencia ejecutada haría falta ejecutar el pipeline, que está prohibido.
- **Límite:** la comparación `raw` vs `procesado` de `dim_municipios` y `distancias_capitales_252` es **un fotograma** (nov 10). La dim procesado se regenera en cada `run_all`; si se regenerara con cambios, la divergencia latente de T-02 podría materializarse.
- **Límite:** la red centro (HDFS 50070 / Kafka 9092) no se usó; esta unidad es estática y no la requiere.
- **No se tocó nada.** `git status --short` después del trabajo sigue mostrando el mismo estado de partida (los 3 registros nuevos respecto al baseline son artefactos del planificador en `openspec/audit/`, no de esta unidad). `transform/__pycache__` existe, pero sus fechas son anteriores a esta sesión.

---

## 7. Impacto, riesgo y opciones

**Impacto (0-10): 7/10** — cambia dos afirmaciones de defensa («el silver es re-ejecutable sin efectos secundarios» y «el chequeo del DAG garantiza que las entradas están al día») y expone una doble fuente de verdad que, si se materializa, degrada coberturas y mapeos. No afecta a la nota de C6/C7/C15, que se acreditan con el código y con el silver ya producido (594 anuncios, 252 municipios, 188 entradas de manifiesto).

**Riesgo (0-10): 4/10** — probabilidad media de que alguien ejecute un transform suelto desde otro directorio o importe un módulo sin guard, y de que un corte a mitad de escritura corrompa un hub silver. Coste medio (fallo visible, sin corrupción del bronce, que sigue read-only).

**Opciones (ninguna ejecutada):**
1. **Unificar la fuente de verdad de la dimensión (recomendada):** que los 9 scripts de T-02 lean `data/procesado/dim_municipios.*` con fallback a raw (el patrón ya mayoritario), o que el manifiesto raw deje de incluir `dim_municipios.*` y `distancias_capitales_252.csv` como canónicos. Elimina T-02 y la mitad de T-03.
2. **Corregir la declaración del DAG:** cambiar `raw:udalmap_empleo_corregido.csv` por `proc:udalmap_empleo_corregido.csv` en `run_all.py:137` y hacer que `_estado` marque «entrada inexistente» cuando `_resolver` devuelva una ruta que no existe (no solo cuando el patrón es vacío). Elimina T-03.
3. **Escritura atómica en los hubs:** envolver las escrituras de `dim_municipios.csv`, `anuncios_unificados.*` y `run_manifest.json` con `NamedTemporaryFile` + `os.replace` (plantilla ya ausente en todo `transform/`). Elimina T-04.
4. **Añadir el guard `if __name__ == "__main__"`** a los 7 scripts de T-05 y mover el código de módulo a `main()`. Elimina T-05 y el efecto secundario de importación.
5. **Renombrar `_raw_guard.assert_raw_writable`** a `log_raw_write_intent` (o hacer que devuelva/ exija `os.access`) para que el nombre no prometa un bloqueo que no existe;documentar que la protección real es `_check_frozen` + permisos read-only. Elimina T-06.
6. **Robustez (lote aparte):** `timeout=` en `subprocess.run` (`run_all.py:371`); `cat()` con guarda `pd.isna` (`calcular_tension_social.py:65`); quitar las cifras tecleadas del título H2 (`generar_figuras_N.py:259`); alinear los docstrings de T-11; extraer el periodo/trimestre a config como en `generar_poblacion_joven_municipal.py:27-29`.
7. **Higiene (P3):** retirar el código muerto de T-13, cerrar los `open()` de T-16a con context manager, y unificar las dos implementaciones de outliers (T-16e).

**Respecto a T-02/T-03:** al ser P2 y no P0/P1, este informe **no se detiene**; se reportan y no se ha aplicado ningún fix.

---

## 8. Cobertura

| Métrica | Valor |
|---|---|
| `.py` en `transform/` | 42/42 revisados |
| Parseados sin error | 42/42 (`ast.parse` + `compile()`) |
| Scripts en el DAG / EXCLUIDOS | 34 / 8 (motivo obligatorio) |
| Entrypoints con `__main__` | 33/42 (9 sin guard; 7 escriben al importar) |
| Llamadas de escritura inventariadas | 49 (0 atómicas) |
| Primitivas de atomicidad | **0** |
| Scripts que escriben en `data/raw` | 2 (`f4_pisos_dirigido.py:62`, `enriquecer_codigo_ine.py:123,199` modo legado) |
| Usuarios de `_raw_guard` | 2/42 |
| Scripts que leen la dim congelada de raw | 9 |
| Secretos / rutas absolutas / primitivas peligrosas | 0 / 0 / 0 |
| Hallazgos | **0 P0 · 0 P1 · 12 P2 · 10 P3** |
| Modificaciones en el repo por esta unidad | **0** (verificado con `git status` tras el trabajo; el árbol staged/modified es el de partida) |
