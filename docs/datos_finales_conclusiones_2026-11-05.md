# Datos finales y conclusiones defendibles — 2026-11-05

Fuente: `pipeline_indicadores_municipio` (252 filas), `pipeline_vpo_por_municipio` (322),
`pipeline_vpo_terminadas` (251), `etxebide_solicitudes` (5040 docs). Verificado en Mongo el 2026-11-05.

## Cobertura real

- 252 municipios con esfuerzo 18-34: 159 oficial + 93 IDW (bandera `is_imputed`).
  Mediana oficial 26,61%, rango 13,9–38,5. En los 159 oficiales, 40 (25,2%)
  por encima del 30%; en los 252 con IDW, mediana 25,37% y 47 (18,7%) por encima.
- Anuncios: 759 en 83 municipios (33%). 169 municipios (67%) sin anuncios.
  Bilbao 173 + Donostia 113 = 38% de la muestra; top-4 = 48%.
  Municipios con >=5: 28; >=10: 20; >=30: 4.
- Precio medio observado: 80 municipios, mediana 1.382 EUR.
  El resto del esfuerzo usa cuantia oficial Eustat, no precio observado.
- Paro Lanbide: 249/252, mediana 5,94%. VPO: flujo oficial 251/252
  (Usansolo sin dato), 322 filas de promociones Etxebide; stock historico
  sin fuente, no se infiere. Etxebide: 5040 solicitudes.

## Conclusiones que se sostienen

1. Bilbao (37,69%) y Donostia (38,17%): peores para emanciparse,
   precio mas alto + esfuerzo maximo entre robustos.
2. Getxo (28,60%): unico robusto bajo el 30%, por solo 1,4 puntos; no asequible.
3. Vitoria (33,37%): esfuerzo por denominador (renta), con la cuantia oficial
   mas baja (700 EUR/mes) y m2 mas barato (9,6).
4. Titular territorial: mediana oficial 26,61% (40/159, 25,2%); sensibilidad IDW-252 25,37% (47/252, 18,7%).

## Suficiente o corto

Suficiente para el reto (5+ indicadores, 9 pipelines, 4 robustos, limitaciones
declaradas). Corto para estudio academico: sin precios en 169 municipios, sin
stock VPO real, renta estimada como proxy de salario, anuncios 2026 vs
rentas/paro 2024. Declarar estos 4 huecos es lo que lo hace defendible.
