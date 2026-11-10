# Verificación de ejecución v10 — 2026-11-10

**Fecha:** 2026-11-10 · **Naturaleza:** solo lectura (única escritura: este informe)
**Pregunta que responde:** ¿lo ya construido funciona y da lugar a errores?
**Respuesta:** **no hay errores de ejecución**. Todo lo comprobado termina con exit 0 y con los conteos esperados.

---

## 1. Alcance

Se verifica lo construido, no lo que falta por decisión de alcance:

- HDFS: **solo originales** (indicación expresa de la profesora).
- Mongo: cadena completa de análisis sobre los datos cargados.
- Gates, suite y gobernanza.
- No se ejecutó `load_all`/`clean_all` (mutan producción) ni el gate `--vivo` (solo prueba TCP).

---

## 2. Comandos y resultados

| # | Comprobación | Comando | Resultado | Exit |
|---|---|---|---|---:|
| 1 | Sintaxis de todo el código | `python -m compileall -q -f extract transform storage analysis scripts tests` | sin errores | **0** |
| 2 | 11 pipelines contra Mongo | `python analysis/run_analisis_mongo.py --salida <tmp>` | 11/11 con filas; 13 CSV + 24 PNG | **0** |
| 3 | Consultas | `mongo_queries.resumen_exists_type()` / `busqueda_avanzada_demo()` | 594 anuncios, 587 con superficie, 561 `precio` Decimal, 594 con coordenadas | **0** |
| 4 | Índices y explain | `mongo_indexes.index_report()` | 4 índices de negocio; COLLSCAN 594 → IXSCAN 1 | **0** |
| 5 | Suite completa | `python -m pytest tests -q` | 235 passed, 2 skipped | **0** |
| 6 | Gobernanza | `python scripts/verificar_gobernanza.py` | TODO OK (11 pipelines, 50 cabeceras, 34 DAG) | **0** |
| 7 | Staleness DAG | `python transform/run_all.py --check` | 34/34 | **0** |
| 8 | Gate offline | `python scripts/gate_extremo_a_extremo.py --offline` | RESULTADO gate: OK | **0** |
| 9 | HDFS originales | WebHDFS `GETCONTENTSUMMARY` de `data/raw` | **fileCount=352**, dirCount=6, 895.597.494 B | **0** |
| 10 | Recuperación de un original | WebHDFS `OPEN` de `udalmap_vpo_terminadas.csv` | 35.427 B, SHA idéntico al local (`70a2937a…4706`) | **0** |

---

## 3. Pipelines: filas devueltas

```
pipeline_indicadores_municipio      252
pipeline_alquiler_por_municipio     252
pipeline_modalidades                  2
pipeline_top_municipios_por_esfuerzo  4
pipeline_esfuerzo_por_sexo          252
pipeline_accesibilidad_extendida    252
pipeline_udalmap_extendido_osrm     252
pipeline_vpo_por_municipio          322
pipeline_vpo_terminadas             251
pipeline_tier_por_municipio         252
pipeline_habitaciones_por_municipio   9
```

- `suma n_anuncios` sobre `indicadores` = **594** = `estimated_document_count()` de `anuncios`. Cuadra.
- Reproducibilidad: dos pasadas del orquestador con la **misma huella** `0f15c729901693ba5cc925d5241140c2bb83251ff0763b813f30865dcff76daa`.
- Salida a directorio temporal dentro de `openspec/audit/v10_2026-11-10/` y borrado al terminar: **`data/` no se tocó**.

---

## 4. HDFS: la ausencia de `procesado` es lo correcto

- `data/raw` en HDFS: **352 ficheros** (recursivo), 6 directorios, 895.597.494 B.
- `data/procesado` en HDFS: `FileNotFoundException`.
- **No es un fallo:** la profesora indicó **solo originales en HDFS**. Está documentado en `README.md:108` y `arquitectura_datos.md:70`.
- Local: 356 ficheros = 354 canónicos + `.FROZEN` + `.gitkeep`; HDFS publica 352 porque 2 alias legacy no se suben (misma línea del README).

---

## 5. Ajuste de puntuación derivado de la indicación

| Criterio | Antes | Ahora | Motivo |
|---|---:|---:|---|
| C2 Almacenamiento HDFS | 7 | **10** | El requisito aplicable es «originales en HDFS + recuperación demostrada»; se cumple |
| BDA RA1 | 34/40 | **37/40 (92,5 %)** | Recalculado |
| Total bruto | 184/190 | **187/190 (98,4 %)** | Recalculado |
| C4 Integración | 7 | **7** | Único con reserva: no hay comando único extracción → silver → Mongo → análisis |

Matriz actualizada: `matriz_rubrica_v10.md` (C2, totales y veredicto).
Hallazgo actualizado: `hallazgos_v10.csv` → H-15 reformulado como decisión indicada por la profesora, ya escrita en `README.md:108`.

---

## 6. Riesgos detectados que **no** son errores de ejecución

| Riesgo | Efecto real | ¿Rompe la demo? |
|---|---|---|
| `get_client()` con `@lru_cache` | Cambiar `MONGO_URI` en caliente no reconecta | No |
| CI sin servicio Mongo | Los tests de integración fallarían en GitHub | No (en local pasan) |
| Gate con `lag 0` / `0 duplicados` tautológicos | Evidencia débil, no falsa ejecución | No |
| BOM en los 8 CSV `mongo_*` | Molesta a consumidores estrictos | No |
| Outlier 109.000 € en `habitaciones` | Máximo engañoso si se cita sin contexto | No |

---

## 7. Límites

- No se ejecutó `load_all`/`clean_all`: escribirían en producción. La carga se acredita por los datos ya presentes, el cuadre 594 y la suite.
- No se ejecutó el gate `--vivo` (solo prueba TCP); HDFS y Kafka se verificaron por API directa.
- `pytest` se ejecutó sobre el árbol actual; los cambios de esta sesión son solo documentos en `openspec/audit/v10_2026-11-10/`, sin código.
