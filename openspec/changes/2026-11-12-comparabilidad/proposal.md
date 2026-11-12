# Proposal: Contrato de comparabilidad y separación de capas

## Intent

Las figuras y conclusiones mezclan magnitudes no comparables: la capa oficial
Eustat 2024 con la IDW comarcal (93) y con los anuncios 2026; €/mes con €/m² y
€/habitación; y denominadores de renta distintos bajo el mismo nombre
«esfuerzo». El dato subyacente es correcto; falla la presentación y la
declaración. Este cambio congela un contrato de comparabilidad, separa y
etiqueta las capas en las figuras, renombra columnas ambiguas y alinea las
declaraciones con los datos reales.

## Scope

### In Scope
- `config/comparabilidad.yaml`, `docs/matriz-comparabilidad.md`,
  `analysis/comparabilidad.py`, `tests/test_comparabilidad.py`.
- Separar capas (oficial 159 / IDW 93 / contexto 252) en N1/N2/A1/A2/F/P.
- Separar unidades (€/mes, €/m², €/habitación) en H6/H8/H8b y alinear H10.
- Renombrar columnas ambiguas: `esfuerzo_joven_pct` (legacy 16-29),
  `esfuerzo_alquiler_pct`, `precio_medio_eur`, `esfuerzo_anuncios_pct`.
- Corregir declaraciones: denominador (INE Atlas renta_hogar 2024), paro
  (Udalmap 2024 general 16-64), conteos (64/252 anuncio, 60/252 precio).
- Recalcular la tensión con el esfuerzo canónico 18-34.
- Deltas OpenSpec en `contrato-reto`, `mongodb-y-analisis` y
  `presentacion-de-resultados`.

### Out of Scope
- Descargas nuevas, `data/raw`, HDFS/Kafka.
- Cambiar el método IDW ni los valores de las capas.
- Tocar H8b, `sensibilidad_idw`, `mongo_tier_confianza` ni el 15,38 €/m².

## Capabilities

### New Capabilities
- `comparabilidad`: contrato de capas, unidades, vintages y denominadores.

### Modified Capabilities
- `contrato-reto`: denominador del esfuerzo y declaración de paro.
- `mongodb-y-analisis`: AGREGACION-01 (capas no mezcladas), PISOS-03 (conteos),
  CAPAS-01 (figuras etiquetadas).
- `presentacion-de-resultados`: PREPARACION-VISUALIZACION-01 (etiquetas),
  CONCLUSION-02 (conciliación), BOOTSTRAP-01 (no comparable).

## Approach

Contrato primero (config + matriz + helpers + tests), luego separar capas y
unidades en los generadores de figuras, renombrar columnas, corregir
declaraciones, recalcular la tensión y recargar Mongo, y regenerar silver y
gold.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `analysis/run_analisis_mongo.py` | Modified | A1/A2/F/P/H6/H8/H10/I: capas y unidades |
| `transform/generar_figuras_N.py` | Modified | N1/N2/F/P/H8: capas y etiquetas |
| `analysis/mongo_aggregations.py` | Modified | `pipeline_alquiler_por_municipio` expone `metodo_imputacion` |
| `transform/calcular_tension_social.py` | Modified | tensión con 18-34 |
| `analysis/sensibilidad.py` | Modified | bootstrap etiquetado no comparable |
| `config/parametros_estudio.yaml` | Modified | denominador y paro declarados |
| `README.md`, `docs/presentacion_v2/` | Modified | conteos y etiquetas |
| `openspec/specs/*` | Modified | deltas |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Recalcular la tensión cambia categorías | Med | Documentar el delta; no forzar checks |
| Renombrar columnas rompe consumidores | Med | Mantener alias legacy declarados |
| Regenerar gold cambia PNG | Baja | Doble ejecución con SHA; verificar |

## Rollback Plan

Revertir por fase (`git revert` de los commits del change). El contrato y los
renombres son aditivos; la tensión se regenera con el generador anterior.

## Dependencies

Mongo local cargado; `.venv` con pandas. `gentle-ai` 4.0.0 no expone
`sdd-status`; se usa el contrato manual.

## Success Criteria

- [ ] `pytest tests -q` verde (237+ passed, 2 skipped).
- [ ] `grep "83/252"` y `grep "62/252 con anuncio"` → 0.
- [ ] N1/N2/A1/A2/F/P etiquetan oficial/IDW; H6/H8/H8b separan unidades.
- [ ] `config/comparabilidad.yaml` y `docs/matriz-comparabilidad.md` coherentes.
- [ ] `run_pipeline --fase gold` regenera 53/53 con SHA idéntico.
