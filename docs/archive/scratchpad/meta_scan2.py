import os, json
import pandas as pd

ROOT="C:/Users/mikel/Documents/bigdata-vivienda-euskadi"
DATA=os.path.join(ROOT,"data")
OUT="C:/Users/mikel/AppData/Local/hermes/cache/scratch/meta_scan2.json"

# dim municipios
DIM=pd.read_csv(os.path.join(ROOT,"data/raw/dim_municipios.csv"))
codes=set(DIM['codigo_ine'].astype(str).str.strip())
names=set(DIM['nombre_canonico'].astype(str).str.strip().str.lower())
names_norm=set(DIM['nombre_normalizado'].astype(str).str.strip().str.lower())
# also names without accents? keep as is

def norm(s): return str(s).strip().lower()

def coverage(series):
    vals=series.dropna().astype(str).str.strip()
    uniq_codes=vals[vals.isin(codes)].nunique()
    uniq_names=vals[vals.str.lower().isin(names)].nunique()
    uniq_norm=vals[vals.str.lower().isin(names_norm)].nunique()
    best=max(uniq_codes,uniq_names,uniq_norm)
    kind='code' if uniq_codes==best else ('name' if uniq_names==best else 'norm')
    return int(best), kind, int(vals.nunique())

def try_read(path):
    ext=os.path.splitext(path)[1].lower()
    try:
        if ext=='.csv':
            # try standard comma
            try:
                df=pd.read_csv(path, low_memory=False)
                if len(df.columns)>2:
                    return df, 'csv'
            except Exception:
                pass
            # semicolon / multi-header
            sample=open(path,encoding='utf-8',errors='replace').read(2000)
            if ';' in sample:
                encs=['utf-8','latin-1']
                candidates=[]
                for enc in encs:
                    for sk in range(0,9):
                        try:
                            df=pd.read_csv(path, sep=';', skiprows=sk, engine='python', encoding=enc, on_bad_lines='skip')
                            if len(df.columns)>=5 and len(df)>0:
                                score=0
                                for c in df.columns:
                                    cl=str(c).lower()
                                    if any(k in cl for k in ['entidad','municip','codigo','comarca','territor','indicador']):
                                        score+=1
                                candidates.append((score,sk,enc,df))
                        except Exception:
                            continue
                if candidates:
                    # prefer highest score, then smallest skiprows
                    candidates.sort(key=lambda x:(-x[0],x[1]))
                    score,sk,enc,df=candidates[0]
                    return df, f'csv (sep=; skiprows={sk}, {enc})'
            # fallback standard
            try:
                df=pd.read_csv(path, low_memory=False)
                return df, 'csv'
            except Exception as e:
                return None, f'ERR: {type(e).__name__}: {str(e)[:100]}'
        if ext=='.json':
            with open(path,encoding='utf-8') as f:
                j=json.load(f)
            if isinstance(j, list):
                if len(j)>0 and all(isinstance(x,dict) for x in j):
                    df=pd.json_normalize(j)
                elif len(j)>0 and all(isinstance(x,str) for x in j):
                    df=pd.DataFrame({'valor':j})
                else:
                    # mixed/empty
                    try:
                        df=pd.json_normalize(j)
                    except Exception:
                        df=pd.DataFrame(j)
            elif isinstance(j, dict):
                best=None
                for k,v in j.items():
                    if isinstance(v, list) and (best is None or len(v)>len(best)):
                        best=v
                if best is not None and len(best)>0 and all(isinstance(x,dict) for x in best):
                    df=pd.json_normalize(best)
                elif best is not None and len(best)>0 and all(isinstance(x,str) for x in best):
                    df=pd.DataFrame({'valor':best})
                else:
                    # maybe dict of records
                    df=pd.DataFrame([j])
            else:
                df=pd.DataFrame(j)
            return df, 'json'
        if ext in ('.xlsx','.xls'):
            xl=pd.ExcelFile(path)
            sheets=xl.sheet_names
            df=xl.parse(sheets[0])
            return df, f'xlsx (sheet1={sheets[0]}; sheets={sheets})'
        if ext=='.geojson':
            with open(path,encoding='utf-8') as f:
                j=json.load(f)
            feats=j.get('features',[])
            props=[f.get('properties',{}) for f in feats]
            df=pd.DataFrame(props)
            return df, 'geojson'
    except Exception as e:
        return None, f'ERR: {type(e).__name__}: {str(e)[:120]}'
    return None, 'unsupported'

files=[]
for root,_,fs in os.walk(DATA):
    for fn in fs:
        files.append(os.path.join(root,fn))
files=sorted(files)

records=[]
for path in files:
    rel=os.path.relpath(path, ROOT).replace("\\","/")
    rec={"rel":rel,"size":os.path.getsize(path),"ext":os.path.splitext(path)[1].lower()}
    df,info=try_read(path)
    rec["read_info"]=info
    if df is not None and isinstance(df,pd.DataFrame):
        rec["rows"]=int(len(df))
        rec["cols"]=int(len(df.columns))
        cols=[str(c) for c in df.columns]
        rec["columns"]=cols
        # nulls
        nulls={}
        total_null=0
        for c in df.columns:
            n=int(df[c].isna().sum())
            if n>0:
                nulls[str(c)]=n
                total_null+=n
        rec["nulls"]=nulls
        rec["total_nulls"]=int(total_null)
        # muni coverage
        muni_cols=[]
        cov={}
        for c in df.columns:
            cl=str(c).lower()
            if any(k in cl for k in ['municip','ine','cod_','territor','nombre']):
                muni_cols.append(str(c))
                try:
                    best,kind,uniq=coverage(df[c])
                    if best>0:
                        cov[str(c)]={"coverage":best,"kind":kind,"unique":uniq}
                except Exception as e:
                    cov[str(c)]={"error":str(e)[:60]}
        rec["muni_cols"]=muni_cols
        rec["coverage"]=cov
        # outliers 3sd for numeric
        out={}
        for c in df.columns:
            if pd.api.types.is_numeric_dtype(df[c]):
                s=df[c].dropna()
                if len(s)>=10:
                    m=s.mean(); sd=s.std()
                    if sd and sd>0:
                        o=int(((s-m).abs()>3*sd).sum())
                        if o>0:
                            out[str(c)]=o
        rec["outliers_3sd"]=out
        # numeric col count
        rec["numeric_cols"]=int(sum(1 for c in df.columns if pd.api.types.is_numeric_dtype(df[c])))
    else:
        rec["rows"]=None; rec["cols"]=None; rec["columns"]=None
        rec["nulls"]=None; rec["total_nulls"]=0
        rec["muni_cols"]=None; rec["coverage"]={}
        rec["outliers_3sd"]=None; rec["numeric_cols"]=0
    records.append(rec)

with open(OUT,"w",encoding="utf-8") as f:
    json.dump(records,f,ensure_ascii=False,indent=1)
print("files",len(records))
