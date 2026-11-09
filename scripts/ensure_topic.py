"""Asegura el topic vivienda_euskadi en el centro antes de producir.

    python -m scripts.ensure_topic
    # o directo: python storage/kafka_topic.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> str:
    from storage.kafka_topic import ensure_topic

    return ensure_topic()


if __name__ == "__main__":
    os.environ.setdefault("KAFKA_TOPIC", "vivienda_euskadi")
    print(main())
