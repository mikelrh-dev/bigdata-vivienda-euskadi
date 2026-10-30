"""Normaliza codigo_ine en todos los JSON crudos de data/raw/."""
from __future__ import annotations
import json, os, glob
from datetime import datetime

RAW = os.path.join("data", "raw")
OUT = os.path.join("data", "procesado")

# Fecha por defecto documentada cuando no hay mtime disponible.
FECHA_DEFAULT = "1970-01-01T00:00:00"


def _fecha_desde_mtime(ruta: str) -> str:
    try:
        return datetime.fromtimestamp(os.path.getmtime(ruta)).isoformat(timespec="seconds")
    except OSError:
        return FECHA_DEFAULT

def norm_code(v):
    if v is None:
        return None
    s = str(v).strip()
    if s.lower() in ("none", "nan", ""):
        return None
    # si es numero sin ceros, zfill 5
    if s.isdigit():
        return s.zfill(5)
    return s

def normalize_obj(obj, fotocasa: bool = False):
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            if k == "codigo_ine":
                # Sanear codigo_ine vacio en JSONs de Fotocasa: '' -> None
                if fotocasa and (v is None or str(v).strip() == "" or str(v).strip().lower() in ("none", "nan", "null")):
                    new[k] = None
                else:
                    new[k] = norm_code(v)
            else:
                new[k] = normalize_obj(v, fotocasa=fotocasa)
        return new
    if isinstance(obj, list):
        return [normalize_obj(x, fotocasa=fotocasa) for x in obj]
    return obj

def main():
    os.makedirs(OUT, exist_ok=True)
    files = sorted(glob.glob(os.path.join(RAW, "*.json")))
    for f in files:
        try:
            with open(f, encoding="utf-8-sig") as fh:
                data = json.load(fh)
        except Exception as e:
            print("SKIP (json error):", f, e)
            continue
        is_fotocasa = "fotocasa" in os.path.basename(f).lower()
        data = normalize_obj(data, fotocasa=is_fotocasa)
        # Inyectar fecha_extraccion en JSON que no la tengan (b5m, dim_municipios,
        # distancias, emal_ampliado, ine_atlas_renta, lanbide_paro_juvenil,
        # osrm, renta_municipal_completa, serpavi, udalmap_empleo_corregido, ...).
        if isinstance(data, dict):
            meta = data.setdefault("metadata", {})
            if not isinstance(meta, dict):
                meta = {}
                data["metadata"] = meta
            if not meta.get("fecha_extraccion"):
                meta["fecha_extraccion"] = _fecha_desde_mtime(f)
        out = os.path.join(OUT, os.path.basename(f).replace(".json", "_normalizado.json"))
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        print("OK:", os.path.basename(f), "->", os.path.basename(out))

if __name__ == "__main__":
    main()
