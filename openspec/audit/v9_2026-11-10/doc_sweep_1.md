# Doc sweep 1 — modelo_mongodb + matriz_indicadores + informe_capacidad_mongo (W4.1)

**Fecha:** 2026-11-10 · **Unidad:** W4.1 (Ronda 4, agente D2) · **Criterios:** 9, 12, 17, 18
**Entrada:** `docs/modelo_mongodb.md`, `docs/matriz_indicadores.md`, `docs/informe_capacidad_mongo.md`
**Cifras vigentes (baseline v9):** 594 anuncios; 30 colecciones (16 vivas + 14 `__backup`); 11 pipelines; 8 CSV `mongo_*`; comparativa 204/126/50/39; explain IXSCAN (depende del filtro); 237 tests (235 passed, 2 skipped); 188 silver; 354 SHA raw.
**Guardrails:** solo lectura. No se modificó código, datos, Mongo, HDFS ni Kafka; no commit/push; no instalación de dependencias. Única escritura: este informe.

---

## 1. Método y evidencia

**Ejecutado (read-only, herramienta real):**
- `pymongo` read-only sobre `localhost:27017` `vivienda_euskadi`: `list_collection_names`, `estimated_document_count`, `count_documents`, `aggregate`, `list_indexes`, `collstats`, `explain` (vía `db.command("explain", …, verbosity="executionStats")`).
- `sha256sum` de los 5 CSV de la huella de `matriz_indicadores.md`.
- `ls` / `wc -l` de `data/resultados/mongo_*.csv`.
- `grep` de `PIPELINE_ORDER` / `EXPORTS_*` en `analysis/run_analisis_mongo.py`; conteo de `^def pipeline` en `analysis/mongo_aggregations.py`.
- Lectura de `analysis/comparativa_mongo.py`, `analysis/mongo_indexes.py`, `tests/test_mongo.py`, `storage/load_mongo.py`.
- `json.load` de `data/procesado/udalmap_extendido_normalizado.json` (conteos por campo).

**Solo leído:** `docs/modelo_mongodb.md`, `docs/matriz_indicadores.md`, `docs/informe_capacidad_mongo.md`, `00_baseline_v9.md`, `plan_ejecucion_v9_rondas_2026-11-10.md`, `AGENT.md`, `rubrica_reextraida.md`.

**No ejecutado:** `load_all`, `clean_all`, `run_analisis_mongo`, productor Kafka, escritura en Mongo/HDFS/Kafka. No se crearon ni se drogaron índices (prohibido escribir en Mongo).

**Escala de severidad:**
- **P0:** integridad de datos o seguridad; resultados incorrectos.
- **P1:** afirmación documentada no reproducible / estado vivo contradice el baseline / cifra imposible.
- **P2:** cifra obsoleta en el doc (contradice el baseline v9).
- **P3:** inconsistencia interna menor, huella histórica obsoleta, omisión.

---

## 2. Resumen de hallazgos

| ID | Sev. | Criterio | Fichero | Título |
|---|---|---|---|---|
| DS1-01 | **P1** | C9 (+C13) | modelo_mongodb.md | Los 4 índices de `anuncios` no existen en vivo |
| DS1-02 | P2 | C9 | modelo_mongodb.md | `anuncios` 759 → 594 |
| DS1-03 | P2 | C9 | modelo_mongodb.md | Geo: 424 de 759 → 424 de 594; nulos 335 → 170 |
| DS1-04 | P2 | C9 | modelo_mongodb.md | 14+13 colecciones → 16+14 |
| DS1-05 | P2 | C12 | modelo_mongodb.md | 10 pipelines → 11 |
| DS1-06 | P2 | C12 | modelo_mongodb.md | 5 CSV → 8 CSV |
| DS1-07 | P2 | C18 | modelo_mongodb.md | Comparativa 173/113/40 → 204/126/50/39 |
| DS1-08 | P2 | C9 (+C13) | modelo_mongodb.md | explain: 759 → 594 y IXSCAN no reproducible |
| DS1-09 | P3 | C9 | modelo_mongodb.md | Tabla de colecciones incompleta |
| DS1-10 | P3 | C9 | modelo_mongodb.md | Listado L160 internamente inconsistente |
| DS1-11 | P2 | C9/C17 | modelo_mongodb.md | `udalmap_extendido`: coberturas 123/150/30/38/67/15 → 252 cada una |
| DS1-12 | P2 | C12 | matriz_indicadores.md | 10 pipelines → 11 |
| DS1-13 | P2 | C18 | matriz_indicadores.md | Comparativa 173/113/40 → 204/126/50/39 |
| DS1-14 | P3 | C12 | matriz_indicadores.md | Huella SHA: 3 de 5 no cuadran con el disco |
| DS1-15 | P3 | C12 | matriz_indicadores.md | 9 pipelines originales → 11 |
| DS1-16 | P3 | C17 | matriz_indicadores.md | Paro 249/252 → 252/252 |
| DS1-17 | P2 | C9 | informe_capacidad_mongo.md | 14+13 colecciones → 16+14 |
| DS1-18 | P2 | C9 | informe_capacidad_mongo.md | `anuncios` 759 → 594 |
| DS1-19 | P2 | C18 | informe_capacidad_mongo.md | Comparativa 173/113/40 → 204/126/50/39 |
| DS1-20 | P2 | C18 | informe_capacidad_mongo.md | «3 municipios» → el CSV tiene 4 filas |
| DS1-21 | P2 | C18 | informe_capacidad_mongo.md | 83 municipios con anuncios → 64 |
| DS1-22 | P2 | C18 | informe_capacidad_mongo.md | 737/759 con habitaciones → 579/594 |
| DS1-23 | P2 | C18 | informe_capacidad_mongo.md | 55 con 1–4 y 169 con 0 → 51 y 188 |
| DS1-24 | P2 | C17 | informe_capacidad_mongo.md | provenance 7/13 vs 13/13 vs 16/16 |
| DS1-25 | P3 | C17 | informe_capacidad_mongo.md | 3 municipios sin paro válido → 0 |

**Recuento: P0 = 0 · P1 = 1 · P2 = 18 · P3 = 6.**

---

## 3. Hallazgos detallados

### 3.1 `docs/modelo_mongodb.md`

#### DS1-01 (P1) — Los 4 índices de `anuncios` no existen en vivo
- **Fichero:línea:** `docs/modelo_mongodb.md:44-47` (definición), `:54-55` (efecto), `:117-142` (evidencia explain), `:136-142` (geo/multikey/parcial).
- **Cita literal:** L44 «- `anuncios`: `{ ubicacion.codigo_ine: 1, modalidad: 1, precio_eur: 1 }` (ESR).» · L45 «- `anuncios`: `{ ubicacion.coordenadas: "2dsphere" }` (sparse).» · L46 «- `anuncios`: `{ portal: 1, id_anuncio: 1 }` único.» · L47 «- `anuncios`: `{ equipamiento: 1 }` multikey.»
- **Cifra correcta:** `anuncios` tiene **solo `_id_`**. Ejecutado: `[ix["name"] for ix in db.anuncios.list_indexes()]` → `['_id_']`; `db.command("collstats","anuncios")["indexSizes"]` → `{'_id_': 24576}`. Los 4 índices no existen. Los índices de `municipios`, `alquiler_municipal`, `etxebide_promociones` y `certificados_energeticos` sí están presentes.
- **Severidad:** P1.
- **Impacto:** la evidencia explain del doc (COLLSCAN→IXSCAN) no es reproducible; las afirmaciones de índice ESR/2dsphere/multikey son falsas en el estado vivo; el baseline v9 §3 también los da por presentes (contradicción vivo vs baseline). No se arregló (guardrail: prohibido escribir en Mongo).

#### DS1-02 (P2) — `anuncios` 759 → 594
- **Fichero:línea:** `docs/modelo_mongodb.md:11,40,129,140,162,164,170,172,176`.
- **Citas literales:** L11 «| `anuncios` | 759 | `ObjectId` | Anuncios unificados …» · L40 «424 de 759 anuncios …» · L129 «totalDocsExamined=759» · L140 «(759 documentos)» · L162 «`anuncios` 759, …» · L164 «424 de 759» · L170 «conteo 759 invariante» · L172 «deja prod en 759» · L176 «759 intacto».
- **Cifra correcta:** **594** (ejecutado: `db.anuncios.estimated_document_count`).
- **Severidad:** P2.
- **Impacto:** el 759 es la cifra histórica pre-v5; todos los recuentos derivados (explains, coberturas, invariantes) quedan falsos.

#### DS1-03 (P2) — Geo: denominador y nulos
- **Fichero:línea:** `docs/modelo_mongodb.md:40,164`.
- **Citas literales:** L40 «424 de 759 anuncios con `{"type":"Point","coordinates":[lon,lat]}` real …» · L164 «… (portal `fotocasa`, 424 de 759). Medición: `db.anuncios.countDocuments({"ubicacion.coordenadas": {"$type": "object"}})` devuelve 424 y `db.anuncios.countDocuments({"ubicacion.coordenadas": null})` devuelve 335.»
- **Cifra correcta:** 424 con geo (sigue igual) y **170** con `null` (ejecutado). Denominador: **594**. El 335 era 759−424.
- **Severidad:** P2.
- **Impacto:** la proporción de anuncios con geo pasa de 424/759 (55,9 %) a 424/594 (71,4 %); el doc subestima la cobertura geo.

#### DS1-04 (P2) — Colecciones 14+13 → 16+14
- **Fichero:línea:** `docs/modelo_mongodb.md:111,160`; `docs/informe_capacidad_mongo.md:3,8`.
- **Citas literales:** L111 «14 colecciones cargadas con PyMongo (+13 `__backup`)» · L160 «(14 colecciones; además hay 13 `__backup` posteriores que no se listan)» · informe L3 «14 colecciones principales (+13 `__backup` posteriores)».
- **Cifra correcta:** **30 = 16 vivas + 14 `__backup`** (ejecutado: `list_collection_names`). Las 2 vivas que faltan en el doc: `anuncios_habitaciones_unificados`, `anuncios_habitaciones_unificados_bigdata`.
- **Severidad:** P2.
- **Impacto:** el inventario de colecciones del doc no coincide con el vivo; las 2 colecciones nuevas no aparecen en cualquier tabla.

#### DS1-05 (P2) — 10 pipelines → 11
- **Fichero:línea:** `docs/modelo_mongodb.md:111,180`; `docs/matriz_indicadores.md:19`.
- **Citas literales:** L111 «10 pipelines en `analysis/mongo_aggregations.py` (… `pipeline_tier_por_municipio`)» · L180 «reutilizando los 10 pipelines de `analysis/mongo_aggregations.py`» · matriz L19 «10 pipelines en `analysis/mongo_aggregations.py`: indicadores, alquiler, modalidades, top esfuerzo, esfuerzo sexo, accesibilidad extendida, udalmap_osrm, vpo promociones, vpo terminadas, tier por municipio.»
- **Cifra correcta:** **11** (`PIPELINE_ORDER`, `analysis/run_analisis_mongo.py:49-61`; 11 defs `^def pipeline` en `analysis/mongo_aggregations.py`). El 11.º es `pipeline_habitaciones_por_municipio`.
- **Severidad:** P2.
- **Impacto:** la lista del doc nombra 10 y omite `habitaciones`; la cifra de pipelines está obsoleta en los 2 ficheros.

#### DS1-06 (P2) — 5 CSV → 8 CSV
- **Fichero:línea:** `docs/modelo_mongodb.md:180-188`.
- **Citas literales:** L180 «5 pipelines a CSV canónico en `data/resultados/` reutilizando los 10 pipelines …» · L188 «El exportador general es `exportar_cinco_csv` / `exportar_csv` (`analysis/run_analisis_mongo.py`); `exportar_tres_csv` se mantiene por compatibilidad y delega en el general con `EXPORTS_3`.»
- **Cifra correcta:** **8** CSV `mongo_*` (ejecutado: `ls data/resultados/mongo_*.csv`): `mongo_accesibilidad_extendida.csv`, `mongo_alquiler_por_municipio.csv`, `mongo_esfuerzo_por_municipio.csv`, `mongo_habitaciones_por_municipio.csv`, `mongo_modalidades.csv`, `mongo_tier_confianza.csv`, `mongo_vpo_por_municipio.csv`, `mongo_vpo_terminadas_por_municipio.csv`. `EXPORTS_8` en `analysis/run_analisis_mongo.py:101-102`. El doc omite `mongo_habitaciones_por_municipio.csv`, `mongo_tier_confianza.csv` y `mongo_vpo_terminadas_por_municipio.csv`.
- **Severidad:** P2.
- **Impacto:** la cifra «5 CSV canónicos» está obsoleta; el exportador general vigente es `EXPORTS_8`/`CSV_POR_PIPELINE`, no `exportar_cinco_csv`.

#### DS1-07 (P2) — Comparativa 173/113/40 → 204/126/50/39
- **Fichero:línea:** `docs/modelo_mongodb.md:115`.
- **Cita literal:** L115 «`comparativa_3_municipios_mongo.csv` (4: Bilbao 173, Donostia 113, Getxo 40, Vitoria-Gasteiz 39).»
- **Cifra correcta:** Bilbao **204**, Donostia **126**, Getxo **50**, Vitoria-Gasteiz **39** (ejecutado: `cat data/resultados/comparativa_3_municipios_mongo.csv`).
- **Severidad:** P2.
- **Impacto:** la comparativa del doc queda desvirtuada; los márgenes entre municipios cambian.

#### DS1-08 (P2) — explain: 759 → 594 y IXSCAN no reproducible
- **Fichero:línea:** `docs/modelo_mongodb.md:129-130`.
- **Citas literales:** L129 «- Antes (sin índice ESR): `COLLSCAN`, `nReturned=1`, `totalDocsExamined=759`, `totalKeysExamined=0`.» · L130 «- Después (con índice ESR): `IXSCAN`, `nReturned=1`, `totalDocsExamined=1`, `totalKeysExamined=1`.»
- **Cifra correcta:** con 594 docs, un COLLSCAN examina **594** (ejecutado: `explain` del filtro del doc → `COLLSCAN`, `nReturned=0`, `totalDocsExamined=594`). El índice ESR no existe (DS1-01), así que el «después IXSCAN» no es reproducible; el filtro del doc devuelve **0** docs (no 1) en vivo.
- **Severidad:** P2 (la cifra 759→594) + P1 asociado a DS1-01.
- **Impacto:** la demostración de rendimiento del doc no se sostiene con el estado vivo.

#### DS1-09 (P3) — Tabla de colecciones incompleta
- **Fichero:línea:** `docs/modelo_mongodb.md:8-22`.
- **Cita literal:** la tabla tiene 13 filas; no incluye `vpo_municipal` (que el propio doc cita en L111) ni las 2 colecciones `anuncios_habitaciones_unificados*`.
- **Cifra correcta:** 16 colecciones vivas (ejecutado).
- **Severidad:** P3.
- **Impacto:** el modelo de datos documentado no refleja el vivo; `vpo_municipal` aparece en el texto pero no en la tabla.

#### DS1-10 (P3) — Listado L160 internamente inconsistente
- **Fichero:línea:** `docs/modelo_mongodb.md:160`.
- **Cita literal:** «(14 colecciones; además hay 13 `__backup` posteriores que no se listan)» — pero el listado incluye 16 nombres (14 vivas + 2 `__backup`: `indicadores__backup`, `municipios__backup`).
- **Severidad:** P3.
- **Impacto:** el recuento del propio listado no cuadra con su contenido.

#### DS1-11 (P2) — `udalmap_extendido`: coberturas
- **Fichero:línea:** `docs/modelo_mongodb.md:20`.
- **Cita literal:** «| `udalmap_extendido` | 252 | `codigo_ine` | 6 indicadores alto valor (123/150/30/38/67/15). |»
- **Cifra correcta:** los 6 campos (`accesibilidad_municipio`, `densidad_comercial_minorista`, `densidad_viviendas_suelo_residencial`, `deuda_viva_municipal_pc`, `rotacion_contractual`, `tiempo_acceso_capital_th`) tienen **252/252** no nulos en Mongo (ejecutado) y 252/252 en la plata `data/procesado/udalmap_extendido_normalizado.json` (ejecutado). Las cifras 123/150/30/38/67/15 no corresponden al estado vivo.
- **Severidad:** P2.
- **Impacto:** la cobertura de los 6 indicadores está sobreestimada en el doc; cualquier conclusión que use esas coberturas es errónea.

### 3.2 `docs/matriz_indicadores.md`

#### DS1-12 (P2) — 10 pipelines → 11
- **Fichero:línea:** `docs/matriz_indicadores.md:19`.
- **Cita literal:** «10 pipelines en `analysis/mongo_aggregations.py`: indicadores, alquiler, modalidades, top esfuerzo, esfuerzo sexo, accesibilidad extendida, udalmap_osrm, vpo promociones, vpo terminadas, tier por municipio.»
- **Cifra correcta:** **11** (añade `pipeline_habitaciones_por_municipio`; `PIPELINE_ORDER`).
- **Severidad:** P2.
- **Impacto:** la lista de pipelines del doc nombra 10 y omite `habitaciones`.

#### DS1-13 (P2) — Comparativa 173/113/40 → 204/126/50/39
- **Fichero:línea:** `docs/matriz_indicadores.md:32`.
- **Cita literal:** «Verificacion: `wc -l` = 253/253/3, comparativa 5 (cabecera + Bilbao 173, Donostia 113, Getxo 40, Vitoria-Gasteiz 39, `codigo_ine` 5 digitos, paro Lanbide no nulo), terminadas 252 …»
- **Cifra correcta:** 204/126/50/39 (ejecutado: CSV).
- **Severidad:** P2.
- **Impacto:** la verificación de la huella queda falsa en los recuentos.

#### DS1-14 (P3) — Huella SHA: 3 de 5 no cuadran con el disco
- **Fichero:línea:** `docs/matriz_indicadores.md:26-30`.
- **Citas literales:** L26 «`mongo_esfuerzo_por_municipio.csv` | 253 | `731d163a956687df1fd1f2fcba1808451de78f4da8ce71676c5e9546ce334c83`» · L28 «`mongo_modalidades.csv` | 3 | `71a7292623ac4d1695f63f7649ae551ae2557d4167e20935b0a863c4946731ef`» · L29 «`comparativa_3_municipios_mongo.csv` (4 robustos) | 5 | `9dc4e8d34d736e6fb74f16a05d064fb249d398b0ceca8b3b7168c3709d3881bb`».
- **Cifra correcta (sha256sum ejecutado):** esfuerzo `7f813fd61ee6800dacd24a230aaef43a8d97e9dbe1abd0300fa1da5b974f75a3` · modalidades `67e8120a311666d8cb7d3522766e8a19da468da34fb578c900d702bf2d81bcf0` · comparativa `be5d26e36cd4bd8c1bcafbc92b5ab98eec6fd50c83288af8b830c3db17ceda7d`. `mongo_alquiler_por_municipio.csv` (`ff39e852…`) y `mongo_vpo_terminadas_por_municipio.csv` (`d9a512c8…`) sí cuadran. Los ficheros se regeneraron el 2026-11-08 (mtimes) y la huella está fechada 2026-11-06.
- **Severidad:** P3 (huella histórica; el doc no avisa de que los ficheros cambiaron).
- **Impacto:** la huella presentada como verificadora no verifica el disco actual.

#### DS1-15 (P3) — 9 pipelines originales → 11
- **Fichero:línea:** `docs/matriz_indicadores.md:32`.
- **Cita literal:** «Huella agregada de los 9 pipelines originales (`huella_resultados`, SHA-256 con `sort_keys=True`; el 10.º, tier, se añadió después y no entra en esta huella histórica)».
- **Cifra correcta:** **11** pipelines vigentes (el 11.º es `pipeline_habitaciones_por_municipio`).
- **Severidad:** P3.
- **Impacto:** la huella agregada es histórica; el doc no la reactualiza al pipeline 11.

#### DS1-16 (P3) — Paro 249/252 → 252/252
- **Fichero:línea:** `docs/matriz_indicadores.md:9`.
- **Cita literal:** «`tasa_paro_lanbide_pct` … presente en Mongo `municipios.empleo.tasa_paro_lanbide_pct` (249/252; Bilbao 9,71, Donostia 5,82, Getxo 6,40, Vitoria-Gasteiz 8,89)».
- **Cifra correcta:** **252/252** no nulos (ejecutado; min 0,28, max 12,57, ningún cero). Los valores de las 4 capitales sí cuadran.
- **Severidad:** P3.
- **Impacto:** la cobertura del indicador está subestimada; la limitación «3 municipios sin paro válido» no aplica al estado vivo.

### 3.3 `docs/informe_capacidad_mongo.md`

#### DS1-17 (P2) — 14+13 colecciones → 16+14
- **Fichero:línea:** `docs/informe_capacidad_mongo.md:3`.
- **Cita literal:** «> Actualización 2026-11-05 (cierre-auditoria): 14 colecciones principales (+13 `__backup` posteriores): `municipios/anuncios/alquiler_municipal/indicadores/ecvi_compraventa/udalmap_indicadores/udalmap_empleo/osrm_tiempos/emancipacion_juventud/etxebide_solicitudes/udalmap_extendido/etxebide_promociones/certificados_energeticos/vpo_municipal`.»
- **Cifra correcta:** **16 vivas + 14 `__backup`** (ejecutado). Faltan en la lista `anuncios_habitaciones_unificados` y `anuncios_habitaciones_unificados_bigdata`.
- **Severidad:** P2.
- **Impacto:** el alcance del informe no coincide con el vivo.

#### DS1-18 (P2) — `anuncios` 759 → 594
- **Fichero:línea:** `docs/informe_capacidad_mongo.md:8`.
- **Cita literal:** «- Colecciones inspeccionadas: `municipios` (252), `anuncios` (759), `alquiler_municipal` (252), …».
- **Cifra correcta:** **594** (ejecutado).
- **Severidad:** P2.
- **Impacto:** el recuento base del informe queda obsoleto.

#### DS1-19 (P2) — Comparativa 173/113/40 → 204/126/50/39
- **Fichero:línea:** `docs/informe_capacidad_mongo.md:14,87-89,93-95,99`.
- **Citas literales:** L14 «… **4 municipios con n≥30 anuncios** (Bilbao 173, Donostia 113, Getxo 40, Vitoria-Gasteiz 39).» · L87 «| 48020 | Bilbao | 173 | 37,69 | 60,70 | 1695,59 | 850,00 | 9,71 |» · L88 «| 20069 | Donostia / San Sebastian | 113 | 38,17 | 61,48 | 2462,89 | 995,00 | 5,82 |» · L89 «| 48044 | Getxo | 40 | 28,60 | 46,06 | 1527,50 | 887,00 | 6,40 |» · L93 «**Getxo (48044, n=40)**: … precio medio de anuncios tambien el menor (1527,50 EUR) …» · L94 «**Bilbao (48020, n=173)**: … El precio medio de sus anuncios es 1695,59 EUR.» · L95 «**Donostia / San Sebastian (20069, n=113)**: … precio medio de anuncios muy superior (2462,89 EUR).» · L99 «… solo 4 municipios tienen n>=30 anuncios (Bilbao 173, Donostia 113, Getxo 40, Vitoria-Gasteiz 39, fuera del top 3).»
- **Cifra correcta:** 204/126/50/39 (ejecutado: CSV). Precios medios vivos: Bilbao **1716,69**, Donostia **2465,32**, Getxo **1536,04**, Vitoria-Gasteiz **1406,13**. Los del doc (1695,59 / 2462,89 / 1527,50) no cuadran.
- **Severidad:** P2.
- **Impacto:** la tabla y las conclusionas por municipio quedan con cifras pre-v5.

#### DS1-20 (P2) — «3 municipios» → el CSV tiene 4 filas
- **Fichero:línea:** `docs/informe_capacidad_mongo.md:81-89`.
- **Citas literales:** L81 «## Comparativa de 3 municipios robustos desde Mongo (CONCLUSION-01)» · L83 «Generada con `analysis/comparativa_mongo.py` (`comparativa_tres_robustos`): top 3 por `n_anuncios` desde `pipeline_indicadores_municipio`, …».
- **Cifra correcta:** el CSV tiene **4** filas Tier A (204/126/50/39); `comparativa_cuatro_robustos` (`analysis/comparativa_mongo.py:133-143`) es la que escribe 4. El doc se contradice con sus propias L14/L99 (4 robustos).
- **Severidad:** P2.
- **Impacto:** la conclusión «Getxo es el de mejores posibilidades de los tres» se sostiene solo sobre 3 de los 4 municipios robustos; el doc excluye a Vitoria-Gasteiz de la tabla pero lo cuenta en el texto.

#### DS1-21 (P2) — 83 municipios con anuncios → 64
- **Fichero:línea:** `docs/informe_capacidad_mongo.md:48`.
- **Cita literal:** «| C4 | … | Solo 83 municipios con anuncios; 737/759 con habitaciones |».
- **Cifra correcta:** **64** municipios con ≥1 anuncio (ejecutado: `aggregate` por `ubicacion.codigo_ine`; 252−64=188 con 0).
- **Severidad:** P2.
- **Impacto:** la cobertura municipal está sobreestimada en 19 municipios; la limitación «solo 83» no aplica.

#### DS1-22 (P2) — 737/759 con habitaciones → 579/594
- **Fichero:línea:** `docs/informe_capacidad_mongo.md:48`.
- **Cita literal:** «737/759 con habitaciones».
- **Cifra correcta:** **579/594** con `habitaciones` no nulo (ejecutado). 737 > 594, imposible con el total vigente.
- **Severidad:** P2.
- **Impacto:** la cifra es imposible con el total actual; delata una medición pre-v5 no actualizada.

#### DS1-23 (P2) — 55 con 1–4 y 169 con 0 → 51 y 188
- **Fichero:línea:** `docs/informe_capacidad_mongo.md:66`.
- **Cita literal:** «| G2 | n<5 anuncios | … | 55 municipios con 1–4 anuncios; 169 con 0 |».
- **Cifra correcta:** **51** con 1–4 (27+12+6+6) y **188** con 0 (ejecutado).
- **Severidad:** P2.
- **Impacto:** la limitación «n<5 anuncios» no describe el estado vivo; el número de municipios sin anuncios se subestima.

#### DS1-24 (P2) — provenance 7/13 vs 13/13 vs 16/16
- **Fichero:línea:** `docs/informe_capacidad_mongo.md:32,69,70,76`.
- **Citas literales:** L32 «`clean_mongo` 13 cols + `fuente/anio_fuente` en 7/13 (base + nuevas)» · L69 «`fuente/anio_fuente/fecha_extraccion` en 13/13» · L70 «`fuente/fuente_url` en 13/13» · L76 «`fuente/anio_fuente` en 13/13 para G5/G6».
- **Cifra correcta:** **16/16** colecciones vivas con `fuente` y `anio_fuente` (ejecutado; 100 % de docs). El «7/13» es además contradictorio con el «13/13» del mismo doc.
- **Severidad:** P2.
- **Impacto:** la limitación de provenance está mal medida y el doc se contradice a sí mismo; la cobertura real es total.

#### DS1-25 (P3) — 3 municipios sin paro válido → 0
- **Fichero:línea:** `docs/informe_capacidad_mongo.md:39`.
- **Cita literal:** «| B1 | Mayor paro juvenil Lanbide | … | 3 municipios sin paro válido |».
- **Cifra correcta:** **0** nulos y **0** ceros en `empleo.tasa_paro_lanbide_pct` (ejecutado; 252/252 no nulos, min 0,28). El FAIL 07 del baseline (Aramaio 0,28 / Gaintza 1,45 / Usansolo 3,26) son valores bajos, no nulos.
- **Severidad:** P3.
- **Impacto:** la limitación de paro no aplica al estado vivo.

---

## 4. Cobertura de criterios

| Criterio | Cubierto | Hallazgos |
|---|---|---|
| **C9 Modelado MongoDB** | sí | DS1-01, DS1-02, DS1-03, DS1-04, DS1-09, DS1-10, DS1-11, DS1-17, DS1-18 |
| **C12 Aggregation Pipeline** | sí | DS1-05, DS1-06, DS1-12, DS1-14, DS1-15 |
| **C17 Indicadores** | sí | DS1-11, DS1-16, DS1-24, DS1-25 |
| **C18 Respuesta al reto** | sí | DS1-07, DS1-13, DS1-19, DS1-20, DS1-21, DS1-22, DS1-23 |

Criterios adicionales tocados por los hallazgos (fuera de la lista de W4.1): **C13 Índices y rendimiento** (DS1-01, DS1-08).

---

## 5. Ejecutado vs solo leído

**Ejecutado (herramienta real, read-only):**
- `pymongo` sobre `localhost:27017` `vivienda_euskadi`: `list_collection_names`, `estimated_document_count`, `count_documents`, `aggregate`, `list_indexes`, `collstats`, `explain` (vía `db.command`).
- `sha256sum` de los 5 CSV de la huella; `ls`/`wc -l` de `data/resultados/mongo_*.csv`.
- `grep`/`read_file` de `analysis/run_analisis_mongo.py` (`PIPELINE_ORDER`, `EXPORTS_*`), `analysis/mongo_aggregations.py` (defs), `analysis/comparativa_mongo.py`, `analysis/mongo_indexes.py`, `tests/test_mongo.py`, `storage/load_mongo.py`.
- `json.load` + conteos de `data/procesado/udalmap_extendido_normalizado.json`.

**Solo leído:** los 3 ficheros de entrada; `00_baseline_v9.md`; `plan_ejecucion_v9_rondas_2026-11-10.md`; `AGENT.md`; `rubrica_reextraida.md`.

**No ejecutado:** `load_all`, `clean_all`, `run_analisis_mongo`, productor Kafka; ninguna escritura en `data/`, Mongo, HDFS o Kafka; no se crearon ni se drogaron índices; no hubo commit/push; no se instalaron dependencias.

---

## 6. Bloqueos

- **DS1-01 (P1): los 4 índices de `anuncios` no existen en vivo.** No se arregló (prohibido escribir en Mongo). El baseline v9 §3 los registra como presentes (07:29) y el estado actual (≈09:00) es solo `_id_`. Se recomienda que W3.2 (Mongo) y W3.1 (verificación dinámica) contrasten el estado y que el coordinador decida si es un estado transitorio de un agente paralelo o una regresión. Mientras tanto, la evidencia explain de `docs/modelo_mongodb.md` no es reproducible.
- Ningún otro bloqueo.
