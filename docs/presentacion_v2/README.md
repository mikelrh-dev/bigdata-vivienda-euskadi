# Presentación v2 — deck nuevo (frontend-slides)

Carpeta de salida para una presentación **nueva**, independiente del deck actual
(`docs/presentacion/`, que sigue generándose con `build_presentacion.py` y no se toca).

## Qué hay aquí

- `guion.md` — guion oral slide por slide, con cifras, gráficas, backups y mapa de rúbrica.
- `index.html` — deck completo, **22 diapositivas + 8 de backup**, en cuatro actos:
  2024 oficial → 2026 de oferta → cómo se construyó → límites y cierre. Estilo
  **Swiss Modern**, una sola página, CSS/JS inline, sin red: se abre con doble clic.
- `assets/` — PNG portables. Los del bloque 2026 salen de
  `visuals/assets_presentacion_esfuerzo_mercado_2026.py` (lee los CSV de
  `data/procesado`, no teclea cifras): top20 con IC, histograma, territorio,
  tipología, diferencia de nivel, intervalos, cobertura y los dos mapas.
- `presentacion_v2.pdf` — exportación a 1920×1080, 30 páginas (22 + 8 backups).
- H8b (`H8b_modalidad_mediana_eur_m2.png`) se genera en `run_analisis_mongo.py` desde
  `pipeline_modalidades`, que ahora calcula `mediana_eur_m2` por modalidad. Gold pasa a 53/53.

## Estado de infraestructura (evidencia v11, 2026-11-12)

- MongoDB: **17 colecciones vivas + 15 de backup = 32**; **25 índices**.
- HDFS: **353 objetos** (352 canónicos + 1 manifiesto), 895.597.901 B. El `OPEN` de
  WebHDFS falla por DNS del datanode; el script de recuperación coteja, no restaura.
- Kafka: sin metadata en la comprobación de hoy (`NodeNotReadyError`); la última
  evidencia buena es v8 (352/352, lag 0).
- Gold: **53 artefactos** (24 CSV + 29 PNG).

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

Cifras que alimentan el bloque 2026 (diapositivas 8 a 13):

| Dato | Valor | Fuente |
|---|---|---|
| Mediana esfuerzo 2026 (50 mun) | 78,6 % | `esfuerzo_mercado_2026.csv` |
| Anuncios usados / excluidos | 287 / 10 | `_anuncios_2026.py` (conciliado en test) |
| Anuncios > 30 % del salario | 98,3 % | mismo CSV, nivel anuncio |
| Cobertura población 18-34 | 71,2 % | `data/resultados/cobertura_representatividad_2026.csv` |
| 2024 oficial → 2026 oferta (misma base) | 44,6 % → 78,6 % | `data/resultados/comparacion_esfuerzo_2024_2026_resumen.csv` |
| 2026 con denominador canónico | 57,8 % | mismo CSV |
| SERPAVI vs Eustat 2024 | ratio 0,976 · Spearman 0,979 | `data/resultados/validacion_alquiler_2024_serpavi.csv` |
| Esfuerzo por tipología (mediana de anuncios) | 78,6 / 82,0 / 116,4 % | `data/resultados/esfuerzo_por_tipo_nivel_anuncio_2026.csv` |
| Sensibilidad al portal | Donostia 116,4 → 93,1 % sin realtyapi | `data/resultados/validacion_portales_2026.csv` |

Los productos de `analysis/` van a `data/resultados` (capa gold): `data/procesado`
queda reservado a `transform/`, que es lo que vigila el manifest silver.

## Comprobar que el deck no se ha desincronizado

```
python scripts/verificar_cifras_deck.py
```

Lee `index.html`, saca **44 comprobaciones** de los CSV gold y falla si alguna ya no
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
enmarcadas con pie mono. Los backups van numerados `B1…B8` para no confundirlos con las 22.

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
