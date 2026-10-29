"""Normaliza codigo_ine en todos los JSON crudos de data/raw/."""
from __future__ import annotations
import json, os, glob

RAW = os.path.join("data", "raw")
OUT = os.path.join("data", "procesado")

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

def normalize_obj(obj):
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            if k == "codigo_ine":
                new[k] = norm_code(v)
            else:
                new[k] = normalize_obj(v)
        return new
    if isinstance(obj, list):
        return [normalize_obj(x) for x in obj]
    return obj

def main():
    os.makedirs(OUT, exist_ok=True)
    files = sorted(glob.glob(os.path.join(RAW, "*.json")))
    for f in files:
        try:
            with open(f, encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception as e:
            print("SKIP (json error):", f, e)
            continue
        data = normalize_obj(data)
        out = os.path.join(OUT, os.path.basename(f).replace(".json", "_normalizado.json"))
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        print("OK:", os.path.basename(f), "->", os.path.basename(out))

if __name__ == "__main__":
    main()
