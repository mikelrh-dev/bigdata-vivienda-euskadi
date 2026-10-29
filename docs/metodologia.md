# Metodología — fuente única de verdad

## Universo de análisis
- CAE (Euskadi): 1 nivel.
- Comarca: 20 comarcas oficiales.
- Municipio robusto: n≥30 anuncios combinados (Fotocasa + Pisos + RealtyAPI). Actualmente: 4 municipios (Bilbao, Donostia, Vitoria, Getxo).
- Municipios con dato oficial de alquiler: 159/252.
- Municipios sin dato oficial: 93/252 (imputados por comarca).

## Métricas canónicas
- Fotocasa anuncios: 471 (57 municipios).
- Pisos anuncios: 230 (37 ámbitos de búsqueda).
- RealtyAPI anuncios: 139 (3 municipios).
- Anuncios unificados: 871 (excluye 155 habitaciones de Fotocasa y 46 de Pisos).
- Pearson renta vs alquiler: r = 0.2094 (159 municipios con alquiler oficial).
- Tests: 59 passed.
- Municipios robustos (n≥30): 6 canónicos (7 claves por variante Donostia).

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
- 170 municipios sin anuncios (solo 4 robustos).
- Mezcla de años (2026 anuncios vs 2024 alquiler/renta).
- Emancipación juvenil solo a nivel CAE (no municipal).
- Pisos con geo inválida (235/235, `geo_invalida=True`).
- 13.45% duplicados en anuncios unificados (sin consumir fingerprint).
- VPO 93.6% ceros (no respondible C1 con datos actuales).

## Limitaciones
- Ranking municipal fino no defendible (solo 4 municipios robustos).
- Tasa de desempleo juvenil real no calculable (falta población activa joven municipal).
- Compraventa vs alquiler solo a nivel territorial/área funcional (7 municipios directos).
