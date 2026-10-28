# Re-auditoría 2026-10-28 — bigdata-vivienda-euskadi

Basada en framework_auditoria_completo2 (03 dato puro + módulo A) tras la recopilación de datos del 27-10. Solo lectura; no se modificaron datos.

## 1. Métricas reales observadas (verdad = dim_municipios.csv, 252 mun)

| Fuente | Brutos | Válidos | Mun. únicos | % sobre 252 | n>=30 | n 5-29 | n<5 (incl. 0) | codigo_ine % | Outliers altos |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| alquiler_municipal.csv | 253 filas (distritos) | 253 | 159 | 63.1 | — | — | — | 100.0 | sin n muestral |
| anuncios_fotocasa.csv | 470 | 456 | 57 | 22.6 | 3 | 9 | 240 | 100.0 | 12 |
| anuncios_pisos.csv | 218 | 192 | 29 | 11.5 | 0 | 11 | 241 | 100.0 | 9 |
| anuncios_realtyapi.csv | 139 | 139 | 3 | 1.2 | 3 | 0 | 249 | 100.0 | 5 |
| Anuncios combinados | 827 | 787 | 71 | 28.2 | 4 | 22 | 226 | 100.0 | — |
| udalmap_empleo.csv | 252 | 252 | 252 | 100.0 | — | — | — | 100.0 | paro 0 |
| distancias_capitales.csv (raw) | 259 | 252 (dedup) | 252 | 100.0 | — | — | — | 100.0 (2 dup) | — |
| distancias_capitales_252.csv | 252 | 252 | 252 | 100.0 | — | — | — | 100.0 | — |
| distancias_municipios.json | 5.000 pares | 2.77% de 180.488 | — | — | — | — | — | — | haversine_252 = 63.504 |
| ine_atlas_renta.csv | 252 | 252 | 252 | 100.0 | — | — | — | 100.0 | — |
| eustat_renta_municipal.csv | 98.532 | 252 (mun) | 252 | 100.0 | — | — | — | — | 24 agregados |
| emancipacion_juventud.csv | 866 filas | 14 indicadores | — | — | — | — | — | — | parsea OK |

- Alquiler oficial: 253 filas = 159 mun, 1-9 distritos/mun (media 1.59). Sin columna n muestral. 93 mun sin alquiler oficial.
- Anuncios: solo 4 mun con n>=30 combinado (Bilbao 240, Donostia 126, Vitoria 48, Getxo 40). 181 mun con 0 anuncios.
- Superficie válida (15-300 m² + habitaciones no nulo): Fotocasa 94.3%, Pisos 85.3%, RealtyAPI 99.3%.
- Temporal vs larga estancia (Fotocasa): 20.20 vs 16.28 €/m² (temporal ~24% más caro) -> no mezclar.
- Outliers €/m² (IQR): Fotocasa 12, Pisos 9, RealtyAPI 5.
- Paro: tasa_paro_aprox_pct 252/252 NaN (invalidada); tasa_paro_lanbide_pct válida 0-12.57, media 5.91, 0 negativos.
- Renta vs alquiler: r=0.280 (Eustat), r=0.263 (INE Atlas), n=159 -> débil (<0.3).
- HTML crudos Fotocasa: 17 archivos.
- pytest: 18 passed, 0 xfail, 0 skip.

## 2. Entity resolution

- codigo_ine 100% en alquiler_municipal, fotocasa, pisos y realtyapi (0 filas perdidas por join).
- Variantes Fotocasa mapeadas por código (Arrankudiaga / Zollo, Donostia - San Sebastián, Arrasate / Mondragón, Vitoria - Gasteiz).
- RealtyAPI: Donostia-San Sebastián -> canónico (solo Bilbao, Donostia, Vitoria).
- Eustat: 276 ámbitos = 252 mun + 24 agregados (CA, 3 provincias, 20 comarcas) -> filtrar.
- Distancias capitales raw: 259 filas con 2 códigos duplicados (Aramaio 01003, Otxandio 48072) -> deduplicar a 252.
- P1 (subagente 2): 51 mun de Araba con codigo_ine de 4 dígitos en distancias_capitales_252 -> solo 201/252 coinciden.
- P2: anuncios_pisos.csv tiene nombre_canonico vacío en 218/218 (JSON sí lo tiene).
- EPSG: shapefile fuente EPSG:25830; GeoJSON convertido declarado EPSG:4326 (coords en rango WGS84, sin prueba explícita del método).

## 3. Gaps y sesgos

P1 Crítico
- Alquiler oficial solo 159/252 (63.1%); 93 mun sin dato; sin n muestral por distrito.
- Anuncios: cobertura municipal baja (71/252, 28.2%); solo 4 mun con n>=30.
- tasa_paro_aprox_pct 100% NaN (usar Lanbide).
- 51 mun de Araba con codigo_ine de 4 dígitos en distancias -> rompe join.
- Outliers de €/m² sin depurar (superficies pequeñas/mal parseadas).

P2 Alto
- Temporal vs larga diferencia ~24% -> no mezclar.
- Renta vs alquiler r≈0.28 (<0.3) -> documentar.
- distancias_municipios.json solo 5.000/180.488 pares (2.77%).
- Mezcla de años (anuncios 2026 vs resto 2024) sin año_fuente en todos.
- Inconsistencia de flags temporal en Fotocasa (304 vs 316, 3 NaN).
- anuncios_pisos.csv nombre_canonico vacío en 218/218.
- HTML crudos no versionados (data/raw ignorado por git).

P3 Medio
- Superficie válida <100% (Pisos 85.3%).
- distancias_capitales.csv raw 259 filas (7 fuera de dim).
- Eustat 24 agregados a filtrar (si no, n=252 falso).
- EPSG: origen 25830 -> 4326 declarado sin prueba explícita.
- Araba solo 1 HTML frente a 12 Bizkaia / 4 Gipuzkoa.

## 4. Veredicto de suficiencia

- Ranking municipal fino de 252: NO (solo 4 mun con n>=30; alquiler 159/252 sin n).
- Análisis comarcal/capitales y 4 municipios robustos: SÍ.
- Tasa de esfuerzo alquiler/renta: PARCIAL (renta 252/252, alquiler 159/252).
- "Dónde hay trabajo y vivienda barata": PARCIAL (paro válido vía Lanbide y distancias completas vía haversine, pero cobertura de alquiler/anuncios limitada).

## 5. Plan de recopilación propuesto (sin proxies, sin infraestructura)

R1 — Ampliar anuncios (Fotocasa + Pisos.com) a municipios objetivo (~40-50): capitales + comarcas principales + los 93 sin alquiler oficial. Hasta n>=30. Separar temporal/larga. Guardar HTML crudo + SHA256.
R2 — Alquiler para los 93 sin dato oficial: scraping de portales hasta n>=10, dataset separado etiquetado como portal (no oficial).
R3 — Completar superficie/habitaciones en Pisos.com (detalle o descarte, sin imputar).
R4 — (Opcional) Idealista API si se aprueba.
R5 — Validación y documentación de gaps.

Municipios sin dato tras R1-R4 se marcan "sin dato" (no proxy).

## 6. Infraestructura y roadmap (fuera de alcance de esta fase)

- Fase 0 extracción + contrato + tests: HECHA (18 tests OK).
- Fase 1 salarios: HECHA (doc desactualizada).
- Fases 2-4,6-9 (HDFS, Mongo, Kafka, análisis, viz, informe): PENDIENTES.
- Fase 5 transformación: PARCIAL.
- Bloqueadores: Docker daemon detenido, VM Kafka inaccesible, falta de storage/analysis/visualization/notebooks/docker-compose. Mongo nativo disponible.

## 7. Baseline para comparar mejoras

Guardar esta auditoría como baseline. Tras cada fase de recopilación, re-ejecutar las métricas de la sección 1 y comparar (cobertura, n>=30, superficie válida, outliers, gaps). Cualquier mejora o empeoramiento debe quedar documentado en un nuevo informe en openspec/audit/.
