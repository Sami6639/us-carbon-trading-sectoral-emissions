# National input panel

`data/us_state_sector_co2_2000_2024.csv` is a complete 50-state × 25-year panel.
The key is `(stateabbr, year)`. DC and the national aggregate are excluded from the
panel but retained in the unmodified source files and control-total audit.

Source: U.S. Energy Information Administration, State Energy Data System (SEDS),
2024F vintage, released June 26, 2026. `TEEIE` (electric power) and `TEICE` (industry)
are million metric tonnes of CO₂. `TPOPP` is resident population including Armed
Forces, in thousands, with July 1 reference date. `2024F` denotes final historical
estimates, not forecasts. Source URLs, byte counts and SHA-256 hashes are in
`receipts/raw_manifest.json`.

For either sector:

```
metric tonnes CO2 per resident = CO2 million tonnes * 1000 / population thousands
```

The panel retains numerators and denominator. There is no interpolation, imputation,
winsorization, logging, artificial offset, outcome-based exclusion or vintage splice.
Source precision is retained; calculated decimal places do not add measurement precision.
No original California predictors are needed or included.

The build checks 1,250 unique keys, complete state-year coverage, nonmissing finite
values, positive population, nonnegative emissions and exact conversion identities.
Source zeros would remain zeros; this selected panel has none. Independent openpyxl
verification checks all 2,500 emissions cells against the workbook, all 1,250
population cells against the source CSV, and per-capita conversions using Decimal.

Industrial US totals include coal-coke net imports not allocated to states. The
50-state-plus-DC total therefore need not equal the US total, and state values are
not rescaled to force agreement. Power/population components can differ through
source rounding. The generated `audit/source_control_totals.csv` retains these
reconciliations and their scientific interpretation.

From the repository root, `python run_all.py` runs the complete offline pipeline.
For input-only rebuilding: `python inputs/scripts/build_panel.py`.
For independent input verification: `python inputs/scripts/verify_panel.py`.
The builder supports `--output` for a separate output directory while always
reading the bundled, hash-verified source files.

See `DATA_DICTIONARY.md` and the root `SOURCES.md` for definitions and source links.
