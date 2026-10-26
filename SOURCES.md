# Sources and scientific references

## Official data and definitions

Source: U.S. Energy Information Administration, State Energy Data System (SEDS), 2024F historical vintage, released June 26, 2026. Source byte checksums are in `inputs/receipts/raw_manifest.json`. Access/provenance date: 2026-10-26.

- [State carbon-dioxide data and release information](https://www.eia.gov/environment/emissions/state/)
- [Sector workbook: electric power TEEIE and industry TEICE](https://www.eia.gov/state/seds/sep_sum/html/xls/co2_sector.xlsx)
- [Energy-indicators CSV: population TPOPP](https://www.eia.gov/state/seds/sep_indicators/energy_indicators.csv)
- [Indicator units](https://www.eia.gov/state/seds/sep_indicators/ei_a.pdf)
- [Population methods](https://www.eia.gov/state/seds/sep_indicators/ei_indicators.pdf)
- [Sector and emissions definitions](https://www.eia.gov/state/seds/sep_co2/notes/co2_intro.pdf)
- [Sector totals and per-capita methods](https://www.eia.gov/state/seds/sep_co2/notes/co2_tot.pdf)
- [EIA rights and reuse](https://www.eia.gov/about/copyrights_reuse.php)

## Policy-calendar evidence

The following official records support historical coding through 2024, not a claim about later legal status. The policy calendar preserves the exact source links and scientific exclusions used in the fixed specification.

- [rggi_history](https://www.rggi.org/program-overview-and-design/design-archive): Discussions began in 2003; seven-state MOU December 2005; MA, RI and MD joined in 2007; compliance began January 2009; NJ withdrew effective 2012 and returned 2020; VA participated 2021–2023 within this sample.
- [rggi_elements](https://www.rggi.org/program-overview-and-design/elements): Power generators of at least 25 MW covered; official annual participation composition supports the nine continuous states. Regional cap changed in 2014 and subsequent reviews.
- [rggi_pa](https://www.rggi.org/program-overview-and-design/new-participation): PA rule effective July 2022 was enjoined July 8; all PA allowances removed before September 2022 auction; not coded as operating treatment.
- [pa_announcement](https://www.pacodeandbulletin.gov/Display/pabull?file=%2Fsecure%2Fpabulletin%2Fdata%2Fvol50%2F50-45%2F1541.html): Pennsylvania executive order 2019-07 signed October 3, 2019 directed RGGI-compatible power-sector rulemaking.
- [ca_start](https://ww2.arb.ca.gov/sites/default/files/barcu/board/books/2015/111915/15-9-3pres.pdf): First CA compliance period January 2013; supplied fuels covered January 2015.
- [ca_authority](https://ww2.arb.ca.gov/resources/documents/cap-and-trade-program-allowance-distribution-factsheet): AB32 enacted 2006; cap-and-trade one component of broad state policy portfolio.
- [wa_start](https://ecology.wa.gov/air-climate/climate-commitment-act/cap-and-invest/): CCA passed 2021; cap-and-invest began January 1, 2023, with first auction February 28, 2023; industry and utilities covered subject to scope thresholds.
- [or_history](https://www.oregonlegislature.gov/cis/GovToGovReports/Annual%20Report%20%28DEQ%29%202024.pdf): CPP adopted December 16, 2021, effective January 1, 2022; December 2023 invalidation decision; 2024 re-establishment rulemaking.
- [or_transition](https://apps.oregon.gov/oregon-newsroom/OR/DEQ/Posts/Post/deq-moves-to-re-establish-the-climate-protection-program-in-wake-of-recent-court-ruling-95357): January 2024 official release said final invalidation would follow appeal deadline; do not treat 2024 as a full operating year.
- [or_scope](https://www.oregon.gov/deq/EQCdocs/111722_B_SlidesStatic.pdf): 2022 CPP covered fossil fuels, including industrial use; electricity generation excluded. This is not equivalent to RGGI power coverage.
- [or_restart](https://www.oregon.gov/deq/ghgp/cpp/Pages/default.aspx): Re-established program first compliance period starts January 1, 2025, outside sample; tradable compliance instruments described.
- [co_rule](https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=5+CCR+1001-31&ruleVersionId=11462): Regulation 27 establishes GEMM industrial obligations for 2024 emissions, with 2025 credit issuance/auction; GEMM 1 adopted 2021. No power-sector RGGI treatment is inferred.
- [ma_overlap](https://www.mass.gov/doc/market-monitor-quarterly-report-2022-q4/download): MA 310 CMR 7.74 adds a separate power-sector cap from 2018, overlapping RGGI.

## Estimation and interpretation references

These references support the explicitly implemented common-cohort comparison and stated inference limitations. The code does not claim to implement full staggered doubly robust DiD, Stata boottest or HonestDiD.

- Callaway, B., and Sant’Anna, P. H. C. (2021). Difference-in-Differences with multiple time periods. Journal of Econometrics, 225(2), 200–230. [Source](https://doi.org/10.1016/j.jeconom.2020.12.001) Group-time contrasts and explicit aggregation motivate single-cohort implementation; the analysis does not claim to run their full doubly robust staggered estimator.
- MacKinnon, J. G., Nielsen, M. Ø., and Webb, M. D. (2023). Cluster-robust inference: A guide to empirical practice. Journal of Econometrics, 232(2), 272–299. [Source](https://doi.org/10.1016/j.jeconom.2022.04.001) Cluster dependence assumptions, CV1 and restricted wild bootstrap; cluster count is not the number of independent policy adoptions.
- MacKinnon, J. G., and Webb, M. D. (2018). The wild bootstrap for few (treated) clusters. The Econometrics Journal, 21(2), 114–135. [Source](https://doi.org/10.1111/ectj.12107) Few treated clusters can invalidate both conventional and bootstrap inference; bootstrap is not a cure for a single regional adoption.
- Roodman, D., Nielsen, M. Ø., MacKinnon, J. G., and Webb, M. D. (2019). Fast and wild: Bootstrap inference in Stata using boottest. The Stata Journal, 19(1), 4–60. [Source](https://doi.org/10.1177/1536867X19830877) Null-imposed wild bootstrap and bootstrap studentization; this project implements its stated elementary algorithm directly, not Stata boottest.
- Roth, J. (2022). Pretest with Caution: Event-Study Estimates after Testing for Parallel Trends. American Economic Review: Insights, 4(3), 305–322. [Source](https://doi.org/10.1257/aeri.20210236) Pretest nonrejection does not establish parallel trends and must not select the reported estimator.
- Rambachan, A., and Roth, J. (2023). A More Credible Approach to Parallel Trends. The Review of Economic Studies, 90(5), 2555–2591. [Source](https://doi.org/10.1093/restud/rdad018) Parallel trends is an identifying restriction requiring sensitivity and substantive justification. No HonestDiD estimator is claimed or newly introduced here.
- Holm, S. (1979). A simple sequentially rejective multiple test procedure. *Scandinavian Journal of Statistics, 6*(2), 65–70. [Source](https://www.jstor.org/stable/4615733). The fixed family consists of the three reported endpoints.
- Roth, J., & Sant’Anna, P. H. C. (2023). When is parallel trends sensitive to functional form? *Econometrica, 91*(2), 737–747. [Source](https://doi.org/10.3982/ECTA19402). Changing outcome scale does not automatically preserve parallel trends; no post-results log specification was fitted.

For the distinct California benchmark and original authors’ source/code archive, see [CALIFORNIA_BENCHMARK.md](CALIFORNIA_BENCHMARK.md). Third-party full texts are linked rather than redistributed.
