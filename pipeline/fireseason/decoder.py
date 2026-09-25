"""Satellite product decoders for MODIS (MYD14A1) and VIIRS (VNP14A1).

Maps raw HDF4/HDF5 fire mask bands and QA bitfields to standardized semantic
observation states and cell-day metrics.
"""

from __future__ import annotations

import re
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import numpy as np
from pyhdf.SD import SD, SDC
import h5py


def parse_granule_date(filename: str) -> date:
    """Extracts date from standard NASA granule filename A<YYYY><DOY>."""
    m = re.search(r"A(\d{4})(\d{3})", filename)
    if not m:
        raise ValueError(f"Could not parse date from filename: {filename}")
    year, doy = int(m.group(1)), int(m.group(2))
    return date(year, 1, 1) + timedelta(days=doy - 1)


def decode_modis_granule(filepath: str | Path, month_start: date, month_end: date) -> dict[str, Any]:
    """
    Decodes an 8-day MODIS MYD14A1 HDF4 file, strictly trimming daily planes
    to the requested [month_start, month_end) window.
    """
    try:
        fname = Path(filepath).name
        granule_start = parse_granule_date(fname)

        hdf = SD(str(filepath), SDC.READ)
        fm = hdf.select("FireMask")[:]
        hdf.end()

        planes = fm.shape[0] if len(fm.shape) == 3 else 1
        detected = 0
        valid_land = 0
        total_pixels = 0
        included_days = 0

        for i in range(planes):
            plane_date = granule_start + timedelta(days=i)
            if month_start <= plane_date < month_end:
                plane = fm[i] if len(fm.shape) == 3 else fm
                # Standard MODIS FireMask legend:
                # 3=non-fire water, 4=cloud, 5=non-fire land, 6=unknown
                # 7=fire low, 8=fire nominal, 9=fire high
                detected += int(np.isin(plane, [7, 8, 9]).sum())
                valid_land += int(np.isin(plane, [5, 7, 8, 9]).sum())
                total_pixels += int(plane.size)
                included_days += 1

        return {
            "detected": detected,
            "valid_land": valid_land,
            "total_pixels": total_pixels,
            "included_days": included_days,
            "planes": planes,
            "success": True,
        }
    except Exception as e:
        return {
            "detected": 0,
            "valid_land": 0,
            "total_pixels": 0,
            "included_days": 0,
            "planes": 0,
            "success": False,
            "error": str(e),
        }


def decode_viirs_granule(filepath: str | Path, month_start: date, month_end: date) -> dict[str, Any]:
    """
    Decodes a daily VIIRS VNP14A1 HDF5 file, verifying the date is within
    the [month_start, month_end) window.
    """
    try:
        fname = Path(filepath).name
        granule_date = parse_granule_date(fname)

        if not (month_start <= granule_date < month_end):
            return {
                "detected": 0,
                "valid_land": 0,
                "total_pixels": 0,
                "included_days": 0,
                "planes": 1,
                "success": True,
            }

        with h5py.File(str(filepath), "r") as f:
            fm = f["HDFEOS/GRIDS/VIIRS_Grid_Daily_Fire/Data Fields/FireMask"][:]
            detected = int(np.isin(fm, [7, 8, 9]).sum())
            valid_land = int(np.isin(fm, [5, 7, 8, 9]).sum())
            total_pixels = int(fm.size)
            return {
                "detected": detected,
                "valid_land": valid_land,
                "total_pixels": total_pixels,
                "included_days": 1,
                "planes": 1,
                "success": True,
            }
    except Exception as e:
        return {
            "detected": 0,
            "valid_land": 0,
            "total_pixels": 0,
            "included_days": 0,
            "planes": 0,
            "success": False,
            "error": str(e),
        }
