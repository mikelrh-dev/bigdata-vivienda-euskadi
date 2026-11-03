import pandas as pd, numpy as np, json
from pathlib import Path
R=Path("data/raw")
def loadcsv(name): return pd.read_csv(R/name, dtype=str, encoding="utf-8-sig")
dim=loadcsv("dim_municipios.csv")
rc=loadcsv("renta_municipal_completa.csv")
alq=loadcsv("alquiler_municipal.csv")
dc=loadcsv("distancias_capitales_252.csv")
ud=loadcsv("udalmap_empleo_corregido.csv")
pe=loadcsv("eustat_poblacion_edad.csv")
re=loadcsv("eustat_renta_edad.csv")
rm=loadcsv("eustat_renta_municipal.csv")

# normalize codes
for df in (dim, rc, dc, ud):
    if "codigo_ine" in df.columns:
        df["codigo_ine"]=df["codigo_ine"].astype(str).str.zfill(5)
# alquiler code
alq["codigo_ine"]=alq["codigo_ine"].astype(str).str.zfill(5)

# Merge base
base = dim[["codigo_ine","nombre_canonico","territorio","tipologia_mercado","n_anuncios","tiene_alquiler_oficial"]].copy()
base = base.merge(rc[["codigo_ine","renta_eustat","renta_hogar","renta_atlas","renta_joven_estimada_16_29"]], on="codigo_ine", how="left")
base = base.merge(ud[["codigo_ine","tasa_actividad_pct","tasa_ocupacion_pct","tasa_paro_lanbide_pct","tasa_ocupacion_juvenil_16_24_pct","trabaja_fuera_pct","afiliacion_ss_16_24_pct","renta_familiar_eur","renta_personal_total_eur","renta_personal_disponible_eur","superficie_media_m2","antiguedad_media_anyos"]], on="codigo_ine", how="left")
base = base.merge(dc[["codigo_ine","dist_bilbao_km","dist_donostia_km","dist_vitoria_km","capital_mas_cercana","dist_centroide_comarca_km"]], on="codigo_ine", how="left")

# alquiler municipal: first row per municipio
alq1 = alq.drop_duplicates("codigo_ine", keep="first")
base = base.merge(alq1[["codigo_ine","renta_media_eur_m2_media","cuantia_media_eur_mes_media","superficie_media_m2_media"]], on="codigo_ine", how="left", suffixes=("","_alq"))

# numeric
for c in ["renta_eustat","renta_hogar","renta_atlas","renta_joven_estimada_16_29","tasa_actividad_pct","tasa_ocupacion_pct","tasa_paro_lanbide_pct","tasa_ocupacion_juvenil_16_24_pct","trabaja_fuera_pct","afiliacion_ss_16_24_pct","renta_familiar_eur","renta_personal_total_eur","renta_personal_disponible_eur","superficie_media_m2","antiguedad_media_anyos","dist_bilbao_km","dist_donostia_km","dist_vitoria_km","dist_centroide_comarca_km","renta_media_eur_m2_media","cuantia_media_eur_mes_media","superficie_media_m2_media"]:
    base[c]=pd.to_numeric(base[c], errors="coerce")

print("BASE shape", base.shape)
print("coverage:")
for c in ["renta_eustat","renta_hogar","renta_atlas","renta_joven_estimada_16_29","tasa_paro_lanbide_pct","tasa_ocupacion_juvenil_16_24_pct","renta_media_eur_m2_media","cuantia_media_eur_mes_media","dist_centroide_comarca_km"]:
    print(f"  {c}: {base[c].notna().sum()}/252")

# alquiler anual (€/mes *12) and effort rate
base["alquiler_anual"]=base["cuantia_media_eur_mes_media"]*12
base["esfuerzo_renta_hogar"]=base["alquiler_anual"]/base["renta_hogar"]
base["esfuerzo_renta_eustat"]=base["alquiler_anual"]/base["renta_eustat"]
base["esfuerzo_renta_joven"]=base["alquiler_anual"]/base["renta_joven_estimada_16_29"]

print("\n=== Correlaciones Pearson (municipios con alquiler oficial) ===")
mask=base["renta_media_eur_m2_media"].notna()
print("n con alquiler oficial:", mask.sum())
vars_list=["renta_eustat","renta_hogar","renta_atlas","renta_joven_estimada_16_29","tasa_actividad_pct","tasa_ocupacion_pct","tasa_paro_lanbide_pct","tasa_ocupacion_juvenil_16_24_pct","trabaja_fuera_pct","afiliacion_ss_16_24_pct","dist_bilbao_km","dist_donostia_km","dist_vitoria_km","dist_centroide_comarca_km","superficie_media_m2"]
for v in vars_list:
    r=base.loc[mask, v].corr(base.loc[mask,"renta_media_eur_m2_media"])
    print(f"  {v:35s} r={r:.4f}")
print("corr renta_media_eur_m2 vs cuantia_media_eur_mes:", base.loc[mask,"renta_media_eur_m2_media"].corr(base.loc[mask,"cuantia_media_eur_mes_media"]))
print("corr renta_hogar vs renta_eustat:", base["renta_hogar"].corr(base["renta_eustat"]))

print("\n=== Descriptivos renta ===")
print(base[["renta_eustat","renta_hogar","renta_atlas","renta_joven_estimada_16_29"]].describe().to_string())
print("\n=== Descriptivos alquiler ===")
print(base[["cuantia_media_eur_mes_media","renta_media_eur_m2_media","alquiler_anual"]].describe().to_string())
print("\n=== Descriptivos esfuerzo ===")
print(base[["esfuerzo_renta_hogar","esfuerzo_renta_eustat","esfuerzo_renta_joven"]].describe().to_string())

print("\n=== Por territorio ===")
print(base.groupby("territorio")[["renta_hogar","renta_eustat","renta_joven_estimada_16_29","cuantia_media_eur_mes_media","tasa_paro_lanbide_pct","tasa_ocupacion_juvenil_16_24_pct"]].median().to_string())

# población por edad municipal?
print("\n=== Ambitos unicos población (sample) ===")
print("n ambitos unicos:", pe["ámbitos territoriales"].nunique())
# filter municipios: codes length 4/5 and province prefix
pe["code"]=pe["ámbitos territoriales"].astype(str).str.zfill(5)
mun_pe=pe[pe["code"].str[:2].isin(["01","20","48"]) & (pe["code"].str.len().isin([4,5]))]
print("muni-level rows:", len(mun_pe), "unique municipios:", mun_pe["code"].nunique())
print("grupos edad:", pe["grandes grupos de edad cumplida__etiqueta"].unique().tolist())
# latest period
print("latest periodo:", pe["periodo"].max())
# total population CA
tot=pe[(pe["ámbitos territoriales"]=="00001")&(pe["grandes grupos de edad cumplida__etiqueta"]=="Total")&(pe["sexo__etiqueta"]=="Total")].sort_values("periodo")
print(tot.tail(3).to_string())
# ratio joven 20-64? not precise
# Save base
base.to_csv(R/"../procesado/analisis_variables_base.csv", index=False, encoding="utf-8-sig")
print("\nsaved base")
# correlation matrix among key vars
corr_cols=["renta_hogar","renta_eustat","renta_joven_estimada_16_29","renta_media_eur_m2_media","cuantia_media_eur_mes_media","tasa_ocupacion_juvenil_16_24_pct","tasa_paro_lanbide_pct","dist_centroide_comarca_km","afiliacion_ss_16_24_pct"]
print("\n=== Corr matrix ===")
print(base[corr_cols].corr().round(3).to_string())
