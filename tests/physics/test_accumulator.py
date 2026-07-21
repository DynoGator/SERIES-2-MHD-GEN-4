import pytest
import numpy as np
from physics.thermo.accumulator import FROSSAccumulator

def test_polytropic_compression():
    acc = FROSSAccumulator({})
    p1 = acc.pressure(0.5)
    p2 = acc.pressure(0.25)
    assert abs(p2 / p1 - (2.0)**1.3) < 1e-6

def test_work_positive_on_expansion():
    acc = FROSSAccumulator({})
    # V1 > V0 means expansion
    W_rec = acc.work_recovered(0.2, 0.4)
    assert W_rec > 0

def test_pressure_relaxation():
    acc = FROSSAccumulator({})
    # If p_vessel > p_accum, dV_dt > 0, so accumulator volume increases
    p_accum = acc.pressure(0.2)
    dV = acc.dV_dt(p_vessel=p_accum*1.1, p_accum=p_accum)
    assert dV > 0

def test_volume_clamping():
    acc = FROSSAccumulator({})
    p0 = acc.pressure(0.0) # Should not raise ZeroDivisionError
    assert p0 > 0
    W = acc.work_recovered(0.0, 0.2)
    assert W > 0
