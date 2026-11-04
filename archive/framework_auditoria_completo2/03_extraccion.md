# 03 · Módulo Extracción (objetivos PDF 1-2 → rúbrica 10 API Y scraping)

## Qué debe existir

- **API automatizada:** ≥1 script `extract/*.py` con `Cliente.get()` + reintentos + log + raw + resumen JSON (ej. `03_euskadi_emancipacion.py`, `10_opendata_bizilagun_etxebide.py`).
- **Scraping automatizado:** ≥1 scraper que guarde HTML crudo (`data/raw/html_fotocasa/`) + parseo separado (ej. `10_scraping_faltantes.py` + `transform/parsear_secciones.py`). Guardar HTML ≠ parsear HTML: el auditor verifica ambos.
- **Complementarios (objetivo 2):** salarios/renta, población, empleo, demografía, transporte/GTFS, distancias/OSRM, ECVI/Etxebide/SERPAVI. No se exige una lista cerrada; se exige que lo usado para "dónde vivir" exista en raw.
- **Gestión JSON/CSV (BDA):** todo raw tabular en CSV con BOM si hay tildes, o JSON con metadatos (fuente, fecha, n).
- **Profesionalidad:** sin credenciales en repo (solo `REALTYAPI_KEY` por env, `.env` ignorado), `requirements.txt` reproduce, cada extractor `main() → int` y `if __name__ == "__main__"`.

## Checks empíricos (ejecutar, no suponer)

1. `ls extract/*.py | wc -l` + `grep -l "Cliente(" extract/*.py` (APIs) + `grep -li "beautifulsoup\|playwright\|selenium\|requests.*html\|html_fotocasa" extract/*.py` (scrapers).
2. `ls data/raw/html_fotocasa/ | wc -l` (debe ser >0 y citado en el extractor).
3. `git ls-files | grep -iE "\.env$|api\.txt|*_key*"` debe estar vacío salvo `.env.example`.
4. Releer 1 CSV Eustat con `;` y `"` (emancipación/ECVI): `pd.read_csv(..., sep=";", quotechar='"', dtype=str)` no debe descuadrar columnas.
5. `python extract/generar_manifest.py --check` o equivalente: 0 mismatches (si el repo usa `data/raw/ingestion_manifest.json` + gate 17).

## P1 / P2 / P3 típicos

- **P1:** solo hay API o solo scraping (rúbrica → 7, no 10); extractor sin log ni resumen (irreproducible); credencial en repo; HTML crudo ausente pero se dice "scraping hecho".
- **P2:** complementario clave ausente sin justificar (p.ej. sin renta ni proxy documentado); CSV sin BOM con tildes rotas; extractor con `bare except` que traga fallos de red.
- **P3:** logs con `print` en vez de logger (cosmético); docstring sin URL de fuente; reintento sin backoff.

## Salida del módulo

Tabla: `fuente | script | tipo (API/scraping) | raw generado | n registros | fecha | reproducibilidad (SÍ/NO)`. + veredicto Extracción: 10 / 7 / <7 con criterio exacto que falta.
