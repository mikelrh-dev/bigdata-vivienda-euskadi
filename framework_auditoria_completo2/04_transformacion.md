# 04 · Módulo Transformación (objetivo PDF 6-parcial → base del 10 futuro)

> Limpieza en Python HOY; limpieza con PyMongo MAÑANA. Este módulo verifica que la de hoy no haya que rehacerla mañana.

## Checks innegociables

1. **Orquestación declarada:** todo `transform/*.py` ejecutable está en `transform/run_all.py` (SCRIPTS) o en EXCLUIDOS con motivo (helpers como `_raw_guard.py`, `muni_resolve.py`, QA como `validar_renta.py`). Test: `test_wp01_todo_script_declarado`.
2. **Raw intacto:** `git status --porcelain data/raw/` limpio tras `run_all.py`; `_raw_guard` activo; manifest 0 errores; `.FROZEN` presente.
3. **Entity resolution:** `codigo_ine` 5 dígitos en silver al 100% (`dim_municipios.csv` como verdad, 252). Joins por `codigo_ine`, nunca por nombre. Variantes (Arrankudiaga-Zollo, Donostia, Vitoria-Gasteiz) mapeadas en `muni_resolve` + mapa de nombres versionado. Filtrar las 24 filas no-municipio de Eustat (CA/provincias/comarcas).
4. **Tipografía segura:** todo `pd.read_csv` de transform con `dtype=str` (cero de Álava); conversión explícita después (`pd.to_numeric(..., errors="coerce")`). Último resto conocido: `10_opendata_bizilagun_etxebide.py` — verificar.
5. **Limpieza honesta:** nulos → `None`/marcador + columna `metodo`/flag, nunca `0` silencioso; outliers marcados (`filtrar_outliers.py`: precio_m2 3-50, superficie 10-500) sin borrar original; duplicados cross-portal a `0%` via `property_fingerprint` (`unificar_anuncios.py` + `generar_fingerprint.py`); unidades y años con `anio`/`año_fuente` explícitos.
6. **Trazabilidad:** cada silver sabe de qué raw viene (sidecar/meta o `docs/trazabilidad_datos.md`); `docs/reglas_limpieza.md` + `docs/metodologia.md` describen decisiones; `cobertura_anuncios.csv` + `ingestion_manifest.json` existen (gate 16-18).
7. **Determinismo:** sin `uuid`/fechas volátiles en outputs; re-ejecución byte-estable donde se declare.

## Comandos

- `python transform/run_all.py --check` (35/35) + `python verificar_fase_datos.py` (18/18) + `pytest tests/ -q` (verde).
- `grep -rn "pd.read_csv(" transform/ | grep -v dtype` debe estar vacío.
- `grep -rn "http://" extract/17_osrm_tiempos.py` debe estar vacío (https).
- Muestreo: `codigo_ine` longitud 5 en `dim_municipios.csv`, `analisis_variables_base.csv`, `dim_municipios_tension.csv`.

## P1 / P2 / P3 típicos

- **P1:** transform escribe en `data/raw/` sin guard; join por nombre que pierde municipios; nulo → 0 que corrompe medias; `dtype` ausente que convierte `01059` en `1059`.
- **P2:** outlier eliminado en vez de marcado; duplicado no tratado; Eustat sin filtrar agregados (n=252 falso); OSRM por http.
- **P3:** `print` en vez de logger; EXCLUIDOS sin motivo de una línea; docstring sin unidades.
