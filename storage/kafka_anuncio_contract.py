"""Shared event contract for Kafka announcement messages."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "data" / "procesado" / "anuncios_unificados.csv"
DEFAULT_BOOTSTRAP = "10.22.87.215:9092"
DEFAULT_TOPIC = "anuncios_eventos"
DEFAULT_GROUP = "anuncios_eventos_test"


def get_topic() -> str:
    return os.getenv("KAFKA_EVENTS_TOPIC") or DEFAULT_TOPIC


def event_from_row(row: dict[str, str]) -> dict:
    """Build the stable JSON event shared by producer and consumer."""
    portal = (row.get("portal") or "").strip()
    source_id = (row.get("id_anuncio") or "").strip()
    code = (row.get("codigo_ine") or "").strip()
    if not portal or not source_id or not code:
        raise ValueError("Evento requiere portal, id_anuncio y codigo_ine")
    if code.isdigit():
        code = code.zfill(5)
    return {
        "type": "anuncio_upsert",
        "event_id": f"{portal}:{source_id}",
        "codigo_ine": code,
        "data": row,
    }
