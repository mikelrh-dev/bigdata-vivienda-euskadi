# `data/resultados` — índice de artefactos (gold)

Capa **gold**: todo lo que hay aquí se genera desde Mongo (`analysis/run_analisis_mongo.py`) o desde
silver (`transform/auditar_lagunas_silver.py`, `transform/generar_mapa_esquema.py`). No se edita a mano.

Cifras vigentes: **594 anuncios, 64/252 municipios con anuncio, 60/252 con precio observable,
188 municipios Tier D sin dato y Bilbao 204 como máximo**. La cifra histórica pre-v5 no es vigente
y no debe citarse como total actual.

## Cómo se regenera

```bash
# Todo (silver + quality + gold), desde data/raw
.venv/Scripts/python.exe scripts/run_pipeline.py --fase silver,quality,gold

# Solo gold (requiere Mongo cargado y silver presente)
.venv/Scripts/python.exe scripts/run_pipeline.py --fase gold

# Comprobación sin escribir
.venv/Scripts/python.exe scripts/run_pipeline.py --check
```

Verificado el 2026-11-11: silver **182/182** ficheros y gold **53/53** artefactos reconstruidos desde
cero con SHA-256 idéntico.

## CSV generados desde Mongo (evidencia RA4 / PREPARACION-VISUALIZACION)

| Fichero | Contenido |
|---|---|
| `mongo_esfuerzo_por_municipio.csv` | 252 municipios con esfuerzo 18-34, tier, precio y paro (253 líneas) |
| `mongo_alquiler_por_municipio.csv` | Alquiler oficial/IDW por municipio con `metodo_imputacion` |
| `mongo_modalidades.csv` | Precio medio y mediana €/m² por modalidad (temporal vs larga estancia) |
| `mongo_accesibilidad_extendida.csv` | Tiempo a capital, servicios y VPO por municipio |
| `mongo_vpo_por_municipio.csv` | VPO por estado y tipo (promociones) |
| `mongo_vpo_terminadas_por_municipio.csv` | Flujo de VPO terminadas por mil habitantes (251/252) |
| `mongo_tier_confianza.csv` | Tier A/B/C/D (4/3/57/188) con rangos de precio |
| `mongo_habitaciones_por_municipio.csv` | 201 anuncios de habitación en 9 municipios |

## CSV de análisis (derivados)

`comparativa_3_municipios_mongo.csv` (4 Tier A), `ranking_esfuerzo.csv`, `bootstrap_robustos.csv`,
`sensibilidad_idw.csv`, `capa_oficial.csv`, `capa_idw.csv`, `capa_contexto.csv`, `udalmap_paro.csv`.

> `bootstrap_robustos.csv` mezcla precio de anuncio 2026 con renta 2024: su columna
> `esfuerzo_anuncios_pct_no_comparable` NO es un esfuerzo comparable. El IC95 mide dispersión
> relativa de anuncios, no incertidumbre de la renta oficial.

## Figuras y esquema

- 29 PNG en la raíz (A1, A2, B, C, D, E, F, H1-H13, H8b, J, O, P, g2-g5, histograma, mapa coroplético,
  transporte) más 8 PNG en `anexo/`.
- `mapa_esquema_silver.html` — grafo de relaciones entre los 40 CSV silver (PyVis, determinista).
- `auditoria_lagunas_silver.csv` — profiling de los 40 CSV silver (filas, nulos, cobertura/252).

## Qué es evidencia y qué no

- **Sí:** los 8 CSV `mongo_*` y las figuras generadas por `analysis/run_analisis_mongo.py`, que leen de
  Mongo con PyMongo y no llevan valores tecleados (P-05).
- **No:** los antiguos `dashboard.html` y `dashboard_completo.html`, retirados el 2026-11-11 por ser
  estáticos, manuales y sin generador. `mapa_esquema_silver.html` visualiza el esquema, no resultados.
