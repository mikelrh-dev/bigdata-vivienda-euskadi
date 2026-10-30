# Plan de alineación — raw + limpieza + estructura (sin regenerar raw)

**Estado:** BORRADOR — pendiente de verificación del usuario. No se ha ejecutado ningún cambio.
**Alcance:** fase de extracción (raw), limpieza de datos y estructura del proyecto.
**Fuera de alcance (diferido):** HDFS, Kafka, MongoDB (modelado, índices, transacciones, agregación), visualización/presentación.
**Fuentes de verdad:** `archivosReto/RETO 1Evaluacion SBD-BDA.pdf`, `archivosReto/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx`.
**Principio rector:** `data/raw/` es inmutable. No se regenera ni se modifica in place. Toda corrección se aplica a scripts (futuras extracciones) o en la capa `data/procesado/` (transformación).

---

## 1. Diagnóstico consolidado

### 1.1 Specs (openspec): ALINEADO para el alcance
Las specs de extracción, contrato (criterios de extracción/formato), limpieza (LIMPIEZA-01) y estructura (project.md, config.yaml) están alineadas con el PDF/DOCX tras las correcciones aplicadas.

### 1.2 Implementación: PARCIALMENTE ALINEADA
Tres inconsistencias menores de formato/metadata (no bloqueantes):
1. Metadata no homogénea en ~9 JSON raw (b5m sin fecha/fuente; otros con `fecha_conversion` en lugar de `fecha_extraccion`).
2. `etxebide_indicador_86.csv` en Latin-1 (no UTF-8).
3. Algunos scripts guardan solo la respuesta parseada, no el payload original byte-for-byte.

### 1.3 Reproducibilidad silver: PARCIALMENTE REPRODUCIBLE
- 4 archivos huérfanos (sin script generador): `anuncios_vivienda_residencial_filtrado.csv`, `cert_energetico_moda_municipio.csv`, `fotocasa_dirigido_informe.csv`, `f4_pisos_objetivo.json`.
- Generadores creados (4 scripts en `transform/`), no ejecutados.
- `f4_pisos_dirigido.py` viola inmutabilidad (scrapea y escribe en raw congelado).
- `f4_pisos_objetivo.json` es una selección manual (62 municipios) no reproducible por criterio simple.
- `filtrar_outliers.py` incrusta `datetime.now()` en metadata (no-determinismo cosmético).

---

## 2. Estrategia (aprobada en principio, pendiente de verificación)

No regenerar raw. En su lugar:

1. **Actualizar scripts de extracción** (`extract/`) para que sean metodológicamente perfectos (UTF-8-sig, payload original, metadatos correctos). Sin ejecutarlos.
2. **Sanear en la capa de transformación** (`transform/`): leer Latin-1 y convertir, inyectar metadatos faltantes en memoria antes de escribir a procesado.
3. **Documentar** las anomalías y decisiones técnicas en `docs/contrato_datos_raw.md`.
4. **Documentar excepciones**: f4 viola inmutabilidad, f4_pisos_objetivo es manual.

---

## 3. Bloques de trabajo (orden de ejecución propuesto)

### Bloque 0 — Contrato de datos (crear documento)
**Archivo nuevo:** `docs/contrato_datos_raw.md`

Contenido:
- Zonas: `data/raw/` = Landing Zone (exclusiva para extractores, append-only, inmutable por diseño). `data/procesado/` = Silver (único destino de `transform/`).
- Tipado: `codigo_ine` siempre string de 5 caracteres (`zfill(5)`) en todo el pipeline.
- Convención de metadata: todo JSON raw debe tener `fuente`, `fecha_extraccion` (ISO), `url` (si aplica), `n_registros`/`n_filas`/`n_anuncios`.
- Encoding: UTF-8-sig en todos los CSV/JSON.
- Anomalías documentadas:
  - `etxebide_indicador_86.csv` entró en Latin-1 en la primera carga; se sanea en silver.
  - ~9 JSON raw sin metadata completa (b5m, dim_municipios, distancias, emal_ampliado, ine_atlas_renta, lanbide_paro_juvenil, osrm, renta_municipal_completa, serpavi, udalmap_empleo_corregido); se inyecta metadato en transformación.
  - Algunos scripts guardan solo la respuesta parseada, no el payload original (limitación de la primera carga).
- Excepciones documentadas:
  - `f4_pisos_dirigido.py` muta raw congelado (scraping dirigido). Violación conocida; se documenta como excepción temporal.
  - `f4_pisos_objetivo.json` es una selección manual (62 municipios). No reproducible automáticamente.

**Riesgo:** bajo. Solo documentación.

### Bloque 1 — Actualizar scripts de extracción (sin ejecutar)
**Archivos a modificar:** `extract/*.py` (especialmente los que generan JSON/CSV raw)

Cambios por script:
- Forzar `encoding="utf-8-sig"` en todas las escrituras CSV/JSON.
- Guardar payload original (respuesta cruda de la API) además del parseado, cuando la fuente lo permita (Eustat, INE, Open Data, b5m, SERPAVI, etc.).
- Homogeneizar metadata: siempre `fuente`, `fecha_extraccion` (ISO), `url`, `n_registros`/`n_filas`/`n_anuncios`.
- No tocar la lógica de red ni la estructura de datos.

**Scripts prioritarios (los que tienen gaps):**
- `extract/04_b5m_geo.py` (b5m_catalogo.json sin fecha/fuente)
- `extract/09_opendata_bizilagun_etxebide.py` (etxebide en Latin-1)
- `extract/06_ine_api.py` / `extract/07_ine_salarios.py` (guardar payload original)
- `extract/01_eustat_api.py` (guardar payload original; API caída, solo actualizar código)
- `extract/16_serpavi_renta.py`, `extract/17_osrm_tiempos.py`, `extract/18_lanbide_paro_juvenil.py` (metadata faltante)

**Riesgo:** bajo. No se ejecutan. Solo se actualiza código.

### Bloque 2 — Sanear en transformación (código, no datos)
**Archivos a modificar:** `transform/normalizar_json_crudos.py`, `transform/corregir_empleo.py` (o nuevo script), `transform/enriquecer_codigo_ine.py`

Cambios:
- `normalizar_json_crudos.py`: inyectar `fecha_extraccion` a JSON que no la tienen (b5m, dim_municipios, distancias, etc.) usando la fecha del archivo o un valor por defecto documentado.
- Nuevo paso o ampliación: leer `etxebide_indicador_86.csv` con `encoding='latin-1'` y escribir UTF-8-sig en procesado.
- `enriquecer_codigo_ine.py`: ya modificado para abortar si `.FROZEN`. Añadir documentación de la excepción.

**Riesgo:** bajo. Solo código, no se toca raw.

### Bloque 3 — Generadores huérfanos (ya creados, pendientes de ejecución)
**Archivos creados (no ejecutados):**
- `transform/generar_cert_energetico_moda_municipio.py`
- `transform/generar_anuncios_residencial_filtrado.py`
- `transform/generar_fotocasa_dirigido_informe.py`
- `transform/generar_f4_pisos_objetivo.py`

Acción: ejecutar con backup previo de los huérfanos para verificar reproducibilidad. Comparar output con existente.

**Riesgo:** bajo. Backup previo.

### Bloque 4 — Documentar excepciones
**Archivos a modificar:** `docs/contrato_datos_raw.md` (del Bloque 0), `docs/gaps_misconceptions_errores.md`

Añadir:
- f4_pisos_dirigido.py viola inmutabilidad (scraping dirigido escribe en raw congelado). Documentar como excepción temporal.
- f4_pisos_objetivo.json es selección manual. Documentar criterio y que no es reproducible automáticamente.
- fotocasa_dirigido_informe.csv depende de scraping (red). Documentar como derivado de raw dirigido.

---

## 4. Tabla de archivos a modificar

| Archivo | Bloque | Tipo de cambio |
|---|---|---|
| `docs/contrato_datos_raw.md` | 0 | Crear |
| `extract/04_b5m_geo.py` | 1 | Patch (encoding + metadata) |
| `extract/09_opendata_bizilagun_etxebide.py` | 1 | Patch (encoding + metadata) |
| `extract/06_ine_api.py` | 1 | Patch (payload original + metadata) |
| `extract/07_ine_salarios.py` | 1 | Patch (payload original + metadata) |
| `extract/01_eustat_api.py` | 1 | Patch (payload original + metadata) |
| `extract/16_serpavi_renta.py` | 1 | Patch (metadata) |
| `extract/17_osrm_tiempos.py` | 1 | Patch (metadata) |
| `extract/18_lanbide_paro_juvenil.py` | 1 | Patch (metadata) |
| `transform/normalizar_json_crudos.py` | 2 | Patch (inyectar metadata) |
| `transform/corregir_empleo.py` | 2 | Patch (documentar) |
| `transform/enriquecer_codigo_ine.py` | 2 | Patch (documentar excepción) |
| `transform/generar_*.py` (4) | 3 | Ejecutar (verificar) |
| `docs/gaps_misconceptions_errores.md` | 4 | Patch (documentar excepciones) |

**No se toca:** `data/raw/`, `data/procesado/`, `tests/`.

---

## 5. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Scripts actualizados pero no verificados por ejecución | Documentar que requieren fuente disponible; no ejecutar sin autorización |
| Inyección de metadata incorrecta en transform | Verificar con `tests/test_contrato.py` y `tests/test_crudos.py` |
| f4_pisos_dirigido.py sigue violando inmutabilidad | Documentar como excepción temporal; no ejecutar |
| Generadores huérfanos sobrescriben archivos existentes | Backup previo de los 4 huérfanos antes de ejecutar |

---

## 6. Criterios de verificación

- `tests/test_contrato.py`: 54 passed (sin regresión).
- `tests/test_crudos.py`: 3 passed (sin regresión).
- `tests/test_raw_inmutable.py`: pasa (raw no modificado).
- Verificación manual: diff de los 4 huérfanos regenerados vs existentes (deben ser idénticos o documentar diferencias).
- Verificación de metadata: todos los JSON raw en procesado tienen `fuente`, `fecha_extraccion`, `url` (donde aplica), `n_registros`.

---

## 7. Lo diferido (no contado como gap en este alcance)

- HDFS, Kafka, integración flujo completo a MongoDB.
- MongoDB: modelado, índices, transacciones, consultas, agregación, transformaciones en BD.
- Visualización/presentación: gráficos, informe, conclusiones.
- Directorios `storage/`, `analysis/`, `visualization/`, `notebooks/`.
- Limpieza en PyMongo (actualmente en pandas/transform).

---

## 8. Próximos pasos (pendientes de tu verificación)

1. Revisar este plan.
2. Autorizar o ajustar bloques/pasos.
3. Si autorizas, ejecutar en orden: Bloque 0 → 1 → 2 → 3 → 4.
4. Verificar con tests y diff.
5. No hacer commit sin tu autorización.

**Espero tu verificación antes de ejecutar cualquier cambio.**
