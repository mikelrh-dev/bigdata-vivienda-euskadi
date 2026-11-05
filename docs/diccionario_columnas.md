# Diccionario de columnas canónicas

Qué columna manda cuando dos parecen medir lo mismo. Si hay discrepancia entre
un artefacto y esta tabla, manda esta tabla y se corrige el artefacto.

## Esfuerzo de alquiler

| Columna | Estado | Definición |
|---|---|---|
| `esfuerzo_joven_pct_18_34` | **canónica** | `cuantia_media_eur_mes_mediana × 12 / renta_joven_estimada_18_34 × 100` |
| `esfuerzo_joven_pct_16_29` | legacy | Mismo numerador con `renta_joven_estimada_16_29`; solo demo y compatibilidad |
| `esfuerzo_joven_pct` | legacy | Alias de 16-29; no usar en conclusiones nuevas |
| `esfuerzo_joven_pct_18_24` / `_25_34` | subgrupo | Ratios CAE aplicados a renta municipal; no son datos municipales |
| `esfuerzo_hogar_pct`, `esfuerzo_eustat_pct` | contraste | Renta de hogar y renta media CAE, no renta joven |

## Alquiler

| Columna | Estado | Definición |
|---|---|---|
| `cuantia_media_eur_mes_mediana` | **canónica** | Cuantía mensual mediana de Eustat (oficial o IDW) |
| `cuantia_media_eur_mes_media` | contraste | Media; no se usa como numerador del esfuerzo |
| `renta_media_eur_m2_mediana` | canónica m² | Renta €/m²/mes mediana |
| `metodo_imputacion` | trazabilidad | `oficial` o `IDW_5_vecinos` |
| `is_imputed` | trazabilidad | Derivado de `metodo_imputacion`; nunca oculta la imputación |

## Renta y empleo

| Columna | Estado | Definición |
|---|---|---|
| `renta_joven_estimada_18_34` | **canónica** | `renta_hogar × ratio_fiscal_18_34` (ratio CAE 2024, no municipal) |
| `renta_joven_estimada_16_29` | legacy | Ratio 16-29, solo comparabilidad histórica |
| `renta_hogar` | base | Renta media del hogar, fuente Eustat/Atlas |
| `tasa_paro_lanbide_pct` | canónica | Paro registrado Lanbide; `tasa_paro_aprox_pct` está invalidada |
| `tasa_paro_valida` | flag | `False` cuando el registro era un cero imposible |
| `tasa_desempleo_juvenil_real_pct` | parcial | Calculada con población 16-24 estimada; 199/252 |

## Tensión social

| Columna | Definición |
|---|---|
| `tension_demanda_social` | Media de percentiles (Etxebide por mil 2024 y esfuerzo canónico), 0-100 |
| `tension_categoria` | `baja` < 33, `media` < 66, `alta` ≥ 66 |
| `etxebide_solicitudes_por_mil` | Solicitudes Etxebide 2024 por mil habitantes |

Reparto vigente: **76 alta / 103 media / 73 baja**.

## VPO

| Columna | Estado | Definición |
|---|---|---|
| `vpo_terminadas_por_mil` | **canónica de flujo** | VPO terminadas 2020-2024 por mil habitantes (Udalmap 73), 251/252 (Usansolo sin dato) |
| `n_promociones` | contexto | Promociones Etxebide agregadas por municipio/estado/tipología |
| `viviendas` / `num_viviendas` | **sin dato** | `NumViviendas` vacío en 406/406 filas de origen; no se imputa |
| stock histórico de VPO | **sin dato** | No existe fuente pública municipal; no se infiere del flujo |

## Anuncios

| Columna | Definición |
|---|---|
| `precio_eur` | Precio mensual del anuncio |
| `precio_m2_calc` | `precio_eur / superficie_m2` calculado |
| `es_outlier_iqr` | Marcado, nunca borrado |
| `modalidad` | `larga_estancia` (491) o `temporal` (268); no se mezclan |
| `property_fingerprint` | Deduplicación cross-portal; 0 duplicados vigentes |
