# Design — Contrato de comparabilidad

## Decisiones

1. **Contrato primero.** `config/comparabilidad.yaml` fija capas, unidades,
   vintages y denominadores; `docs/matriz-comparabilidad.md` lo traduce a
   lenguaje humano; `analysis/comparabilidad.py` expone helpers puros y
   `tests/test_comparabilidad.py` lo verifica. Los generadores de figuras
   consumen el contrato, no al revés.
2. **Denominador canónico.** El esfuerzo usa `renta_hogar` INE Atlas 2024 (el
   código ya lo hacía). Se corrige la declaración del spec en lugar de cambiar
   el código, porque cambiar la base alteraría las conclusiones. Eustat RPF
   2024 queda como contraste.
3. **Separación de capas en figuras, no en los datos.** `mongo_esfuerzo_por_municipio.csv`
   sigue con 252 filas (159 oficial + 93 idw). Las figuras N1/N2/A1/A2/F/P
   filtran o etiquetan. Es aditivo y reversible.
4. **Tensión alineada al canónico.** `calcular_tension_social.py` pasa de
   `esfuerzo_joven_pct` (legacy 16-29) a `esfuerzo_joven_pct_18_34`, con
   fallback declarado. Requiere recargar Mongo (demanda_social embebida) y
   regenerar gold.
5. **Renombrado con alias.** Las columnas ambiguas se renombran con sufijo
   (`_legacy`, `_no_comparable`) y el alias viejo se conserva declarado para no
   romper consumidores.

## Alternativas rechazadas

- **Cambiar el código a Eustat RPF 2024**: altera el esfuerzo (Bilbao 37,69 %
  subiría) y las conclusiones. Rechazado: el contrato debe reflejar el dato.
- **Recalcular el IDW**: fuera de alcance; el IDW es sensibilidad declarada.
- **Dividir el change en varios**: el contrato es transversal y los generadores
  comparten entrada; un solo change con fases de commit es la unidad honesta.

## Known limitations

- La recarga de Mongo es destructiva en local (`--allow-mongo-write`), pero no
  introduce datos nuevos.
- Los PNG de gold cambian de bytes al regenerar; se verifica con doble ejecución.
- El contrato no reescribe los specs existentes: solo deltas.

## Diagrama

```
config/comparabilidad.yaml ──► analysis/comparabilidad.py ──► tests/test_comparabilidad.py
                                        │
                                        ▼
   run_analisis_mongo.py / generar_figuras_N.py  (capas, unidades, etiquetas)
                                        │
                                        ▼
   data/resultados/*.csv + *.png  ──►  docs/presentacion_v2 (deck)
```
