# Proposal: p1p2-stale-docs

## Intent

Documentation and verification scripts remain stale after v5. Align text, counts, and claims to current truth (594/843, 352 HDFS raw, Tier) without re-executing data pipelines.

## Scope

### In Scope
- P1-1 — `scripts/verificar_fase_datos.py`: FAIL 06 `759/843` → `594/843`; FAIL 07 paro-zero cases Aramaio 0.28 / Gaintza 1.45 / Usansolo 3.26 as documented known failures.
- P1-2 — `README.md:100` Docker Compose HDFS+Mongo → "HDFS centro + Mongo local sin Docker Compose en repo"; remove `(Docker)` from `AGENT.md`.
- P2 — `metodologia`: 174 tests, chain `845→759`→`594`; `README`: `174/190-187/249`→`177/188/252`; guiones `187→188,174→177,249→252`; `AGENT.md`: `185/151`→`177/188`; HDFS `352` vs `354` canonical `352`.
- `docs/presentacion/build_presentacion.py` docstring + `presentacion/README`: `759`→`594`.
- Bootstrap `n_larga_solo_vivienda` `67/60/39/37`≠Tier `204/126/50/39`; IC95 Bilbao `33.75-40.95`, Getxo `27.54-31.77`.
- Phrase Nivel (tipologia `4/54/194`) vs Tier (confianza `4/3/57/188`) in metodologia/guion.
- `chart_mapa_tier.svg` ~5.9MB lighten; remove duplicate g1/A1.

### Out of Scope
- Re-running datos/Mongo/HDFS/Kafka; touching `data/raw`; adding Docker Compose; Kafka→Mongo; HDFS beyond raw (352); comarcal/IDW as municipal.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `extraccion-datos`: verificar script expectations (M1).
- `presentacion-de-resultados`: docs, bootstrap, mapa Tier.
- `contrato-reto`: Docker text removal.

## Approach

Patch script thresholds and docs counts; fix bootstrap n/IC95; rewrite Nivel/Tier phrasing; optimize SVG. Docs/scripts only.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `scripts/verificar_fase_datos.py` | Modified | 594/843, paro-zero FAILs |
| `README.md`,`AGENT.md`,`docs/metodologia*`,`guiones*` | Modified | Counts, Docker, Nivel/Tier |
| `docs/presentacion/build_presentacion.py`,`presentacion/README` | Modified | 759→594 |
| bootstrap files | Modified | n_larga, IC95 Bilbao/Getxo |
| `chart_mapa_tier.svg` | Modified | <5.9MB, dedupe g1/A1 |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Count drift reappears | Med | Single sweep + grep verify |
| SVG lighten breaks map | Low | Visual diff before commit |

## Rollback Plan

`git checkout --` affected docs/scripts only; no data migration.

## Dependencies

- v5 truth: 594/843, HDFS 352 raw, Tier values above.

## Success Criteria

- [ ] verificar FAIL 06 shows 594/843; FAIL 07 lists paro-zero cases
- [ ] No Docker Compose claims remain
- [ ] No `759`,`174`,`187`,`249`,`354` stale counts in scoped docs
- [ ] SVG reduced and no duplicate g1/A1
