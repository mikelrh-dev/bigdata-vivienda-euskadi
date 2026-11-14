# Spec: H6 ranking de habitaciones + impresión general

**Fecha:** 2026-11-13 · **Rama:** `fix/regeneracion-procesado-resultados`

## 1. Objetivo

Sustituir el gráfico H6 de mediana/min-max logarítmico por uno que responda a dos preguntas:

1. ¿Dónde es más caro alquilar una habitación, con muestra suficiente?
2. ¿Cómo es el mercado de habitaciones en conjunto?

Sin mezclar habitaciones con vivienda entera y sin convertir los municipios con n=1–3 en un ranking.

## 2. Contrato de datos

### Ranking

- Universo: `pipeline_habitaciones_por_municipio`.
- Entran en el ranking: `n_precio >= 10`.
- Mediana: `mediana_precio_eur`.
- IC95: bootstrap determinista de la mediana, 2.000 remuestreos, semilla 42.
- Colores: firme si `n_precio >= 30`; indicativo si 10–29.

Resultado esperado:

| Municipio | n | Mediana | IC95 | Nivel |
|---|---:|---:|---:|---|
| Vitoria-Gasteiz | 12 | 400 € | 380–535 | Indicativo |
| Barakaldo | 11 | 500 € | 350–550 | Indicativo |
| Bilbao | 96 | 600 € | 568–650 | Firme |
| Donostia | 66 | 1.200 € | 690–1.400 | Firme |

Getxo (n=8), Irun (3), Errenteria (2), Durango (2) y Eibar (1) quedan fuera del ranking.

### Distribución

- Universo: `pipeline_habitaciones_precios` (precios individuales, 200 con precio).
- Mediana global: 640 €.
- Q1–Q3: 500–1.200 €.
- Porcentaje ≤700 €: 61 %.
- Outlier máximo: 109.000 €; el histograma se limita a 2.500 € y lo anota.

## 3. Contrato de presentación

B4:

- “201 anuncios en 9 municipios; 200 con precio.”
- “Solo Bilbao (96) y Donostia (66) son firmes; Vitoria (12) y Barakaldo (11), indicativos; Getxo (8) y el resto, fuera del ranking.”
- “Mediana global 640 €; 61 % ≤700 €. No se agregan con vivienda entera.”

## 4. Comandos

```bash
.venv/Scripts/python.exe analysis/run_analisis_mongo.py
.venv/Scripts/python.exe scripts/verificar_cifras_deck.py
.venv/Scripts/python.exe -m pytest tests -q
```

## 5. Reproducibilidad

- H6 se genera en `data/resultados` desde Mongo.
- La misma ejecución copia H6/H8b a `docs/presentacion_v2/assets` (`sync_deck=True`).
- No hay valores tecleados: medianas, IC, Q1/Q3 y porcentaje salen de los datos.
- No se añade CSV ni PNG nuevo: H6 conserva nombre y gold sigue en 53.

## 6. Criterios de éxito

- [ ] H6 tiene dos paneles legibles.
- [ ] El asset del deck coincide byte a byte con `data/resultados/H6...`.
- [ ] B4 no usa el antiguo “mediana/min-max” como texto principal.
- [ ] Gold 53/53; verificador y tests pasan; PDF 30 páginas.

## 7. Boundaries

- **Always:** mediana, no media; n visible; n<10 fuera de ranking.
- **Ask first:** cambiar el esquema silver, añadir loader de habitaciones, promover B4 a principal.
- **Never:** rankear los 9 municipios, mezclar con vivienda entera, inventar el outlier.
