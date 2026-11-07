# Tasks: 2026-11-07-pisos-re-resolver-ubicacion

## Review Workload Forecast

| Task | Estimated effort | Risk | Notes |
|------|------------------|------|-------|
| 1. Prototipo parser subtítulo → variantes + gazetteer (solo lectura) | 4 h | Med | Gazetteer barrio→municipio incompleto; mitigación: cuarentena motivada, sin adivinar |
| 2. Parche `transform_pisos` + `resolver_codigo` | 2 h | High | Quita `municipio_busqueda` como ubicación; riesgo de regresión en otros portales |
| 3. Re-ejecución orden base → enricher + recount L1/L2/L3 y precio/superficie | 2 h | High | Reescribe `data/procesado/dim_municipios.csv` y `anuncios_unificados.csv`; sin Docker |
| 4. Recarga Mongo (staging + backup + rename) + regenerar 13 PNG + 6 CSV con doble SHA | 3 h | High | Requiere MongoDB local; Kafka → HDFS exclusivamente, nunca Kafka → Mongo |
| 5. Tests nuevos `test_pisos_ubicacion_real.py` + suite completa | 3 h | Med | 151 tests base + nuevos; sin imputación comarcal/IDW verificable |
| 6. Sync docs (README, tipología, guion, precio 80/252, manifest 185 vs 188) | 3 h | Low | Todo valor de Mongo, nunca tecleado; defensa honesta L1/L2/L3 |

**Approximate total:** ~17 h. **Decision needed before apply:** No — specs aprobados; pendiente solo conteo real de T1 (resueltos vs cuarentenados sobre 230) antes de fijar T2.

---

## 1. Prototipo read-only: parser subtítulo → `dim_municipios` variantes + gazetteer barrio→municipio

**Description:** Prototipo de solo lectura que re-resuelve la ubicación real de los pisos.com (230 anuncios dirigido+enriquecido, universo total 245) usando exclusivamente subtítulo/título: coincidencia textual contra `variantes`/`nombre_canonico` de `data/procesado/dim_municipios.csv` (252 filas) y gazetteer barrio→municipio (Santutxu→Bilbao, etc.). Cuenta resueltos con `origen_resolucion` y cuarentenados motivados. No escribe CSV/JSON/Mongo ni modifica ningún módulo del repo; vive como script scratch o salida a stdout. Detecta barrio ambiguo y fuera-de-Euskadi (Madrid et al.) sin clasificarlos por búsqueda. Reporta suma resueltos + cuarentena = total, y usos de `municipio_busqueda` como ubicación = 0.

**Acceptance:**
- [x] Corre solo-lectura sobre `anuncios_pisos_dirigido.csv` + `anuncios_pisos_enriquecido.csv` (columna `subtitulo`/`titulo` ya presentes, confirmado en cabecera) sin mutar `data/procesado/` ni Mongo.
- [x] Orden de resolución verificable por anuncio: (1) subtítulo, (2) título, (3) gazetteer, (4) fallback detalle, (5) cuarentena — nunca `municipio_busqueda` (PISOS-01/EXTRACCION-01).
- [x] Reporta `resueltos` (con `origen_resolucion ∈ {subtitulo, titulo, gazetteer, fallback}`) y `cuarentenados` (motivo: fuera_de_euskadi | ambiguo | sin_subtitulo); `resueltos + cuarentena = total`; reconcilia 230 del prototipo contra 245 del universo pitch en el informe.
- [x] Lista explícita de barrios ambiguos no resueltos → cuarentena, sin adivinar ni caer a búsqueda.
- [x] Baseline de comparación: 187/245 (76%) en L2 por `municipio_busqueda` documentado como punto de partida, 0 tras el prototipo.

**Verification:**
- Comando: `python -m scratchpad.prototipo_pisos_ubicacion --read-only --input-dir data/procesado --dim data/procesado/dim_municipios.csv` *(nombre del scratch asumido; el agente lo fijará en apply y lo anotará en el informe)*
- Salida esperada (ejemplo de formato): `TOTAL=230 RESUELTOS=<N1> CUARENTENA=<N2> SUMA_OK=True MUNICIPIO_BUSQUEDA_USOS=0 AMBIGUOS=<K>` con `N1 + N2 == 230` y `MUNICIPIO_BUSQUEDA_USOS=0`; además `git status --porcelain data/procesado` vacío (nada escrito).

**Dependencies:** Ninguna. Es la primera puerta: fija el conteo real que T2 implementa y T3 consume.

**Files:** `data/procesado/anuncios_pisos_dirigido.csv`, `data/procesado/anuncios_pisos_enriquecido.csv`, `data/procesado/dim_municipios.csv` (solo lectura), `scratchpad/prototipo_pisos_ubicacion.py` (o equivalente, solo lectura), informe de cuarentena en stdout/`scratchpad/`.

**Estimacion:** 4 h (M). Mayor esfuerzo en construir el gazetteer mínimo barrio→municipio y en clasificar ambiguos; poner umbral stop si <80% resuelve: entonces T2 debe reforzar fallback antes de parchear.

---

## 2. Parche `transform_pisos` + `resolver_codigo`: subtítulo manda, `municipio_busqueda` prohibida, cuarentena reversible

**Description:** Parchea el pipeline para que la ubicación real provenga de subtítulo/título + gazetteer, nunca de `municipio_busqueda` ni de `codigo_ine` huérfano. Cambios: `extract/08_pisos_scraper.py:163-169` conserva `subtitulo`/`titulo` y `es_busqueda_no_ubicacion=True`; `transform/unificar_anuncios.py:130` deja de leer `municipio_busqueda`/`nombre_canonico_resuelto` como ubicación en `transform_pisos` y pasa a leer subtítulo→título→gazetteer→fallback; `transform/muni_resolve.py:37-43` no propaga `codigo_ine` (p. ej. `VALID_CODES`) sin coincidencia textual y añade el pase gazetteer; lo no resuelto o fuera de `dim_municipios` se marca `geo_invalida=True` y queda en cuarentena reversible (excluido de `dim_municipios` y conteos L1/L2), sin tocar Eustat/Lanbide. Sin Docker; HDFS raw intocable; Kafka→HDFS exclusivamente, nunca Kafka→Mongo.

**Acceptance:**
- [x] `transform_pisos` (`transform/unificar_anuncios.py:130`) resuelve solo por subtítulo/título/gazetteer/fallback; cero lecturas de `municipio_busqueda` como ubicación (sigue existiendo como metadato de búsqueda, con `es_busqueda_no_ubicacion=True`).
- [x] `resolver_codigo` (`transform/muni_resolve.py:37-43`): `codigo_ine` sin coincidencia textual en subtítulo/título → sin asignar, a cuarentena motivada (SCENARIO código sin texto no vale).
- [x] Todo piso fuera de Euskadi / sin subtítulo / ambiguo → `geo_invalida=True` + cuarentena reversible (se puede reabrir si aparece evidencia; nunca se borra el anuncio).
- [x] `extract/08_pisos_scraper.py:163-169` conserva `subtitulo`/`titulo` del raw y mantiene `es_busqueda_no_ubicacion=True` para que T3 y futuramente otros scrapes no pierdan la evidencia.
- [x] Eustat (252/252) y Lanbide (249/252) intactos: el parche solo afecta a `portal=="pisos"`; prueba de no-regresión en T5.

**Verification:**
- Comando: `grep -n "municipio_busqueda" transform/unificar_anuncios.py` → salida esperada: solo la línea 64 (filtro de validez) y **cero** ocurrencias dentro de `transform_pisos` (líneas 127+).
- Comando: `python -c "from transform.muni_resolve import resolver_codigo; print(resolver_codigo(None, '48020'))"` → salida esperada: `(None, None)` (código sin texto no se propaga).
- Comando: `grep -n "subtitulo\|titulo" transform/unificar_anuncios.py | head` → muestra lectura de `subtitulo`/`titulo` en `transform_pisos` y `grep -n "geo_invalida" transform/unificar_anuncios.py` → `geo_invalida=True` en el camino de cuarentena.

**Dependencies:** Tarea 1 (conteo resueltos/cuarentenados + gazetteer mínimo). No se escribe código de T2 hasta tener el informe de T1; si T1 deja >20% en cuarentena, ampliar gazetteer antes.

**Files:** `extract/08_pisos_scraper.py` (163-169), `transform/unificar_anuncios.py` (`transform_pisos`, línea 130), `transform/muni_resolve.py` (`resolver_codigo`, 37-43; gazetteer barrio→municipio nuevo o extendido), `transform/aplicar_cobertura_mercado.py` (delegado a T3 para la cuarentena en conteo).

**Estimacion:** 2 h (S, alto riesgo). Pocas líneas pero gran blast radius: `resolver_codigo` es compartido con otros portales; el parche debe acotar el nuevo orden a pisos.

---

## 3. Re-ejecución `unificar_anuncios` → `aplicar_cobertura_mercado` (base → enricher) + recount L1/L2/L3 y precio/superficie

**Description:** Con el parche de T2 integrado, re-ejecuta en orden estricto el writers de `data/procesado/dim_municipios.csv`: primero `transform/unificar_anuncios.py` (reconstruye `anuncios_unificados.csv` con pisos re-resueltos y cuarentena), después `transform/aplicar_cobertura_mercado.py` (base `dim_municipios` primero; recalcula `n_anuncios`/`n_anuncios_raw` y `tipologia_mercado` con regla `n≥30 → Nivel1`, `n≥1 + mercado oficial → Nivel2`, resto `Nivel3`). Recount honesto post re-resolución: L1 = 4 municipios fuertes (Bilbao 173, Donostia 113, Getxo 40, Vitoria-Gasteiz 39, n≥30), L2 = 16 (10–29, solo indicativo con min-max + mediana + `n_precio`, temporal y larga separados), L3 = 1–9 / 0 (sin dato). Precio/superficie solo donde hay anuncio real: `None` + `metodo_imputacion=ninguno` en municipios con `n_anuncios=0`, **sin imputación IDW ni comarcal** (PISOS-03). `n_anuncios` cuenta solo no-cuarentena; `n_anuncios_raw` conserva conteo pre-limpieza. Presupuesto: Eustat 252/252 y Lanbide 249/252 sin regresión; espera que los conteos L1/L2/L3 difieran del baseline (pisos ya no inflan por búsqueda).

**Acceptance:**
- [x] Orden base → enricher respetado y reproducible en una sola línea de comando; cuarentena excluida de `n_anuncios` pero visible en `n_anuncios_raw` y en informe de cuarentena.
- [x] Recount L1/L2/L3 derivado de `dim_municipios.csv` post re-resolución; Getxo 40 vs Vitoria 39 advertido (diferencia de 1 anuncio); L2 con min-max + mediana + `n_precio`, temporal vs larga separados.
- [x] Precio/superficie = `None` (sin IDW/comarcal) donde `n_anuncios=0`; verificado por agregación sobre `anuncios_unificados.csv`/`dim_municipios.csv`.
- [x] 0 pisos por `municipio_busqueda`; 245 re-resueltos o en cuarentena motivada (245 = 230 dirigido+enriquecido del prototipo + resto reconcileado en informe).
- [x] Sin regresión 252/252 (Eustat) ni 249/252 (Lanbide); rollback posible vía `git checkout -- data/procesado/dim_municipios.csv data/procesado/anuncios_unificados.csv` + cuarentena reversible.

**Verification:**
- Comando: `python transform/unificar_anuncios.py && python transform/aplicar_cobertura_mercado.py` → salida esperada: ambas completan sin excepciones y regeneran `data/procesado/anuncios_unificados.csv` + `data/procesado/dim_municipios.csv` (+ `cobertura_anuncios.csv`, 252 filas).
- Comando: `python -c "import pandas as pd; d=pd.read_csv('data/procesado/dim_municipios.csv',dtype=str); print('L1', (d['n_anuncios'].astype(int)>=30).sum(), 'L2', ((d['n_anuncios'].astype(int)>=10)&(d['n_anuncios'].astype(int)<=29)).sum())"` → salida esperada: `L1 4 L2 16` (valores exactos pendientes del conteo real T1/T3: si difieren, anotar los reales con motivo en el informe y no forzar 4/16 a mano).
- Comando: `grep -c "geo_invalida" <informe_cuarentena>` → salida esperada: igual al número de pisos fuera de Euskadi contados.
- Comando: `python -c "import pandas as pd; d=pd.read_csv('data/procesado/dim_municipios.csv'); print('precio_nulos_sin_anuncio', ((d['n_anuncios']==0)).sum())"` → salida esperada: conteo de municipios con `n_anuncios=0` y precio/superficie `None`, cero imputaciones comarcales/IDW.

**Dependencies:** Tarea 2 (parche integrado y verificado). Pre-requisito de T4 (sin CSV re-ejecutados no hay recarga).

**Files:** `transform/unificar_anuncios.py` (ejecutado), `transform/aplicar_cobertura_mercado.py` (ejecutado; si falta cuarentena explícita, parche mínimo aquí), `data/procesado/anuncios_unificados.csv`, `data/procesado/dim_municipios.csv`, `data/procesado/cobertura_anuncios.csv`.

**Estimacion:** 2 h (S, alto impacto). El riesgo no es el tiempo sino la tentación de redondear el recount a 4/16: el apply debe publicar los números reales y explicar cualquier deriva respecto al baseline.

---

## 4. Recarga Mongo staging + backup + rename + regenerar 13 PNG + 6 CSV con doble SHA

**Description:** Recarga Mongo con el silver re-resuelto vía `storage/load_mongo.py` (staging + `<name>__backup` + rename atómico, recreando índices con `ensure_indexes`; nunca `drop()` directo; si staging vacío, aborta sin tocar la colección original con 759 documentos). Después regenera `data/resultados/` con `analysis/run_analisis_mongo.py`: 13 PNG + 6 `mongo_*.csv` (`mongo_alquiler_por_municipio.csv`, `mongo_esfuerzo_por_municipio.csv`, `mongo_modalidades.csv`, `mongo_vpo_por_municipio.csv`, `mongo_vpo_terminadas_por_municipio.csv`, `mongo_accesibilidad_extendida.csv`). Regla de estabilidad: doble ejecución da SHA256 idéntico en los 6 CSV (PISOS-04), sin regresión 252/252 ni 249/252. Sin Docker; MongoDB local; HDFS solo raw; Kafka→HDFS, nunca Kafka→Mongo (sin cambios de topología en esta tarea).

**Acceptance:**
- [x] Colección original preservada: existe `anuncios__backup` con los 759 documentos previos; rename atómico verificado; si staging está vacío, la carga aborta y Mongo no pierde datos.
- [x] Post-recarga: Eustat 252/252 y Lanbide 249/252; `n_anuncios` por municipio coincide con T3; cuarentena fuera de conteos.
- [x] `data/resultados/`: 13 PNG + 6 `mongo_*.csv` regenerados desde Mongo (sin valores tecleados); doble ejecución → SHA256 idéntico en los 6 CSV.
- [x] Índices recreados (`ensure_indexes`) tras el rename; sin `drop()` directo en el código de carga.

**Verification:**
- Comando: `python storage/load_mongo.py` → salida esperada: `loaded anuncios: <N> localidades...` (o conteos por colección) y generación de `anuncios__backup` con 759 docs; `mongosh --eval "db.anuncios.countDocuments()"` devuelve el total post-recarga y `db.getCollectionNames()` incluye `anuncios__backup`.
- Comando: `python analysis/run_analisis_mongo.py && python analysis/run_analisis_mongo.py && sha256sum data/resultados/mongo_*.csv` → salida esperada: 6 líneas SHA256, **idénticas entre ambas ejecuciones** (comparar con `sha256sum` de la primera corrida; cualquier diferencia = bloqueo).
- Comando: `ls data/resultados/*.png | wc -l && ls data/resultados/mongo_*.csv | wc -l` → salida esperada: `13` PNG y `6` CSV.

**Dependencies:** Tarea 3 (CSV re-ejecutados en orden base→enricher). Sin T3, no hay silver que recargar.

**Files:** `storage/load_mongo.py` (carga staging+backup+rename), `analysis/run_analisis_mongo.py` (generador), `data/resultados/` (13 PNG + 6 `mongo_*.csv`), colección MongoDB local `anuncios` + `anuncios__backup`.

**Estimacion:** 3 h (M). Incluye ventana de verificación manual de backup y de los dos SHA; si Mongo local no responde, parar y reportar — no inventar conteos.

---

## 5. Tests nuevos `tests/test_pisos_ubicacion_real.py` + suite completa (151+)

**Description:** Suite de regresión de la re-resolución: nuevo fichero `tests/test_pisos_ubicacion_real.py` que verifica (a) los 245 pisos re-resueltos por subtítulo/título/gazetteer con `origen_resolucion` trazable o en cuarentena motivada, (b) 0 pisos por `municipio_busqueda` (`grep` funcional/tipo test: ninguna ubicación igual a `municipio_busqueda`), (c) fuera-de-Euskadi con `geo_invalida=True` y cuarentena reversible (excluido de `dim_municipios` y L1/L2), (d) `codigo_ine` sin texto no se propaga, (e) backup presente post-recarga con 0 documentos perdidos, (f) doble ejecución SHA idéntico de los 6 CSV, (g) `n_anuncios`/precio sin imputación comarcal/IDW. Suite completa: 151 tests base + nuevos todos en verde. Sin Docker; HDFS solo raw; Kafka→HDFS (tests de pipeline existentes deben seguir verdes sin re-enrutar nada a Mongo).

**Acceptance:**
- [x] `tests/test_pisos_ubicacion_real.py` cubre: re-resolución textual (subtítulo tipo «Piso en Santutxu, Bilbao» → Bilbao vía gazetteer), orden PISOS-01, código sin texto → cuarentena, fuera-de-Euskadi → `geo_invalida=True`, nunca `municipio_busqueda`, backup sin pérdida, SHA doble idéntico, y precio/superficie `None` sin imputación.
- [x] Casos borde explícitos: subtítulo ambiguo («Santutxu» sin municipio → gazetteer o cuarentena), sin subtítulo (fallback detalle o cuarentena), municipio con `n_anuncios=0` (precio `None`, `metodo_imputacion=ninguno`).
- [x] Suite completa sin regresión: 151 tests base + nuevos en verde; tests de HDFS/Kafka intactos (sin Docker, sin Kafka→Mongo).

**Verification:**
- Comando: `python -m pytest tests/test_pisos_ubicacion_real.py -q` → salida esperada: `N passed` donde N = nº de casos nuevos (245 escenarios de re-resolución + cuarentena + invariantes; parametrización por anuncio 245 cubre el universo — el número exacto lo fija el apply).
- Comando: `python -m pytest tests -q` → salida esperada: `151+<N> passed` (o `0 failed`), con la línea final tipo `====== 1xx passed in Xs ======`; cualquier fallo en tests de HDFS/Kafka = bloqueo, no ignorar.

**Dependencies:** Tarea 1 (conteo/convenio de cuarentena), Tarea 2 (parche, para asertos de unidad) y Tarea 3/4 (artefactos Silver/Mongo para asertos de integración). No es la última: T6 consume sus conteos para sincronizar docs, y T6 cierra el change.

**Files:** `tests/test_pisos_ubicacion_real.py` (nuevo), suite existente `tests/test_*.py` (solo lectura/verificación; no modificar salvo asertos de regresión directamente rotos por el nuevo orden, justificados en el informe).

**Estimacion:** 3 h (M). Incluye parametrizar los 245 escenarios y montar la comparación SHA doble sin depender de Mongo vivo en CI (usar CSVs generados en T4).

---

## 6. Sync docs: README Nivel2/3 66/182, tipología, guion con falsación exterior/no-ascensor, precio solo 80/252, manifest 185 vs 188

**Description:** Sincroniza la documentación pública con los conteos reales post re-resolución (valores de T3/T4/T5, derivados de Mongo y `data/procesado/`, nunca tecleados a mano desde el informe pitch): README con Nivel2/3 = **66/182** y los 4 municipios L1 (Bilbao 173, Donostia 113, Getxo 40, Vitoria-Gasteiz 39) — o los reales si T3 diverge, con explicación; tipología de mercado consistente con la regla n≥30 en las tres tablas que la citan; guion de defensa (`docs/guion_defensa.md` + 12 min) con sección de falsación exterior explícita (qué evidencia externa tumbaría la conclusión: rebote de pisos.com fuera de búsqueda, falsación por no-ascensor — grupo con ascensor vs sin ascensor no comparable — y precio solo en 80/252 donde hay anuncio real); `docs/conclusiones_municipios.md` con L1 firme, L2 indicativo (min-max + mediana + `n_precio`, temporal ≠ larga) y L3 «sin dato», más coletilla «252 contextual sobre 159 oficiales»; aclaración manifest: **185** entradas en manifest vs **188** archivos silver en disco (3 no rastreados — justificar su exclusión o regenerar manifest; no ocultar la diferencia).

**Acceptance:**
- [x] README: Nivel2/3 como **66/182** (o reales de T3 con justificación si difieren), 4 L1 n≥30 con n y código INE; sin ranking 1-16 ni lectura de `municipio_busqueda`.
- [x] Tipología sincronizada en README + `docs/conclusiones_municipios.md` + `docs/metodologia.md`/`docs/diccionario_columnas.md` (misma regla n≥30, mismos conteos).
- [x] Guion defensa: falsación exterior y no-ascensor escritos explícitamente; precio calificado como observable solo en **80/252** municipios con anuncio (resto `None`, sin imputación); esfuerzo «252 contextual sobre 159 oficiales» presente (verificado con grep).
- [x] Manifest: nota 185 vs 188 cerrada (archivos extra identificados en §Sync) en README o `docs/raw_manifest_sha256.txt` según evidencia de apply.
- [x] Ningún número de docs tecleado a mano: cada cifra enlaza a `dim_municipios.csv` post T3 o a `mongo_*.csv` post T4.

**Verification:**
- Comando: `grep -n "66\|182\|Nivel2\|Nivel3\|173\|113\|40\|39" README.md` → salida esperada: línea de O2 con los 4 L1 n≥30 y Nivel2 (66) / Nivel3 (182) coherentes con T3; `grep -v "125\|41\|205"` no muestra conteos del baseline como si fueran actuales.
- Comando: `grep -n "80/252\|contextual\|159\|falsación\|ascensor\|exterior" docs/guion_defensa.md docs/conclusiones_municipios.md` → salida esperada: ≥1 ocurrencia de `contextual`, mención de `80/252`, y bloque falsación (exterior + no-ascensor) presente; `grep -c "contextual" docs/conclusiones_municipios.md` ≥ 1.
- Comando: `python -c "import pandas as pd; d=pd.read_csv('data/procesado/dim_municipios.csv'); print(len(d), (d['tipologia_mercado']=='Nivel2_Mercado_Regulado').sum(), (d['tipologia_mercado']=='Nivel3_Mercado_Rural_Cerrado').sum())"` → salida esperada: `252 66 182` (o reales con justificación documentada si T3 difiere; en ese caso README debe coincidir con esta salida, no con 66/182 de memoria).

**Dependencies:** Tarea 5 (conteos verificados por tests) y, transitivamente, Tareas 1–4. Cierra el change: sin T6 cerrado no se declara éxito.

**Files:** `README.md`, `docs/conclusiones_municipios.md`, `docs/guion_defensa.md`, `docs/guion_defensa_12min.md`, `docs/metodologia.md` / `docs/diccionario_columnas.md` (solo si citan tipología), `docs/raw_manifest_sha256.txt` (aclaración 185 vs 188), evidencia en `data/procesado/dim_municipios.csv` + `data/resultados/mongo_*.csv` (solo lectura).

**Estimacion:** 3 h (M, bajo riesgo técnico). El riesgo es textual: contradecir T3 con números de memoria. Frenar si T3 no dejó números cerrados o si manifest 185 vs 188 no se distingue en apply.

