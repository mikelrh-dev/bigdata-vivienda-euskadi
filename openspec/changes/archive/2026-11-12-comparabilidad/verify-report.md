# Verify Report — Contrato de comparabilidad

**Fecha:** 2026-11-12
**Change:** `2026-11-12-comparabilidad`
**Comandos:** `.venv/Scripts/python.exe -m pytest tests -q`, `scripts/run_pipeline.py --check`, `--fase mongo --allow-mongo-write`, `--fase gold`, `--fase quality`.

## Resultados

| Comprobación | Resultado | Evidencia |
|---|---|---|
| Suite pytest | 277 colectados, 275 passed, 2 skipped, exit 0 | `pytest tests -q` |
| Manifiestos integridad | 354 raw + 182 silver, 0 errores | `run_pipeline.py --check` |
| Fase mongo | OK (rc=0, 2.7 s); 15 colecciones recargadas | `run_mongo_pipeline` |
| Fase gold | 4/4 OK (análisis, comparativa, sensibilidad, figuras) | `run_pipeline.py --fase gold` |
| Tensión canónica | 252 municipios, fallback fiscal 0 | `dim_municipios_tension.csv` |
| Categorías tensión | media 104 / alta 76 / baja 72 (delta documentado) | `dim_municipios_enriquecido.csv` |
| Conteos | 64/252 con anuncio, 60/252 con precio observable, 7 con `n_precio` | `mongo_esfuerzo_por_municipio.csv` |
| grep `83/252` en README/docs | 0 coincidencias | `grep -rn` |
| CSV alquiler con capa | `metodo_imputacion` e `is_imputed` presentes | `mongo_alquiler_por_municipio.csv` |
| Bootstrap no comparable | `esfuerzo_anuncios_pct_no_comparable` + `aviso` + `mezcla_vintage` | `bootstrap_robustos.csv` |

## Escenarios de los deltas

- COMPARABILIDAD-01 (capas no mezcladas): N1/N2/A1/A2/F/P filtran o etiquetan oficial/IDW. Verificado en código y en las figuras regeneradas.
- COMPARABILIDAD-02 (unidades y vintages): H8b usa €/m²; H6 usa €/habitación; P y F declaran año. Verificado en el código de `run_analisis_mongo.py` y `generar_figuras_N.py`.
- COMPARABILIDAD-03 (denominadores): el spec y `parametros_estudio.yaml` declaran INE Atlas renta_hogar 2024.
- AGREGACION-01/PISOS-03/CAPAS-01: conteos 64/252 y 60/252; capas etiquetadas.
- PREPARACION-VISUALIZACION-01/CONCLUSION-02/BOOTSTRAP-01: etiquetas y no comparabilidad declaradas.

## Limitaciones

- `gentle-ai` 4.0.0 no expone `sdd-verify-validate`; la verificación se hizo con los comandos del repo.
- El IC95 del bootstrap sigue midiendo dispersión relativa de anuncios 2026; se etiqueta como no comparable.
- Las figuras PNG cambian de bytes al regenerar; el manifest de silver se regeneró con `--fase quality`.

## Veredicto

PASS. Las 12 concepciones erróneas quedan corregidas o etiquetadas; la suite y los manifiestos están verdes.
