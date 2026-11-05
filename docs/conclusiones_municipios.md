# Conclusiones municipales (4 robustos)

Fuente de verdad: Mongo pipeline `pipeline_indicadores_municipio` (n y `precio_medio_eur` desde `anuncios`, esfuerzo desde `alquiler_municipal.cuantia_media_eur_mes_mediana` x12 / renta joven estimada x100) + silver `analisis_variables_base.csv` / `alquiler_municipal_completo.csv` para paro Lanbide y precio m2. No se inventa ningun valor: Vitoria se calcula con el mismo pipeline que los otros tres. `codigo_ine` a 5 digitos (Vitoria `01059`, no `1059`).

| Municipio | Codigo INE | n anuncios (Mongo `pipeline_indicadores_municipio`) | Esfuerzo 18-34 (%) | Esfuerzo 16-29 legacy (%) | Precio medio EUR (Mongo `precio_medio_eur`) | Cuantia alquiler EUR/mes (mediana oficial) | Precio m2 EUR/mes (mediana oficial) | Paro Lanbide (%) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Bilbao | 48020 | 173 | 37,69 | 60,70 | 1695,59 | 850,00 | 11,4 | 9,71 |
| Donostia / San Sebastian | 20069 | 113 | 38,17 | 61,48 | 2462,89 | 995,00 | 14,6 | 5,82 |
| Getxo | 48044 | 40 | 28,60 | 46,06 | 1527,50 | 887,00 | 11,1 | 6,40 |
| Vitoria-Gasteiz | 01059 | 39 | 33,37 | 53,75 | 1406,13 | 700,00 | 9,6 | 8,89 |

Verificacion rapida: `data/resultados/comparativa_3_municipios_mongo.csv` repite las cuatro filas (Bilbao 173, Donostia 113, Getxo 40, Vitoria-Gasteiz 39, `codigo_ine` a 5 digitos) con `esfuerzo_joven_pct_18_34`, `precio_medio_eur` y `tasa_paro_lanbide_pct` no nulo identicos a la tabla. Paro: Mongo `municipios.empleo.tasa_paro_lanbide_pct` via `pipeline_indicadores_municipio` (silver `analisis_variables_base.csv` col. `tasa_paro_lanbide_pct` como respaldo coherente, nunca `tasa_paro_aprox_pct` que es NaN en 252). Precio m2: `alquiler_municipal_completo.csv` columna `renta_media_eur_m2_mediana` (Eustat oficial 2024) y Mongo `renta_m2_alquiler`.

## Una frase por municipio

- **Bilbao (48020, n=173, esfuerzo 18-34 37,69%)**: con la muestra mas robusta del estudio, supera el umbral de 30% por casi 8 puntos y combina el paro Lanbide mas alto de los cuatro (9,71%), por lo que la tension no viene solo del precio sino de la renta disponible.
- **Donostia / San Sebastian (20069, n=113, esfuerzo 18-34 38,17%)**: esfuerzo canonico maximo entre los robustos con el precio medio (2462,89 EUR) y el precio m2 (14,6 EUR/m2) mas altos, pese al paro mas bajo (5,82%), lo que indica presion pura de mercado y no de empleo.
- **Getxo (48044, n=40, esfuerzo 18-34 28,60%)**: es el unico robusto por debajo del 30% en 18-34, pero solo por 1,4 puntos y con cuantia de 887 EUR/mes, por lo que no se puede declarar asequible sin refuerzo de muestra.
- **Vitoria-Gasteiz (01059, n=39, esfuerzo 18-34 33,37%)**: esfuerzo necesitado 33,37% con cuantia oficial de 700 EUR/mes (la minima de los cuatro) y precio m2 de 9,6 EUR/m2, con paro 8,89%, por lo que el esfuerzo viene del denominador (renta joven estimada) mas que de un alquiler caro.

## Advertencia metodologica

- **Getxo 40 vs Vitoria-Gasteiz 39 (1 anuncio de diferencia)**: el umbral robusto n>=30 es una linea de decision, no una diferencia economica; el ranking fino Getxo > Vitoria puede invertirse con un solo anuncio nuevo. Por eso el esfuerzo 18-34 (28,60% frente a 33,37%) se cita con su n y con la cuantia, no como victoria; Getxo 40 vs Vitoria no es ranking firme.
- **Barakaldo (48013, n=13, esfuerzo 18-34 38,49%) supera a Donostia (38,17%)**: el ejemplo de Barakaldo (Mongo `pipeline_indicadores_municipio`, esfuerzo 18-34 = 38,4959%) demuestra que el esfuerzo alto aparece tambien fuera de los robustos; no se puede convertir el ranking de esfuerzo en ranking de municipios sin aplicar el filtro n>=30.

## O1 canonico (ver `README.md`)

- Universo canonico 18-34 oficial: 159 municipios con alquiler oficial Eustat (mediana Mongo `pipeline_indicadores_municipio` verificada 26,61%, ver tabla abajo).
- Sobre el 30%: 40 de 159 = 25,2% superan el 30% en esfuerzo 18-34 oficial.
- Sensibilidad Eje D: oficial 159 mediana 26,61%; IDW 93 mediana 23,38%; media global 252 mediana 25,37%.

## Tabla O1 (canonico, verificable)

| Universo | n | Mediana esfuerzo 18-34 (%) | Sobre 30% (%) |
|---|---:|---:|---:|
| Oficial 159 (Eustat directo) | 159 | 26,61 | 25,2 (40/159) |
| IDW 93 (imputado) | 93 | 23,38 | (sensibilidad) |
| Todos 252 | 252 | 25,37 | 18,7 (47/252) |

## Notas de fuente del pipeline

- Esfuerzo 18-34 = `cuantia_media_eur_mes_mediana` x12 / `renta_joven_estimada_18_34` x100; esfuerzo 16-29 legacy usa `renta_joven_estimada_16_29` con el mismo numerador. El pipeline principal es `pipeline_indicadores_municipio` en `analysis/mongo_aggregations.py`.
- `n_anuncios` y `precio_medio_eur` vienen del `$lookup` a `anuncios` por `ubicacion.codigo_ine`; son foto 2026 (Fotocasa + Pisos + RealtyAPI), no stock oficial.
- Paro y cuello de botella: cadena offline actual — HDFS centro solo lectura (raw intacto, procesado sin subir) + Kafka VM pid 1832 verificado en `docs/trazabilidad_vm.md`; todas las cifras anteriores salen de CSV regenerados y de Mongo en local (Docker).
