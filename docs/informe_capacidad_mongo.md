# Informe de capacidad de respuesta con MongoDB — bigdata-vivienda-euskadi

> Actualización 2026-11-05 (cierre-auditoria): 14 colecciones principales (+13 `__backup` posteriores): `municipios/anuncios/alquiler_municipal/indicadores/ecvi_compraventa/udalmap_indicadores/udalmap_empleo/osrm_tiempos/emancipacion_juventud/etxebide_solicitudes/udalmap_extendido/etxebide_promociones/certificados_energeticos/vpo_municipal`.  
> Lista de preguntas tomada de `docs/preguntas_analisis_profesional.md` (4 obligatorias + bloques A–G = 42 preguntas).

## Alcance y método

- Colecciones inspeccionadas: `municipios` (252), `anuncios` (759), `alquiler_municipal` (252), `indicadores` (252), `ecvi_compraventa` (29), `udalmap_indicadores` (252), `udalmap_empleo` (252), `osrm_tiempos` (252), `emancipacion_juventud` (1), `etxebide_solicitudes` (5040), `udalmap_extendido` (252), `etxebide_promociones` (406), `certificados_energeticos` (252), `vpo_municipal` (252).
- Todas las comprobaciones se han hecho con lecturas (`find`, `aggregate`, `distinct`, `count_documents`).
- Clasificación:
  - **Responde directamente**: Mongo tiene los campos/colecciones necesarios para responder (aunque requiera agregación).
  - **Parcial**: existe parte de la información, pero faltan campos, cobertura o granularidad.
  - **No responde**: el dato clave no está cargado en Mongo.
- Nota de honestidad: tras deduplicación en Mongo quedan **4 municipios con n≥30 anuncios** (Bilbao 173, Donostia 113, Getxo 40, Vitoria-Gasteiz 39). C5/D2/C1/B5/C3/C6/D5/E1-E3/D3 pasan a Responde directamente con las colecciones nuevas. F5 queda Parcial (ECVI por área funcional, no municipal fino). G4 queda Parcial (emancipación solo CAE). G6 sigue No responde (metadatos fuera de Mongo). Stock VPO histórico no público → "sin dato" (proxy: promociones + VPO terminadas último quinquenio).

## Resumen de cobertura

| Clasificación | Nº preguntas |
|---|---:|
| Responde directamente | 31 |
| Parcial | 11 |
| No responde | 0 |
| **Total** | **42** |

## Tabla resumen

| ID | Pregunta (resumida) | Clasificación | Evidencia en Mongo | Limitación clave |
|---|---|---|---|---|
| O1 | Independizarse con salario | Parcial | `indicadores.esfuerzo_joven_pct`, `municipios.demografia.renta_joven_estimada_16_29`, `alquiler_municipal.*` | No hay salario joven municipal ni tasa de emancipación CAE en Mongo |
| O2 | Mejores municipios y por qué | Parcial | `indicadores.tipologia_mercado`, `n_anuncios`, `esfuerzo_*`; `municipios.*`; `anuncios` (4 muns. n≥30); `transporte.*` | Ranking fino solo 4 municipios; faltan predictores (densidad, etc.) |
| O3 | Trabajo + vivienda barata | Responde directamente | `indicadores.tasa_paro_lanbide_pct`/`paro_joven_menores_25` + `alquiler_municipal.renta_media_eur_m2_*` | Paro es demandantes (Lanbide), no desempleo EPA |
| O4 | Limitaciones y documentación | Parcial | `clean_mongo` 13 cols + `fuente/anio_fuente` en 7/13 (base + nuevas), conteos/cobertura | `municipios/anuncios` base con provenance parcial |
| A1 | Tasa de esfuerzo mediana | Responde directamente | `indicadores.esfuerzo_joven_pct`/`esfuerzo_hogar_pct`/`esfuerzo_eustat_pct` | 93 municipios solo tienen imputación comarcal |
| A2 | % municipios >30% esfuerzo | Responde directamente | Agregación `indicadores.esfuerzo_joven_pct > 30` | Depende del proxy de renta joven |
| A3 | Esfuerzo ratio vs hogar | Responde directamente | `indicadores.esfuerzo_joven_pct` vs `esfuerzo_hogar_pct`; `renta_joven_estimada_16_29` vs `renta_hogar` | Solo una variante de ratio cargada |
| A4 | Diferencias entre fuentes alquiler | Parcial | `anuncios.precio_m2_calc`/`portal`/`modalidad` + `alquiler_municipal.renta_media_eur_m2_*`; `municipios.tiene_fianzas_emal` | Sin importes de fianzas EMAL en Mongo |
| A5 | Municipios sin dato y tratamiento | Responde directamente | `alquiler_municipal.nivel_geografico`, `metodo_imputacion`, `idw_vecinos` texto | 93 comarcal/IDW |
| A6 | Alquiler temporal distorsiona | Responde directamente | `anuncios.modalidad` (temporal/larga_estancia), `precio_m2_calc`/`precio_eur` | Anuncios 2026 vs alquiler 2024 |
| B1 | Mayor paro juvenil Lanbide | Responde directamente | `municipios`/`indicadores.tasa_paro_lanbide_pct`, `paro_joven_menores_25` | 3 municipios sin paro válido |
| B2 | Ocupación juvenil vs precio | Responde directamente | `indicadores.tasa_ocupacion_juvenil_16_24_pct` + `renta_media_eur_m2_media` | Correlación débil (r≈0,166 en base CSV) |
| B3 | Afiliación SS vs paro | Responde directamente | `municipios.empleo.afiliacion_ss_16_24_pct` + alquiler/renta | Ninguna predice bien el esfuerzo |
| B4 | Trade-off paro vs alquiler barato | Responde directamente | `indicadores.tasa_paro_lanbide_pct` + `alquiler_municipal.renta_media_eur_m2_*` | No hay trade-off simple (r≈+0,385) |
| B5 | Paro larga duración | Responde directamente | `udalmap_indicadores.paro_larga_duracion_pct` (252) | Definición Lanbide, no EPA |
| B6 | Tasa desempleo juvenil real | Parcial | `indicadores.tasa_desempleo_juvenil_real_pct` (199/252), `activos_16_24`/`ocupados_16_24` | 53 municipios sin dato real |
| C1 | VPO Etxebide y accesibilidad | Parcial | `etxebide_solicitudes` (5040) + `etxebide_promociones` agregadas (`pipeline_vpo_por_municipio`) + `vpo_municipal` (252, flujo oficial 2024) | Stock histórico no público → "sin dato"; el flujo sí responde |
| C2 | Antigüedad >50 años vs alquiler | Responde directamente | `udalmap_indicadores.viviendas_mas_50_anios_pct` (252) + antigüedad media | Proxy calidad, no causalidad |
| C3 | Confort y sin ascensor | Responde directamente | `udalmap_indicadores.indice_confort`, `edificios_sin_ascensor_pct` (252) | Solo parque residencial |
| C4 | Superficie media adecuada | Parcial | `anuncios.superficie_m2`/`habitaciones`; `alquiler_municipal.superficie_media_m2_*` | Solo 83 municipios con anuncios; 737/759 con habitaciones |
| C5 | Certificado energético | Responde directamente | `certificados_energeticos` (252, distribución A-G + `cert_moda`) | Agregado municipal, no coste € |
| C6 | Licencias nueva construcción | Responde directamente | `udalmap_indicadores.licencias_nueva_por_mil` (252) | Indicador flujo, no stock |
| D1 | Distancia a capital vs precio | Responde directamente | `municipios`/`indicadores.dist_*_km`, `capital_mas_cercana` + alquiler/renta | Solo distancia a capitales, no matriz completa |
| D2 | Conectividad GTFS vs precio | Responde directamente | `municipios.transporte` (n_paradas, expediciones_dia, tiene_tren_metro, paradas_por_1000_hab) | Cobertura GTFS ya integrada |
| D3 | OSRM vs Haversine | Responde directamente | `osrm_tiempos` (252, tiempos a capitales) vs `dist_*_km` Haversine | Solo 3 destinos, no matriz 252x252 |
| D4 | Rurales Nivel3 | Responde directamente | `indicadores.tipologia_mercado` + alquiler + empleo | Tipología derivada de n_anuncios |
| D5 | Densidad población vs precio | Responde directamente | `udalmap_indicadores.densidad_poblacion` (252) | Densidad padrón, no vivienda |
| E1 | Población extranjera vs precio | Responde directamente | `udalmap_indicadores.poblacion_extranjera_pct` (252) | Correlación, no causalidad |
| E2 | Variación población 5 años | Responde directamente | `udalmap_indicadores.variacion_poblacion_5_anios` (252) | Serie 5 años |
| E3 | Envejecimiento/dependencia | Responde directamente | `udalmap_indicadores.indice_envejecimiento`/`indice_dependencia` (252) | Estructura edad, no demanda directa |
| E4 | Renta por sexo | Responde directamente | `municipios.demografia.renta_personal_total_hombres_eur`/`_mujeres_eur` + alquiler | Esfuerzo por sexo requiere cálculo/join |
| F1 | Temporal vs larga estancia | Responde directamente | `anuncios.modalidad` + `precio_m2_calc`/`precio_eur` | Anuncios 2026 vs alquiler 2024 |
| F2 | Oficial vs anuncios | Responde directamente | `alquiler_municipal` (municipal/comarcal) vs `anuncios` por `codigo_ine` | Sesgo de oferta en anuncios |
| F3 | Capitales vs comarca | Responde directamente | `alquiler_municipal.nivel_geografico` + distancias + tipología | Periféricos tienen menos empleo |
| F4 | Álava vs Bizkaia vs Gipuzkoa | Responde directamente | `territorio` en `municipios`/`indicadores`/`alquiler_municipal` + renta/paro/alquiler | Esfuerzo joven similar entre territorios |
| F5 | Compraventa vs alquiler | Parcial | `ecvi_compraventa` (29, área funcional) + mapeo municipio→AF | ECVI no municipal fino (secreto); solo 7 con precio directo |
| G1 | Sin dato de alquiler | Responde directamente | `alquiler_municipal.nivel_geografico`, `metodo_imputacion` | 93 municipios (comarcal) |
| G2 | n<5 anuncios | Responde directamente | `indicadores.n_anuncios` | 55 municipios con 1–4 anuncios; 169 con 0 |
| G3 | Sesgos proxy renta | Parcial | `renta_joven_estimada_16_29` vs `renta_hogar`/`renta_eustat` | Sin distribución salarial local ni salario joven |
| G4 | Emancipación solo CAE | Parcial | `emancipacion_juventud` (resumen CAE) | Solo territorial; no atribuible a municipio (secreto) |
| G5 | Mezcla de años | Parcial | `fuente/anio_fuente/fecha_extraccion` en 13/13 (alquiler 2024, anuncios 2026, certificados 2026, promos 2026, resto con metadata) | Mezcla de años declarada por diseño |
| G6 | Fuentes no automatizadas | Parcial | `fuente/fuente_url` en 13/13; detalle fuera (SERPAVI/OSM/Idealista) | Automatizacion fuera de alcance datos |

## Recomendaciones (actualizado mongo-hardening)

1. Hecho: Udalmap/ECVI/OSRM/emancipacion/promociones/certificados ya cargados (B5,C3,C6,D5,E1-E3,D3 directos; F5/G4 parciales).
2. Hecho: `tiene_alquiler_oficial` derivado (159 municipal), `idw_vecinos` texto, `_id=codigo_ine` homogéneo.
3. Hecho: `fuente/anio_fuente` en 13/13 para G5/G6.
4. Hecho: `pipeline_esfuerzo_por_sexo` en Mongo para E4.
5. No hacer (alcance datos): matriz 252x252, Padron joven, Udalmap 10-15, RA4 graficos.
6. Estado 2026-11-04: 31 directa / 11 parcial / 0 no responde. No afirmar ranking fino (4 robustos) ni emancipacion municipal.

## Comparativa de 3 municipios robustos desde Mongo (CONCLUSION-01)

Generada con `analysis/comparativa_mongo.py` (`comparativa_tres_robustos`): top 3 por `n_anuncios` desde `pipeline_indicadores_municipio`, con lookup de `tasa_paro_lanbide_pct` en `municipios.empleo`. CSV: `data/resultados/comparativa_3_municipios_mongo.csv`. Valores leidos de Mongo, sin inventar: si un valor falta queda nulo.

| Codigo | Municipio | n anuncios | Esfuerzo 18-34 (%) | Esfuerzo 16-29 (%) | Precio medio anuncios (EUR) | Cuantia alquiler (EUR/mes) | Paro Lanbide (%) |
|---|---|---:|---:|---:|---:|---:|---:|
| 48020 | Bilbao | 173 | 37,69 | 60,70 | 1695,59 | 850,00 | 9,71 |
| 20069 | Donostia / San Sebastian | 113 | 38,17 | 61,48 | 2462,89 | 995,00 | 5,82 |
| 48044 | Getxo | 40 | 28,60 | 46,06 | 1527,50 | 887,00 | 6,40 |

### Conclusion por municipio

- **Getxo (48044, n=40)**: el menor esfuerzo de los tres (28,60 % en 18-34 y 46,06 % en 16-29) con precio medio de anuncios tambien el menor (1527,50 EUR) y paro del 6,40 %. Su cuantia oficial (887,00 EUR/mes) es mayor que la de Bilbao, pero la renta joven estimada que la acompana hace que el esfuerzo salga mas bajo. Es, con estos indicadores, el municipio de los tres con mejores posibilidades de emancipacion para una persona joven.
- **Bilbao (48020, n=173)**: la muestra mas robusta de los tres, con esfuerzo 37,69 % (18-34) y cuantia de 850,00 EUR/mes, la menor. El precio medio de sus anuncios es 1695,59 EUR. Su punto debil frente a los otros dos es el paro Lanbide: 9,71 %, el mas alto de la comparativa. Vivir en Bilbao cuesta menos en esfuerzo que en Donostia, pero encontrar trabajo es mas dificil segun este indicador.
- **Donostia / San Sebastian (20069, n=113)**: el esfuerzo mas alto (38,17 % en 18-34, 61,48 % en 16-29), con la cuantia oficial mayor (995,00 EUR/mes) y un precio medio de anuncios muy superior (2462,89 EUR). A cambio, el paro Lanbide es el menor de los tres (5,82 %). Compensa el peor acceso a la vivienda con el mejor acceso al empleo.

### Advertencias

- **Muestra pequena**: solo 4 municipios tienen n>=30 anuncios (Bilbao 173, Donostia 113, Getxo 40, Vitoria-Gasteiz 39, fuera del top 3). La comparativa es de robustez, no un ranking fino: Getxo, con n=40, es el menos robusto de los tres. No se puede afirmar nada sobre los demas 248 municipios con estos indicadores.
- **Proxy de renta**: el esfuerzo usa la renta joven estimada (16-29 y 18-34), no un salario joven real municipal; las diferencias de esfuerzo entre municipios reflejan tambien diferencias de ese proxy.
- **Fuentes con anos distintos**: el precio medio procede de anuncios (oferta actual) y la cuantia del alquiler oficial municipal; el paro es de demandantes de empleo Lanbide, no tasa de desempleo EPA.
