# Análisis: Correlación renta municipal vs alquiler municipal

**Fecha:** 2026-10-27  
**Métrica:** Pearson r = 0.2094 (calculada sobre 159 municipios con alquiler oficial).

## Interpretación

La correlación entre renta media municipal (Eustat 2024) y alquiler medio (€/m², Eustat) es **débil** (r < 0.3).

Esto implica que el precio del alquiler **no se explica por la renta local**. Otros factores (oferta, demanda, turismo, distancia a capitales, tamaño del municipio) tienen mayor peso.

## Implicación para la defensa

En el informe final se debe:
1. Mencionar r = 0.2094 y su interpretación.
2. No atribuir el precio del alquiler únicamente a la renta.
3. Explorar otras variables explicativas: distancia a capitales (distancias_capitales.csv), tasa de ocupación (udalmap), densidad de población (eustat_poblacion_edad.csv).

## Acción futura

Cuando el paro/ocupación se corrija (Fase 0.1), recalcular la correlación multivariante (renta + ocupación + distancia a capital → alquiler).
PY