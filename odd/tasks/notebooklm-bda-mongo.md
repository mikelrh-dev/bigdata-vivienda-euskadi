# NotebookLM NB04 — BDA + MongoDB completo

**Estado:** en curso · **Inicio:** 2026-11-13 · **Ruta:** implementación delegada (fichas y notas)
**Ubicación de artefactos:** `vaultVivienda/notebooklm/NB04-BDA-Mongo/` (carpeta gitignored)

## Objetivo

Producir 27 fuentes markdown para un cuaderno de NotebookLM que explique (a) cómo
está montada la BDA del proyecto y (b) todo MongoDB: modelo, ingesta, aggregation,
índices, consultas, una ficha por colección, límites y defensa.

## Problema que resuelve

Las fuentes existentes (README, NB01-NB03, vault 2026-11-08) están desfasadas y se
contradicen: 16 vs 17 colecciones, 10 vs 11 pipelines, topic Kafka viejo, 251 vs 252
VPO, 10 índices definidos vs 8 creados. Un cuaderno construido sobre ellas responde
mal con seguridad.

## Alcance

Dentro:
- `scripts/nb_acta_mongo.py` (read-only) + `00-acta-de-cifras-vigentes.md`.
- 26 fuentes restantes (2 módulos A/B + defensa y glosario).
- Render a HTML/PDF y carga en NotebookLM (etapa final, manual).

Fuera:
- Tocar la base de datos o regenerar artefactos del pipeline.
- Reescribir NB01-NB03 (quedan como histórico).
- Subir datos raw, `.env` o CSVs.

## Tareas

- [x] T1 — Explorar repo, vault y base viva; detectar desfases.
- [x] T2 — Acordar estructura de 27 fuentes y 3 videos.
- [x] T3 — `scripts/nb_acta_mongo.py` genera `_facts.json` + acta (17 vivas + 15 backup, 8/10 índices, 11+1 pipelines).
- [x] T4 — `_brief-redaccion.md` (plantilla y reglas) + `_explain.json` real.
- [ ] T5 — Transversales A: `01-arquitectura-end-to-end.md`, `02-infraestructura-hdfs-kafka.md`.
- [ ] T6 — Transversales B: `03-modelo-y-reglas.md`, `04-mongo-ingesta-y-calidad.md`, `07-indices-panorama-esr.md`.
- [ ] T7 — `05-mongo-aggregations.md`, `06-mongo-consultas-y-geo.md`.
- [ ] T8 — Fichas F01-F06.
- [ ] T9 — Fichas F07-F12.
- [ ] T10 — Fichas F13-F17.
- [ ] T11 — `26-decisiones-limites-defensa.md`, `27-glosario-y-bateria-preguntas.md`.
- [ ] T12 — QA de fidelidad (17 preguntas trampa) y corrección de fuentes.
- [ ] T13 — Render HTML/PDF + carga en NotebookLM + 3 videos.

## Criterios de aceptación

1. Toda cifra de las 27 fuentes coincide con `_facts.json` o con el código citado.
2. Cada colección viva tiene ficha con sus índices explicados uno por uno.
3. Cada índice definido aparece con estado real (creado / no creado).
4. Ninguna fuente menciona cifras del README desfasado como si fueran vigentes.
5. QA: 17/17 preguntas trampa responden la cifra correcta.

## Verificación

- `.venv/Scripts/python.exe scripts/nb_acta_mongo.py` regenera el acta sin error.
- Revisión cruzada: `grep` de cifras clave contra `_facts.json`.
- QA final contra el cuaderno ya cargado en NotebookLM.

## Decisiones

- **Acta como fuente 00 y autoridad.** Cualquier conflicto lo resuelve el acta.
- **Una fuente por colección**, para que las citas de NotebookLM apunten a la ficha.
- **Índices dentro de su ficha** + una nota transversal de rendimiento: se explican
  una sola vez para no contradecirse.
- **17 micro-videos descartados**; 3 videos narrativos (arquitectura / Mongo / defensa).
- `__backup` no lleva ficha: se explica el mecanismo una vez.

## Riesgos

- Deriva doc↔base si la base se recarga a mitad de redacción → regenerar acta.
- NotebookLM no renderiza mermaid → cada diagrama va como código + PNG.
