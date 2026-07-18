import pytest
from config.system_config import SystemConfig
from physics.scavengers.spark_loop import SparkLoop
from physics.scavengers.thermoelectric import Thermoelectric
from physics.scavengers.piezo_tribo import PiezoTribo
from physics.scavengers.magnetic_leakage import MagneticLeakage
from physics.scavengers.hydraulic_regen import HydraulicRegen
from physics.base import ControlVector
from core.state_vector import StateVector

@pytest.fixture
def state_control_config():
    config = SystemConfig()
    state = StateVector(theta=0.0, omega=0.0, T_core=300.0, p_vessel=1e5, V_accum=0.1)
    control = ControlVector()
    return state, control, config

@pytest.mark.parametrize("scavenger_cls", [
    SparkLoop, Thermoelectric, PiezoTribo, MagneticLeakage, HydraulicRegen
])
def test_kill_disables_module(scavenger_cls, state_control_config):
    state, control, config = state_control_config
    mod = scavenger_cls(config)
    mod.kill("Testing kill")
    
    contrib = mod.compute(state, control, config)
    assert contrib.power_ledger.power_generated_w == 0.0
    assert contrib.power_ledger.power_dissipated_w == 0.0

@pytest.mark.parametrize("scavenger_cls, expected_positive", [
    (SparkLoop, False),
    (Thermoelectric, True),
    (PiezoTribo, True),
    (MagneticLeakage, True),
    (HydraulicRegen, True),
])
def test_positive_net_contribution(scavenger_cls, expected_positive, state_control_config):
    state, control, config = state_control_config
    mod = scavenger_cls(config)
    mod.compute(state, control, config)
    
    net = mod.net_contribution()
    if expected_positive:
        assert net > 0.0
    else:
        assert net < 0.0

@pytest.mark.parametrize("scavenger_cls", [
    SparkLoop, Thermoelectric, PiezoTribo, MagneticLeakage, HydraulicRegen
])
def test_ab_test_quantifies_benefit(scavenger_cls, state_control_config):
    state, control, config = state_control_config
    mod = scavenger_cls(config)
    # Just passing dummy twin since it's mocked anyway
    with_w, without_w = mod.ab_test(None, 0.1)
    assert with_w != without_w or (with_w == 0.0 and without_w == 0.0) # wait, spark loop returns 1000, 1200
    if scavenger_cls == Thermoelectric:
        assert with_w == 15.0 and without_w == 0.0
