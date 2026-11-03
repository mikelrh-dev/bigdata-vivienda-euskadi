import pandas as pd, numpy as np
from pathlib import Path
R=Path("data/raw")
re=pd.read_csv(R/"eustat_renta_edad.csv", dtype=str, encoding="utf-8-sig")
print("edad etiquetas:", sorted(re["edad__etiqueta"].unique()))
print("tipo renta:", sorted(re["tipo de renta__etiqueta"].unique()))
print("sexo:", sorted(re["sexo__etiqueta"].unique()))
# latest period
print("max periodo:", re["periodo"].max())
latest=re[re["periodo"]==re["periodo"].max()]
# total renta CA by edad
t=latest[(latest["sexo__etiqueta"]=="Total") & (latest["tipo de renta__etiqueta"]=="Renta total")]
print(t[["edad__etiqueta","Renta personal media de la C.A. de Euskadi (euros)"]].to_string())
# ratio 18-29? labels maybe 15-19, 20-24, 25-29
for lab in ["15 - 19","18 - 19","20 - 24","25 - 29","30 - 34","Total"]:
    rows=t[t["edad__etiqueta"]==lab]
    if not rows.empty:
        print(lab, rows["Renta personal media de la C.A. de Euskadi (euros)"].iloc[0])
# renta municipal latest
rm=pd.read_csv(R/"eustat_renta_municipal.csv", dtype=str, encoding="utf-8-sig")
print("\nmuni renta latest period:", rm["periodo"].max())
latestm=rm[rm["periodo"]==rm["periodo"].max()]
print("ambitos len", latestm["ámbitos territoriales"].nunique())
# filter municipios
muni=latestm[latestm["ámbitos territoriales"].astype(str).str.zfill(5).str[:2].isin(["01","20","48"]) & (latestm["ámbitos territoriales"].astype(str).str.len().isin([4,5]))]
print("municipios with renta total latest:", muni[muni["tipo de renta__etiqueta"]=="Renta total"].shape)
print(muni[muni["tipo de renta__etiqueta"]=="Renta total"].head(3).to_string())
# population young ratio
pe=pd.read_csv(R/"eustat_poblacion_edad.csv", dtype=str, encoding="utf-8-sig")
print("\npop latest:", pe["periodo"].max())
peL=pe[pe["periodo"]==pe["periodo"].max()]
# municipal total pop and 20-64 and 0-19
muni_pe=peL[peL["ámbitos territoriales"].astype(str).str.zfill(5).str[:2].isin(["01","20","48"]) & (peL["ámbitos territoriales"].astype(str).str.len().isin([4,5]))]
print("unique muni pop:", muni_pe["ámbitos territoriales"].nunique())
# pivot
piv=muni_pe.pivot_table(index="ámbitos territoriales", columns="grandes grupos de edad cumplida__etiqueta", values="Población de la C.A. de Euskadi", aggfunc="first")
print(piv.head())
piv=muni_pe.pivot_table(index="ámbitos territoriales", columns="grandes grupos de edad cumplida__etiqueta", values="Población de la C.A. de Euskadi", aggfunc="first")
for c in piv.columns: piv[c]=pd.to_numeric(piv[c],errors="coerce")
print(piv.head())
print("share 20-64 mean:", (piv["20 - 64"]/(piv["Total"])).mean())
print("share 0-19 mean:", (piv["0 - 19"]/(piv["Total"])).mean())
print("share >=65 mean:", (piv[">= 65"]/(piv["Total"])).mean())
print("pop total CA 2025:", peL[(peL["ámbitos territoriales"]=="00001")&(peL["grandes grupos de edad cumplida__etiqueta"]=="Total")&(peL["sexo__etiqueta"]=="Total")]["Población de la C.A. de Euskadi"].iloc[0])
print("share 20-64 CA:", int(piv["20 - 64"].sum()), "/", int(piv["Total"].sum()), "=", piv["20 - 64"].sum()/piv["Total"].sum())
# factor check
print("factor 18-24/total:", (1599+8156)/28170)
print("factor 18-29/total:", (1599+8156+20109)/28170)
print("factor 18-34/total:", (1599+8156+20109+25609)/28170)
# OVJ salario joven monthly -> annual
print("OVJ salario joven annual:", 1564*12)
print("Eustat renta joven 18-34?", 25609)
print("INE salario 16-24:", 1372.8*12, "25-34:", 2131.6*12)
# emancipacion file
em=pd.read_csv(R/"emancipacion_juventud.csv", dtype=str, encoding="utf-8-sig")
print("emancipacion shape", em.shape)
print(em.columns.tolist()[:30])
print(em.head(3).to_string())
print("emancipacion resumen json")
import json
rj=json.loads((R/"emancipacion_juventud_resumen.json").read_text(encoding="utf-8"))
print(type(rj), list(rj.keys()) if isinstance(rj,dict) else rj[:2] if isinstance(rj,list) else rj)
