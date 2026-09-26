import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "pipeline"))

from fireseason.calibrator import fit_and_evaluate_transfer


class CalibrationGateTests(unittest.TestCase):
    def test_ratio_candidate_never_becomes_a_released_calibration(self):
        records = []
        for year in range(2013, 2025):
            records.append({
                "year": year,
                "viirs_to_modis_ratio": 1.2,
                "viirs_rate_per_1000": 12.0,
                "modis_rate_per_1000": 10.0,
            })

        result = fit_and_evaluate_transfer(records)

        self.assertEqual(result["status"], "experimental")
        self.assertFalse(result["release_eligible"])
        self.assertIsNone(result["calibration"])
        self.assertIn("geographic transfer", result["reason"])

    def test_zero_identity_error_does_not_divide_by_zero(self):
        records = []
        for year in range(2013, 2025):
            records.append({
                "year": year,
                "viirs_to_modis_ratio": 1.0,
                "viirs_rate_per_1000": 10.0,
                "modis_rate_per_1000": 10.0,
            })
        result = fit_and_evaluate_transfer(records)
        self.assertIsNone(result["candidate"]["improvement_pct_vs_identity"])


if __name__ == "__main__":
    unittest.main()
