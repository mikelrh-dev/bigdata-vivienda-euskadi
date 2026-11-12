# presentacion-de-resultados — Delta

## MODIFIED Requirements

### Requirement: PREPARACION-VISUALIZACION-01 — Tres conjuntos automáticos para representar

El sistema SHALL generar mediante PyMongo datos utilizables para gráficos
(nivel 7 de la rúbrica v2) y, para el nivel 10, SHALL generar
automáticamente mediante PyMongo al menos 3 conjuntos de resultados
diferentes preparados para representar. Los valores SHALL proceder de
consultas PyMongo, nunca de números tecleados a mano. Cada figura SHALL
declarar la unidad (€/mes, €/m², €/habitación) y el vintage (alquiler 2024,
anuncios 2026, paro 2024, renta 2024) que representa.
(Previously: sin requisito de etiquetas de unidad y vintage.)

> Cotejo PDF (2026-11-05): PDF línea 123, columna *10 puntos* literal:
> «Genera automáticamente mediante PyMongo al menos 3 conjuntos de
> resultados diferentes preparados para representar». Sin diferencias
> literales.

> Extensión propia más estricta que el PDF: «nunca de números tecleados a
> mano» y «regenerar ... reproduce los mismos resultados». El PDF (línea
> 123) solo dice «Genera automáticamente mediante PyMongo al menos 3
> conjuntos ... preparados para representar»; no detalla la prohibición de
> tecleado ni la reproducibilidad de la regeneración. Se conserva sin borrar
> como endurecimiento propio (prohibición P-05 + reproducibilidad del
> orquestador `analysis/run_analisis_mongo.py`), verificado por
> `tests/test_mongo_orquestador.py`. No es requisito v2.

#### Scenario: Figuras con unidad y vintage

- GIVEN las figuras N1/N2/A1/A2/F/P/H6/H8/H8b/H10/I
- WHEN se generan
- THEN cada una declara la unidad y el vintage que representa
- AND H8b usa €/m²; H6 usa €/habitación

#### Scenario: Datos utilizables para gráficos — nivel 7

- GIVEN una agregación sobre MongoDB
- WHEN se genera el conjunto de resultados
- THEN los datos quedan utilizables directamente para representar

#### Scenario: Al menos 3 conjuntos automáticos diferentes — nivel 10

- GIVEN los análisis principales ejecutados
- WHEN el script PyMongo termina
- THEN existen al menos 3 conjuntos de resultados diferentes
- AND cada conjunto queda preparado para su representación
- AND ningún valor procede de un número escrito a mano
- AND regenerar los conjuntos reproduce los mismos resultados

### Requirement: CONCLUSION-02 — Tiers A/B/C/D, conciliación 60/252 vs n_precio=7 y ranking n>=30 (M2/M3, extensión 2026-11-07, sustituye L1/L2/L3)

El sistema SHALL clasificar municipios por `n_anuncios` post re-resolución y SHALL NOT presentar ranking municipal 1-16 ni imputar precio comarcal/IDW. Tier A (n≥30): Bilbao 204, Donostia 126, Getxo 50, Vitoria-Gasteiz 39 — comparación fuerte con ranking firme. Tier B (10-29): Sopela 19, Zarautz 15, Santurtzi 11 — solo indicativo, separando temporal vs larga estancia, con min-max + mediana y `n_precio`. Tier C (1-9): sin precio municipal, solo conteo. Tier D (0): sin dato, con contexto oficial cuando exista. Precio observable solo en 60/252 municipios con anuncio real (64/252 con anuncio).
(Previously: niveles L1/L2/L3 con L3 1-9/0 sin dato; precio observable 62/252.)

El sistema SHALL documentar en `data/resultados/README.md` la tabla de conciliación: 60/252 municipios con precio observable real (post re-resolución) frente a `n_precio=7` del tier agregado — los 7 son exclusivamente los municipios A+B robustos (4 Tier A + 3 Tier B) que sí publican precio municipal tras suprimir C/D; los C/D con precio no se publican. README SHALL mostrar ambas cifras juntas con esta explicación, sin esconder ninguna. El sistema MUST NOT presentar ranking, top-10 ni ordenación de esfuerzo o precios con municipios de `n_anuncios<30`: Barakaldo (`n=6`) SHALL NOT ranking verse por encima de Donostia (`n=126`) ni de ningún Tier A. Los municipios Tier C/D con `n<30` SHALL mostrarse como «n insuficiente» (con su `n` visible), nunca ocultarse ni ordenarse.

| Tier | n_anuncios | Nº | Tratamiento |
|---|---|---|---|
| A | ≥30 | 4 | fuerte |
| B | 10-29 | 3 | indicativo, temporal ≠ larga, con min-max + mediana + `n_precio` |
| C | 1-9 | 57 | sin precio municipal, solo conteo |
| D | 0 | 188 | sin dato, + contexto oficial |

#### Scenario: Ranking firme solo Tier A

- GIVEN los 4 Tier A con n≥30
- WHEN corre `python analysis/run_analisis_mongo.py` desde Mongo
- THEN `openspec/archive/2026-11-10-docs/conclusiones_municipios.md` compara solo Tier A con `n_anuncios` real
- AND salida: 13 PNG + 6 CSV, sin valores tecleados a mano

#### Scenario: Tier B separa modalidades

- GIVEN Sopela 19, Zarautz 15, Santurtzi 11
- WHEN se agregan indicadores
- THEN cada Tier B lleva min-max + mediana + `n_precio_temporal` y `n_precio_larga` por separado
- AND prohibido promediar temporal + larga; no hay ranking 1-16

#### Scenario: Edge Tier C/D sin precio municipal

- GIVEN municipio Tier C (1-9) o Tier D (0)
- WHEN se genera la tabla
- THEN figura «sin dato» con solo conteo, sin precio municipal y sin ranking
- AND Tier D añade contexto oficial sin conclusión de precio

#### Scenario: Conciliación 60 vs 7 publicada en README

- GIVEN resultados regenerados por `python analysis/run_analisis_mongo.py`
- WHEN se lee `data/resultados/README.md`
- THEN consta «60/252 con precio observable» y «`n_precio=7` = A+B robusto (4 A + 3 B); C/D suprimidas» en la misma tabla
- AND `grep -n "60/252" data/resultados/README.md` → salida: ≥ 1 línea; `grep -n "n_precio=7" data/resultados/README.md` → salida: ≥ 1 línea

#### Scenario: Ranking bloqueado para `n<30`

- GIVEN el ranking de esfuerzo con Barakaldo `n=6` y Donostia `n=126`
- WHEN corre `python analysis/run_analisis_mongo.py` y se genera el ranking
- THEN Barakaldo figura como «n insuficiente» (n=6 visible) y no ordena por encima de Donostia; el top-10 solo contiene `n>=30`
- AND `python -c "import pandas as pd; d=pd.read_csv('data/resultados/ranking_esfuerzo.csv'); print(d['n_anuncios'].min())"` → salida: `>= 30` (nunca 6)

### Requirement: BOOTSTRAP-01 — `n_larga_solo_vivienda` ≠ Tier

El sistema SHALL documentar que el bootstrap usa `n_larga_solo_vivienda` 67/60/39/37 (Bilbao/Donostia/Getxo/Vitoria-Gasteiz), distinto del `n_anuncios` Tier 204/126/50/39. SHALL constar IC95 Bilbao 33.75–40.95 y Getxo 27.54–31.77. Los dos `n` SHALL NOT intercambiarse en textos ni gráficos. El bootstrap SHALL declarar que mezcla precio de anuncio 2026 con renta 2024 y NO es un esfuerzo comparable; la columna `esfuerzo_anuncios_pct` SHALL llevar sufijo `_no_comparable` y una columna de aviso.
(Previously: sin declaración de no comparabilidad.)

#### Scenario: Bootstrap con su propio n

- GIVEN `data/resultados/bootstrap_robustos.csv`
- WHEN se lee
- THEN `n_anuncios_larga_vivienda` es 67/60/39/37, IC95 Bilbao 33.75–40.95 y Getxo 27.54–31.77
- AND el texto distingue ese `n` del Tier 204/126/50/39

#### Scenario: Bootstrap declarado no comparable

- GIVEN `bootstrap_robustos.csv`
- WHEN se lee
- THEN `esfuerzo_anuncios_pct_no_comparable` lleva aviso «precio 2026 vs renta 2024»
- AND el deck no presenta el 74,27 % de Bilbao como esfuerzo
