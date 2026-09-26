# Fire Season browser application

This static browser app displays the QA-filtered March 2023 NASA raster sample for two candidate study windows. The release preserves separate native Aqua MYD14A1 and Suomi-NPP VNP14A1 records, an Aqua reference-product 10×10-cell heatmap, an Evidence Receipt, and explicit limitations. A blank calendar month means no raster sample was processed; it does not mean zero detections.

Start it from the repository root:

```sh
python3 -m http.server 8000 --directory app
```

Open [http://localhost:8000](http://localhost:8000). The app does not need an API, database, LLM, or network connection after the static files are available.

Rebuild the data bundle from the repository root. Install the science dependencies first as shown in the [root README](../README.md):

```sh
venv/bin/python pipeline/build_research_bundle.py
```

Install the pinned HDF and projection packages first using `pipeline/requirements-science.lock`. The browser itself has no runtime API, LLM, remote font, or other network dependency.

The bundle is a research sample, not a harmonized time series. It keeps MODIS and VIIRS records separate; Comparable Activity, anomaly, uncertainty interval, and priority remain unavailable. The candidate region boundaries are not frozen. The evidence investigator remains out of scope until a calibration passes temporal, geographic, overlap, and interval-coverage evaluation.

For exact UI behavior, see [implemented features](../docs/12-CORE-FEATURES.md). For the data and screen flow, see [as-built architecture](../docs/13-ARCHITECTURE-AND-DATA-FLOW.md).
