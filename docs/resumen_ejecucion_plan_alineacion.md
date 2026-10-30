# Resumen de ejecución — Plan de alineación raw/limpieza/estructura

**Fecha:** 2026-10-30
**Autor:** Hermes Agent (sesión)
**Plan base:** `docs/plan_alineacion_raw_limpieza_estructura.md`

---

## 1. Objetivo

Ejecutar el plan de alineación entre la capa raw (inmutable) y la capa silver (procesado), reconciliando la convención opt-in de raw (ya implementada por OpenCode) con las anomalías históricas detectadas en la primera carga, y creando los generadores faltantes para los 4 archivos huérfanos de `data/procesado/`.

## 2. Bloque 0 — Reconciliación del contrato (docs/contrato_datos_raw.md)

- **No se sobrescribió** el archivo existente (convención opt-in con escape hatch auditado: `_raw_guard.py`, `--write-raw/--reason/--force`, lista blanca).
- Se patcheó añadiendo:
  - **Sección 11 — Anomalías históricas (primera carga):** 13 defectos documentados (Latin-1 en `etxebide_indicador_86.csv`, JSON sin `fecha_extraccion`, uso de `fecha`/`fecha_conversion`, falta de payload original, etc.) con su saneamiento asignado a `transform/`.
  - **Sección 12 — Excepciones documentadas:** `f4_pisos_dirigido.py` (violación controlada de inmutabilidad), `f4_pisos_objetivo.json` (selección manual), `fotocasa_dirigido_informe.csv` (dependencia de red), `filtrar_outliers.py` (no-determinismo cosmético).

## 3. Bloque 1 — Actualización de scripts de extracción (extract/)

8 scripts modificados (solo código, sin ejecución de red):

| Script | Cambio |
|---|---|
| `extract/04_b5m_geo.py` | metadata homogénea (fuente, fecha_extraccion ISO, url, n_registros); lectura UTF-8-sig |
| `extract/10_opendata_bizilagun_etxebide.py` | documentado UTF-8-sig en escritura (fuente Latin-1 saneada) |
| `extract/06_ine_api.py` | añadido `payload_original` + archivo `_raw.json`; n_registros |
| `extract/07_ine_salarios.py` | idem |
| `extract/01_eustat_api.py` | raw GET/POST guardados (`payload_original` + `_raw.json`); n_registros |
| `extract/16_serpavi_renta.py` | añadido url, fecha_extraccion, n_registros |
| `extract/17_osrm_tiempos.py` | idem |
| `extract/18_lanbide_paro_juvenil.py` | idem |

Todos pasan `py_compile`.

## 4. Bloque 2 — Saneamiento en transform/

- `transform/normalizar_json_crudos.py`: inyecta `fecha_extraccion` (file mtime o default documentado) en JSON que carecen de ella; lectura UTF-8-sig.
- `transform/corregir_empleo.py`: comentario documental sobre manejo Latin-1.
- `transform/enriquecer_codigo_ine.py`: comentario documental sobre la excepción de inmutabilidad (ya tenía `--write-raw/--force`).

Todos pasan `py_compile`.

## 5. Bloque 3 — Ejecución de generadores huérfanos

Backup previo en `data/procesado_backup_pre_gen/` (4 archivos).

| Generador | Resultado |
|---|---|
| `generar_cert_energetico_moda_municipio.py` | 252 filas (original tenía 60, subconjunto de versión anterior; no bit-identical — documentado como E1) |
| `generar_anuncios_residencial_filtrado.py` | 570 filas, 16 outliers — **bit-identical** con el original ✓ |
| `generar_fotocasa_dirigido_informe.py` | 62 filas (counts actualizados; original en backup — documentado como E3) |
| `generar_f4_pisos_objetivo.py` | 62 códigos, no modificado (idempotente — documentado como E4) |

Corrección aplicada: `generar_cert_energetico_moda_municipio.py` usaba columna inexistente `cert_energetico_moda` (real: `cert_moda`); se mapeó correctamente. `generar_fotocasa_dirigido_informe.py` se corrigió para incluir todos los objetivos (n=0 si sin raw dirigido).

## 6. Bloque 4 — Documentación de excepciones

Sección 6 añadida a `docs/gaps_misconceptions_errores.md` (E1-E4) con generador, fuente, diferencia y acción para cada huérfano.

## 7. Verificación

- Tests: **65/66 pasan**.
- Único fallo: `test_unificados_columns_superset` (pre-existente, fallaba en HEAD antes de mis cambios). Causa: `anuncios_unificados.csv` tiene 13 columnas vs 12 esperadas — consecuencia de cambios del otro agente en `unificar_anuncios.py`. No tocado por esta ejecución.
- `data/raw/` no modificado.
- No se realizó commit (a petición del usuario).

## 8. Archivos creados/modificados (resumen)

**Creados:**
- `data/procesado_backup_pre_gen/` (4 archivos de backup)
- `docs/contrato_datos_raw.md` (patcheado, no sobrescrito)

**Modificados (código):**
- `extract/`: 8 scripts
- `transform/`: 3 scripts + 4 generadores nuevos (generar_cert_energetico_moda_municipio.py, generar_anuncios_residencial_filtrado.py, generar_fotocasa_dirigido_informe.py, generar_f4_pisos_objetivo.py) + correcciones

**Modificados (docs):**
- `docs/contrato_datos_raw.md`
- `docs/gaps_misconceptions_errores.md`
