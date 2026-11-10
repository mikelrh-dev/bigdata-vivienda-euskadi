# Índice de documentación — BigData Vivienda Euskadi

Documentación vigente en `docs/`. El histórico (planes, auditorías y versiones antiguas) se conserva en el archivo local no versionado, fuera de este repositorio.

## Núcleo
- `informe_final.md` — informe final y conclusiones.
- `conclusiones_municipios.md` — conclusiones por municipio.
- `datos_finales_conclusiones_2026-11-05.md` — cifras canónicas de cierre.
- `metodologia.md` — metodología y decisiones.
- `matriz_indicadores.md` — indicadores y su cálculo.
- `informe_capacidad_mongo.md` — capacidad y operaciones de MongoDB.

## Datos y trazabilidad
- `raw_manifest_sha256.txt` — SHA-256 canónico de los 354 ficheros raw (dependencia del gate).
- `contrato_datos_raw.md` — contrato del raw inmutable.
- `reglas_limpieza.md` — reglas de limpieza.
- `diccionario_columnas.md` — diccionario de columnas.
- `arquitectura_datos.md` — arquitectura del pipeline.
- `modelo_mongodb.md` — modelo y operaciones Mongo.
- `trazabilidad_vm.md` — evidencia literal de comandos en VM/HDFS/Kafka.

## Análisis y defensa
- `preguntas_analisis_profesional.md` — preguntas de análisis O1–O4.
- `guion_defensa.md` — guion corto.
- `guion_defensa_12min.md` — guion completo de 12 minutos.
- `presentacion/` — deck de defensa (ver `presentacion/README.md`).

## Artefactos visuales y evidencia RA4 (P-05)
- NOTA: `dashboard.html`, `dashboard_completo.html` y `mapa_esquema_silver.html` son **manuales** con valores tecleados y **no** son evidencia automática RA4; `G_gaps_limitaciones.png` se genera desde conteos Mongo en `analysis/run_analisis_mongo.py::exportar_png_desde_mongo` (imputados/sin anuncios/sin precio), no con literales; el generador DuckDB antiguo fue retirado. La única evidencia válida son los 8 CSV `mongo_*` auto generados con PyMongo en `data/resultados/` (`mongo_esfuerzo_por_municipio.csv` 253 líneas, `mongo_alquiler_por_municipio.csv` 253, `mongo_modalidades.csv` 3, `mongo_accesibilidad_extendida.csv` 253, `mongo_tier_confianza.csv` 253, `mongo_vpo_por_municipio.csv` 323, `mongo_vpo_terminadas_por_municipio.csv` 252, `mongo_habitaciones_por_municipio.csv` 10, `comparativa_3_municipios_mongo.csv` 4).
