#!/usr/bin/env python3
"""Legacy diagnostic: monthly FireMask inventory over the full h26v06 tile.

Counts use the same QA-land and nominal/high-confidence policy as the science
pipeline (``fireseason.decoder``), but pixels are not clipped to a candidate
region. The output is not a science artifact and must not be used for
calibration or comparison. The app publisher is
``pipeline/build_research_bundle.py``.

``--offline`` reads granules already stored under ``data/timeseries/``. Without
it, ``earthaccess`` searches and downloads granules using ~/.netrc Earthdata
credentials. The plot needs matplotlib. Neither package is in the science lock.
"""

import argparse
import csv
import json
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "pipeline"))

from fireseason.decoder import decode_modis_granule, decode_viirs_granule, parse_granule_date  # noqa: E402

# Fixed bounding box for tile h26v06 (NE India - Myanmar / Chattogram region)
BBOX = (93.0, 23.0, 96.0, 26.5)
MODIS_SHORT_NAME = "MYD14A1"
MODIS_VERSION = "061"
VIIRS_SHORT_NAME = "VNP14A1"
VIIRS_VERSION = "002"

DATA_DIR = ROOT / "data" / "timeseries"
MODIS_DIR = DATA_DIR / "modis"
VIIRS_DIR = DATA_DIR / "viirs"
OUTPUT_DIR = ROOT / "output" / "timeseries"

# Both products use the 1200 x 1200 h26v06 sinusoidal grid; the whole tile is the "AOI".
FULL_TILE = np.ones((1200, 1200), dtype=bool)
ANALYSIS_STATUS = "legacy_full_tile_not_for_comparison"
SPATIAL_SCOPE = "entire h26v06 tile; requested bounding box was used only for granule search"
QUALITY_POLICY = "firemask-qa-land-highnominal-v1 (same as science pipeline); no AOI clipping"


def ensure_dirs():
    MODIS_DIR.mkdir(parents=True, exist_ok=True)
    VIIRS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def find_granules(short_name, version, directory, month_start, month_end, offline, max_granules):
    """Return local granule paths that can hold days in [month_start, month_end)."""
    if offline:
        # MYD14A1 files hold eight daily planes, so one may start up to 7 days before the month.
        files = [
            path for path in sorted(directory.glob(f"{short_name}.A*"))
            if month_start - timedelta(days=7) <= parse_granule_date(path.name) < month_end
        ]
        return files[:max_granules] if max_granules else files

    import earthaccess

    results = earthaccess.search_data(
        short_name=short_name,
        version=version,
        temporal=(month_start.isoformat(), (month_end - timedelta(days=1)).isoformat()),
        bounding_box=BBOX,
    )
    print(f"Found {len(results)} {short_name} granules")
    if max_granules:
        results = results[:max_granules]
    return earthaccess.download(results, str(directory))


def count_month(files, decode, month_start, month_end, label):
    totals = {"granules": len(files), "days": 0, "detected": 0, "valid": 0}
    for path in files:
        stats = decode(path, month_start, month_end, FULL_TILE)
        if not stats["success"]:
            print(f"Error decoding {label} {path}: {stats.get('error')}")
            continue
        totals["days"] += stats["included_days"]
        totals["detected"] += stats["detected"]
        totals["valid"] += stats["valid_land"]
    return totals


def process_month(year: int, month: int, offline: bool, max_granules: int = None):
    """Count one year-month for both products; abstain when a day is missing."""
    month_start = date(year, month, 1)
    month_end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    expected_days = (month_end - month_start).days

    print("\n==========================================")
    print(f"Processing {year}-{month:02d} ({month_start} to {month_end - timedelta(days=1)})")
    print("==========================================")

    modis_files = find_granules(MODIS_SHORT_NAME, MODIS_VERSION, MODIS_DIR, month_start, month_end, offline, max_granules)
    viirs_files = find_granules(VIIRS_SHORT_NAME, VIIRS_VERSION, VIIRS_DIR, month_start, month_end, offline, max_granules)
    modis = count_month(modis_files, decode_modis_granule, month_start, month_end, "MODIS")
    viirs = count_month(viirs_files, decode_viirs_granule, month_start, month_end, "VIIRS")

    def rate(totals):
        # Fail closed: a month missing any calendar day has no rate.
        if totals["valid"] > 0 and totals["days"] == expected_days:
            return 1000 * totals["detected"] / totals["valid"]
        return None

    modis_rate, viirs_rate = rate(modis), rate(viirs)
    ratio = viirs_rate / modis_rate if modis_rate and viirs_rate else None

    result = {
        "year": year,
        "month": month,
        "period": f"{year:04d}-{month:02d}",
        "analysis_status": ANALYSIS_STATUS,
        "spatial_scope": SPATIAL_SCOPE,
        "quality_policy": QUALITY_POLICY,
        "modis_granules": modis["granules"],
        "modis_days_counted": modis["days"],
        "modis_coverage_complete": modis["days"] == expected_days,
        "modis_detected": modis["detected"],
        "modis_valid_land": modis["valid"],
        "modis_rate_per_1000": round(modis_rate, 4) if modis_rate is not None else None,
        "viirs_granules": viirs["granules"],
        "viirs_days_counted": viirs["days"],
        "viirs_coverage_complete": viirs["days"] == expected_days,
        "viirs_detected": viirs["detected"],
        "viirs_valid_land": viirs["valid"],
        "viirs_rate_per_1000": round(viirs_rate, 4) if viirs_rate is not None else None,
        "viirs_to_modis_ratio": round(ratio, 4) if ratio is not None else None,
    }

    print(f"Summary for {year}-{month:02d}:")
    print(f"  MODIS ({modis['days']}/{expected_days} days): Rate={result['modis_rate_per_1000']} (Det={modis['detected']}, Valid={modis['valid']})")
    print(f"  VIIRS ({viirs['days']}/{expected_days} days): Rate={result['viirs_rate_per_1000']} (Det={viirs['detected']}, Valid={viirs['valid']})")
    print(f"  VIIRS/MODIS Ratio: {result['viirs_to_modis_ratio']}")
    return result


def save_results(results: list[dict], json_path: Path, csv_path: Path):
    with open(json_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(results, f, indent=2)
        f.write("\n")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(results)


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
    ax1.set_title("LEGACY FULL-TILE MASK COUNTS · NOT A COMPARATIVE RESULT")
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
    ax2.set_title("Exploratory ratio only · pipeline QA policy, but no AOI clipping or release evaluation")
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend()

    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_plot, dpi=200)
    plt.close()
    print(f"\nPlot saved to: {output_plot}")


def main():
    parser = argparse.ArgumentParser(description="Legacy full-tile FireMask inventory (not a science result)")
    parser.add_argument(
        "--allow-legacy-diagnostic",
        action="store_true",
        help="Confirm that this is a full-tile diagnostic and must not be compared or released.",
    )
    parser.add_argument("--start-year", type=int, default=2013, help="Start year (default: 2013)")
    parser.add_argument("--end-year", type=int, default=2024, help="End year (default: 2024)")
    parser.add_argument("--months", type=int, nargs="+", default=[3], help="Months to sample (e.g. 3 for March peak fire season)")
    parser.add_argument("--max-granules", type=int, default=None, help="Limit granules per month for quick testing")
    parser.add_argument("--force-refresh", action="store_true", help="Ignore cached JSON summary and recompute")
    parser.add_argument("--offline", action="store_true", help="Use granules already in data/timeseries/; no Earthdata login")
    args = parser.parse_args()
    if not args.allow_legacy_diagnostic:
        parser.error("This legacy tool is not suitable for comparison; pass --allow-legacy-diagnostic only for exploratory inventory. Use pipeline/build_research_bundle.py to rebuild the validated raster sample.")

    ensure_dirs()

    if not args.offline:
        import earthaccess

        print("Authenticating with Earthdata...")
        if not earthaccess.login(strategy="netrc").authenticated:
            print("ERROR: Failed to authenticate via .netrc. Please check ~/.netrc credentials.")
            sys.exit(1)
        print("Authentication successful.")

    csv_path = OUTPUT_DIR / "timeseries_results.csv"
    json_path = OUTPUT_DIR / "timeseries_results.json"
    plot_path = OUTPUT_DIR / "timeseries_ratio.png"

    all_results = []
    if json_path.exists() and not args.force_refresh:
        cached = json.loads(json_path.read_text(encoding="utf-8"))
        # Records counted under another quality policy are recomputed, never relabelled.
        all_results = [record for record in cached if record.get("quality_policy") == QUALITY_POLICY]
        print(f"Loaded {len(all_results)} cached records; {len(cached) - len(all_results)} stale-policy records will be recomputed")

    existing_periods = {r["period"] for r in all_results}

    for year in range(args.start_year, args.end_year + 1):
        for month in args.months:
            period_key = f"{year:04d}-{month:02d}"
            if period_key in existing_periods:
                print(f"Skipping {period_key} (already processed)")
                continue

            all_results.append(process_month(year, month, args.offline, max_granules=args.max_granules))
            save_results(all_results, json_path, csv_path)
            if not args.offline:
                time.sleep(0.5)

    all_results.sort(key=lambda x: x["period"])
    if all_results:
        save_results(all_results, json_path, csv_path)
        plot_timeseries(all_results, plot_path)

    print("\n==========================================")
    print("Completed! Output saved to:")
    print(f"  CSV:  {csv_path}")
    print(f"  JSON: {json_path}")
    print(f"  Plot: {plot_path}")
    print("==========================================")


if __name__ == "__main__":
    main()
