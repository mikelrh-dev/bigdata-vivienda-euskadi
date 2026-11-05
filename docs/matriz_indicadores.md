# Matriz de indicadores (5)

Fuente de verdad: pipeline Mongo `analysis/mongo_aggregations.py` + CSV silver `data/procesado/analisis_variables_base.csv`. Un indicador = una fuente, un pipeline y una limitacion.

| # | Indicador | Definicion y formula | Fuente cruda (raw / silver) | Pipeline Mongo (verificacion) | Cobertura y laguna |
|---|---|---|---|---|---|
| 1 | Esfuerzo 18-34 canonico | `cuantia_media_eur_mes_mediana` (Eustat oficial, Eje D) x12 / `renta_joven_estimada_18_34` x100; sin imputar, solo 159 oficiales | Eustat alquiler oficial 2024 + Eustat renta (proxy ratio fiscal) | `pipeline_indicadores_municipio` (esfuerzo_joven_pct_18_34 con fallback legacy) + `pipeline_top_municipios_por_esfuerzo` + `comparativa_3_municipios_mongo.csv` | 159/252 oficial; 93 IDW solo sensibilidad. Proxy de renta, no salario real. |
| 2 | Esfuerzo 16-29 legacy | `cuantia_media_eur_mes_mediana` x12 / `renta_joven_estimada_16_29` x100; se conserva por compatibilidad | Eustat alquiler oficial 2024 + Eustat renta 16-29 | `pipeline_indicadores_municipio` (esfuerzo_joven_pct_16_29 = esfuerzo_joven_pct) y espejo en `pipeline_vpo_por_municipio` / `pipeline_accesibilidad_extendida` | Solo legacy/demo; no usar para conclusiones nuevas. Mediana 16-29 oficial 43,5% no comparable con 18-34. |
| 3 | Tension social (demanda social) | `(percentil(Etxebide solicitudes por mil 2024) + percentil(esfuerzo joven canonico)) / 2` en 0-100; categoria baja <33, media <66, alta >=66 | `data/raw/etxebide_solicitudes.csv` (anio 2024) + `dim_municipios_renta.csv` (esfuerzo), presente en Mongo `municipios.demanda_social` y coleccion `etxebide_solicitudes` (5040 docs, auditada solo lectura) | `pipeline_indicadores_municipio` expone `demanda_social.*` (`tension_demanda_social`, `tension_categoria`, `etxebide_solicitudes_por_mil`) desde Mongo; el percentil se calculo en silver `transform/calcular_tension_social.py` y quedo almacenado en `municipios.demanda_social` (252/252). | Juicio percentil, no metrica; 76 alta / 103 media / 73 baja. |
| 4 | Paro Lanbide | `tasa_paro_lanbide_pct` municipal 2026; nunca `tasa_paro_aprox_pct` (NaN en 252) | Lanbide -> `analisis_variables_base.csv` col. `tasa_paro_lanbide_pct`, presente en Mongo `municipios.empleo.tasa_paro_lanbide_pct` (249/252; Bilbao 9,71, Donostia 5,82, Getxo 6,40, Vitoria-Gasteiz 8,89) | `pipeline_indicadores_municipio` (`tasa_paro_lanbide_pct` desde `empleo`, sin join silver) + `comparativa_mongo.comparativa_cuatro_robustos`. | Anio 2026 vs renta 2024; em mezclan vintage. |
| 5 | Precio m2 (alquiler) | `renta_media_eur_m2_mediana` EUR/m2/mes (Eustat oficial) | Eustat alquiler oficial -> `alquiler_municipal_completo.csv` + `alquiler_municipal` en Mongo | `pipeline_indicadores_municipio` (`renta_m2_alquiler`) + `pipeline_alquiler_por_municipio` (`$group`/`$lookup`/`$unwind` a `municipios`) | 159 oficial y 93 IDW; mediana canonica. |

## Notas transversales

- `n_anuncios` y `precio_medio_eur` pertenecen al pipeline 1 y a `anuncios` (2026), no al precio m2 oficial; no confundir `precio_medio_eur` (foto de anuncios) con `cuantia_media_eur_mes_mediana` (Eustat).
- `pipeline_esfuerzo_por_sexo`, `pipeline_accesibilidad_extendida`, `pipeline_udalmap_extendido_osrm` y `pipeline_vpo_por_municipio` replican los esfuerzos para desglose por sexo, accesibilidad y VPO; no crean indicadores nuevos.
- 9 pipelines en `analysis/mongo_aggregations.py`: indicadores, alquiler, modalidades, top esfuerzo, esfuerzo sexo, accesibilidad extendida, udalmap_osrm, vpo promociones, vpo terminadas.
- Imputacion explicita (Bloque 4): `pipeline_indicadores_municipio` preserva `metodo_imputacion` (`oficial` 159 / `IDW_5_vecinos` 93) y deriva `is_imputed` (False oficial, True IDW); ningun calculo rellena con medianas en silencio.

## Huella Bloque 4 (2026-11-05, regenerado desde Mongo prod solo lectura)

| CSV canonico | Lineas | SHA-256 |
|---|---|---|
| `data/resultados/mongo_esfuerzo_por_municipio.csv` | 253 | `831e69cefda918698001f45f161f32295c190aac9d6b65bbf33297a488b4c9a4` |
| `data/resultados/mongo_alquiler_por_municipio.csv` | 253 | `ff39e852d27a754eabb2fe3db76c71c1ac35e8a0cdcd4e799ff9fb7c9798263e` |
| `data/resultados/mongo_modalidades.csv` | 3 | `71a7292623ac4d1695f63f7649ae551ae2557d4167e20935b0a863c4946731ef` |
| `data/resultados/comparativa_3_municipios_mongo.csv` (4 robustos) | 5 | `9dc4e8d34d736e6fb74f16a05d064fb249d398b0ceca8b3b7168c3709d3881bb` |

Huella agregada de los 9 pipelines (`huella_resultados`, SHA-256 con `sort_keys=True`): `08665d03687bbbde663831de8872d129983252de1881027a2e243bfd86f4c30a`. Verificacion: `wc -l data/resultados/mongo_esfuerzo_por_municipio.csv data/resultados/mongo_alquiler_por_municipio.csv data/resultados/mongo_modalidades.csv` = 253/253/3 y `data/resultados/comparativa_3_municipios_mongo.csv` = 5 (cabecera + Bilbao 173, Donostia 113, Getxo 40, Vitoria-Gasteiz 39, `codigo_ine` 5 digitos, paro Lanbide no nulo). Rango canonico 18-34; 16-29 legacy (mediana oficial 43,5%, no comparable, solo demo).
