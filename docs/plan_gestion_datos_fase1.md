# Análisis y plan de gestión de datos — Fase 1 (sin MongoDB)

> Plan de referencia: `openspec/plan/planificaci_n_de_cruces_preparaci_n_de_datos_y_arquitectura_mongodb.md` (sugerencia Gemini).
> Decisión final: **MongoDB/HDFS/Kafka están prohibidos en esta fase.** Solo se gestiona y normaliza la Fase 1 (obtención y formato) para dejar los datos listos y trazables antes de cambiar de fase.

---

## 1. Resumen del plan de Gemini

El plan propone una arquitectura Medallion adaptada al reto:
- **Fase 1 (actual):** Descarga, limpieza de formato, normalización de `codigo_ine` (5 dígitos), estructura JSON anidada para anuncios.
- **Fase 2 (prohibida ahora):** HDFS + Kafka + MongoDB.
- **Fase 3 (prohibida ahora):** Limpieza operativa, cruces `$lookup`, KPIs en Aggregation Pipeline.

Problemas detectados por Gemini:
1. Bug `codigo_ine` en JSON de Álava (201/252).
2. ECVI con 65 CSVs de cabeceras múltiples (`Unnamed`).
3. Eustat Renta/Población con 98k/89k filas sin desglosar.
4. Anuncios sin esquema JSON unificado (ubicacion anidada + array equipamiento).

---

## 2. Validación con datos reales

| Problema Gemini | ¿Existe? | Evidencia |
|---|---|---|
| Bug `codigo_ine` 201/252 en JSON Álava | **Parcial / no general** | `udalmap`, `osrm`, `etxebide`, `ine_atlas`, `lanbide`, `transporte` tienen 252/252 en JSON. Fotocasa tiene 61 códigos + 1 `None` (no 4 dígitos). Solo el string `'None'` reduce minlen a 4. |
| ECVI cabeceras múltiples | **Sí** | 65 CSVs con 6 líneas de cabecera y columnas `Unnamed`. No hay archivo limpio. |
| Eustat Renta/Población sin desglosar | **Sí** | `eustat_renta_municipal.csv` 98.532 filas; `eustat_poblacion_edad.csv` 89.424 filas. Sin filtro por último año ni por sexo. |
| Anuncios sin esquema unificado | **Parcial** | JSONs ya tienen `ubicacion` (algunos) y `equipamiento` (en CSV). Falta unificar y añadir array `equipamiento` en JSON para MongoDB. |

**Conclusión de validación:** El plan es útil para ECVI y Eustat, pero el bug de `codigo_ine` en JSON no es sistemático; solo Fotocasa tiene un `None`. No obstante, conviene normalizar todos los JSONs por robustez.

---

## 3. Decisión final (qué hacemos ahora)

- **Hacer ahora (Fase 1):** Tareas 1.1–1.4 del plan (normalización de JSON, limpieza ECVI, desglose Eustat, esquema anuncios).
- **Diferir (Fase 2/3):** HDFS, Kafka, MongoDB, PyMongo, Aggregation Pipelines, Docker.
- **No descargar nuevas fuentes:** Ya tenemos 325 archivos; el plan no requiere Internet.
- **Documentar trazabilidad:** Cada transformación genera un archivo nuevo en `data/procesado/` con sufijo `_limpio` o `_normalizado`, sin sobrescribir crudos. Registrar origen y motivo en `docs/trazabilidad_datos.md`.

---

## 4. Plan de acción Fase 1 (solo gestión de datos)

| Tarea | Script | Entrada (origen) | Salida (destino) | Tiempo est. | Objetivo |
|---|---|---|---|---|---|
| 1.1 Normalizar `codigo_ine` en todos los JSON | `transform/normalizar_json_crudos.py` | `data/raw/*.json` | `data/procesado/*.json` (copia normalizada) | 30 min | Forzar `str(valor).strip().zfill(5)` en `codigo_ine` raíz y `ubicacion.codigo_ine`. Eliminar `None`. |
| 1.2 Limpiar ECVI | `transform/limpiar_ecvi.py` | `data/raw/ecvi_ecvi_es_2026t2_t*.csv` (65) | `data/procesado/ecvi_compraventa_limpio.json` + `.csv` | 45 min | Parser de 6 líneas de cabecera → columnas: `ambito_tipo`, `nombre_ambito`, `codigo_ine`, `trimestre`, `precio_medio_total_eur`, `precio_m2_libre_eur`, `precio_m2_usada_eur`. |
| 1.3 Desglosar Eustat Renta/Población | `transform/limpiar_eustat_demografia.py` | `data/raw/eustat_renta_municipal.csv`, `eustat_poblacion_edad.csv` | `data/procesado/eustat_demografia_renta_252.json` + `.csv` | 45 min | 252 filas (1 por municipio): renta personal total (ambos/hombres/mujeres), renta disponible, población total, población joven 15–29, año. |
| 1.4 Unificar esquema anuncios | `transform/unificar_anuncios.py` | `anuncios_fotocasa_enriquecido_geo.json`, `anuncios_pisos_enriquecido_geo.json`, `anuncios_realtyapi.json` | `data/procesado/anuncios_unificados.json` | 30 min | Campos: `id_anuncio`, `portal`, `modalidad`, `precio_eur`, `superficie_m2`, `ubicacion` (anidado), `equipamiento` (array), `auditoria`. |
| 1.5 Actualizar tests | `pytest` | — | `tests/test_contrato.py` | 15 min | Verificar cobertura 252/252, nulos, esquemas. |

**Total estimado:** ~2.5 horas. No se toca infraestructura.

---

## 5. Trazabilidad (origen → destino)

| Archivo origen | Transformación | Archivo destino | Motivo |
|---|---|---|---|
| `data/raw/*.json` | Normalizar `codigo_ine` | `data/procesado/*_normalizado.json` | Evitar pérdida de Álava en `$lookup` futuro. |
| `data/raw/ecvi_ecvi_es_2026t2_t*.csv` | Parser cabeceras múltiples | `data/procesado/ecvi_compraventa_limpio.json` | MongoDB no consulta `Unnamed`. |
| `data/raw/eustat_renta_municipal.csv` | Filtrar último año + pivotar sexo | `data/procesado/eustat_demografia_renta_252.json` | Desbloquear brecha de género y paro juvenil. |
| `data/raw/eustat_poblacion_edad.csv` | Filtrar último año + grupo 15–29 | `data/procesado/eustat_demografia_renta_252.json` | Población joven para tasa de paro. |
| `data/raw/anuncios_*_enriquecido_geo.json` | Unificar esquema | `data/procesado/anuncios_unificados.json` | Consultas anidadas y arrays en MongoDB. |

---

## 6. Riesgos y limitaciones

- **No se resuelve el salario joven municipal:** Sigue siendo proxy por ratio (documentado en `docs/decision_salario_proxy.md`).
- **ECVI solo cubre municipios >40.000 hab. y áreas funcionales:** No hay dato municipal para los 252; se mantiene a nivel territorial/comarcal.
- **Anuncios siguen con cobertura parcial:** 61 municipios Fotocasa, 37 Pisos, 3 RealtyAPI. No se descargan nuevas fuentes.
- **No se ejecuta MongoDB:** Los pipelines de cruces se diferirán a Fase 3.

---

## 7. Checklist de verificación antes de pasar a Fase 2/3

- [ ] Todos los JSON tienen `codigo_ine` con 5 dígitos (252/252 donde aplique).
- [ ] ECVI tiene archivo limpio con columnas nombradas.
- [ ] Eustat demografía/renta tiene 252 filas con renta por sexo y población joven.
- [ ] Anuncios unificados tienen `ubicacion` anidada y `equipamiento` array.
- [ ] Tests (`pytest`) en verde.
- [ ] Documentación de trazabilidad actualizada en `docs/trazabilidad_datos.md`.

---

## 8. Estado de ejecución (Fase 1 completada)

| Tarea | Estado | Archivo generado |
|---|---|---|
| 1.1 Normalizar JSON | ✅ Completada | `data/procesado/*_normalizado.json` (47) |
| 1.2 Limpiar ECVI | ✅ Completada | `data/procesado/ecvi_compraventa_limpio.json` + `.csv` (29) |
| 1.3 Desglosar Eustat | ✅ Completada | `data/procesado/eustat_demografia_renta_252.json` + `.csv` (252) |
| 1.4 Unificar anuncios | ✅ Completada | `data/procesado/anuncios_unificados.json` + `.csv` (840) |
| 1.5 Tests | ✅ Completada | `pytest` → 57 passed |

Ver trazabilidad detallada en `docs/trazabilidad_datos.md`.  
Inventario de crudos: `docs/inventario_datos.md` (325 archivos; añadir los nuevos normalizados en próxima regeneración).
