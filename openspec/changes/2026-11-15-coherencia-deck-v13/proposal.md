# Proposal — coherencia deck/memoria tras auditoría v13

## Why

La auditoría v13 encontró 3 P1 y un incumplimiento de spec, **todos de coherencia documental**,
no de motor:

- H-01: deck, guion y memoria publican 295 tests / 293 pasan; la suite tiene 300 / 298.
- H-02: el Spearman 0,988 y el 159/159 son correctos, pero solo sobre los 159 municipios con
  alquiler oficial; el universo de 160 da 0,979 y 159/160. No está declarado.
- H-03: tres columnas publicadas de esfuerzo son el mismo número y `_18_24` es 2,552× `_18_34`
  por construcción CAE. Documentado en `config/`, no en el entregable.
- H-19: `contrato-reto/spec.md:167` exige la frase Nivel/Tier ortogonales «en metodología y
  guion»; no existe en ninguno de los dos.
- A4/A7: el desglose por tipo suma 277 con titulares de 287; ratio SERPAVI 0,976 vs 0,977.

## What changes

Solo texto y un check. **No** se regenera gold, **no** se toca Mongo, **no** se renombran columnas
(riesgo 8–9 en el informe v13 para beneficio 3–4).

1. `docs/presentacion_v2/index.html` — conteo de tests, etiquetas de subconjunto, n=277,
   HDFS solo raw, Nivel/Tier.
2. `docs/presentacion_v2/guion.md` — los mismos literales + nota oral del subconjunto.
3. `docs/memoria/_cifras.json` + `docs/memoria/build.py` — `verif.tests_*` y `verif.deck_checks`
   (la memoria los resuelve por token, no se edita `memoria.md` a mano).
4. `docs/presentacion_v2/README.md` + `README.md` — 0,977 y 55/55.
5. `scripts/verificar_cifras_deck.py` — nuevo check del conteo de tests para que H-01 no vuelva.
6. Reexportar `presentacion_v2.pdf` y `memoria.pdf`.

## Impact

- Riesgo esperado 4/10: no por el texto, por la cadena HTML → PDF y por `memoria.md` generado.
- Mitigación: una sola reexportación al final, verificación con `verificar_cifras_deck.py`
  (debe seguir en 120/120 + el check nuevo), `build.py --check`, `grep` de literales viejos y
  `pytest` para descartar que algún test lea estas cifras.
- Fuera de alcance explícito: B3/B4 (regenerar gold, renombrar columnas), gate C4, subir
  procesado a HDFS (decisión: HDFS solo raw), `_hab_col`, `addopts`.
