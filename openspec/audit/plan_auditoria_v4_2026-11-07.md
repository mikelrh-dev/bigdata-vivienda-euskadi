# Plan de auditoría v4 — doble eje: técnica+rúbrica / datos

Fecha: 2026-11-07
Estado: PLAN (sin ejecutar). No se modifica data/, storage/, extract/, transform/, analysis/ ni MongoDB.
Objetivo: sustituir la "sensación de que está bien" por evidencia re-ejecutada desde cero.

## 0. Principios (no negociables)

1. Umbral literal: 10 solo si se cumple la columna del 10 palabra por palabra. "Casi" = 7.
2. Evidencia triple: comando ejecutado + salida numérica + fichero:línea. Sin las tres, no hay 10.
3. La documentación no es evidencia (P-08). READMEs/guiones no puntúan; puntúan código ejecutado, Mongo real y artefactos regenerados.
4. No verificable ≠ 10. Se marca PENDIENTE con qué falta exactamente para verificarlo.
5. Prueba de falsación: cada 10 frágil lleva anotado qué lo bajaría a 7 (ej. si `ascensor` no está en el array de equipamiento, la demo que lo usa cae).
6. Datos reales (P-01/P-02/P-03/P-05): sin simulados, sin valores tecleados, alquiler de Eustat, alquiler como eje.
7. Waiver ≠ cambio de rúbrica: el waiver "HDFS solo raw" y "Kafka→HDFS, no Kafka→Mongo" se documenta y se dan las dos lecturas (PDF literal / con waiver) pero no se reescribe la rúbrica.
8. Re-auditoría comparativa: cada métrica de datos se compara con la auditoría anterior (antes/después/cambio/veredicto). Sin tabla de comparación, "ha mejorado" no se afirma (skill data-audit).
9. Solo lectura en la auditoría. Las reparaciones van a un backlog separado tras autorización, con triaje de riesgo (risk-if-not-fixed vs implementation risk; SDD completo solo si implementation risk > 5/10).

## 1. Alcance

### Eje A — Técnica + rúbrica (26 criterios)
| Bloque | Criterios | Peso en 1ª eval | Spec |
|---|---|---|---|
| BDA RA1 | 4 (extracción, HDFS, Kafka, integración) | — | almacenamiento-y-streaming, extraccion-datos |
| SBD RA1 | 4 (integración fuentes, construcción conjunto, limpieza, automatización) | 46,7% | extraccion-datos |
| SBD RA3 | 6 (modelado, CRUD, consultas, aggregation, índices, consistencia) | 13,3% | mongodb-y-analisis |
| SBD RA4 | 5 (heterogéneos, automatización análisis, indicadores, respuesta reto, viz) | 40% | presentacion-de-resultados |
| Tema 8 (eval. separada, no se suma) | 7 (modelado 15%, CRUD/limpieza/consultas 15%, aggregation 20%, índices 15%, transacciones 10%, PyMongo profesional 15%, defensa 10%) | separado | contrato-reto §Tema 8 |

Referencia de verdad: `openspec/specs/contrato-reto/spec.md` (357 líneas) + PDF/DOCX en brief/ cotejados contra binario, no contra la transcripción.

### Eje B — Datos (suficiencia y calidad)
Cobertura municipal (252), n≥30, robustez estadística, sesgo urbano/rural, calidad de proxies, mezcla de años, granularidad, integridad de archivos (manifest/BOM/encoding), trazabilidad de fuentes (API/scraping/descarga directa), reproducibilidad de artefactos.

## 2. Fases

### F0 — Preflight (bloqueante, antes de todo)
- [ ] 0.1 Baseline git: `git status --short`, `git log -1` (esperado: árbol limpio desde 0ada593)
- [ ] 0.2 Digest: `git ls-files -s | sha256sum` antes y después (probar no-escritura; se repite al cerrar)
- [ ] 0.3 Entorno: `.venv/Scripts/python --version`, `pip freeze | sha256sum`
- [ ] 0.4 MongoDB local: ping `127.0.0.1:27017`, `getCollectionNames()`, `count_documents` por colección. Sin Mongo → auditoría "estática" declarada en cabecera, F4/F5/D3 en PENDIENTE
- [ ] 0.5 Inventario: conteo de ficheros en `data/raw`, `data/procesado`, `data/resultados` (base de F7/D1)
- [ ] 0.6 Suite: `.venv/Scripts/python -m pytest tests --collect-only -q` (esperado: 151 colectados; cualquier desviación se anota)

Criterio de salida: si 0.4 falla, Eje A F4/F5 y Eje B D3 quedan en PENDIENTE con evidencia estática, nunca en PASS.

### F1 — Fidelidad de la rúbrica (cotejo binario)
Extraer texto del PDF (`pypdf`, 6 págs.) y del DOCX (`word/document.xml`) y comparar celda a celda con `contrato-reto/spec.md`. Entregable: tabla fidelidad (X/Y celdas idénticas) + lista de desvíos. Detecta "suavizados" (un 10 del PDF convertido en SHOULD) antes de puntuar.

### F2 — BDA RA1 (4 criterios)
- Extracción: API real (`requests` + `_common.Cliente`) vs scraping real (regex/HTML sobre Fotocasa/Pisos/RealtyAPI). Contar extractores por tipo, scripts con sidecar `.meta.json`/total. La descarga directa de un CSV/XLSX estático NO cuenta como API/scraping (plus, no sustituto).
- HDFS: originales (354 manifest vs ficheros reales, SHA-256, bytes) + procesados ("solo raw" = waiver; dar las dos notas: literal 7 / con waiver 10) + recuperación (`hdfs_utils`, script de recuperación de un fichero).
- Kafka: productor (`produce()` + Future/callbacks) y consumidor (`poll()` + `KAFKA_IDLE_MS`, sin `for msg in consumer`) procesando mensajes contra el clúster centro `10.22.87.215:9092`. Sin broker vivo → evidencia congelada 2026-11-06, no PASS, demo en clase marcada como dependencia.
- Integración: cadena real extracción→`data/raw`→silver→`load_mongo.load_all()`→colecciones Mongo. Rama Kafka→HDFS declarada separada por indicación expresa. Preparar frase de waiver para el tribunal (Kafka no está "en el camino a Mongo").

### F3 — SBD RA1 (4 criterios, 46,7%)
- Integración fuentes: ≥2 y relación por ≥1 campo común. Medir joins reales por colección (baseline v3: 11 colecciones 252/252 + `ecvi_compraventa` 7/29 parcial; re-medir, no copiar).
- Construcción conjunto: ≥2 colecciones + 1 relación/embedding/referencia DEMOSTRADA (embedding `municipios.demografia`, `anuncios.ubicacion` GeoJSON; referencing por `codigo_ine` de 5 dígitos; arrays `equipamiento`).
- Limpieza: ≥4 operaciones distintas incluyendo nulos/ausentes, duplicados y tipos/formato (`clean_mongo`: canonicalize_codigo_ine, mark_nulls, resolve_duplicates, convert_types, unset). Medir: 0 duplicados `(portal,id_anuncio)`, nº `Decimal128`.
- Automatización: `load_mongo.load_all()` + `clean_all()` + `run_mongo_pipeline.py` + `transform/run_all.py` ejecutan carga+limpieza+transformación sin editar a mano en Mongo (incl. `ensure_indexes` que propaga errores).

### F4 — SBD RA3 (6 criterios, 13,3%)
- Modelado: tipos BSON reales + decisión embedding vs referencing explicada y demostrada (`docs/modelo_mongodb.md` es explicación, el esquema es la prueba).
- CRUD: 4 operaciones + comprobación por código del resultado (`demo_crud_operations`, contadores). Tests `tests/test_mongo.py`.
- Consultas: ≥5 útiles, una con anidados/arrays y otra con 2+ condiciones (`analysis/mongo_queries.py`, 20+ funciones). Hoy en vivo: 2 condiciones→24 filas, anidado→50, array `exterior`→79. OJO vocabulario: `ascensor` NO está en el array; si la demo lo usa, cae a 0 filas.
- Aggregation: ≥3 pipelines del reto, ≥5 etapas, `$group` + (`$lookup|$unwind|$facet`). Contar etapas en `analysis/mongo_aggregations.py` (v3: 9 pipelines, 8 etapas) y ejecutar cada pipeline contando filas devueltas (252/252 en indicadores).
- Índices: `explain()` antes/después sin borrar índices (`hint: {$natural:1}`): COLLSCAN docs=759 keys=0 vs IXSCAN docs=1 keys=1, `nReturned` igual. 9 índices: ESR, 2dsphere sparse, multikey, unique `(portal,id_anuncio)`.
- Consistencia: transacción real o atómica + justificación técnica (`find_one_and_update` + `ValueError` fuera de dominio, test de sonda standalone). Mongo standalone degrada a "rechazado-standalone": documentar por qué la transacción sería innecesaria en este modelo.

### F5 — SBD RA4 (5 criterios, 40%)
- Heterogéneos: CSV Eustat, JSON anidado Udalmap/Etxebide, XLSX ECVI, GTFS transporte, HTML scrapeado, API INE/B5M → adaptados con Python/PyMongo (GeoJSON 424, array 759, anidado 252, Decimal 722).
- Automatización análisis: `analysis/run_analisis_mongo.py` orquesta pipelines y escribe 5 CSV + 13 PNG desde Mongo (sin DuckDB legacy). Re-ejecutar en sesión cerrada (antes/después SHA) o marcar "no re-ejecutado" como en v3.
- Indicadores: ≥5 de 2+ fuentes sobre 252 municipios (esfuerzo_joven_pct, 18_34, cuantia, renta_m2, tension, paro Lanbide 249, n_anuncios...). `precio_medio_eur` solo en 80/252: no generalizarlo.
- Respuesta al reto: ≥3 municipios comparados, cada conclusión ligada a indicador de Mongo (esfuerzo_joven_pct calculable en 252/252; robustos Bilbao 173 / Donostia 113 / Getxo 40 / Vitoria 39 anuncios; 83 municipios con anuncios).
- Viz: ≥3 conjuntos generados automáticamente desde PyMongo (13 PNG actuales + nuevos assets `topo.svg`/`trama.svg`/`shots/` de la presentación; verificar génesis, no solo existencia).

### F6 — Tema 8 (7 bloques, 100% evaluación separada)
Modelado 15%, CRUD/limpieza/consultas 15%, aggregation 20%, índices 15%, transacciones 10%, PyMongo profesional 15%, defensa 10% (solo lo escrito en guion). Extra que casi nadie cubre y se verifica: índices justificados uno a uno (unique/compuesto/multikey/2dsphere/sparse/partial/TTL), iteración de cursores, `MongoClient` único y URI configurable, manejo de errores, conexión con recreación de índices tras swap.

### F7 — Integridad y reproducibilidad (transversal, bloqueante para D9)
- Manifest raw 354 vs ficheros reales; `.FROZEN`; guards `test_raw_guardrails`; silver manifest 185; `run_all.py --check`.
- Doble ejecución de `run_analisis_mongo.py` con misma huella SHA-256.
- Conteos canónicos: 759 anuncios, 83 municipios con anuncios, 252 municipios, 159 con alquiler oficial, 4 robustos. Todo número que no cuadre con la documentación se anota como desync.
- BOM `utf-8-sig` en todos los CSV silver (`head -c 3`); `codigo_ine` con zfill(5) (Araba 4 dígitos rompe joins); Fotocasa `codigo_ine` float (`int(float(x))` + zfill); `tasa_paro_aprox_pct` inválida (NaN 252) → usar `tasa_paro_lanbide_pct`.

### D1 — Inventario de fuentes (clasificación según rúbrica)
Tipo por fuente: API estructurada / scraping HTML-JS / descarga directa (CSV/XLSX/ZIP/PDF estático). Solo API+scraping cuentan para el 10 de extracción; descarga directa automatizada es plus. Automatizado (script con `main()`) vs manual. Entregable: `openspec/audit/inventario_fuentes_2026-11-07.md` con score 0-10 por dimensión (extracción, muestreo, granularidad, cobertura, calidad de proxies) y global (antes v3 vs hoy). Pre-check (skill data-audit): antes de crear un extractor, validador read-only que haga join contra `dim_municipios` (252) y cuente `codigo_ine` distintos alcanzados; la decisión alta/baja va a `openspec/audit/validacion_fuentes_2026-11-07.md` con test que corre el validador. Regla de oro: la cobertura se prueba con un join, nunca se presume (SERPAVI y EMAL cubren los mismos 159; ninguno cierra el gap de 93).

### D2 — Cobertura por ámbito (counts crudos vs filtrados, siempre)
- Raw counts vs filtered counts (la depuración — IQR por segmento, 10-500 m² — puede eliminar TODOS los registros de un municipio; filtered < raw no es pérdida de datos).
- Municipios con alguna observación / n≥30 / alquiler oficial / ≥1 proxy. Distancias: verificar matriz 252×252 real (no asumir gap de ~5k pares). HTML crudos: recontar (v3: 99 vs 101 histórico).
- Filtrar agregados ("C.A. de Euskadi", code 00001) por prefijo 01/20/48 o `dim_municipios` queda en 253.
- Tipología de mercado con catch-all: buckets n≥30 / n<30 con oficial / 0 anuncios & 0 fianzas + edge cases fuera de todo bucket (documentar conteos, ej. 6/63/183).

### D3 — Suficiencia para conclusiones profesionales
1. Definir alcance defendible: ranking municipal / tipología / comarcal-capital / solo contexto. No prometer granularidad que la muestra no sostiene.
2. Regla n≥30: si <~10% de unidades tienen n≥30, NO hay ranking municipal; se clasifica por tipología y el resto "sin dato". Sin imputar comarcal como municipal; sin proxys comarcales como municipales.
3. Score de tensión 0-10 por dimensión (cobertura, robustez, sesgo urbano/rural, calidad de proxies, mezcla de años, granularidad, bloqueos de implementación) + global. 0 = suficiente, 10 = máxima insuficiencia. Las medias de tensión son juicio, no métrica: publicar categorías y conteos que la sostienen.
4. Separar suficiencia de datos de suficiencia de implementación (se puede tener datos suficientes y HDFS/Kafka/Mongo pendientes, o al revés).
5. Proxies honestos: renta municipal ≠ salario; emancipación territorial (CA/TH) ≠ municipal; Haversine ≈ aproximación.

### D4 — Calidad y anomalías (limpieza verificada, no asumida)
- IQR **por segmento** (temporal vs larga estancia, no umbral fijo €50 que pierde outliers 31-50), con bornes fijas como guarda externa. Temporal vs larga: split obligatorio, nunca media combinada (observado ~70% arriba: 27,65 vs 16,08 €/m²).
- `superficie_media_m2` solo 82/252, `precio_medio_eur` 80/252 → cualquier conclusión de precio sobre 252 es inválida.
- Nombres Fotocasa no canónicos → normalizar por `dim_municipios.variantes` antes de agregar. Join de dashboards por `codigo_ine` (nombre_canonico pierde ~177 variantes).
- `distancias_capitals`: dups y municipios fuera de alcance (limítrofes) → filtrar a `dim_municipios` y dedup antes de analizar.
- Orden de pipeline: el enricher (`aplicar_cobertura_mercado`) corre DESPUÉS del writer base de `dim_municipios` o el base lo sobrescribe y `n_anuncios_raw` desaparece.
- Contacto raw sin `codigo_ine`: resolver vía `alquiler_completo` (oficial/municipal) o mapa `nombre_canonico`; nunca asumir la columna.
- Bandas de edad gruesas (0-19 + 20-64) NO pueden derivar 15-29 (el intervalo cruza dos bandas y el split interior no es separable). Listar etiquetas distintas del raw antes de prometer población joven.

### D5 — Trazabilidad e ingestión
- Raw inmutable; lineage en `*_meta.json` (`_metadata`, `property_fingerprint`) no en raw. Manifest con SHA-256 + timestamp UTC + record count por fichero (incl. `.html`).
- Fingerprint determinista (`codigo_ine | superfície redondeada 5 m² | habitaciones | precio redondeado 50 €`) para dedup PyMongo posterior; no deduplicar al ingerir.
- Tests de ingestión por extractor nuevo (existencia, >0 registros, `codigo_ine` en rangos Euskadi). `metadata.n_anuncios == len(datos)` tras cada cambio.
- Orquestador explícito: globs numéricos (`extract/[0-9][0-9]_*.py`) NO deben duplicar la lista AUX (set intersection vacío) ni ignorar auxiliares (`entity_resolution`, `euskadi_geo`, `fotocasa_detalle`, `ine_atlas_renta`, `udalmap_empleo`).
- Mongo sin drops destructivos: staging → backup con `$out` → rename atómico (`collection.rename`, no `db.rename_collection` en pymongo 4); docs vacíos abortan sin tocar original; recrear índices tras el swap. Tests CRUD destructivos en skipped por defecto (`MONGO_ALLOW_DESTRUCTIVE=1`), reportados por separado (colectados/pasados/salteados).

### D6 — Comparativa con la auditoría anterior (v3, 2026-11-06)
Recalcular TODAS las métricas con script contra datos currentes; tabla antes/después/cambio/veredicto (mejorado/regresión/mixto) + gaps persistentes P1/P2/P3. Re-ejecutar el script de auditoría antes de heredar su gap list: requisitos marcados "unmet" en frameworks antiguos (HTML crudos, superficie, distancias) pueden estar resueltos ya; documentar el delta.

### D7 — Artefactos frescos (stale artifacts invalidan la auditoría)
Comparar mtimes de `data/resultados/` (PNG/HTML/CSV) contra el último CSV procesado; regenerar con `transform/` si quedan stale. README "N PNGs" == `ls *.png | wc -l` real. `data/resultados/mongo_*.csv` (252/252/2/252/322) desde `analysis/run_analisis_mongo.py` (huella `f1e78870`); DuckDB solo legacy.

### D8 — Veredicto de suficiencia y siguientes pasos
Veredicto global (mejorado/regresión/mixto) + qué conclusiones son defendibles hoy + backlog R3/fixes/docs. Score global de calidad de datos v3 vs v4 (desde D1).

### D9 — Sincronización documental (cero contradicciones)
Cuando un cambio de datos altere una métrica (cuarentena 6→4 robustos, enriquecedor 134/873→0/759), actualizar TODAS las referencias: metodología, trazabilidad, snapshot argon, informes, framework. `grep -r` del valor viejo antes de declarar cierre; una sola referencia stale rompe la siguiente auditoría. README: sin nombres de tooling interno; métricas numéricas siempre = dato real.

## 3. Checkpoints y dependencias

| Punto | Orden correcto (data-audit + planning) |
|---|---|
| Dependencias | Preflight (F0) → F1 fidelidad → Eje A (F2-F6) y Eje B (D1-D5) en paralelo → F7+D7 (artefactos frescos) → D6 comparativa → D8/D9 cierre |
| Orden de pipeline (no confundir) | `dim_municipios` base → enricher cobertura → checks; `anuncios` raw → `unificar_anuncios` (zfill) → filtros → silver → Mongo |
| Regla de 2 fases | No crear extractor nuevo (D1) sin validador de cobertura previo (gate antes de extractor) |
| Punto de no retorno | Ninguno durante la auditoría (solo lectura). El primer cambio real va al backlog, no a la auditoría |
| Checkpoints | Tras F0 (entorno listo), tras F3+D2 (cobertura medida), tras F4/F5+D3 (rúbrica y suficiencia calculadas), tras D6 (comparativa) |

## 4. Orquestación multi-agente (preferencia del usuario)

- Ventana deslizante, **máx. 3 agentes concurrentes**. Primera oleada: los más fundacionales (correctness/arquitectura + ML/reproducibilidad + tests/gate). Cola FIFO; al completarse uno, se rellena la ventana al instante (comprobar con `delegate_task(action='list')`, no estimando conteos).
- Si dos fases tocan los mismos ficheros/dato Mongo → 1 solo agente (sin paralelizar escrituras — aquí no hay escrituras, toda la auditoría es read-only).
- Al final, 2 jueces independientes que re-ejecutan el scope completo con sus propias probes y clasifican cada afirmación previa como confirmada / refutada / no verificable (sin leer las transcripciones ajenas). Un score de juez sin rúbrica o con conteo de tests que mezcla skipped destructivos = no verificable.
- Orden sugerido de oleadas (FIFO): F0+F1 → F2 (HDFS/Kafka) → F4 (Mongo: modelado/CRUD/queries/indices) → F3 (limpieza/automatización) → F5 (indicadores/viz) → F6 (Tema 8) → D1 (inventario) → D2+D3 (cobertura/suficiencia) → D5 (trazabilidad) → F7+D7 (frescura) → D6 (comparativa) → jueces.

## 5. Entregables (archivos)

| Archivo | Contenido |
|---|---|
| `openspec/audit/plan_auditoria_v4_2026-11-07.md` | Este plan |
| `openspec/audit/informe_auditoria_v4_2026-11-07.md` | Informe: preflight, matriz 26 criterios (nota + falsación + evidencia triple), veredicto de datos, comparativa v3→v4 |
| `openspec/audit/inventario_fuentes_2026-11-07.md` | Clasificación API/scraping/descarga + scores 0-10 por dimensión y global |
| `openspec/audit/validacion_fuentes_2026-11-07.md` | Decisiones alta/baja de fuentes candidatas (si alguna) |
| `openspec/audit/backlog_v4_2026-11-07.md` | Gaps P1/P2/P3 con risk-if-not-fixed y implementation risk (separa lo que toca SDD completo) |

## 6. Verificación

```bash
cd C:/Users/mikel/Documents/bigdata-vivienda-euskadi
.venv/Scripts/python -m pytest tests/ -q                      # suite completa (esperado 151 passed)
.venv/Scripts/python -m pytest tests/test_kafka_pipeline.py tests/test_mongo_queries.py -q
git ls-files -s | sha256sum   # antes (F0) y después (cierre): idéntico
ls data/resultados/*.png | wc -l  # == "N PNGs" del README
git status --short              # árbol limpio salvo este plan/informe/backlog
```

Criterio de aceptación de la auditoría (no del proyecto): informe con las 26 filas Eje A + comparativa Eje B + digest idéntico + 2 veredictos de juez, cada afirmación con evidencia triple.

## 7. Riesgos y mitigaciones

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Sin broker Kafka ni HDFS (acceso solo Windows local) | Criterios BDA 3/4 y F7 en PENDIENTE, notas no subibles | Evidencia congelada 2026-11-06 para no BAJAR la nota; nunca para subirla. Marcar demo en clase como dependencia del clúster |
| Waiver "HDFS solo raw" verbal | Literal BDA-HDFS = 7, no 10 | Las dos lecturas en el informe; preparar frase de defensa; fila P1 en backlog |
| Kafka no termina en Mongo (va a HDFS) | Tribunal estricto = Integración 7 | Frase de waiver preparada (indicación expresa de la profesora); no cambiar la rúbrica |
| Artefactos stale en `data/resultados/` | Números "de memoria" | F7+D7: mtimes + regeneración + conteo real PNG antes de cualquier afirmación |
| Mongo no accesible el día de la auditoría | F4/F5/D3 en estático | Preflight 0.4 declara la degradación en cabecera; ninguna nota 10 por documentación |
| Deriva de métricas entre docs (un README desactualizado) | Contradicción en próxima auditoría | D9: grep del valor viejo en todo el repo antes de cerrar |
| Fotocasa (regex frágil, float `codigo_ine`, nombres no canónicos) | Cobertura y joins erróneos | D1/D2/D4: zfill, `int(float())`, filtro `dim_municipios`, variantes, splits temporal/larga |
| Paralelizar agentes que toquen Mongo/datos | Escrituras cruzadas | Auditoría read-only; 1 agente si hay conflicto de fichero/dato (regla del usuario) |
| Gustarse con un "10 fácil" por documentación | Inflar la nota | Umbral literal + falsación por fila; jueces independientes |

## 8. Preguntas abiertas (para el usuario, no bloquean el plan)

- Q1: ¿Ejecutamos F0 con Mongo local levantado o en modo "estático" si Mongo no está?
- Q2: ¿Entregable en español (como v3) o en inglés (convención SDD)? Se asume español salvo que indiques lo contrario.
- Q3: ¿Se incluye el benchmark de los tests destructivos de Mongo (skipped separados) o se excluyen para tener la suite 100% verde?
- Q4: ¿Bonus Tema 8 "defensa" se verifica solo contra el guion escrito (guion_defensa_12min) o en vivo?

## 9. Qué NO hace este plan

- No modifica código ni datos (solo lectura).
- No archiva los 15 `openspec/changes/` sin merge delta (6.3 diferido de 2026-11-05-cierre-suficiencia-auditoria: archivarlos perdería requisitos).
- No toca `data/raw` (inmutable) ni sube procesados a HDFS (decisión solo-raw firmada).
- No trata un pull-request/PR como requisito (no hay PRs abiertos; si se abren, se verifican por separado).

## Plantillas rápidas

```markdown
### Informe — fila por criterio (Eje A)

| # | Criterio | Umbral 10 literal | Evidencia medida hoy | Nota | Falsación (qué lo bajaría) |
|---|---|---|---|---|---|
| n | ... | ... | comando + salida + fichero:línea | 10/7/3/0/PENDIENTE | ... |

### Informe — comparativa por métrica (Eje B)

| Métrica | v3 (2026-11-06) | Hoy (2026-11-07) | Cambio | Veredicto |
|---|---|---|---|---|
```

---

*Relaciones: `openspec/specs/contrato-reto/spec.md` (verdad), `openspec/audit/informe_auditoria_v3_2026-11-06.md` (baseline técnico), `data-audit` skill (comparativa + suficiencia + trazabilidad), `planning-and-task-breakdown` (ventana deslizante máx. 3 + jueces independientes).*

