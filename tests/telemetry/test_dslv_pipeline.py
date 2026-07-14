import pytest
import os
import zmq
from telemetry.dslv_zpdi_pipeline import DSLVZPDIPipeline
from core.state_vector import StateVector
from config.sites import SITES

def test_schema_valid(tmp_path):
    site = SITES["penrose_co"]
    pipeline = DSLVZPDIPipeline(site["node_id"], site)
    state = StateVector(theta=0.0, omega=100.0, T_core=3000.0, p_vessel=1.5e5, V_accum=0.5)
    telemetry = {"safety": "STEADY_OPERATION", "exergy": {"eta_ii": 0.36}}
    
    h5_path = os.path.join(tmp_path, "test.h5")
    pipeline.write_twin_snapshot(state, telemetry, h5_path)
    assert pipeline.validate_schema(h5_path)

def test_node_id_in_path(tmp_path):
    site = SITES["albuquerque_nm"]
    pipeline = DSLVZPDIPipeline(site["node_id"], site)
    state = StateVector(theta=0.0, omega=100.0, T_core=3000.0, p_vessel=1.5e5, V_accum=0.5)
    telemetry = {}
    
    h5_path = os.path.join(tmp_path, "test.h5")
    pipeline.write_twin_snapshot(state, telemetry, h5_path)
    import h5py
    with h5py.File(h5_path, "r") as f:
        assert "node_beta" in f

def test_zmq_stream():
    # Simple check that we can create socket without error
    site = SITES["penrose_co"]
    pipeline = DSLVZPDIPipeline(site["node_id"], site)
    assert pipeline.socket.type == zmq.PUB
