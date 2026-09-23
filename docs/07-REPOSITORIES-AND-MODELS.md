# Related code and model due diligence

This is a focused inventory of relevant starting points, not a claim to have inspected every related repository. README inspection, repository metadata, license text, endpoint tests and executed model evaluations are different evidence levels. No external research repository was installed or executed in this work.

## Recommended fire stack and prior art

| Repository / source | What it offers | Reuse decision and verification limit |
|---|---|---|
| [GROW](https://github.com/Florianopolis-NASA-Space-Apps/wildfires_chat_dashboard) | Current implementation of a 2024 winning environmental GIS project: FIRMS, React, Mapbox and voice/tool interaction | Verified identity against NASA award announcement; MIT shown. Study interaction, but calendar calibration must be the new contribution. Current code need not match its 2024 submission. |
| [FireAtlas / FEDS](https://github.com/Earth-Information-System/fireatlas) | Groups satellite detections into estimated fire events/perimeters | Useful scientific prior art; not a MODIS–VIIRS historical transfer model. Root LICENSE request returned 404; do not assume reuse rights without locating authoritative terms. |
| [NASA fire-events viewer](https://github.com/NASA-IMPACT/us-fire-events-tool) | Existing fire-event exploration application | Apache-2.0 license text downloaded. Study its data-navigation patterns; adding another map alone offers limited differentiation. |
| [earthaccess](https://earthaccess.readthedocs.io/en/latest/) | NASA Earthdata discovery, authentication and access workflows | Candidate ingestion library. Documentation read; GitHub metadata calls hit rate limits. Pin and review its distribution/license when implementing. |
| [statsmodels](https://github.com/statsmodels/statsmodels) | GLMs, count models and statistical diagnostics | Preferred transparent model implementation. Documentation inspected; no model fitted. |
| [MapLibre GL JS](https://github.com/maplibre/maplibre-gl-js) | Browser vector-map rendering | Proposed context map; library and basemap licenses are separate. README inspected; version and full dependency-license audit deferred to build. |
| [TiTiler](https://github.com/developmentseed/titiler) | Dynamic raster tile services | Optional when raster context is needed. Omit from MVP if static regional tiles suffice. |
| [Storm Prophet](https://github.com/Wizard2007/storm-prophet) | 2023 winning space-weather LSTM project | Relevant precedent for a model-led entry; Dst prediction is not transferable fire training data. Architecture/hyperparameters were not independently reproduced. |

The proposed binomial transfer model is new project work. None of these repositories is represented as a ready-made validated solution to this year's harmonization task. Model evaluation must compare against straightforward native and seasonal baselines before adding complexity.

## Agriculture alternatives checked

| Model | Inputs and intended use | License/access evidence | Fit for Field Shift |
|---|---|---|---|
| [AquaCrop-OSPy](https://github.com/aquacropos/aquacrop) | Weather, crop, soil, water and management; crop-water scenarios | GitHub license metadata: Apache-2.0 | Accessible Python option for comparative water scenarios; calibration still required. Do not assume full soil fertility, salinity or rotation carryover support. |
| [FAO-endorsed AquaCrop source](https://github.com/KUL-RSDA/AquaCrop) | Process-based crop-water model | Downloaded license explicitly states BSD-3 for the Fortran version, despite GitHub `NOASSERTION` | More direct source implementation; distinguish its features/version from OSPy. |
| [PCSE / WOFOST](https://github.com/ajwdewit/pcse) | Weather, soil, cultivar and management parameters | Official documentation states EUPL; GitHub automated classification was inconclusive | Strong process-model candidate with appropriate crop parameters and domain review; not plug-and-play crop advice. |
| [DSSAT CSM](https://github.com/DSSAT/dssat-csm-os) | Crop/soil/weather/management simulation | BSD-3-Clause license metadata/text checked | Domain-rich but parameter and setup burden may exceed MVP. |
| [APSIM Next Generation](https://github.com/APSIMInitiative/ApsimX) | Agricultural systems and management simulation | Custom general-use license downloaded; do not label as ordinary permissive OSS | Consider only after reviewing intended use and distribution terms. |

FAO describes AquaCrop as a field-scale crop-water model with uniform-field assumptions and vertical water fluxes. That supports bounded scenarios; it does not justify guaranteed yield or soil-health gains for an arbitrary farm. [FAO overview](https://www.fao.org/aquacrop/overview/en) The primary NASA-supported crop-rotation research also reports effects that depend on sequence and weather, reinforcing the need for local agronomic rules. [NASA crop-rotation article](https://science.nasa.gov/earth/earth-observatory/how-to-rotate-crops-154601/)

## Foundation models and radar tooling

[Prithvi-EO-2.0](https://github.com/NASA-IMPACT/Prithvi-EO-2.0) has MIT repository metadata and released model information; [TerraTorch](https://github.com/torchgeo/terratorch) and [HLS foundation examples](https://github.com/NASA-IMPACT/hls-foundation-os) have Apache-2.0 metadata. These are relevant to optical EO representation learning and task adaptation. Repository licensing does not automatically establish every checkpoint/dataset's terms. No checkpoint, GPU inference or downstream score was tested here.

For Fire Season, a foundation model would add data preparation and validation without directly solving the sampling mismatch. It may later assist reference-image segmentation if task-specific labels and a clear evaluation justify it. It should not be selected merely to advertise AI.

ISCE3 and MintPy were considered as radar-processing leads, but GitHub API requests hit rate limits before their metadata/license review completed. They are not verified dependencies in this plan. NISAR selection still requires a real compatible repeat pair, product maturity review and SAR interpretation skill. Do not confuse a foundation model pretrained on optical imagery with a validated NISAR change detector.

## Model-selection conclusion

Start with a transparent statistical transfer and deterministic explanations. CPU-scale science is sufficient for a strong demonstration if the measurement, validation and interface are compelling. Add a constrained language-model explanation only after numerical consistency tests work. If a model does not outperform the relevant baseline or cannot explain when it abstains, leave it out of the released product.
