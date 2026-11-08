# Empieza aquí — estado de la auditoría v6

**Para retomar el 2026-11-09.** La auditoría está **cerrada** y el plan de solución **redactado**, pero **no se ha aplicado ningún cambio**. Todo lo escrito vive en `openspec/audit/`; `data/`, código, Mongo, HDFS y Kafka siguen intactos.

---

## 1. Qué leer, en este orden

| Orden | Documento | Para qué |
|---:|---|---|
| 1 | `informe_auditoria_v6_2026-11-08.md` | Veredicto, 18 dominios, rúbrica, límites |
| 2 | `hallazgos_v6_2026-11-08.csv` | Los 19 hallazgos (4 P1 / 9 P2 / 6 P3) con evidencia |
| 3 | `plan_solucion_v6_2026-11-08.md` | Qué hacer, en qué orden y con qué aceptación |
| 4 | `analisis_beneficio_riesgo_v6_2026-11-08.md` | Beneficio y riesgo de cada implementación |
| 5 | `evidencia/2026-11-08/` | Logs crudos por si hay que rebatir una cifra |

> `plan_auditoria_v5_2026-11-07.md`, `informe_auditoria_v5_2026-11-07.md` y anteriores son **histórico**, no estado vigente.

---

## 2. Estado en una tabla

| Hecho | Valor |
|---|---:|
| Commit base | `3171d5a906062f5bb85ab2e0c0423af604979a6a` (`master`) |
| Árbol | 3 `M` + 23 `??` (los `??` incluyen estos documentos) |
| Tests | **242 colectados · 240 passed · 2 skipped** |
| Gate offline | **OK** (354 raw / 188 silver / 14 declaradas / 0 duplicados / lag 0) |
| `run_all.py --check` | **exit 1** (staleness de `normalizar_json_crudos.py`) |
| `verificar_fase_datos.py` | **exit 1 / PENDIENTE** (FAIL 07 paro-cero) |
| `verificar_gobernanza.py` | **exit 1** (46/45 requisitos, 45/44 scripts, 11/10 pipelines) |
| Mongo | **16 vivas + 14 backups = 30**; 594 anuncios; 252 municipios |
| Resultados | 17 CSV (8 `mongo_*`), 28 PNG + 8 anexo |

**Veredicto: APTO CON RESERVAS.** No hay P0. Los P1 son de documentación y de dos gates automatizados, no de integridad.

---

## 3. Mañana, en este orden

### Paso 0 — Decidir (15 min)

| # | Decisión | Recomendación |
|---|---|---|
| D1 | Cifra canónica de colecciones | **14 de negocio + 2 habitaciones + 14 backups** |
| D2 | Paro-cero (Aramaio 0,28 / Gaintza 1,45 / Usansolo 3,26) | **Recalcular** desde paro/activos; si falta denominador → waiver documentado |
| D3 | Resultados en git | **Sí los 17 CSV**, no los PNG (manifiesto SHA aparte) |

Sin D2 no se toca `data/procesado`; es la única decisión que puede cambiar cifras.

### Paso 1 — Quick wins sin datos (1 h)

- Rama: `git switch -c fix/auditoria-v6`.
- Baseline: `git rev-parse HEAD`, `git diff | sha256sum`, `git ls-files -s | sha256sum`.
- Tabla canónica única + IDs `CHART-*` + guardián 50/45/34/11.
- `[TEMPLATE]` en `.env.example`.

### Paso 2 — P1 con control (3–5 h)

1. **S3** rerun del normalizador con copia, hashes y restauración de `mtime` de los no cambiados.
2. **S4** recalcular paro (o S4b con fuente oficial).
3. Una sola pasada de la cadena afectada.
4. **S2** sustituciones en README/AGENT/arquitectura/guion/spec.
5. Verificar `run_all --check` y `verificar_fase_datos` en verde.

**Parada:** si S3 cambia más de 2 ficheros o la cadena supera ~5 scripts, o S4 toca el top-4, no seguir; dejar `CUMPLE CON SALVEDAD` con evidencia.

### Paso 3 — Automatización (2 h)

- CI a `master` y prueba en clon limpio.
- Ajustar `test_pisos_ubicacion_real.py` **antes** de versionar CSV (hoy exige `pngs and csvs`; en CI no hay PNG).
- Commit de CSV canónicos + manifiesto SHA.

### Paso 4 — Después de la defensa

- Archivar la colección legacy de habitaciones (comparar contenido, no solo count).
- Framework archivado, enlaces, `except Exception`.

---

## 4. Requiere autorización expresa

| Acción | Por qué |
|---|---|
| Escribir en `data/procesado` (S3/S4) | Regenera silver; hay copia y hashes, pero cambia mtimes |
| Renombrar/archivar `anuncios_habitaciones_unificados_bigdata` | Toca Mongo; solo tras comparar los 201 documentos |
| Commitear `data/resultados/*.csv` | Cambia qué entra en git y el comportamiento del test |
| Cualquier `git push` | No se ha publicado nada |

---

## 5. Qué no hacer

- No volver a 759 anuncios ni a 14 colecciones “para que cuadre” con documentos viejos.
- No convertir el FAIL 07 en PASS cambiando el umbral.
- No ejecutar el DAG completo la víspera de la defensa.
- No `drop` de backups ni `git reset --hard`.
- No commitear `data/raw` (inmutable) ni `.env`/`api.txt`.

---

## 6. Comandos de verificación (copiar y pegar)

```bash
# Baseline
git rev-parse HEAD && git status --porcelain
git diff | sha256sum && git ls-files -s | sha256sum

# Suite (sin -qq)
.venv/Scripts/python.exe -m pytest tests -o addopts="" -q -rs

# Gates
.venv/Scripts/python.exe scripts/gate_extremo_a_extremo.py --offline
.venv/Scripts/python.exe transform/run_all.py --check
.venv/Scripts/python.exe scripts/verificar_fase_datos.py
.venv/Scripts/python.exe scripts/verificar_gobernanza.py
.venv/Scripts/python.exe extract/generar_manifest.py --verify

# Cifras obsoletas (debe salir vacío, salvo citas históricas)
grep -rnE "10 pipelines|759|13 PNG|12 PNG|178 tests|177 passed|14 colecciones|44 scripts|6 CSV" \
  --include=*.md . | grep -v archive | grep -v openspec/audit
```

**GO solo si:** suite verde, gate offline OK, `--check` 0, fase datos `OK 18/18`, gobernanza `TODO OK`, manifest 0 errores y el grep vacío.

---

## 7. Límites que siguen abiertos

- **HDFS/Kafka en vivo:** no verificados (sin acceso al centro); los criterios de infraestructura quedan `N/V`.
- **Tier A/B/C/D:** no re-contado en esta pasada (el CSV de 252 filas existe).
- **13 ficheros >25 MB:** inventariados por tamaño/mtime, sin SHA-256.
- **Mongo:** una sola foto; no hay snapshot antes/después.
- **Tests destructivos:** no ejecutados (`MONGO_ALLOW_DESTRUCTIVE` ausente).

---

## 8. Índice de entregables

| Fichero | Contenido |
|---|---|
| `informe_auditoria_v6_2026-11-08.md` | Informe completo |
| `hallazgos_v6_2026-11-08.csv` | 19 hallazgos |
| `plan_solucion_v6_2026-11-08.md` | Plan S1–S10 + P3 |
| `analisis_beneficio_riesgo_v6_2026-11-08.md` | Beneficio/riesgo por implementación |
| `plan_auditoria_v6_2026-11-08.md` | Plan de la auditoría aplicado |
| `evidencia/2026-11-08/` | 12 logs + inventario de 1416 ficheros |

*Nada de esto está commiteado: son 4 documentos y una carpeta de evidencia sin trackear.*
