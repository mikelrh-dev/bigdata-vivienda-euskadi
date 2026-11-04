# 02 · Rúbrica auditable (0/3/7/10) — qué mirar para cada punto

> Traducción literal del PDF + DOCX a checks ejecutables. Sin evidencia del umbral 10, se puntúa 7 aunque "funcione".

## BDA · RA1 (PDF p.3)

| Criterio | 0 | 3 | 7 (umbral) | 10 (qué exige el auditor) |
|----------|---|---|------------|---------------------------|
| **Extracción Python** | No obtiene datos | Una fuente manual | Automatiza **API o scraping** | Automatiza **API Y scraping**, ambos con script + log + raw generado. Ver: `extract/` con ≥1 cliente API (`Cliente.get`) y ≥1 scraper HTML (`html_fotocasa/` o equivalente), cada uno con `main() → 0` y sidecar/resumen. |
| **HDFS** | No almacena | Crea directorios | Guarda y recupera archivos | **En esta fase:** layout que anticipa HDFS: `data/raw/` (originales) separado de `data/procesado/`, manifest con hash/tamaño, y prueba de recuperación (releer raw y comparar SHA). HDFS real = futuro. |
| **Kafka** | No funciona | Crea tópico | Productor Python envía | **Futuro.** En fase datos solo: ¿los anuncios tienen `id_anuncio` + `property_fingerprint` estables para hacer idempotencia después? (`06`). |
| **Integración** | Sin integración | Por separado | Integra 2+ componentes | **Futuro (flujo hasta Mongo).** En fase datos: `extract/main_ingest.py` + `transform/run_all.py` + gate encadenados sin intervención manual. |

## SBD · RA3 (PDF p.4) — en fase datos SOLO readiness

| Criterio | 10 real (futuro) | Qué audita HOY (`06`) |
|----------|------------------|------------------------|
| Modelado MongoDB | Justifica modelo y relaciones | ¿Silver ya trae `codigo_ine` 5 dígitos, tipos BSON-amigables (números como número o string canónico documentado, fechas ISO), arrays estables? ¿Hay propuesta embedding vs referencing escrita? |
| Operaciones PyMongo | Automatiza + comprueba `matched/modified/deleted/inserted` | ¿Los scripts comprueban resultados (conteos antes/después, logs) en vez de asumir? |
| Consultas | Anidados + arrays | ¿Existen campos anidados (`ubicacion.codigo_ine`) y arrays (`historico_precios` o equivalente) consultables? Si no, ¿documentado por qué? |
| Aggregation | ≥4 etapas → indicadores complejos | ¿Silver permite `$match/$lookup/$unwind/$group/$sort` sin re-limpieza? (joins por `codigo_ine`, sin nulos encubiertos) |

## SBD · RA4 (PDF p.4) — en fase datos SOLO base

| Criterio | 10 real | Qué audita HOY |
|----------|---------|----------------|
| Gráficos (3 tipos adecuados) | 3 tipos adecuados a los datos | ¿Hay al menos distribuciones + ranking + serie/mapa en `docs/` o `scratchpad/` aunque sean provisionales? No se exige belleza final. |
| Datos utilizados | Gráficos desde consultas PyMongo | **Futuro.** Hoy: prohibido hardcodear (ningún municipio/precio a mano en código de análisis); todo número viene de CSV/JSON leído. |
| Presentación | Títulos, unidades, leyendas + comparación entre municipios | Hoy: ¿las tablas provisionales traen unidades (€/mes, €/m², %) y comparan municipios? |
| Interpretación | Relaciona resultados e implicaciones | Hoy: `05` exige limitaciones explícitas (n pequeño, proxy renta, paro relativo). Sin limitaciones = NO 10 futuro. |

## DOCX Tema 8 · Pesos Mongo (solo para no hipotecar futuro)

Modelado 15% · CRUD 15% · Aggregation 20% · Índices 15% · Transacciones 10% · PyMongo profesional 15% · Defensa 10%.
El auditor de fase datos verifica que **ninguna decisión silver bloquee** estos pesos: p.ej. no serializar números como texto ambiguo (bloquea Aggregation 20%), no perder `id_anuncio` (bloquea idempotencia y transacciones), no dejar joins por nombre sin `codigo_ine` (bloquea Modelado 15%).

## Regla de puntuación

- Cada criterio: **0 / 3 / 7 / 10** con evidencia (comando + número + fichero:línea).
- Si el umbral 10 pide "API Y scraping" y solo hay API → **7 aunque la API sea perfecta**.
- Lo futuro se marca `DIFERIDO (readiness ✅/⚠️/❌)`, nunca 0.
