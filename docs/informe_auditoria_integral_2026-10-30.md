# Informe de auditoría integral — bigdata-vivienda-euskadi

**Fecha:** 2026-10-30
**Modo:** Read-only (ningún archivo modificado, creado ni eliminado durante la auditoría)
**Alcance:** Capa Raw (Landing Zone), Capa Transform/Silver, Reproducibilidad y Pruebas

---

## Resumen ejecutivo

- **Raw inmutable certificado:** `.FROZEN` presente, manifest SHA-256 con 316 entradas, 0 mismatches, 0 missing.
- **Suite de tests:** 66/66 pasan.
- **Sin hallazgos CRÍTICOS.** 2 ALTO, 5 MEDIO, 6 BAJO, varios INFO.

---

## 1. Capa Raw (Landing Zone)

### ALTO
| # | Hallazgo | Archivo | Causa raíz |
|---|---|---|---|
| A1 | Encoding Latin-1 (no UTF-8-sig) | `etxebide_indicador_86.csv` | Byte `0xc1`; falla `pd.read_csv(..., encoding="utf-8-sig")`. Anomalía documentada #1. |
| A2 | `codigo_ine='0'` en lugar de null/5-digit | `educacion_centros.json`, `salud_centros.json` | 1 valor inválido cada uno; rompe joins con `dim_municipios`. |

### MEDIO
| # | Hallazgo | Archivos | Causa raíz |
|---|---|---|---|
| M1 | Sin `fecha_extraccion` (11) | b5m_catalogo, dim_municipios (usa `fecha`), distancias_municipios, emal_fianzas_ampliado, ine_atlas_renta (usa `fecha_conversion`), lanbide_paro_juvenil, osrm_tiempos_capitales, renta_municipal_completa (usa `fecha_conversion`), serpavi_renta_municipal, udalmap_empleo_corregido, distancias_b5m_gipuzkoa | Anomalías históricas #2–#11; saneamiento en `transform/normalizar_json_crudos.py`. |
| M2 | Sin `fuente` (3) | b5m_catalogo, emancipacion_juventud_resumen, ovj_salario_joven_2024 | Anomalía documentada. |
| M3 | Sin `url` (41) y sin `n_registros` (51) | anuncios, distancias, indicadores JSONs | Aceptado como variante histórica (contrato §11.12). |

### BAJO
| # | Hallazgo | Archivos | Causa raíz |
|---|---|---|---|
| B1 | 2 JSONs sin envelope `metadata` (top-level) | emancipacion_juventud_resumen, ovj_salario_joven_2024 | Estructura distinta; aceptada. |

### INFO
- `_raw_guard.py` funcional (`assert_raw_writable` valida reason non-empty).
- Solo 5/60 JSONs fully compliant con las 4 claves canónicas; el resto usa variantes aceptadas (`n_anuncios`, `n_filas`, `n_centros`, `fecha`, `fecha_conversion`, `fuente_url`).
- Guardrails tests: 9 passed.
- Manifest: 316 entradas, 0 mismatches, 0 missing, 3 extra (`.FROZEN`, `.gitkeep`, `manifest_sha256.txt` — auxiliares documentados).

---

## 2. Capa Transform / Silver

### MEDIO
| # | Hallazgo | Archivos | Causa raíz |
|---|---|---|---|
| M4 | 6 CSVs sin BOM (no utf-8-sig) | cert_energetico_municipal_252, comparativa_compra_alquiler_af, ecvi_compraventa_limpio, dim_municipios_enriquecido, eustat_demografia_renta_252, transporte_paradas_municipio_enriquecido | Scripts usan `encoding="utf-8"` o default (`generar_cert_energetico_municipal.py`, `generar_mercado_area_funcional.py`, `calcular_renta_joven.py`, `calcular_tension_social.py`, `limpiar_ecvi.py`, `limpiar_eustat_demografia.py`, `enriquecer_gtfs_conectividad.py`). |
| M5 | No-determinismo: `datetime.now()` + `uuid.uuid4()` en nombres de archivos raw | `f4_pisos_dirigido.py` | Wall-clock/UUID en metadata y nombres de lote; rompe reproducibilidad byte-for-byte. |
| M6 | No-determinismo: `datetime.now().isoformat()` en metadata JSON | `filtrar_outliers.py` | Marca temporal innecesaria en metadatos. |

### BAJO
| # | Hallazgo | Archivos | Causa raíz |
|---|---|---|---|
| B2 | `codigo_ine` vacío (2 filas) | `anuncios_fotocasa_enriquecido.csv` (Las Rozas de Madrid, fuera de Euskadi) | Legítimo (municipio fuera de alcance). |
| B3 | `codigo_ine` vacío (22 filas) | `ecvi_compraventa_limpio.csv` (agregados territorio/área funcional) | Legítimo (sin código municipal). |
| B4 | Riesgo latente zfill-on-NaN | `enriquecer_equipamiento_realtyapi.py` | Si hubiera códigos faltantes, `str(NaN).zfill(5)` → `"00nan"`. No ocurre actualmente. |
| B5 | Latin-1 no decodificado explícitamente | `corregir_empleo.py` | Input ya es UTF-8-sig; script no maneja Latin-1 directamente (declarativo). |

### INFO
- 39 scripts en `transform/` compilan (py_compile OK).
- `unificar_anuncios.py`, `generar_fingerprint.py`, `enriquecer_equipamiento_realtyapi.py`: zfill(5) preservado, encoding utf-8-sig, columnas consistentes con contrato de 13 columnas.
- `normalizar_json_crudos.py`: inyecta `fecha_extraccion`, normaliza `codigo_ine` recursivamente, escribe solo en `procesado/`.
- `corregir_empleo.py`: valida rangos, escribe solo en `procesado/`.
- No hay escrituras no guardadas en raw: solo `enriquecer_codigo_ine.py` (`--write-raw --reason`) y `f4_pisos_dirigido.py` (append-only, guardado por `assert_raw_writable`).
- Guardrails: 66/66 pasan.

---

## 3. Reproducibilidad y pruebas

### BAJO
| # | Hallazgo | Detalle | Causa raíz |
|---|---|---|---|
| B6 | Scripts generadores sobrescriben sin guard de existencia | 15 de 16 `generar_*.py` | Aceptable para regeneración determinista, pero sin protección contra sobrescritura accidental. |
| B7 | `generar_f4_pisos_objetivo.py` genera 238 códigos vs 62 manuales | Documentado como excepción (selección ad-hoc) | Criterio original no reproducible por regla simple. |

### INFO
- 104 archivos en `data/procesado/`, todos mapeados a generadores en `transform/` (directos, dinámicos o `normalizar_json_crudos.py`).
- 16 `generar_*.py`, todos funcionales (verificados en ejecución aislada).
- 4 generadores huérfanos creados y funcionales: `generar_cert_energetico_moda_municipio.py` (252 filas), `generar_anuncios_residencial_filtrado.py` (570 filas, 16 outliers), `generar_fotocasa_dirigido_informe.py` (62 filas), `generar_f4_pisos_objetivo.py` (62 códigos, idempotente).
- `_raw_guard.py` usa `datetime.now()` solo para log de auditoría (no en datos) — no es defecto de reproducibilidad.
- `pytest`: **66/66 pasan**, 0 fallos, 2.09s.

---

## 4. Veredicto

| Área | Estado |
|---|---|
| Raw inmutable | ✅ Certificado (manifest + .FROZEN) |
| Contrato encoding | ⚠️ 1 archivo Latin-1 (documentado) |
| Contrato metadata | ⚠️ 9 JSONs sin fecha_extraccion/fuente (documentado) |
| codigo_ine zfill(5) raw | ✅ CSVs OK; 2 JSONs con '0' inválido |
| codigo_ine zfill(5) silver | ✅ 100% en CSVs (tras corrección) |
| Encoding silver (BOM) | ⚠️ 6 CSVs sin BOM |
| No-determinismo | ⚠️ 2 scripts (f4_pisos_dirigido, filtrar_outliers) |
| Reproducibilidad | ✅ Todos los outputs mapeados a generadores |
| Tests | ✅ 66/66 |
| Raw writes guardados | ✅ Solo allowlisted |

**Sin hallazgos críticos.** El sistema está en buen estado. Los hallazgos ALTO/MEDIO son documentados y tienen saneamiento asignado a `transform/`. Los MEDIO de BOM y no-determinismo son mejoras recomendadas pero no bloqueantes.

---

*Auditoría realizada en modo read-only. Ningún archivo fue modificado, creado ni eliminado durante la auditoría.*