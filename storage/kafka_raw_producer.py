"""Productor Kafka de manifiesto raw (Window -> VM -> Hadoop).

Por cada fichero de data/raw sin legacy publica un JSON
{type: raw_manifest, rel, size, sha256} con clave rel. Los bytes
viajan por scp a ~/staging/raw en la VM; Kafka orquesta.
vm design: 2026-11-06-hdfs-windows-vm-kafka.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW_DIR = ROOT / "data" / "raw"
DEFAULT_BOOTSTRAP_SERVERS = "192.168.201.162:9094"
DEFAULT_TOPIC = "anuncios_inmobiliarios"


def get_bootstrap_servers() -> str:
    return os.getenv("KAFKA_BOOTSTRAP_SERVERS") or DEFAULT_BOOTSTRAP_SERVERS


def get_topic() -> str:
    return os.getenv("KAFKA_TOPIC") or DEFAULT_TOPIC


def iter_raw_files(raw_dir: Path | str | None = None) -> list[Path]:
    src = Path(raw_dir) if raw_dir is not None else DEFAULT_RAW_DIR
    return sorted(p for p in src.rglob("*") if p.is_file() and "legacy_obsoleto_no_usar" not in p.parts)


def manifest_entry(path: Path, raw_dir: Path | str | None = None) -> dict:
    src = Path(raw_dir) if raw_dir is not None else DEFAULT_RAW_DIR
    rel = path.relative_to(src).as_posix()
    data = path.read_bytes()
    return {"type": "raw_manifest", "rel": rel, "size": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def produce(limit: int | None = None, topic: str | None = None, bootstrap_servers: str | None = None, producer=None) -> int:
    files = iter_raw_files()
    if limit is not None:
        files = files[:limit]
    own = producer is None
    if own:
        from kafka import KafkaProducer

        producer = KafkaProducer(bootstrap_servers=bootstrap_servers or get_bootstrap_servers())
    try:
        for p in files:
            m = manifest_entry(p)
            key = m["rel"].encode("utf-8")
            value = json.dumps(m, ensure_ascii=False).encode("utf-8")
            fut = producer.send(topic or get_topic(), key=key, value=value)
            fut.add_callback(lambda meta: print(f"Publicado {meta.topic}:{meta.partition}@{meta.offset}"))
            fut.add_errback(lambda e: print(f"Error publicar raw: {e}"))
        producer.flush()
    finally:
        if own:
            producer.close()
    print(f"ADAPTER_RAW_PUBLICADOS {len(files)} en {topic or get_topic()}")
    return len(files)


if __name__ == "__main__":
    import sys

    lim = int(sys.argv[1]) if len(sys.argv) > 1 else None
    produce(limit=lim)
