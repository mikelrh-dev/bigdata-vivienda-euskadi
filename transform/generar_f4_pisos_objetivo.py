#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""transform/generar_f4_pisos_objetivo.py

Valida (y, si falta, crea a partir de un criterio documentado) el archivo
data/procesado/f4_pisos_objetivo.json (lista de codigos INE objetivo para el
scraping dirigido de Pisos.com).

El archivo original es una seleccion manual (62 municipios, todos con
tipologia Nivel2/Nivel3 y baja cobertura de anuncios en Fotocasa). No existe
un criterio simple y reproducible que reproduzca exactamente esa lista, por lo
que este script es IDEMPOTENTE: si el archivo existe y es valido, no lo
modifica. Si no existe, lo genera a partir del criterio documentado
(municipios con tipologia Nivel2 o Nivel3 y menos de 5 anuncios en Fotocasa,
ordenados por codigo_ine) y avisa de que la lista puede diferir de la
original.
"""
from __future__ import annotations

import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.path.join(BASE, "data", "procesado")
RAW = os.path.join(BASE, "data", "raw")


def _validar(obj, nombres) -> list[str]:
    errores = []
    if not isinstance(obj, list):
        errores.append("no es una lista")
        return errores
    if not all(isinstance(x, str) for x in obj):
        errores.append("no todos los elementos son strings")
    desconocidos = [c for c in obj if c not in nombres]
    if desconocidos:
        errores.append(f"{len(desconocidos)} codigos no estan en dim_municipios: {desconocidos[:5]}")
    if len(obj) != len(set(obj)):
        errores.append("contiene duplicados")
    return errores


def main() -> int:
    dim_path = os.path.join(RAW, "dim_municipios.json")
    if not os.path.exists(dim_path):
        print(f"[ERROR] No existe {dim_path}")
        return 1
    dim = json.loads(open(dim_path, encoding="utf-8").read())
    regs = dim.get("datos", dim) if isinstance(dim, dict) else dim
    nombres = {r["codigo_ine"]: r["nombre_canonico"] for r in regs}

    out_path = os.path.join(PROC, "f4_pisos_objetivo.json")

    # Si existe, validar y no modificar (idempotente)
    if os.path.exists(out_path):
        try:
            obj = json.loads(open(out_path, encoding="utf-8").read())
        except Exception as e:
            print(f"[ERROR] JSON invalido: {e}")
            return 1
        errores = _validar(obj, nombres)
        if errores:
            print("[WARN] Archivo existente con problemas:", "; ".join(errores))
        else:
            print(f"[OK] {out_path} valido: {len(obj)} codigos (no modificado)")
        return 0

    # Si no existe, generar a partir del criterio documentado
    print("[INFO] Archivo no existe; generando a partir del criterio documentado")
    avb_path = os.path.join(PROC, "analisis_variables_base.csv")
    fc_path = os.path.join(RAW, "anuncios_fotocasa.csv")
    if not (os.path.exists(avb_path) and os.path.exists(fc_path)):
        print("[ERROR] Faltan analisis_variables_base.csv o anuncios_fotocasa.csv para generar")
        return 1
    import pandas as pd
    avb = pd.read_csv(avb_path, dtype=str)
    fc = pd.read_csv(fc_path, dtype=str)
    fc_count = fc["codigo_ine"].value_counts().to_dict() if "codigo_ine" in fc.columns else {}
    candidatos = avb[avb["tipologia_mercado"].isin(["Nivel2_Mercado_Regulado", "Nivel3_Mercado_Rural_Cerrado"])]
    seleccion = [c for c in candidatos["codigo_ine"].tolist() if fc_count.get(c, 0) < 5]
    seleccion = sorted(set(seleccion))
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(seleccion, fh, ensure_ascii=False, indent=2)
    print(f"[OK] {out_path}: {len(seleccion)} codigos generados (criterio: Nivel2/3 con <5 anuncios en Fotocasa)")
    print("[WARN] Lista generada puede diferir de la seleccion manual original (62 codigos)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
