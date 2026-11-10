# Pendientes y limitaciones — cierre v9 (2026-11-10)

**Naturaleza:** documentación de residuales. No se modifican código, datos, Mongo, HDFS ni Kafka.
**Alcance:** todo lo detectado en la reauditoría que **no** se corrige en `2026-11-10-defensa-v9-p0`.

---

## 1. Corregido hoy (para no confundirlo con pendiente)

| Punto | Archivo | Cambio |
|---|---|---|
| MongoDB «Docker Desktop» | `openspec/project.md:30` | Ahora: MongoDB local standalone, sin Docker en el repo |
| Flujo `Kafka → MongoDB` | `openspec/project.md:38` | Ahora: Kafka → HDFS; silver → MongoDB local |
| Kafka «VM Ubuntu Server» | `openspec/project.md:29` | Ahora: clúster centro `10.22.87.215:9092` |
| HDFS/Kafka como disponibles | `docs/guion_defensa.md:5` | Ahora: evidencia histórica v8 y aviso de que hoy el centro no es alcanzable |
| Comandos a scripts borrados | `data/resultados/README.md:127-133` | Retirados los dos generadores DuckDB; nota de que los HTML son estáticos (fichero local ignorado por git: el arreglo no se versiona) |

---

## 2. Pendientes de proceso o cobertura (no rompen hoy)

| ID | Hallazgo | Severidad | Qué lo dispara | Riesgo actual | Recomendación |
|---|---|---|---|---|---|
| **H-08** | `extract/26_vpo_terminadas.py` promueve un raw nuevo sin regenerar `_meta/ingestion_manifest.json` | P2 | Una extracción futura con fuente cambiada (`--promote`) | Ninguno: el raw actual está congelado y su SHA está verificado | Tras un `--promote` con `escrito=True`, ejecutar `extract/generar_ingestion_manifest.py`; el check 17 de `verificar_fase_datos.py` lo detectaría |
| **H-09** | `docs/contrato_datos_raw.md` y `transform/_raw_guard.py` discrepan sobre `.FROZEN` | P2 | Lectura del contrato de datos | Ninguno en ejecución; el guard funciona | Alinear el contrato con `.FROZEN` o documentar la excepción |
| **H-10** | `validar()` del VPO no comprueba pertenencia a `dim_municipios` | P3 | Reextracción con entidades disueltas | Ninguno: el parser filtra a 252 y el join descarta el resto | Añadir el join a `dim_municipios` si se reextrae |
| **HM-06** | `anuncios_habitaciones_unificados` y `_bigdata` duplican 201 `_id` | P3 | Que una de las dos se actualice y la otra no | Bajo: `_hab_col()` prefiere `_bigdata` si tiene docs; hoy ambas tienen 201 y el resultado es determinista | Elegir la canónica, retirar la otra y dejar una sola ruta en `_hab_col()` |
| **DS2-25** | La huella de los 11 pipelines no está registrada en el repo | P3 | Auditoría de reproducibilidad | Ninguno: la huella se imprime al ejecutar, pero no queda versionada | Ejecutar `run_analisis_mongo.py` en lectura y guardar la huella en `docs/` o en el audit |
| **R-4** | `test_mongo_geo.py` ya no asertan el geo real de prod (424/594) | P3 | Regresión del geo sin test que la detecte | Bajo: la sonda read-only lo verificó y está documentado | Añadir una lectura read-only del geo al gate offline (sin escribir en prod) |

---

## 3. Documentación histórica que se deja como está

| Documento | Contenido | Por qué se deja |
|---|---|---|
| `docs/auditoria_10_10_SDD_2026-11-05.md` | `TOTAL 759`, `totalDocsExamined=759`, `6 CSV` | Es un acta fechada del 2026-11-05; reescribirla falsearía el histórico |
| `docs/analisis_vault_vs_rubrica.md:4,24` | `759 anuncios, 151 tests, 9 pipelines`; aritmética del vault | Describe el documento del vault auditado, no el estado vigente |
| `docs/trazabilidad_vm.md` | 759, topic `anuncios_inmobiliarios`, VM legacy | Traza de la VM previa al 2026-11-06; histórico |
| `docs/archive/**` | Cifras y scripts antiguos | Archivo inmutable |
| `vaultVivienda/vault-tecnico/**` | Referencias a `generar_dashboard_*` y `auditoria_duckdb.py` | Notas de Obsidian; no son documentación operativa del repo |

---

## 4. Fallo conocido que se mantiene visible

**FAIL 07 de `scripts/verificar_fase_datos.py` (exit 1):** paro-cero con tasa no nula en Aramaio 0,28 / Gaintza 1,45 / Usansolo 3,26. Es un dato real de Lanbide/INE; se muestra sin imputar ni enmascarar. No lo ejecuta el CI ni bloquea la suite, el gate offline ni la gobernanza. **No se corrige a propósito**: tocar el dato para forzar el verde sería peor que el rojo.

---

## 5. Límites de la verificación

- **HDFS/Kafka no revalidados en vivo:** el usuario no está en el centro. La evidencia es el histórico v8 y el gate offline (`PENDA-01`). No es un fallo del proyecto.
- **CI no ejecutado en Ubuntu:** se inspeccionó el workflow; los tests de Mongo llevan `skipif(not ping())` y el CI no invoca `verificar_fase_datos.py`. La primera ejecución real en GitHub es la validación pendiente.
- **`clean_all()` (HM-03) no ejecutado:** solo con autorización; los pipelines no dependen de los flags.
