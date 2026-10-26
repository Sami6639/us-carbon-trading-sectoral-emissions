# Separate California synthetic-control benchmark

This is a **summary of an updated 2005–2024 California SCM benchmark**, not a result
from the national RGGI estimator and not the original authors' published estimate.
The national `python run_all.py` command does **not** reproduce California SCM.
Updated California benchmark code and its third-party predictor inputs are not
included in this slim public export.

## Retained benchmark

| 2024 measure | Electricity (primary) | Industry (secondary) |
|---|---:|---:|
| Actual, t CO₂/person | 0.790499174393497 | 1.48088403404039 |
| Synthetic, t CO₂/person | 1.80165598495818 | 1.85534145567154 |
| Gap, t CO₂/person | −1.01115681056469 | −0.374457421631149 |
| Relative gap, percent of synthetic | −56.1237449883173 | −20.1826688282354 |
| Late/pre-MSPE placebo rank bounds | 0.0810810810810811–0.135135135135135 | 0.0434782608695652–0.152173913043478 |

The prefit window is 2005–2012; the postperiod is 2013–2024. The primary rank
statistic is 2020–2024 MSPE divided by 2005–2012 MSPE. Five original-vintage
predictors and updated outcome lags (2012, 2011, 2010, 2005) enter this separate
SCM design. Outcomes and population use EIA 2024F throughout, without old/new
outcome splicing.

Electricity uses 36 donors: 34 valid placebo fits and two failed/invalid fits.
The resulting all-unit rank bounds are 3/37–5/37, not a single identified rank
fraction and **not 5% confirmatory evidence**. Industry uses 45 donors: 40 valid
and five failed/invalid placebo fits. A uniform numerical repair increased both
Synth optimizer budgets to 10,000 iterations for every actual/placebo fit;
failures remain in the reported bounds. This benchmark is not independent causal
confirmation of the national comparison.

## Public source and code access

- Lessmann, C., & Kramer, N. (2024). *The effect of cap-and-trade on sectoral
  emissions: Evidence from California*. Energy Policy, 188, 114066.
  [Article DOI](https://doi.org/10.1016/j.enpol.2024.114066).
- [Original authors' data and code archive, Zenodo record 14412801](https://zenodo.org/records/14412801).
  The record provides `ReplicationFiles_Lessmann_Kramer_2024.zip` under its stated
  CC BY 4.0 terms. It supports their original **2005–2019** study, not the updated
  benchmark summarized above.
- [Accessible institutional article copy](https://publications.pik-potsdam.de/pubman/item/item_29845_2/component/file_29857/29845oa.pdf).
  Linked, not redistributed.

Access verification on 2026-10-26 confirmed the Zenodo record and institutional
article. The DOI is corroborated by those records; direct publisher access may
require a different access route. No public URL for the updated benchmark code is
asserted.

The summary was checked against the retained benchmark tables
`all_sectors_fit_metrics.csv` (SHA-256
`c411a037c4d0f1dd73edb75aad4e3d9d9b532765d2fb1aaad9b76ce9eb2be315`)
and `all_donor_rank_summaries.csv` (SHA-256
`d6a6fc2c204832cd4c3b67bd784b22a52f7e3096bf2d234155b09db2638eaa1f`).
Those files are not bundled here; the hashes identify the summary's evidence,
not a claim of full California reproducibility from this repository.
