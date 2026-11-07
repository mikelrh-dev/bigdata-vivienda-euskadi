# presentacion-de-resultados — Delta

## Purpose

Defender el resultado sin ranking falso: 4 municipios fuertes (L1), resto solo indicativo (L2) o sin dato (L3). Esfuerzo 252 = contextual sobre 159 oficiales.

## MODIFIED Requirements

### Requirement: CONCLUSION-01 — Niveles L1/L2/L3, sin ranking 1-16

El sistema SHALL clasificar municipios por `n_anuncios` post re-resolución y SHALL NOT presentar ranking municipal 1-16. L1 (n≥30): Bilbao 173, Donostia 113, Getxo 40, Vitoria-Gasteiz 39 — comparación firme. L2 (10-29): solo indicativo, separando temporal vs larga estancia, con min-max + mediana y `n_precio`. L3 (1-9) y 0: sin dato, sin conclusión.

| Nivel | n_anuncios | Tratamiento |
|---|---|---|
| L1 | ≥30 (4) | fuerte, comparable |
| L2 | 10-29 (16) | indicativo, temporal ≠ larga |
| L3 | 1-9 / 0 | sin dato |

#### Scenario: Sin ranking con n<30

- GIVEN 16 municipios L2 con 10-29 anuncios
- WHEN se redacta `docs/conclusiones_municipios.md`
- THEN no hay ranking 1-16; cada L2 lleva min-max + mediana + `n_precio`
- AND Getxo 40 vs Vitoria 39 se advierte (1 anuncio)

#### Scenario: L2 separa modalidades

- GIVEN L2 con anuncios temporales y de larga estancia
- WHEN se agregan indicadores
- THEN temporal y larga se reportan por separado con su `n_precio`
- AND `python analysis/run_analisis_mongo.py` → 13 PNG + 6 CSV desde Mongo

## ADDED Requirements

### Requirement: PISOS-05 — Esfuerzo contextual y texto defendible

El esfuerzo municipal SHALL presentarse como contextual: 252 municipios sobre 159 con dato oficial (base Eustat), y SHALL NOT leerse como estimación oficial donde `n_anuncios<30`. Todo valor SHALL venir de Mongo (nunca tecleado a mano).

#### Scenario: Esfuerzo 252 contextual sobre 159

- GIVEN `esfuerzo_joven_pct_18_34` en 252 municipios
- WHEN se presenta
- THEN consta «252 contextual sobre 159 oficiales» y L2/L3 sin conclusión de esfuerzo
- AND `grep -c "contextual" docs/conclusiones_municipios.md` ≥ 1

#### Scenario: Edge 0-9 anuncios

- GIVEN municipio con 0-9 anuncios
- WHEN se genera la tabla
- THEN figura «sin dato» y no entra en mediana ni comparativa
