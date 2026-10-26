# Carbon trading and sectoral emissions: U.S. state research data and code

Repository: https://github.com/Sami6639/us-carbon-trading-sectoral-emissions

This repository reproduces a fixed **national RGGI comparative analysis** from
archived official EIA source bytes. It includes the 50-state, 2000–2024 panel
(1,250 state-years), the scientific specification and policy calendar, all six
result tables, and scientific figure code, data and images. No article manuscript
or third-party paper text is included.

## Reproduce offline

From the repository root, with the dependencies below already available:

```bash
python run_all.py
```

The command verifies both raw-input SHA-256 hashes, rebuilds the panel, independently
checks source cells and unit conversions, runs synthetic estimator self-tests,
reproduces all six fixed result CSVs, compares their checksums with the reference
outputs, and regenerates both scientific figures. It requires no internet access,
API key, R installation or proprietary statistical software. It overwrites generated
outputs deterministically; run on a copy to preserve a separate run.

Dependencies: Python 3, NumPy, pandas, SciPy, openpyxl and Matplotlib. The checked
runtime used Python 3.12.14, NumPy 2.3.5, pandas 2.2.3, SciPy 1.17.0,
openpyxl 3.1.5 and Matplotlib 3.10.8. Exact tested versions are listed in
`requirements.txt`; packages themselves are not bundled.
Nested scientific-directory `.gitattributes` preserve original line endings and
checksum-guarded bytes on checkout; the official EIA CSV retains its source CRLF.
Generated CSV writers explicitly use LF line endings. Exact execution on other
operating systems or numerical-library builds is not asserted.
Cross-platform/library changes can affect floating-point serialization or image
rendering; the command stops rather than silently accepting a result-checksum change.

## Fixed design and principal results

Nine continuously participating RGGI states are compared with 34 fixed comparison
states. Each state receives equal weight within its group, and years receive equal
weight within each window. The baseline is 2000–2004; 2005–2008 is an anticipation
window, excluded from the baseline and primary postperiod. The specification uses
annual tonnes of CO₂ per resident, without logs, retuning or population weighting.

| Endpoint | Level contrast, t CO₂/resident/year | Raw WCR p | Holm p |
|---|---:|---:|---:|
| Power, 2009–2024 (primary) | +2.21307593628 | 0.0116 | 0.0232 |
| Industry, 2009–2024 | +0.0469254013163 | 0.8983 | 0.8983 |
| Power, 2020–2024 | +3.9975763561 | 0.0039 | 0.0117 |

These are **descriptive/comparative level contrasts, not valid literal causal policy
effects**. Both power groups declined; the positive contrasts mean smaller absolute
per-resident declines in the RGGI group, whose baseline was much lower. The fitted
additive no-policy power means are negative (−0.3093 for 2009–2024 and −2.4849 for
2020–2024 t/resident), a serious scale/support warning. This is not a claim that
RGGI caused emissions to rise, nor a formal test against population parallel trends.

All intervals and p-values condition on independent state-level shocks after common
changes. RGGI is one coordinated regional policy, not nine independent adoptions.
Regional energy-market changes, other policies and interstate electricity trade
limit identification. Power emissions are production-based, not a consumption
footprint; industrial energy-related CO₂ excludes some industrial-process emissions.

Endpoint intervals are conventional HC1 intervals using t(41), not bootstrap
intervals. WCR p-values use 9,999 fixed Rademacher draws (PCG64 seed 20261026).
Holm adjustment covers the three endpoints. Annual figures use separately labeled
unrestricted wild-bootstrap-t simultaneous bands across all 50 outcome-year
coefficients. Pretrend nonrejection does not establish parallel trends. All
endpoints, diagnostics and the fixed early-baseline sensitivity are retained.

## Files

- `inputs/raw/`: unchanged EIA sector workbook and energy-indicators CSV.
- `inputs/data/`: complete panel; `inputs/DATA_DICTIONARY.md` gives definitions.
- `inputs/scripts/`: offline transformation and independent source-cell verification.
- `design/`: fixed scientific specification, source records and policy calendar.
- `analysis/run_analysis.py`: exact national estimator; `analysis/results/`: six CSVs.
- `diagnostics/`: additive-support arithmetic from the fixed analysis.
- `figures/`: figure code, plotted data, PNG/SVG images and provenance.
- `CALIFORNIA_BENCHMARK.md`: separate benchmark and public source-access boundaries.
- `SOURCES.md` and `RIGHTS_AND_ATTRIBUTION.md`: citations and rights notices.
- `PUBLIC_EXPORT_MANIFEST.json`: original/public specification hash mapping and
  nonscientific changes. Scientific sections are unchanged.
- `validation/public_reproduction_check.json`: fresh-directory reproduction receipt.

The specification was fixed before national outcome fitting, but was **not externally
preregistered**; earlier California results were already known. The public copy
removes workflow attribution only. The original specification hash and the public
hash are documented, and the copied runner guards the public hash. National raw
inputs, panel, all six result tables, model, sample, outcomes, windows, weights,
inference and seed are unchanged.

## California and reuse

The separate California SCM is a contextual benchmark, not a pooled estimate or
independent causal confirmation. **The national command does not reproduce that
legacy SCM.** Its original-author source archive and the updated benchmark are
explicitly distinguished in [CALIFORNIA_BENCHMARK.md](CALIFORNIA_BENCHMARK.md).
Unused original California predictors and third-party replication archives are omitted.

Source: U.S. Energy Information Administration, SEDS 2024F, released June 26, 2026.
Raw source URLs and SHA-256 hashes are retained. EIA source data are redistributed
with attribution under its [reuse policy](https://www.eia.gov/about/copyrights_reuse.php).
No new license grant is made for the research code or documentation; see
[RIGHTS_AND_ATTRIBUTION.md](RIGHTS_AND_ATTRIBUTION.md).
