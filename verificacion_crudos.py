"""Verificación aceptación fase crudos (sin proxys, sin imputar)."""
from pathlib import Path
import pandas as pd
RAW = Path("data/raw")
ok = True
def check(name, cond, det=""):
    global ok
    print(("PASS" if cond else "FAIL"), name, det)
    if not cond: ok = False

dim = pd.read_csv(RAW/"dim_municipios.csv", dtype=str, encoding="utf-8-sig")
dim["codigo_ine"] = dim["codigo_ine"].str.strip().str.zfill(5)
check("dim 252/252 len5", len(dim)==252 and (dim["codigo_ine"].str.len()==5).all(),
      f"{len(dim)} filas")
check("dim 0 bad_pref", (~dim["codigo_ine"].str[:2].isin(["01","20","48"])).sum()==0,
      f"prefs {dim['codigo_ine'].str[:2].value_counts().to_dict()}")

alq = pd.read_csv(RAW/"alquiler_municipal.csv", dtype=str, encoding="utf-8-sig")
alq["codigo_ine"] = alq["codigo_ine"].str.strip().str.zfill(5)
check("alquiler 159 mun", alq["municipio"].nunique()==159, f"{alq['municipio'].nunique()} mun, {len(alq)} filas distrito")

em = pd.read_csv(RAW/"emal_fianzas_ampliado.csv", dtype=str, encoding="utf-8-sig")
check("emal ampliado 73 + n_muestral", em["codigo_ine"].nunique()==73 and "n_muestral" in em.columns and "tipo_fuente" in em.columns,
      f"{em['codigo_ine'].nunique()} mun")

larga = pd.read_csv(RAW/"anuncios_fotocasa_larga.csv", dtype=str, encoding="utf-8-sig", low_memory=False)
temp = pd.read_csv(RAW/"anuncios_fotocasa_temporal.csv", dtype=str, encoding="utf-8-sig", low_memory=False)
for n, df in [("larga", larga), ("temp", temp)]:
    df["eurm2"] = pd.to_numeric(df["precio_eur"], errors="coerce")/pd.to_numeric(df["superficie_m2"], errors="coerce")
    df = df[(df["eurm2"]>0)&(df["eurm2"]<200)]
    print(f"  fotocasa {n}: n={len(df)} mediana={df['eurm2'].median():.2f}")
check("fotocasa split 167/304", len(larga)==167 and len(temp)==304, f"{len(larga)}/{len(temp)}")

pi = pd.read_csv(RAW/"anuncios_pisos_busqueda.csv", dtype=str, encoding="utf-8-sig", low_memory=False)
check("pisos ambito_busqueda", "ambito_busqueda" in pi.columns and "es_municipio_verificado" in pi.columns,
      f"{len(pi)} filas, {pi['ambito_busqueda'].nunique()} ambitos")

re = pd.read_csv(RAW/"anuncios_realtyapi.csv", dtype=str, encoding="utf-8-sig")
check("realtyapi 3 capitales (techo sin creditos)", re["municipio"].nunique()==3, f"{re['municipio'].nunique()} mun, {len(re)} filas")

rc = pd.read_csv(RAW/"renta_municipal_completa.csv", dtype=str, encoding="utf-8-sig")
check("renta origen transparente", set(rc["renta_origen"].unique())=={"Eustat+INE_Atlas"} and len(rc)==252,
      f"{rc['renta_origen'].value_counts().to_dict()}")

tr = pd.read_csv(RAW/"transporte_paradas_municipio.csv", dtype=str, encoding="utf-8-sig")
osrm = pd.read_csv(RAW/"osrm_tiempos_capitales.csv", dtype=str, encoding="utf-8-sig")
hav = pd.read_csv(RAW/"distancias_haversine_252.csv", dtype=str, encoding="utf-8-sig")
check("transporte 252", len(tr)==252, f"{len(tr)}")
check("OSRM 252", len(osrm)==252, f"{len(osrm)}")
check("haversine 63504", len(hav)==63504, f"{len(hav)}")

print("RESULTADO:", "OK" if ok else "PENDIENTE (ver FAIL)")
raise SystemExit(0 if ok else 1)
