"""Create native-only Analysis Artifacts from decoded raster sample inputs."""

from __future__ import annotations

import hashlib
import json
import platform
from pathlib import Path
from typing import Any

from .sample import PRODUCTS, REGIONS, region_id

ZERO_SHA = "0" * 64
ROOT = Path(__file__).resolve().parents[2]


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def candidate_region_geojson(region_key: str) -> dict[str, Any]:
    region = REGIONS[region_key]
    west, south, east, north = region["bounds"]
    ring = [[west, south], [east, south], [east, north], [west, north], [west, south]]
    return {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {
                "region_id": region_id(region),
                "region_key": region_key,
                "revision": region["revision"],
                "boundary_status": "candidate_not_frozen",
                "bounds_wsen": list(region["bounds"]),
                "crs": "OGC:CRS84",
                "pixel_inclusion_rule": "native-grid pixel center inside polygon",
            },
            "geometry": {"type": "Polygon", "coordinates": [ring]},
        }],
    }


def build_research_release(
    region_key: str,
    sample: dict[str, Any],
    release_fingerprint: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    region = REGIONS[region_key]
    region_data = sample["regions"][region_key]
    science_sources = []
    receipt_sources = []
    for product_key in ("modis", "viirs"):
        product = PRODUCTS[product_key]
        record = {
            **product,
            "stream": "science_mask",
            "nominal_resolution_m": 1000,
        }
        science_sources.append(record)
        receipt_sources.append({
            **record,
            "provider_objects": sample["sources"][product_key],
        })

    month = sample["month"]
    artifact_id = f"art_{region_key}_aoi_sample_{month.replace('-', '')}_r{region['revision']}_{release_fingerprint[:12]}"
    receipt_id = f"rcpt_{release_fingerprint[:12]}"
    metric = {
        "metric_id": "detected_active_land_cell_days_per_1000_valid_land_cell_days",
        "label": "Detected activity rate",
        "unit": "detected active land-cell-days per 1,000 valid observed land-cell-days",
        "scale": 1000,
        "minimum": 0,
        "maximum": 1000,
        "definition": "1,000 × nominal/high-confidence active land-cell-days ÷ valid observed land-cell-days.",
    }
    comparison = {
        "status": "calibration_not_released",
        "estimate_per_1000": None,
        "lower_90": None,
        "upper_90": None,
        "interval_method": None,
        "calibration_id": None,
        "reason": "The current sample has one month and no independent temporal or geographic transfer evaluation.",
    }
    artifact = {
        "schema_version": "1.0.0",
        "artifact_id": artifact_id,
        "release_status": "native_only",
        "generated_at": sample["generated_at"],
        "region": {
            "region_id": region_id(region),
            "name": region["name"],
            "revision": region["revision"],
            "role": region["role"],
            "geometry_ref": "region.geojson",
            "geometry_sha256": ZERO_SHA,
            "bounds_wsen": list(region["bounds"]),
        },
        "grid_version": sample["grid_version"],
        "period": {"start_date": sample["start_date"], "end_date": sample["end_date"]},
        "metric": metric,
        "reference_product_id": PRODUCTS["modis"]["product_id"],
        "sources": science_sources,
        "quality_policy": {
            "version": "firemask-qa-land-highnominal-v1",
            "minimum_monthly_support_fraction": 0.5,
            "low_confidence_fire_policy": "excluded",
        },
        "calibration": None,
        "months": [{
            "month": month,
            "native_records": region_data["native_records"],
            "comparison": comparison,
            "anomaly": {
                "status": "indeterminate",
                "baseline_start_year": None,
                "baseline_end_year": None,
                "usable_baseline_years": 0,
                "rank": None,
                "percentile": None,
                "difference_per_1000": None,
                "reason": "A single-month sample cannot establish a seasonal baseline or activity anomaly.",
            },
            "investigation_priority": {
                "status": "unavailable",
                "reason": "No independently evaluated priority rule is declared.",
                "block_ids": [],
            },
        }],
        "receipt_ref": "evidence-receipt.json",
        "files": [],
        "limitations": [
            "Research sample only: native mask counts were decoded from the listed NASA granules for March 2023.",
            "The bounding box is a candidate analysis window inherited from the project; the team and local event have not frozen it.",
            "A daily cell is counted once per product composite. MYD14A1 is an eight-day file containing daily planes; VNP14A1 is daily.",
            "QA land cells define eligible support; clear land and nominal/high-confidence fire define valid support; nominal/high-confidence fire define detections.",
            "Low-confidence fire, water, cloud, unknown, and unprocessed cells are excluded from valid support and detections.",
            "The metric describes product detections, not independent fires, burned area, ignition probability, or fire danger.",
            "The two native sensor rates are not directly comparable; no transfer model, anomaly, interval, or priority score is released.",
            "Original local download timestamps were not retained; source file identity is established by filename, byte size, and SHA-256.",
        ],
    }

    lock_path = ROOT / "pipeline" / "requirements-science.lock"
    receipt = {
        "schema_version": "1.0.0",
        "receipt_id": receipt_id,
        "artifact_id": artifact_id,
        "published_at": sample["generated_at"],
        "region": {
            "region_id": region_id(region),
            "revision": region["revision"],
            "name": region["name"],
            "role": region["role"],
            "geometry_ref": "region.geojson",
            "geometry_sha256": ZERO_SHA,
            "bounds_wsen": list(region["bounds"]),
        },
        "analysis": {
            "start_date": sample["start_date"],
            "end_date": sample["end_date"],
            "metric_id": metric["metric_id"],
            "reference_product_id": PRODUCTS["modis"]["product_id"],
            "source_manifest_id": sample["source_manifest_id"],
            "source_manifest_sha256": sample["source_manifest_sha256"],
            "grid_version": sample["grid_version"],
            "quality_policy_version": artifact["quality_policy"]["version"],
            "minimum_monthly_support_fraction": 0.5,
            "daily_coverage": sample["daily_coverage"],
        },
        "sources": receipt_sources,
        "exclusions": region_data["exclusions"],
        "calibration": None,
        "environment": {
            "python_version": platform.python_version(),
            "dependency_lock_sha256": _sha256_file(lock_path) if lock_path.exists() else ZERO_SHA,
            "pipeline_revision": "science-sample-2023-03-v1",
            "operating_system": platform.system(),
        },
        "limitations": artifact["limitations"],
        "files": [],
    }
    return artifact, receipt
