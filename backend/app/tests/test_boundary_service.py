import os
import tempfile

_tmp = tempfile.mkdtemp()
os.environ["DATA_DIR"] = _tmp

from app.db import connect  # noqa: E402
from app.seed import init_db  # noqa: E402
from app.services.billing_service import BillingService  # noqa: E402

init_db()


def _run_count(conn) -> int:
    return conn.execute("SELECT COUNT(*) c FROM calc_runs").fetchone()["c"]


def test_bill_uses_and_reports_current_mode():
    with BillingService() as svc:
        assert svc.settings_map().get("boundary_mode") == "right"
        r = svc.run_bill(180, False, None, persist=False)
        assert r["boundary_mode"] == "right"
        assert r["total"] == 93.60

        svc.set_boundary_mode("left")
        r2 = svc.run_bill(180, False, None, persist=False)
        assert r2["boundary_mode"] == "left"
        assert r2["total"] == 93.70
        # 档价表数值未被模式切换改动
        assert [(t["up_to"], t["price"]) for t in svc.list_tiers()] == [
            (180.0, 0.52),
            (260.0, 0.62),
            (None, 0.82),
        ]

    # 复位，避免用例间状态串扰
    with BillingService() as svc:
        svc.set_boundary_mode("right")


def test_boundary_compare_returns_both_modes_and_does_not_persist():
    conn = connect()
    before = _run_count(conn)
    conn.close()

    with BillingService() as svc:
        out = svc.run_boundary_compare(180)
        assert set(out["modes"]) == {"left", "right"}
        assert out["current_mode"] == "right"
        assert out["modes"]["right"]["total"] == 93.60
        assert out["modes"]["left"]["total"] == 93.70
        assert out["modes"]["left"]["boundary_mode"] == "left"

    conn = connect()
    after = _run_count(conn)
    conn.close()
    assert after == before


def test_boundary_compare_modes_agree_away_from_boundary():
    with BillingService() as svc:
        out = svc.run_boundary_compare(200)
        assert out["modes"]["left"]["segments"] == out["modes"]["right"]["segments"]
        assert out["modes"]["left"]["total"] == out["modes"]["right"]["total"]


def test_invalid_mode_rejected():
    import pytest

    with BillingService() as svc, pytest.raises(ValueError):
        svc.set_boundary_mode("middle")
