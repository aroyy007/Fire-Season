# Science, data and model protocol

All algorithms and thresholds below are proposed. Access smoke tests have run; no calibration has been trained and no accuracy is claimed.

## Measurement definition

The primary quantity is **detected active land-cell-days per 1,000 valid observed land-cell-days**, for a specified product and period. A 1 km cell with several detections in its daily composite contributes at most one active cell-day. This measures product-specific detected activity, not independent fires, burned area, ignition probability or danger to a person.

For product s, analysis block g and month t, let F be accepted fire cell-days and N be valid observed land-cell-days. The native rate is `R = 1000 × F/N`; if N is zero, R is null. The proposed primary mask policy counts nominal/high-confidence fire as positive and clear non-fire land as negative. Low-confidence fire is excluded from primary support and included in a sensitivity run. Water, cloud, unknown and unprocessed cells are excluded. Map these semantic classes from each current product guide; fail ingestion if class definitions are not verified. [MODIS guide](https://www.earthdata.nasa.gov/s3fs-public/2023-09/MODIS_C6_C6.1_Fire_User_Guide_1.0.pdf) · [VIIRS guide](https://viirsland.gsfc.nasa.gov/PDF/VIIRS_activefire_User_Guide.pdf)

Daily composites do not describe every clear overpass. Consequently, this is a valid-support normalization, not a complete observation-effort correction. Sampling time, subpixel fire size and product-specific detection effects remain. A derived transfer estimates a reference product's behavior; it does not recover invisible historical small fires.

## Candidate data inventory

| Source | Intended role | Access and verification | Limitations / fallback |
|---|---|---|---|
| MYD14A1.061, Aqua MODIS daily 1 km | Historical reference masks | Historical CMR granules found for March 2023; binary raster not fetched | Decode daily planes inside eight-day packaging; use authorized Earthdata access. |
| VNP14A1.002, NPP VIIRS daily 1 km | Overlap transfer masks | Historical CMR records found | Uses 750 m bands, not the FIRMS 375 m algorithm; delivery transition in Nov 2026. |
| VJ114A1.002 / VJ214A1 | NOAA-20/21 future continuity | NOAA-20 catalog discovery tested; NOAA-21 recommended in official notice | Fit platform-specific transfer; no silent substitution. |
| FIRMS MODIS / VIIRS regional CSV | Recent point context and ingestion proof | Real public CSVs downloaded and parsed | NRT, positive detections only; no valid/no-fire denominator. |
| MYD14 / VNP14 L2 and geolocation | Later matched-overpass method | MYD14 and VNP14IMG catalog discovery tested; VNP14 750 m route needs separate check | Swath matching and geolocation increase effort; IMG is a different algorithm. |
| HLS / Landsat imagery | Selected external reference interpretation | HLS catalog sample returned; imagery not downloaded | Clouds; burned scars and active fire are different targets. |
| MCD64A1 / VIIRS burned area | Corroborating seasonal context | Documented, not tested here | Not independent ground truth; algorithm uses active-fire information. |
| Land-cover product | Stratify heterogeneous areas | Optional and not fetched | Must record version/year; no global extrapolation from one biome. |
| Agency incident records | Independent event reference where accessible | No specific regional incident set secured | Reporting bias, differing incident definitions and time/location tolerances. |

Product access: [NASA VNP14A1](https://www.earthdata.nasa.gov/data/catalog/lpcloud-vnp14a1-002), [MYD14A1 file specification](https://ladsweb.modaps.eosdis.nasa.gov/filespec/MODIS/6/MYD14A1), [FIRMS archive](https://firms.modaps.eosdis.nasa.gov/download/), [FIRMS Area API](https://firms.modaps.eosdis.nasa.gov/api/area/), [HLS](https://hls.gsfc.nasa.gov/).

## Spatial and temporal support

Retain verified native sinusoidal tile/pixel coordinates. Group aligned 1 km cells into fixed 10×10-pixel analysis blocks. “10 km” is shorthand; calculate area from the actual grid. Use a documented centroid inclusion rule for AOI boundary pixels to retain integer binomial trials; state that narrow/small AOIs are not reliable at this scale. Reject areas with too few land pixels. Do not create a false fine-resolution result by upsampling.

The unit for model fitting is block-month. Training uses the intersection of valid pixel-days from the two products, with matching date/grid and the same QA policy. This removes some coverage mismatch during fitting but selects observable conditions; it cannot make cloudy periods representative. Store common support, each native support, and the fractions lost through matching. At inference, moving from paired support to single-sensor support is a domain assumption and must be checked explicitly.

Aggregate monthly for the MVP. Daily maps are for inspection. Weekly early-warning claims need a separate evaluation because sparse counts and daily sampling are less stable. The proposed historical study interval is 2013–2024, subject to archive completeness and version checks. NRT data is not spliced into a science-quality historical series without a visibly provisional mode.

## Model ladder

| Candidate | Purpose | Training / compute | Decision |
|---|---|---|---|
| Native sensor calendars | Honest baseline | No fitted model; CPU aggregation | Always retain. |
| Same-scale identity mapping | Transfer baseline | No fitting | Measures whether extra modeling helps. |
| Seasonal constant / simple monotone calibration | Minimal fitted baseline | Regional overlap; CPU | Required comparison. |
| Grouped binomial GLM with logit link | Transparent reference transfer | Block-month successes/trials; CPU | Primary candidate. |
| Beta-binomial or hierarchical logistic model | Extra dispersion / partial pooling | More fitting and diagnostic work | Adopt only if GLM residuals justify it. |
| Gradient-boosted trees | Nonlinear challenger | Needs enough independent blocks and calibration | Later; avoid opaque improvement on leaked splits. |
| Prithvi / TerraTorch | Optical reference-image tasks | Pretrained EO backbone still needs task setup and validation | Not the harmonization engine. |
| LLM | Explain saved evidence | Optional service inference | Never predicts the scientific quantity. |

For the GLM, target the Aqua fire count `F_A` out of paired support `N_pair`. Predictors initially include a smoothed VIIRS activity logit, seasonal sine/cosine, and support fractions. A land-cover term is added only if available and supported by sufficient samples. Do not use a target-year ID that would make future generalization meaningless. The response is passed as successes/failures, not incorrectly as raw counts under an unconstrained linear regression. [Statsmodels GLM documentation](https://www.statsmodels.org/stable/generated/statsmodels.genmod.generalized_linear_model.GLM.html)

For prediction, report `1000 × predicted_probability` as **Aqua-reference estimated activity**. Historical Aqua observations and modeled VIIRS estimates retain distinct visual marks. Where both exist, prefer the fixed reference measurement for the historical line and use the transfer for evaluation; do not double-count or average correlated streams without a justified fusion model. No global multiplier is proposed.

## Evaluation protocol

Pre-register candidate splits before fitting: 2013–2019 training, 2020–2021 model/threshold selection, 2022–2024 untouched temporal test, plus one geographically separated test area. These dates are a proposed template and can change once coverage is inspected, but freeze them before inspecting test performance. Keep neighboring spatial blocks and adjacent seasonal sequences together. Any smoothing, feature scaling, tuning and resampling must operate within training folds.

Report rate MAE, signed bias, seasonal peak-month error, skill against identity and seasonal baselines, and prediction-interval empirical coverage. Report results by region, season, activity stratum and coverage stratum; pooled performance can hide failure in small-fire areas. Compare interval width as well as coverage, since an uninformatively broad interval can cover everything. Check pseudo-transitions within a stable overlap period and sensitivity to confidence filters. Do not require a real physical trend to disappear merely because a sensor changes.

Use spatial and annual/seasonal block resampling for uncertainty, initially 200 bootstrap fits as a planning default. Inspect residual dependence before choosing block sizes. A binomial observation model is a working approximation: fires cluster and observations are dependent. Bootstrap or overdispersion modeling addresses some of this; it does not remove cloud-selection bias. Label intervals by their actual construction.

Proposed release gate: at least 10% lower held-out MAE than the best simple transfer baseline, absolute bias not materially worse in either pilot, and peak-season timing error no greater than one month where season peaks are identifiable. Assess a nominal 90% interval, targeting empirical coverage of 85–95% with adequate independent test blocks. These are team acceptance targets, not published universal scientific standards. If test support is too small to assess them, say so and keep the model experimental.

## Abstention and anomaly rules

Proposed guardrails: require at least 50% usable land-cell-day support in a displayed month, five training seasons, two held-out seasons and sufficient positive examples for fitting. Determine positive-example minimum and covariate-support bounds from training-only diagnostics; an example starting gate is 50 positive block-months, not proof of adequacy. These gates are configurable, versioned and sensitivity-tested. Mask changes and unsupported products invalidate old calibration unless re-evaluated.

An anomaly is a descriptive comparison against the same month in a fixed reference period, initially 2013–2021 for later test years. Require at least eight usable baseline years for percentile display. With few years, show a rank and range rather than a spurious precise tail probability. Bootstrap uncertainty may make the anomaly indeterminate. Baseline years must not include the queried year; long-term trend and nonstationarity are disclosed. This feature describes unusual recorded activity, not tomorrow's fire forecast.

## What the current checks establish

Saved evidence includes real MODIS and VIIRS regional CSV responses, NASA POWER weather JSON, NISAR and HLS catalog metadata, fire-product granule metadata, product manuals and repository/license metadata. The recent MODIS sample contains 3,759 rows; the VIIRS sample contains 11,695 rows from the downloaded regional feeds. Their counts are **not a comparative result**: platform coverage, timing and sensitivity differ. Checksums and request URLs are in the endpoint ledgers.

No authenticated historical raster download, paired mask decode, training run, model score or field-impact test has occurred. These remain the first implementation gates. A downloadable catalog entry is not a successfully decoded science file. An observed hotspot is not independently verified wildfire truth.
