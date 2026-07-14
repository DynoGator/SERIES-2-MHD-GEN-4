import os
import h5py
from telemetry.dslv_zpdi_pipeline import DSLVZPDIPipeline
from core.state_vector import StateVector
from config.sites import SITES


def test_production_group_written(tmp_path):
    site = SITES["penrose_co"]
    pipeline = DSLVZPDIPipeline(site["node_id"], site)
    state = StateVector(theta=0.0, omega=100.0, T_core=3000.0, p_vessel=1.5e5, V_accum=0.5)
    telemetry = {
        "safety": "STEADY_OPERATION",
        "exergy": {"eta_ii": 0.36},
        "production": {
            "production_unit_id": "2MHD-PRA-0001",
            "batch_number": "BATCH-2026-07",
            "compliance_status": {"fcc": True, "ce": False, "ul": False},
            "cost_to_date_usd": 12345.67,
        },
    }
    h5_path = os.path.join(tmp_path, "prod.h5")
    pipeline.write_twin_snapshot(state, telemetry, h5_path)

    with h5py.File(h5_path, "r") as f:
        grp = f[f"node_{site['node_id']}/production"]
        assert grp.attrs["production_unit_id"] == "2MHD-PRA-0001"
        assert grp.attrs["batch_number"] == "BATCH-2026-07"
        assert bool(grp["compliance_fcc"][()]) is True
        assert bool(grp["compliance_ce"][()]) is False
        assert abs(float(grp["cost_to_date_usd"][()]) - 12345.67) < 1e-3


def test_production_defaults_when_absent(tmp_path):
    site = SITES["penrose_co"]
    pipeline = DSLVZPDIPipeline(site["node_id"], site)
    state = StateVector(theta=0.0, omega=100.0, T_core=3000.0, p_vessel=1.5e5, V_accum=0.5)
    h5_path = os.path.join(tmp_path, "prod_default.h5")
    pipeline.write_twin_snapshot(state, {}, h5_path)
    with h5py.File(h5_path, "r") as f:
        grp = f[f"node_{site['node_id']}/production"]
        assert grp.attrs["production_unit_id"] == "UNSET"
        assert float(grp["cost_to_date_usd"][()]) == 0.0
