# Spec: esfuerzo individual de habitación

## Fórmula

```text
esfuerzo_pct = mediana_precio_habitacion_eur_mes / salario_joven_2026_ajustado_18_34_eur_mes * 100
```

- Numerador global: mediana de los 200 precios individuales = 640 €.
- Numerador municipal: `mediana_precio_eur` de `mongo_habitaciones_por_municipio.csv`.
- Denominador: mediana de `salario_joven_2026_ajustado_18_34_eur_mes` en `pipeline_esfuerzo_mercado_2026` = **1.718,65 €/mes**.
- Es esfuerzo **individual**, no de hogar: una habitación sobre un salario joven. No se compara con la vivienda entera.

## Resultados esperados

| Ámbito | Mediana | Esfuerzo |
|---|---:|---:|
| Global (200 precios) | 640 € | 37,2 % |
| Donostia | 1.200 € | 69,8 % |
| Bilbao | 600 € | 34,9 % |

## Presentación

- H6: línea “Esfuerzo mediano 37,2 % del salario joven 2026” en el título del panel de distribución.
- B4: “Esfuerzo individual 37,2 % del salario joven; Donostia 69,8 %, Bilbao 34,9 %.”
- Guion: misma formulación y fuente.

## Reproducibilidad

`run_analisis_mongo.py` obtiene el salario de `pipeline_esfuerzo_mercado_2026` y el precio de `pipeline_habitaciones_precios`; no hay cifras tecleadas. El bootstrap y el salario son constantes/deterministas. El asset se copia al deck en la misma ejecución.

## Boundaries

- **Always:** usar mediana, no media; etiquetar “individual”; no mezclar con vivienda entera.
- **Ask first:** cambiar el denominador a renta de hogar, añadir carga de alquiler al salario o imputar salarios locales.
- **Never:** presentar 37,2 % como esfuerzo de hogar o como tasa neta.
