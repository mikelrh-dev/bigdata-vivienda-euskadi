"""Rescate de superficie_m2 y habitaciones via regex sobre titulo/subtitulo."""
from __future__ import annotations
import json, os, re

RAW = os.path.join("data", "raw")
OUT = os.path.join("data", "procesado")

RE_M2 = re.compile(r"(\d+)\s*m[²2]", re.IGNORECASE)
RE_HAB = re.compile(r"(\d+)\s*hab", re.IGNORECASE)


def rescue(rec):
    rescued_m2 = False
    rescued_hab = False
    if rec.get("superficie_m2") is None:
        text = " ".join(str(x) for x in [rec.get("titulo"), rec.get("subtitulo")] if x)
        m = RE_M2.search(text)
        if m:
            val = int(m.group(1))
            if 15 <= val <= 500:
                rec["superficie_m2"] = val
                rescued_m2 = True
            # update outlier flag
            sup = rec.get("superficie_m2")
            try:
                supf = float(sup) if sup is not None else None
            except (ValueError, TypeError):
                supf = None
            rec["es_outlier_superficie"] = bool(supf is not None and (supf < 10 or supf > 500))
    if rec.get("habitaciones") is None:
        text = " ".join(str(x) for x in [rec.get("titulo"), rec.get("subtitulo")] if x)
        m = RE_HAB.search(text)
        if m:
            val = int(m.group(1))
            if val <= 10:
                rec["habitaciones"] = val
                rescued_hab = True
    # recalcular precio_m2_calc si hay superficie y precio
    if rec.get("superficie_m2") and rec.get("precio_eur"):
        try:
            rec["auditoria"]["precio_m2_calc"] = round(float(rec["precio_eur"]) / float(rec["superficie_m2"]), 2)
        except Exception:
            pass
    return rescued_m2, rescued_hab


def main():
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "anuncios_unificados.json"), encoding="utf-8") as f:
        recs = json.load(f)
    r_m2 = r_hab = 0
    for r in recs:
        a, b = rescue(r)
        if a:
            r_m2 += 1
        if b:
            r_hab += 1
    with open(os.path.join(OUT, "anuncios_unificados.json"), "w", encoding="utf-8") as f:
        json.dump(recs, f, ensure_ascii=False, indent=2)
    import pandas as pd
    csv_path = os.path.join(OUT, "anuncios_unificados.csv")
    prev = None
    if os.path.exists(csv_path):
        try:
            prev = pd.read_csv(csv_path)
        except Exception:
            prev = None
    df = pd.DataFrame([{
        "id_anuncio": r["id_anuncio"],
        "portal": r["portal"],
        "modalidad": r["modalidad"],
        "precio_eur": r["precio_eur"],
        "superficie_m2": r["superficie_m2"],
        "habitaciones": r["habitaciones"],
        "es_outlier_superficie": r.get("es_outlier_superficie", False),
        "codigo_ine": r["ubicacion"]["codigo_ine"],
        "municipio": r["ubicacion"]["municipio"],
        "titulo": r.get("titulo"),
        "subtitulo": r.get("subtitulo"),
        "equipamiento": ",".join(r["equipamiento"]),
    } for r in recs])
    # Salida aditiva: conservar las columnas que ya existian en el CSV.
    if prev is not None:
        for col in prev.columns:
            if col in df.columns:
                continue
            if "id_anuncio" in prev.columns and "id_anuncio" in df.columns:
                mapping = dict(zip(prev["id_anuncio"].astype(str), prev[col]))
                df[col] = df["id_anuncio"].astype(str).map(mapping)
            else:
                df[col] = pd.NA
    df.to_csv(csv_path, index=False)
    print(f"Rescatados: superficie={r_m2}, habitaciones={r_hab}")
    print("Total anuncios:", len(recs))

if __name__ == "__main__":
    main()
