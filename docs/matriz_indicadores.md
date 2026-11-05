# Matriz de indicadores (5)

Fuente de verdad: pipeline Mongo `analysis/mongo_aggregations.py` + CSV silver `data/procesado/analisis_variables_base.csv`. Un indicador = una fuente, un pipeline y una limitacion.

| # | Indicador | Definicion y formula | Fuente cruda (raw / silver) | Pipeline Mongo (verificacion) | Cobertura y laguna |
|---|---|---|---|---|---|
| 1 | Esfuerzo 18-34 canonico | `cuantia_media_eur_mes_mediana` (Eustat oficial, Eje D) x12 / `renta_joven_estimada_18_34` x100; sin imputar, solo 159 oficiales | Eustat alquiler oficial 2024 + Eustat renta (proxy ratio fiscal) | `pipeline_indicadores_municipio` (esfuerzo_joven_pct_18_34 con fallback legacy) + `pipeline_top_municipios_por_esfuerzo` + `comparativa_3_municipios_mongo.csv` | 159/252 oficial; 93 IDW solo sensibilidad. Proxy de renta, no salario real. |
| 2 | Esfuerzo 16-29 legacy | `cuantia_media_eur_mes_mediana` x12 / `renta_joven_estimada_16_29` x100; se conserva por compatibilidad | Eustat alquiler oficial 2024 + Eustat renta 16-29 | `pipeline_indicadores_municipio` (esfuerzo_joven_pct_16_29 = esfuerzo_joven_pct) y espejo en `pipeline_vpo_por_municipio` / `pipeline_accesibilidad_extendida` | Solo legacy/demo; no usar para conclusiones nuevas. Mediana 16-29 oficial 43,5% no comparable con 18-34. |
| 3 | Tension social (demanda social) | `(percentil(Etxebide solicitudes por mil 2024) + percentil(esfuerzo joven canonico)) / 2` en 0-100; categoria baja <33, media <66, alta >=66 | `data/raw/etxebide_solicitudes.csv` (anio 2024) + `dim_municipios_renta.csv` (esfuerzo) | No hay pipeline Mongo directo; se genera en silver `transform/calcular_tension_social.py` -> `data/procesado/dim_municipios_tension.csv` (`tension_demanda_social`, `tension_categoria`). | Juicio percentil, no metrica; 73 alta / 102 media / 77 baja. |
| 4 | Paro Lanbide | `tasa_paro_lanbide_pct` municipal 2026; nunca `tasa_paro_aprox_pct` (NaN en 252) | Lanbide -> `analisis_variables_base.csv` col. `tasa_paro_lanbide_pct` | Sin pipeline propio; se join-a en silver por `codigo_ine` a 5 digitos. | Anio 2026 vs renta 2024; em mezclan vintage. |
| 5 | Precio m2 (alquiler) | `renta_media_eur_m2_mediana` EUR/m2/mes (Eustat oficial) | Eustat alquiler oficial -> `alquiler_municipal_completo.csv` + `alquiler_municipal` en Mongo | `pipeline_indicadores_municipio` (`renta_m2_alquiler`) + `pipeline_alquiler_por_municipio` (`$group`/`$lookup`/`$unwind` a `municipios`) | 159 oficial y 93 IDW; mediana canonica. |

## Notas transversales

- `n_anuncios` y `precio_medio_eur` pertenecen al pipeline 1 y a `anuncios` (2026), no al precio m2 oficial; no confundir `precio_medio_eur` (foto de anuncios) con `cuantia_media_eur_mes_mediana` (Eustat).
- `pipeline_esfuerzo_por_sexo`, `pipeline_accesibilidad_extendida`, `pipeline_udalmap_extendido_osrm` y `pipeline_vpo_por_municipio` replican los esfuerzos para desglose por sexo, accesibilidad y VPO; no crean indicadores nuevos.
- 8 pipelines en `analysis/mongo_aggregations.py`: indicadores, alquiler, modalidades, top esfuerzo, esfuerzo sexo, accesibilidad extendida, udalmap_osrm, vpo.
