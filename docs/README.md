# Índice de documentación — BigData Vivienda Euskadi

Documentación vigente (docs/). Los archivos en argon/ son una copia para revisión externa (gitignored).

## Núcleo
- archive/2026-11/estado_proyecto_2026-10-29.md — estado actual del proyecto (conteos, fases).
- archive/2026-11/inventario_datos.md — inventario de archivos raw/procesado.
- metodologia.md — metodología y decisiones.
- archive/2026-11/trazabilidad_datos.md — trazabilidad raw → silver.
- archive/2026-11/gaps_misconceptions_errores.md — gaps y limitaciones.
- archive/2026-11/puntos_flacos_dataset.md — puntos flacos del dataset.

## Decisiones y fuentes
- archive/2026-11/decision_salario_proxy.md — proxy salarial joven.
- archive/2026-11/fuentes_cartografia_empleo.md — fuentes cartografía/empleo.
- archive/2026-11/fuentes_salario_joven.md — fuentes salario joven.
- archive/2026-11/correlacion_renta_alquiler.md — correlación renta-alquiler.
- archive/2026-11/plan_gestion_datos_fase1.md — plan fase 1.

## Mapas y análisis
- archive/2026-11/mapa_relaciones.md — mapa ER y relaciones (v2).
- preguntas_analisis_profesional.md — preguntas de análisis.
- archive/2026-11/informe_preguntas_respuesta.md — informe preguntas/respuestas.

## Auditorías e informes recientes
- archive/2026-11/auditoria_argon_2026-10-30.md
- archive/2026-11/auditoria_framework_completo2_2026-10-30.md
- archive/2026-11/informe_implementacion_cuarentena_2026-10-30.md

## Archivo
- archive/ — planes y versiones antiguas (legacy).

## Artefactos visuales y evidencia RA4 (P-05)
- NOTA: `dashboard.html`, `dashboard_completo.html` y `mapa_esquema_silver.html` son **manuales** con valores tecleados y **no** son evidencia automática RA4; `G_gaps_limitaciones.png` se genera desde conteos Mongo en `analysis/run_analisis_mongo.py::exportar_png_desde_mongo` (imputados/sin anuncios/sin precio), no con literales; el generador DuckDB antiguo fue retirado. La única evidencia válida son los 8 CSV `mongo_*` auto generados con PyMongo en `data/resultados/` (`mongo_esfuerzo_por_municipio.csv` 253 líneas, `mongo_alquiler_por_municipio.csv` 253, `mongo_modalidades.csv` 3, `mongo_accesibilidad_extendida.csv` 253, `mongo_tier_confianza.csv` 253, `mongo_vpo_por_municipio.csv` 323, `mongo_vpo_terminadas_por_municipio.csv` 252, `mongo_habitaciones_por_municipio.csv` 10, `comparativa_3_municipios_mongo.csv` 4).

