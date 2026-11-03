# Re-audit: framework_auditoria_completo2 vs estado actual (2026-10-29)

Modo solo lectura. Comparación de claims del framework (stats_audit.md, entity_audit.md, diagnostico.py, 03 framework) con archivos actuales.

## Métricas reales actuales

| Fuente | Filas | Municipios | Notas |
|---|---:|---:|---|
| anuncios_unificados (fotocasa 469 + pisos 261 + realty 139) | 869 | 84 (código_ine) | valid pm2 821 / 81 mun |
| anuncios_fotocasa.csv (raw) | 471 | 61 | temporal 304, larga 167 |
| anuncios_pisos.csv (raw) | 235 | 37 | superficie notnull 229/235, hab 227/235 |
| anuncios_realtyapi.csv (raw) | 139 | 3 | — |
| alquiler_municipal.csv (distritos) | 253 | 159 | sin cambio |
| alquiler_municipal_completo.csv | 252 | 252 | oficial 159 + IDW_5_vecinos 93 |
| eustat_renta_municipal (zfill 5) | — | 252/252 | antes reportado 201 por no zfill |
| serpavi_renta_municipal | 249 | 249 | — |
| renta_municipal_completa | 252 | 252 | — |
| udalmap_empleo (original) | 252 | 252 | tasa_paro_aprox ahora null (deprecated) |
| udalmap_empleo_corregido | 252 | 252 | tasa_paro_lanbide 0–12.57, 0 nulls |
| dim_municipios_enriquecido | 252×65 | 252 | tasa_desempleo_juvenil_real 199/252 (53 null) |
| transporte_paradas_municipio (raw) | 252 | 252 | n_paradas 0–857 |
| transporte_paradas_municipio_enriquecido | 252 | 252 | paradas_por_1000_hab 0–70.06, 0 nulls |
| distancias_capitales (original) | 259 | 257 (dup) | — |
| distancias_capitales_252 | 252 | 252 | deduplicado |
| distancias_haversine_252 | 63504 | 252×252 | matriz completa, 0 NaN |
| distancias_municipios.json | 63504 | 252×252 | reemplaza legacy 5.000 pares |
| municipios_euskadi.geojson | 252 features | 252 | EPSG:4326 |
| html_fotocasa | 101 archivos | — | EXTRACCION-01 cumplido |
| tests | 59 passed | 0 fail/skip | — |

## Discrepancias vs claims del framework

1. **Anuncios totales/robustos**: framework decía 662 válidos, 68 municipios, ≥30 en 3 (Bilbao, Donostia, Getxo). Ahora: 821 válidos, 81 municipios, ≥30 en **4** (Bilbao 238, Donostia 129, Vitoria 48, Getxo 40). Fotocasa 461 válidos/59 mun (antes 469/54); pisos 207/36 (antes 193/29); realty 139/3.

2. **Temporal vs larga estancia (Fotocasa)**: framework citaba 289/469 temporal y medias 18.91 (global) / 16.12 (larga). Actual: 304/471 temporal, media temporal **27.65** €/m² (n=298) vs larga **16.08** (n=163). La brecha es mayor que la documentada (16%); no mezclar.

3. **Superficie/habitaciones (Pisos.com)**: framework (diagnostico.py) decía 0% superficie. Actual: 229/235 (97.4%) superficie, 227/235 (96.6%) habitaciones. Incumplimiento resuelto (scraping enriquecido).

4. **Entity resolution / codigo_ine**: framework entity_audit decía alquiler/fotocasa/pisos/realty sin codigo_ine. Actual: los 4 CSV raw ya incluyen codigo_ine y nombre_canonico. Unificado: 869 filas, 0 nulls codigo_ine, 84 municipios.

5. **Renta (Eustat)**: framework stats_audit decía 201/252 (80%). Causa: códigos sin zfill (Álava 4 dígitos). Actual tras zfill: **252/252**. Correlación renta vs alquiler oficial: r=0.275 (antes 0.17). Mejora leve, sigue débil.

6. **Paro**: framework reportaba tasa_paro_aprox media −10.10% (negativa, fórmula mal derivada). Actual: columna `tasa_paro_aprox_pct` está vacía (deprecated); se usa `tasa_paro_lanbide_pct` (0–12.57, 0 nulls) y `tasa_desempleo_juvenil_real_pct` (199/252, 0–20.64). El claim de paro negativo ya no aplica.

7. **Distancias**: framework decía distancias_municipios.json = 5.000 pares (2.7%) y no permite "municipio barato a <30km". Actual: matriz completa **63.504 pares** (252×252), 0 NaN. distancias_capitales: 252 filas deduplicadas (antes 259 con 2 duplicados). OSRM: 252 con minutos a capitales.

8. **GTFS**: framework no cuantificaba; estado actual: 252/252 municipios, n_paradas 0–857, paradas_por_1000_hab 0–70.06, **0 nulls** (densidad corregida; antes nulls). operadores null en 51 (cosmético).

9. **GeoJSON**: framework pedía 251 mun en EPSG:4326. Actual: 252 features, EPSG:4326, filtrado a dim_municipios.

10. **Outliers €/m²**: framework 9 pisos + 13 fotocasa. Actual: pisos 9 (upper 29.26), fotocasa 15 (upper 36.45), realty 5 (upper 35.73). Superficie outlier 6.973 m² flagged (es_outlier_superficie True en 5 filas).

11. **Emancipación**: framework advertía parsing corrupto con ';'. Actual: CSV parsea con sep=';' quotechar='"' → 866 filas, 9 cols. (Sin verificación de 14 indicadores; no se revalidó.)

12. **HTML crudo Fotocasa**: framework diagnostico.py decía no se guarda. Actual: 101 HTML en data/raw/html_fotocasa/. Cumple EXTRACCION-01.

13. **09_realtyapi literal 'PY'**: framework decía NameError. Actual: no presente (corregido).

14. **04_b5m truncación 5.000**: framework decía truncado. Actual: distancias_municipios.json ya es matriz haversine completa (nota explícita "Reemplaza legacy b5m truncado"). El script 04 sigue siendo solo Gipuzkoa, pero la matriz final se genera con transform/generar_distancias.py.

15. **EQUIVALENCIAS_EXTRA dead code**: framework readiness lo marcaba. Actual: eliminado (solo comentario en extract/entity_resolution.py).

## Veredicto de suficiencia (actualizado)

- Renta: 252/252 (resuelto vía zfill) → tasa de esfuerzo calculable para todos los municipios.
- Paro: válido (Lanbide + desempleo juvenil real) → municipio-level OK.
- Distancias: completas → "municipio barato a <X km" respondible.
- Anuncios: solo **4 municipios** con n≥30 → ranking municipal fino sigue NO; comarcal/capitales OK. Temporal y larga estancia deben separarse (brecha 27.65 vs 16.08).
- Tests: 59 passed, 0 xfail/skip.
- Código: incumplimientos principales (HTML raw, superficie, PY, truncación, dead code) resueltos; deuda menor: outlier superficie 6.973 (flagged), operadores GTFS 51 nulls.

Conclusión: el framework queda parcialmente desactualizado; los cuellos de botella P1 (renta 201, paro negativo, distancias 5k, superficie 0%) han sido resueltos. El cuello de botella remanente es cobertura muestral de anuncios (4 robustos).
PY