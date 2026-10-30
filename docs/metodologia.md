# Metodología — fuente única de verdad

## Universo de análisis
- CAE (Euskadi): 1 nivel.
- Comarca: 20 comarcas oficiales.
- Municipio robusto: n≥30 anuncios combinados (Fotocasa + Pisos + RealtyAPI). Actualmente: 6 municipios (Bilbao 239, Donostia 130, Vitoria 48, Getxo 40, Abanto 31, Ayala 30).
- Municipios con dato oficial de alquiler: 159/252.
- Municipios sin dato oficial: 93/252 (imputados por IDW_5_vecinos, no comarcal).

## Métricas canónicas
- Fotocasa anuncios: 471 (57 municipios).
- Pisos anuncios: 230 (37 ámbitos de búsqueda).
- RealtyAPI anuncios: 139 (3 municipios).
- Anuncios unificados: 873 (excluye 155 habitaciones de Fotocasa y 46 de Pisos).
- Pearson renta vs alquiler: r = 0.2094 (159 municipios con alquiler oficial).
- Tests: 59 passed.
- Municipios robustos (n≥30): 6 canónicos (7 claves por variante Donostia).
- Salario joven ajustado (mediana): 1.402 € (base 1.381 €; ajuste por riesgo local ±15 %).
- Tensión social (Etxebide): 73 municipios alta / 102 media / 77 baja.

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
- 93 municipios con alquiler imputado por IDW_5_vecinos (no comarcal).
- 170 municipios sin anuncios (solo 6 robustos).
- Mezcla de años (2026 anuncios vs 2024 alquiler/renta).
- Emancipación juvenil solo a nivel CAE (no municipal).
- Pisos con geo inválida (235/235, `geo_invalida=True`).
- 13,06% duplicados en anuncios unificados (114 filas extra en 93 grupos; sin consumir fingerprint).
- VPO 83.73% ceros (no respondible C1 con datos actuales).

## Limitaciones
- Ranking municipal fino no defendible (solo 6 municipios robustos).
- Tasa de desempleo juvenil real no calculable (falta población activa joven municipal).
- Compraventa vs alquiler solo a nivel territorial/área funcional (7 municipios directos).

## Decisiones congeladas

- No ranking municipal fino: solo 6 municipios robustos (Bilbao, Donostia, Vitoria, Getxo, Abanto, Ayala) + tipología (Nivel1/Nivel2/Nivel3). Evita ataque en defensa por F5/B6.
