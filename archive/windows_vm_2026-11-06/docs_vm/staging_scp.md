# staging_scp — copia data/raw a la VM (~/staging/raw)

**Fecha:** 2026-11-06
**Script:** `scripts/staging_scp.py` (Windows, `subprocess`, sin dependencias nuevas)
**VM:** `mikel@192.168.201.162` · clave `C:/Users/mikel/.ssh/id_vm_hermes`
**Origen:** `data/raw/` · **Destino:** `~/staging/raw/` en la VM
**Relacionado:** [`flujo_raw_windows_vm_hdfs.md`](ubuntu/flujo_raw_windows_vm_hdfs.md) ·
[`00_verificacion.md`](ubuntu/00_verificacion.md) · `storage/kafka_raw_producer.py`

## 1. Objetivo

Transferir los **bytes** de `data/raw/` a `~/staging/raw/` en la VM para
que el uploader VM→HDFS (`kafka_hdfs_uploader.py`) los suba a
`/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw`.

Kafka **no** lleva los bytes (solo manifiestos); `scp` lleva el contenido.
Ver §4.

El script:

- cuenta ficheros/bytes locales antes de copiar,
- lee conteo/bytes remotos antes y después **solo en modo real** (SSH
  solo lectura, `python3` remoto),
- ejecuta `scp -r` con `BatchMode` (nunca pide password),
- aborta si el conteo/bytes remoto final no coincide con el local,
- nunca borra nada en local ni en remoto.

En `--dry-run` no toca la VM: ni `scp` ni `ssh`.

## 2. Comando exacto

Desde la raíz del repo, en Windows (PowerShell o Git-Bash):

### 2.1 Dry-run (no copia, no llama a subprocess)

```bash
.venv/Scripts/python.exe scripts/staging_scp.py --dry-run
```

Opciones explícitas (mismos valores por defecto):

```bash
.venv/Scripts/python.exe scripts/staging_scp.py --dry-run \
  --src data/raw \
  --host 192.168.201.162 \
  --user mikel \
  --key C:/Users/mikel/.ssh/id_vm_hermes \
  --remote-dir ~/staging/raw
```

### 2.2 Copia real

```bash
.venv/Scripts/python.exe scripts/staging_scp.py
```

El `scp` interno es (list-form vía `subprocess`, sin shell):

```text
scp -i C:/Users/mikel/.ssh/id_vm_hermes -o BatchMode=yes -r <src>/ mikel@192.168.201.162:~/staging/raw/
```

La verificación remota es (solo lectura):

```text
ssh -i C:/Users/mikel/.ssh/id_vm_hermes -o BatchMode=yes mikel@192.168.201.162 "python3 -c ..."
```

con el `python3` remoto contando ficheros y sumando `st_size` bajo
`~/staging/raw` e imprimiendo `"<n> <bytes>"`.

## 3. Salida esperada

### 3.1 Dry-run (verificado el 2026-11-06)

```text
STAGING_LOCAL n=356 bytes=901772304 src=C:/Users/mikel/Documents/bigdata-vivienda-euskadi/data/raw
SCP_CMD scp -i C:/Users/mikel/.ssh/id_vm_hermes -o BatchMode=yes -r C:/Users/mikel/Documents/bigdata-vivienda-euskadi/data/raw/ mikel@192.168.201.162:~/staging/raw/
STAGING_REMOTE_BEFORE SKIPPED (dry-run, cero llamadas)
DRY_RUN_OK CERO_COPIAS NO_COPIADO
```

- `STAGING_LOCAL n=356` (incluye `.FROZEN` y `.gitkeep`, 0 B).
- `bytes=901772304` (~859,8 MiB).
- `STAGING_REMOTE_BEFORE SKIPPED` prueba que no hubo SSH.
- `DRY_RUN_OK` + exit `0` = nada copiado.

### 3.2 Copia real

```text
STAGING_LOCAL n=356 bytes=901772304 src=...
SCP_CMD scp -i C:/Users/mikel/.ssh/id_vm_hermes -o BatchMode=yes -r ... mikel@192.168.201.162:~/staging/raw/
STAGING_REMOTE_BEFORE n=<antes> bytes=<antes>
SCP_CMD scp -i ... ...
SCP_EXIT 0
STAGING_REMOTE_AFTER n=356 bytes=901772304
STAGING_VERIFIED OK
```

Exit code:

| Código | Significado |
|---|---|
| `0` | Copia + verificación OK, o dry-run OK |
| `1` | `scp` falló, o verificación remota falló / no cuadra |
| `2` | No existe `--src` |

Criterio de aceptación real: `STAGING_REMOTE_AFTER` igual a
`STAGING_LOCAL` (`n=356 bytes=901772304`) y `STAGING_VERIFIED OK`.

### 3.3 Tests offline

```bash
.venv/Scripts/python.exe -m pytest tests/test_staging_scp.py -q
```

Salida esperada:

```text
..........                                                               [100%]
10 passed
```

Los tests mockean `subprocess.run` (offline, cero red): dry-run sin
llamadas, comando con `BatchMode=yes` + clave, verificación OK,
fallo de `scp` y mismatch de conteo/bytes.

## 4. Por qué Kafka no puede con ficheros de 114 M (> límite 1 M)

Medido localmente (2026-11-06):

| Fichero | Bytes | MiB |
|---|---|---|
| `certificados_energeticos_bizkaia_completo.csv` | 118 793 174 | 113,3 |
| `distancias_b5m_gipuzkoa.json` | 91 986 422 | 87,7 |
| `certificados_energeticos_gipuzkoa_completo.csv` | 72 961 771 | 69,6 |
| Total `data/raw/` (356 ficheros) | 901 772 304 | 859,8 |

El límite es `max.message.bytes=1048588` (~1 MiB), el `max.message.bytes`
por defecto del broker (grupo `anuncios_inmobiliarios`, `192.168.201.162:9094`):

- 118 793 174 / 1 048 588 ≈ **113×** el límite.
- No cabe en un solo mensaje de Kafka: publicar los bytes daría
  `RecordTooLargeError` / `MessageTooLargeError`.
- Partirlo en trozos (chunking) rompería la semántica atómica del
  manifiesto `{type, rel, size, sha256}`: habría que reensamblar,
  revalidar SHA/bytes y gestionar parcialmente fallidos. Fuera de
  alcance y sin beneficio.

Por eso el flujo es:

```text
Windows storage/kafka_raw_producer.py ──manifiestos {rel,size,sha256}──▶ Kafka
Windows data/raw/ ──────────────────────────bytes────────────────────────▶ VM ~/staging/raw (scp)
VM consumidor ──lee manifiestos y commit──▶ decide QUE subir
VM kafka_hdfs_uploader.py ──WebHDFS put──▶ HDFS .../data/raw
```

Kafka decide **qué** subir y con qué SHA; `scp` lleva el **contenido**.
