"""Behavioral checks for the public Analysis Artifact seam.

The full JSON Schema files are the machine-readable contract. These checks cover
the cross-field invariants that a JSON Schema cannot express portably and keep
the demo builder dependency-free.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Mapping


COMPARISON_STATUSES = {
    "available",
    "insufficient_observation_support",
    "insufficient_overlap",
    "insufficient_training_support",
    "out_of_domain",
    "incompatible_product",
    "calibration_not_released",
    "calibration_withdrawn",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _number(value: Any, field: str, *, minimum: float | None = None, maximum: float | None = None) -> None:
    _require(isinstance(value, (int, float)) and not isinstance(value, bool), f"{field} must be numeric")
    if minimum is not None:
        _require(value >= minimum, f"{field} must be >= {minimum}")
    if maximum is not None:
        _require(value <= maximum, f"{field} must be <= {maximum}")


def _integer(value: Any, field: str, *, minimum: int = 0) -> None:
    _require(isinstance(value, int) and not isinstance(value, bool), f"{field} must be an integer")
    _require(value >= minimum, f"{field} must be >= {minimum}")


def _date(value: str, field: str) -> None:
    try:
        date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an ISO date") from exc


def _datetime(value: str, field: str) -> None:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an ISO date-time") from exc


def _sha(value: str, field: str) -> None:
    _require(isinstance(value, str) and len(value) == 64, f"{field} must be a SHA-256 hex string")
    _require(all(char in "0123456789abcdef" for char in value), f"{field} must be lowercase hex")


def _file_list(files: Any, field: str) -> None:
    _require(isinstance(files, list) and files, f"{field} must contain files")
    paths = []
    for item in files:
        _require(isinstance(item, Mapping), f"{field} entries must be objects")
        path = item.get("path")
        _require(isinstance(path, str) and path and not path.startswith("/") and ".." not in path, f"{field} path is unsafe")
        _require(path not in paths, f"{field} contains duplicate path {path}")
        paths.append(path)
        _integer(item.get("size_bytes"), f"{field}.{path}.size_bytes")
        _sha(item.get("sha256"), f"{field}.{path}.sha256")


def _validate_source(source: Mapping[str, Any]) -> None:
    for key in ("product_id", "short_name", "version", "platform", "stream", "source_url", "product_guide_url"):
        _require(source.get(key), f"source.{key} is required")
    _require(source["stream"] in {"science_mask", "recent_context"}, "source.stream is invalid")
    _integer(source.get("nominal_resolution_m"), "source.nominal_resolution_m", minimum=1)


def _validate_native(record: Mapping[str, Any]) -> None:
    for key in ("product_id", "observation_status", "detected_cell_days", "valid_cell_days", "eligible_land_cell_days", "support_fraction", "rate_per_1000"):
        _require(key in record, f"native record is missing {key}")
    status = record["observation_status"]
    _require(status in {"available", "insufficient_support", "no_observation"}, "native observation status is invalid")
    _integer(record["eligible_land_cell_days"], "eligible_land_cell_days", minimum=1)
    _integer(record["valid_cell_days"], "valid_cell_days")
    _require(record["valid_cell_days"] <= record["eligible_land_cell_days"], "valid cells exceed eligible cells")
    _number(record["support_fraction"], "support_fraction", minimum=0, maximum=1)
    if status == "no_observation":
        _require(record["detected_cell_days"] is None, "no observation cannot have detections")
        _require(record["valid_cell_days"] == 0, "no observation must have zero valid cells")
        _require(record["rate_per_1000"] is None, "no observation cannot have a rate")
        return
    _integer(record["detected_cell_days"], "detected_cell_days")
    _require(record["detected_cell_days"] <= record["valid_cell_days"], "detected cells exceed valid cells")
    if record["valid_cell_days"] == 0:
        _require(record["rate_per_1000"] is None, "zero support cannot have a rate")
    else:
        _number(record["rate_per_1000"], "rate_per_1000", minimum=0, maximum=1000)
        expected = round(1000 * record["detected_cell_days"] / record["valid_cell_days"], 4)
        _require(record["rate_per_1000"] == expected, "native rate does not match counts")


def _validate_comparison(comparison: Mapping[str, Any]) -> None:
    status = comparison.get("status")
    _require(status in COMPARISON_STATUSES, "comparison status is invalid")
    numeric = ("estimate_per_1000", "lower_90", "upper_90", "interval_method", "calibration_id")
    if status == "available":
        for key in numeric:
            _require(comparison.get(key) is not None, f"available comparison needs {key}")
        _number(comparison["estimate_per_1000"], "estimate_per_1000", minimum=0, maximum=1000)
        _number(comparison["lower_90"], "lower_90", minimum=0, maximum=1000)
        _number(comparison["upper_90"], "upper_90", minimum=0, maximum=1000)
        _require(comparison["lower_90"] <= comparison["estimate_per_1000"] <= comparison["upper_90"], "comparison interval is invalid")
        _require(comparison.get("reason") is None, "available comparison cannot have a reason")
    else:
        for key in numeric:
            _require(comparison.get(key) is None, f"unavailable comparison cannot have {key}")
        _require(isinstance(comparison.get("reason"), str) and comparison["reason"], "unavailable comparison needs a reason")


def validate_analysis_artifact(artifact: Mapping[str, Any]) -> None:
    """Validate the analysis contract and its most important cross-field rules."""

    required = ("schema_version", "artifact_id", "release_status", "generated_at", "region", "period", "metric", "reference_product_id", "sources", "quality_policy", "calibration", "months", "receipt_ref", "files", "limitations")
    for key in required:
        _require(key in artifact, f"artifact is missing {key}")
    _require(artifact["schema_version"] == "1.0.0", "unsupported artifact schema")
    _require(artifact["artifact_id"].startswith("art_"), "invalid artifact ID")
    _require(artifact["release_status"] in {"released", "native_only"}, "invalid artifact release status")
    _datetime(artifact["generated_at"], "generated_at")
    region = artifact["region"]
    _require(region.get("region_id") and region.get("name") and region.get("revision", 0) >= 1, "region identity is incomplete")
    _require(region.get("role") in {"science_pilot", "local_impact_case", "transfer_test_region"}, "region role is invalid")
    _sha(region["geometry_sha256"], "region.geometry_sha256")
    _date(artifact["period"]["start_date"], "period.start_date")
    _date(artifact["period"]["end_date"], "period.end_date")
    _require(artifact["period"]["start_date"] <= artifact["period"]["end_date"], "period is reversed")
    _require(artifact["metric"]["metric_id"] == "detected_active_land_cell_days_per_1000_valid_land_cell_days", "unsupported metric")
    _require(artifact["reference_product_id"], "reference product is required")
    _require(isinstance(artifact["sources"], list) and len(artifact["sources"]) >= 2, "at least two sources are required")
    source_ids = set()
    for source in artifact["sources"]:
        _validate_source(source)
        _require(source["product_id"] not in source_ids, "duplicate source product")
        source_ids.add(source["product_id"])
    policy = artifact["quality_policy"]
    _require(policy.get("version") and policy.get("low_confidence_fire_policy") in {"excluded", "included"}, "quality policy is incomplete")
    _number(policy.get("minimum_monthly_support_fraction"), "minimum_monthly_support_fraction", minimum=0, maximum=1)
    _file_list(artifact["files"], "artifact.files")
    _require(isinstance(artifact["limitations"], list) and artifact["limitations"], "artifact needs limitations")
    _require(isinstance(artifact["months"], list) and artifact["months"], "artifact needs months")
    month_keys = []
    comparison_available = False
    for month in artifact["months"]:
        key = month.get("month")
        _require(isinstance(key, str) and len(key) == 7 and key[4] == "-", "month key is invalid")
        _require(key not in month_keys, "duplicate month")
        month_keys.append(key)
        records = month.get("native_records")
        _require(isinstance(records, list) and records, "month needs native records")
        for record in records:
            _require(record["product_id"] in source_ids, "native record refers to unknown product")
            _validate_native(record)
        _validate_comparison(month["comparison"])
        comparison_available = comparison_available or month["comparison"]["status"] == "available"
    if artifact["release_status"] == "native_only":
        _require(not comparison_available, "native-only artifact cannot contain available comparison")
        _require(artifact["calibration"] is None, "native-only artifact cannot reference calibration")
    else:
        _require(comparison_available and artifact["calibration"] is not None, "released artifact needs available comparison and calibration")
    _require(isinstance(artifact["receipt_ref"], str) and not artifact["receipt_ref"].startswith("/"), "receipt reference is unsafe")


def validate_evidence_receipt(receipt: Mapping[str, Any]) -> None:
    """Validate the receipt fields needed for reproducible review."""

    required = ("schema_version", "receipt_id", "artifact_id", "published_at", "region", "analysis", "sources", "exclusions", "calibration", "environment", "limitations", "files")
    for key in required:
        _require(key in receipt, f"receipt is missing {key}")
    _require(receipt["schema_version"] == "1.0.0", "unsupported receipt schema")
    _datetime(receipt["published_at"], "published_at")
    _sha(receipt["region"]["geometry_sha256"], "receipt.region.geometry_sha256")
    analysis = receipt["analysis"]
    _date(analysis["start_date"], "receipt.analysis.start_date")
    _date(analysis["end_date"], "receipt.analysis.end_date")
    _sha(analysis["source_manifest_sha256"], "source_manifest_sha256")
    _number(analysis["minimum_monthly_support_fraction"], "receipt support threshold", minimum=0, maximum=1)
    _require(isinstance(receipt["sources"], list) and len(receipt["sources"]) >= 2, "receipt needs source records")
    for source in receipt["sources"]:
        _validate_source({**source, "nominal_resolution_m": source.get("nominal_resolution_m", 1000)})
        _require(isinstance(source.get("provider_objects"), list) and source["provider_objects"], "receipt source needs provider objects")
        for obj in source["provider_objects"]:
            _sha(obj["sha256"], "provider object sha256")
            _integer(obj["size_bytes"], "provider object size")
            _datetime(obj["observed_start"], "provider object start")
            _datetime(obj["observed_end"], "provider object end")
            _datetime(obj["retrieved_at"], "provider object retrieval")
    env = receipt["environment"]
    _require(env.get("python_version") and env.get("pipeline_revision") and env.get("operating_system"), "environment is incomplete")
    _sha(env["dependency_lock_sha256"], "dependency lock sha256")
    _file_list(receipt["files"], "receipt.files")
    _require(isinstance(receipt["limitations"], list) and receipt["limitations"], "receipt needs limitations")
