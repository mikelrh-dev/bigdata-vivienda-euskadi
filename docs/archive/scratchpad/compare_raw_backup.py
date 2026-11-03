import hashlib, json, os
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

print("RAW files:", len(raw_files))
print("BACKUP files:", len(bak_files))
print("Solo en RAW:", sorted(raw_files - bak_files))
print("Solo en BACKUP:", sorted(bak_files - raw_files))
common = sorted(raw_files & bak_files)
print("Comunes:", len(common))

identical = []
diff = []
for rel in common:
    rp = RAW/rel; bp = BACKUP/rel
    if sha(rp)==sha(bp):
        identical.append(rel)
    else:
        diff.append(rel)
print("Identical (hash):", len(identical))
print("Different (hash):", len(diff))
print("\nDIFERENTES:")
for rel in diff:
    rp=RAW/rel; bp=BACKUP/rel
    print(f"  {rel}: raw={rp.stat().st_size}B backup={bp.stat().st_size}B")
EOF