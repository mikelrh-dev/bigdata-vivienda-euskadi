# Plan de corrección de los 10 puntos débiles — bigdata-vivienda-euskadi

**Fecha:** 2026-10-30
**Modo:** Planificación (no se modifica nada hasta autorización)
**Origen:** Auditoría spec-vs-proyecto (sin infraestructura ni Mongo) + análisis de subagentes (deleg_1e4d07f6)
**Alcance:** 10 puntos débiles corregibles. Excluye HDFS/Kafka/MongoDB (fuera de alcance).

---

## 0. Resumen ejecutivo

| # | Punto | Esfuerzo | Acción recomendada | Prioridad |
|---|---|---|---|---|
| 1 | 6 CSVs sin BOM | Bajo | Regenerar con 7 scripts corregidos | 🔴 Alta |
| 2 | 2 JSONs Fotocasa con codigo_ine vacío | Bajo | Ejecutar normalizar_json_crudos.py | 🔴 Alta |
| 3 | No-determinismo en outputs | Bajo | Regenerar f4 + filtrar_outliers | 🔴 Alta |
| 4 | 14 derivados en procesado_pre_silver | Bajo | Promover pob_rank.csv, descartar 13 | 🟡 Media |
| 5 | EMAL/SERPAVI/transporte nulls | Medio | Crear script de imputación con flags | 🟡 Media |
| 6 | VPO 93,6% ceros | — | Documentar como limitación (no corregir) | ⚪ Baja |
| 7 | ECVI precio_m2 nulls (29/29) | Bajo | Extender limpiar_ecvi.py para capturar Viv. Usadas | 🟢 Media |
| 8 | Cobertura anuncios (84/252, 6 robustos) | Medio-Alto | Scraping dirigido + documentar sesgo | 🟡 Media |
| 9 | Idealista no automatizado | Medio | Documentar como limitación (coste/aprobación) | ⚪ Baja |
| 10 | Pisos.com geo inválida 100% | Medio-Alto | Pilot geocoding (opcional) | ⚪ Baja |

**Estimación total:** 1-2 días de trabajo para puntos 1-5 + 7. Puntos 6, 9, 10 se documentan sin código.

---

## 1. Punto 1 — 6 CSVs sin BOM

### Estado actual
- Los 7 scripts ya tienen `encoding="utf-8-sig"` (corregido en Q2).
- Los 6 CSVs en `data/procesado/` son salidas stale sin BOM:
  - `cert_energetico_municipal_252.csv`
  - `comparativa_compra_alquiler_af.csv`
  - `dim_municipios_enriquecido.csv`
  - `ecvi_compraventa_limpio.csv`
  - `eustat_demografia_renta_252.csv`
  - `transporte_paradas_municipio_enriquecido.csv`

### Plan de corrección
Ejecutar los 7 scripts en orden de dependencias:

```bash
# Orden: limpiar_ecvi → generar_mercado_area_funcional; calcular_renta_joven → calcular_tension_social
.venv/Scripts/python.exe transform/limpiar_ecvi.py
.venv/Scripts/python.exe transform/limpiar_eustat_demografia.py
.venv/Scripts/python.exe transform/enriquecer_gtfs_conectividad.py
.venv/Scripts/python.exe transform/generar_cert_energetico_municipal.py
.venv/Scripts/python.exe transform/calcular_renta_joven.py
.venv/Scripts/python.exe transform/calcular_tension_social.py
.venv/Scripts/python.exe transform/generar_mercado_area_funcional.py
```

### Verificación
- Los 6 CSVs deben empezar con BOM (`EF BB BF`).
- Row/column counts sin cambio.
- `pytest tests/test_raw_guardrails.py -q` sigue pasando.

### Riesgos
- In-place overwrite; si un script falla, el archivo queda parcial.
- Scripts usan rutas relativas → ejecutar desde la raíz del proyecto.
- `generar_mercado_area_funcional` depende de `ecvi_compraventa_limpio.csv`.

### Dependencias
Raw inputs + `dim_municipios.csv`, `municipio_area_funcional_ecvi.csv`, `alquiler_municipal_completo.csv`, `analisis_variables_base.csv`, `distancias_haversine_252.csv`.

---

## 2. Punto 2 — 2 JSONs Fotocasa con codigo_ine vacío

### Estado actual
- `normalizar_json_crudos.py` ya maneja `norm_code('') → None` y la rama Fotocasa asigna `None`.
- Los 2 JSONs raw (`anuncios_fotocasa.json`, variantes geo/meta) tienen 2-4 vacíos.
- Los JSONs normalizados no se han regenerado.

### Plan de corrección
Ejecutar el normalizador (no requiere cambio de código):

```bash
.venv/Scripts/python.exe transform/normalizar_json_crudos.py
```

### Verificación
- Los JSONs normalizados tienen `codigo_ine: null` donde estaba vacío.
- `metadata.fecha_extraccion` inyectado donde faltaba.
- Raw intacto (no modificado).

### Riesgos
- Sobrescribe todos los `*_normalizado.json`.
- JSONs inválidos se saltan.
- No refresca CSVs downstream a menos que se re-ejecuten sus generadores.

### Dependencias
JSONs raw válidos en UTF-8.

---

## 3. Punto 3 — No-determinismo en outputs

### Estado actual
- `f4_pisos_dirigido.py` y `filtrar_outliers.py` ya corregidos (fecha fija `2026-10-30T00:00:00`, sin `datetime.now`/`uuid`).
- Los outputs generados anteriormente tienen timestamps/UUIDs.

### Plan de corrección
```bash
.venv/Scripts/python.exe transform/filtrar_outliers.py
.venv/Scripts/python.exe transform/f4_pisos_dirigido.py
```

### Verificación
- `f4_pisos_dirigido` escribe nombre de lote determinista, sin timestamps/UUIDs.
- `filtrar_outliers` flags/metadata reproducibles.

### Riesgos
- `f4_pisos_dirigido` requiere acceso a red a Pisos.com (puede fallar/bloquear).
- Crea un archivo de lote raw (conteo raw crece) vía `_raw_guard`.
- Necesita `f4_pisos_objetivo.json`.

### Dependencias
`extract/_common.py`, `entity_resolution.py`, `extract/08_pisos_scraper.py`, `data/raw/anuncios_pisos.json`, `data/procesado/f4_pisos_objetivo.json`, red.

---

## 4. Punto 4 — 14 derivados en procesado_pre_silver

### Estado actual
Los 14 derivados son: `alquiler_rescatado_seccion.csv`, `f4_fotocasa.log`, `f4_pisos_objetivo.json.bak_r1`, `informe_calidad_f5.csv`, `pob_rank.csv`, `r1_batch_1..4.json`, `r1_fotocasa_informe.csv`, `r1_municipios_objetivo.json`, `r1_pisos_informe.csv`, `r1_sin_alquiler.json`, `v1_detalle.log`.

### Plan de corrección
- **Promover** `pob_rank.csv` a `data/procesado/` (con BOM).
- **Descartar** los otros 13 (dejar en `procesado_pre_silver` como backup; no borrar).

```bash
.venv/Scripts/python.exe -c "import pandas as pd; pd.read_csv('data/procesado_pre_silver/pob_rank.csv').to_csv('data/procesado/pob_rank.csv', index=False, encoding='utf-8-sig')"
```

### Verificación
- `data/procesado/pob_rank.csv` existe con BOM.
- Los otros 13 permanecen en `procesado_pre_silver/` (backup).

### Riesgos
- `pob_rank.csv` actualmente no tiene BOM; la conversión lo corrige.
- Borrar los 13 sería destructivo; dejarlos en backup es seguro.

### Dependencias
Ninguna.

---

## 5. Punto 5 — EMAL 73/252, SERPAVI 89 nulls, transporte 51 nulls

### Estado actual
- EMAL: 73/252 municipios con dato.
- SERPAVI: 89/249 nulls en `renta_m2_mes_eur`.
- Transporte: 51 nulls en `operadores`.
- Documentado en `docs/gaps_misconceptions_errores.md` pero sin saneamiento.

### Plan de corrección

**a) Transporte (fácil):** En `enriquecer_gtfs_conectividad.py`, rellenar nulls de `operadores` con `"sin_servicio"` y añadir flag `tiene_transporte_publico`.

**b) EMAL + SERPAVI (medio):** Crear `transform/imputar_nulos_fuentes.py`:
- Imputar por mediana de comarca → fallback a mediana regional.
- Añadir flags: `emal_imputado`, `serpavi_imputado`, `metodo_imputacion_*`.
- Mantener valores originales donde existen.

**c) Documentación:** Actualizar `docs/gaps_misconceptions_errores.md` con estrategia y conteos post-imputación.

### Comandos (tras implementación)
```bash
.venv/Scripts/python.exe transform/enriquecer_gtfs_conectividad.py
.venv/Scripts/python.exe transform/imputar_nulos_fuentes.py
.venv/Scripts/python.exe scratchpad/compare_calidad.py
.venv/Scripts/python.exe -m pytest tests/ -q
```

### Verificación
- `operadores` sin nulls.
- EMAL/SERPAVI target columns pobladas o flaggeadas como imputadas.
- Totales de nulls reducidos.
- Tests 66/66.

### Riesgos
- La imputación puede ocultar datos faltantes → mantener flags obligatorios.
- Necesita mapeo fiable de comarca.
- Código downstream que asume 51/89 nulls deberá actualizarse.

### Dependencias
`distancias_capitales.csv` (comarca), `dim_municipios`, `distancias_haversine_252.csv`, JSONs procesados de EMAL/SERPAVI.

---

## 6. Punto 6 — VPO 93,6% ceros

### Análisis
- Los ceros son **datos reales** (no hay dataset público de stock VPO municipal).
- Etxebide mide **demanda**, no stock.
- Imputar VPO fabricaría un efecto de política → inaceptable.

### Decisión: Documentar como limitación, no corregir.
- Añadir a `docs/gaps_misconceptions_errores.md` y `docs/puntos_flacos_dataset.md`.
- Opcional (bajo valor): transform que genere flag binario `tiene_vpo_adjudicada` + agregación territorial.

### Esfuerzo: Bajo (solo documentación).

---

## 7. Punto 7 — ECVI precio_m2 nulls (29/29)

### Análisis
- `precio_m2_usada_eur` es null en todos los 29 registros del CSV limpio.
- Pero los CSVs raw de ECVI (`t1_3`, `t2_3`, `t3_3`) contienen columnas `Viv. Usadas` con precios utilizables:
  - 4/4 territorios, 6/15 áreas, 3/7 municipios.
  - El resto son `n.d.` (no dato).

### Plan de corrección
Extender `transform/limpiar_ecvi.py` para:
1. Capturar columnas `Viv. Usadas` del raw.
2. Manejar `n.d.` como null.
3. Regenerar `ecvi_compraventa_limpio.csv` y `municipio_area_funcional_ecvi.csv`.

### Verificación
- `precio_m2_usada_eur` poblado donde hay dato real.
- `n.d.` restantes documentados como limitación o imputados por ratio territorio.

### Riesgos
- Alineación de columnas por territorio/área/municipio.
- Muchos `n.d.` permanecerán.

### Esfuerzo: Pequeño-Medio. **Recomendado: hacer.**

---

## 8. Punto 8 — Cobertura anuncios (84/252, 6 robustos)

### Análisis
- Fotocasa provincial ya agota páginas disponibles: Gipuzkoa 117, Bizkaia 338, Araba 14.
- Los municipios rurales simplemente no tienen anuncios.
- Scraping dirigido (`09_fotocasa_dirigido.py`, `10_scraping_faltantes.py`) puede añadir marginalmente.

### Plan de corrección
1. Ejecutar batches dirigidos para municipios de alta población sin cobertura (2 páginas cada uno).
2. Re-ejecutar `transform/unificar_anuncios.py`.
3. Documentar sesgo de selección (urbano vs rural).

### Esfuerzo: Medio-Alto. **Recomendado: parcial (batches dirigidos) + documentar sesgo.**

### Riesgos
- Límites de tasa/bloqueo IP.
- Duplicados.
- No alcanzará 252/252.

---

## 9. Punto 9 — Idealista no automatizado

### Análisis
- Script existe (`extract/09_realtyapi.py`, soporta `--todos`).
- No hay `REALTYAPI_KEY` configurada (solo placeholder `IDEALISTA_API_KEY` en `.env`).
- Requiere compra de key y/o aprobación de API oficial.

### Decisión: Documentar como limitación.
- No automatizable sin presupuesto/aprobación.
- Si se justifica por necesidad de cobertura media, obtener key y ejecutar.

### Esfuerzo: Medio (si se decide hacer).

---

## 10. Punto 10 — Pisos.com geo inválida 100%

### Análisis
- Las páginas de detalle de Pisos.com exponen lat/lon en la URL de la imagen del mapa.
- Existen polígonos municipales (`municipios_euskadi_252.geojson`).
- Se podría construir un scraper de detalle + spatial join.

### Plan de corrección (opcional, pilot)
1. Pilot en 20 anuncios para cuantificar valor.
2. Si el valor es alto, scraper completo + spatial join + actualizar `unificar_anuncios.py`.
3. Documentar incertidumbre (ubicaciones aproximadas).

### Esfuerzo: Medio-Alto. **Recomendado: pilot primero, luego decidir.**

---

## Orden de ejecución recomendado

### Fase A — Regeneración inmediata (puntos 1, 2, 3, 4, 7)
Ejecutar en orden:
1. `limpiar_ecvi.py` (point 7 + 1)
2. `limpiar_eustat_demografia.py` (point 1)
3. `enriquecer_gtfs_conectividad.py` (point 1 + 5a)
4. `generar_cert_energetico_municipal.py` (point 1)
5. `calcular_renta_joven.py` (point 1)
6. `calcular_tension_social.py` (point 1)
7. `generar_mercado_area_funcional.py` (point 1)
8. `normalizar_json_crudos.py` (point 2)
9. `filtrar_outliers.py` (point 3)
10. `f4_pisos_dirigido.py` (point 3, requiere red)
11. Promover `pob_rank.csv` (point 4)

### Fase B — Saneamiento de nulls (punto 5)
12. Implementar `imputar_nulos_fuentes.py`.
13. Actualizar `enriquecer_gtfs_conectividad.py` (operadores).
14. Actualizar docs.

### Fase C — Mejoras opcionales (puntos 8, 10)
15. Scraping dirigido Fotocasa (point 8).
16. Pilot geocoding Pisos.com (point 10).

### Fase D — Documentación (puntos 6, 9)
17. Documentar VPO, Idealista como limitaciones.

---

## Archivos afectados por la regeneración

### Fase A — Regeneración inmediata

| Comando | Archivos de entrada (read) | Archivos de salida (write/overwrite) |
|---|---|---|
| `limpiar_ecvi.py` | `data/raw/ecvi_*.csv` (t1_3, t2_3, t3_3) | `data/procesado/ecvi_compraventa_limpio.csv`, `municipio_area_funcional_ecvi.csv` |
| `limpiar_eustat_demografia.py` | `data/raw/poblacion_edad.csv`, `renta_municipal.csv` | `data/procesado/eustat_demografia_renta_252.csv` |
| `enriquecer_gtfs_conectividad.py` | `data/raw/gtfs_*.zip`, `dim_municipios.csv` | `data/procesado/transporte_paradas_municipio_enriquecido.csv` |
| `generar_cert_energetico_municipal.py` | `data/raw/certificados_energeticos.csv` | `data/procesado/cert_energetico_municipal_252.csv` |
| `calcular_renta_joven.py` | `data/procesado/alquiler_municipal_completo.csv`, `analisis_variables_base.csv` | `data/procesado/renta_joven_estimada.csv` |
| `calcular_tension_social.py` | `data/procesado/alquiler_municipal_completo.csv`, `renta_joven_estimada.csv` | `data/procesado/tension_social_municipal.csv` |
| `generar_mercado_area_funcional.py` | `data/procesado/ecvi_compraventa_limpio.csv`, `municipio_area_funcional_ecvi.csv` | `data/procesado/comparativa_compra_alquiler_af.csv` |
| `normalizar_json_crudos.py` | `data/raw/*.json` (todos los JSONs) | `data/procesado/*_normalizado.json` (todos) |
| `filtrar_outliers.py` | `data/procesado/anuncios_unificados.csv` | `data/procesado/anuncios_unificados.csv` (in-place, flags) |
| `f4_pisos_dirigido.py` | `data/raw/anuncios_pisos.json`, `f4_pisos_objetivo.json` | `data/raw/f4_lote_*.json` (nuevo raw, append-only), `data/procesado/fotocasa_dirigido_informe.csv` |
| Promover pob_rank | `data/procesado_pre_silver/pob_rank.csv` | `data/procesado/pob_rank.csv` (nuevo) |

**Archivos raw que CRECEN:** `data/raw/` gana 1 nuevo archivo por ejecución de `f4_pisos_dirigido.py` (lote determinista). El resto solo sobrescribe outputs en `data/procesado/`.

### Fase B — Saneamiento de nulls

| Comando | Archivos de entrada | Archivos de salida |
|---|---|---|
| `enriquecer_gtfs_conectividad.py` (modificado) | `data/raw/gtfs_*.zip`, `dim_municipios.csv` | `data/procesado/transporte_paradas_municipio_enriquecido.csv` (overwrite) |
| `imputar_nulos_fuentes.py` (nuevo) | `data/procesado/udalmap_empleo_corregido.csv`, `data/procesado/serpavi_renta.csv`, `distancias_capitales.csv` | `data/procesado/emal_imputado.csv`, `serpavi_imputado.csv` (nuevos) o columnas añadidas a existentes |

### Fase C — Mejoras opcionales

| Comando | Archivos de entrada | Archivos de salida |
|---|---|---|
| Scraping dirigido Fotocasa | Red (Fotocasa) | `data/raw/anuncios_fotocasa_dirigido_*.json` (nuevos raw) |
| `unificar_anuncios.py` (re-ejecutar) | `data/raw/anuncios_*.json` | `data/procesado/anuncios_unificados.csv` (overwrite) |
| Pilot geocoding Pisos.com | `data/raw/anuncios_pisos.json`, `municipios_euskadi_252.geojson` | `data/procesado/anuncios_pisos_geocodificado.csv` (nuevo) |

### Resumen de impacto

- **Raw:** +1 archivo por ejecución de f4 (append-only, guardado por `_raw_guard`). El resto no toca raw.
- **Procesado:** 6 CSVs sobrescritos (BOM), 1 CSV nuevo (pob_rank), 2 CSVs nuevos (imputación), todos los `*_normalizado.json` sobrescritos.
- **Tests:** 66/66 sin cambios (no se modifican tests).
- **Docs:** `gaps_misconceptions_errores.md`, `metodologia.md`, `trazabilidad_datos.md` actualizados.

## Estado de ejecución (2026-10-30)

### Fase A — Regeneración inmediata ✅ COMPLETADA
- [x] 7 scripts BOM ejecutados (ECVI, eustat demografía, GTFS, cert, renta joven, tensión, mercado AF)
- [x] normalizar_json_crudos.py ejecutado (todos los JSONs normalizados)
- [x] filtrar_outliers.py ejecutado (flags reproducibles)
- [x] f4_pisos_dirigido.py ejecutado (red Pisos.com)
- [x] pob_rank.csv promovido a data/procesado/ (275 filas, BOM)
- [x] Verificación BOM: 36/36 CSVs con BOM (0 sin BOM)
- [x] Tests: 66/66 passing

### Fase B — Saneamiento de nulls ✅ COMPLETADA
- [x] enriquecer_gtfs_conectividad.py modificado: operadores vacío → "sin_servicio" + flag tiene_transporte_publico (51 sin_servicio, 201 con transporte)
- [x] imputar_nulos_fuentes.py creado: SERPAVI 89 nulls → provincia mediana (89), 0 regional, 0 restantes
- [x] docs/gaps_misconceptions_errores.md actualizado (EMAL/SERPAVI/transporte)
- [x] Tests: 66/66 passing

### Fase C — Mejoras opcionales ⏳ PENDIENTE
- [ ] Scraping dirigido Fotocasa (batches por municipio de alta población)
- [ ] Pilot geocoding Pisos.com (20 anuncios)

### Fase D — Documentación ✅ COMPLETADA (parcial)
- [x] EMAL documentado como cobertura parcial (73/252, ceros son datos reales)
- [x] SERPAVI documentado como imputado
- [x] Transporte documentado como corregido
- [ ] VPO documentado como limitación (pendiente)
- [ ] Idealista documentado como limitación (pendiente)

### Punto 7 — ECVI precio_m2 usada ✅ COMPLETADA
- [x] limpiar_ecvi.py extendido para capturar "Viv. Usadas" (t1_3, t2_3, t3_3)
- [x] 13/29 registros con precio_m2_usada_eur (antes 0)
- [x] Re-ejecutado, BOM verificado

### Verificación final ✅
- Tests: 66/66 passing
- BOM: 36/36 CSVs
- codigo_ine: 100% 5 dígitos (verificado anteriormente)
- Duplicados: 0% (verificado anteriormente)

```bash
# Tests
.venv/Scripts/python.exe -m pytest tests/ -q  # esperado: 66+ sin regresiones

# BOM check
.venv/Scripts/python.exe -c "
import os, glob
bad = [f for f in glob.glob('data/procesado/*.csv') if open(f,'rb').read(3) != b'\xef\xbb\xbf']
print(f'CSVs sin BOM: {len(bad)}')
"

# Determinismo check
.venv/Scripts/python.exe -c "
import json, hashlib
# verificar que f4_pisos_dirigido no tiene timestamps/uuid en output
"

# Calidad
.venv/Scripts/python.exe scratchpad/compare_calidad.py
.venv/Scripts/python.exe transform/auditoria_duckdb.py
```

### Criterio de éxito
- 0 CSVs sin BOM en `data/procesado/`.
- 0 codigo_ine inválido (ya corregido).
- Duplicados <1% (ya corregido, 0%).
- EMAL/SERPAVI/transporte con estrategia de null-handling documentada o imputada.
- ECVI precio_m2 poblado donde hay dato real.
- Tests 66+ sin regresiones.
- Docs actualizadas (gaps, metodologia, trazabilidad).

---

## Fuentes
- Auditoría spec-vs-proyecto: `docs/auditoria_specs_sin_infra_2026-10-30.md`
- Análisis subagentes: deleg_1e4d07f6 (task-0 y task-1)
- Plan v2 ejecutado: `docs/plan_replanning_ajustado_v2_2026-10-30.md`
- Informe de auditoría integral: `docs/informe_auditoria_integral_2026-10-30.md`
