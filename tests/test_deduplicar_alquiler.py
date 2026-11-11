"""Deduplicacion del alquiler enriquecido (transform/deduplicar_alquiler_enriquecido.py).

Cubre la logica pura y el contrato de fallo: sin el par de entrada producido
por enriquecer_codigo_ine.py el script debe fallar con mensaje accionable,
no saltarse el paso en silencio.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_spec = importlib.util.spec_from_file_location(
    "transform_dedup_alquiler",
    ROOT / "transform" / "deduplicar_alquiler_enriquecido.py")
assert _spec is not None and _spec.loader is not None
dedup = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dedup)

FILAS = [
    {"codigo_ine": "48001", "renta_media_eur_m2_media": "12.0",
     "cuantia_media_eur_mes_media": "900", "superficie_media_m2_media": "75"},
    {"codigo_ine": "48001", "renta_media_eur_m2_media": "12.0",
     "cuantia_media_eur_mes_media": "900", "superficie_media_m2_media": "75"},
    {"codigo_ine": "48002", "renta_media_eur_m2_media": "11.0",
     "cuantia_media_eur_mes_media": "800", "superficie_media_m2_media": "72"},
]


def test_deduplicar_filas_conserva_la_primera_ocurrencia():
    resultado = dedup.deduplicar_filas(FILAS)
    assert len(resultado) == 2
    assert [f["codigo_ine"] for f in resultado] == ["48001", "48002"]
    assert resultado[0] is FILAS[0]


def test_main_falla_si_falta_el_productor(tmp_path, monkeypatch, capsys):
    """Regresion F-01: antes imprimia [SKIP] y devolvia 0."""
    monkeypatch.setattr(dedup, "CSV_PATH", tmp_path / "alquiler_municipal_enriquecido.csv")
    monkeypatch.setattr(dedup, "JSON_PATH", tmp_path / "alquiler_municipal_enriquecido.json")

    rc = dedup.main()

    assert rc == 1
    assert "enriquecer_codigo_ine.py" in capsys.readouterr().err


def test_main_falla_si_falta_el_json(tmp_path, monkeypatch, capsys):
    csv_path = tmp_path / "alquiler_municipal_enriquecido.csv"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(FILAS[0]))
        w.writeheader()
        w.writerows(FILAS)
    monkeypatch.setattr(dedup, "CSV_PATH", csv_path)
    monkeypatch.setattr(dedup, "JSON_PATH", tmp_path / "alquiler_municipal_enriquecido.json")

    rc = dedup.main()

    assert rc == 1
    assert "enriquecer_codigo_ine.py" in capsys.readouterr().err


def test_main_deduplica_csv_y_json(tmp_path, monkeypatch, capsys):
    csv_path = tmp_path / "alquiler_municipal_enriquecido.csv"
    json_path = tmp_path / "alquiler_municipal_enriquecido.json"
    with csv_path.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(FILAS[0]))
        w.writeheader()
        w.writerows(FILAS)
    json_path.write_text(
        json.dumps({"metadata": {"n_registros": 3}, "datos": FILAS},
                   ensure_ascii=False),
        encoding="utf-8")
    monkeypatch.setattr(dedup, "CSV_PATH", csv_path)
    monkeypatch.setattr(dedup, "JSON_PATH", json_path)

    assert dedup.main() == 0

    with csv_path.open(encoding="utf-8-sig", newline="") as fh:
        assert len(list(csv.DictReader(fh))) == 2
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert len(data["datos"]) == 2
    assert data["metadata"]["n_registros"] == 2
    assert data["metadata"]["n_municipios"] == 2
    assert "CSV: 3 -> 2" in capsys.readouterr().out
