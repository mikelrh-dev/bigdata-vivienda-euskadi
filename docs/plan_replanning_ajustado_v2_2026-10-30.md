# Plan de re-planning ajustado (v2) — bigdata-vivienda-euskadi

**Fecha:** 2026-10-30
**Basado en:** Reevaluación de 7 claims corregidos (verificados con datos reales) + auditoría integral + veredicto externo
**Objetivo:** Ajustar conclusiones y plan de acción con datos corregidos, listo para aprobación

---

## 0. Correcciones verificadas (7 claims)

| # | Claim | Valor anterior | Valor corregido | Verificado |
|---|---|---|---|---|
| 1 | Raw count desfase | 316 vs 317 | 319 total = 316 manifest + 3 auxiliares | ✅ Sin desfase |
| 2 | Silver intersección | 86 comunes / 18 perdidos | 92 comunes (91 tabular) / 14 perdidos (11 tabular + 3 no-tabular) | ✅ Corregido |
| 3 | Media puntuación | 8,6 | 8,24 ≈ 8,2 | ✅ Corregido |
| 4 | Robustos | 4 | 6 (Bilbao 239, Donostia 130, Vitoria 48, Getxo 40, Abanto 31, Ayala 30) | ✅ Corregido |
| 4b | Metodología IDW | "comarcal" | IDW_5_vecinos (no comarcal) | ✅ Corregido |
| 4c | Salario ajustado | 1381 € | mediana 1401,66 € (≈1402) | ✅ Corregido |
| 4d | Tensión social | 76 alta | 73 alta / 102 media / 77 baja | ✅ Corregido |
| 4e | Duplicados | 13,45% | 13,06% (114 filas extra en 93 grupos) | ✅ Corregido |
| 5 | codigo_ine='0' en educación/salud | Sí (2 JSONs) | No reproducido — todos 5 dígitos. Solo 2 vacíos en Fotocasa base | ✅ Falso (corregido) |
| 6 | ECVI mapeo 252/252 | "no visto" | Existe con 252/252, 0 null | ✅ Confirmado |
| 6b | Certificados A-G 252/252 | "parcial 7/10" | Distribución real completa (E=175, G=74, F=2, A=1) | ✅ Confirmado |
| 7 | Equipamiento | 139/840 | 134/873 | ✅ Corregido |
| 7b | Trazabilidad modalidad/equipamiento/población joven | "no documentado" | Documentado parcialmente (modalidad sí, equipamiento con conteo desactualizado, poblacion_joven null sí) | ✅ Parcial |
| 7c | EMAL/SERPAVI/transporte en gaps doc | "no documentado" | EMAL y SERPAVI no en gaps doc; transporte sí (sin estrategia null-handling) | ✅ Parcial |

---

## 1. Correcciones de documentación (prioridad 1, esfuerzo bajo, read-only sobre docs)

| # | Acción | Archivo | Detalle |
|---|---|---|---|
| D1 | Corregir media 8,6 → 8,24 | `argon/README_ARGON.md`, `argon/estado_proyecto_2026-10-29.md` | Media real sobre 42 scores = 8,24 |
| D2 | Corregir "30 preguntas ≥9" → 22/42 | `argon/estado_proyecto_2026-10-29.md` | Real: 22/42 (52%), no 30 (71%) |
| D3 | Reescribir metodologia.md con números canónicos | `docs/metodologia.md` | IDW (no comarcal) para 93, 6 robustos (no 4), salario ajustado 1402€ (no 1381), tensión 73/102/77 (no 76), duplicados 13,06% (no 13,45%) |
| D4 | Congelar decisión "no ranking municipal fino" | `docs/metodologia.md` | Solo 6 robustos + tipología. Evita ataque en defensa por F5/B6 |
| D5 | Corregir trazabilidad (equipamiento 134/873) | `docs/trazabilidad_datos.md` | Conteo actualizado |
| D6 | Añadir EMAL (73/252), SERPAVI (89 nulls), estrategia null-handling | `docs/gaps_misconceptions_errores.md` | Tabla de gaps + estrategia por fuente |
| D7 | Actualizar scores F5 → 7/10, C5 → mantener 7/10 | `docs/informe_preguntas_respuesta.md`, `docs/preguntas_analisis_profesional.md` | F5: mapeo ECVI 252/252 disponible. C5: cobertura completa pero sin impacto en coste |

## 2. Correcciones de calidad (prioridad 2, esfuerzo bajo-medio)

| # | Acción | Archivo | Detalle |
|---|---|---|---|
| Q1 | Sanear código_ine vacío en Fotocasa JSONs (2 filas) | `transform/normalizar_json_crudos.py` | Convertir '' a null, no modificar raw (educación/salud no tienen '0') |
| Q2 | Añadir BOM a 6 CSVs sin utf-8-sig | `generar_cert_energetico_municipal.py`, `generar_mercado_area_funcional.py`, `calcular_renta_joven.py`, `calcular_tension_social.py`, `limpiar_ecvi.py`, `limpiar_eustat_demografia.py`, `enriquecer_gtfs_conectividad.py` | `encoding="utf-8-sig"` en to_csv |
| Q3 | Determinismo: reemplazar datetime.now()/uuid | `f4_pisos_dirigido.py`, `filtrar_outliers.py` | Usar hash del contenido o seed fijo |
| Q4 | Consumir property_fingerprint en dedup cross-portal | `unificar_anuncios.py` | Agrupar por fingerprint, marcar duplicados. Bajar de 13,06% a <1% |
| Q5 | Documentar EMAL (73/252), SERPAVI (89 nulls), transporte (51 nulls) | `docs/gaps_misconceptions_errores.md` | Estrategia de null-handling por fuente |
| Q6 | Fortalecer _raw_guard.py | `transform/_raw_guard.py` | Verificar .FROZEN + persistir audit log (no solo validar reason) |

## 3. Implementación MongoDB + Aggregation (prioridad 3, esfuerzo alto)

| # | Acción | Detalle | P-04 |
|---|---|---|---|
| A1 | Crear capa MongoDB con PyMongo | Colecciones: municipios, anuncios, indicadores | RA3 |
| A2 | Aggregation Pipeline ≥4 etapas | $match → $group → $lookup → $project (ej: esfuerzo por tipología) | RA3 |
| A3 | Visualizaciones desde PyMongo cursors | Gráficos conectados a resultados de aggregation | RA3 |
| A4 | Tests de aggregation | Verificar ≥4 etapas, resultados correctos | RA3 |

## 4. Recuperación de derivados (prioridad 4, esfuerzo medio)

| # | Acción | Detalle |
|---|---|---|
| R1 | Evaluar los 14 derivados en procesado_pre_silver | Determinar cuáles regenerar vs descartar |
| R2 | Crear generadores para los que se regeneren | Seguir patrón de los 4 generadores huérfanos ya creados |
| R3 | Re-ejecutar compare_calidad.py tras restauración | Verificar 0 regresiones en el conjunto completo |

## 5. Verificación final

```bash
# 1. Raw
pytest tests/test_raw_inmutable.py tests/test_raw_guardrails.py -q

# 2. Inventario
# Regenerar counts desde data/procesado/

# 3. Calidad
python transform/compare_calidad.py  # si existe
python transform/auditoria_duckdb.py  # si existe

# 4. Preguntas
# Reevaluar informe_preguntas_respuesta.md con números corregidos

# 5. Metodología
# Verificar metodologia.md con IDW, 6 robustos, salario ajustado 1402, tensión 73/102/77, duplicados 13,06%

# 6. Tests completos
pytest tests/ -q
```

## Criterios de éxito

1. Raw: 0 mismatches, .FROZEN presente, guardrails pasan.
2. Silver: 0 CSVs sin BOM, 0 codigo_ine inválidos, duplicados <1%.
3. Documentación: counts consistentes (319 raw, 104 silver), media 8,24, 6 robustos, equipamiento 134/873.
4. Metodología: IDW documentado, salario ajustado 1402, tensión 73/102/77, duplicados 13,06%, decisión no-ranking congelada.
5. Gaps doc: EMAL/SERPAVI/transporte con estrategia null-handling.
6. MongoDB: colecciones + aggregation ≥4 etapas + tests.
7. pytest: 66+ (sin regresiones).

## Notas

- Infraestructura (HDFS, Kafka) se incluye solo en la fase de implementación MongoDB (A1-A4). HDFS y Kafka quedan fuera del alcance actual (según petición del usuario).
- Todos los cambios son quirúrgicos y no tocan data/raw/.
- El working tree debe limpiarse con commits atómicos antes de la defensa.
- Los claims del veredicto externo que eran inexactos (codigo_ine='0', 18 perdidos, 86 intersección, 76 alta, 13,45% duplicados, 139 equipamiento, 8,6 media, 4 robustos, ECVI no visto, C5 parcial) han sido corregidos con datos verificados.