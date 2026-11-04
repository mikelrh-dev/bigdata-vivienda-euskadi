# Informe de Implementación — Cuarentena Silver y Reconciliación Documental

Repo: bigdata-vivienda-euskadi | Fecha: 2026-10-30
Autorización: usuario (T1→T2→T3→T4). Modo: ejecución con backup y pytest.

## 1. Resumen ejecutivo

Se aplicó la cuarentena estricta en la capa Silver mediante integridad referencial contra `dim_municipios.csv`, se derivaron las vistas de mercado desde el maestro ya limpio, se depuró la dimensión de empleo en processed y se reconcilió la documentación de `argon/`. Raw inmutable intacto. Tests: 59/59 passed.

## 2. Tareas ejecutadas

### T1 — Cuarentena Estricta (Silver Maestro)
- Script: `transform/unificar_anuncios.py`
- Backup: `data/procesado_backup_pre_t1/`
- Cambios: filtro por `codigo_ine` en dimensión (purga Las Rozas y cualquier no canónico) + sanity bounds (`superficie_m2 < 10`, `pm2 > 100`).
- Resultado: 873 → 873 (Las Rozas ya excluidas por resolver; cuarentena explícita ahora implementada).

### T2 — Vistas Analíticas (derivadas del maestro limpio)
- Script: `transform/generar_vistas_mercado.py`
- Cambios: residencial lee unificado limpio; habitaciones aplica cuarentena por `codigo_ine`.
- Resultado: residencial 570, habitaciones 201. Ambos con 0 filas que fallan cuarentena.

### T3 — Depuración de Dimensión (Silver)
- Script: `transform/corregir_empleo.py`
- Cambio: `.drop(columns=['tasa_paro_aprox_pct'])` en memoria antes de escribir.
- Resultado: processed 27 → 26 columnas. Raw `udalmap_empleo.csv` (24 cols) intacto.

### T4 — Reconciliación Documental
- Archivos: `argon/inventario_datos.md`, `argon/estado_proyecto_2026-10-29.md`, `argon/README_ARGON.md`, `argon/informe_preguntas_respuesta.md`, `docs/estado_proyecto_2026-10-29.md`, `docs/inventario_datos.md`.
- Conteos corregidos: raw 317, silver 101, unificados 873, residencial 570, habitaciones 201, robustos 6, html 101, haversine 63504, geojson 252, alquiler 253×15 (sin codigo_ine), ECVI xlsx 3, fotocasa 60 canónicos.
- Deuda fantasma eliminada (HTML persistido, superficie extraída, haversine completo). Nombres/rutas corregidos. Score normalizado a 8.6.

## 3. Métricas finales

| Artefacto | Valor |
|---|---:|
| anuncios_unificados.csv | 873 |
| anuncios_vivienda_residencial.csv | 570 |
| anuncios_habitaciones_unificados.csv | 201 |
| udalmap_empleo_corregido (cols) | 26 (raw 24) |
| Municipios robustos (n≥30) | 6 |
| pytest | 59 passed |

## 4. Integridad

- `data/raw/` no modificado (raw immutability tests pasan).
- Backup previo: `data/procesado_backup_pre_t1/`.
- Manifest SHA-256 sin cambios (raw intacto).

## 5. Siguiente paso sugerido

Autorizar Fase 4 (Docker Compose HDFS + MongoDB) o continuar con análisis Silver (agregaciones, esfuerzo). No se han tocado infraestructura ni código de producción más allá de transform/.
PY