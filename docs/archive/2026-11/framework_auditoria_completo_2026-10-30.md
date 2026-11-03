# Framework de Auditoría Completo (MSA) — bigdata-vivienda-euskadi

**Versión:** 2.0
**Fecha:** 2026-10-30
**Alcance:** Obtención + Transformación + Presentación + Documentación
**Fuera de alcance:** HDFS, Kafka, MongoDB, Aggregation Pipeline, PyMongo
**Estado del proyecto:** Fase de obtención+transformación completada; infraestructura diferida

---

## 0. Objetivo y alcance

Este framework define una auditoría multi-etapa (MSA) que puede ejecutarse en cualquier momento para verificar el estado del proyecto. Cada etapa produce un veredicto por criterio: **CUMPLE / PARCIAL / NO CUMPLE** (o **COMPLIANT / VIOLATION / PARTIAL** para prohibiciones).

### Reglas de ejecución
- **Read-only:** No modificar, crear ni borrar archivos durante la auditoría.
- **Evidencia obligatoria:** Cada veredicto debe citar file paths, counts, test results o output de comandos.
- **Subagentes:** Usar hasta 2 subagentes en paralelo (read-only) para etapas independientes.
- **Checklist final:** Al terminar, generar `docs/auditoria_msa_<fecha>.md` con todos los resultados.

---

## 1. Etapas de auditoría

### Etapa 1 — Capa Raw (Landing Zone)

**Objetivo:** Verificar inmutabilidad, contrato, encoding y estandarización de `data/raw/`.

| # | Check | Comando / Evidencia | Criterio CUMPLE |
|---|---|---|---|
| 1.1 | `.FROZEN` presente | `ls data/raw/.FROZEN` | Archivo existe |
| 1.2 | Manifiesto SHA-256 válido | `python tests/test_raw_inmutable.py` | 0 mismatches |
| 1.3 | Contrato de datos raw | `cat docs/contrato_datos_raw.md` (secciones 1-12) | Documentado con opt-in + anomalías + excepciones |
| 1.4 | Encoding utf-8-sig en raw | `file -i data/raw/*.csv` o Python check | CSVs con BOM; JSONs en UTF-8 |
| 1.5 | codigo_ine estandarizado | `python -c "..."` (zfill(5) en silver) | 100% 5 dígitos en procesado |
| 1.6 | Metadata en raw JSONs | `python -c "import json; ..."` | ≥90% con fuente + fecha + n_registros |
| 1.7 | HTML raw preservado | `ls data/raw/html_fotocasa/` | ≥100 páginas |
| 1.8 | `_raw_guard.py` funcional | `python transform/_raw_guard.py --check` | 0 violaciones |
| 1.9 | No credenciales en repo | `git ls-files | grep -E '\.env\|api\.txt'` | Vacío (ignorados) |
| 1.10 | Raw count consistente | `ls data/raw/ | wc -l` vs manifest | 319 = 316 + .FROZEN + .gitkeep + manifest |

**Veredicto Etapa 1:** CUMPLE si ≥9/10 checks pasan.

---

### Etapa 2 — Capa Transform / Silver

**Objetivo:** Verificar normalización, limpieza, enriquecimiento, dedup, outliers, null-handling.

| # | Check | Comando / Evidencia | Criterio CUMPLE |
|---|---|---|---|
| 2.1 | Scripts py_compile | `python -m compileall transform/` | 0 errores |
| 2.2 | Normalización JSON crudos | `python transform/normalizar_json_crudos.py` (dry-run check) | Empty codigo_ine → null |
| 2.3 | BOM en todos los CSVs procesados | Python check `read(3) == b'\xef\xbb\xbf'` | 0 sin BOM |
| 2.4 | codigo_ine 5 dígitos | `python -c "df['codigo_ine'].str.len().value_counts()"` | 100% len=5 |
| 2.5 | Dedup por (portal, id_anuncio) | `python transform/unificar_anuncios.py` (check) | 0 duplicados exactos |
| 2.6 | Fingerprint cross-portal | `grep property_fingerprint transform/unificar_anuncios.py` | Consumido en dedup |
| 2.7 | Outliers marcados (no borrados) | `grep es_outlier transform/filtrar_outliers.py` | Flags presentes, valores originales conservados |
| 2.8 | Validación de rangos | `grep corregir_empleo transform/corregir_empleo.py` | Rangos validados |
| 2.9 | Nulls explícitos (no 0) | `python tests/test_raw_guardrails.py` (test_limpieza_nulos_explicitos) | Pasa |
| 2.10 | Null-handling documentado | `grep -A3 "Null-handling" docs/gaps_misconceptions_errores.md` | Estrategia por fuente |
| 2.11 | EMAL cobertura documentada | `grep "73 / 252" docs/gaps_misconceptions_errores.md` | 73/252 documentado |
| 2.12 | SERPAVI imputado o documentado | `ls data/procesado/serpavi_renta_imputado.csv` o docs | Imputado o estrategia documentada |
| 2.13 | Transporte sin nulls operadores | `python -c "df['operadores'].isna().sum()"` | 0 nulls (sin_servicio) |
| 2.14 | VPO documentado como limitación | `grep "VPO" docs/gaps_misconceptions_errores.md` | Documentado |
| 2.15 | ECVI precio_m2 usada capturado | `python -c "df['precio_m2_usada_eur'].notna().sum()"` | ≥10 no null |

**Veredicto Etapa 2:** CUMPLE si ≥13/15 checks pasan.

---

### Etapa 3 — Reproducibilidad

**Objetivo:** Verificar que todos los outputs tienen generador, son idempotentes y deterministas.

| # | Check | Comando / Evidencia | Criterio CUMPLE |
|---|---|---|---|
| 3.1 | Generadores para todos los CSVs | `ls transform/*.py` vs `ls data/procesado/*.csv` | Cada CSV tiene script |
| 3.2 | Huérfanos identificados | `docs/plan_correccion_10_puntos_debiles_2026-10-30.md` (punto 4) | 14 evaluados, 13 discard, 1 keep |
| 3.3 | Determinismo (sin datetime.now/uuid) | `grep -rn "datetime.now\|uuid.uuid4" transform/` | 0 matches (o documentado) |
| 3.4 | Idempotencia (re-ejecutar = mismo output) | Ejecutar un script 2 veces, comparar hash | Hash idéntico |
| 3.5 | _raw_guard funcional | `python transform/_raw_guard.py --audit` | 0 violaciones |
| 3.6 | Backup pre-generación existe | `ls data/procesado_backup_pre_gen/` | Directorio existe |
| 3.7 | compare_calidad.py existe | `ls scratchpad/compare_calidad.py` | Archivo existe |
| 3.8 | auditoria_duckdb.py existe | `ls transform/auditoria_duckdb.py` | Archivo existe |

**Veredicto Etapa 3:** CUMPLE si ≥7/8 checks pasan.

---

### Etapa 4 — Tests automatizados

**Objetivo:** Verificar que la suite de tests pasa sin regresiones.

| # | Check | Comando | Criterio CUMPLE |
|---|---|---|---|
| 4.1 | test_contrato.py | `pytest tests/test_contrato.py -q` | All passed |
| 4.2 | test_crudos.py | `pytest tests/test_crudos.py -q` | All passed |
| 4.3 | test_raw_inmutable.py | `pytest tests/test_raw_inmutable.py -q` | All passed |
| 4.4 | test_raw_guardrails.py | `pytest tests/test_raw_guardrails.py -q` | All passed |
| 4.5 | Suite completa | `pytest tests/ -q` | ≥66 passed, 0 failed |
| 4.6 | py_compile todos los scripts | `python -m compileall extract/ transform/ tests/` | 0 errores |
| 4.7 | No tests skipped inesperados | `pytest tests/ -q -rs` | 0 skipped (o justificados) |

**Veredicto Etapa 4:** CUMPLE si 7/7 checks pasan.

---

### Etapa 5 — Presentación de resultados

**Objetivo:** Verificar gráficos, interpretación, conclusión.

| # | Check | Comando / Evidencia | Criterio CUMPLE |
|---|---|---|---|
| 5.1 | ≥3 tipos de gráfico | `grep -E "bar\|scatter\|boxplot\|hist" transform/generar_dashboard_*.py` | Barras + dispersión + boxplot |
| 5.2 | Títulos en gráficos | `grep "set_title\|title=" transform/generar_dashboard_*.py` | Presentes |
| 5.3 | Unidades en ejes | `grep "xlabel\|ylabel\|set_xlabel\|set_ylabel" transform/generar_dashboard_*.py` | Presentes |
| 5.4 | Leyendas | `grep "legend\|hue=" transform/generar_dashboard_*.py` | Presentes |
| 5.5 | Comparación por territorio/municipio | `grep "groupby\|hue=" transform/generar_dashboard_*.py` | Presente |
| 5.6 | ≥3 resultados con causa/implicación | `wc -l docs/informe_preguntas_respuesta.md` + lectura | Documentado |
| 5.7 | Conclusión con municipios concretos | `grep -E "Bilbao\|Donostia\|Vitoria" docs/informe_preguntas_respuesta.md` | Presente |
| 5.8 | Advertencia de muestra pequeña | `grep -i "robusto\|muestra\|n≥30\|n>=30" docs/informe_preguntas_respuesta.md` | Presente |
| 5.9 | Dashboards HTML existen | `ls data/resultados/*.html` o `data/procesado/*.html` | ≥1 dashboard |
| 5.10 | Gráficos no hardcoded | `grep -v "plt.text\|annotate" transform/generar_dashboard_*.py | grep -c "read_csv\|pd.read"` | Lee de CSV |

**Veredicto Etapa 5:** CUMPLE si ≥9/10 checks pasan.

---

### Etapa 6 — Prohibiciones (P-01 a P-08)

**Objetivo:** Verificar cumplimiento de las 8 prohibiciones del contrato.

| # | Prohibición | Check | Criterio COMPLIANT |
|---|---|---|---|
| 6.1 | P-01: No compraventa como eje | `grep -rn "compraventa" transform/ --include="*.py" \| grep -v "comparativa\|ratio"` | 0 matches en eje principal |
| 6.2 | P-02: No simular valores | Verificar salarios/población/renta provienen de fuentes reales | Fuentes reales documentadas |
| 6.3 | P-03: No INE alquiler para Euskadi | `grep -rn "ine.*alquiler" transform/ --include="*.py"` | 0 matches |
| 6.4 | P-04: No contar etapa única | Verificar que no se reclama agregación como cubierta | Spec marca "Pendiente" |
| 6.5 | P-05: No gráficos hardcoded | `grep -rn "values=\[" transform/generar_dashboard_*.py` | 0 hardcoded |
| 6.6 | P-06: Todo en Python | `find . -name "*.py" | wc -l` vs otros lenguajes | Solo .py |
| 6.7 | P-07: No credenciales en repo | `git ls-files | grep -E '\.env\|api\.txt'` | Vacío |
| 6.8 | P-08: No marcar cubierto sin verificación | Verificar que criterios no implementados no están marcados como cubiertos | Consistente |

**Veredicto Etapa 6:** COMPLIANT si 8/8 pasan.

---

### Etapa 7 — Documentación

**Objetivo:** Verificar que la documentación está actualizada y consistente.

| # | Check | Comando / Evidencia | Criterio CUMPLE |
|---|---|---|---|
| 7.1 | Specs alineados con PDF/DOCX | `cat docs/auditoria_specs_vs_proyecto_2026-10-30.md` | ALINEADO |
| 7.2 | argon/ actualizado | `cat argon/README_ARGON.md` (última fecha) | Fecha reciente |
| 7.3 | metodologia.md consistente | `grep "IDW\|1402\|73/102/77\|13,06%" docs/metodologia.md` | Presente |
| 7.4 | trazabilidad_datos.md consistente | `grep "134/873" docs/trazabilidad_datos.md` | Presente |
| 7.5 | gaps_misconceptions_errores.md actualizado | `grep "SERPAVI.*imputado\|transporte.*sin_servicio" docs/gaps_misconceptions_errores.md` | Presente |
| 7.6 | README principal actualizado | `cat README.md` (o docs/readme) | Fecha reciente |
| 7.7 | Contrato de datos raw reconciliado | `grep "opt-in\|sección 11\|sección 12" docs/contrato_datos_raw.md` | Presente |
| 7.8 | Plan de corrección documentado | `ls docs/plan_correccion_10_puntos_debiles_2026-10-30.md` | Existe |
| 7.9 | Informe de auditoría más reciente | `ls docs/auditoria_*.md` | ≥1 reciente |
| 7.10 | Openspec changes documentados | `ls openspec/changes/` | ≥1 change |

**Veredicto Etapa 7:** CUMPLE si ≥9/10 checks pasan.

---

### Etapa 8 — Calidad de datos (métricas)

**Objetivo:** Verificar métricas clave de calidad de datos.

| # | Métrica | Valor esperado | Fuente |
|---|---|---|---|
| 8.1 | Raw files total | 319 (316 manifest + 3 aux) | `ls data/raw/ \| wc -l` |
| 8.2 | Silver files total | 104 (103 data + .gitkeep) | `ls data/procesado/ \| wc -l` |
| 8.3 | Anuncios unificados | 873 filas, 13 cols | `wc -l data/procesado/anuncios_unificados.csv` |
| 8.4 | codigo_ine 5 dígitos | 100% | Python check |
| 8.5 | Duplicados cross-portal | <1% (0% actual) | `transform/unificar_anuncios.py` |
| 8.6 | Media preguntas análisis | 8.24/10 (42 preguntas) | `docs/informe_preguntas_respuesta.md` |
| 8.7 | Municipios robustos (n≥30) | 6 (Bilbao 239, Donostia 130, Vitoria 48, Getxo 40, Abanto 31, Ayala 30) | `docs/metodologia.md` |
| 8.8 | IDW imputación | 93 municipios | `docs/metodologia.md` |
| 8.9 | Salario ajustado mediana | 1402€ | `docs/metodologia.md` |
| 8.10 | Tensión social | 73 alta / 102 media / 77 baja | `docs/metodologia.md` |
| 8.11 | Duplicados fingerprint | 13.06% (114 filas extra en 93 grupos) | `docs/metodologia.md` |
| 8.12 | Equipamiento | 134/873 | `docs/trazabilidad_datos.md` |
| 8.13 | ECVI mapeo | 252/252, 0 null | `docs/README_ARGON.md` |
| 8.14 | Certificados | 252/252 (E=175, G=74, F=2, A=1) | `docs/README_ARGON.md` |
| 8.15 | EMAL cobertura | 73/252 | `docs/gaps_misconceptions_errores.md` |
| 8.16 | SERPAVI nulls | 0 (imputado) | `data/procesado/serpavi_renta_imputado.csv` |
| 8.17 | Transporte nulls operadores | 0 (sin_servicio) | `data/procesado/transporte_paradas_municipio_enriquecido.csv` |
| 8.18 | ECVI precio_m2 usada | 13/29 | `data/procesado/ecvi_compraventa_limpio.csv` |
| 8.19 | BOM CSVs | 36/36 | Python check |
| 8.20 | Tests | 66/66 | `pytest tests/ -q` |

**Veredicto Etapa 8:** CUMPLE si ≥18/20 métricas coinciden.

---

## 2. Ejecución del framework

### Orden recomendado

```
Etapa 1 (Raw) → Etapa 4 (Tests) → Etapa 2 (Transform) → Etapa 3 (Reproducibilidad) → Etapa 5 (Presentación) → Etapa 6 (Prohibiciones) → Etapa 7 (Documentación) → Etapa 8 (Métricas)
```

### Uso de subagentes
- **Subagente 1:** Etapas 1 + 2 + 3 (read-only, verificación de archivos y scripts)
- **Subagente 2:** Etapas 5 + 6 + 7 + 8 (read-only, verificación de docs y métricas)
- **Orquestador:** Consolida resultados, genera informe final

### Comando de verificación rápida

```bash
# Tests
.venv/Scripts/python.exe -m pytest tests/ -q

# BOM check
.venv/Scripts/python.exe -c "
import glob, os
csvs = glob.glob('data/procesado/*.csv')
bad = [f for f in csvs if open(f,'rb').read(3) != b'\xef\xbb\xbf']
print(f'CSVs: {len(csvs)}, sin BOM: {len(bad)}')
"

# codigo_ine check
.venv/Scripts/python.exe -c "
import pandas as pd, glob
for f in glob.glob('data/procesado/*unificados*.csv'):
    df = pd.read_csv(f, dtype=str)
    if 'codigo_ine' in df.columns:
        print(f, df['codigo_ine'].str.len().value_counts().to_dict())
"

# py_compile
.venv/Scripts/python.exe -m compileall extract/ transform/ tests/ 2>&1 | tail -3

# Raw immutability
.venv/Scripts/python.exe tests/test_raw_inmutable.py
```

---

## 3. Informe de salida

Al terminar la auditoría, generar `docs/auditoria_msa_<YYYY-MM-DD>.md` con:

1. **Resumen ejecutivo:** Tabla de etapas con veredicto (CUMPLE/PARCIAL/NO CUMPLE).
2. **Detalle por etapa:** Cada check con evidencia (file path, count, test result).
3. **Métricas clave:** Tabla de métricas vs esperado.
4. **Puntos débiles:** Lista de checks que fallaron con causa raíz.
5. **Recomendaciones:** Acciones correctivas priorizadas.
6. **Veredicto global:** Nota sobre 10 (solo obtención+transformación+presentación, sin infra).

### Plantilla de veredicto global

| Área | Criterios | CUMPLE | PARCIAL | NO CUMPLE |
|---|---|---|---|---|
| Raw (Etapa 1) | 10 | ? | ? | ? |
| Transform (Etapa 2) | 15 | ? | ? | ? |
| Reproducibilidad (Etapa 3) | 8 | ? | ? | ? |
| Tests (Etapa 4) | 7 | ? | ? | ? |
| Presentación (Etapa 5) | 10 | ? | ? | ? |
| Prohibiciones (Etapa 6) | 8 | ? | ? | ? |
| Documentación (Etapa 7) | 10 | ? | ? | ? |
| Métricas (Etapa 8) | 20 | ? | ? | ? |
| **Total** | **88** | **?** | **?** | **?** |

**Nota esperada (sin infra):** ~9.0 (solo 2 brechas por dependencias externas: FORMATO-01 PARCIAL y DATOS-PYMONGO-01 NO CUMPLE).

---

## 4. Historial de auditorías

| Fecha | Framework | Resultado | Documento |
|---|---|---|---|
| 2026-10-30 | MSA v1.0 (manual) | 17/19 criterios | `docs/auditoria_specs_sin_infra_2026-10-30.md` |
| 2026-10-30 | MSA v2.0 (este framework) | Pendiente | `docs/auditoria_msa_2026-10-30.md` (por generar) |

---

## 5. Notas para el auditor

- **No modificar archivos.** Si se detecta un defecto, documentarlo, no corregirlo.
- **Evidencia obligatoria.** Cada veredicto debe citar file path, count o output de comando.
- **Consistencia.** Los valores deben coincidir con los documentados en argon/README_ARGON.md y docs/metodologia.md.
- **Subagentes.** Usar hasta 2 subagentes read-only en paralelo para etapas independientes.
- **Infraestructura.** No evaluar HDFS, Kafka, MongoDB, PyMongo ni Aggregation Pipeline. Están fuera de alcance.
- **Actualización.** Este framework se actualiza cuando se añaden nuevos criterios o se resuelven puntos débiles.
