# Fire Season offline raster sample

The browser shell renders native-only March 2023 records decoded from the stored MYD14A1 and VNP14A1 rasters. Its data bundle includes two candidate region windows, a QA-aware paired sample, raster-derived 10×10-cell reference blocks, a checksum receipt, and explicit limits. A blank calendar month means no sample was processed; it does not mean zero detections.

Rebuild the data bundle from the repository root:

```sh
venv/bin/python pipeline/build_research_bundle.py
```

Install the pinned HDF and projection packages first using `pipeline/requirements-science.lock`. The browser itself has no runtime API, LLM, remote font, or other network dependency.

The bundle is a research sample, not a harmonized time series. It keeps MODIS and VIIRS records separate; Comparable Activity, anomaly, uncertainty interval, and priority remain unavailable. The evidence investigator remains out of scope until a calibration passes temporal, geographic, overlap, and interval-coverage evaluation.
