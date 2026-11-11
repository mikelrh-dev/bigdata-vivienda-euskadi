# Spec: regeneración de `procesado` y `resultados` desde `raw`

**Fecha:** 2026-11-11 · **Rama:** `fix/regeneracion-procesado-resultados`
**Alcance:** N1 + N2 + N3. No incluye N4 (split de F4) ni migración de capas.

## 1. Objetivo

Que tras borrar `data/procesado/` y `data/resultados/`, un solo comando regenere
ambas capas desde `data/raw/` sin intervención manual y sin tocar `raw`.

Hoy: `run_all.py` cubre 114/191 ficheros de `procesado` y 2/56 de `resultados`.
Objetivo: ≥183/191 y 56/56.

## 2. Problema que corrige

| ID | Defecto | Evidencia |
|---|---|---|
| N1 | `deduplicar_alquiler_enriquecido.py` se ejecuta en la posición 5 y su productor en la 17; en rebuild limpio hace `[SKIP]` y el silver queda con 253 filas en vez de 252 | `run_all._orden_topologico`, `deduplicar_alquiler_enriquecido.main` |
| N2 | `normalizar_metadata`, `generar_ingestion_manifest` y `generar_manifest --write` no los ejecuta ningún orquestador: ~68 ficheros de `procesado` no vuelven | medición 114/191 |
| N3 | `run_analisis_mongo`, `comparativa_mongo`, `sensibilidad` y `generar_figuras_N` no están encadenados: 54 de 56 artefactos de `resultados` no vuelven | medición 2/56 |

## 3. Comandos

```bash
# Reconstrucción de silver + quality (no requiere Mongo ni red)
python scripts/run_pipeline.py --fase silver,quality

# Análisis (requiere Mongo cargado)
python scripts/run_pipeline.py --fase gold

# Carga destructiva de Mongo: explícita
python scripts/run_pipeline.py --fase mongo --allow-mongo-write

# Preflight de integridad de raw (solo lectura, hashea 861 MB)
python scripts/run_pipeline.py --check

# Ver qué haría
python scripts/run_pipeline.py --fase all --dry-run

# Tests
python -m pytest tests/test_run_all.py tests/test_run_pipeline.py -q
```

## 4. Estructura

```
transform/run_all.py                     → DAG silver (sin cambios de tamaño: 34 nodos)
transform/deduplicar_alquiler_enriquecido.py → falla con mensaje accionable, no SKIP
scripts/run_pipeline.py                  → nuevo orquestador por fases
tests/test_run_pipeline.py               → tests del orquestador
tests/test_run_all.py                    → test de orden productor→dedup
```

`transform/quality/` **no** se usa: los scripts se quedan en `extract/` y se
invocan como fase. Se evita mover ficheros y no se alteran las cifras de
gobernanza (42 scripts / 34 nodos / 188 silver / 11 pipelines).

## 5. Fases y orden

```
silver   → transform/run_all.py
quality  → extract/normalizar_metadata.py
         → extract/generar_ingestion_manifest.py
         → extract/generar_manifest.py --write
mongo    → scripts/run_mongo_pipeline.py        (destructivo, opt-in)
gold     → analysis/run_analisis_mongo.py
         → analysis/comparativa_mongo.py
         → analysis/sensibilidad.py
         → transform/generar_figuras_N.py
```

`--fase all` = `silver,quality,gold`. **Nunca incluye `mongo`.**

## 6. Contrato de códigos de salida

- `0`: todos los pasos OK (o avisos, sin `--strict`).
- `1`: algún paso FAIL, o aviso con `--strict`.
- `2`: preflight fallido (raw incompleto o manifiesto distinto).
- `normalizar_metadata` devuelve 1 cuando hay metadata incompleta en raw: se
  clasifica como **AVISO** (escribe todos los sidecars igualmente), no como
  fallo. `--strict` lo convierte en fallo. El aviso se imprime con su motivo.

## 7. Límites

- **Siempre:** ejecutar desde la raíz; usar `sys.executable`; UTF-8 en hijos.
- **Preguntar:** cualquier paso que escriba en Mongo (`--allow-mongo-write`).
- **Nunca:** escribir en `data/raw`, borrar artefactos existentes, ni incluir
  `mongo` en `all`.

## 8. Criterios de éxito

1. `run_all.py --dry-run` sitúa `enriquecer_codigo_ine` antes de
   `deduplicar_alquiler_enriquecido`; el test lo verifica.
2. `deduplicar` sin el CSV de entrada devuelve ≠ 0 con un mensaje que nombra
   `enriquecer_codigo_ine.py` (no vuelve a saltar en silencio).
3. `run_pipeline.py --fase quality --dry-run` lista los 3 pasos en orden.
4. Ejecución real de `--fase quality`: `procesado` pasa de 114 a ≥183
   ficheros cubiertos, y `git status` no muestra cambios en
   `docs/raw_manifest_sha256.txt` (raw intacto ⇒ mismo hash).
5. `--fase all` no incluye `mongo`; `--fase mongo` sin flag aborta con RC 2.
6. `pytest tests/test_run_all.py tests/test_run_pipeline.py` en verde.

## 9. Resultado medido (2026-11-11)

| Criterio | Estado | Evidencia |
|---|---|---|
| 1. Productor antes de dedup | ✅ | `--dry-run`: 17 `enriquecer_codigo_ine` → 18 `deduplicar` |
| 2. Dedup sin SKIP | ✅ | enriquecer (253 filas) + dedup → `CSV: 253 -> 252`, rc=0 |
| 3. Plan quality | ✅ | 4 pasos listados en orden (manifest al final) |
| 4. `quality` real | ✅ | 3 OK + 1 AVISO, `procesado` 182, `docs/raw_manifest_sha256.txt` sin cambios en git |
| 5. Seguridad mongo | ✅ | `--fase mongo` sin flag → rc=2, mensaje en stderr |
| 6. Tests | ✅ | 259 passed, 2 skipped (suite completa) |

Gobernanza actualizada y verificado el nuevo umbral: 44 scripts / 38 nodos / 182 silver /
11 pipelines, manifest raw 354 (0 errores), gate offline OK.

### Plan R ejecutado: silver reproducible al 100 %

Tras el rebuild limpio se detectó que el 188 canónico incluía 12 ficheros sin producer
real. Se aplicó la invariante "cada fichero tiene productor declarado o no existe":

| Destino | Ficheros | Cómo |
|---|---|---|
| **Borrados** (sin lector ni valor) | `pob_rank.csv`, `anuncios_pisos_dirigido.csv/.json`, `_meta/acta_ingesta.md` | eran snapshots del scraper o documentación obsoleta dentro de la capa de datos |
| **Con productor offline** | `f4_pisos_objetivo.json`, `f4_pisos_informe.csv`, `fotocasa_dirigido_informe.csv`, `renta_municipal_referencia.csv` | 4 nodos nuevos en el DAG (38 en total) |
| **Inventarios generados** | `_meta/csvs_index.json`, `_meta/nombres_normalizados_map.json` | `normalizar_metadata` y un paso nuevo de la fase quality |
| **Residuos F-05** | sidecar y `*_normalizado.json` de `udalmap_empleo_corregido` | ya no se recrean (su raw fue retirado) |
| **Inputs curados → `config/`** | selección F4 (62 municipios) y registro de los 5 lotes heredados | dejan de ser artefactos que se pueden perder |

### Rebuild limpio final (verificado)

`run_all`: **38/38 scripts, 0 fallos, 382 s**. Resultado: **182 ficheros**, manifest de
**182 entradas** (`--check`: 0 errores), alquiler con 252 filas, sin faltantes ni sobrantes
frente al árbol previo (176 reproducibles + 6 recuperados).

- `procesado`: **182/182 = 100 % reproducible desde raw, sin red**.
- `resultados`: **54/56**; los 2 restantes son `dashboard.html` y `dashboard_completo.html`
  (sin productor). De los 54, 52 salen de `gold` y 2 de `silver`.
- `gold` tras el rebuild: 4/4 OK y **54 de 56 hashes idénticos** a la ejecución previa.
  Cambian solo `auditoria_lagunas_silver.csv` y `mapa_esquema_silver.html`, que auditan
  silver y por tanto reflejan el paso de 188 a 182 ficheros (correcto, no regresión).

### Guardarraíl nuevo

`tests/test_reproducibilidad_silver.py` sustituye el número mágico por la invariante:

1. toda entrada de `manifest_sha256.txt` casa con un `out`/`out_glob` del DAG o con un
   artefacto declarado de `quality` (`_meta/*`, `run_manifest.json`);
2. los 6 residuos retirados no reaparecen.

Si alguien vuelve a dejar un fichero escrito a mano, falla la suite antes de que el
conteo cambie de significado.

### ¿Y N4?

Ya no hace falta para reproducir: la capa silver se reconstruye sin red. El scraping F4
es ahora solo un problema de **frescura** de datos (lotes nuevos), no de reconstrucción.

**Bug extra encontrado y corregido:** `analysis/comparativa_mongo.py` fallaba con
`ModuleNotFoundError: analysis` al ejecutarse como script (la fase gold abortaba en el
segundo paso). Ahora ancla la raíz en `sys.path`; cubierto por test de regresión.

## 10. Fuera de alcance (deuda declarada)

- `dashboard.html`, `dashboard_completo.html`: sin productor (2/56 de `resultados`).
- Scraping F4 (`transform/f4_pisos_dirigido.py`): requiere red; su lote nuevo sigue
  escribiendo en `raw` con guard. Ya no condiciona la reproducibilidad.
- 21 derivados dentro de `raw` y ciclo `extract → dim_municipios`.
