# Datos finales y conclusiones defendibles — 2026-11-05 (rev. 2026-11-07)

Fuente: `pipeline_indicadores_municipio` (252 filas), `pipeline_vpo_por_municipio` (322),
`pipeline_vpo_terminadas` (251), `etxebide_solicitudes` (5040 docs). Verificado en Mongo el 2026-11-05;
recarga vigente tras P0/P1 (2026-11-07): **594 anuncios** (326 larga estancia + 268 temporal),
**188 municipios Tier D en cero** (sin anuncios) y **Bilbao 204 anuncios como máximo**.
759 era el pre-change.

## Cobertura real

- 252 municipios con esfuerzo 18-34: 159 oficial + 93 IDW (bandera `is_imputed`; ver capas en
  `data/resultados/capa_oficial.csv` 159 / `capa_idw.csv` 93 / `capa_contexto.csv` 252).
  Mediana oficial 26,61%, rango 13,9–38,5. En los 159 oficiales, 40 (25,2%)
  por encima del 30%; en los 252 con IDW, mediana 25,37% y 47 (18,7%) por encima.
- Anuncios: 594 en 64 municipios (25%). 188 municipios (75%) sin anuncios (Tier D en cero).
  Bilbao 204 + Donostia 126 = 56% de la muestra; top-4 = 71%.
  Municipios con >=5: 13; >=10: 7; >=30: 4.
- Conciliación 62/252 vs `n_precio=7`: 62 municipios tienen precio observable real
  (anuncio con `precio_eur` no nulo), pero solo 7 publican precio municipal
  (`n_precio=7` = 4 Tier A + 3 Tier B robustos; C/D con precio no se publican).
- Ranking bloqueado n>=30: `ranking_esfuerzo.csv` solo con n>=30 (Donostia 126, Bilbao 204,
  Vitoria 39, Getxo 50). Barakaldo (48013) n=6 figura como `n_insuficiente` y nunca
  ranking por encima de Donostia (n=126) ni de ningún Tier A.
- Precio medio observado: 60 municipios, mediana 1.328 EUR. Mediana winsorizada p1-99
  (`mediana_precio_m2_winsorizada`) para las conclusiones de precio/m2; el precio medio
  excluye outliers IQR (`precio_m2` solo en [3, 50], superficie [10, 500]).
  El resto del esfuerzo usa cuantia oficial Eustat, no precio observado.
- Paro Lanbide: 252/252 oficial (mediana 5,91%), 0 imputadas (M5: 01003/20037/48916
  rellenadas desde Lanbide directo, fuente oficial). VPO: flujo oficial 251/252
  (Usansolo sin dato), 322 filas de promociones Etxebide; stock historico
  sin fuente, no se infiere. Etxebide: 5040 solicitudes.

## Conclusiones que se sostienen

1. Bilbao (37,69%) y Donostia (38,17%): peores para emanciparse,
   precio mas alto + esfuerzo maximo entre robustos (ranking n>=30).
2. Getxo (28,60%): unico robusto bajo el 30%, por solo 1,4 puntos; no asequible.
3. Vitoria (33,37%): esfuerzo por denominador (renta), con la cuantia oficial
   mas baja (700 EUR/mes) y m2 mas barato (9,6).
4. Titular territorial: mediana oficial 26,61% (40/159, 25,2%); sensibilidad IDW-252 25,37% (47/252, 18,7%).

## Suficiente o corto

Suficiente para el reto (5+ indicadores, 11 pipelines, 4 robustos, limitaciones
declaradas). Corto para estudio academico: sin precios en 188 municipios, sin
stock VPO real, renta estimada como proxy de salario, anuncios 2026 vs
rentas/paro 2024. Declarar estos 4 huecos es lo que lo hace defendible.
