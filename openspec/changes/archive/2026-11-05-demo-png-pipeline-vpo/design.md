# Design: demo-png-pipeline-vpo

## D-01 — PNG: escribir bytes, no rutas

Traza reproducida:

```
File ".../matplotlib/image.py", line 1729, in imsave
    image.save(fname, **pil_kwargs)
File ".../PIL/Image.py", line 2707, in save
    fp = builtins.open(filename, "w+b")
OSError: [Errno 22] Invalid argument: 'data\\resultados\\g5_esfuerzo_robustos.png'
```

El mismo `open(..., "w+b")` funciona desde Python puro, así que el fallo está
en la ruta relativa que PIL recibe de matplotlib en Windows. Se guarda en
memoria (`BytesIO`) y se escribe con `Path.write_bytes`, que resuelve la ruta
con la API de Python y da un error legible si el sistema la rechaza.

*Alternativa rechazada:* `os.chdir` o rutas absolutas mágicas. No atacan la
causa y rompen la portabilidad.

## D-02 — Novena pipeline sin CSV nuevo

`pipeline_vpo_terminadas` agrega `vpo_municipal`:

```
$match (vpo no nulo) → $lookup municipios → $unwind → $project → $sort
```

Devuelve 251 filas (Usansolo sin dato). Se registra en `PIPELINE_ORDER` para
que `huella_resultados` la cubra, pero no se añade a `EXPORTS_5`: el contrato
de 5 CSV canónicos no cambia y se evita tocar el formato de la defensa.

## D-03 — Guion: dos cifras nuevas, ninguna promesa nueva

Se añaden la sensibilidad (oficial 26,61 vs IDW 25,37; intervalos solapados
Bilbao–Donostia) y la VPO de flujo (251/252). No se introduce ningún ranking
nuevo: Getxo y Vitoria siguen a un anuncio de distancia.

## D-04 — Demo cronometrada

Se ejecuta la secuencia real y se anotan tiempos y salidas. No se inventa un
runbook aparte: el guion ya contiene el orden y el verify-report guarda la
evidencia de la ejecución.
