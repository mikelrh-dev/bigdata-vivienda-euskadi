# Plan de reauditoría v8 — 2026-11-09

## 0. Estado de partida

- Cambio auditado: eliminación de `data/staging/` del flujo VPO.
- Diff tracked: 6 ficheros (`extract/26_vpo_terminadas.py`, `.gitignore` y 4 docs del cambio 2026-11-05) + 1 carpeta nueva `openspec/changes/2026-11-09-vpo-sin-staging/`.
- Raw local: `data/raw/udalmap_vpo_terminadas.csv`, 35.427 B, SHA `70a2937a3026b01c5e73ff641241c2fad0a77c3b995d2863034fba2da1294706`, mtime `1793914427`.
- HDFS raw: `GETFILESTATUS` 200, `length=35427`, `OPEN` con el mismo SHA; 201 entradas top-level en `data/raw`; `data/procesado` 404.
- `data/staging/` ausente; `.gitignore` sin la entrada.
- Suite: 238 tests colectados (236 passed, 2 skipped); gobernanza TODO OK; `run_all --check` exit 0.
- v7: 187/190; C2 HDFS = 7 por `procesado` 404; hallazgos H-01…H-07.
- Universo actual: 874 ficheros no-data + 605 de datos = 1.479; 625 tracked; 193 `.py`, 431 `.md`, 317 `.json`, 115 `.html`, 205 `.csv`.

## 1. Objetivo

Reauditar el proyecto completo con evidencia nueva, no heredada, y determinar:

1. Si el cambio VPO sin staging es correcto, seguro y coherente con el contrato.
2. Si el cambio ha introducido regresiones en raw, HDFS, silver, Mongo, análisis, tests, CI o documentación.
3. Si el estado global sigue siendo defendible contra los 19 criterios / 190 puntos de la rúbrica.
4. Qué hallazgos quedan, con severidad, evidencia y acción propuesta.

No se corregirá nada durante la auditoría. Cualquier fix se propondrá como cambio separado y requerirá autorización.

## 2. Universo y cobertura

Todo fichero se inventaría y recibe un nivel de control explícito. La cobertura se registra en `cobertura_archivos_v8.csv`; al final, el 100% debe estar clasificado.

| Capa | Ficheros | Control |
|---|---:|---|
| Núcleo Python (`extract`, `transform`, `storage`, `analysis`, `scripts`, `tests`) | 140 | AST + lectura semántica + imports + entrypoints |
| Tests | 31 ficheros / 238 tests | Mapa test → requisito/criterio; asserts; skips; mutaciones |
| OpenSpec | 296 (248 `.md`, 1 `.py`, resto JSON) | Requisitos, escenarios, cambios, trazas y staleness |
| Documentación activa | 146 (77 `.md`, 36 `.py`, resto artefactos) | Contraste con código y datos; comandos; cifras |
| Config/CI/root | `config/`, `.github/`, `requirements.txt`, `README.md`, `AGENT.md`, `.env.example` | Secretos, env, dependencias, paths, gates |
| Datos | 605 (356 raw, 191 procesado, 58 resultados) | Hash, manifest, esquema, filas, nulos, HDFS/Mongo |
| Auxiliares/generados | `archive/`, `vaultVivienda/`, `graphify-out/`, `demo-*`, `scratchpad/`, `plan/`, `brief/` | Provenance, referencias, secretos y clasificación histórica |
| Binarios | ZIP, XLSX, PDF, DOCX, PNG, JPG, SVG, MP4, WEBP | Hash/metadatos/estructura; sin revisión visual salvo petición |

Definición de “tocado”:

- Código: todos los `.py` se parsean y se leen; no se acepta “no lo miré”.
- Docs/specs activos: lectura semántica y contraste; los históricos se clasifican y se grep-ean.
- Datos: todos los CSV tienen cabecera, filas, nulos y hash; los binarios tienen hash y metadatos.
- Generados/archivados: se verifica que no son runtime, que no tienen secretos y que sus referencias no engañan.
- No se promete lectura línea a línea de binarios ni de `data/raw` completo; sí integridad y estructura de todos.

## 3. Hipótesis de impacto del cambio

Se intentarán falsar una a una:

- **H1 — CLI**: `--desde-raw`, alias `--sin-descargar`, `--promote` y combinaciones se comportan como dice el docstring y el spec.
- **H2 — Sin staging**: ninguna ruta crea, lee ni espera `data/staging/`; la descarga real no lo recrea.
- **H3 — Raw inmutable**: sin `--promote` no hay escritura; con mismo SHA no hay reescritura; con SHA distinto se aborta; el mtime no cambia.
- **H4 — Raw ausente**: si se borra el raw, `--promote` escribe con `assert_raw_writable`; ¿actualiza manifest? Si no, es un hallazgo.
- **H5 — Guard**: `assert_raw_writable` exige `.FROZEN`, motivo no vacío y deja auditoría; no hay bypass por `sys.path.insert`.
- **H6 — Validación**: 272 códigos, 252 mínimos, año 2024, rango 0–100, duplicados, decimales y encoding latin-1.
- **H7 — Red**: timeout, `raise_for_status`, tamaño, content-type, fallo de red y respuesta vacía.
- **H8 — Downstream**: raw → `limpiar_vpo_municipal.py` → 252 filas / 251 con dato / Usansolo nulo → Mongo → `pipeline_vpo_terminadas` → 8 CSV/PNG.
- **H9 — HDFS/manifest**: 354 SHA locales, 352 canónicos HDFS, 2 alias legacy; el cambio no altera ninguno.
- **H10 — Tests/CI**: la suite sigue en 238/236/2; CI offline no depende de red ni de staging.
- **H11 — Docs**: no queda una instrucción de usar staging; las menciones son “no se crea”; no hay conteos nuevos desfasados.
- **H12 — Histórico**: `archive/`, `vaultVivienda/`, `graphify-out/` y evidencia 2026-11-08 pueden mencionar staging; se clasifican como históricos y no se reescriben.

## 4. Fases

### Fase 0 — Baseline y congelación (read-only)

- `git status`, `git diff`, `git diff --check`, `git log -5`.
- Inventario completo con ruta, tamaño, SHA-256, extensión, tracked/untracked y categoría.
- Snapshot de raw, manifest, HDFS, Mongo, Kafka, CSV de resultados y suite.
- `compileall` de todo el código.
- Guardar en `openspec/audit/v8_2026-11-09/00_baseline_v8.md` y `evidencia/baseline/`.
- **Gate A**: si raw/HDFS/Mongo no coinciden con el baseline conocido, parar y reportar.

### Fase 1 — Impacto del cambio VPO (prioridad máxima)

1. **Extractor**: AST de `26_vpo_terminadas.py`; revisar `descargar`, `validar`, `promover`, `main`, imports, errores y constantes.
2. **Matriz CLI**: sin flags, `--desde-raw`, `--sin-descargar`, `--promote`, `--desde-raw --promote`, raw ausente, CSV corrupto, 251 códigos, valor fuera de rango, red caída.
3. **Raw**: SHA, tamaño, mtime, `.FROZEN`, manifest línea 354; sonda de `promover` con mismo SHA, SHA distinto y raw ausente en `tempfile`/monkeypatch.
4. **Staging**: `find data/staging`, `git check-ignore`, grep de referencias activas, ejecución real de descarga sin `--promote`.
5. **Downstream**: `limpiar_vpo_municipal.py` sobre copia temporal; verificar 252 filas, 251 valores, Usansolo nulo, columnas y SHA del silver; no sobrescribir `data/procesado`.
6. **Mongo/analysis**: lectura de `load_vpo_municipal`, `pipeline_vpo_terminadas`, `run_analisis_mongo`; conteos 252/251; 8 exports; H5/K.
7. **OpenSpec**: proposal/spec/design/tasks/verify-report del cambio nuevo; coherencia con el cambio 2026-11-05 y con `config/fuentes.yaml`.
8. **Docs**: `README`, `AGENT`, `docs/arquitectura_datos.md`, `docs/modelo_mongodb.md`, `docs/matriz_indicadores.md`, `docs/diccionario_columnas.md`, `docs/guion_defensa_12min.md`, `docs/informe_final.md`.
9. **CI**: `.github/workflows/quality-gate.yml`; comprobar que `pytest tests -q` no requiere red ni staging.
10. **Gate B**: si raw/HDFS cambian, o si el cambio rompe el flujo, parar y reportar antes de seguir.

### Fase 2 — Auditoría estática integral

- **Python**: 193 ficheros; AST, imports, funciones, clases, entrypoints, `if __name__`, rutas, encoding, IO, red, Mongo, HDFS/Kafka, raw.
- **Patrones de riesgo**: `except:`/`except Exception` vacíos, `pass`, `TODO/FIXME`, `drop()`, `delete_many`, `replace_collection`, `write_bytes`, `open(...,"w")`, `subprocess`, `eval`, `exec`, `pickle`, `yaml.load`, `requests` sin timeout, secretos, paths absolutos, `sys.path`.
- **Tests**: los 238; mapa a 46 requisitos y 19 criterios; comprobar que no hay asserts triviales, skips injustificados ni tests que muten producción.
- **OpenSpec**: 248 `.md`; requisitos con ID, escenarios Given/When/Then, cambios cerrados, trazas y referencias muertas.
- **Docs**: 77 `.md` activos; cifras (594 vs 759, 16 vs 14, 11 vs 10, IXSCAN 8 vs 1, 204/126/50/39 vs 173/113/40, 238 vs 136), comandos y estados “pendiente”.
- **Config/CI**: `.env.example`, `requirements.txt`, `config/fuentes.yaml`, workflow; dependencias, env y permisos.
- **Datos**: 356 raw, 191 procesado, 58 resultados; manifiestos, cabeceras, filas, nulos, rangos, hashes y correspondencia HDFS.
- **Auxiliares**: `archive/`, `vaultVivienda/`, `graphify-out/`, `demo-*`, `scratchpad/`, `brief/`, `plan/`; clasificar y buscar secretos/referencias obsoletas.

### Fase 3 — Verificación dinámica y de datos

- `pytest tests -q` y suites focalizadas: raw, VPO, contrato, manifest, run_all, extremo a extremo, Mongo, Kafka.
- `scripts/verificar_gobernanza.py`, `transform/run_all.py --check`, `scripts/gate_extremo_a_extremo.py --offline`, `scripts/verificar_fase_datos.py`.
- `compileall` y `git diff --check`.
- HDFS: `GETFILESTATUS`, `OPEN`, SHA, `LISTSTATUS`, `GETCONTENTSUMMARY`; solo lectura.
- Mongo: conteos, 11 pipelines con `limit 2`, `explain`; solo lectura; tests contra `vivienda_euskadi_test`.
- Kafka: metadata, offsets, lag; sin producir mensajes.
- Datos: recomputar 252/251, 594, 188 silver, 354 manifest, 352 HDFS; comparar CSV/PNG esperados.
- Si un comando escribe (`load_all`, `clean_all`, `run_analisis_mongo` completo), se ejecuta con `--dry-run`, `--salida` temporal o no se ejecuta; se documenta.

### Fase 4 — Contrato y rúbrica

- Reextraer la rúbrica del PDF/DOCX con la skill `pdf-extraction` y cotejar con `openspec/specs/contrato-reto/spec.md`.
- Reconstruir la matriz 19 criterios / 190 puntos con evidencia nueva, no con la v7.
- Revalidar H-01…H-07 y buscar regresiones del cambio.
- Puntuar C2 HDFS con la misma regla: 7 si `procesado` sigue 404; no inflar por el cambio VPO.
- Separar “criterio cumple” de “documentación lo cuenta bien”.

### Fase 5 — Adversarial y regresión

- `doubt-driven-development`: revisar el cambio como si otro agente lo hubiera escrito; buscar el fallo que el verify-report no vio.
- Pruebas de borde del CSV: duplicados, 251 códigos, año ausente, columna desplazada, decimales, latin-1, payload vacío, HTML de error.
- Pruebas de raw: `.FROZEN` ausente, raw vacío, SHA distinto, permisos, concurrencia exists/write.
- Pruebas de red: timeout, 404, 500, redirect, respuesta gigante; sin descargar a disco.
- Comprobar que `--promote` no deja raw a medias si falla la escritura.
- Comprobar que el manifest no queda desactualizado si se escribe raw nuevo (H4).
- Revisar que `data/staging` no reaparece por ningún script, test, doc o workflow.

### Fase 6 — Informe y gate

- `00_baseline_v8.md`
- `inventario_archivos_v8.csv` + `cobertura_archivos_v8.csv`
- `inventario_funciones_v8.csv`
- `matriz_tests_v8.csv`
- `matriz_cambio_vpo_v8.md`
- `matriz_rubrica_v8.md`
- `hallazgos_v8.csv` (P0/P1/P2/P3, criterio, evidencia, impacto, acción)
- `backlog_v8.md`
- `informe_reauditoria_v8.md`
- `evidencia/` con logs, JSON, CSV y hashes
- Actualizar `openspec/changes/2026-11-09-vpo-sin-staging/verify-report.md` solo si hay evidencia nueva; no reescribir historia.

## 5. Skills

| Skill | Uso |
|---|---|
| `spec-driven-development` | Contrato, requisitos, escenarios y trazabilidad |
| `code-review-and-quality` | Revisión multi-eje de código cambiado y crítico |
| `doubt-driven-development` | Pase adversarial e hipótesis alternativas |
| `test-driven-development` | Calidad de tests, regresión y cobertura del cambio |
| `debugging-and-error-recovery` | Análisis de fallos y causa raíz |
| `security-and-hardening` | Secretos, red, input, paths, escrituras |
| `documentation-and-adrs` | Deriva docs/specs y decisiones |
| `systematic-issue-triage` | Clasificación por clase raíz y backlog |
| `exploratory-data-analysis` | Integridad de CSV, nulos, rangos y conteos |
| `ci-cd-and-automation` | Workflow offline y gates |
| `pdf-extraction` | Rúbrica PDF/DOCX y cotejo contractual |
| `performance-optimization` | Solo si aparece un problema real de memoria/tiempo |

No se usarán `browser-testing` (no hay UI web), `mongo` (es una skill de examen, no de auditoría) ni skills de modelado/ML.

## 6. Guardrails

- No escribir en `data/raw`, `data/procesado`, `data/resultados`, Mongo, HDFS ni Kafka.
- No ejecutar `load_all`, `clean_all`, `run_analisis_mongo` completo ni productor Kafka.
- No borrar ni mover ficheros fuera de `openspec/audit/v8_2026-11-09/`.
- No instalar dependencias sin autorización.
- No commit ni push.
- Cualquier prueba de escritura usa `tempfile`, copia o monkeypatch; nunca el raw real.
- Si un gate vivo no tiene modo read-only, no se ejecuta; se documenta la limitación.
- Los históricos no se reescriben: se clasifican.

## 7. Criterios de aceptación

- 100% de los 1.479 ficheros inventariados y clasificados; 100% de los 193 `.py` parseados; 100% de los 238 tests mapeados; 100% de los 46 requisitos y 19 criterios con evidencia.
- Raw: mismo SHA, tamaño y mtime; HDFS: mismo SHA y `length`; staging: ausente.
- Suite 238/236/2, gobernanza OK, `run_all --check` 34/34, gate offline OK; solo FAIL 07 conocido en fase de datos.
- Cero P0/P1 introducidos por el cambio; si aparece uno, parar y reportar.
- Documentación sin instrucciones activas de staging y sin cifras nuevas contradictorias.
- Veredicto explícito: PASS / PASS CON RESERVAS / FAIL, con puntuación y reservas.
- Ningún fix aplicado sin autorización.

## 8. Autorización

No se ejecutará ninguna fase hasta recibir una de estas respuestas:

- **“Autorizo la reauditoría v8 completa”**: fases 0–6, solo lectura y pruebas, sin mutar datos.
- **“Autorizo solo el impacto del cambio VPO”**: fases 0–1 y verificación dirigida.
- **“Ajusta el plan”**: se modifica antes de ejecutar.
