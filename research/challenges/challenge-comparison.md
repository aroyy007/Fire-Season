# Which 2026 NASA Space Apps challenge should this team choose?

Research date: 18 September 2026. Decision memo, with live data smoke tests. Status: research and proposed design, not a scientifically validated application.

## Executive Summary

Choose **Harmonization of MODIS and VIIRS Hot Spots** if the team has strong Python/data-science or remote-sensing capability and wants a practical Earth application. Build a calendar that answers a specific question: “Is this region experiencing unusually early or intense burning, or did our observing system change?” The core contribution should be a transparent comparison and calibration of satellite records, including uncertainty and observation coverage. The fire map is supporting context. This recommendation is an analyst judgment based on fit, achievable scope and demonstrated data access, not an estimate of winning probability.

The top three are **fire harmonization**, **Field Shift**, and **Earth System Trend Detective**. Field Shift has the clearest potential connection to everyday decisions if the team can recruit an agronomist and interview farmers. Without that expertise, a polished crop-ranking interface risks presenting unvalidated agricultural advice. Trend Detective is the fallback with the best balance of mature data and tractable statistics, but it needs a concrete local investigation to differentiate it from NASA's existing analytical tools.

NISAR is the strongest specialist alternative. Public provisional L-band data became available in July 2026; saying it is unavailable would be wrong. However, collection discovery is not proof that suitable before/after imagery exists for a chosen event. A NISAR entry should be selected only after downloading and processing an actual matching image pair.

Small live requests succeeded for NASA POWER daily weather and FIRMS VIIRS regional detections. NISAR catalog metadata also returned successfully. Historical fire archives and Earthdata-protected science granules remain untested. Two integration hazards materially affect the farming option: SoilGrids reports its REST service paused, and NSIDC flags a 2026 SMAP geolocation issue. These findings favor a reproducible, cached scientific demonstration over dependence on unverified live integrations. [2–9,12–15,22–24]

## Introduction

The comparison covers all fourteen entries in the user's pasted challenge list. The browser retrieval service initially returned errors. A later direct HTTP fetch of the official index and fire challenge succeeded; the fire summary is present in the page payload and matches the supplied brief. Its resources tab is empty in the retrieved payload. The supplied text remains the basis for the fourteen-way comparison; no additional resource requirements are invented. [1]

The initial assumption was four to six mixed engineering/design teammates; the user subsequently confirmed strong Python/data-science or remote-sensing capability and a preference for farming, fire, climate or disaster impact. The decision method therefore weights practical impact at 25%, data readiness at 20%, scientific distinctiveness at 20%, demonstrability at 15%, hackathon feasibility at 15%, and validation tractability at 5%. Scores below are explicitly **analyst estimates**, not measured properties or official judging criteria. A score of five is favorable. The risk column remains separate to avoid hiding critical blockers in averages.

## Main Analysis

### 1. All fourteen choices

Brief descriptions and intended outcomes below are paraphrases of the user-supplied challenge text. Scores, demo concepts and risks are proposed analysis. Data readiness outside the four deep dives is a planning estimate, not a completed dataset audit. [1]

| Challenge | Impact | Data | Distinctiveness | Demo | Feasibility | Validation | Weighted /5 | Scientific or delivery risk; a focused demo |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Harmonization of MODIS and VIIRS Hot Spots | 5 | 5 | 5 | 5 | 4 | 3 | **4.75** | High statistical risk if raw counts are merged; show sensor discontinuity disappearing only where calibration passes validation. |
| Field Shift: Adapting Farms with NASA Data | 5 | 4 | 4 | 5 | 4 | 2 | **4.30** | Agronomy and field-scale validity; compare three feasible rotations under a farmer's water and labor constraints. |
| Be An Earth System Trend Detective! | 4 | 5 | 4 | 4 | 4 | 4 | **4.20** | False significance and causal overclaiming; show two nearby regions with opposing trends and honest uncertainty. |
| Dancing with the SARs | 5 | 3 | 5 | 5 | 2 | 2 | **4.00** | Paired coverage, interpretation and provisional quality; one verified wetland or flood-change case study. |
| The Earth Information Jukebox | 3 | 4 | 4 | 5 | 4 | 3 | **3.85** | Meaningful accessible mapping must be tested with users; hear and navigate one variable through time. |
| Build a Junior Astronaut Mission Trainer | 3 | 4 | 3 | 5 | 5 | 3 | **3.80** | Game balances can become invented science; one outpost survival loop with documented trade-offs. |
| Space Mission Design Game | 3 | 4 | 3 | 5 | 4 | 3 | **3.65** | Broad game scope; one mission design with visible mass/power/budget consequences. |
| CLPS Lunar Mission Browser | 3 | 3 | 5 | 5 | 2 | 2 | **3.50** | Terrain horizon and geometry precision; compare sunlight and Earth visibility at two sites. |
| Abandoned but not Forgotten: Storytelling about NASA's Discarded Equipment on the Moon and Mars | 2 | 5 | 2 | 4 | 5 | 4 | **3.50** | Low technical barrier but educational impact needs proof; an object-centered interactive historical story. |
| Flame in Freefall: AI-Powered Fire Safety Insights from Microgravity Combustion Data | 4 | 2 | 4 | 4 | 3 | 2 | **3.35** | Experimental comparability and document extraction; evidence-backed comparison of tightly selected experiments. |
| Identify Earth Locations that Analog the Permanent Moon Base Locations and Mars | 3 | 3 | 4 | 4 | 3 | 2 | **3.30** | Similarity depends on mission-specific weights; explain why one analog outranks another. |
| Interplanetary Survival Guide: Martian Map | 3 | 3 | 4 | 5 | 2 | 1 | **3.25** | Surface data integration and unsupported route safety; one annotated route with terrain uncertainty. |
| Create Health Monitoring Software for Astronauts on Space Missions | 4 | 2 | 3 | 4 | 3 | 1 | **3.10** | Representative longitudinal clinical data and intervention validity; human-reviewed health diary/trend prototype. |
| Planet X and SPHEREx | 2 | 2 | 5 | 5 | 2 | 1 | **3.00** | Image availability and astronomy expertise not audited here; image blinking with candidate triage, no discovery claims. |

The ranks are intentionally sensitive to team composition. Adding a SAR scientist and a verified image pair could move NISAR above Trend Detective. Adding an agronomist and local extension partner could move Field Shift to first. Removing scientific capability would lower fire harmonization because its main achievement must survive scientific questioning. A beautiful map cannot compensate for an invalid merged record.

### 2. Fire harmonization: the recommended scientific product

**Verified data position.** FIRMS offers historical MODIS Collection 6.1 records beginning 1 November 2000 and Suomi-NPP VIIRS 375 m records beginning 20 January 2012; NOAA-20 and NOAA-21 begin later. The historical archive supports CSV, JSON and shapefiles, with Earthdata or email authentication. NRT records are subsequently replaced by standard science-quality records with an approximately five-month lag. [8] The Area API requires a free map key, accepts a bounding box, and currently documents one to five days per call. Its stated transaction allowance is 5,000 per ten-minute interval; this is not permission to make inefficient bulk queries. [9]

A live South Asia Suomi-NPP CSV returned HTTP 200, 63,834 bytes, and 787 records dated 17–18 September 2026. The local file preserves latitude, longitude, acquisition time, confidence, scan/track dimensions, brightness and FRP. This verifies one live regional feed; it does not verify a multi-year calibration dataset. [23] NASA documents nominal MODIS and VIIRS hotspot display scales of approximately 1 km and 375 m respectively, and cautions that fires of differing size/intensity can trigger detections. A hotspot is consequently not a count of independent wildfire incidents or a measured burned-area polygon. [10,11]

**Proposed MVP.** Select one substantial area with a known fire season and one contrasting validation area, subject to data inspection. Keep a stable pair of streams, preferably Aqua MODIS and Suomi-NPP VIIRS, separate during baseline analysis. Show (a) native records, (b) common spatial/temporal summaries, and (c) the experimental adjusted series. Build a weekly or monthly burning calendar rather than pretending individual 375 m pixels can be reconstructed before VIIRS existed. Use regional/seasonal calibration on the overlap period. Show the training period, withheld periods, calibration direction, sample sizes and uncertainty beside the chart.

**Critical denominator decision.** FIRMS CSV contains positive detections. A date with no records cannot distinguish a clear no-fire observation from a cloudy or missing observation. MOD14A1 explicitly distinguishes fire, no fire and no observation through a daily 1 km fire mask. NASA also lists VNP14A1 as a daily gridded 1 km VIIRS product. [18,19] The latter should not silently be treated as the observation mask for a different 375 m detection algorithm. Product compatibility, temporal compositing and coverage assumptions need explicit verification. Daily gridded coverage is an approximation of valid observed area-days, not exact satellite overpass effort.

If compatible coverage is available, a proposed metric is detected active cell-days divided by valid observed land cell-days, multiplied by a stated scale such as 1,000. It must retain sensor identity, filters and uncertainty. If coverage cannot be obtained, label the result “sensor-calibrated detected activity” and show coverage unknown; do not claim an effort-adjusted or unbiased fire rate. A sensor-specific seasonal percentile can still support useful comparisons within that sensor, provided the limitations remain visible.

**Validation plan (early alternatives; the final selected binomial model is specified in docs/03-MODEL-AND-DATA-PROTOCOL.md).** Compare unadjusted common-grid aggregation against a transparent regional calibration baseline and one more flexible candidate. Use blocked time validation and a geographically withheld area; random row splitting would let closely related records contaminate evaluation. Report bias and error for monthly activity, peak-season timing error, interval coverage and behavior around sensor-change dates. Use a negative-binomial or hurdle/count model only if the count distribution and available covariates justify it. A high correlation alone does not prove harmonization: two sensors can track seasonality while disagreeing systematically in level.

Ground truth must be named precisely. Landsat/HLS image interpretation or suitable agency incident records can provide external reference checks for selected events, with cloud/missingness and reporting limitations. A published MODIS study compared roughly 250,000 agency reports and found detection differences linked to fire/environmental attributes. [21] MCD64A1 and VNP64A1 burned-area products are useful corroboration but are not independent truth: the burned-area processing uses active-fire information. A recent primary study validated VIIRS burned area with interpreted Landsat pairs and still found substantial omission and commission error. [20] Do not optimize active-fire occurrence counts against burned hectares as though they were the same quantity.

The strongest pitch is a visible before/after scientific diagnosis: a naive merge suggests an apparent change; the app exposes the sensor switch, applies a region-specific tested correction, and reports where evidence is insufficient. Every saved result includes a method receipt with source versions, filters, geometry and calibration version. An optional agent can explain that receipt and request a new analysis through constrained tools. It should never create measurements or make operational evacuation decisions.

### 3. Field Shift: potentially larger local relevance, more domain dependence

**Verified data position.** POWER provides analysis-ready daily meteorological data, including an agriculture community and standard JSON/CSV formats. Its underlying meteorological spatial resolution is documented as 0.5 by 0.625 degrees. Requesting many nearby farm coordinates does not create local observations. [2,3] A live three-day request near Dhaka returned temperature and corrected precipitation, with unit metadata; the test demonstrates the connector, not accuracy at a particular farm. [24] HLS supplies harmonized surface reflectance at 30 m, with frequent nominal observations. Clouds still limit usable optical observations, and spectral greenness does not directly identify soil nutrient availability or guaranteed crop yield. [4]

SMAP SPL4SMGP Version 8 provides three-hourly, 9 km modeled surface and root-zone soil moisture, with Earthdata authentication. The provider page notes a geolocation issue during 14 May–28 July 2026 and ongoing standard-product reprocessing; the effect on chosen exact granules must be checked. [5] SoilGrids offers 250 m predictions, six depth intervals and quantified uncertainty, but its official page reports the REST API temporarily paused without a restoration estimate. The maps use CC-BY 4.0. Official documentation describes GeoTIFF tiles and VRT access as alternatives. [6,7]

**Proposed product.** Limit the pilot to a defined agricultural zone, a small crop library and a documented set of rotations. Begin with current crop history, irrigation access, planting window, soil test or clearly labeled predicted soil properties, labor constraints and farmer priorities. Return three feasible rotation scenarios rather than an unsupported “best crop.” Each scenario explains which constraints it passes, where it requires irrigation or soil confirmation, and which priorities change its ranking. Climate anomalies inform stress scenarios; they do not become claims about exact field outcomes.

The differentiator should be a legible rotation ledger: season one, season two, water demand assumptions, crop-family succession constraints, labor peak and evidence behind every rule. A useful live interaction is to reduce available irrigation or move a planting date and show which scenario becomes infeasible. Uncertainty must change the output, including asking for a soil measurement when a crucial variable is missing. Avoid invented percentages of yield improvement, income gain or nitrogen recovery.

This option requires an agronomist or extension adviser to review crop rules and a few farmer interviews to establish the actual decision. A deterministic constraint engine and transparent scoring can be more defensible than training a predictive model on unrelated geography. Farmer-entered soil results should override coarse map priors with provenance preserved. The hackathon MVP can use cached raster subsets and explicit data timestamps. A multilingual explanation feature is valuable only after the agronomic comparison itself works.

### 4. Trend Detective and NISAR: two different alternatives

**Trend Detective.** Mature NASA time-series access is a strength. Giovanni already supports visualization and analysis of geophysical variables and requires Earthdata login; its current beta page also warns of cloud-credit limits. MERRA-2 documentation points to visualization, statistics and downloads through Giovanni. [14,15] IMERG provides half-hourly 0.1-degree precipitation products, with Final Run more suited to retrospective research and a typical multi-month latency. [16,17] These are concrete acquisition routes, though no protected granules were downloaded in this memo.

The proposed product should focus on one real investigation, such as changing dry-season heat and rainfall in contrasting agricultural districts. Include trend magnitude in physical units per decade, a baseline period, missingness, seasonal adjustment and confidence intervals. Distinguish change from evidence of a monotonic trend, and both from causal explanation. The Mann–Kendall test alone does not account for serial correlation or seasonality; the documentation explicitly warns about these assumptions. [25] Appropriate resampling, season handling and multiple-testing control are requirements for the proposed analysis, not cosmetic advanced features.

The distinctive demo could let a user compare a raw trend with its seasonal and autocorrelation-aware assessment, then reveal when a visually striking change is statistically inconclusive. A plain map with linear trend lines would reproduce existing tools. A claim-checking workbench that explains exactly why a statement is or is not supported is more compelling, and can be delivered with a small reproducible dataset.

**NISAR.** ASF's release notice dates initial public calibrated L-band access to 20 July 2026, covering observations on or after 17 June, with the full first-year record expected later in 2026. The catalog now contains provisional and beta collections, so that notice must not be interpreted as a permanent lower bound on every dataset's available date. [12,22] A live CMR query found `NISAR_L2_GCOV_PROVISIONAL_V1`, collection `C2854338529-ASF`. Its metadata explicitly describes partial validation and ongoing quality work; beta metadata says beta products are not intended for scientific research. [22]

GCOV is an attractive entry point because it provides terrain-corrected gamma-0 backscatter. The guide describes 10 or 20 m posting for many primary-frequency land products and 80 m for the secondary frequency; pixel spacing is not synonymous with independently validated physical resolving power. Polarization availability depends on acquisition mode. [13] A credible hackathon demo would use one actual, matching before/after pair with compatible geometry, polarization, product maturity and processing version. It would show radar change candidates and supporting context, not automatically classify all bright/dark changes as flood, forest loss or crop failure.

No NISAR binary science file was downloaded here, and no usable pair for Bangladesh or another target was verified. That is a selection gate, not a minor implementation detail. NISAR can outperform the top-three options for a team with SAR experience and prevalidated imagery. Without that gate, it introduces more schedule risk than the mature fire record.

## Synthesis & Insights

The four strongest options all become more credible when the unit of decision is narrow: a region-month for fire, a rotation for farms, a testable local claim for trends, or a verified image pair for NISAR. More datasets increase the number of assumptions that have to be reconciled. NASA source count is not a substitute for showing what each source contributes.

Fire harmonization best matches the revised team profile because the difficult scientific work is also the product's main story. Field Shift can deliver more immediate local understanding, but its critical knowledge lies partly outside satellite data. NISAR offers freshness and visual drama at the cost of a stricter acquisition and interpretation gate. Trend Detective has the safest fallback path if time or access blocks the others.

## Recommendations

Select fire harmonization provisionally, then run a short feasibility gate before recruiting around an overbroad vision. The data lead must obtain overlapping historical MODIS and VIIRS data for two candidate areas, inspect completeness, and establish whether compatible non-fire/coverage masks are obtainable. The science lead must define the target quantity and an honest validation reference. If those gates fail, retain a sensor-separated calendar and disclose the limits, or switch to Trend Detective rather than claiming a corrected record that was never validated.

Recruit one geospatial/data engineer, one statistician or remote-sensing scientist, one backend engineer, one visualization/frontend engineer, and one product/design/storytelling lead; a sixth teammate can focus on external reference review and user interviews. These are responsibilities and can overlap. The first demonstration should contain a single scientifically meaningful interaction, a failure case and a reproducible evidence export. Add agent explanations only after that workflow is dependable.

## Limitations & Caveats

This memo does not promise exhaustive coverage of all datasets or all possible challenge concepts. Ten challenges received a brief-level comparison rather than a data-by-data audit. Rankings depend on inferred team size, confirmed technical strength and preference for practical Earth impact. The selected official fire page was retrieved directly after browser-service errors; its resource tab was empty at retrieval. Dataset versions, service notices and access rules can change before the hackathon.

The small live tests establish HTTP access and response structure, not scientific validity or reliability at scale. Earthdata-authenticated file downloads, FIRMS historical export completion, end-to-end calibration, reference labeling and agronomic validation remain future work. Most metadata facts appropriately have one canonical provider source; independent validation is discussed separately and was not invented to satisfy an arbitrary citation count.

## Methodology Appendix

Primary-source searches covered the official Space Apps domain, NASA POWER, FIRMS, NASA Earthdata, HLS, NSIDC, ASF, ISRIC, NASA GPM and primary research on fire validation. Contradictions were retained: SoilGrids Swagger remains searchable while its official landing page says the service is paused; NISAR's dated release notice and live catalog describe different stages of archive growth. Current provider notices took precedence over stale generalized assumptions.

Files `sources.jsonl`, `evidence.jsonl`, `claims.jsonl` and `run_manifest.json` preserve source identity, short quotes with locators, claim status and limitations. `access_checks.json` records live request results. Downloaded NASA samples are preserved alongside this memo. A direct shell network test initially failed under the sandbox; the authorized network-enabled retry succeeded. No private credentials were read or created, and no historical dataset availability is inferred merely from an API documentation page.

## Bibliography

[1] 2026 challenge briefs supplied by user. [user_supplied](https://www.spaceappschallenge.org/2026/challenges/). Retrieved 18 September 2026.

[2] NASA POWER API tutorial. [official_documentation](https://power.larc.nasa.gov/docs/tutorials/service-data-request/api/). Retrieved 18 September 2026.

[3] NASA POWER Daily API. [official_documentation](https://power.larc.nasa.gov/docs/services/api/temporal/daily/). Retrieved 18 September 2026.

[4] Harmonized Landsat and Sentinel-2. [official_documentation](https://hls.gsfc.nasa.gov/). Retrieved 18 September 2026.

[5] SMAP SPL4SMGP Version 8. [official_data_centre](https://nsidc.org/data/spl4smgp/versions/8). Retrieved 18 September 2026.

[6] SoilGrids global gridded soil information. [official_data_provider](https://isric.org/explore/soilgrids). Retrieved 18 September 2026.

[7] SoilGrids layers. [official_documentation](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_01.html). Retrieved 18 September 2026.

[8] FIRMS archive download. [official_documentation](https://firms.modaps.eosdis.nasa.gov/download/). Retrieved 18 September 2026.

[9] FIRMS Area API. [official_documentation](https://firms.modaps.eosdis.nasa.gov/api/area/). Retrieved 18 September 2026.

[10] NASA FIRMS WMS. [official_documentation](https://firms.modaps.eosdis.nasa.gov/mapserver/wms-info/). Retrieved 18 September 2026.

[11] FIRMS US/Canada FAQ. [official_support](https://forum.earthdata.nasa.gov/viewtopic.php?t=5200). Retrieved 18 September 2026.

[12] NISAR L-Band Data Now Publicly Available. [official_data_centre](https://asf.alaska.edu/notices/nisar-l-band-data-now-publicly-available/). Retrieved 18 September 2026.

[13] NISAR GCOV Data User Guide. [official_documentation](https://nisar-docs.asf.alaska.edu/gcov/). Retrieved 18 September 2026.

[14] NASA Giovanni. [official_application](https://giovanni.earthdata.nasa.gov/). Retrieved 18 September 2026.

[15] MERRA-2 data access. [official_documentation](https://gmao.gsfc.nasa.gov/gmao-products/merra-2/wmo-data-access_merra-2/). Retrieved 18 September 2026.

[16] IMERG technical documentation. [official_documentation](https://gpm.nasa.gov/sites/default/files/2023-07/IMERG_TechnicalDocumentation_final_230713.pdf). Retrieved 18 September 2026.

[17] IMERG latency. [official_documentation](https://gpm.nasa.gov/resources/faq/what-determines-latency-imerg). Retrieved 18 September 2026.

[18] MOD14A1.061 Earth Engine catalog. [platform_documentation](https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD14A1). Retrieved 18 September 2026.

[19] VNP14A1 NASA product record. [official_product_record](https://ladsweb.modaps.eosdis.nasa.gov/missions-and-measurements/products/VNP14A1). Retrieved 18 September 2026.

[20] NASA VIIRS burned area product validation and MODIS comparison. [primary_research](https://doi.org/10.1016/j.rse.2025.115006). Retrieved 18 September 2026.

[21] Detection rates and biases of MODIS and agency reports. [primary_research](https://www.sciencedirect.com/science/article/pii/S0034425718304826). Retrieved 18 September 2026.

[22] NISAR CMR catalog query, live response. [live_api](https://cmr.earthdata.nasa.gov/search/collections.json?keyword=NISAR%20GCOV&page_size=5). Retrieved 18 September 2026.

[23] FIRMS VIIRS South Asia 24-hour sample. [live_api](https://firms.modaps.eosdis.nasa.gov/data/active_fire/viirs/csv/SUOMI_VIIRS_C2_South_Asia_24h.csv). Retrieved 18 September 2026.

[24] POWER Dhaka-area 3-day sample. [live_api](https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,PRECTOTCORR&community=AG&longitude=90.4&latitude=23.8&start=20240101&end=20240103&format=JSON). Retrieved 18 September 2026.

[25] Trend generation documentation. [platform_documentation](https://gis.earthdata.nasa.gov/portal/help/en/11.5/analyze/generate-trend.htm). Retrieved 18 September 2026.
