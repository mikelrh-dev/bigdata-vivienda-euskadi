# Reauditoría post-plan crudos — 2026-10-28

Plan ejecutado sin proxys HTTP/SOCKS y sin imputar. `verificacion_crudos.py: OK`, `pytest 54 passed`, `manifest_sha256.txt: 47 CSV`.

## Qué cambió

- Blindaje: `leer_csv_seguro(dtype=str, utf-8-sig, zfill)` en `_common.py`, aplicado en `dim_municipios.py`. `dim 252/252 len5`, prefs `48:113, 20:88, 01:51`, 0 bad_pref.
- EMAL: `emal_fianzas_ampliado.csv/json` 73 mun con `n_muestral, anio_fuente, tipo_fuente=EMAL`. T1 es subconjunto >20000, T3-T8 distritos/barrios, no nuevos municipios. 73/252 es techo estructural (>5000 hab + >=30 fianzas). Resto = sin_dato_estructural.
- Fotocasa: `anuncios_fotocasa_larga.csv` 167 + `anuncios_fotocasa_temporal.csv` 304. Medianas 15.52 vs 18.90 (+21.8%), medias 16.08 vs 20.33. No mezclar.
- Pisos: `anuncios_pisos_busqueda.csv` 230 filas, 37 ámbitos, `ambito_busqueda + es_municipio_verificado` (12 verificados). Abanto 30 y Ayala 30 son búsquedas, no geolocalizados. No usar para ranking.
- RealtyAPI: techo en 3 capitales / 139 filas sin gastar créditos. Ampliar a 13-20 municipios requiere key + 60 req (pendiente, no fabricado).
- Renta: `renta_origen=Eustat+INE_Atlas` en 252/252 (ambas presentes). `renta_municipal_referencia.csv` regenerada (hogar 48015, personal 27996). No hay imputación oculta.
- Empleo: `udalmap_empleo_corregido.csv` 252, `tasa_paro_aprox=None`, Lanbide 252 media 5.91 rango 0-12.57. Transporte 252, OSRM 252, haversine 63504. Blindados.
- Limpieza: `distancias_capitales.csv` 259 obsoleto documentado (usar `_252`), Eustat crudo 275 ámbitos filtrar por dim.

## Estado final gaps

- Alquiler 159/252 + EMAL 73/252. 93 sin dato = estructural (EMAL exige 30 fianzas, SERPAVI 14 tensionados). No imputar.
- Portales: solo capitales+corona con n>=30 en larga. No ranking 252.
- Renta 252/252 transparente. Empleo/contexto 252/252.

## Criterio aceptación

- dim 252/252 len5 0 bad_pref: PASS
- alquiler 159 + emal 73 con n_muestral: PASS (techo estructural, no 110)
- fotocasa larga vs temporal separadas: PASS
- pisos ambito_busqueda: PASS
- realtyapi >=13: PENDIENTE (requiere créditos, no fabricado)
- renta transparente: PASS
- transporte/OSRM/haversine: PASS
