"""Regresión de la deduplicación del alquiler municipal enriquecido."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "deduplicar_alquiler_enriquecido",
    ROOT / "transform" / "deduplicar_alquiler_enriquecido.py",
)
assert _spec is not None and _spec.loader is not None
dedup = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dedup)


def test_deduplica_csv_y_json_y_actualiza_metadata(tmp_path, monkeypatch):
    csv_path = tmp_path / "alquiler_municipal_enriquecido.csv"
    json_path = tmp_path / "alquiler_municipal_enriquecido.json"
    rows = [
        {"codigo_ine": "48082", "renta_media_eur_m2_media": "10.3",
         "cuantia_media_eur_mes_media": "700.0",
         "superficie_media_m2_media": "70.0", "municipio": "A"},
        {"codigo_ine": "48082", "renta_media_eur_m2_media": "10.3",
         "cuantia_media_eur_mes_media": "700.0",
         "superficie_media_m2_media": "70.0", "municipio": "B"},
        {"codigo_ine": "48020", "renta_media_eur_m2_media": "12.0",
         "cuantia_media_eur_mes_media": "900.0",
         "superficie_media_m2_media": "75.0", "municipio": "Bilbao"},
    ]
    with csv_path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    json_path.write_text(json.dumps({
        "metadata": {"n_registros": 3, "n_municipios": 2},
        "datos": rows,
    }), encoding="utf-8")
    monkeypatch.setattr(dedup, "CSV_PATH", csv_path)
    monkeypatch.setattr(dedup, "JSON_PATH", json_path)

    assert dedup.main() == 0

    with csv_path.open(encoding="utf-8-sig", newline="") as fh:
        csv_rows = list(csv.DictReader(fh))
    json_data = json.loads(json_path.read_text(encoding="utf-8"))
    assert len(csv_rows) == 2
    assert len(json_data["datos"]) == 2
    assert json_data["metadata"]["n_registros"] == 2
    assert json_data["metadata"]["n_municipios"] == 2
    assert csv_rows[0]["municipio"] == "A"  # conserva primera ocurrencia
