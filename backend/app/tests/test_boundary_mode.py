import pytest

from app.engines.peak_compare import compare_plain_vs_peak
from app.engines.tier_progressive import (
    BOUNDARY_LEFT,
    BOUNDARY_RIGHT,
    calc_bill,
)

TIERS = [
    {"up_to": 180, "price": 0.52},
    {"up_to": 260, "price": 0.62},
    {"up_to": None, "price": 0.82},
]


def test_boundary_right_keeps_whole_usage_in_lower_band():
    r = calc_bill(180, TIERS, 1.0, BOUNDARY_RIGHT)
    assert r["boundary_mode"] == "right"
    assert r["total"] == 93.60
    assert len(r["segments"]) == 1
    assert r["segments"][0]["from_kwh"] == 0
    assert r["segments"][0]["to_kwh"] == 180


def test_boundary_left_pushes_last_unit_to_higher_band():
    r = calc_bill(180, TIERS, 1.0, BOUNDARY_LEFT)
    assert r["boundary_mode"] == "left"
    assert r["total"] == 93.70
    assert [(s["from_kwh"], s["to_kwh"], s["qty"]) for s in r["segments"]] == [
        (0, 179, 179),
        (179, 180, 1),
    ]


def test_boundary_left_second_boundary_reaches_open_band():
    right = calc_bill(260, TIERS, 1.0, BOUNDARY_RIGHT)
    left = calc_bill(260, TIERS, 1.0, BOUNDARY_LEFT)
    assert right["total"] == 143.20
    assert left["total"] == 143.40
    assert len(left["segments"]) == 3
    assert left["segments"][-1]["qty"] == 1
    assert left["segments"][-1]["price"] == 0.82


def test_non_boundary_usage_identical_in_both_modes():
    for kwh in (0, 120, 200, 260.5, 400):
        right = calc_bill(kwh, TIERS, 1.0, BOUNDARY_RIGHT)
        left = calc_bill(kwh, TIERS, 1.0, BOUNDARY_LEFT)
        assert right["total"] == left["total"], kwh
        assert right["segments"] == left["segments"], kwh


def test_boundary_left_with_peak_factor():
    r = calc_bill(180, TIERS, 1.2, BOUNDARY_LEFT)
    assert r["peak_factor"] == 1.2
    assert r["total"] == 112.44
    assert r["segments"][0]["price"] == 0.624
    assert r["segments"][1]["price"] == 0.744


def test_compare_plain_vs_peak_carries_mode():
    c = compare_plain_vs_peak(180, TIERS, 1.2, BOUNDARY_LEFT)
    assert c["boundary_mode"] == "left"
    assert c["plain_total"] == 93.70
    assert c["peak_total"] == 112.44


def test_invalid_boundary_mode_raises():
    with pytest.raises(ValueError):
        calc_bill(180, TIERS, 1.0, "middle")
