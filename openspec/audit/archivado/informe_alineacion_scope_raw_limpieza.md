# Informe de alineación — alcance: obtención de datos raw + limpieza + estructura del proyecto

**Fecha:** 2026-10-30
**Alcance:** fase de extracción (raw), limpieza de datos y estructura del proyecto.
**Fuera de alcance (diferido):** HDFS, Kafka, MongoDB (modelado, índices, transacciones, agregación), visualización/presentación.
**Fuentes de verdad:** `archivosReto/RETO 1Evaluacion SBD-BDA.pdf`, `archivosReto/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx`.
**Specs verificadas:** `openspec/specs/extraccion-datos/spec.md`, `openspec/specs/contrato-reto/spec.md` (criterios de extracción/formato), `openspec/specs/mongodb-y-analisis/spec.md` (LIMPIEZA-01), `openspec/project.md`, `openspec/config.yaml`.

---

## 1. Veredicto

- **Specs (openspec):** ALINEADO con el PDF/DOCX para el alcance (raw + limpieza + estructura). Las correcciones previas (fuentes marcadas como instancia del proyecto, ENTREGABLES-01, etc.) cerraron los desvíos principales.
- **Implementación:** PARCIALMENTE ALINEADA. Tres inconsistencias menores de formato/metadata, no bloqueantes.

---

## 2. Checklist in-scope

| Requisito | Estado | Evidencia |
|---|---|---|
| EXTRACCION-01 (API + scraping, raw + parseado) | ✅ | Eustat/INE APIs + Fotocasa/Pisos scraping; HTML crudo conservado; `data/raw/` con JSON/CSV |
| EXTRACCION-02 (≥3 fuentes independientes) | ✅ | Eustat, INE, euskadi.eus, b5m, Fotocasa; fallos capturados sin abortar |
| FORMATO-01 (JSON/CSV + metadata fuente/fecha/recuento) | ⚠️ Parcial | Formatos válidos; metadata inconsistente (ver §3) |
| COMPLEMENTARIOS-01 (salarios/población/indicadores) | ✅ | Población/renta Eustat, salarios INE/OVJ, indicadores adicionales |
| PYTHON-01 (todo en Python, venv) | ✅ | Scripts en `extract/`/`transform/`, venv Python 3.12 |
| LIMPIEZA-01 (incompletos/duplicados/incorrectos) | ✅ (dato) | Nulos no convertidos a 0, dedup, outliers marcados; implementación PyMongo diferida (scope Mongo) |
| Layout `openspec/project.md` | ⚠️ Parcial | Existen `extract/`, `transform/`, `tests/`, `config/`, `data/{raw,procesado,resultados}`; faltan `storage/`, `analysis/`, `visualization/`, `notebooks/` (diferidos) |
| `openspec/config.yaml` | ✅ | Stack/Python/fuentes coherentes; infra declarada pendiente |
| Prohibiciones P-02, P-03, P-05, P-06, P-07, P-08 | ✅ | Alquiler de Eustat, salario de fuente oficial, solo Python, credenciales no trackeadas, tests 66/66 verdes |

---

## 3. Gaps de implementación (no de spec)

1. **Metadata no homogénea en ~9 JSON raw:** `b5m_catalogo.json` sin fecha/fuente; otros usan `fecha_conversion` en lugar de `fecha_extraccion`. La spec FORMATO-01 exige metadata fuente/fecha/recuento.
2. **`data/raw/etxebide_indicador_86.csv` no es UTF-8** (Latin-1). Inconsistente con el resto (UTF-8-sig).
3. **Algunos scripts guardan solo la respuesta parseada**, no el payload original byte-for-byte (p. ej. Eustat). La spec EXTRACCION-01 exige guardar la respuesta original junto con la forma parseada.

---

## 4. Plan para alinear (sin tocar raw inmutable)

Principio: `data/raw/` es inmutable (`.FROZEN` + read-only). No se modifica in place. Las correcciones se aplican a scripts (futuras extracciones) y, donde sea seguro, a copias en `data/procesado/`.

| Paso | Acción | Archivos | Riesgo |
|---|---|---|---|
| 1 | Normalizar metadata en scripts extractores: usar siempre `fecha_extraccion` (ISO), `fuente`, `url`, `n_registros`/`n_filas` en todos los JSON raw. | `extract/*.py` (especialmente `b5m`, `etxebide`) | Bajo |
| 2 | Forzar encoding UTF-8-sig en todos los CSV/JSON raw. | `extract/*.py` | Bajo |
| 3 | Guardar payload original byte-for-byte (`.json` raw de la API) además del parseado, cuando la fuente lo permita. | `extract/01_eustat_api.py`, `extract/03_ine_*.py` | Bajo |
| 4 | Documentar en `docs/contrato_datos_raw.md` (Bloque 0) la convención de metadata y encoding. | `docs/contrato_datos_raw.md` | Bajo |
| 5 | Regenerar raw afectado desde los scripts corregidos (solo si la API está disponible; Eustat API REST está caída → usar backup o interfaz pxweb). | `data/raw/` (nuevos archivos, no modificar existentes) | Medio |
| 6 | Verificar con `tests/test_contrato.py` y `tests/test_crudos.py` tras regeneración. | tests | Bajo |

Pasos 1-4 son seguros y no tocan raw. Pasos 5-6 dependen de disponibilidad de fuentes (Eustat API REST caída).

---

## 5. Diferido (no contado como gap en este alcance)

- HDFS (almacenamiento/recuperación), Kafka (productor/consumidor), integración flujo completo a MongoDB.
- MongoDB: modelado, índices, transacciones, consultas anidadas/arrays, Aggregation Pipeline, transformaciones en BD.
- Visualización/presentación: gráficos, informe, conclusiones.
- Directorios `storage/`, `analysis/`, `visualization/`, `notebooks/`.
- Limpieza en PyMongo (actualmente en pandas/transform).

---

## 6. Conclusión

Las specs están al día para el alcance. La implementación tiene 3 inconsistencias menores de metadata/encoding que se corrigen en scripts (pasos 1-4) sin tocar raw. Los pasos 5-6 dependen de la disponibilidad de la API de Eustat (actualmente caída; datos válidos provienen del backup).
