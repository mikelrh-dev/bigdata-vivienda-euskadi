"""Helper de resolucion de municipios para unificar_anuncios."""
from __future__ import annotations
import unicodedata, difflib, pandas as pd, os

RAW = os.path.join("data", "raw")

def _load_dim():
    dim = pd.read_csv(os.path.join(RAW, "dim_municipios.csv"), dtype=str, encoding="utf-8-sig")
    dim["codigo_ine"] = dim["codigo_ine"].astype(str).str.zfill(5)
    code2name = dict(zip(dim["codigo_ine"], dim["nombre_canonico"]))
    name2code = {}
    for _, r in dim.iterrows():
        name2code[str(r["nombre_canonico"]).strip().lower()] = r["codigo_ine"]
        for v in str(r.get("variantes", "")).split("|"):
            v = v.strip().lower()
            if v:
                name2code[v] = r["codigo_ine"]
    return code2name, name2code, set(dim["codigo_ine"])

CODE2NAME, NAME2CODE, VALID_CODES = _load_dim()

MANUAL_MAP = {
    "donostia-san sebastian": "Donostia/San Sebastián",
    "donostia - san sebastian": "Donostia/San Sebastián",
    "arrasate": "Arrasate/Mondragón",
    "vitoria": "Vitoria-Gasteiz",
    "arrankudiaga-zollo": "Arrankudiaga",
    "arrankudiaga zollo": "Arrankudiaga",
}


def norm(s):
    if s is None:
        return ""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode("ascii")
    return " ".join(s.lower().replace("-", " ").replace("_", " ").split())


def resolver_codigo(municipio, codigo_ine):
    if codigo_ine is not None:
        s = str(codigo_ine).strip()
        if s.isdigit():
            s = s.zfill(5)
        if s in VALID_CODES:
            return s, CODE2NAME.get(s)
    key = norm(municipio)
    if key in MANUAL_MAP:
        canon = MANUAL_MAP[key]
        for c, n in CODE2NAME.items():
            if n == canon:
                return c, n
    if key in NAME2CODE:
        c = NAME2CODE[key]
        return c, CODE2NAME.get(c)
    best_score = 0.0
    best = None
    for c, n in CODE2NAME.items():
        score = difflib.SequenceMatcher(None, key, norm(n)).ratio()
        if score > best_score:
            best_score = score
            best = (c, n)
    if best and best_score >= 0.85:
        return best
    return None, None
