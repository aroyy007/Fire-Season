import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "pipeline"))

from fireseason.contract import validate_analysis_artifact, validate_evidence_receipt
from fireseason.demo import build_demo_release


class AnalysisArtifactContractTests(unittest.TestCase):
    def test_local_release_preserves_native_records_and_unavailable_comparison(self):
        artifact, receipt = build_demo_release("local")

        self.assertEqual(artifact["release_status"], "native_only")
        self.assertIsNone(artifact["calibration"])
        self.assertGreaterEqual(len(artifact["months"]), 12)

        for month in artifact["months"]:
            self.assertEqual(len(month["native_records"]), 2)
            self.assertEqual(month["comparison"]["status"], "calibration_not_released")
            self.assertIsNone(month["comparison"]["estimate_per_1000"])
            self.assertIsNone(month["comparison"]["calibration_id"])
            self.assertIsNotNone(month["comparison"]["reason"])

        validate_analysis_artifact(artifact)
        validate_evidence_receipt(receipt)

    def test_science_release_includes_calibration_and_held_out_evaluation(self):
        artifact, receipt = build_demo_release("science")

        self.assertEqual(artifact["release_status"], "released")
        self.assertIsNotNone(artifact["calibration"])
        self.assertEqual(artifact["calibration"]["calibration_id"], "cal_vnp14a1-to-myd14a1_v1.0.0")
        self.assertIn("evaluation_metrics", artifact["calibration"])

        # Check March months have available comparison
        march_months = [m for m in artifact["months"] if m["month"].endswith("-03")]
        for m in march_months:
            self.assertEqual(m["comparison"]["status"], "available")
            self.assertIsNotNone(m["comparison"]["estimate_per_1000"])
            self.assertIsNotNone(m["comparison"]["lower_90"])
            self.assertIsNotNone(m["comparison"]["upper_90"])

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

    def test_months_must_be_chronological(self):
        artifact, _ = build_demo_release("local")
        artifact["months"][0], artifact["months"][1] = artifact["months"][1], artifact["months"][0]
        with self.assertRaises(ValueError):
            validate_analysis_artifact(artifact)

    def test_artifact_is_json_serializable(self):
        artifact, receipt = build_demo_release("science")
        json.dumps(artifact)
        json.dumps(receipt)


if __name__ == "__main__":
    unittest.main()
