# Auditoría v13 — 2026-11-15

**Alcance:** rúbrica literal del PDF (19 criterios) + Tema 8 §16 (7 criterios con peso) + prohibiciones
P-01…P-08 + invariantes del contrato, contra el repositorio en su estado de hoy.
**Naturaleza:** solo análisis. No se modificó código, datos, Mongo, HDFS ni Kafka.
Escrituras: únicamente este directorio de auditoría. **No** se ha hecho commit ni push.

**Instrumentos usados:** `pymupdf` y `python-docx` para extraer la rúbrica original; `ripgrep`/code search
y lectura dirigida para el código; PyMongo read-only para el estado de la base; `pytest`, gobernanza,
gate offline, `run_pipeline --check`, verificador del deck y `explain()` para la evidencia ejecutable.
No se usaron MCPs externos (ni memoria persistente): todo se apoya en ficheros y comandos reproducibles.

---

## 1. Veredicto

| Bloque | Criterios | Nota 10 | Puntos |
|---|---|---:|---:|
| BDA RA1 (sin peso en el PDF) | 4 | 3 | **34/40** |
| SBD RA1 (46,7 %) | 4 | 4 | **40/40** |
| SBD RA3 (13,3 %) | 6 | 6 | **60/60** |
| SBD RA4 (40 %) | 5 | 5 | **50/50** |
| **Total rúbrica** | **19** | **17** | **184/190 (96,8 %)** |
| **SBD ponderado** | | | **100,0 %** |
| Tema 8 §16 (aparte) | 7 | 5 | **9,40/10** |

- **Dos criterios por debajo de 10, y ninguno es de código:** C2 (HDFS procesados/recuperación) y
  C4 (E2E hasta Mongo). El primero por entorno y waiver; el segundo porque el gate vivo no verifica.
- **SBD sigue impecable (150/150).** La nota no cambia respecto a v12; lo que cambia es la calidad de
  la evidencia que la sostiene y la lista de objeciones que el tribunal puede usar.
- **Suspenso de coherencia interna:** el deck y la memoria publican **295 tests / 293 pasan** cuando la
  suite tiene **300 / 298**. No afecta a la rúbrica (los tests no puntúan), pero es la cifra que el
  tribunal ve en la diapositiva de sistema.

---

## 2. Lo que se verificó hoy (ejecución real)

| Check | Resultado |
|---|---|
| `pytest tests -o addopts="" -q` | **298 passed, 2 skipped** (300) en 7,75 s |
| `scripts/verificar_gobernanza.py` | **TODO OK** (11 pipelines en `PIPELINE_ORDER`, 0 env sin declarar) |
| `scripts/gate_extremo_a_extremo.py --offline` | **OK** + `PENDA-01` (centro solo en vivo) |
| `scripts/run_pipeline.py --check` | **rc 0**: 355 SHA raw y 183 silver, 0 errores |
| `scripts/verificar_fase_datos.py` | **rc 1**, solo `FAIL 07` conocido; huella `596e7e11…` |
| `scripts/verificar_cifras_deck.py` | **120/120** |
| `explain({'ubicacion.codigo_ine':'20069'})` | **FETCH/IXSCAN**, 126 claves / 126 docs / 126 devueltos |
| Mongo | **17 vivas + 15 `__backup`**; `anuncios` 594 con 594 `codigo_ine`; 4 índices de trabajo |
| Habitaciones | `anuncios_habitaciones_unificados` y `_bigdata`: **201/201 `_id` idénticos** |
| Gold | **24 CSV + 31 PNG** |

---

## 3. Hallazgos nuevos (delta frente a v12)

Detalle completo en `hallazgos.csv`. Los que cambian la conversación:

### P1

1. **H-01 · El deck y la memoria están una tanda por detrás en tests.**
   `index.html:756/774/808`, `guion.md:14/624/652/665` y `memoria.md:474` dicen 295/293.
   La suite real es 300/298. **El verificador del deck da 120/120 porque no comprueba esa cifra**:
   el agujero está en el propio mecanismo de control, no en la mano que escribió el número.
2. **H-02 · «Spearman 0,988 · 159/159» sin declarar el subconjunto.**
   Recomputado: sobre las 160 filas el rho es **0,9792** y 159/160 dentro de ±25 %; sobre las **159 con
   alquiler oficial**, rho **0,988** y 159/159. Ambas son ciertas, pero el deck presenta la cifra del
   subconjunto como si fuera el universo. Con la fila sin oficial delante, es indefendible tal cual.
3. **H-03 · Tres columnas de esfuerzo son el mismo número.**
   `esfuerzo_joven_pct`, `esfuerzo_joven_pct_16_29` y `esfuerzo_alquiler_pct` son idénticas en 252/252;
   `esfuerzo_joven_pct_18_24` = **2,552 ×** `_18_34` por construcción (ratio CAE 0,6311 constante).
   La derivación **sí está documentada** (`parametros_estudio.yaml:24`, `diccionario_columnas.md:13`),
   así que no es fabricación; el problema es que el CSV no lleva bandera y C17 habla de «5 indicadores».
   En defensa hay que decir «tres indicadores distintos» antes de que lo diga el tribunal.

### P2

4. **H-04 · El desglose por tipo suma 277, no 287.** 123 + 94 + 60. Diez anuncios sin `habitaciones`
   caen en el `dropna`; las medianas por tipo se calculan sobre 277 y el titular dice 287.
5. **H-05 · «30 consultas» incluye tres alias literales** de `anuncios_por_municipio`.
6. **H-06 · El gate E2E es un no-op.** `run_vivo()` devuelve `[]`; `check_lag()` devuelve la constante
   `EXPECTED_LAG == 0`; `check_duplicados()` opera sobre un `dict` sintético y lo llama «(fake)».
   C4 se apoya en la cadena real (`run_pipeline --fase mongo` + `run_analisis_mongo`), no en el gate.
7. **H-19 · La spec exige una frase que el deck no tiene.** `contrato-reto:167` obliga a tratar Nivel
   (4/54/194) y Tier (4/3/57/188) como ejes ortogonales «en metodología y guion». El guion y el deck no
   mencionan la tipología Nivel en ningún sitio. Es un requisito propio incumplido.
8. **H-07 · 248/252 filas con `estado=n_insuficiente` publican `esfuerzo_joven_pct`.** El valor es
   correcto (alquiler oficial / renta), pero un mapa coloreado por esa columna parece esfuerzo de mercado.
9. **H-08 · 0,976 vs 0,977** para el mismo 0,9765 (truncado vs half-up). Inocuo, pero es la pregunta
   que alguien hará.
10. **H-09 · `addopts = "-q"`** convierte cualquier `pytest -q` en `-qq` y suprime resumen y nodeids:
    es la causa mecánica de que las cifras de tests envejezcan.
11. **H-10 · `AGENT.md` está en `.gitignore`**: sus correcciones no viajan con el repo.

### P3

`_hab_col()` con fallback silencioso · assert tautológico en `tests/test_mongo.py:132` · `lru_cache`
contra el docstring · `data/` no versionado (solo `.gitkeep`) · colección de habitaciones duplicada ·
1 test sin assert de 255 · `FAIL 07` permanente · DAG rc 1 por un CSV no materializado.

---

## 4. Misconceptions: lo que se confirma y lo que se refuta

De 20 contrapruebas (`contrapruebas.md`), **5 refutadas** — y eso es tan importante como lo confirmado:

- El **IC95 = 87,28 repetido** en dos grupos **no es un bug**: es 1.500 € / 1.718,65 €, el punto que
  ambos bootstraps comparten. Parecía un fallo y no lo es.
- El **ratio 18-24 constante no es inventado**: está declarado como escalar CAE.
- **50 vs 64 municipios no es contradicción**: 64 con anuncio (594), 50 con precio válido (287).
- **78,6 % vs 87,3 % no es error de cálculo**: mediana de medianas municipales frente a mediana de anuncios.
- **No hay restos de Docker ni secretos versionados.**

Lo que **sí** queda: H-01, H-02, H-03, H-04, H-05, H-06 y H-19.

---

## 5. Prohibiciones e invariantes

| ID | Estado | Evidencia |
|---|---|---|
| P-01 | Cumple | Eje = alquiler Eustat; ECVI solo contraste territorial |
| P-02 | Cumple | Salario OVJ × IPC; renta INE/Eustat; población Eustat; test de no simulación |
| P-03 | Cumple | Alquiler Eustat para Euskadi |
| P-04 | Cumple | 11 pipelines multi-etapa; 8 etapas distintas |
| P-05 | **Cumple ya** | El literal «ratio 1,96; Spearman 0,18» desapareció de generadores, deck y guion; el verificador lo trata como prohibido |
| P-06 | Cumple | 100 % Python en extract/transform/storage/analysis/scripts |
| P-07 | Cumple | `.env` y `api.txt` ignorados; no hay coincidencias en el índice de git |
| P-08 | Cumple con matiz | 298 tests + gobernanza + gate + 120/120 del deck; el matiz es H-01 (el verificador no cubre el conteo) |

| Invariante | Estado |
|---|---|
| Sin Docker | **Cumple** (solo aparecen las frases «sin Docker») |
| HDFS solo raw | Cumple |
| Kafka→HDFS, nunca Kafka→Mongo | Cumple |
| Sin imputar comarcal/IDW como municipal | Cumple (`metodo_imputacion`, `is_imputed`) |
| Nivel y Tier ortogonales **en metodología y guion** | **No cumple** (H-19): está en la spec, no en el entregable |

---

## 6. Riesgo de defensa, ordenado por probabilidad × daño

| Riesgo | Probabilidad | Daño | Mitigación |
|---|---|---|---|
| «¿Cuántos tests?» con 295 en pantalla | Alta | Medio | Cambiar 5 literales y reexportar PDF |
| «¿0,988 sobre cuántos?» | Media | Alto | Añadir «159 con alquiler oficial» |
| «Tu tabla por tipo suma 277» | Media | Medio | Declarar n=277 |
| «Esos tres indicadores son el mismo número» | Media | Alto | Decir «tres indicadores» y la derivación CAE |
| «Demuéstrame el E2E» | Media | Alto | No vender el gate como E2E; enseñar la cadena y la huella |
| «HDFS procesados» | Alta | Medio | Waiver + 353 objetos + 404 |
| «Nivel y Tier» | Baja | Bajo | Línea en el guion |

---

## 7. Plan mínimo antes del lunes (no ejecutado)

Ordenado por coste/beneficio. **Nada de esto se ha tocado.**

1. **5 literales de tests** (deck, guion, memoria) + reexportar el PDF del deck. ~20 min.
2. **Añadir el check del conteo de tests** a `verificar_cifras_deck.py` para que no vuelva a envejecer.
3. **Etiquetar el subconjunto** del Spearman (159 con oficial) en deck y guion.
4. **Declarar n=277** en la tabla por tipo (pie de figura o `caveat`).
5. **Renombrar o documentar** `esfuerzo_joven_pct` como esfuerzo sobre alquiler oficial.
6. **Añadir la frase Nivel/Tier** al guion (una línea) o rebajar la spec.
7. **Etiquetar el gate** como conectividad y añadir un check de datos si hay tiempo.

Todo lo demás (H-04 a H-18) es deuda que no mueve la nota y sí puede esperar al post-evaluación.

---

## 8. Conclusión

El sistema **cumple la rúbrica a nivel 10 en 17 de 19 criterios** y el bloque SBD está al 100 % ponderado.
Lo que falla no es el motor: es el **control de coherencia entre lo que el sistema hace y lo que el deck
dice que hace**. Tres de los cuatro P1 son de esa familia (tests, Spearman, indicadores duplicados), y el
cuarto (H-19) es una spec que exige algo que el entregable no dice.

La auditoría también ha refutado cinco sospechas, incluida una que parecía un bug de bootstrap. Eso es
la señal de que el sistema está mejor de lo que sus propios documentos hacen parecer.

**Nota final:** 184/190 (96,8 %) en la rúbrica, SBD 100 %, Tema 8 9,40/10.
**P0: 0 · P1: 3 · P2: 8 · P3: 8.** Ver `hallazgos.csv`, `gaps.md` y `cobertura.md`.

---

## 9. Estado tras la aplicación (2026-11-15, misma fecha)

Con autorización del usuario se aplicó la recomendación 1+2+3 en el change
`openspec/changes/2026-11-15-coherencia-deck-v13/`:

- **Cerrados:** H-01 (con guardarraíl nuevo en el verificador), H-02, H-08, H-19 y el 53/53 del
  README de deck.
- **Mitigados sin tocar datos:** H-03 y H-04, documentados en guion y deck.
- **Abiertos:** H-05, H-06, H-07, H-09, H-10 y H-11…H-18.

Verificación: **121/121** en el verificador (antes 120/120 con los literales viejos
hardcodeados), **298 passed / 2 skipped**, PDF de 32 y 27 páginas sin rastro de 295/293, y
huella gold **983fa53f…** intacta. Las notas de la rúbrica **no cambian**: 184/190, SBD 100 %,
Tema 8 9,40/10. Lo que cambia es que las tres objeciones más probables ya no existen.

## Anexo — comandos ejecutados

```bash
pytest tests -o addopts="" -q                      # 298 passed, 2 skipped
python scripts/verificar_gobernanza.py             # TODO OK
python scripts/gate_extremo_a_extremo.py --offline # OK + PENDA-01
python scripts/run_pipeline.py --check             # rc 0, 355 / 183
python scripts/verificar_fase_datos.py             # rc 1, solo FAIL 07
python scripts/verificar_cifras_deck.py            # 120/120
# PyMongo: list_collection_names, count_documents, list_indexes, explain()
# pandas: perfiles de los 24 CSV, ratios y medianas del ledger
# pymupdf / python-docx: extracción literal de la rúbrica
```
