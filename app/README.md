# Fire Season static demo

This directory is a zero-dependency browser shell for the Competition MVP contract fixture. Open `index.html` directly or serve the repository with any static server. The generated `data.js` bundle is offline-capable and intentionally contains contract-fixture values marked in the interface; it is not a scientific result.

Regenerate the bundle from the dependency-free Python pipeline with:

```sh
python3 pipeline/build_demo_artifact.py
```

The first real-data implementation must replace the fixture with a decoded paired MODIS–VIIRS Analysis Artifact and retain the same public contract.
