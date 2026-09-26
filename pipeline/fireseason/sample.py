"""Build compact, reproducible March 2023 records from stored NASA granules."""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import numpy as np
from pyproj import Transformer

from .raster_analysis import (
    assert_complete_daily_coverage,
    assert_same_grid,
    block_count_arrays,
    classify_fire_mask,
    modis_grid_coordinates,
    points_in_polygon,
    projected_bbox_ring,
    qa_land_mask,
    read_modis_planes,
    read_viirs_plane,
    sinusoidal_bbox_mask,
    viirs_grid_coordinates,
    SINUSOIDAL_CRS,
)

ROOT = Path(__file__).resolve().parents[2]
MODIS_DIR = ROOT / "data" / "timeseries" / "modis"
VIIRS_DIR = ROOT / "data" / "timeseries" / "viirs"
SAMPLE_YEAR = 2023
SAMPLE_MONTH = 3
MONTH_START = date(SAMPLE_YEAR, SAMPLE_MONTH, 1)
MONTH_END = date(SAMPLE_YEAR, SAMPLE_MONTH + 1, 1)
SAMPLE_DATES = [MONTH_START + timedelta(days=i) for i in range((MONTH_END - MONTH_START).days)]
BLOCK_SIZE = 10
GRID_VERSION = "modis-viirs-sinusoidal-h26v06-926m-v1"

# Existing project windows are retained as candidates for proving the pipeline.
# The boundary must be frozen by the team/local event before a competition claim.
REGIONS = {
    "science": {
        "region_id_prefix": "region_ne_india_myanmar_candidate",
        "revision": 2,
        "name": "Northeast India–Myanmar candidate window",
        "role": "science_pilot",
        "bounds": (93.0, 23.0, 96.0, 26.5),
    },
    "local": {
        "region_id_prefix": "region_chattogram_hills_candidate",
        "revision": 2,
        "name": "Chattogram Hills and Cox’s Bazar candidate window",
        "role": "local_impact_case",
        "bounds": (91.4, 20.6, 92.7, 23.2),
    },
}


def region_id(region: dict[str, Any]) -> str:
    """Derive the stable identifier from its base name and explicit revision."""
    return f"{region['region_id_prefix']}_r{region['revision']}"

PRODUCTS = {
    "modis": {
        "product_id": "myd14a1_061_aqua",
        "short_name": "MYD14A1",
        "version": "Collection 6.1",
        "platform": "Aqua",
        "source_url": "https://www.earthdata.nasa.gov/data/catalog/lpcloud-myd14a1-061",
        "product_guide_url": "https://www.earthdata.nasa.gov/s3fs-public/2023-09/MODIS_C6_C6.1_Fire_User_Guide_1.0.pdf",
    },
    "viirs": {
        "product_id": "vnp14a1_002_suomi_npp",
        "short_name": "VNP14A1",
        "version": "Version 2",
        "platform": "Suomi-NPP",
        "source_url": "https://www.earthdata.nasa.gov/data/catalog/lpcloud-vnp14a1-002",
        "product_guide_url": "https://viirsland.gsfc.nasa.gov/PDF/VIIRS_activefire_User_Guide.pdf",
    },
}


def parse_granule_date(filename: str) -> date:
    match = re.search(r"A(\d{4})(\d{3})", filename)
    if not match:
        raise ValueError(f"Could not parse granule date from filename: {filename}")
    year, day_of_year = map(int, match.groups())
    return date(year, 1, 1) + timedelta(days=day_of_year - 1)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _month_arrays(shape: tuple[int, int]) -> dict[str, np.ndarray]:
    return {key: np.zeros(shape, dtype=np.uint16) for key in ("eligible", "valid", "detected")}


def _add_counts(
    totals: dict[str, np.ndarray],
    fire_mask: np.ndarray,
    qa: np.ndarray,
    aoi_mask: np.ndarray,
) -> None:
    eligible, valid, detected = classify_fire_mask(fire_mask, qa, aoi_mask)
    totals["eligible"] += eligible.astype(np.uint16)
    totals["valid"] += valid.astype(np.uint16)
    totals["detected"] += detected.astype(np.uint16)


def _count_exclusions(fire_mask: np.ndarray, qa: np.ndarray, aoi_mask: np.ndarray) -> Counter:
    """Count mutually exclusive AOI cell-days excluded from valid support."""
    qa_land = qa_land_mask(qa)
    in_aoi = np.asarray(aoi_mask, dtype=bool)
    counts = Counter()
    classes = {
        "low_confidence_excluded": in_aoi & qa_land & (fire_mask == 7),
        "cloud": in_aoi & qa_land & (fire_mask == 4),
        "unknown": in_aoi & qa_land & (fire_mask == 6),
        "unprocessed": in_aoi & qa_land & np.isin(fire_mask, (0, 1, 2)),
        "water_or_non_land": in_aoi & (~qa_land | (fire_mask == 3)),
    }
    for reason, mask in classes.items():
        counts[reason] += int(mask.sum())
    return counts


def _candidate_files(directory: Path, product: str) -> list[Path]:
    pattern = "MYD14A1.*.hdf" if product == "modis" else "VNP14A1.*.h5"
    candidates = []
    for path in sorted(directory.glob(pattern)):
        start = parse_granule_date(path.name)
        duration = 8 if product == "modis" else 1
        if start < MONTH_END and start + timedelta(days=duration) > MONTH_START:
            candidates.append(path)
    return candidates


def _decode_modis_month(files: list[Path], aoi_masks: dict[str, np.ndarray]) -> tuple[dict[str, dict[str, np.ndarray]], list[Path], dict[str, Counter]]:
    if not files:
        raise ValueError("No MYD14A1 granules cover the selected month")
    first_mask, _ = read_modis_planes(files[0])
    shape = tuple(first_mask.shape[-2:])
    totals = {key: _month_arrays(shape) for key in aoi_masks}
    exclusions = {key: Counter() for key in aoi_masks}
    seen_days: list[date] = []
    used_files: list[Path] = []
    for path in files:
        fire, qa = read_modis_planes(path)
        planes = fire.shape[0] if fire.ndim == 3 else 1
        if qa.shape != fire.shape:
            raise ValueError(f"MYD14A1 FireMask/QA dimensions differ in {path.name}")
        start = parse_granule_date(path.name)
        used = False
        for index in range(planes):
            observed = start + timedelta(days=index)
            if not MONTH_START <= observed < MONTH_END:
                continue
            seen_days.append(observed)
            used = True
            fire_plane = fire[index] if fire.ndim == 3 else fire
            qa_plane = qa[index] if qa.ndim == 3 else qa
            for region_key, mask in aoi_masks.items():
                _add_counts(totals[region_key], fire_plane, qa_plane, mask)
                exclusions[region_key].update(_count_exclusions(fire_plane, qa_plane, mask))
        if used:
            used_files.append(path)
    assert_complete_daily_coverage(SAMPLE_DATES, seen_days, "MYD14A1")
    return totals, used_files, exclusions


def _decode_viirs_month(files: list[Path], aoi_masks: dict[str, np.ndarray]) -> tuple[dict[str, dict[str, np.ndarray]], list[Path], dict[str, Counter]]:
    totals: dict[str, dict[str, np.ndarray]] | None = None
    exclusions = {key: Counter() for key in aoi_masks}
    seen_days: list[date] = []
    used_files: list[Path] = []
    reference_x = reference_y = None
    for path in files:
        observed = parse_granule_date(path.name)
        if not MONTH_START <= observed < MONTH_END:
            continue
        fire, qa = read_viirs_plane(path)
        if qa.shape != fire.shape:
            raise ValueError(f"VNP14A1 FireMask/QA dimensions differ in {path.name}")
        x_coords, y_coords = viirs_grid_coordinates(path)
        if totals is None:
            totals = {key: _month_arrays(tuple(fire.shape)) for key in aoi_masks}
            reference_x, reference_y = x_coords, y_coords
        else:
            assert_same_grid(reference_x, reference_y, x_coords, y_coords)
        seen_days.append(observed)
        used_files.append(path)
        for region_key, mask in aoi_masks.items():
            _add_counts(totals[region_key], fire, qa, mask)
            exclusions[region_key].update(_count_exclusions(fire, qa, mask))
    assert_complete_daily_coverage(SAMPLE_DATES, seen_days, "VNP14A1")
    assert totals is not None
    return totals, used_files, exclusions


def _manifest_object(path: Path, product_key: str) -> dict[str, Any]:
    product = PRODUCTS[product_key]
    granule_start = parse_granule_date(path.name)
    duration = 8 if product_key == "modis" else 1
    granule_end = granule_start + timedelta(days=duration - 1)
    doy = f"{granule_start.timetuple().tm_yday:03d}"
    archive_collection = "61" if product_key == "modis" else "5200"
    archive_url = (
        f"https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/{archive_collection}/"
        f"{product['short_name']}/{granule_start.year}/{doy}/{path.name}"
    )
    return {
        "provider_object_id": path.name,
        "source_url": archive_url,
        "observed_start": f"{granule_start.isoformat()}T00:00:00Z",
        "observed_end": f"{granule_end.isoformat()}T23:59:59Z",
        "retrieved_at": None,
        "retrieval_timestamp_status": "not_recorded_for_local_copy",
        "provider_checksum": None,
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def _block_rows(
    region: dict[str, Any],
    region_key: str,
    counts: dict[str, np.ndarray],
    aoi_mask: np.ndarray,
    x_coords: np.ndarray,
    y_coords: np.ndarray,
) -> list[dict[str, Any]]:
    block_counts = block_count_arrays(
        counts["eligible"], counts["valid"], counts["detected"], BLOCK_SIZE
    )
    aoi_cells = block_count_arrays(
        aoi_mask.astype(np.uint8), aoi_mask.astype(np.uint8), aoi_mask.astype(np.uint8), BLOCK_SIZE
    )["eligible"]
    rows, cols = block_counts["eligible"].shape
    x_step = float(np.median(np.diff(x_coords)))
    y_step = float(np.median(np.diff(y_coords)))
    transformer = Transformer.from_crs(SINUSOIDAL_CRS, "EPSG:4326", always_xy=True)
    result = []
    for block_row in range(rows):
        for block_col in range(cols):
            if int(aoi_cells[block_row, block_col]) == 0:
                continue
            eligible = int(block_counts["eligible"][block_row, block_col])
            valid = int(block_counts["valid"][block_row, block_col])
            detected = int(block_counts["detected"][block_row, block_col])
            if eligible == 0:
                continue
            support = round(valid / eligible, 6)
            rate = round(1000 * detected / valid, 4) if valid else None
            center_x = float(x_coords[block_col * BLOCK_SIZE:block_col * BLOCK_SIZE + BLOCK_SIZE].mean())
            center_y = float(y_coords[block_row * BLOCK_SIZE:block_row * BLOCK_SIZE + BLOCK_SIZE].mean())
            longitude, latitude = transformer.transform(center_x, center_y)
            result.append({
                "artifact_id": "",
                "region_id": region_id(region),
                "block_id": f"h26v06_r{block_row:03d}_c{block_col:03d}",
                "block_row": block_row,
                "block_col": block_col,
                "longitude": round(float(longitude), 5),
                "latitude": round(float(latitude), 5),
                "month": f"{SAMPLE_YEAR:04d}-{SAMPLE_MONTH:02d}",
                "product_id": PRODUCTS["modis"]["product_id"],
                "eligible_land_cell_days": eligible,
                "valid_cell_days": valid,
                "detected_cell_days": detected,
                "native_rate_per_1000": rate,
                "support_fraction": support,
                "observation_status": "available" if support >= 0.5 and valid > 0 else "insufficient_support",
                "comparison_status": "calibration_not_released",
                "investigation_priority": "unavailable",
            })
    return result


def build_march_2023_sample() -> dict[str, Any]:
    """Decode the checked-in paired sample and return compact artifact inputs."""
    modis_files = _candidate_files(MODIS_DIR, "modis")
    viirs_files = _candidate_files(VIIRS_DIR, "viirs")
    if not modis_files or not viirs_files:
        raise FileNotFoundError("March 2023 MYD14A1 and VNP14A1 granules must be present locally")

    modis_fire, _ = read_modis_planes(modis_files[0])
    shape = tuple(modis_fire.shape[-2:])
    x_coords, y_coords = modis_grid_coordinates(modis_files[0], shape)
    viirs_x, viirs_y = viirs_grid_coordinates(next(path for path in viirs_files if parse_granule_date(path.name).month == 3))
    assert_same_grid(x_coords, y_coords, viirs_x, viirs_y)

    aoi_masks = {
        key: sinusoidal_bbox_mask(region["bounds"], x_coords, y_coords)
        for key, region in REGIONS.items()
    }
    if any(not mask.any() for mask in aoi_masks.values()):
        raise ValueError("A candidate analysis window falls outside the paired tile grid")

    modis_counts, used_modis, modis_exclusions = _decode_modis_month(modis_files, aoi_masks)
    viirs_counts, used_viirs, viirs_exclusions = _decode_viirs_month(viirs_files, aoi_masks)

    regions: dict[str, Any] = {}
    for key, region in REGIONS.items():
        native_records = []
        for product_key, counts in (("modis", modis_counts[key]), ("viirs", viirs_counts[key])):
            eligible = int(counts["eligible"].sum())
            valid = int(counts["valid"].sum())
            detected = int(counts["detected"].sum())
            support = round(valid / eligible, 6) if eligible else 0.0
            native_records.append({
                "product_id": PRODUCTS[product_key]["product_id"],
                "observation_status": "available" if support >= 0.5 and valid > 0 else "insufficient_support",
                "detected_cell_days": detected,
                "valid_cell_days": valid,
                "eligible_land_cell_days": eligible,
                "support_fraction": support,
                "rate_per_1000": round(1000 * detected / valid, 4) if valid else None,
            })
        regions[key] = {
            "native_records": native_records,
            "blocks": _block_rows(region, key, modis_counts[key], aoi_masks[key], x_coords, y_coords),
            "aoi_bounds": list(region["bounds"]),
            "exclusions": [
                {"product_id": product_id, "reason": reason, "cell_days": count}
                for product_id, counts in (
                    (PRODUCTS["modis"]["product_id"], modis_exclusions[key]),
                    (PRODUCTS["viirs"]["product_id"], viirs_exclusions[key]),
                )
                for reason, count in sorted(counts.items())
                if count > 0
            ],
        }

    used_files = {
        "modis": [_manifest_object(path, "modis") for path in used_modis],
        "viirs": [_manifest_object(path, "viirs") for path in used_viirs],
    }
    canonical = "\n".join(
        f"{product_key}\t{obj['provider_object_id']}\t{obj['sha256']}"
        for product_key in ("modis", "viirs")
        for obj in used_files[product_key]
    ).encode("utf-8")
    return {
        "month": f"{SAMPLE_YEAR:04d}-{SAMPLE_MONTH:02d}",
        "start_date": MONTH_START.isoformat(),
        "end_date": (MONTH_END - timedelta(days=1)).isoformat(),
        "expected_days": len(SAMPLE_DATES),
        "daily_coverage": {
            "expected_calendar_days": len(SAMPLE_DATES),
            "myd14a1_observed_days": len(SAMPLE_DATES),
            "vnp14a1_observed_days": len(SAMPLE_DATES),
            "complete": True,
        },
        "grid_version": GRID_VERSION,
        "block_size_native_pixels": BLOCK_SIZE,
        "regions": regions,
        "sources": used_files,
        "source_manifest_id": "src_" + hashlib.sha256(canonical).hexdigest()[:12],
        "source_manifest_sha256": hashlib.sha256(canonical).hexdigest(),
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
