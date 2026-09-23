# Fire Season static demo

This directory is a zero-dependency browser shell for the Competition MVP contract fixture. Open `index.html` directly or serve the repository with any static server. The generated `data.js` bundle is offline-capable and intentionally contains contract-fixture values marked in the interface; it is not a scientific result.

Regenerate the bundle from the dependency-free Python pipeline with:

```sh
python3 pipeline/build_demo_artifact.py
```

The shell includes a seasonal pulse summary, responsive year/month list, selectable 10 km block heatmap, equivalent block table, evidence receipt, CSV/JSON exports, and a printable Monitoring Brief. These are all artifact-driven; there is no LLM or runtime API in the browser.

The first real-data implementation must replace the fixture with a decoded paired MODIS–VIIRS Analysis Artifact and retain the same public contract. A future Evidence Investigator may use a local model only to explain released fields; it must never calculate or invent scientific values.
