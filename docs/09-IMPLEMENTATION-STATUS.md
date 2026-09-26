# Implementation status

The repository now builds a real, narrow raster-analysis sample. It does not claim a validated sensor harmonization result.

## Executable sample

- `pipeline/fireseason/raster_analysis.py` decodes the MODIS and VIIRS QA land bits, applies the declared confidence policy, projects candidate region windows into the shared h26v06 sinusoidal grid, and groups reference-product pixels into 10×10 native-cell blocks.
- `pipeline/fireseason/sample.py` verifies all 31 March 2023 dates for both sensors, rejects duplicate or missing days and misaligned grids, then aggregates both candidate windows.
- `pipeline/fireseason/science_release.py` publishes native-only artifacts and an Evidence Receipt with the source granule names, byte sizes, and SHA-256 hashes. Original local download timestamps were not retained and are recorded as unknown.
- `pipeline/build_research_bundle.py` regenerates the static offline bundle from the stored HDF4/HDF5 granules. Release IDs bind source hashes, region revision and geometry, code/schema hashes, the dependency lock, and runtime. Identical rebuilds reuse a checked immutable directory; changed region geometry within the same revision fails closed.
- `pipeline/fireseason/calibrator.py` can report only exploratory monthly-ratio diagnostics. It cannot issue a Calibration Release. The app publishes no Comparable Activity estimate, anomaly, uncertainty interval, or priority score.
- The two bounding boxes are candidate analysis windows carried over from prior project files. They remain unfrozen and must be confirmed by the team and local event before they are described as final regions. After a boundary decision, update its bounds and increment `revision` in `pipeline/fireseason/sample.py`; the new artifact uses a new path and leaves previous receipts intact.

The observed March 2023 sample includes 5 MYD14A1 eight-day granules and 31 VNP14A1 daily granules. The QA policy counts QA-land pixels as eligible; clear non-fire land and nominal/high-confidence fire as valid; nominal/high-confidence fire as detections. Low confidence, water, cloud, unknown, and unprocessed cells do not enter valid support or detections. See NASA’s [MODIS C6/C6.1 Fire User Guide](https://www.earthdata.nasa.gov/s3fs-public/2023-09/MODIS_C6_C6.1_Fire_User_Guide_1.0.pdf) and [VIIRS Active Fire User Guide](https://viirsland.gsfc.nasa.gov/PDF/VIIRS_activefire_User_Guide.pdf) for the product FireMask and QA meanings.

## Rebuild and verify

The static browser has no runtime network dependency. The analysis builder needs the pinned HDF/geospatial Python packages:

```sh
python3 -m venv venv
venv/bin/python -m pip install -r pipeline/requirements-science.lock
venv/bin/python pipeline/build_research_bundle.py
venv/bin/python -m unittest discover -s pipeline/tests -v
node --check app/app.js
python3 scripts/check_package.py
```

The source rasters are already stored under `data/timeseries/`; rebuilding does not require an Earthdata login or another download. The local retrieval timestamps are unknown, and the publisher says so in each receipt.

## Remaining science work

The real sample proves file decoding, QA interpretation, spatial clipping, complete-month coverage, grid alignment, artifact validation, and raster-derived block output for one month. It does not prove that a MODIS-to-VIIRS transfer generalizes. The candidate boundaries remain unfrozen; the study has only one sample month; there is no independent geographic transfer test, multi-year held-out evaluation, reference-data assessment, calibrated interval, or field-impact evaluation. Keep native sensor records separate and the comparison unavailable until those gates are run and pass.

The app’s sparse calendar intentionally leaves unprocessed months blank. The standalone legacy `build_timeseries.py` output is a full-tile exploratory inventory, not an AOI-clipped science artifact and not a source for the browser bundle or model release.
