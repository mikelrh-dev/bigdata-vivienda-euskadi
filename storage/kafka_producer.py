"""Productor Kafka de anuncios unificados (KAFKA-01).

Lee data/procesado/anuncios_unificados.csv (759 filas), serializa cada
anuncio a JSON en bytes y lo publica en el topic anuncios_inmobiliarios
con clave portal:id_anuncio, callback de envío y flush al final.

VM destino según ficha: 192.168.201.162:9094. La configuración de
bootstrap puede sobrescribirse con KAFKA_BOOTSTRAP_SERVERS y el topic
con KAFKA_TOPIC; el valor de VM_HOST/VM_KAFKA_PORT de .env/.env.example
es un placeholder (192.168.1.100:9092) y no se usa como defecto.
"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from storage.mongo import to_float, to_str

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = ROOT / "data" / "procesado" / "anuncios_unificados.csv"
DEFAULT_BOOTSTRAP_SERVERS = "192.168.201.162:9094"
DEFAULT_TOPIC = "anuncios_inmobiliarios"


def get_bootstrap_servers() -> str:
    return os.getenv("KAFKA_BOOTSTRAP_SERVERS") or DEFAULT_BOOTSTRAP_SERVERS


def get_topic() -> str:
    return os.getenv("KAFKA_TOPIC") or DEFAULT_TOPIC


def _normalise_row(row: dict[str, Any]) -> dict[str, Any]:
    """Normaliza claves de CSV (BOM utf-8-sig y espacios)."""
    clean: dict[str, Any] = {}
    for key, value in row.items():
        if key is None:
            continue
        name = str(key).strip().lstrip("\ufeff")
        clean[name] = value
    return clean


def row_to_anuncio(row: dict[str, Any]) -> dict[str, Any]:
    """Convierte una fila del CSV en el payload JSON del anuncio."""
    r = _normalise_row(row)
    return {
        "portal": to_str(r.get("portal")),
        "id_anuncio": to_str(r.get("id_anuncio")),
        "modalidad": to_str(r.get("modalidad")),
        "precio_eur": to_float(r.get("precio_eur")),
        "superficie_m2": to_float(r.get("superficie_m2")),
        "habitaciones": to_float(r.get("habitaciones")),
        "codigo_ine": to_str(r.get("codigo_ine")),
        "municipio": to_str(r.get("municipio")),
    }


def serialize_anuncio(anuncio: dict[str, Any]) -> tuple[bytes, bytes]:
    """Devuelve (clave, valor) en bytes para Kafka.

    La clave es portal:id_anuncio (orden de partición por anuncio) y el
    valor es el anuncio serializado a JSON con precio y municipio.
    """
    key = f"{anuncio.get('portal')}:{anuncio.get('id_anuncio')}".encode("utf-8")
    value = json.dumps(anuncio, ensure_ascii=False).encode("utf-8")
    return key, value


def build_message(row: dict[str, Any]) -> tuple[bytes, bytes]:
    """Atajo fila CSV -> (clave, valor JSON bytes) listos para send()."""
    return serialize_anuncio(row_to_anuncio(row))


def read_anuncios(csv_path: str | Path | None = None) -> list[dict[str, Any]]:
    path = Path(csv_path) if csv_path is not None else DEFAULT_CSV
    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        anuncios = [row_to_anuncio(row) for row in reader]
    return [
        a for a in anuncios if a.get("portal") is not None and a.get("id_anuncio") is not None
    ]


def _on_send_success(metadata: Any) -> None:
    if isinstance(metadata, Exception):
        print(f"Error al publicar anuncio: {metadata}")
        return
    print(
        f"Publicado topic={metadata.topic} partition={metadata.partition} "
        f"offset={metadata.offset}"
    )


def produce(
    csv_path: str | Path | None = None,
    topic: str | None = None,
    bootstrap_servers: str | None = None,
    producer: Any | None = None,
) -> int:
    """Publica todos los anuncios del CSV y devuelve cuántos ha enviado.

    Si se inyecta un producer (tests), no se crea conexión Kafka real.
    En cualquier caso se hace flush() con callback en cada send().
    """
    anuncios = read_anuncios(csv_path)
    topic_name = topic or get_topic()
    own_producer = producer is None
    if own_producer:
        from kafka import KafkaProducer

        producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers or get_bootstrap_servers()
        )
    try:
        for anuncio in anuncios:
            key, value = serialize_anuncio(anuncio)
            producer.send(
                topic_name,
                key=key,
                value=value,
                callback=_on_send_success,
            )
        producer.flush()
    finally:
        if own_producer:
            producer.close()
    print(f"Publicados {len(anuncios)} anuncios en {topic_name}")
    return len(anuncios)


if __name__ == "__main__":
    produce()
