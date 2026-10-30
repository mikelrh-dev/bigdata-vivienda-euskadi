"""Limpieza básica de ECVI: extrae precio total y €/m² para último trimestre (2026T2)."""
from __future__ import annotations
import csv, json, os

RAW = os.path.join("data", "raw")
OUT = os.path.join("data", "procesado")

def read_ecvi(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        hdr = [next(reader) for _ in range(4)]
    data = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        for _ in range(4):
            next(reader)
        for row in reader:
            if not row or all(c.strip() == "" for c in row):
                continue
            data.append(row)
    return hdr, data

def last_quarter_row(data):
    for row in data:
        if len(row) >= 2 and row[0].strip() == "2026" and row[1].strip() == "II":
            return row
    return data[-1] if data else []

def parse_t1(path_total, path_m2):
    hdr_t, data_t = read_ecvi(path_total)
    hdr_m, data_m = read_ecvi(path_m2)
    target = last_quarter_row(data_t)
    target_m = last_quarter_row(data_m)
    terrs = hdr_t[1]; subcols = hdr_t[2]; names = hdr_t[3]
    terrs_m = hdr_m[1]; subcols_m = hdr_m[2]; names_m = hdr_m[3]
    price_map = {}
    for idx in range(2, len(terrs)):
        s = subcols[idx].strip()
        n = names[idx].strip()
        t = terrs[idx].strip()
        if not t:
            for j in range(idx-1, 1, -1):
                if terrs[j].strip():
                    t = terrs[j].strip()
                    break
        if (s in ("Viv", "Viv total") and n == "Total") or (n in ("Vitoria-Gasteiz", "Bilbao", "Donostia-San Sebastián")):
            ambito = t if n == "Total" else n
            price_map[ambito] = idx
    m2_map = {}
    for idx in range(2, len(terrs_m)):
        s = subcols_m[idx].strip()
        n = names_m[idx].strip()
        t = terrs_m[idx].strip()
        if not t:
            for j in range(idx-1, 1, -1):
                if terrs_m[j].strip():
                    t = terrs_m[j].strip()
                    break
        if (s in ("Viv", "Viv total") and n == "Total") or (n in ("Vitoria-Gasteiz", "Bilbao", "Donostia-San Sebastián")):
            ambito = t if n == "Total" else n
            m2_map[ambito] = idx
    records = []
    for ambito, col in price_map.items():
        m2_col = m2_map.get(ambito)
        pv = target[col].strip() if col < len(target) else ""
        mv = target_m[m2_col].strip() if (m2_col is not None and m2_col < len(target_m)) else ""
        records.append({
            "ambito_tipo": "territorio",
            "nombre_ambito": ambito,
            "codigo_ine": None,
            "trimestre": "2026T2",
            "precio_medio_total_eur": float(pv) if pv else None,
            "precio_m2_libre_eur": float(mv) if mv else None,
            "precio_m2_usada_eur": None,
        })
    return records

def parse_t2(path_total, path_m2):
    hdr_t, data_t = read_ecvi(path_total)
    hdr_m, data_m = read_ecvi(path_m2)
    target = last_quarter_row(data_t)
    target_m = last_quarter_row(data_m)
    areas = hdr_t[2]
    subcols = hdr_t[3]
    areas_m = hdr_m[2]
    subcols_m = hdr_m[3]
    records = []
    i = 2
    while i < len(areas):
        area_name = areas[i].strip()
        if not area_name:
            i += 1
            continue
        col = i
        m2_col = i
        pv = target[col].strip() if col < len(target) else ""
        mv = target_m[m2_col].strip() if m2_col < len(target_m) else ""
        records.append({
            "ambito_tipo": "area_funcional",
            "nombre_ambito": area_name,
            "codigo_ine": None,
            "trimestre": "2026T2",
            "precio_medio_total_eur": float(pv) if pv else None,
            "precio_m2_libre_eur": float(mv) if mv else None,
            "precio_m2_usada_eur": None,
        })
        i += 3
    return records

def parse_t3(path_total, path_m2):
    hdr_t, data_t = read_ecvi(path_total)
    hdr_m, data_m = read_ecvi(path_m2)
    target = last_quarter_row(data_t)
    target_m = last_quarter_row(data_m)
    munis = hdr_t[2]
    subcols = hdr_t[3]
    munis_m = hdr_m[2]
    subcols_m = hdr_m[3]
    records = []
    i = 2
    while i < len(munis):
        mun_name = munis[i].strip()
        if not mun_name:
            i += 1
            continue
        code = None
        name = mun_name
        if " - " in mun_name:
            code, name = mun_name.split(" - ", 1)
            code = code.strip()
            name = name.strip()
        col = i
        m2_col = i
        pv = target[col].strip() if col < len(target) else ""
        mv = target_m[m2_col].strip() if m2_col < len(target_m) else ""
        records.append({
            "ambito_tipo": "municipio",
            "nombre_ambito": name,
            "codigo_ine": code,
            "trimestre": "2026T2",
            "precio_medio_total_eur": float(pv) if pv else None,
            "precio_m2_libre_eur": float(mv) if mv else None,
            "precio_m2_usada_eur": None,
        })
        i += 3
    return records

def main():
    os.makedirs(OUT, exist_ok=True)
    recs = []
    recs += parse_t1(
        os.path.join(RAW, "ecvi_ecvi_es_2026t2_t1_2.csv"),
        os.path.join(RAW, "ecvi_ecvi_es_2026t2_t1_3.csv"),
    )
    recs += parse_t2(
        os.path.join(RAW, "ecvi_ecvi_es_2026t2_t2_2.csv"),
        os.path.join(RAW, "ecvi_ecvi_es_2026t2_t2_3.csv"),
    )
    recs += parse_t3(
        os.path.join(RAW, "ecvi_ecvi_es_2026t2_t3_2.csv"),
        os.path.join(RAW, "ecvi_ecvi_es_2026t2_t3_3.csv"),
    )
    with open(os.path.join(OUT, "ecvi_compraventa_limpio.json"), "w", encoding="utf-8") as f:
        json.dump(recs, f, ensure_ascii=False, indent=2)
    import pandas as pd
    pd.DataFrame(recs).to_csv(os.path.join(OUT, "ecvi_compraventa_limpio.csv"), index=False, encoding="utf-8-sig")
    print("ECVI limpio:", len(recs), "registros")

if __name__ == "__main__":
    main()
