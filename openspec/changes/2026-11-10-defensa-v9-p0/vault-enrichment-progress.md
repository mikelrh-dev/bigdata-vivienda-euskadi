# Vault enrichment progress — 2026-11-10-defensa-v9-p0

Estado: **INTERRUMPIDO** (subagente `deleg_821f36c3` / `sa-0-72f40549`, cancelado por el usuario).

- Inicio: 2026-11-10 14:15:56
- Interrupción: 2026-11-10 14:40:03
- Duración: ~24 min (1446 s)
- api_calls: 60
- Motivo: retry de API fallido (error de red/proveedor) — no bloqueo de código.

## Ubicación del vault

`C:/Users/mikel/Documents/bigdata-vivienda-euskadi/vaultVivienda` (gitignored, no tracked).
Copia en `Desktop/vaultVivienda` (69 notas) y `ObsidianVault/vaultVivienda` (75) NO contienen `vault-defensa`.
El vault de defensa está en `vaultVivienda/vault-defensa/` (38 notas originales + 5 nuevas = 43).

## Tareas completadas (10/10 del plan)

### P0 (críticos)
- ✅ Patch `04-El-modelo/16-indices-esr-y-explain.md` — comando válido (20069, larga_estancia, precio_eur <= 1000), tabla before/after (594→1, totalDocsExamined 594→1, totalKeysExamined 0→1), 8 índices creados, 2dsphere sparse, explain read-only. Pedagogía ESR, $natural hint, por qué no dropear en prod.
- ✅ Patch `03-La-arquitectura/15-aggregation-pipelines.md` — sustituido $median por mediana winsorizada p1–p99 + IQR. Tabla de 11 pipelines Mongo (función → CSV → filas → etapas). Enlace a vault-tecnico.
- ✅ Nueva `04-El-modelo/16b-explain-antes-despues.md` — COLLSCAN vs IXSCAN, $natural hint, por qué no dropear índice en prod. Mermaid + flashcards.

### P1
- ✅ Patch `04-El-modelo/18-consultas-utiles.md` — mediana winsorizada / $group en vez de $median por grupo.
- ✅ Nueva `03-La-arquitectura/15b-pipelines-mongo-11.md` — 11 funciones, filas (252/322/251/2/10/4), etapas $lookup/$unwind/$group. Mermaid.
- ✅ Nueva `04-El-modelo/19-indices-2dsphere-y-geo.md` — 424/594 con geo, índice sparse, motivo de nulos. Mermaid.
- ✅ Nueva `06-Las-pruebas/23b-mongo-read-only.md` — mongo_indexes.py --explain, run_analisis_mongo.py --mediana, 26,61%.
- ✅ Patch `03-La-arquitectura/11-que-hace-cada-pipeline.md` — separado "11 pipelines de orquestación" vs "11 pipelines de agregación Mongo".

### P2
- ✅ Nueva `00-trazabilidad-claims-a-repo.md` — mapa afirmación defensa → fichero:línea.
- ✅ Auditoría `07-Ensayo/27-flashcards.md` y `28-treinta-preguntas.md` — sin referencias a 759 (eliminadas), usan 594.

## Artefactos creados

### Nuevas notas (5)
| Archivo | Líneas | Mermaid inline | .mmd gemelo | Flashcards |
|---|---:|---|---|---|
| `04-El-modelo/16b-explain-antes-despues.md` | 91 | 1 | `visuals/explain-antes-despues.mmd` | 1 sección |
| `03-La-arquitectura/15b-pipelines-mongo-11.md` | 96 | 1 | `visuals/pipelines-mongo-11.mmd` | 1 sección |
| `04-El-modelo/19-indices-2dsphere-y-geo.md` | 83 | 1 | `visuals/indices-2dsphere-y-geo.mmd` | 1 sección |
| `06-Las-pruebas/23b-mongo-read-only.md` | 90 | 1 | `visuals/mongo-read-only.mmd` | 1 sección |
| `00-trazabilidad-claims-a-repo.md` | 79 | 1 | `visuals/trazabilidad-claims-a-repo.mmd` | 1 sección |

### Visuals nuevos (5 .mmd)
- `visuals/explain-antes-despues.mmd`
- `visuals/pipelines-mongo-11.mmd`
- `visuals/indices-2dsphere-y-geo.mmd`
- `visuals/mongo-read-only.mmd`
- `visuals/trazabilidad-claims-a-repo.mmd`

Total visuals: 13 .mmd (8 originales + 5 nuevos).

### Notas parcheadas (5)
- `15-aggregation-pipelines.md` — $median → winsorizada p1–p99 (15 menciones de "winsor")
- `16-indices-esr-y-explain.md` — comando válido + before/after (12 menciones COLLSCAN/IXSCAN)
- `18-consultas-utiles.md` — winsorizada (2 menciones)
- `11-que-hace-cada-pipeline.md` — orquestación vs agregación (2 menciones)
- `27-flashcards.md` y `28-treinta-preguntas.md` — 0 referencias a 759 (limpiadas)

## Verificación realizada (parcial)

El subagente ejecutó checks de consistencia mermaid inline vs .mmd:
- ✅ `16b-explain-antes-despues.md` inline == `explain-antes-despues.mmd` (verificado manualmente tras la interrupción).
- ✅ `15-aggregation-pipelines.md` inline == `aggregation-pipelines.mmd` (verificado en transcript: "BLOCK matches mmd").
- ⚠️ Se encontró un mismatch en `16b` durante la sesión (BLOCK2 matches mmd: False) que el subagente corrigió con un patch (16-indices-esr-y-explain.md mermaid actualizado) y reescritura del .mmd.
- ⚠️ Los checks de las otras 3 notas nuevas (15b, 19, 23b, 00-trazabilidad) no se completaron por la interrupción.

## Lo que falta (pendiente de verificación)

1. **Verificar consistencia mermaid inline vs .mmd** para las 4 notas restantes (15b, 19, 23b, 00-trazabilidad) y las 5 notas parcheadas (15, 16, 18, 11, 27, 28).
2. **Verificar enlaces wikilink** — cada `[[...]]` debe apuntar a un archivo existente.
3. **Verificar frontmatter YAML** válido en todas las notas nuevas.
4. **Verificar flashcards** — formato `<pregunta>? :: <respuesta>.` bajo `## Flashcards #flashcards`.
5. **Verificar archivos vacíos** — ninguno debe tener 0 bytes.
6. **Auditar 27-flashcards y 28-treinta-preguntas** — confirmar que no quedan cifras históricas (759, 68) y que las preguntas reflejan las cifras canónicas (594, 1).
7. **Verificar que no se crearon archivos prohibidos** — no `index.md`, `Home.md`, `README.md`, ni carpetas `notas/`, `entidades/`, `comparaciones/`, `flashcards/`, `visuales/`.

## Notas

- El vault es gitignored (`vaultVivienda/` en `.gitignore:64`), por lo que estos cambios no están en git ni se pushearán.
- No se modificó código ni Mongo. Solo vault.
- El subagente siguió el estilo pedagógico TeachMe (verdades incondicionales, camino motivado, mermaid, flashcards, frontmatter Obsidian).
- Las cifras canónicas (594, 252, 204/126/50/39, 28+8 PNG, 8 CSV, 24 índices) se usaron consistentemente.

## Cómo reanudar

1. Lanzar un subagente de verificación (read-only) que ejecute el checklist de arriba.
2. Corregir cualquier mismatch mermaid inline vs .mmd.
3. Corregir enlaces rotos o flashcards mal formateadas.
4. Marcar como completo cuando el checklist pase al 100%.
