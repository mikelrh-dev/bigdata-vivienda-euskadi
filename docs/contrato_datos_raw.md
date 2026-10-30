# Contrato de datos raw (CAPA BRONZE)

Estado: **activo**. Vigente desde el cambio `raw-immutability-hardening`.

Este documento sustituye a la convención anterior (marcador `.FROZEN` + memoria
sobre "no tocar raw"). La inmutabilidad de `data/raw/` pasa a estar **bloqueada
por código** y verificada por tests automatizados.

Referencia OpenSpec: `openspec/changes/raw-immutability-hardening/`
(especificaciones `contrato-datos`, `inmutabilidad-raw`, `extraccion-datos`).

---

## 1. Capas

| Capa | Ruta | Quién escribe | Regla |
|---|---|---|---|
| Bronze (landing) | `data/raw/` | **Solo `extract/`** (adquisición) | Append-only. Inmutable para el resto del pipeline. |
| Silver (limpieza) | `data/procesado/` | **Solo `transform/`** | Derivado. Regenerable. Salidas aditivas. |
| Resultados | `data/resultados/` | `transform/` (gráficos) | Derivado, no contractual. |

---

## 2. Reglas de la capa raw

1. **Único productor:** `extract/*.py`. Cada ejecución crea ficheros nuevos o
   escribe lotes con nombre único; nunca sobrescribe un fichero raw existente.
2. **Prohibido para `transform/`:** escribir en `data/raw/`. La única excepción
   es una lista blanca explícita, y cada escritura debe pasar antes por el guard
   compartido `transform/_raw_guard.py::assert_raw_writable(reason)`, con un
   `reason` no vacío y auditable.
3. **Lista blanca** (`transform/` puede escribir en raw):
   - `enriquecer_codigo_ine.py` — solo con `--write-raw --reason "..."`.
     El valor por defecto escribe en `data/procesado/` (sufijo `_enriquecido`).
   - `f4_pisos_dirigido.py` — crea un lote dirigido nuevo con nombre único
     (`anuncios_pisos_dirigido_{YYYYMMDDHHMMSS}_{token}.json`), nunca sobrescribe.
4. **El marcador `.FROZEN` ya no es un mecanismo de control.** Solo queda como
   marca informativa de versión congelada; la protección real es el guard y los
   tests de `tests/test_raw_guardrails.py`.
5. **Verificación:** `pytest tests/test_raw_guardrails.py -q` falla si un
   transform escribe en raw sin estar en la lista blanca con guard.

---

## 3. Integridad y manifest

- `docs/raw_manifest_sha256.txt`: SHA-256 de cada fichero de `data/raw/`, con
  formato `<sha256>  <ruta_relativa_a_data/raw>`, ordenado por ruta.
- Excepciones del manifest (no son datos):
  - `.FROZEN`
  - `.gitkeep`
  - `ingestion_manifest.json` (manifiesto de ejecución, se reescribe en cada run)
  - `manifest_sha256.txt` (copia legacy dentro de `data/raw/`; el manifiesto
    autoritativo es `docs/raw_manifest_sha256.txt` y no puede contener su propio
    hash)
- `data/raw/ingestion_manifest.json`: inventario de la última ejecución
  (nombre, timestamp UTC, SHA-256, nº de registros, estado).
- `tests/test_raw_inmutable.py` verifica en ambos sentidos:
  - todo fichero listado en el manifest existe y su hash coincide;
  - todo fichero de `data/raw/` (salvo excepciones) está listado en el manifest.

---

## 4. Esquema de `codigo_ine`

- Tipo: **string**, no entero. Se conserva siempre con **5 caracteres**.
- Normalización: `str(x).strip().zfill(5)`. Preserva `None` / vacío como nulo
  (no convierte a `"00000"` ni a `"nan"`).
- Motivo: los códigos de Álava empiezan por `01`; leído como entero se pierde
  el cero inicial y el join con `dim_municipios` se rompe en silencio.
- Lectura de CSV: `pd.read_csv(..., dtype=str, encoding="utf-8-sig")` en todo
  el pipeline que toque `codigo_ine`.
- Tabla de verdad: `data/raw/dim_municipios.csv` (252 municipios).

---

## 5. Canónico de anuncios

- `data/procesado/anuncios_unificados.json` — registro completo (JSON).
- `data/procesado/anuncios_unificados.csv` — columnas base obligatorias:

```
id_anuncio, portal, modalidad, precio_eur, superficie_m2, habitaciones,
es_outlier_superficie, codigo_ine, municipio, titulo, subtitulo, equipamiento
```

- **Regla de salida aditiva:** cualquier fichero derivado del canónico
  (`anuncios_unificados*.csv`) debe tener como **superset** estas columnas.
  Está prohibido reescribir el canónico con menos columnas.
- Las tablas por fuente (`anuncios_fotocasa_enriquecido.csv`,
  `anuncios_pisos_enriquecido.csv`, `anuncios_realtyapi_enriquecido.csv`) y las
  vistas analíticas (`anuncios_vivienda_residencial*.csv`,
  `anuncios_habitaciones_unificados.csv`) **no** están sujetas a esta regla:
  son datasets distintos, no enriquecimiento del canónico.
- **Dedup determinista:** por `(portal, id_anuncio)`, tras ordenar por
  `(_source_order, portal, id_anuncio)`. El orden de los ficheros de entrada no
  cambia el resultado. Informe en `data/procesado/dedup_report.json`.

---

## 6. Resolución de municipios

- Normalización canónica (`extract/entity_resolution.py::norm`):
  NFKD → ascii → minúsculas → `[\s\-_/]+` → espacio → colapsar espacios.
- `NAME2CODE` y `MANUAL_MAP` se construyen **con claves normalizadas**.
- Orden de resolución (`transform/muni_resolve.py::resolver_codigo`):
  1. `codigo_ine` válido (5 dígitos, presente en `dim_municipios`).
  2. `MANUAL_MAP` (alias normalizados).
  3. Coincidencia exacta en `NAME2CODE`.
  4. Fallback difuso (`difflib`) con umbral **0.85**.
  5. Sin match → `(None, None)`. No se inventa ni se fuerza un código.

---

## 7. Lots dirigidos (append-only)

- Nombre: `anuncios_{portal}_dirigido_{YYYYMMDDHHMMSS}_{token}.json`
  (`token = uuid4().hex[:8]`).
- El timestamp incluye **segundos** y token: dos ejecuciones el mismo día
  nunca colisionan ni sobrescriben.
- Integración en el canónico: `transform/unificar_anuncios.py` con *schema
  guard* (JSON válido, `datos` es lista, metadata con `n_anuncios`).

---

## 8. Temp dir

- Prohibido el literal `/tmp` (no existe en Windows).
- Uso de `tempfile.gettempdir()` + `mkdir(parents=True, exist_ok=True)`.
- Aplicado en `extract/22_geo_areas_funcionales.py`.

---

## 9. Orden de ejecución Silver (dependencias)

Orden obligatorio de los pasos de limpieza:

1. `transform/enriquecer_codigo_ine.py` → genera `*_enriquecido` en `data/procesado/`.
2. `transform/deduplicar_alquiler_enriquecido.py` → 253 → 252 filas en
   `alquiler_municipal_enriquecido.csv/.json` (el fichero fuente tiene una fila
   duplicada). **Debe ejecutarse después del paso 1**, porque el enriquecimiento
   regenera el fichero desde raw.
3. `transform/unificar_anuncios.py` → canónico + `dedup_report.json`.
4. Enriquecimientos aditivos del canónico (`generar_fingerprint.py`,
   `enriquecer_equipamiento_realtyapi.py`, `rescatar_features_nlp.py`) → solo
   añaden columnas; nunca reducen el esquema.

## 10. Cómo se verifica

```bash
.venv/Scripts/python.exe -m pytest tests/test_raw_guardrails.py -q   # guardrails
.venv/Scripts/python.exe -m pytest tests/test_raw_inmutable.py -q   # manifest raw
.venv/Scripts/python.exe -m pytest tests -q                          # suite completa
```

Si un transform intenta escribir en `data/raw/`, el guardrail falla y el
cambio no puede pasar. Esa es la diferencia frente al modelo anterior: la
inmutabilidad no depende de que nadie recuerde una instrucción.

---

## 11. Anomalías históricas (primera carga)

Los siguientes defectos se detectaron en la primera carga de datos y se asumen
como limitación histórica. No se regenera raw (inmutable); se sanearán en la
capa silver (`transform/`).

| # | Archivo | Defecto | Sanear en |
|---|---|---|---|
| 1 | `etxebide_indicador_86.csv` | Encoding Latin-1 (no UTF-8) | `transform/` (leer con `encoding='latin-1'`, escribir UTF-8-sig) |
| 2 | `b5m_catalogo.json` | Sin `fecha_extraccion`, sin `fuente` (solo `url`) | `transform/normalizar_json_crudos.py` (inyectar metadato) |
| 3 | `dim_municipios.json` | Usa `fecha` en lugar de `fecha_extraccion` | `transform/normalizar_json_crudos.py` |
| 4 | `distancias_municipios.json` | Sin `fecha_extraccion` | `transform/normalizar_json_crudos.py` |
| 5 | `emal_fianzas_ampliado.json` | Sin `fecha_extraccion` | `transform/normalizar_json_crudos.py` |
| 6 | `ine_atlas_renta.json` | Usa `fecha_conversion` en lugar de `fecha_extraccion` | `transform/normalizar_json_crudos.py` |
| 7 | `lanbide_paro_juvenil.json` | Sin `fecha_extraccion` | `transform/normalizar_json_crudos.py` |
| 8 | `osrm_tiempos_capitales.json` | Sin `fecha_extraccion` | `transform/normalizar_json_crudos.py` |
| 9 | `renta_municipal_completa.json` | Usa `fecha_conversion` | `transform/normalizar_json_crudos.py` |
| 10 | `serpavi_renta_municipal.json` | Sin `fecha_extraccion` | `transform/normalizar_json_crudos.py` |
| 11 | `udalmap_empleo_corregido.json` | Sin `fecha_extraccion` | `transform/normalizar_json_crudos.py` |
| 12 | Varios JSON raw | Sin `url` ni `n_registros` (usan `n_anuncios`, `n_centros`, etc.) | Aceptar como variante; documentar en inventario |
| 13 | Varios scripts | Guardan solo respuesta parseada, no payload original byte-for-byte | Limitación de la primera carga; futuras extracciones guardarán payload original |

**Decisión de arquitectura:** la primera carga se asume como snapshot histórico. No se regenera raw (inmutable). Los defectos se sanearán en `transform/` (capa silver), demostrando capacidad de limpieza de datos incompletos (requisito PDF/SBD).

---

## 12. Excepciones documentadas

### 12.1 `f4_pisos_dirigido.py` viola inmutabilidad
- **Qué hace:** scrapea Pisos.com en vivo y escribe un lote nuevo en `data/raw/` (append-only, filename con timestamp+UUID).
- **Por qué:** scraping dirigido a municipios con baja cobertura (Fase 4).
- **Mitigación:** requiere `assert_raw_writable` (borrar `.FROZEN` + registrar motivo). Documentado como excepción temporal. No ejecutar sin autorización explícita.

### 12.2 `f4_pisos_objetivo.json` es selección manual
- **Qué es:** lista de 62 códigos INE objetivo para scraping dirigido de Pisos.com.
- **Criterio original:** municipios con tipología Nivel2/Nivel3 y baja cobertura de anuncios en Fotocasa (selección ad-hoc, no reproducible por criterio simple).
- **Reproducibilidad:** no regenerable automáticamente. El generador `transform/generar_f4_pisos_objetivo.py` es idempotente (valida si existe, genera aproximación si no).

### 12.3 `fotocasa_dirigido_informe.csv` depende de red
- **Qué es:** informe de anuncios obtenidos por municipio en scraping dirigido de Fotocasa.
- **Reproducibilidad:** derivado de `data/raw/anuncios_fotocasa_dirigido_*.json`. Si no hay raw dirigido, se genera con `n=0` a partir de la lista de objetivos.

### 12.4 `filtrar_outliers.py` no-determinismo cosmético
- Incrusta `datetime.now()` en metadata JSON. Las filas y conteos son deterministas. No afecta reproducibilidad de datos.
