"""Consumer Windows: consume manifiesto Kafka y sube a HDFS (Windows -> Kafka -> HDFS).

Grupo hdfs_centro, topic anuncios_inmobiliarios, broker centro
10.22.87.215:9092. Descarta mensajes sin type raw_manifest, valida
rel (sin .. / absoluta), comprueba SHA+size en data/raw local
contra manifiesto y hace put WebHDFS con
InsecureClient('http://10.22.87.215:50070') en
/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw.
Solo raw, NO silver. Sin VM.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DEFAULT_TOPIC = "anuncios_inmobiliarios"
DEFAULT_GROUP = "hdfs_centro"
DEFAULT_BOOTSTRAP = "10.22.87.215:9092"
DEFAULT_HDFS_URL = "http://10.22.87.215:50070"
DEFAULT_HDFS_USER = "iabd-user15"
DEFAULT_DEST = "/user/iabd-user15/bigdata_reto/vivienda_euskadi/data/raw"
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW_DIR = ROOT / "data" / "raw"


def get_bootstrap() -> str:
    return os.getenv("KAFKA_BOOTSTRAP_SERVERS") or DEFAULT_BOOTSTRAP


def get_group() -> str:
    return os.getenv("KAFKA_GROUP_ID") or DEFAULT_GROUP


def get_hdfs_url() -> str:
    return os.getenv("HDFS_URL") or DEFAULT_HDFS_URL


def get_hdfs_user() -> str:
    return os.getenv("HDFS_USER") or DEFAULT_HDFS_USER


def is_valid_rel(rel: str) -> bool:
    if not rel or ".." in Path(rel).parts:
        return False
    if Path(rel).is_absolute():
        return False
    if "legacy_obsoleto_no_usar" in rel:
        return False
    return True


def verify_local(raw_dir: Path, rel: str, size: int, sha: str) -> bool:
    p = Path(raw_dir) / rel
    if not p.is_file():
        return False
    data = p.read_bytes()
    return len(data) == size and hashlib.sha256(data).hexdigest() == sha


def consume(
    max_messages: int | None = None,
    poll_timeout_ms: int = 5000,
    group_id: str | None = None,
    topic: str | None = None,
    bootstrap_servers: str | None = None,
    raw_dir: Path | str | None = None,
    hdfs_url: str | None = None,
    hdfs_user: str | None = None,
    dest: str | None = None,
) -> dict:
    from hdfs import InsecureClient
    from kafka import KafkaConsumer, OffsetAndMetadata
    from kafka.structs import TopicPartition

    raw = Path(raw_dir) if raw_dir is not None else DEFAULT_RAW_DIR
    url = hdfs_url or get_hdfs_url()
    user = hdfs_user or get_hdfs_user()
    client = InsecureClient(url, user=user)
    dest_base = (dest or DEFAULT_DEST).rstrip("/")
    consumer = KafkaConsumer(
        topic or DEFAULT_TOPIC,
        bootstrap_servers=bootstrap_servers or get_bootstrap(),
        group_id=group_id or get_group(),
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        consumer_timeout_ms=poll_timeout_ms,
    )
    uploaded = skipped = 0
    offsets: list[tuple[int, int]] = []

    def _commit(msg) -> None:  # type: ignore[no-untyped-def]
        consumer.commit(
            {TopicPartition(msg.topic, msg.partition): OffsetAndMetadata(msg.offset + 1, "")}  # type: ignore[arg-type]
        )

    try:
        for msg in consumer:
            try:
                payload = json.loads(msg.value.decode("utf-8"))
            except Exception:
                skipped += 1
                _commit(msg)
                continue
            if payload.get("type") != "raw_manifest":
                # Mensajes previos del topic (p.ej. {"precio":850,...}) se descartan.
                skipped += 1
                _commit(msg)
                continue
            rel = payload.get("rel", "")
            size = int(payload.get("size", -1))
            sha = payload.get("sha256", "")
            if not is_valid_rel(rel):
                print(f"REL INVALIDA {rel!r} offset={msg.offset}")
                skipped += 1
                _commit(msg)
                continue
            if not verify_local(raw, rel, size, sha):
                print(f"SHA/SIZE MISMATCH {rel} offset={msg.offset}")
                skipped += 1
                _commit(msg)
                continue
            local_path = raw / rel
            with local_path.open("rb") as fp:
                data = fp.read()
            # Asegura directorios padre en HDFS (hdfs lib no crea padres anidados).
            parent = f"{dest_base}/{Path(rel).parent.as_posix()}"
            if str(Path(rel).parent) != "." and parent != dest_base:
                try:
                    client.makedirs(parent)
                except Exception:
                    pass
            client.write(f"{dest_base}/{rel}", data=data, overwrite=True)
            uploaded += 1
            offsets.append((msg.partition, msg.offset))
            _commit(msg)
            if uploaded % 50 == 0:
                print(f"SUBIDOS {uploaded}")
            if max_messages is not None and uploaded >= max_messages:
                break
        print(f"HDFS_CENTRO_UPLOADED {uploaded} a {dest_base} (skipped={skipped})")
        if offsets:
            print(f"OFFSETS {offsets[0][0]}:{offsets[0][1]}..{offsets[-1][0]}:{offsets[-1][1]}")
        return {"uploaded": uploaded, "skipped": skipped, "offsets": offsets}
    finally:
        consumer.close()


if __name__ == "__main__":
    import sys

    max_msg = int(sys.argv[1]) if len(sys.argv) > 1 else None
    print(consume(max_messages=max_msg))
