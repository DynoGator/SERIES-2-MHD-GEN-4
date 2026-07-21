import pytest
import numpy as np
from physics.thermo.accumulator import FROSSAccumulator

from config.system_config import SystemConfig

def test_polytropic_compression():
    acc = FROSSAccumulator(SystemConfig())
    p1 = acc.pressure(0.5)
    p2 = acc.pressure(0.25)
    assert abs(p2 / p1 - (2.0)**1.3) < 1e-6

def test_work_positive_on_expansion():
    acc = FROSSAccumulator(SystemConfig())
    # V1 > V0 means expansion
    W_rec = acc.work_recovered(0.2, 0.4)
    assert W_rec > 0

def test_pressure_relaxation():
    acc = FROSSAccumulator(SystemConfig())
    # If p_vessel > p_accum, dV_dt < 0, so accumulator gas volume decreases
    p_accum = acc.pressure(0.2)
    dV = acc.dV_dt(p_vessel=p_accum*1.1, p_accum=p_accum)
    assert dV < 0

