"""Tests de la comparativa de 3 municipios robustos desde MongoDB.

CONCLUSION-01 (nivel 10 de Respuesta): la comparativa generada por
`analysis.comparativa_mongo.comparativa_tres_robustos` debe devolver 3
filas con n>=30 y paro Lanbide no nulo, con valores reales de Mongo.
"""

from __future__ import annotations

import csv

from analysis.comparativa_mongo import COLUMNAS, comparativa_tres_robustos


def test_comparativa_tres_robustos_n30(tmp_path) -> None:
    filas = comparativa_tres_robustos()
    assert len(filas) == 3
    assert [f["n_anuncios"] for f in filas] == sorted(
        (f["n_anuncios"] for f in filas), reverse=True
    )
    for fila in filas:
        assert fila["n_anuncios"] >= 30
        assert fila["tasa_paro_lanbide_pct"] is not None
        assert fila["codigo_ine"]
        assert fila["nombre"]

    salida = tmp_path / "comparativa.csv"
    filas_csv = comparativa_tres_robustos(output_path=salida)
    assert salida.exists()
    with salida.open(encoding="utf-8") as fh:
        lector = csv.DictReader(fh)
        assert lector.fieldnames == COLUMNAS
        leidas = list(lector)
    assert len(leidas) == 3
    for leida, fila in zip(leidas, filas_csv):
        assert leida["codigo_ine"] == fila["codigo_ine"]
        assert int(leida["n_anuncios"]) == fila["n_anuncios"]
        assert leida["tasa_paro_lanbide_pct"] != ""
