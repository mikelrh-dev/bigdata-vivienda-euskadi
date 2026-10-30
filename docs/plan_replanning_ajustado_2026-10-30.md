# Plan de re-planning ajustado — bigdata-vivienda-euskadi

**Fecha:** 2026-10-30
**Basado en:** Re-evaluación read-only (7 tareas verificadas) + veredicto externo + auditoría integral
**Objetivo:** Ajustar conclusiones y plan de acción con datos corregidos

---

## 0. Correcciones a los claims del veredicto externo

La reevaluación verificó que varios claims del veredicto externo eran inexactos:

| Claim externo | Realidad verificada | Fuente |
|---|---|---|
| "manifest 316 vs 317 (1 desfase)" | 319 archivos totales, 316 manifest-listed (resto: .FROZEN, .gitkeep, manifest_sha256.txt) | `ls data/raw/` + `wc -l manifest` |
| "18 derivados perdidos" | 14 archivos solo en procesado_pre_silver (11 tabular + 3 no-tabular) | comparación directorios |
| "86 archivos en intersección" | 92 comunes (90 tabular) | comparación directorios |
| "76 municipios en tensión alta" | 73 alta / 102 media / 77 baja | `tension_social` en procesado |
| "codigo_ine='0' en educación/salud" | No reproducido — todos 5 dígitos. Solo 2 empty en Fotocasa JSONs | verificación directa |
| "media 8.6/10" | Media real = 8.24 ≈ 8.2/10. El 8.6 es desactualizado | cálculo sobre 42 scores |
| "robustos 4 vs 6 (Donostia)" | 6 robustos (Bilbao 239, Donostia 130, Vitoria 48, Getxo 40, Abanto 31, Ayala 30). metodologia.md se contradice (4 en un sitio, 6 en otro) | anuncios_unificados.csv |
| "ECVI mapeo no visto" | `municipio_area_funcional_ecvi.csv` existe con 252/252, 0 null codigo_ine | verificación directa |
| "C5 certificados 7/10 parcial" | Distribución A-G disponible para 252/252 municipios | cert_energetico_municipal_252.csv |
| "modalidad/equipamiento/poblacion_joven no documentados" | Documentados en trazabilidad_datos.md y preguntas_analisis_profesional.md | lectura directa |
| "13.45% duplicados" | 13.06% (114 filas extra en 93 grupos por fingerprint) | cálculo directo |

## 1. Correcciones de documentación (prioridad 1, esfuerzo bajo)

| # | Acción | Archivo | Detalle |
|---|---|---|---|
| D1 | Corregir count raw 317→319 en README_ARGON y estado_proyecto | `argon/README_ARGON.md`, `argon/estado_proyecto_2026-10-29.md` | 319 archivos totales, 316 manifest-listed |
| D2 | Corregir media 8.6→8.2 en README_ARGON y estado_proyecto | idem | Media real = 8.24 |
| D3 | Reescribir metodologia.md con números canónicos | `docs/metodologia.md` | IDW (no comarcal) para 93, 6 robustos (no 4), salario ajustado 1402€ (no 1381), tensión 73/102/77 (no 76), duplicados 13.06% |
| D4 | Documentar decisión "no ranking municipal fino" | `docs/metodologia.md` | Solo 6 robustos + tipología. Evita ataque en defensa por F5/B6 |
| D5 | Actualizar trazabilidad con modalidad/equipamiento/poblacion_joven | `docs/trazabilidad_datos.md` | Ya documentado parcialmente; completar con equipamiento (134 filas, no 139) |

## 2. Correcciones de calidad (prioridad 2, esfuerzo bajo-medio)

| # | Acción | Archivo | Detalle |
|---|---|---|---|
| Q1 | Sanear codigo_ine vacío en Fotocasa JSONs (2 filas) | `transform/normalizar_json_crudos.py` | Convertir '' a null, no modificar raw |
| Q2 | Añadir BOM a 6 CSVs sin utf-8-sig | `generar_cert_energetico_municipal.py`, `generar_mercado_area_funcional.py`, `calcular_renta_joven.py`, `calcular_tension_social.py`, `limpiar_ecvi.py`, `limpiar_eustat_demografia.py`, `enriquecer_gtfs_conectividad.py` | `encoding="utf-8-sig"` en to_csv |
| Q3 | Determinismo: reemplazar datetime.now()/uuid por valores derivados | `f4_pisos_dirigido.py`, `filtrar_outliers.py` | Usar hash del contenido o seed fijo |
| Q4 | Consumir property_fingerprint en dedup cross-portal | `unificar_anuncios.py` | Agrupar por fingerprint, marcar duplicados. Bajar de 13.06% a <1% |
| Q5 | Documentar EMAL (73/252), SERPAVI (89 nulls), transporte (51 nulls) | `docs/gaps_misconceptions_errores.md` | Estrategia de null-handling para cada fuente |
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
# Verificar metodologia.md con IDW, 6 robustos, salario ajustado, tensión 73/102/77

# 6. Tests completos
pytest tests/ -q
```

## Criterios de éxito

1. Raw: 0 mismatches, .FROZEN presente, guardrails pasan.
2. Silver: 0 CSVs sin BOM, 0 codigo_ine inválidos, duplicados <1%.
3. Documentación: counts consistentes (319 raw, 104 silver), media 8.2, 6 robustos.
4. Metodología: IDW documentado, salario ajustado, tensión 73/102/77, decisión no-ranking congelada.
5. MongoDB: colecciones + aggregation ≥4 etapas + tests.
6. pytest: 66+ (sin regresiones).

## Notas

- Infraestructura (HDFS, Kafka, Mongo) se incluye solo en la fase de implementación MongoDB (A1-A4). HDFS y Kafka quedan fuera del alcance actual (según petición del usuario).
- Todos los cambios son quirúrgicos y no tocan data/raw/.
- El working tree debe limpiarse con commits atómicos antes de la defensa.