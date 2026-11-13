# C2 · Almacenamiento HDFS — por qué hoy no llega a 10

**Fecha:** 2026-11-12 · **HEAD:** `b29c6ac` (6 ficheros modificados sin commit)
**Criterio:** BDA RA1 · *Almacenamiento HDFS* · 10 puntos
**Naturaleza:** solo lectura. No se modificó código, `data/`, Mongo, HDFS ni Kafka. Este documento **no** aplica arreglos: fija el motivo de la nota y la lista de errores pendientes.

---

## 1. La rúbrica, literal

Transcripción del PDF (`openspec/audit/evidencia/2026-11-07/rubrica_pdf.txt`, líneas 76-82):

| 0 puntos | 3 puntos | 7 puntos | **10 puntos** |
|---|---|---|---|
| No almacena datos | Crea directorios | Guarda y recupera archivos | **Organiza originales y procesados y demuestra su recuperación** |

La escala es acumulativa y el 10 añade **tres** exigencias sobre el 7: organizar *originales*, organizar *procesados* y **demostrar** la recuperación.

---

## 2. Traducción a condiciones comprobables

| # | Condición que exige el 10 | Evidencia que la acreditaría | Estado hoy |
|---|---|---|---|
| K1 | Organiza los **originales** | Inventario de HDFS con rutas separadas y recuento estable | ✅ `GETCONTENTSUMMARY /data/raw` = **353 ficheros / 895.597.901 B**, 6 directorios |
| K2 | Organiza los **procesados** | Ruta propia en HDFS **o** excepción declarada y atribuible | ⚠️ Excepción declarada, **sin fecha ni canal** (§5) |
| K3 | **Demuestra** la recuperación | Ejecución real con salida `rc 0` y SHA iguales, guardada como evidencia | ❌ `rc 2` hoy (§3) |
| K4 | **Recupera** (restaura) el fichero | El script materializa el fichero recuperado | ❌ El script solo coteja; no escribe (§4) |

Con K1 ✅, K2 ⚠️, K3 ❌ y K4 ❌, lo acreditado hoy es el escalón **7 («Guarda y recupera archivos»)**. Por eso C2 = **7**, no 10.

> Nota: el waiver de procesados **no** es la causa de la nota. Es una decisión legítima y ya está razonada en `README.md:108` y en el spec (`openspec/specs/almacenamiento-y-streaming/spec.md:35-40`, originales `SHALL` / procesados `SHOULD`). Lo que falta es demostrar y restaurar.

---

## 3. Motivo bloqueante 1 — hoy no se puede demostrar (externo al código)

| Comprobación | Resultado |
|---|---|
| `GETCONTENTSUMMARY /data/raw` por IP | ✅ 353 ficheros, 895.597.901 B |
| `LISTSTATUS /data` | ✅ solo `raw` |
| `GETFILESTATUS` de un fichero concreto | ✅ responde el NameNode |
| `OPEN` (lectura del contenido) | ❌ redirige a `hadoop-worker1/2.tartangalh.eus:50075` |
| `socket.gethostbyname` de `hadoop-master1/worker1/worker2.tartangalh.eus` | ❌ `gaierror [Errno 11001]` |
| `scripts/hdfs_recuperacion_un_fichero.py` | ❌ **rc 2** para el fichero por defecto y para `udalmap_vpo_terminadas.csv` |

El NameNode está sano y el código del script es correcto: **falla la resolución del nombre del datanode** al que WebHDFS redirige la lectura. Mientras eso no se resuelva (hosts del aula, DNS del centro o descarga contra la IP del datanode), K3 es indemostrable en vivo.

---

## 4. Motivo bloqueante 2 — el script coteja, no recupera (interno al código)

`scripts/hdfs_recuperacion_un_fichero.py` es un verificador de integridad, no un recuperador. Dos hechos del propio código:

1. **Sin copia local no hay recuperación.** Antes de tocar HDFS:
   ```python
   # scripts/hdfs_recuperacion_un_fichero.py:86-89
   if not local.is_file():
       info["error"] = "LOCAL_NO_EXISTE"
       info["local"] = str(local)
       return 1, info
   ```
   Si el fichero local se ha perdido —el escenario exacto de una recuperación— el script sale con `rc 1` **sin consultar HDFS**. No puede reconstruir nada.

2. **Descarga a memoria y compara; nunca escribe.** No existe opción de destino:
   ```python
   # scripts/hdfs_recuperacion_un_fichero.py:100-101
   with client.read(info["hdfs_path"]) as reader:
       remote = cast(BinaryIO, reader).read()
   ```
   La salida `HDFS_REC OK SHA_TAMANO_IGUALES` significa «la copia de HDFS coincide con la mía», no «he recuperado el fichero».

Consecuencia: aun con el DNS arreglado, el script acredita el escalón 7 y no el 10, porque el 10 pide *demostrar su recuperación* y esto demuestra *igualdad*. La simplicidad del `.py` no resta; la ausencia de restauración sí.

---

## 5. Motivo argumentativo — la excepción de procesados no está fechada

`README.md:108` afirma «los `procesado` **no** se suben por indicación expresa de la profesora», pero **no consta cuándo ni por qué canal** se autorizó. `openspec/specs/almacenamiento-y-streaming/spec.md:39-40` lo rebaja a `SHOULD`, lo que es coherente, pero un waiver sin fecha ni soporte es discutible ante el tribunal: es la pieza que convierte K2 de ⚠️ en ✅.

---

## 6. Errores potenciales (no bloquean la nota, sí la defensa)

| ID | Sev. | Qué | Dónde | Efecto | Arreglo |
|---|---|---|---|---|---|
| E-1 | P2 | El fichero completo se carga en RAM; el mayor raw pesa **118,8 MB** (`certificados_energeticos_bizkaia_completo.csv`) | `:100-101` | Contradice el hashing en streaming que el vault atribuye al proyecto; fragilidad en portátiles del aula | Hashear por bloques (`chunk`) y no retener el `bytes` salvo en modo `--out` |
| E-2 | P2 | `--timeout` por defecto **10 s** | `:37`, `:126` | Es *read timeout* por petición, no total: si la red se atasca >10 s entre bloques, aborta con `rc 2` y se confunde con un fallo del script | Subir el defecto (30-60 s) o exponerlo en la ayuda como read-timeout |
| E-3 | P2 | `status.length` se guarda pero **no se compara ni se imprime** | `:114` vs salida en `:133-145` | La rúbrica habla de «tamaño en bytes»; ese es el dato que acreditaría `FileStatus` frente al local y no aparece | Comparar `remote_status_length` con `local_size` y sacarlo en pantalla |
| E-4 | P3 | `except Exception` etiqueta **cualquier** fallo como `HDFS_NO_ALCANZABLE` | `:102` | Un `TypeError` o una ruta mal formada se reporta como red caída y desvía el diagnóstico en plena demo | Capturar `HdfsError`/`OSError`/`requests` y dejar propagar el resto |
| E-5 | P3 | `test_main_devuelve_2_sin_red` **asserta `code == 1`** y no hay caso `rc 0` por CLI | `tests/test_hdfs_recuperacion.py:87-91` | Nombre engañoso; el camino feliz solo se prueba en `recuperar()`, no en `main()` | Renombrar y añadir un test de CLI con `--out`/doble que devuelva 0 |
| E-6 | P2 | El vault afirma cosas que el código no hace: «valida el SHA remoto contra el local **antes de restaurarlo**» y «lectura streaming del hash remoto **sin cargar el archivo completo en memoria**» | `vaultVivienda/notebooklm/NB02-infraestructura-y-gate.md:66` | Respuesta incorrecta lista para salir si alguien pregunta por C2 | Corregir el vault o implementar E-1 + `--out` |
| E-7 | P3 | El deck dice «**352** canónicos» | `docs/presentacion_v2/index.html:491` | Contradice los 353 verificados hoy y el propio `README.md:108` | Actualizar a 353 |

---

## 7. Qué falta exactamente para el 10

| # | Cambio | Criterio de aceptación |
|---|---|---|
| 1 | Modo `--out DIR` en el script: descarga, escribe el fichero en el destino y **recalcula SHA** contra el remoto | `--out` produce un fichero byte a byte igual; sigue siendo solo lectura sobre HDFS y no toca `data/raw` |
| 2 | Comparar e imprimir `FileStatus.length` frente al tamaño local y al descargado | La salida muestra los tres tamaños y los dos SHA |
| 3 | Corrida real `rc 0` contra el centro y JSON de evidencia fechado | `openspec/audit/<fecha>/evidencia/` con `FICHERO / HDFS_PATH / LOCAL_SIZE SHA / REMOTE_SIZE SHA / HDFS_REC OK` |
| 4 | Fecha y canal de la autorización de la profesora | Una línea en `README.md:108` y en el spec con la fecha y el medio |
| 5 | Arreglos E-1 a E-7 | Suite verde y vault sin afirmaciones falsas |

Los puntos 1 y 2 son código; el 3 depende de resolver el DNS del datanode; el 4 es documentación; el 5 son correcciones menores.

---

## 8. Alcance

- **No** se ejecutó `load_all`/`clean_all`, **no** se produjo ni consumió Kafka, **no** se escribió en Mongo/HDFS, **no** se tocó `data/`.
- Los hechos de HDFS citados en §3 son de esta sesión (2026-11-12); la evidencia v8 (`openspec/audit/v8_2026-11-09/evidencia/vivo/hdfs.json`) es un inventario de `FileStatus`, **no** una recuperación, y no se usa aquí como prueba de K3.
- La puntuación C2 = 7 está razonada en `openspec/audit/v11_2026-11-12/auditoria_completa_v11.md`; este documento solo la desglosa.
