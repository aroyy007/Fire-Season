# Fire Season: duplication audit and competition verdict

**Audit date:** 2026-09-19  
**Question:** Has this product already been built, and is it strong enough to pursue for NASA Space Apps?

## Scope and confidence

No search can prove that nothing similar exists anywhere on the internet or in every GitHub repository. This audit used four independent search tracks: official NASA and Space Apps pages; operational fire platforms; scientific and technical literature; and public GitHub repositories. It searched exact challenge language, feature combinations, sensor names, historical fire calendars, harmonization, time series, and previous Space Apps fire projects.

The result is sufficient for a product decision, but it is not a patent or freedom-to-operate search. Confidence is **high** about the major products and previous Space Apps overlap, and **moderate** about small or poorly indexed repositories.

## Direct answer

The broad idea has already been built in pieces:

- NASA FIRMS already supplies MODIS and VIIRS hotspots through maps, alerts, downloads, archives, APIs, and web services.
- GWIS already provides current-season comparisons, historical fire seasonality, separate MODIS and VIIRS anomaly charts, and near-real-time fire perimeters derived from both sensors.
- Public repositories already map both sensors, compare historical counts, cluster detections, and create regional fire time series.
- NASA-funded research and a 2026 scientific paper already work on correction or harmonization of multi-sensor fire records.
- Space Apps has many earlier fire maps, prediction tools, alert systems, and AI dashboards. GROW won the 2024 Local Impact global award with a FIRMS map, historical context, weather, and a voice assistant.

I did **not** find a previous Space Apps project or public product matching the whole proposed interaction: an area-of-interest burning calendar built from compatible MODIS and VIIRS daily fire masks, calibrated in the overlap period, evaluated on held-out data, showing raw versus harmonized values, uncertainty, observation quality, and a reproducible evidence receipt. That combination is the defensible product gap. It is narrower than the original idea.

## Closest prior art

| Existing work | What already overlaps | What remains different |
|---|---|---|
| [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/) | MODIS/VIIRS fire map, archive, alerts, downloads, services | Primarily distributes and visualizes sensor products; it does not present the proposed evaluated cross-sensor calendar workflow. |
| [GWIS applications](https://gwis.jrc.ec.europa.eu/applications) | Fire-season trends, historical seasonality, MODIS and VIIRS anomaly counts, combined NRT products | Its public description presents sensor counts separately and seasonality mainly from burned-area/fire-event products. The proposed project must demonstrate calibrated comparability and uncertainty, not merely combine detections. |
| [GROW](https://github.com/Florianopolis-NASA-Space-Apps/wildfires_chat_dashboard) | Winning Space Apps fire map, historical context, weather, AI voice/tools | A generic map or assistant would duplicate it. Fire Season's contribution must be the measured sensor transition and evidence workflow. |
| [Amazon fire-count workflow](https://github.com/mirandadam/fires) | Historical MODIS and VIIRS counts, regional comparisons | It keeps the records as separate series and documents sampling caveats; it does not establish a validated common measurement scale. |
| [FireTracks](https://github.com/dominiktraxl/firetracks) | Daily 1 km MODIS fire-mask extraction and spatiotemporal events | MODIS-only scientific dataset rather than an evaluated MODIS-to-VIIRS decision calendar. |
| [MODIS-VIIRS-fires](https://github.com/meredithfranklin/MODIS-VIIRS-fires) | Processing, annual comparison, and clustering of both sensors | Research pipeline for persistent combustion sources; no equivalent decision product or challenge-specific validation was found. |
| [NASA MODIS/VIIRS harmonization research](https://modis.gsfc.nasa.gov/sci_team/meetings/202204/presentations/session1/justice.pdf) | The scientific problem itself, including product intercomparison and calibrated records | This means the project cannot claim to invent harmonization. It can translate the problem into an open, understandable, evaluated tool. |
| [FRP correction and fusion study](https://www.mdpi.com/2072-4292/18/10/1650) | Correction-based MODIS/VIIRS harmonization and fusion | Scientific method and results, rather than the proposed user workflow. Its methods are prior art to study and cite, not originality to claim. |

## Earlier Space Apps overlap

Previous Space Apps projects include alerting and citizen coordination (sat-ELITE, 2019), fire risk and spread tools (Spot That Fire V3.0 projects, 2020), VIIRS monitoring plus communities and biodiversity (Mayas, 2020), wildfire image analysis and prediction (The Inspirit, 2022), and GROW's global-winning AI wildfire console (2024). These projects make the following directions weak:

- another hotspot map;
- another generic risk score;
- a chatbot or voice assistant as the main innovation;
- weather overlays and alerts without new evidence;
- an unsupported claim that AI predicts fires.

No indexed prior Space Apps project found in this audit demonstrates the exact calibrated burning-calendar workflow requested by the 2026 challenge. Because the 2026 challenge explicitly asks teams to harmonize the record, other 2026 teams will converge on similar calendars. Differentiation must come from scientific validity, a sharp use case, and presentation.

## Competition verdict

### Present state

The concept is **promising but not top-10-ready**. The current package has a strong problem framing and architecture, but it has not yet decoded a paired historical raster sample, fitted a transfer, beaten a transparent baseline on held-out regions or years, or passed a user test. Without those results, judges could reasonably describe it as a polished proposal for another fire dashboard.

Provisional assessment against the most recently published Space Apps criteria:

| Criterion | Now | What would make it exceptional |
|---|---:|---|
| Impact | Strong | A real monitoring decision and a named user group; one locally relevant case study. |
| Creativity | Moderate | Make the sensor-change reveal and evidence receipt the central interaction. |
| Validity | Unproven | Paired-data experiment, baseline comparison, held-out evaluation, uncertainty, and honest abstention. |
| Relevance | Very strong | Stay strictly on a harmonized hotspot calendar; avoid feature sprawl. |
| Presentation | High potential | A 30-second visual before/after story with one surprising, defensible result. |

### Likely competition level

- **Local event shortlist or local top group:** realistic if the prototype works and the story is disciplined.
- **Global Nominee:** plausible with the validity gate, a polished demo, and clear local impact.
- **One of the 10 Global Winners:** possible in concept, but not a responsible prediction at this stage. The 2024 competition had 9,996 submitted projects and the 2025 competition had 11,511. A top-10 result requires evidence, execution, and communication at an unusually high level.

There is no standard NASA award tier called “regional top 10.” The official path is Local Event or Universal Event judging, Global Nominee, Global Finalist, and then 10 Global Winners. Local organizers may use their own shortlist or awards.

## Go/no-go standard

Continue with Fire Season only if the team can complete this gate before committing the full build:

1. Decode matching MODIS and compatible VIIRS daily fire-mask samples for one overlap region and period.
2. Use comparable products. Do not silently harmonize the VIIRS 375 m FIRMS detection feed against a MODIS 1 km daily mask as if their detection behavior were equivalent.
3. Define an observation-aware target and a simple baseline.
4. Fit the calibration on one subset and evaluate on held-out time or geography.
5. Show that the adjusted series reduces sensor discontinuity without erasing true events.
6. Publish uncertainty and abstain where coverage or transfer is inadequate.
7. Test the calendar with at least three people in a credible user role and record what decision it changes.

If the transfer does not beat the baseline or cannot be explained, do not market it as harmonized. Show the two native sensor calendars and state that the attempted transfer failed. Scientific honesty will score better than a fabricated seamless record.

## Positioning that survives the prior-art test

**Fire Season is an evidence-first burning calendar that measures and explains the MODIS-to-VIIRS sensor transition, so a land or emergency analyst can tell whether apparent change reflects burning or observation.**

The winning demo should show one region where raw counts jump when the sensor changes, the evaluated calendar changes the interpretation, and the user can open the receipt to see sensors, coverage, method, uncertainty, and validation. That is materially stronger than adding more layers or an agent.

## Sources reviewed

- [2026 challenge summary](https://www.spaceappschallenge.org/2026/challenges/harmonization-of-modis-and-viirs-hot-spots/)
- [NASA FIRMS](https://firms.modaps.eosdis.nasa.gov/)
- [NASA VIIRS active-fire product continuity description](https://viirsland.gsfc.nasa.gov/Products/NASA/FireESDR.html)
- [GWIS applications](https://gwis.jrc.ec.europa.eu/applications)
- [GWIS active-fire limitations](https://gwis.jrc.ec.europa.eu/about-gwis/technical-background/active-fire-detection)
- [2024 Space Apps winners announcement](https://www.nasa.gov/learning-resources/stem-engagement-at-nasa/nasa-international-space-apps-challenge-announces-2024-global-winners/)
- [2025 judging and submission guide](https://www.spaceappschallenge.org/resources/project-submission-guide/)
- [2025 awards process](https://www.spaceappschallenge.org/2025/awards/)
- [Space Apps results and metrics](https://www.spaceappschallenge.org/about/results-and-metrics/)
- [sat-ELITE, 2019](https://2019.spaceappschallenge.org/challenges/living-our-world/spot-fire-v20/teams/sat-elite/)
- [Mayas, 2020](https://covid19.spaceappschallenge.org/challenges/covid-challenges/quiet-planet/teams/mayas/)
- [The Inspirit, 2022](https://2022.spaceappschallenge.org/challenges/2022-challenges/earth-data-analysis-developers-wanted/teams/the-inspirit-1/)
- [GROW source](https://github.com/Florianopolis-NASA-Space-Apps/wildfires_chat_dashboard)
- [FireTracks](https://github.com/dominiktraxl/firetracks)
- [MODIS-VIIRS-fires](https://github.com/meredithfranklin/MODIS-VIIRS-fires)
- [FIRECAM](https://github.com/tianjialiu/FIRECAM)
- [Amazon historical fire comparison](https://github.com/mirandadam/fires)
- [NASA MODIS/VIIRS research presentation](https://modis.gsfc.nasa.gov/sci_team/meetings/202204/presentations/session1/justice.pdf)
- [NASA harmonized multi-sensor active-fire project summary](https://disasters.nasa.gov/sites/default/files/2022-03/NASA%20Disasters%202021%20Annual%20Summary.pdf)
- [FRP correction and fusion paper](https://www.mdpi.com/2072-4292/18/10/1650)

