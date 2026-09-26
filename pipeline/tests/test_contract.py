import hashlib
import json
import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "pipeline"))

from fireseason.contract import (
    _canonical_json_payload,
    validate_analysis_artifact,
    validate_artifact_receipt_pair,
    validate_evidence_receipt,
)
from fireseason.demo import build_demo_release


class AnalysisArtifactContractTests(unittest.TestCase):
    @staticmethod
    def _geojson_bytes(region_id, bounds, *, coordinate_bounds=None):
        west, south, east, north = coordinate_bounds or bounds
        ring = [[west, south], [east, south], [east, north], [west, north], [west, south]]
        return _canonical_json_payload({
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": {"region_id": region_id, "bounds_wsen": list(bounds)},
                "geometry": {"type": "Polygon", "coordinates": [ring]},
            }],
        })

    def _release_candidate(self):
        artifact, _ = build_demo_release("science")
        zero_sha = "0" * 64
        calibration_id = "cal_test_2023"
        source_version = next(source["version"] for source in artifact["sources"] if source["product_id"] == "vnp14a1_002_suomi_npp")
        reference_version = next(source["version"] for source in artifact["sources"] if source["product_id"] == "myd14a1_061_aqua")
        transfer_region_id = "region_transfer_test_r1"
        artifact["release_status"] = "released"
        artifact["calibration"] = {
            "calibration_id": calibration_id,
            "status": "released",
            "source_product_id": "vnp14a1_002_suomi_npp",
            "reference_product_id": "myd14a1_061_aqua",
            "model_family": "grouped_binomial_glm",
            "evaluation_ref": "evaluation.json",
            "domain_summary": "Declared test domain.",
            "domain": {
                "source_product_version": source_version,
                "reference_product_version": reference_version,
                "quality_policy_version": artifact["quality_policy"]["version"],
                "grid_version": artifact["grid_version"],
                "region_ids": [artifact["region"]["region_id"], transfer_region_id],
                "source_activity_range_per_1000": {"minimum": 0, "maximum": 30},
                "comparable_activity_range_per_1000": {"minimum": 0, "maximum": 50},
                "minimum_support_fraction": 0.5,
            },
            "training_manifest_sha256": zero_sha,
            "split_manifest_sha256": zero_sha,
            "model_sha256": zero_sha,
            "code_revision": "abcdef1234567",
            "release_gate_status": "pass",
        }
        artifact["months"][0]["comparison"] = {
            "status": "available",
            "estimate_per_1000": 18.0,
            "lower_90": 15.0,
            "upper_90": 21.0,
            "interval_method": "annual-and-spatial-block-bootstrap",
            "calibration_id": calibration_id,
            "reason": None,
        }
        evaluation = {
            "training_seasons": 5,
            "heldout_seasons": 2,
            "positive_block_months": 50,
            "identity_mae": 10.0,
            "seasonal_baseline_mae": 12.0,
            "candidate_mae": 9.0,
            "mae_improvement_fraction": 0.1,
            "regional_bias": {"science_pilot": 0.2, "local_impact_case": -0.1},
            "regional_bias_baseline": {"science_pilot": 0.25, "local_impact_case": -0.12},
            "regional_bias_tolerance": {"science_pilot": 0.1, "local_impact_case": 0.1},
            "peak_month_identifiable": True,
            "peak_month_error": 1,
            "nominal_interval_level": 0.9,
            "empirical_interval_coverage": 0.9,
            "independent_test_block_months": 80,
            "paired_support_fraction": 0.75,
            "transfer_test_status": "pass",
            "transfer_test_region_id": transfer_region_id,
            "transfer_test_region_geometry_ref": "transfer-test-region.geojson",
            "transfer_test_region_geometry_sha256": "f" * 64,
            "transfer_test_region_bounds_wsen": [100.0, 0.0, 101.0, 1.0],
            "gate_results": {
                "training_and_holdout_support": "pass",
                "paired_support": "pass",
                "baseline_skill": "pass",
                "regional_bias": "pass",
                "peak_timing": "pass",
                "interval_coverage": "pass",
                "transfer_test": "pass",
                "declared_domain": "pass",
                "provenance_reproducibility": "pass",
            },
            "release_gate_status": "pass",
        }
        target_geometry = self._geojson_bytes(artifact["region"]["region_id"], artifact["region"]["bounds_wsen"])
        transfer_geometry = self._geojson_bytes(transfer_region_id, evaluation["transfer_test_region_bounds_wsen"])
        artifact["region"]["geometry_sha256"] = hashlib.sha256(target_geometry).hexdigest()
        evaluation["transfer_test_region_geometry_sha256"] = hashlib.sha256(transfer_geometry).hexdigest()
        evaluation_bytes = _canonical_json_payload(evaluation)
        artifact["files"] = [
            {"path": "training-manifest.ndjson", "media_type": "application/octet-stream", "size_bytes": 0, "sha256": zero_sha},
            {"path": "split-manifest.json", "media_type": "application/octet-stream", "size_bytes": 0, "sha256": zero_sha},
            {"path": "model.bin", "media_type": "application/octet-stream", "size_bytes": 0, "sha256": zero_sha},
            {"path": "region.geojson", "media_type": "application/geo+json", "size_bytes": len(target_geometry), "sha256": artifact["region"]["geometry_sha256"]},
            {"path": "transfer-test-region.geojson", "media_type": "application/geo+json", "size_bytes": len(transfer_geometry), "sha256": evaluation["transfer_test_region_geometry_sha256"]},
            {
                "path": "evaluation.json",
                "media_type": "application/json",
                "size_bytes": len(evaluation_bytes),
                "sha256": hashlib.sha256(evaluation_bytes).hexdigest(),
            },
        ]
        self.geometry_payloads = {
            "region.geojson": target_geometry,
            "transfer-test-region.geojson": transfer_geometry,
        }
        return artifact, evaluation

    def _validate_candidate(self, artifact, evaluation):
        validate_analysis_artifact(
            artifact,
            calibration_evaluation=evaluation,
            geometry_payloads=self.geometry_payloads,
        )

    def _replace_transfer_geometry(self, artifact, evaluation, payload, *, declared_bounds=None, declared_region_id=None):
        if declared_bounds is not None:
            evaluation["transfer_test_region_bounds_wsen"] = list(declared_bounds)
        if declared_region_id is not None:
            evaluation["transfer_test_region_id"] = declared_region_id
        payload_sha = hashlib.sha256(payload).hexdigest()
        evaluation["transfer_test_region_geometry_sha256"] = payload_sha
        ref = evaluation["transfer_test_region_geometry_ref"]
        self.geometry_payloads[ref] = payload
        geometry_entry = next(item for item in artifact["files"] if item["path"] == ref)
        geometry_entry["size_bytes"] = len(payload)
        geometry_entry["sha256"] = payload_sha
        evaluation_bytes = _canonical_json_payload(evaluation)
        evaluation_entry = next(item for item in artifact["files"] if item["path"] == "evaluation.json")
        evaluation_entry["size_bytes"] = len(evaluation_bytes)
        evaluation_entry["sha256"] = hashlib.sha256(evaluation_bytes).hexdigest()

    def test_local_release_preserves_native_records_and_unavailable_comparison(self):
        artifact, receipt = build_demo_release("local")

        self.assertEqual(artifact["release_status"], "native_only")
        self.assertIsNone(artifact["calibration"])
        self.assertEqual(len(artifact["months"]), 1)

        for month in artifact["months"]:
            self.assertEqual(len(month["native_records"]), 2)
            self.assertEqual(month["comparison"]["status"], "calibration_not_released")
            self.assertIsNone(month["comparison"]["estimate_per_1000"])
            self.assertIsNone(month["comparison"]["calibration_id"])
            self.assertIsNotNone(month["comparison"]["reason"])

        validate_analysis_artifact(artifact)
        validate_evidence_receipt(receipt)

    def test_science_fixture_cannot_release_calibration_from_monthly_ratio(self):
        artifact, receipt = build_demo_release("science")

        self.assertEqual(artifact["release_status"], "native_only")
        self.assertIsNone(artifact["calibration"])

        for month in artifact["months"]:
            self.assertEqual(month["comparison"]["status"], "calibration_not_released")
            self.assertIsNone(month["comparison"]["estimate_per_1000"])
            self.assertIsNone(month["comparison"]["lower_90"])
            self.assertIsNone(month["comparison"]["upper_90"])
        self.assertIn("contract_fixture_not_scientific_result", artifact["limitations"])

        validate_analysis_artifact(artifact)
        validate_evidence_receipt(receipt)

    def test_native_rate_is_independent_of_comparison(self):
        artifact, _ = build_demo_release("local")
        month = artifact["months"][0]
        for record in month["native_records"]:
            if record["rate_per_1000"] is None:
                self.assertIsNone(record["detected_cell_days"])
                continue
            expected = round(
                1000 * record["detected_cell_days"] / record["valid_cell_days"], 4
            )
            self.assertEqual(record["rate_per_1000"], expected)
        self.assertNotIn("rate_per_1000", month["comparison"])

    def test_invalid_unavailable_result_is_rejected(self):
        artifact, _ = build_demo_release("local")
        artifact["months"][0]["comparison"]["estimate_per_1000"] = 4.0
        with self.assertRaises(ValueError):
            validate_analysis_artifact(artifact)

    def test_support_fraction_must_match_counts(self):
        artifact, _ = build_demo_release("local")
        artifact["months"][0]["native_records"][0]["support_fraction"] = 0.5
        with self.assertRaises(ValueError):
            validate_analysis_artifact(artifact)

    def test_released_calibration_requires_passed_evaluation_evidence(self):
        artifact, evaluation = self._release_candidate()

        with self.assertRaisesRegex(ValueError, "evaluation evidence"):
            validate_analysis_artifact(artifact)

        with self.assertRaisesRegex(ValueError, "actual GeoJSON payloads"):
            validate_analysis_artifact(artifact, calibration_evaluation=evaluation)

        self._validate_candidate(artifact, evaluation)

    def test_transfer_region_must_be_separate_from_artifact_region(self):
        artifact, evaluation = self._release_candidate()
        evaluation["transfer_test_region_id"] = artifact["region"]["region_id"]

        with self.assertRaisesRegex(ValueError, "must be separate"):
            self._validate_candidate(artifact, evaluation)

    def test_transfer_region_bounds_must_not_overlap_artifact_region(self):
        artifact, evaluation = self._release_candidate()
        overlap = [-96.5, 40.5, -95.5, 41.5]
        geometry = self._geojson_bytes(evaluation["transfer_test_region_id"], overlap)
        self._replace_transfer_geometry(artifact, evaluation, geometry, declared_bounds=overlap)

        with self.assertRaisesRegex(ValueError, "bounds overlap"):
            self._validate_candidate(artifact, evaluation)

    def test_transfer_geojson_region_id_must_match_evaluation(self):
        artifact, evaluation = self._release_candidate()
        geometry = self._geojson_bytes("region_other_transfer_r1", evaluation["transfer_test_region_bounds_wsen"])
        self._replace_transfer_geometry(artifact, evaluation, geometry)

        with self.assertRaisesRegex(ValueError, "GeoJSON region ID does not match"):
            self._validate_candidate(artifact, evaluation)

    def test_transfer_geojson_coordinates_must_match_declared_bounds(self):
        artifact, evaluation = self._release_candidate()
        geometry = self._geojson_bytes(
            evaluation["transfer_test_region_id"],
            evaluation["transfer_test_region_bounds_wsen"],
            coordinate_bounds=[101.0, 0.0, 102.0, 1.0],
        )
        self._replace_transfer_geometry(artifact, evaluation, geometry)

        with self.assertRaisesRegex(ValueError, "coordinates do not match the declared bounds"):
            self._validate_candidate(artifact, evaluation)

    def test_transfer_geojson_polygon_must_use_closed_linear_rings(self):
        artifact, evaluation = self._release_candidate()
        document = json.loads(self.geometry_payloads[evaluation["transfer_test_region_geometry_ref"]])
        document["features"][0]["geometry"]["coordinates"] = [[
            [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0],
        ]]
        self._replace_transfer_geometry(artifact, evaluation, _canonical_json_payload(document))

        with self.assertRaisesRegex(ValueError, "must be closed"):
            self._validate_candidate(artifact, evaluation)

    def test_transfer_geojson_polygon_rejects_flat_coordinate_arrays(self):
        artifact, evaluation = self._release_candidate()
        document = json.loads(self.geometry_payloads[evaluation["transfer_test_region_geometry_ref"]])
        document["features"][0]["geometry"]["coordinates"] = [
            [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 0.0],
        ]
        self._replace_transfer_geometry(artifact, evaluation, _canonical_json_payload(document))

        with self.assertRaisesRegex(ValueError, "closed linear ring"):
            self._validate_candidate(artifact, evaluation)

    def test_transfer_geometry_checksum_must_match_manifest(self):
        artifact, evaluation = self._release_candidate()
        evaluation["transfer_test_region_geometry_sha256"] = "e" * 64

        with self.assertRaisesRegex(ValueError, "checksum does not match its manifest entry"):
            self._validate_candidate(artifact, evaluation)

    def test_evaluation_payload_must_match_its_checksummed_file(self):
        artifact, evaluation = self._release_candidate()
        evaluation["candidate_mae"] = 8.0
        evaluation["mae_improvement_fraction"] = 0.2

        with self.assertRaisesRegex(ValueError, "checksum does not match"):
            self._validate_candidate(artifact, evaluation)

    def test_release_gate_rejects_missing_support_and_wrong_comparison_calibration(self):
        artifact, evaluation = self._release_candidate()
        evaluation["paired_support_fraction"] = 0.49
        with self.assertRaisesRegex(ValueError, "paired_support_fraction"):
            self._validate_candidate(artifact, evaluation)

        artifact, evaluation = self._release_candidate()
        artifact["months"][0]["comparison"]["calibration_id"] = "cal_other"
        with self.assertRaisesRegex(ValueError, "calibration ID"):
            self._validate_candidate(artifact, evaluation)

    def test_release_gate_rejects_baseline_bias_interval_and_domain_failures(self):
        failure_cases = (
            ("baseline skill", "candidate_mae", 9.2, "mae_improvement_fraction", 0.08, "10%"),
            ("regional bias", "regional_bias", {"science_pilot": 0.2, "local_impact_case": 1.0}, None, None, "materially regresses"),
            ("interval coverage", "empirical_interval_coverage", 0.84, None, None, "empirical_interval_coverage"),
            ("domain", "quality_policy_version", "different-policy", None, None, "quality policy does not match"),
        )
        for label, field, value, secondary_field, secondary_value, expected_error in failure_cases:
            with self.subTest(gate=label):
                artifact, evaluation = self._release_candidate()
                if field == "quality_policy_version":
                    artifact["calibration"]["domain"][field] = value
                else:
                    evaluation[field] = value
                if secondary_field:
                    evaluation[secondary_field] = secondary_value
                with self.assertRaisesRegex(ValueError, expected_error):
                    self._validate_candidate(artifact, evaluation)

    def test_evidence_receipt_requires_gate_evidence_and_checksummed_release_inputs(self):
        artifact, evaluation = self._release_candidate()
        _, receipt = build_demo_release("science")
        receipt["region"] = copy.deepcopy(artifact["region"])
        calibration = artifact["calibration"]
        receipt["calibration"] = {
            **{key: calibration[key] for key in (
                "calibration_id", "status", "source_product_id", "reference_product_id",
                "training_manifest_sha256", "split_manifest_sha256", "model_sha256", "code_revision", "domain", "evaluation_ref",
            )},
            "evaluation": evaluation,
        }
        artifact_bytes = _canonical_json_payload(artifact)
        receipt["files"] = [
            {"path": "analysis.json", "media_type": "application/json", "size_bytes": len(artifact_bytes), "sha256": hashlib.sha256(artifact_bytes).hexdigest()},
            *copy.deepcopy(artifact["files"]),
        ]
        validate_evidence_receipt(receipt, geometry_payloads=self.geometry_payloads)
        validate_artifact_receipt_pair(
            artifact,
            receipt,
            calibration_evaluation=evaluation,
            geometry_payloads=self.geometry_payloads,
        )

        mutations = (
            ("status", "withdrawn"),
            ("code_revision", "fedcba9876543"),
            ("domain", {**receipt["calibration"]["domain"], "source_activity_range_per_1000": {"minimum": 0, "maximum": 10}}),
        )
        for field, value in mutations:
            with self.subTest(calibration_field=field):
                original_calibration = copy.deepcopy(receipt["calibration"])
                receipt["calibration"][field] = value
                with self.assertRaisesRegex(ValueError, f"calibration {field} differ"):
                    validate_artifact_receipt_pair(artifact, receipt, calibration_evaluation=evaluation, geometry_payloads=self.geometry_payloads)
                receipt["calibration"] = original_calibration

        original_calibration = copy.deepcopy(receipt["calibration"])
        receipt["calibration"]["model_sha256"] = "1" * 64
        next(item for item in receipt["files"] if item["path"] == "model.bin")["sha256"] = "1" * 64
        with self.assertRaisesRegex(ValueError, "payload metadata differs for model.bin"):
            validate_artifact_receipt_pair(artifact, receipt, calibration_evaluation=evaluation, geometry_payloads=self.geometry_payloads)
        receipt["calibration"] = original_calibration
        next(item for item in receipt["files"] if item["path"] == "model.bin")["sha256"] = "0" * 64

        receipt["calibration"]["evaluation"]["candidate_mae"] = 8.0
        receipt["calibration"]["evaluation"]["mae_improvement_fraction"] = 0.2
        with self.assertRaisesRegex(ValueError, "checksum does not match"):
            validate_artifact_receipt_pair(artifact, receipt, calibration_evaluation=evaluation, geometry_payloads=self.geometry_payloads)

    def test_months_must_be_chronological(self):
        artifact, _ = build_demo_release("local")
        earlier = dict(artifact["months"][0])
        earlier["month"] = "2023-04"
        artifact["months"].insert(0, earlier)
        with self.assertRaises(ValueError):
            validate_analysis_artifact(artifact)

    def test_artifact_is_json_serializable(self):
        artifact, receipt = build_demo_release("science")
        json.dumps(artifact)
        json.dumps(receipt)


if __name__ == "__main__":
    unittest.main()
