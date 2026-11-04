# Puntos flacos del dataset — bigdata-vivienda-euskadi

**Fecha:** 2026-10-29
**Fuente:** auditoría DuckDB (`scratchpad/auditoria_duckdb.md`) + docs/metodologia.md + docs/trazabilidad_datos.md

---

## 1. Cobertura municipal (gaps estructurales)

| Variable | Cubre | Falta | Impacto |
|---|---|---|---|
| Alquiler Eustat | 159/252 | 93 municipios (imputados por comarca) | Ranking municipal fino no defendible |
| Anuncios Fotocasa | 57/252 | 195 municipios | Solo capitales y áreas urbanas |
| Anuncios Pisos.com | 30/252 | 222 municipios | Cobertura muy limitada |
| Anuncios RealtyAPI | 3/252 | 249 municipios | Solo capitales |
| Renta personal Eustat | 201/252 | 51 municipios (INE Atlas) | Proxy fiscal incompleto |
| ECVI precio | 7/252 | 245 municipios | Solo grandes ciudades |
| Cert. energético | 252/252 | 0 municipios | RESUELTO: Open Data Euskadi (registro oficial) |
| VPO terminadas | ~16/252 | 83.73% ceros | No hay stock VPO municipal público |

## 2. Calidad de datos (bugs y problemas)

| Problema | Magnitud | Estado | Prioridad |
|---|---|---|---|
| `tipo_inmueble` (Pisos.com) | 248/251 nulos | Bug de parseo sin resolver | Alta |
| `nombre_canonico` (Pisos.com) | 218/251 nulos | Bug de parseo sin resolver | Alta |
| Pisos sin geo | 235/235 | geo_invalida documentada (G6) | Media |
| Duplicados anuncios | 113/840 (13,45%) | Identificados, sin deduplicar | Media |
| GTFS operadores | 51/252 nulos | Sin resolver | Baja |
| Población joven 15-29 | Estimación (no fuente real) | Eustat solo da 0-19/20-64/≥65 | Media |
| Salario joven | Proxy (OVJ 1564€/1381€) | No hay salario municipal por edad | Media |
| Robustos (n≥30 anuncios) | Solo 6 municipios | Ranking municipal fino no defendible | Alta |
| Compraventa vs alquiler | Sin mapeo municipio→Área Funcional | Limitación estructural (F5) | Baja |

## 3. Lo que SÍ está completo (252/252)

- Udalmap empleo (27 indicadores)
- Eustat demografía y renta (201/252 con renta)
- OSRM distancias a capitales
- GTFS paradas (n_paradas, derivado paradas_por_1000_hab)
- ECVI mapeo a 15 áreas funcionales
- Población joven municipal (estimación transparente)

## 4. Veredicto

El dataset es **sólido para análisis a nivel de tipología, comarca y capitales** (6 municipios robustos, 159 con dato directo). **No es defendible para ranking municipal fino** ni para atribución de emancipación a un municipio concreto con la muestra actual.

Las limitaciones están documentadas en:
- `docs/metodologia.md`
- `docs/trazabilidad_datos.md`
- `argon/conclusiones_finales.md`
- `docs/informe_preguntas_respuesta.md` (puntuación 8,2/10)

## 5. Acciones futuras (prioridad)

1. **Alta:** Corregir parseo Pisos.com (`tipo_inmueble`, `nombre_canonico`).
2. **Alta:** Deduplicar anuncios (fingerprint ya generado, 113 duplicados).
3. **Media:** Resolver GTFS operadores (51 nulos).
4. **Media:** Buscar fuentes de salario municipal por edad (actualmente solo proxy OVJ).
5. **Baja:** Mapeo municipio→Área Funcional para compraventa (F5).
6. **Baja:** Cobertura ECVI (actualmente solo 7 municipios con precio).

---

*Documento generado para seguimiento. No bloquea Fase 1-3 (obtención y procesado).*
