# LLM decision

Fire Season does not need a Hugging Face, Groq, or other hosted LLM API for the Competition MVP.

The core judging question is whether a MODIS–VIIRS comparison is scientifically defensible. Numeric values, anomaly flags, heatmaps, and release decisions must come from a versioned Analysis Artifact and reproducible pipeline. An LLM cannot improve those calculations and would add a network dependency, latency, cost/rate limits, privacy concerns, and an avoidable risk of unsupported wording during an offline judging flow.

If the calibration release succeeds, an optional **Evidence Investigator** can be added later. It should run locally with an open model or use a hosted provider only as a non-critical convenience. Its tools would be read-only: retrieve fields from the released artifact, explain a receipt, and link to source evidence. It must not fit a model, change a value, infer fire cause, issue a warning, or answer from data outside the receipt. Every answer needs a deterministic template fallback so the product remains complete with the model disabled.

The current UI therefore uses no AI chat surface. Its “intelligence” is visible in the evidence contract, abstention state, seasonal pulse, and block heatmap.
