"""Entity resolution centralizada: nombre de municipio -> codigo_ine.

Tabla de verdad durante Extract: extracto municipal de Eustat en raw/.
Uso:
  from entity_resolution import resolver_municipio, cargar_dim
  codigo, canonico = resolver_municipio("Donostia-San Sebastián")
"""
from __future__ import annotations

import re
import sys
import unicodedata
from functools import lru_cache
from pathlib import Path

import pandas as pd

try:
    from extract._common import RAW_DIR
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _common import RAW_DIR  # noqa: E402


def norm(texto: str) -> str:
    t = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    t = t.lower().strip()
    t = re.sub(r"[\s\-_/]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


MANUAL_MAP = {
    norm("donostia san sebastian"): "Donostia/San Sebastián",
    norm("donostia - san sebastian"): "Donostia/San Sebastián",
    norm("arrasate"): "Arrasate/Mondragón",
    norm("vitoria"): "Vitoria-Gasteiz",
    norm("arrankudiaga zollo"): "Arrankudiaga",
    norm("donostia/san sebastian"): "Donostia/San Sebastián",
    norm("arrasate/mondragon"): "Arrasate/Mondragón",
    norm("arrasate - mondragon"): "Arrasate/Mondragón",
    # Fotocasa escribe "Plasencia"; el nombre oficial usa "Placencia".
    norm("Soraluze / Plasencia de las Armas"): "Soraluze-Placencia de las Armas",
}


@lru_cache(maxsize=1)
def cargar_dim() -> pd.DataFrame:
    """Carga municipios desde Eustat raw; nunca consulta ni escribe Silver."""
    source_path = RAW_DIR / "eustat_renta_municipal.csv"
    if not source_path.exists():
        raise FileNotFoundError(
            f"Falta {source_path}; ejecuta primero el extractor eustat."
        )
    source = pd.read_csv(source_path, dtype=str, encoding="utf-8-sig")
    codigos = source["ámbitos territoriales"].astype(str).str.strip()
    municipios = source[
        codigos.str.len().isin([4, 5])
        & codigos.str[:2].isin(["01", "20", "48"])
    ][["ámbitos territoriales", "ámbitos territoriales__etiqueta"]].drop_duplicates()
    territorios = {"01": "Araba/Álava", "20": "Gipuzkoa", "48": "Bizkaia"}
    registros = [
        {
            "codigo_ine": str(row["ámbitos territoriales"]).strip().zfill(5),
            "nombre_canonico": str(row["ámbitos territoriales__etiqueta"]).strip(),
            "territorio": territorios[str(row["ámbitos territoriales"]).strip()[:2]],
            "variantes": [],
        }
        for _, row in municipios.iterrows()
    ]
    dim = pd.DataFrame(registros)
    dim["codigo_ine"] = dim["codigo_ine"].astype(str).str.zfill(5)
    return dim


@lru_cache(maxsize=1)
def _mapa() -> dict[str, tuple[str, str]]:
    """{nombre_normalizado: (codigo_ine, nombre_canonico)}"""
    dim = cargar_dim()
    mapa: dict[str, tuple[str, str]] = {}
    for _, r in dim.iterrows():
        cod, can = r["codigo_ine"], r["nombre_canonico"]
        mapa[norm(can)] = (cod, can)
        variantes = r.get("variantes", [])
        if isinstance(variantes, str):
            variantes = variantes.split("|")
        for v in variantes or []:
            v = str(v).strip()
            if v:
                mapa.setdefault(norm(v), (cod, can))
    # fold manual aliases
    for key, canon in MANUAL_MAP.items():
        canon_norm = norm(canon)
        if canon_norm in mapa:
            mapa.setdefault(key, mapa[canon_norm])
    return mapa


def resolver_municipio(nombre: str | None) -> tuple[str | None, str | None]:
    """Devuelve (codigo_ine, nombre_canonico) o (None, None)."""
    if nombre is None or (isinstance(nombre, float) and pd.isna(nombre)):
        return None, None
    s = str(nombre).strip()
    if not s:
        return None, None
    mapa = _mapa()
    hit = mapa.get(norm(s))
    if hit:
        return hit[0], hit[1]
    return None, None


def resolver_serie(serie: pd.Series) -> pd.DataFrame:
    res = serie.apply(resolver_municipio)
    return pd.DataFrame(res.tolist(), columns=["codigo_ine", "nombre_canonico"])
