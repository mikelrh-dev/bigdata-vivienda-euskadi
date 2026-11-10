# Rebuild de `transform/run_all.py` — auditoría de los 4 fallos, `_meta` y recuento de resultados

**Fecha:** 2026-11-10 · **Naturaleza:** diagnóstico + corrección de código (no se tocó `data/raw`, no se ejecutó Mongo)
**Pregunta:** el rebuild desde raw deja 30/34 pasos OK y 4 en rojo, y en `data/resultados/` «solo» se regeneran 39 artefactos. ¿Son fallos reales, son evitables, y qué es `data/procesado/_meta`?
**Respuesta:** 3 de los 4 fallos son **declaraciones erróneas del DAG** (el orquestador ordena por `in`/`out` declarados, no por lo que el script lee) y 1 es una línea **dependiente de la versión de pandas**. Los cuatro están corregidos y verificados. Los 39 de resultados **no son una pérdida**: son exactamente la ruta Mongo, que no se ejecutó.

---

## 1. Resumen de hallazgos

| ID | Sev. | Dónde | Qué pasaba | Estado |
|---|---|---|---|---|
| F-01 | P1 | `transform/deduplicar_alquiler_enriquecido.py` | Nodo *in-place* sobre `alquiler_municipal_enriquecido.csv/.json`, artefacto que **ningún paso produce** y que está **gitignorado**: en un rebuild limpio no existe → `FileNotFoundError` | **Corregido** (se salta con exit 0) |
| F-02 | P1 | `transform/generar_cert_energetico_municipal.py` | `merged["cert_moda"].fillna(None)`: en pandas < 3 lanza `ValueError: Must specify a fill 'value' or 'method'`; era un **no-op** | **Corregido** (línea eliminada) |
| F-03 | P1 | `transform/run_all.py` | `generar_cert_energetico_moda_municipio.py` declaraba `in: []`, así que el DAG no tenía arista hacia su entrada real → fallo en cascada del anterior | **Corregido** (arista declarada) |
| F-04 | P1 | `transform/run_all.py` | `generar_anuncios_residencial_filtrado.py` declaraba leer `anuncios_unificados.csv`, pero lee `anuncios_vivienda_residencial.csv` (de `generar_vistas_mercado.py`, que corría **después**) → `[ERROR] No existe` en rebuild limpio | **Corregido** (entrada real declarada) |
| F-05 | P2 | `data/procesado/_meta/` | 62 sidecars para 61 JSON de raw: `udalmap_empleo_corregido.json.meta.json` es residuo de un derivado retirado de raw (WP-08). Ningún check lo detecta | Documentado |

Severidad P1 = rompe el rebuild extremo a extremo (no la demo, porque en el árbol actual los artefactos existían y el paso pasaba).

---

## 2. F-01 · El paso de deduplicación no es reproducible desde raw

**Evidencia (ejecutada).** Con el artefacto retirado (simulando rebuild limpio) el script termina en:

```
FileNotFoundError: [Errno 2] No such file or directory:
'...\data\procesado\alquiler_municipal_enriquecido.csv'
```

Y con el artefacto presente funciona (`CSV: 253 -> 252`, `JSON: 253 -> 252`).

**Por qué es deuda, no un fallo de datos:**

1. **Nadie lo produce.** Ningún `out` de `SCRIPTS` genera `alquiler_municipal_enriquecido.*`; el paso es in-place (`in == out`).
2. **Nadie lo consume.** `storage/load_mongo.py::load_alquiler()` lee `alquiler_municipal_completo.csv` (salida de `completar_alquiler_comarca.py`). Los artefactos «enriquecidos» solo aparecen en documentos históricos de `openspec/`.
3. **No sobrevive a un clon.** `data/procesado/*` está gitignorado (`.gitignore:18`), así que el par 253 filas existía solo en la copia local de quien ya lo había generado.

**Corrección aplicada.** El script comprueba la existencia y sale con 0:

```
[SKIP] No existe alquiler_municipal_enriquecido.csv: paso heredado sin productor, nada que deduplicar
```

**Se mantiene el nodo en `SCRIPTS`** para no alterar las cifras canónicas que vigila la gobernanza (42 scripts / **34 nodos DAG**). Convertirlo en exclusión formal exige actualizar `scripts/verificar_gobernanza.py` (assert `dag == 34`) y las menciones «34 DAG» de README/docs: es una decisión de equipo, no un arreglo silencioso.

**Efecto colateral detectado (P2).** `data/procesado/manifest_sha256.txt` (188 entradas) **incluye** los dos ficheros heredados:

```
68:a19abf7d…  alquiler_municipal_enriquecido.csv
69:08d81020…  alquiler_municipal_enriquecido.json
```

Un rebuild limpio no puede reproducir el manifest de 188 porque 2 de sus entradas dependen de un artefacto sin productor. O se regenera el manifest sin ese par, o se documenta como «silver histórico no reproducible».

---

## 3. F-02 · `fillna(None)` y el desajuste de versión de pandas

**Evidencia.** `requirements.txt` fija `pandas==2.2.3`; el `.venv` real ejecuta **pandas 3.1.0** (mismo patrón que el desajuste ya registrado en H-14 para pytest). Comprobado en esta máquina:

- pandas **3.1.0**: `Series.fillna(None)` se acepta → el script **termina con exit 0** y produce 252 filas.
- pandas **2.2.3** (la versión declarada, la que tenía el compañero): `fillna(None)` sin `value`/`method` es error de API → `ValueError`, que es el fallo reportado.

Por eso el fallo **no era reproducible aquí**: no era un problema de datos ni de rutas, era de entorno.

**Corrección aplicada.** Se elimina la línea. Era semánticamente vacía: rellenar con `None` no rellena nada y el `NaN` del `merge(how="left")` ya se serializa como celda vacía. El resultado es idéntico en ambas versiones y deja de depender del pin.

**Recomendación (no aplicada).** Alinear el pin: o `requirements.txt` sube a la versión que usa el equipo, o el `.venv` se recrea desde `requirements.txt`. Mientras convivan 2.2.3 y 3.1.0, cualquier rebuild puede dar resultados distintos en la misma máquina.

---

## 4. F-03 · Cascada del certificado energético

`generar_cert_energetico_moda_municipio.py` solo copia dos columnas de `cert_energetico_municipal_252.csv` y ya devolvía exit 1 con mensaje claro si faltaba. El problema no era el script sino la declaración: `in: []` en `run_all.py` impedía que el orden topológico lo colocara detrás de su productor. Ahora la arista existe y el orden es determinista: `cert_energetico_municipal` (19) → `cert_energetico_moda_municipio` (20).

También se declaró la entrada real del municipal (`raw:certificados_energeticos_*_completo.csv` + `proc:dim_municipios.csv`), que antes era `in: []` pese a leer la dim: la arista garantiza que corre **después** de `aplicar_cobertura_mercado.py`, que reescribe `dim_municipios.csv`.

---

## 5. F-04 · El paso que corría antes que su propia entrada

Cadena causal exacta:

1. `generar_anuncios_residencial_filtrado.py` lee `PROC/anuncios_vivienda_residencial.csv`.
2. Ese fichero lo escribe `generar_vistas_mercado.py` (segunda salida de las tres que declara).
3. Pero en `SCRIPTS` el *filtrado* estaba declarado **antes** que las *vistas* y con `in: ["proc:anuncios_unificados.csv"]`.
4. Sin arista hacia las vistas, el desempate estable del Kahn respetó el orden del diccionario: **31 filtrado → 32 vistas**. En el árbol local pasaba porque el CSV existía de una ejecución previa; en rebuild limpio, `[ERROR] No existe …/anuncios_vivienda_residencial.csv`.

Es el fallo más peligroso de los cuatro porque **no siempre se manifiesta**: el paso «funciona» hasta que se reconstruye desde cero, y `--check` tampoco lo detecta (solo compara mtimes de las entradas *declaradas*, y la declarada era la equivocada).

**Corrección aplicada.** `in: ["proc:anuncios_vivienda_residencial.csv"]`. Orden verificado: **31 vistas → 32 filtrado**.

---

## 6. Qué es `data/procesado/_meta` (pregunta de Mikel)

**No es silver y no lo genera `run_all.py`.** Es la **capa de procedencia de la ingesta** (WP-07/WP-17): vive bajo `procesado` por convenio de ruta, pero la escriben dos scripts de `extract/`.

| Fichero | Contenido | Lo escribe | Lo lee |
|---|---|---|---|
| `*.meta.json` (62) | Un sidecar por JSON de raw con los 6 campos obligatorios (`fuente`, `url`, `fecha_extraccion`, `n_registros`, `hash_sha256`, `version_parser`) + `completa`, `incidencias`, `n_registros_detalle` | `extract/normalizar_metadata.py` | `scripts/verificar_fase_datos.py` (checks 03/04), `tests/test_fase_datos.py` |
| `index.json` | `n_ficheros: 61`, `completos: 22`, array `ficheros[]` con el estado de cada JSON | `extract/normalizar_metadata.py` | check 03 |
| `csvs_index.json` | Inventario de los **129** CSV de raw | `extract/normalizar_metadata.py` | check 04 |
| `ingestion_manifest.json` | Acta legible por máquina: **354** fichas con bytes + SHA-256 de todo raw | `extract/generar_ingestion_manifest.py` | gobernanza / trazabilidad |
| `acta_ingesta.md` | Acta legible por personas | manual + manifest | documentación |
| `nombres_normalizados_map.json` | Mapa de normalización de nombres de municipio | pipeline de ingesta | checks y joins |

**Estado real hoy:** cobertura completa (61/61 JSON con sidecar, 129/129 CSV indexados, 354 fichas en el acta).

**Trampa para el rebuild (importante).** Como `_meta` cuelga de `data/procesado/`, un «borro procesado y regenero» **destruye la procedencia** y deja `verificar_fase_datos.py` (checks 03/04) y `tests/test_fase_datos.py` fallando con `FileNotFoundError`, además de perder `ingestion_manifest.json` (que no se recalcula en `run_all`). Si se hace rebuild limpio, hay que re-ejecutar antes:

```bash
.venv/Scripts/python.exe extract/normalizar_metadata.py
.venv/Scripts/python.exe extract/generar_ingestion_manifest.py
```

**F-05 (P2).** Hay **62 sidecars para 61 JSON**: sobra `udalmap_empleo_corregido.json.meta.json`, residuo de cuando ese derivado vivía en raw (el check 02 prohíbe «corregido» en raw y ya no está). `index.json` cuenta 61 y el check 03 cuadra, así que **nadie detecta el sidecar huérfano**. Borrarlo es inocuo; conviene además que el check compare sidecars contra `index.json`, no solo el total.

---

## 7. Por qué en `data/resultados/` «solo» salen 39 (+ anexo)

Recuento verificado de las **50 entradas** del directorio (45 artefactos + 3 HTML + `README.md` + `.gitkeep`):

| Productor | Artefactos | ¿Lo ejecuta `run_all.py`? |
|---|---:|---|
| `analysis/run_analisis_mongo.py` (24 PNG + CSV `mongo_*`/`capa_*`/`ranking`/`udalmap_paro`) | 36 | **No** (necesita Mongo vivo) |
| `analysis/sensibilidad.py` + `analysis/comparativa_mongo.py` (3 CSV) | 3 | **No** |
| **Subtotal ruta Mongo** | **39** | — |
| `transform/generar_figuras_N.py` (N1, N2, N3, N7) | 4 | **No**: está en `EXCLUIDOS` con justificación firmada |
| `transform/auditar_lagunas_silver.py` + `transform/generar_mapa_esquema.py` | 2 | **Sí** (grupo `resultados`) |
| `dashboard.html`, `dashboard_completo.html` (cifras a mano) | 2 | No (estáticos) |
| `README.md`, `.gitkeep` | 2 | No |
| `anexo/` (8 PNG relegados) | 8 | **Sí**, vía `ANEXO_PNG` de `run_analisis_mongo.py` |

**Conclusión:** los «39 + anexo» son exactamente lo que produce la ruta Mongo. No se perdió nada: el compañero **no ejecutó Mongo** (lo dijo), así que no podía aparecer el resto. `run_all.py` solo es dueño de **2 de los 45** artefactos; los otros 43 se reparten entre Mongo (39), las 4 figuras P0 y los 2 dashboards manuales.

**Riesgo real que esto deja visible (C4):** no hay un comando único. `run_all.py` se llama «run all» pero solo cubre silver + 2 artefactos, y **las 4 figuras P0 se quedan obsoletas en silencio** tras un rebuild de transform, porque su generador es determinista (solo CSV/GeoJSON, sin Mongo) y aun así está fuera del orquestador. Dos salidas posibles, ambas de decisión:

- **(a)** mover `generar_figuras_N.py` al grupo `resultados` de `SCRIPTS` (pasaría de 2 a 6 artefactos por rebuild; el DAG seguiría en 35 nodos, no en 34 → toca gobernanza);
- **(b)** dejarlo fuera y añadir a `run_all.py` un aviso final del tipo «resultados: 2/45 regenerados; faltan `run_analisis_mongo.py` y `generar_figuras_N.py`».

No se aplicó ninguna: la exclusión tiene justificación firmada y el recuento de gobernanza es cifra canónica.

---

## 8. Verificación ejecutada

| # | Comprobación | Resultado |
|---|---|---|
| 1 | `run_all.py --dry-run` (orden DAG) | vistas_mercado **31** → residencial_filtrado **32**; cert municipal **19** → cert moda **20** |
| 2 | `deduplicar_alquiler_enriquecido.py` con artefacto | `CSV: 253 -> 252`, `JSON: 253 -> 252`, exit 0 |
| 3 | `deduplicar_alquiler_enriquecido.py` sin artefacto (rebuild limpio) | `[SKIP] … paso heredado sin productor`, **exit 0** |
| 4 | `generar_cert_energetico_municipal.py` | 283.456 filas → 247.870 viviendas, **252 municipios**, exit 0 |
| 5 | `generar_cert_energetico_moda_municipio.py` | 252 filas, exit 0 |
| 6 | `generar_anuncios_residencial_filtrado.py` | 326 filas, 10 outliers, `habitaciones_int=100%`, exit 0 |
| 7 | `run_all.py --check` | **34/34 OK**, exit 0 |
| 8 | `scripts/verificar_gobernanza.py` | **TODO OK** (50 cabeceras, 42 scripts, **34 nodos DAG**, 188 silver, 11 pipelines) |
| 9 | `git diff` de los tres ficheros tocados | solo declaraciones `in` + comentarios + retirada del `fillna` |

**No se ejecutó:** `run_all.py` completo (reconstruiría todo el silver), Mongo, `load_mongo`/`clean_mongo`, ni escritura alguna en `data/raw` (356 hashes del compañero siguen siendo válidos: no se tocó ningún fichero de raw).

---

## 9. Pendiente (decisión de equipo, no ejecutado)

1. **Alinear pandas** (pin 2.2.3 vs venv 3.1.0): sin esto, dos máquinas pueden dar resultados distintos con el mismo código.
2. **Exclusión formal de `deduplicar_alquiler_enriquecido`** del DAG y actualización de las cifras canónicas 42/34 → 42/33 (gobernanza + README + docs).
3. **Regenerar o anotar `manifest_sha256.txt`**: sus 188 entradas incluyen el par heredado irreproducible.
4. **Borrar el sidecar huérfano** `_meta/udalmap_empleo_corregido.json.meta.json` y endurecer el check 03.
5. **Cerrar la brecha C4**: o `generar_figuras_N.py` entra en `run_all`, o `run_all` avisa de lo que no cubre.

---

## 10. Declaraciones completadas (respuesta a «¿no habría que incluir los ficheros que faltan?»)

De los 17 ficheros que nadie declaraba, **6 ya se escribían** dentro de pasos del DAG. Se declaran como `out`: no cambia qué se ejecuta, sí lo que `--check` y `run_manifest.json` vigilan.

| Script | Salidas añadidas | Línea del productor |
|---|---|---|
| `unificar_anuncios.py` | `cuarentena_pisos.csv`, `cuarentena_pisos.json`, `dedup_report.json` | `:334`, `:422-423` |
| `limpiar_ecvi.py` | `ecvi_compraventa_limpio.json` | `:173` |
| `enriquecer_codigo_ine.py` | `informe_entity_resolution.csv` | `:205` |
| `filtrar_outliers.py` | `log_filtrado.txt` | `:274` |
| `deduplicar_alquiler_enriquecido.py` | `alquiler_municipal_enriquecido.csv` | `:48` |

Nodos del DAG: siguen **34** (solo cambian las salidas, no las claves). `--check` y gobernanza se re-verificaron tras el cambio.

### Lo que NO se añade, y por qué

| Candidato | Decisión | Motivo |
|---|---|---|
| `generar_figuras_N.py` | **No** al DAG silver | Lee CSV de `data/resultados/` que produce Mongo (`mongo_esfuerzo`, `capa_*`, `mongo_tier`). Meterlo en `run_all` haría que el orquestador silver dependiera de una fase que no ejecuta: en árbol limpio falla o dibuja datos viejos. Su sitio es el cierre de la fase de análisis |
| `generar_f4_pisos_objetivo.py` | No | Idempotente, pero su salida es la lista de objetivos de una **captura manual**; pertenece al flujo de extracción dirigida |
| `generar_fotocasa_dirigido_informe.py` | No | Informe de esa misma captura manual; se regenera con ella |
| `f4_pisos_dirigido.py` | **Nunca** | Scraping de red (~350 s) y **escribe en `data/raw`** con `_raw_guard` |
| `validar_renta.py` | No | Exclusión firmada 2026-11-05: es QA, no ETL silver, y altera el manifest 188 |
| `_meta` (67 ficheros) | No | Fase extract (`extract/normalizar_metadata.py`, `extract/generar_ingestion_manifest.py`); `run_all` solo resuelve rutas bajo `transform/` |

**Conclusión:** incluir ficheros en `run_all` **no** hace la regeneración completa. Cierra el recuento de `data/procesado`, pero `data/resultados` (39 de 45) depende de Mongo y `_meta` de la fase extract. La completitud real exige un orquestador extremo a extremo (brecha C4), no más nodos en el DAG silver.

---

## 11. Robustez ante un tercero que reproduce (profesor)

Escenario: alguien recibe el repo y ejecuta. Riesgos ordenados por probabilidad de dar la cara:

| Riesgo | Estado | Práctica recomendada |
|---|---|---|
| **`data/` no viaja en git** (`.gitignore:14-22`): un clon no tiene raw ni procesado | **Inherente** | Entregar `data/raw` aparte (HDFS/VM) y verificar con `docs/raw_manifest_sha256.txt` (354 SHA). Ya existe el manifiesto; falta decirlo en el contrato de reproducción |
| **Entorno declarado ≠ validado**: `requirements.txt` fija `pandas==2.2.3`, el `.venv` tiene **3.1.0** y `uv.lock` no fija pandas | **Pendiente** | Una única fuente de verdad. Si se entrega `requirements.txt`, el tercero instalará 2.2.3 y el código ya funciona ahí (tras quitar `fillna(None)`), pero nadie sabe qué versión se validó |
| **Fallos mudos por codificación** en Windows: `text=True` sin `encoding` → `stdout=None`, paso FAIL sin diagnóstico | **Corregido** | `encoding="utf-8", errors="replace"` en `run_all`, `extract/main_ingest.py` y `scripts/verificar_fase_datos.py` |
| **`--check` daba falso verde** con entradas ausentes (`_resolver` devuelve ruta exista o no) | **Corregido** | Ahora comprueba `.exists()`; test de regresión en `tests/test_run_all.py`. Un árbol sin `data/raw` sale en rojo con «entradas inexistentes» en vez de «OK» |
| **Sin comando único** (C4): `run_all` = silver; resultados = Mongo; `_meta` = extract | **Pendiente** | Contrato de reproducción con las 6 órdenes, o `scripts/reproducir.py` con fases y prerequisitos |
| `verificar_fase_datos.py` sale 1 por FAIL 07 conocido (paro-cero) | **Por diseño** | Ya documentado en README:245; citarlo en el contrato para que no se lea como regresión |
| Scraping de red dentro del rebuild | **Evitado** | `f4_pisos_dirigido.py` sigue excluido; el rebuild no toca red ni `data/raw` |

**Veredicto.** `transform/run_all.py` ya es reproducible sin fallos en un árbol limpio con datos: 34/34 pasos, sin fallos mudos, sin pasos que dependan del orden accidental y con un `--check` que dice la verdad. Lo que **no** está resuelto es «reproducir el contenido completo con una orden»: eso exige datos entregados, Mongo vivo, `_meta` y un orquestador de fases. Sin esos tres, el tercero reproduce el silver, no el entregable.
