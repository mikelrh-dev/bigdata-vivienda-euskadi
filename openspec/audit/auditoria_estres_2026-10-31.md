# Auditoría de estrés del proyecto — 2026-10-31

**Alcance:** todo lo construido hasta la fecha (extracción, raw, silver, features, gold, tests, specs, documentación).
**Modo:** auditoría con evidencia ejecutable. Cada cifra de este informe sale de una sonda reproducible, no de leer código de memoria.
**Revisión:** **rev. 2 (2026-10-31b)**. Se re-midieron los ejes E4/E5 contra el manifest **canónico** (`docs/raw_manifest_sha256.txt`), se re-contaron los ceros y se añadieron tres hallazgos nuevos (§3.2 H-04b y H-16, §4.3 H-19). Siete afirmaciones de la rev. 1 eran incorrectas o estaban mal atribuidas: están listadas en §10 con la corrección y la evidencia. Donde la rev. 1 y la rev. 2 discrepan, manda la rev. 2.

**Artefactos de la auditoría:**

| Artefacto | Ruta |
|---|---|
| Batería de sondas (solo lectura) | `openspec/audit/estres/sondas_estres_2026-10-31.py` |
| Salida cruda de las sondas | `openspec/audit/estres/resultados_sondas_2026-10-31.json` |
| Este informe | `openspec/audit/auditoria_estres_2026-10-31.md` |
| Plan de arreglos para esta fase | `openspec/audit/plan_10_10_datos_2026-10-31.md` |

**Reproducir:**

```bash
.venv/Scripts/python.exe openspec/audit/estres/sondas_estres_2026-10-31.py
.venv/Scripts/python.exe -m pytest -q          # 66 passed
```

**Fuentes de verdad usadas:** `openspec/specs/contrato-reto/spec.md`, `openspec/project.md`, `RETO 1Evaluacion SBD-BDA.pdf` (vía contrato), datos en `data/{raw,procesado,resultados}`, código en `extract/` y `transform/`, tests en `tests/`.

**Inventario medido:** `data/raw` 319 ficheros (127 CSV, 101 HTML, 60 JSON, 14 ZIP, 6 XLSX); `data/procesado` 113; `data/resultados` 19 (13 PNG, 3 HTML).

---

## 0. Veredicto en una página

El proyecto está **bien construido en la capa de datos y mal cubierto en la capa de contrato**. No hay corrupción estructural: claves foráneas limpias, percentiles coherentes, deduplicación efectiva, 66 tests en verde, sin credenciales versionadas. Pero hay cuatro problemas que **sí pueden invalidar la conclusión del reto**, y ninguno aparece en las auditorías previas:

1. **La respuesta a "¿qué municipios son mejores?" no es robusta.** De los 20 municipios con menor esfuerzo de alquiler, **17 tienen la renta imputada por IDW** (no oficial) y **20 de 20 tienen menos de 5 anuncios** (17 tienen cero). El ranking lo decide la imputación, no el mercado.
2. **Conviven dos definiciones incompatibles de "esfuerzo joven"** en dos tablas distintas: correlación de rangos 0,53 y **solapamiento de solo 1 municipio en el top-20**. Además una de las dos usa un salario constante autonómico, que por construcción **no puede ordenar municipios**.
3. **Hay ceros que significan "sin dato"**, no "cero", y el pipeline los convierte en datos plausibles. Usansolo (48916) figura con 0,0 % de paro y 0,0 % de afiliación; el flag `tasa_paro_valida` lo da por válido porque solo comprueba nulos. Peor: su tasa de desempleo juvenil se calcula bien (**13 parados / 152 activos = 8,6 %**) y luego **se anula por el clip de sanidad** contra `tasa_paro_lanbide_pct × 4 = 0`, porque el clip compara contra un cero. Lo publicado es 0,0 %.
4. **El pipeline no se reproduce desde cero.** **18 de los 39 scripts de `transform/` no están en `run_all.py`**, incluidos los productores de `alquiler_municipal_completo.csv` y `analisis_variables_base.csv`, que son entradas de scripts sí orquestados. Hoy funciona porque esos CSV existen de ejecuciones manuales: borrar `data/procesado/` deja el pipeline roto.

Además, **11 de los 18 criterios de la rúbrica no tienen implementación ni test** (HDFS, Kafka, integración, modelado, PyMongo, consultas, agregación, gráficos desde PyMongo, transformaciones en MongoDB, interpretación y conclusiones). Los specs lo declaran como "Pendiente" —hay honestidad documental— pero los 66 tests en verde dan una sensación de cobertura que el contrato no respalda: el único test llamado `P-08` comprueba que el contrato *enumera* criterios, no que estén cubiertos.

**Puntuación global: 5,4 / 10 como proyecto del reto** (media simple de los nueve ejes de §1). Como **pipeline de datos: 7,5 / 10** — 8/10 de realismo estadístico pero 6/10 de reproducibilidad. El 5,5 de la rev. 1 no reproducía la media de la tabla; el `readiness_report_2026-10-29.md` puntuaba 8,5 / 10 midiendo solo realismo, no contrato ni robustez del ranking.

---

## 1. Método y parámetros de estrés

Se evaluaron nueve ejes. Para cada uno se define qué se estresó y con qué resultado.

| # | Eje | Qué se estresó | Nota | Evidencia |
|---|---|---|---:|---|
| E1 | Contrato / rúbrica | 18 criterios frente a implementación y tests observables | **3 / 10** | §2 |
| E2 | Integridad de datos | claves, FKs, percentiles, duplicados, rangos | **8 / 10** | §3.1 |
| E3 | Validez analítica | sensibilidad del ranking a decisiones metodológicas | **3 / 10** | §3.2 |
| E4 | Trazabilidad / metadata | metadata exigida por FORMATO-01 en 60 JSON y 127 CSV | **5 / 10** | §4.1 |
| E5 | Inmutabilidad de raw | manifest canónico de hashes frente a los 316 ficheros reales | **8 / 10** | §4.2 |
| E6 | Reproducibilidad | orquestación, idempotencia, nombres volátiles, manifest de silver | **4 / 10** | §4.3 |
| E7 | Robustez de código | lectura de CSV, excepciones, fallbacks, asserts | **6 / 10** | §4.4 |
| E8 | Escala | coste de lectura y algoritmos O(n²) | **7 / 10** | §4.5 |
| E9 | Documentación vs realidad | cifras de `project.md` y audits previas frente a medición | **5 / 10** | §4.6 |

Cambios respecto a la rev. 1: **E4 4→5** (los 60 JSON sí tienen `fuente` y fecha bajo algún alias; el defecto real es la ausencia de esquema único y de `n_registros`), **E5 3→8** (el manifest canónico está completo y correcto; el roto es una copia legacy), **E6 5→4** (18 scripts sin orquestar: el pipeline no se reconstruye desde cero).

Escenarios adversos probados (resultado: resiste / falla):

| Escenario | Resultado |
|---|---|
| Municipio nuevo sin serie histórica (Usansolo) | **Falla**: 0,0 % de paro válido, y su 8,6 % real de desempleo juvenil se anula por el clip de sanidad |
| Fila sin `codigo_ine` con ceros a la izquierda (`01001`) | Resiste en la mayoría: `zfill(5)` tras leer; 42 de 84 `read_csv` sin `dtype=str` dependen de ese parche |
| CSV con separador `;` o Latin-1 | **Resiste**: `sep=";"` explícito y `encoding="latin-1"` donde toca |
| Reejecutar un transform aislado fuera de orden | **Falla**: `calcular_renta_joven.py` reescribe `dim_municipios_enriquecido.csv` y borra 27 columnas |
| Pipeline desde cero (borrar `data/procesado` y lanzar `run_all.py`) | **Falla**: 18 scripts fuera del orquestador, entre ellos los productores de dos entradas clave |
| API Eustat caída o parseo fallido | **Falla en silencio**: ratios caen a constantes hardcodeadas (1599/8156/20109/28170) |
| Raw modificado a mano | **Detectado**: el manifest canónico cubre 316/316 ficheros con 0 hashes discrepantes. La copia legacy de `data/raw/` sí está rota (47 entradas, 5 obsoletas) y es una trampa para cualquier verificación manual |
| Duplicados de anuncio entre portales | Resiste: 0 duplicados por `(portal, id)` y 0 por `property_fingerprint` |
| Volumen ×10 (≈7.600 anuncios) | Sin riesgo de memoria; sí `iterrows` en `dim_municipios.py` y distancias O(n²) |

---

## 2. Cobertura del contrato (E1) — 3 de 18 criterios verificables

| # | Criterio (nivel 10) | Requisito | Implementación | Test observable | Estado |
|---|---|---|---|---|:--:|
| 1 | Extracción API + scraping | EXTRACCION-01/02 | `extract/` (35 scripts) | `test_contrato` + `test_crudos` | ✅ |
| 2 | HDFS originales/procesados/recuperación | HDFS-01 | **no existe** | ninguno | ❌ |
| 3 | Kafka productor + consumidor | KAFKA-01 | **no existe** | ninguno | ❌ |
| 4 | Integración hasta MongoDB | INTEGRACION-01 | **no existe** | ninguno | ❌ |
| 5 | Modelado MongoDB justificado | MODELO-01 | **no existe** | ninguno | ❌ |
| 6 | PyMongo CRUD + comprobación | PYMONGO-01 | **no existe** | ninguno | ❌ |
| 7 | Consultas con anidados/arrays | CONSULTAS-01 | **no existe** | ninguno | ❌ |
| 8 | Aggregation ≥4 etapas | AGREGACION-01 | **no existe** | ninguno | ❌ |
| 9 | ≥3 tipos de gráfico | GRAFICOS-01 | 13 PNG + dashboards HTML | ninguno (no hay test de figuras) | ⚠️ |
| 10 | Gráficos desde consultas PyMongo | DATOS-PYMONGO-01 | **no existe** (DuckDB sobre CSV) | ninguno | ❌ |
| 11 | Títulos/unidades/leyendas | PRESENTACION-01 | dashboards HTML | ninguno | ⚠️ |
| 12 | Interpretación de resultados | INTERPRETACION-01 | **no hay informe** | ninguno | ❌ |
| 13 | Salarios/población/indicadores | COMPLEMENTARIOS-01 | Eustat/INE/OVJ/Lanbide | `test_complementarios_*` | ✅ |
| 14 | Formato JSON/CSV + metadata | FORMATO-01 | parcial (ver §4.1) | 1 solo fichero comprobado | ⚠️ |
| 15 | Limpieza incompletos/duplicados/erróneos | LIMPIEZA-01 | pandas (no PyMongo) | 1 fichero, 1 columna | ⚠️ |
| 16 | Transformaciones en MongoDB | TRANSFORM-01 | **no existe** | ninguno | ❌ |
| 17 | Resultado final: municipios y por qué | CONCLUSION-01 | **no hay informe** | ninguno | ❌ |
| 18 | Todo en Python | PYTHON-01 | ✅ | `test_p06` (trivial: extensión `.py`) | ✅ |

**3 ✅ · 4 ⚠️ · 11 ❌.** Con la rúbrica del PDF (todo o nada al nivel de 10 puntos), el proyecto acredita hoy **3 criterios completos** de 18.

**Nota sobre la fase actual:** los criterios 1, 13, 14, 15 y 18 son los únicos que se pueden cerrar sin HDFS, Kafka ni MongoDB. El techo alcanzable en "obtención de datos + transformación" es **5 de 18**; el plan para llegar a 10 en esos cinco está en `plan_10_10_datos_2026-10-31.md`.

Tres tests merecen mención porque **dan verde sin medir el criterio**:

| Test | Qué comprueba de verdad | Por qué no basta |
|---|---|---|
| `test_formato_metadatos_en_json` | metadata de **un** fichero (`anuncios_fotocasa.json`) | 2 de 60 JSON no tienen bloque `metadata`, 9 no tienen fecha, 6 no tienen recuento y 40 no tienen `url`; el test mira uno y pasa |
| `test_limpieza_nulos_explicitos` | `superficie_m2 != 0` en el mismo fichero | no detecta ceros-como-nulo en `tasa_paro_lanbide_pct` ni `ocupación > actividad` |
| `test_p08_contrato_cubre_los_criterios` | que el texto del contrato enumera los 12 criterios | es circular: P-08 prohíbe marcar cubierto sin verificación, y el test no verifica ninguno |

No es un fallo de los tests como código: es que **el conjunto mide el pipeline, no el contrato**. Con 66 verdes y 11 criterios sin implementar, el semáforo induce a error.

---

## 3. Datos: lo que está bien y lo que invalida conclusiones

### 3.1 Integridad estructural — sólida (E2: 8/10)

| Comprobación | Resultado |
|---|---|
| `dim_municipios`: 252 filas, 252 códigos únicos, longitud 5 | ✅ |
| Prefijos provinciales | 01→51, 20→88, 48→113 |
| FKs `alquiler_municipal_completo` → dim | 0 huérfanos, 0 sin código |
| FKs `analisis_variables_base` → dim | 0 huérfanos |
| FKs `distancias_capitales_252` → dim | 0 huérfanos |
| FKs `anuncios_unificados` → dim | 0 huérfanos, pero **169 municipios del dim sin ningún anuncio** |
| Percentiles de alquiler (`p25 ≤ mediana ≤ p75`) | **0 violaciones** en renta €/m², cuantía €/mes y superficie |
| Negativos/ceros/nulos en percentiles de alquiler | 0 / 0 / 0 |
| Duplicados de anuncio por `(portal, id_anuncio)` | 0 |
| Duplicados por `property_fingerprint` | 0 |
| Cobertura de alquiler | 159 oficiales + 93 IDW_5_vecinos = 252 |

**Sobre los 252 municipios:** el delta frente a los 251 "clásicos" de Euskadi **no es un duplicado**. Es Usansolo (48916), segregado de Galdakao y municipio desde 2023; aparece en el Eustat de alquiler territorial y en Udalmap. Verificado contra las fuentes, no es un error. (Bizkaia pasa de 112 a 113 por este motivo.)

**Importante:** integridad estructural ≠ corrección semántica. Las FKs y los percentiles están limpios, pero dos columnas derivadas son inservibles (§3.2 H-04b y H-16). Eso no se detecta comprobando rangos; se detecta comprobando **identidades aritméticas entre campos**.

### 3.2 Validez del ranking — el hallazgo más grave (E3: 3/10)

**H-01 (crítico). El top-20 de "mejores municipios" está construido sobre renta imputada y sin mercado observado.**

Ordenando los 252 municipios por `esfuerzo_renta_joven` (menor = mejor):

| Métrica del top-20 | Valor |
|---|---|
| Con renta IDW (no oficial) | **17 / 20** |
| Sin ningún anuncio | **17 / 20** |
| Con menos de 5 anuncios | **20 / 20** |

Los cinco primeros son Gabiria, Garai, Laukiz, Gamiz-Fika y Murueta: entre **33 y 136 jóvenes de 16-24 años estimados** cada uno, y una renta de alquiler que es media ponderada de municipios vecinos, no un precio observado. Presentar eso como "dónde puede emanciparse un joven" es defender una conclusión que los datos no sostienen. No es un bug de código: es un problema de diseño analítico que el informe debe resolver explícitamente (excluir IDW del ranking, o publicar dos rankings y etiquetar la fiabilidad).

**H-02 (crítico). Dos definiciones de esfuerzo joven que no coinciden.**

| Columnas comparadas | Diferencia mediana | Diferencia máxima | Correlación de rangos | Top-20 en común |
|---|---:|---:|---:|---:|
| `analisis_variables_base.esfuerzo_renta_joven × 100` vs `dim_municipios_enriquecido.esfuerzo_ovj_individual_pct` | 3,9 pp | 26,3 pp | **0,53** | **1 / 20** |
| `esfuerzo_renta_hogar × 100` vs `esfuerzo_alquiler_hombres_pct` | 12,6 pp | 30,5 pp | 0,82 | — |

Caso claro: Laukiz sale 26 % por una vía y 52 % por la otra. La primera usa renta joven estimada (renta municipal × ratio fiscal); la segunda un salario OVJ plano de 1.381 €.

**El problema no es la discrepancia, es qué puede hacer cada una.** `esfuerzo_ovj_individual_pct` divide el alquiler municipal entre una **constante autonómica**: su ordenación es, matemáticamente, la ordenación del alquiler. No aporta información municipal sobre capacidad de pago, pero al llamarse "esfuerzo" compite con la otra en el informe. Ambas son defendibles por separado; **tener las dos sin declarar cuál manda no lo es**, y la que se elija cambia el top-20 casi entero (1 municipio en común de 20).

**H-03 (alto). `n_anuncios` no cuenta los anuncios que se analizan.**

`dim_municipios.n_anuncios` se calcula en `transform/dim_municipios.py:155-178` leyendo los CSV **crudos** (`anuncios_fotocasa.csv`, `anuncios_pisos.csv`, `anuncios_realtyapi.csv`) con `iterrows`, antes de deduplicar y de marcar outliers.

| Fuente | Valor |
|---|---:|
| Filas crudas de los 3 CSV (471 + 235 + 139) | **845** |
| Suma de `n_anuncios` en el dim (2 filas sin `codigo_ine`) | **843** |
| Filas reales de `anuncios_unificados.csv` | **759** (428/247/84) |
| Desviación | **+11 %** |

Se usa como umbral en `transform/generar_dashboard_visual.py:101` (`WHERE n_anuncios >= 30`) y en `dim_municipios.py:207-216` para asignar `tipologia_mercado`. El sobreconteo **no es uniforme** (realtyapi pasa de 139 a 84, fotocasa de 471 a 428), así que no solo infla el total: **cambia la clasificación de municipios concretos** en el umbral de 30.

Restricción de orden que hay que respetar al arreglarlo: `dim_municipios.py` corre en el grupo `dim_municipios`, **antes** de `unificacion`, cuando `anuncios_unificados.csv` todavía no existe. No se puede resolver dentro de `dim_municipios.py`; hace falta un paso posterior declarado (WP-03 del plan).

**H-04 (alto). Ceros que significan "sin dato".**

| Municipio | `tasa_paro_lanbide_pct` | `afiliacion_ss_16_24_pct` | `tasa_desempleo_juvenil_real_pct` | `tasa_paro_valida` |
|---|---:|---:|---:|:--:|
| Usansolo (48916) | 0,00 | 0,00 | 0,00 | **True** |
| Aramaio (01003) | 0,00 | (no cero) | 0,00 | True |
| Gaintza (20037) | 0,00 | (no cero) | nulo | True |

El 0,0 de paro viene de la fuente (Udalmap lo publica así para Usansolo), no de una conversión del pipeline. El 0,0 de **afiliación** también es de fuente. El problema es qué hace el pipeline con ellos:

- `transform/corregir_empleo.py:50`: `tasa_paro_valida = notna()`. **Valida como buena una tasa de paro del 0 %** en un municipio que solo existe como tal desde 2023.
- El mínimo real no nulo de `tasa_paro_lanbide_pct` es **0,5 %**. Un 0,00 exacto en 3 de 252 municipios (Aramaio, Gaintza, Usansolo) es un artefacto de municipios con muy pocos activos, no una medición.

**H-04b (alto, nuevo en rev. 2). El clip de sanidad destruye un valor correcto.**

`transform/generar_analisis_variables_base.py:101-105` limita la tasa de desempleo juvenil a `4 × tasa_paro_lanbide_pct`:

```python
cap = base["tasa_paro_lanbide_pct"] * 4
base.loc[m, "tasa_desempleo_juvenil_real_pct"] = base[...].clip(upper=cap[m])
```

Con `tasa_paro_lanbide_pct = 0` el techo es **0**, y un valor calculado correctamente se anula:

| Municipio | parados 16-24 | activos 16-24 | cálculo correcto | cap (`tasa_paro × 4`) | publicado |
|---|---:|---:|---:|---:|---:|
| Usansolo (48916) | 13 | 151,7 | **8,57 %** | 0,0 | **0,00 %** |
| Aramaio (01003) | 1 | 54,8 | 1,82 % | 0,0 | **0,00 %** |

Ocho municipios acaban con 0 % exacto de desempleo juvenil. Seis son aritméticamente correctos (`paro_joven_menores_25 = 0`: cero parados registrados). **Dos son un bug del pipeline**, y no un dato de la fuente: el pipeline calculó 8,57 % y lo tiró a la basura con el clip.

Efecto analítico doble: cualquier índice que premie el empleo juvenil colocará a Usansolo el primero, y el mismo cero que se marca como inválido alimenta la tasa que se publica como válida. Un solo arreglo (tratar el 0 como nulo en `corregir_empleo.py`) corrige los dos síntomas, porque el cap pasa a ser `NaN` en lugar de `0`.

**H-05 (medio). Dos tablas "gold base" con métricas duplicadas y unidades distintas.**

`analisis_variables_base.csv` (38 columnas) expresa el esfuerzo como **fracción 0–1** (`esfuerzo_renta_joven = 0,49`); `dim_municipios_enriquecido.csv` (65 columnas) lo expresa como **porcentaje 0–100** (`esfuerzo_ovj_individual_pct = 49,4`). Misma realidad, dos convenciones, dos ficheros, sin un campo que declare unidades. Un `×100` olvidado en el informe produce un error de dos órdenes de magnitud.

**H-16 (alto, nuevo en rev. 2). `brecha_ocupacion_actividad_pct` es semánticamente imposible en 248 de 252 municipios.**

`transform/corregir_empleo.py:48` define:

```python
df["brecha_ocupacion_actividad_pct"] = tasa_ocupacion_pct - tasa_actividad_pct
```

| Métrica | Valor |
|---|---|
| Municipios con `ocupación > actividad` | **248 / 252** |
| Mediana de la brecha | **+5,05 pp** |
| Rango | −1,73 a +18,17 pp |

Por definición, `ocupados ⊆ activos`, luego la brecha debería ser ≤ 0 y es igual a `−tasa_paro` en valor absoluto. Que sea **sistemáticamente positiva** significa que las dos tasas de Udalmap no comparten base (edad o denominador), y por tanto la columna no mide ninguna brecha: mide la discrepancia entre dos indicadores distintos. Se escribe en `udalmap_empleo_corregido.csv` con un nombre que invita a usarla en el informe.

Ningún test lo detecta porque los tests comprueban rangos (`0-100`), no identidades. Arreglo: eliminar la columna, o recalcularla con las dos tasas en la misma base y documentar las bases en el spec.

---

## 4. Proceso, trazabilidad y robustez

### 4.1 Metadata FORMATO-01 (E4: 5/10)

**H-06 (alto, reformulado en rev. 2). La metadata existe pero no tiene esquema.**

La rev. 1 afirmaba "47 de 60 JSON incumplen". **Falso**: los 60 tienen `metadata` bajo `{metadata, datos}` salvo dos excepciones, y todos usan `fecha_extraccion` como fecha. Lo que sí está mal es que cada script inventó su propio vocabulario:

| Campo exigido por FORMATO-01 | Situación medida |
|---|---|
| `fuente` | 59 / 60. Falta en `b5m_catalogo.json` |
| fecha | 51 / 60 (bajo `fecha_extraccion`). 9 sin ningún alias de fecha |
| número de registros | 54 / 60. 6 sin ningún recuento |
| bloque `metadata` | 58 / 60. Faltan `emancipacion_juventud_resumen.json` y `ovj_salario_joven_2024.json` |
| `url` de la fuente | 20 / 60. **40 sin URL**, lo que rompe la trazabilidad de origen |

Variantes de recuento encontradas: `n_filas`, `n_series`, `n_anuncios`, `n_municipios`, `n_items`, `n_sin_duplicar` — **seis nombres para el mismo concepto**. Y seis esquemas de claves distintos, sin campo de versión del parser ni hash del payload.

Dato a favor, que la rev. 1 no supo medir: **los 60 recuentos son coherentes con el contenido** (`n_* == len(datos)` en los 60). No hay metadata mentirosa, solo heterogénea.

El coste de arreglarlo es bajo: todas las escrituras JSON pasan por `extract/_common.py:167 guardar_json`, que hoy no valida nada. Un solo punto de control cierra el criterio.

En CSV: **16 de 127** sin BOM/UTF-8-sig, de los cuales 11 usan `;` como separador y 1 (`etxebide_indicador_86.csv`) es Latin-1. El código lo maneja explícitamente (`encoding="latin-1"`, `sep=";"`), así que **no hay riesgo de corrupción silenciosa hoy**; el riesgo es que cualquier lector nuevo asuma `,` + UTF-8.

### 4.2 Inmutabilidad de raw (E5: 8/10)

**H-07 (corregido en rev. 2). El raw sí está certificado; lo que está roto es una copia.**

| Comprobación | Resultado |
|---|---|
| Marcador `data/raw/.FROZEN` | ✅ existe |
| Ficheros en `data/raw/` (recursivo, sin contar directorios) | **319** |
| Entradas en el manifest **canónico** `docs/raw_manifest_sha256.txt` | **316** |
| Ficheros sin hash (excluyendo `.FROZEN`, `.gitkeep`, `ingestion_manifest.json`, `manifest_sha256.txt`) | **0** |
| Hashes que no coinciden | **0** |
| Test que lo verifica | `tests/test_raw_inmutable.py` (4 tests, en verde) |

La rev. 1 midió el fichero equivocado: `data/raw/manifest_sha256.txt`, una **copia legacy** de 47 entradas con 5 hashes obsoletos (`alquiler_municipal.csv`, `dim_municipios.csv`, `distancias_capitales_252.csv`, `osrm_tiempos_capitales.csv`, `renta_municipal_referencia.csv`). El manifest canónico vive en `docs/` y está completo y correcto.

Queda un riesgo real, aunque menor: **dos ficheros de manifest con el mismo nombre lógico y contenidos distintos**. Cualquiera que ejecute `sha256sum -c data/raw/manifest_sha256.txt` obtiene 5 fallos y concluye que el raw está corrupto. Arreglo: borrar la copia legacy o regenerarla desde la canónica, y dejar una sola fuente de verdad documentada.

**H-08 (bajo, matizado en rev. 2). El guard existe y se aplica, pero es trivial de satisfacer.**

`transform/_raw_guard.py` define `assert_raw_writable(reason)`. Se invoca en **2** scripts (`enriquecer_codigo_ine.py:137`, `f4_pisos_dirigido.py:68`) y `tests/test_raw_guardrails.py:128` recorre el AST de `transform/*.py` y **falla si un script escribe en `data/raw` sin estar en la lista blanca o sin el guard**. Es decir: la política se hace cumplir, no solo se documenta.

Lo que sigue siendo débil: el guard acepta cualquier cadena no vacía como justificación, así que no distingue "reingesta autorizada" de "hola". Valorar como higiene, no como agujero. La rev. 1 decía "decorativo" y "1 script de 30+": ambas cosas eran incorrectas.

### 4.3 Reproducibilidad (E6: 4/10)

**H-19 (crítico, nuevo en rev. 2). El pipeline no se reconstruye desde cero.**

`transform/` tiene 39 scripts ejecutables; `TRANSFORM_GROUPS` en `run_all.py` orquesta 21. Los 18 restantes, con su papel:

| Script no orquestado | Por qué importa |
|---|---|
| `completar_alquiler_comarca.py` | **produce `alquiler_municipal_completo.csv`**, entrada de `generar_analisis_variables_base.py` |
| `generar_analisis_variables_base.py` | **produce `analisis_variables_base.csv`**, entrada de `calcular_renta_joven.py` (que sí está orquestado) |
| `parsear_secciones.py` | produce `alquiler_seccion.csv` |
| `deduplicar_alquiler_enriquecido.py` | deduplicación de alquiler |
| `generar_poblacion_joven_municipal.py`, `generar_vistas_mercado.py`, `asignar_area_funcional_ecvi.py` | features usadas por dashboards |
| `generar_distancias.py`, `generar_emancipacion_tier3_93.py`, `generar_municipios_faltantes_93.py` | generadores de tablas auxiliares |
| `generar_anuncios_residencial_filtrado.py`, `generar_f4_pisos_objetivo.py`, `generar_fotocasa_dirigido_informe.py`, `f4_pisos_dirigido.py` | captura dirigida (manual por diseño) |
| `muni_resolve.py`, `validar_renta.py`, `auditoria_duckdb.py` | librería / QA / auditoría |
| `run_all.py` | el propio orquestador (18.º fichero de la cuenta) |

Consecuencia medible: **`alquiler_municipal_completo.csv` no tiene productor orquestado** y es requisito de un script orquestado. Si `data/procesado/` desaparece, `run_all.py` falla o —peor— reutiliza artefactos viejos que nadie regeneró. El pipeline es reproducible en un directorio ya poblado y no reproducible en uno limpio.

Agravante: el docstring de `run_all.py` promete "orden topológico de dependencias" y "orden alfabético dentro del grupo", pero la ejecución es una lista fija, en el orden en que está escrita. `calcular_tension_social` funciona solo porque está detrás de `calcular_renta_joven` por abecedario. No hay dependencias declaradas, así que nadie detecta si alguien reordena.

- **Idempotencia comprobada:** `auditar_lagunas_silver.py` ejecutado dos veces produce hash idéntico y coincide con el artefacto previo (`9c810525bd01e199`). Bien, pero es 1 de 30.
- **H-09 (medio). `run_all.py` promete un manifest que no escribe.** No hay ningún fichero `*manifest*` en `data/procesado`. Y `--check` compara el `max(mtime)` de `data/raw` contra el de `data/procesado` en bloque: no detecta staleness por dependencia y da "OK" con scripts individuales desactualizados.
- **H-10 (medio). Nombres de salida volátiles:** 3 ficheros de `data/procesado` llevan timestamp en el nombre (`..._20261029_230030_normalizado.json`). Cada reejecución crea ficheros nuevos en lugar de sobrescribir → el directorio crece y no hay forma de saber cuál es el vigente.
- **H-11 (alto). El claim "silver byte-idéntico" no es verificable:** no existe manifest de hashes de `data/procesado`, y `data/` está entero en `.gitignore`, así que un clon del repositorio no reproduce ni un dato. La reproducibilidad depende hoy de tener el directorio local.

### 4.4 Robustez de código (E7: 6/10)

| Comprobación | Medición | Valoración |
|---|---:|---|
| `except:` desnudos | 0 | ✅ |
| `except Exception:` con `pass` | 10 | ⚠️ silencios que ocultan fallos de fuente |
| `read_csv` sin `dtype=str` | 42 de 84 | ⚠️ salvado por `zfill(5)` posterior; un lector nuevo rompe |
| `assert` en código de producción | 8 | ⚠️ desaparecen con `python -O` |
| Rutas absolutas hardcodeadas | 0 | ✅ |
| Credenciales versionadas | 0 (`api.txt` no trackeado) | ✅ |

**H-12 (medio). Fallback silencioso a constantes.** `transform/calcular_renta_joven.py:47`: si el parseo de Eustat falla, usa `1599, 8156, 20109, 28170` sin avisar. Un informe generado con esas constantes sería indistinguible de uno con datos reales.

**H-13 (alto, confirmado en rev. 2). Propiedad compartida de `dim_municipios_enriquecido.csv`.** Dos escritores verificados:

- `calcular_renta_joven.py:116` construye la salida desde `analisis_variables_base.csv` (`out = base.copy()`) y la escribe sobre el fichero enriquecido.
- `calcular_tension_social.py:54` lee ese fichero, añade las columnas de tensión y lo reescribe.

Hoy funciona **solo porque `run_all.py` los ejecuta en ese orden**. Ejecutar `calcular_renta_joven.py` suelto después borra las 27 columnas que no vienen de la base (tensión social, Etxebide, certificados, etc.). Es la fragilidad más probable que rompa un re-run futuro, y el escenario típico de demo en vivo.

### 4.5 Escala (E8: 7/10)

- Leer los 36 CSV de `data/procesado` (252 filas cada uno): **0,08 s**. Sin problema.
- `dim_municipios.py` cuenta anuncios con `iterrows` sobre 3 CSV crudos: O(n) con coste alto por fila; con 10× anuncios se nota, pero no rompe.
- Distancias b5m: el JSON contiene **180.488 pares completos** (91 MB), sin truncado —la afirmación contraria de auditorías previas está desactualizada—. El coste es cuadrático si se amplía el ámbito geográfico, pero hoy está acotado y materializado.
- Raw: 844,5 MB en 319 ficheros. Sin riesgo de memoria (se lee por fichero).

### 4.6 Documentación vs realidad (E9: 5/10)

**H-14 (medio). `openspec/project.md` está desactualizado en cuatro cifras.**

| Afirmación en `project.md` (línea 6 y 77-80) | Medición real |
|---|---|
| "59 tests en verde" | **66 passed** |
| "314 archivos" en raw | **319** |
| "313 manifest" | **316 entradas** (canónico, en `docs/`) |
| "silver 96 archivos" | **113** en `data/procesado` |

También hay drift en los audits: `readiness_report_2026-10-29.md` documenta 869 anuncios (reparto 471/261/139) y la tabla real tiene **759** (428/247/84). O el filtrado posterior los redujo sin actualizar el informe, o el informe describía otro estado. Cualquiera de las dos cosas es un problema de trazabilidad: el documento que se usa para decidir "GO" no coincide con el dato que se va a analizar.

**H-15 (bajo). Higiene del repositorio:** `api.txt` (40 bytes) en la raíz, ignorado por git pero presente; directorios de trabajo en la raíz (`argon/`, `auditoria_avanzada/`, `framework_auditoria_completo2/`, `graphify-out/`, `scratchpad/`, `data_regen/`, `b1.html`); 190 ficheros trackeados pero `data/` completo ignorado. Y `requirements.txt` instala `pymongo` y `kafka-python-ng` (sin uso) pero **no** un cliente HDFS, que el criterio 2 va a necesitar.

---

## 5. Qué está bien (para no romperlo al corregir)

- **Extracción real y multi-fuente:** 35 scripts, API (Eustat, INE, Udalmap, b5m) y scraping (Fotocasa, Pisos, RealtyAPI), con HTML crudo conservado (101 ficheros).
- **Cero huérfanos** en todas las tablas gold y **0 violaciones** de monotonía en percentiles.
- **Deduplicación efectiva:** 0 duplicados por clave de portal y por fingerprint.
- **Trazabilidad de imputación:** `metodo_imputacion` (`oficial` / `IDW_5_vecinos`) e `idw_vecinos` existen y son correctos.
- **Integridad de raw certificada:** manifest canónico 316/316, 0 hashes discrepantes, `.FROZEN`, y un test que lo comprueba en cada ejecución.
- **Política de escritura de raw aplicada por test**, no solo documentada (AST + lista blanca).
- **Manejo explícito de encoding y separador** en las fuentes que lo necesitan (Latin-1, `;`).
- **Sin credenciales en git** (P-07 cumplida) y sin `except:` desnudos.
- **Idempotencia** verificada al menos en un generador.
- **Los specs declaran honestamente lo pendiente** (`Estado: Pendiente` en almacenamiento y MongoDB); el problema no es la honestidad, es que los tests no reflejan esa pendencia.

---

## 6. Mejoras propuestas, priorizadas

> El desarrollo detallado de las que pertenecen a la fase actual (obtención + transformación), con parches y criterios de aceptación, está en `plan_10_10_datos_2026-10-31.md`.

### Bloqueantes (antes de escribir una sola línea del informe del reto)

| # | Acción | Dónde | Esfuerzo |
|---|---|---|---|
| M-01 | **Elegir un indicador canónico de esfuerzo** y declararlo en el contrato. Recomendado: el fiscal por municipio (`renta_joven_estimada_16_29`), porque el salario OVJ es una constante autonómica y no puede ordenar municipios. La variante OVJ queda como referencia, nunca como ranking. | `transform/generar_analisis_variables_base.py`, `specs/contrato-reto` | 2 h |
| M-02 | **Publicar el ranking con flag de fiabilidad**: excluir o etiquetar `metodo_imputacion != oficial` y `n_anuncios < 5`. Dos rankings (oficial vs ampliado) con la advertencia explícita. | `transform/generar_analisis_variables_base.py` + informe | 3 h |
| M-03 | **`0.0 → NaN` en tasas con cero imposible**, `tasa_paro_valida = notna & > 0`, y **no aplicar el clip contra un cap nulo**. Un solo cambio corrige el 0 % de paro y el 8,57 %→0 % de Usansolo. | `transform/corregir_empleo.py`, `generar_analisis_variables_base.py:101-105` | 2 h |
| M-04 | **`n_anuncios` desde `anuncios_unificados.csv`**, en un paso declarado posterior a `unificacion` (no dentro de `dim_municipios.py`, que corre antes). Recalcular también `tipologia_mercado`. | paso nuevo tras `unificacion` | 1 h |
| M-05 | **Eliminar o recalcular `brecha_ocupacion_actividad_pct`**: positiva en 248/252 es imposible por definición. | `transform/corregir_empleo.py:48` | 30 min |
| M-06 | **Orquestar los 18 scripts restantes** con dependencias declaradas (`in`/`out`) y orden topológico real; escribir el manifest de ejecución. Sin esto, ningún claim de reproducibilidad es cierto. | `transform/run_all.py` | 3 h |

### Altas (necesarias para aprobar, no para el análisis)

| # | Acción | Esfuerzo |
|---|---|---|
| M-07 | **Cerrar los 11 criterios pendientes en orden de dependencia:** HDFS (originales/procesados + recuperación) → Kafka (productor/consumidor) → MongoDB (modelado + PyMongo) → consultas/agregación → gráficos desde PyMongo → informe con conclusiones. | 3–4 semanas |
| M-08 | **Añadir un test de cobertura de contrato** que falle si un requisito no tiene implementación observable (no que el texto lo enumere). Sustituir la lógica circular de `test_p08`. | 4 h |
| M-09 | **Manifest de hashes de silver** con verificación en CI local, y borrar o regenerar la copia legacy `data/raw/manifest_sha256.txt`. | 2 h |
| M-10 | **Separar ficheros por script:** que `calcular_renta_joven.py` escriba `dim_municipios_renta.csv` en vez de reescribir el enriquecido, o que haga merge por `codigo_ine` en lugar de `base.copy()`. | 2 h |
| M-11 | **Esquema único de metadata** en `guardar_json` (fuente, url, fecha ISO, `n_registros`, hash, versión de parser) con validación en escritura. Los 60 ficheros existentes no se reescriben: se normalizan al subir a HDFS. | 3 h |
| M-12 | **Subir `n_anuncios`/`esfuerzo` a un solo contrato de unidades** (fracción o porcentaje, no ambos) y documentarlo en el spec. | 2 h |

### Medias

| # | Acción |
|---|---|
| M-13 | Escribir el manifest de ejecución que `run_all.py` ya promete, con estado/duración/hash por script, y hacer que `--check` compare por dependencia declarada. |
| M-14 | Eliminar timestamps de nombres de salida; versionar con `manifest` en lugar de con el nombre. |
| M-15 | Sustituir los 8 `assert` de producción por validación explícita + `raise`. |
| M-16 | Cambiar los 10 `except Exception: pass` por log de advertencia con nombre de fuente. |
| M-17 | Endurecer `assert_raw_writable`: exigir un motivo de una lista cerrada (`reingesta`, `correccion_fuente`) en lugar de cualquier cadena. |
| M-18 | `read_csv(..., dtype=str)` en las 42 llamadas restantes sobre tablas con `codigo_ine`; eliminar el `zfill` como red de seguridad. |
| M-19 | Actualizar las cifras de `project.md` (66 tests, 319 raw, 316 manifest, 113 procesado) y las 869→759 de los audits. |
| M-20 | Mover `api.txt` fuera del repo, limpiar directorios de trabajo de la raíz y añadir `hdfs` a `requirements.txt`. |

---

## 7. Correcciones a auditorías previas

| Auditoría previa | Afirmaba | Realidad medida |
|---|---|---|
| `readiness_report_2026-10-29.md` | 8,5/10, "GO" | correcto en realismo de datos; incompleto en contrato (3/18), reproducibilidad (18 scripts sin orquestar) y validez del ranking |
| `readiness_report_2026-10-29.md` | "nulos no convertidos a 0" | falso para `tasa_paro_lanbide_pct` (3 ceros) y, por el clip, `tasa_desempleo_juvenil_real_pct` (2 ceros artificiales sobre 8) |
| `readiness_report_2026-10-29.md` | 869 anuncios (471/261/139) | 759 (428/247/84) |
| `informe_alineacion_scope_raw_limpieza.md` | "~9 JSON sin metadata" | 2 sin bloque `metadata`; 9 sin fecha; 6 sin recuento; 40 sin `url`; 6 esquemas distintos |
| `informe_alineacion_scope_raw_limpieza.md` | "59/66 tests en verde" como evidencia de P-08 | los tests no cubren 11 criterios; el test de P-08 es circular |
| `informe_alineacion_scope_raw_limpieza.md` | raw inmutable y manifest | **correcto en el canónico** (316/316, 0 fallos); la copia legacy de `data/raw/` es la que está rota |
| `readiness_report_2026-10-29.md` | "distancias truncadas: 5.000 de ~180.000 pares" | falsa: 180.488 pares completos en `distancias_b5m_gipuzkoa_normalizado.json` |
| `readiness_report_2026-10-29.md` | `EQUIVALENCIAS_EXTRA` como dead code pendiente | ya no existe en el código: deuda cerrada |

---

## 8. Limitaciones de esta auditoría

- No se ha reejecutado el pipeline completo (habría sobrescrito gold y podido tocar raw). El determinismo se comprobó en un generador, no en los 30.
- El hallazgo H-19 se ha establecido por análisis estático de `run_all.py` frente a `transform/*.py`; no se ha ejecutado el escenario destructivo (borrar `data/procesado` y reejecutar) porque no es reversible sin volver a bajar datos.
- No se ha verificado el contenido de los dashboards HTML ni la calidad visual de los 13 PNG (fuera de alcance: no se pidió revisión visual).
- No se ha evaluado HDFS/Kafka/MongoDB porque no existen; su puntuación es 0 por ausencia, no por defecto de implementación.
- Las cifras de sensibilidad del ranking dependen del estado actual de `data/procesado`; si se regenera el gold, deben repetirse con la misma sonda.
- La puntuación global (5,4/10) es una síntesis de los nueve ejes con pesos iguales; es una herramienta de comunicación, no una medida física.

---

## 9. Historial de revisiones

| Rev. | Fecha | Cambio |
|---|---|---|
| 1 | 2026-10-31 | Auditoría inicial (9 ejes, 15 hallazgos) |
| 2 | 2026-10-31b | Re-medición de E4/E5 contra el manifest canónico; reescritura de H-04 y H-06; H-08 matizado; nuevos H-04b (clip), H-16 (brecha), H-19 (orquestación); puntuaciones y media corregidas; §10 con las siete correcciones |

---

## 10. Errata de la rev. 1

Errores de la propia auditoría, con la evidencia que los corrige. Se mantienen visibles porque un informe que no se corrige a sí mismo no sirve para decidir.

| # | Rev. 1 decía | Rev. 2 corrige | Evidencia |
|---|---|---|---|
| 1 | "Manifest cubre 47 de 319; 5 hashes no coinciden; raw sin certificar (E5=3)" | El canónico `docs/raw_manifest_sha256.txt` cubre **316/316** con **0** discrepancias; E5=8. Lo roto es una copia legacy en `data/raw/` | recálculo sha256 de los 316 ficheros; `tests/test_raw_inmutable.py` en verde |
| 2 | "47 de 60 JSON sin metadata completa" (n_registros 44, fecha 7, fuente 3) | 2 sin bloque `metadata`, 1 sin `fuente`, 9 sin fecha, 6 sin recuento, 40 sin `url`. El defecto real es la falta de esquema común, no la ausencia de metadata | recuento por campo sobre los 60 JSON (`fecha_extraccion` es el alias usado) |
| 3 | "`b5m_catalogo.json` sin bloque de metadata" | Sí tiene `{metadata, datos}`. Es el único sin `fuente` | lectura del fichero |
| 4 | "Los 60 recuentos no son verificables" | Los 60 recuentos **coinciden** con `len(datos)`; 0 incoherencias | comprobación `n_* == len(datos)` en los 60 |
| 5 | "`_raw_guard` solo se usa en 1 script de 30+; guard decorativo" | Se usa en 2 scripts y **un test AST lo exige** con lista blanca; la política se aplica | `tests/test_raw_guardrails.py:128`, `enriquecer_codigo_ine.py:137`, `f4_pisos_dirigido.py:68` |
| 6 | "Usansolo con 0,0 % de desempleo juvenil" (implicando que la fuente lo propaga) | El pipeline calcula **8,57 %** (13/151,7) y lo anula con `clip(upper = tasa_paro × 4 = 0)`. Es un bug de código, no un dato de fuente | `analisis_variables_base.csv` fila 48916 + `generar_analisis_variables_base.py:101-105` |
| 7 | "5,5/10 global" | 5,4/10 (media de los nueve ejes con las notas corregidas); el 5,5 no reproducía la tabla | §1 |

Además, la rev. 1 **no detectó** tres problemas que la rev. 2 incorpora: el pipeline no orquestado (H-19), el clip que destruye la tasa juvenil (H-04b) y la brecha ocupación-actividad imposible en 248/252 municipios (H-16).
