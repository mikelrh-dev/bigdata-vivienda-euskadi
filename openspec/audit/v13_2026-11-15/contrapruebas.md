# Contrapruebas — lo que intenté refutar y cómo quedó

Regla: ninguna nota alta ni ningún P1 se publica sin un intento explícito de tirarlo abajo.
Aquí están los intentos, incluidos los que **no** confirmaron el defecto.

| # | Hipótesis | Contraprueba ejecutada | Veredicto |
|---|---|---|---|
| X-01 | «El ratio 18-24 es inventado» | `ratio = renta_joven_18_24 / renta_joven` en 252 filas | **FALSO**: 0,6311 constante, pero declarado en `config/parametros_estudio.yaml:24` («escalar CAE») y en `diccionario_columnas.md`. Es estimación documentada, no fabricación |
| X-02 | «El esfuerzo 18-24 aporta información propia» | `ratio = esfuerzo_18_24 / esfuerzo_18_34` | **CONFIRMADO**: 2,552 constante. Deriva de X-01; no es un indicador independiente |
| X-03 | «Tres columnas de esfuerzo son la misma» | `np.allclose` entre `esfuerzo_joven_pct`, `_16_29`, `esfuerzo_alquiler_pct` | **CONFIRMADO**: idénticas en las 252 filas |
| X-04 | «El IC95 superior 87,28 repetido en dos grupos es un bug de bootstrap» | 1500 / 1718,65 × 100 | **FALSO**: 87,278. Ambos grupos contienen el punto 1.500 €, que es el percentil 97,5 del bootstrap. Coincidencia explicada, no error |
| X-05 | «287 anuncios válidos, pero el desglose por tipo no cuadra» | `sum(n_anuncios)` de `esfuerzo_por_tipo_nivel_anuncio_2026.csv` | **CONFIRMADO**: 277. Diez anuncios sin `habitaciones` caen en el `dropna` |
| X-06 | «La cobertura de 50 municipios contradice los 64 con anuncio» | Cruce de `cobertura_representatividad_2026.csv`, `mongo_tier_confianza.csv` y `mongo_esfuerzo_por_municipio.csv` | **FALSO como contradicción**: 64 con anuncio (594), 50 con precio válido de la capa 2026 (287). El deck lo distingue («64 municipios con anuncio / 287 válidos en 50 municipios»). Es trampa de lectura, no error |
| X-07 | «El p-valor del 78,6 % está mal calculado» | Recalculo de la mediana municipal desde `mongo_esfuerzo_por_municipio.csv` y comparación con `validacion_portales_2026.csv` (50 filas) | **FALSO**: 78,55 sale de las 50 medianas municipales; 87,3 de los 287 anuncios. Ambas correctas en su unidad, y el deck lo explica |
| X-08 | «El Spearman 0,988 del deck es falso» | Recomputado sobre 160 y sobre los 159 con alquiler oficial | **PARCIAL**: 0,988 existe, pero solo sobre 159 con oficial; el universo de 160 da 0,979 y 159/160 dentro de ±25 %. El deck no declara el subconjunto → H-02 |
| X-09 | «El deck está sincronizado con los tests» | `pytest -o addopts="" -q` vs literales del deck | **CONFIRMADO el desfase**: 300/298 real vs 295/293 publicado |
| X-10 | «El verificador del deck detectaría el desfase» | `verificar_cifras_deck.py` → 120/120; grep de comprobaciones | **CONFIRMADO el hueco**: no hay check del número de tests |
| X-11 | «El gate vivo demuestra el E2E» | Lectura de `run_vivo`, `check_lag`, `check_duplicados` | **CONFIRMADO**: no-op, constante y simulación |
| X-12 | «Los 594 anuncios tienen código INE» | `count_documents({'ubicacion.codigo_ine':{'$exists':False}})` | **FALSO**: 0 sin código; 594/594 con código |
| X-13 | «El índice no se usa» | `explain()` de `{'ubicacion.codigo_ine':'20069'}` | **FALSO**: `FETCH/IXSCAN`, 126 claves / 126 docs examinados |
| X-14 | «Las dos colecciones de habitaciones difieren» | Comparación de `_id` | **FALSO**: 201/201 idénticos, delta 0 |
| X-15 | «Hay secretos versionados» | `.gitignore` y `git ls-files` | **FALSO**: `.env` y `api.txt` ignorados; sin coincidencias en el índice |
| X-16 | «Los 41 scripts de extracción son reales» | `extract/` con cliente común, retry y `main_ingest` | **FALSO el escepticismo**: la extracción está automatizada de verdad |
| X-17 | «El deck y la memoria tienen cifras distintas de cobertura» | 50/252, 19,84 %, 71,21 %, 287 | **FALSO**: coinciden los tres artefactos |
| X-18 | «La suite tiene tests de humo» | AST sobre 255 funciones test | **CASI FALSO**: solo 1 sin assert (`test_con_frozen_ok`); el resto comprueba |
| X-19 | «Los datos están en el repo» | `git ls-files data/raw` | **CONFIRMADO**: solo `.gitkeep`; el corpus es externo |
| X-20 | «Quedan restos de Docker» | grep en README, config, `.env.example` | **FALSO**: solo frases «sin Docker» |
