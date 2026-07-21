from config.system_config import SystemConfig
import pytest
from physics.thermo.heat_transfer import HeatTransfer

def test_h_increases_with_pressure():
    ht = HeatTransfer(SystemConfig())
    h1 = ht.h_dynamic(1e5, 100.0, 1000.0, 300.0)
    h2 = ht.h_dynamic(2e5, 100.0, 1000.0, 300.0)
    assert h2 > h1

def test_h_increases_with_rpm():
    ht = HeatTransfer(SystemConfig())
    h1 = ht.h_dynamic(1e5, 0.0, 1000.0, 300.0)
    h2 = ht.h_dynamic(1e5, 100.0, 1000.0, 300.0)
    assert h2 > h1

def test_coriolis_enhancement():
    ht = HeatTransfer(SystemConfig())
    Nu0 = 100.0
    Nu_coriolis = ht.nusselt_coriolis(Nu0, 50.0, 0.5, 1e-5)
    assert Nu_coriolis > Nu0

def test_cooling_flux_direction():
    ht = HeatTransfer(SystemConfig())
    h = ht.h_dynamic(1e5, 100.0, 1000.0, 300.0)
    # Heat from wall to coolant is Q = h * A * (T_wall - T_coolant)
    Q = h * 1.0 * (1000.0 - 300.0)
    assert Q > 0
    Q_rev = h * 1.0 * (300.0 - 1000.0)
    assert Q_rev < 0
