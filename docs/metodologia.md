# Metodología — fuente única de verdad

## Universo de análisis
- CAE (Euskadi): 1 nivel.
- Comarca: 20 comarcas oficiales.
- Municipio robusto: n≥30 anuncios combinados (Fotocasa + Pisos + RealtyAPI). Actualmente: 4 municipios (Bilbao 204, Donostia 126, Getxo 50, Vitoria-Gasteiz 39).
- Municipios con dato oficial de alquiler: 159/252.
- Municipios sin dato oficial: 93/252 (imputados por IDW_5_vecinos, no comarcal).

## Métricas canónicas
- Fotocasa anuncios: 471 (57 municipios).
- Pisos anuncios: 87 en silver tras re-resolucion por subtitulo/titulo (261 ids unicos raw → 87 + 45 cuarentena + 129 fingerprint); 230 en enriquecido_geo.
- RealtyAPI anuncios: 139 (3 municipios).
- Anuncios unificados: 594 (excluye 155 habitaciones de Fotocasa y 46 de Pisos; cuarentena pisos 45 fuera de Euskadi en `cuarentena_pisos.csv`).
- Pearson renta vs alquiler: r = 0.2094 (159 municipios con alquiler oficial).
- Tests: 235 passed, 2 skipped (237 colectados; `pytest tests -q`; Tier A/B/C/D en `tests/test_tier_confianza.py`).
- Municipios robustos Tier A (n≥30): 4 canónicos (Bilbao 204, Donostia 126, Getxo 50, Vitoria-Gasteiz 39) — fuerte. Tier B indicativo 10-29 = 3 (Sopela 19, Zarautz 15, Santurtzi 11, temporal!=larga); Tier C sin precio municipal 1-9 = 57; Tier D sin dato 0 = 188. Nivel (tipología 4/54/194) es ortogonal a Tier (confianza 4/3/57/188): Nivel mide estructura del mercado; Tier mide cuánta muestra sustenta la conclusión para ese municipio; son ejes ortogonales, no intercambiables. Tier derivado de n_anuncios real en Mongo (`pipeline_tier_por_municipio`, `mongo_tier_confianza.csv`, 252 filas).
- Bootstrap robusto (`data/resultados/bootstrap_robustos.csv`): usa `n_larga_solo_vivienda` 67/60/39/37 (Bilbao/Donostia/Getxo/Vitoria-Gasteiz), distinto del `n_anuncios` Tier 204/126/50/39; los dos `n` no se intercambian en textos ni gráficos. IC95 Bilbao 33.75–40.95 y Getxo 27.54–31.77 (10.000 remuestreos); Bilbao y Donostia se solapan, sin orden firme.
- Salario joven ajustado (mediana): 1.402 € (base 1.381 €; ajuste por riesgo local ±15 %).
- Tensión social (Etxebide): 76 municipios alta / 103 media / 73 baja.

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
- 169 municipios sin anuncios residenciales (solo 4 robustos).
- Mezcla de años (2026 anuncios vs 2024 alquiler/renta).
- Emancipación juvenil solo a nivel CAE (no municipal).
- Pisos con geo inválida (235/235, `geo_invalida=True`).
- 251 duplicados/retirados en anuncios unificados (845 crudos → 594; 29,70 %; cadena histórica 845→759→594; 0 duplicados de fingerprint).
- VPO: 406 promociones Etxebide en 77 municipios con `NumViviendas` vacío (stock no público). El flujo oficial municipal (indicador 73) ya está integrado: 251/252 municipios con VPO terminada 2024 (Usansolo sin dato), en ‰ habitantes y carácter quinquenal.

## Limitaciones
- Ranking municipal fino no defendible (solo 4 municipios robustos).
- Tasa de desempleo juvenil real no calculable (falta población activa joven municipal).
- Compraventa vs alquiler solo a nivel territorial/área funcional (7 municipios directos).

## Decisiones congeladas

- No ranking municipal fino: solo Tier A sustenta ranking (Bilbao, Donostia, Getxo, Vitoria-Gasteiz); Tier B/C/D sin ranking. + tipología (Nivel1/Nivel2/Nivel3). Evita ataque en defensa por F5/B6.
