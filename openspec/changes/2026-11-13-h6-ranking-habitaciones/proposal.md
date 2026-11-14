# Proposal: 2026-11-13-h6-ranking-habitaciones

## Intent

H6 enseña bien el rango, pero no el precio por habitación: la escala logarítmica comprime las medianas, el outlier de Vitoria (109.000 €) domina las rayas y no se ve el `n`. B4 no tiene un ranking legible ni una impresión general. Sustituir H6 por un gráfico de dos paneles: ranking n≥10 con IC95 y distribución global.

## Scope

### In Scope

- `pipeline_habitaciones_precios`: consulta auxiliar de precios individuales desde la colección de habitaciones; no entra en `PIPELINE_ORDER`.
- H6 de dos paneles: ranking n≥10 con IC bootstrap + histograma global con mediana, Q1/Q3 y porcentaje ≤700 €.
- Copia automática de H6/H8b a `docs/presentacion_v2/assets` al ejecutar `run_analisis_mongo.py` con `sync_deck=True`.
- Texto de B4 y guion; verificación del deck; PDF.

### Out of Scope

- Cambios en silver.
- Modalidad temporal en habitaciones.
- Loader de habitaciones (deuda de B4 desde cero).
- Nuevo CSV gold o cambio de 53 artefactos.
- Commit/push.

## Success Criteria

- [ ] H6 se regenera desde Mongo; ranking n≥10: Vitoria 400 (12), Barakaldo 500 (11), Bilbao 600 (96), Donostia 1.200 (66).
- [ ] Distribución global: 200 precios, mediana 640 €, Q1 500, Q3 1.200, 61 % ≤700 €.
- [ ] H6 en `data/resultados` y en `docs/presentacion_v2/assets` con el mismo SHA.
- [ ] B4 cita 200 con precio, firmes/indicativos, mediana global 640 € y 61 % ≤700 €.
- [ ] Gold sigue en 53; tests y verificador pasan; PDF con 30 páginas.

## Rollback Plan

Revertir `analysis/mongo_aggregations.py`, `analysis/run_analisis_mongo.py`, B4/guion/README y regenerar gold. No se toca Mongo ni silver.
