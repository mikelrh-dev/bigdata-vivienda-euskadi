import duckdb
con = duckdb.connect()

print("=== RESIDENCIAL ===")
r = con.execute("""
SELECT COUNT(*) AS n, COUNT(DISTINCT codigo_ine) AS muns,
       MEDIAN(precio_eur/superficie_m2) AS mediana_pm2,
       MIN(precio_eur/superficie_m2) AS min_pm2,
       MAX(precio_eur/superficie_m2) AS max_pm2,
       MEDIAN(precio_eur) AS mediana_precio, MEDIAN(superficie_m2) AS mediana_sup
FROM read_csv_auto('data/procesado/anuncios_vivienda_residencial.csv')
""").fetchdf()
print(r.to_string(index=False))

print("\n=== MUNICIPIOS SIN ANUNCIOS RESIDENCIALES ===")
g = con.execute("""
SELECT d.codigo_ine, d.nombre_canonico, d.territorio
FROM read_csv_auto('data/procesado/dim_municipios.csv') d
LEFT JOIN (SELECT DISTINCT codigo_ine FROM read_csv_auto('data/procesado/anuncios_vivienda_residencial.csv')) a
  ON d.codigo_ine = a.codigo_ine
WHERE a.codigo_ine IS NULL
""").fetchdf()
print(f"Total: {len(g)}")
print(g.to_string(index=False))

print("\n=== DIM MUNICIPIOS ===")
d = con.execute("SELECT COUNT(*) AS n, COUNT(DISTINCT codigo_ine) AS uniq FROM read_csv_auto('data/procesado/dim_municipios.csv')").fetchdf()
print(d.to_string(index=False))

print("\n=== HABITACIONES ===")
h = con.execute("""
SELECT COUNT(*) AS n, COUNT(DISTINCT codigo_ine) AS muns,
       MEDIAN(precio_eur) AS mediana_precio, MEDIAN(superficie_m2) AS mediana_sup
FROM read_csv_auto('data/procesado/anuncios_habitaciones_unificados.csv')
""").fetchdf()
print(h.to_string(index=False))

print("\n=== TOP MUNICIPIOS POR ANUNCIOS RESIDENCIALES ===")
top = con.execute("""
SELECT codigo_ine, COUNT(*) AS n
FROM read_csv_auto('data/procesado/anuncios_vivienda_residencial.csv')
GROUP BY codigo_ine ORDER BY n DESC LIMIT 10
""").fetchdf()
print(top.to_string(index=False))
