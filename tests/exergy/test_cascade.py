import pytest
from physics.exergy.cascade import ExergyCascade
from config.system_config import SystemConfig

def test_exergy_of_heat_increases_with_temperature():
    config = SystemConfig()
    cascade = ExergyCascade(config)
    x1 = cascade.exergy_of_heat(1000.0, 400.0)
    x2 = cascade.exergy_of_heat(1000.0, 600.0)
    assert x2 > x1

def test_destruction_non_negative():
    config = SystemConfig()
    cascade = ExergyCascade(config)
    assert cascade.destruction_rate() >= 0.0

def test_efficiency_ii_bounded():
    config = SystemConfig()
    cascade = ExergyCascade(config)
    cascade._W_net = 100.0
    cascade._X_useful = 50.0
    cascade._X_source = 1000.0
    cascade._W_shaft_in = 0.0
    eff1 = cascade.efficiency_ii()
    assert 0.0 <= eff1 <= 1.0
    
    cascade._W_net = 2000.0
    cascade._X_useful = 0.0
    cascade._X_source = 1000.0
    cascade._W_shaft_in = 0.0
    eff2 = cascade.efficiency_ii()
    assert eff2 == 1.0 # Bounded to 1.0
