# NASA Space Apps: verified winners, prior art, and competition constraints

Research date: 18 September 2026. Scope: official 2023–2025 global winners; relevant creator repositories; rules discoverable for 2026. This is a research module for challenge selection, not a prediction of winning odds.

## What changes the product decision

Agricultural decision support and environmental interfaces have already won. In 2024, Waterwise won Best Use of Data, 2plant | ! 2plant won Galactic Impact, and G.R.O.W. won Local Impact. A new crop map, irrigation dashboard, or conversational wildfire map therefore needs a specific improvement over existing work. These identities and award categories are confirmed by NASA, rather than inferred from a team describing itself as a finalist. [2024 NASA announcement](https://www.nasa.gov/learning-resources/stem-engagement-at-nasa/nasa-international-space-apps-challenge-announces-2024-global-winners/)

**Recommended differentiation test (our inference):** name one user, one consequential decision, one observable input, one reproducible calculation, and one evidence-backed output. Then demonstrate why that decision is better supported than by the nearest winner. For a smallholder application, potential differences include cooperative resource allocation, explicit satellite-resolution limits, field observations that can overturn the model, and a retrospective test on a named season. These are proposed product directions, not established gaps across the entire market.

Do not present an LLM, agent workflow, or number of integrated datasets as the innovation itself. GROW's current public implementation already documents OpenAI Realtime, tool calls, satellite data, map navigation, weather context, and cached queries. A voice assistant over a map would be weak differentiation. [GROW repository](https://github.com/Florianopolis-NASA-Space-Apps/wildfires_chat_dashboard)

## Relevant winning approaches

| Verified winner | What is substantiated | Implication for a new project |
|---|---|---|
| 2024 GaamaRamma — Waterwise; Best Use of Data | Farmer water management | Avoid treating generic agricultural water advice as new. |
| 2024 NVS-knot — 2plant \| ! 2plant; Galactic Impact | Planting risk from soil moisture and evapotranspiration | A planting recommendation needs a differentiated workflow or validation. |
| 2024 Team I.O. — G.R.O.W.; Local Impact | Accessible environmental GIS | A map/chat interface alone is insufficient novelty. |

Source for award identities and descriptions: [NASA's 2024 winner announcement](https://www.nasa.gov/learning-resources/stem-engagement-at-nasa/nasa-international-space-apps-challenge-announces-2024-global-winners/).

The creators of 2Plant describe a field map with charts, moisture information, forecasts, and a final recommendation about planting. Their own account identifies a team containing software development, design, QA, and remote-sensing expertise. This is stronger evidence for combining domain knowledge with implementation than for choosing a fashionable ML architecture. The creator article labels a section “2025,” but NASA attributes the award to the **2024 competition**, announced in January 2025; retain the competition year in comparisons. The creator article is first-party product description, not an independent validation of crop outcomes. [VITech account](https://vitechteam.com/blog/how-vitech-s-agtech-innovation-won-the-nasa-space-apps-challenge)

| Verified 2025 winner | Relevant approach | Product lesson, inferred |
|---|---|---|
| Twisters — SkySense; Best Use of Technology | Weather risk and activity windows | Turn data into a bounded decision. |
| QUEÑARIS; Local Impact | Queñua restoration for Arequipa water security | Tie a specific ecosystem to a specific community need. |
| Zumorroda-X; Art & Technology | Agricultural learning through games | Education can be central when the challenge calls for it. |
| SpaceGenes+; Best Use of Science | Combined spaceflight stressors and molecular responses | A scientific question can organize the interface. |

Source: [NASA's 2025 winner announcement](https://www.nasa.gov/learning-resources/stem-engagement-at-nasa/nasa-announces-2025-international-space-apps-challenge-global-winners/). These descriptions substantiate project intentions, not validated prediction accuracy or measured social impact.

QUEÑARIS also has evidence of activity after the competition: Peru's forestry service reported work with Tecsup in February 2026 to identify suitable planting locations from moisture, soil, slope, and other inputs. This supports the value of an implementable partner relationship; it does not establish survival improvement or causal water benefits. [SERFOR government report](https://www.gob.pe/institucion/serfor/noticias/1352647-arequipa-serfor-y-tepsup-impulsan-reforestacion-de-quenua-con-inteligencia-artificial-como-herramienta-tecnica)

For a Bangladesh team, there is a relevant precedent: **TeamVoyagers won 2023 Best Storytelling** with a water-cycle game. Storm Prophet won that year's Best Use of Data using LSTM-based geomagnetic-storm modeling. These show that educational communication and technical modeling have both been recognized, but do not prove that either approach is favored in 2026. [NASA's 2023 announcement](https://science.nasa.gov/directorates/smd/2023-nasa-international-space-apps-challenge-announces-10-global-winners/)

## What was actually checked in code and models

**GROW:** the current repository declares MIT licensing, React/TypeScript, Mapbox, FIRMS MODIS NRT, Open-Meteo, browser SQL persistence, and OpenAI Realtime tool calling. It identifies Team I.O. and links NASA's winner announcement, making the identity connection strong. The README is an implementation description; we did not run the app, independently benchmark it, or verify its exact submission-time commit. Its present content must not be described as a verbatim snapshot of the 2024 hackathon. Its inconsistent “finalist” terminology does not override NASA's confirmed Local Impact award. [Repository](https://github.com/Florianopolis-NASA-Space-Apps/wildfires_chat_dashboard)

**Storm Prophet:** the repository identifies the 2023 team and links the matching official team/challenge. It documents TensorFlow LSTM prediction of Dst from DSCOVR, StandardScaler preprocessing, anomaly processing, a visualization app, and an MIT license. The referenced training file is `src/ml/lstm_andrew_clean.py`, but a direct code-file fetch failed; architecture depth, exact hyperparameters, split methodology, accuracy, and checkpoint reproducibility remain unverified. [Repository](https://github.com/Wizard2007/storm-prophet)

**Other winner model claims:** NASA describes 42 QuakeHeroes as using a deep neural network and signal processing; this does not identify a reproducible architecture. Model names, training data partitions, evaluation results, and deployable checkpoints for Waterwise, 2Plant, SkySense, and QUEÑARIS were not verified in this bounded search. Do not invent them or label guessed GitHub matches as their official code. [2024 announcement](https://www.nasa.gov/learning-resources/stem-engagement-at-nasa/nasa-international-space-apps-challenge-announces-2024-global-winners/)

The unrelated `water-wise/WATERWISE` repository describes a MENA water-infrastructure initiative; its name alone does not establish a relationship to GaamaRamma. It is **excluded from verified winning repositories**. [Unmatched repository](https://github.com/water-wise/WATERWISE)

## Competition rules: current versus historical

The official homepage confirms **14–15 November 2026**. [Official homepage](https://www.spaceappschallenge.org/)

The **2026 Participant Terms and Conditions**, updated August 7, require an eligible submission to address official challenge statements. Original content must be freely available without restriction or under an OSI-compliant license; NASA specifies Apache 2.0 distribution if no eligible license is selected. Third-party material requires appropriate availability/licensing documentation. Every source must be credited, including open resources. The terms allow removal of awards for missing resource citations. These requirements make a license-and-provenance inventory part of the architecture, not optional paperwork. [2026 terms](https://www.spaceappschallenge.org/legal/)

The discoverable submission and formation guides are still labeled **2025**. Treat the following as preparation defaults pending 2026 confirmation: maximum six members; all members confirmed at the same event; a public project and demo; English submission; demo up to seven slides or 30 seconds; NASA data/resources for Global Award eligibility; judging across Impact, Creativity, Validity, Relevance, Presentation. The 2025 AI policy permits AI but requires disclosure, visible watermarks on generated images/video, and descriptive/metadata acknowledgment for audio, code, and data. Generated material may not modify/include NASA branding. These are historical guide requirements, not silently asserted 2026 rules. [Team formation guide](https://www.spaceappschallenge.org/resources/team-formation-guide/) · [Submission guide](https://www.spaceappschallenge.org/resources/project-submission-guide/)

**Pre-event work is unresolved for 2026.** A legacy 2022 FAQ asks teams to begin actual work when that hackathon starts; it cannot establish this year's exact boundary. Researching users, evaluating data availability, identifying teammates, and drafting an explicitly labeled preparation plan are sensible now. Before building a competition submission, obtain the current official rule on prebuilt code, derived models, and pre-event prototypes. This recommendation follows from uncertainty; it is not a claimed rule that forbids the present research. [Legacy FAQ](https://legacy.spaceappschallenge.org/resources/faq/)

## Recommended team and evidence strategy

Our recommendation is a five-person core: domain/data science, geospatial engineering, backend/model evaluation, product/frontend, and research/storytelling. Assign a secondary reviewer for every scientific claim. A sixth teammate is useful only if they add a concrete capability such as agronomy, hydrology, accessibility research, or high-quality scientific communication. Confirm the 2026 team limit before registration.

For challenge selection, favor the project with the strongest reachable domain partner and usable validation labels. Recruit an actual decision-maker early, prepare three task scenarios, define a baseline the product must beat, and agree which uncertainty requires human review. A polished demonstration should expose its input dataset, date, resolution, and calculation behind each recommendation. The judge should be able to inspect an answer rather than trust its wording.

Keep a dated research folder now. During the event, keep a separate implementation history, dataset manifest, model card, assumptions register, and AI assistance disclosure. Select one primary award fit but satisfy the full judging rubric; award categories are not separate scientific validity standards. None of these actions guarantees selection.

## Limits and source handling

Official award announcements are authoritative for winner status, not independent audits of a project's marketing claims. Project page detail links frequently returned 502/timeouts. Search snippets were used where official indexed text was accessible; those failures are recorded in `evidence.jsonl`. Repository readmes were inspected, but projects were not executed. This module does not claim an exhaustive scan of GitHub or all historical submissions. All 30 award/team identities are listed in `global-winners-2023-2025.csv`; focused interpretation above is deliberately narrower.

`sources.jsonl` contains stable source IDs and retrieval details. `evidence.jsonl` stores paraphrased evidence and limitations; `claims.jsonl` distinguishes directly supported facts from inferred recommendations. Independent corroboration is unavailable for most implementation claims, so they remain attributed rather than presented as proven outcomes.
