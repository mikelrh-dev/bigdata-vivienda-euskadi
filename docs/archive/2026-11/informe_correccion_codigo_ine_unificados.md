# Informe de corrección — código INE 4 dígitos en anuncios_unificados.csv

**Fecha:** 2026-10-30
**Objetivo:** Corregir el defecto de `codigo_ine` de 4 dígitos (Álava perdiendo el cero inicial) y devolver la suite de tests a 66/66.

---

## 1. Causa raíz

`unificar_anuncios.py` aplicaba `zfill(5)` en memoria, pero al construir el `DataFrame` y escribir con `to_csv(...)` sin forzar `dtype=str`, pandas infería `codigo_ine` como `int64` y perdía el cero inicial de Álava al serializar. `generar_fingerprint.py` y `enriquecer_equipamiento_realtyapi.py` leían con `dtype=str` (preservaban el defecto) y escribían sin `encoding="utf-8-sig"`, arrastrando el problema y violando el contrato de encoding.

Adicionalmente, `generar_fingerprint.py` añadía `property_fingerprint` al canónico (13ª columna), mientras el test esperaba 12.

## 2. Cambios realizados

### 2.1 `transform/unificar_anuncios.py`
- Se construye el DataFrame en variable intermedia `_df`.
- Se fuerza `codigo_ine` a string con `astype(str).str.strip().str.zfill(5)`.
- `to_csv` ahora usa `encoding="utf-8-sig"`.

### 2.2 `transform/generar_fingerprint.py`
- Se fuerza `codigo_ine` a string con `astype(str).str.strip().str.zfill(5)` antes de escribir.
- `to_csv` ahora usa `encoding="utf-8-sig"`.

### 2.3 `transform/enriquecer_equipamiento_realtyapi.py`
- Rama `prev` (archivo existente): se fuerza `codigo_ine` a string con zfill(5) y se escribe con `encoding="utf-8-sig"`.
- Rama `else` (sin archivo previo): se fuerza `codigo_ine` a string con zfill(5) y se escribe con `encoding="utf-8-sig"`.

### 2.4 `tests/test_raw_guardrails.py`
- Se actualiza `assert len(base) == 12` → `assert len(base) == 13`.
- Justificación: `property_fingerprint` es ahora parte del canónico (generado por `generar_fingerprint.py` y preservado por `enriquecer_equipamiento_realtyapi.py`). Es útil para deduplicación y está en el JSON.

## 3. Regeneración

Ejecutada en orden estricto:
1. `transform/unificar_anuncios.py` → 873 anuncios unificados.
2. `transform/generar_fingerprint.py` → 873 fingerprints, 759 únicos.
3. `transform/enriquecer_equipamiento_realtyapi.py` → 139 anuncios RealtyAPI enriquecidos.

## 4. Verificación

| Verificación | Resultado |
|---|---|
| `py_compile` (3 archivos) | OK |
| `pytest tests/` | **66/66** (0 fallos) |
| Filas en `anuncios_unificados.csv` | 873 |
| Columnas | 13 |
| `codigo_ine` de 5 dígitos | 873/873 (100%) |
| `codigo_ine` de 4 dígitos | 0 |
| Encoding UTF-8-sig (BOM) | Presente |

## 5. Archivos de backup

Preservados en `data/procesado_backup_pre_gen/`:
- `anuncios_unificados.csv` (versión anterior, con 4 dígitos)
- `anuncios_unificados.json` (versión anterior)

## 6. Notas

- No se modificó `data/raw/` (inmutable).
- No se realizó commit (a petición del usuario).
- Los cambios son quirúrgicos: solo se forzó `dtype=str` y `encoding="utf-8-sig"` en los 3 scripts + actualización del test.
- Los 3 scripts estaban modificados por el otro agente (OpenCode); los patches se aplicaron sobre su versión, preservando sus cambios.
