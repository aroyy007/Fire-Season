"""Exploratory transfer diagnostics; this module does not release calibration."""

from __future__ import annotations

from typing import Any


def fit_and_evaluate_transfer(timeseries_records: list[dict[str, Any]]) -> dict[str, Any]:
    """Return a ratio candidate and holdout diagnostics, always marked experimental.

    Monthly ratios alone do not establish paired pixel support, geographic
    transfer, or calibrated prediction intervals. The result is intentionally
    not consumable as a Calibration Release by the Analysis Artifact contract.
    """
    train = [
        record for record in timeseries_records
        if record.get("year", 9999) <= 2020 and record.get("viirs_to_modis_ratio") is not None
    ]
    test = [
        record for record in timeseries_records
        if record.get("year", 0) >= 2021 and record.get("viirs_to_modis_ratio") is not None
    ]
    if not train or not test:
        return {
            "status": "insufficient_data",
            "release_eligible": False,
            "candidate": None,
            "calibration": None,
            "reason": "Training and held-out ratio records are both required for exploratory diagnostics.",
        }

    ratios = [float(record["viirs_to_modis_ratio"]) for record in train]
    mean_ratio = sum(ratios) / len(ratios)
    if mean_ratio <= 0:
        return {
            "status": "insufficient_data",
            "release_eligible": False,
            "candidate": None,
            "calibration": None,
            "reason": "Training ratios do not support a positive transfer multiplier.",
        }

    multiplier = 1.0 / mean_ratio
    identity_errors = []
    candidate_errors = []
    for record in test:
        viirs = record.get("viirs_rate_per_1000")
        modis = record.get("modis_rate_per_1000")
        if viirs is None or modis is None:
            continue
        viirs = float(viirs)
        modis = float(modis)
        identity_errors.append(abs(viirs - modis))
        candidate_errors.append(abs(viirs * multiplier - modis))
    if not identity_errors:
        return {
            "status": "insufficient_data",
            "release_eligible": False,
            "candidate": None,
            "calibration": None,
            "reason": "No complete held-out sensor pairs are available.",
        }

    identity_mae = sum(identity_errors) / len(identity_errors)
    candidate_mae = sum(candidate_errors) / len(candidate_errors)
    improvement_pct = None if identity_mae == 0 else round((1 - candidate_mae / identity_mae) * 100, 1)
    return {
        "status": "experimental",
        "release_eligible": False,
        "candidate": {
            "model_type": "exploratory_mean_ratio",
            "training_record_count": len(train),
            "held_out_record_count": len(identity_errors),
            "mean_training_ratio": round(mean_ratio, 4),
            "candidate_multiplier": round(multiplier, 4),
            "identity_mae_per_1000": round(identity_mae, 4),
            "candidate_mae_per_1000": round(candidate_mae, 4),
            "improvement_pct_vs_identity": improvement_pct,
        },
        "calibration": None,
        "reason": (
            "Monthly full-tile ratios are exploratory only; paired-mask, independent geographic transfer, "
            "baseline-skill, and interval-coverage gates have not been established."
        ),
    }
