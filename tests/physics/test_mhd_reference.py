import math
import pytest
from physics.reference.mhd_reference import (
    mhd_faraday_power_density,
    carnot_exergy_of_heat,
    exergy_imbalance,
    second_law_efficiency,
    saha_electron_density,
    orifice_flow
)

def test_mhd_reference_values():
    assert math.isclose(mhd_faraday_power_density(0, 1200, 4, 0.5), 0.0)
    assert math.isclose(mhd_faraday_power_density(50, 1200, 4, 0.5), 2.88e8, rel_tol=1e-5)
    assert math.isclose(carnot_exergy_of_heat(200e3, 600, 300), 1.0e5)
    assert math.isclose(exergy_imbalance(150e3, 1.0e5), 5.0e4)
    assert math.isclose(second_law_efficiency(150e3, 1.0e5), 1.5)
