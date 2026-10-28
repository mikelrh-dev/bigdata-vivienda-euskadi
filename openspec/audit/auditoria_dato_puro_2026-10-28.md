# Auditoría Dato Puro — 2026-10-28 (fase recopilación crudos, sin proxys)

Framework: `framework_auditoria_completo2/03_framework_auditoria_dato_puro.md`
Alcance: `data/raw/` actual. Solo lectura, sin modificar datos.

## 1. Métricas reales observadas

| Fuente | Filas válidas | Municipios | % /252 | n>=30 | n 5-29 | n<5 | codigo_ine | Outliers |
|---|---|---|---|---|---|---|---|---|
| dim_municipios.csv | 252 | 252 | 100% | — | — | — | 252/252 len 5 como str | — |
| alquiler_municipal.csv | 253 filas distrito | 159 | 63% | — | — | — | 159/159 | 1 alto Donostia |
| anuncios_fotocasa.csv | 456 válidos | 61 nombres / 60 códigos | 24% | 3: Bilbao 189, Donostia 80, Getxo 40 | 9 | 49 | 469/471 len5 | 13 (>36.45 €/m2) |
| anuncios_pisos.csv | 201 válidos | 37 busqueda / 7 canonico | 15% | 2: Abanto 30, Ayala 30 (búsqueda, no geoloc) | 11 | 24 | 230/230 | 9 (>29.67) |
| anuncios_realtyapi.csv | 139 válidos | 3 capitales | 1% | 3/3 | 0 | 0 | 139/139 | 5 (>35.73) |
| renta_municipal_completa.csv | 252 | 252 | 100% | — | — | — | 252/252 | — |
| ine_atlas_renta.csv | 252 | 252 | 100% | — | — | — | 252/252 | — |
| udalmap_empleo + corregido + lanbide | 252 | 252 | 100% | — | — | — | 252/252 | — |
| emal_fianzas.csv | 730 filas | 73 | 29% | — | — | — | 73/73 | — |
| etxebide_solicitudes.csv | 5040 | 252 | 100% | — | — | — | 252/252 | — |
| educacion_centros.csv | 1309 centros | 197 | 78% | — | — | — | parcial len5 | — |
| salud_centros.csv | 528 centros | 231 | 92% | — | — | — | parcial | — |
| transporte_paradas_municipio.csv | 252 | 252 | 100% | — | — | — | 252/252 | — |
| distancias_haversine_252.csv | 63504 = 252x252 | 252 | 100% | — | — | — | — | — |
| distancias_capitales_252.csv | 252 | 252 | 100% | — | — | — | 252/252 | — |
| osrm_tiempos_capitales.csv | 252, 0 nulos | 252 | 100% | — | — | — | 252/252 | — |
| eustat_renta_municipal.csv crudo | 98532 filas, 275 ámbitos | — | — | — | — | — | necesita filtro 24 agregados | — |
| emancipacion_juventud.csv | 866 con ; + quote | — | — | — | — | — | — | — |
| ine_salarios_edad.csv | 198 series | nacional | n/a | — | — | — | — | — |

Verificados:
- Zero-padding Araba OK si se lee como str (dim 252/252 len5, alquiler 01051, fotocasa 20069, pisos 01003). El falso 4 dígitos era por leer codigo_ine como int. Blindar con dtype=str + zfill(5).
- Temporal vs larga: True 296 media 20.38 mediana 18.92 vs False 160 media 16.29 mediana 15.53. +25%/+21% >15%: separar siempre.
- Renta vs alquiler n=159: r=0.28 Eustat, 0.26 Atlas. Débil.
- Paro: tasa_paro_aprox todo NaN (fórmula retirada), lanbide 252/252 media 5.91 rango 0-12.57 sin negativos. Ocup juvenil 2 ceros.
- Distancias: haversine 63504 completo, capitales_252 252 limpio, OSRM 252 sin nulos. distancias_capitales.csv viejo 259 con prefijos 15,19 obsoleto.
- Emancipación parsea con delimiter=';' quotechar='"'.
- Cero proxy red en extract/.

## 2. Gaps P1/P2/P3

P1:
1. Pisos municipio_busqueda 37 vs nombre_canonico 7. Subtítulo es barrio. No usar para ranking municipal.
2. Fotocasa 49/61 con <5. Solo 3 >=30.
3. Alquiler oficial 159/252 sin n muestral. 93 sin dato.
4. EMAL 73/252.
5. renta_municipal_completa renta_origen=Eustat en 252/252. Transparentar cómo se cubrieron 51 faltantes Eustat.

P2:
- Educación 197/252, Salud 231/252. Ausencia = dato (0/sin centro), no imputar.
- Eustat crudo 275 ámbitos. Filtrar a 252 dim.
- Emancipación requiere ;.

P3:
- Archivar distancias_capitales.csv viejo. Encoding utf-8 (Donostia, Ciérvana).

## 3. Veredicto suficiencia

1. Ranking 252 con error <20%? NO. Solo comarca + capitales.
2. Tasa esfuerzo para 252? CASI. Renta 252 ok, alquiler 159. Faltan 93.
3. Trabajo + vivienda barata? PARCIAL. Paro/distancias/OSRM sí. Vivienda municipal no.

## 4. Ruta sin proxys (solo cubrir dato)

1. dtype=str+zfill(5) en _common, entity_resolution, enriquecer_codigo_ine, dim_municipios.
2. Alquiler 159→252 vía Eustat/Bizilagun agregada separada + EMAL 73→más. Añadir n_muestral + anio_fuente.
3. Portales: capitales + corona hasta n>=30 en larga separada de temporal. Pisos geocodificar subtitulo o marcar ambito_busqueda.
4. Renta: renta_origen fila a fila real (Eustat vs Atlas).
5. Servicios: ausencia como 0/sin centro.
6. Archivar capitales.csv viejo. Usar lanbide como paro oficial, retirar aprox del esfuerzo.
7. Emancipación ;, salarios solo contexto nacional joven.
