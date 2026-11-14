# Cifras vigentes

Generado: `2026-11-14T17:12:19+00:00` · Fuente: `vaultVivienda/notebooklm/NB04-BDA-Mongo/_facts.json` + `data/resultados/`.

> No editar a mano: se regenera con `python docs/memoria/build.py --refresh`.

## MongoDB

| Clave | Valor | Fuente |
|---|---:|---|
| `mongo.anuncios_docs` | 594 | _facts.json · anuncios.docs |
| `mongo.backup` | 15 | _facts.json · collections_backup |
| `mongo.certificados_docs` | 252 | _facts.json · certificados_energeticos.docs |
| `mongo.csv_salidas` | 8 | _facts.json · pipelines.csv_outputs |
| `mongo.esfuerzo_2026_docs` | 252 | _facts.json · esfuerzo_mercado_2026.docs |
| `mongo.habitaciones` | 201 | _facts.json · anuncios_habitaciones_unificados.docs |
| `mongo.indices_creados` | 8 | _facts.json · defined_indexes - defined_indexes_missing |
| `mongo.indices_definidos` | 10 | _facts.json · defined_indexes |
| `mongo.municipios_docs` | 252 | _facts.json · municipios.docs |
| `mongo.pipelines` | 11 | _facts.json · pipelines.ordered |
| `mongo.pipelines_fuera_orden` | 1 | _facts.json · pipelines.outside_order |
| `mongo.pipelines_total` | 12 | _facts.json · pipelines.defined |
| `mongo.total` | 32 | _facts.json · collections_total |
| `mongo.vivas` | 17 | _facts.json · collections_live |
| `mongo.vpo_municipal_docs` | 252 | _facts.json · vpo_municipal.docs |

## Datos y análisis

| Clave | Valor | Fuente |
|---|---:|---|
| `datos.alquiler_imputado` | 93 | mongo_esfuerzo_por_municipio.csv · 252 - oficiales |
| `datos.alquiler_oficial` | 159 | mongo_esfuerzo_por_municipio.csv · tiene_alquiler_oficial |
| `datos.anuncios_2026` | 287 | comparacion_esfuerzo_2024_2026_resumen.csv · n_anuncios |
| `datos.anuncios_2026_tipo_1_2` | 123 | esfuerzo_por_tipo_nivel_anuncio_2026.csv · 1-2 hab |
| `datos.anuncios_2026_tipo_3` | 94 | esfuerzo_por_tipo_nivel_anuncio_2026.csv · 3 hab |
| `datos.anuncios_2026_tipo_4` | 60 | esfuerzo_por_tipo_nivel_anuncio_2026.csv · 4+ hab |
| `datos.anuncios_larga` | 326 | n_larga_estancia |
| `datos.anuncios_larga_municipios` | 53 | municipios con n_larga_estancia > 0 |
| `datos.anuncios_municipios` | 64 | municipios con n_anuncios > 0 |
| `datos.anuncios_sin` | 188 | municipios sin anuncio |
| `datos.anuncios_temporal` | 268 | n_temporal |
| `datos.anuncios_temporal_municipios` | 38 | municipios con n_temporal > 0 |
| `datos.anuncios_total` | 594 | mongo_esfuerzo_por_municipio.csv · n_anuncios |
| `datos.brecha_mediana_n5` | 52,7 | brecha_esfuerzo_2024_2026.csv · mediana de brecha_pp_18_34 con n>=5 |
| `datos.brecha_municipios_n5` | 7 | brecha_esfuerzo_2024_2026.csv · municipios con n>=5 |
| `datos.cobertura_anuncios_n30_pct` | 70,38 | cobertura_representatividad_2026.csv · pct_anuncios_en_municipios_n_mayor_igual_30 |
| `datos.cobertura_municipios_pct` | 19,84 | cobertura_representatividad_2026.csv · pct_municipios_cubiertos |
| `datos.cobertura_poblacion` | 334.753 | cobertura_representatividad_2026.csv · poblacion_18_34_cubierta |
| `datos.cobertura_poblacion_pct` | 71,21 | cobertura_representatividad_2026.csv · pct_poblacion_18_34_cubierta |
| `datos.esfuerzo_2024_canonico` | 30,70 | comparacion_esfuerzo_2024_2026_resumen.csv · 2024 canónico |
| `datos.esfuerzo_2024_salario` | 44,57 | comparacion_esfuerzo_2024_2026_resumen.csv · 2024 base salario |
| `datos.esfuerzo_2026_renta` | 57,77 | comparacion_esfuerzo_2024_2026_resumen.csv · 2026 base renta 2024 |
| `datos.esfuerzo_2026_salario` | 78,55 | comparacion_esfuerzo_2024_2026_resumen.csv · 2026 base salario |
| `datos.esfuerzo_2026_tipo_1_2` | 78,55 | esfuerzo_por_tipo_nivel_anuncio_2026.csv · 1-2 hab |
| `datos.esfuerzo_2026_tipo_3` | 81,95 | esfuerzo_por_tipo_nivel_anuncio_2026.csv · 3 hab |
| `datos.esfuerzo_2026_tipo_4` | 116,37 | esfuerzo_por_tipo_nivel_anuncio_2026.csv · 4+ hab |
| `datos.esfuerzo_idw_sobre30` | 47 | esfuerzo_joven_pct_18_34 > 30 · 252 municipios |
| `datos.esfuerzo_idw_sobre30_pct` | 18,65 | sobre30 / 252 * 100 |
| `datos.esfuerzo_mediana_idw` | 25,37 | mediana de esfuerzo_joven_pct_18_34 · 252 municipios |
| `datos.esfuerzo_mediana_oficial` | 26,61 | mediana de esfuerzo_joven_pct_18_34 · oficiales |
| `datos.esfuerzo_oficial_sobre30` | 40 | esfuerzo_joven_pct_18_34 > 30 · oficiales |
| `datos.esfuerzo_oficial_sobre30_pct` | 25,16 | sobre30 / oficiales * 100 |
| `datos.habitaciones_municipios` | 9 | mongo_habitaciones_por_municipio.csv · filas |
| `datos.mun_astigarraga_alquiler` | 867 | mongo_esfuerzo_por_municipio.csv · 20903 · cuantia_alquiler_mes |
| `datos.mun_astigarraga_esfuerzo` | 36,37 | mongo_esfuerzo_por_municipio.csv · 20903 |
| `datos.mun_barakaldo_alquiler` | 746 | mongo_esfuerzo_por_municipio.csv · 48013 · cuantia_alquiler_mes |
| `datos.mun_barakaldo_esfuerzo` | 38,50 | mongo_esfuerzo_por_municipio.csv · 48013 |
| `datos.mun_basauri_alquiler` | 672 | mongo_esfuerzo_por_municipio.csv · 48015 · cuantia_alquiler_mes |
| `datos.mun_basauri_esfuerzo` | 36,09 | mongo_esfuerzo_por_municipio.csv · 48015 |
| `datos.mun_bilbao_alquiler` | 850 | mongo_esfuerzo_por_municipio.csv · 48020 · cuantia_alquiler_mes |
| `datos.mun_bilbao_esfuerzo` | 37,69 | mongo_esfuerzo_por_municipio.csv · 48020 |
| `datos.mun_bilbao_esfuerzo_2026` | 98,19 | comparacion_esfuerzo_2024_2026.csv · 48020 · esfuerzo 2026 base salario |
| `datos.mun_bilbao_n_2026` | 68 | comparacion_esfuerzo_2024_2026.csv · 48020 · n_anuncios_2026 |
| `datos.mun_bilbao_precio_2026` | 1.687,50 | comparacion_esfuerzo_2024_2026.csv · 48020 · precio mediano 2026 |
| `datos.mun_donostia_alquiler` | 995 | mongo_esfuerzo_por_municipio.csv · 20069 · cuantia_alquiler_mes |
| `datos.mun_donostia_esfuerzo` | 38,17 | mongo_esfuerzo_por_municipio.csv · 20069 |
| `datos.mun_donostia_esfuerzo_2026` | 116,37 | comparacion_esfuerzo_2024_2026.csv · 20069 · esfuerzo 2026 base salario |
| `datos.mun_donostia_n_2026` | 58 | comparacion_esfuerzo_2024_2026.csv · 20069 · n_anuncios_2026 |
| `datos.mun_donostia_precio_2026` | 2.000,00 | comparacion_esfuerzo_2024_2026.csv · 20069 · precio mediano 2026 |
| `datos.mun_erandio_alquiler` | 720 | mongo_esfuerzo_por_municipio.csv · 48902 · cuantia_alquiler_mes |
| `datos.mun_erandio_esfuerzo` | 37,65 | mongo_esfuerzo_por_municipio.csv · 48902 |
| `datos.mun_errenteria_alquiler` | 705 | mongo_esfuerzo_por_municipio.csv · 20067 · cuantia_alquiler_mes |
| `datos.mun_errenteria_esfuerzo` | 36,41 | mongo_esfuerzo_por_municipio.csv · 20067 |
| `datos.mun_getxo_esfuerzo` | 28,60 | mongo_esfuerzo_por_municipio.csv · 48044 |
| `datos.mun_getxo_esfuerzo_2026` | 78,55 | comparacion_esfuerzo_2024_2026.csv · 48044 · esfuerzo 2026 base salario |
| `datos.mun_getxo_n_2026` | 39 | comparacion_esfuerzo_2024_2026.csv · 48044 · n_anuncios_2026 |
| `datos.mun_getxo_precio_2026` | 1.350,00 | comparacion_esfuerzo_2024_2026.csv · 48044 · precio mediano 2026 |
| `datos.mun_irun_alquiler` | 729 | mongo_esfuerzo_por_municipio.csv · 20045 · cuantia_alquiler_mes |
| `datos.mun_irun_esfuerzo` | 35,44 | mongo_esfuerzo_por_municipio.csv · 20045 |
| `datos.mun_lasarte_oria_alquiler` | 766 | mongo_esfuerzo_por_municipio.csv · 20902 · cuantia_alquiler_mes |
| `datos.mun_lasarte_oria_esfuerzo` | 36,47 | mongo_esfuerzo_por_municipio.csv · 20902 |
| `datos.mun_lezo_alquiler` | 702 | mongo_esfuerzo_por_municipio.csv · 20053 · cuantia_alquiler_mes |
| `datos.mun_lezo_esfuerzo` | 35,62 | mongo_esfuerzo_por_municipio.csv · 20053 |
| `datos.mun_pasaia_alquiler` | 691 | mongo_esfuerzo_por_municipio.csv · 20064 · cuantia_alquiler_mes |
| `datos.mun_pasaia_esfuerzo` | 36,87 | mongo_esfuerzo_por_municipio.csv · 20064 |
| `datos.mun_portugalete_alquiler` | 702 | mongo_esfuerzo_por_municipio.csv · 48078 · cuantia_alquiler_mes |
| `datos.mun_portugalete_esfuerzo` | 35,65 | mongo_esfuerzo_por_municipio.csv · 48078 |
| `datos.mun_santurtzi_alquiler` | 697 | mongo_esfuerzo_por_municipio.csv · 48082 · cuantia_alquiler_mes |
| `datos.mun_santurtzi_esfuerzo` | 36,02 | mongo_esfuerzo_por_municipio.csv · 48082 |
| `datos.mun_sestao_alquiler` | 650 | mongo_esfuerzo_por_municipio.csv · 48084 · cuantia_alquiler_mes |
| `datos.mun_sestao_esfuerzo` | 38,10 | mongo_esfuerzo_por_municipio.csv · 48084 |
| `datos.mun_vitoria_esfuerzo` | 33,37 | mongo_esfuerzo_por_municipio.csv · 01059 |
| `datos.mun_vitoria_esfuerzo_2026` | 75,64 | comparacion_esfuerzo_2024_2026.csv · 01059 · esfuerzo 2026 base salario |
| `datos.mun_vitoria_n_2026` | 37 | comparacion_esfuerzo_2024_2026.csv · 01059 · n_anuncios_2026 |
| `datos.mun_vitoria_precio_2026` | 1.300,00 | comparacion_esfuerzo_2024_2026.csv · 01059 · precio mediano 2026 |
| `datos.municipios` | 252 | mongo_esfuerzo_por_municipio.csv · filas |
| `datos.municipios_2026` | 50 | comparacion_esfuerzo_2024_2026_resumen.csv · n_municipios |
| `datos.n_precio_positivo` | 7 | mongo_esfuerzo_por_municipio.csv · n_precio > 0 |
| `datos.precio_observable` | 60 | precio_medio_eur no nulo |
| `datos.precio_sin_muestra` | 53 | precio_medio_eur no nulo con n_precio = 0 (Tier C/D) |
| `datos.sesgo_superficie_anuncios` | 90,0 | cobertura_representatividad_2026.csv · superficie_mediana_anuncios |
| `datos.sesgo_superficie_oficial` | 80,7 | cobertura_representatividad_2026.csv · superficie_mediana_oficial_2024 |
| `datos.tier_a` | 4 | mongo_tier_confianza.csv · tier A |
| `datos.tier_ab` | 7 | mongo_tier_confianza.csv · A + B |
| `datos.tier_b` | 3 | mongo_tier_confianza.csv · tier B |
| `datos.tier_c` | 57 | mongo_tier_confianza.csv · tier C |
| `datos.tier_d` | 188 | mongo_tier_confianza.csv · tier D |
| `datos.vpo_promociones` | 406 | _facts.json · etxebide_promociones.docs |
| `datos.vpo_sin_dato` | 406 | etxebide_promociones · NumViviendas ausente o nulo |

## Gold

| Clave | Valor | Fuente |
|---|---:|---|
| `gold.anexo_png` | 8 | data/resultados/anexo/*.png |
| `gold.artefactos` | 54 | CSV + PNG de la raíz |
| `gold.csv` | 24 | data/resultados/*.csv |
| `gold.png` | 30 | data/resultados/*.png |

## Raw

| Clave | Valor | Fuente |
|---|---:|---|
| `raw.disco` | 357 | find data/raw -type f |
| `raw.manifest` | 355 | docs/raw_manifest_sha256.txt · líneas |
| `raw.visibles` | 355 | find data/raw -type f -not -name '.*' |

## Silver

| Clave | Valor | Fuente |
|---|---:|---|
| `silver.disco` | 187 | find data/procesado -type f |
| `silver.manifest` | 183 | data/procesado/manifest_sha256.txt · líneas |

## Infraestructura (manual)

| Clave | Valor | Fuente |
|---|---:|---|
| `infra.hdfs_bytes` | 895.597.901 | GETCONTENTSUMMARY /data/raw · 2026-11-13 |
| `infra.hdfs_objetos` | 353 | GETCONTENTSUMMARY /data/raw · 2026-11-13 |
| `infra.kafka_factor_replicacion` | 1 | KafkaAdminClient.describe_topics · 2026-11-13 |
| `infra.kafka_particiones` | 1 | KafkaAdminClient.describe_topics · 2026-11-13 |
| `infra.kafka_topic` | vivienda_euskadi | KafkaAdminClient.describe_topics · 2026-11-13 |

## Verificación (manual)

| Clave | Valor | Fuente |
|---|---:|---|
| `verif.deck_checks` | 41 | scripts/verificar_cifras_deck.py · 2026-11-13 |
| `verif.gobernanza_cabeceras` | 53 | scripts/verificar_gobernanza.py · 2026-11-13 |
| `verif.gobernanza_dag` | 40 | scripts/verificar_gobernanza.py · 2026-11-13 |
| `verif.gobernanza_ids` | 49 | scripts/verificar_gobernanza.py · 2026-11-13 |
| `verif.gobernanza_scripts` | 47 | scripts/verificar_gobernanza.py · 2026-11-13 |
| `verif.tests_collected` | 295 | pytest -q tests · 2026-11-14 |
| `verif.tests_passed` | 293 | pytest -q tests · 2026-11-14 |
| `verif.tests_skipped` | 2 | pytest -q tests · 2026-11-14 |
