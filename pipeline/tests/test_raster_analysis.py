import sys
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "pipeline"))

from fireseason.raster_analysis import (
    assert_complete_daily_coverage,
    block_count_arrays,
    classify_fire_mask,
    points_in_polygon,
)
from fireseason.decoder import decode_modis_granule
from fireseason.sample import _decode_modis_month


class RasterAnalysisTests(unittest.TestCase):
    def test_fire_mask_uses_land_qa_and_excludes_low_confidence_and_unknown(self):
        mask = np.array([[5, 7, 8, 9, 4, 8, 9, 5]], dtype=np.uint8)
        qa = np.array([[2, 2, 2, 2, 2, 0, 1, 3]], dtype=np.uint8)
        aoi = np.ones(mask.shape, dtype=bool)

        eligible, valid, detected = classify_fire_mask(mask, qa, aoi)

        self.assertEqual(int(eligible.sum()), 5)
        self.assertEqual(int(valid.sum()), 3)
        self.assertEqual(int(detected.sum()), 2)
        self.assertTrue(np.all(detected <= valid))
        self.assertTrue(np.all(valid <= eligible))

    def test_polygon_mask_uses_pixel_centers_and_includes_boundary(self):
        x = np.array([[0.5, 1.5, 2.5], [0.5, 1.5, 2.5]])
        y = np.array([[0.5, 0.5, 0.5], [1.5, 1.5, 1.5]])
        ring = [(0.5, 0.5), (2.0, 0.5), (2.0, 1.5), (0.5, 1.5), (0.5, 0.5)]

        mask = points_in_polygon(x, y, ring)

        self.assertEqual(mask.tolist(), [[True, True, False], [True, True, False]])

    def test_block_counts_sum_exact_pixel_cell_days(self):
        eligible = np.ones((20, 20), dtype=np.uint16)
        valid = np.zeros((20, 20), dtype=np.uint16)
        detected = np.zeros((20, 20), dtype=np.uint16)
        valid[:10, :10] = 2
        detected[:3, :3] = 1

        blocks = block_count_arrays(eligible, valid, detected, block_size=10)

        self.assertEqual(blocks["eligible"].shape, (2, 2))
        self.assertEqual(int(blocks["eligible"][0, 0]), 100)
        self.assertEqual(int(blocks["valid"][0, 0]), 200)
        self.assertEqual(int(blocks["detected"][0, 0]), 9)
        self.assertEqual(int(blocks["detected"].sum()), 9)

    def test_incomplete_month_coverage_fails_with_missing_dates(self):
        start = date(2023, 3, 1)
        expected = [start + timedelta(days=i) for i in range(31)]
        actual = [day for day in expected if day.day != 17]

        with self.assertRaisesRegex(ValueError, "2023-03-17"):
            assert_complete_daily_coverage(expected, actual, "VIIRS")

    def test_duplicate_day_coverage_is_rejected(self):
        day = date(2023, 3, 1)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            assert_complete_daily_coverage([day], [day, day], "MODIS")

    def test_modis_planes_outside_requested_month_are_trimmed(self):
        # A2023057 is 26 February 2023. The eight planes span into March;
        # only the final five planes belong to the requested month.
        fire = np.array([9, 9, 9, 5, 8, 5, 5, 5], dtype=np.uint8).reshape(8, 1, 1)
        qa = np.full(fire.shape, 2, dtype=np.uint8)
        with patch("fireseason.decoder.read_modis_planes", return_value=(fire, qa)):
            result = decode_modis_granule(
                "MYD14A1.A2023057.061.test.hdf",
                date(2023, 3, 1),
                date(2023, 4, 1),
                np.ones((1, 1), dtype=bool),
            )

        self.assertTrue(result["success"], result.get("error"))
        self.assertEqual(result["included_days"], 5)
        self.assertEqual(result["detected"], 1)
        self.assertEqual(result["valid_land"], 5)
        self.assertEqual(result["total_aoi_pixels"], 5)

    def test_publisher_month_decoder_trims_spanning_modis_granules(self):
        starts = ("057", "065", "073", "081", "089")
        files = [Path(f"MYD14A1.A2023{day}.061.test.hdf") for day in starts]
        aoi_masks = {"pilot": np.ones((1, 1), dtype=bool)}
        first_fire = np.array([9, 9, 9, 5, 8, 5, 5, 5], dtype=np.uint8).reshape(8, 1, 1)
        other_fire = np.full((8, 1, 1), 5, dtype=np.uint8)
        qa = np.full((8, 1, 1), 2, dtype=np.uint8)

        def read_planes(path):
            return (first_fire if Path(path).name == files[0].name else other_fire), qa

        with patch("fireseason.sample.read_modis_planes", side_effect=read_planes):
            counts, used_files, _ = _decode_modis_month(files, aoi_masks)

        self.assertEqual(len(used_files), 5)
        self.assertEqual(int(counts["pilot"]["eligible"].sum()), 31)
        self.assertEqual(int(counts["pilot"]["valid"].sum()), 31)
        self.assertEqual(int(counts["pilot"]["detected"].sum()), 1)


if __name__ == "__main__":
    unittest.main()
