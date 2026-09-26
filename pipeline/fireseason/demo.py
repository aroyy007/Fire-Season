"""Tiny explicit contract fixture used by unit tests; never used by publisher."""

from __future__ import annotations

from typing import Any

from .contract import validate_analysis_artifact, validate_evidence_receipt

ZERO_SHA = "0" * 64
GENERATED_AT = "2026-09-24T00:00:00Z"
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


def build_demo_release(region_key: str = "science") -> tuple[dict[str, Any], dict[str, Any]]:
    """Return a hand-sized, unmistakably test-only artifact for contract tests."""
    is_science = region_key == "science"
    region_id = "region_contract_fixture_r1" if is_science else "region_local_contract_fixture_r1"
    name = "Contract fixture region" if is_science else "Local contract fixture region"
    artifact_id = "art_contract_fixture_000000000001" if is_science else "art_local_contract_fixture_000000000002"
    records = [
        {
            "product_id": PRODUCTS[0]["product_id"],
            "observation_status": "available",
            "detected_cell_days": 12,
            "valid_cell_days": 800,
            "eligible_land_cell_days": 1000,
            "support_fraction": 0.8,
            "rate_per_1000": 15.0,
        },
        {
            "product_id": PRODUCTS[1]["product_id"],
            "observation_status": "available",
            "detected_cell_days": 14,
            "valid_cell_days": 700,
            "eligible_land_cell_days": 900,
            "support_fraction": round(700 / 900, 6),
            "rate_per_1000": 20.0,
        },
    ]
    unavailable = {
        "status": "calibration_not_released",
        "estimate_per_1000": None,
        "lower_90": None,
        "upper_90": None,
        "interval_method": None,
        "calibration_id": None,
        "reason": "Contract fixture only; no scientific comparison is computed.",
    }
    limitations = ["contract_fixture_not_scientific_result", "No NASA raster values are represented by this test fixture."]
    artifact = {
        "schema_version": "1.0.0",
        "artifact_id": artifact_id,
        "release_status": "native_only",
        "generated_at": GENERATED_AT,
        "region": {
            "region_id": region_id,
            "name": name,
            "revision": 1,
            "role": "science_pilot" if is_science else "local_impact_case",
            "geometry_ref": "region.geojson",
            "geometry_sha256": ZERO_SHA,
            "bounds_wsen": [-97.0, 40.0, -96.0, 41.0],
        },
        "grid_version": "fixture-only",
        "period": {"start_date": "2023-03-01", "end_date": "2023-03-31"},
        "metric": {
            "metric_id": "detected_active_land_cell_days_per_1000_valid_land_cell_days",
            "label": "Detected activity rate",
            "unit": "detected active land-cell-days per 1,000 valid observed land-cell-days",
            "scale": 1000,
            "minimum": 0,
            "maximum": 1000,
            "definition": "1,000 × detected active land-cell-days ÷ valid observed land-cell-days.",
        },
        "reference_product_id": PRODUCTS[0]["product_id"],
        "sources": [dict(product) for product in PRODUCTS],
        "quality_policy": {
            "version": "fixture-only",
            "minimum_monthly_support_fraction": 0.5,
            "low_confidence_fire_policy": "excluded",
        },
        "calibration": None,
        "months": [{
            "month": "2023-03",
            "native_records": records,
            "comparison": unavailable,
            "anomaly": {
                "status": "indeterminate",
                "baseline_start_year": None,
                "baseline_end_year": None,
                "usable_baseline_years": 0,
                "rank": None,
                "percentile": None,
                "difference_per_1000": None,
                "reason": "Test fixture has no historical baseline.",
            },
            "investigation_priority": {
                "status": "unavailable",
                "reason": "Test fixture has no declared priority rule.",
                "block_ids": [],
            },
        }],
        "receipt_ref": "evidence-receipt.json",
        "files": [{"path": "calendar.csv", "media_type": "text/csv", "size_bytes": 0, "sha256": ZERO_SHA}],
        "limitations": limitations,
    }
    receipt = {
        "schema_version": "1.0.0",
        "receipt_id": "rcpt_000000000001" if is_science else "rcpt_000000000002",
        "artifact_id": artifact_id,
        "published_at": GENERATED_AT,
        "region": {
            "region_id": region_id,
            "revision": 1,
            "name": name,
            "role": artifact["region"]["role"],
            "geometry_ref": "region.geojson",
            "geometry_sha256": ZERO_SHA,
            "bounds_wsen": list(artifact["region"]["bounds_wsen"]),
        },
        "analysis": {
            "start_date": "2023-03-01",
            "end_date": "2023-03-31",
            "metric_id": artifact["metric"]["metric_id"],
            "reference_product_id": PRODUCTS[0]["product_id"],
            "source_manifest_id": "src_contract_fixture",
            "source_manifest_sha256": ZERO_SHA,
            "grid_version": "fixture-only",
            "quality_policy_version": "fixture-only",
            "minimum_monthly_support_fraction": 0.5,
            "daily_coverage": {
                "expected_calendar_days": 31,
                "myd14a1_observed_days": 31,
                "vnp14a1_observed_days": 31,
                "complete": True,
            },
        },
        "sources": [
            {
                **dict(product),
                "provider_objects": [{
                    "provider_object_id": f"test-only-{product['product_id']}",
                    "source_url": product["source_url"],
                    "observed_start": "2023-03-01T00:00:00Z",
                    "observed_end": "2023-03-31T23:59:59Z",
                    "retrieved_at": GENERATED_AT,
                    "retrieval_timestamp_status": "recorded",
                    "provider_checksum": None,
                    "size_bytes": 0,
                    "sha256": ZERO_SHA,
                }],
            }
            for product in PRODUCTS
        ],
        "exclusions": [],
        "calibration": None,
        "environment": {
            "python_version": "test-only",
            "dependency_lock_sha256": ZERO_SHA,
            "pipeline_revision": "contract-fixture",
            "operating_system": "test-only",
        },
        "limitations": limitations,
        "files": [
            {"path": "analysis.json", "media_type": "application/json", "size_bytes": 0, "sha256": ZERO_SHA},
            *artifact["files"],
        ],
    }
    validate_analysis_artifact(artifact)
    validate_evidence_receipt(receipt)
    return artifact, receipt
