import pytest
from physics.thermo.dloop import DLoopRankine
from config.system_config import SystemConfig

def test_efficiency_bounded():
    config = SystemConfig()
    dloop = DLoopRankine(config)
    # Carnot at 600K source, 300K sink is 0.5. Rankine approx 0.25
    assert dloop.rankine_efficiency(600.0, 300.0) <= 0.5
    assert dloop.rankine_efficiency(300.0, 600.0) == 0.0

def test_steam_generation_increases_with_exhaust_temp():
    config = SystemConfig()
    dloop = DLoopRankine(config)
    m1 = dloop.steam_generation_rate(1000.0, 400.0)
    m2 = dloop.steam_generation_rate(2000.0, 500.0)
    assert m2 > m1

def test_no_generation_below_boiling():
    config = SystemConfig()
    dloop = DLoopRankine(config)
    assert dloop.steam_generation_rate(1000.0, 300.0) == 0.0
