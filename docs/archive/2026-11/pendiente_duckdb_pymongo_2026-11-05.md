# Pendiente DuckDB → PyMongo (RA4) — 2026-11-05

## Estado
- CSV canónicos (`data/resultados/mongo_*.csv`, 252/252/2/252/322) generados por PyMongo vía `analysis/run_analisis_mongo.py` (huella `f1e78870`). Evidencia RA4 válida.
- PNG (`g1..g5`, `A1..G`) generados hoy con DuckDB + matplotlib desde CSV silver (`transform/generar_dashboard_visual.py`, `transform/generar_dashboard_completo.py`, joins con `LPAD(CAST(codigo_ine AS VARCHAR),5,'0')`). No son evidencia “generado mediante PyMongo”.
- HTML (`dashboard.html`, `dashboard_completo.html`, `mapa_esquema_silver.html`) manuales (P-05). `G_gaps_limitaciones.png` tabla literal en `generar_dashboard_completo.py:174-185`.

## Resolución 2026-11-05
Migrado: `analysis/run_analisis_mongo.py::exportar_png_desde_mongo` genera los 13 PNG solo desde los 8 pipelines en memoria (PyMongo + matplotlib, `_fnum` normaliza Decimal128). `png_mongo: 13 ficheros`, `pytest 130 passed`, huella `f1e78870` intacta. DuckDB queda como legacy en `transform/generar_dashboard_*.py`, ya no es fuente de resultados.

Sin tocar `data/raw`, sin subir `procesado/` a HDFS (decisión solo-raw firmada).
