# Verify report — coherencia deck/memoria v13

**Fecha:** 2026-11-15 · **Modo:** SDD aplicado (texto + un check). **Sin cambios en datos, Mongo,
HDFS ni Kafka.** `git status data/` → 0 ficheros.

## 1. Ficheros tocados

| Fichero | Cambio |
|---|---|
| `docs/presentacion_v2/index.html` | 295/293→300/298 (3 sitios) · «Spearman · 159 con alquiler oficial» · nota n=277 · «HDFS · solo raw» · «Nivel 4/54/194: ejes ortogonales» |
| `docs/presentacion_v2/guion.md` | 295/293→300/298 (4 sitios) · subconjunto SERPAVI en B7 · Nivel/Tier en B8 · nota de indicadores derivados en B2 · «solo raw» en cabecera |
| `docs/presentacion_v2/README.md` | gold 53/53→55/55 · SERPAVI 0,977 / 0,988 / 159 con oficial |
| `docs/presentacion_v2/presentacion_v2.pdf` | reexportado (Chrome headless) |
| `docs/memoria/_cifras.json` | `verif.tests_*` 300/298/2, `verif.deck_checks` 120, fuente 2026-11-15 |
| `docs/memoria/build.py` | mismos valores por defecto |
| `docs/memoria/memoria.{md,html,docx,pdf}` | regenerados por `build.py` |
| `scripts/verificar_cifras_deck.py` | `_test_run()`: el check de tests ejecuta la suite en vez de comparar contra literales |

## 2. Verificación (D1–D7)

| # | Check | Resultado |
|---|---|---|
| D1 | `verificar_cifras_deck.py` | **121/121**, 0 FALLA (antes 120/120 con 295 y 293 hardcodeados) |
| D2 | `build.py --check` | **OK** 9 capítulos, tokens y figuras resueltos |
| D3 | grep `295 tests\|293 pasan\|295 recogidos\|115/115\|53/53\|0,976` | **0 coincidencias** en README, deck, guion, memoria y capítulos |
| D4 | `pytest tests -o addopts="" -q` | **298 passed, 2 skipped** en 7,63 s |
| D5 | PDF deck | **32 páginas** · `295`: 0 · `293`: 0 · `300`: 3 · `298`: 2 · `277`: 1 · `ortogon`: 1 |
| D6 | PDF memoria | **27 páginas** · `295`: 0 · `293`: 0 · `300`: 2 · `298`: 1 |
| D7 | `run_analisis_mongo.py --salida $TEMP/gold_v13 --sin-sync-deck` | **rc 0** · 40 ficheros · huella **983fa53fb5c61f37f526f4f27a9ffbc408a633c17c3a0cdf9d17771b00668b9e** |

## 3. Contraprueba del guardarraíl

El check nuevo se probó contra el fallo real: con el deck en 295 el verificador daba **FALLA**
en `tests` y `tests pasan`; con el deck en 300/298 da 121/121. Es decir, **H-01 ya no puede volver
en silencio**.

## 4. Hallazgos de la auditoría v13

| ID | Estado |
|---|---|
| H-01 tests | **Cerrado** + guardarraíl |
| H-02 Spearman sin subconjunto | **Cerrado** (deck, guion, README) |
| H-03 indicadores derivados | **Mitigado** (documentado en B2; no se renombran columnas: riesgo 9) |
| H-04 desglose 277 | **Mitigado** (nota en el deck; no se regenera el gold: riesgo 8) |
| H-08 0,976 vs 0,977 | **Cerrado** (unificado a 0,977) |
| H-19 Nivel/Tier | **Cerrado** (guion B8 + deck B2, con 4/54/194 verificado en Mongo) |
| Extra: `docs/presentacion_v2/README.md` «Gold 53/53» | **Cerrado** (55/55) |
| H-05, H-06, H-07, H-09, H-10, H-11…H-18 | **Abiertos** (deuda declarada, sin impacto en nota) |

## 5. Riesgos residuales

1. `memoria.docx` y `memoria.html` cambian como binario: el diff no es revisable línea a línea.
2. El verificador tarda ~8 s más porque ejecuta la suite. Si pytest no está disponible, **omite**
   los checks de tests en vez de fallar (no rompe CI sin dependencias).
3. Los PDF se reexportaron con Chrome headless: se conserva el número de páginas (32 y 27), pero
   el contenido visual no se ha revisado diapositiva a diapositiva.
4. Rollback: `git checkout -- <fichero>`; los PDF anteriores están en `%TEMP%` (`deck_prev.pdf`,
   `memoria_prev.pdf`).

## 6. Lo que NO se hizo (por decisión)

Regenerar el CSV por tipo (H-04 en datos), renombrar `esfuerzo_joven_pct` (H-03 en datos), gate
C4, subir procesado a HDFS (HDFS solo raw por diseño), `_hab_col`, `addopts`, unificar colecciones
de habitaciones. Todo ello con beneficio ≤ 4 y riesgo ≥ 6 en el informe v13.
