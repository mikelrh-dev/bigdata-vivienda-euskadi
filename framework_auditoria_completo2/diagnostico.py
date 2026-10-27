import json, pandas as pd

pd.set_option('display.width', 200)

# 1. Oferta muestral
fot = pd.read_csv('data/raw/anuncios_fotocasa.csv')
real = pd.read_csv('data/raw/anuncios_realtyapi.csv')
print("=== 1. OFERTA MUESTRAL ===")
print("Fotocasa anuncios:", len(fot), "municipios:", fot['municipio'].nunique())
print("RealtyAPI anuncios:", len(real), "municipios:", real['municipio'].nunique())
print("\nFotocasa por provincia:")
print(fot.groupby('provincia').agg(anuncios=('id_anuncio','count'), municipios=('municipio','nunique')))
fot_sup = fot[fot['superficie_m2'].notna() & (fot['superficie_m2'] > 0)]
counts = fot_sup.groupby('municipio').size()
print("\nFotocasa municipios con n>=5 anuncios con superficie valida:", (counts >= 5).sum(), "de", fot['municipio'].nunique())
print("Municipios con <=3 anuncios (Fotocasa):", (fot.groupby('municipio').size() <= 3).sum(), "de", fot['municipio'].nunique())
print("Municipios con <=2 anuncios:", (fot.groupby('municipio').size() <= 2).sum())
print("\nTop 10 municipios Fotocasa:")
print(fot.groupby('municipio').size().sort_values(ascending=False).head(10).to_string())

# 2. Entity resolution
print("\n=== 2. ENTITY RESOLUTION (join por string normalizado) ===")
renta = pd.read_csv('data/raw/eustat_renta_municipal.csv')
def norm(s):
    s = str(s).strip().lower()
    for a,b in [('á','a'),('é','e'),('í','i'),('ó','o'),('ú','u')]:
        s = s.replace(a,b)
    return s
eustat_mun = set(norm(x) for x in renta['ámbitos territoriales__etiqueta'].dropna().unique())
print("Eustat renta ambitos unicos:", len(eustat_mun))
fot_mun = set(norm(x) for x in fot['municipio'].unique())
print("Fotocasa municipios unicos:", len(fot_mun))
match_fot = fot_mun & eustat_mun
print("Fotocasa match exacto normalizado:", len(match_fot), "de", len(fot_mun), "-> no match:", len(fot_mun - match_fot))
print("No match Fotocasa:", sorted(fot_mun - eustat_mun)[:20])
alq = pd.read_csv('data/raw/alquiler_municipal.csv')
alq_mun = set(norm(x) for x in alq['municipio'].unique())
print("\nAlquiler municipal municipios:", len(alq_mun))
match_alq = alq_mun & eustat_mun
print("Alquiler match exacto:", len(match_alq), "de", len(alq_mun), "-> no match:", len(alq_mun - match_alq))
print("No match Alquiler:", sorted(alq_mun - eustat_mun)[:20])

# 3. Geografia
print("\n=== 3. GEOGRAFIA ===")
dist = json.load(open('data/raw/distancias_municipios.json'))
print("Distancias guardadas:", len(dist), "(total real ~180k)")
pol = json.load(open('data/raw/municipios_gipuzkoa.geojson'))
print("Poligonos Gipuzkoa:", len(pol.get('features', [])))

# 4. Salario
print("\n=== 4. SALARIO ===")
sal = pd.read_csv('data/raw/ine_salarios_edad.csv')
print("Salarios EPA ambito unico:", sal['ambito'].unique())
print("Grupos edad:", list(sal['grupo_edad_o_decil'].dropna().unique()[:10]))
renta_edad = pd.read_csv('data/raw/eustat_renta_edad.csv')
print("Renta por edad ambito (muestra):", list(renta_edad['sexo__etiqueta'].unique()))
print("Renta municipal ambitos (muestra):", list(renta['ámbitos territoriales__etiqueta'].unique()[:5]))

# 5. Incumplimientos
print("\n=== 5. INCUMPLIMIENTOS (verificados por inspeccion de codigo) ===")
print("- 05_fotocasa: NO guarda HTML crudo (solo JSON parseado). Incumple EXTRACCION-01 escenario 'HTML crudo se conserva'.")
print("- 09_realtyapi: literal 'PY' suelto al final (linea 269) -> NameError si se importa.")
print("- 08_pisos: NO extrae superficie_m2 ni habitaciones (solo precio, titulo, subtitulo, enlace, tipo).")
print("- 04_b5m: distancias truncadas a 5000 de ~180k.")
PY