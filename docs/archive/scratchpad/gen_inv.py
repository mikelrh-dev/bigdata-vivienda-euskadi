import os, json
from pathlib import Path
import pandas as pd

BASE = Path(".")
RAW = BASE/"data"/"raw"
PROC = BASE/"data"/"procesado"

def size_kb(p):
    return p.stat().st_size/1024

raw_files = []
for root,_,files in os.walk(RAW):
    for fn in files:
        p = Path(root)/fn
        rel = p.relative_to(RAW).as_posix()
        if fn == ".FROZEN":
            continue
        raw_files.append((rel,p))
raw_files.sort()

from collections import defaultdict
groups = defaultdict(lambda: {"n":0,"size":0})
for rel,p in raw_files:
    top = rel.split("/")[0] if "/" in rel else "raiz"
    if "/" not in rel:
        top = "raiz"
    groups[top]["n"] += 1
    groups[top]["size"] += p.stat().st_size

proc_files = sorted([p for p in PROC.iterdir() if p.name != ".gitkeep"], key=lambda x:x.name)

def tabular_shape(p):
    ext = p.suffix.lower()
    try:
        if ext == ".csv":
            df = pd.read_csv(p, dtype=str)
            return f"{len(df)}×{len(df.columns)}"
        if ext == ".json":
            try:
                with open(p, encoding="utf-8") as fh:
                    obj = json.load(fh)
                if isinstance(obj, list):
                    # try cols from first dict
                    cols = len(obj[0]) if obj and isinstance(obj[0], dict) else 0
                    return f"{len(obj)}×{cols}" if cols else f"{len(obj)} (lista)"
                if isinstance(obj, dict):
                    # common containers
                    for key in ("data","items","records","rows"):
                        if key in obj and isinstance(obj[key], list):
                            arr = obj[key]
                            cols = len(arr[0]) if arr and isinstance(arr[0], dict) else 0
                            return f"{len(arr)}×{cols}" if cols else f"{len(arr)} (lista)"
                    return f"dict ({len(obj)} claves)"
            except Exception:
                pass
            return "JSON"
        if ext in (".geojson",):
            return "GeoJSON"
    except Exception:
        pass
    return "—"

lines = []
lines.append("# Inventario de datos — bigdata-vivienda-euskadi")
lines.append("")
lines.append("> Regenerado 2026-10-29 a partir de inspección automatizada (solo lectura) sobre `data/raw/` y `data/procesado/`.")
lines.append(f"> Archivos en `data/raw/`: **{len(raw_files)}** (excluye marcador `.FROZEN`). Archivos en `data/procesado/`: **{len(proc_files)}**.")
lines.append("")
lines.append("## 1. Resumen")
lines.append("")
lines.append(f"- Archivos raw: {len(raw_files)}")
lines.append(f"- Archivos procesado: {len(proc_files)}")
lines.append(f"- Tamaño raw: {sum(p.stat().st_size for _,p in raw_files)/1024/1024:.1f} MB")
lines.append(f"- Tamaño procesado: {sum(p.stat().st_size for p in proc_files)/1024/1024:.1f} MB")
lines.append("")
lines.append("## 2. Inventario `data/raw/` por grupo")
lines.append("")
lines.append("| Grupo | Archivos | Tamaño (MB) |")
lines.append("|---|---:|---:|")
for g in sorted(groups):
    lines.append(f"| `{g}` | {groups[g]['n']} | {groups[g]['size']/1024/1024:.1f} |")
lines.append(f"| **Total** | **{len(raw_files)}** | **{sum(p.stat().st_size for _,p in raw_files)/1024/1024:.1f}** |")
lines.append("")
lines.append("## 3. Inventario `data/procesado/` (93 archivos)")
lines.append("")
lines.append("| Archivo | Tipo | Tamaño (KB) | Filas×Cols |")
lines.append("|---|---|---:|---:|")
for p in proc_files:
    shape = tabular_shape(p)
    lines.append(f"| `{p.name}` | {p.suffix} | {size_kb(p):.1f} | {shape} |")
lines.append("")
lines.append("## 4. Archivos nuevos (procesado) destacados")
lines.append("")
new = ["areas_funcionales_municipios.csv","municipio_area_funcional_ecvi.csv","poblacion_joven_municipal.csv","municipios_faltantes_93.csv","emancipacion_tier3_93.csv","analisis_variables_base.csv"]
for name in new:
    p = (RAW/name) if (RAW/name).exists() else (PROC/name)
    shape = tabular_shape(p)
    lines.append(f"- `{p.relative_to(BASE).as_posix()}` — {shape}")
lines.append("")
lines.append("## 5. Notas")
lines.append("")
lines.append("- `data/raw/` no se modificó (solo lectura). El marcador `.FROZEN` se excluye del conteo.")
lines.append("- Los archivos procesados incluyen normalizados, limpios y derivados (Fase 1 + Tier2/Tier3).")
lines.append("- Ver `docs/trazabilidad_datos.md` para el mapeo transformación → entrada/salida.")
lines.append("")

out = "\n".join(lines)
Path("docs/inventario_datos.md").write_text(out, encoding="utf-8")
print("written", len(lines), "lines")
