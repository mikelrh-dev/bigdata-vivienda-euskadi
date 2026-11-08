# Análisis beneficio / riesgo por implementación — v6

**Fecha:** 2026-11-08 · **Base:** `plan_solucion_v6_2026-11-08.md` (S1–S10, F0, P3) y `hallazgos_v6_2026-11-08.csv`.
**Naturaleza:** estimación de decisión, no medición. Beneficio = cierre de hallazgo + valor de defensa. Riesgo = probabilidad × impacto (1–5 cada uno; exposición 1–25).
**Escala:** Bajo ≤ 4 · Medio 5–9 · Alto ≥ 10. Reversibilidad: Alta (git/texto) · Media (datos regenerables con copia) · Baja (historia/datos sin backup).

---

## 1. Matriz resumen

| ID | Implementación | Cierra | Beneficio (1–5) | Riesgo P×I | Nivel | Reversibilidad | Decisión |
|---|---|---|---:|---:|---|---|---|
| F0.1 | Rama `fix/auditoria-v6` | — | 3 | 2×1 = 2 | Bajo | Alta | Hacer ya |
| F0.2 | Baseline (HEAD, diff, índice) | PRE-01 | 4 | 1×1 = 1 | Bajo | Alta | Hacer ya |
| F0.3 | Inventario de cifras obsoletas | P1-01 | 3 | 1×1 = 1 | Bajo | Alta | Hacer ya |
| F0.4/S8 | Commits por unidad | P2-05 | 4 | 3×3 = 9 | Medio | Media | Hacer con control |
| S3 | Rerun `normalizar_json_crudos.py` | P1-03 | 4 | 4×4 = 16 | **Alto** | Media | Hacer con control |
| S4 | Recalcular paro-cero | P1-04 | 5 | 3×4 = 12 | **Alto** | Media | Hacer con control |
| S4b | Waiver del check 07 | P1-04 | 3 | 2×5 = 10 | **Alto** | Alta | Solo si S4 no es posible |
| S5 | IDs `CHART-*` | P2-04 | 3 | 2×2 = 4 | Bajo | Alta | Hacer ya |
| S5b | Guardián a 50/45/34/11 | P2-01 | 3 | 2×2 = 4 | Bajo | Alta | Hacer ya |
| S6 | Archivar colección legacy de habitaciones | P2-02 | 3 | 3×4 = 12 | **Alto** | Media | Posponer tras defensa |
| S6b | Dueño de carga + check vivo | P2-02/P2-08 | 3 | 2×3 = 6 | Medio | Alta | Hacer con control |
| S1 | Tabla canónica única | P1-01 | 4 | 2×2 = 4 | Bajo | Alta | Hacer ya |
| S2 | Sustituciones en docs/spec | P1-01/P1-02/P2-09 | 5 | 3×3 = 9 | Medio | Alta | Hacer ya (tras gates) |
| S9 | README enlaza a fuente única | P2-09 | 3 | 1×2 = 2 | Bajo | Alta | Hacer ya |
| S7 | CI en `master` | P2-03 | 4 | 3×3 = 9 | Medio | Alta | Hacer con control |
| S9bis | Versionar 17 CSV | P2-06 | 4 | 3×4 = 12 | **Alto** | Media | Hacer con control |
| S10 | Arreglar framework archivado | P2-07 | 2 | 1×1 = 1 | Bajo | Alta | Posponer |
| P3-01 | 9 enlaces rotos | P3-01 | 2 | 1×1 = 1 | Bajo | Alta | Posponer |
| P3-02 | Encoding tolerante en 5 CSV | P3-02 | 3 | 2×2 = 4 | Bajo | Alta | Hacer con control |
| P3-03 | Acotar `except Exception` | P3-03 | 3 | 3×3 = 9 | Medio | Media | Posponer tras defensa |
| P3-04 | Asserts de dominio | P3-04 | 3 | 2×3 = 6 | Medio | Alta | Hacer con control |
| P3-05 | `[TEMPLATE]` en `.env.example` | P3-05 | 1 | 1×1 = 1 | Bajo | Alta | Hacer ya |
| P3-06 | Documentar dueño de habitaciones | P3-06 | 2 | 1×1 = 1 | Bajo | Alta | Se funde con S6 |

---

## 2. Detalle por implementación

### F0.1 — Rama de trabajo

- **Beneficio:** aísla 10–13 h de cambios; permite revertir por fase y comparar contra `master`.
- **Riesgo:** bajo (olvidar volver a `master`, conflicto al mergear). No toca datos.
- **Mitigación:** una rama, commits pequeños, `git status` antes de cambiar de contexto.
- **Reversibilidad:** alta. **Veredicto:** hacer ya.

### F0.2 — Baseline pineado

- **Beneficio:** convierte la auditoría en reproducible (HEAD + hash del diff + índice). Sin esto, cualquier cifra es discutible.
- **Riesgo:** nulo; solo lectura.
- **Mitigación:** guardar la salida en `evidencia/2026-11-08/`.
- **Reversibilidad:** alta. **Veredicto:** hacer ya.

### F0.3 — Inventario de cifras obsoletas

- **Beneficio:** cierra la lista de sustituciones antes de editar; evita arreglar 10 sitios y dejar 5.
- **Riesgo:** bajo; falsos positivos (citas históricas como «759 era el pre-change») que no deben tocarse.
- **Mitigación:** revisar cada match; marcar explícitamente lo histórico.
- **Reversibilidad:** alta. **Veredicto:** hacer ya.

### F0.4/S8 — Commits por unidad

- **Beneficio:** hace revisable el +604/−36 actual; separa gate, análisis, transform y docs. Sin esto, el P2-05 sigue abierto y la defensa no puede enseñar un diff limpio.
- **Riesgo:** **medio** (3×3). Escenarios: `git add -A` mete artefactos locales, `.env` no (ignorado), pero sí `uv.lock`/PNG; un commit gigante mezcla 11 pipelines con docs y oculta errores; reescribir la historia si se intenta «limpiar» después.
- **Mitigación:** `git add <rutas explícitas>`, `git diff --cached --stat` y `git diff --cached --check` antes de cada commit; nada de `--amend` sobre commits ya publicados; no commitear `data/` salvo CSV decididos en S9bis.
- **Reversibilidad:** media (`git revert`; si se publica, la historia queda). **Veredicto:** hacer con control.

### S3 — Rerun de `normalizar_json_crudos.py` (P1-03)

- **Beneficio:** cierra el staleness que hoy deja `run_all.py --check` en 1; devuelve el DAG a verde y elimina la excusa «34/34» en la defensa.
- **Riesgo:** **alto** (4×4), y el plan original lo subestimaba.
  - El script reescribe **todos** los `data/raw/*.json` normalizados.
  - `run_all.py::_estado` (`transform/run_all.py:325-350`) compara `mtime(entrada) > min(mtime(salida))`. Al tocar los 62 normalizados, **todos sus consumidores pasan a `DESACTUALIZADO`**: el `--check` no queda en 0 con el rerun solo.
  - Si se reejecuta el DAG completo, se reescriben muchos silver y hay que revisar cifras antes de la defensa.
  - `fecha_extraccion` se inyecta desde el mtime del raw; un cambio de mtime altera metadatos.
- **Mitigación:** copia de `data/procesado`; rerun; restaurar `mtime` de los ficheros con hash idéntico (snippet Python con `os.utime`); comparar hashes antes/después; ejecutar **solo la cadena** que `--check` marque; si la cadena supera ~5 scripts, parar y valorar `--check` por hash de contenido o dejar `CUMPLE CON SALVEDAD`.
- **Reversibilidad:** media (copia + datos regenerables). **Veredicto:** hacer con control; **no** ejecutar el DAG completo antes de la defensa.

### S4 — Recalcular paro-cero (P1-04)

- **Beneficio:** cierra el único FAIL de `verificar_fase_datos` y corrige un dato incoherente (paro registrado 0 con tasa 0,28/1,45/3,26). Impacto directo en `OK 18/18`.
- **Riesgo:** **alto** (3×4).
  - No se ha verificado que exista denominador (`activos`) para los 3 municipios; inventarlo sería peor que el FAIL.
  - Cambiar la tasa altera silver, `udalmap_paro.csv`, mapas/figuras y quizá conclusiones; los 3 no están en el top-4, pero pueden aparecer en capas y anexos.
  - Igual que S3, reescribir el silver cascada staleness a los consumidores.
- **Mitigación:** localizar el productor (`grep -rn "tasa_paro_lanbide_pct" transform/`), reutilizar la fórmula existente, test unitario con 3 casos, tabla antes/después, snapshot y `--check` de la cadena. Si falta denominador en ≥2 municipios → S4b.
- **Reversibilidad:** media. **Veredicto:** hacer con control, **antes** de la pasada final de documentación.

### S4b — Waiver del check 07

- **Beneficio:** desbloquea el gate en horas si se demuestra que Lanbide publica esos valores; evita tocar datos.
- **Riesgo:** **alto** (2×5) de credibilidad: un evaluador puede leerlo como «relajar el gate para que pase». El código actual **fuerza FAIL** a propósito (`verificar_fase_datos.py:67-90`); convertirlo en PASS genérico sería maquillar.
- **Mitigación:** captura/fuente oficial, texto `CUMPLE CON SALVEDAD` con fecha y alcance, y que el check siga distinguiendo «waiver documentado» de «PASS». Nunca un `return 0` silencioso.
- **Reversibilidad:** alta (texto). **Veredicto:** solo si S4 no es posible y hay fuente.

### S5 — IDs `CHART-*` (P2-04)

- **Beneficio:** 50/50 requisitos rastreables; el guardián puede contar sin heurísticas; mejora la matriz requisito→test.
- **Riesgo:** bajo (2×2): churn en la spec y referencias por nombre; un ID mal elegido confunde más que ayuda.
- **Mitigación:** añadir ID delante conservando el nombre (`CHART-TIERB-01 — chart_tierB_range`), `grep` de referencias, actualizar guardián en el mismo commit.
- **Reversibilidad:** alta. **Veredicto:** hacer ya.

### S5b — Guardián a 50/45/34/11 (P2-01)

- **Beneficio:** elimina el rojo permanente por cifras canónicas; el guardián vuelve a ser señal, no ruido.
- **Riesgo:** bajo (2×2), pero volverá a quedarse viejo si se hardcodea otra vez.
- **Mitigación:** una constante/JSON canónico (`docs/cifras_canonicas.json`) consumido por el guardián y por el chequeo de docs; si no, comentar junto a cada número qué lo invalida.
- **Reversibilidad:** alta. **Veredicto:** hacer ya.

### S6 — Archivar la colección legacy de habitaciones (P2-02)

- **Beneficio:** deja 15 vivas + backups y elimina el duplicado de 201 docs; contrato claro para el evaluador.
- **Riesgo:** **alto** (3×4): `_hab_col()` (`analysis/mongo_aggregations.py:665-673`) **prefiere `_bigdata` si tiene docs**. Renombrarla hace que la agregación use `unificados`; si los documentos no son idénticos (mismo count y claves no garantiza mismo contenido), cambia `mongo_habitaciones_por_municipio.csv` y las figuras. Además, no hay script activo que escriba ninguna de las dos.
- **Mitigación:** comparar sets de `_id` **y** hash/contenido de los 201 docs; ejecutar el pipeline antes/después y `diff` del CSV; renombrar a `__backup_20261108` (nunca `drop`); actualizar `_hab_col()` y el gate en el mismo commit.
- **Reversibilidad:** media (rename inverso). **Veredicto:** posponer tras la defensa; antes, solo documentar.

### S6b — Dueño de carga + check vivo (P2-08)

- **Beneficio:** evita que el gate offline diga «14» mientras Mongo tiene 16; deja por escrito quién escribe habitaciones.
- **Riesgo:** medio (2×3): el gate vivo puede ponerse rojo en la demo si hay colecciones inesperadas (`system.*`, backups).
- **Mitigación:** allowlist explícita (16 canónicas + `__backup`), ignorar `system.*`, y que el check vivo solo corra con `GATE_LIVE=1`.
- **Reversibilidad:** alta. **Veredicto:** hacer con control.

### S1 — Tabla canónica única

- **Beneficio:** una sola verdad (252/594/11/45/242/28+8/17) que todos enlazan; corta la recurrencia de P1-01.
- **Riesgo:** bajo (2×2): la tabla se queda vieja. No toca código.
- **Mitigación:** fecha de medición, comando que la produce y un chequeo `grep` en la verificación final.
- **Reversibilidad:** alta. **Veredicto:** hacer ya.

### S2 — Sustituciones en docs/spec (P1-01/P1-02/P2-09)

- **Beneficio:** el mayor beneficio de la lista (5): elimina las contradicciones que el tribunal verá en README, AGENT, guion y spec; convierte 4 P1/P2 en cerrados sin tocar datos.
- **Riesgo:** medio (3×3): un `sed` global rompe citas históricas («759 era el pre-change») o cambia el significado de una acceptance de la spec; dejar una cifra vieja en un anexo.
- **Mitigación:** sustituciones **dirigidas** por fichero/línea, revisar `git diff` completo, conservar lo histórico etiquetado, y ejecutar el `grep` de verificación. La spec se toca **después** de S3/S4, para que 18/18 sea verdad.
- **Reversibilidad:** alta (git). **Veredicto:** hacer ya, en último lugar de los P1.

### S9 — README enlaza a la fuente única

- **Beneficio:** evita duplicar la tabla; el README deja de ser un punto de desincronización.
- **Riesgo:** bajo (1×2): si se deja la tabla vieja y se añade la nueva, hay dos fuentes.
- **Mitigación:** borrar la tabla duplicada, dejar resumen + enlace.
- **Reversibilidad:** alta. **Veredicto:** hacer ya.

### S7 — CI en `master` (P2-03)

- **Beneficio:** el gate deja de ser local; cada push ejecuta 242 tests. Cierra P2-03 y da evidencia de automatización.
- **Riesgo:** medio (3×3): el workflow **nunca se ha ejecutado**; en un clon limpio no está `data/`, y algunos tests podrían depender de ella. Además `pytest tests -q` + `addopts=-q` = `-qq` (menos resumen, no fallo). Diferencias Linux/Windows en rutas.
- **Mitigación:** probar en clon limpio (`git clone . /tmp/clean && pytest`) antes de push; usar `-o addopts=""`; no bloquear el merge hasta ver el primer run verde; job separado para vivo.
- **Reversibilidad:** alta. **Veredicto:** hacer con control.

### S9bis — Versionar los 17 CSV (P2-06)

- **Beneficio:** los resultados canónicos quedan en git, el test deja de saltarse y la defensa puede citar CSV versionados.
- **Riesgo:** **alto** (3×4):
  - `tests/test_pisos_ubicacion_real.py` termina con `assert pngs and csvs`. Si se versionan CSV pero no PNG, **en CI no hay PNG y el test falla**; hoy se salta precisamente porque no hay nada trackeado.
  - Ruido en cada rerun, CSV obsoletos commiteados, conflictos de merge.
- **Mitigación:** **antes** de commitear, cambiar el test a «tracked ⊆ local, sin exigir PNG» o versionar un manifiesto SHA de PNG sin binarios; regenerar los 17 CSV desde el estado final; `.gitattributes` para LF; dry-run en clon limpio.
- **Reversibilidad:** media. **Veredicto:** hacer con control, **después** de S3/S4 (si no, se commitean cifras viejas).

### S10 — Framework archivado (P2-07)

- **Beneficio:** el diagnóstico deja de dar falsos NO-GO si alguien lo reutiliza.
- **Riesgo:** bajo (1×1); es código archivado, no entra en la entrega.
- **Mitigación:** corregir `ROOT` y rutas del runbook; smoke test; no usarlo para puntuar.
- **Reversibilidad:** alta. **Veredicto:** posponer.

### P3-01 — Enlaces rotos

- **Beneficio:** navegación limpia en documentación archivada. Valor bajo para la nota.
- **Riesgo:** bajo; editar archivo histórico puede introducir ruido.
- **Mitigación:** corregir o marcar «archivado».
- **Reversibilidad:** alta. **Veredicto:** posponer.

### P3-02 — Encoding tolerante

- **Beneficio:** los 5 CSV raw (3 ECVI, 2 latin-1) se leen sin excepción; menos fallos silenciosos.
- **Riesgo:** bajo (2×2): **no** se debe reescribir el raw (inmutabilidad); solo lectura con fallback. Si se «normaliza» el raw, se rompe el manifiesto SHA.
- **Mitigación:** helper de lectura `utf-8-sig`→`latin-1`, sin escribir en `data/raw`; test con los 5 ficheros.
- **Reversibilidad:** alta. **Veredicto:** hacer con control.

### P3-03 — Acotar `except Exception`

- **Beneficio:** los fallos de carga/índices dejan de ocultarse; mejor depuración.
- **Riesgo:** medio (3×3): al acotar, aparecen excepciones antes silenciadas y el pipeline puede romperse en un momento incómodo.
- **Mitigación:** solo rutas críticas (`storage/`, carga, índices), una por commit, con tests; no hacer barrido masivo antes de la defensa.
- **Reversibilidad:** media. **Veredicto:** posponer tras la defensa.

### P3-04 — Asserts de dominio

- **Beneficio:** los 20 asserts débiles pasan a verificar algo real; menos falsa cobertura.
- **Riesgo:** medio (2×3): algunos tests fallarán al descubrir bugs reales (eso es beneficio, pero consume tiempo).
- **Mitigación:** empezar por los tests de contrato (Tier, dedup, `codigo_ine`), no por los de UI.
- **Reversibilidad:** alta. **Veredicto:** hacer con control.

### P3-05 — `[TEMPLATE]` en `.env.example`

- **Beneficio:** template limpio; evita que un parser estricto lo interprete como clave.
- **Riesgo:** nulo.
- **Mitigación:** comentar la línea (`# [TEMPLATE]`).
- **Reversibilidad:** alta. **Veredicto:** hacer ya.

### P3-06 — Dueño de habitaciones

- **Beneficio:** deja por escrito qué script llena las colecciones; cierra la ambigüedad de P2-02 sin tocar Mongo.
- **Riesgo:** nulo (documentación).
- **Mitigación:** enlazar el pipeline y la carga; se funde con S6.
- **Reversibilidad:** alta. **Veredicto:** incluido en S6.

---

## 3. Los cinco riesgos que pueden costar la defensa

| # | Riesgo | Exposición | Por qué | Go / No-Go |
|---|---|---:|---|---|
| 1 | **Cascada de S3** | 16 | Tocar 62 normalizados deja stale todo el DAG; el `--check` no queda en 0 solo | **No-Go** si el diff >2 ficheros o la cadena >5 scripts |
| 2 | **Recalcular paro sin denominador** | 12 | Inventar activos sería peor que el FAIL; cambia 3 municipios y sus agregados | **No-Go** si falta denominador en ≥2 o se toca el top-4 |
| 3 | **Renombrar `_bigdata`** | 12 | La agregación la prefiere; si el contenido difiere, cambia el CSV y las figuras | **No-Go** si los 201 docs no son idénticos o el CSV cambia |
| 4 | **Versionar CSV sin PNG** | 12 | El test exige `pngs and csvs`; en CI no hay PNG y falla | **No-Go** si el clon limpio no pasa |
| 5 | **Waiver del 07** | 10 | Puede leerse como relajar el gate para aprobar | **No-Go** sin fuente oficial y texto de salvedad |

---

## 4. Orden ajustado por riesgo

1. **Quick wins (sin datos):** F0.1–F0.3 · S1 · S5 · S5b · S9 · P3-05.
2. **P1 con control:** S3 (con backup y mtime) → S4 (o S4b) → una sola pasada de cadena → S2.
3. **Automatización:** S7 (clon limpio) → S9bis (test ajustado primero).
4. **Contrato Mongo:** S6b (documentar + check vivo); S6 (archivar) **después** de la defensa.
5. **Diferible:** S10 · P3-01 · P3-03.

**Regla:** si S3 o S4 consumen más de media jornada o cambian cifras del top-4, se para y se declara `CUMPLE CON SALVEDAD` con evidencia, en lugar de reejecutar todo el DAG la víspera.

---

*Relacionado: `plan_solucion_v6_2026-11-08.md`, `informe_auditoria_v6_2026-11-08.md`, `hallazgos_v6_2026-11-08.csv`.*
