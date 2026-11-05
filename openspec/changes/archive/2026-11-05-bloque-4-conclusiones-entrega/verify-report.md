# Verify Report: bloque-4-conclusiones-entrega

Fecha: 2026-11-05
Modo: READ-ONLY (sin modificar código, sin git add/commit, sin tocar data/raw, sin HDFS)
Rama: master HEAD `123d01c` (feat(bloque2-bloque3): HDFS Kafka gate versionado y Mongo PyMongo cerrado)

## Veredicto: PASS WITH WARNINGS

Justificación: Los artefactos técnicos del gate Bloque 4 están verificados en disco (CSV 253/253/3 con huella `f1e78870…`, comparativa 4 robustos con paro no nulo, matriz/guion/conclusiones con 26,61/25,2% y advertencia Getxo/Vitoria, pytest 130, manifest 353/184, `git status --short data/raw` vacío). Las WARNINGS son de proceso/trazabilidad: `tasks.md` consta con 0/11 `[x]` (11/11 `[ ]`) aunque el apply se anuncia como cerrado, y `docs/trazabilidad_vm.md` NO contiene entrada Bloque 4 (ni re-verificación Kafka pid 1832 ni comparativa Bilbao 173/Donostia 113 con Fecha/Objetivo/Máquina/Comando/Salida/Conclusión). Sin cerrar esas dos, no se recomienda archivar el change.

## Evidencia ejecutada (solo lectura)

| Check | Comando / salida |
|---|---|
| Suite | `.venv/Scripts/python.exe -m pytest tests -q` → `130 passed in 9.89s` |
| Manifest | `wc -l docs/raw_manifest_sha256.txt data/procesado/manifest_sha256.txt` → `353 docs/raw_manifest_sha256.txt`, `184 data/procesado/manifest_sha256.txt` |
| CSV canónicos | `wc -l data/resultados/mongo_esfuerzo_por_municipio.csv data/resultados/mongo_alquiler_por_municipio.csv data/resultados/mongo_modalidades.csv` → `253 / 253 / 3` |
| Comparativa | `wc -l data/resultados/comparativa_3_municipios_mongo.csv` → `5` (cabecera + Bilbao 173, Donostia 113, Getxo 40, Vitoria-Gasteiz 39) |
| fillna | `grep -n fillna analysis/mongo_aggregations.py` → vacío; `grep -rn fillna analysis/` → vacío |
| metodo_imputacion | `grep -n metodo_imputacion docs/matriz_indicadores.md docs/conclusiones_municipios.md` → `docs/matriz_indicadores.md:18` (oficial 159 / IDW_5_vecinos 93, `is_imputed` False/True); NOTFOUND en `docs/conclusiones_municipios.md` |
| Pipeline | `grep -n pipeline_indicadores_municipio\|silver\|is_imputed\|metodo_imputacion analysis/mongo_aggregations.py` → def línea 23, preserva `metodo_imputacion` líneas 89-94, proyección 192-193 |
| Guardrail raw | `git status --short data/raw` → vacío |
| Estado repo | `git status --short` → `M analysis/comparativa_mongo.py`, `M analysis/mongo_aggregations.py`, `M docs/conclusiones_municipios.md`, `M docs/guion_defensa.md`, `M docs/matriz_indicadores.md`, `?? openspec/changes/bloque-4-conclusiones-entrega/` |
| Diff | `git diff --stat` → 5 ficheros, 80 inserciones, 21 borrados (`comparativa_mongo.py` 15, `mongo_aggregations.py` 28, `conclusiones_municipios.md` 6, `guion_defensa.md` 36, `matriz_indicadores.md` 16) |
| Huella SHA-256 disco | `sha256sum` CSV → `831e69ce…` esfuerzo, `ff39e852…` alquiler, `71a72926…` modalidades, `9dc4e8d3…` comparativa — idénticos a la tabla de `docs/matriz_indicadores.md:22-27` y huella agregada `f1e788701ee4b0bfa3da2b9a82c0d2de33df4c1c5ea587af333e874d5a0c63eb` línea 29 |
| Tasks checkboxes | `grep -c \[x\] tasks.md` → `0`; `grep -c \[ \] tasks.md` → `11` (tareas 1.1-1.4, 2.1-2.3, 3.1-3.3, 4.1 todas `[ ]`) |
| Trazabilidad Bloque 4 | `grep -n "Bloque 4" docs/trazabilidad_vm.md` → vacío; última entrada es Bloque 3 gate (líneas 1439-1468). `grep -n "pid 1832\|LISTEN\|9093"` solo líneas 14-40 (Bloque 1). `grep -n "HDFS centro\|10.22.87.215"` solo líneas 3, 46, 1217, 1295 (previas). Sin entrada 2026-11-05 Bloque 4 con Fecha/Objetivo/Máquina/Comando/Salida/Conclusión |
| Guion | `wc -l docs/guion_defensa.md` → `39`; `grep -c "embedding\|índices\|atomicidad"` → `2` líneas (título Tema 8 + entrada); 10 criterios líneas en tabla 1-10 con columna Laguna |
| 16-29 legacy | `grep -rn "16-29" docs/guion_defensa.md docs/conclusiones_municipios.md docs/matriz_indicadores.md` → guion:13,28; conclusiones:5,42; matriz:8,29 — todas marcadas legacy, canónico 18-34 en los tres documentos |

## Evidencia por requirement

### INDICADORES-01 — PASS
- `pipeline_indicadores_municipio` existe en `analysis/mongo_aggregations.py:23` con proyección `metodo_imputacion` (159 oficial / 93 IDW) e `is_imputed` derivado (False oficial, True IDW), líneas 89-94 y 192-193, documentado en `docs/matriz_indicadores.md:18`.
- Cero `fillna` en `analysis/` (sin mediana silenciosa).
- CSV 253/253/3 verificados con `wc -l` y SHA-256 idénticos a la tabla de huella de `docs/matriz_indicadores.md:20-29`.

### RESPUESTA-01 — PASS WITH WARNINGS
- Comparativa `data/resultados/comparativa_3_municipios_mongo.csv` 5 líneas: Bilbao 48020 n=173 paro 9,71; Donostia 20069 n=113 paro 5,82; Getxo 48044 n=40 paro 6,4; Vitoria-Gasteiz 01059 n=39 paro 8,89 — `codigo_ine` 5 dígitos, paro Lanbide no nulo en los 4.
- `docs/conclusiones_municipios.md`: tabla 4 robustos (líneas 5-10), mediana 26,61 y 25,2% sobre 30 (40/159) líneas 28-29 y tabla O1 líneas 32-37, advertencia literal «Getxo 40 vs Vitoria-Gasteiz 39 (1 anuncio de diferencia)… no es ranking firme» línea 23.
- WARNING: `docs/conclusiones_municipios.md` solo desarrolla sección O1 (líneas 26, 32); O2-O4 aparecen en `docs/guion_defensa.md:14-16`, no como matriz O1-O4 completa en conclusiones.
- WARNING: La trazabilidad exigida («SHALL registrarse en `docs/trazabilidad_vm.md` con Fecha/Objetivo/Máquina/Comando/Salida/Conclusión») NO consta para Bloque 4: grep «Bloque 4» vacío, sin línea «Bilbao 173 / Donostia 113» en trazabilidad. Tarea 2.3 queda sin evidencia.

### CONCLUSION-01 — PASS WITH WARNINGS
- `docs/guion_defensa.md` (39 líneas): título «Guion Tema 8 (1 página)», sección «Tema 8: embedding, índices, atomicidad» con definición de los tres, cadena «HDFS centro `http://10.22.87.215:50070` solo lectura + Kafka VM `192.168.201.162:9094` broker 4.3.1 KRaft pid 1832» línea 3, tabla de 10 criterios con laguna por criterio (líneas 24-35), y 16-29 legacy / 18-34 canónico líneas 13, 28.
- WARNING: «1 página» es afirmación del título; 39 líneas con 3 tablas no se verificó por paginación renderizada (sin DOCX/PDF en el change). Tarea 3.1 marcada como cumplida en contenido, página solo declarada.
- WARNING: Re-verificación Kafka pid 1832 (tarea 3.3): solo hay evidencia de Bloque 1 en `docs/trazabilidad_vm.md:14-40` (LISTEN 9093/9094, `java pid=1832`). No hay entrada Bloque 4 con `LISTEN 9093/9094` actual; el guion línea 3 afirma «re-verificado en `docs/trazabilidad_vm.md`», afirmación no soportada por una entrada nueva. HDFS centro queda reflejado en trazabilidad en entradas previas (líneas 46, 1217, 1295), no en una entrada Bloque 4.

### Gate Bloque 4 — PASS (con observaciones)
- CSV 253/253/3 con huella: PASS. Comparativa 4 con paro no nulo: PASS. Guion con 10 criterios, lagunas y 16-29 legacy: PASS contenido. Pytest 130 passed: PASS. Manifest 353/184: PASS. `git status --short data/raw` vacío: PASS. Procesado sin subir (sin cambios en `data/procesado/` en git status): PASS.
- Observación: `git status --short` muestra 5 modificados sin commit (esperable en fase verify) y el change `openspec/changes/bloque-4-conclusiones-entrega/` untracked. No se hizo git add/commit en esta fase.

## Risks

- HIGH — Trazabilidad bloqueante: Sin entrada Bloque 4 en `docs/trazabilidad_vm.md`, las tareas 2.3 y 3.3 y la sub-cláusula de trazabilidad de RESPUESTA-01/CONCLUSION-01 no se pueden cerrar en auditoría; la defensa «re-verificado en trazabilidad» es hoy falsa en sentido estricto (solo Bloque 1).
- MED — Tasks sin marcar: 0/11 `[x]` contradice el parte del apply («11 tareas [x]»). Hay que marcarlas solo tras subsanar la trazabilidad, no antes.
- MED — O1-O4 disperso: conclusiones solo O1; evaluador que busque matriz O1-O4 en `conclusiones_municipios.md` no la encontrará completa (está en guion).
- MED — «1 página» no probada por render: riesgo bajo si el evaluador cuenta líneas, alto si exige paginación A4.
- LOW — Kafka pid 1832 y HDFS centro son IPs/DNS efímeros de VM; sin re-verificación fechada Bloque 4, el guion puede quedar obsoleto en la fecha de defensa (pregunta abierta de `design.md:119-121`).
- LOW — `metodo_imputacion` no aparece literal en `conclusiones_municipios.md` (sí en matriz y pipeline); coherencia terminológica a normalizar.

## Recomendación

1. Añadir en `docs/trazabilidad_vm.md` una entrada 2026-11-05 Bloque 4 (Fecha/Objetivo/Máquina/Comando/Salida/Conclusión) con: regeneración CSV + huella `f1e78870…`, comparativa Bilbao 173/Donostia 113/Getxo 40/Vitoria 39, y re-verificación `ss -tlnp | grep 9093/9094` + `ps pid 1832` + HDFS centro solo lectura. Sin tocar `data/raw` ni subir procesado.
2. Marcar las 11 tareas `[x]` en `tasks.md` solo tras (1).
3. Opcional: completar matriz O1-O4 en `conclusiones_municipios.md` o citar explícitamente dónde están O2-O4.

Este informe es el único fichero creado en la fase 6. Ningún código implementado, ningún git add/commit.
