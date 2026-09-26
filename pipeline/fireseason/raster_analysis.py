"""QA-aware raster utilities for the bounded NASA fire-mask research sample."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
from pyproj import Transformer

SINUSOIDAL_CRS = "+proj=sinu +R=6371007.181 +lon_0=0 +x_0=0 +y_0=0 +units=m +no_defs"
MODIS_FIREMASK_PATH = "FireMask"
MODIS_QA_PATH = "QA"
VIIRS_GRID_PATH = "HDFEOS/GRIDS/VIIRS_Grid_Daily_Fire"
VIIRS_DATA_PATH = VIIRS_GRID_PATH + "/Data Fields"


def qa_land_mask(qa: np.ndarray) -> np.ndarray:
    """Return pixels whose product QA land/water bits identify land."""
    return (np.asarray(qa) & 0b11) == 0b10


def classify_fire_mask(
    fire_mask: np.ndarray,
    qa: np.ndarray,
    aoi_mask: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return eligible land, valid land, and nominal/high fire boolean masks.

    QA bits 0–1 identify land as ``10``. Low-confidence detections (class 7)
    count as eligible land but are excluded from both valid support and fires.
    Only clear non-fire land (5) and nominal/high detections (8/9) are valid.
    """
    fire_mask = np.asarray(fire_mask)
    qa = np.asarray(qa)
    aoi_mask = np.asarray(aoi_mask, dtype=bool)
    if fire_mask.shape != qa.shape or fire_mask.shape != aoi_mask.shape:
        raise ValueError("FireMask, QA, and AOI mask must have identical shapes")

    land = aoi_mask & qa_land_mask(qa)
    valid = land & np.isin(fire_mask, (5, 8, 9))
    detected = land & np.isin(fire_mask, (8, 9))
    return land, valid, detected


def points_in_polygon(
    x: np.ndarray,
    y: np.ndarray,
    ring: Sequence[tuple[float, float]],
) -> np.ndarray:
    """Test projected pixel-center coordinates against a closed polygon ring.

    Points exactly on the polygon boundary are included. This implements the
    protocol's pixel-center AOI rule and avoids fractional pixel weights.
    """
    x, y = np.broadcast_arrays(np.asarray(x, dtype=float), np.asarray(y, dtype=float))
    if len(ring) < 4 or ring[0] != ring[-1]:
        raise ValueError("polygon ring must be closed and contain at least four points")

    inside = np.zeros(x.shape, dtype=bool)
    boundary = np.zeros(x.shape, dtype=bool)
    scale = max(1.0, *(abs(value) for point in ring for value in point))
    epsilon = scale * 1e-12
    for (x1, y1), (x2, y2) in zip(ring[:-1], ring[1:]):
        cross = (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)
        on_edge = (
            (np.abs(cross) <= epsilon)
            & (x >= min(x1, x2) - epsilon)
            & (x <= max(x1, x2) + epsilon)
            & (y >= min(y1, y2) - epsilon)
            & (y <= max(y1, y2) + epsilon)
        )
        boundary |= on_edge
        if y1 == y2:
            continue
        crosses = (y1 > y) != (y2 > y)
        crossing_x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
        inside ^= crosses & (x < crossing_x)
    return inside | boundary


def projected_bbox_ring(
    bounds: tuple[float, float, float, float],
    edge_segments: int = 32,
) -> list[tuple[float, float]]:
    """Project a lon/lat rectangle to sinusoidal coordinates with densified edges."""
    west, south, east, north = bounds
    if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
        raise ValueError("invalid geographic bounding box")
    if edge_segments < 1:
        raise ValueError("edge_segments must be positive")

    transformer = Transformer.from_crs("EPSG:4326", SINUSOIDAL_CRS, always_xy=True)
    coordinates: list[tuple[float, float]] = []
    edges = (
        ((west, south), (east, south)),
        ((east, south), (east, north)),
        ((east, north), (west, north)),
        ((west, north), (west, south)),
    )
    for (x0, y0), (x1, y1) in edges:
        for i in range(edge_segments):
            t = i / edge_segments
            lon, lat = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            px, py = transformer.transform(lon, lat)
            coordinates.append((float(px), float(py)))
    coordinates.append(coordinates[0])
    return coordinates


def sinusoidal_bbox_mask(
    bounds: tuple[float, float, float, float],
    x_centers: np.ndarray,
    y_centers: np.ndarray,
) -> np.ndarray:
    """Create a raster mask by testing each native-grid pixel center in the AOI."""
    xs = np.asarray(x_centers, dtype=float)
    ys = np.asarray(y_centers, dtype=float)
    if xs.ndim != 1 or ys.ndim != 1 or len(xs) == 0 or len(ys) == 0:
        raise ValueError("grid coordinates must be non-empty one-dimensional arrays")

    ring = projected_bbox_ring(bounds)
    ring_x = [point[0] for point in ring]
    ring_y = [point[1] for point in ring]
    cols = np.flatnonzero((xs >= min(ring_x)) & (xs <= max(ring_x)))
    rows = np.flatnonzero((ys >= min(ring_y)) & (ys <= max(ring_y)))
    mask = np.zeros((len(ys), len(xs)), dtype=bool)
    if len(rows) == 0 or len(cols) == 0:
        return mask
    xx, yy = np.meshgrid(xs[cols], ys[rows])
    mask[np.ix_(rows, cols)] = points_in_polygon(xx, yy, ring)
    return mask


def assert_complete_daily_coverage(
    expected_dates: Iterable[object],
    observed_dates: Iterable[object],
    sensor: str,
) -> None:
    """Fail closed on missing or multiply represented calendar days."""
    expected = list(expected_dates)
    observed = list(observed_dates)
    expected_set = set(expected)
    observed_set = set(observed)
    missing = sorted(expected_set - observed_set)
    unexpected = sorted(observed_set - expected_set)
    duplicates = sorted({day for day in observed if observed.count(day) > 1})
    if missing or unexpected or duplicates or len(expected) != len(expected_set):
        parts = []
        if missing:
            parts.append("missing " + ", ".join(str(day) for day in missing))
        if unexpected:
            parts.append("unexpected " + ", ".join(str(day) for day in unexpected))
        if duplicates:
            parts.append("duplicate " + ", ".join(str(day) for day in duplicates))
        if len(expected) != len(expected_set):
            parts.append("expected date list contains duplicates")
        raise ValueError(f"{sensor} daily coverage is incomplete: {'; '.join(parts)}")


def block_count_arrays(
    eligible: np.ndarray,
    valid: np.ndarray,
    detected: np.ndarray,
    block_size: int = 10,
) -> dict[str, np.ndarray]:
    """Sum cell-day count arrays into fixed native-grid blocks."""
    eligible = np.asarray(eligible)
    valid = np.asarray(valid)
    detected = np.asarray(detected)
    if eligible.shape != valid.shape or eligible.shape != detected.shape:
        raise ValueError("eligible, valid, and detected arrays must have identical shapes")
    if block_size <= 0 or eligible.ndim != 2:
        raise ValueError("block_size must be positive and inputs must be two-dimensional")
    rows, cols = eligible.shape
    if rows % block_size or cols % block_size:
        raise ValueError("raster dimensions must be divisible by block_size")

    def aggregate(values: np.ndarray) -> np.ndarray:
        return values.reshape(rows // block_size, block_size, cols // block_size, block_size).sum(axis=(1, 3))

    return {
        "eligible": aggregate(eligible),
        "valid": aggregate(valid),
        "detected": aggregate(detected),
    }


def modis_grid_coordinates(filepath: str | Path, shape: tuple[int, int]) -> tuple[np.ndarray, np.ndarray]:
    """Return MYD14A1 pixel centers from the provider's outer tile bounds."""
    from pyhdf.SD import SD, SDC

    handle = SD(str(filepath), SDC.READ)
    try:
        metadata = handle.attributes()["StructMetadata.0"]
    finally:
        handle.end()
    if isinstance(metadata, bytes):
        metadata = metadata.decode("utf-8", errors="replace")
    upper = re.search(r"UpperLeftPointMtrs=\(([-+0-9.eE]+),([-+0-9.eE]+)\)", metadata)
    lower = re.search(r"LowerRightMtrs=\(([-+0-9.eE]+),([-+0-9.eE]+)\)", metadata)
    if not upper or not lower:
        raise ValueError(f"{filepath} has no parseable sinusoidal tile bounds")
    rows, cols = shape
    ulx, uly = map(float, upper.groups())
    lrx, lry = map(float, lower.groups())
    pixel_width = (lrx - ulx) / cols
    pixel_height = (uly - lry) / rows
    return (
        ulx + (np.arange(cols, dtype=float) + 0.5) * pixel_width,
        uly - (np.arange(rows, dtype=float) + 0.5) * pixel_height,
    )


def viirs_grid_coordinates(filepath: str | Path) -> tuple[np.ndarray, np.ndarray]:
    """Read the VNP14A1 native sinusoidal XDim/YDim coordinates."""
    import h5py

    with h5py.File(str(filepath), "r") as handle:
        group = handle[VIIRS_GRID_PATH]
        x_edges = np.asarray(group["XDim"][:], dtype=float)
        y_edges = np.asarray(group["YDim"][:], dtype=float)
        x_step = float(np.median(np.diff(x_edges)))
        y_step = float(np.median(np.diff(y_edges)))
        return x_edges + x_step / 2, y_edges + y_step / 2


def assert_same_grid(
    reference_x: np.ndarray,
    reference_y: np.ndarray,
    candidate_x: np.ndarray,
    candidate_y: np.ndarray,
    tolerance_m: float = 2.0,
) -> None:
    """Reject shape, origin, or pixel-spacing mismatches across tile products."""
    reference_x = np.asarray(reference_x)
    reference_y = np.asarray(reference_y)
    candidate_x = np.asarray(candidate_x)
    candidate_y = np.asarray(candidate_y)
    if reference_x.shape != candidate_x.shape or reference_y.shape != candidate_y.shape:
        raise ValueError("paired product coordinate dimensions differ")
    differences = [
        float(np.max(np.abs(reference_x - candidate_x))),
        float(np.max(np.abs(reference_y - candidate_y))),
    ]
    if any(difference > tolerance_m for difference in differences):
        raise ValueError(f"paired product grids differ by up to {max(differences):.3f} m")


def read_modis_planes(filepath: str | Path) -> tuple[np.ndarray, np.ndarray]:
    """Read the daily MYD14A1 FireMask and QA stacks."""
    from pyhdf.SD import SD, SDC

    handle = SD(str(filepath), SDC.READ)
    try:
        return handle.select(MODIS_FIREMASK_PATH)[:], handle.select(MODIS_QA_PATH)[:]
    finally:
        handle.end()


def read_viirs_plane(filepath: str | Path) -> tuple[np.ndarray, np.ndarray]:
    """Read the VNP14A1 FireMask and QA layers."""
    import h5py

    with h5py.File(str(filepath), "r") as handle:
        return (
            handle[f"{VIIRS_DATA_PATH}/FireMask"][:],
            handle[f"{VIIRS_DATA_PATH}/QA"][:],
        )
