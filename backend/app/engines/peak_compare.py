from app.engines.tier_progressive import calc_bill


def compare_plain_vs_peak(kwh: float, tiers: list[dict], peak_factor: float, boundary_mode: str = "right") -> dict:
    plain = calc_bill(kwh, tiers, 1.0, boundary_mode)
    peak = calc_bill(kwh, tiers, peak_factor, boundary_mode)
    delta = round(peak["total"] - plain["total"], 2)
    return {
        "kwh": plain["kwh"],
        "boundary_mode": boundary_mode,
        "plain_total": plain["total"],
        "peak_total": peak["total"],
        "peak_factor": float(peak_factor),
        "delta": delta,
        "plain_segments": plain["segments"],
        "peak_segments": peak["segments"],
    }
