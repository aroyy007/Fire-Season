"""QA-aware MYD14A1 and VNP14A1 decoders for a caller-supplied AOI mask."""

from __future__ import annotations

import re
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import numpy as np

from .raster_analysis import classify_fire_mask, read_modis_planes, read_viirs_plane


def parse_granule_date(filename: str) -> date:
    """Extract the first observation date from an A<YYYY><DOY> granule name."""
    match = re.search(r"A(\d{4})(\d{3})", filename)
    if not match:
        raise ValueError(f"Could not parse date from filename: {filename}")
    year, day_of_year = map(int, match.groups())
    return date(year, 1, 1) + timedelta(days=day_of_year - 1)


def _empty_result(planes: int = 0) -> dict[str, Any]:
    return {
        "detected": 0,
        "valid_land": 0,
        "eligible_land": 0,
        "total_aoi_pixels": 0,
        "included_days": 0,
        "planes": planes,
        "success": False,
    }


def _accumulate(
    totals: dict[str, Any],
    fire_mask: np.ndarray,
    qa: np.ndarray,
    aoi_mask: np.ndarray,
) -> None:
    eligible, valid, detected = classify_fire_mask(fire_mask, qa, aoi_mask)
    totals["eligible_land"] += int(eligible.sum())
    totals["valid_land"] += int(valid.sum())
    totals["detected"] += int(detected.sum())
    totals["included_days"] += 1


def _require_aoi_mask(aoi_mask: np.ndarray | None) -> np.ndarray:
    if aoi_mask is None:
        raise ValueError("aoi_mask is required; full-tile counts are not a regional analysis")
    mask = np.asarray(aoi_mask, dtype=bool)
    if mask.ndim != 2 or not mask.any():
        raise ValueError("aoi_mask must be a non-empty two-dimensional boolean mask")
    return mask


def decode_modis_granule(
    filepath: str | Path,
    month_start: date,
    month_end: date,
    aoi_mask: np.ndarray | None = None,
) -> dict[str, Any]:
    """Decode only MYD14A1 daily planes in ``[month_start, month_end)``."""
    aoi_mask = _require_aoi_mask(aoi_mask)
    result = _empty_result()
    try:
        fire_stack, qa_stack = read_modis_planes(filepath)
        planes = fire_stack.shape[0] if fire_stack.ndim == 3 else 1
        result["planes"] = planes
        if fire_stack.shape != qa_stack.shape or fire_stack.shape[-2:] != aoi_mask.shape:
            raise ValueError("FireMask, QA, and AOI mask dimensions do not match")
        start = parse_granule_date(Path(filepath).name)
        for index in range(planes):
            observed = start + timedelta(days=index)
            if not month_start <= observed < month_end:
                continue
            fire_plane = fire_stack[index] if fire_stack.ndim == 3 else fire_stack
            qa_plane = qa_stack[index] if qa_stack.ndim == 3 else qa_stack
            _accumulate(result, fire_plane, qa_plane, aoi_mask)
        result["total_aoi_pixels"] = int(aoi_mask.sum()) * result["included_days"]
        result["success"] = True
        return result
    except Exception as error:
        result["error"] = str(error)
        return result


def decode_viirs_granule(
    filepath: str | Path,
    month_start: date,
    month_end: date,
    aoi_mask: np.ndarray | None = None,
) -> dict[str, Any]:
    """Decode one VNP14A1 daily observation when its date is in the interval."""
    aoi_mask = _require_aoi_mask(aoi_mask)
    result = _empty_result(planes=1)
    try:
        observed = parse_granule_date(Path(filepath).name)
        if not month_start <= observed < month_end:
            result["success"] = True
            return result
        fire_mask, qa = read_viirs_plane(filepath)
        if fire_mask.shape != qa.shape or fire_mask.shape != aoi_mask.shape:
            raise ValueError("FireMask, QA, and AOI mask dimensions do not match")
        _accumulate(result, fire_mask, qa, aoi_mask)
        result["total_aoi_pixels"] = int(aoi_mask.sum())
        result["success"] = True
        return result
    except Exception as error:
        result["error"] = str(error)
        return result


#hello 