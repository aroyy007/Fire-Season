#!/usr/bin/env python3
"""
build_timeseries.py: Download and aggregate MODIS (MYD14A1) and VIIRS (VNP14A1)
fire masks for tile h26v06 across 2013-2024 with exact daily plane boundary trimming.
"""

import os
import sys
import time
import argparse
import csv
import json
import re
from pathlib import Path
from datetime import datetime, date, timedelta
import numpy as np
import earthaccess
from pyhdf.SD import SD, SDC
import h5py
import matplotlib.pyplot as plt

# Fixed bounding box for tile h26v06 (NE India - Myanmar / Chattogram region)
BBOX = (93.0, 23.0, 96.0, 26.5)
MODIS_SHORT_NAME = "MYD14A1"
MODIS_VERSION = "061"
VIIRS_SHORT_NAME = "VNP14A1"
VIIRS_VERSION = "002"

DATA_DIR = Path("./data/timeseries")
MODIS_DIR = DATA_DIR / "modis"
VIIRS_DIR = DATA_DIR / "viirs"
OUTPUT_DIR = Path("./output/timeseries")


def ensure_dirs():
    MODIS_DIR.mkdir(parents=True, exist_ok=True)
    VIIRS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_granule_date(filename: str) -> date:
    """Extracts date from standard NASA granule filename A<YYYY><DOY>."""
    m = re.search(r"A(\d{4})(\d{3})", filename)
    if not m:
        raise ValueError(f"Could not parse date from filename: {filename}")
    year, doy = int(m.group(1)), int(m.group(2))
    return date(year, 1, 1) + timedelta(days=doy - 1)


def decode_modis_granule(filepath: str, month_start: date, month_end: date) -> dict:
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
        print(f"Error decoding MODIS {filepath}: {e}")
        return {
            "detected": 0,
            "valid_land": 0,
            "total_pixels": 0,
            "included_days": 0,
            "planes": 0,
            "success": False,
        }


def decode_viirs_granule(filepath: str, month_start: date, month_end: date) -> dict:
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
        print(f"Error decoding VIIRS {filepath}: {e}")
        return {
            "detected": 0,
            "valid_land": 0,
            "total_pixels": 0,
            "included_days": 0,
            "planes": 0,
            "success": False,
        }


def process_month(year: int, month: int, max_days: int = None):
    """Processes a single year-month for both MODIS and VIIRS with exact trimming."""
    month_start = date(year, month, 1)
    if month == 12:
        month_end = date(year + 1, 1, 1)
    else:
        month_end = date(year, month + 1, 1)

    start_date_str = month_start.isoformat()
    end_date_str = (month_end - timedelta(days=1)).isoformat()

    print(f"\n==========================================")
    print(f"Processing {year}-{month:02d} ({start_date_str} to {end_date_str})")
    print(f"==========================================")

    # 1. Search and download MODIS
    modis_query = earthaccess.search_data(
        short_name=MODIS_SHORT_NAME,
        version=MODIS_VERSION,
        temporal=(start_date_str, end_date_str),
        bounding_box=BBOX,
    )
    print(f"Found {len(modis_query)} MODIS granules")
    if max_days and len(modis_query) > max_days:
        modis_query = modis_query[:max_days]

    modis_detected = 0
    modis_valid_land = 0
    modis_total_pixels = 0
    modis_days_counted = 0
    modis_files = earthaccess.download(modis_query, str(MODIS_DIR))
    for f in modis_files:
        stats = decode_modis_granule(f, month_start, month_end)
        if stats["success"]:
            modis_detected += stats["detected"]
            modis_valid_land += stats["valid_land"]
            modis_total_pixels += stats["total_pixels"]
            modis_days_counted += stats["included_days"]

    # 2. Search and download VIIRS
    viirs_query = earthaccess.search_data(
        short_name=VIIRS_SHORT_NAME,
        version=VIIRS_VERSION,
        temporal=(start_date_str, end_date_str),
        bounding_box=BBOX,
    )
    print(f"Found {len(viirs_query)} VIIRS granules")
    if max_days and len(viirs_query) > max_days:
        viirs_query = viirs_query[:max_days]

    viirs_detected = 0
    viirs_valid_land = 0
    viirs_total_pixels = 0
    viirs_days_counted = 0
    viirs_files = earthaccess.download(viirs_query, str(VIIRS_DIR))
    for f in viirs_files:
        stats = decode_viirs_granule(f, month_start, month_end)
        if stats["success"]:
            viirs_detected += stats["detected"]
            viirs_valid_land += stats["valid_land"]
            viirs_total_pixels += stats["total_pixels"]
            viirs_days_counted += stats["included_days"]

    # Metrics calculation
    modis_rate = (modis_detected / modis_valid_land * 1000) if modis_valid_land > 0 else None
    viirs_rate = (viirs_detected / viirs_valid_land * 1000) if viirs_valid_land > 0 else None
    ratio = (viirs_rate / modis_rate) if (modis_rate and viirs_rate and modis_rate > 0) else None

    result = {
        "year": year,
        "month": month,
        "period": f"{year:04d}-{month:02d}",
        "modis_granules": len(modis_files),
        "modis_days_counted": modis_days_counted,
        "modis_detected": modis_detected,
        "modis_valid_land": modis_valid_land,
        "modis_rate_per_1000": round(modis_rate, 4) if modis_rate is not None else None,
        "viirs_granules": len(viirs_files),
        "viirs_days_counted": viirs_days_counted,
        "viirs_detected": viirs_detected,
        "viirs_valid_land": viirs_valid_land,
        "viirs_rate_per_1000": round(viirs_rate, 4) if viirs_rate is not None else None,
        "viirs_to_modis_ratio": round(ratio, 4) if ratio is not None else None,
    }

    print(f"Summary for {year}-{month:02d}:")
    print(f"  MODIS ({modis_days_counted} days): Rate={result['modis_rate_per_1000']} (Det={modis_detected}, Valid={modis_valid_land})")
    print(f"  VIIRS ({viirs_days_counted} days): Rate={result['viirs_rate_per_1000']} (Det={viirs_detected}, Valid={viirs_valid_land})")
    print(f"  VIIRS/MODIS Ratio: {result['viirs_to_modis_ratio']}")

    return result


def plot_timeseries(results: list[dict], output_plot: Path):
    """Plots the rates and ratio timeseries."""
    periods = [r["period"] for r in results]
    m_rates = [r["modis_rate_per_1000"] for r in results]
    v_rates = [r["viirs_rate_per_1000"] for r in results]
    ratios = [r["viirs_to_modis_ratio"] for r in results]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # Subplot 1: Detected Rates
    ax1.plot(periods, m_rates, marker="o", color="#2c6674", label="Aqua MODIS (MYD14A1)")
    ax1.plot(periods, v_rates, marker="s", color="#b94a2c", label="Suomi-NPP VIIRS (VNP14A1)")
    ax1.set_ylabel("Rate per 1,000 valid land cells")
    ax1.set_title("MODIS vs VIIRS Monthly Detection Rates (Tile h26v06)")
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend()

    # Subplot 2: VIIRS / MODIS Ratio
    valid_ratios = [(p, r) for p, r in zip(periods, ratios) if r is not None]
    if valid_ratios:
        px, rx = zip(*valid_ratios)
        ax2.plot(px, rx, marker="^", color="#4a7c59", label="VIIRS / MODIS Ratio")
        ax2.axhline(1.0, color="grey", linestyle=":", label="Parity (1.0)")
    ax2.set_ylabel("Sensor Ratio (VIIRS / MODIS)")
    ax2.set_xlabel("Time Period")
    ax2.set_title("Sensor Comparison Ratio (Evaluating Sensor Stability & Drift)")
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend()

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_plot, dpi=200)
    plt.close()
    print(f"\nPlot saved to: {output_plot}")


def main():
    parser = argparse.ArgumentParser(description="Build MODIS vs VIIRS Time Series")
    parser.add_argument("--start-year", type=int, default=2013, help="Start year (default: 2013)")
    parser.add_argument("--end-year", type=int, default=2024, help="End year (default: 2024)")
    parser.add_argument("--months", type=int, nargs="+", default=[3], help="Months to sample (e.g. 3 for March peak fire season)")
    parser.add_argument("--max-granules", type=int, default=None, help="Limit granules per month for quick testing")
    parser.add_argument("--force-refresh", action="store_true", help="Ignore cached JSON summary and recompute")
    args = parser.parse_args()

    ensure_dirs()

    print("Authenticating with Earthdata...")
    auth = earthaccess.login(strategy="netrc")
    if not auth.authenticated:
        print("ERROR: Failed to authenticate via .netrc. Please check ~/.netrc credentials.")
        sys.exit(1)
    print("Authentication successful.")

    csv_path = OUTPUT_DIR / "timeseries_results.csv"
    json_path = OUTPUT_DIR / "timeseries_results.json"
    plot_path = OUTPUT_DIR / "timeseries_ratio.png"

    all_results = []
    
    # Load existing results if any unless forced
    if json_path.exists() and not args.force_refresh:
        try:
            with open(json_path, "r") as f:
                all_results = json.load(f)
            print(f"Loaded {len(all_results)} existing records from {json_path}")
        except Exception:
            all_results = []

    existing_periods = {r["period"] for r in all_results}

    for year in range(args.start_year, args.end_year + 1):
        for month in args.months:
            period_key = f"{year:04d}-{month:02d}"
            if period_key in existing_periods:
                print(f"Skipping {period_key} (already processed)")
                continue

            res = process_month(year, month, max_days=args.max_granules)
            all_results.append(res)
            
            # Save incremental results
            with open(json_path, "w") as f:
                json.dump(all_results, f, indent=2)

            with open(csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=list(res.keys()))
                writer.writeheader()
                writer.writerows(all_results)

            time.sleep(0.5)

    # Sort results by period
    all_results.sort(key=lambda x: x["period"])

    if all_results:
        plot_timeseries(all_results, plot_path)

    print("\n==========================================")
    print(f"Completed! Output saved to:")
    print(f"  CSV:  {csv_path}")
    print(f"  JSON: {json_path}")
    print(f"  Plot: {plot_path}")
    print("==========================================")


if __name__ == "__main__":
    main()
