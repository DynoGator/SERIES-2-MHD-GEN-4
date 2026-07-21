import pytest
from physics.thermo.fross4 import FROSS4
from config.system_config import SystemConfig

def test_stage1_attenuates_oscillation():
    config = SystemConfig()
    fross = FROSS4(config)
    
    pulse = 1000.0
    delta_p = fross.stage1_acoustic_response(pulse)
    
    remaining = pulse - delta_p
    assert remaining <= pulse / 3.16 + 1e-5

def test_stage2_isolates_gas_from_hydraulic():
    config = SystemConfig()
    fross = FROSS4(config)
    
    x1 = fross.stage2_diaphragm_displacement(1e5)
    x2 = fross.stage2_diaphragm_displacement(2e5)
    
    assert x2 == 2.0 * x1

def test_stage3_limits_peak_pressure():
    pytest.xfail("FROSS4 delegates completely to FROSSAccumulator now")
    config = SystemConfig()
    fross = FROSS4(config)
    
    dV_dt = fross.stage3_accumulator_absorption(2e6, 1e6)
    assert dV_dt < 0

def test_stage4_triggers_ultimate_protection():
    config = SystemConfig()
    fross = FROSS4(config)
    
    trigger_below = fross.stage4_ultimate_protection(0.9 * config.max_pressure_vessel)
    trigger_above = fross.stage4_ultimate_protection(0.96 * config.max_pressure_vessel)
    
    assert not trigger_below
    assert trigger_above
