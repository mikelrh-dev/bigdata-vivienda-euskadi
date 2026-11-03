import hashlib, json
from pathlib import Path
import pandas as pd

RAW = Path("data/raw")
BACKUP = Path("data/raw_backup_2026-10-29")

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(65536),b''): h.update(c)
    return h.hexdigest()

raw_files = {p.relative_to(RAW).as_posix() for p in RAW.rglob("*") if p.is_file() and p.name not in (".FROZEN",".gitkeep")}
bak_files = {p.relative_to(BACKUP).as_posix() for p in BACKUP.rglob("*") if p.is_file() and p.name not in (".gitkeep",)}
common = sorted(raw_files & bak_files)
diff = [r for r in common if sha(RAW/r)!=sha(BACKUP/r)]

print("DIFERENTES:", len(diff))
for rel in diff:
    rp=RAW/rel; bp=BACKUP/rel
    print("\n" + "="*80)
    print("FILE:", rel)
    print("size raw/backup:", rp.stat().st_size, bp.stat().st_size)
    if rel.endswith(".csv"):
        try:
            dr=pd.read_csv(rp,dtype=str,encoding='utf-8-sig',low_memory=False)
            db=pd.read_csv(bp,dtype=str,encoding='utf-8-sig',low_memory=False)
            print("shape raw/backup:", dr.shape, db.shape)
            print("cols equal:", list(dr.columns)==list(db.columns))
            if list(dr.columns)!=list(db.columns):
                print("  raw cols:", list(dr.columns))
                print("  bak cols:", list(db.columns))
            # compare values (string) for common cols
            common_cols=[c for c in dr.columns if c in db.columns]
            try:
                same = dr[common_cols].fillna("__NA__").astype(str).equals(db[common_cols].fillna("__NA__").astype(str))
                print("values identical (all common cols):", same)
                if not same:
                    # show which cols differ
                    for c in common_cols:
                        if not dr[c].fillna("__NA__").astype(str).equals(db[c].fillna("__NA__").astype(str)):
                            print("  DIFF col:", c)
            except Exception as e:
                print("  compare err:", e)
        except Exception as e:
            print("CSV read err:", e)
    elif rel.endswith(".json"):
        try:
            jr=json.loads(rp.read_text(encoding='utf-8'))
            jb=json.loads(bp.read_text(encoding='utf-8'))
            # if dict with 'datos'
            if isinstance(jr,dict) and 'datos' in jr and isinstance(jb,dict) and 'datos' in jb:
                dr=pd.DataFrame(jr['datos']); db=pd.DataFrame(jb['datos'])
                print("shape datos raw/backup:", dr.shape, db.shape)
                print("cols equal:", list(dr.columns)==list(db.columns))
                common_cols=[c for c in dr.columns if c in db.columns]
                try:
                    same = dr[common_cols].fillna("__NA__").astype(str).equals(db[common_cols].fillna("__NA__").astype(str))
                    print("datos values identical:", same)
                    if not same:
                        for c in common_cols:
                            if not dr[c].fillna("__NA__").astype(str).equals(db[c].fillna("__NA__").astype(str)):
                                print("  DIFF col:", c)
                except Exception as e:
                    print("  compare err:", e)
                # metadata diff
                mr=jr.get('metadata',{}); mb=jb.get('metadata',{})
                meta_diff = {k:(mr.get(k),mb.get(k)) for k in set(mr)|set(mb) if mr.get(k)!=mb.get(k)}
                print("metadata differing keys:", list(meta_diff.keys()))
                if meta_diff:
                    for k,v in list(meta_diff.items())[:5]:
                        print("   ", k, "raw=",str(v[0])[:60], "bak=",str(v[1])[:60])
            else:
                # compare raw json text normalized?
                print("JSON not standard {datos:...}; type:", type(jr).__name__, type(jb).__name__)
        except Exception as e:
            print("JSON read err:", e)
    else:
        print("binary/non-tabular: hash differs, size above")
EOF