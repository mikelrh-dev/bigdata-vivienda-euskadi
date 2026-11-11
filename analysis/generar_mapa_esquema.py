"""Genera un mapa visual (HTML) del esquema silver (CSVs) con pyvis.

Lee UNICAMENTE las cabeceras de los CSVs (utf-8-sig), no los datos.
Los nodos son archivos CSV (coloreados por familia) y las aristas conectan
cada CSV con los hubs ``dim_municipios`` (si tiene codigo_ine/territorio)
y ``anuncios_unificados`` (si tiene id_anuncio). Sin auto-bucles ni aristas
duplicadas. Layout fuerza-dirigido. Salida en data/resultados/.
"""

from __future__ import annotations

import csv
import os
from pathlib import Path

import networkx as nx
from pyvis.network import Network

ROOT = Path(__file__).resolve().parents[1]
CSV_DIR = ROOT / "data" / "procesado"
OUT_DIR = ROOT / "data" / "resultados"
OUT_FILE = OUT_DIR / "mapa_esquema_silver.html"

HUBS = ("dim_municipios", "anuncios_unificados")

FAMILY_COLORS = {
    "anuncios": "#e74c3c",
    "alquiler": "#3498db",
    "dim_municipios": "#2ecc71",
    "distancias": "#9b59b6",
    "eustat": "#f39c12",
    "udalmap": "#1abc9c",
    "certificado": "#e67e22",
    "municipio": "#27ae60",
    "poblacion": "#2980b9",
    "renta": "#8e44ad",
    "transporte": "#16a085",
    "ecvi": "#d35400",
    "emancipacion": "#c0392b",
    "comparativa": "#7f8c8d",
    "analisis": "#f1c40f",
    "fotocasa": "#e91e63",
    "informe": "#95a5a6",
    "otros": "#bdc3c7",
}


def familia_de(stem: str) -> str:
    s = stem.lower()
    for pref, fam in [
        ("anuncios", "anuncios"),
        ("alquiler", "alquiler"),
        ("dim_municipios", "dim_municipios"),
        ("distancias", "distancias"),
        ("eustat", "eustat"),
        ("udalmap", "udalmap"),
        ("cert_", "certificado"),
        ("municipio", "municipio"),
        ("municipios", "municipio"),
        ("poblacion", "poblacion"),
        ("renta", "renta"),
        ("transporte", "transporte"),
        ("ecvi", "ecvi"),
        ("emancipacion", "emancipacion"),
        ("comparativa", "comparativa"),
        ("analisis", "analisis"),
        ("f4", "fotocasa"),
        ("fotocasa", "fotocasa"),
        ("informe", "informe"),
    ]:
        if s.startswith(pref):
            return fam
    return "otros"


def leer_cabecera(ruta: Path) -> list[str]:
    with ruta.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.reader(fh)
        try:
            return next(reader)
        except StopIteration:
            return []


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)

    csvs = sorted(CSV_DIR.glob("*.csv"))
    tablas: dict[str, list[str]] = {}
    for ruta in csvs:
        tablas[ruta.stem] = leer_cabecera(ruta)

    # Grafo sin auto-bucles ni aristas duplicadas
    g = nx.Graph()
    for stem, cols in tablas.items():
        fam = familia_de(stem)
        g.add_node(
            stem,
            label=stem,
            title=f"{stem}.csv\nfamilia={fam}\ncolumnas={len(cols)}",
            color=FAMILY_COLORS.get(fam, FAMILY_COLORS["otros"]),
            size=24 if stem in HUBS else 12,
        )

    aristas: set[tuple[str, str]] = set()
    for stem, cols in tablas.items():
        colset = set(cols)
        conecta_dim = bool({"codigo_ine", "territorio"} & colset)
        conecta_anun = "id_anuncio" in colset
        if conecta_dim and stem != "dim_municipios":
            aristas.add(tuple(sorted((stem, "dim_municipios"))))
        if conecta_anun and stem != "anuncios_unificados":
            aristas.add(tuple(sorted((stem, "anuncios_unificados"))))

    for u, v in sorted(aristas):
        if u == v:
            continue
        g.add_edge(u, v)

    # Red pyvis con layout fuerza-dirigido
    net = Network(height="800px", width="100%", bgcolor="#ffffff", font_color="#222222",
                  cdn_resources="in_line")
    net.from_nx(g)
    net.toggle_physics(True)
    net.force_atlas_2based(gravity=-50, central_gravity=0.01, spring_length=100)
    net.show_buttons(filter_=["physics"])
    net.show(str(OUT_FILE), notebook=False)

    # Nodos hub = mayor grado (los dos hubs declarados)
    grados = sorted(g.degree, key=lambda x: (-x[1], x[0]))
    hub_nodes = [n for n, _ in grados if n in HUBS]
    print("Hub nodes:", hub_nodes)
    print(f"CSVs: {len(tablas)} | nodos: {g.number_of_nodes()} | aristas: {g.number_of_edges()}")
    print(f"Salida: {OUT_FILE}")


if __name__ == "__main__":
    main()
