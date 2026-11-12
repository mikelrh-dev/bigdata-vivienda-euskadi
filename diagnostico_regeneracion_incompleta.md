# Diagnóstico: por qué no salen todos los datos al regenerar

## Resumen ejecutivo
Tu compañero tenía razón: borrar `data/procesado/` y `data/resultados/` dejó el sistema en un estado que **no es recuperable ejecutando solo `transform/run_all.py`**. Hay productos en esas dos carpetas que el orquestador no genera, hay scripts que existen y que los generan pero no están en `run_all.py`, y algunos scripts de extracción producen productos de procesado directamente. A continuación está el diagnóstico verificado con el código real.

He verificado esto:

- `extract/_common.py` → `RAW_DIR`, `PROCESADO_DIR`, `RESULTADOS_DIR`
- `extract/normalizar_metadata.py` → escribe `procesado/_meta/*.meta.json` e `index.json`  y `ingestion_manifest.json`
- `extract/generar_manifest.py` → escribe `docs/raw_manifest_sha256.txt` y `data/procesado/manifest_sha256.txt`
- `extract/09_fotocasa_dirigido.py` → escribe en `raw` + `data/procesado/fotocasa_dirigido_informe.csv`
- `extract/generar_ingestion_manifest.py` → escribe `procesado/_meta/ingestion_manifest.json`
- `transform/run_all.py` → `SCRIPTS`, `EXCLUIDOS`, lógica de ejecución, dry-run
- `transform/_raw_guard.py` → `assert_raw_writable`
- `tests/test_raw_guardrails.py`
- `openspec/archive/2026-11-10-docs/contrato_datos_raw.md`
- `scripts/verificar_fase_datos.py` → qué productos necesita para considerar fase OK
- `analysis/run_analisis_mongo.py` → 8 CSV + varios PNG y capas en `data/resultados/`
- `transform/generar_figuras_N.py` → N1, N2, N3, N7, H2, F, H8, J, P en `data/resultados/`
- `transform/auditar_lagunas_silver.py` → `auditoria_lagunas_silver.csv`
- `transform/generar_mapa_esquema.py` → `mapa_esquema_silver.html`
- `analysis/sensibilidad.py` → `sensibilidad_idw.csv`, `bootstrap_robustos.csv`
- `docs/presentacion/build_presentacion.py`
- `data/resultados/README.md` → índice de productos y qué script los genera
- Contenido real de disco en `data/procesado/` y `data/resultados/` (esta copia, con datos)

## Totales reales en esta copia del proyecto
- `data/procesado/`: 129 ficheros
- `data/resultados/`: 58 ficheros
- `transform/run_all.py` declara 34 scripts y 116 ficheros de procesado
- `transform/run_all.py` tiene 8 scripts `EXCLUIDOS`

## Verdicto esquemático por capa

```
Capa        | Orquestador   | Qué genera realmente                    | Veredicto
raw         | extract/*.py  | raw/*.json, raw/*.csv                   | no error
procesado   | extract/* +   | metadatos de ingesta, informes de      | Hay producers
            | transform/*   | captura dirigida, manifiesto de raw    | fuera del orquestador
silver      | transform/run_all.py | 116 ficheros declarados     | no error (el orquestador
            |               |                                        | declara lo que genera)
resultados  | 2 scripts en  | 8 CSV de mongo, figuras N1-N3,N7, H2, | Hay producers
            | run_all.py    | F, H8, J, P; sensibilidad; dashboards; | fuera del orquestador
            |               | mapa esquema; auditoría lagunas         | y scripts no declarados
```

## Problema concreto 1: los `.py` que sacen esas capas no se ejecutaron con los orquestadores

### Procesado tiene producers que no están en `transform/run_all.py`

Esto es lo que pasa cuando solo ejecutas `python transform/run_all.py` desde un estado vacío:

1. `run_all.py` genera 116 ficheros de procesado declarados.
2. Pero en esta copia existen otros 129 ficheros. De esos, varios son producidos por scripts que **no están en el orquestador**:

```
f4_pisos_objetivo.json              -> transform/generar_f4_pisos_objetivo.py (EXCLUIDO)
fotocasa_dirigido_informe.csv       -> transform/generar_fotocasa_dirigido_informe.py (EXCLUIDO)
f4_pisos_informe.csv                -> 09_fotocasa_dirigido.py (extract, productor de procesado)
ingestion_manifest.json             -> extract/generar_ingestion_manifest.py (productor de procesado)
_meta/*.meta.json                   -> extract/normalizar_metadata.py (productor de procesado)
index.json                          -> extract/normalizar_metadata.py
csvs_index.json                     -> extract/normalizar_metadata.py
manifest_sha256.txt                 -> extract/generar_manifest.py
acta_ingesta.md                     -> extract/normalizar_metadata.py
```

Esto significa que **si tu compañero borró `data/procesado/` y ejecutó solo `transform/run_all.py`, le faltarán esos artefactos**.

Además, hay scripts de extracción que escriben directamente en `procesado/`. Eso no es un error de diseño por sí mismo, pero sí significa que no puedes reconstruir todo ejecutando solo la capa `transform/`.

### Resultados tiene muchos producers que no están en `transform/run_all.py`

El orquestador solo genera dos artefactos de resultados:

```
resultados/mapa_esquema_silver.html            -> generar_mapa_esquema.py
resultados/auditoria_lagunas_silver.csv        -> auditar_lagunas_silver.py
```

El resto de los 58 ficheros de resultados provienen de scripts que **no están en `run_all.py`**:

```
analysis/run_analisis_mongo.py:
  mongo_esfuerzo_por_municipio.csv
  mongo_alquiler_por_municipio.csv
  mongo_modalidades.csv
  mongo_vpo_por_municipio.csv
  mongo_accesibilidad_extendida.csv
  mongo_tier_confianza.csv
  mongo_vpo_terminadas_por_municipio.csv
  comparativa_3_municipios_mongo.csv
  capa_oficial.csv
  capa_idw.csv
  capa_contexto.csv
  udalmap_paro.csv
  ranking_esfuerzo.csv
  24 PNG (A1,A2,B,C,D,E,F,g2,g3,g4,g5,H1-H13,I,J,K,L,O,P)

analysis/sensibilidad.py:
  sensibilidad_idw.csv
  bootstrap_robustos.csv

transform/generar_figuras_N.py:
  mapa_coroplastico_esfuerzo_18_34.png   (N1)
  hist_esfuerzo_18_34_umbral30.png      (N2)
  dumbbell_esfuerzo_18_24_vs_25_34.png  (N3)
  transporte_oferta_vs_esfuerzo.png     (N7)
  H2_tier_confianza_ABCD.png
  F_comparativa_TH.png
  H8_tier_mediana_temporal_vs_larga.png
  J_tier_confianza_vs_precio.png
  P_oficial_vs_anuncios_por_TH.png

docs/presentacion/build_presentacion.py (y posible otros):
  dashboard.html
  dashboard_completo.html

8 PNG relegados a anexo/:
  anexo/G_gaps_limitaciones.png
  anexo/H12_vpo_promociones_estado_tipologia.png
  anexo/H4_esfuerzo_18_34_vs_16_29.png
  anexo/H9_modalidades_larga_vs_temporal.png
  anexo/I_modalidad_temporal_vs_larga.png
  anexo/K_vpo_terminadas_vs_esfuerzo.png
  anexo/L_confort_accesibilidad_vs_esfuerzo.png
  anexo/g1_esfuerzo_por_territorio.png
```

Por lo tanto, **ejecutar solo `transform/run_all.py` no regenera ninguna de estas things**.

## Problema concreto 2: la regeneración incompleta es esperable

Cuando borras `data/procesado/` y `data/resultados/`, la única forma de regenerarlos todos es ejecutar varios orquestadores y scripts sueltos:

- `transform/run_all.py` → silver + 2 resultados
- `extract/normalizar_metadata.py` → metadatos de ingesta
- `extract/generar_manifest.py --write` → manifiesto canónico de raw
- `extract/generar_ingestion_manifest.py` → manifiesto de ingesta
- `extract/09_fotocasa_dirigido.py` → informe de captura dirigida
- `transform/generar_fotocasa_dirigido_informe.py` → informe de captura dirigida (EXCLUIDO)
- `transform/generar_f4_pisos_objetivo.py` → lista de objetivos (EXCLUIDO)
- `transform/generar_figuras_N.py` → figuras P0 (EXCLUIDO)
- `analysis/run_analisis_mongo.py` → 8 CSV + 24 PNG (no está en el orquestador)
- `analysis/sensibilidad.py` → sensibilidad (no está en el orquestador)
- `docs/presentacion/build_presentacion.py` → dashboards si se usan

## Scripts excluidos del orquestador (razón documentada en el código)

```python
EXCLUIDOS = {
    "run_all.py": "el propio orquestador",
    "f4_pisos_dirigido.py": "captura dirigida manual (escribe en raw con guard)",
    "generar_f4_pisos_objetivo.py": "genera la lista manual de objetivos de f4",
    "generar_fotocasa_dirigido_informe.py": "informe de captura dirigida",
    "muni_resolve.py": "libreria, no script ejecutable del pipeline",
    "validar_renta.py": "QA bajo demanda, no ETL silver",
    "generar_figuras_N.py": "genera PNG P0 N1,N2,N3,N7 y H2 desde CSV sin Mongo vivo (evidencia visual, no silver)",
    "_raw_guard.py": "libreria de guardia raw, no paso del pipeline",
}
```

Esto confirma que los productos de resultados que no dependen de `run_all.py` son **intencionales**: figuras, mongo, sensibilidad y dashboards están fuera del orquestador por diseño.

## Productos de procesado que dependen exclusivamente de extract/

Estos son datos que solo pueden llegar desde `extract/` y que `transform/run_all.py` no genera:

```
data/procesado/_meta/acta_ingesta.md
data/procesado/_meta/*.meta.json
data/procesado/_meta/index.json
data/procesado/_meta/csvs_index.json
data/procesado/_meta/ingestion_manifest.json
data/procesado/_meta/nombres_normalizados_map.json
data/procesado/manifest_sha256.txt
data/procesado/fotocasa_dirigido_informe.csv
data/procesado/f4_pisos_objetivo.json
data/procesado/f4_pisos_informe.csv    # de 09_fotocasa_dirigido.py
```

## Qué comandos de regeneración necesarios

Para reconstruir todo desde cero (raw ya existente), tu compañero necesitaría ejecutar esto:

```bash
# 1. Normalizar metadatos de raw
python extract/normalizar_metadata.py

# 2. Manifiesto de ingesta
python extract/generar_ingestion_manifest.py

# 3. Manifiesto canónico de raw (opcional si no se toca raw)
python extract/generar_manifest.py --write

# 4. Silver
python transform/run_all.py

# 5. Informes de captura dirigida
python transform/generar_fotocasa_dirigido_informe.py
python transform/generar_f4_pisos_objetivo.py

# 6. Resultados de Mongo
python analysis/run_analisis_mongo.py

# 7. Figuras P0 (N1,N2,N3,N7,H2,F,H8,J,P)
python transform/generar_figuras_N.py

# 8. Sensibilidad
python analysis/sensibilidad.py

# 9. Mapa esquema silver (ya se genera con run_all.py, pero si se borra solo)
python transform/generar_mapa_esquema.py

# 10. Auditoría de lagunas silver (ya se genera con run_all.py, pero si se borra solo)
python transform/auditar_lagunas_silver.py
```

## Veredicto final

**Error: sí, hay un problema real de orquestación.** No es un error de diseño de la capa raw, sino un problema de reconstruibilidad: si tu compañero borra `data/procesado/` y `data/resultados/` y ejecuta solo `transform/run_all.py`, no va a regenerar todo lo que hay en esas carpetas. Esto es porque:

1. Hay scripts fuera del orquestador que producen artefactos de procesado y resultados.
2. Hay scripts de extracción que escriben directamente en `procesado/`.
3. El orquestador `transform/run_all.py` solo genera una parte de los productos esperados.

Esto no es necesariamente un bug, pero sí es una fuente de confusión operativa. Si el objetivo es poder reconstruir todo desde cero ejecutando un solo comando, el sistema actual no lo soporta.
