import pytest
import os
import numpy as np
from digital_twin.cfd_bridge import OpenFOAMBridge
from core.state_vector import StateVector
from config.system_config import SystemConfig

def test_boundary_write(tmp_path):
    config = SystemConfig()
    bridge = OpenFOAMBridge(str(tmp_path), config)
    state = StateVector(theta=0.0, omega=100.0, T_core=2000.0, p_vessel=1.5e5, V_accum=0.5, segments_current=np.array([500.0]*8))
    bridge.write_boundary_conditions(state)
    
    with open(os.path.join(tmp_path, "0", "U")) as f:
        assert "100.0" in f.read()

def test_field_read():
    config = SystemConfig()
    bridge = OpenFOAMBridge("dummy", config)
    fields = bridge.read_fields()
    assert fields["U"].shape == (64, 16)

def test_extract_averages():
    config = SystemConfig()
    bridge = OpenFOAMBridge("dummy", config)
    avgs = bridge.extract_section_averages()
    assert avgs["U"] == 1.0

def test_close_cleans_process():
    config = SystemConfig()
    bridge = OpenFOAMBridge("dummy", config)
    bridge.close() # Shouldn't error
