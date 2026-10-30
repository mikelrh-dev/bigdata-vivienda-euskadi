# Gaps, misconceptions y errores — bigdata-vivienda-euskadi

**Fecha:** 2026-10-29
**Fuente:** `docs/informe_preguntas_respuesta.md` (42 preguntas, media 8,2/10)

---

## 1. Preguntas NO respondibles (puntuación ≤7)

### C1 — VPO y accesibilidad: 3/10
**Por qué:** 93,6% de VPO es cero en Udalmap. Las adjudicaciones son escasísimas (mediana 0,0 por mil). No hay dataset público de stock VPO municipal.
**Qué falta:** Stock VPO por municipio (no disponible públicamente). Solo hay solicitudes Etxebide (demandantes, no stock).
**Acción:** Documentar como limitación. No intentar arreglar.

### F5 — Compraventa vs alquiler: 6/10
**Por qué:** ECVI solo tiene 29 registros (CAE, 3 TH, 15 áreas funcionales, 7 municipios >40k). No hay mapeo municipio→área funcional completo.
**Qué falta:** Mapeo de cada municipio a su área funcional ECVI (parcialmente resuelto con `municipio_area_funcional_ecvi.csv` pero solo 7 municipios con precio).
**Acción:** Completar mapeo (ya creado `asignar_area_funcional_ecvi.py`). Mejorará a ~7/10.

### O1 — Independizarse con salario: 7/10
**Por qué:** No existe salario joven municipal. Se usa proxy de renta (ratio CAE 18-34 / total = 0,3534). La emancipación solo existe a nivel CAE.
**Qué falta:** Salario neto joven por municipio (no existe en fuentes públicas). OVJ da 1.564 €/mes (18-34) y 1.381 € (16-29) a nivel CAE.
**Acción:** Documentar como limitación. El proxy está justificado en `docs/decision_salario_proxy.md`.

### A4 — Diferencias entre fuentes de alquiler: 7/10
**Por qué:** Anuncios (Fotocasa) son ~56% más caros que el oficial Eustat. La brecha se explica por sesgo de selección (oferta disponible vs toda la vivienda) y temporalidad.
**Qué falta:** Más anuncios en municipios rurales (actualmente 57/252 con Fotocasa).
**Acción:** Documentar como sesgo de selección. No es un error, es una característica del mercado.

### B6 — Tasa desempleo juvenil real: 7/10
**Por qué:** Lanbide da demandantes, no tasa de desempleo. Eustat solo da grupos de edad amplios (0-19, 20-64, ≥65). Falta población activa joven municipal.
**Qué falta:** Población activa joven (16-24) por municipio (no disponible en Eustat municipal).
**Acción:** Documentar como limitación. Usar proxies (ocupación juvenil 16-24, afiliación SS).

### C5 — Certificado energético: 7/10
**Por qué:** Certificado en detalle de anuncios (3 nulos en Fotocasa) y NLP sobre descripciones (RealtyAPI). `cert_energetico_por_mil` (Udalmap) da proxy municipal. No se puede cuantificar impacto en coste total.
**Qué falta:** Certificado energético agregado por municipio (solo 60 municipios con moda).
**Acción:** Ampliar cobertura con más anuncios (actualmente 470 Fotocasa).

### F2 — Oficial vs anuncios: 7/10
**Por qué:** Sesgo de selección (anuncios = vivienda disponible). La diferencia es estructural, no un error.
**Qué falta:** Más datos de anuncios en municipios rurales.
**Acción:** Documentar como limitación metodológica.

---

## 2. Misconceptions (errores de interpretación a evitar)

### M1. "El alquiler oficial (Eustat) es lo que paga un joven"
**Falso.** Eustat mide la renta media de **todos los contratos** (no solo jóvenes). Un joven paga más porque alquila vivienda de menor tamaño en zonas más caras. El proxy de renta joven (ratio 0,3534) intenta corregir esto pero es una estimación con falacia ecológica.

### M2. "Los anuncios son representativos del mercado"
**Falso.** Los anuncios capturan la **oferta disponible** (sesgo de selección). Son ~56% más caros que el oficial porque representan vivienda de mayor calidad/ubicación. No son el mercado entero.

### M3. "El proxy de renta joven es preciso"
**Falso.** La renta municipal (18+) se aplica homogéneamente asumiendo distribución por edad idéntica (ratio CAE). No captura precariedad juvenil ni variación local de salarios. Es un intervalo [40,5%–76,3%], no un punto.

### M4. "La VPO afecta a la accesibilidad"
**No defendible.** Con 93,6% de VPO cero y adjudicaciones escasísimas, no se puede atribuir efecto de VPO a la accesibilidad. Solo hay datos de solicitudes (demanda), no de stock.

### M5. "Se puede calcular desempleo juvenil real"
**Falso.** Lanbide da demandantes registrados, no tasa de desempleo. Eustat no da población activa joven municipal. Solo se usan proxies (ocupación 16-24, afiliación SS).

### M6. "La compraventa es comparable al alquiler"
**Falso a nivel municipal.** ECVI solo tiene datos a nivel territorial/área funcional (29 registros). No hay mapeo completo municipio→área funcional.

### M7. "El esfuerzo joven es un número único"
**Falso.** Es un intervalo [40,5%–76,3%] con dos proxies (fiscal Eustat + salarial OVJ). El punto seco (43,5%) es engañoso.

---

## 3. Errores técnicos sin resolver

| Error | Magnitud | Archivo afectado | Prioridad |
|---|---|---|---|
| `tipo_inmueble` nulos (Pisos.com) | 248/251 | `anuncios_pisos_dirigido.csv` | Alta |
| `nombre_canonico` nulos (Pisos.com) | 218/251 | `anuncios_pisos_dirigido.csv` | Alta |
| Pisos sin geo | 235/235 | `anuncios_pisos_enriquecido.csv` | Media |
| Duplicados anuncios | 114/873 (13,06%) | `anuncios_unificados.csv` | Media |
| GTFS operadores nulos | 51/252 | `transporte_paradas_municipio_enriquecido.csv` | Baja |
| Población joven estimada | Estimación (no fuente) | `poblacion_joven_municipal.csv` | Media |
| Cert. energético cobertura | 60/252 | `cert_energetico_moda_municipio.csv` | Baja |

---

## 3.1 Null-handling por fuente (EMAL / SERPAVI / transporte)

| Fuente | Cobertura / nulos | Estrategia de null-handling |
|---|---|---|
| EMAL (fianzas) | 73 / 252 municipios (179 nulos) | Mantener como cobertura parcial: analizar solo los 73 municipios con dato; documentar sesgo de cobertura; no imputar por comarca/IDW. |
| SERPAVI | 89 nulos (249/252 con dato) | Mantener nulos explícitos; no imputar; usar como indicador de disponibilidad y excluir de rankings finos. |
| Transporte / GTFS (`operadores`) | 51 / 252 nulos | Mantener `paradas_por_1000_hab` y `expediciones_dia` sin nulos; `operadores` nulo documentado como "sin operador identificado"; no bloquea análisis de conectividad. |

---

## 4. Lo que SÍ es sólido (no tocar)

- Udalmap empleo: 252/252, 27 indicadores
- Eustat demografía y renta: 201/252 con renta
- OSRM distancias: 252/252
- GTFS paradas: 252/252 (n_paradas, paradas_por_1000_hab)
- ECVI mapeo a 15 áreas funcionales: 252/252
- Población joven municipal: 252/252 (estimación transparente)
- Robustos: 6 municipios con n≥30 anuncios
- Alquiler temporal vs larga estancia: +21,9% más caro (robusto)
- Distancia a capital vs alquiler: r=-0,603 (robusto)
- Densidad vs alquiler: r=0,456 (robusto)

---

## 5. Acciones para mejorar puntuación (de 8,2 a 9+)

### Alta prioridad (sube +0,5-1,0)
1. Corregir parseo Pisos.com (`tipo_inmueble`, `nombre_canonico`) → +0,3 en C4
2. Deduplicar anuncios (fingerprint ya generado) → +0,2 en A4/F2
3. Completar mapeo municipio→área funcional ECVI → +0,5 en F5

### Media prioridad (sube +0,2-0,5)
4. Resolver GTFS operadores (51 nulos) → +0,1 en D2
5. Buscar fuentes de salario municipal por edad → +0,5 en O1
6. Ampliar cobertura cert. energético (más anuncios) → +0,2 en C5

### Baja prioridad (documentar, no arreglar)
7. VPO: no hay dataset público → documentar como limitación
8. Desempleo juvenil real: falta población activa → documentar como limitación
9. Compraventa municipal: ECVI no tiene granularidad → documentar como limitación

---

*Documento para seguimiento. No bloquea Fase 1-3.*

---

## 6. Excepciones documentadas (reproducibilidad de silver)

### E1. `cert_energetico_moda_municipio.csv` — 60/252 cobertura
- **Generador:** `transform/generar_cert_energetico_moda_municipio.py`
- **Fuente:** `data/procesado/cert_energetico_municipal_252.csv` (252 filas, cert_moda para todos).
- **Diferencia:** el original tenía 60 filas (subconjunto de municipios con certificados de vivienda). El generador produce 252 filas (versión completa). El original es de una versión anterior de los datos; no reproducible bit-identical.
- **Acción:** generador produce versión completa; original preservado en `data/procesado_backup_pre_gen/`.

### E2. `anuncios_vivienda_residencial_filtrado.csv` — reproducible
- **Generador:** `transform/generar_anuncios_residencial_filtrado.py`
- **Fuente:** `data/procesado/anuncios_vivienda_unificados.csv`.
- **Resultado:** bit-identical con el original (570 filas, 16 outliers).

### E3. `fotocasa_dirigido_informe.csv` — counts actualizados
- **Generador:** `transform/generar_fotocasa_dirigido_informe.py`
- **Fuente:** `data/raw/anuncios_fotocasa_dirigido_*.json` + `f4_pisos_objetivo.json` (62 objetivos).
- **Diferencia:** el original tenía counts de una ejecución anterior. El generador produce 62 filas con counts actuales (n=0 para municipios sin raw dirigido).
- **Acción:** generador produce versión actual; original preservado en backup.

### E4. `f4_pisos_objetivo.json` — selección manual
- **Generador:** `transform/generar_f4_pisos_objetivo.py`
- **Comportamiento:** idempotente (valida si existe, no modifica). Si no existe, genera aproximación (62 códigos INE).
- **Criterio original:** municipios con tipología Nivel2/Nivel3 y baja cobertura de anuncios en Fotocasa (selección ad-hoc, no reproducible por criterio simple).
- **Acción:** no regenerar automáticamente; preservar el archivo original.
