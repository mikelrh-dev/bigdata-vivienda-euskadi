# Reauditoría dato puro v2 — 2026-10-28 (framework 03)

## FASE 0 — Inventario real

| Fuente | Válidos | Municipios | %/252 | n>=30 | n 5-29 | n<5 |
|---|---|---|---|---|---|---|
| dim_municipios | 252 | 252 | 100% | — | — | Tipología N1:6 N2:63 N3:183 |
| alquiler_municipal (253 filas distrito) | 253 | 159 | 63% | 0 dist>=30 | 10 | 149 |
| fotocasa total | 471 | 61 | 24% | 3 | 9 | 49 |
| fotocasa_larga | 167 | 46 | 18% | 2 (Bilbao 42, Getxo 31) | 4 | 40 |
| fotocasa_temporal | 304 | 38 | 15% | 2 (Bilbao 147, Donostia 62) | 5 | 31 |
| pisos_busqueda | 230 | 37 ámbitos | 15% | 2 (búsqueda, no geoloc) | 11 | 24 |
| realtyapi | 139 | 3 | 1% | 3/3 | 0 | 0 |
| emal_ampliado | 730 | 73 | 29% | 0 | 73 (10 años c/u) | 0 |
| renta_completa | 252 | 252 | 100% | — | — | origen Eustat+INE_Atlas 252 |
| udalmap_corregido + lanbide | 252 | 252 | 100% | — | — | paro 0-12.57, 0 neg |
| transporte / osrm / haversine | 252/252/63504 | 252 | 100% | — | — | — |
| educación / salud | 1309/528 | 197/231 | 78%/92% | — | — | ausencia esperada |
| emancipación `;` | 866 | — | — | — | — | 9 cols |

## FASE 1 — Entity resolution

- dim 252/252 len5, prefs 01:51/20:88/48:113, 0 bad_pref. Blindaje `leer_csv_seguro` OK.
- alquiler 253/253 len5, 0 bad_pref.
- fotocasa total 469/471 len5 + 2 sin código (bad_pref 2). larga 167/167 OK. temporal 302/304 + 2 sin código. P1 menor: 2 anuncios sin `codigo_ine`.
- pisos_busqueda 230/230 len5, realty 139/139, emal 730/730, renta 252/252. 0 bad_pref.
- Variantes mapeadas: `Arrankudiaga / Zollo`, `Arrasate / Mondragón`, `Donostia - San Sebastián`, `Vitoria - Gasteiz`. Realty `Donostia-San Sebastián` normaliza.
- Eustat crudo 275 ámbitos: filtrar por dim. Usar `renta_completa` o `referencia`.

## FASE 2 — Cobertura muestral

- Solo 6 municipios Nivel1 (>=30 combinados). En larga sola: 2 (Bilbao 42, Getxo 31). Donostia larga solo 18 (62 son temporales).
- La partición cambia el mapa: temporal domina Bilbao/Donostia, larga sostiene Getxo.
- Alquiler oficial 159 sin `n_muestral` por distrito. EMAL 73 techo estructural (>5000 hab).
- Veredicto: ranking 252 NO. Comarca + capitales sí.

## FASE 3 — Calidad y sesgos

- Outliers segmentados: larga 4 (>31.20), temporal 10 (>37.50), pisos 9 (>29.68), realty 5 (>35.73). Mezclarlos daba 13; separados suman 14 con umbrales distintos. Obliga a separar.
- Superficie 15-300: larga 162/163, temporal 298/304, pisos 222/230. Bien.
- Renta vs alquiler n=159: r=0.280 Eustat, 0.263 Atlas. Débil (<0.3).
- Emancipación parsea con `;` + quote (866x9).

## FASE 4 — Dominio

- Paro Lanbide 252 media 5.91, 0 negativos, 3 ceros. Ocupación juvenil 2 ceros (micropueblos). `paro_aprox=None` correcto.
- Distancias 252 + OSRM 252 + haversine 63504. `capitales.csv` viejo 259 archivado en `legacy_obsoleto_no_usar`.
- Salarios INE nacional 1372€ 16-24. Solo contexto, no tasa municipal.
- Educación 55 sin centro y salud 21 sin centro = ausencia, no imputar.

## FASE 5 — Veredicto suficiencia

1. Ranking 252 error <20%: NO. Solo 2-6 con n>=30 en larga.
2. Esfuerzo 252: CASI. Renta 252 ok, alquiler 159 + EMAL 73.
3. Trabajo + vivienda barata: PARCIAL. Contexto 252 sí, precio municipal no.

## Plan quirúrgico

1. P1 menor: 2 anuncios fotocasa/temporal sin `codigo_ine`. Re-resolver por nombre o marcar `sin_codigo`.
2. No ampliar EMAL por hojas (T1 subconjunto, T3-T8 barrios). 73 es techo.
3. RealtyAPI a 13+ requiere créditos. No fabricar.
4. Mantener `larga vs temporal` separados en todo downstream + tests en `test_crudos.py` (57 passed).
