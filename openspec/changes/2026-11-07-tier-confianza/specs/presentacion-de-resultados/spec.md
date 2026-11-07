# presentacion-de-resultados — Delta

## Purpose

Sustituir L1/L2/L3 por Tier A/B/C/D derivado solo de `n_anuncios` real, para que nada indicativo se lea como firme.

## MODIFIED Requirements

### Requirement 1: CONCLUSION-01 — Tiers A/B/C/D, sin ranking 1-16

El sistema SHALL clasificar municipios por `n_anuncios` post re-resolución y SHALL NOT presentar ranking municipal 1-16 ni imputar precio comarcal/IDW. Tier A (n≥30): Bilbao 204, Donostia 126, Getxo 50, Vitoria-Gasteiz 39 — comparación fuerte con ranking firme. Tier B (10-29): Sopela 19, Zarautz 15, Santurtzi 11 — solo indicativo, separando temporal vs larga estancia, con min-max + mediana y `n_precio`. Tier C (1-9): sin precio municipal, solo conteo. Tier D (0): sin dato, con contexto oficial cuando exista. Precio observable solo en 62/252 municipios con anuncio real.
(Previously: niveles L1/L2/L3 con L3 1-9/0 sin dato.)

| Tier | n_anuncios | Nº | Tratamiento |
|---|---|---|---|
| A | ≥30 | 4 | fuerte |
| B | 10-29 | 3 | indicativo, temporal ≠ larga, con min-max + mediana + `n_precio` |
| C | 1-9 | 57 | sin precio municipal, solo conteo |
| D | 0 | 188 | sin dato, + contexto oficial |

#### Scenario: Ranking firme solo Tier A

- GIVEN los 4 Tier A con n≥30
- WHEN corre `python analysis/run_analisis_mongo.py` desde Mongo
- THEN `docs/conclusiones_municipios.md` compara solo Tier A con `n_anuncios` real
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

### Requirement 2: PISOS-05 — Esfuerzo contextual, frase literal

El esfuerzo municipal SHALL citarse literalmente «252 contextual sobre 159» y SHALL NOT leerse como estimación oficial donde `n_anuncios<30`. Todo valor SHALL venir de Mongo (nunca tecleado a mano).
(Previously: frase «252 contextual sobre 159 oficiales».)

#### Scenario: Frase literal en conclusiones

- GIVEN `esfuerzo_joven_pct_18_34` en 252 municipios
- WHEN se revisa `docs/conclusiones_municipios.md`
- THEN consta «252 contextual sobre 159»
- AND `grep -c "252 contextual sobre 159" docs/conclusiones_municipios.md` ≥ 1

#### Scenario: Edge 0-9 anuncios

- GIVEN municipio con 0-9 anuncios
- WHEN se genera la tabla
- THEN figura «sin dato» y no entra en mediana ni comparativa
