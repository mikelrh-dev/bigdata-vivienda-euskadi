# Diagnóstico de la regeneración incompleta

Tu compañero tenía razón. La causa es exactamente la que sospechaban: al borrar `data/procesado/` y `data/resultados/`, la regeneración ejecutada no volvió a producir todos los documentos porque **los `.py` que los sacan no se ejecutaron con el orquestador que regeneró esas capas**. Hay dos efectos distintos y ambos confirmados por código real.

## Conteo real (esta copia, con datos)

### data/resultados/
- 56 ficheros reales (excluyendo `.gitkeep`, `README.md` y `anexo/`).
- `transform/run_all.py` declara 2 resultados: `mapa_esquema_silver.html` y `auditoria_lagunas_silver.csv`.
- Los otros **54 ficheros no están declarados por `run_all.py`**, pero existen en disco porque alguien los generó con otros scripts.

Entre esos 54, están:

**12 CSV de MongoDB:**
`mongo_esfuerzo_por_municipio.csv`, `mongo_alquiler_por_municipio.csv`, `mongo_modalidades.csv`, `mongo_vpo_por_municipio.csv`, `mongo_accesibilidad_extendida.csv`, `mongo_tier_confianza.csv`, `mongo_vpo_terminadas_por_municipio.csv`, `comparativa_3_municipios_mongo.csv`, `capa_oficial.csv`, `capa_idw.csv`, `capa_contexto.csv`, `udalmap_paro.csv`, `ranking_esfuerzo.csv`
→ todos producidos por **`analysis/run_analisis_mongo.py`**.

**2 CSV de sensibilidad:**
`sensibilidad_idw.csv`, `bootstrap_robustos.csv`
→ producidos por **`analysis/sensibilidad.py`**.

**9 PNG de P0 o PNG compartidos:**
`mapa_coroplastico_esfuerzo_18_34.png`, `hist_esfuerzo_18_34_umbral30.png`, `dumbbell_esfuerzo_18_24_vs_25_34.png`, `transporte_oferta_vs_esfuerzo.png`, `F_comparativa_TH.png`, `H2_tier_confianza_ABCD.png`, `H8_tier_mediana_temporal_vs_larga.png`, `J_tier_confianza_vs_precio.png`, `P_oficial_vs_anuncios_por_TH.png`
→ producidos por **`transform/generar_figuras_N.py`** (y `run_analisis_mongo.py` para algunos de ellos).

**24 PNG de `run_analisis_mongo.py`:**
`A1_distribucion_esfuerzo_por_TH.png`, `A2_pct_inasequibles_por_TH.png`, `B_paro_vs_precio.png`, `C_vpo_por_estado.png`, `D_distancia_vs_precio.png`, `E_confort_vs_esfuerzo.png`, `g2_renta_vs_alquiler.png`, `g3_top10_precio_medio.png`, `g4_distribucion_anuncios.png`, `g5_esfuerzo_robustos.png`, `H1_ranking_esfuerzo_18_34.png`, `H3_esfuerzo_por_sexo.png`, `H5_vpo_terminadas_por_mil.png`, `H6_habitaciones_mediana_rango.png`, `H7_accesibilidad_tiempo_capital.png`, `H10_tension_vs_esfuerzo.png`, `H11_imputacion_oficial_idw_por_TH.png`, `H13_mediana_precio_m2_winsorizada.png`, `O_ranking_bloqueado_n30.png`, y los 5 anexos que quedan en `data/resultados/anexo/` (`G_gaps_limitaciones.png`, `H4_esfuerzo_18_34_vs_16_29.png`, `H9_modalidades_larga_vs_temporal.png`, `I_modalidad_temporal_vs_larga.png`, `K_vpo_terminadas_vs_esfuerzo.png`, `L_confort_accesibilidad_vs_esfuerzo.png`, `H12_vpo_promociones_estado_tipologia.png`, `g1_esfuerzo_por_territorio.png`).

**2 HTML manuales:**
`dashboard.html`, `dashboard_completo.html`
→ **no generados por script**; son documentos estáticos, según `data/resultados/README.md`.

## data/procesado/

- 128 ficheros reales (excluyendo `.meta.json`, `.gitkeep`, `run_manifest.json`).
- `transform/run_all.py` declara 116 productos en `data/procesado/`.
- Los otros **14 productos no están declarados por `run_all.py`**, pero existen porque se generaron con scripts que no está en el orquestador:

```
acta_ingesta.md, csvs_index.json, index.json, ingestion_manifest.json,
manifest_sha256.txt, nombres_normalizados_map.json                        → extract/normalizar_metadata.py
fotocasa_dirigido_informe.csv, anuncios_pisos_dirigido.csv, anuncios_pisos_dirigido.json  → extract/09_fotocasa_dirigido.py
f4_pisos_informe.csv                                                        → extract/09_fotocasa_dirigido.py
f4_pisos_objetivo.json                                                      → transform/generar_f4_pisos_objetivo.py (EXCLUIDO)
pob_rank.csv, renta_municipal_referencia.csv                              → no cubiertos por run_all.py en este estado
run_manifest.json                                                           → lo escribe run_all.py al ejecutarse
```

**Lo más importante:** `run_all.py` declara 116 productos, pero hay 128 en disco, y de esos 116, muchos están vacíos en este estado porque el orquestador no se ejecutó (o no llegó a generarlos por falta de dependencias). Esto significa que no solo faltan los que no genera, sino también los que sí debería generar y no los generó.

## Scripts excluidos del orquestador

`transform/run_all.py` tiene un diccionario `EXCLUIDOS` con 8 scripts que no ejecuta:

```
_raw_guard.py                        → librería, no paso del pipeline
f4_pisos_dirigido.py                 → captura dirigida manual (escribe en raw con guard)
generar_f4_pisos_objetivo.py         → lista manual de objetivos de f4
generar_figuras_N.py                 → PNG P0 N1,N2,N3,N7 y H2 sin Mongo vivo
generar_fotocasa_dirigido_informe.py → informe de captura dirigida
muni_resolve.py                      → librería, no ejecutable del pipeline
run_all.py                           → el propio orquestador
validar_renta.py                     → QA bajo demanda, no ETL silver
```

Esto significa que **`run_all.py` no va a ejecutar a los productores de los productos que faltan**. Por diseño.

## Qué hace cada orquestador real y qué no

- `transform/run_all.py`: genera parte del silver (116 productos declarados, algunos vacíos en este estado) y solo 2 resultados (`mapa_esquema_silver.html`, `auditoria_lagunas_silver.csv`).
- `extract/normalizar_metadata.py`: genera la metadata de ingesta en `data/procesado/_meta/`.
- `extract/generar_manifest.py --write`: genera `data/procesado/manifest_sha256.txt`.
- `extract/09_fotocasa_dirigido.py`: genera informes de captura dirigida en `data/procesado/`.
- `analysis/run_analisis_mongo.py`: genera 12 CSV de mongo + 24 PNG en `data/resultados/`.
- `analysis/sensibilidad.py`: genera 2 CSV de sensibilidad en `data/resultados/`.
- `transform/generar_figuras_N.py`: genera 9 PNG en `data/resultados/` (N1,N2,N3,N7,H2,F,H8,J,P).
- `transform/auditar_lagunas_silver.py`: genera `auditoria_lagunas_silver.csv`.
- `transform/generar_mapa_esquema.py`: genera `mapa_esquema_silver.html`.
- `docs/presentacion/build_presentacion.py`: posible generador de los dashboards HTML (no se ha verificado si están presentes o son manuales).
- `dashboard.html` y `dashboard_completo.html`: no se regeneran por script (según `data/resultados/README.md`, son estáticos).

## Veredicto

La causa es **real y verificada**: la regeneración que tu compañero ejecutó no produjo todos los documentos porque ejecutó solo un orquestador (`transform/run_all.py`) que no genera casi nada de `data/resultados/` y no genera parte de `data/procesado/`. Los scripts productores están en el proyecto, pero están fuera del orquestador que regeneró las capas. Esto no es un bug del sistema de raw ni un error de los guardrails: es que la reconstrucción completa requiere varios orquestadores y scripts manuales, y tu compañero ejecutó solo uno.

## Qué comandos necesitaría para regenerar todo (desde raw intacto)

```bash
# 1. Metadata de ingesta
python extract/normalizar_metadata.py

# 2. Manifiesto canónico de raw
python extract/generar_manifest.py --write

# 3. Silver
python transform/run_all.py

# 4. Informes de captura dirigida
python extract/09_fotocasa_dirigido.py
python transform/generar_fotocasa_dirigido_informe.py
python transform/generar_f4_pisos_objetivo.py

# 5. Resultados desde MongoDB
python analysis/run_analisis_mongo.py
python analysis/sensibilidad.py

# 6. Figuras P0 y complementarias
python transform/generar_figuras_N.py

# 7. Auditoría y mapa silver
python transform/auditar_lagunas_silver.py
python transform/generar_mapa_esquema.py
```

Y los dashboards HTML no se regeneran por script.
