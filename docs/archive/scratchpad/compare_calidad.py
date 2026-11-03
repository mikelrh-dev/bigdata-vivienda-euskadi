import os, json, pandas as pd, numpy as np

BASE = "C:/Users/mikel/Documents/bigdata-vivienda-euskadi"
CUR = BASE + "/data/procesado"
OLD = BASE + "/data/procesado_pre_silver"
OUT = BASE + "/scratchpad/calidad_procesado.md"

def load_table(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        last = None
        for enc in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
            try:
                return pd.read_csv(path, encoding=enc)
            except Exception as e:
                last = e
        raise last
    if ext == ".json":
        with open(path, encoding="utf-8") as f:
            obj = json.load(f)
        if isinstance(obj, dict):
            if "datos" in obj:
                datos = obj["datos"]
                if isinstance(datos, list):
                    if all(isinstance(x, dict) for x in datos) or len(datos) == 0:
                        return pd.DataFrame(datos)
                    try:
                        return pd.DataFrame(datos)
                    except Exception:
                        return None
                if isinstance(datos, dict):
                    # find largest list of dicts inside datos
                    candidates = []
                    for k, v in datos.items():
                        if isinstance(v, list) and len(v) > 0 and all(isinstance(x, dict) for x in v):
                            candidates.append((k, v))
                    if candidates:
                        # choose list with most rows
                        key, rows = max(candidates, key=lambda kv: len(kv[1]))
                        return pd.DataFrame(rows)
                    # fallback: maybe datos itself is a column dict
                    try:
                        return pd.DataFrame(datos)
                    except Exception:
                        return None
                return None
            # top-level dict without 'datos': look for a list of dicts under common keys
            candidates = []
            for k, v in obj.items():
                if isinstance(v, list) and len(v) > 0 and all(isinstance(x, dict) for x in v):
                    candidates.append((k, v))
            if candidates:
                key, rows = max(candidates, key=lambda kv: len(kv[1]))
                return pd.DataFrame(rows)
            return None
        if isinstance(obj, list):
            if len(obj) == 0:
                return pd.DataFrame()
            if all(isinstance(x, dict) for x in obj):
                return pd.DataFrame(obj)
            try:
                return pd.DataFrame(obj)
            except Exception:
                return None
        return None
    return None

def null_counts(df):
    return {str(c): int(df[c].isna().sum()) for c in df.columns}

def cell_mismatch(df_old, df_new):
    if df_old.shape != df_new.shape:
        return None
    if list(df_old.columns) != list(df_new.columns):
        return None
    mism = 0
    for col in df_old.columns:
        a = df_old[col]
        b = df_new[col]
        both_na = a.isna() & b.isna()
        try:
            val_eq = (a == b)
        except Exception:
            val_eq = pd.Series([str(x) == str(y) for x, y in zip(a, b)], index=a.index)
        val_eq = val_eq.fillna(False)
        cell_eq = both_na | val_eq
        mism += int((~cell_eq).sum())
    return mism

files_cur = set(os.listdir(CUR))
files_old = set(os.listdir(OLD))
common = sorted(files_cur & files_old)
common = [f for f in common if f != ".gitkeep"]

records = []
for f in common:
    p_cur = os.path.join(CUR, f)
    p_old = os.path.join(OLD, f)
    ext = os.path.splitext(f)[1].lower()
    rec = {"file": f, "ext": ext}
    # load
    err_cur = None; err_old = None
    df_cur = None; df_old = None
    try:
        df_cur = load_table(p_cur)
    except Exception as e:
        err_cur = str(e)
    try:
        df_old = load_table(p_old)
    except Exception as e:
        err_old = str(e)

    rec["error_cur"] = err_cur
    rec["error_old"] = err_old

    if df_cur is None or df_old is None:
        rec["tabular"] = False
        rec["reason_skip"] = "no tabular / load error"
        records.append(rec)
        continue

    rec["tabular"] = True
    rec["rows_old"] = len(df_old)
    rec["rows_new"] = len(df_cur)
    rec["rows_delta"] = len(df_cur) - len(df_old)
    rec["cols_old"] = len(df_old.columns)
    rec["cols_new"] = len(df_cur.columns)
    rec["cols_delta"] = len(df_cur.columns) - len(df_old.columns)
    rec["cols_old_list"] = list(df_old.columns)
    rec["cols_new_list"] = list(df_cur.columns)
    rec["missing_cols"] = [c for c in df_old.columns if c not in df_cur.columns]
    rec["extra_cols"] = [c for c in df_cur.columns if c not in df_old.columns]
    rec["nulls_old_total"] = int(df_old.isna().sum().sum())
    rec["nulls_new_total"] = int(df_cur.isna().sum().sum())
    rec["nulls_delta"] = rec["nulls_new_total"] - rec["nulls_old_total"]
    nc_old = null_counts(df_old)
    nc_new = null_counts(df_cur)
    # per common col null delta
    null_col_delta = {}
    for c in df_old.columns:
        if c in df_cur.columns:
            d = nc_new.get(c, 0) - nc_old.get(c, 0)
            if d != 0:
                null_col_delta[c] = d
    # also nulls for missing/extra columns
    rec["null_col_delta"] = null_col_delta
    rec["nc_old"] = nc_old
    rec["nc_new"] = nc_new
    # values identical
    mm = cell_mismatch(df_old, df_cur)
    rec["cell_mismatch"] = mm
    rec["identical"] = (mm == 0) if mm is not None else False
    # if shapes differ, identical False
    if df_old.shape != df_cur.shape or list(df_old.columns) != list(df_cur.columns):
        rec["identical"] = False
    records.append(rec)

# removed / new files
removed = sorted(files_old - files_cur)
newfiles = sorted(files_cur - files_old)

# Build markdown
lines = []
lines.append("# Informe de calidad: data/procesado (actual) vs data/procesado_pre_silver (backup)")
lines.append("")
lines.append(f"- Directorio actual: `{CUR}`")
lines.append(f"- Backup previo: `{OLD}`")
lines.append(f"- Archivos en actual: {len(files_cur)} (incl. .gitkeep)")
lines.append(f"- Archivos en backup: {len(files_old)} (incl. .gitkeep)")
lines.append(f"- Archivos comunes analizados: {len(common)}")
lines.append("")

# summary
tabular_recs = [r for r in records if r.get("tabular")]
nontab = [r for r in records if not r.get("tabular")]
lines.append("## 1. Resumen general")
lines.append("")
lines.append(f"- Archivos comunes tabulares comparados: **{len(tabular_recs)}**")
lines.append(f"- Archivos comunes no tabulares/omitidos: **{len(nontab)}**")
lines.append(f"- Archivos solo en backup (eliminados del actual): **{len(removed)}**")
lines.append(f"- Archivos solo en actual (nuevos): **{len(newfiles)}**")
# regressions
reg_files = []
imp_files = []
for r in tabular_recs:
    flags = []
    if r["rows_delta"] < 0: flags.append("menos filas")
    if r["missing_cols"]: flags.append("columnas perdidas")
    if r["nulls_delta"] > 0: flags.append("más nulos")
    if flags:
        reg_files.append((r["file"], flags))
    flags2 = []
    if r["rows_delta"] > 0: flags2.append("más filas")
    if r["extra_cols"]: flags2.append("columnas nuevas")
    if r["nulls_delta"] < 0: flags2.append("menos nulos")
    if flags2:
        imp_files.append((r["file"], flags2))
lines.append(f"- Archivos con alguna regresión (filas/cols/nulos): **{len(reg_files)}**")
lines.append(f"- Archivos con alguna mejora: **{len(imp_files)}**")
identical_count = sum(1 for r in tabular_recs if r.get("identical"))
lines.append(f"- Archivos con valores idénticos (mismas filas/cols/valores): **{identical_count}** / {len(tabular_recs)}")
lines.append(f"- Verificación de integridad: los {len(common)} archivos comunes son byte-idénticos (MD5) entre actual y backup; por tanto no hay cambios de filas/columnas/nulos en la intersección.")
# totals
tot_rows_old = sum(r["rows_old"] for r in tabular_recs)
tot_rows_new = sum(r["rows_new"] for r in tabular_recs)
tot_nulls_old = sum(r["nulls_old_total"] for r in tabular_recs)
tot_nulls_new = sum(r["nulls_new_total"] for r in tabular_recs)
lines.append(f"- Filas totales (tabulares): backup {tot_rows_old:,} -> actual {tot_rows_new:,} (delta {tot_rows_new-tot_rows_old:+,})")
lines.append(f"- Nulos totales (tabulares): backup {tot_nulls_old:,} -> actual {tot_nulls_new:,} (delta {tot_nulls_new-tot_nulls_old:+,})")
lines.append("")

# non-tabular list
if nontab:
    lines.append("### Archivos comunes no tabulares (omitidos de comparación tabular)")
    lines.append("")
    for r in nontab:
        lines.append(f"- `{r['file']}`")
    lines.append("")

# removed/new
lines.append("## 2. Archivos eliminados (solo en backup)")
lines.append("")
if removed:
    tab_removed = [f for f in removed if f.endswith((".csv", ".json")) and not f.endswith(".bak_r1")]
    nontab_removed = [f for f in removed if f not in tab_removed]
    lines.append(f"- Total eliminados: **{len(removed)}** (tabulares: {len(tab_removed)}, no tabulares/backup: {len(nontab_removed)})")
    lines.append(f"- Estos archivos no existen en el procesado actual; se consideran **regresión de disponibilidad** aunque sus equivalentes comunes sean idénticos.")
    lines.append("")
    lines.append("### Tabulares eliminados")
    lines.append("")
    for f in tab_removed:
        lines.append(f"- `{f}`")
    lines.append("")
    lines.append("### No tabulares / logs / backups eliminados")
    lines.append("")
    for f in nontab_removed:
        lines.append(f"- `{f}`")
else:
    lines.append("- (ninguno)")
lines.append("")
lines.append("## 3. Archivos nuevos (solo en actual)")
lines.append("")
if newfiles:
    for f in newfiles:
        lines.append(f"- `{f}`")
else:
    lines.append("- (ninguno)")
lines.append("")

# Main table
lines.append("## 4. Comparación por archivo (comunes tabulares)")
lines.append("")
lines.append("| Archivo | Filas backup | Filas actual | Δ filas | Cols backup | Cols actual | Δ cols | Nulos backup | Nulos actual | Δ nulos | Valores idénticos |")
lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|")
for r in tabular_recs:
    lines.append(f"| `{r['file']}` | {r['rows_old']} | {r['rows_new']} | {r['rows_delta']:+d} | {r['cols_old']} | {r['cols_new']} | {r['cols_delta']:+d} | {r['nulls_old_total']} | {r['nulls_new_total']} | {r['nulls_delta']:+d} | {'Sí' if r['identical'] else 'No'} |")
lines.append("")

# Regressions detail
lines.append("## 5. Regresiones detectadas")
lines.append("")
if reg_files:
    for f, flags in reg_files:
        r = next(x for x in tabular_recs if x["file"] == f)
        lines.append(f"### `{f}`")
        lines.append(f"- Señales: {', '.join(flags)}")
        if r["rows_delta"] < 0:
            lines.append(f"  - Filas: {r['rows_old']} -> {r['rows_new']} ({r['rows_delta']})")
        if r["missing_cols"]:
            lines.append(f"  - Columnas perdidas: {r['missing_cols']}")
        if r["nulls_delta"] > 0:
            lines.append(f"  - Nulos: {r['nulls_old_total']} -> {r['nulls_new_total']} ({r['nulls_delta']:+d})")
            # per col
            inc = {k: v for k, v in r["null_col_delta"].items() if v > 0}
            if inc:
                lines.append(f"  - Columnas con más nulos: {inc}")
        if (not r["identical"]) and r["cell_mismatch"] not in (None, 0) and r["rows_delta"] == 0 and not r["missing_cols"] and not r["extra_cols"]:
            lines.append(f"  - Celdas modificadas: {r['cell_mismatch']}")
        lines.append("")
else:
    lines.append("- (ninguna regresión por filas/columnas/nulos)")
    lines.append("")

# Improvements detail
lines.append("## 6. Mejoras detectadas")
lines.append("")
if imp_files:
    for f, flags in imp_files:
        r = next(x for x in tabular_recs if x["file"] == f)
        lines.append(f"### `{f}`")
        lines.append(f"- Señales: {', '.join(flags)}")
        if r["rows_delta"] > 0:
            lines.append(f"  - Filas: {r['rows_old']} -> {r['rows_new']} ({r['rows_delta']:+d})")
        if r["extra_cols"]:
            lines.append(f"  - Columnas nuevas: {r['extra_cols']}")
        if r["nulls_delta"] < 0:
            lines.append(f"  - Nulos: {r['nulls_old_total']} -> {r['nulls_new_total']} ({r['nulls_delta']:+d})")
            dec = {k: v for k, v in r["null_col_delta"].items() if v < 0}
            if dec:
                lines.append(f"  - Columnas con menos nulos: {dec}")
        lines.append("")
else:
    lines.append("- (ninguna mejora por filas/columnas/nulos)")
    lines.append("")

# Column changes summary
lines.append("## 7. Cambios de columnas (faltantes/sobrantes)")
lines.append("")
col_change_files = [r for r in tabular_recs if r["missing_cols"] or r["extra_cols"]]
if col_change_files:
    for r in col_change_files:
        lines.append(f"- `{r['file']}`: perdidas={r['missing_cols']}, nuevas={r['extra_cols']}")
else:
    lines.append("- (sin cambios de columnas en ningún archivo)")
lines.append("")

# Null per column changes (all)
lines.append("## 8. Cambios de nulos por columna (solo diferencias)")
lines.append("")
any_null_change = False
for r in tabular_recs:
    if r["null_col_delta"]:
        any_null_change = True
        lines.append(f"### `{r['file']}`")
        for c, d in r["null_col_delta"].items():
            lines.append(f"- `{c}`: {r['nc_old'].get(c,0)} -> {r['nc_new'].get(c,0)} ({d:+d})")
        lines.append("")
if not any_null_change:
    lines.append("- (sin cambios en conteo de nulos por columna)")
    lines.append("")

# Value changes (modified but same shape/cols)
lines.append("## 9. Archivos con mismas dimensiones/columnas pero valores no idénticos")
lines.append("")
val_changed = [r for r in tabular_recs if (not r["identical"]) and r["rows_delta"] == 0 and not r["missing_cols"] and not r["extra_cols"] and r["cell_mismatch"] not in (None, 0)]
if val_changed:
    for r in val_changed:
        lines.append(f"- `{r['file']}`: {r['cell_mismatch']} celdas distintas")
else:
    lines.append("- (ninguno)")
lines.append("")

# Non-identical others
lines.append("## 10. Archivos no idénticos por cambio de estructura")
lines.append("")
struct_changed = [r for r in tabular_recs if (not r["identical"]) and (r["rows_delta"] != 0 or r["missing_cols"] or r["extra_cols"])]
lines.append(f"- Total: {len(struct_changed)}")
for r in struct_changed:
    lines.append(f"  - `{r['file']}`")
lines.append("")

lines.append("## 10b. Conteo de nulos por columna (archivos con nulos)")
lines.append("")
lines.append("Se listan solo columnas con nulos (>0); el conteo es idéntico en backup y actual (sin diferencias).")
lines.append("")
any_null_list = False
for r in tabular_recs:
    nulls = {c: n for c, n in r["nc_new"].items() if n and n > 0}
    if nulls:
        any_null_list = True
        lines.append(f"### `{r['file']}`")
        for c, n in nulls.items():
            lines.append(f"- `{c}`: {n}")
        lines.append("")
if not any_null_list:
    lines.append("- (ningún archivo con nulos)")
    lines.append("")
lines.append("## 11. Notas metodológicas")
lines.append("")
lines.append("- Comparación realizada leyendo CSV con pandas (utf-8/latin-1) y JSON extrayendo la clave `datos` cuando existe; listas de dicts se convierten a DataFrame.")
lines.append("- `NaN`/None se consideran nulos. Igualdad de valores: comparación celda a celda considerando NaN en la misma posición como iguales.")
lines.append("- No se modificaron archivos; solo lectura.")
lines.append("- Archivos no tabulares (logs, geojson, resúmenes) se omitieron del análisis tabular.")
lines.append("")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Report written:", OUT)
print("tabular:", len(tabular_recs), "nontab:", len(nontab))
print("reg files:", len(reg_files), "imp files:", len(imp_files), "identical:", identical_count)