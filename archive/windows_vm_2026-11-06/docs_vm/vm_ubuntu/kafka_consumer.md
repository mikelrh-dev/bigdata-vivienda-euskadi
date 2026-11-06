# Consumidor Kafka de la VM (`hdfs_vm`)

**Estado:** vivo como proceso efímero (heredoc). **No existe `.py` en la VM ni en el repo.**

## Comando actual

```bash
cd ~/bigdata_hdfs_vm && python3 - <<'PY'
import json
from kafka import KafkaConsumer

cons = KafkaConsumer(
    'anuncios_inmobiliarios',
    bootstrap_servers='192.168.201.162:9094',
    group_id='hdfs_vm',
    auto_offset_reset='earliest',
    enable_auto_commit=False,
)
n = 0
for msg in cons:
    m = json.loads(msg.value.decode())
    if m.get('type') == 'raw_manifest':
        n += 1
        cons.commit()
        if n % 50 == 0:
            print(f'manifests consumidos {n}')
print(f'TOTAL_MANIFESTS {n}')
cons.close()
PY
```

## Qué hace

- Lee el topic `anuncios_inmobiliarios` desde `192.168.201.162:9094`.
- Grupo `hdfs_vm`, `auto_offset_reset='earliest'`, `enable_auto_commit=False`.
- Descarta mensajes sin `type == "raw_manifest"`.
- Hace `commit()` por cada manifiesto.
- Cuenta y reporta cada 50.

## Qué NO hace

- No sube a HDFS.
- No valida `rel`, `size` ni `sha256`.
- No llama al uploader.
- No deduplica.

## Evidencia

- Proceso vivo (pid 11710 al verificar), lanzado desde `~/bigdata_hdfs_vm`.
- 362 mensajes; offsets 124/121/117; **LAG 0**.
- El grupo queda en `hdfs_vm`.

## Qué falta

1. Moverlo a `storage/kafka_consumer_vm.py` (versionado).
2. Validar `rel` con `is_valid_rel`, `size` y `sha256` con `verify_staging`.
3. Llamar a `upload_raw_excluding_legacy` con `raw_dir=~/staging/raw` y `state_dir`.
4. Abortar si un SHA no cuadra.

## Referencias

- [`flujo_raw_windows_vm_hdfs.md`](flujo_raw_windows_vm_hdfs.md)
- `storage/kafka_raw_producer.py` (productor Windows)
