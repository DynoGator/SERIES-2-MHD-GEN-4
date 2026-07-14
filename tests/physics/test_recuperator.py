import pytest
from physics.thermo.recuperator import Recuperator
from config.system_config import SystemConfig

def test_effectiveness_bounded():
    config = SystemConfig()
    rec = Recuperator(config)
    # T_hot_in, T_cold_in, T_cold_out
    assert rec.effectiveness(1000.0, 300.0, 650.0) == 0.5
    assert rec.effectiveness(1000.0, 300.0, 1100.0) == 1.0 # Bounded to 1.0
    assert rec.effectiveness(200.0, 300.0, 250.0) == 0.0 # Bounded to 0.0

def test_higher_effectiveness_reduces_source_heat():
    config = SystemConfig()
    rec = Recuperator(config)
    # Given net_value, a higher recovered Q translates to more W_avoided
    val1 = rec.net_value(1000.0, 50.0)
    val2 = rec.net_value(2000.0, 50.0)
    assert val2 > val1

def test_compressor_penalty_accounted():
    config = SystemConfig()
    rec = Recuperator(config)
    val1 = rec.net_value(1000.0, 50.0)
    val2 = rec.net_value(1000.0, 100.0)
    assert val1 > val2
