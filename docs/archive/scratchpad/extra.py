import pandas as pd, numpy as np, json
from pathlib import Path
R=Path("data/raw"); P=Path("data/procesado")
base=pd.read_csv(P/"analisis_variables_base.csv",dtype=str,encoding="utf-8-sig")
for c in base.columns:
    if c not in ("codigo_ine","nombre_canonico","territorio","tipologia_mercado","capital_mas_cercana"):
        base[c]=pd.to_numeric(base[c],errors="coerce")
# load osrm
os=pd.read_csv(R/"osrm_tiempos_capitales.csv",dtype=str,encoding="utf-8-sig")
os["codigo_ine"]=os["codigo_ine"].str.zfill(5)
for c in os.columns[1:]:
    os[c]=pd.to_numeric(os[c],errors="coerce")
base=base.merge(os,on="codigo_ine",how="left")
# min to nearest capital
base["min_capital"]=base[["minutos_Vitoria-Gasteiz","minutos_Bilbao","minutos_Donostia-San Sebastian"]].min(axis=1)
print("corr alquiler vs min_capital:", base["renta_media_eur_m2_media"].corr(base["min_capital"]))
print("corr alquiler vs ocup_joven:", base["renta_media_eur_m2_media"].corr(base["tasa_ocupacion_juvenil_16_24_pct"]))
print("corr alquiler vs afiliacion:", base["renta_media_eur_m2_media"].corr(base["afiliacion_ss_16_24_pct"]))
print("corr alquiler vs paro:", base["renta_media_eur_m2_media"].corr(base["tasa_paro_lanbide_pct"]))
print("corr renta_hogar vs ocup_joven:", base["renta_hogar"].corr(base["tasa_ocupacion_juvenil_16_24_pct"]))
print("corr renta_hogar vs paro:", base["renta_hogar"].corr(base["tasa_paro_lanbide_pct"]))
# effort by tipologia
print("\nesfuerzo joven by tipologia:")
print(base.groupby("tipologia_mercado")[["esfuerzo_renta_joven","esfuerzo_renta_hogar"]].median().to_string())
# top/bottom effort joven
print("\nTop 10 mayor esfuerzo joven (municipios con alquiler oficial):")
print(base.nlargest(10,"esfuerzo_renta_joven")[["nombre_canonico","territorio","cuantia_media_eur_mes_media","renta_joven_estimada_16_29","esfuerzo_renta_joven","tasa_ocupacion_juvenil_16_24_pct","tasa_paro_lanbide_pct"]].to_string(index=False))
print("\nBottom 10 menor esfuerzo joven:")
print(base.nsmallest(10,"esfuerzo_renta_joven")[["nombre_canonico","territorio","cuantia_media_eur_mes_media","renta_joven_estimada_16_29","esfuerzo_renta_joven","tasa_ocupacion_juvenil_16_24_pct","tasa_paro_lanbide_pct"]].to_string(index=False))
# population young share stats
pe=pd.read_csv(R/"eustat_poblacion_edad.csv",dtype=str,encoding="utf-8-sig")
peL=pe[pe["periodo"]=="20250101"]
muni=peL[peL["ámbitos territoriales"].astype(str).str.zfill(5).str[:2].isin(["01","20","48"]) & (peL["ámbitos territoriales"].astype(str).str.len().isin([4,5]))]
piv=muni.pivot_table(index="ámbitos territoriales",columns="grandes grupos de edad cumplida__etiqueta",values="Población de la C.A. de Euskadi",aggfunc="first")
for c in piv.columns: piv[c]=pd.to_numeric(piv[c],errors="coerce")
piv["share_20_64"]=piv["20 - 64"]/piv["Total"]
print("\npop share 20-64: min/max/mean", piv["share_20_64"].min(), piv["share_20_64"].max(), piv["share_20_64"].mean())
print("municipios con <30% 20-64:", (piv["share_20_64"]<0.3).sum())
print("municipios con <500 hab:", (piv["Total"]<500).sum(), "de 252")
print("municipios con <1000 hab:", (piv["Total"]<1000).sum())
# correlation effort with population size
base2=base.merge(piv[["Total","share_20_64"]],left_on="codigo_ine",right_index=True,how="left")
print("corr cuantia alquiler vs pop total:", base2["cuantia_media_eur_mes_media"].corr(base2["Total"]))
print("corr renta_hogar vs pop total:", base2["renta_hogar"].corr(base2["Total"]))
# OVJ indicators latest
em=pd.read_csv(R/"emancipacion_juventud.csv",sep=";",dtype=str,encoding="utf-8-sig")
latest=em[em["Periodo"]=="2024"]
print("\nOVJ 2024 indicadores clave:")
for ind in ["Tasa de emancipación, según sexo, grupos de edad y TTHH",
            "Edad media de emancipación, según sexo",
            "Coste de acceso a la vivienda libre en alquiler, según sexo, grupos de edad y TTHH",
            "Sobreesfuerzo económico para el pago de la hipoteca o de la renta de alquiler, según sexo, grupos de edad y TTHH"]:
    sub=latest[latest["Indicador"]==ind]
    print("\n",ind)
    print(sub[["Categoría 1-Valor","Valor"]].to_string(index=False))
