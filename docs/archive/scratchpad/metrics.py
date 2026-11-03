import pandas as pd, numpy as np, json, os

print("=== SUPERFICIE VALIDA ===")
for name, path in [("Fotocasa","data/procesado/anuncios_fotocasa_filtrado.csv"),
                   ("Pisos","data/procesado/anuncios_pisos_filtrado.csv"),
                   ("RealtyAPI","data/raw/anuncios_realtyapi.csv")]:
    df = pd.read_csv(path)
    sup = df['superficie_m2']
    valid = (sup>=15)&(sup<=300)&(sup.notna())
    if 'habitaciones' in df.columns:
        hab = df['habitaciones'].notna()
    else:
        hab = pd.Series([True]*len(df))
    both = valid & hab
    print(f"{name}: n={len(df)}, surf_valid={(valid.sum()/len(df)*100):.1f}%, surf+hab={(both.sum()/len(df)*100):.1f}%")

print("\n=== OUTLIERS ===")
for name,path in [("Fotocasa","data/procesado/anuncios_fotocasa_filtrado.csv"),
                  ("Pisos","data/procesado/anuncios_pisos_filtrado.csv")]:
    df = pd.read_csv(path)
    out = df['outlier']==True if 'outlier' in df.columns else pd.Series([False]*len(df))
    print(f"{name}: outliers={out.sum()}, max pm2={df['precio_m2_calculado'].max():.2f}")

print("\n=== TEMPORAL VS LARGA (Fotocasa) ===")
fc = pd.read_csv("data/procesado/anuncios_fotocasa_filtrado.csv")
if 'alquiler_temporal' in fc.columns:
    t = fc[fc['alquiler_temporal']==1]['precio_m2_calculado'].median()
    l = fc[fc['alquiler_temporal']==0]['precio_m2_calculado'].median()
    print(f"temporal median pm2={t:.2f}, larga median pm2={l:.2f}, diff={(t/l-1)*100:.1f}%")
    print("NaN temporal:", fc['alquiler_temporal'].isna().sum())

print("\n=== DISTANCIAS ===")
hav = pd.read_csv("data/raw/distancias_haversine_252.csv")
print("haversine rows:", len(hav), "mun:", hav['origen_codigo'].nunique())
cap = pd.read_csv("data/raw/distancias_capitales_252.csv")
print("capitales_252 rows:", len(cap), "mun:", cap['codigo_ine'].nunique() if 'codigo_ine' in cap.columns else 'NA')
raw_cap = pd.read_csv("data/raw/distancias_capitales.csv")
print("raw capitales rows:", len(raw_cap))
code_col = [c for c in raw_cap.columns if 'codigo' in c.lower() or 'ine' in c.lower()]
print("code cols:", code_col)
if code_col:
    c = code_col[0]
    bad = raw_cap[raw_cap[c].astype(str).str.len()==4]
    print("4-digit codes in raw capitales:", len(bad))

print("\n=== PARO ===")
ud = pd.read_csv("data/raw/udalmap_empleo_corregido.csv")
print("udalmap rows:", len(ud))
print("tasa_paro_aprox NaN:", ud['tasa_paro_aprox_pct'].isna().sum() if 'tasa_paro_aprox_pct' in ud.columns else 'col missing')
print("tasa_paro_lanbide valid:", ud['tasa_paro_lanbide_pct'].notna().sum() if 'tasa_paro_lanbide_pct' in ud.columns else 'col missing')
print("lanbide range:", ud['tasa_paro_lanbide_pct'].min(), ud['tasa_paro_lanbide_pct'].max())

print("\n=== PISOS nombre_canonico empty? ===")
pi_raw = pd.read_csv("data/raw/anuncios_pisos.csv")
print("Pisos raw nombre_canonico null:", pi_raw['nombre_canonico'].isna().sum(), "of", len(pi_raw))

print("\n=== HTML CRUDOS ===")
print("Fotocasa HTML files:", len([f for f in os.listdir('data/raw') if f.endswith('.html') and 'fotocasa' in f.lower()]))
EOF