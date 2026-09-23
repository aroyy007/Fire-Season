# Fire Season — product requirements document

Version 2.0  
Status: approved scope for implementation planning  
Prepared: 20 September 2026  
Team: One Last Launch  
Challenge: Harmonization of MODIS and VIIRS Hot Spots

## Product decision

Fire Season is a sensor-aware burning activity calendar for regional land and forest monitoring. It helps an analyst answer one question:

> Did recorded burning change, or did the observing system change?

The product will preserve native MODIS and VIIRS measurements, then show a common-reference comparison only when a documented transfer has passed held-out evaluation. It will state when a comparison is unavailable. The judged experience will run from precomputed, versioned evidence and remain usable without a network connection.

This narrow product is the team's entry for the [2026 Harmonization of MODIS and VIIRS Hot Spots challenge](https://www.spaceappschallenge.org/2026/challenges/harmonization-of-modis-and-viirs-hot-spots/). It is designed for a four-person team and can absorb a fifth member with forestry, fire-ecology, or user-access experience.

## Why this problem is still open

A map of satellite detections is easy to build and easy to misread. MODIS and VIIRS differ in spatial resolution, detection response, sampling, product construction, and quality flags. A larger VIIRS count in a later year may reflect smaller detectable sources rather than more burning. Cloud and missing observations add another ambiguity: a blank month can mean low detected activity or little usable evidence.

Public fire dashboards already cover maps, recent detections, alerts, weather context, and conversational explanations. Fire Season will not compete by adding another set of those features. Its contribution is an evaluated bridge between two specific daily active-fire products, together with the evidence needed to inspect that bridge.

## User and decision

The primary user is a **Monitoring Analyst** working at district or regional level in land or forest management. The named institutional target is a Bangladesh Forest Department regional analyst. Until that person is available, an environmental or remote-sensing researcher may act as a testing proxy.

The analyst prepares a seasonal monitoring plan. Fire Season supports three parts of that job:

1. identify months that usually show higher detected burning activity;
2. inspect whether an unusual historical month remains unusual after the sensor transition is accounted for;
3. select months and 10 km analysis blocks for human review, field coordination, or closer monitoring.

An **Investigation Priority** is not an emergency severity score. Fire Season does not dispatch responders, predict spread, determine legality, or label a region safe.

## Product promise

The application must make five things clear without requiring the user to read a methods paper:

- which satellite product produced a Native Sensor Record;
- what was actually observed and how much valid support exists;
- whether Comparable Activity is available;
- what uncertainty and calibration limits apply;
- how to reproduce the displayed result from its Evidence Receipt.

If any of those points is missing, the product has not solved the interpretation problem.

## Study design

The Competition MVP contains two predefined regions.

| Region | Role | Release rule |
| --- | --- | --- |
| Northeast India–Myanmar bounded pilot | Science Pilot | Used to establish that data access, paired support, calibration, and evaluation are viable. |
| Chattogram Hill Tracts with adjacent Cox's Bazar candidate | Local Impact Case | Shown as a comparable result only if its support and calibration scope pass; otherwise shown as an honest unavailable case. |

Exact boundaries are frozen only after paired masks, land support, activity frequency, and product overlap have been inspected. Users cannot draw or upload polygons in the Competition MVP.

## Measurement contract

The primary measurement is the **Detected Activity Rate** for a declared product, region or 10 km block, and month:

`1,000 × detected active land-cell-days ÷ valid observed land-cell-days`

The science stream uses these compatible daily 1 km mask products:

- Aqua MODIS MYD14A1 Collection 6.1;
- Suomi-NPP VIIRS VNP14A1 Version 2.

The first transfer expresses VIIRS activity on the Aqua MODIS **Reference Product** scale. **Comparable Activity** means what the released model estimates Aqua MODIS would have recorded under the declared conditions. It does not mean the physical number of fires.

FIRMS 375 m detections may appear as recent context. They remain a separate stream and never contribute to the daily-mask numerator or denominator.

## Core experience

The application opens directly on the burning activity calendar for a Curated Region. The user sees the selected region, analysis period, measurement definition, sensor-era boundary, observation coverage, and view control.

The primary path is:

1. choose a Curated Region;
2. scan the year-by-month calendar;
3. select an unusual month;
4. switch between Native Sensor Records and Comparable Activity;
5. inspect Observation Support, uncertainty, and block-level Investigation Priorities;
6. open the Evidence Receipt;
7. export a one-page Monitoring Brief.

The product must also demonstrate a month or region where the comparison is unavailable. Scientific refusal is a normal result state.

## Functional requirements

| ID | Priority | Requirement | Acceptance condition |
| --- | --- | --- | --- |
| PR-01 | Must | Curated Region selection | Two named regions are listed. No login is required. Each region states whether it is the Science Pilot or Local Impact Case. |
| PR-02 | Must | Burning activity calendar | A year-by-month matrix loads from a released Analysis Artifact and exposes the activity unit, selected period, and sensor-era boundary. |
| PR-03 | Must | Native Sensor Records | MODIS and VIIRS records retain platform, product, collection, and measurement identity. The UI never labels a sum of their counts as harmonization. |
| PR-04 | Must | Observation states | No observation, observed non-fire, detected activity, and insufficient support are distinct in data, text, and visual treatment. |
| PR-05 | Must | Observation Support | Each month reports eligible, valid, and detected land-cell-days plus the valid-support fraction. |
| PR-06 | Must | Comparable Activity | A value appears only when the linked calibration is released and eligible for the product versions, geography, activity range, and support. |
| PR-07 | Must | Unavailable Comparison | An ineligible comparison has a null value and a specific machine-readable and human-readable reason. Native evidence stays visible. |
| PR-08 | Must | Uncertainty | Available Comparable Activity includes a labeled interval. The interface states that it does not cover every source of sensor omission or domain shift. |
| PR-09 | Must | Activity Anomaly | The selected month is compared with the same calendar month in a fixed historical window that excludes the selected year. |
| PR-10 | Must | Evidence inspection | A selected month links to sources, checksums, quality policy, calibration release, evaluation summary, limitations, and receipt ID. |
| PR-11 | Must | Immutable exports | The user can download CSV values and a JSON Evidence Receipt whose values match the displayed artifact. |
| PR-12 | Must | Offline judged path | Region selection, calendar inspection, comparison, receipt viewing, and export work from the built application with network access disabled. |
| PR-13 | Should | Context map | A small map locates the region and selectable 10 km analysis blocks. Equivalent information is available in a table. |
| PR-14 | Should | Investigation Priority | Supported months and blocks can be marked for human review without implying emergency severity or automatic action. |
| PR-15 | Should | Monitoring Brief | A printable one-page brief contains the chosen evidence, limitation text, and receipt ID. |
| PR-16 | Should | Region-to-region consistency | Both Curated Regions use the same metric and reference direction while preserving their own support and eligibility. |
| PR-17 | Could | Recent context | A clearly separated FIRMS layer may show recent detections if it does not compete with the historical interpretation flow. |
| PR-18 | Later | Evidence Investigator | A bounded local assistant may explain released evidence after every core gate passes. It may not calculate scientific results. |

## Scientific release gates

A candidate calibration becomes a **Calibration Release** only when all of the following are true:

- it has at least five training seasons and two untouched held-out seasons;
- the held-out mean absolute error is at least 10% lower than the best simple transfer baseline;
- signed bias is not materially worse in either pilot geography;
- the seasonal peak-month error is no more than one month where a peak is identifiable;
- a nominal 90% interval achieves 85–95% empirical coverage on adequate independent test support;
- the product versions, quality policy, geography, activity range, and support fall inside its declared domain;
- a geographically separate Transfer Test Region has been reported;
- source and model artifacts have checksums and a reproducible environment record.

The starting monthly support gate is 50% valid land-cell-days. Fifty positive block-months is a diagnostic floor for model fitting, not proof of adequate evidence. Threshold changes must be decided from training data, versioned, and disclosed before held-out results are examined.

When a release gate fails, Fire Season publishes Native Sensor Records and an Unavailable Comparison. It does not publish an experimental estimate with softer wording.

## Monitoring Brief content

The one-page brief contains:

- region and analysis period;
- typical higher-activity months;
- the selected Activity Anomaly;
- Native Sensor Records and eligible Comparable Activity;
- Observation Support and interval bounds;
- Investigation Priority for month and blocks;
- calibration status and main limitations;
- Evidence Receipt identifier and source attribution.

The brief is generated from fixed artifact fields. A language model is not needed to create it.

## Language and content rules

The interface uses “No usable observations” rather than “No fires,” “Estimated on the Aqua reference scale” rather than “True activity,” and “Higher than this region's March baseline” rather than “High danger.” A hot spot may correspond to wildfire, agricultural burning, or another thermal source; the product does not assign cause.

The judged interface and submission are in English. A short Bengali summary may be added after the English experience passes its release checks.

## Accessibility requirements

- Every calendar cell is reachable and selectable by keyboard.
- Focus returns to the selected cell when the evidence panel closes.
- Accessible names include period, value type, activity, support, interval, and status.
- Charts and the map have table alternatives.
- Color is never the sole carrier of activity, missingness, uncertainty, or selection.
- Text and controls meet WCAG 2.2 AA contrast targets.
- The narrow layout converts one selected year into a twelve-row month list.
- Reduced-motion preferences disable nonessential animation.

## Success measures

### Science

- The calibration release gates pass on untouched data, or the interface correctly abstains.
- A second geography has a separately reported transfer result.
- Every displayed comparable value resolves to a Calibration Release and Evidence Receipt.
- No observation state is silently converted to zero activity.

### Usability

Five representative testers complete three tasks: identify the typical higher-activity season, distinguish no observation from no detected activity, and locate the Evidence Receipt. The working target is at least four successful testers for each task. Time, errors, and incorrect interpretations are recorded.

### Reliability

- The complete primary path works offline on the presentation laptop.
- A cached region opens within two seconds on the declared test laptop.
- Selecting a month updates its evidence within 300 ms after the artifact is loaded.
- CSV, receipt, brief, and screen values agree for the demonstrated month.

### Competition communication

- A reviewer can state the problem and product contribution after the opening interaction.
- The demonstration shows both a released comparison and a deliberate unavailable result.
- NASA sources, open-source components, assets, and AI assistance are attributed.
- The final public links work in a private browser without authentication.

## Explicit exclusions

The Competition MVP excludes arbitrary polygons, live processing, user accounts, paid services, commercial map tokens, global coverage claims, fire spread prediction, emergency advice, burned-area estimation from hot-spot counts, ignition-cause classification, carbon accounting, alerts, hardware, and a chatbot or voice interface.

## Free and open-resource policy

The project must build, reproduce approved analyses, run the judged demonstration, and publish the application using Open Resources. Free NASA registration and access keys are allowed during preparation. Paid APIs, trial credits, proprietary inference endpoints, and paid hosting cannot be required.

The intended stack is Python and open geospatial/statistical libraries for science, React and TypeScript for the interface, MapLibre for optional map rendering, local open/public-domain geography, and GitHub Pages plus a local static fallback for delivery.

## Team and delivery boundary

Four owners cover remote-sensing/statistics, Python data and reproducibility, frontend/data visualization, and product/testing/submission. A fifth member should bring domain knowledge or direct user access.

The pre-event feasibility gate is a real paired MODIS–VIIRS sample that can be retrieved, decoded, aligned, aggregated, and timed. If paired-mask access or overlap remains untenable by 18 October 2026, the team pivots rather than making an unsupported harmonization claim.

The event build cuts optional AI, Bengali UI, live refresh, additional layers, extra exports, and broader region support before cutting Native Sensor Records, Observation Support, the unavailable state, or Evidence Receipts.

## Remaining evidence to obtain

This PRD defines the product; it does not claim that a calibration has passed. Before implementation can be described as validated, the team still needs:

- decoded paired daily masks from the two declared products;
- frozen region boundaries and temporal splits;
- held-out and transfer-test results;
- a released Analysis Artifact;
- five recorded usability sessions;
- confirmation of the final 2026 submission format and preparation rules.

## Source documents

- [NASA Space Apps challenge page](https://www.spaceappschallenge.org/2026/challenges/harmonization-of-modis-and-viirs-hot-spots/)
- [MODIS Collection 6/6.1 Active Fire Product User's Guide](https://www.earthdata.nasa.gov/s3fs-public/2023-09/MODIS_C6_C6.1_Fire_User_Guide_1.0.pdf)
- [VIIRS Active Fire Product User's Guide](https://viirsland.gsfc.nasa.gov/PDF/VIIRS_activefire_User_Guide.pdf)
- [VNP14A1 Version 2 catalog record](https://www.earthdata.nasa.gov/data/catalog/lpcloud-vnp14a1-002)
- [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/)
