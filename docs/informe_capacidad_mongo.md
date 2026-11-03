# Informe de capacidad de respuesta con MongoDB — bigdata-vivienda-euskadi

> Generado por inspección de solo lectura de las colecciones MongoDB `municipios`, `anuncios`, `alquiler_municipal` e `indicadores` (localhost:27017 / `vivienda_euskadi`), de `storage/load_mongo.py`, `storage/clean_mongo.py`, `analysis/mongo_queries.py` y `analysis/mongo_aggregations.py`.  
> Lista de preguntas tomada de `docs/preguntas_analisis_profesional.md` (4 obligatorias + bloques A–G = 42 preguntas).  
> No se han modificado datos ni colecciones.

## Alcance y método

- Colecciones inspeccionadas: `municipios` (252), `anuncios` (759), `alquiler_municipal` (252), `indicadores` (252).
- Todas las comprobaciones se han hecho con lecturas (`find`, `aggregate`, `distinct`, `count_documents`).
- Clasificación:
  - **Responde directamente**: Mongo tiene los campos/colecciones necesarios para responder (aunque requiera agregación).
  - **Parcial**: existe parte de la información, pero faltan campos, cobertura o granularidad.
  - **No responde**: el dato clave no está cargado en Mongo.
- Nota de honestidad: tras deduplicación en Mongo quedan **4 municipios con n≥30 anuncios** (Bilbao 173, Donostia 113, Getxo 40, Vitoria-Gasteiz 39), no 6 como figuraba en el informe basado en CSV. Mongo no contiene variables Udalmap extendidas (densidad, extranjería, envejecimiento, confort, licencias, etc.), ECVI, emancipación CAE ni metadatos de año/fuente.

## Resumen de cobertura

| Clasificación | Nº preguntas |
|---|---:|
| Responde directamente | 20 |
| Parcial | 10 |
| No responde | 12 |
| **Total** | **42** |

## Tabla resumen

| ID | Pregunta (resumida) | Clasificación | Evidencia en Mongo | Limitación clave |
|---|---|---|---|---|
| O1 | Independizarse con salario | Parcial | `indicadores.esfuerzo_joven_pct`, `municipios.demografia.renta_joven_estimada_16_29`, `alquiler_municipal.*` | No hay salario joven municipal ni tasa de emancipación CAE en Mongo |
| O2 | Mejores municipios y por qué | Parcial | `indicadores.tipologia_mercado`, `n_anuncios`, `esfuerzo_*`; `municipios.*`; `anuncios` (4 muns. n≥30); `transporte.*` | Ranking fino solo 4 municipios; faltan predictores (densidad, etc.) |
| O3 | Trabajo + vivienda barata | Responde directamente | `indicadores.tasa_paro_lanbide_pct`/`paro_joven_menores_25` + `alquiler_municipal.renta_media_eur_m2_*` | Paro es demandantes (Lanbide), no desempleo EPA |
| O4 | Limitaciones y documentación | Parcial | `clean_mongo` (nulls, dedup, tipos), conteos/cobertura | Fuentes/años se documentan fuera de Mongo |
| A1 | Tasa de esfuerzo mediana | Responde directamente | `indicadores.esfuerzo_joven_pct`/`esfuerzo_hogar_pct`/`esfuerzo_eustat_pct` | 93 municipios solo tienen imputación comarcal |
| A2 | % municipios >30% esfuerzo | Responde directamente | Agregación `indicadores.esfuerzo_joven_pct > 30` | Depende del proxy de renta joven |
| A3 | Esfuerzo ratio vs hogar | Responde directamente | `indicadores.esfuerzo_joven_pct` vs `esfuerzo_hogar_pct`; `renta_joven_estimada_16_29` vs `renta_hogar` | Solo una variante de ratio cargada |
| A4 | Diferencias entre fuentes alquiler | Parcial | `anuncios.precio_m2_calc`/`portal`/`modalidad` + `alquiler_municipal.renta_media_eur_m2_*`; `municipios.tiene_fianzas_emal` | Sin importes de fianzas EMAL en Mongo |
| A5 | Municipios sin dato y tratamiento | Responde directamente | `alquiler_municipal.nivel_geografico`, `metodo_imputacion` | `idw_vecinos` cargado como nulo (texto no convertido) |
| A6 | Alquiler temporal distorsiona | Responde directamente | `anuncios.modalidad` (temporal/larga_estancia), `precio_m2_calc`/`precio_eur` | Anuncios 2026 vs alquiler 2024 |
| B1 | Mayor paro juvenil Lanbide | Responde directamente | `municipios`/`indicadores.tasa_paro_lanbide_pct`, `paro_joven_menores_25` | 3 municipios sin paro válido |
| B2 | Ocupación juvenil vs precio | Responde directamente | `indicadores.tasa_ocupacion_juvenil_16_24_pct` + `renta_media_eur_m2_media` | Correlación débil (r≈0,166 en base CSV) |
| B3 | Afiliación SS vs paro | Responde directamente | `municipios.empleo.afiliacion_ss_16_24_pct` + alquiler/renta | Ninguna predice bien el esfuerzo |
| B4 | Trade-off paro vs alquiler barato | Responde directamente | `indicadores.tasa_paro_lanbide_pct` + `alquiler_municipal.renta_media_eur_m2_*` | No hay trade-off simple (r≈+0,385) |
| B5 | Paro larga duración | No responde | No existe `paro_larga_duracion_pct` en Mongo | Falta cargar Udalmap indicadores |
| B6 | Tasa desempleo juvenil real | Parcial | `indicadores.tasa_desempleo_juvenil_real_pct` (199/252), `activos_16_24`/`ocupados_16_24` | 53 municipios sin dato real |
| C1 | VPO Etxebide y accesibilidad | Parcial | `municipios.demanda_social.etxebide_solicitudes_por_mil_2024` | Sin VPO adjudicadas/terminadas ni stock |
| C2 | Antigüedad >50 años vs alquiler | Parcial | `municipios.vivienda_contexto.antiguedad_media_anyos` | Falta `viviendas_mas_50_anios_pct` |
| C3 | Confort y sin ascensor | No responde | No existen `indice_confort`, `edificios_sin_ascensor_pct` | Falta cargar Udalmap indicadores |
| C4 | Superficie media adecuada | Parcial | `anuncios.superficie_m2`/`habitaciones`; `alquiler_municipal.superficie_media_m2_*` | Solo 83 municipios con anuncios; 737/759 con habitaciones |
| C5 | Certificado energético | No responde | No hay certificado energético en Mongo | Anuncios sin campo; solo proxy Udalmap no cargado |
| C6 | Licencias nueva construcción | No responde | No existe `licencias_nueva_por_mil` | Falta cargar Udalmap indicadores |
| D1 | Distancia a capital vs precio | Responde directamente | `municipios`/`indicadores.dist_*_km`, `capital_mas_cercana` + alquiler/renta | Solo distancia a capitales, no matriz completa |
| D2 | Conectividad GTFS vs precio | Responde directamente | `municipios.transporte` (n_paradas, expediciones_dia, tiene_tren_metro, paradas_por_1000_hab) | Cobertura GTFS ya integrada |
| D3 | OSRM vs Haversine | No responde | Solo `dist_*_km`; sin tiempos OSRM ni matriz Haversine | No se cargaron distancias OSRM |
| D4 | Rurales Nivel3 | Responde directamente | `indicadores.tipologia_mercado` + alquiler + empleo | Tipología derivada de n_anuncios |
| D5 | Densidad población vs precio | No responde | No existe `densidad_poblacion` | Falta cargar Udalmap indicadores |
| E1 | Población extranjera vs precio | No responde | No existe `poblacion_extranjera_pct` | Falta cargar Udalmap indicadores |
| E2 | Variación población 5 años | No responde | No existe `variacion_poblacion_5_anios` | Falta cargar Udalmap indicadores |
| E3 | Envejecimiento/dependencia | No responde | No existen `indice_envejecimiento`/`indice_dependencia` | Falta cargar Udalmap indicadores |
| E4 | Renta por sexo | Responde directamente | `municipios.demografia.renta_personal_total_hombres_eur`/`_mujeres_eur` + alquiler | Esfuerzo por sexo requiere cálculo/join |
| F1 | Temporal vs larga estancia | Responde directamente | `anuncios.modalidad` + `precio_m2_calc`/`precio_eur` | Anuncios 2026 vs alquiler 2024 |
| F2 | Oficial vs anuncios | Responde directamente | `alquiler_municipal` (municipal/comarcal) vs `anuncios` por `codigo_ine` | Sesgo de oferta en anuncios |
| F3 | Capitales vs comarca | Responde directamente | `alquiler_municipal.nivel_geografico` + distancias + tipología | Periféricos tienen menos empleo |
| F4 | Álava vs Bizkaia vs Gipuzkoa | Responde directamente | `territorio` en `municipios`/`indicadores`/`alquiler_municipal` + renta/paro/alquiler | Esfuerzo joven similar entre territorios |
| F5 | Compraventa vs alquiler | No responde | No hay ECVI/compraventa en Mongo | Falta cargar ECVI y mapeo área funcional |
| G1 | Sin dato de alquiler | Responde directamente | `alquiler_municipal.nivel_geografico`, `metodo_imputacion` | 93 municipios (comarcal) |
| G2 | n<5 anuncios | Responde directamente | `indicadores.n_anuncios` | 55 municipios con 1–4 anuncios; 169 con 0 |
| G3 | Sesgos proxy renta | Parcial | `renta_joven_estimada_16_29` vs `renta_hogar`/`renta_eustat` | Sin distribución salarial local ni salario joven |
| G4 | Emancipación solo CAE | No responde | No hay colección de emancipación juvenil | Dato solo territorial, no municipal |
| G5 | Mezcla de años | Parcial | `fecha_carga` en colecciones | Sin año fuente en los documentos |
| G6 | Fuentes no automatizadas | No responde | Sin metadatos de fuentes/automatización | SERPAVI/OSM/Idealista documentados fuera |

## Recomendaciones

1. **Cargar variables Udalmap extendidas en Mongo** (`densidad_poblacion`, `poblacion_extranjera_pct`, `variacion_poblacion_5_anios`, `indice_envejecimiento`, `indice_dependencia`, `indice_confort`, `edificios_sin_ascensor_pct`, `viviendas_mas_50_anios_pct`, `licencias_nueva_por_mil`, `paro_larga_duracion_pct`) para pasar de "No responde" a "Responde directamente" en B5, C3, C6, D5, E1, E2, E3.
2. **Corregir `tiene_alquiler_oficial`**: en `dim_municipios_enriquecido.csv` aparece siempre `False` aunque 159 municipios tienen alquiler oficial; derivarlo de `alquiler_municipal.nivel_geografico='municipal'` o `metodo_imputacion='oficial'`.
3. **Corregir `idw_vecinos`**: es texto con vecinos y distancias, pero `load_mongo.py` usa `to_int`; almacenarlo como string o array estructurado.
4. **Cargar ECVI y emancipación CAE** como colecciones (`ecvi_compraventa`, `emancipacion_juventud`) y el mapeo `municipio_area_funcional_ecvi` para F5 y O1/G4.
5. **Cargar distancias OSRM y matriz Haversine** (tiempos a capitales) para D3; completar GTFS si se quiere análisis de conectividad más fino.
6. **Añadir metadatos de procedencia y año** (`fuente`, `anio_fuente`, `fecha_extraccion`) a todos los documentos para G5/G6.
7. **Homogeneizar `_id`**: `indicadores` y `alquiler_municipal` usan `ObjectId` y `codigo_ine` separado; usar `codigo_ine` como `_id` en todas para joins directos.
8. **Mantener transformaciones existentes** (`mark_nulls`, `resolve_duplicates`, `convert_types`, `pipeline_indicadores_municipio`) y documentar que la deduplicación reduce municipios robustos a 4 (n≥30).
9. **Calcular en Mongo los derivados por sexo** (`esfuerzo_alquiler_hombres_pct`, `esfuerzo_alquiler_mujeres_pct`) mediante agregación para E4.
10. **No afirmar cobertura inexistente**: las 12 preguntas clasificadas como "No responde" no deben responderse con los datos actualmente cargados en Mongo.
