"""Behavioral checks for the public Analysis Artifact seam.

The full JSON Schema files are the machine-readable contract. These checks cover
the cross-field invariants that a JSON Schema cannot express portably and keep
the demo builder dependency-free.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
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
RELEASE_GATES = {
    "training_and_holdout_support",
    "paired_support",
    "baseline_skill",
    "regional_bias",
    "peak_timing",
    "interval_coverage",
    "transfer_test",
    "declared_domain",
    "provenance_reproducibility",
}
ARTIFACT_ID_PATTERN = re.compile(r"^art_[a-z0-9][a-z0-9_-]*_[0-9a-f]{12}$")
RECEIPT_ID_PATTERN = re.compile(r"^rcpt_[0-9a-f]{12}$")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _number(value: Any, field: str, *, minimum: float | None = None, maximum: float | None = None) -> None:
    _require(isinstance(value, (int, float)) and not isinstance(value, bool), f"{field} must be numeric")
    _require(math.isfinite(value), f"{field} must be finite")
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


def _canonical_json_payload(value: Mapping[str, Any]) -> bytes:
    """Serialize JSON payloads exactly as the publisher does before hashing."""
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _validate_json_payload(payload: bytes, files: Any, path: Any, field: str) -> None:
    _require(isinstance(path, str) and path and not path.startswith("/") and ".." not in path, f"{field} reference is unsafe")
    entry = next((item for item in files if item["path"] == path), None)
    _require(entry is not None, f"{field} reference is not in the file manifest")
    _require(entry["media_type"] == "application/json", f"{field} payload must be JSON")
    expected_hash = hashlib.sha256(payload).hexdigest()
    _require(entry["size_bytes"] == len(payload), f"{field} payload size does not match its manifest entry")
    _require(entry["sha256"] == expected_hash, f"{field} checksum does not match its manifest entry")


def _validate_evaluation_payload(
    evaluation: Mapping[str, Any],
    files: Any,
    path: Any,
    field: str,
) -> None:
    _validate_json_payload(_canonical_json_payload(evaluation), files, path, field)


def _validate_calibration_domain(
    domain: Any,
    *,
    source: Mapping[str, Any],
    reference: Mapping[str, Any],
    quality_policy_version: str,
    grid_version: str,
    artifact_region_id: str,
    transfer_region_id: str,
    minimum_policy_support: float,
    field: str,
) -> tuple[float, tuple[float, float], tuple[float, float]]:
    """Validate domain declarations shared by artifact and receipt contracts."""
    _require(isinstance(domain, Mapping), f"{field} is required")
    _require(domain.get("source_product_version") == source["version"], f"{field} source version does not match")
    _require(domain.get("reference_product_version") == reference["version"], f"{field} reference version does not match")
    _require(domain.get("quality_policy_version") == quality_policy_version, f"{field} quality policy does not match")
    _require(domain.get("grid_version") == grid_version, f"{field} grid does not match")
    _require(transfer_region_id != artifact_region_id, "transfer test region must be separate from the artifact region")

    region_ids = domain.get("region_ids")
    _require(
        isinstance(region_ids, list)
        and all(isinstance(region_id, str) and region_id for region_id in region_ids)
        and len(region_ids) == len(set(region_ids)),
        f"{field} region_ids must be unique non-empty strings",
    )
    _require(artifact_region_id in region_ids, f"artifact region is outside {field}")
    _require(transfer_region_id in region_ids, f"transfer test region is outside {field}")

    minimum_support = domain.get("minimum_support_fraction")
    _number(minimum_support, f"{field}.minimum_support_fraction", minimum=minimum_policy_support, maximum=1)

    def validate_range(name: str) -> tuple[float, float]:
        value = domain.get(name)
        _require(isinstance(value, Mapping), f"{field}.{name} is required")
        lower, upper = value.get("minimum"), value.get("maximum")
        _number(lower, f"{field}.{name}.minimum", minimum=0, maximum=1000)
        _number(upper, f"{field}.{name}.maximum", minimum=0, maximum=1000)
        _require(lower <= upper, f"{field}.{name} is reversed")
        return lower, upper

    return (
        minimum_support,
        validate_range("source_activity_range_per_1000"),
        validate_range("comparable_activity_range_per_1000"),
    )


def _validate_bounds_wsen(bounds: Any, field: str) -> tuple[float, float, float, float]:
    _require(isinstance(bounds, list) and len(bounds) == 4, f"{field} must contain west, south, east, north")
    west, south, east, north = bounds
    _number(west, f"{field}[0]", minimum=-180, maximum=180)
    _number(south, f"{field}[1]", minimum=-90, maximum=90)
    _number(east, f"{field}[2]", minimum=-180, maximum=180)
    _number(north, f"{field}[3]", minimum=-90, maximum=90)
    _require(west < east and south < north, f"{field} is reversed or empty")
    return west, south, east, north


def _geojson_geometry_bounds(
    payload: bytes,
    *,
    expected_region_id: str,
    expected_bounds: tuple[float, float, float, float],
    field: str,
) -> tuple[float, float, float, float]:
    _require(isinstance(payload, bytes), f"{field} payload must be bytes")
    try:
        document = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{field} payload is not valid GeoJSON") from exc

    if isinstance(document, Mapping) and document.get("type") == "FeatureCollection":
        features = document.get("features")
    elif isinstance(document, Mapping) and document.get("type") == "Feature":
        features = [document]
    else:
        features = None
    _require(isinstance(features, list) and features, f"{field} must be a non-empty GeoJSON Feature or FeatureCollection")

    positions: list[tuple[float, ...]] = []

    def parse_position(value: Any, position_field: str) -> tuple[float, ...]:
        _require(
            isinstance(value, list)
            and len(value) >= 2
            and all(isinstance(coordinate, (int, float)) and not isinstance(coordinate, bool) for coordinate in value),
            f"{position_field} must be a GeoJSON coordinate position",
        )
        _number(value[0], f"{position_field}.longitude", minimum=-180, maximum=180)
        _number(value[1], f"{position_field}.latitude", minimum=-90, maximum=90)
        for index, coordinate in enumerate(value[2:], start=2):
            _number(coordinate, f"{position_field}[{index}]")
        return tuple(value)

    def parse_ring(value: Any, ring_field: str) -> list[tuple[float, ...]]:
        _require(isinstance(value, list) and len(value) >= 4, f"{ring_field} must be a closed linear ring with at least four positions")
        ring = [parse_position(position, f"{ring_field}[{index}]") for index, position in enumerate(value)]
        _require(ring[0] == ring[-1], f"{ring_field} must be closed")
        positions.extend(ring)
        return ring

    def parse_polygon(value: Any, polygon_field: str) -> None:
        _require(isinstance(value, list) and value, f"{polygon_field} must contain at least one linear ring")
        for ring_index, ring in enumerate(value):
            parse_ring(ring, f"{polygon_field}[{ring_index}]")

    for index, feature in enumerate(features):
        _require(isinstance(feature, Mapping) and feature.get("type") == "Feature", f"{field}.features[{index}] must be a GeoJSON Feature")
        properties = feature.get("properties")
        _require(isinstance(properties, Mapping), f"{field}.features[{index}].properties is required")
        _require(properties.get("region_id") == expected_region_id, f"{field} GeoJSON region ID does not match its declaration")
        declared_feature_bounds = _validate_bounds_wsen(properties.get("bounds_wsen"), f"{field}.features[{index}].bounds_wsen")
        _require(
            all(abs(actual - expected) <= 1e-9 for actual, expected in zip(declared_feature_bounds, expected_bounds)),
            f"{field} GeoJSON declared bounds do not match its release metadata",
        )
        geometry = feature.get("geometry")
        _require(isinstance(geometry, Mapping), f"{field}.features[{index}] must contain a Polygon or MultiPolygon")
        geometry_type = geometry.get("type")
        coordinates = geometry.get("coordinates")
        if geometry_type == "Polygon":
            parse_polygon(coordinates, f"{field}.features[{index}].geometry.coordinates")
        elif geometry_type == "MultiPolygon":
            _require(isinstance(coordinates, list) and coordinates, f"{field}.features[{index}] MultiPolygon must contain a polygon")
            for polygon_index, polygon in enumerate(coordinates):
                parse_polygon(polygon, f"{field}.features[{index}].geometry.coordinates[{polygon_index}]")
        else:
            _require(False, f"{field}.features[{index}] must contain a Polygon or MultiPolygon")

    _require(positions, f"{field} GeoJSON contains no coordinate positions")
    actual_bounds = (
        min(point[0] for point in positions),
        min(point[1] for point in positions),
        max(point[0] for point in positions),
        max(point[1] for point in positions),
    )
    _require(
        all(abs(actual - expected) <= 1e-9 for actual, expected in zip(actual_bounds, expected_bounds)),
        f"{field} GeoJSON coordinates do not match the declared bounds",
    )
    return actual_bounds


def _validate_region_geometry_binding(
    region: Mapping[str, Any],
    files: Any,
    field: str,
    geometry_payloads: Mapping[str, bytes],
) -> tuple[float, float, float, float]:
    geometry_ref = region.get("geometry_ref")
    _require(isinstance(geometry_ref, str) and geometry_ref, f"{field}.geometry_ref is required")
    _require(not geometry_ref.startswith("/") and ".." not in geometry_ref, f"{field}.geometry_ref is unsafe")
    geometry_file = next((item for item in files if item["path"] == geometry_ref), None)
    _require(geometry_file is not None, f"{field}.geometry_ref is not in the file manifest")
    _require(geometry_file["media_type"] == "application/geo+json", f"{field} geometry must be GeoJSON")
    _require(geometry_file["sha256"] == region["geometry_sha256"], f"{field} geometry checksum does not match its manifest entry")
    declared_bounds = _validate_bounds_wsen(region.get("bounds_wsen"), f"{field}.bounds_wsen")
    payload = geometry_payloads.get(geometry_ref)
    _require(payload is not None, f"{field} GeoJSON payload is required for geometry validation")
    _require(hashlib.sha256(payload).hexdigest() == geometry_file["sha256"], f"{field} GeoJSON bytes do not match the manifest checksum")
    return _geojson_geometry_bounds(
        payload,
        expected_region_id=region["region_id"],
        expected_bounds=declared_bounds,
        field=field,
    )


def _validate_transfer_geometry(
    evaluation: Mapping[str, Any],
    region: Mapping[str, Any],
    files: Any,
    geometry_payloads: Mapping[str, bytes],
    field: str,
) -> None:
    target_bounds = _validate_region_geometry_binding(region, files, field, geometry_payloads)
    transfer_geometry_ref = evaluation.get("transfer_test_region_geometry_ref")
    _require(
        isinstance(transfer_geometry_ref, str)
        and transfer_geometry_ref
        and not transfer_geometry_ref.startswith("/")
        and ".." not in transfer_geometry_ref,
        f"{field} transfer geometry reference is unsafe or missing",
    )
    _require(transfer_geometry_ref != region["geometry_ref"], f"{field} transfer geometry must be a separate file")
    transfer_geometry_sha = evaluation.get("transfer_test_region_geometry_sha256")
    _sha(transfer_geometry_sha, f"{field} transfer geometry checksum")
    _require(transfer_geometry_sha != region["geometry_sha256"], f"{field} transfer geometry must differ from the artifact geometry")
    transfer_file = next((item for item in files if item["path"] == transfer_geometry_ref), None)
    _require(transfer_file is not None, f"{field} transfer geometry is not in the file manifest")
    _require(transfer_file["media_type"] == "application/geo+json", f"{field} transfer geometry must be GeoJSON")
    _require(transfer_file["sha256"] == transfer_geometry_sha, f"{field} transfer geometry checksum does not match its manifest entry")
    transfer_bounds = _validate_bounds_wsen(
        evaluation.get("transfer_test_region_bounds_wsen"),
        f"{field} transfer_test_region_bounds_wsen",
    )
    transfer_payload = geometry_payloads.get(transfer_geometry_ref)
    _require(transfer_payload is not None, f"{field} transfer GeoJSON payload is required for geometry validation")
    _require(hashlib.sha256(transfer_payload).hexdigest() == transfer_geometry_sha, f"{field} transfer GeoJSON bytes do not match the manifest checksum")
    transfer_bounds = _geojson_geometry_bounds(
        transfer_payload,
        expected_region_id=evaluation["transfer_test_region_id"],
        expected_bounds=transfer_bounds,
        field=f"{field} transfer geometry",
    )
    west, south, east, north = target_bounds
    transfer_west, transfer_south, transfer_east, transfer_north = transfer_bounds
    _require(
        transfer_east <= west or transfer_west >= east or transfer_north <= south or transfer_south >= north,
        f"{field} transfer region bounds overlap the artifact region",
    )


def _file_list(files: Any, field: str) -> None:
    _require(isinstance(files, list) and files, f"{field} must contain files")
    paths = []
    for item in files:
        _require(isinstance(item, Mapping), f"{field} entries must be objects")
        path = item.get("path")
        _require(isinstance(path, str) and path and not path.startswith("/") and ".." not in path, f"{field} path is unsafe")
        _require(path not in paths, f"{field} contains duplicate path {path}")
        _require(isinstance(item.get("media_type"), str) and item["media_type"], f"{field}.{path}.media_type is required")
        paths.append(path)
        _integer(item.get("size_bytes"), f"{field}.{path}.size_bytes")
        _sha(item.get("sha256"), f"{field}.{path}.sha256")


def validate_release_manifest(
    manifest: Mapping[str, Any],
    *,
    expected_artifact_id: str | None = None,
    expected_file_paths: set[str] | None = None,
) -> None:
    """Validate the checksum inventory used for atomic publication."""
    for key in ("schema_version", "artifact_id", "manifest_created_at", "files"):
        _require(key in manifest, f"manifest is missing {key}")
    _require(manifest["schema_version"] == "1.0.0", "unsupported manifest schema")
    _require(isinstance(manifest["artifact_id"], str) and ARTIFACT_ID_PATTERN.fullmatch(manifest["artifact_id"]), "invalid manifest artifact ID")
    if expected_artifact_id is not None:
        _require(manifest["artifact_id"] == expected_artifact_id, "manifest artifact ID does not match the analysis artifact")
    _datetime(manifest["manifest_created_at"], "manifest_created_at")
    _file_list(manifest["files"], "manifest.files")
    paths = {entry["path"] for entry in manifest["files"]}
    _require("analysis.json" in paths and "evidence-receipt.json" in paths, "manifest must include analysis and receipt")
    if expected_file_paths is not None:
        _require(paths == expected_file_paths, "manifest file inventory does not match the complete release bundle")


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
    expected_support = round(record["valid_cell_days"] / record["eligible_land_cell_days"], 6)
    _require(record["support_fraction"] == expected_support, "support fraction does not match counts")
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


def _validate_release_evaluation(evaluation: Mapping[str, Any]) -> None:
    """Fail closed unless every documented scientific release gate is evidenced."""
    required = {
        "training_seasons", "heldout_seasons", "positive_block_months", "identity_mae",
        "seasonal_baseline_mae", "candidate_mae", "mae_improvement_fraction", "regional_bias",
        "regional_bias_baseline", "regional_bias_tolerance",
        "peak_month_identifiable", "peak_month_error", "nominal_interval_level",
        "empirical_interval_coverage", "independent_test_block_months", "paired_support_fraction",
        "transfer_test_status", "transfer_test_region_id", "gate_results", "release_gate_status",
        "transfer_test_region_geometry_ref", "transfer_test_region_geometry_sha256",
        "transfer_test_region_bounds_wsen",
    }
    _require(required.issubset(evaluation), "release evaluation is missing required gate evidence")
    _integer(evaluation["training_seasons"], "evaluation.training_seasons", minimum=5)
    _integer(evaluation["heldout_seasons"], "evaluation.heldout_seasons", minimum=2)
    _integer(evaluation["positive_block_months"], "evaluation.positive_block_months", minimum=50)

    identity_mae = evaluation["identity_mae"]
    seasonal_mae = evaluation["seasonal_baseline_mae"]
    candidate_mae = evaluation["candidate_mae"]
    _number(identity_mae, "evaluation.identity_mae", minimum=0)
    _number(seasonal_mae, "evaluation.seasonal_baseline_mae", minimum=0)
    _number(candidate_mae, "evaluation.candidate_mae", minimum=0)
    best_baseline = min(identity_mae, seasonal_mae)
    _require(best_baseline > 0, "release evaluation has no positive simple-baseline error")
    observed_improvement = 1 - candidate_mae / best_baseline
    _number(evaluation["mae_improvement_fraction"], "evaluation.mae_improvement_fraction")
    _require(abs(evaluation["mae_improvement_fraction"] - observed_improvement) <= 0.001, "reported MAE improvement does not match the scores")
    _require(observed_improvement >= 0.1 - 1e-9, "candidate does not beat the best simple baseline by 10%")

    regional_bias = evaluation["regional_bias"]
    baseline_bias = evaluation["regional_bias_baseline"]
    bias_tolerance = evaluation["regional_bias_tolerance"]
    _require(isinstance(regional_bias, Mapping), "evaluation regional bias is required")
    _require(isinstance(baseline_bias, Mapping), "evaluation regional baseline bias is required")
    _require(isinstance(bias_tolerance, Mapping), "evaluation regional bias tolerance is required")
    for role in ("science_pilot", "local_impact_case"):
        _require(role in regional_bias, f"evaluation is missing {role} bias")
        _require(role in baseline_bias and role in bias_tolerance, f"evaluation is missing {role} bias comparator or tolerance")
        _number(regional_bias[role], f"evaluation.regional_bias.{role}")
        _number(baseline_bias[role], f"evaluation.regional_bias_baseline.{role}")
        _number(bias_tolerance[role], f"evaluation.regional_bias_tolerance.{role}", minimum=0)
        _require(
            abs(regional_bias[role]) <= abs(baseline_bias[role]) + bias_tolerance[role],
            f"candidate bias materially regresses in {role}",
        )

    peak_identifiable = evaluation["peak_month_identifiable"]
    _require(isinstance(peak_identifiable, bool), "evaluation.peak_month_identifiable must be boolean")
    if peak_identifiable:
        _integer(evaluation["peak_month_error"], "evaluation.peak_month_error")
        _require(evaluation["peak_month_error"] <= 1, "seasonal peak timing exceeds one month")
    else:
        _require(evaluation["peak_month_error"] is None, "unidentifiable peak timing must have a null error")

    _number(evaluation["nominal_interval_level"], "evaluation.nominal_interval_level", minimum=0, maximum=1)
    _require(evaluation["nominal_interval_level"] == 0.9, "release evaluation must use a nominal 90% interval")
    _number(evaluation["empirical_interval_coverage"], "evaluation.empirical_interval_coverage", minimum=0.85, maximum=0.95)
    _integer(evaluation["independent_test_block_months"], "evaluation.independent_test_block_months", minimum=1)
    _number(evaluation["paired_support_fraction"], "evaluation.paired_support_fraction", minimum=0.5, maximum=1)
    _require(evaluation["transfer_test_status"] == "pass", "independent transfer test has not passed")
    transfer_region_id = evaluation["transfer_test_region_id"]
    _require(
        isinstance(transfer_region_id, str) and transfer_region_id.startswith("region_"),
        "a Transfer Test Region ID must be identified",
    )

    gates = evaluation["gate_results"]
    _require(isinstance(gates, Mapping) and set(gates) == RELEASE_GATES, "evaluation must report every release gate exactly once")
    _require(all(result == "pass" for result in gates.values()), "every release sub-gate must pass")
    _require(evaluation["release_gate_status"] == "pass", "overall release gate has not passed")


def _validate_calibration_metadata(
    artifact: Mapping[str, Any],
    calibration: Mapping[str, Any],
    evaluation: Mapping[str, Any],
    geometry_payloads: Mapping[str, bytes],
) -> None:
    required = {
        "calibration_id", "status", "source_product_id", "reference_product_id", "model_family",
        "evaluation_ref", "domain_summary", "training_manifest_sha256", "split_manifest_sha256",
        "model_sha256", "code_revision", "release_gate_status",
    }
    _require(required.issubset(calibration), "released calibration metadata is incomplete")
    _require(calibration["status"] == "released", "released artifact must reference a released calibration")
    _require(calibration["source_product_id"] in {source["product_id"] for source in artifact["sources"]}, "calibration source product is not in the artifact")
    _require(calibration["source_product_id"] != artifact["reference_product_id"], "calibration source and reference products must differ")
    _require(calibration["reference_product_id"] == artifact["reference_product_id"], "calibration reference product differs from the artifact")
    _require(calibration["model_family"] in {"seasonal_monotone", "grouped_binomial_glm", "beta_binomial", "hierarchical_logistic"}, "calibration model family is invalid")
    _require(isinstance(calibration["domain_summary"], str) and calibration["domain_summary"].strip(), "calibration domain summary is required")
    _require(calibration["release_gate_status"] == "pass", "calibration release gate has not passed")
    _require(isinstance(calibration["code_revision"], str) and len(calibration["code_revision"]) >= 7, "calibration code revision is required")
    _validate_release_evaluation(evaluation)

    sources = {source["product_id"]: source for source in artifact["sources"]}
    _require(calibration["reference_product_id"] in sources, "calibration reference product is not in the artifact")
    source = sources[calibration["source_product_id"]]
    reference = sources[calibration["reference_product_id"]]
    _require(source["stream"] == "science_mask" and reference["stream"] == "science_mask", "calibration must use declared science-mask products")
    minimum_support, source_range, comparable_range = _validate_calibration_domain(
        calibration["domain"],
        source=source,
        reference=reference,
        quality_policy_version=artifact["quality_policy"]["version"],
        grid_version=artifact["grid_version"],
        artifact_region_id=artifact["region"]["region_id"],
        transfer_region_id=evaluation["transfer_test_region_id"],
        minimum_policy_support=artifact["quality_policy"]["minimum_monthly_support_fraction"],
        field="calibration.domain",
    )
    _validate_transfer_geometry(evaluation, artifact["region"], artifact["files"], geometry_payloads, "calibration")
    source_min, source_max = source_range
    comparable_min, comparable_max = comparable_range
    for month in artifact["months"]:
        comparison = month["comparison"]
        if comparison["status"] != "available":
            continue
        source_record = next(record for record in month["native_records"] if record["product_id"] == calibration["source_product_id"])
        reference_record = next(record for record in month["native_records"] if record["product_id"] == calibration["reference_product_id"])
        _require(source_record["support_fraction"] >= minimum_support and reference_record["support_fraction"] >= minimum_support, "available comparison is below its calibration support domain")
        _require(source_record["rate_per_1000"] is not None, "available comparison requires a source rate")
        _require(source_min <= source_record["rate_per_1000"] <= source_max, "source activity is outside the calibration domain")
        _require(comparable_min <= comparison["estimate_per_1000"] <= comparable_max, "Comparable Activity is outside the calibration domain")

    file_hashes = {entry["sha256"] for entry in artifact["files"]}
    _validate_evaluation_payload(
        evaluation,
        artifact["files"],
        calibration["evaluation_ref"],
        "calibration evaluation",
    )
    for field in ("training_manifest_sha256", "split_manifest_sha256", "model_sha256"):
        _sha(calibration[field], f"calibration.{field}")
        _require(calibration[field] in file_hashes, f"calibration {field} must resolve to a checksummed artifact file")


def validate_analysis_artifact(
    artifact: Mapping[str, Any],
    *,
    calibration_evaluation: Mapping[str, Any] | None = None,
    geometry_payloads: Mapping[str, bytes] | None = None,
) -> None:
    """Validate the analysis contract and its most important cross-field rules."""

    required = ("schema_version", "artifact_id", "release_status", "generated_at", "region", "grid_version", "period", "metric", "reference_product_id", "sources", "quality_policy", "calibration", "months", "receipt_ref", "files", "limitations")
    for key in required:
        _require(key in artifact, f"artifact is missing {key}")
    _require(artifact["schema_version"] == "1.0.0", "unsupported artifact schema")
    _require(isinstance(artifact["artifact_id"], str) and ARTIFACT_ID_PATTERN.fullmatch(artifact["artifact_id"]), "invalid artifact ID")
    _require(artifact["release_status"] in {"released", "native_only"}, "invalid artifact release status")
    _datetime(artifact["generated_at"], "generated_at")
    region = artifact["region"]
    _require(region.get("region_id") and region.get("name") and region.get("revision", 0) >= 1, "region identity is incomplete")
    _require(region.get("role") in {"science_pilot", "local_impact_case", "transfer_test_region"}, "region role is invalid")
    _sha(region["geometry_sha256"], "region.geometry_sha256")
    _require(isinstance(artifact["grid_version"], str) and artifact["grid_version"], "grid_version is required")
    _date(artifact["period"]["start_date"], "period.start_date")
    _date(artifact["period"]["end_date"], "period.end_date")
    _require(artifact["period"]["start_date"] <= artifact["period"]["end_date"], "period is reversed")
    _require(artifact["metric"]["metric_id"] == "detected_active_land_cell_days_per_1000_valid_land_cell_days", "unsupported metric")
    _require(artifact["reference_product_id"], "reference product is required")
    _require(isinstance(artifact["sources"], list) and len(artifact["sources"]) >= 2, "at least two sources are required")
    source_ids = set()
    science_source_ids = set()
    for source in artifact["sources"]:
        _validate_source(source)
        _require(source["product_id"] not in source_ids, "duplicate source product")
        source_ids.add(source["product_id"])
        if source["stream"] == "science_mask":
            science_source_ids.add(source["product_id"])
    policy = artifact["quality_policy"]
    _require(policy.get("version") and policy.get("low_confidence_fire_policy") in {"excluded", "included"}, "quality policy is incomplete")
    _number(policy.get("minimum_monthly_support_fraction"), "minimum_monthly_support_fraction", minimum=0, maximum=1)
    _file_list(artifact["files"], "artifact.files")
    if geometry_payloads is not None:
        _validate_region_geometry_binding(region, artifact["files"], "artifact region", geometry_payloads)
    _require(isinstance(artifact["limitations"], list) and artifact["limitations"], "artifact needs limitations")
    _require(isinstance(artifact["months"], list) and artifact["months"], "artifact needs months")
    month_keys = []
    comparison_available = False
    available_calibration_ids = set()
    for month in artifact["months"]:
        key = month.get("month")
        _require(isinstance(key, str) and len(key) == 7 and key[4] == "-", "month key is invalid")
        _date(f"{key}-01", "month key")
        _require(key not in month_keys, "duplicate month")
        if month_keys:
            _require(key > month_keys[-1], "months must be chronological")
        month_keys.append(key)
        records = month.get("native_records")
        _require(isinstance(records, list) and records, "month needs native records")
        for record in records:
            _require(record["product_id"] in source_ids, "native record refers to unknown product")
            _require(record["product_id"] in science_source_ids, "native record must resolve to a science-mask source")
            _validate_native(record)
            if record["observation_status"] == "available":
                _require(record["support_fraction"] >= policy["minimum_monthly_support_fraction"], "available record is below support policy")
            if record["observation_status"] == "insufficient_support":
                _require(record["support_fraction"] < policy["minimum_monthly_support_fraction"], "insufficient-support record meets support policy")
        _validate_comparison(month["comparison"])
        comparison_available = comparison_available or month["comparison"]["status"] == "available"
        if month["comparison"]["status"] == "available":
            available_calibration_ids.add(month["comparison"]["calibration_id"])
    if artifact["release_status"] == "native_only":
        _require(not comparison_available, "native-only artifact cannot contain available comparison")
        _require(artifact["calibration"] is None, "native-only artifact cannot reference calibration")
    else:
        _require(comparison_available and isinstance(artifact["calibration"], Mapping), "released artifact needs available comparison and calibration")
        _require(calibration_evaluation is not None, "released artifact requires linked calibration evaluation evidence")
        _require(geometry_payloads is not None, "released artifact requires actual GeoJSON payloads for geometry validation")
        _validate_calibration_metadata(artifact, artifact["calibration"], calibration_evaluation, geometry_payloads)
        _require(available_calibration_ids == {artifact["calibration"]["calibration_id"]}, "available comparison calibration ID does not match the artifact release")
    _require(isinstance(artifact["receipt_ref"], str) and not artifact["receipt_ref"].startswith("/"), "receipt reference is unsafe")


def validate_evidence_receipt(
    receipt: Mapping[str, Any],
    *,
    geometry_payloads: Mapping[str, bytes] | None = None,
) -> None:
    """Validate the receipt fields needed for reproducible review."""

    required = ("schema_version", "receipt_id", "artifact_id", "published_at", "region", "analysis", "sources", "exclusions", "calibration", "environment", "limitations", "files")
    for key in required:
        _require(key in receipt, f"receipt is missing {key}")
    _require(receipt["schema_version"] == "1.0.0", "unsupported receipt schema")
    _require(isinstance(receipt["receipt_id"], str) and RECEIPT_ID_PATTERN.fullmatch(receipt["receipt_id"]), "invalid receipt ID")
    _datetime(receipt["published_at"], "published_at")
    _sha(receipt["region"]["geometry_sha256"], "receipt.region.geometry_sha256")
    analysis = receipt["analysis"]
    _date(analysis["start_date"], "receipt.analysis.start_date")
    _date(analysis["end_date"], "receipt.analysis.end_date")
    analysis_start = date.fromisoformat(analysis["start_date"])
    analysis_end = date.fromisoformat(analysis["end_date"])
    _require(analysis_start <= analysis_end, "receipt analysis period is reversed")
    _require(
        analysis["metric_id"] == "detected_active_land_cell_days_per_1000_valid_land_cell_days",
        "receipt analysis metric_id is invalid",
    )
    _sha(analysis["source_manifest_sha256"], "source_manifest_sha256")
    _number(analysis["minimum_monthly_support_fraction"], "receipt support threshold", minimum=0, maximum=1)
    coverage = analysis.get("daily_coverage")
    _require(isinstance(coverage, Mapping), "receipt daily_coverage is required")
    expected_days = coverage.get("expected_calendar_days")
    _integer(expected_days, "daily_coverage.expected_calendar_days", minimum=1)
    expected_span = (analysis_end - analysis_start).days + 1
    _require(expected_days == expected_span, "daily coverage expected calendar days do not match the inclusive analysis period")
    modis_days = coverage.get("myd14a1_observed_days")
    viirs_days = coverage.get("vnp14a1_observed_days")
    _integer(modis_days, "daily_coverage.myd14a1_observed_days")
    _integer(viirs_days, "daily_coverage.vnp14a1_observed_days")
    _require(coverage.get("complete") is True, "published sample must have complete daily coverage")
    _require(modis_days == expected_days and viirs_days == expected_days, "daily coverage counts do not match the expected calendar days")
    _require(isinstance(receipt["sources"], list) and len(receipt["sources"]) >= 2, "receipt needs source records")
    source_ids = set()
    for source in receipt["sources"]:
        _validate_source({**source, "nominal_resolution_m": source.get("nominal_resolution_m", 1000)})
        _require(source["product_id"] not in source_ids, "duplicate receipt source product")
        source_ids.add(source["product_id"])
        _require(isinstance(source.get("provider_objects"), list) and source["provider_objects"], "receipt source needs provider objects")
        for obj in source["provider_objects"]:
            _sha(obj["sha256"], "provider object sha256")
            _integer(obj["size_bytes"], "provider object size")
            _datetime(obj["observed_start"], "provider object start")
            _datetime(obj["observed_end"], "provider object end")
            if obj.get("retrieved_at") is None:
                _require(
                    obj.get("retrieval_timestamp_status") == "not_recorded_for_local_copy",
                    "unknown retrieval time must be labeled not_recorded_for_local_copy",
                )
            else:
                _datetime(obj["retrieved_at"], "provider object retrieval")
                if "retrieval_timestamp_status" in obj:
                    _require(
                        obj["retrieval_timestamp_status"] == "recorded",
                        "known retrieval time must be labeled recorded",
                    )
    _file_list(receipt["files"], "receipt.files")
    if geometry_payloads is not None:
        _validate_region_geometry_binding(receipt["region"], receipt["files"], "receipt region", geometry_payloads)
    env = receipt["environment"]
    _require(env.get("python_version") and env.get("pipeline_revision") and env.get("operating_system"), "environment is incomplete")
    _sha(env["dependency_lock_sha256"], "dependency lock sha256")
    for exclusion in receipt["exclusions"]:
        _require(exclusion.get("product_id") in source_ids, "exclusion refers to an unknown product")
        _require(exclusion.get("reason") in {"low_confidence_excluded", "cloud", "unknown", "unprocessed", "water_or_non_land", "outside_region"}, "exclusion reason is invalid")
        _integer(exclusion.get("cell_days"), "exclusion.cell_days")
    calibration = receipt["calibration"]
    if calibration is not None:
        _require(isinstance(calibration, Mapping), "receipt calibration must be an object or null")
        for key in (
            "calibration_id", "status", "source_product_id", "reference_product_id",
            "training_manifest_sha256", "split_manifest_sha256", "model_sha256", "code_revision", "domain", "evaluation_ref", "evaluation",
        ):
            _require(key in calibration, f"receipt calibration is missing {key}")
        _require(calibration["status"] in {"released", "withdrawn"}, "receipt calibration status is invalid")
        _require(calibration["source_product_id"] in source_ids, "receipt calibration source is not listed")
        _require(calibration["reference_product_id"] == analysis["reference_product_id"], "receipt calibration reference does not match the analysis")
        _require(calibration["source_product_id"] != calibration["reference_product_id"], "receipt calibration products must differ")
        _require(isinstance(calibration["code_revision"], str) and len(calibration["code_revision"]) >= 7, "receipt calibration code revision is invalid")
        file_hashes = {entry["sha256"] for entry in receipt["files"]}
        for field in ("training_manifest_sha256", "split_manifest_sha256", "model_sha256"):
            _sha(calibration[field], f"receipt.calibration.{field}")
            _require(calibration[field] in file_hashes, f"receipt calibration {field} must resolve to a checksummed receipt file")
        evaluation = calibration["evaluation"]
        _validate_release_evaluation(evaluation)
        _require(geometry_payloads is not None, "released receipt requires actual GeoJSON payloads for geometry validation")
        _validate_transfer_geometry(evaluation, receipt["region"], receipt["files"], geometry_payloads, "receipt calibration")
        _validate_evaluation_payload(
            evaluation,
            receipt["files"],
            calibration["evaluation_ref"],
            "receipt calibration evaluation",
        )
        source = next((item for item in receipt["sources"] if item["product_id"] == calibration["source_product_id"]), None)
        reference = next((item for item in receipt["sources"] if item["product_id"] == calibration["reference_product_id"]), None)
        _require(source is not None and reference is not None, "receipt calibration products are not listed")
        _validate_calibration_domain(
            calibration["domain"],
            source=source,
            reference=reference,
            quality_policy_version=analysis["quality_policy_version"],
            grid_version=analysis["grid_version"],
            artifact_region_id=receipt["region"]["region_id"],
            transfer_region_id=evaluation["transfer_test_region_id"],
            minimum_policy_support=analysis["minimum_monthly_support_fraction"],
            field="receipt calibration domain",
        )
    _require(isinstance(receipt["limitations"], list) and receipt["limitations"], "receipt needs limitations")


def validate_artifact_receipt_pair(
    artifact: Mapping[str, Any],
    receipt: Mapping[str, Any],
    *,
    calibration_evaluation: Mapping[str, Any] | None = None,
    geometry_payloads: Mapping[str, bytes] | None = None,
) -> None:
    """Validate identity and calibration evidence links across a published pair."""
    validate_analysis_artifact(
        artifact,
        calibration_evaluation=calibration_evaluation,
        geometry_payloads=geometry_payloads,
    )
    validate_evidence_receipt(receipt, geometry_payloads=geometry_payloads)
    _require(artifact["artifact_id"] == receipt["artifact_id"], "receipt belongs to a different analysis artifact")
    _require(
        receipt["receipt_id"] == f"rcpt_{artifact['artifact_id'].rsplit('_', 1)[-1]}",
        "receipt ID must use the artifact's 12-character suffix",
    )
    _require(artifact["region"]["region_id"] == receipt["region"]["region_id"], "artifact and receipt region IDs differ")
    _require(artifact["region"]["revision"] == receipt["region"]["revision"], "artifact and receipt region revisions differ")
    _require(artifact["region"]["geometry_sha256"] == receipt["region"]["geometry_sha256"], "artifact and receipt region geometry differs")
    _require(artifact["region"]["geometry_ref"] == receipt["region"]["geometry_ref"], "artifact and receipt region geometry references differ")
    _require(artifact["region"]["bounds_wsen"] == receipt["region"]["bounds_wsen"], "artifact and receipt region bounds differ")
    _require(artifact["period"]["start_date"] == receipt["analysis"]["start_date"], "artifact and receipt start dates differ")
    _require(artifact["period"]["end_date"] == receipt["analysis"]["end_date"], "artifact and receipt end dates differ")
    _require(artifact["metric"]["metric_id"] == receipt["analysis"]["metric_id"], "artifact and receipt metric IDs differ")
    _require(artifact["reference_product_id"] == receipt["analysis"]["reference_product_id"], "artifact and receipt reference products differ")
    _require(artifact["quality_policy"]["version"] == receipt["analysis"]["quality_policy_version"], "artifact and receipt quality policies differ")
    _require(artifact["grid_version"] == receipt["analysis"]["grid_version"], "artifact and receipt grid versions differ")
    artifact_sources = {source["product_id"]: source for source in artifact["sources"]}
    receipt_sources = {source["product_id"]: source for source in receipt["sources"]}
    _require(set(artifact_sources) == set(receipt_sources), "artifact and receipt source product sets differ")
    for product_id, artifact_source in artifact_sources.items():
        receipt_source = receipt_sources[product_id]
        for field in (
            "short_name",
            "version",
            "platform",
            "stream",
            "nominal_resolution_m",
            "source_url",
            "product_guide_url",
        ):
            _require(
                artifact_source[field] == receipt_source.get(field),
                f"artifact and receipt source {product_id} {field} differs",
            )
    artifact_files = {entry["path"]: entry for entry in artifact["files"]}
    receipt_payload_files = {
        entry["path"]: entry for entry in receipt["files"] if entry["path"] != "analysis.json"
    }
    _require(set(artifact_files) == set(receipt_payload_files), "artifact and receipt payload inventories differ")
    for path, artifact_file in artifact_files.items():
        receipt_file = receipt_payload_files[path]
        _require(
            all(receipt_file.get(field) == artifact_file.get(field) for field in ("media_type", "size_bytes", "sha256")),
            f"artifact and receipt payload metadata differs for {path}",
        )
    _validate_json_payload(
        _canonical_json_payload(artifact),
        receipt["files"],
        "analysis.json",
        "receipt analysis artifact",
    )
    if artifact["release_status"] == "native_only":
        _require(receipt["calibration"] is None, "native-only artifact cannot have a receipt calibration")
        return

    artifact_calibration = artifact["calibration"]
    receipt_calibration = receipt["calibration"]
    _require(isinstance(receipt_calibration, Mapping), "released artifact requires a receipt calibration")
    for field in (
        "calibration_id",
        "status",
        "source_product_id",
        "reference_product_id",
        "training_manifest_sha256",
        "split_manifest_sha256",
        "model_sha256",
        "code_revision",
        "domain",
        "evaluation_ref",
    ):
        _require(
            artifact_calibration[field] == receipt_calibration[field],
            f"artifact and receipt calibration {field} differ",
        )
    _require(calibration_evaluation == receipt_calibration["evaluation"], "receipt evaluation differs from the artifact evaluation evidence")
    artifact_eval_file = next(item for item in artifact["files"] if item["path"] == artifact_calibration["evaluation_ref"])
    receipt_eval_file = next(item for item in receipt["files"] if item["path"] == receipt_calibration["evaluation_ref"])
    _require(
        artifact_eval_file["sha256"] == receipt_eval_file["sha256"]
        and artifact_eval_file["size_bytes"] == receipt_eval_file["size_bytes"],
        "artifact and receipt evaluation payload checksums differ",
    )
