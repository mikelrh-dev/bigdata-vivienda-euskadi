"""Entity resolution centralizada: nombre de municipio -> codigo_ine.

Tabla de verdad: data/raw/dim_municipios.csv (252 municipios).
Uso:
  from entity_resolution import resolver_municipio, cargar_dim
  codigo, canonico = resolver_municipio("Donostia-San Sebastián")
"""
from __future__ import annotations

import re
import unicodedata
from functools import lru_cache
from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" \
    if (Path(__file__).resolve().parent.parent / "data").exists() \
    else Path(__file__).resolve().parent / "data" / "raw"


def norm(texto: str) -> str:
    t = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    t = t.lower().strip()
    t = re.sub(r"[\s\-_/]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


# (bloque EQUIVALENCIAS_EXTRA eliminado: dead code, las variantes viven en dim_municipios.json)


@lru_cache(maxsize=1)
def cargar_dim() -> pd.DataFrame:
    try:
        from extract._common import RAW_DIR as _RAW
    except ModuleNotFoundError:
        from _common import RAW_DIR as _RAW  # noqa: E402
    dim = pd.read_csv(_RAW / "dim_municipios.csv", dtype=str, encoding="utf-8-sig")
    dim["codigo_ine"] = dim["codigo_ine"].str.zfill(5)
    return dim


@lru_cache(maxsize=1)
def _mapa() -> dict[str, tuple[str, str]]:
    """{nombre_normalizado: (codigo_ine, nombre_canonico)}"""
    dim = cargar_dim()
    mapa: dict[str, tuple[str, str]] = {}
    for _, r in dim.iterrows():
        cod, can = r["codigo_ine"], r["nombre_canonico"]
        mapa[norm(can)] = (cod, can)
        variantes = str(r.get("variantes", "") or "")
        for v in variantes.split("|"):
            v = v.strip()
            if v:
                mapa.setdefault(norm(v), (cod, can))
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
