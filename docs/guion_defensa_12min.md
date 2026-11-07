# Presentación de defensa — 12 minutos

> Presentación generada: `docs/presentacion/index.html` (PDF en la misma carpeta).
>
> **La pregunta manda.** Esto no es una demo de MongoDB: es la respuesta a
> "¿puede una persona joven independizarse en Euskadi con su salario?", con
> MongoDB como evidencia. Regla de reparto: **7 minutos responden**, **4
> demuestran cómo se calculó**, **1 cierra con límites**.
>
> Sustituye P1/P2/P3 por los nombres del equipo. Si defendéis entre dos,
> fusiona P2 y P3. Si defiendes solo, cambia de sombrero en cada bloque.

## Por qué este orden

| Fuente | Qué premia | Dónde se gana |
|---|---|---|
| RA4 (40 %) | Respuesta al reto, ≥3 municipios, cada conclusión atada a un indicador de Mongo | 0:00–7:30 y 11:30 |
| SBD RA1 (46,7 %) | Integración de fuentes, limpieza, automatización | 1:00–3:00 y 7:30–9:30 |
| SBD RA3 (13,3 %) | Modelo, consultas, aggregation, índices, consistencia | 7:30–10:30 |
| Tema 8 | Aggregation 20 %, índices 15 %, modelado 15 %, defensa 10 % | 7:30–10:30 |

Si la presentación empieza por colecciones e índices, el tribunal oye "otro
proyecto de MongoDB" y la pregunta queda para el final. Al revés, cada detalle
técnico cae sobre una conclusión que ya está en pie.

## Diapositivas (10)

1. **La pregunta** y la respuesta en una frase.
2. **Cómo se mide**: esfuerzo = cuantía × 12 / renta joven 18-34; umbral 30 %.
3. **Mapa de Euskadi** por municipios (159 oficiales, color por esfuerzo).
4. **La respuesta en cuatro cifras**: 54 con margen / 65 justos / 40 no / 93 solo IDW.
5. **Los 4 robustos** con n y esfuerzo; Getxo 50/Vitoria 39 (diferencia 11).
6. **Sensibilidad**: oficial vs IDW vs bootstrap (intervalos).
7. **Quién queda fuera**: 188 sin anuncios, 93 IDW, falacia ecológica.
8. **Arquitectura** en una línea: fuentes → raw → silver → Mongo → 10 pipelines.
9. **Pruebas**: explain 594→1, 177 tests, gate en `scripts/verificar_fase_datos.py`, huella.
10. **Límites y qué haríamos con más datos**.

## Reparto y tiempos

| Inicio | Fin | Quién | Qué cuenta | Diapo |
|---|---|---|---|---|
| 0:00 | 0:50 | P1 | Pregunta + respuesta en 30 segundos | 1 |
| 0:50 | 2:30 | P1 | Cómo se mide y qué universo hay | 2 |
| 2:30 | 4:00 | P1 | El mapa: 26,61 %, 40/159, territorios | 3 |
| 4:00 | 4:50 | P1 | La respuesta en cuatro cifras: 54/65/40/93 | 4 |
| 4:50 | 6:10 | P1 | Los 4 robustos y qué se puede afirmar | 5 |
| 6:10 | 7:00 | P2 | Sensibilidad: el titular aguanta | 6 |
| 7:00 | 7:40 | P2 | Quién queda fuera y por qué importa | 6 |
| 7:40 | 9:10 | P2 | Arquitectura, modelo y pipelines | 7 |
| 9:10 | 10:20 | P3 | Pruebas en terminal: explain, tests, gate | 8 |
| 10:20 | 11:20 | P3 | Consistencia y decisiones técnicas | 8 |
| 11:20 | 12:00 | P1 | Límites + cierre | 9 |

## 0:00–0:50 · P1 · Pregunta y respuesta

> "Nos preguntaron si una persona joven puede independizarse en Euskadi con su
> salario. **Con el alquiler oficial, la mediana se lleva el 26,6 % del salario
> joven; en 40 de los 159 municipios con dato se supera el 30 %, y en Bilbao y
> Donostia se roza el 38 %.** La respuesta es: en la mayoría del territorio,
> justo; en las dos capitales grandes, no; y en 188 municipios no podemos
> afirmarlo porque no hay anuncios."

No empieces por la arquitectura. Esa frase es la presentación.

## 0:50–2:30 · P1 · Cómo se mide

- Esfuerzo = **cuantía mediana del alquiler × 12 / renta joven 18-34**.
- Se usa **mediana**, no media: los alquileres tienen outliers.
- Universo: **252 municipios**; **159 con alquiler oficial Eustat** y **93
  imputados por IDW** que solo valen para sensibilidad.
- Umbral: **30 %** del salario, el que usa la literatura de emancipación.
- Datos de apoyo: paro Lanbide 252/252, Etxebide 5.040 solicitudes, VPO flujo
  251/252.

Frase: "El indicador no es nuestro: es el estándar; lo que aportamos es
calcularlo municipal y decir dónde no se puede calcular."

## 2:30–4:00 · P1 · El mapa

- **Mediana 26,61 %** en los 159 oficiales; **40 municipios (25,2 %) por
  encima del 30 %**.
- **Álava, Bizkaia y Gipuzkoa** no se comportan igual: la mediana sube donde
  hay mercado de alquiler tensionado.
- Con IDW el titular no cambia: **25,37 % (47/252, 18,7 %)**.
- Tensión social (Etxebide + esfuerzo): **76 alta / 103 media / 73 baja**.
- Paro y alquiler: **r(conteo, alquiler) ≈ 0,39** (conteos, no tasa), relación débil; no hay trade-off simple.

> "El mapa no dice 'Euskadi es caro'. Dice dónde el alquiler se come el
> salario y dónde ni siquiera tenemos precio para decirlo."

## 4:00–4:50 · P1 · La respuesta en cuatro cifras

> "Si el tribunal quiere un sí o un no, esta es la tabla: **54 municipios**
> pueden con margen, **65** pueden pero justo, **40** no llegan y **93** solo
> tienen una estimación, no un dato. Tres de cada cuatro con dato oficial
> están en el umbral o por debajo; el problema se concentra en Bilbao,
> Donostia y una decena más por encima del 35 %."

Los 93 IDW van en barra aparte: no se suman a los 159 oficiales.

## 4:50–6:10 · P1 · Los 4 robustos

| Municipio | n anuncios | Esfuerzo | Lectura |
|---|---|---|---|
| Bilbao | 204 | 37,69 % | peor: precio alto + esfuerzo máximo |
| Donostia | 126 | 38,17 % | peor: misma pauta |
| Getxo | 50 | 28,60 % | bajo el umbral por 1,4 puntos |
| Vitoria-Gasteiz | 39 | 33,37 % | esfuerzo por renta, m² más barato |

- **Getxo 50 vs Vitoria 39: diferencia 11 (no 1).** No hay ranking firme entre los dos, pero el umbral n>=30 está superado en ambos.
- Barakaldo (n=6) queda fuera por muestra, aunque su esfuerzo sea alto.
- Bilbao + Donostia = **56 % de los anuncios**; el top-4, el 71 %.
- Nivel (tipología 4/54/194) es ortogonal a Tier (confianza 4/3/57/188): son ejes ortogonales, no intercambiables.

Frase: "Podemos comparar cuatro; podemos rankear dos. La diferencia es la que
la rúbrica llama conclusión defendible."

## 6:10–7:00 · P2 · Sensibilidad: ¿aguanta el titular?

- **Oficial 159**: 26,61 % de mediana, 40 > 30.
- **IDW 252**: 25,37 %, 47 > 30 → el signo no cambia.
- **Bootstrap 10.000** (n_larga_solo_vivienda 67/60/39/37, distinto del n_anuncios Tier 204/126/50/39; no intercambiables): Bilbao 33.75–40.95; Donostia 32,4–45,8; **se solapan**.
  Getxo 27.54–31.77; Vitoria 30,8–39,4.

> "El titular aguanta, el orden entre Bilbao y Donostia no. Eso lo decimos
> nosotros antes de que lo pregunte el tribunal."

## 7:00–7:40 · P2 · Quién queda fuera

- **188 municipios (75 %) sin anuncios** → sin precio observado.
- **93 IDW** → sensibilidad, nunca titular.
- Renta municipal como **proxy**: falacia ecológica, no es renta individual.
- Años mezclados: anuncios 2026, renta/paro 2024.
- **VPO**: flujo 2020–2024, no stock histórico (Usansolo sin dato).

Frase: "Estos cuatro huecos no son un fallo del proyecto: son el perímetro de
lo que se puede afirmar."

## 7:40–9:10 · P2 · Cómo se calculó (técnico, comprimido)

- Cadena: `extract/` → **raw 352 en HDFS** (solo `raw`) → silver **188** →
  Mongo **14 colecciones** → **10 pipelines** → 6 CSV + 12 PNG únicos de 13 emitidos.
- Modelo: **embedding** de demografía/empleo/demanda social en `municipios`
  (se leen juntos, cambian poco); **referencing** por `codigo_ine` para
  `anuncios` y `etxebide_promociones` (crecen sin límite).
- Limpieza: **843 raw → 594** anuncios (dedup portal+id 955, fingerprint 234,
  cuarentena pisos 45); Usansolo no se
  imputa.
- Pipelines que sostienen la respuesta:
  1. `pipeline_indicadores_municipio` → 252 filas, esfuerzo, tensión, paro.
  2. `pipeline_vpo_terminadas` → 251 filas, VPO de flujo.
  3. `pipeline_esfuerzo_por_sexo` → 252 filas, esfuerzo calculado en Mongo.
- **Huella reproducible** (ver salida de `run_analisis_mongo`): dos ejecuciones del mismo estado, mismos CSV.

No expliques las 9: tres bastan si cada una responde a una pregunta del reto.

## 9:10–10:20 · P3 · Pruebas en terminal

```bash
.venv/Scripts/python.exe extract/generar_manifest.py --verify
.venv/Scripts/python.exe -m pytest tests -q
.venv/Scripts/python.exe analysis/run_analisis_mongo.py
.venv/Scripts/python.exe scripts/verificar_fase_datos.py
```

| Comando | Salida que se lee en voz alta |
|---|---|
| manifest | `352` raw en HDFS y `188` silver, **0 errores** |
| pytest | **177 passed + 1 skipped** |
| run_analisis | **10 pipelines**, 6 CSV, **12 PNG únicos de 13 emitidos**, huella reproducible |
| gate | `scripts/verificar_fase_datos.py` (06 PASS 594/843; 07 FAIL conocido paro-cero) |

Índices: la consulta municipio + modalidad + precio ≤1000 pasa de
**COLLSCAN 594 examinados** a **IXSCAN 1**. Índice ESR
`(codigo_ine, modalidad, precio_eur)`; coste: escrituras y espacio.

Consulta que puedes enseñar (verificada):

```python
from storage.mongo import get_collection
get_collection("municipios").find_one(
    {"_id": "48020"},
    {"nombre_canonico": 1, "demanda_social.tension_categoria": 1,
     "demanda_social.tension_demanda_social": 1},
)
# -> Bilbao, 'alta', 94.8
```

## 10:20–11:20 · P3 · Consistencia y decisiones

- **Sin transacción**: cada cambio cabe en un documento;
  `marcar_calidad_municipio` usa `find_one_and_update` +
  `ReturnDocument.AFTER`, con test.
- Carga con **staging + backup + rename**, nunca `drop()` sobre producción.
- Si se denormalizara el conteo de anuncios en `municipios` y hubiera que
  borrarlos a la vez, **sí** haría falta sesión con commit/abort.
- Shard key si preguntan: `codigo_ine` hashed evita hotspots pero provoca
  scatter-gather; a esta escala no shardearía.

## 11:20–12:00 · P1 · Límites y cierre

1. **188 sin anuncios**: no hay precio que comparar (precio solo en 62/252).
2. **93 IDW**: solo sensibilidad; esfuerzo 252 contextual sobre 159 oficiales.
3. **4 robustos**: Getxo 50 vs Vitoria 39 (diferencia 11, no ranking firme entre ambos).
4. **Años y VPO**: 2026 vs 2024; flujo no es stock.

> "La conclusión que sostenemos es esta: Bilbao y Donostia son las peores
> plazas para emanciparse con el salario joven; Getxo y Vitoria quedan cerca
> del umbral; y en tres cuartos de los municipios no hay datos para afirmarlo.
> Con más anuncios y stock de VPO podríamos ampliar el mapa, no cambiar el
> signo del titular."

## Preguntas por persona

**P1 (la pregunta)**
- ¿Por qué mediana? → outliers; canónico declarado.
- ¿Getxo es más asequible? → diferencia 11 con n firme en ambos, pero sin ranking municipal fuera de los 4.
- ¿Y una persona concreta? → renta municipal ≠ individual; falacia ecológica.

**P2 (método y modelo)**
- ¿Por qué 14 colecciones? → una por fuente/frecuencia; los 13 `__backup` no cuentan.
- ¿Qué va embebido y qué referenciado? → ficha municipal vs arrays que crecen.
- ¿Por qué IDW y no imputar todo? → no inventar precio donde no lo hay.

**P3 (pruebas)**
- ¿Qué etapa hace qué? → entra/sale por etapa, sin recitar JSON.
- ¿Por qué ESR? → igualdad, orden, rango.
- ¿Qué pasa si el índice no se usa? → `explain` lo delata y se revisa el orden.

## Frases prohibidas

- "HDFS tiene originales y procesados" → solo originales (rúbrica: 7, no 10).
- "Tenemos stock de VPO" → flujo 2020–2024; stock sin fuente.
- "Getxo es el más asequible" → sin ranking municipal fuera de Tier A (Tier B solo indicativo).
- "Los 252 son oficiales" → 159 + 93 IDW; esfuerzo 252 contextual sobre 159 oficiales.
- "La huella es un hex fijo" → la huella depende del estado; dos ejecuciones del mismo estado coinciden.
- "16-29 es el canónico" → legacy; el canónico es 18–34.

## Si vas justo de tiempo

Recorta en este orden: pruebas a 30 s (manifest + pytest), consistencia a 20 s,
modelo a 40 s. **Nunca** recortes la respuesta, los 4 robustos ni los límites.

## Checklist 10 minutos antes

- [ ] Mongo responde (`pipeline_vpo_terminadas` → 251).
- [ ] `.venv` activo y `pytest -q` verde.
- [ ] CSV y 12 PNG únicos de 13 emitidos en `data/resultados`.
- [ ] Huella `08665d03…c30a` copiada.
- [ ] Mapa y tabla de robustos abiertos, no buscados en vivo.
- [ ] `git status` limpio.
