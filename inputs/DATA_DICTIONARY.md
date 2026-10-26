# Data dictionary

Main file: `data/us_state_sector_co2_2000_2024.csv`

Grain: one US state and calendar year. Key: (`stateabbr`, `year`). Geographic universe: the 50 states, excluding DC, territories and national aggregates. Years: 2000–2024, inclusive. Rows are sorted by postal abbreviation, then year.

| Field | Type and unit | Meaning and provenance |
|---|---|---|
| `stateabbr` | Text, two letters | State postal abbreviation used to join the EIA source tables. Not a numeric FIPS identifier. |
| `state` | Text | Full state name; fixed one-to-one mapping to `stateabbr`. |
| `year` | Integer | Calendar year. |
| `population_thousands` | Numeric, thousand persons | EIA TPOPP, resident population including Armed Forces; July 1 Census estimate as incorporated by EIA. Source Data_Status = 2024F. |
| `electricity_co2_mmt` | Numeric, million metric tonnes CO2 | EIA TEEIE, stored values from the `Electric power` worksheet. Source unit label: `Million metric tons CO2`. |
| `industry_co2_mmt` | Numeric, million metric tonnes CO2 | EIA TEICE, stored values from the `Industrial` worksheet. Source unit label: `Million metric tons CO2`. |
| `electricity_co2_tpc` | Numeric, metric tonnes CO2/person | `electricity_co2_mmt * 1000 / population_thousands`. |
| `industry_co2_tpc` | Numeric, metric tonnes CO2/person | `industry_co2_mmt * 1000 / population_thousands`. |

All three source series are from the EIA SEDS 2024F vintage released June 26, 2026. Values are estimates, not forecasts. Source amounts and population are not replaced with author-replication outcomes. `tpc` means tonnes per capita and never tonnes per thousand persons.

## Missing and zero rules

The expected panel contains no missing values. Missing source cells, nonnumeric entries, nonfinite values or duplicate keys cause a build failure. A zero is a valid observed outcome and would not be substituted for a missing value; none occurs in this selected panel. No logarithmic variables or artificial constants are generated.

The smallest electric-power source value is 0.002 million tonnes. Such small positive values can produce large relative annual changes. The audit reports them without trimming or altering the source series.

## Source references

- [EIA state carbon-dioxide data and release information](https://www.eia.gov/environment/emissions/state/)
- [EIA sector workbook](https://www.eia.gov/state/seds/sep_sum/html/xls/co2_sector.xlsx)
- [EIA energy-indicators CSV](https://www.eia.gov/state/seds/sep_indicators/energy_indicators.csv)
- [EIA indicator units](https://www.eia.gov/state/seds/sep_indicators/ei_a.pdf)
- [EIA population methods](https://www.eia.gov/state/seds/sep_indicators/ei_indicators.pdf)
- [EIA sector and emissions definitions](https://www.eia.gov/state/seds/sep_co2/notes/co2_intro.pdf)
- [EIA sector totals and per-capita formula](https://www.eia.gov/state/seds/sep_co2/notes/co2_tot.pdf)
