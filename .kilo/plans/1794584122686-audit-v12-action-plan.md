# Plan de acción tras auditoría v12 (2026-11-13)

## Conclusiones clave

| Bloque | Estado | Nota |
|--------|--------|------|
| **SBD (RA1+RA3+RA4)** | ✅ Impecable | 150/150 (100%) |
| **Tema 8** | ✅ Muy fuerte | 9,40/10 |
| **BDA RA1** | ⚠️ 2 criterios en 7 | 34/40 (C2 y C4) |
| **Defensa/relato** | ❌ Desalineado | Conteos HDFS falsos, deck dice que HDFS/Kafka fallan cuando funcionan |

**Total bruto: 184/190 (96,8%)** → Con waivers escritos: **190/190 (100%)**

---

## Acciones priorizadas (P1 = bloquean defensa)

### P1-01: Corregir conteos HDFS/manifiesto en TODOS los documentos
**Archivos afectados:**
- `docs/presentacion_v2/index.html` (líneas 203, 208, 462, 473, 474, 740, 757)
- `README.md` (líneas 119, 126, 152, 258, 274)
- `AGENT.md` (línea 4)
- `scripts/verificar_cifras_deck.py` (líneas 149-150)

**Realidad verificada:**
- 355 SHA = **351 datos + 4 legacy**
- 353 objetos HDFS = **351 datos + .FROZEN + .gitkeep**
- **NO hay ingestion_manifest.json en HDFS**

### P1-02: Actualizar estado vivo HDFS/Kafka en deck y README
- DNS resuelve ✅
- OPEN 3 ficheros con SHA idéntico ✅
- Kafka: 1.058 mensajes, lag 0, 3 pasadas de 353 ✅
- **Eliminar frases "fallan", "DNS falla", "metadata no entrega"**

### P1-03: Formalizar waiver HDFS procesado (escrito)
- Documentar: fecha, canal, autorización profesora
- O subir procesados a HDFS (1h)
- **Impacto: C2 7 → 10**

### P1-04: Gate E2E real (C4 7 → 10)
- `run_pipeline.py --fase all` debe incluir Mongo + análisis
- Gate vivo debe leer HDFS, offsets Kafka, docs Mongo (no solo TCP)
- **Coste: 2-4h**

---

## P2: Incoherencias visibles (30 min cada una)

| Acción | Archivos | Impacto |
|--------|----------|---------|
| Renombrar `n_precio` → `n_precio_ab` o añadir `n_precio_total` | `mongo_esfuerzo_por_municipio.csv`, deck | C17/C18/T7 |
| Añadir `codigo_ine` espejo en colección `municipios` | Migración Mongo + índice | C5 más defendible |
| Corregir README: consumidor usa `overwrite=True`, no descarte por SHA | `README.md:275`, `storage/kafka_hdfs_uploader.py` | P2-03 |
| Verificar/eliminar topic `anuncios_inmobiliarios` (1.420 msg) | `README.md:122,259,275`, `AGENT.md:18` | P2-04 |
| Generar `auditoria_lagunas_silver.csv` faltante | `run_all.py --check` | P2-05 |
| Unificar conteo colecciones: 17 vivas + 15 backup = 32 | `README.md:52,120,311`, `AGENT.md:4` | P2-06 |
| Eliminar referencia Docker en `openspec/config.yaml:11` | `openspec/config.yaml` | P2-07 |
| Fix `verificar_cifras_deck.py`: validar manifiesto real, no `len(*.csv)+len(*.png)` | `verificar_cifras_deck.py` | P2-08 |

---

## P3: Deuda técnica (opcional, post-defensa)

- Quitar `@lru_cache` de `get_client()` o corregir docstring `get_mongo_uri()`
- Fix assert tautológico `tests/test_mongo.py:132`
- `verificar_gobernanza.py`: no hardcodear 47 scripts / 40 nodos
- Gate offline: esperar 17 colecciones vivas, no 15
- CI: tests contra Mongo real, no `mongomock`
- `run_analisis_mongo.main()`: no devolver 0 si fallan exports
- Commit local antes de defender

---

## Checklist de defensa (mínimo viable)

- [ ] Conteos 351/355/353 corregidos en deck, README, AGENT, verificador
- [ ] Deck actualizado: HDFS/Kafka funcionan, 1.058/lag 0
- [ ] Waiver HDFS procesado escrito (PDF/firma/fecha) O procesados subidos
- [ ] `run_pipeline.py --fase all` incluye Mongo (o waiver C4 documentado)
- [ ] `n_precio` desambiguado en deck y CSV
- [ ] `codigo_ine` espejo en `municipios` (migración + índice)
- [ ] `auditoria_lagunas_silver.csv` generado
- [ ] Colecciones: 17+15=32 unificado en todos los docs
- [ ] Commit local con todos los cambios