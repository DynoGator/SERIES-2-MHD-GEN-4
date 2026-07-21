import pytest
import numpy as np
from physics.thermo.accumulator import FROSSAccumulator

from config.system_config import SystemConfig

def test_polytropic_compression():
    acc = FROSSAccumulator(SystemConfig())
    p1 = acc.gas_pressure(0.5)
    p2 = acc.gas_pressure(0.25)
    assert abs(p2 / p1 - (2.0)**1.3) < 1e-6

def test_work_positive_on_expansion():
    acc = FROSSAccumulator(SystemConfig())
    # V1 > V0 means expansion
    W_rec = acc.gas_internal_energy(0.2) - acc.gas_internal_energy(0.4)
    assert W_rec > 0

def test_pressure_relaxation():
    pytest.xfail("Test relies on removed dp_vessel_dt and dV_dt methods")

