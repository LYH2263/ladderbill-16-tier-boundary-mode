import pytest

from app.engines.boundary_compare import compare_boundary_modes
from app.engines.peak_compare import compare_plain_vs_peak
from app.engines.tier_progressive import calc_bill

TIERS = [{"up_to": 180, "price": 0.52}, {"up_to": 260, "price": 0.62}, {"up_to": None, "price": 0.82}]


def test_tier_first_band_only():
    r = calc_bill(120, TIERS, 1.0)
    assert r["total"] == 62.40
    assert len(r["segments"]) == 1


def test_tier_three_bands():
    r = calc_bill(400, TIERS, 1.0)
    assert r["total"] == 258.00
    assert len(r["segments"]) == 3


def test_peak_factor_multiplies_prices():
    plain = calc_bill(400, TIERS, 1.0)
    peak = calc_bill(400, TIERS, 1.2)
    assert peak["total"] == 309.60
    assert peak["total"] > plain["total"]


def test_compare_delta():
    c = compare_plain_vs_peak(400, TIERS, 1.2)
    assert c["plain_total"] == 258.00
    assert c["peak_total"] == 309.60
    assert c["delta"] == 51.60


def test_negative_kwh_raises():
    with pytest.raises(ValueError):
        calc_bill(-1, TIERS, 1.0)


def test_default_boundary_mode_is_right():
    r = calc_bill(180, TIERS, 1.0)
    assert r["boundary_mode"] == "right"
    assert r["total"] == 93.60
    assert len(r["segments"]) == 1


def test_right_mode_boundary_stays_in_lower_band():
    r = calc_bill(180, TIERS, 1.0, "right")
    assert r["boundary_mode"] == "right"
    assert r["total"] == 93.60
    assert [(s["from_kwh"], s["to_kwh"]) for s in r["segments"]] == [(0.0, 180.0)]


def test_left_mode_boundary_moves_to_next_band():
    r = calc_bill(180, TIERS, 1.0, "left")
    assert r["boundary_mode"] == "left"
    assert r["total"] == 93.70
    assert [(s["from_kwh"], s["to_kwh"], s["price"]) for s in r["segments"]] == [
        (0.0, 179.0, 0.52),
        (179.0, 180.0, 0.62),
    ]


def test_left_mode_boundary_at_second_tier():
    r = calc_bill(260, TIERS, 1.0, "left")
    assert r["total"] == 143.40
    assert [(s["from_kwh"], s["to_kwh"]) for s in r["segments"]] == [
        (0.0, 180.0),
        (180.0, 259.0),
        (259.0, 260.0),
    ]
    assert calc_bill(260, TIERS, 1.0, "right")["total"] == 143.20


def test_non_boundary_kwh_same_in_both_modes():
    left = calc_bill(400, TIERS, 1.0, "left")
    right = calc_bill(400, TIERS, 1.0, "right")
    assert left["total"] == right["total"] == 258.00
    assert left["segments"] == right["segments"]


def test_invalid_boundary_mode_raises():
    with pytest.raises(ValueError):
        calc_bill(100, TIERS, 1.0, "middle")


def test_boundary_compare_returns_both_modes():
    c = compare_boundary_modes(180, TIERS)
    assert c["kwh"] == 180.0
    assert c["left"]["boundary_mode"] == "left"
    assert c["right"]["boundary_mode"] == "right"
    assert c["left"]["total"] == 93.70
    assert c["right"]["total"] == 93.60
    assert c["delta"] == 0.10
