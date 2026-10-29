# Genera data/procesado/municipio_area_funcional_ecvi.csv
# Cruza municipio -> area funcional (GeoEuskadi) con ECVI compraventa.
# Regla bronce: solo lectura; escribe en procesado.

import pandas as pd
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
PROC = BASE / "data" / "procesado"

# 1. Correspondencia municipio -> area funcional
afm = pd.read_csv(RAW / "areas_funcionales_municipios.csv", dtype=str, encoding="utf-8-sig")
afm["codigo_ine"] = afm["codigo_ine"].astype(str).str.zfill(5)

# 2. ECVI (area funcional)
ecvi = pd.read_csv(PROC / "ecvi_compraventa_limpio.csv", dtype=str, encoding="utf-8-sig")
ecvi_af = ecvi[ecvi["ambito_tipo"] == "area_funcional"].copy()

# mapeo nombre area funcional (GeoEuskadi) -> nombre_ambito (ECVI)
mapa = {
    "ALTO DEBA": "12 - A.F. de Alto Deba",
    "ARRATIA": "9 - A.F. de Arratia",
    "AYALA": "11 - A.F. de Ayala",
    "BAJO DEBA": "7 - A.F. de Bajo Deba",
    "BILBAO METROPOLITANO": "4 - A.F. de Bilbao Metropolitano",
    "BUSTURIALDEA-ARTIBAI": "8 - A.F. de Busturialdea-Artibai",
    "DONOSTIALDEA-BAJO BIDASOA": "5 - A.F. de Donostialdea-Bajo Bidasoa",
    "DURANGALDEA": "6 - A.F. de Durangaldea",
    "ENCARTACIONES": "2 - A.F. de Encartaciones",
    "GOIERRI": "3 - A.F. de Goierri",
    "MUNGIALDEA": "13 - A.F. de Mungialdea",
    "RIOJA ALAVESA": "10 - A.F. de Rioja Alavesa",
    "TOLOSALDEA": "14 - A.F. de Tolosaldea",
    "UROLA KOSTA": "15 - A.F. de Urola Kosta",
    "ÁLAVA CENTRAL": "1 - A.F. de Alava Central",
}
afm["nombre_ambito"] = afm["area_funcional"].map(mapa)

# 3. Merge con ECVI
out = afm.merge(ecvi_af[["nombre_ambito", "trimestre", "precio_medio_total_eur",
                         "precio_m2_libre_eur", "precio_m2_usada_eur"]],
                on="nombre_ambito", how="left")

# 4. Salida
cols = ["codigo_ine", "nombre", "area_funcional", "cod_area_funcional",
        "nombre_ambito", "trimestre", "precio_medio_total_eur",
        "precio_m2_libre_eur", "precio_m2_usada_eur"]
out = out[cols].sort_values("codigo_ine").reset_index(drop=True)
out["codigo_ine"] = out["codigo_ine"].astype(str).str.zfill(5)

dest = PROC / "municipio_area_funcional_ecvi.csv"
out.to_csv(dest, index=False, encoding="utf-8-sig")
print("Generado " + str(dest) + ": " + str(len(out)) + " filas")
print("sin precio:", out["precio_medio_total_eur"].isna().sum())
print(out.head(3).to_string(index=False))
