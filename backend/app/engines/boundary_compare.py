"""Boundary-mode comparison: same probe kWh billed under both inclusive modes."""

from app.engines.tier_progressive import calc_bill


def compare_boundary_modes(kwh: float, tiers: list[dict], peak_factor: float = 1.0) -> dict:
    """只读对比：同一探针电量在含左端/含右端两种模式下的分段与合计。"""
    left = calc_bill(kwh, tiers, peak_factor, "left")
    right = calc_bill(kwh, tiers, peak_factor, "right")
    return {
        "kwh": right["kwh"],
        "peak_factor": right["peak_factor"],
        "left": left,
        "right": right,
        "delta": round(left["total"] - right["total"], 2),
    }
