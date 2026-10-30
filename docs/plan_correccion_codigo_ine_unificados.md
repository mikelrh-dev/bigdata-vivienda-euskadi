# Plan de corrección — código INE 4 dígitos y test 66/66

**Fecha:** 2026-10-30
**Objetivo:** Corregir el defecto de `codigo_ine` de 4 dígitos en `anuncios_unificados.csv` (Álava perdiendo el cero inicial) y devolver la suite de tests a 66/66.

**Causa raíz:** `unificar_anuncios.py` aplica `zfill(5)` en memoria pero al construir el `DataFrame` y escribir con `to_csv(...)` sin forzar `dtype=str`, pandas infiere `codigo_ine` como `int64` y pierde el cero inicial. `generar_fingerprint.py` y `enriquecer_equipamiento_realtyapi.py` leen con `dtype=str` (preservan el defecto) y escriben sin `encoding="utf-8-sig"`.

---

## Paso 1 — Patch `unificar_anuncios.py`

**Archivo:** `transform/unificar_anuncios.py`
**Línea objetivo:** el bloque `pd.DataFrame([...]).to_csv(...)` final (línea ~310).

**Cambio:** forzar la columna `codigo_ine` a string en el DataFrame y añadir `encoding="utf-8-sig"`.

```python
# ANTES:
    pd.DataFrame([{
        "id_anuncio": r["id_anuncio"],
        ...
        "codigo_ine": r["ubicacion"]["codigo_ine"],
        ...
    } for r in recs]).to_csv(os.path.join(OUT, "anuncios_unificados.csv"), index=False)

# DESPUES:
    _df = pd.DataFrame([{
        "id_anuncio": r["id_anuncio"],
        ...
        "codigo_ine": r["ubicacion"]["codigo_ine"],
        ...
    } for r in recs])
    _df["codigo_ine"] = _df["codigo_ine"].astype(str).str.strip().str.zfill(5)
    _df.to_csv(os.path.join(OUT, "anuncios_unificados.csv"), index=False, encoding="utf-8-sig")
```

## Paso 2 — Patch `generar_fingerprint.py`

**Archivo:** `transform/generar_fingerprint.py`
**Líneas objetivo:** 39-60.

**Cambios:**
1. Forzar `codigo_ine` a string en el DataFrame (línea 45).
2. Añadir `encoding="utf-8-sig"` en `to_csv` (línea 60).

```python
# Linea 45: "codigo_ine": r["ubicacion"]["codigo_ine"],
# Cambiar a: "codigo_ine": str(r["ubicacion"]["codigo_ine"]).zfill(5) if r["ubicacion"].get("codigo_ine") else None,

# Linea 60: df.to_csv(csv_path, index=False)
# Cambiar a: df.to_csv(csv_path, index=False, encoding="utf-8-sig")
```

Además, forzar dtype en la construcción:
```python
df = pd.DataFrame([...])
df["codigo_ine"] = df["codigo_ine"].astype(str).str.strip().str.zfill(5)
```

## Paso 3 — Patch `enriquecer_equipamiento_realtyapi.py`

**Archivo:** `transform/enriquecer_equipamiento_realtyapi.py`
**Líneas objetivo:** 76 (rama prev) y 88 (rama else).

**Cambios:**
1. Rama prev (línea 76): `prev.to_csv(csv_path, index=False)` → `prev.to_csv(csv_path, index=False, encoding="utf-8-sig")` y forzar `codigo_ine` a str antes.
2. Rama else (línea 88): `df.to_csv(csv_path, index=False)` → `df.to_csv(csv_path, index=False, encoding="utf-8-sig")` y forzar `codigo_ine` a str.

En la rama prev, antes de to_csv:
```python
if "codigo_ine" in prev.columns:
    prev["codigo_ine"] = prev["codigo_ine"].astype(str).str.strip().str.zfill(5)
```

En la rama else:
```python
df["codigo_ine"] = df["codigo_ine"].astype(str).str.strip().str.zfill(5)
df.to_csv(csv_path, index=False, encoding="utf-8-sig")
```

## Paso 4 — Actualizar test

**Archivo:** `tests/test_raw_guardrails.py`
**Línea:** 217.

**Cambio:** `assert len(base) == 12, base` → `assert len(base) == 13, base`

**Justificación:** `property_fingerprint` es ahora parte del canónico (generado por `generar_fingerprint.py` y preservado por `enriquecer_equipamiento_realtyapi.py`). Es una columna útil para deduplicación y está en el JSON. El test debe reflejar el contrato actualizado.

## Paso 5 — Regenerar en secuencia

```bash
cd "C:/Users/mikel/Documents/bigdata-vivienda-euskadi"
.venv/Scripts/python.exe transform/unificar_anuncios.py
.venv/Scripts/python.exe transform/generar_fingerprint.py
.venv/Scripts/python.exe transform/enriquecer_equipamiento_realtyapi.py
```

**Orden obligatorio:** unificar → fingerprint → enriquecer.

## Paso 6 — Verificación

```bash
# py_compile
.venv/Scripts/python.exe -m py_compile transform/unificar_anuncios.py transform/generar_fingerprint.py transform/enriquecer_equipamiento_realtyapi.py

# pytest completo
.venv/Scripts/python.exe -m pytest tests/ -q

# verificar codigo_ine 5 digitos
.venv/Scripts/python.exe -c "
import pandas as pd
df=pd.read_csv('data/procesado/anuncios_unificados.csv', dtype=str)
vals=df['codigo_ine'].astype(str)
print('total:', len(df))
print('lens:', vals.str.len().value_counts().to_dict())
print('all 5 digits:', vals.str.match(r'^\d{5}$').all())
"
```

## Criterios de éxito

1. `py_compile` sin errores en los 3 archivos.
2. `pytest` → 66/66 (0 fallos).
3. `codigo_ine` en `anuncios_unificados.csv` → 100% de 5 dígitos (0 de 4 dígitos).
4. Encoding UTF-8-sig en el CSV (BOM presente).
5. `property_fingerprint` preservada en el CSV (13 columnas).

## Riesgos

- **Conflictos con OpenCode:** los 3 scripts están modificados por el otro agente. Si hay conflictos al integrar, resolver manualmente preservando los cambios de ambos.
- **Orden de ejecución:** fingerprint depende del output de unificar; enriquecer depende de ambos. Ejecutar en orden estricto.
- **Backup:** antes de ejecutar, hacer backup de `anuncios_unificados.csv` y `anuncios_unificados.json` en `data/procesado_backup_pre_gen/`.

## Notas

- No se toca `data/raw/` (inmutable).
- No se commitea (a petición del usuario).
- Los cambios son quirúrgicos: solo se fuerza `dtype=str` y `encoding="utf-8-sig"` en los 3 scripts + actualización del test.
