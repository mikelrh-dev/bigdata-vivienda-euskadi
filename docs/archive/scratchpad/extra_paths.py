import re, os
text=open("docs/inventario_datos.md",encoding="utf-8").read()
paths=set(p for p in re.findall(r"`([^`]+)`", text) if p.startswith("data/"))
actual=set(os.path.join(r,f).replace(chr(92),"/") for r,_,fs in os.walk("data") for f in fs)
extra=sorted(paths-actual)
print(extra)