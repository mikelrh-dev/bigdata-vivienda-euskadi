# Plan de regeneración completa de data/raw (con verificación contra inventario)

> Planificación cuidadosa. NO ejecutar sin confirmación explícita.
> Inventario de referencia (NO modificar): `docs/inventario_datos.md` (325 archivos, 2026-10-28).
> Backup de seguridad: `data/raw_backup_2026-10-29/` (380 MB) — estado congelado actual.
> Manifest canonical actual: `docs/raw_manifest_sha256.txt` (297 archivos).

## 0. Objetivo

Regenerar `data/raw/` desde las fuentes para:
- Confirmar reproducibilidad de las extracciones.
- Partir de un raw "limpio" (lo más cercano posible a la fuente) antes de aplicar la regla bronce estricta.
- Aplicar después la inmutabilidad (congelar + manifest + test).

Aceptación explícita: las APIs vivas devuelven datos actualizados → **no se exigen hashes idénticos**; se comparan estructura, filas y rangos.

## 1. Precondiciones (verificar antes de empezar)

- [ ] Backup `data/raw_backup_2026-10-29/` existe y es legible (verificado: 380 MB).
- [ ] Inventario `docs/inventario_datos.md` intacto (no modificar).
- [ ] Entorno Python 3.12 `.venv` activo con dependencias (`pip install -r requirements.txt`).
- [ ] Red disponible (APIs Eustat/INE/SERPAVI/OSRM/Lanbide/ECVI/Open Data).
- [ ] `data/raw` congelado (`.FROZEN`) — se mantiene intacto durante la regeneración paralela.

## 2. Estrategia: regeneración PARALELA (no destructiva)

Trabajar en `data/raw_regen/`, dejar `data/raw` intacto hasta promover.

Ventajas: rollback trivial (borrar `raw_regen`), sin pérdida de datos, comparación lado a lado.

## 3. Pasos

### 3.1 Preparar directorio paralelo

```bash
rm -rf data/raw_regen && mkdir -p data/raw_regen
cp data/raw/.gitkeep data/raw_regen/.gitkeep 2>/dev/null || true
```

### 3.2 Ejecutar extractores de APIs estables (en orden)

Ejecutar desde `extract/`, salida a `RAW_DIR` → redirigir `RAW_DIR` a `data/raw_regen` (ver 3.6).

1. `01_eustat_api.py`
2. `02_eustat_alquiler.py`
3. `03_euskadi_emancipacion.py`
4. `04_b5m_geo.py`
5. `06_ine_api.py`
6. `07_ine_salarios.py`
7. `10_opendata_bizilagun_etxebide.py`
8. `11_transporte_gtfs_paradas.py`
9. `16_serpavi_renta.py`
10. `17_osrm_tiempos.py`
11. `18_lanbide_paro_juvenil.py`
12. `19_udalmap_indicadores_adicionales.py`
13. `20_ecvi_compraventa.py`
14. `21_lanbide_historico_paro_joven.py`

Anotar fallos por script (Eustat dio 400 en el pasado; hoy 200).

### 3.3 Copiar scraping del backup (NO re-ejecutar)

```bash
cp data/raw_backup_2026-10-29/anuncios_fotocasa* data/raw_regen/
cp data/raw_backup_2026-10-29/anuncios_pisos* data/raw_regen/
cp data/raw_backup_2026-10-29/anuncios_realtyapi* data/raw_regen/
```

### 3.4 Copiar archivos no regenerables del backup

- GTFS (13 ZIP) + shapefile (5 componentes) + HTML Fotocasa (101) + ECVI XLSX (2) + metadatos/control.
- Cualquier archivo del backup no producido por los extractores de 3.2.

Estrategia: copiar **todo** el backup a `raw_regen` y luego sobrescribir con lo regenerado en 3.2 (así no se pierde nada).

```bash
cp -r data/raw_backup_2026-10-29/* data/raw_regen/
# luego ejecutar 3.2 (sobrescribe APIs)
```

### 3.5 Ejecutar transforms derivados en raw_regen

```bash
python transform/corregir_empleo.py
python transform/dim_municipios.py
python transform/validar_renta.py
python transform/completar_alquiler_comarca.py
python transform/parsear_secciones.py
python transform/generar_distancias.py
```

(Requieren que `RAW_DIR` apunte a `raw_regen`.)

### 3.6 Redirección de RAW_DIR

Los scripts usan `extract/_common.py:RAW_DIR`. Opciones:
- Opción (a): variable de entorno / parche temporal en `_common.py` (no recomendado, afecta al repo).
- Opción (b): copiar `extract/` a `extract_regen/` con `RAW_DIR` modificado (más seguro, aislado).
- Opción (c): ejecutar con `PYTHONPATH` y monkeypatch (frágil).

Recomendado: (b) — copia aislada, se borra al terminar.

### 3.7 Verificación contra inventario (`docs/inventario_datos.md`)

Comparar `raw_regen` con el inventario (NO modificarlo). Checklist automatizable:

- [ ] Conteo total de archivos en `raw_regen` ≈ 325 (según inventario; hoy `raw` tiene ~297 + no tabulares).
- [ ] Conteo por categoría (anuncios 28+101+4, alquiler 8+5+4, ECVI 68, GTFS 13, shapefile 5, etc.).
- [ ] Filas por archivo clave: `anuncios_fotocasa.csv` ~471, `anuncios_pisos.csv` ~?, `dim_municipios.csv` 252, `renta_municipal_completa.csv` 252, `alquiler_municipal.csv` ~159+93.
- [ ] Columnas clave presentes: `codigo_ine` (donde aplica), `municipio`, métricas.
- [ ] Sin errores de ejecución en los logs.

Script de verificación: reutilizar `scratchpad/check_paths.py` / `inventory.py` adaptados a `raw_regen`, o escribir uno nuevo `scratchpad/verify_regen.py`.

### 3.8 Decisión de promoción

- Si la verificación pasa → promover:
  ```bash
  mv data/raw data/raw_pre_regen_2026-10-29
  mv data/raw_regen data/raw
  ```
  (mantener `raw_backup_2026-10-29` como último recurso)
- Si falla → descartar `raw_regen`, documentar qué falló, mantener `raw` actual.

### 3.9 Re-congelar y re-manifestar

Tras promover:
```bash
rm -f data/raw/.FROZEN
chmod -R u+w data/raw
# regenerar manifest
find data/raw -type f ! -name .FROZEN | sort | xargs sha256sum > docs/raw_manifest_sha256.txt
touch data/raw/.FROZEN
chmod -R a-w data/raw
```
Ejecutar `tests/test_raw_inmutable.py` → debe pasar.

## 4. Riesgos y mitigación

| Riesgo | Mitigación |
|---|---|
| API falla a mitad | Log por script; reintentar; si persiste, documentar y usar backup |
| Scraping no regenerable | Copiar del backup (3.3) |
| raw_regen inconsistente | No promover; descartar y analizar |
| Pérdida de datos | `raw` intacto hasta promoción; backups múltiples |
| Tests rotos | Ejecutar `pytest tests/` antes de promover |

## 5. Deuda técnica (fuera de este plan)

La regeneración **no** elimina la entity resolution en raw (los extractores la añaden en origen y el backup de scraping la incluye). Para cumplir la regla bronce estricta se requiere una fase posterior:
- Mover `enriquecer_codigo_ine.py` a `procesado/`.
- Eliminar entity resolution de scrapers (guardar solo datos fuente).
- Actualizar tests para leer `codigo_ine` desde `procesado/`.

Esta fase se planificará por separado tras validar la regeneración.

## 6. Estimación

- Ejecución de APIs: ~20-40 min (depende de rate limits).
- Copias: ~2 min.
- Transforms: ~5 min.
- Verificación: ~5 min.
- Total: ~1 hora.

## 7. Decisión requerida

Confirmar antes de ejecutar:
- [ ] ¿Regeneración paralela (recomendada) o destructiva?
- [ ] ¿Se crea copia aislada de `extract/` para redirigir `RAW_DIR`?
- [ ] ¿Se promueve automáticamente si la verificación pasa, o se revisa manualmente?

---

## 8. Ejecución (2026-10-29)

- Regeneración paralela ejecutada en `data_regen/` (backup base: `data/raw_backup_2026-10-29/`).
- APIs ejecutadas: 02, 03, 04, 06, 07, 10, 11, 16, 17, 18, 19, 20, 21 (OK). `01_eustat_api` falló HTTP 400 en todos los endpoints (bloqueo temporal del servidor Eustat); esos archivos provienen del backup.
- Transforms derivados ejecutados: corregir_empleo, dim_municipios, validar_renta, completar_alquiler_comarca, parsear_secciones, generar_distancias (OK). Corregidos bugs de dtype=str en corregir_empleo y validar_renta.
- Verificación estructural: filas clave OK (dim_municipios 252, renta 252, fotocasa 471, pisos 235, udalmap 252).
- Promoción: `data/raw` → `data/raw_pre_regen_2026-10-29/` (copia); `data_regen/raw` → `data/raw`.
- Re-congelado: `data/raw/.FROZEN` creado, `chmod -R a-w`.
- Manifest regenerado: `docs/raw_manifest_sha256.txt` (301 archivos).
- `tests/test_raw_inmutable.py`: 2 passed.
