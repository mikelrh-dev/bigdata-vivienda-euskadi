import pandas as pd, numpy as np, json
from pathlib import Path
R=Path("data/raw"); P=Path("data/procesado")
pd.set_option("display.width",200)
def load(name):
    p=R/name
    if p.suffix==".csv": return pd.read_csv(p, dtype=str, encoding="utf-8-sig")
    if p.suffix==".json":
        d=json.loads(p.read_text(encoding="utf-8"))
        if isinstance(d,dict) and "datos" in d: d=d["datos"]
        if isinstance(d,dict) and "features" in d: 
            # geojson skip
            pass
        if isinstance(d,list): return pd.DataFrame(d)
        return d
    return None

# dim
dim=load("dim_municipios.csv")
print("dim shape",dim.shape)
print(dim.columns.tolist())
print(dim["territorio"].value_counts())
print("tipologia", dim["tipologia_mercado"].value_counts().to_dict() if "tipologia_mercado" in dim else None)
# renta completa
rc=load("renta_municipal_completa.csv")
print("renta_completa shape",rc.shape)
print(rc.columns.tolist())
print(rc.head(2).T)
# alquiler
alq=load("alquiler_municipal.csv")
print("alquiler shape",alq.shape)
print(alq.columns.tolist())
# distancias capitales 252
dc=load("distancias_capitales_252.csv")
print("dist shape",dc.shape)
print(dc.columns.tolist())
# udalmap corregido
ud=load("udalmap_empleo_corregido.csv")
print("ud shape",ud.shape)
print(ud.columns.tolist())
# poblacion edad
pe=load("eustat_poblacion_edad.csv")
print("pop shape",pe.shape)
print(pe.columns.tolist())
print(pe.head(3))
# renta edad
re=load("eustat_renta_edad.csv")
print("renta_edad shape",re.shape)
print(re.columns.tolist())
print(re.head(3))
# renta municipal eustat
rm=load("eustat_renta_municipal.csv")
print("renta_muni shape",rm.shape)
print(rm.columns.tolist())
print(rm.head(3).to_string())