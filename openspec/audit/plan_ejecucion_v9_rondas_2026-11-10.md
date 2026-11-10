# Plan de ejecución por rondas — auditoría v9 (2026-11-10)

**Propósito:** ejecutar el plan v9 por fases con **3 subagentes por ronda** y ventana deslizante.
**Referencia:** `openspec/audit/plan_reauditoria_v9_2026-11-10.md` (17 unidades) + `unidades_trabajo_v9.csv`.
**Baseline congelada:** `openspec/audit/v9_2026-11-10/00_baseline_v9.md`.
**Unidades nuevas:** W2.5 (config/CI/root) y W2.6 (auxiliares) tapan dos capas del universo que el plan v9 dejaba sin unidad propia. Total: **18 unidades + W0.1 ya hecha**.

---

## 0. Modelo de orquestación

- **3 agentes concurrentes como máximo**, ventana deslizante.
- Las **rondas son la agrupación lógica por fase**; la ejecución real la marcan la cola y los slots libres.
- Cuando un agente termina, se lanza la **primera unidad de la cola cuyas dependencias estén cubiertas**. Nunca más de 3 vivos.
- Si dos unidades tocan la **misma carpeta, se serializan**: no se solapan.
- Cada agente escribe **solo** en `openspec/audit/v9_2026-11-10/` con su prefijo. No toca código, datos, Mongo, HDFS ni Kafka. No instala dependencias. No commit/push.
- Si un agente encuentra un **P0/P1 nuevo, para y reporta**; no lo arregla.
- Tras cada ronda, el coordinador revisa los artefactos y decide: **continuar, pausar o parar**.

---

## 1. Tabla de rondas (espina de ejecución)

| Ronda | Fase | Agente 1 | Agente 2 | Agente 3 | Gate de salida |
|---|---|---|---|---|---|
| **R1** | 1+2 | W1.1 rúbrica PDF (19 criterios) | W1.2 46 requisitos → 19 criterios + Tema 8 | W2.1 `extract/` (41 `.py`) | `rubrica_reextraida.md` + `mapa_requisitos.md` + `informe_extract.md` |
| **R2** | 1+2 | W1.3 cotejo literal PDF/docx vs contrato | W2.2 `transform/` (42 `.py`) | W2.3 `storage/`+`analysis/`+`scripts/` (21 `.py`) | `desviaciones_rubrica_contrato.md` + `informe_transform.md` + `informe_storage_analysis_scripts.md` |
| **R3** | 2+3 | W2.4 `tests/` (30 ficheros) | W3.2 Mongo read-only | W3.3 datos + sonda HDFS/Kafka | `mapa_tests.md` + `informe_mongo_v9.md` + `informe_datos_v9.md` |
| **R4** | 3+4 | W3.1 verificación dinámica | W4.1 doc sweep 1 | W4.2 doc sweep 2 | `verificacion_dinamica.md` + `doc_sweep_1.md` + `doc_sweep_2.md` |
| **R5** | 4+5 | W4.3 doc sweep 3 | W5.1 pase adversarial | W2.5 config/CI/root | `doc_sweep_3.md` + `informe_adversarial.md` + `informe_config_ci.md` |
| **R6** | 5+6 | W5.2 simulacro tribunal | W2.6 auxiliares | W6.1 síntesis *(entra al terminar W5.2)* | `simulacro_tribunal.md` + `informe_auxiliares.md` + `matriz_rubrica_v9.md` + `hallazgos_v9.csv` + `backlog_v9.md` + `informe_reauditoria_v9.md` |

**Cadena crítica:** W1.1 → W1.3 → (W4.1–W4.3) → W5.2 → W6.1. Las unidades de código (W2.x) y datos (W3.x) corren en paralelo y desbloquean W5.1.

---

## 2. Detalle por ronda

### Ronda 1 — arranque (Fase 1 + Fase 2)

**Objetivo:** fijar la rúbrica y el mapa de requisitos, y abrir el código por la extracción.

| Agente | Unidad | Entrada | Salida | Criterios | Est. |
|---|---|---|---|---|---|
| A1 | W1.1 | `brief/RETO 1Evaluacion SBD-BDAv2.pdf`, contrato, `matriz_rubrica_v8.md` | `rubrica_reextraida.md` | 1–19 | M (45 min) |
| A2 | W1.2 | `openspec/specs/*/spec.md` (5 ficheros) | `mapa_requisitos.md` | 1–19; Tema 8 | M (45 min) |
| A3 | W2.1 | `extract/*.py` (41) | `informe_extract.md` | 1; 15 | L (90 min) |

**Gate de salida:** existen los 3 artefactos; W1.1 y W1.2 completadas (desbloquean W1.3 y W4.1–W4.3).
**Ventana deslizante:** al terminar A1 o A2, entran W1.3 (si W1.1 está) y W2.2/W2.3.

### Ronda 2 — cierre de rúbrica + núcleo de transformación

**Objetivo:** cerrar el cotejo literal y auditar `transform/` y `storage/analysis/scripts/`.

| Agente | Unidad | Entrada | Salida | Criterios | Est. |
|---|---|---|---|---|---|
| B1 | W1.3 | PDF + docx + contrato | `desviaciones_rubrica_contrato.md` | todos | S (30 min) |
| B2 | W2.2 | `transform/*.py` (42) | `informe_transform.md` | 6; 7; 15 | L (90 min) |
| B3 | W2.3 | `storage/*.py` (7), `analysis/*.py` (7), `scripts/*.py` (7) | `informe_storage_analysis_scripts.md` | 2; 3; 4; 10–14; 16–19 | L (90 min) |

**Gate de salida:** existen los 3 artefactos; W1.3 sin desviaciones sin declarar.
**Ventana deslizante:** al terminar B1, entra W2.4; al terminar B2 o B3, entra W3.2 o W3.3.

### Ronda 3 — tests + datos + Mongo

**Objetivo:** mapear tests a requisitos y revalidar Mongo y datos en vivo (o documentar la caída de HDFS/Kafka).

| Agente | Unidad | Entrada | Salida | Criterios | Est. |
|---|---|---|---|---|---|
| C1 | W2.4 | `tests/*.py` (30) | `mapa_tests.md` | todos | M (60 min) |
| C2 | W3.2 | Mongo read-only; `analysis/mongo_aggregations.py`, `mongo_indexes.py`, `run_analisis_mongo.py`, `storage/mongo.py` | `informe_mongo_v9.md` | 5; 6; 9–14; 16–19 | M (60 min) |
| C3 | W3.3 | `data/raw/`, `data/procesado/`, `data/resultados/`, manifests, 8 CSV `mongo_*` | `informe_datos_v9.md` | 2; 3; 19 | M (45 min) |

**Gate de salida:** existen los 3 artefactos; C3 documenta la sonda HDFS/Kafka (si no hay red, lo declara; no lo trata como fallo del proyecto).
**Ventana deslizante:** al terminar C1, entra W3.1 (si W2.4 está); al terminar C2 o C3, entra W4.1 o W4.2.

### Ronda 4 — verificación dinámica + barrido doc 1 y 2

**Objetivo:** ejecutar la suite y gates, y barrer los documentos que más citen cifras.

| Agente | Unidad | Entrada | Salida | Criterios | Est. |
|---|---|---|---|---|---|
| D1 | W3.1 | `tests/`, `verificar_gobernanza.py`, `run_all.py`, `gate_extremo_a_extremo.py`, workflow CI | `verificacion_dinamica.md` | todos | M (60 min) |
| D2 | W4.1 | `docs/modelo_mongodb.md`, `docs/matriz_indicadores.md`, `docs/informe_capacidad_mongo.md` | `doc_sweep_1.md` | 9; 12; 17; 18 | M (60 min) |
| D3 | W4.2 | `docs/informe_final.md`, `docs/preguntas_analisis_profesional.md`, `docs/guion_defensa_12min.md`, `docs/guion_defensa.md` | `doc_sweep_2.md` | 12; 13; 16; 18 | M (60 min) |

**Gate de salida:** existen los 3 artefactos; D1 con suite 235/2 y gates OK (o FAIL 07 aislado).
**Ventana deslizante:** al terminar D2 o D3, entra W4.3.

### Ronda 5 — barrido doc 3 + adversarial + config/CI

**Objetivo:** cerrar el barrido documental, hacer el pase adversarial y auditar config/CI/root.

| Agente | Unidad | Entrada | Salida | Criterios | Est. |
|---|---|---|---|---|---|
| E1 | W4.3 | `docs/README.md`, `README.md`, `AGENT.md`, `openspec/project.md`, `docs/arquitectura_datos.md`, `docs/analisis_vault_vs_rubrica.md` | `doc_sweep_3.md` | 2; 3; 6; 13; 19 | M (60 min) |
| E2 | W5.1 | todo el repo (read-only) | `informe_adversarial.md` | todos | M (60 min) |
| E3 | W2.5 | `.env.example`, `requirements.txt`, `config/fuentes.yaml`, `.github/workflows/quality-gate.yml`, `README.md`, `AGENT.md` | `informe_config_ci.md` | 2; 3; 19 | S (30 min) |

**Gate de salida:** existen los 3 artefactos; W4.3 con H-03/H-06/H-07/H-14/H-15 localizados con fichero:línea.
**Ventana deslizante:** al terminar E1, entra W5.2 (si W3.1, W4.1, W4.2, W4.3 están).

### Ronda 6 — simulacro + auxiliares + síntesis

**Objetivo:** cerrar con el simulacro de tribunal y la síntesis accionable.

| Agente | Unidad | Entrada | Salida | Criterios | Est. |
|---|---|---|---|---|---|
| F1 | W5.2 | `docs/guion_defensa.md`, `docs/guion_defensa_12min.md`, `docs/conclusiones_municipios.md`, contrato | `simulacro_tribunal.md` | todos | M (60 min) |
| F2 | W2.6 | `vaultVivienda/`, `archive/`, `demo-kpi/`, `demo-mapa/`, `scratchpad/`, `plan/`, `brief/` | `informe_auxiliares.md` | 2; 3; 19 | S (30 min) |
| F3 | W6.1 | salidas de R1–R5 + `simulacro_tribunal.md` | `matriz_rubrica_v9.md`, `hallazgos_v9.csv`, `backlog_v9.md`, `informe_reauditoria_v9.md`, `cobertura_archivos_v9.csv` | 1–19 | L (90 min) |

**Gate de salida:** existen los 6 artefactos; F3 entra **después** de que F1 entregue `simulacro_tribunal.md` (dependencia W5.2).
**Handoff interno:** F1 y F2 corren primero; cuando F1 termina, F3 ocupa su slot.

---

## 3. Distribución por fase

| Fase | Unidades | Rondas |
|---|---|---|
| 0. Baseline | W0.1 (hecha) | — |
| 1. Rúbrica y contrato | W1.1, W1.2, W1.3 | R1 (W1.1, W1.2), R2 (W1.3) |
| 2. Auditoría estática | W2.1, W2.2, W2.3, W2.4, W2.5, W2.6 | R1 (W2.1), R2 (W2.2, W2.3), R3 (W2.4), R5 (W2.5), R6 (W2.6) |
| 3. Verificación dinámica y datos | W3.1, W3.2, W3.3 | R3 (W3.2, W3.3), R4 (W3.1) |
| 4. Barrido documental | W4.1, W4.2, W4.3 | R4 (W4.1, W4.2), R5 (W4.3) |
| 5. Adversarial y defensa | W5.1, W5.2 | R5 (W5.1), R6 (W5.2) |
| 6. Síntesis | W6.1 | R6 |

---

## 4. Cola de ventana deslizante

Orden de la cola (dependencias ya resueltas):

```
W1.1, W1.2, W2.1,          # R1
W1.3, W2.2, W2.3,          # R2
W2.4, W3.2, W3.3,          # R3
W3.1, W4.1, W4.2,          # R4
W4.3, W5.1, W2.5,          # R5
W5.2, W2.6, W6.1           # R6 (W6.1 tras W5.2)
```

**Regla:** cuando quede un slot libre, se lanza la primera unidad de la cola cuyas dependencias estén cubiertas. Si la primera no puede, se prueba la siguiente.

---

## 5. Nomenclatura de artefactos y reglas de conflicto

Todos en `openspec/audit/v9_2026-11-10/`:

| Prefijo | Unidad | Fichero |
|---|---|---|
| `rubrica_` | W1.1 | `rubrica_reextraida.md` |
| `mapa_requisitos` | W1.2 | `mapa_requisitos.md` |
| `desviaciones_` | W1.3 | `desviaciones_rubrica_contrato.md` |
| `informe_extract` | W2.1 | `informe_extract.md` |
| `informe_transform` | W2.2 | `informe_transform.md` |
| `informe_storage_analysis_scripts` | W2.3 | `informe_storage_analysis_scripts.md` |
| `mapa_tests` | W2.4 | `mapa_tests.md` |
| `informe_config_ci` | W2.5 | `informe_config_ci.md` |
| `informe_auxiliares` | W2.6 | `informe_auxiliares.md` |
| `verificacion_dinamica` | W3.1 | `verificacion_dinamica.md` |
| `informe_mongo_v9` | W3.2 | `informe_mongo_v9.md` |
| `informe_datos_v9` | W3.3 | `informe_datos_v9.md` |
| `doc_sweep_1/2/3` | W4.1/W4.2/W4.3 | `doc_sweep_1.md`, `doc_sweep_2.md`, `doc_sweep_3.md` |
| `informe_adversarial` | W5.1 | `informe_adversarial.md` |
| `simulacro_tribunal` | W5.2 | `simulacro_tribunal.md` |
| `matriz_rubrica_v9` + `hallazgos_v9.csv` + `backlog_v9.md` + `informe_reauditoria_v9.md` + `cobertura_archivos_v9.csv` | W6.1 | 5 ficheros |

**Reglas de conflicto:**
- W4.1/W4.2/W4.3 escriben en `docs/` y `openspec/project.md`: sus ficheros de entrada están particionados y no se solapan. Ninguna otra unidad escribe en `docs/`.
- W6.1 es el único que escribe `matriz_rubrica_v9.md`, `hallazgos_v9.csv`, `backlog_v9.md`, `informe_reauditoria_v9.md` y `cobertura_archivos_v9.csv`.
- Las unidades de código son de solo lectura: no escriben en el repo, solo en su informe.

---

## 6. Gates

### Gates de ronda

| Gate | Condición |
|---|---|
| **G0** (antes de R1) | Baseline v9 congelada; usuario autoriza. |
| **G1** (fin R1) | `rubrica_reextraida.md` + `mapa_requisitos.md` + `informe_extract.md` existen; W1.1 y W1.2 completadas. |
| **G2** (fin R2) | `desviaciones_rubrica_contrato.md` + `informe_transform.md` + `informe_storage_analysis_scripts.md`; sin desviaciones sin declarar. |
| **G3** (fin R3) | `mapa_tests.md` + `informe_mongo_v9.md` + `informe_datos_v9.md`; sonda HDFS/Kafka documentada. |
| **G4** (fin R4) | `verificacion_dinamica.md` + `doc_sweep_1.md` + `doc_sweep_2.md`; suite 235/2 y gates OK. |
| **G5** (fin R5) | `doc_sweep_3.md` + `informe_adversarial.md` + `informe_config_ci.md`. |
| **G6** (fin R6) | `simulacro_tribunal.md` + `informe_auxiliares.md` + los 5 ficheros de síntesis. |

### Gate global

- C2/C3 **no revalidables en vivo** (HDFS 50070 y Kafka 9092 caídos): se documenta la limitación y se usa el histórico v8 como evidencia clasificada. **No se infla ni degrada la nota por la caída de red.**
- Nota de referencia: **187/190 (98,4 %)**, C2 = 7 por `data/procesado` 404.
- Veredicto final: PASS / PASS CON RESERVAS / FAIL, con puntuación y reservas explícitas.
- **Ningún fix se aplica durante la auditoría.**

---

## 7. Estimación

| Ronda | Unidades | Duración dominante |
|---|---|---|
| R1 | W1.1 (M), W1.2 (M), W2.1 (L) | ~90 min |
| R2 | W1.3 (S), W2.2 (L), W2.3 (L) | ~90 min |
| R3 | W2.4 (M), W3.2 (M), W3.3 (M) | ~60 min |
| R4 | W3.1 (M), W4.1 (M), W4.2 (M) | ~60 min |
| R5 | W4.3 (M), W5.1 (M), W2.5 (S) | ~60 min |
| R6 | W5.2 (M), W2.6 (S), W6.1 (L) | ~120 min |
| **Total** | 18 unidades | **~8–9 h de pared** en 6 rondas |

---

## 8. Autorización

No se lanza ninguna ronda hasta recibir una de estas respuestas:

- **«Autorizo la ronda 1»** → se lanzan W1.1, W1.2 y W2.1 (3 agentes, solo lectura).
- **«Autorizo las 6 rondas de golpe»** → se ejecuta el calendario completo con la ventana deslizante.
- **«Autorizo solo el barrido documental»** → R4 y R5 (W4.1–W4.3), sin tocar código ni datos.
- **«Ajusta el plan»** → se modifica antes de ejecutar.
