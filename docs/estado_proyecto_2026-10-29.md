# Estado del proyecto — bigdata-vivienda-euskadi

**Fecha del informe:** 2026-10-29
**Rama / commit base:** `1a993a9` — *chore: remove argon/ from git tracking (local-only radiography)*
**Fuente de verdad:** `openspec/specs/contrato-reto/spec.md`
**Generado a partir de:** estado real del repositorio (`git status`, `pytest`, inventario de archivos, `scratchpad/evaluacion_preguntas.md`, `scratchpad/calidad_procesado.md`). No se modificó ningún dato.

---

## 1. Resumen ejecutivo

- **Fase de datos (Fase 0 + 1) completada y congelada.** `data/raw/` es inmutable: 313 archivos de datos, marcador `.FROZEN`, manifest SHA-256 de 312 entradas y test de integridad en verde.
- **Silver regenerado y verificado byte-idéntico.** `data/procesado/` contiene 97 archivos de datos (más `.gitkeep`); los comunes con `data/procesado_pre_silver` son byte-idénticos (MD5), sin regresiones de filas/columnas/nulos.
- **Transforms alineados con la regla bronce.** Los 8 transforms del grupo A ahora escriben a `data/procesado/` (y los 8 del grupo B ya lo hacían); ninguno escribe en `data/raw/` en modo silver.
- **Tests en verde.** `pytest` → **59 passed** en 2,84 s (`tests/test_contrato.py`, `tests/test_crudos.py`, `tests/test_raw_inmutable.py`).
- **Cobertura analítica.** 252 municipios de referencia; alquiler completo 252 (159 directo Eustat + 93 por comarca); 871 anuncios unificados en 85 municipios; GTFS paradas_por_1000_hab resuelto (0 nulos); 8,6/10 de grado medio en 42 preguntas objetivo.
- **Pendiente principal.** Infraestructura y análisis (HDFS, MongoDB, Kafka, agregaciones, visualización, informe) — Fases 2 a 9 del plan. `data/resultados/` sigue vacío.

---

## 2. Estado por fases

| Fase | Entrega principal | Estado |
|---:|---|---|
| 0 | Entorno + contrato + tests | ✅ Hecha |
| 1 | Extracción (scripts 01–06 + auxiliares) | ✅ Hecha |
| 1b | Salarios INE EPA (script 07) | ✅ Hecha |
| 1c | Pisos.com (script 08) | ✅ Hecha |
| 1d | Idealista/RealtyAPI (script 09) | ✅ Opcional, 139 anuncios |
| 2 | Descargas directas Open Data Euskadi (EMAL, Etxebide, GTFS) | ✅ Hecha |
| 3 | Transformaciones (entity resolution, dim_municipios, distancias, filtrado, enriquecimiento, geojson, metadata) | ✅ Hecha (parcial) |
| 4 | Docker Compose HDFS + MongoDB | ⬜ Pendiente |
| 5 | Subida HDFS + recuperación | ⬜ Pendiente |
| 6 | Modelado + operaciones PyMongo | ⬜ Pendiente |
| 7 | Aggregation Pipeline | ⬜ Pendiente |
| 8 | Kafka productor/consumidor | ⬜ Pendiente |
| 9 | Gráficos desde PyMongo | ⬜ Pendiente |
| 10 | Informe, arquitectura y demo | ⬜ Pendiente |

---

## 3. Raw inmutable (bronce)

| Elemento | Valor real |
|---|---|
| Archivos de datos en `data/raw/` | **313** (más marcador `.FROZEN` = 314 entradas en el directorio) |
| Marcador de congelación | `data/raw/.FROZEN` — archivo vacío (0 bytes), permisos 644 (no read-only) |
| Manifest SHA-256 | `docs/raw_manifest_sha256.txt` — **312 líneas** (un hash por archivo) |
| Test de integridad | `tests/test_raw_inmutable.py` — `test_raw_congelado_marker` + `test_raw_hashes_manifest` |
| Resultado test | ✅ Incluido en los 59 passed |
| Regeneración | Regenerado desde `data_regen/` (backup base `data/raw_backup_2026-10-29`); Eustat (`01_eustat_api`) falló HTTP 400 y esos archivos provienen del backup |
| `.gitkeep` | **Ausente** en `data/raw/` (eliminado durante la regeneración; no crítico, `.FROZEN` presente) |

**Regla bronce vigente:** no modificar archivos in place; toda normalización va a `data/procesado/`.

---

## 4. Procesado silver (regenerado)

| Elemento | Valor real |
|---|---|
| Archivos en `data/procesado/` | **97** (96 de datos + `.gitkeep`) |
| Archivos en backup `data/procesado_pre_silver/` | 107 (incl. `.gitkeep`) |
| Archivos comunes analizados | 88 |
| Archivos comunes tabulares | 86 |
| Archivos comunes no tabulares omitidos | 2 (`emancipacion_juventud_resumen_normalizado.json`, `municipios_euskadi_252.geojson`) |
| Archivos solo en backup (eliminados del actual) | **18** (15 tabulares + 3 logs/backups) |
| Archivos solo en actual (nuevos) | 0 |
| Regresiones por filas/columnas/nulos | **0** |
| Mejoras por filas/columnas/nulos | 0 |
| Archivos con valores idénticos | **86 / 86** |
| Integridad byte-a-byte | Los 88 comunes son **byte-idénticos (MD5)** |
| Filas totales (tabulares) | 595.636 → 595.636 (delta +0) |
| Nulos totales (tabulares) | 44.514 → 44.514 (delta +0) |

**Conclusión de calidad:** la regeneración de silver preserva íntegramente el contenido de la intersección; la única pérdida es de **disponibilidad** (18 derivados ausentes), no de contenido.

---

## 5. Transforms modificados para escribir a `procesado`

### Grupo A — leían raw y escribían raw (modificados)

| Script | Lee | Escribe ahora (procesado) |
|---|---|---|
| `transform/corregir_empleo.py` | `raw/udalmap_empleo.csv` | `procesado/udalmap_empleo_corregido.csv/.json` |
| `transform/dim_municipios.py` | `raw/*` (Eustat, anuncios, alquiler, EMAL) | `procesado/dim_municipios.csv/.json` |
| `transform/generar_distancias.py` | `raw/dim_municipios.csv`, `distancias_capitales.csv`, geojson | `procesado/distancias_capitales_252.csv`, `distancias_haversine_252.csv`, `municipios_euskadi_252.geojson` |
| `transform/validar_renta.py` | `raw/renta_municipal_completa.csv`, `dim_municipios.csv` | `procesado/renta_municipal_referencia.csv` |
| `transform/parsear_secciones.py` | `raw/alquiler_seccion_*_original.csv` | `procesado/alquiler_seccion.csv` + `alquiler_seccion_resumen.csv` |
| `transform/f4_pisos_dirigido.py` | `raw/anuncios_pisos.json`, `dim_municipios.json` | `procesado/anuncios_pisos_dirigido.csv/.json` + `f4_pisos_informe.csv` |
| `transform/enriquecer_codigo_ine.py` | `raw/*` | `procesado/*_enriquecido` + `informe_entity_resolution.csv` (con `--silver`) |
| `transform/completar_alquiler_comarca.py` | `raw/*` | `procesado/alquiler_municipal_completo.csv` |

### Grupo B — ya escribían a procesado (sin cambio de I/O)

`filtrar_outliers.py`, `limpiar_ecvi.py`, `limpiar_eustat_demografia.py`, `normalizar_json_crudos.py`, `unificar_anuncios.py`, `enriquecer_equipamiento_realtyapi.py`, `enriquecer_gtfs_conectividad.py`, `generar_fingerprint.py`.

### Nuevos transforms recientes (no listados arriba)
`calcular_renta_joven.py`, `generar_cert_energetico_municipal.py`, `generar_dashboard_completo.py`, `generar_dashboard_visual.py`, `auditoria_duckdb.py`, `asignar_area_funcional_ecvi.py`, `generar_analisis_variables_base.py`, `generar_emancipacion_tier3_93.py`, `generar_municipios_faltantes_93.py`, `generar_poblacion_joven_municipal.py`, `completar_alquiler_comarca.py` (IDW), `calcular_tension_social.py`, `generar_mercado_area_funcional.py`.

### Protección de raw

- `enriquecer_codigo_ine.py` añade `_check_frozen()` y argumentos `--force` / `--silver`; sin `--silver` aborta si existe `data/raw/.FROZEN`.
- `RAW_DIR` se usa solo para lectura; las salidas usan `PROC_DIR = RAW_DIR.parent / "procesado"`.

---

## 6. Tests

| Comando | Resultado |
|---|---|
| `pytest -q` | **59 passed** en 2,84 s |
| `tests/test_contrato.py` | Contrato OpenSpec (anuncios, fuentes, formato, metadatos) |
| `tests/test_crudos.py` | Padding 5 dígitos, temporal/larga no mezclados, renta origen transparente |
| `tests/test_raw_inmutable.py` | Marcador `.FROZEN` + hashes del manifest |

**Nota:** `tests/test_crudos.py` sigue leyendo de `data/raw/` (crudos); el contrato y los umbrales (≥400 anuncios, ≥150 municipios, ≥80.000 filas población, ≥90.000 filas renta) se mantienen.

---

## 7. Preguntas respondibles con puntuaciones

**Fuente:** `scratchpad/evaluacion_preguntas.md` (evaluación 2026-10-29 sobre raw 301 + silver 88).
**Preguntas evaluadas:** 42 (4 obligatorias + 38 de bloques A–G).
**Grado medio:** **8,6 / 10**. Preguntas con grado ≥ 9: 30 (71%). Preguntas con mayor limitación (≤ 7): O1 (7), A4 (7), B6 (7), C1 (7), C5 (7), F5 (6).

| ID | Pregunta | Grado |
|---:|---|---:|
| O1 | ¿Puede una persona joven independizarse en Euskadi con su salario? | 7 |
| O2 | ¿Qué municipios ofrecen mejores posibilidades de emancipación y por qué? | 8 |
| O3 | ¿Dónde hay trabajo y vivienda barata a la vez? | 8 |
| O4 | ¿Qué limitaciones tiene el estudio y cómo se documentan? | 9 |
| A1 | ¿Tasa de esfuerzo (alquiler/ingresos) mediana por municipio? | 9 |
| A2 | ¿% municipios que supera el 30% de esfuerzo (inasequible)? | 9 |
| A3 | ¿Cómo cambia el esfuerzo con renta joven estimada vs renta hogar? | 9 |
| A4 | ¿Diferencias de esfuerzo entre Eustat, anuncios y EMAL? | 7 |
| A5 | ¿Municipios con alquiler "sin dato" y tratamiento? | 9 |
| A6 | ¿El alquiler temporal distorsiona la accesibilidad? | 9 |
| B1 | ¿Municipios con mayor paro juvenil (Lanbide)? | 9 |
| B2 | ¿Ocupación juvenil (16–24) se correlaciona con precio alquiler? | 9 |
| B3 | ¿Afiliación SS 16–24 predice mejor el esfuerzo que el paro? | 9 |
| B4 | ¿Municipios con más paro juvenil tienen alquiler más barato (trade-off)? | 9 |
| B5 | ¿Paro de larga duración identifica vulnerabilidad? | 9 |
| B6 | ¿Tasa de desempleo juvenil real (no solo ratio)? | 7 |
| C1 | ¿Mayor proporción de VPO (Etxebide) y efecto en accesibilidad? | 7 |
| C2 | ¿Antigüedad media >50 años se asocia con alquiler barato? | 9 |
| C3 | ¿Índice de confort y edificios sin ascensor marcan peor calidad? | 9 |
| C4 | ¿Superficie media de viviendas en alquiler adecuada para jóvenes? | 8 |
| C5 | ¿Certificado energético (clase) varía por municipio y afecta coste total? | 7 |
| C6 | ¿Licencias de nueva construcción indican dinamismo? | 9 |
| D1 | ¿Distancia a la capital del TH predice precio alquiler? | 9 |
| D2 | ¿Municipios mejor conectados por TP tienen alquiler más caro? | 9 |
| D3 | ¿OSRM vs Haversine cambia el ranking de accesibilidad? | 9 |
| D4 | ¿Municipios rurales (Nivel3) más accesibles pero con menos empleo? | 9 |
| D5 | ¿Densidad de población se asocia con mayor precio alquiler? | 9 |
| E1 | ¿Población extranjera (%) se asocia con demanda y precio alquiler? | 9 |
| E2 | ¿Variación de población (5 años) identifica crecimiento/declive? | 9 |
| E3 | ¿Índice de envejecimiento/dependencia marca menor demanda joven? | 9 |
| E4 | ¿Renta por sexo muestra desigualdad en capacidad de emancipación? | 9 |
| F1 | ¿Temporal vs larga estancia: cuánto influye en el precio (~24% más caro)? | 9 |
| F2 | ¿Alquiler oficial (Eustat) vs anuncios (Fotocasa/Pisos): diferencia y por qué? | 8 |
| F3 | ¿Capitales vs comarca: periféricos más accesibles? | 9 |
| F4 | ¿Álava vs Bizkaia vs Gipuzkoa: qué territorio ofrece mejores posibilidades? | 9 |
| F5 | ¿Compraventa (ECVI) vs alquiler: compra más/menos accesible? | 6 |
| G1 | ¿Municipios "sin dato" de alquiler y cómo se documentan? | 9 |
| G2 | ¿Municipios con n<5 anuncios y por qué no se usan en el ranking? | 9 |
| G3 | ¿El proxy de renta municipal introduce qué sesgos (falacia ecológica)? | 9 |
| G4 | ¿La emancipación juvenil solo existe a nivel territorial (CAE): cómo se comunica? | 9 |
| G5 | ¿La mezcla de años (2026 anuncios, 2024 alquiler/renta) afecta conclusiones? | 9 |
| G6 | ¿Qué fuentes no se pudieron automatizar y por qué (SERPAVI, OSM, Idealista)? | 8 |

### Coberturas clave verificadas (silver)

| Dato | Cobertura |
|---|---:|
| Municipios de referencia | 252 / 252 |
| Alquiler oficial (Eustat 2024) directo | 159 / 252 |
| Alquiler completado por IDW (5 vecinos) | 93 / 252 (metodo_imputacion='IDW_5_vecinos') |
| Anuncios unificados (Fotocasa+Pisos+RealtyAPI) | 871 anuncios, 85 municipios |
| Dimensión enriquecida | 252 × 65 (salario ajustado, tensión social, brecha género, desempleo juvenil, etc.) |
| Municipios con ≥30 anuncios | 7 (6 canónicos: Donostia dividida en 2 variantes) |
| Municipios con 5–29 anuncios | 23 |
| Municipios con <5 anuncios | 55 |
| Tipología de mercado | 6 Nivel1 / 41 Nivel2 / 205 Nivel3 |
| Lanbide paro juvenil | 252 / 252 |
| Udalmap empleo + indicadores | 252 / 252 |
| Transporte público enriquecido (GTFS) | 252 / 252 (expediciones_dia y paradas_por_1000_hab sin nulos; operadores nulo en 51) |
| Distancias OSRM a capitales | 252 / 252 |
| Renta municipal (hogar/atlas) | 252 / 252 |
| Renta joven estimada (16–29) | 252 / 252 (proxy transparente) |
| Demografía/renta por sexo (Udalmap) | 252 / 252 |
| Etxebide solicitudes VPO | 252 / 252 (20 años) |
| EMAL fianzas | 73 municipios |
| ECVI compraventa | 7 municipios + 15 áreas funcionales + 7 territorios |
| Certificado energético (Fotocasa detalle) | 467 / 470 anuncios |
| Certificado energético (Open Data Euskadi) | 252 / 252 municipios (distribución A-G real) |
| Emancipación juvenil (Eustat) | nivel CAE, 2010–2026, 14 indicadores |

---

## 8. Deuda técnica pendiente

### Disponibilidad de derivados (silver)

- **18 derivados presentes solo en `data/procesado_pre_silver`**, no en el silver actual: `analisis_variables_base.csv`, `emancipacion_tier3_93.csv`, `municipios_faltantes_93.csv`, `alquiler_rescatado_seccion.csv`, `f4_pisos_informe.csv`, `informe_calidad_f5.csv`, `pob_rank.csv`, `r1_batch_1..4.json`, `r1_fotocasa_informe.csv`, `r1_municipios_objetivo.json`, `r1_pisos_informe.csv`, `r1_sin_alquiler.json`, `f4_fotocasa.log`, `f4_pisos_objetivo.json.bak_r1`, `v1_detalle.log`. Es regresión de disponibilidad, no de contenido; recuperables desde el backup.

### Datos y metodología

- Renta joven estimada es **proxy transparente** (factor ×0,3534), no salario real municipal; población activa joven municipal nula (`poblacion_joven_15_29` = 252 nulos).
- Anuncios: solo **7 municipios con n≥30**, 55 con n<5; no se defiende ranking municipal fino.
- Outliers de superficie marcados con `es_outlier_superficie` (5 anuncios >500 m²); valor original conservado.
- ECVI: solo 7 municipios + 15 áreas funcionales + 7 territorios; `precio_m2_usada_eur` nulo en 29/29; mapeo municipio→área funcional ya disponible (252/252).
- Certificado energético agregado por municipio (252/252) desde Open Data Euskadi; coste energético real aún pendiente.
- Stock de VPO municipal no disponible; Etxebide mide solicitudes (≠ viviendas disponibles).
- `transporte_paradas_municipio_enriquecido.csv`: `paradas_por_1000_hab` sin nulos (0 nulos tras corrección); `operadores` nulo en 51.
- EMAL solo 73 municipios; SERPAVI 249/252 (89 nulos); Idealista no automatizado.
- GTFS: `enriquecer_gtfs_conectividad.py` lee `data/raw/municipios_euskadi.geojson`, mientras `generar_distancias.py` ahora escribe el geojson filtrado a `data/procesado/municipios_euskadi_252.geojson` (posible inconsistencia de ruta si se reejecuta la cadena).

### Extracción y entity resolution (auditoría framework)

- `extract/05_fotocasa_scraper.py` no persiste HTML crudo → incumple EXTRACCION-01.
- `extract/09_realtyapi.py` tiene literal `PY` suelto (línea 269) → NameError al importar.
- `extract/08_pisos.py` no extrae `superficie_m2` ni `habitaciones` (solo precio/título/subtítulo/enlace/tipo).
- `extract/04_b5m.py` trunca distancias a 5.000 de ~180.000 pares.
- `EQUIVALENCIAS_EXTRA` eliminado (dead code).
- Variantes Fotocasa (Arrankudiaga/Zollo, Arrasate, Donostia, Vitoria) mapeadas a canónico en unificación (Donostia unificada 130 anuncios).
- `distancias_capitales.csv`: 259 filas (252 Euskadi + 5 limítrofes + 2 duplicados por `codigo_ine`); filtrar a dim para análisis.

### Conclusiones recientes (features v2)

- **IDW**: los 93 municipios sin dato directo se imputan por distancia; mantiene gradientes espaciales y evita el “mapa plano” comarcal.
- **Salario ajustado**: mediana 1.402 € (base 1.381 €); el esfuerzo mediano sube 0,7 pp (40,9 → 41,6 %); el ajuste ±15 % solo afecta a colas de paro joven.
- **Tensión social**: 76 municipios en tensión alta (áreas caras + alta demanda Etxebide), 93 media, 83 baja.
- **Compra vs alquiler**: ratio 237–557 meses de alquiler; Urola Kosta y Donostialdea los más desequilibrados; Ríoja Alavesa el más accesible.
- **Limitaciones**: entity resolution (Donostia dividida), superficie en pisos, raw HTML fotocasa; los nuevos features son proxy/estimación, no dato real.

### Infraestructura y análisis (Fases 4–10)

- `storage/` (HDFS, MongoDB, Kafka) vacío; `analysis/`, `visualization/`, `notebooks/`, `data/resultados/` vacíos salvo `.gitkeep`.
- README sigue declarando Docker/HDFS/Mongo/Kafka pendientes; su tabla de estado está desactualizada respecto a la Fase 3 (transformaciones) real.

### Repositorio / gobernanza

- `data/raw/.gitkeep` eliminado; `.gitignore` actualizado para ignorar `data/raw_backup*/`, `data/raw_pre_regen*/`, `data/raw_crudo*/`.
- **Working tree sucio:** 12 archivos modificados (tracked) + 159 sin seguimiento; cambios no commiteados.
- `enriquecer_codigo_ine.py` conserva modo por defecto que puede escribir en raw (`--force`); el modo seguro requiere `--silver`.
- Inventario de datos (`docs/inventario_datos.md`) no refleja los transforms nuevos ni el regenerado raw.

---

## 9. Próximos pasos

### Inmediatos (cierre de datos)

1. Recuperar los 18 derivados desde `data/procesado_pre_silver` a `data/procesado` (o regenerarlos con los transforms) y verificar con un segundo pase de `compare_calidad.py`.
2. Implementar `renta_joven_estimada` en `validar_renta.py` (o nuevo `calcular_renta_joven.py`) usando `eustat_renta_edad` y documentar el factor en `docs/metodologia.md`.
3. Derivar `paradas_por_1000_hab` en `transporte_paradas_municipio_enriquecido.csv` y agregar certificado energético por municipio.
4. Añadir mapeo municipio→área funcional ECVI para comparar compraventa vs alquiler a nivel municipal.
5. Commit de los cambios actuales (transforms + docs + config) una vez verificados los tests.

### Medio plazo (infraestructura)

6. Fase 4: `docker-compose.yml` con HDFS (NameNode+DataNode) y MongoDB; validar en Windows.
7. Fase 5: `storage/hdfs_utils.py` — subida y recuperación byte-idéntica de `raw/` y `procesado/`.
8. Fase 6: modelado PyMongo + CRUD con upsert (diseño pensado para Kafka).
9. Fase 7: limpieza/transformación en Mongo (`transform/limpieza.py`, `transform/enrich.py`).

### Análisis y entrega

10. Fase 8: Aggregation Pipeline (≥4 etapas) + indicadores (alquiler medio, % esfuerzo, ranking de accesibilidad).
11. Fase 9: Kafka en VM (productor/consumidor + flujo a Mongo) — validar primero en Kafka local.
12. Fase 10: visualización (≥3 tipos desde PyMongo) + informe final (`notebooks/informe.ipynb`, `docs/informe_resultados.md`) + demo end-to-end.

---

## 10. Referencias

- `scratchpad/evaluacion_preguntas.md` — puntuaciones y coberturas.
- `scratchpad/calidad_procesado.md` — comparación silver vs pre-silver.
- `docs/plan_silver_sin_tocar_raw.md` — plan de transforms a procesado.
- `docs/plan_regeneracion_raw.md` / `docs/plan_regeneracion_completa.md` — regeneración raw.
- `docs/trazabilidad_datos.md`, `docs/metodologia.md`, `docs/decision_salario_proxy.md`.
- `openspec/plan/fases.md`, `openspec/specs/contrato-reto/spec.md`.
- `tests/` — `test_contrato.py`, `test_crudos.py`, `test_raw_inmutable.py`.