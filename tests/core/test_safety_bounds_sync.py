import pytest
from config.system_config import SystemConfig
from core.state_bounds import SAFETY_BOUNDS

def test_safety_bounds_sync():
    config = SystemConfig()
    
    assert config.max_temp_electrode == SAFETY_BOUNDS["T_core"]["max"], "T_core limit silently diverged!"
    assert abs((config.max_pressure_vessel * 0.90) - SAFETY_BOUNDS["p_vessel"]["max"]) < 1e-6, "p_vessel limit silently diverged!"
    assert abs((config.max_rpm * 2.0 * 3.141592653589793 / 60.0) - SAFETY_BOUNDS["omega"]["max"]) < 1e-6, "omega limit silently diverged!"
