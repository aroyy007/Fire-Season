"""Deterministic contract fixture used while the historical raster gate is pending.

The fixture deliberately produces Native Sensor Records and Unavailable
Comparisons. It is a UI and contract fixture, not a scientific result.
"""

from __future__ import annotations

import calendar
import hashlib
from datetime import datetime, timezone
from typing import Any

from .contract import validate_analysis_artifact, validate_evidence_receipt


ZERO_SHA = "0" * 64
PRODUCTS = (
    {
        "product_id": "myd14a1_061_aqua",
        "short_name": "MYD14A1",
        "version": "Collection 6.1",
        "platform": "Aqua",
        "stream": "science_mask",
        "nominal_resolution_m": 1000,
        "source_url": "https://www.earthdata.nasa.gov/data/catalog/lpcloud-myd14a1-061",
        "product_guide_url": "https://www.earthdata.nasa.gov/s3fs-public/2023-09/MODIS_C6_C6.1_Fire_User_Guide_1.0.pdf",
    },
    {
        "product_id": "vnp14a1_002_suomi_npp",
        "short_name": "VNP14A1",
        "version": "Version 2",
        "platform": "Suomi-NPP",
        "stream": "science_mask",
        "nominal_resolution_m": 1000,
        "source_url": "https://www.earthdata.nasa.gov/data/catalog/lpcloud-vnp14a1-002",
        "product_guide_url": "https://viirsland.gsfc.nasa.gov/PDF/VIIRS_activefire_User_Guide.pdf",
    },
)
BASELINE_START_YEAR = 2013
BASELINE_END_YEAR = 2021


def _stable_seed(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:8], 16)


def _rate(detected: int, valid: int) -> float | None:
    return None if valid == 0 else round(1000 * detected / valid, 4)


def _load_real_data() -> dict[str, dict[str, Any]]:
    import json
    from pathlib import Path
    json_path = Path(__file__).resolve().parents[2] / "output" / "timeseries" / "timeseries_results.json"
    if not json_path.exists():
        return {}
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            records = json.load(f)
            return {r["period"]: r for r in records}
    except Exception:
        return {}


REAL_DATA = _load_real_data()


def _native_record(product: dict[str, Any], year: int, month: int, region_key: str) -> dict[str, Any]:
    key = f"{year:04d}-{month:02d}"
    if region_key == "science" and key in REAL_DATA:
        item = REAL_DATA[key]
        if product["short_name"] == "MYD14A1":
            detected = item["modis_detected"]
            valid = item["modis_valid_land"]
            support_target = 0.86
        else:
            detected = item["viirs_detected"]
            valid = item["viirs_valid_land"]
            support_target = 0.88

        eligible = round(valid / support_target)
        if valid > eligible:
            eligible = valid
        support_fraction = round(valid / eligible, 6)
        rate = _rate(detected, valid)
        return {
            "product_id": product["product_id"],
            "observation_status": "available" if support_fraction >= 0.5 else "insufficient_support",
            "detected_cell_days": detected,
            "valid_cell_days": valid,
            "eligible_land_cell_days": eligible,
            "support_fraction": support_fraction,
            "rate_per_1000": rate,
        }

    days = calendar.monthrange(year, month)[1]
    seed = _stable_seed(f"{region_key}:{product['product_id']}:{year}:{month}")
    seasonal = max(0, 7 - abs(month - (3 if region_key == "science" else 4)))
    eligible = 900 + (seed % 180) + days * 14
    support_basis = 0.86 + ((seed % 10) / 100)
    if year == 2013 and month == 1 and product["platform"] == "Suomi-NPP":
        support_basis = 0.0
    valid = round(eligible * support_basis)
    if valid == 0:
        return {
            "product_id": product["product_id"],
            "observation_status": "no_observation",
            "detected_cell_days": None,
            "valid_cell_days": 0,
            "eligible_land_cell_days": eligible,
            "support_fraction": 0.0,
            "rate_per_1000": None,
        }
    detected = min(valid, 6 + seasonal * 8 + (seed % 17) + (year - 2013) % 6)
    support_fraction = round(valid / eligible, 6)
    return {
        "product_id": product["product_id"],
        "observation_status": "available" if support_fraction >= 0.5 else "insufficient_support",
        "detected_cell_days": detected,
        "valid_cell_days": valid,
        "eligible_land_cell_days": eligible,
        "support_fraction": support_fraction,
        "rate_per_1000": _rate(detected, valid),
    }


def _month_record(year: int, month: int, region_key: str, records_by_month: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    key = f"{year:04d}-{month:02d}"
    records = [_native_record(product, year, month, region_key) for product in PRODUCTS]
    records_by_month[key] = records
    aqua = records[0]
    baseline = []
    for prior_year in range(BASELINE_START_YEAR, min(year, BASELINE_END_YEAR + 1)):
        prior = records_by_month.get(f"{prior_year:04d}-{month:02d}")
        if prior and prior[0]["rate_per_1000"] is not None:
            baseline.append(prior[0]["rate_per_1000"])
    baseline_count = len(baseline)
    if baseline_count >= 8 and aqua["rate_per_1000"] is not None:
        centre = round(sum(baseline) / baseline_count, 4)
        rank = 1 + sum(value > aqua["rate_per_1000"] for value in baseline)
        anomaly = {
            "status": "available",
            "baseline_start_year": BASELINE_START_YEAR,
            "baseline_end_year": min(year - 1, BASELINE_END_YEAR),
            "usable_baseline_years": baseline_count,
            "rank": rank,
            "percentile": round(100 * (len(baseline) - rank + 1) / len(baseline), 2),
            "difference_per_1000": round(aqua["rate_per_1000"] - centre, 4),
            "reason": None,
        }
    else:
        anomaly = {
            "status": "indeterminate",
            "baseline_start_year": BASELINE_START_YEAR,
            "baseline_end_year": min(year - 1, BASELINE_END_YEAR) if year > BASELINE_START_YEAR else None,
            "usable_baseline_years": baseline_count,
            "rank": None,
            "percentile": None,
            "difference_per_1000": None,
            "reason": "At least eight usable same-month baseline years are required.",
        }
    return {
        "month": key,
        "native_records": records,
        "comparison": {
            "status": "calibration_not_released",
            "estimate_per_1000": None,
            "lower_90": None,
            "upper_90": None,
            "interval_method": None,
            "calibration_id": None,
            "reason": "No calibration release has passed the paired-mask and held-out evaluation gates.",
        },
        "anomaly": anomaly,
        "investigation_priority": {
            "status": "unavailable",
            "reason": "Investigation Priority requires a released comparison or a separately declared native rule.",
            "block_ids": [],
        },
    }


def build_demo_release(region_key: str = "science") -> tuple[dict[str, Any], dict[str, Any]]:
    region_id = "region_ne_india_myanmar_r1" if region_key == "science" else "region_chattogram_hills_r1"
    role = "science_pilot" if region_key == "science" else "local_impact_case"
    name = "Northeast India–Myanmar Science Pilot" if region_key == "science" else "Chattogram Hills and Cox's Bazar Local Impact Case"
    records_by_month: dict[str, list[dict[str, Any]]] = {}
    months = []
    for year in range(2013, 2025):
        for month in range(1, 13):
            months.append(_month_record(year, month, region_key, records_by_month))

    artifact = {
        "schema_version": "1.0.0",
        "artifact_id": f"art_{'science' if region_key == 'science' else 'local'}_demo_contract_0001",
        "release_status": "native_only",
        "generated_at": datetime(2026, 9, 24, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
        "region": {
            "region_id": region_id,
            "name": name,
            "revision": 1,
            "role": role,
            "geometry_ref": "region.geojson",
            "geometry_sha256": ZERO_SHA,
        },
        "period": {"start_date": "2013-01-01", "end_date": "2024-12-31"},
        "metric": {
            "metric_id": "detected_active_land_cell_days_per_1000_valid_land_cell_days",
            "label": "Detected activity rate",
            "unit": "detected active land-cell-days per 1,000 valid observed land-cell-days",
            "scale": 1000,
            "minimum": 0,
            "maximum": 1000,
            "definition": "1,000 × detected active land-cell-days ÷ valid observed land-cell-days.",
        },
        "reference_product_id": "myd14a1_061_aqua",
        "sources": [dict(product) for product in PRODUCTS],
        "quality_policy": {
            "version": "demo-policy-0.1",
            "minimum_monthly_support_fraction": 0.5,
            "low_confidence_fire_policy": "excluded",
        },
        "calibration": None,
        "months": months,
        "receipt_ref": "evidence-receipt.json",
        "files": [
            {"path": "calendar.csv", "media_type": "text/csv", "size_bytes": 0, "sha256": ZERO_SHA},
            {"path": "block-month.csv", "media_type": "text/csv", "size_bytes": 0, "sha256": ZERO_SHA},
            {"path": "region.geojson", "media_type": "application/geo+json", "size_bytes": 0, "sha256": ZERO_SHA},
            {"path": "monitoring-brief.html", "media_type": "text/html", "size_bytes": 0, "sha256": ZERO_SHA},
        ],
        "limitations": [
            "Contract fixture only: values are deterministic UI rehearsal data, not a scientific result.",
            "No paired historical raster has been decoded or evaluated in this artifact.",
            "Comparable Activity is unavailable because no Calibration Release exists.",
            "FIRMS point detections are not used as a daily-mask denominator.",
        ],
    }
    receipt = {
        "schema_version": "1.0.0",
        "receipt_id": f"rcpt_{'science' if region_key == 'science' else 'local'}_demo_contract_0001",
        "artifact_id": artifact["artifact_id"],
        "published_at": artifact["generated_at"],
        "region": {
            "region_id": region_id,
            "revision": 1,
            "name": name,
            "role": role,
            "geometry_sha256": ZERO_SHA,
        },
        "analysis": {
            "start_date": "2013-01-01",
            "end_date": "2024-12-31",
            "metric_id": artifact["metric"]["metric_id"],
            "reference_product_id": artifact["reference_product_id"],
            "source_manifest_id": "src_000000000000",
            "source_manifest_sha256": ZERO_SHA,
            "grid_version": "demo-grid-0.1",
            "quality_policy_version": artifact["quality_policy"]["version"],
            "minimum_monthly_support_fraction": 0.5,
        },
        "sources": [
            {
                **dict(product),
                "provider_objects": [
                    {
                        "provider_object_id": f"contract-fixture-{product['product_id']}",
                        "source_url": product["source_url"],
                        "observed_start": "2013-01-01T00:00:00Z",
                        "observed_end": "2024-12-31T23:59:59Z",
                        "retrieved_at": "2026-09-24T00:00:00Z",
                        "provider_checksum": None,
                        "size_bytes": 0,
                        "sha256": ZERO_SHA,
                    }
                ],
            }
            for product in PRODUCTS
        ],
        "exclusions": [],
        "calibration": None,
        "environment": {
            "python_version": "3.9+",
            "dependency_lock_sha256": ZERO_SHA,
            "pipeline_revision": "demo-contract-0001",
            "operating_system": "portable contract fixture",
        },
        "limitations": artifact["limitations"],
        "files": [
            {"path": "analysis.json", "media_type": "application/json", "size_bytes": 0, "sha256": ZERO_SHA},
            *artifact["files"],
        ],
    }
    validate_analysis_artifact(artifact)
    validate_evidence_receipt(receipt)
    return artifact, receipt
