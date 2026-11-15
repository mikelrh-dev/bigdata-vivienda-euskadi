# `data/resultados` — índice de artefactos (gold)

Capa **gold**: todo lo que hay aquí se genera desde Mongo (`analysis/run_analisis_mongo.py`) o desde
silver (`transform/auditar_lagunas_silver.py`, `transform/generar_mapa_esquema.py`). No se edita a mano.

Cifras vigentes: **594 anuncios, 64/252 municipios con anuncio, 60/252 con precio observable,
188 municipios Tier D sin dato y Bilbao 204 como máximo**. La cifra histórica pre-v5 no es vigente
y no debe citarse como total actual.

## Cómo se regenera

```bash
# Silver + quality, desde data/raw (gold exige Mongo ya cargado)
.venv/Scripts/python.exe scripts/run_pipeline.py --fase silver,quality

# Solo gold (requiere Mongo cargado y silver presente)
.venv/Scripts/python.exe scripts/run_pipeline.py --fase gold

# Comprobación sin escribir
.venv/Scripts/python.exe scripts/run_pipeline.py --check
```

Verificado el 2026-11-11: silver **183/183** ficheros y gold **53/53** artefactos reconstruidos desde
cero con SHA-256 idéntico. Tras añadir la serie de VPO, gold son **55/55** (24 CSV + 31 PNG).

## CSV generados desde Mongo (evidencia RA4 / PREPARACION-VISUALIZACION)

| Fichero | Contenido |
|---|---|
| `mongo_esfuerzo_por_municipio.csv` | 252 municipios con esfuerzo 18-34, tier, precio y paro (253 líneas) |
| `mongo_alquiler_por_municipio.csv` | Alquiler oficial/IDW por municipio con `metodo_imputacion` |
| `mongo_modalidades.csv` | Precio medio, mediana €/m² y mediana de superficie por modalidad (temporal vs larga estancia) |
| `mongo_accesibilidad_extendida.csv` | Tiempo a capital, servicios y VPO por municipio |
| `mongo_vpo_por_municipio.csv` | VPO por estado y tipo (promociones) |
| `mongo_vpo_terminadas_por_municipio.csv` | Flujo de VPO terminadas por mil habitantes (251/252) |
| `mongo_tier_confianza.csv` | Tier A/B/C/D (4/3/57/188) con rangos de precio |
| `mongo_habitaciones_por_municipio.csv` | 201 anuncios de habitación en 9 municipios; `n_precio` cuenta los 140 utilizables tras descartar los 60 cuyo precio alcanza el alquiler mediano de vivienda del municipio (`tope_alquiler_eur_mes`, `n_descartados_precio`) |

## CSV de análisis (derivados)

`comparativa_3_municipios_mongo.csv` (4 Tier A), `ranking_esfuerzo.csv`, `bootstrap_robustos.csv`,
`sensibilidad_idw.csv`, `capa_oficial.csv`, `capa_idw.csv`, `capa_contexto.csv`, `udalmap_paro.csv`.

> `bootstrap_robustos.csv` mezcla precio de anuncio 2026 con renta 2024: su columna
> `esfuerzo_anuncios_pct_no_comparable` NO es un esfuerzo comparable. El IC95 mide dispersión
> relativa de anuncios, no incertidumbre de la renta oficial.

## Figuras y esquema

- 31 PNG en la raíz (A1, A2, B, C, D, E, F, H1-H13, H8b, J, O, P, S, g2-g5, histograma, mapa
  coroplético, transporte) más 8 PNG en `anexo/`.
- `H6_habitaciones_mediana_rango.png` — ranking n≥10 con IC95, distribución de los 140 precios
  plausibles y esfuerzo individual sobre salario joven 2026; se copia al deck al ejecutar
  `run_analisis_mongo.py` (`sync_deck=True`).
- `mapa_esquema_silver.html` — grafo de relaciones entre los 42 CSV silver (PyVis, determinista).
- `auditoria_lagunas_silver.csv` — **pendiente de materializar** en este checkout: la genera
  `transform/auditar_lagunas_silver.py` (audita los 42 CSV silver) y `transform/run_all.py --check`
  la reporta como salida que falta. Regenerarla sube el gold de 55 a 56 artefactos.

## Vintage (año) de cada figura

Cada PNG declara a qué año pertenecen sus datos. La autoridad única es
`config/vintage_figuras.yaml`; el generador imprime la etiqueta abajo a la derecha
y la escribe como metadato PNG (`Vintage`, `Description`), así que se comprueba
sobre el fichero, no sobre el código.

```bash
.venv/Scripts/python.exe scripts/verificar_vintage_figuras.py
# OK  52 figuras declaradas · gold, deck y memoria sellados y coherentes
```

| Código | Qué significa | Figuras |
|---|---|---|
| `2024` | Ancla oficial: alquiler Eustat Bizilagun 2024 y renta INE Atlas 2024 | A1, A2, E, F, H1, H3, H4\*, H10, H11, O\*, g1\*, g2, L\*, `mapa_coroplastico_esfuerzo_18_34`, `hist_esfuerzo_18_34_umbral30`, `dumbbell_esfuerzo_18_24_vs_25_34` |
| `2026` | Capa de oferta: anuncios Fotocasa/Pisos/RealtyAPI 2026 | H2, H6, H8, H8b, H9\*, H13, I\*, J, g3, g4, todo `M26_*` y los `barras_*`/`scatter_*` de `visuals/` |
| `mixto` | Mezcla declarada: **no comparable** | B (paro 2024 + precio 2026), D y H7 (2024/anuncios + distancia sin año), g5 (esfuerzo 2024 frente a muestra 2026), P, K\*, `transporte_oferta_vs_esfuerzo`, `M26_brecha_2024_2026` |
| `flujo` | Flujo, no stock | H5 (2020-2024), S (2004-2024, ventana de 5 años) |
| `acumulado` | Registro Etxebide: no hay un año único, solo fecha de sorteo (2001-2014) en parte de las promociones | C, H12\* |
| `sin-fecha` | Conteos del pipeline | G\* |

\* figuras de `anexo/`.

Reglas que se respetan y se verifican:

- Una figura que mezcla anuncios 2026 con una fuente 2024 se declara `mixto`
  salvo que los anuncios solo filtren la muestra (`muestra_2026: true`, caso de O).
- `P_oficial_vs_anuncios_por_TH.png` no puede declararse de un solo año.
- El paro de la figura B es Udalmap 2024 (249 municipios) con 3 de Lanbide
  directo; no es una serie 2026.

El mismo comando que regenera el gold deja al día las copias: 12 PNG al deck
(`sincronizacion.deck`) y 8 a `docs/memoria/figuras` (`sincronizacion.memoria`).
Antes se copiaban a mano y H2, H8, P y dos figuras de la memoria se habían
quedado en la versión anterior.

## Qué es evidencia y qué no

- **Sí:** los 8 CSV `mongo_*` y las figuras generadas por `analysis/run_analisis_mongo.py`, que leen de
  Mongo con PyMongo y no llevan valores tecleados (P-05).
- **No:** los antiguos `dashboard.html` y `dashboard_completo.html`, retirados el 2026-11-11 por ser
  estáticos, manuales y sin generador. `mapa_esquema_silver.html` visualiza el esquema, no resultados.
