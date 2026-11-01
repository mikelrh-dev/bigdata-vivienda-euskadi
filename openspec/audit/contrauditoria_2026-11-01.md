# Contraauditoría — fase recopilación + transformación (2026-11-01)

**Tipo:** contraauditoría read-only de la `verificacion_fase_datos_2026-11-01` (otro modelo).
**Alcance:** SOLO capa raw → transformación (silver). No se modifica código ni datos; solo exploración y análisis.
**Método:** lectura directa de `archivosReto/` (PDF + DOCX), `extract/`, `transform/`, `tests/`, `docs/`, `openspec/`, conteos e inventarios con comandos de solo lectura (`ls`, `find`, `grep`, `head`). No se ha ejecutado `run_all.py` completo ni `--check` con escritura, ni `pytest` completo: los conteos de tests se hacen por inspección (`def test_` + parametrización) para no tocar nada.
**Skills cargadas:** `code-review-and-quality` (revisión en 5 ejes), `documentation-and-adrs` (documentar el porqué).
**Fecha:** 2026-11-01.

---

## 0. Veredicto ejecutivo

1. **El informe del otro modelo es globalmente fiable en su conclusión** ("fase de datos sustancialmente hecha pero no cerrada al 10/10") **pero impreciso en ~1/3 de los detalles.** Coincido en el fondo, matizo o corrijo la forma en 8 de sus 20+ afirmaciones (ver §3).
2. **Para la fase recopilación + transformación, el 10/10 "de lo evaluable antes de Mongo" SÍ está al alcance y está cerca, pero hoy NO es 10/10.** Faltan 5–6 cierres pequeños de trazabilidad, no de datos: `renta_origen` constante por fila (WP-15), `cobertura_anuncios.csv` + `nivel_fiabilidad` (WP-12), `ingestion_manifest.json` (WP-17), bloque `metadata` en 2 JSON de salario (WP-18), `dim` fuera de raw o decisión documentada (WP-16), y fallback fiscal Eustat con flag (WP-11). Ninguno exige regenerar el raw.
3. **NO hay que regenerar el raw. Hacerlo sería un error.** El raw está congelado, con manifest de 314 entradas coherente con el inventario real (195 en raíz + 121 en subdirectorios `gtfs/`, `html_fotocasa/`, `legacy_obsoleto_no_usar/`, `shp_euskadi/`). `ls data/raw | wc -l = 195` es una lectura ingenua; `find data/raw -type f | wc -l = 316` menos 2 excluidos (`.FROZEN`, `.gitkeep`) = 314 = manifest. Quien lea solo el 195 concluirá erróneamente que faltan 119 ficheros.
4. **Lo que el otro informe llama "infraestructura no empezada" (HDFS, Kafka, Mongo, `storage/`, `docker-compose.yml`, `analysis/`, `notebooks/`) es correcto factualmente, pero NO penaliza a esta fase.** El PDF y el DOCX separan esas piezas en criterios propios (RA1 HDFS/Kafka/Integración, RA3, RA4). Evaluar la fase raw→silver con la vara de HDFS/Kafka/Mongo es un error de alcance. Lo que SÍ puede penalizar dentro de esta fase se lista en §4.
5. **Dos "fallos" del otro informe son falsos positivos míos verificados:** `transform/parsear_secciones.py` SÍ escribe con `encoding="utf-8-sig"` (el `grep` de una línea lo marcó mal porque el argumento está en la línea siguiente), y el salario OVJ SÍ tiene procedencia (`descripcion`, `fuente_url`, `fecha_extraccion`, `anio_fuente`, `n_filas`) aunque no bajo la clave literal `metadata`. Corregir el informe sin verificar esto llevaría a "arreglar" lo que ya está bien.

---

## 1. Alcance y método (qué se revisó y qué no)

### Revisado (solo lectura)

- `archivosReto/RETO 1Evaluacion SBD-BDA.pdf` y `Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx` (fuentes absolutas; el PDF ya estaba extraído a `rubrica_tmp/reto1.txt`, el DOCX a `rubrica_tmp/tema8.txt`).
- `extract/` (37 scripts + `_common.py`, `main_ingest.py`, `generar_manifest.py`, `normalizar_metadata.py`), `transform/` (44 scripts + `_raw_guard.py`, `run_all.py`), `tests/` (5 ficheros, 47 funciones `def test_`).
- `verificar_fase_datos.py` (gate 15 checks), `verificacion_crudos.py`, `docs/reglas_limpieza.md`, `docs/raw_manifest_sha256.txt` (314 líneas), `data/procesado/manifest_sha256.txt` (115 líneas), `data/procesado/_meta/` (63 ficheros), `config/fuentes.yaml`, `requirements.txt`, `openspec/project.md`, `AGENT.md`, `openspec/specs/contrato-reto/spec.md`.
- Inventarios: `ls`/`find`/`grep`/`head` sobre `data/raw` y `data/procesado` (conteos, nombres con timestamp, lectores de `dim_municipios`, `renta_origen`, `cobertura*`, `ingestion_manifest*`, `storage/`, `docker-compose.yml`).

### No ejecutado (a propósito)

- No se ha corrido `transform/run_all.py` (ni `--check`), ni `extract/generar_manifest.py --verify`, ni `pytest`, ni ningún script que escriba en `data/`. Los estados "77 passed", "15/15", "35 rc=0" se toman del informe anterior como **declarados, no re-verificados por ejecución** en esta contraauditoría. Donde el informe anterior da un número, lo he contrastado por inspección estática (código + ficheros), no re-ejecutando.
- No se ha leído `.env` ni secretos. `test_p07_sin_credenciales_en_el_repositorio` existe y cubre este punto.

---

## 2. Qué exigen realmente PDF y DOCX para ESTA fase

### PDF — RA1 (BDA). Solo 1 de los 4 criterios cae íntegramente en esta fase

| Criterio PDF | 10/10 literal | Qué parte es de esta fase |
|---|---|---|
| Extracción mediante Python | **"Automatiza API y scraping"** | SÍ, íntegramente aquí. Objetivos 1 (alquiler/compraventa con API + scraping) y 2 (salarios, población u otros) + "Gestión de datos en JSON o CSV". |
| HDFS | "Organiza originales y procesados y demuestra su recuperación" | NO es de esta fase. Nuestra capa (raw congelado + manifest + silver) es **la materia prima que se subirá**, pero el 10 exige HDFS real. |
| Kafka | "Productor y consumidor Python funcionan y procesan mensajes" | NO es de esta fase. |
| Integración | "Demuestra el flujo completo hasta MongoDB" | NO es de esta fase. `run_all` + `run_manifest.json` es integración intra-silver, no el flujo completo. |

### DOCX — checklist §17 + §6 (lo que SÍ nos toca)

- "Datos reales, procedencia explicable" → nos toca (acta + `_meta/` + `config/fuentes.yaml` + `docs/`).
- "Código organizado, ejecutable según README" → nos toca (`run_all`, tests, gate).
- "Conclusiones respaldadas, limitaciones reconocidas" → nos toca (núcleo de 28, cobertura declarada, proxy salarial declarado).
- **"La carga y limpieza se realizan utilizando operaciones de MongoDB" (§6) → es el único gap estructural real de esta fase.** Nuestra limpieza pandas es correcta como silver, pero ese item solo se cierra operando en Mongo. `docs/reglas_limpieza.md` (R1–R7 con operador Mongo equivalente) es el puente correcto, no la sustitución.

**Consecuencia:** un 10/10 "fase datos" significa 10/10 en Extracción RA1 + requisitos BDA/SBD de limpieza/CSV/JSON **en lo evaluable antes de Mongo**, con el item Mongo explícitamente marcado como "pendiente de fase, con reglas portables ya escritas". Cualquier informe que mezcle HDFS/Kafka/Mongo en la nota de esta fase está cambiando la rúbrica.

---

## 3. Claim-by-claim del informe 2026-11-01: coincido / matizo / discrepo

Leyenda: ✅ coincido · ⚠️ matizo (fondo ok, forma inexacta) · ❌ discrepo.

### 3.1 Tabla WP por WP

| WP (nombre del otro informe) | Su veredicto | Mi veredicto | Evidencia |
|---|---|---|---|
| WP-01 Orquestador declarativo | Parcial (falta DoD `test_run_all_orquesta_todos_los_scripts`) | ✅ coincido | `transform/run_all.py`: registro `SCRIPTS` con `group/in/out/out_glob`, Kahn, `EXCLUIDOS` con motivo, `--dry-run`. Conté ~40 entradas `group` (él dice 35; diferencia menor por cómo contar). No existe test que afirme "todo script no excluido está declarado". Su nombre de test propuesto no existe, pero el hueco sí existe. |
| WP-02 Un escritor dim gold | Done | ✅ coincido | Solo `construir_dim_gold.py` escribe `dim_municipios_enriquecido.csv`. |
| WP-03 `n_anuncios` real | Done (759/843) | ✅ coincido | Gate 06 del `verificar_fase_datos.py` lo afirma; `aplicar_cobertura_mercado.py` es el escritor declarado. |
| WP-04 Ceros/clip | Done | ✅ coincido | `corregir_empleo.py` (bruto/flag/mask) + gate 07. |
| WP-05 Brecha eliminada | Done | ✅ coincido | `brecha_ocupacion_actividad_pct` ausente en gold (gate 08 + `test_wp05_...`). |
| WP-06 Esfuerzo canónico | Done | ✅ coincido | `esfuerzo_joven_pct` en base y renta, gate 09 + 2 tests WP-06. |
| WP-07 Metadata única | Parcial (validación estricta solo en raw; tests ausentes) | ⚠️ matizo | El fondo es correcto: `extract/_common.py::guardar_json` exige `fuente, url, fecha_extraccion, n_registros, hash_sha256, version_parser` y **falla en raw** / avisa fuera de raw (`REQUIRED_METADATA`, `_es_raw`). Sidecars en `data/procesado/_meta/` (63 ficheros, ver §4). Pero "tests dedicados ausentes" es inexacto: existen `test_formato_metadatos_en_json`, `test_wp11_...`, `test_wp12_...` que tocan metadata; lo que falta es un test DoD específico "sidecar cubre todo JSON raw", no "ningún test". |
| WP-08 Manifests | Parcial (raw OK 314; silver stale 85 faltantes `_meta/*`) | ⚠️ matizo | Raw OK 314 **confirmado por inspección** (314 líneas = 316 ficheros − 2 excluidos; ver §6). Silver "85 errores" lo tomo como declarado (no re-ejecuté `--verify` para no tocar nada); la causa que apunta (silver manifest no incluye `_meta/*` generados después) es plausible y coherente con `EXCLUIDOS` de `generar_manifest.py` (excluye `manifest_sha256.txt` pero el desfase `_meta` es real). El número exacto 85 queda como no re-verificado. |
| WP-09 Nombres estables | Parcial (3 ficheros con timestamp) | ✅ coincido, con corrección al alza | Yo encuentro **5**, no 3: `anuncios_faltantes_fotocasa_batch1_20261029_230030_normalizado.json`, `anuncios_faltantes_pisos_batch1_20261029_230030_normalizado.json`, `anuncios_fotocasa_dirigido_20261029_223523_normalizado.json`, `anuncios_fotocasa_dirigido_20261029_normalizado.json`, `anuncios_pisos_dirigido_20261029_normalizado.json` (`ls data/procesado | grep -E "[0-9]{8}_"`). El hueco es real; el conteo del otro informe se queda corto. |
| WP-10 Lectura tipada | Parcial (transform OK por AST; extract 2 sin `dtype`) | ⚠️ matizo | Transform: `grep pd.read_csv transform/*.py | grep -v dtype=str` devuelve **vacío** → coincido (todo tipado). Extract: el 2.º caso citado (`_common.py`) es **falso positivo**: es `leer_csv_seguro` que hace `kwargs.setdefault("dtype", str)` + `zfill(5)` — es el helper correcto, no un hueco. Quedan como huecos reales: `extract/10_scraping_faltantes.py:52` (`pd.read_csv(csv_path)` sin dtype) y `extract/10_opendata_bizilagun_etxebide.py:236` con `dtype={0:str,1:str}` parcial (solo 2 columnas, resto inferido; para separador `;`/decimal `,` es riesgo menor pero real). O sea: 1 hueco claro + 1 parcial, no 2 huecos claros. |
| WP-11 Fallback Eustat | Missing (constantes silenciosas, sin `flag_ratio_fiscal`) | ✅ coincido en el fondo, matizo el alcance | `transform/calcular_renta_joven.py::_ratio_fiscal_desde_eustat` SÍ calcula desde `eustat_renta_edad.csv` (filtro `sexo==Total`, `Renta total`, `periodo==2024` como str) y el docstring declara `ratio_fiscal=(1599+8156+20109)/3/28170=0.353` como documentado, no silencioso. PERO el `except` implícito existe: `if ... is None: r18_19, r20_24, r25_29, rtotal = 1599, 8156, 20109, 28170` — fallback cableado **sin columna flag** que lo marque por municipio. El hueco real es "sin trazabilidad del fallback", no "todo constantes". |
| WP-12 Cobertura | Missing (`cobertura_anuncios.csv`, `nivel_fiabilidad`) | ✅ coincido | `ls data/procesado/cobertura*` → no existe; `grep -rn cobertura_anuncios|nivel_fiabilidad transform/ tests/ verificar_fase_datos.py` → **0 hits**. La regla R5 existe en `docs/reglas_limpieza.md` y `test_wp12_cobertura_mercado` existe, pero el artefacto de cobertura por municipio no existe. Hueco real y barato de cerrar. |
| WP-13 Higiene/docs | Parcial (`project.md` stale 314/96/59; `requirements.txt` sin hdfs) | ✅ coincido, +2 precisiones | `openspec/project.md:6` y `AGENT.md:9` dicen "314 / 96 / 59 tests" desactualizados (hoy: raw 314 manifest pero 195 en raíz; procesado 117 top-level; tests 47 funciones → ~77 casos con parametrización). `requirements.txt` verificado: **sin `hdfs`/`webhdfs`/`pyhdfs** (grep vacío). Precisión 1: el "96 silver" del project.md hoy es 117 en `data/procesado` top-level (o 115 manifest silver) — el doc está stale en ambas direcciones. Precisión 2: su "316/180/77" propuesto también está sin fuente; no lo adopto (ver §4). |
| WP-14 Gate | Done (15/15 exit 0) | ✅ coincido como declarado | `verificar_fase_datos.py` implementa 15 checks (leídos §§1–15). No re-ejecutado en esta contraauditoría por regla read-only; se audita el código del gate, que es sólido (manifest, gemelos `corregido`, índices `_meta`, dim 252, 759/843, ceros, brecha, esfuerzo, tensión, pytest, dry-run, población joven con `metodo`, tipología, raw-solo-lectura). |
| WP-15 `renta_origen` por fila | Missing (252/252 constante) | ✅ coincido, con corrección de ruta | El fichero vive en **`data/raw/renta_municipal_completa.csv`** (NO en procesado como dice el informe). Inspección: columnas incluyen `renta_origen` y `renta_joven_origen`; `value_counts → Eustat+INE_Atlas 252/252`. O sea: el hueco es real (origen constante, sin trazabilidad por fila) pero la ruta del informe es errónea. Existe además `test_renta_origen_transparente` en `test_crudos.py` — el DoD parcial ya está pensado. |
| WP-16 dim fuera de raw | Missing (7+ extractores leen `data/raw/dim_municipios.json`) | ✅ coincido (9, no 7+) | `grep -rln dim_municipios.json|dim_municipios.csv extract/` → **9 ficheros**: `09_fotocasa_dirigido, 10_scraping_faltantes, 19_udalmap_indicadores_adicionales, educacion_centros, entity_resolution, euskadi_geo, ine_atlas_renta, salud_centros, udalmap_empleo`. Más `dim_municipios.csv/json` físicamente en `data/raw/`. Es deuda taxonómica real (universo versionado dentro de raw). Cierres posibles: mover a `data/procesado/` + shim, o documentar como universo versionado (ver §7). |
| WP-17 Ingestion manifest | Missing | ✅ coincido | `ls data/raw/ingestion_manifest.json` → **no existe**. Existe `docs/raw_manifest_sha256.txt` (integridad) y `acta_ingesta.md` en `procesado/_meta/`, pero no el acta máquina-leíble de ingesta por fuente. |
| WP-18 Metadata salario | Missing (2 JSON sin `metadata`) | ⚠️ matizo fuerte | `data/raw/ovj_salario_joven_2024.json` SÍ tiene procedencia: claves `descripcion, fuente_url, fecha_extraccion, anio_fuente, n_filas, datos` (2 filas). Lo que falta es la **envoltura canónica** `{"metadata": {...}, "datos": [...]}` de `_common.guardar_json` (el fichero es plano con metadatos como hermanos, no como bloque `metadata`). Mismo patrón probable en `emancipacion_juventud_resumen.json` (no verificado campo a campo aquí). El hueco es de **formato canónico**, no de "sin procedencia". Arreglarlo como "añadir procedencia" duplicaría información; lo correcto es envolver/migrar al esquema WP-07. |
| WP-19 Archivar auditorías | Done | ✅ coincido | `openspec/audit/archivado/` existe (él dice 19 docs; no contado aquí por ser irrelevante para la nota). |
| WP-20 Reglas portables | Done | ✅ coincido | `docs/reglas_limpieza.md` R1–R7 con operador Mongo equivalente. Es el puente correcto hacia la fase Mongo. |

### 3.2 Problemas estructurales (su §3)

| Su afirmación | Veredicto | Comentario |
|---|---|---|
| Tests 77 vs ~85 previstos, faltan ~8 DoD (WP-01, 07, 08, 09, 10, 11, 12, 13) | ⚠️ fondo ok, número sin fuente | 47 funciones `def test_` (11 fase_datos + 24 contrato + 3 crudos + 5 guardrails + 4 inmutable). 77 casos vía parametrización (`test_nuevas_fuentes_*` × N) es plausible y coherente con "77 passed" declarado. **El "~85 previstos" no tiene fuente en el repo** (ningún plan fija 85). Lo correcto: "faltan DoD para WP-01/08/15/16/17/18; WP-09/10/11/12 SÍ tienen test (ver §3.1)". Su lista de "8 ausentes" mezcla WPs que sí tienen test (09, 10, 11, 12) con los que no. |
| Raw 59 JSON vs plan 60; sidecars 60 (uno extra) | ⚠️ no verificable aquí | `ls data/raw/*.json = 59` confirmado. El "plan 60" no se localiza en esta auditoría (ningún `config/fuentes.yaml` fija 60). `data/procesado/_meta/` = 63 ficheros (sidecars + `index.json` + `csvs_index.json` + `acta_ingesta.md`...). Sin el plan que diga 60, el "uno extra" no es hallazgo. |
| `run_all --check`: 7 stale + 1 sin declarar | ✅ como declarado | No re-ejecutado (read-only). La causa que apunta (reescrituras in-place de `dim_municipios.csv` y `anuncios_unificados.csv` que vuelven stale a downstream: `aplicar_cobertura_mercado` y `deduplicar_alquiler_enriquecido` declaran el mismo fichero como in y out) es **visible en el código** (`run_all.py`: `aplicar_cobertura_mercado: in proc:dim_municipios.csv → out proc:dim_municipios.csv`; `deduplicar...: in/out alquiler_municipal_enriquecido.json`). Es deuda de modelado del DAG, no corrupción de datos. |
| Silver manifest no verifica; 3 timestamps; 2 lecturas sin dtype en extract | ⚠️ ver arriba | Timestamps son 5 (§3.1 WP-09). Lecturas sin dtype son 1+1 parcial (§3.1 WP-10). Silver manifest: declarado, no re-verificado. |
| Docs de inventario desactualizados (`AGENT.md`, `project.md`) | ✅ coincido | Ver §3.1 WP-13. Ambas dicen "59 tests" cuando hay 47 funciones / ~77 casos; "96 silver" cuando hay 117 top-level / 115 manifest; "314" sin explicar raíz vs recursivo. |

### 3.3 Infraestructura (su §4)

| Su afirmación | Veredicto |
|---|---|
| No existe `storage/`, `analysis/`, `visualization/`, `notebooks/`, `docker-compose.yml`, `plan/arquitectura.md`, `transform/limpieza.py`, `transform/enrich.py` | ✅ coincido (verificado con `ls`: todos ausentes). Matiz: `transform/limpieza.py`/`enrich.py` ausentes **como nombres**, pero existen equivalentes funcionales (`limpiar_*.py`, `corregir_*.py`, `imputar_*.py`, `enriquecer_*.py`, `filtrar_outliers.py`). Pedir los ficheros por nombre literal es rigor mortis; lo que falta es la fase, no esos dos nombres. |
| `pymongo` + `kafka-python-ng` presentes; sin cliente HDFS; Docker disponible sin compose en repo | ✅ coincido (`requirements.txt` leído: `pymongo==4.17.0`, `kafka-python-ng==2.2.3`, sin `hdfs`). Docker no verificado aquí (no procede en read-only de repo). |

### 3.4 Conclusiones y próximos pasos (sus §5–6)

- Conclusión 1 ("datos sustancialmente hechos pero no cerrados") → ✅.
- Conclusión 2 ("reproducible pero no verificable con `--check`") → ✅ como declarada.
- Conclusión 3 ("infra no empezada") → ✅ factualmente, ⚠️ en encuadre (no es de esta fase).
- Conclusión 4 ("cerrar WPs antes de infra") → ✅, con el orden de §7 (primero lo que afecta nota de esta fase).
- Pasos A–E → ✅ en espíritu; corrijo B (sus cifras "316/180/77" tampoco tienen fuente; hay que contar de verdad antes de escribir) y C (reordenar el DAG in-place requiere decidir si se permite in-place o se parte en `_v1/_v2`; no es solo "reordenar").

---

## 4. Hallazgos propios (organizados por severidad, solo fase datos)

### Críticos (impiden el 10 en esta fase si el tribunal mira trazabilidad)

**C-1. `renta_origen` constante por fila (WP-15).** `data/raw/renta_municipal_completa.csv`: 252/252 `Eustat+INE_Atlas`. El tribunal que abra el CSV verá una columna de procedencia que no discrimina nada. Además vive en raw con nombre de "completa" (mezcla de fuentes + estimación joven) — taxonómicamente es silver con nombre raw. Cierre: añadir `renta_joven_origen`-style por fila (qué tramo vino de Eustat/Atlas/imputación) o, mínimo, documentar la fórmula por fila en `acta_ingesta` + test. Existe `test_renta_origen_transparente` como gancho.
**C-2. Sin artefacto de cobertura por municipio (WP-12).** No existe `cobertura_anuncios.csv` ni `nivel_fiabilidad`. Con 759 únicos sobre 252 municipios la media es ~3/municipio: el tribunal preguntará "¿qué municipios tienen mercado observable y cuáles son extrapolación?". `aplicar_cobertura_mercado.py` calcula el recuento pero no lo publica como tabla auditable. Cierre barato, impacto alto en credibilidad.

### Altos (bajan nota de buenas prácticas / reproducibilidad)

**A-1. Nombres con timestamp en silver (WP-09).** 5 ficheros `*20261029*_normalizado.json` en `data/procesado/`. Rompen idempotencia nominal (cada re-ingesta crea nombres nuevos) y el manifest silver. Cierre: renombrar a canónicos + mapa de equivalencia, o declararlos `out_glob` con política de retención.
**A-2. `dim_municipios.*` dentro de raw leído por 9 extractores (WP-16).** `data/raw/dim_municipios.csv/json` + 9 lectores en `extract/`. Raw debe ser solo observado; el universo de 252 es construido/versionado. Cierre: mover a `data/procesado/dim_municipios.csv` (generado por `transform/dim_municipios.py`) y dejar en raw solo un `universo_252.v1.json` congelado con nota, o documentar la excepción como "universo versionado, no observado". Sin esto, cualquier `--check` limpio es imposible por diseño.
**A-3. Reescrituras in-place en el DAG (causa del `--check` rojo).** `aplicar_cobertura_mercado` (dim→dim) y `deduplicar_alquiler_enriquecido` (json→json) declaran el mismo fichero como entrada y salida. Con staleness por mtime, downstream siempre parece stale. Cierre: partir en `_raw`→`_v2` o cambiar `--check` a comparación por hash de contenido en vez de mtime para nodos in-place.
**A-4. Fallback fiscal sin flag (WP-11).** `_ratio_fiscal_desde_eustat` cae a `(1599, 8156, 20109, 28170)` si falta un tramo, sin columna que lo marque. Hoy funciona (el CSV trae los tramos), pero el tribunal que lea el `if ... is None` verá "constantes mágicas". Cierre: `flag_ratio_fiscal=calculado|fallback` + test.
**A-5. Sin `ingestion_manifest.json` máquina-leíble (WP-17).** Existe acta humana (`procesado/_meta/acta_ingesta.md`) y manifest de integridad, pero no el inventario por fuente (qué script, qué URL/ID, cuándo, cuántas filas, qué hash). Es lo que permite decir "759 anuncios vienen de aquí y aquí". Cierre: generarlo desde `normalizar_metadata.py` + `_meta/`.

### Medios (higiene, docs, tipos)

**M-1. Un `read_csv` sin `dtype` en extract + uno parcial.** `10_scraping_faltantes.py:52` (`pd.read_csv(csv_path)` sobre `anuncios_unificados.csv`: `codigo_ine` `01001` → `1001` si se infiere entero; además lee `PROC` desde `extract/` rompiendo la dirección del flujo). `10_opendata_bizilagun_etxebide.py:236` tipa solo 2 columnas. Transform está limpio (todo `dtype=str` + `to_numeric` explícito + `zfill(5)`).
**M-2. Docs de estado stale.** `openspec/project.md:6` ("314/313 manifest, 96 silver, 59 tests, fecha 2026-10-29") y `AGENT.md:9` ("314, 96, 59 tests") desactualizados. Riesgo: el tribunal lee el doc, cuenta otra cosa y descuenta "rigor documental".
**M-3. Salario: formato no canónico (WP-18).** `ovj_salario_joven_2024.json` trae procedencia pero fuera de la envoltura `{"metadata","datos"}` que exige `_common.guardar_json`. Un validador estricto WP-07 lo rechazaría si se re-ingestara hoy. Cierre: migrar a envoltura canónica (no duplicar campos).
**M-4. `requirements.txt` sin cliente HDFS.** Correcto como hallazgo, **pero no es de esta fase**: añadir `hdfs` ahora sin Docker HDFS no sube nota de datos. Va al plan de infra, no al cierre de datos.

### Bajos (no bajan nota, no tocar ahora)

**B-1. `parsear_secciones.py` marcado erróneamente.** Escribe con `encoding="utf-8-sig"` en ambas salidas (líneas 66–72). El grep de una línea del otro informe lo marcó por no ver la continuación. No tocar.
**B-2. `_common.py` marcado erróneamente.** `leer_csv_seguro` es el helper correcto (`dtype=str` + `utf-8-sig` + `zfill`). No tocar.
**B-3. Nombres `transform/limpieza.py`/`enrich.py` ausentes.** Equivalentes existen con otros nombres. Pedir esos literales es nominalismo; no crear shims vacíos para contentar al informe.
**B-4. `legacy_obsoleto_no_usar/` y `html_fotocasa/` dentro de raw.** Están en el manifest (forman parte de los 314). Si son realmente legacy, excluirlos del manifest con justificación; si son evidencia de scraping, renombrar la carpeta (el nombre "no_usar" invita al tribunal a preguntar por qué cuenta como raw).

---

## 5. Buenas prácticas: qué está bien (y el informe anterior no valora)

1. **Raw inmutable de verdad:** `.FROZEN`, `test_raw_congelado_marker`, `test_raw_hashes_manifest`, `test_raw_manifest_complete`, `_raw_guard.py`, gate 01–02. Pocos proyectos de aula tienen esto.
2. **Lectura tipada sistemática en transform** (`dtype=str` + `pd.to_numeric(errors="coerce")` + `zfill(5)`): es la práctica correcta contra el "cero de Álava" (`01001`→`1001`). El informe anterior lo registra como parcial; en transform es total.
3. **Reglas de limpieza portables a Mongo (R1–R7)** con test asociado por regla. Es exactamente lo que permite defender "la limpieza pandas es silver; la de Mongo será la misma regla" ante el §6 del DOCX.
4. **Orquestador declarativo con Kahn + manifest + dry-run.** La deuda in-place (§4 A-3) no invalida el diseño; es mejor que 44 scripts sueltos.
5. **`config/fuentes.yaml` con IDs de tabla Eustat verificados** + `entity_resolution` para las tres capitales. Trazabilidad de fuentes por encima del mínimo.

---

## 6. Raw inmutable: ¿hay que regenerarlo? No

- **No regenerar.** Los 314 del manifest cuadran: 316 ficheros recursivos − 2 excluidos (`.FROZEN`, `.gitkeep`) = 314. El "195" es solo la raíz; los 121 restantes están en `gtfs/`, `html_fotocasa/` (+2 subcarpetas), `legacy_obsoleto_no_usar/`, `shp_euskadi/`.
- **Lo único a decidir sobre raw:** (a) si `legacy_obsoleto_no_usar/` debe seguir en el manifest o excluirse con acta; (b) si `dim_municipios.*` se queda como "universo versionado" documentado o se mueve a silver con shim. Ambas son decisiones de 1 línea + acta, no regeneración.
- **Riesgo si se regenera:** se invalidan hashes, sidecars, índices y el `.FROZEN`; se pierde la cadena de custodia que hoy es el mejor activo del proyecto. Cualquier cierre WP-11/12/15/17/18 debe escribir en `data/procesado/` + `docs/` + `procesado/_meta/`, jamás en `data/raw/`.

---

## 7. Plan mínimo para el 10/10 de ESTA fase (sin inflar)

Ordenado por impacto en nota / esfuerzo. Todo en silver + docs + tests; nada toca raw.

1. **WP-12:** publicar `data/procesado/cobertura_anuncios.csv` (`codigo_ine, n_crudo, n_unico, fuente_mix, nivel_fiabilidad`) desde `aplicar_cobertura_mercado.py` + test. (Cierra C-2.)
2. **WP-15:** `renta_origen` por fila de verdad (qué tramo es Eustat/Atlas/imputado) o acta que lo derive + `test_renta_origen_transparente` en verde estricto. (Cierra C-1.)
3. **WP-17:** `data/raw/ingestion_manifest.json`… no: en `data/procesado/_meta/ingestion_manifest.json` (raw no se toca) o `data/raw/` solo si el congelado lo permite por acta — por defecto, en `_meta/` + referencia en acta. (Cierra A-5.)
4. **WP-11:** `flag_ratio_fiscal` (+ `metodo` ya existe en población joven; extender el patrón) + test. (Cierra A-4.)
5. **WP-18:** migrar los 2 JSON de salario/emancipación a envoltura `{"metadata","datos"}` canónica. (Cierra M-3.)
6. **WP-16:** decisión documentada + shim (mover o declarar universo). (Cierra A-2.)
7. **WP-09 + A-3:** renombrar timestamps a canónicos (con mapa) y partir los 2 nodos in-place (o hash-based `--check`). (Cierra A-1/A-3.)
8. **M-1/M-2:** `dtype=str` en `10_scraping_faltantes.py:52` (+ no leer `PROC` desde `extract/`); completar `dtype` en `10_opendata…:236`; actualizar `project.md` + `AGENT.md` contando de verdad (raíz vs recursivo vs manifest, funciones vs casos).
9. **Re-verificación:** `run_all` completo + `pytest` + gate 15/15 + `generar_manifest --verify` (raw OK, silver OK tras 1–8). Solo entonces declarar 10/10 de fase.

Fuera de esta fase (no mezclar en la nota de datos): HDFS + `hdfs` en requirements, `docker-compose.yml`, `storage/`, Kafka productor/consumidor, Mongo + PyMongo + Aggregation, `analysis/`, `visualization/` desde PyMongo, informe y demo. El tribunal los puntúa en sus criterios propios.

---

## 8. Anexos — evidencias (rutas y comandos de solo lectura)

- Fuentes: `archivosReto/RETO 1Evaluacion SBD-BDA.pdf`, `archivosReto/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx`.
- Informe auditado: `openspec/audit/verificacion_fase_datos_2026-11-01.md` (§§1–6).
- Orquestador: `transform/run_all.py` (cabecera + `SCRIPTS` + `EXCLUIDOS` + `--dry-run/--check`).
- Metadata: `extract/_common.py::REQUIRED_METADATA`, `guardar_json`, `leer_csv_seguro`, `_es_raw`.
- Manifests: `docs/raw_manifest_sha256.txt` (314), `data/procesado/manifest_sha256.txt` (115), `extract/generar_manifest.py` (`EXCLUIDOS`, `_inventario`, `_verificar`).
- Gate: `verificar_fase_datos.py` (checks 01–15).
- Reglas: `docs/reglas_limpieza.md` (R1–R7).
- Contrato: `openspec/specs/contrato-reto/spec.md` (rúbrica transcripta).
- Estado docs: `openspec/project.md:6`, `AGENT.md:9`, `config/fuentes.yaml`, `requirements.txt`.
- Conteos: `ls data/raw | wc -l` (=195 raíz), `ls data/raw/*.json | wc -l` (=59), `ls data/raw/*.csv | wc -l` (=123), `ls data/procesado/_meta | wc -l` (=63), `find data/raw -type d` (`gtfs`, `html_fotocasa`, `legacy_obsoleto_no_usar`, `shp_euskadi`), `find data/raw -type f | wc -l` (=316).
- Timestamps: `ls data/procesado | grep -E "[0-9]{8}_"` (5 ficheros, §3.1 WP-09).
- Tipos: `grep -rn pd.read_csv extract/*.py` (hueco `10_scraping_faltantes.py:52`; parcial `10_opendata…:236`; `_common.py:161` es helper correcto); `grep -rn pd.read_csv transform/*.py | grep -v dtype=str` (vacío); `transform/parsear_secciones.py:66-72` (ambos `to_csv` con `utf-8-sig`).
- Traza: `grep -rln dim_municipios.json|dim_municipios.csv extract/` (9 ficheros); `data/raw/dim_municipios.*` existen; `ls data/raw/ingestion_manifest.json` (no existe); `ls data/procesado/cobertura*` (no existe); `grep -rn cobertura_anuncios|nivel_fiabilidad` (0 hits); `ls -d storage analysis visualization notebooks docker-compose.yml` (ausentes); `grep -in hdfs requirements.txt` (vacío).
- Renta/salario: `data/raw/renta_municipal_completa.csv` (`renta_origen=Eustat+INE_Atlas 252/252`); `transform/calcular_renta_joven.py:33-54` (fallback sin flag); `data/raw/ovj_salario_joven_2024.json` (claves `descripcion, fuente_url, fecha_extraccion, anio_fuente, n_filas, datos`, sin bloque `metadata`).
- Tests: `def test_` = 47 funciones (11+24+3+5+4); 77 casos declarados por parametrización (`test_nuevas_fuentes_*`); "~85 previstos" sin fuente en repo.
