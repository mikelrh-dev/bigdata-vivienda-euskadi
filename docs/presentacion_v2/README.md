# Presentación v2 — deck nuevo (frontend-slides)

Carpeta de salida para una presentación **nueva**, independiente del deck actual
(`docs/presentacion/`, que sigue generándose con `build_presentacion.py` y no se toca).

## Qué hay aquí

- `guion.md` — guion oral slide por slide, con cifras, gráficas, backups y mapa de rúbrica.
- `index.html` — deck completo, **26 diapositivas + 12 de backup**, en cuatro actos:
  2024 oficial → 2026 de oferta → cómo se construyó → límites y cierre. Estilo
  **Swiss Modern**, una sola página, CSS/JS inline, sin red: se abre con doble clic.
- `assets/` — PNG portables. Los del bloque 2026 salen de
  `visuals/assets_presentacion_esfuerzo_mercado_2026.py` (lee los CSV de
  `data/procesado`, no teclea cifras): top20 con IC, histograma, territorio,
  tipología, diferencia de nivel, intervalos, cobertura y los dos mapas.
- `presentacion_v2.pdf` — exportación a 1920×1080, 38 páginas (26 + 12 backups).
- H8b (`H8b_modalidad_mediana_eur_m2.png`) se genera en `run_analisis_mongo.py` desde
  `pipeline_modalidades`, que ahora calcula `mediana_eur_m2` y `mediana_superficie_m2`
  por modalidad. Gold pasa a 55/55.

## Estado de infraestructura (evidencia v11, 2026-11-12)

- MongoDB: **17 colecciones vivas + 15 de backup = 32**; **25 índices**.
- HDFS: **353 objetos** (351 canónicas + `.FROZEN` + `.gitkeep`), 895.597.901 B. El `OPEN` de
  WebHDFS falla por DNS del datanode; el script de recuperación coteja, no restaura.
- Kafka: sin metadata en la comprobación de hoy (`NodeNotReadyError`); la última
  evidencia buena es v8 (352/352, lag 0).
- Gold: **55 artefactos** (24 CSV + 31 PNG).

## Año de cada figura

Toda figura del deck declara su vintage en `config/vintage_figuras.yaml`. El PNG
lleva la etiqueta impresa abajo a la derecha (`Datos: 2024`, `Datos: 2026`,
`Datos: 2024 + 2026 (no comparable)`) y el pie de la diapositiva lo repite, para
que no haya que adivinar el año ni en pantalla ni en el PDF.

- 2024 = alquiler Eustat Bizilagun + renta INE Atlas (ancla oficial).
- 2026 = anuncios Fotocasa/Pisos/RealtyAPI (capa de oferta).
- `mixto` = mezcla declarada; se dice «no comparable» en voz alta, nunca «serie».
- `acumulado` = registro Etxebide: no hay un año único. Solo las promociones
  terminadas traen fecha de sorteo (2001-2014); las de en curso, convenio y
  proyecto no la traen, así que el sello declara el rango y la limitación.

```bash
.venv/Scripts/python.exe scripts/verificar_vintage_figuras.py
```

El mismo comando del gold (`run_pipeline.py --fase gold`) copia los 12 PNG
compartidos a `assets/` y los 8 de la memoria a `docs/memoria/figuras`; antes se
copiaban a mano y H2, H8 y P se quedaron atrás.

### VPO: escala común y unidad

La serie `S_serie_vpo_2004_2024.png` ya no tiene un panel propio para
Araba/Álava. El panel izquierdo comparte escala 0-44 ‰ para los cuatro
territorios y el derecho es un zoom declarado 0-14 ‰ para CAE, Bizkaia y
Gipuzkoa. El H5 titula «tasa», no «número de viviendas». No se editan los PNG a
mano: se regeneran desde los scripts y se sincronizan con el deck y la memoria.

```bash
.venv/Scripts/python.exe transform/generar_figuras_N.py
.venv/Scripts/python.exe analysis/run_analisis_mongo.py
.venv/Scripts/python.exe scripts/sincronizar_figuras.py
```

## Cómo se usa

Abrir `index.html` en Chrome. `←` / `→` o clic para navegar; `Ctrl+P` → «Guardar como PDF».
El PDF incluido se generó con Chrome headless:

```
chrome --headless=new --no-pdf-header-footer \
  --print-to-pdf=docs/presentacion_v2/presentacion_v2.pdf \
  file:///.../docs/presentacion_v2/index.html
```

Si cambias una cifra en `guion.md`, actualízala también en `index.html` y vuelve a exportar.
Las cifras canónicas siguen en `data/resultados/*.csv`.

## Regenerar el bloque 2026

```
python scripts/regenerar_capa_2026.py
```

Encadena en orden (fail-fast) los dos `transform/` de 2026, la calibración del
premium, la comparación con denominador común, la diferencia de nivel, cobertura,
validación SERPAVI, mapas, gráficos y assets. Al final imprime el SHA-256 de cada
salida. No toca `data/raw` ni `extract/`, y no modifica el esfuerzo canónico 2024.

Cifras que alimentan el bloque 2026 (diapositivas 9 a 14):

| Dato | Valor | Fuente |
|---|---|---|
| Mediana esfuerzo 2026 (50 mun) | 78,6 % | `esfuerzo_mercado_2026.csv` |
| Anuncios usados / excluidos | 287 / 10 | `_anuncios_2026.py` (conciliado en test) |
| Anuncios > 30 % del salario | 98,3 % | mismo CSV, nivel anuncio |
| Composición oferta 2026 (795 = 594 + 201) | 41 % larga · 34 % temporal · 25 % habitación; 287 = 36 % | `mongo_modalidades.csv` + `anuncios_habitaciones_unificados.csv` |
| Cobertura población 18-34 | 71,2 % | `data/resultados/cobertura_representatividad_2026.csv` |
| 2024 oficial → 2026 oferta (misma base) | 44,6 % → 78,6 % | `data/resultados/comparacion_esfuerzo_2024_2026_resumen.csv` |
| 2026 con denominador canónico | 57,8 % | mismo CSV |
| SERPAVI vs Eustat 2024 | ratio 0,977 · Spearman 0,988 · 159/159 dentro de ±25 % (159 con alquiler oficial; las 160 dan 0,979 y 159/160) | `data/resultados/validacion_alquiler_2024_serpavi.csv` |
| Esfuerzo por tipología (mediana de anuncios) | 78,6 / 82,0 / 116,4 % | `data/resultados/esfuerzo_por_tipo_nivel_anuncio_2026.csv` |
| Sensibilidad al portal | Donostia 116,4 → 93,1 % sin realtyapi | `data/resultados/validacion_portales_2026.csv` |

Los productos de `analysis/` van a `data/resultados` (capa gold): `data/procesado`
queda reservado a `transform/`, que es lo que vigila el manifest silver.

H6 (`H6_habitaciones_mediana_rango.png`) se genera en `run_analisis_mongo.py`:
ranking n≥10 con IC95, distribución y esfuerzo individual sobre el salario joven
2026, calculados solo sobre los anuncios plausibles (precio por debajo del
alquiler mediano de vivienda del municipio, `_hab_tope_stages`). Esa misma
ejecución copia H6/H8b a `assets/`, así que el deck no depende de un `cp` manual.

## Comprobar que el deck no se ha desincronizado

```
python scripts/verificar_cifras_deck.py
```

Lee `index.html`, saca **159 comprobaciones** de los CSV gold y falla si alguna ya no
coincide. Existe porque el deck se quedó una vez con el corte viejo (79,3 % / 52
municipios) mientras los CSV ya daban 78,6 % / 50. Se ejecuta antes de exportar el PDF.

## Skill instalado

```
.agents/skills/frontend-slides/     # 163 ficheros, ~3.9 MB, MIT
```

Invocación en el agente: skill `frontend-slides`. El flujo del skill es:

1. Contarle el contenido (guion, mensajes, imágenes) y el público.
2. Genera 3 previews de estilo; se elige una.
3. Genera el deck completo en el estilo elegido, con escenario fijo 16:9 (1920×1080).
4. Exporta a PDF (`scripts/export-pdf.sh`, requiere Playwright + Chromium) o se imprime
   desde Chrome.

## Estilo elegido

**A · Swiss Modern**: papel `#F5F4F0`, tinta `#121212`, acento bermellón `#C8451B`, rejilla
visible, titulares en Bahnschrift (fallback DIN / Helvetica), cifras tabulares y figuras
enmarcadas con pie mono. Los backups van numerados `B1…B12` para no confundirlos con las 26.

## Reglas para no romper lo que ya funciona

- **No mezclar con `docs/presentacion/`**: el deck de la defensa actual no se regenera aquí.
- Si el deck nuevo usa cifras del proyecto, **alimentarlo desde `data/resultados/*.csv`**;
  no teclear números (P-05).
- Revisar acentos, `ñ` y símbolos (€, ‰, ≥) en el HTML y en el PDF: los presets usan fuentes
  web y conviene comprobar que cargan sin red.
- Comprobar que ningún texto se corta en 16:9 y que el PDF no parte diapositivas.

## Estilos disponibles

12 presets en `STYLE_PRESETS.md` (Swiss Modern, Editorial, Vellum, Terminal Green, etc.) y 34
plantillas "bold" en `bold-template-pack/`, con previews progresivas.
