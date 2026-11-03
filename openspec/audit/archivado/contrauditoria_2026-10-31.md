# Contrauditoría — 2026-10-31

**Objeto:** auditar TODO el proyecto tomando como única fuente de verdad `archivosReto/` (PDF de la primera evaluación + DOCX del Tema 8 MongoDB), con conclusiones propias e independientes.
**Relación con la auditoría de Luna** (`auditoria_estres_2026-10-31.md`, rev. 2): la he usado como mapa, no como veredicto. Confirmo con sondas propias lo que suscribo (§4), corrijo lo que no (§5) y aporto hallazgos que ella no tiene (§3). Este documento la complementa; no la sustituye.
**Foco pedido:** fase de extracción + transformación al 10/10. Infraestructura, Kafka y MongoDB constan como no hechos y no se evalúan.

**Método:** extracción de texto íntegro del PDF (4 páginas) y del DOCX (104 párrafos, 15 tablas) con `pypdf`/`python-docx`; 9 sondas de solo lectura sobre `data/`, `extract/`, `transform/`, `tests/` y `openspec/`; ejecución completa de la batería (`66 passed`). No se ha reejecutado el pipeline (habría tocado gold) ni se ha descargado nada (el raw está congelado).

---

## 1. Lo que la fuente de verdad exige (y lo que no)

### 1.1. El PDF puntúa 12 criterios, no 18

La rúbrica del PDF tiene tres tablas con escala 0/3/7/10:

| Bloque | Criterios con escala |
|---|---|
| BDA RA1 | Extracción, HDFS, Kafka, Integración (4) |
| SBD RA3 | Modelado, Operaciones, Consultas, Aggregation (4) |
| SBD RA4 | Gráficos, Datos utilizados, Presentación, Interpretación (4) |

**"Formato JSON o CSV", "Limpieza", "Salarios/población", "Transformaciones", "Todo en Python" y "Resultado final: municipios y por qué" NO tienen fila en ninguna tabla.** Aparecen como *objetivos*, *requisitos técnicos* o *entregables*: se cumplen o no se cumplen, no se puntúan de 0 a 10. Los "18 criterios" de `openspec/specs/contrato-reto/spec.md` son una extensión razonable del equipo, pero **no es lo que el tribunal puntúa fila por fila**. Consecuencia directa: el relato "3 de 18" mezcla dos naturalezas distintas y dramatiza la fase de datos más de lo que la rúbrica hace.

### 1.2. Qué significa 10/10 en la fase de datos, según el PDF

| Exigencia del PDF | Dónde vive | Estado |
|---|---|---|
| Fila *Extracción*: "Automatiza API **y** scraping" | escala 0–10 | exige ambas cosas automatizadas |
| Requisito BDA: "Gestión de datos en formato JSON o CSV" | binario | los 60 JSON + 127 CSV cumplen el formato |
| Objetivo 2: salarios, población "u otros indicadores" | binario | salarios (OVJ/INE) + población + paro + 10 fuentes más |
| Requisito SBD: "Limpieza de datos incompletos, duplicados o incorrectos" | binario | duplicados 0; incompletos e incorrectos: ver §3 |
| Requisito SBD: "Transformaciones mediante operaciones de MongoDB" | binario | **no hecho** (es fase Mongo, declarado pendiente) |
| Entregable: "Datos: ficheros originales en HDFS y MongoDB" | binario | **no hecho** (fase siguiente) |
| Resultado final: "demostrar con datos reales qué municipios ofrecen mejores posibilidades de emancipación y explicar por qué; conclusiones respaldadas por los datos" | binario, **pero es la pregunta del reto** | los datos para responderla existen; la respuesta defendible, no (§3, C-01) |

**Mi conclusión:** el techo honesto de esta fase es la fila de Extracción al 10 + todos los requisitos de datos cumplidos de forma *demostrable*, más una base analítica que no invalide la respuesta final. El plan de Luna (`plan_10_10_datos_2026-10-31.md`) apunta bien; este documento dice qué le falta y qué le sobra.

### 1.3. Lo que el DOCX añade (y nadie había cruzado con el proyecto)

El DOCX no es contexto: es la mitad de la nota futura. Lo relevante para la fase actual:

- **No hay modelo único correcto** ("un equipo puede trabajar con alquiler, otro con compraventa…"). La presión por "el esquema perfecto" sobra; lo que se evalúa es justificación, no conformidad.
- **Limpieza y transformaciones DEBEN hacerse con PyMongo** ("La limpieza y transformación de la información deberá realizarse utilizando operaciones de MongoDB desde Python"). Esto cambia el plan de fase: parte de la limpieza actual en pandas tendrá que *re-hacerse o re-demostrarse* en Mongo. Limpiar hoy solo en pandas no cierra el requisito; lo adelanta.
- **Los pipelines deben producir indicadores "directamente relacionados con la emancipación"**, cada uno con finalidad analítica y explicación etapa por etapa. Un `$group` genérico no vale.
- **Índices con `explain()` antes/después** sobre una consulta real; transacciones solo si el modelo las justifica (y si no, hay que *demostrar por qué no*); defensa individual sin depender de soluciones prefabricadas.
- **Checklist final de 11 puntos** (§17): datos reales con procedencia explicable, modelo justificado, carga reproducible, consultas reales, pipelines útiles, índice con `explain`, decisión sobre transacciones, replica/sharding relacionable, código ejecutable vía README, defensa individual, conclusiones respaldadas **que reconozcan sus limitaciones**.

El último punto del checklist es la frase más importante para esta fase: las conclusiones deben reconocer sus limitaciones. Eso convierte C-01 en bloqueante documental, no solo analítico.

---

## 2. Mi veredicto de fase (extracción + transformación)

| Exigencia | Nota propia | Evidencia |
|---|---|---|
| Fila Extracción (API + scraping automatizados) | **9 / 10** | 33 scripts orquestados (`main_ingest` cubre `01–23` + 7 AUX); API Eustat/INE/Udalmap/b5m + scraping 3 portales; HTML crudo conservado (101). Falta el punto: sin `ingestion_manifest.json` no hay prueba de una ejecución completa (C-04) |
| Complementarios (salarios, población, +) | **9 / 10** | OVJ + INE + Eustat + Lanbide + 10 fuentes. Falta el punto: el fichero de salario joven es de los peor documentados (C-07) |
| Formato JSON/CSV | **7 / 10** | formato 100 %; metadata sin esquema único (verificado por mí: 2 sin bloque, 1 sin fuente, 9 sin fecha, 6 sin recuento, 40 sin URL) |
| Limpieza | **6 / 10** | duplicados 0 (verificado); pero ceros imposibles, clip que destruye un 8,57 %, brecha imposible en 248/252, `renta_origen` sin información (C-02) |
| Base para el resultado final | **4 / 10** | solo **28 de 252** municipios tienen renta oficial y muestra mínima (C-01); dos esfuerzos incompatibles (verificado por mí: spearman 0,526, solape top-20 = 1) |
| Trazabilidad e integridad del raw | **9 / 10** | verificado por mí: manifest canónico 316/316, 0 hashes malos, `.FROZEN`, 66 tests en verde |
| Reproducibilidad del pipeline | **4 / 10** | comparto H-19 (verificado por mí: 21/39 en `run_all`); matizo extracción en C-05 |

**Lectura ejecutiva:** la extracción es casi de 10; la transformación produce datos *íntegros pero no siempre correctos*; y la base analítica, tal cual está, **no sostiene la pregunta del reto más que en 28 municipios**. El trabajo que falta para el 10/10 de fase es menos código del que parece y más decisiones documentadas de lo que parece.

---

## 3. Hallazgos propios (no están en la auditoría previa)

### C-01 (crítico). El núcleo defendible son 28 municipios, no 252

Crucé `metodo_imputacion` del alquiler (159 oficial / 93 IDW, verificado) con el recuento real de anuncios unificados (759):

| | ≥ 5 anuncios | 1–4 anuncios | 0 anuncios |
|---|---:|---:|---:|
| Renta **oficial** | **28** | 42 | **89** |
| Renta **IDW** | **0** | 13 | 80 |

- **Cero** municipios IDW tienen muestra mínima: cualquier ranking que incluya IDW ordena municipios sin mercado observado.
- **89 municipios con renta oficial no tienen ni un anuncio**: la renta oficial existe, pero no hay oferta visible. Son analizables en precio oficial, no en mercado.
- Solo **28 de 252 (11 %)** tienen las dos cosas: precio oficial + muestra mínima (≥ 5).

Esto es más grave y más preciso que "el top-20 es IDW": significa que la respuesta a "¿dónde puede emanciparse un joven?" solo puede darse con respaldo completo en 28 municipios, y que el informe necesita tres niveles de evidencia (núcleo / oficial sin muestra / IDW), no un ranking único. El DOCX lo respalda: *"¿qué limitaciones tienen los datos y cómo afectan a las conclusiones?"* es pregunta obligada de defensa.

### C-02 (alto). `renta_origen` no informa de nada

`data/raw/renta_municipal_completa.csv`, columna `renta_origen`: **valor único `Eustat+INE_Atlas` en las 252 filas** (verificado). Y `test_crudos.py` lo "verifica" así:

```python
assert set(rc["renta_origen"].unique()) == {"Eustat+INE_Atlas"}
```

El test comprueba presencia, no validez: una columna constante pasa como "origen transparente". Nadie puede saber qué filas son Eustat oficial y cuáles relleno del Atlas INE. La trazabilidad de la *denominador* del esfuerzo joven es, hoy, una etiqueta decorativa.

### C-03 (alto). La dim vive en dos capas a la vez

`data/raw/dim_municipios.json` existe (252 filas, 2026-10-27) y **7 extractores la leen como maestro** (`ine_atlas_renta`, `euskadi_geo`, `educacion_centros`, `19_udalmap…`, etc.). El productor actual (`transform/dim_municipios.py`) escribe en `data/procesado/`. Verifiqué que ambas copias coinciden hoy (mismos 252 códigos, suma 843, mismas tipologías), pero:

- nada garantiza la sincronía: la copia de raw está congelada y la de procesado se regenera;
- si `dim_municipios.py` cambia mañana, la extracción seguirá leyendo la copia vieja;
- el docstring del productor dice `Salida: data/raw/dim_municipios.json` cuando el código escribe en `PROC_DIR`: la documentación del propio script describe otro estado.

Es un defecto arquitectónico silencioso: la lista maestra de municipios para *extraer* depende de un fichero congelado en la capa equivocada.

### C-04 (alto). `main_ingest.py` promete un manifest que no existe

El orquestador de extracción genera `data/raw/ingestion_manifest.json` "con un registro por cada fichero tocado: nombre, timestamp, SHA-256, nº de registros y estado". Búsqueda en todo el repo: **el fichero no existe**. O no se ejecutó la ingesta completa en esta copia, o se borró. Sin él, la fila de Extracción al 10 no tiene prueba de ejecución end-to-end: hay scripts y hay datos, pero falta el acta.

### C-05 (matiz a favor). La extracción SÍ está orquestada

`main_ingest.py:_live` ejecuta por glob `[0-9][0-9]_*.py` (cubre del 01 al 23) más 7 AUX (`educacion_centros`, `salud_centros`, `entity_resolution`, `euskadi_geo`, `fotocasa_detalle`, `ine_atlas_renta`, `udalmap_empleo`). Es decir: **los 33 extractores están cubiertos**. El problema de orquestación es exclusivo de `transform/` (H-19, que confirmo: 21/39). La narrativa "nada es reproducible" es injusta con la extracción; el plan debe decirlo así.

### C-06 (medio). Tres escritores, no dos, tocan la salida enriquecida

Además de `calcular_renta_joven.py:116` y `calcular_tension_social.py:54`, `transform/generar_municipios_faltantes_93.py` y `generar_emancipacion_tier3_93.py` existen fuera del orquestador y operan sobre tablas gold. El riesgo H-13 es correcto pero incompleto: no solo el orden importa, también hay productores fantasma fuera del pipeline declarado.

### C-07 (medio). El salario joven, clave del reto, es de lo peor documentado

`ovj_salario_joven_2024.json` es uno de los **2 JSON sin bloque `metadata`** (verificado). El dato que responde a "¿puede un joven independizarse con su salario?" —el 1.381 € que alimenta `esfuerzo_ovj_individual_pct`— no tiene fuente, fecha ni recuento en su propio fichero. Para el criterio de complementarios al 10, este fichero concreto es el primero que hay que normalizar, no uno cualquiera.

### C-08 (medio). `AGENT.md` describe otro proyecto

El contexto que leen los agentes dice: "Raw inmutable congelado (**314** archivos), silver regenerado (**96**), **59** tests en verde". Medido hoy: 319, 113, 66. Un agente (o un revisor) que trabaje desde esas cifras tomará decisiones con un 5–15 % de error en los inventarios. El drift documental no está solo en `project.md`.

### C-09 (bajo, pero operativo). Hay 27 informes de auditoría y se contradicen

`openspec/audit/` contiene 27 `.md` (la mayoría del 28-10). Ejemplos de contradicción interna que un tribunal detectaría: readiness 8,5/10 "GO" frente a 3 criterios cubiertos; "869 anuncios" frente a 759; "distancias truncadas" frente a 180.488 pares completos; "`EQUIVALENCIAS_EXTRA` pendiente" frente a inexistente. Cada auditoría nueva sin retirar o versionar la anterior **aumenta** la superficie de contradicción. Propuesta: `openspec/audit/_historico/` para todo lo anterior a la rev. 2 + este documento como índice vigente.

---

## 4. Lo que confirmo de la auditoría previa (con sonda propia)

| Afirmación de Luna (rev. 2) | Mi verificación |
|---|---|
| Manifest canónico 316/316, 0 fallos | **Confirmado por mí** (sha256 de los 316 + `pytest` 66 en verde) |
| Metadata: 2 sin bloque, 1 sin fuente, 9 sin fecha, 6 sin recuento, 40 sin URL | **Confirmado por mí**, recuento campo a campo independiente |
| Ceros de paro en 3 municipios; Usansolo 13/151,7 → publicado 0,00 % por el clip | **Confirmado**: cap `×4` sobre `tasa_paro=0` (líneas 101-105); Aramaio 1/54,8 → 0,00 % por la misma vía |
| 8 ceros de desempleo juvenil (6 reales + 2 artefactos), 53 nulos | **Confirmado** (8 y 53 exactos) |
| Brecha ocupación−actividad positiva en 248/252 | **Confirmado exacto** (mediana +5,05) |
| Dos esfuerzos: spearman 0,53, solape top-20 = 1, dif. mediana 3,9 / máx. 26,3 | **Confirmado por mí**: 0,526 / 1 / 3,9 / 26,3 |
| `n_anuncios` 843 vs 759; dim corre antes que unificación | **Confirmado** (845 crudos − 2 sin código = 843) |
| 18/39 scripts fuera de `run_all` | **Confirmado por mí** (21 orquestados, 18 fuera) |
| Dos escritores de `dim_municipios_enriquecido.csv` | **Confirmado** (líneas 116 y 54); añado C-06 |
| Tests circulares (P-08, formato 1/60, limpieza 1 columna) | **Confirmado por lectura propia** del `test_contrato.py` completo; añado: `test_p06` solo comprueba que los `.py` acaban en `.py`, y los umbrales `MIN_*` (400 anuncios, 150 municipios) pasarían con la mitad de los datos actuales |

Matiz mío a H-03: con la regla reproducida al 100 % (252/252), el recuento real solo mueve **3 municipios** de tipología (Abanto y Ciérvana 31→29 cae de Nivel1 a Nivel2; Ayala/Aiara 30→29 cae de Nivel1 a Nivel3; Güeñes 0→10 sube de Nivel3 a Nivel2). El daño del 11 % no es masivo en clasificación, pero toca exactamente el umbral de 30 en dos municipios Nivel1. Hay que corregirlo igual, pero sin alarmismo: son 3 filas, no "la clasificación".

---

## 5. Dónde discrepo de la auditoría previa

1. **El marco de "3 de 18".** El PDF puntúa 12 filas; formato, limpieza, complementarios, transformaciones, Python y conclusiones son requisitos/entregables, no filas de 0–10. El semáforo correcto para la fase es el de §2, no el de 18. Esto no sube la nota: la baja por otro lado (C-01).
2. **"Cambia la clasificación de municipios concretos" (H-03).** Correcto en dirección, exagerado en magnitud: son 3 municipios (verificado). El argumento fuerte no es la tipología, es C-01.
3. **Prioridad del plan.** El plan de Luna pone el orquestador (WP-01) primero por reproducibilidad. Yo lo pongo primero por otro motivo: **sin WP-01 ningún otro arreglo es verificable dos veces**, y la defensa del DOCX exige reproducibilidad ejecutable ("README + código ejecutable"). Coincidimos en el orden, discrepamos en el porqué, y el porqué importa para defenderlo.
4. **Falta en su plan:** C-02 (`renta_origen` constante), C-03 (dim en raw), C-04 (`ingestion_manifest`), C-07 (metadata del salario primero), C-09 (archivar auditorías viejas) y la advertencia del DOCX de que **la limpieza en pandas no cuenta como limpieza del reto**: la fase Mongo exigirá re-hacerla con PyMongo, así que la limpieza actual debe diseñarse ya como reglas portables (predicados documentados, no solo celdas corregidas).

---

## 6. Lo que falta para el 10/10 de la fase (operativo)

Suma a `plan_10_10_datos_2026-10-31.md` estos cinco paquetes; el resto del plan lo suscribo.

| # | Paquete | Cierra / alimenta | Esfuerzo |
|---|---|---|---|
| WP-15 | `renta_origen` por fila: re-ejecutar el merge Eustat+Atlas guardando el origen real por municipio (`Eustat` / `INE_Atlas`), o declararlo imposible y marcar toda la columna como no fiable | Limpieza + C-02 | 1,5 h |
| WP-16 | Sacar `dim_municipios.json` de `data/raw`: los extractores leen el maestro desde `data/procesado/` (o se congela una copia con versión y checksum referenciado) | Trazabilidad + C-03 | 1 h |
| WP-17 | Regenerar `ingestion_manifest.json` ejecutando `main_ingest.py` y archivarlo como acta de extracción (con fecha, SHAs y estados) | Extracción 10/10 + C-04 | 2 h (incluye re-ejecución supervisada) |
| WP-18 | Metadata primero del salario: `ovj_salario_joven_2024.json` y `emancipacion_juventud_resumen.json` normalizados antes que ningún otro fichero | Complementarios + C-07 | 30 min |
| WP-19 | Congelar la historia de auditorías: mover a `_historico/` todo lo anterior a rev. 2, dejar como vigentes solo rev. 2, plan y este documento | Defensa + C-09 | 30 min |
| WP-20 | Reglas de limpieza portables a PyMongo: reescribir cada regla (ceros, clip, brecha, duplicados) como predicado `{campo, condición, acción}` en un `docs/reglas_limpieza.md` que la fase Mongo pueda ejecutar tal cual | Requisito SBD + §1.3 | 2 h |

**Definición de 10/10 de fase** (verificable en 5 minutos ante el tribunal):

```bash
# 1. La extracción está completa y registrada (WP-17: regenerar el acta)
test -f data/raw/ingestion_manifest.json          # hoy NO existe: bloquea el 10
# 2. El pipeline se reconstruye solo y deja manifest (WP-01)
python transform/run_all.py --check               # todo OK, sin "faltan salidas"
# 3. La batería cubre los invariantes (WP-14)
python -m pytest -q                               # ~85 passed
# 4. El gate de fase, verde: es lo que se enseña en la demo
python openspec/audit/verificar_fase_datos.py    # 15/15 OK, exit 0
```

más una pregunta oral respondida sin dudar: *"¿en cuántos municipios podéis defender la respuesta con precio oficial y muestra mínima?"* → **28, listados en `cobertura_anuncios.csv` con su nivel de fiabilidad**.

---

## 7. Riesgos para la defensa (preguntas que caerán, según el DOCX)

| Pregunta (del checklist §17) | Respuesta hoy | Riesgo |
|---|---|---|
| "¿De dónde sale este dato?" (procedencia) | 40 JSON sin URL; salario sin metadata | **Alto**: C-07 + metadata |
| "¿Qué limitaciones tienen los datos y cómo afectan?" | Sin documentar por niveles | **Alto**: C-01 sin publicar |
| "¿Por qué este municipio sale primero?" | Depende de qué esfuerzo se use (solape 1/20) | **Alto**: indicador sin declarar |
| "¿Qué es cero y qué es sin dato?" | 3 ceros validados como buenos; 2 tasas anuladas por el clip | **Medio-alto** |
| "¿Se puede reejecutar?" | Extracción sí; transformación no (18 fuera) | **Medio-alto** |
| "Si el modelo no necesita transacciones, ¿por qué?" | Nadie lo ha analizado | Medio (fase Mongo, pero conviene ir pensando) |
| "¿Qué índice crearíais y qué demuestra el explain?" | Sin consultas Mongo todavía | Bajo hoy (fase Mongo) |

---

## 8. Limitaciones de esta contrauditoría

- No reejecuté extracción (red + freeze) ni transformación (reescribiría gold): todo es lectura y recomputación sobre los artefactos existentes.
- No evalué HDFS/Kafka/MongoDB: constan como no implementados y así se asume.
- No revisé visualmente dashboards ni los 13 PNG.
- Las cifras dependen del estado actual de `data/`; si se regenera, repetir las 9 sondas (todas están descritas arriba y son reejecutables en minutos).
- Instalé `pypdf` y `python-docx` en el `.venv` solo para leer `archivosReto/`; no afectan al proyecto.

## 9. Historial

| Rev. | Fecha | Contenido |
|---|---|---|
| 1 | 2026-10-31 | Contrauditoría inicial: fuente de verdad extraída íntegra, 9 hallazgos propios (C-01…C-09), confirmaciones y discrepancias con la rev. 2 de Luna, 6 paquetes adicionales (WP-15…WP-20) |
