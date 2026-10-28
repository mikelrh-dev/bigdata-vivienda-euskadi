# Reauditoría — framework_auditoria_completo2 (parámetros de tensión)

**Fecha:** 2026-10-28  
**Fuente:** framework_auditoria_completo2 (plantilla maestra, módulos A-D, auditoría dato puro, entity_audit, stats_audit).  
**Datos:** 203 archivos raw, 22 procesado, 101 HTML crudos, 54 tests passed.

---

## Puntuación por parámetro de tensión (0-10)

| Parámetro | Puntuación | Justificación |
|---|---:|---|
| Cobertura municipal anuncios | 3/10 | Solo 3 mun con n≥30; 12 con ≥5; 46 con ≤3. |
| Alquiler oficial | 6/10 | 159/252 (63%); 93 sin dato. |
| Renta municipal | 10/10 | 252/252 (Eustat 201 + INE Atlas 51). |
| Paro municipal | 7/10 | Lanbide válido 252/252; aprox NaN (fórmula mal derivada). |
| Distancias | 9/10 | Haversine 100% (63.504 pares); capitales 252; Araba 4-dígitos (54) rompe joins. |
| Entity resolution | 8/10 | codigo_ine 100%; Fotocasa 56/61 match (5 sin match). |
| Calidad estadística | 8/10 | Superficie 97.9%/97.2%; outliers marcados (8); temporal separado; outliers restantes. |
| Tests | 10/10 | 54/54 passed; 0 xfail; 0 skip. |
| Trazabilidad | 7/10 | 101 HTML crudos; _meta con linaje; manifiesto no existe. |
| Automatización | 9/10 | 24 fuentes automatizadas; orquestador con --mode live/replay-raw. |
| Documentación | 9/10 | openspec completo; planes/auditorías; inventario actualizado. |
| **Total (media)** | **8.1/10** | **8/10** |

---

## Veredicto de suficiencia (3 preguntas)

1. **Ranking de 252 por coste de acceso con error<20%:** NO (solo 5 mun con n≥30; 93 sin alquiler oficial).
2. **Tasa de esfuerzo alquiler/renta para 252:** PARCIAL (159 oficial + 93 proxy comarcal).
3. **"Dónde hay trabajo y vivienda barata":** PARCIAL (paro Lanbide válido, distancias completas, pero cobertura anuncios baja).

---

## Gaps detectados

- **Cobertura anuncios baja:** 75/252 mun con anuncios; solo 5 con n≥30.
- **Alquiler oficial:** 159/252 (63%); 93 sin dato.
- **Salario solo nacional:** no se puede calcular esfuerzo municipal real.
- **Paro aprox NaN:** solo Lanbide válido.
- **Temporal vs larga ~21%:** no mezclar.
- **Renta vs alquiler r≈0.27:** documentado.
- **169 mun sin anuncios.**
- **EPSG sin prueba explícita.**
- **Eustat 24 agregados sin filtrar.**
- **Araba 4-dígitos (54):** rompe joins.
- **diagnostico.py:** FileNotFoundError (`municipios_gipuzkoa.geojson` no existe; hay `municipios_euskadi.geojson`).

---

## Conclusión

Proyecto en **8/10** bajo parámetros de tensión. Fuerte en calidad, tests, automatización y documentación; débil en cobertura municipal de anuncios y alquiler oficial. No es un 10 hasta cerrar gaps de cobertura y paro.