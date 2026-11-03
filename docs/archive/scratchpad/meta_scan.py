import os, json, glob
import pandas as pd

ROOT="C:/Users/mikel/Documents/bigdata-vivienda-euskadi"
DATA=os.path.join(ROOT,"data")
OUT="C:/Users/mikel/AppData/Local/hermes/cache/scratch/meta_scan.json"

def size(path): return os.path.getsize(path)

def try_read(path):
    ext=os.path.splitext(path)[1].lower()
    try:
        if ext=='.csv':
            df=pd.read_csv(path, low_memory=False)
            return df, "csv"
        if ext=='.json':
            with open(path,encoding='utf-8') as f:
                j=json.load(f)
            if isinstance(j, list):
                df=pd.json_normalize(j)
            elif isinstance(j, dict):
                # find largest list
                best=None; bestk=None
                for k,v in j.items():
                    if isinstance(v, list) and (best is None or len(v)>len(best)):
                        best=v; bestk=k
                if best is not None and len(best)>0:
                    try:
                        df=pd.json_normalize(best)
                    except Exception:
                        df=pd.DataFrame([j])
                else:
                    df=pd.DataFrame([j])
            else:
                df=pd.DataFrame(j)
            return df, "json"
        if ext in ('.xlsx','.xls'):
            xl=pd.ExcelFile(path)
            sheets=xl.sheet_names
            # read first sheet with data
            df=xl.parse(sheets[0])
            return df, f"xlsx(sheet={sheets[0]}; sheets={sheets})"
        if ext=='.geojson':
            with open(path,encoding='utf-8') as f:
                j=json.load(f)
            feats=j.get('features',[])
            props=[f.get('properties',{}) for f in feats]
            df=pd.DataFrame(props)
            return df, "geojson"
    except Exception as e:
        return None, f"ERR: {type(e).__name__}: {str(e)[:120]}"
    return None, "unsupported"

files=[]
for root,_,fs in os.walk(DATA):
    for fn in fs:
        files.append(os.path.join(root,fn))
files=sorted(files)

records=[]
for path in files:
    rel=os.path.relpath(path, ROOT).replace("\\","/")
    rec={"rel":rel,"size":size(path),"ext":os.path.splitext(path)[1].lower()}
    df,info=try_read(path)
    rec["read_info"]=info
    if df is not None and isinstance(df,pd.DataFrame):
        rec["rows"]=int(len(df))
        rec["cols"]=int(len(df.columns))
        rec["columns"]=list(df.columns)
        # null counts
        nulls={}
        for c in df.columns:
            n=int(df[c].isna().sum())
            if n>0:
                nulls[c]=n
        rec["nulls"]=nulls
        # muni-like columns coverage
        muni_cols=[]
        for c in df.columns:
            cl=str(c).lower()
            if any(k in cl for k in ['municip','ine','cod_','territor','nombre']):
                muni_cols.append(c)
        rec["muni_cols"]=muni_cols
        # numeric summary for potential outliers: count of values beyond 3 std for each numeric col (sample)
        out={}
        for c in df.columns:
            if pd.api.types.is_numeric_dtype(df[c]):
                s=df[c].dropna()
                if len(s)>=10:
                    m=s.mean(); sd=s.std()
                    if sd and sd>0:
                        o=int(((s-m).abs()>3*sd).sum())
                        if o>0:
                            out[c]=o
        rec["outliers_3sd"]=out
    else:
        rec["rows"]=None; rec["cols"]=None; rec["columns"]=None; rec["nulls"]=None; rec["muni_cols"]=None; rec["outliers_3sd"]=None
    records.append(rec)

with open(OUT,"w",encoding="utf-8") as f:
    json.dump(records,f,ensure_ascii=False,indent=1)
print("files:",len(records))
# summary by ext
from collections import Counter
print(Counter(r["ext"] for r in records))
