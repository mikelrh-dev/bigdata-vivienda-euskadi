# Metodología — fuente única de verdad

## Universo de análisis
- CAE (Euskadi): 1 nivel.
- Comarca: 20 comarcas oficiales.
- Municipio robusto: n≥30 anuncios combinados (Fotocasa + Pisos + RealtyAPI). Actualmente: 6 municipios (Bilbao, Donostia-San Sebastián, Vitoria-Gasteiz, Getxo, Abanto y Ciérvana, Ayala).
- Municipios con dato oficial de alquiler: 159/252.
- Municipios sin dato oficial: 93/252 (imputados por comarca).

## Métricas canónicas
- Fotocasa anuncios: 471 (57 municipios).
- Pisos anuncios: 230 (37 ámbitos de búsqueda).
- RealtyAPI anuncios: 139 (3 municipios).
- Anuncios unificados: 840 (excluye 155 habitaciones de Fotocasa y 46 de Pisos).
- Pearson renta vs alquiler: r = 0.2094 (159 municipios con alquiler oficial).
- Tests: 57 passed.
- Municipios robustos (n≥30): 6.

## Fórmula canónica de esfuerzo
```
esfuerzo_joven_pct = alquiler_anual / renta_joven_estimada × 100
```
- `renta_joven_estimada` = proxy por ratio (Eustat RPF CAE por edad / Eustat RPF CAE total) × renta municipal 18+.
- Sesgo: asume distribución homogénea por municipio (falacia ecológica).

## Fuentes
- Eustat Renta Personal y Familiar (municipal, 18+).
- Eustat Población por edad (grupos 0-19, 20-64, ≥65).
- INE Atlas de la Vivienda (renta hogar, vivienda >50 años, sin ascensor, confort, densidad, extranjeros, variación población).
- Lanbide Paro Juvenil (252 municipios).
- Udalmap Empleo (252 municipios, 47 indicadores).
- Fotocasa scraping (471 anuncios, 57 municipios).
- Pisos.com scraping (230 anuncios, 37 ámbitos).
- RealtyAPI (139 anuncios, 3 municipios).
- ECVI Compraventa (29 registros: 4 TH + 15 áreas funcionales + 7 municipios >40k).
- GTFS (13 operadores, 252 municipios enriquecidos).

## Vintage
- Anuncios: 2026 (Fotocasa, Pisos, RealtyAPI).
- Alquiler oficial: 2024 (Eustat).
- Renta: 2024 (Eustat).
- Población: 2025 (Eustat).
- Paro Lanbide: 2026.
- Udalmap: 2024.

## Sesgos documentados
- Proxy de renta joven (no salario real).
- 93 municipios con alquiler comarcal (no municipal).
- 170 municipios sin anuncios (solo 6 robustos).
- Mezcla de años (2026 anuncios vs 2024 alquiler/renta).
- Emancipación juvenil solo a nivel CAE (no municipal).
- Pisos con geo inválida (235/235, `geo_invalida=True`).
- 13.45% duplicados en anuncios unificados (sin consumir fingerprint).
- VPO 93.6% ceros (no respondible C1 con datos actuales).

## Limitaciones
- Ranking municipal fino no defendible (solo 6 municipios robustos).
- Tasa de desempleo juvenil real no calculable (falta población activa joven municipal).
- Compraventa vs alquiler solo a nivel territorial/área funcional (7 municipios directos).

## Estimación de población joven (15-29)

- Fuente: Eustat población por grandes grupos de edad (0-19, 20-64, ≥65) a nivel municipal (2025).
- Eustat no publica el grupo 15-29 a nivel municipal; se estima de forma transparente:
  - `poblacion_15_19_est = 0.25 × (0-19)` (5 de 20 años).
  - `poblacion_20_29_est = (10/45) × (20-64)` (10 de 45 años).
  - `poblacion_15_29_est = poblacion_15_19_est + poblacion_20_29_est`.
- Resultado en `data/procesado/poblacion_joven_municipal.csv` (252 municipios) con columna `metodo`.
- Sesgo: asume distribución uniforme dentro de cada grupo de edad (falacia ecológica); usar como aproximación, no dato real.

## Mapeo ECVI (área funcional)

- Correspondencia municipio → área funcional derivada de GeoEuskadi (`data/raw/areas_funcionales_municipios.csv`, 252 municipios) mediante centroide point-in-polygon.
- ECVI compraventa se publica por territorio, área funcional y 7 municipios >40k hab.; no es municipal.
- Cruce en `data/procesado/municipio_area_funcional_ecvi.csv` (252 municipios × área funcional × trimestre × precio medio total/m² libre/usada).
- Limitación: el precio ECVI asignado a un municipio es el de su área funcional, no un dato municipal directo.

## Estándar OVJ + Housing Wage (aditivo)
- Solución 1 (OVJ): salario neto real joven = 1.381 €/mes (18-29) y 1.564 €/mes (18-34), certificado por el Observatorio Vasco de la Juventud (2024).
- Solución 2 (Housing Wage): salario neto necesario para no superar el 30% de esfuerzo = alquiler_medio_mes / 0,30.
- Motivo: el salario joven municipal no existe por secreto estadístico (Ley 4/1986). No se inventa salario municipal.
- Campos añadidos: `salario_ovj_neto_mes`, `housing_wage_mes`, `esfuerzo_ovj_individual_pct`, `esfuerzo_ovj_pareja_pct`, `brecha_emancipacion_eur`.
- Referencia: `transform/calcular_renta_joven.py`.
