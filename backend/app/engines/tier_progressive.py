"""Progressive tier electricity: each kWh charged at its band price.

Boundary mode decides which band owns the exact boundary point when the
metered usage equals a tier's ``up_to``:

* ``right`` (default): band interval ``(prev, up_to]`` — the boundary kWh
  stays in the current (lower) band. Backwards-compatible behaviour.
* ``left``: band interval ``[prev, up_to)`` — when usage lands exactly on
  ``up_to`` the last metered unit (1 kWh, the meter's whole-kWh
  granularity) is billed by the next (higher) band.

Only a usage amount exactly equal to an ``up_to`` boundary is affected;
any other amount bills identically under both modes, and tier prices are
never modified by the mode.
"""

from app.engines.helpers import kwh_qty, money

BOUNDARY_LEFT = "left"
BOUNDARY_RIGHT = "right"
BOUNDARY_MODES = (BOUNDARY_LEFT, BOUNDARY_RIGHT)
BOUNDARY_EPS = 1e-9
# Meters settle in whole kWh; under "left" mode this one unit crosses the line.
BOUNDARY_UNIT = 1.0


def calc_bill(
    kwh: float,
    tiers: list[dict],
    peak_factor: float = 1.0,
    boundary_mode: str = BOUNDARY_RIGHT,
) -> dict:
    """tiers: [{up_to, price}] last up_to may be None for open end."""
    if boundary_mode not in BOUNDARY_MODES:
        raise ValueError(f"invalid boundary_mode: {boundary_mode}")
    remain = float(kwh)
    if remain < 0:
        raise ValueError("kwh must be non-negative")
    segments = []
    total = 0.0
    prev = 0.0
    pf = float(peak_factor)
    for t in tiers:
        up = t.get("up_to")
        price = float(t["price"]) * pf
        eff_up = None
        if up is not None:
            up = float(up)
            eff_up = up
            at_boundary = abs(float(kwh) - up) <= BOUNDARY_EPS
            if (
                boundary_mode == BOUNDARY_LEFT
                and at_boundary
                and up - BOUNDARY_UNIT > prev
            ):
                # Boundary belongs to the next band: shrink this band by one
                # metered unit so the higher band owns the boundary kWh.
                eff_up = up - BOUNDARY_UNIT
        if up is None:
            qty = remain
        else:
            qty = min(remain, max(0.0, eff_up - prev))
        if qty > 1e-9:
            amount = money(qty * price)
            segments.append(
                {
                    "from_kwh": prev,
                    "to_kwh": prev + qty,
                    "qty": kwh_qty(qty),
                    "price": round(price, 4),
                    "amount": amount,
                }
            )
            total += amount
            remain -= qty
        if up is not None:
            # Next band starts where this one actually ended.
            prev = eff_up
        if remain <= 1e-9:
            break
    return {
        "kwh": kwh_qty(kwh),
        "peak_factor": pf,
        "boundary_mode": boundary_mode,
        "total": money(total),
        "segments": segments,
    }
