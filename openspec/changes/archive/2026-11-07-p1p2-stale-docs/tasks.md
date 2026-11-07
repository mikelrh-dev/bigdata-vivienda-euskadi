# Tasks: P1/P2 stale docs (verificar + stale + mapa)

Change: `2026-11-07-p1p2-stale-docs` · Proposal: `proposal.md` · Specs:
`extraccion-datos` (VERIFICACION-01), `presentacion-de-resultados` (BOOTSTRAP-01,
DOCS-01, chart_mapa_tier), `contrato-reto` (ENTREGABLES-01, ARQUITECTURA-01).
Rutas reales (verificadas hoy): `scripts/verificar_fase_datos.py`,
`README.md`, `AGENT.md`, `docs/metodologia.md`, `docs/guion_defensa.md`,
`docs/guion_defensa_12min.md`, `docs/presentacion/build_presentacion.py`,
`docs/presentacion/README.md`, `docs/presentacion/assets/chart_mapa_tier.svg`
(5.907.130 bytes), `data/resultados/bootstrap_robustos.csv` (13 PNG en
`data/resultados/`, g1 byte-idéntico a A1 SHA `25948f0f…`).
Verdad canónica v5: `594/843` anuncios, HDFS 352 raw, tests 177, Tier
`4/3/57/188` (=252), Nivel tipología `4/54/194`, bootstrap
`n_larga_solo_vivienda` `67/60/39/37`, IC95 Bilbao `33.75–40.95` / Getxo
`27.54–31.77`, Tier `n_anuncios` `204/126/50/39`.

Prohibiciones transversales (todas las tareas): sin Docker ni Docker Compose
(arquitectura contractual: «HDFS centro + Mongo local sin Docker Compose en
el repo»); HDFS solo raw 352 (sin subidas de procesado); Kafka → HDFS, nunca
Kafka → Mongo; sin imputar comarcal/IDW como municipal; sin re-ejecutar
pipelines datos/Mongo/HDFS/Kafka; `data/raw` intacto (0 diffs); sin teclear
valores (todo de CSV/manifest).

## 1. `verificar_fase_datos.py`: gate FAIL 06/07 + huella (P1-1)

Archivos: `scripts/verificar_fase_datos.py` (líneas 62-70, 134-135, 144-146);
fuentes `data/procesado/dim_municipios.csv`, `…/udalmap_empleo_corregido.csv`.
Spec: `extraccion-datos` VERIFICACION-01.

- [x] 1.1 Check 06 (líneas 62-65): cambiar `759/843` → `594/843` — nombre
  `06 n_anuncios 594/843`, aserción `sum(n_anuncios) == 594` y
  `sum(n_anuncios_raw) == 843` sobre `dim_municipios.csv` (PROC). No tocar el
  843.
- [x] 1.2 Check 07 (líneas 69-70): la lógica actual exige
  `paro_registrado_cero=True ⇒ tasa isna` para todos; con v5 hay ceros no
  nulos conocidos. Reemplazar por FAIL conocido que nombre exactamente
  Aramaio `0.28`, Gaintza `1.45`, Usansolo `3.26`
  (`paro_registrado_cero=True` con `tasa_paro_lanbide_pct` no nulo) como
  casos documentados; ningún caso se enmascara como PASS ni se imputa valor
  comarcal. El resto de ceros no conocidos sigue fallando sin lista cerrada.
- [x] 1.3 Huella verificable: cuando el resto de checks alcanza PASS, el
  gate imprime `RESULTADO` (línea 144) + huella SHA-256 reproducible de los
  artefactos comprobados (mismo patrón que check 01 con
  `docs/raw_manifest_sha256.txt`); sin PASS global mientras 06/07 figuren
  como FAIL conocido, el mensaje distingue PENDIENTE de OK.
- [x] 1.4 Verificación: `python scripts/verificar_fase_datos.py` → check
  `06 n_anuncios 594/843` PASS con `real=594`; `FAIL 07` lista Aramaio
  0.28 / Gaintza 1.45 / Usansolo 3.26; `grep -c "759/843"
  scripts/verificar_fase_datos.py` → `0`.
- [x] 1.5 Auditar check 17 (líneas 134-135): hoy espera
  `n_ficheros == 354`; si esa cifra es la misma que el canónico HDFS 352,
  alinearla a `352` con el mismo criterio que la tarea 2.3 (no es de la
  spec VERIFICACION-01, pero es la única otra cifra stale del script).

## 2. Normalizar taras stale en docs y presentación (P1-2 + P2)

Archivos: `README.md`, `AGENT.md`, `docs/metodologia.md`,
`docs/guion_defensa.md`, `docs/guion_defensa_12min.md`,
`docs/presentacion/build_presentacion.py:218`,
`docs/presentacion/README.md:62`, `data/resultados/bootstrap_robustos.csv`
(solo lectura del texto, el CSV ya trae 67/60/39/37 e IC95 correctos).
Specs: `contrato-reto` ENTREGABLES-01/ARQUITECTURA-01,
`presentacion-de-resultados` BOOTSTRAP-01/DOCS-01.

- [x] 2.1 Texto Docker contractual (ENTREGABLES-01): `README.md:100`
  `Docker Compose HDFS + MongoDB` → «HDFS centro + Mongo local sin Docker
  Compose en el repo»; `README.md:24` etiqueta `mongo — MongoDB<br/>Docker`
  → Mongo local sin tupla Docker; `AGENT.md:4` quitar `(Docker)` de
  `BD MongoDB (Docker) + PyMongo` con la misma frase contractual.
  Verificación: `grep -in "docker" README.md AGENT.md` solo devuelve la
  frase contractual; `grep -c "Docker Compose HDFS" README.md` → `0`.
- [x] 2.2 Cuentas de tests y ficheros (P2): barrido único con valores
  canónicos, sin mezclarlos — `README.md:110,148,258` `174 → 177` tests;
  `README.md:125,136,138` y `AGENT.md:9` `190/manifest 187 → 188/188` y
  `antes 188/manifest 185` como historia, no vigente;
  `AGENT.md:9` `151 tests → 177`; `docs/metodologia.md:16` `174 → 177`;
  `docs/guion_defensa.md:41` `174+1s → 177+1s`; `docs/guion_defensa_12min.md:36`
  cifras de tests/gate obsoletas (`166 tests`, `gate 18/18`) → valores
  vigentes o eliminar la cifra y remitir al gate. Cualquier `249` que
  refiera a municipios → `252`; ningún `252` real se toca.
- [x] 2.3 HDFS 352 vs 354 (canónico 352): `AGENT.md:9` `(manifest 354)` →
  `352`; `README.md:136` `356 (354 con hash)` → distinguir: conteo local
  en disco ≠ 352 ficheros raw publicados en HDFS; `README.md:101,108,253`
  ya dicen 352 y quedan intactos. Toda mención HDFS dice solo `raw` 352.
- [x] 2.4 Cadena de dedup: `docs/metodologia.md:55` `845 crudos → 759` →
  `845 → 594` (10,18 % se recalcula o se marca como cifra histórica de la
  cadena 845→759); `docs/metodologia.md:14` ya dice 594 y queda intacto.
- [x] 2.5 Presentación 759 → 594 (DOCS-01): docstring `decor_trama`
  `docs/presentacion/build_presentacion.py:218` (`759 dibujos`) → `594`;
  `docs/presentacion/README.md:62` (trama `759`) → `594`. Verificación:
  `grep -c "594"` ≥ 1 en ambos y 759 no figura como cifra vigente (solo
  como historia 845→759→594 si se conserva).
- [x] 2.6 Bootstrap `n_larga_solo_vivienda` ≠ Tier (BOOTSTRAP-01): en
  `docs/metodologia.md` y guiones, documentar que el bootstrap usa
  `n_larga_solo_vivienda` `67/60/39/37` (Bilbao/Donostia/Getxo/
  Vitoria-Gasteiz, `data/resultados/bootstrap_robustos.csv`) distinto del
  `n_anuncios` Tier `204/126/50/39`; constar IC95 Bilbao `33.75–40.95` y
  Getxo `27.54–31.77`. Los dos `n` no se intercambian en textos ni gráficos;
  el CSV no se edita (sus valores ya son los canónicos).
- [x] 2.7 Frase ortogonal Nivel/Tier (ARQUITECTURA-01 + DOCS-01):
  `docs/metodologia.md:17` ya trae la frase (`Nivel1 4 / Nivel2 54 /
  Nivel3 194` ortogonal a Tier `4/3/57/188`) — verificar y no degradarla;
  añadir la misma frase a `docs/guion_defensa.md` y
  `docs/guion_defensa_12min.md` (hoy solo aparecen conteos sueltos de
  Nivel2/Nivel3). Nivel (tipología) y Tier (confianza por `n_anuncios`)
  son ejes ortogonales, no intercambiables.
- [x] 2.8 Verificación del barrido: `grep -rn "759\|174\|187\|249\|354"`
  sobre `README.md`, `AGENT.md`, `docs/metodologia.md`, ambos guiones y
  `docs/presentacion/{build_presentacion.py,README.md}` → `0` salvo
  historia explícita 845→759→594 o citas de la cadena; `pytest tests/ -q`
  sigue verde (177 passed, 1 skipped destructivo) para validar la cifra
  nueva de tests antes de commitear.

## 3. Mapa Tier + dedupe g1/A1 (presentacion-de-resultados, chart_mapa_tier)

Archivos: `docs/presentacion/assets/chart_mapa_tier.svg`,
`docs/presentacion/build_presentacion.py:323-432` (`chart_mapa_tier()`,
asserts 252/252), `data/resultados/*.png` (13 tubos del pipeline).

- [x] 3.1 Aligerar `chart_mapa_tier.svg` (hoy 5.907.130 bytes ≈ 5,9 MB) a
  <2 MB con utilidades de simplificación (redondeo de coordenadas a 1
  decimal ya vigente, simplificación de anillos con tolerancia, eliminar
  path duplicados de la misma geometría), sin cambiar los 13 tubos
  (`data/resultados/*.png`) ni la clasificación 252/252 A/B/C/D. Regenerar
  vía `python docs/presentacion/build_presentacion.py` o post-procesar el
  SVG generado; los asserts `len(features) == 252`, `unidas == 252`,
  `n_oficial + n_idw == 252` deben seguir pasando.
- [x] 3.2 Diff visual antes de commitear: el mapa ligero conserva
  coroplético A/B/C/D, borde sólido oficial / discontinuo IDW, leyenda
  `official {n_oficial} / IDW {n_idw} / contexto 252` y texto literal
  `252 contextual sobre 159`; `252/252 clasificados` intacto en el SVG.
- [x] 3.3 Dedupe g1/A1: `data/resultados/g1_esfuerzo_por_territorio.png` es
  byte-a-byte idéntico a `A1_distribucion_esfuerzo_por_TH.png` (SHA
  `25948f0f6bf3…`). Eliminar el fichero g1 redundante conservando A1 como
  canónico, **sin renumerar ni renombrar** el resto de los tubos
  (A2, B, C, D, E, F, G, g2-g5 quedan con su nombre). Quedan 12 PNG únicos
  de 13 nombres emitidos: registrar la excepción y actualizar en la tarea 4
  las afirmaciones «13 PNG» de docs a 12 únicos / 13 emitidos. Verificar
  que ningún `*.py/*.md/*.html` referencia `g1_esfuerzo_por_territorio.png`
  (grep fuera de `.venv` y `openspec/changes/archive`).
- [x] 3.4 Verificación: tamaño SVG <2 MB (`ls -lh`), `grep -c "252/252"`
  y conteos por tier desde el CSV intactos, `sha256sum
  data/resultados/*.png` sin duplicados, `ls data/resultados/*.png | wc -l`
  → `12` con los 12 nombres restantes sin renumerar.

## 4. Sync P1/P2 + manifest checks (cierre del change)

Archivos: los de las tareas 1-3 + `docs/raw_manifest_sha256.txt`,
`data/procesado/_meta/ingestion_manifest.json`, `docs/presentacion/index.html`
/ `index.template.html` (si el SVG cambia de peso, el texto del mapa/regeneración).

- [x] 4.1 Manifest checks (sin re-ejecutar pipelines): ejecutar el gate
  completo `python scripts/verificar_fase_datos.py` y constatar el estado
  final — 06 PASS 594/843, 07 FAIL conocido con los 3 ceros de paro,
  01 manifest íntegro, 17 ingestion manifest alineado (tarea 1.5);
  `python scripts/hdfs_verify.py` solo como lectura si existe (sin subidas,
  sin tocar HDFS) para confirmar 352 raw. Anotar en el verify-report el
  `RESULTADO` + huella SHA-256 de la tarea 1.3.
- [x] 4.2 Sync de cifras derivadas: cualquier doc que afirme «13 PNG»,
  `18/18`, `759`, `356/354` o `174/190/187/249` como vigente tras las
  tareas 2-3 se actualiza (index/presentación, README de
  `docs/presentacion/`, metodología); `git status` sin cambios en
  `data/raw`, sin Dockerfile, Kafka no escribe en Mongo.
- [x] 4.3 Criterios de éxito de la propuesta (verificación final):
  verificar FAIL 06 muestra 594/843; FAIL 07 lista los ceros de paro
  (Aramaio 0.28 / Gaintza 1.45 / Usansolo 3.26); ningún claim Docker
  Compose; ningún `759/174/187/249/354` stale en docs de alcance; SVG <2 MB
  sin duplicado g1/A1. Commitear solo docs + `scripts/verificar_fase_datos.py`
  + SVG + borrado g1; el resto (pipeline, datos, HDFS, Kafka) queda fuera.
