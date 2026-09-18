"""Progressive tier electricity: each kWh charged at its band price.

boundary_mode 控制电量恰好等于某档 up_to 时边界电量的归属：
- "right"（含右端，默认）：区间 (prev, up]，边界电量留在本档；
- "left"（含左端）：区间 [prev, up)，边界的 1 个最小计费单位（1 kWh）归下一档。
只影响分段归属，不修改档价表数值本身。
"""

from app.engines.helpers import kwh_qty, money

BOUNDARY_MODES = ("left", "right")
# 边界电量的最小计费单位：1 kWh
BOUNDARY_UNIT = 1.0
_TOL = 1e-9


def calc_bill(kwh: float, tiers: list[dict], peak_factor: float = 1.0, boundary_mode: str = "right") -> dict:
    """tiers: [{up_to, price}] last up_to may be None for open end."""
    if boundary_mode not in BOUNDARY_MODES:
        raise ValueError(f"boundary_mode must be one of {BOUNDARY_MODES}")
    remain = float(kwh)
    if remain < 0:
        raise ValueError("kwh must be non-negative")
    segments = []
    total = 0.0
    pos = 0.0
    pf = float(peak_factor)
    last_idx = len(tiers) - 1
    for i, t in enumerate(tiers):
        up = t.get("up_to")
        price = float(t["price"]) * pf
        if up is None:
            qty = remain
        else:
            span = float(up) - pos
            qty = min(remain, max(0.0, span))
            if (
                boundary_mode == "left"
                and i < last_idx
                and span > BOUNDARY_UNIT
                and abs(remain - span) <= _TOL
            ):
                # 含左端：电量恰好到达档界，边界单位电量归下一档
                qty = span - BOUNDARY_UNIT
        if qty > _TOL:
            amount = money(qty * price)
            segments.append(
                {
                    "from_kwh": kwh_qty(pos),
                    "to_kwh": kwh_qty(pos + qty),
                    "qty": kwh_qty(qty),
                    "price": round(price, 4),
                    "amount": amount,
                }
            )
            total += amount
            remain -= qty
            pos += qty
        if remain <= _TOL:
            break
    return {
        "kwh": kwh_qty(kwh),
        "peak_factor": pf,
        "boundary_mode": boundary_mode,
        "total": money(total),
        "segments": segments,
    }
