from storage.mongo import get_collection

municipios = get_collection('municipios')
anuncios = get_collection('anuncios')

pipeline = [
    {'$lookup': {'from': 'anuncios', 'localField': '_id', 'foreignField': 'ubicacion.codigo_ine', 'as': 'anuncios'}},
    {'$addFields': {'n_anuncios': {'$size': '$anuncios'}}},
    {'$project': {'_id': 1, 'nombre_canonico': 1, 'territorio': 1, 'n_anuncios': 1}},
    {'$sort': {'territorio': 1, 'nombre_canonico': 1}}
]

resultados = list(municipios.aggregate(pipeline))

def contar_palabras(nombre):
    if not nombre:
        return 0
    norm = nombre.replace('/', ' ').replace('-', ' ').replace('_', ' ')
    return len([p for p in norm.split() if p])

stats = {}
for m in resultados:
    nombre = m.get('nombre_canonico') or m.get('_id')
    n_pal = contar_palabras(nombre)
    n_ads = m.get('n_anuncios', 0)
    territorio = m.get('territorio', '?')
    
    if n_pal not in stats:
        stats[n_pal] = {'total': 0, 'con': 0, 'sin': 0, 'municipios': []}
    
    stats[n_pal]['total'] += 1
    if n_ads > 0:
        stats[n_pal]['con'] += 1
    else:
        stats[n_pal]['sin'] += 1
    stats[n_pal]['municipios'].append({'codigo': m['_id'], 'nombre': nombre, 'territorio': territorio, 'n_anuncios': n_ads})

print('MUNICIPIOS POR NÚMERO DE PALABRAS:')
for n_pal in sorted(stats.keys()):
    s = stats[n_pal]
    print(f'  {n_pal} palabra(s): {s["total"]} municipios (con: {s["con"]}, sin: {s["sin"]})')

print()
print('DETALLE 2+ PALABRAS:')
for n_pal in sorted([k for k in stats.keys() if k >= 2]):
    s = stats[n_pal]
    print(f'\n--- {n_pal} palabras ({s["total"]}) ---')
    for m in s['municipios']:
        estado = '✓' if m['n_anuncios'] > 0 else '✗'
        print(f'  {estado} {m["codigo"]} | {m["nombre"]:40s} | {m["territorio"]:12s} | n={m["n_anuncios"]}')

total = len(resultados)
compuestos = sum(s['total'] for n_pal, s in stats.items() if n_pal >= 2)
compuestos_con = sum(s['con'] for n_pal, s in stats.items() if n_pal >= 2)
compuestos_sin = sum(s['sin'] for n_pal, s in stats.items() if n_pal >= 2)

print(f'\nRESUMEN: Total={total}, Compuestos={compuestos} ({compuestos/total*100:.1f}%), Con={compuestos_con}, Sin={compuestos_sin}')