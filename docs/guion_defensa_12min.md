# Guion de defensa — 12 minutos

> Sustituye `P1`, `P2`, `P3` por los nombres del equipo. Si defendéis entre
> dos, fusiona P2 y P3 y reparte los minutos 3:30–10:30. Si defiendes solo,
> mantén los tres sombreros y cambia de pie/cursor en cada bloque: la rúbrica
> premia que **cada integrante** explique lo suyo, no que uno lo lea todo.

## Ficha

| Campo | Valor |
|---|---|
| Duración | 12:00 duros (11:15 si hay preguntas) |
| Objetivo | Responder al reto y demostrar las evidencias del Tema 8 |
| Material | `docs/guion_defensa_12min.md`, `docs/matriz_indicadores.md`, `docs/informe_final.md` |
| Terminal | `.venv/Scripts/python.exe`, Mongo local arrancado |
| Regla | Ninguna cifra se dice de memoria si está en un CSV |

## Reparto y tiempos

| Inicio | Fin | Quién | Bloque | Evidencia |
|---|---|---|---|---|
| 0:00 | 0:45 | P1 | Tesis y alcance | `informe_final.md` |
| 0:45 | 2:00 | P1 | Problema, fuentes y universo | `matriz_indicadores.md` |
| 2:00 | 3:30 | P2 | Arquitectura y cadena | `arquitectura_datos.md` |
| 3:30 | 5:00 | P2 | Modelo: embedding vs referencing | `modelo_mongodb.md` |
| 5:00 | 6:30 | P2 | Carga, limpieza y CRUD | `storage/clean_mongo.py`, `load_mongo.py` |
| 6:30 | 8:00 | P3 | Consultas y aggregation | `mongo_aggregations.py` |
| 8:00 | 9:30 | P3 | Terminal: demo y huella | `run_analisis_mongo.py` |
| 9:30 | 10:30 | P3 | Índices y explain | `mongo_indexes.py` |
| 10:30 | 11:15 | P1 | Consistencia y transacción | `modelo_mongodb.md` §Transacciones |
| 11:15 | 12:00 | P1 | Límites y cierre | `informe_final.md` |

## 0:00–0:45 · P1 · Tesis y alcance

> "La pregunta es si una persona joven puede independizarse en Euskadi con su
> salario. La respuesta corta: **con el alquiler oficial, 4 de cada 10
> municipios exigen más del 30 % del salario joven; en Bilbao y Donostia
> ronda el 38 %**. Lo defendemos con 252 municipios, 159 con alquiler oficial
> y 93 imputados solo para sensibilidad. Lo que no tenemos es stock histórico
> de VPO: tenemos flujo oficial 2020–2024, 251 de 252 municipios."

**Alcance dicho en voz alta:** HDFS guarda originales; `procesado/` no se
subió (decisión firmada). Kafka funciona en VM. Así nadie te pilla
sobrevendiendo.

## 0:45–2:00 · P1 · Problema, fuentes y universo

- Fuentes: Fotocasa/Pisos/RealtyAPI (anuncios), Eustat (renta y alquiler),
  Lanbide (paro), Etxebide (solicitudes y promociones), Udalmap (VPO y
  vivienda), OSRM (tiempos), INE (apoyo).
- **759 anuncios en 83 municipios**; **169 municipios sin anuncios** (67 %).
- Esfuerzo: `cuantía mediana × 12 / renta joven 18–34`.
- Titular: **26,61 % de mediana en los 159 oficiales**; **40 de 159 (25,2 %)**
  por encima del 30 %. Con IDW: **25,37 % (47/252, 18,7 %)**.
- Tensión social: **76 alta / 103 media / 73 baja**.

Frase de cierre del bloque: "La muestra no permite ranking fino; permite
comparar 4 municipios con n≥30 y decir dónde no se puede concluir".

## 2:00–3:30 · P2 · Arquitectura y cadena

> "Todo entra por `extract/`, se congela en `data/raw` con manifest SHA-256
> (**354 ficheros, 0 errores**), se transforma a silver (**185**), se carga
> en Mongo (**16 colecciones**) y se analiza con **9 pipelines** que escriben
> 5 CSV y 13 PNG. Kafka alimenta `anuncios` por upsert; el análisis solo lee."

Enseñar el diagrama y decir el campo común: **`codigo_ine` de 5 dígitos**.
Mencionar la decisión: `procesado/` se queda en local, no sube a HDFS.

## 3:30–5:00 · P2 · Modelo: embedding vs referencing

Responder a las preguntas del docx §5, no a teoría genérica:

- **Se lee junto y cambia poco** → embebido: demografía, empleo, demanda
  social y transporte dentro de `municipios`.
- **Crece sin límite** → colección propia: `anuncios` (759), `etxebide_solicitudes`
  (5.040).
- **Patrón de acceso** → la ficha municipal se abre entera; los anuncios se
  filtran por municipio, modalidad y precio.
- **Referencia** por `codigo_ine`: `anuncios.ubicacion.codigo_ine`,
  `alquiler_municipal._id`, `etxebide_promociones.codigo_ine`.
- **No denormalizamos** indicadores calculados: `n_anuncios` y `esfuerzo_*`
  salen de aggregation, no se guardan a mano.

> "Elegimos referencing donde el array podría crecer sin límite y embedding
> donde el documento se lee como una ficha. Esa es la decisión que la rúbrica
> pide justificar."

## 5:00–6:30 · P2 · Carga, limpieza y CRUD

- Carga: `insert_many` para colecciones municipales, `update_one(upsert=True)`
  para lo que llega por Kafka.
- Limpieza real: **845 → 759 anuncios**; **86 duplicados (10,18 %)** por
  `(portal, id_anuncio)`.
- Nulos: Usansolo (48916) sin VPO **no se imputa a 0**; queda nulo y el
  pipeline lo excluye (251).
- Tipos: dinero en `Decimal128`, `codigo_ine` string de 5, geo como GeoJSON
  Point.
- Comprobaciones: `matched_count` / `modified_count` en las actualizaciones.

Enseñar una línea: `storage/mongo.py:replace_collection` usa
staging + backup + rename, nunca `drop()` sobre producción.

## 6:30–8:00 · P3 · Consultas y aggregation

Tres pipelines, cada uno con **qué entra y qué sale**:

1. `pipeline_indicadores_municipio`: 252 filas; `$lookup` anuncios +
   alquiler + indicadores; expone tensión, paro y esfuerzo.
2. `pipeline_vpo_terminadas`: 251 filas; `$match` excluye el nulo, `$lookup`
   trae nombre y territorio; **Berango 62,55 ‰**.
3. `pipeline_esfuerzo_por_sexo`: 252 filas; `$addFields` calcula el esfuerzo
   de hombres y mujeres en Mongo, no en Python.

Regla de oro al explicar: "`$lookup` antes de `$unwind` para no multiplicar
filas; `$group` para el agregado; `$project` para dejar solo lo que se
defiende".

### Consultas que puedes enseñar (verificadas)

```python
from storage.mongo import get_collection

# 1) Dot notation + proyección: ficha de Bilbao.
get_collection("municipios").find_one(
    {"_id": "48020"},
    {"nombre_canonico": 1, "demanda_social.tension_categoria": 1,
     "demanda_social.tension_demanda_social": 1},
)
# -> Bilbao, tension_categoria 'alta', tension_demanda_social 94.8

# 2) Comparación + igualdad + proyección anidada.
q = {"precio_eur": {"$lte": 1000}, "modalidad": "larga_estancia"}
get_collection("anuncios").count_documents(q)   # -> 74
get_collection("anuncios").find_one(q, {"precio_eur": 1, "ubicacion.codigo_ine": 1, "_id": 0})
# -> 995.0 EUR en el municipio 20055
```

Si preguntan por arrays: `anuncios.equipamiento` y `historico_precios` son
arrays; el índice multikey existe precisamente por `equipamiento`. No fuerces
un `$elemMatch` en vivo si no lo has ensayado.

## 8:00–9:30 · P3 · Terminal

```bash
.venv/Scripts/python.exe extract/generar_manifest.py --verify
.venv/Scripts/python.exe -m pytest tests -q
.venv/Scripts/python.exe analysis/run_analisis_mongo.py
.venv/Scripts/python.exe scripts/verificar_fase_datos.py
```

Salidas que hay que saber leer:

| Comando | Salida esperada |
|---|---|
| manifest | `354 entradas, 0 errores` + `185 entradas, 0 errores` |
| pytest | `136 passed` |
| run_analisis | `9 pipelines`, 5 CSV (252/252/2/252/322), `13 PNG`, huella `08665d03…c30a`, `reproducibilidad: ok` |
| gate | `RESULTADO: OK 18/18` |

Si Mongo no responde: enseñar los CSV y PNG ya generados y decir "la huella
es reproducible; la última ejecución está en `data/resultados`". **No
improvisar una demo en vivo sin Mongo.**

## 9:30–10:30 · P3 · Índices y explain

> "La consulta es municipio + modalidad + precio ≤ 1000. Antes:
> **COLLSCAN, 759 documentos examinados**. Después del índice ESR
> `(codigo_ine, modalidad, precio_eur)`: **IXSCAN, 1 examinado, 1 clave**.
> El coste es escritura y espacio; por eso solo creamos índices con consulta
> detrás."

Mencionar 2dsphere sparse para geo (424 de 759 con punto real) y el multikey
de `equipamiento`.

## 10:30–11:15 · P1 · Consistencia y transacción

> "No usamos transacción porque cada cambio cabe en un documento. La prueba
> es `marcar_calidad_municipio`: `find_one_and_update` con
> `ReturnDocument.AFTER` devuelve el valor nuevo en una sola operación; hay
> test contra la base de test. La carga usa staging + backup + rename. Si
> denormalizáramos el conteo de anuncios en `municipios` y hubiera que
> borrarlos a la vez, sí necesitaríamos sesión con commit/abort."

Shard key si preguntan: `codigo_ine` hashed reduce hotspots pero provoca
scatter-gather; ranged concentra Bilbao/Donostia. "A esta escala no shardearía".

## 11:15–12:00 · P1 · Límites y cierre

Cuatro límites, uno por frase:

1. **169 municipios sin anuncios** → sin precio observado; se usa cuantía oficial.
2. **93 IDW** → solo sensibilidad, nunca titular.
3. **4 robustos** → Getxo 40 y Vitoria 39 se diferencian en 1 anuncio.
4. **Años mezclados** (anuncios 2026, renta/paro 2024) y **VPO flujo ≠ stock**.

Cierre: "Con esos límites, la conclusión defendible es que Bilbao y Donostia
son los peores para emanciparse, Getxo y Vitoria quedan cerca del umbral, y
el resto no se puede rankear con esta muestra. Eso es lo que los datos
sostienen, ni más ni menos."

## Preguntas por persona

**P1 (reto y conclusiones)**
- ¿Por qué mediana y no media? → outliers de alquiler; canónico declarado.
- ¿Getxo es más asequible que Vitoria? → 28,60 vs 33,37 con 1 anuncio de
  diferencia; no hay ranking firme.
- ¿Qué cambiaría con datos individuales? → falacia ecológica: la renta es
  municipal, no personal.

**P2 (modelo y CRUD)**
- ¿Por qué 16 colecciones? → una por fuente/frecuencia; backups aparte.
- ¿Dónde crecería un array sin límite? → `anuncios` y `etxebide_solicitudes`;
  por eso son colecciones.
- ¿Qué operador no usaste? → los que no tenían necesidad; forzarlos sería
  empeorar el modelo.

**P3 (rendimiento y demo)**
- ¿Qué etapa hace qué? → entra/sale por etapa, no recitar el JSON.
- ¿Por qué ESR? → igualdad, orden, rango.
- ¿Qué pasa si el índice no se usa? → `explain` lo delata; se revisa el orden
  de campos.

## Frases prohibidas

- "HDFS tiene originales **y procesados**" → solo originales (rúbrica: 7, no 10).
- "Tenemos stock de VPO" → flujo 2020–2024; stock sin fuente.
- "Getxo es el más asequible" → 1 anuncio de diferencia.
- "Los 252 municipios son oficiales" → 159 oficiales + 93 IDW.
- "La huella es `f1e78870`" → la vigente es `08665d03…c30a`.
- "16-29 es el esfuerzo canónico" → legacy; el canónico es 18–34.

## Si vas justo de tiempo

Recorta en este orden: consultas (6:30–8:00) a 45 s; consistencia
(10:30–11:15) a 20 s; nunca recortes la demo ni los límites.

## Checklist 10 minutos antes

- [ ] Mongo local responde (`pipeline_vpo_terminadas` devuelve 251).
- [ ] `.venv` activo y `pytest -q` verde.
- [ ] CSV y 13 PNG ya generados en `data/resultados`.
- [ ] Huella `08665d03…c30a` copiada a mano.
- [ ] `git status` limpio (no enseñar cambios sin commitear).
