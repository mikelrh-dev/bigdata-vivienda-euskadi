import os, json, glob
import pandas as pd

ROOT="C:/Users/mikel/Documents/bigdata-vivienda-euskadi"
DIM=pd.read_csv(ROOT+"/data/raw/dim_municipios.csv")
codes=set(DIM['codigo_ine'].astype(str).str.strip())
names=set(DIM['nombre_canonico'].astype(str).str.strip().str.lower())
names_norm=set(DIM['nombre_normalizado'].astype(str).str.strip().str.lower())

def norm(s):
    return str(s).strip().lower()

def muni_col(df):
    cands=[]
    for c in df.columns:
        cl=c.lower()
        if any(k in cl for k in ['municip','ine','cod_','territor']):
            cands.append(c)
    return cands

def coverage_count(series):
    # try codes
    vals=series.dropna().astype(str).str.strip()
    code_hits=vals.isin(codes).sum()
    # unique
    uniq_codes=vals[vals.isin(codes)].nunique()
    name_hits=vals.str.lower().isin(names).sum()
    uniq_names=vals[vals.str.lower().isin(names)].nunique()
    name_norm_hits=vals.str.lower().isin(names_norm).sum()
    uniq_norm=vals[vals.str.lower().isin(names_norm)].nunique()
    best=max(uniq_codes,uniq_names,uniq_norm)
    kind = 'code' if uniq_codes==best else ('name' if uniq_names==best else 'norm')
    return best, kind, len(vals.unique())

def load_file(path):
    ext=os.path.splitext(path)[1].lower()
    if ext=='.csv':
        try:
            return pd.read_csv(path, low_memory=False)
        except Exception as e:
            return ("ERR", str(e))
    if ext in ('.json',):
        try:
            with open(path,encoding='utf-8') as f:
                j=json.load(f)
            if isinstance(j, list):
                return pd.json_normalize(j)
            if isinstance(j, dict):
                # find list
                for k,v in j.items():
                    if isinstance(v, list) and len(v)>0:
                        try:
                            return pd.json_normalize(v)
                        except: pass
                # maybe dict of records
                return pd.DataFrame([j])
            return pd.DataFrame(j)
        except Exception as e:
            return ("ERR", str(e))
    if ext in ('.xlsx','.xls'):
        try:
            return pd.read_excel(path)
        except Exception as e:
            return ("ERR", str(e))
    if ext=='.geojson':
        try:
            with open(path,encoding='utf-8') as f:
                j=json.load(f)
            feats=j.get('features',[])
            props=[f.get('properties',{}) for f in feats]
            return pd.DataFrame(props)
        except Exception as e:
            return ("ERR", str(e))
    return None

targets=[]
for root,_,files in os.walk(ROOT+"/data"):
    for fn in files:
        ext=os.path.splitext(fn)[1].lower()
        if ext in ('.csv','.json','.xlsx','.xls','.geojson'):
            targets.append(os.path.join(root,fn))

# filter to raw/procesado
targets=[t for t in targets if ('/data/raw' in t.replace(chr(92),'/')) or ('/data/procesado' in t.replace(chr(92),'/'))]
targets=sorted(targets)

for path in targets:
    rel=os.path.relpath(path, ROOT)
    df=load_file(path)
    if isinstance(df,tuple):
        print(f"\n=== {rel} === ERROR {df[1]}")
        continue
    if df is None:
        continue
    # skip tiny/empty
    print(f"\n=== {rel} === rows={len(df)} cols={len(df.columns)}")
    print("  columns:", list(df.columns)[:40])
    mc=muni_col(df)
    if mc:
        for c in mc:
            try:
                best,kind,uniq=coverage_count(df[c])
                print(f"  muni-col '{c}': unique={uniq} coverage_of_252={best} ({kind})")
            except Exception as e:
                print(f"  muni-col '{c}': err {e}")
