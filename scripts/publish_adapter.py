"""Adapter versionado de publicación Kafka (Bloque 2, paso 6).

Reproduce de forma determinista la publicación que en scratch publicó
759 y el gate de 10, sin código fuera del repo.

Uso:
    .venv/Scripts/python.exe scripts/publish_adapter.py
    .venv/Scripts/python.exe scripts/publish_adapter.py 10
    .venv/Scripts/python.exe scripts/publish_adapter.py --limit 10

Sin límite publica los 759 vía storage.kafka_producer.produce()
(Future.add_callback/add_errback, kafka-python 2.2.3). Con límite publica
el subset determinista de los N primeros ordenados por (portal,
id_anuncio), con la misma metadata topic/partition/offset.

Sin --dry-run no hace nada más: es escritura en Kafka (permitida) y
lectura local del CSV; no toca data/raw ni HDFS.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from storage.kafka_producer import (  # noqa: E402
    _on_send_error,
    _on_send_success,
    get_bootstrap_servers,
    get_topic,
    produce,
    read_anuncios,
    serialize_anuncio,
)


def _publish_subset(limit: int) -> int:
    from kafka import KafkaProducer

    anuncios = read_anuncios()
    subset = sorted(
        anuncios, key=lambda a: (str(a.get("portal")), str(a.get("id_anuncio")))
    )[:limit]
    print(f"SUBSET {len(subset)}")
    for a in subset:
        print(
            f"  {a.get('portal')}:{a.get('id_anuncio')} "
            f"codigo_ine={a.get('codigo_ine')} municipio={a.get('municipio')}"
        )
    topic = get_topic()
    producer = KafkaProducer(bootstrap_servers=get_bootstrap_servers())
    try:
        for anuncio in subset:
            key, value = serialize_anuncio(anuncio)
            future = producer.send(topic, key=key, value=value)
            future.add_callback(_on_send_success)
            future.add_errback(_on_send_error)
        producer.flush()
    finally:
        producer.close()
    print(f"ADAPTER_PUBLICADOS {len(subset)} en {topic}")
    return len(subset)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "limit_pos",
        nargs="?",
        type=int,
        default=None,
        help="N del subset determinista (compat. posicional).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="N del subset determinista (primeros N por portal,id_anuncio).",
    )
    args = parser.parse_args(argv)
    limit = args.limit if args.limit is not None else args.limit_pos
    if limit is None:
        n = produce()
        print(f"ADAPTER_PUBLICADOS {n}")
        return 0
    if limit <= 0:
        print("LIMIT debe ser positivo")
        return 2
    _publish_subset(limit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
