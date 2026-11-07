# presentacion-de-resultados — Delta

## Purpose

Cerrar los huecos narrativos P0/P1 para que nadie lea cifras incoherentes: (M2) documentar la conciliación entre los 62/252 municipios con precio observable y el `n_precio=7` publicado tras suprimir los tiers C/D — el 7 es solo el A+B robusto, no el total de municipios con precio; (M3) bloquear cualquier ranking o top-10 de esfuerzo/precios con municipios de `n<30`, para que Barakaldo (`n=6`) no aparezca por encima de Donostia (`n=126`); (M4) sincronizar la cifra de anuncios 759→594 con 188 y 204 en los cuatro documentos que hoy siguen diciendo 759. Estado: propuesta (delta desde base Hecho). Sin Docker; HDFS solo raw; Kafka→HDFS, nunca Kafka→Mongo; sin imputar comarcal/IDW como municipal.

## MODIFIED Requirements

### Requirement: CONCLUSION-01 — Conciliación 62/252 vs `n_precio=7` y ranking `n>=30` (M2/M3)

El sistema SHALL documentar en `data/resultados/README.md` la tabla de conciliación: 62/252 municipios con precio observable real (post re-resolución) frente a `n_precio=7` del tier agregado — los 7 son exclusivamente los municipios A+B robustos (4 Tier A + 3 Tier B) que sí publican precio municipal tras suprimir C/D; los C/D con precio no se publican. README SHALL mostrar ambas cifras juntas con esta explicación, sin esconder ninguna. El sistema MUST NOT presentar ranking, top-10 ni ordenación de esfuerzo o precios con municipios de `n_anuncios<30`: Barakaldo (`n=6`) SHALL NOT ranking verse por encima de Donostia (`n=126`) ni de ningún Tier A. Los municipios Tier C/D con `n<30` SHALL mostrarse como «n insuficiente» (con su `n` visible), nunca ocultarse ni ordenarse.

#### Scenario: Conciliación 62 vs 7 publicada en README

- GIVEN resultados regenerados por `python analysis/run_analisis_mongo.py`
- WHEN se lee `data/resultados/README.md`
- THEN consta «62/252 con precio observable» y «`n_precio=7` = A+B robusto (4 A + 3 B); C/D suprimidas» en la misma tabla
- AND `grep -n "62/252" data/resultados/README.md` → salida: ≥ 1 línea; `grep -n "n_precio=7" data/resultados/README.md` → salida: ≥ 1 línea

#### Scenario: Ranking bloqueado para `n<30`

- GIVEN el ranking de esfuerzo con Barakaldo `n=6` y Donostia `n=126`
- WHEN corre `python analysis/run_analisis_mongo.py` y se genera el ranking
- THEN Barakaldo figura como «n insuficiente» (n=6 visible) y no ordena por encima de Donostia; el top-10 solo contiene `n>=30`
- AND `python -c "import pandas as pd; d=pd.read_csv('data/resultados/ranking_esfuerzo.csv'); print(d['n_anuncios'].min())"` → salida: `>= 30` (nunca 6)

### Requirement: RESPUESTA-01 — Sincronización 759→594/188/204 en cuatro documentos (M4)

El sistema SHALL corregir la cifra stale 759 a 594 (post re-resolución + cuarentena) en los cuatro documentos: `docs/datos_finales_conclusiones_2026-11-05.md`, `docs/informe_final.md`, `data/resultados/README.md` y `presentacion/index.html`. La recarga real es 594 anuncios con 188 municipios en cero (Tier D) y Bilbao 204 como máximo; esas tres cifras (594/188/204) SHALL aparecer unidas en cada uno de los cuatro documentos, con la nota «759 era el pre-change». Ningún documento SHALL afirmar 759 como cifra vigente tras el cambio. La verificación SHALL hacerse con `grep` por documento.

#### Scenario: Los cuatro documentos dicen 594, no 759

- GIVEN Mongo recargado con `anuncios=594` vía `python -m storage.load_mongo`
- WHEN se verifican los cuatro documentos con `grep -c "594"`
- THEN cada uno contiene 594/188/204 y no contiene 759 como total vigente (`grep -c "759" docs/informe_final.md` → salida: `0`, salvo nota histórica «759 era el pre-change»)
- AND `pytest tests -q` sigue en verde tras la sincronización
