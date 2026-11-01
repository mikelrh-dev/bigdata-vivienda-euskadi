# Acta de cierre — fase recopilación + transformación (2026-11-01)

## 1. De qué documento viene cada cosa (trazabilidad)

| Sigla | Documento | Qué aporta a este acta |
|---|---|---|
| PDF | `archivosReto/RETO 1Evaluacion SBD-BDA.pdf` | Rúbrica oficial (RA1 BDA). Fuente absoluta de la nota. |
| DOCX | `archivosReto/Tema_8_MongoDB_Proyecto_Reto_Vivienda.docx` | Checklist §17 + exigencia §6 (limpieza con operaciones MongoDB). |
| CONTRA | `openspec/audit/contrauditoria_2026-11-01.md` | Contraauditoría claim-by-claim del informe externo; define los 10 WP pendientes y su severidad. |
| VERIF-EXT | `openspec/audit/verificacion_fase_datos_2026-11-01.md` | Informe del otro modelo (2026-11-01): conclusión global correcta, ~1/3 de detalles imprecisos (ver CONTRA §3). |
| PLAN | Replanificación autorizada en chat (Bloques A–D, 10 pasos) | Orden de ejecución autorizado por el propietario. |
| CONTRATO | `openspec/specs/contrato-reto/spec.md` | Transcripción de la rúbrica; manda sobre el código si discrepan. |

## 2. Qué se ha hecho (por bloque, con commits)

- **Bloque A** (`dbad9f9`): WP-12 `cobertura_anuncios.csv` (252 filas, niveles alta/media/baja/sin_mercado) emitido por `transform/aplicar_cobertura_mercado.py` y declarado en `run_all.py`; WP-15 `renta_joven_origen` por fila en `dim_municipios_renta.csv` (derivado de nulidad real Eustat/Atlas); WP-17 `data/procesado/_meta/ingestion_manifest.json` (314 ficheros) vía nuevo `extract/generar_ingestion_manifest.py`. Tests: `test_wp12` endurecido + `test_wp15_renta_origen_fila` + `test_wp17_ingestion_manifest` nuevos.
- **Bloque B** (`2531984`): WP-11 `_ratio_fiscal_desde_eustat` retorna `(ratio, flag)` y añade `flag_ratio_fiscal` (corregidas además las etiquetas reales `18 - 19 años`, que el código anterior no matcheaba y caía en fallback silencioso); WP-18 rescate de procedencia legacy en `extract/normalizar_metadata.py` (alias `fuente_url`, fallback top-level, mapa `FUENTES_LEGACY` para emancipación) sin tocar raw; M-1 `dtype=str + utf-8-sig + zfill(5)` en `extract/10_scraping_faltantes.py:52`. Tests: `test_wp11_flag_fiscal` + `test_wp18_metadata_salario` nuevos. Efecto: sidecars `ovj_salario` y `emancipacion` pasan a `completa=true`.
- **Bloque C** (`3c7d29f`): WP-09 mapa `data/procesado/_meta/nombres_normalizados_map.json` + `test_wp09_mapa_nombres_estables` (ver §4 desvío 1); WP-16 `docs/universo_252_decision.md` (ver §4 desvío 2); M-2 cifras reales en `openspec/project.md` y `AGENT.md` (manifest 314 = 316 − 2 excluidos; silver 115→180; 52 funciones de test); nota de nodos in-place en `run_all.py`.
- **Bloque D** (`f594fe5`): reordenación del DAG (escritores in-place de `anuncios_unificados` antes que lectores; `aplicar_cobertura` antes que todo lector de `dim`), `out` explícitos en `generar_vistas_mercado` (2 CSV) y dashboards (5 + 8 PNG, fin del glob `res:*`), auto-exclusión de entradas propias en `_estado` (el csv/json del mismo script se escriben con ms de diferencia y se marcaban stale entre sí). Regeneración de manifests: raw 314 (mismo conjunto, solo orden determinista — verificado por diff normalizado), silver 115→180.

## 3. Ficheros cambiados (código y docs versionados)

`transform/aplicar_cobertura_mercado.py`, `transform/calcular_renta_joven.py`,
`transform/run_all.py`, `extract/normalizar_metadata.py`,
`extract/10_scraping_faltantes.py`, `extract/generar_ingestion_manifest.py` (nuevo),
`tests/test_fase_datos.py`, `docs/universo_252_decision.md` (nuevo),
`openspec/project.md`, `AGENT.md`, `docs/raw_manifest_sha256.txt` (reordenado).
Artefactos generados no versionados (`data/` está ignorado por git):
`cobertura_anuncios.csv`, `_meta/ingestion_manifest.json`,
`_meta/nombres_normalizados_map.json`, `manifest_sha256.txt` (silver),
`run_manifest.json` y salidas silver reescritas por el pipeline.

## 4. Desvíos del PLAN (decididos en el loop SDD con evidencia)

1. **WP-09: no renombrar, registrar.** Los dos lotes `fotocasa_dirigido_20261029*.json` tienen distinto contenido (122 KB vs 9 KB) y heredan el timestamp del raw congelado; renombrar rompía la correspondencia raw→silver. Mapa + test + política de nombres canónicos en su lugar.
2. **WP-16: no mover, documentar.** 9 lectores dependen de `data/raw/dim_municipios.*`; moverlo era riesgo 7/10 por beneficio taxonómico. Declarado universo versionado en `docs/universo_252_decision.md`.
3. **Hallazgo del verify:** `analisis_variables_base` consumía `n_anuncios` crudo (843) mientras `dim` publicaba 759. Tras el reorden consume post-dedup (759). `dim_municipios`, `anuncios_unificados`, gold y tensión salen byte-idénticos; solo cambian `analisis` y `renta` (cambio intended).

## 5. Verificación final (2026-11-01, todo en verde)

- `transform/run_all.py`: 35 scripts, 0 fallos.
- `transform/run_all.py --check`: 35/35 OK (partía de 7 stale + 1 sin declarar).
- `pytest tests/`: 82 passed (partía de 77).
- `verificar_fase_datos.py`: OK 15/15.
- `generar_manifest.py --verify`: raw 314 + silver 180, 0 errores; raw intacto.

## 6b. Adenda 2026-11-01 — cierre G-1, G-2, G-4

- **G-1 (sidecars): 17/59 → 19/59 completas.** Segundo rescate en
  `extract/normalizar_metadata.py`: `n_registros` se cuenta desde `datos`
  (incidencia `recuento-contado`, validado contra el propio recuento) y
  `b5m_catalogo.json` recibe fuente legacy documentada. Resto declarado
  como desconocido conocido, no fabricado: 39 `sin-url` (los scrapers de
  2026-10-28/29 nunca guardaron la URL de consulta), 8 `sin-fecha`,
  1 `sin-recuento`. Las URL exactas de scraping son irrecuperables por
  diseño del congelado; constan aquí como limitación, no como deuda.
- **G-2 (`renta_municipal_completa.json`):** derivado sin acta de
  construcción (fuente y 252 registros sí, fecha/URL no). Excepción
  documentada; no reconstruible sin tocar raw.
- **G-4 (`legacy_obsoleto_no_usar/`):** forma parte del manifest 314 a
  propósito (integridad de lo observado, aunque ya no se use). No es
  deuda: es evidencia con nombre desafortunado.

## 6. Qué queda pendiente (NO es de esta fase, para el siguiente agente)

HDFS (subida de originales/procesados), Kafka (productor/consumidor),
MongoDB (modelo + PyMongo + Aggregation Pipeline; las reglas portables están en
`docs/reglas_limpieza.md` R1–R7), visualización desde consultas PyMongo e
informe comparativo (RA4). Ninguno de ellos puede bajar la nota de la fase
cerrada en este acta; puntúan en sus criterios propios (ver CONTRA §2).
