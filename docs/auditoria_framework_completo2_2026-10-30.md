# Auditoría Framework Completo2 — Análisis Empírico

Repo: bigdata-vivienda-euskadi | Modo: solo lectura | Fecha: 2026-10-30

## 1. Métricas reales observadas

Fuentes principales (252 municipios canónicos: Bizkaia 113, Gipuzkoa 88, Araba 51):

| Fuente | Filas | Muns únicos | % sobre 252 | n>=30 | 5-29 | <5 | codigo_ine % | Sup válida |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| dim_municipios | 252 | 252 | 100% | - | - | - | 100% | - |
| fotocasa | 471 | 61 (60 Euskadi + Las Rozas Madrid) | 24% | 3 | 9 | 49 | 99.6% | 95.3% |
| pisos.com | 235 | 37 | 15% | 2 | 11 | 24 | 100% | 93.6% |
| realtyapi | 139 | 3 (capitales) | 1% | 3 | 0 | 0 | 100% | 99.3% |
| alquiler_municipal | 253 | 159 | 63% | - | - | - | 0% (sin campo) | - |
| eustat renta 2024 | - | 201 | 80% | - | - | - | sí (ámbito) | - |
| udalmap empleo | 252 | 252 | 100% | - | - | - | sí | - |

- distancias capitales: 259 filas con 2 duplicados (usar distancias_capitales_252: 252).
- distancias haversine: 63504 pares (252x252), 0 NaN.
- geojson Euskadi: 252 features, EPSG:4326.
- emancipación: parsea correctamente con delimiter ';' (866 filas, 14 indicadores).
- html_fotocasa: 99 archivos HTML crudos.
- pytest: 59 passed, 0 xfail, 0 skip.

Calidad estadística:
- pm2 outliers: fotocasa 15 (max 2200 por superficie 1 m2, y 83.33), pisos 9 (30-43.92), realtyapi 5.
- fotocasa temporal vs larga: 304 temporales mean 27.65 €/m2 vs 167 largas mean 16.08 €/m2 (diferencia 72%) -> no mezclar.
- combinado largos: 402 anuncios, 74 municipios; solo 4 con n>=30 (Bilbao, Getxo, Ayala/Aiara, Abanto y Ciérvana-Abanto Zierbena); 54 con <=4.
- correlación renta municipal vs alquiler: r=0.165 (n=139), débil.
- udalmap: actividad 40.63-60.09, ocupación 41.39-74.14, paro lanbide 0.0-12.57; tasa_paro_aprox_pct 100% NaN (columna rota).
- salarios INE: solo nacional (198 series), sin desglose municipal.
- distancias_municipios.json: 63504 pares completos (no 5k como decía auditoría previa).

## 2. Incumplimientos / riesgos

### P1 CRÍTICO
- fotocasa codigo_ine tiene 2 null (Las Rozas de Madrid): contaminación fuera de Euskadi, excluir.
- tasa_paro_aprox_pct 100% NaN -> no usable; usar tasa_paro_lanbide_pct o recalcular.
- alquiler_municipal sin codigo_ine ni n_contratos por distrito -> no se conoce muestra real.
- fotocasa pm2 max 2200 por superficie 1 m2 (error de parseo) y 83.33 (30 m2) -> limpiar antes de agregar.
- n muestral: solo 4 municipios con >=30 anuncios largos; 54 con <=4 -> no ranking municipal fino.

### P2 ALTO
- eustat renta cubre 201/252 (51 faltantes) -> tasa esfuerzo incompleta.
- alquiler oficial cubre 159/252 (93 faltantes).
- fotocasa temporal (62% de anuncios) infla media 72%; separar siempre.
- fotocasa tiene 5 nombres no canónicos (4 variantes + Las Rozas de Madrid); mapear antes de agregar.
- pisos.com no cubre capitales (0 listings en Bilbao/Donostia/Vitoria) -> sesgo.
- realtyapi solo 3 municipios (capitales) pero n 39-50 -> útil solo capitales.

### P3 MEDIO
- distancias_capitales.csv tiene 2 duplicados (usar _252).
- eustat incluye 75 ámbitos no municipio (CA, provincias, comarcas) -> filtrar códigos de 5 dígitos.
- superficie válida al 95% pero 5% fuera de rango o habitaciones null.
- correlación renta-alquiler débil r=0.165 -> documentar que renta local explica poco.
- html_fotocasa: 99 archivos (revisar si faltan 2 municipios).

## 3. Veredicto de suficiencia

- Ranking de 252 municipios por coste de acceso con error <20%: NO. Solo 4 municipios con n>=30 anuncios largos; alquiler oficial cubre 159/252 sin n por distrito. Viable a nivel comarcal/capitales.
- Tasa de esfuerzo alquiler/renta para 252: PARCIAL. Renta 201/252, alquiler 159/252. Para 93 municipios sin alquiler oficial no se puede calcular; usar comarca o imputación documentada.
- "Dónde hay trabajo y vivienda barata": PARCIAL. Empleo (lanbide) y distancias completas para 252, pero paro aproximado roto y salario solo nacional (usar renta como proxy).

## 4. Módulo A (extracción y codigo_ine)

- codigo_ine: fotocasa 99.6%, pisos 100%, realtyapi 100% (alquiler 0% por diseño).
- superficie/habitaciones: fotocasa 95.3%, pisos 93.6%, realtyapi 99.3%.
- HTML crudo fotocasa: 99 archivos (EXTRACCION-01 parcial; verificar municipios faltantes).
- GeoJSON: 252 features, EPSG:4326 (cumple).
- Haversine: 63504 pares, 0 NaN (cumple).
- pytest: 59 passed, 0 xfail, 0 skip (cumple).

## 5. Plan de corrección (esperar OK)

1. Filtrar fotocasa a codigo_ine válido y Euskadi; excluir Las Rozas de Madrid (2 filas).
2. Limpiar pm2 outliers (superficie <10 o >600 o precio/superficie extremo) antes de agregar.
3. Separar siempre temporal vs larga; no mezclar.
4. Mapear 4 variantes fotocasa a canónico via dim_municipios.
5. Usar tasa_paro_lanbide_pct en lugar de tasa_paro_aprox_pct (o recalcular aprox).
6. Agregar codigo_ine a alquiler_municipal en transform; añadir n_contratos si disponible.
7. Completar renta para 51 faltantes (INE Atlas) o documentar gap.
8. Usar distancias_capitales_252 (dedup) y distancias_municipios.json (completo) en análisis.

No se modificó código ni datos.
PY